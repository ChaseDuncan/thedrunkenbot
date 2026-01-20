console.log('Autocomplete script loaded!');

const editor = document.getElementById('lyricEditor');
const suggestionEl = document.getElementById('suggestion');
const statusEl = document.getElementById('status');

console.log('Editor element:', editor);
console.log('Suggestion element:', suggestionEl);
console.log('Status element:', statusEl);

if (!editor || !suggestionEl || !statusEl) {
  console.error('Missing elements!', { editor, suggestionEl, statusEl });
}

let debounceTimer = null;
let currentSuggestion = '';
let isLoading = false;

// Debounced autocomplete trigger
editor.addEventListener('input', () => {
    console.log('Input event fired! Value:', editor.value);
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }

  clearSuggestion();

  const text = editor.value.trim();
    console.log('Text length:', text.length); 
  if (text.length < 10) {
    console.log('Text too short, skipping');
    return;
  }

  setStatus('Waiting...', 'loading');

  debounceTimer = setTimeout(async () => {
    console.log('Debounce timeout, calling fetchSuggestion');
    await fetchSuggestion(text);
  }, 500);
});

async function fetchSuggestion(partialLyric) {
  if (isLoading) return;
  
  isLoading = true;
  setStatus('Thinking...', 'loading');

  try {
    console.log('Fetching suggestion for:', partialLyric);
    
    const response = await fetch('/api/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ partialLyric }),
    });

    console.log('Response status:', response.status);

    const data = await response.json();
    
    console.log('Response data:', data);

    if (!response.ok) {
      throw new Error(data.error || 'Failed to get suggestion');
    }

    currentSuggestion = data.completion;
    displaySuggestion();
    setStatus('');

  } catch (err) {
    console.error('Autocomplete error:', err);
    setStatus(err.message || 'Error getting suggestion', 'error');
  } finally {
    isLoading = false;
  }
}

function displaySuggestion() {
  if (!currentSuggestion) return;
  const currentText = editor.value;
  suggestionEl.textContent = currentText + currentSuggestion;
}

function clearSuggestion() {
  currentSuggestion = '';
  suggestionEl.textContent = '';
}

function acceptSuggestion() {
  if (!currentSuggestion) return;
  
  editor.value += currentSuggestion;
  clearSuggestion();
  setStatus('Accepted', 'success');
  setTimeout(() => setStatus(''), 1500);
  
  editor.focus();
  editor.setSelectionRange(editor.value.length, editor.value.length);
}

async function requestNewSuggestion() {
  const text = editor.value.trim();
  if (text.length < 10) {
    setStatus('Need more text', 'error');
    setTimeout(() => setStatus(''), 2000);
    return;
  }
  
  clearSuggestion();
  await fetchSuggestion(text);
}

function setStatus(message, type = '') {
  statusEl.textContent = message;
  statusEl.className = 'status' + (type ? ' ' + type : '');
}

editor.addEventListener('keydown', (e) => {
  // Shift+Tab for new suggestion
  if (e.key === 'Tab' && e.shiftKey) {
    e.preventDefault();
    requestNewSuggestion();
    return;
  }

  // Tab or Right Arrow to accept suggestion
  if ((e.key === 'Tab' || e.key === 'ArrowRight') && currentSuggestion) {
    e.preventDefault();
    acceptSuggestion();
    return;
  }

  // Escape to dismiss suggestion
  if (e.key === 'Escape') {
    clearSuggestion();
    setStatus('');
  }
});

// Clear suggestion if user moves cursor
editor.addEventListener('click', () => {
  clearSuggestion();
});

console.log('Autocomplete initialized!');