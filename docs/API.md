# PKS API Documentation

Complete API reference for the Personal Knowledge Synthesizer backend.

## Base URL

```
http://localhost:8100/api/v1
```

## Authentication

Currently, no authentication is required. For production deployments, implement API key authentication.

## Endpoints

### Health Check

#### GET /health

Check system health and Qdrant connection status.

**Request:**
```bash
curl http://localhost:8100/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collection_name": "knowledge_base"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "qdrant_connected": false,
  "error": "Connection refused"
}
```

---

### Ingest Content

#### POST /ingest

Ingest content from a URL, raw text, or file into the knowledge base.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**

Ingest a URL:
```json
{
  "url": "https://example.com/article",
  "metadata": {
    "source": "web",
    "tags": ["tech", "tutorial"]
  }
}
```

Ingest raw text:
```json
{
  "text": "This is the content to ingest into the knowledge base.",
  "metadata": {
    "source": "manual",
    "title": "My Notes"
  }
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | No* | URL to fetch and ingest |
| `text` | string | No* | Raw text content to ingest |
| `metadata` | object | No | Additional metadata (tags, source, etc.) |

*Either `url` or `text` must be provided.

**Response (200 OK):**
```json
{
  "document_id": "doc_1711387230000",
  "chunks_count": 5,
  "point_ids": ["point_1", "point_2", "point_3", "point_4", "point_5"],
  "status": "success"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Either 'url' or 'text' must be provided"
}
```

**cURL Examples:**

Ingest a URL:
```bash
curl -X POST http://localhost:8100/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "metadata": {"source": "web"}
  }'
```

Ingest text:
```bash
curl -X POST http://localhost:8100/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog.",
    "metadata": {"title": "Animal Facts"}
  }'
```

Ingest YouTube video (transcript):
```bash
curl -X POST http://localhost:8100/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

---

### Chat with Knowledge Base

#### POST /chat

Chat with your knowledge base using RAG (Retrieval-Augmented Generation).

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What is the main topic of the ingested documents?",
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you today?"
    }
  ]
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | User question/query |
| `history` | array | No | Conversation history for context |

**Response (200 OK):**
```json
{
  "response": "Based on the ingested documents, the main topics include...",
  "sources": [
    {
      "title": "Example Article",
      "url": "https://example.com/article",
      "source": "web"
    }
  ],
  "context_used": 3
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8100/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize the documents about machine learning"
  }'
```

---

### Documents

#### GET /documents

List all documents in the knowledge base.

**Response (200 OK):**
```json
{
  "documents": [
    {
      "document_id": "doc_1711387230000",
      "title": "Example Article",
      "url": "https://example.com/article",
      "source": "web",
      "chunk_count": 5,
      "ingested_at": "2026-03-26T03:20:30Z"
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8100/api/v1/documents
```

---

#### DELETE /documents/{document_id}

Delete a document and all its chunks from the knowledge base.

**URL Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `document_id` | string | The document ID to delete |

**Response (200 OK):**
```json
{
  "status": "success",
  "deleted_count": 5
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Document not found"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8100/api/v1/documents/doc_1711387230000
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server-side error |

---

## Interactive API Documentation

When the backend is running, visit the interactive Swagger UI:

```
http://localhost:8100/docs
```

This provides a web interface to test all API endpoints directly.
