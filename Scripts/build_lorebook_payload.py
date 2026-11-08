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
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, BASE_DIR)
            if rel_path == "Categories/00. Canon/CANON.MD" or not (fname.endswith(".MD") or fname.endswith(".md")):
                continue

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

    planned_files = ['Categories/01. Location/01.01 Insulinde/01.01.01 The Insulindian Isola.MD', 'Categories/01. Location/01.01 Insulinde/01.01.02 The Bay of Revachol.MD', 'Categories/01. Location/01.01 Insulinde/01.01.03 The Esperance River.MD', 'Categories/01. Location/01.01 Insulinde/01.01.04 Le Caillou.MD', 'Categories/01. Location/01.01 Insulinde/01.01.05 Sea of Insulinde.MD', 'Categories/01. Location/01.01 Insulinde/01.01.06 Osona and Surrounding Reefs.MD', 'Categories/01. Location/01.01 Insulinde/01.01.07 The Sea Fortress Island.MD', 'Categories/01. Location/01.02 Martinaise/01.02.01 Martinaise District.MD', 'Categories/01. Location/01.02 Martinaise/01.02.02 The Whirling-in-Rags.MD', 'Categories/01. Location/01.02 Martinaise/01.02.03 The Martinaise Coastal Boardwalk.MD', 'Categories/01. Location/01.02 Martinaise/01.02.04 The Martinaise Fishing Village.MD', 'Categories/01. Location/01.02 Martinaise/01.02.05 The Church of the Dolorian.MD', 'Categories/01. Location/01.02 Martinaise/01.02.06 The Martinaise Commercial Harbour.MD', 'Categories/01. Location/01.02 Martinaise/01.02.07 The Feld Building.MD', 'Categories/01. Location/01.02 Martinaise/01.02.08 The Doomed Commercial Area.MD', "Categories/01. Location/01.02 Martinaise/01.02.09 Land's End and Martinaise Canal.MD", 'Categories/01. Location/01.02 Martinaise/01.02.10 The Capeside Apartments.MD', 'Categories/01. Location/01.02 Martinaise/01.02.11 The Martinaise Boulodrome Crater.MD', 'Categories/01. Location/01.03 Jamrock/01.03.01 Jamrock District.MD', 'Categories/01. Location/01.03 Jamrock/01.03.02 RCM Precinct 41 Headquarters.MD', 'Categories/01. Location/01.03 Jamrock/01.03.03 Central Jamrock and Motorway.MD', 'Categories/01. Location/01.03 Jamrock/01.03.04 Couron and Grand-Couron.MD', 'Categories/01. Location/01.04 Other Revachol Districts/01.04.01 Coal City.MD', 'Categories/01. Location/01.04 Other Revachol Districts/01.04.02 Old Town.MD', 'Categories/01. Location/01.04 Other Revachol Districts/01.04.03 Stella Maris and North Coast.MD', 'Categories/01. Location/01.04 Other Revachol Districts/01.04.04 Boogie Street and Valley of the Dogs.MD', 'Categories/02. Item/02.01 Weapons and Armor/02.01.01 Villiers 9mm Pepperbox Pistol.MD', 'Categories/02. Item/02.01 Weapons and Armor/02.01.02 Kiejl A9 Compression Rifle.MD', 'Categories/02. Item/02.01 Weapons and Armor/02.01.03 Fairweather T-56 Body Armor.MD', 'Categories/02. Item/02.01 Weapons and Armor/02.01.04 RCM Heavy Duty Prybar and Baton.MD', 'Categories/02. Item/02.02 Technology and Tools/02.02.01 Filament Wire Radiocomputer.MD', 'Categories/02. Item/02.02 Technology and Tools/02.02.02 FALN Heavy LED Flashlight.MD', 'Categories/02. Item/02.02 Technology and Tools/02.02.03 RCM Blue Ledger and Clipboard.MD', 'Categories/02. Item/02.02 Technology and Tools/02.02.04 Coupris Kineema Motor Carriage.MD', 'Categories/02. Item/02.03 Narcotics and Consumables/02.03.01 Astra Brand Filterless Cigarettes.MD', 'Categories/02. Item/02.03 Narcotics and Consumables/02.03.02 Goracy 1 Spirits and Potent Wine.MD', 'Categories/02. Item/02.03 Narcotics and Consumables/02.03.03 Pyrholidon and Preptocain.MD', 'Categories/02. Item/02.04 Cultural and Relic Items/02.04.01 Suzerainty Historical Board Game.MD', 'Categories/02. Item/02.04 Cultural and Relic Items/02.04.02 Sad Surreal Interisolary Tape.MD', 'Categories/02. Item/02.04 Cultural and Relic Items/02.04.03 Pre-Revolutionary Frissel Medals.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.01 Lieutenant Kim Kitsuragi.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.02 Captain Pryce.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.03 Lieutenant Jean Vicquemare.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.04 Officer Judit Minot.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.05 Officer Trant Heidelstam.MD', 'Categories/03. Side character/03.01 RCM Officers/03.01.06 Chester McLaine and Alice Steine.MD', 'Categories/03. Side character/03.02 Union and Hardie Boys/03.02.01 Evrart Claire.MD', 'Categories/03. Side character/03.02 Union and Hardie Boys/03.02.02 Titus Hardie and Hardie Boys.MD', 'Categories/03. Side character/03.02 Union and Hardie Boys/03.02.03 Leo the Harmless Dockworker.MD', 'Categories/03. Side character/03.03 Wild Pines and Mercenaries/03.03.01 Joyce Messier.MD', 'Categories/03. Side character/03.03 Wild Pines and Mercenaries/03.03.02 Colonel Kortenaer.MD', 'Categories/03. Side character/03.03 Wild Pines and Mercenaries/03.03.03 Ruud Hoogenstraten and De Pauw.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.01 Garte the Cafeteria Manager.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.02 Lena and Morell the Cryptozoologist.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.03 Rene Arnoux and Gaston Martin.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.04 Cuno and Cunoesse.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.05 Klaasje Amandou.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.06 The Paledriver.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.07 Plaisance and Annette.MD', 'Categories/03. Side character/03.04 Martinaise Citizens/03.04.08 Iosef Lilianovich Dros the Deserter.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.01 Dolores Dei Arrival in Insulinde.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.02 Suzerainty of the Frissel Monarchy.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.03 The Antecentennial War.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.04 The Revachol Commune Revolution.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.05 The Coalition Naval Bombardment of Year 08.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.06 Post-Commune Executions and Wall of Martyrs.MD', 'Categories/04. Event/04.01 Historical Eras/04.01.07 Formation of the Revachol Citizens Militia.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.01 The Martinaise Dockworkers Strike of 51.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.02 The Lynching Behind the Whirling.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.03 The Sinking of the Motor Carriage into the Ice.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.04 The Church Dance Club Incident.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.05 The Martinaise Mercenary Tribunal.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.06 Sighting of the Insulindian Phasmid.MD', 'Categories/04. Event/04.02 Modern Crisis and Timeline/04.02.07 The Era of the Great Disappearance.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.01 Revachol Citizens Militia.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.02 Debardeurs Union Local 41.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.03 The Hardie Boys Council.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.04 Wild Pines Group.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.05 Coalition of Nations and Moralintern.MD', 'Categories/05. Faction/05.01 Civic and Corporate/05.01.06 Coalition Armed Forces and Warships.MD', 'Categories/05. Faction/05.02 Political and Ideological/05.02.01 Revachol Communards and Historic Party.MD', 'Categories/05. Faction/05.02 Political and Ideological/05.02.02 Royalist Carabiniers and Monarchists.MD', 'Categories/05. Faction/05.02 Political and Ideological/05.02.03 Revacholian Nationalists.MD', 'Categories/05. Faction/05.02 Political and Ideological/05.02.04 Sunday Friends and Bureaucrats.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.01 Krenel Mercenary Company.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.02 La Puta Madre Criminal Syndicate.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.03 Capeside Drug Smuggling Ring.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.04 The Forgotten Red Army Guerrillas.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.05 Martinaise Youth Gangs and Speedfreaks.MD', 'Categories/05. Faction/05.03 Militant and Underground/05.03.06 Holy Dolorian Congregation of Revachol.MD', 'Categories/06. System/06.01 Geography and Physics/06.01.01 Insulindian Oceanic Geography and Climate.MD', 'Categories/06. System/06.01 Geography and Physics/06.01.02 Pale Borderlands of the Insulindian Isola.MD', 'Categories/06. System/06.01 Geography and Physics/06.01.03 Pale Sickness and Entropic Amnesia.MD', 'Categories/06. System/06.02 Law and Civic Order/06.02.01 Legal Status of Revachol Administrative Region.MD', 'Categories/06. System/06.02 Law and Civic Order/06.02.02 RCM Jurisdictional Authority and Protocols.MD', 'Categories/06. System/06.02 Law and Civic Order/06.02.03 Revacholian Currency Real and Centimes.MD', 'Categories/06. System/06.03 Technology and Infrastructure/06.03.01 Radiocomputing and Magnetic Filament Storage.MD', 'Categories/06. System/06.03 Technology and Infrastructure/06.03.02 Kineema Mechanics and Motor Transport.MD', 'Categories/06. System/06.03 Technology and Infrastructure/06.03.03 Insulindian Aerostatics and Air Navigation.MD', 'Categories/06. System/06.03 Technology and Infrastructure/06.03.04 Revachol Subterranean Brick Sewers and Ruins.MD', 'Categories/06. System/06.04 Medicine and Sociolinguistics/06.04.01 Revacholian Vernacular Slang and Dialects.MD', 'Categories/06. System/06.04 Medicine and Sociolinguistics/06.04.02 Insulindian Pharmacology and Street Chemistry.MD', 'Categories/06. System/06.04 Medicine and Sociolinguistics/06.04.04 The Innocence Succession Doctrine in Revachol.MD', 'Categories/07. Culture and Religion/07.01 Society and Belief/07.01.01 Revacholian Identity and Spirit of Le Caillou.MD', 'Categories/07. Culture and Religion/07.01 Society and Belief/07.01.02 Martinaise Working Class Coastal Culture.MD', 'Categories/07. Culture and Religion/07.01 Society and Belief/07.01.03 Holy Dolorian Faith and Stained Glass Cult.MD', 'Categories/07. Culture and Religion/07.01 Society and Belief/07.01.04 Royalist Nostalgia and Suzerainty Traditions.MD', 'Categories/07. Culture and Religion/07.01 Society and Belief/07.01.05 Communard Memory and Revolutionary Graffitis.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.01 Anodic Dance Music and Tape Underground.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.02 Suzerainty Strategic Board Game Culture.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.03 Revacholian Working Class Cuisine and Chicory.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.04 Astra Tobacco Culture and Drinking Rituals.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.05 Mass Entertainment and Guillaume le Million.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.06 Mourning Customs and Insulindian Cemeteries.MD', 'Categories/07. Culture and Religion/07.02 Arts, Pastimes and Customs/07.02.07 Martinaise Petanque and Coastal Pastimes.MD', 'Categories/08. Species/08.01 Insulindian Demographics/08.01.01 Human Populations of the Insulindian Isola.MD', 'Categories/08. Species/08.01 Insulindian Demographics/08.01.02 Revacholian Colonial Demographics and Migrations.MD', 'Categories/08. Species/08.01 Insulindian Demographics/08.01.03 Seolite Minorities in Revachol West.MD', 'Categories/08. Species/08.01 Insulindian Demographics/08.01.04 Physiological Impact of Insulindian Pale Proximity.MD', 'Categories/09. Creatures/09.01 Insulindian Fauna/09.01.01 Insulindian Phasmid.MD', 'Categories/09. Creatures/09.01 Insulindian Fauna/09.01.02 Insulindian Coastal Gulls and Seabirds.MD', 'Categories/09. Creatures/09.01 Insulindian Fauna/09.01.03 Insulindian Sea-Bears and Marine Beasts.MD', 'Categories/09. Creatures/09.01 Insulindian Fauna/09.01.04 Coastal Crustaceans and Kelp Feeders.MD', 'Categories/09. Creatures/09.01 Insulindian Fauna/09.01.05 Jamrock Urban Stray Dogs and Vermin.MD', 'Categories/Canon.MD']
    written_files = [e["file"] for e in all_entries]
    unwritten_files = [f for f in planned_files if f not in written_files]

    pos_data["max_allowed_entries"] = 128
    pos_data["total_planned_entries"] = len(planned_files)
    pos_data["written_count"] = len(written_files)
    pos_data["written_files"] = written_files
    pos_data["unwritten_count"] = len(unwritten_files)
    pos_data["unwritten_files"] = unwritten_files
    pos_data["total_entries"] = len(all_entries)
    pos_data["uploaded_count"] = len(uploaded_files)
    pos_data["pending_count"] = len(pending_list)
    pos_data["pending_files"] = pending_list
    save_positions(pos_data)

    print(f"Total planned:   {len(planned_files)}")
    print(f"Written entries: {len(written_files)}")
    print(f"Remaining:       {len(unwritten_files)}")
    print(f"Uploaded:        {len(uploaded_files)}")
    print(f"Pending upload:  {len(pending_list)}")

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
