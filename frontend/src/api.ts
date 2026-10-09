import type { ApiError, Health, IndexStatus, IndexSummary, Preview, SearchResponse, SearchResult } from './types'

export const fixtureMode = import.meta.env.DEV && import.meta.env.VITE_SIFT_DEV_FIXTURES === 'true'
const demoSamples: Array<{ file: SearchResult; terms: string[]; preview: string }> = [
  {
    file: { file_id: 'file_001', name: 'IMG_2034.png', relative_path: 'receipts/IMG_2034.png', file_type: 'png', size_bytes: 128400, modified_at: '2026-06-12T08:30:00Z', snippet: 'Laptop repair: replacement keyboard. Total PHP 2,500.', location: { page: null }, match_kind: 'hybrid' },
    terms: ['laptop', 'repair', 'keyboard', 'receipt', '2500', '2,500'],
    preview: 'Laptop repair\nReplacement keyboard\nTotal PHP 2,500\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
  },
  {
    file: { file_id: 'file_002', name: 'biology-review.md', relative_path: 'school/biology-review.md', file_type: 'md', size_bytes: 4620, modified_at: '2024-08-19T12:00:00Z', snippet: 'Photosynthesis uses chlorophyll to convert light into stored chemical energy.', location: { page: null }, match_kind: 'semantic' },
    terms: ['biology', 'photosynthesis', 'chlorophyll', 'class', 'study'],
    preview: 'Biology review\nPhotosynthesis uses chlorophyll to convert light into stored chemical energy.\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
  },
  {
    file: { file_id: 'file_003', name: 'hotel-booking.txt', relative_path: 'travel/hotel-booking.txt', file_type: 'txt', size_bytes: 2380, modified_at: '2023-03-04T09:15:00Z', snippet: 'Booking confirmed: three nights in Kyoto, check-in on April 18.', location: { page: null }, match_kind: 'keyword' },
    terms: ['hotel', 'booking', 'travel', 'kyoto', 'confirmation'],
    preview: 'Hotel booking confirmation\nThree nights in Kyoto\nCheck-in: April 18\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
  },
  {
    file: { file_id: 'file_004', name: 'monthly-budget.pdf', relative_path: 'home/finance/monthly-budget.pdf', file_type: 'pdf', size_bytes: 34820, modified_at: '2022-11-22T16:45:00Z', snippet: 'Monthly budget notes: rent, transit, groceries, and savings goals.', location: { page: 2 }, match_kind: 'hybrid' },
    terms: ['budget', 'finance', 'rent', 'savings', 'expenses'],
    preview: 'Monthly budget\nRent, transit, groceries, and savings goals.\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
  },
  {
    file: { file_id: 'file_005', name: 'garden-notes.txt', relative_path: 'hobbies/garden-notes.txt', file_type: 'txt', size_bytes: 1910, modified_at: '2021-05-11T07:00:00Z', snippet: 'Tomatoes need steady sun, deep watering, and support as the plants grow.', location: { page: null }, match_kind: 'semantic' },
    terms: ['garden', 'tomato', 'plants', 'watering', 'hobby'],
    preview: 'Garden notes\nTomatoes need steady sun, deep watering, and support as the plants grow.\n\nDEVELOPMENT SAMPLE — synthetic content for interface review only.',
  },
]

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
    const results = demoSamples.filter(sample => sample.terms.some(term => query.includes(term))).map(sample => sample.file)
    return { results, elapsed_ms: 180, searchable_files: 24, index_in_progress: false } satisfies SearchResponse
  }
  if (path.endsWith('/preview')) {
    const fileId = decodeURIComponent(path.slice('/files/'.length, path.lastIndexOf('/')))
    const sample = demoSamples.find(item => item.file.file_id === fileId)
    if (!sample) throw new ApiFailure('That sample file is unavailable.', 'FIXTURE_FILE_NOT_FOUND', false, 404)
    return { file_id: sample.file.file_id, name: sample.file.name, relative_path: sample.file.relative_path, file_type: sample.file.file_type, text: sample.preview, truncated: false } satisfies Preview
  }
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
