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
   - No markdown headers (# or ##) inside the content fields
   - No tables or pipe characters (|)
   - No backticks or code blocks (`)
   - No unicode curly quotes or apostrophes; use standard ASCII single quotes (') and standard ASCII double quotes (")
   - No special symbols or emojis

## Rule 2: Strict Canonical Grounding (No Hallucinations)
1. Every claim, name, date, entity, and event must strictly originate from Tier 1 or Tier 2 canon as listed in Categories/00-Canon/CANON.MD.
2. If a detail is unknown or unrevealed in canon, it must be stated as unknown or omitted entirely. Do not invent details to bridge gaps.

## Rule 3: Exact File Format
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

## Rule 4: Naming Conventions
- Category Folders: Named with two digits followed by hyphen and lowercase/title name:
  xx-text (example: 01-world, 02-history, 03-skills, 04-factions)
- Subfolders: Numbered x-x (example: 1-0, 1-1, 1-2)
- Entry Files: Numbered x-x-x (example: 1-0-0.md, 1-0-1.md)
