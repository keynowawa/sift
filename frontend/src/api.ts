import type { ApiError, Health, IndexStatus, IndexSummary, Preview, SearchResponse } from './types'

export const fixtureMode = import.meta.env.DEV && import.meta.env.VITE_SIFT_DEV_FIXTURES === 'true'
const demoFile = {
  file_id: 'file_001', name: 'IMG_2034.png', relative_path: 'receipts/IMG_2034.png',
  file_type: 'png', size_bytes: 128400, modified_at: '2026-06-12T08:30:00Z',
  snippet: 'Laptop repair: replacement keyboard. Total PHP 2,500.',
  location: { page: null }, match_kind: 'hybrid' as const,
}

export class ApiFailure extends Error {
  code: string
  retryable: boolean
  status: number
  constructor(message: string, code = 'NETWORK_ERROR', retryable = true, status = 0) {
    super(message)
    this.name = 'ApiFailure'
    this.code = code
    this.retryable = retryable
    this.status = status
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (fixtureMode) {
    const result = fixtureResponse(path, init)
    await new Promise(resolve => window.setTimeout(resolve, 160))
    return result as T
  }
  let response: Response
  try {
    response = await fetch(`/api${path}`, {
      ...init,
      headers: { ...(init.body ? { 'Content-Type': 'application/json' } : {}), ...init.headers },
    })
  } catch {
    throw new ApiFailure('Could not reach Sift. Check that the local app is running, then retry.')
  }
  if (!response.ok) {
    let detail: ApiError | undefined
    try { detail = await response.json() as ApiError } catch { /* response may not be JSON */ }
    throw new ApiFailure(
      detail?.error?.message ?? `Sift returned an unexpected response (${response.status}).`,
      detail?.error?.code ?? 'HTTP_ERROR',
      detail?.error?.retryable ?? response.status >= 500,
      response.status,
    )
  }
  return response.json() as Promise<T>
}

function fixtureResponse(path: string, init: RequestInit): unknown {
  if (path === '/health') return {
    status: 'ready', platform: 'windows', embedding: { ready: true, model: 'DEVELOPMENT FIXTURE — no model used' },
    ocr: { ready: true }, capabilities: { folder_picker: true, open_file: true, reveal_file: true }, setup_steps: [],
  } satisfies Health
  if (path === '/index') return {
    root: 'C:\\Sift demo files', indexed_files: 24, searchable_files: 24, total_chunks: 36,
    last_updated: '2026-06-12T08:30:00Z', active_job_id: null,
  } satisfies IndexSummary
  if (path === '/folder/pick') return { path: 'C:\\Sift demo files' }
  if (path === '/index/start') return { job_id: 'fixture_job' }
  if (path.startsWith('/index/status')) return {
    job_id: 'fixture_job', state: 'completed', phase: 'finished', discovered: 24, processed: 24,
    searchable: 24, skipped: 0, failed: 0, current_file: null, elapsed_ms: 940, errors: [],
  } satisfies IndexStatus
  if (path === '/index/cancel') return { accepted: true }
  if (path === '/search') {
    const payload = JSON.parse(String(init.body ?? '{}')) as { query?: string }
    const query = payload.query?.toLowerCase() ?? ''
    const results = /laptop|repair|keyboard|receipt|2500|2,500/.test(query) ? [demoFile] : []
    return { results, elapsed_ms: 180, searchable_files: 24, index_in_progress: false } satisfies SearchResponse
  }
  if (path.endsWith('/preview')) return {
    file_id: 'file_001', name: demoFile.name, relative_path: demoFile.relative_path, file_type: 'png',
    text: 'Laptop repair\nReplacement keyboard\nTotal PHP 2,500\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
    truncated: false,
  } satisfies Preview
  if (path.endsWith('/open') || path.endsWith('/reveal')) return { ok: true }
  throw new ApiFailure('This action is not included in development fixture mode.', 'FIXTURE_UNAVAILABLE', false)
}

const json = (body: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(body) })

export const api = {
  health: () => request<Health>('/health'),
  index: () => request<IndexSummary>('/index'),
  pickFolder: () => request<{ path: string | null }>('/folder/pick', json({})),
  startIndex: (root: string, replace_index: boolean) => request<{ job_id: string }>('/index/start', json({ root, replace_index })),
  jobStatus: (jobId: string) => request<IndexStatus>(`/index/status?job_id=${encodeURIComponent(jobId)}`),
  cancelIndex: (job_id: string) => request<{ accepted: boolean }>('/index/cancel', json({ job_id })),
  search: (query: string, file_types: string[]) => request<SearchResponse>('/search', json({ query, limit: 10, file_types })),
  preview: (fileId: string) => request<Preview>(`/files/${encodeURIComponent(fileId)}/preview`),
  openFile: (fileId: string) => request<{ ok: boolean }>(`/files/${encodeURIComponent(fileId)}/open`, json({})),
  revealFile: (fileId: string) => request<{ ok: boolean }>(`/files/${encodeURIComponent(fileId)}/reveal`, json({})),
}
