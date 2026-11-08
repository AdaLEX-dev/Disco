// ==UserScript==
// @name         Character.ai Lorebook Auto-Sync
// @namespace    https://github.com/AdaLEX-dev/Disco
// @version      1.3.0
// @description  Automated lorebook note sync with exact "+ New keyword" button interaction.
// @author       DiscoElysium-Lorebook
// @match        https://character.ai/lorebooks/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      localhost
// @connect      127.0.0.1
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function findElementByText(selector, textPattern) {
    const elements = Array.from(document.querySelectorAll(selector));
    return elements.find(el => {
      const content = (el.innerText || el.textContent || '').trim().toLowerCase();
      if (typeof textPattern === 'string') {
        return content === textPattern.toLowerCase() || content.includes(textPattern.toLowerCase());
      }
      return textPattern.test(content);
    });
  }

  function setNativeValue(element, value) {
    const lastValue = element.value;
    element.value = value;
    const tracker = element._valueTracker;
    if (tracker) {
      tracker.setValue(lastValue);
    }
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // Exact UI interaction for Character.ai:
  // 1. Click "+ New keyword" button
  // 2. An input appears -> type keyword
  // 3. Click the keyword button / submit again (or Enter) to finalize chip
  async function addKeywordToCai(keyword) {
    // Look for button with "+ New keyword" or "New keyword"
    let newKwBtn = findElementByText('button, div[role="button"], span', 'New keyword')
                || findElementByText('button, div[role="button"], span', '+ New keyword');

    if (!newKwBtn) {
      console.warn("Could not find '+ New keyword' button!");
      return false;
    }

    // Step 1: Click the "+ New keyword" button to open the input
    newKwBtn.click();
    await sleep(250);

    // Step 2: Find the newly created or focused input field
    const activeEl = document.activeElement;
    let kwInput = (activeEl && activeEl.tagName === 'INPUT') ? activeEl : null;

    if (!kwInput) {
      // Find input inside or immediately next to the keywords section
      const allInputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
      // Filter out Title input (usually has large font or 'Untitled entry' / title placeholder)
      kwInput = allInputs.find(inp => {
        const p = (inp.placeholder || '').toLowerCase();
        const a = (inp.getAttribute('aria-label') || '').toLowerCase();
        return p.includes('keyword') || a.includes('keyword') || (!p.includes('title') && inp.value === '');
      }) || allInputs[allInputs.length - 1];
    }

    if (kwInput) {
      kwInput.focus();
      setNativeValue(kwInput, keyword);
      await sleep(150);

      // Dispatch enter
      kwInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
      kwInput.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
      await sleep(150);

      // Step 3: If input still holds value, click "+ New keyword" or container to commit
      if (kwInput.value !== '') {
        if (newKwBtn && document.body.contains(newKwBtn)) {
          newKwBtn.click();
          await sleep(150);
        }
      }
      return true;
    }
    return false;
  }

  // Helper to execute single note submission
  async function submitNoteEntry(item) {
    // 0. Click "Add a new entry"
    let addBtn = findElementByText('button, div[role="button"], span', 'Add a new entry') 
              || findElementByText('button, div[role="button"], span', 'Add entry');

    if (addBtn) {
      addBtn.click();
      await sleep(700);
    }

    // 1. Title: The title in the screenshot is an input or editable heading ("Untitled entry")
    const titleCandidates = Array.from(document.querySelectorAll('input[type="text"], input:not([type]), div[contenteditable="true"]'));
    let titleInput = titleCandidates.find(el => {
      const p = (el.placeholder || '').toLowerCase();
      const v = (el.value || el.innerText || '').toLowerCase();
      return p.includes('title') || v.includes('untitled entry') || p.includes('entry title');
    }) || titleCandidates[0];

    if (titleInput) {
      if (titleInput.tagName === 'INPUT') {
        setNativeValue(titleInput, item.title);
      } else {
        titleInput.innerText = item.title;
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      await sleep(300);
    }

    // 2. Content: The textarea under "Content"
    const contentTextarea = document.querySelector('textarea') 
      || Array.from(document.querySelectorAll('div[contenteditable="true"]')).find(el => el !== titleInput);

    if (contentTextarea) {
      if (contentTextarea.tagName === 'TEXTAREA') {
        setNativeValue(contentTextarea, item.text);
      } else {
        contentTextarea.innerText = item.text;
        contentTextarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
      await sleep(400);
    }

    // 3. Keywords: Click "+ New keyword", type, and commit for each keyword
    if (item.keywords && item.keywords.length > 0) {
      console.log(`Injecting ${item.keywords.length} keywords for "${item.title}"...`);
      for (const kw of item.keywords) {
        await addKeywordToCai(kw);
        await sleep(300);
      }
    }

    await sleep(500);

    // 4. Update / Save button (top right of page as seen in screenshot: "Update" with gear icon)
    let saveBtn = findElementByText('button, div[role="button"]', 'Update')
               || Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('Up'));

    if (saveBtn) {
      saveBtn.click();
      await sleep(1500);
      return true;
    } else {
      console.warn("Could not find Update button.");
    }
    return false;
  }

  // --- UI Floating Panel ---
  function createControlPanel() {
    if (document.getElementById('cai-lore-sync-panel')) return;

    const panel = document.createElement('div');
    panel.id = 'cai-lore-sync-panel';
    panel.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 999999;
      background: #1e1e2e;
      color: #cdd6f4;
      border: 1px solid #45475a;
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 13px;
      width: 300px;
    `;

    panel.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <strong style="color:#89b4fa; font-size:14px;">Disco Elysium Lore Sync</strong>
        <span id="cai-sync-status-badge" style="background:#313244; padding:2px 8px; border-radius:6px; font-size:11px; color:#a6adc8;">Idle</span>
      </div>
      <div id="cai-sync-info" style="margin-bottom:12px; font-size:12px; color:#bac2de; line-height:1.4;">
        Tampermonkey bridge ready.
      </div>
      <div style="display:flex; gap:6px; margin-bottom:8px;">
        <button id="cai-sync-start-btn" style="flex:1; background:#a6e3a1; color:#11111b; border:none; border-radius:6px; padding:7px 10px; font-weight:bold; cursor:pointer;">
          Start Sync
        </button>
        <button id="cai-sync-test-btn" style="flex:1; background:#f9e2af; color:#11111b; border:none; border-radius:6px; padding:7px 10px; font-weight:bold; cursor:pointer;">
          Test (2)
        </button>
        <button id="cai-sync-stop-btn" style="background:#f38ba8; color:#11111b; border:none; border-radius:6px; padding:7px 10px; font-weight:bold; cursor:pointer; display:none;">
          Stop
        </button>
      </div>
      <div style="display:flex;">
        <button id="cai-sync-reset-btn" style="flex:1; background:#313244; color:#f38ba8; border:1px solid #45475a; border-radius:6px; padding:6px 10px; font-size:11px; cursor:pointer;">
          Reset Progress (Clear)
        </button>
      </div>
      <div id="cai-sync-progress" style="margin-top:10px; font-size:11px; color:#9399b2; word-break:break-all;"></div>
    `;

    document.body.appendChild(panel);

    const startBtn = document.getElementById('cai-sync-start-btn');
    const testBtn = document.getElementById('cai-sync-test-btn');
    const stopBtn = document.getElementById('cai-sync-stop-btn');
    const resetBtn = document.getElementById('cai-sync-reset-btn');
    const statusBadge = document.getElementById('cai-sync-status-badge');
    const infoText = document.getElementById('cai-sync-info');
    const progressText = document.getElementById('cai-sync-progress');

    let isRunning = false;

    // Reset Progress
    resetBtn.onclick = () => {
      GM_xmlhttpRequest({
        method: 'POST',
        url: 'http://127.0.0.1:8765/api/reset',
        onload: function() {
          infoText.innerText = 'Progression tracker reset to empty!';
          statusBadge.innerText = 'Reset Done';
          statusBadge.style.background = '#89b4fa';
          statusBadge.style.color = '#11111b';
          progressText.innerText = '';
        },
        onerror: function() {
          infoText.innerText = 'Could not reach server. Start: python3 Scripts/lore_server.py';
        }
      });
    };

    // Stop execution
    stopBtn.onclick = () => {
      isRunning = false;
      stopBtn.style.display = 'none';
      startBtn.style.display = 'block';
      testBtn.style.display = 'block';
      statusBadge.innerText = 'Stopped';
      statusBadge.style.background = '#f38ba8';
      statusBadge.style.color = '#11111b';
    };

    // Runner function
    async function runBatch(maxCount = null) {
      statusBadge.innerText = 'Connecting...';
      infoText.innerText = 'Fetching entries from local repository...';

      GM_xmlhttpRequest({
        method: 'GET',
        url: 'http://127.0.0.1:8765/api/entries',
        onload: async function(response) {
          if (response.status !== 200) {
            infoText.innerText = 'Error: Run python3 Scripts/lore_server.py first!';
            statusBadge.innerText = 'Server Offline';
            return;
          }

          let data = JSON.parse(response.responseText);
          let pending = data.entries.filter(e => !e.done);
          if (maxCount) {
            pending = pending.slice(0, maxCount);
          }

          if (pending.length === 0) {
            infoText.innerText = 'No pending entries to sync!';
            statusBadge.innerText = 'Up to date';
            return;
          }

          isRunning = true;
          startBtn.style.display = 'none';
          testBtn.style.display = 'none';
          stopBtn.style.display = 'block';
          statusBadge.innerText = maxCount ? 'Testing...' : 'Syncing...';
          statusBadge.style.background = maxCount ? '#f9e2af' : '#89b4fa';
          statusBadge.style.color = '#11111b';

          for (let i = 0; i < pending.length; i++) {
            if (!isRunning) break;
            const item = pending[i];
            infoText.innerText = `[${i + 1}/${pending.length}]:\n"${item.title}"`;
            progressText.innerText = `${item.keywords.length} keywords: ${item.keywords.join(', ')}`;

            const success = await submitNoteEntry(item);
            if (success) {
              GM_xmlhttpRequest({
                method: 'POST',
                url: 'http://127.0.0.1:8765/api/mark_done',
                data: JSON.stringify({ file: item.file }),
                headers: { 'Content-Type': 'application/json' }
              });
            }
          }

          if (isRunning) {
            infoText.innerText = maxCount ? 'Test (2 entries) complete!' : 'All sync completed!';
            statusBadge.innerText = 'Done';
            statusBadge.style.background = '#a6e3a1';
            stopBtn.style.display = 'none';
            startBtn.style.display = 'block';
            testBtn.style.display = 'block';
          }
        },
        onerror: function() {
          infoText.innerText = 'Server offline. Start: python3 Scripts/lore_server.py';
          statusBadge.innerText = 'Offline';
          statusBadge.style.background = '#f38ba8';
        }
      });
    }

    startBtn.onclick = () => runBatch(null);
    testBtn.onclick = () => runBatch(2);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createControlPanel);
  } else {
    setTimeout(createControlPanel, 1500);
  }
})();
