# Disco Elysium Lorebook for Character.ai

A comprehensive, highly structured, 125-entry canonical lorebook and bot engine tailored for Character.ai, strictly confined to the Insulindian Isola and the city of Revachol.

---

## Documentation & Guides

- **Firefox & Ingestion Guide**: [`FIREFOX_USER_GUIDE.md`](FIREFOX_USER_GUIDE.md) — Complete setup instructions for Firefox users, Tampermonkey bridge setup, Web Console DOM injector, and permission guards.
- **Quick User Guide**: [`USER_GUIDE.md`](USER_GUIDE.md) — Quick reference for entries and sync automation.
- **Project Specifications**: [`PROJECT.MD`](PROJECT.MD) — Scope restrictions, budget constraints, and formatting rules.
- **Bot Persona & Definition**: [`Prompts/CAIBOT.MD`](Prompts/CAIBOT.MD) — Full Character.ai character definition (the 24 internal Skills, primal voices, and crosstalk).
- **Opening Greeting**: [`Prompts/SCENE.MD`](Prompts/SCENE.MD) — Canonical opening scene in Martinaise.
- **In-Universe Canon**: [`Categories/Canon.MD`](Categories/Canon.MD) — Master simulation boundaries and reality definitions.

---

## Directory Structure

```
DiscoElysium-Lorebook/
├── Categories/                 # 125 Completed Lore Entries (01 Location through 09 Creatures + Canon)
│   ├── Canon.MD                # Master simulation boundaries and in-universe canon
│   ├── 00. Canon/              # Source authority and developer reference
│   ├── 01. Location/           # 26 entries (Martinaise, Jamrock, Bay of Revachol, etc.)
│   ├── 02. Item/               # 14 entries (Weapons, narcotics, technology, garments, relics)
│   ├── 03. Side character/     # 20 entries (RCM officers, union leaders, mercenaries, locals)
│   ├── 04. Event/              # 14 entries (Historical eras, Commune, Great Disappearance)
│   ├── 05. Faction/            # 16 entries (RCM, Union, Wild Pines, Moralintern, Royalists)
│   ├── 06. System/             # 13 entries (Geography, physics, law, radiocomputing, dialects)
│   ├── 07. Culture and Religion/# 12 entries (Music, suzerainty, cuisine, mourning, sports)
│   ├── 08. Species/            # 4 entries (Demographics, colonial waves, Seolite diaspora)
│   └── 09. Creatures/          # 5 entries (Phasmid, seabirds, sea-bears, crustaceans, stray dogs)
├── POS/                        # Position & synchronization tracking
│   └── UPLOAD-POSITIONS.json   # Real-time upload queue and status
├── Prompts/                    # Bot definitions and scene greetings
│   ├── CAIBOT.MD               # Master 24-skill character definition
│   ├── SCENE.MD                # Opening greeting
│   └── WRITING_RULES.md        # File formatting constraints
├── Scripts/                    # Automation and ingestion scripts
│   ├── cai_lorebook_tampermonkey.user.js # Tampermonkey auto-sync script
│   ├── lore_server.py          # Local HTTP bridge server (port 8765)
│   ├── build_lorebook_payload.py # Payload generator and position validator
│   └── inject_cai_lorebook.js  # Firefox Web Console standalone injector
└── Sources/                    # Canonical source materials and references
```
