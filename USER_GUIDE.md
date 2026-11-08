# User Guide: Disco Elysium Lorebook for Character.ai

For full Firefox-specific instructions, security guards, Tampermonkey bridge setup, and Web Console tips, see:
- [`FIREFOX_USER_GUIDE.md`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/FIREFOX_USER_GUIDE.md)

---

## Quick Reference Summary

1. **Total Entries**: 125 entries (strictly under the Character.ai 128-entry budget).
2. **Directory Structure**:
   - `Categories/Canon.MD`: Foundational in-universe canon and simulation boundaries.
   - `Categories/01. Location/` through `Categories/09. Creatures/`: Complete lore database.
   - `Prompts/CAIBOT.MD`: Master Character Definition (24 internal Skills, primal voices, crosstalk syntax).
   - `Prompts/SCENE.MD`: Master Greeting (Martinaise crater opening).
   - `Scripts/`: Tampermonkey userscript (`cai_lorebook_tampermonkey.user.js`), Python bridge server (`lore_server.py`), and DOM injector (`inject_cai_lorebook.js`).
3. **Sync Automation**:
   - Start local bridge: `python3 Scripts/lore_server.py`
   - Install Tampermonkey userscript: `Scripts/cai_lorebook_tampermonkey.user.js`
   - Navigate to `https://character.ai/lorebooks/<id>` in Firefox and click **Start Sync**.
