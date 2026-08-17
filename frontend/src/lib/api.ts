import type {
  ChatRequest,
  ChatResponse,
  DocumentListResponse,
  IngestResponse,
  HealthResponse,
} from '@/types/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (data && data.detail) detail = String(data.detail)
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  async getSettings(): Promise<{ llm_provider: string; llm_model: string; embedding_provider: string; embedding_model: string }> {
    // Backend route is POST /api/v1/settings/ ; GET equivalent exposed as /api/v1/settings/v1
    const res = await fetch(`${API_URL}/api/v1/settings/v1`)
    return handle<{ llm_provider: string; llm_model: string; embedding_provider: string; embedding_model: string }>(res)
  },

  async saveSettings(body: {
    llm_provider: string
    llm_model: string
    embedding_provider: string
    embedding_model: string
  }): Promise<{ llm_provider: string; llm_model: string; embedding_provider: string; embedding_model: string }> {
    const res = await fetch(`${API_URL}/api/v1/settings/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    return handle<{ llm_provider: string; llm_model: string; embedding_provider: string; embedding_model: string }>(res)
  },

  async chat(req: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${API_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    })
    return handle<ChatResponse>(res)
  },

  async ingest(body: { url?: string; text?: string; metadata?: Record<string, unknown> }): Promise<IngestResponse> {
    const res = await fetch(`${API_URL}/api/v1/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    return handle<IngestResponse>(res)
  },

  async uploadFile(file: File): Promise<IngestResponse> {
    const form = new FormData()
    form.append('file', file)
    form.append('metadata', JSON.stringify({ filename: file.name }))
    const res = await fetch(`${API_URL}/api/v1/upload`, {
      method: 'POST',
      body: form,
    })
    return handle<IngestResponse>(res)
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await fetch(`${API_URL}/api/v1/documents`)
    return handle<DocumentListResponse>(res)
  },

  async deleteDocument(id: string): Promise<{ status: string; deleted_count: number }> {
    const res = await fetch(`${API_URL}/api/v1/documents/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    })
    return handle<{ status: string; deleted_count: number }>(res)
  },

  async health(): Promise<HealthResponse> {
    const res = await fetch(`${API_URL}/api/v1/health`)
    return handle<HealthResponse>(res)
  },
}