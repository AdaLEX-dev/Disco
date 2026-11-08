#!/usr/bin/env python3
"""
record_cai_lorebook_positions.py

Tracks and updates upload positions and metadata for Character.ai lorebook compilation.
Maintains POS/UPLOAD-POSITIONS.json with file indices, keyword associations, and upload statuses.
"""

import json
import os
import sys

POSITIONS_FILE = os.path.join(os.path.dirname(__file__), "POS", "UPLOAD-POSITIONS.json")
CATEGORIES_DIR = os.path.join(os.path.dirname(__file__), "Categories")

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {POSITIONS_FILE}: {e}", file=sys.stderr)
    return {"project": "Disco Elysium Lorebook", "categories": {}, "uploaded_files": []}

def save_positions(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated {POSITIONS_FILE}")

def scan_and_record():
    data = load_positions()
    categories = {}

    if not os.path.isdir(CATEGORIES_DIR):
        print(f"Directory {CATEGORIES_DIR} does not exist.")
        return

    for cat in sorted(os.listdir(CATEGORIES_DIR)):
        cat_path = os.path.join(CATEGORIES_DIR, cat)
        if not os.path.isdir(cat_path):
            continue

        categories[cat] = {}
        for sub in sorted(os.listdir(cat_path)):
            sub_path = os.path.join(cat_path, sub)
            if not os.path.isdir(sub_path):
                continue

            md_files = [f for f in sorted(os.listdir(sub_path)) if f.endswith(".md") or f.endswith(".MD")]
            categories[cat][sub] = {
                "file_count": len(md_files),
                "files": md_files
            }

    data["categories"] = categories
    save_positions(data)

if __name__ == "__main__":
    scan_and_record()
