import sqlite3
import os
import re

def clean_ascii(text):
    if not text:
        return ""
    text = text.replace("—", " - ").replace("–", " - ")
    text = text.replace("“", "\"").replace("”", "\"").replace("’", "'").replace("‘", "'")
    text = text.replace("…", "...")
    # Remove markdown formatting characters
    text = re.sub(r"[*_`#~|]", "", text)
    # Convert to pure ASCII
    text = text.encode("ascii", errors="ignore").decode("ascii")
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

conn = sqlite3.connect("/tmp/DiscoBrowser/db/discobase.sqlite3")
cur = conn.cursor()

# 1. Clean and export Items
items_path = "Sources/MATERIALS/02_ITEMS_AND_EQUIPMENT/CANONICAL_ITEMS_INDEX.txt"
with open(items_path, "w", encoding="ascii") as out:
    for row in cur.execute("SELECT id, name, description FROM items ORDER BY id"):
        item_id, name, desc = row
        c_name = clean_ascii(name)
        c_desc = clean_ascii(desc)
        out.write(f"Item ID: {item_id}\nName: {c_name}\nDescription: {c_desc}\n\n")

# 2. Clean and export Actors
actors_path = "Sources/MATERIALS/03_CHARACTERS_AND_ACTORS/CANONICAL_ACTORS_INDEX.txt"
with open(actors_path, "w", encoding="ascii") as out:
    for row in cur.execute("SELECT id, name FROM actors ORDER BY id"):
        act_id, name = row
        c_name = clean_ascii(name)
        out.write(f"Actor ID: {act_id}\nName: {c_name}\n\n")

# 3. Clean and export Conversations Hubs
convs_path = "Sources/MATERIALS/05_CONVERSATIONAL_HUBS/CANONICAL_CONVERSATIONS_INDEX.txt"
with open(convs_path, "w", encoding="ascii") as out:
    for row in cur.execute("SELECT id, title, description FROM conversations ORDER BY id"):
        c_id, title, desc = row
        c_title = clean_ascii(title)
        c_desc = clean_ascii(desc)
        out.write(f"Conversation ID: {c_id}\nTitle: {c_title}\nDescription: {c_desc}\n\n")

# 4. Clean and export Subtasks
subtasks_path = "Sources/MATERIALS/06_TASKS_AND_HISTORICAL_NOTES/CANONICAL_TASKS_INDEX.txt"
with open(subtasks_path, "w", encoding="ascii") as out:
    for row in cur.execute("SELECT id, conversationid, name FROM subtasks ORDER BY id"):
        s_id, c_id, name = row
        c_name = clean_ascii(name)
        out.write(f"Task ID: {s_id}\nConversation ID: {c_id}\nTask Name: {c_name}\n\n")

# 5. Clean and export Sacred and Terrible Air
book_src = "/tmp/sacred_and_terrible_air_raw.txt"
book_dst = "Sources/MATERIALS/04_LITERATURE_SACRED_AND_TERRIBLE_AIR/SACRED_AND_TERRIBLE_AIR_CLEAN_ASCII.txt"
if os.path.exists(book_src):
    with open(book_src, "r", encoding="utf-8", errors="ignore") as f_in:
        raw_book = f_in.read()
    clean_book = clean_ascii(raw_book)
    with open(book_dst, "w", encoding="ascii") as f_out:
        f_out.write(clean_book)

# 6. Extract Canonical Dialogue Nodes by Key Lore Concepts
# Map actor id to name
actor_map = {}
for aid, aname in cur.execute("SELECT id, name FROM actors"):
    actor_map[aid] = clean_ascii(aname)

# Extract dialogue entries where text is substantive (length > 30)
dialogue_out = "Sources/MATERIALS/01_DIALOGUE_AND_ORBS/CANONICAL_DIALOGUE_LORE_DUMP.txt"
with open(dialogue_out, "w", encoding="ascii") as out:
    query = """
    SELECT d.conversationid, c.title, d.actor, d.dialoguetext
    FROM dentries d
    LEFT JOIN conversations c ON d.conversationid = c.id
    WHERE d.dialoguetext IS NOT NULL AND length(d.dialoguetext) > 40
    ORDER BY d.conversationid, d.id
    """
    for row in cur.execute(query):
        conv_id, c_title, actor_id, d_text = row
        actor_name = actor_map.get(actor_id, "Narrator")
        clean_text = clean_ascii(d_text)
        if clean_text:
            out.write(f"[{clean_ascii(c_title)}] {actor_name}: {clean_text}\n\n")

print("Processing complete. All sources cleaned to strict ASCII.")
