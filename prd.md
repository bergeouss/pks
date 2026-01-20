# Product Requirement Document: Personal Knowledge Synthesizer (PKS)

## 1. Introduction
**Project Name:** Personal Knowledge Synthesizer (Internal Name: `pks-core`)
**Version:** 1.0 (MVP)
**Description:** A self-hosted, Docker-based personal knowledge management system designed to ingest unstructured data (web pages, documents, videos) and allow a user to interact with it via an AI chat interface. The system prioritizes privacy, semantic search, and flexible AI provider integration.

## 2. Problem Statement
As a power user, information is scattered across the web (YouTube, articles), local files (PDFs, Docs), and various formats. Existing solutions often require cloud subscriptions (privacy concerns) or lack flexibility in AI models. There is a need for a centralized "second brain" that automatically ingests content, understands the context, and answers questions based on *all* accumulated data, running entirely on personal hardware (Local/VPS).

## 3. User Persona
*   **Name:** The "Solo Researcher"
*   **Technical Proficiency:** High (Comfortable with Docker, VPS, APIs).
*   **Goal:** To build a personal, private intelligence repository that requires minimal manual organization but provides maximum retrieval capability.
*   **Frustrations:** Data silos, privacy leaks in public AI tools, vendor lock-in.

## 4. System Architecture (High Level)
The system will follow a microservices architecture orchestrated by Docker Compose.

1.  **Frontend:** Next.js (React) - Handles the Dashboard, Chat UI, and Settings.
2.  **Backend API:** FastAPI (Python) - Handles ingestion logic, embedding generation, and chat orchestration.
3.  **Vector Database:** Qdrant - Stores vector embeddings and metadata.
4.  **Browser Extension:** Chrome/Firefox Extension - Sends content to Backend API.
5.  **File Watcher Service:** Python script - Monitors a mounted volume for new files.
6.  **Queue (Optional but recommended):** Redis/Task Queue - To handle heavy processing (embedding large PDFs) asynchronously.

---

## 5. Functional Requirements

### 5.1 Data Ingestion (The "Input")
| ID | Feature | Description |
| :--- | :--- | :--- |
| **FR-01** | **Browser Extension - Full Page** | User can click the extension to capture the full text content of the current URL. HTML tags are stripped, and only clean text is sent to the API. |
| **FR-02** | **Browser Extension - Metadata** | Alongside text, the system must capture and store: URL, Page Title, Timestamp, and Author (if available). |
| **FR-03** | **Local Folder Watcher** | A background service monitors a specific directory (e.g., `/app/data/inbox`). When a file (PDF, DOCX, TXT) is added, it is automatically queued for processing and deleted/moved upon success. |
| **FR-04** | **YouTube Transcription** | If the input URL is a YouTube link, the system must fetch the transcript (using a library like `youtube-transcript-api`) rather than scraping the video description. |
| **FR-05** | **Content Parsing** | The system must use parsers (e.g., `PyPDF2`, `python-docx`, `BeautifulSoup`) to extract raw text from binary formats. |

### 5.2 Processing Pipeline (The "Brain")
| ID | Feature | Description |
| :--- | :--- | :--- |
| **FR-06** | **Chunking Strategy** | Text is split into semantic chunks (e.g., 500-1000 tokens) with overlap to maintain context. |
| **FR-07** | **Embedding Generation** | Each chunk is converted into a vector embedding using the model specified in settings (default: `text-embedding-3-small`). |
| **FR-08** | **Qdrant Upsert** | Generated vectors and associated metadata are upserted into the Qdrant collection. |
| **FR-09** | **Dynamic Classification** | The system does not rely on hardcoded tags. Instead, it relies on **Vector Similarity** to implicitly classify content. (e.g., "Theme" is determined by the proximity of embeddings in vector space). |

