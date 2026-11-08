#!/usr/bin/env python3
"""
lore_server.py

Local lightweight HTTP daemon connecting Character.ai Tampermonkey script directly
to the repository's lore database.

Endpoints:
- GET  /api/entries   : Returns all entries parsed from Categories/ with upload status
- POST /api/mark_done : Marks a specific MD file as done in POS/UPLOAD-POSITIONS.json
"""

import http.server
import json
import os
import socketserver
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(BASE_DIR, "Categories")
POS_FILE = os.path.join(BASE_DIR, "POS", "UPLOAD-POSITIONS.json")
PORT = 8765

def parse_lore_md(file_path):
    with open(file_path, "r", encoding="ascii") as f:
        content = f.read()

    title = ""
    text_lines = []
    keywords = []
    mode = None

    for line in content.split("\n"):
        if line.startswith("Title:"):
            mode = "title"
            continue
        elif line.startswith("Text:"):
            mode = "text"
            continue
        elif line.startswith("Keywords:"):
            mode = "keywords"
            continue

        if mode == "title" and not title and line.strip():
            title = line.strip()
        elif mode == "text":
            text_lines.append(line)
        elif mode == "keywords" and line.strip():
            raw_kw = line.strip()
            keywords = [k.strip() for k in raw_kw.split(",") if k.strip()]

    body_text = "\n".join(text_lines).strip()
    return title, body_text, keywords

def load_pos():
    if os.path.exists(POS_FILE):
        try:
            with open(POS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"project": "Disco Elysium Lorebook", "uploaded_files": []}

def save_pos(data):
    os.makedirs(os.path.dirname(POS_FILE), exist_ok=True)
    with open(POS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_all_entries():
    pos_data = load_pos()
    uploaded = set(pos_data.get("uploaded_files", []))
    entries = []

    for root, dirs, files in os.walk(CATEGORIES_DIR):
        dirs.sort()
        for fname in sorted(files):
            if fname == "CANON.MD" or not (fname.endswith(".MD") or fname.endswith(".md")):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, BASE_DIR)
            try:
                title, text, keywords = parse_lore_md(fpath)
            except Exception as e:
                continue

            entries.append({
                "file": rel,
                "title": title,
                "text": text,
                "keywords": keywords,
                "done": rel in uploaded
            })
    return entries

class LoreRequestHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/entries":
            entries = get_all_entries()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"entries": entries}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/mark_done":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body.decode("utf-8"))
            file_done = data.get("file")

            if file_done:
                pos = load_pos()
                uploaded = set(pos.get("uploaded_files", []))
                uploaded.add(file_done)
                pos["uploaded_files"] = sorted(list(uploaded))
                save_pos(pos)
                print(f"[Done] Marked uploaded: {file_done}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Quiet standard HTTP access log
        return

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), LoreRequestHandler) as httpd:
        print(f"Lorebook local bridge listening on http://127.0.0.1:{PORT}")
        print("Ready for Tampermonkey sync requests...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run()
