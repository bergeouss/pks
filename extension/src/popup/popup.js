// Get the active tab
let currentTab = null;

// Initialize popup
async function init() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTab = tab;

    if (tab) {
      document.getElementById('pageTitle').textContent = tab.title || 'Untitled Page';
      document.getElementById('pageUrl').textContent = tab.url || '';
    }
  } catch (error) {
    console.error('Error getting tab info:', error);
    showStatus('Error loading page info', 'error');
  }
}

// Show status message
function showStatus(message, type = 'loading') {
  const statusEl = document.getElementById('status');
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.style.display = 'block';

  if (type === 'success') {
    setTimeout(() => {
      statusEl.style.display = 'none';
    }, 3000);
  }
}

// Save page to PKS
async function saveToPKS() {
  if (!currentTab || !currentTab.url) {
    showStatus('No page to save', 'error');
    return;
  }

  const saveBtn = document.getElementById('saveBtn');
  saveBtn.disabled = true;
  showStatus('Saving...', 'loading');

  try {
    const response = await fetch('http://localhost:8100/api/v1/ingest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: currentTab.url,
        metadata: {
          title: currentTab.title,
          timestamp: new Date().toISOString(),
          source: 'browser-extension'
        }
      })
    });

    if (response.ok) {
      const result = await response.json();
      console.log('Saved successfully:', result);
      showStatus(`✓ Saved! (${result.chunks_count} chunks)`, 'success');
    } else {
      const error = await response.json();
      console.error('Save failed:', error);
      showStatus(`✗ Failed: ${error.detail || 'Unknown error'}`, 'error');
    }
  } catch (error) {
    console.error('Error saving:', error);
    showStatus('✗ Failed to connect to PKS backend', 'error');
  } finally {
    saveBtn.disabled = false;
  }
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
  init();
  document.getElementById('saveBtn').addEventListener('click', saveToPKS);
});
