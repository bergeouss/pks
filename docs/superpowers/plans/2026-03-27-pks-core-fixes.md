# PKS Core Functionality Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 4 breaking issues preventing PKS from functioning: Z.ai wrong URL, web scraping blocked, YouTube ingestion fails, Ollama embeddings missing.

**Architecture:** Minimal surgical fixes - update config URL, add User-Agent headers, implement Ollama embedding provider, improve YouTube error handling.

**Tech Stack:** FastAPI, Python 3.11, LangChain, httpx, youtube_transcript_api

---

## File Structure

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/core/config.py` | Modify | Fix Z.ai base URL |
| `backend/app/services/parser_service.py` | Modify | Add User-Agent headers |
| `backend/app/services/embedding_service.py` | Modify | Add Ollama embeddings |
| `backend/app/services/youtube_service.py` | Modify | Better error handling |

---

### Task 1: Fix Z.ai Base URL

**Files:**
- Modify: `backend/app/core/config.py:19`

- [ ] **Step 1: Update Z.ai base URL**

Change line 19 in `config.py`:

```python
# FROM:
ZAI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"

# TO:
ZAI_BASE_URL: str = "https://api.z.ai/api/coding/paas/v4"
```

- [ ] **Step 2: Verify the change**

Run: `grep -n "ZAI_BASE_URL" backend/app/core/config.py`
Expected: Shows the new URL with `api.z.ai`

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/config.py
git commit -m "fix: update Z.ai base URL to api.z.ai endpoint"
```

---

### Task 2: Add User-Agent Headers for Web Scraping

**Files:**
- Modify: `backend/app/services/parser_service.py:22-27`

- [ ] **Step 1: Add User-Agent constant**

Add after imports (line 11):

```python
# Default headers for web scraping to avoid 403 errors
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
```

- [ ] **Step 2: Update fetch_webpage method**

Replace the `fetch_webpage` method (lines 22-47):

```python
async def fetch_webpage(self, url: str) -> str:
    """Fetch and extract text from a webpage"""
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=DEFAULT_HEADERS) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        logger.error(f"Error fetching webpage {url}: {str(e)}")
        raise
```

- [ ] **Step 3: Test URL ingestion manually**

Run: `docker compose restart backend && sleep 5`
Run: `curl -X POST http://localhost:8100/api/v1/ingest -H "Content-Type: application/json" -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'`
Expected: Returns document_id and chunks_count (not 403 error)

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/parser_service.py
git commit -m "fix: add User-Agent headers for web scraping to avoid 403 errors"
```

---

### Task 3: Add Ollama Embeddings Support

**Files:**
- Modify: `backend/app/services/embedding_service.py:14-36`

- [ ] **Step 1: Add Ollama import**

Add at line 2 (after langchain_google_genai import):

```python
from langchain_ollama import OllamaEmbeddings
```

- [ ] **Step 2: Update config.py to support ollama embedding provider**

Update `config.py` line 22 to include ollama:

```python
DEFAULT_EMBEDDING_PROVIDER: Literal["openai", "gemini", "ollama"] = "gemini"
```

- [ ] **Step 3: Update embedding_service.py to handle Ollama**

Replace the `embeddings` property (lines 18-36):

```python
@property
def embeddings(self):
    if self._embeddings is None:
        if self.provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.GEMINI_API_KEY,
            )
            logger.info("Initialized Gemini embeddings (gemini-embedding-001)")
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self._embeddings = OpenAIEmbeddings(
                model=settings.DEFAULT_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
            )
            logger.info(f"Initialized OpenAI embeddings: {settings.DEFAULT_EMBEDDING_MODEL}")
        elif self.provider == "ollama":
            self._embeddings = OllamaEmbeddings(
                model=settings.DEFAULT_EMBEDDING_MODEL or "mxbai-embed-large",
                base_url=settings.OLLAMA_BASE_URL,
            )
            logger.info(f"Initialized Ollama embeddings: {settings.DEFAULT_EMBEDDING_MODEL or 'mxbai-embed-large'}")
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}")
    return self._embeddings
