# Firefox User Guide: Disco Elysium Lorebook for Character.ai

This guide provides end-to-end instructions for Mozilla Firefox users to install, synchronize, and operate the Disco Elysium Lorebook and bot engine on [Character.ai](https://character.ai).

---

## 1. Overview and Architecture

The project consists of three core components:
1. **Lorebook Database (125 Entries)**: Located in `Categories/`, containing 125 strictly formatted markdown files (1,800–2,000 characters, plain ASCII, 2–8 keywords, zero markdown formatting, and compliant with Character.ai content policies).
2. **Bot Prompt & Skills Architecture**: Located in `Prompts/CAIBOT.MD` (character definition for the 24 internal Skills and primal subconscious voices) and `Prompts/SCENE.MD` (opening greeting in Martinaise).
3. **Automated Ingestion Pipeline**: Tools in `Scripts/` to batch-upload all 125 entries into a Character.ai Lorebook without manual copy-pasting.

---

## 2. Ingestion Methods for Firefox Users

You can sync the lorebook into Character.ai using either of two methods:

### Method 1: Automated Tampermonkey Sync Bridge (Recommended)

This method uses a local Python HTTP bridge combined with a Tampermonkey userscript to stream entries directly into the Character.ai web interface.

#### Step 1: Install Tampermonkey in Firefox
1. Open Firefox and navigate to the Firefox Add-ons store: [Tampermonkey on AMO](https://addons.mozilla.org/firefox/addon/tampermonkey/).
2. Click **Add to Firefox** and grant permissions.

#### Step 2: Install the Userscript
1. Open the Tampermonkey dashboard in Firefox (click the Tampermonkey icon in the toolbar -> **Dashboard**).
2. Click the **+** (Add a new script) tab or select **Utilities -> Import from file**.
3. Copy the entire contents of [`Scripts/cai_lorebook_tampermonkey.user.js`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/Scripts/cai_lorebook_tampermonkey.user.js) and paste it into the editor.
4. Press `Ctrl+S` to save. Ensure the script is enabled (version 1.4.0+).

#### Step 3: Start the Local Lore Bridge
Open a terminal in the project directory and run:
```bash
python3 Scripts/lore_server.py
```
The server will start listening on `http://127.0.0.1:8765`.

#### Step 4: Firefox Permission & Security Guard
When you first open Character.ai with the userscript active:
1. Navigate to your Lorebook editor: `https://character.ai/lorebooks/<your-lorebook-id>`
2. A floating widget titled **"C.AI Lore Sync"** will appear in the top-right corner.
3. Tampermonkey will display an authorization banner requesting access to connect to `127.0.0.1:8765`.
4. **Click "Always allow domain"**.
   - *Technical Note*: Tampermonkey bypasses Firefox's strict mixed-content and CORS restrictions by routing requests via `GM_xmlhttpRequest`.

#### Step 5: Run the Sync
1. Click **Start Sync** on the floating widget.
2. The script will:
   - Query `http://127.0.0.1:8765/api/entries`.
   - Skip any entries already marked `done` in `POS/UPLOAD-POSITIONS.json`.
   - Automatically click `+ Add a new entry`, populate the Title and Content, create individual keyword chips via `+ New keyword`, and record completion.
   - Automatically click **Save / Update** once all entries are populated.
3. You can pause or resume at any time.

---

### Method 2: Firefox Web Console Injector (Zero-Extension Fallback)

If you prefer not to use Tampermonkey, you can execute the self-contained JavaScript bundle directly in Firefox's Web Console.

#### Step 1: Generate the Bundle
Run the builder script in terminal:
```bash
python3 Scripts/build_lorebook_payload.py
```
This generates the standalone script [`Scripts/inject_cai_lorebook.js`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/Scripts/inject_cai_lorebook.js) with all pending entries embedded.

#### Step 2: Firefox "Allow Pasting" Guard
1. Navigate to your Lorebook page: `https://character.ai/lorebooks/<your-lorebook-id>`.
2. Open the Firefox Developer Tools by pressing `F12` (or `Ctrl+Shift+K`).
3. Switch to the **Console** tab.
4. **Firefox Security Guard**: Firefox protects users by blocking script pasting in the console by default. If prompted with a warning:
   - Type `allow pasting` into the console prompt and hit `Enter`.
   - Script pasting is now unlocked for this Firefox tab.

#### Step 3: Paste and Execute
1. Open [`Scripts/inject_cai_lorebook.js`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/Scripts/inject_cai_lorebook.js) in your text editor.
2. Select all (`Ctrl+A`) and copy (`Ctrl+C`).
3. Paste into the Firefox Console and press `Enter`.
4. Watch the console log real-time progress as each entry is added and saved.

---

### Method 3: Manual Entry Guidelines (If Adding Entries Manually)

If pasting entries into Character.ai by hand:
- **Zero Leading Spaces/Tabs**: Ensure every line is flush-left (starts at column 0). Do not include leading indentation or blockquote syntax (`> `).
- **Exact Field Mapping**:
  - `Title`: Use the plain title text (e.g., `Canon`).
  - `Content / Text`: Paste the body text without asterisks, markdown headers, or double hyphens.
  - `Keywords`: Add each keyword individually as a chip.
- **Content Policy Guard**: Character.ai strictly filters entries containing terms related to self-harm, suicide, or minors placed in abusive or traumatic settings. All entries in this repository have been pre-screened and sanitized against these triggers.

---

## 3. Configuring the Character.ai Bot

To pair the lorebook with the official bot persona:

1. **Character Name**: Disco Elysium / Revachol Engine
2. **Short Description**:
   ```
   The 24 internal Skills, primal subconscious voices, and living world of Revachol in Year '51.
   ```
3. **Greeting (First Message)**:
   - Open [`Prompts/SCENE.MD`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/Prompts/SCENE.MD).
   - Copy the text (1,992 characters) and paste directly into the Character.ai **Greeting** box.
4. **Character Definition (Advanced)**:
   - Open [`Prompts/CAIBOT.MD`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/Prompts/CAIBOT.MD).
   - Copy the entire contents (25,353 characters, under the 32k Character.ai limit).
   - Paste into the Character.ai **Definition** box.
5. **Attach Lorebook**:
   - In character settings, link your synced lorebook (`ad0d6c50-5dde-4074-b6a9-0973fa4a4f83` or your own ID).

---

## 4. State Management and Troubleshooting

### Sync State File
Upload progress is tracked in [`POS/UPLOAD-POSITIONS.json`](file:///home/jules/Documents/Programming/DiscoElysium-Lorebook/POS/UPLOAD-POSITIONS.json):
- `uploaded_files`: Array of successfully uploaded file paths.
- `pending_files`: Array of remaining files to upload.
- `total_entries`: 125.

### Resetting Progress
To clear upload tracking and force a full re-sync from entry 1:
```bash
curl -X POST http://127.0.0.1:8765/api/reset
```
Or delete `POS/UPLOAD-POSITIONS.json` and re-run:
```bash
python3 Scripts/build_lorebook_payload.py
```

### Checking Local Bridge Status
To test if the Python server is responding:
```bash
curl -s http://127.0.0.1:8765/api/entries | jq '{total: (.entries | length), pending: ([.[] | select(.done == false)] | length)}'
```

### Port Conflict (Port 8765 in use)
If port 8765 is occupied, terminate any running server instances:
```bash
pkill -f "python3 Scripts/lore_server.py"
```
Then restart the server.
