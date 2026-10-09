export type Health = {
  status: 'ready' | 'setup_required'
  platform: 'windows' | 'macos' | 'other'
  embedding: { ready: boolean; model: string }
  ocr: { ready: boolean }
  capabilities: { folder_picker: boolean; open_file: boolean; reveal_file: boolean }
  setup_steps: string[]
}

export type IndexSummary = {
  root: string | null
  indexed_files: number
  searchable_files: number
  total_chunks: number
  last_updated: string | null
  active_job_id: string | null
}

export type IndexStatus = {
  job_id: string
  state: 'queued' | 'running' | 'completed' | 'cancelled' | 'failed' | 'interrupted'
  phase: 'discovering' | 'extracting' | 'embedding' | 'finished'
  discovered: number
  processed: number
  searchable: number
  skipped: number
  failed: number
  current_file: string | null
  elapsed_ms: number
  errors: Array<{ relative_path: string; message: string }>
}

export type SearchResult = {
  file_id: string
  name: string
  relative_path: string
  file_type: 'txt' | 'md' | 'pdf' | 'png' | 'jpg' | string
  size_bytes: number
  modified_at: string
  snippet: string
  location: { page: number | null }
  match_kind: 'semantic' | 'keyword' | 'hybrid'
}

export type SearchResponse = {
  results: SearchResult[]
  elapsed_ms: number
  searchable_files: number
  index_in_progress: boolean
}

export type Preview = {
  file_id: string
  name: string
  relative_path: string
  file_type: string
  text: string
  truncated: boolean
}

export type ApiError = { error: { code: string; message: string; retryable: boolean } }