```

- [ ] **Step 4: Update settings route to include ollama embedding models**

Check `backend/app/api/routes/settings.py` - it should already fetch Ollama models. Verify the endpoint returns ollama in the providers list.

- [ ] **Step 5: Test Ollama embeddings**

Run: `curl -X POST http://localhost:8100/api/v1/settings -H "Content-Type: application/json" -d '{"embedding_provider": "ollama", "embedding_model": "mxbai-embed-large"}'`
Expected: Settings updated successfully

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/config.py backend/app/services/embedding_service.py
git commit -m "feat: add Ollama embeddings support"
```

---

### Task 4: Improve YouTube Error Handling

**Files:**
- Modify: `backend/app/services/youtube_service.py:26-41`

- [ ] **Step 1: Add better error handling with fallbacks**

Replace the `get_transcript` method (lines 26-41):

```python
async def get_transcript(self, url: str) -> str:
    """Fetch transcript from YouTube video"""
    try:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")

        # Try to get transcript with multiple language fallbacks
        transcript_list = None
        languages_to_try = ['en', 'en-US', 'en-GB']  # Try English variants first

        for lang in languages_to_try:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                break
            except Exception:
                continue

        # If no English transcript, try to get any available transcript
        if transcript_list is None:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception:
                pass

        if transcript_list is None:
            raise ValueError(f"No transcript available for video: {video_id}")

        transcript_text = "\n".join([entry['text'] for entry in transcript_list])

        logger.info(f"Fetched transcript for video {video_id}")
        return transcript_text

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error fetching YouTube transcript: {str(e)}")
        # Provide more helpful error message
        if "no element found" in str(e).lower():
            raise ValueError(f"Could not fetch transcript for video {video_id}. The video may not have captions, or YouTube may be blocking automated requests. Try a different video or use direct text/file ingestion instead.")
        raise ValueError(f"Failed to fetch YouTube transcript: {str(e)}")
```

- [ ] **Step 2: Test YouTube error handling**

Run: `curl -X POST http://localhost:8100/api/v1/ingest -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'`
Expected: Better error message (not just "no element found")

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/youtube_service.py
git commit -m "fix: improve YouTube transcript error handling with language fallbacks"
```

---

### Task 5: Rebuild and Verify All Fixes

**Files:**
- None (verification only)

- [ ] **Step 1: Rebuild containers**

```bash
docker compose down
docker compose up -d --build
```

- [ ] **Step 2: Verify services are healthy**

Run: `docker compose ps`
Expected: All 4 services running (backend, frontend, qdrant, file-watcher)

- [ ] **Step 3: Test health endpoint**

Run: `curl http://localhost:8100/api/v1/health`
Expected: `{"status": "healthy", "qdrant_connected": true}`

- [ ] **Step 4: Test URL ingestion**

Run: `curl -X POST http://localhost:8100/api/v1/ingest -H "Content-Type: application/json" -d '{"url": "https://example.com"}'`
Expected: Returns document_id and chunks_count

- [ ] **Step 5: Test chat with Ollama (if Z.ai still fails)**

Run: `curl -X POST http://localhost:8100/api/v1/settings -H "Content-Type: application/json" -d '{"llm_provider": "ollama", "llm_model": "llama3.2:1b"}'`
Then: `curl -X POST http://localhost:8100/api/v1/chat -H "Content-Type: application/json" -d '{"query": "hello"}'`
Expected: Response with answer (not 500 error)

---

## Summary

| Issue | Fix | File |
|-------|-----|------|
| Z.ai wrong URL | Update base URL to api.z.ai | config.py |
| Web scraping 403 | Add User-Agent headers | parser_service.py |
| Ollama embeddings missing | Add OllamaEmbeddings support | embedding_service.py |
| YouTube cryptic errors | Better error messages + language fallbacks | youtube_service.py |

**User Action Required:** Add credits to Z.ai account OR switch to Ollama/DeepSeek as LLM provider.