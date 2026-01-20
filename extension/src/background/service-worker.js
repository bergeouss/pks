// Background service worker for PKS Saver extension

// Keep service worker alive
const KEEP_ALIVE_INTERVAL = 20 * 1000; // 20 seconds

// Keep alive function to prevent service worker from being suspended
function keepAlive() {
  // Set up alarm to keep service worker alive
  chrome.alarms.create('keepAlive', { delayInMinutes: 1 });
}

// Listen for alarm events
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    keepAlive();
  }
});

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('PKS Saver extension installed');
  keepAlive();
});

// Listen for extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log('PKS Saver extension started');
  keepAlive();
});

// Keep alive when service worker starts
keepAlive();

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'savePage') {
    // Handle page save requests
    sendResponse({ status: 'received' });
  }
  return true; // Keep message channel open for async response
});
