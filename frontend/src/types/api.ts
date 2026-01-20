export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: SourceInfo[]
}

export interface SourceInfo {
  title: string
  url: string
  source: string
}

export interface ChatRequest {
  query: string
  history?: ChatMessage[]
}

export interface ChatResponse {
  response: string
  sources: SourceInfo[]
  context_used: number
}

export interface IngestRequest {
  url?: string
  text?: string
  metadata?: Record<string, any>
}

export interface IngestResponse {
  document_id: string
  chunks_count: number
  point_ids: string[]
  status: string
}

export interface DocumentInfo {
  id: string
  title: string
  url: string
  source: string
  timestamp: string
}

export interface DocumentListResponse {
  documents: DocumentInfo[]
}

export interface HealthResponse {
  status: string
  qdrant_connected: boolean
  collection_name: string
}
