// Content script for PKS Saver extension
// This script runs in the context of web pages to extract content

// Extract main content from the page
function extractPageContent() {
  // Try to find the main content area
  const contentSelectors = [
    'article',
    'main',
    '[role="main"]',
    '#content',
    '.content',
    '.post-content',
    '.article-content',
    'body'
  ];

  let contentElement = null;
  for (const selector of contentSelectors) {
    contentElement = document.querySelector(selector);
    if (contentElement) {
      // Make sure we have actual content
      const text = contentElement.innerText || contentElement.textContent;
      if (text && text.trim().length > 100) {
        break;
      }
    }
  }

  // Fallback to body if nothing found
  if (!contentElement) {
    contentElement = document.body;
  }

  // Extract and clean text content
  let text = contentElement ? (contentElement.innerText || contentElement.textContent || '') : '';

  // Clean up the text
  text = text
    .replace(/\s+/g, ' ')  // Normalize whitespace
    .replace(/\n\s*\n/g, '\n\n')  // Normalize line breaks
    .trim();

  return {
    title: document.title,
    url: window.location.href,
    content: text,
    author: extractAuthor(),
    description: extractDescription(),
  };
}

// Extract author metadata
function extractAuthor() {
  const authorSelectors = [
    'meta[name="author"]',
    'meta[property="author"]',
    'meta[name="dc.creator"]',
    '[rel="author"]',
    '.author',
    '.byline',
  ];

  for (const selector of authorSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      const content = element.getAttribute('content') || element.textContent;
      if (content && content.trim()) {
        return content.trim();
      }
    }
  }

  return null;
}

// Extract description metadata
function extractDescription() {
  const descSelectors = [
    'meta[name="description"]',
    'meta[property="og:description"]',
    'meta[name="twitter:description"]',
  ];

  for (const selector of descSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      const content = element.getAttribute('content');
      if (content && content.trim()) {
        return content.trim();
      }
    }
  }

  return null;
}

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getContent') {
    const content = extractPageContent();
    sendResponse({ success: true, data: content });
  }
  return true;
});

// Log that content script is loaded
console.log('PKS Saver content script loaded');
