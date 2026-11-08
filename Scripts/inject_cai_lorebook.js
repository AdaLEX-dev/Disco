// Character.ai Lorebook Automation Injector
// Target URL: https://character.ai/lorebooks/ad0d6c50-5dde-4074-b6a9-0973fa4a4f83
(async function() {
  const ENTRIES = [];
  
  console.log("%c[C.AI Lorebook Loader] Starting automated ingestion...", "color: #10b981; font-weight: bold; font-size: 14px;");

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
    const event = new Event('input', { bubbles: true });
    const changeEvent = new Event('change', { bubbles: true });
    const tracker = element._valueTracker;
    if (tracker) {
      tracker.setValue(lastValue);
    }
    element.dispatchEvent(event);
    element.dispatchEvent(changeEvent);
  }

  const pendingEntries = ENTRIES.filter(e => !e.done);
  console.log(`Found ${pendingEntries.length} pending entries to upload.`);

  for (let i = 0; i < pendingEntries.length; i++) {
    const item = pendingEntries[i];
    console.log(`\n[%c${i + 1}/${pendingEntries.length}%c] Processing: "${item.title}" (${item.file})`, "color: #3b82f6; font-weight: bold;", "");

    // 0. Locate and click "Add a new entry" or "New Note"
    let addBtn = findElementByText('button, div[role="button"], span', 'Add a new entry') 
              || findElementByText('button, div[role="button"], span', 'Add entry')
              || findElementByText('button, div[role="button"], span', 'New note');

    if (addBtn) {
      addBtn.click();
      await sleep(700);
    }

    // 1. Locate Title Field
    const inputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
    const titleInput = inputs.find(inp => {
      const placeholder = (inp.placeholder || '').toLowerCase();
      const aria = (inp.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('title') || aria.includes('title') || inp.name.includes('title');
    }) || inputs[0];

    if (titleInput) {
      setNativeValue(titleInput, item.title);
      await sleep(300);
    } else {
      console.warn("Could not find Title input field.");
    }

    // 2. Locate Content / Text field
    const textareas = Array.from(document.querySelectorAll('textarea'));
    const contentTextarea = textareas.find(ta => {
      const placeholder = (ta.placeholder || '').toLowerCase();
      const aria = (ta.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('content') || placeholder.includes('text') || aria.includes('content');
    }) || textareas[0];

    if (contentTextarea) {
      setNativeValue(contentTextarea, item.text);
      await sleep(400);
    } else {
      console.warn("Could not find Content textarea field.");
    }

    // 3. Locate Keywords Field & Add Keywords
    const keywordInput = inputs.find(inp => {
      const placeholder = (inp.placeholder || '').toLowerCase();
      const aria = (inp.getAttribute('aria-label') || '').toLowerCase();
      return placeholder.includes('keyword') || aria.includes('keyword');
    });

    if (keywordInput && item.keywords && item.keywords.length > 0) {
      for (const kw of item.keywords) {
        keywordInput.focus();
        setNativeValue(keywordInput, kw);
        await sleep(150);
        keywordInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
        keywordInput.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
        await sleep(200);
      }
    }

    // 4. Click Update / Save button
    let saveBtn = findElementByText('button, div[role="button"]', 'Update')
               || findElementByText('button, div[role="button"]', 'Save')
               || findElementByText('button, div[role="button"]', 'Save changes');

    if (saveBtn) {
      saveBtn.click();
      console.log(`%c✔ Saved "${item.title}"`, "color: #10b981;");
      await sleep(1200);
    } else {
      console.error("Could not find Update/Save button.");
    }
  }

  console.log("%c[C.AI Lorebook Loader] Batch ingestion finished.", "color: #10b981; font-weight: bold; font-size: 14px;");
})();
