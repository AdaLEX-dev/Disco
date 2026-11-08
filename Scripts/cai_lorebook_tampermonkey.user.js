// ==UserScript==
// @name         Character.ai Lorebook Auto-Sync
// @namespace    https://github.com/AdaLEX-dev/Disco
// @version      1.1.0
// @description  Automated, robust lorebook note sync directly inside Character.ai with robust keyword entry.
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

    // 1. Dispatch clipboard/paste event simulation or direct input
    setNativeValue(inputElement, keyword);
    await sleep(100);

    // 2. Dispatch sequence of keyboard events that trigger tag creation (Enter, Tab, Comma)
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
      // Check if input was cleared (indicating tag was successfully created)
      if (inputElement.value === '') {
        break;
      }
    }

    // 3. Check for any explicit "Add" button right next to the keyword input
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
      width: 280px;
    `;

    panel.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <strong style="color:#89b4fa; font-size:14px;">Disco Elysium Lore Sync</strong>
        <span id="cai-sync-status-badge" style="background:#313244; padding:2px 8px; border-radius:6px; font-size:11px; color:#a6adc8;">Idle</span>
      </div>
      <div id="cai-sync-info" style="margin-bottom:12px; font-size:12px; color:#bac2de; line-height:1.4;">
        Connect to local server or load payload.
      </div>
      <div style="display:flex; gap:8px;">
        <button id="cai-sync-start-btn" style="flex:1; background:#a6e3a1; color:#11111b; border:none; border-radius:6px; padding:8px 12px; font-weight:bold; cursor:pointer;">
          Start Sync
        </button>
        <button id="cai-sync-stop-btn" style="background:#f38ba8; color:#11111b; border:none; border-radius:6px; padding:8px 12px; font-weight:bold; cursor:pointer; display:none;">
          Stop
        </button>
      </div>
      <div id="cai-sync-progress" style="margin-top:10px; font-size:11px; color:#9399b2; word-break:break-all;"></div>
    `;

    document.body.appendChild(panel);

    const startBtn = document.getElementById('cai-sync-start-btn');
    const stopBtn = document.getElementById('cai-sync-stop-btn');
    const statusBadge = document.getElementById('cai-sync-status-badge');
    const infoText = document.getElementById('cai-sync-info');
    const progressText = document.getElementById('cai-sync-progress');

    let isRunning = false;

    stopBtn.onclick = () => {
      isRunning = false;
      stopBtn.style.display = 'none';
      startBtn.style.display = 'block';
      statusBadge.innerText = 'Stopped';
      statusBadge.style.background = '#f38ba8';
      statusBadge.style.color = '#11111b';
    };

    startBtn.onclick = async () => {
      statusBadge.innerText = 'Connecting...';
      infoText.innerText = 'Fetching pending entries from local repository...';

      GM_xmlhttpRequest({
        method: 'GET',
        url: 'http://127.0.0.1:8765/api/entries',
        onload: async function(response) {
          if (response.status !== 200) {
            infoText.innerText = 'Error: Run python3 Scripts/lore_server.py first!';
            statusBadge.innerText = 'Server Offline';
            return;
          }

          let data;
          try {
            data = JSON.parse(response.responseText);
          } catch(e) {
            infoText.innerText = 'Invalid response from local server.';
            return;
          }

          const pending = data.entries.filter(e => !e.done);
          if (pending.length === 0) {
            infoText.innerText = `All ${data.entries.length} entries are already synced!`;
            statusBadge.innerText = 'Up to date';
            return;
          }

          isRunning = true;
          startBtn.style.display = 'none';
          stopBtn.style.display = 'block';
          statusBadge.innerText = 'Syncing...';
          statusBadge.style.background = '#89b4fa';
          statusBadge.style.color = '#11111b';

          for (let i = 0; i < pending.length; i++) {
            if (!isRunning) break;
            const item = pending[i];
            infoText.innerText = `Syncing [${i + 1}/${pending.length}]:\n"${item.title}"`;
            progressText.innerText = item.file;

            // Step 0: Click "Add a new entry"
            let addBtn = findElementByText('button, div[role="button"], span', 'Add a new entry') 
                      || findElementByText('button, div[role="button"], span', 'Add entry')
                      || findElementByText('button, div[role="button"], span', 'New note');

            if (addBtn) {
              addBtn.click();
              await sleep(700);
            }

            // Step 1: Set Title
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

            // Step 2: Set Content
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

            // Step 3: Find and Insert Keywords
            // Find keyword input: either explicit placeholder/aria, or input near a "Keywords" label
            const currentInputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
            let keywordInput = currentInputs.find(inp => {
              if (inp === titleInput) return false;
              const p = (inp.placeholder || '').toLowerCase();
              const a = (inp.getAttribute('aria-label') || '').toLowerCase();
              const n = (inp.name || '').toLowerCase();
              const id = (inp.id || '').toLowerCase();
              return p.includes('keyword') || a.includes('keyword') || n.includes('keyword') || id.includes('keyword');
            });

            // If not found by attributes, search by parent/label association
            if (!keywordInput) {
              const kwLabel = findElementByText('label, div, span, p', 'Keyword') || findElementByText('label, div, span, p', 'Keywords');
              if (kwLabel) {
                const container = kwLabel.closest('div, section') || kwLabel.parentElement;
                if (container) {
                  keywordInput = container.querySelector('input');
                }
              }
            }

            // Fallback: any text input that is not the title input
            if (!keywordInput) {
              keywordInput = currentInputs.find(inp => inp !== titleInput);
            }

            if (keywordInput && item.keywords && item.keywords.length > 0) {
              console.log(`Adding ${item.keywords.length} keywords to field:`, keywordInput);
              for (const kw of item.keywords) {
                await insertKeywordTag(keywordInput, kw);
                await sleep(250);
              }
            } else {
              console.warn("Could not find keyword input element on page!");
            }

            await sleep(500);

            // Step 4: Click Update / Save button
            let saveBtn = findElementByText('button, div[role="button"]', 'Update')
                       || findElementByText('button, div[role="button"]', 'Save')
                       || findElementByText('button, div[role="button"]', 'Save changes');

            if (saveBtn) {
              saveBtn.click();
              await sleep(1400);

              // Notify local server that this file was successfully uploaded
              GM_xmlhttpRequest({
                method: 'POST',
                url: 'http://127.0.0.1:8765/api/mark_done',
                data: JSON.stringify({ file: item.file }),
                headers: { 'Content-Type': 'application/json' }
              });
            } else {
              console.warn("Could not find Update/Save button.");
            }
          }

          if (isRunning) {
            infoText.innerText = 'Sync completed successfully!';
            statusBadge.innerText = 'Completed';
            statusBadge.style.background = '#a6e3a1';
            stopBtn.style.display = 'none';
            startBtn.style.display = 'block';
          }
        },
        onerror: function() {
          infoText.innerText = 'Could not reach local server. Start: python3 Scripts/lore_server.py';
          statusBadge.innerText = 'Offline';
          statusBadge.style.background = '#f38ba8';
        }
      });
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createControlPanel);
  } else {
    setTimeout(createControlPanel, 1500);
  }
})();
