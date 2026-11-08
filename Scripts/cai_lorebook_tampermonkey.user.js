// ==UserScript==
// @name         Character.ai Lorebook Auto-Sync
// @namespace    https://github.com/AdaLEX-dev/Disco
// @version      1.2.0
// @description  Automated lorebook note sync inside Character.ai with Test (2 entries) & Reset Progress buttons.
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

  // Robustly commits a keyword tag to React/C.ai chip inputs
  async function insertKeywordTag(inputElement, keyword) {
    inputElement.focus();
    await sleep(50);

    setNativeValue(inputElement, keyword);
    await sleep(100);

    // Sequence of keyboard events (Enter, Comma, Tab)
    const keyConfigs = [
      { key: 'Enter', code: 'Enter', keyCode: 13, which: 13 },
      { key: ',', code: 'Comma', keyCode: 188, which: 188 },
      { key: 'Tab', code: 'Tab', keyCode: 9, which: 9 }
    ];

    for (const conf of keyConfigs) {
      inputElement.dispatchEvent(new KeyboardEvent('keydown', { ...conf, bubbles: true, cancelable: true }));
      inputElement.dispatchEvent(new KeyboardEvent('keypress', { ...conf, bubbles: true, cancelable: true }));
      inputElement.dispatchEvent(new KeyboardEvent('keyup', { ...conf, bubbles: true, cancelable: true }));
      await sleep(80);
      if (inputElement.value === '') break;
    }

    // Check adjacent Add button
    const parentContainer = inputElement.closest('div, form, section') || inputElement.parentElement;
    if (parentContainer) {
      const addKeywordBtn = Array.from(parentContainer.querySelectorAll('button, span[role="button"]')).find(b => {
        const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
        return txt === 'add' || txt === '+' || txt.includes('add keyword');
      });
      if (addKeywordBtn) {
        addKeywordBtn.click();
        await sleep(100);
      }
    }
  }

  // Helper to execute single note submission
  async function submitNoteEntry(item) {
    // 0. Add a new entry
    let addBtn = findElementByText('button, div[role="button"], span', 'Add a new entry') 
              || findElementByText('button, div[role="button"], span', 'Add entry')
              || findElementByText('button, div[role="button"], span', 'New note');

    if (addBtn) {
      addBtn.click();
      await sleep(700);
    }

    // 1. Title
    const allInputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
    const titleInput = allInputs.find(inp => {
      const p = (inp.placeholder || '').toLowerCase();
      const a = (inp.getAttribute('aria-label') || '').toLowerCase();
      return p.includes('title') || a.includes('title') || (inp.name && inp.name.includes('title'));
    }) || allInputs[0];

    if (titleInput) {
      setNativeValue(titleInput, item.title);
      await sleep(300);
    }

    // 2. Content
    const allTextareas = Array.from(document.querySelectorAll('textarea'));
    const contentTextarea = allTextareas.find(ta => {
      const p = (ta.placeholder || '').toLowerCase();
      const a = (ta.getAttribute('aria-label') || '').toLowerCase();
      return p.includes('content') || p.includes('text') || a.includes('content');
    }) || allTextareas[0];

    if (contentTextarea) {
      setNativeValue(contentTextarea, item.text);
      await sleep(400);
    }

    // 3. Keywords
    const currentInputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
    let keywordInput = currentInputs.find(inp => {
      if (inp === titleInput) return false;
      const p = (inp.placeholder || '').toLowerCase();
      const a = (inp.getAttribute('aria-label') || '').toLowerCase();
      const n = (inp.name || '').toLowerCase();
      const id = (inp.id || '').toLowerCase();
      return p.includes('keyword') || a.includes('keyword') || n.includes('keyword') || id.includes('keyword');
    });

    if (!keywordInput) {
      const kwLabel = findElementByText('label, div, span, p', 'Keyword') || findElementByText('label, div, span, p', 'Keywords');
      if (kwLabel) {
        const container = kwLabel.closest('div, section') || kwLabel.parentElement;
        if (container) keywordInput = container.querySelector('input');
      }
    }

    if (!keywordInput) {
      keywordInput = currentInputs.find(inp => inp !== titleInput);
    }

    if (keywordInput && item.keywords && item.keywords.length > 0) {
      for (const kw of item.keywords) {
        await insertKeywordTag(keywordInput, kw);
        await sleep(200);
      }
    }

    await sleep(500);

    // 4. Update / Save
    let saveBtn = findElementByText('button, div[role="button"]', 'Update')
               || findElementByText('button, div[role="button"]', 'Save')
               || findElementByText('button, div[role="button"]', 'Save changes');

    if (saveBtn) {
      saveBtn.click();
      await sleep(1500);
      return true;
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
          infoText.innerText = 'Could not reach server to reset. Check: python3 Scripts/lore_server.py';
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
