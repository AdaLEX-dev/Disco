# Disco Elysium Lorebook Project: Insulinde & Revachol

Master documentation and specification for the Character.ai Disco Elysium Lorebook repository.

## Mission
Build an exhaustive, strictly canonical lore database covering the Insulindian Isola and the city of Revachol, optimized for Character.ai bot persona grounding, dynamic context retrieval, and seamless integration.

## Scope Restriction: Insulinde & Revachol Only
- The database is strictly confined to the Insulindian Isola and the city of Revachol.
- Do not flesh out external isolas (Mundi, Graad, Seol, Katla, Samara, etc.) as standalone lore entries.
- The entire Insulindian Isola, the Bay of Revachol, Martinaise, Jamrock, Coal City, Old Town, and the surrounding reefs and islands are covered in exhaustive, living detail.

## Entry Budget: Exactly 125 Final Entries
To comply with Character.ai's maximum single lorebook capacity (128 entries max), the repository contains exactly 125 completed markdown entry files:

0. Categories/Canon.MD: 1 entry (Master in-universe canon and simulation boundaries)
1. 01. Location: 26 entries (Martinaise, Jamrock, Bay of Revachol, districts, landmarks, sea ruins)
2. 02. Item: 14 entries (Weapons, narcotics, technology, garments, cultural artifacts)
3. 03. Side character: 20 entries (RCM officers, union leaders, mercenaries, locals, suspects)
4. 04. Event: 14 entries (Antecentennial War, Commune, Bombardment, Strike, Tribunal, Great Disappearance)
5. 05. Faction: 16 entries (RCM, Debardeurs Union, Wild Pines, Moralintern, Royalists, Gangs)
6. 06. System: 13 entries (Pale borderlands, radiocomputers, RCM protocols, currencies, pale sickness)
7. 07. Culture and Religion: 12 entries (Anodic music, Dolores Dei cult, suzerainty, cuisine, cinema)
8. 08. Species: 4 entries (Insulindian human populations, demographic migrations, pale exposure)
9. 09. Creatures: 5 entries (Insulindian Phasmid, coastal birds, sea-bears, crustaceans, urban stray dogs)

Total: 125 entries (100% complete, verified, and synchronized).

## Strict Format Constraints for Entry Files
Every entry markdown file residing inside category subfolders must follow this exact schema:

Title:
<Exact Title>

Text:
<Body text strictly between 1800 and 2000 characters spaces included>

Keywords:
<keyword 1>, <keyword 2> (minimum 2, maximum 8)

## Zero Formatting Rules
- Strictly plain ASCII characters only (no unicode, curly quotes, or accented glyphs outside canonical ASCII transliterations).
- Absolutely no markdown asterisks, em dashes, en dashes, unnatural hyphens, tables, bullet points, backticks, or headers inside the text field.
- No outside non-canonical sources, fanfiction, or speculative hallucinations.
