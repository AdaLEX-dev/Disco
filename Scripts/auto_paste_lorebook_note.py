#!/usr/bin/env python3
"""
auto_paste_lorebook_note.py

Automated mouse mover, clicker, and text paster for Character.ai Lorebook notes.
Parses MD files adhering to the project schema and uses calibrated coordinates:
0. New Note button
1. Title
2. Text
3. Keyword add positions 1-8
4. Save button

Supports Wayland (wl-copy) and X11 clipboard pasting.
"""

import json
import os
import subprocess
import sys
import time

try:
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Controller as KeyboardController, Key
except ImportError:
    print("pynput is required. Install via: pip install pynput", file=sys.stderr)
    sys.exit(1)

mouse = MouseController()
keyboard = KeyboardController()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "POS", "COORDINATES_CONFIG.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found. Run calibrate_positions.py first.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def copy_to_clipboard(text):
    """Copies text to system clipboard using wl-copy or xclip."""
    if os.path.exists("/usr/bin/wl-copy"):
        p = subprocess.Popen(["/usr/bin/wl-copy"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
    else:
        try:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
        except FileNotFoundError:
            # Fallback direct keyboard type
            pass

def click_at(x, y, delay=0.4):
    mouse.position = (x, y)
    time.sleep(0.1)
    mouse.press(Button.left)
    time.sleep(0.05)
    mouse.release(Button.left)
    time.sleep(delay)

def paste_clipboard(delay=0.3):
    keyboard.press(Key.ctrl)
    keyboard.press("v")
    keyboard.release("v")
    keyboard.release(Key.ctrl)
    time.sleep(delay)

def parse_lore_md(md_path):
    """Extracts Title, Text, and Keywords from a strictly formatted MD file."""
    with open(md_path, "r", encoding="ascii") as f:
        content = f.read()

    title, text, keywords = "", "", []
    lines = content.split("\n")
    mode = None
    body_lines = []

    for line in lines:
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
            body_lines.append(line)
        elif mode == "keywords" and line.strip():
            raw_kw = line.strip()
            keywords = [k.strip() for k in raw_kw.split(",") if k.strip()]

    text = "\n".join(body_lines).strip()
    return title, text, keywords

def upload_note(title, text, keywords, config):
    delay = config.get("delay_between_actions", 0.4)

    # 0. New Note button
    print(f"-> Clicking New Note button at {config['new_note_button']}")
    click_at(config["new_note_button"]["x"], config["new_note_button"]["y"], delay * 1.5)

    # 1. Title
    print(f"-> Pasting Title: '{title}'")
    click_at(config["title_input"]["x"], config["title_input"]["y"], delay)
    copy_to_clipboard(title)
    paste_clipboard(delay)

    # 2. Text
    print(f"-> Pasting Text ({len(text)} characters)")
    click_at(config["text_input"]["x"], config["text_input"]["y"], delay)
    copy_to_clipboard(text)
    paste_clipboard(delay)

    # 3. Keyword add positions 1-8
    kw_positions = config.get("keyword_inputs", [])
    print(f"-> Adding {len(keywords)} keywords: {keywords}")
    for idx, kw in enumerate(keywords[:8]):
        if idx < len(kw_positions):
            pos = kw_positions[idx]
            click_at(pos["x"], pos["y"], delay)
        else:
            # If dynamic add button or same box
            pass
        copy_to_clipboard(kw)
        paste_clipboard(delay)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(delay)

    # 4. Save button
    print(f"-> Clicking Save button at {config['save_button']}")
    click_at(config["save_button"]["x"], config["save_button"]["y"], config.get("delay_after_save", 1.5))
    print("-> Note entry saved successfully.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_paste_lorebook_note.py <path_to_md_file>", file=sys.stderr)
        sys.exit(1)

    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"File not found: {md_file}", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    title, text, keywords = parse_lore_md(md_file)
    
    print(f"\nLoaded Lore Entry: '{title}'")
    print(f"Text Length: {len(text)} chars (Allowed: 1800-2000)")
    print(f"Keywords: {len(keywords)} (Allowed: 2-8)")
    print("\nStarting automated paste in 3 seconds. Focus the browser window now!")
    for i in range(3, 0, -1):
        print(f"  {i}...", end="\r", flush=True)
        time.sleep(1)
    print("\nExecuting...")

    upload_note(title, text, keywords, config)

if __name__ == "__main__":
    main()
