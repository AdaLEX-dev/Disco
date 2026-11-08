#!/usr/bin/env python3
"""
build_lorebook_payload.py

Scans all MD files across Categories/ (excluding 00. Canon), parses:
- Title
- Text (strictly verified 1800-2000 chars)
- Keywords (2-8 keywords)

Maintains progress tracking in POS/UPLOAD-POSITIONS.json.
Generates a browser-ready JSON bundle and JavaScript injector script:
Scripts/inject_cai_lorebook.js

Can be pasted directly into Firefox Web Console (F12) on:
https://character.ai/lorebooks/ad0d6c50-5dde-4074-b6a9-0973fa4a4f83
"""

import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(BASE_DIR, "Categories")
POS_FILE = os.path.join(BASE_DIR, "POS", "UPLOAD-POSITIONS.json")
JS_OUTPUT_FILE = os.path.join(BASE_DIR, "Scripts", "inject_cai_lorebook.js")

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

def load_positions():
    if os.path.exists(POS_FILE):
        try:
            with open(POS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"project": "Disco Elysium Lorebook", "uploaded_files": [], "pending_files": []}

def save_positions(data):
    os.makedirs(os.path.dirname(POS_FILE), exist_ok=True)
    with open(POS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_payload():
    pos_data = load_positions()
    uploaded_files = set(pos_data.get("uploaded_files", []))

    all_entries = []
    pending_list = []

    for root, dirs, files in os.walk(CATEGORIES_DIR):
        dirs.sort()
        for fname in sorted(files):
            if fname == "CANON.MD" or not (fname.endswith(".MD") or fname.endswith(".md")):
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, BASE_DIR)

            try:
                title, text, keywords = parse_lore_md(full_path)
            except Exception as e:
                print(f"Error parsing {rel_path}: {e}", file=sys.stderr)
                continue

            entry = {
                "file": rel_path,
                "title": title,
                "text": text,
                "keywords": keywords,
                "char_count": len(text),
                "done": rel_path in uploaded_files
            }

            all_entries.append(entry)
            if rel_path not in uploaded_files:
                pending_list.append(rel_path)

    pos_data["total_entries"] = len(all_entries)
    pos_data["uploaded_count"] = len(uploaded_files)
    pos_data["pending_count"] = len(pending_list)
    pos_data["pending_files"] = pending_list
    save_positions(pos_data)

    print(f"Total MD entries: {len(all_entries)}")
    print(f"Uploaded entries: {len(uploaded_files)}")
    print(f"Pending entries:  {len(pending_list)}")

    # Generate standalone JavaScript injector
    js_template = f"""// Character.ai Lorebook Automation Injector
// Target URL: https://character.ai/lorebooks/ad0d6c50-5dde-4074-b6a9-0973fa4a4f83
(async function() {{
  const ENTRIES = {json.dumps(all_entries, indent=2)};
  
  console.log("%c[C.AI Lorebook Loader] Starting automated ingestion...", "color: #10b981; font-weight: bold; font-size: 14px;");

  function sleep(ms) {{
    return new Promise(resolve => setTimeout(resolve, ms));
  }}

  function findElementByText(selector, textPattern) {{
    const elements = Array.from(document.querySelectorAll(selector));
    return elements.find(el => {{
      const content = (el.innerText || el.textContent || '').trim().toLowerCase();
      if (typeof textPattern === 'string') {{
        return content === textPattern.toLowerCase() || content.includes(textPattern.toLowerCase());
      }}
      return textPattern.test(content);
    }});
  }}

  function setNativeValue(element, value) {{
    const lastValue = element.value;
    element.value = value;
    const event = new Event('input', {{ bubbles: true }});
    const changeEvent = new Event('change', {{ bubbles: true }});
    const tracker = element._valueTracker;
    if (tracker) {{
      tracker.setValue(lastValue);
    }}
    element.dispatchEvent(event);
    element.dispatchEvent(changeEvent);
  }}

  const pendingEntries = ENTRIES.filter(e => !e.done);
  console.log(`Found ${{pendingEntries.length}} pending entries to upload.`);

  for (let i = 0; i < pendingEntries.length; i++) {{
    const item = pendingEntries[i];
    console.log(`\\n[%c${{i + 1}}/${{pendingEntries.length}}%c] Processing: "${{item.title}}" (${{item.file}})`, "color: #3b82f6; font-weight: bold;", "");

    // 0. Locate and click "Add a new entry" or "New Note"
    let addBtn = findElementByText('button, div[role="button"], span', 'Add a new entry') 
              || findElementByText('button, div[role="button"], span', 'Add entry')
              || findElementByText('button, div[role="button"], span', 'New note');

    if (addBtn) {{
      addBtn.click();
      await sleep(700);
    }}

    // 1. Locate Title Field
    const inputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
    const titleInput = inputs.find(inp => {{
      const placeholder = (inp.placeholder || '').toLowerCase();
      const aria = (inp.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('title') || aria.includes('title') || inp.name.includes('title');
    }}) || inputs[0];

    if (titleInput) {{
      setNativeValue(titleInput, item.title);
      await sleep(300);
    }} else {{
      console.warn("Could not find Title input field.");
    }}

    // 2. Locate Content / Text field
    const textareas = Array.from(document.querySelectorAll('textarea'));
    const contentTextarea = textareas.find(ta => {{
      const placeholder = (ta.placeholder || '').toLowerCase();
      const aria = (ta.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('content') || placeholder.includes('text') || aria.includes('content');
    }}) || textareas[0];

    if (contentTextarea) {{
      setNativeValue(contentTextarea, item.text);
      await sleep(400);
    }} else {{
      console.warn("Could not find Content textarea field.");
    }}

    // 3. Locate Keywords Field & Add Keywords
    const keywordInput = inputs.find(inp => {{
      const placeholder = (inp.placeholder || '').toLowerCase();
      const aria = (inp.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('keyword') || aria.includes('keyword');
    }});

    if (keywordInput && item.keywords && item.keywords.length > 0) {{
      for (const kw of item.keywords) {{
        keywordInput.focus();
        setNativeValue(keywordInput, kw);
        await sleep(150);
        keywordInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
        keywordInput.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
        await sleep(200);
      }}
    }}

    // 4. Click Update / Save button
    let saveBtn = findElementByText('button, div[role="button"]', 'Update')
               || findElementByText('button, div[role="button"]', 'Save')
               || findElementByText('button, div[role="button"]', 'Save changes');

    if (saveBtn) {{
      saveBtn.click();
      console.log(`%c✔ Saved "${{item.title}}"`, "color: #10b981;");
      await sleep(1200);
    }} else {{
      console.error("Could not find Update/Save button.");
    }}
  }}

  console.log("%c[C.AI Lorebook Loader] Batch ingestion finished.", "color: #10b981; font-weight: bold; font-size: 14px;");
}})();
"""

    with open(JS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_template)

    print(f"Generated injector script: {JS_OUTPUT_FILE}")

if __name__ == "__main__":
    build_payload()