### 5.3 Retrieval & Chat (The "Output")
| ID | Feature | Description |
| :--- | :--- | :--- |
| **FR-10** | **AI Chat Interface** | A ChatGPT-like UI where the user types queries. |
| **FR-11** | **RAG Context Retrieval** | When a query is received, the system performs a semantic search against Qdrant to find the top-K (e.g., top 5) most relevant chunks. |
| **FR-12** | **Context Injection** | The retrieved chunks are injected into the System Prompt of the LLM. |
| **FR-13** | **Multi-Provider Support** | The user can configure the API Key and Base URL for different providers (OpenAI, DeepSeek, Anthropic, Ollama for local). The backend abstracts this via a unified interface. |
| **FR-14** | **Source Citation** | The AI's response must include clickable links to the original source documents or URLs found in the metadata. |

### 5.4 Dashboard & Management
| ID | Feature | Description |
| :--- | :--- | :--- |
| **FR-15** | **Ingestion Status** | A dashboard showing "Processing," "Success," and "Failed" items. |
| **FR-16** | **Document List** | A searchable list of all ingested documents with the ability to delete them (which cascades to deleting vectors from Qdrant). |
| **FR-17** | **Settings Panel** | UI to manage API Keys, select the active LLM model, select the Embedding model, and view Qdrant connection status. |

---

## 6. Technical Specifications

### 6.1 Tech Stack
*   **Frontend:** **Next.js (App Router)** + TypeScript + Tailwind CSS + Shadcn/UI (for rapid, beautiful components).
*   **Backend:** **FastAPI** + Python 3.11+.
*   **AI/Orchestration:** **LangChain** (handles LLM abstraction and Qdrant integration).
*   **Database:** **Qdrant** (Vector DB).
*   **File Storage:** Local volume mounting (e.g., `/app/data`).
*   **Deployment:** **Docker Compose**.

### 6.2 Multi-Provider Logic
The backend will utilize an environment variable configuration strategy.
*   `DEFAULT_LLM_PROVIDER`: `openai` | `deepseek` | `ollama`
*   `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, etc.
*   The LangChain `ChatPromptTemplate` will dynamically initialize the correct chat model class based on the user's selection.

---

## 7. Non-Functional Requirements
*   **Privacy:** All API keys are stored locally in `.env` files. No telemetry is sent to external servers other than the selected AI Provider.
*   **Performance:** Ingestion of a standard web article should happen in < 5 seconds. Chat response latency depends on the LLM provider but system overhead should be < 1s.
*   **Reliability:** If the file watcher fails, it should log the error and retry rather than crashing the container.
*   **Portability:** The entire system must be startable with a single `docker-compose up` command.

---

## 8. User Stories

1.  **Ingestion:** "As a user, I want to click a button in my browser while reading a blog post so that the text is immediately saved to my knowledge base without me copying and pasting."
2.  **Research:** "As a user, I want to drop 10 PDF research papers into a folder so that I can later ask specific questions about the data across all of them simultaneously."
3.  **Flexibility:** "As a user, I want to switch my AI model from GPT-4 to DeepSeek instantly in the settings menu to compare cost or speed."
4.  **Retrieval:** "As a user, when I ask the AI 'What did I learn about quantum mechanics last week?', it provides a summary based on the videos I watched and articles I saved."

---

## 9. Implementation Roadmap (MVP)

### Phase 1: The Core (Backend & DB)
*   Setup Docker Compose with Qdrant and FastAPI.
*   Implement the "Ingestion Endpoint" (accepts text/metadata).
*   Implement LangChain pipeline: Text -> Chunk -> Embed -> Qdrant Upsert.
*   Implement "Chat Endpoint": Query -> Qdrant Search -> LLM Context -> Response.

### Phase 2: The Interface (Frontend)
*   Setup Next.js project with Shadcn/UI.
*   Build the Chat Interface (Input box, Message history).
*   Build the Settings Page (API Key management).
*   Connect Frontend to Backend via REST API.

### Phase 3: The Inputs (Extension & Watcher)
*   Build Chrome Extension (Manifest V3) content script to scrape page text.
*   Write Python File Watcher script to detect new files in `/data/inbox`.
*   Add YouTube transcript fetching logic to the ingestion pipeline.

### Phase 4: Polish
*   Add "Source Citations" to the chat response.
*   Implement Delete functionality (UI + Vector cleanup).
*   Docker optimization and documentation.
