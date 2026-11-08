# Writing Rules and Structural Specification

This document lays down the strict formatting and content rules for every Markdown file in this lorebook. These rules are mandatory and non-negotiable.

## Rule 1: Zero Formatting Policy
1. Strictly plain ASCII characters only.
2. Absolutely NO markdown decoration:
   - No asterisks (* or **)
   - No em dashes (-- or unicode em-dash)
   - No en dashes
   - No unnatural hyphens
   - No bullet points (- or *)
   - No markdown headers (# or ##) inside content fields
   - No tables or pipe characters (|)
   - No backticks or code blocks (`)
   - No unicode curly quotes or apostrophes; use standard ASCII single quotes (') and standard ASCII double quotes (")
   - No special symbols, mathematical glyphs, or emojis

## Rule 2: Strict In-Universe Lore and No Fourth Wall Breaking
1. ZERO fourth-wall breaking in any MD entry.
2. Never mention that this is a game, an RPG, character.ai, an AI prompt, a video game by ZA/UM, mechanics, dice rolls, or stats.
3. Treat all subjects as objective, historical, physical, and sociological reality within the world of Elysium.
4. Entries must be pure in-universe factual encyclopedic documentation.
5. No meta-commentary, no out-of-character disclaimers, no references to the player or developer.

## Rule 3: Strict Canonical Grounding (No Hallucinations)
1. Every claim, name, date, entity, geographical feature, and event must strictly originate from Tier 1 or Tier 2 canon as listed in Categories/00. Canon/CANON.MD.
2. Unknown or deliberate mysteries must remain unknown. Never invent lore, dates, numbers, or events to fill gaps.
3. No non-canonical theories, fanfiction, or unauthorized headcanons.

## Rule 4: Distinct Separation of Skills and Lore
1. Internal consciousness, psychological faculties, and the 24 Skills are defined entirely within the bot persona architecture (Prompts/CAIBOT.MD).
2. Lorebook MDs must strictly document external reality: geography, history, factions, people, items, biology, technology, and culture.
3. Do not include Skills or Psyche as standalone categories in the lorebook directory tree.

## Rule 5: Exact File Format
Every markdown file residing in category subfolders must follow this exact schema:

Title:
<Exact Title>

Text:
<Body text of the entry. Minimum 1800 characters spaces included, maximum 2000 characters spaces included. Plain ASCII text only.>

Keywords:
<keyword 1>, <keyword 2>, <keyword 3>

### Format Constraints:
- Length: Text section MUST be strictly between 1800 and 2000 characters (including spaces).
- Keywords: Minimum 2 keywords, maximum 8 keywords, separated by commas.

## Rule 6: Directory and Naming Conventions
- Category Folders: Follow the standard two-digit indexed schema:
  01. Location, 02. Item, 03. Side character, 04. Event, 05. Faction, 06. System, 07. Culture and Religion, 08. Species, 09. Creatures.
- Subfolders: Indexed matching the category schema (e.g., 01.01 World, 01.02 Insulinde).
- Entry Files: Numbered matching the subfolder schema (e.g., 01.01.01 The World.MD).
