# Personal Knowledge Synthesizer (PKS)

A self-hosted, Docker-based personal knowledge management system with RAG-powered AI chat interface.

## Features

- **Multi-source ingestion**: Web pages (browser extension), documents (PDF, DOCX, TXT), YouTube transcripts, file watcher
- **Semantic search**: Vector embeddings powered by Qdrant
- **RAG-powered chat**: AI assistant with source citations
- **Multi-provider AI**: OpenAI, DeepSeek, Anthropic, Ollama, Z.ai (GLM) support
- **Multi-provider embeddings**: OpenAI, Google Gemini support
- **Privacy-first**: Self-hosted, no data leaves your infrastructure

## Tech Stack

- **Backend**: FastAPI + Python 3.11 + LangChain
- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Vector DB**: Qdrant
- **Deployment**: Docker Compose
- **Browser Extension**: Chrome/Firefox (Manifest V3)
- **File Watcher**: Python watchdog with automatic ingestion

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (replace with your actual repository URL)
git clone https://github.com/yourusername/pks.git
cd pks
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Services

```bash
docker compose up -d --build
```

Services will be available at:
- **Frontend**: http://localhost:3100
- **Backend API**: http://localhost:8100
- **API Docs**: http://localhost:8100/docs
- **Qdrant Console**: http://localhost:7333/dashboard

**Port Mappings:**
| Service | Internal Port | External Port |
|---------|---------------|---------------|
| Frontend | 3000 | 3100 |
| Backend | 8000 | 8100 |
| Qdrant | 6333/6334 | 7333/7334 |

### 3. Configure API Keys

Edit `.env` and add at least one LLM provider key:

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=sk-...              # For GPT models
DEEPSEEK_API_KEY=...               # For DeepSeek models
ANTHROPIC_API_KEY=sk-ant-...       # For Claude models
ZAI_API_KEY=...                    # For Zhipu GLM models

# Required: Embedding provider
GEMINI_API_KEY=...                 # For embeddings (recommended)

# Optional: Defaults (see below)
```

### 4. Ingest Content

**Option 1: Browser Extension** (Recommended)

1. Load the extension in Chrome/Edge:
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `extension/` directory from the PKS project

2. Load the extension in Firefox:
   - Navigate to `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select `extension/manifest.json` from the PKS project

3. Navigate to any webpage and click the PKS extension icon
4. Click "Save to PKS"

**Option 2: File Watcher**
```bash
# Drop files in the watched directory
cp mydocument.txt data/inbox/
# File watcher will automatically process and ingest
```

**Option 3: Direct API**
```bash
curl -X POST http://localhost:8100/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### 5. Chat with Your Knowledge

Access the chat interface at http://localhost:3100/chat

## Browser Extension

The PKS Saver browser extension allows you to save web pages directly from your browser.

### Installation

**Chrome/Edge:**
1. Navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension/` directory from the PKS project

**Firefox:**
1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `extension/manifest.json` from the PKS project

### Permissions

The extension requires:
- `activeTab` - Access to the current tab's content
- `scripting` - Inject content scripts for page extraction
- Host permission for `http://localhost:8100/*` - Communication with PKS backend

### Usage

1. Navigate to any webpage you want to save
2. Click the PKS Saver extension icon in your browser toolbar
3. Review the page title and URL
4. Click "Save to PKS"
5. The page content will be extracted and ingested into your knowledge base

## File Watcher

The file watcher service monitors `data/inbox/` for new files and automatically ingests them.

### Supported File Types

| Extension | Description | Status |
|-----------|-------------|--------|
| `.txt` | Plain text files | Supported |
| `.md` | Markdown files | Supported |
| `.pdf` | PDF documents | Supported |
| `.docx` | Word documents | Planned |
| `.html` | Saved web pages | Supported |

### Usage

```bash
# Simply copy files to the inbox directory
cp mydocument.txt data/inbox/

# The file watcher will:
# 1. Detect the new file
# 2. Send it to the backend for processing
# 3. Move it to data/processed/ when done
```

### Troubleshooting

If files aren't being processed:

1. Check file watcher logs: `docker compose logs -f file-watcher`
2. Verify file is in correct directory: `ls data/inbox/`
3. Check backend health: `curl http://localhost:8100/api/v1/health`
4. Ensure file type is supported (see table above)

## API Documentation

For complete API documentation with request/response examples, see [docs/API.md](docs/API.md).

### Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/ingest` | Ingest URL/text/file |
| POST | `/api/v1/chat` | Chat with RAG |
| GET | `/api/v1/documents` | List documents |
| DELETE | `/api/v1/documents/:id` | Delete document |
| GET | `/api/v1/health` | Health check |

Interactive API documentation is available at http://localhost:8100/docs when the backend is running.

## Configuration

Environment variables (create from `.env.example`):

### LLM Providers (at least one required)

```bash
# OpenAI (GPT-4, GPT-3.5)
OPENAI_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Z.ai (Zhipu GLM models)
ZAI_API_KEY=...
ZAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### Embedding Providers (required)

```bash
# Google Gemini (recommended for embeddings)
GEMINI_API_KEY=...
DEFAULT_EMBEDDING_PROVIDER=gemini
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small

# OpenAI embeddings
OPENAI_API_KEY=...
DEFAULT_EMBEDDING_PROVIDER=openai
```

### Default Providers

```bash
# Choose your default LLM
DEFAULT_LLM_PROVIDER=zai
# Options: openai, deepseek, anthropic, ollama, zai
```

### Optional Configuration

```bash
# Qdrant (vector database)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=knowledge_base

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8100
```

## Docker Services

### Service Architecture

```
┌─────────────┐
│   Frontend  │ Next.js 16 + React 19
│   :3100     │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌──────────────────┐
│   Backend   │────▶│   File Watcher    │
│   :8100     │     │   (auto ingest)   │
└──────┬──────┘     └──────────────────┘
       │                        ↑
       ↓                        │
┌─────────────┐           ┌─────┴──────┐
│   Qdrant    │           │  Inbox Dir │
│   :7333     │           └────────────┘
└─────────────┘

┌──────────────────────────────┐
│     Browser Extension         │
│  (Save pages from browser)    │
└──────────────────────────────┘
```

### Service Dependencies

- **Frontend** depends on Backend
- **Backend** depends on Qdrant (health check)
- **File Watcher** depends on Backend

All services have `restart: unless-stopped` policy.

## Development

### Running in Development Mode

```bash
# Backend (with hot reload)
docker compose up backend

# Frontend (development server)
cd frontend
npm install
npm run dev

# All services
docker compose up
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f qdrant
docker compose logs -f file-watcher
```

### Stopping Services

```bash
docker compose down
```

## Project Status

- [x] **Phase 1**: Core Backend (FastAPI, Qdrant, LangChain) ✅
- [x] **Phase 2**: Frontend (Next.js, Tailwind CSS) ✅
- [x] **Phase 3**: Extensions (Browser Extension, File Watcher) ✅
- [ ] Phase 4: Polish (Enhanced Citations, Advanced Features)

## What's Implemented

### Backend (FastAPI)
- Multi-provider LLM support (OpenAI, DeepSeek, Anthropic, Ollama, Z.ai)
- Multi-provider embeddings (OpenAI, Gemini)
- RAG-powered chat with source citations
- Document ingestion (URL, text, file)
- Semantic chunking and vector storage
- YouTube transcript fetching
- PDF/DOCX document parsing
- Health check and system status endpoints

### Frontend (Next.js)
- Home page with navigation
- Chat interface with message history and source citations
- Document management page with delete functionality
- Settings page with system health status
- Responsive design with dark mode support
- Real-time API integration

### Browser Extension
- Manifest V3 compatible (Chrome, Firefox, Edge)
- Popup UI with page preview
- One-click save to PKS
- Content script for page metadata extraction
- Background service worker for persistence

### File Watcher
- Monitors `data/inbox/` directory
- Automatic file detection and processing
- Supports text files and documents
- Moves processed files to `data/processed/`
- Python watchdog-based implementation

## Troubleshooting

### Extension not connecting to backend

1. Verify backend is running: `docker compose ps`
2. Check backend is accessible: `curl http://localhost:8100/api/v1/health`
3. Check extension console for errors (F12)

### File watcher not processing files

1. Check file watcher logs: `docker compose logs -f file-watcher`
2. Verify file is in correct directory: `ls data/inbox/`
3. Check backend health status

### Documents not appearing in chat

1. Verify Qdrant connection: Check Settings page
2. Check if embedding provider is configured (Gemini API key)
3. Try re-indexing: Delete and re-ingest the document

### Port already in use

If default ports are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3101:3000"  # Change 3100 to 3101
```

## License

MIT
