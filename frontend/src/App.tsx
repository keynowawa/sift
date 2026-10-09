import { FormEvent, useCallback, useEffect, useRef, useState } from 'react'
import { api, ApiFailure, fixtureMode } from './api'
import type { Health, IndexStatus, IndexSummary, Preview, SearchResult } from './types'

const terminal = new Set<IndexStatus['state']>(['completed', 'cancelled', 'failed', 'interrupted'])
const formatBytes = (n: number) => n < 1024 ? `${n} B` : n < 1024 * 1024 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 / 1024).toFixed(1)} MB`
const prettyDate = (value: string) => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [healthError, setHealthError] = useState('')
  const [summary, setSummary] = useState<IndexSummary | null>(null)
  const [job, setJob] = useState<IndexStatus | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [folder, setFolder] = useState('')
  const [consented, setConsented] = useState(false)
  const [busy, setBusy] = useState(false)
  const [cancelRequested, setCancelRequested] = useState(false)
  const [query, setQuery] = useState('')
  const [searchedTerm, setSearchedTerm] = useState('')
  const [results, setResults] = useState<SearchResult[] | null>(null)
  const [searchInfo, setSearchInfo] = useState<{ elapsed: number; count: number; indexing: boolean } | null>(null)
  const [searching, setSearching] = useState(false)
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [preview, setPreview] = useState<Preview | null>(null)
  const [notice, setNotice] = useState('')
  const [actionError, setActionError] = useState('')
  const [controlsOpen, setControlsOpen] = useState(false)
  const searchSeq = useRef(0)

  const refresh = useCallback(async () => {
    try {
      const [h, i] = await Promise.all([api.health(), api.index()])
      setHealth(h); setHealthError(''); setSummary(i)
      if (i.active_job_id) setJobId(i.active_job_id)
    } catch (e) { setHealthError(message(e)) }
  }, [])

  useEffect(() => { void refresh() }, [refresh])

  useEffect(() => {
    if (!jobId) return
    let live = true
    const poll = async () => {
      try {
        const next = await api.jobStatus(jobId)
        if (!live) return
        setJob(next)
        if (terminal.has(next.state)) {
          setJobId(null); setCancelRequested(false)
          const latest = await api.index()
          if (live) setSummary(latest)
        }
      } catch (e) { if (live) setActionError(message(e)) }
    }
    void poll()
    const timer = window.setInterval(() => { void poll() }, 1000)
    return () => { live = false; window.clearInterval(timer) }
  }, [jobId])

  async function chooseFolder() {
    setActionError('')
    try {
      const picked = await api.pickFolder()
      if (picked.path !== null) setFolder(picked.path)
    } catch (e) { setActionError(message(e)) }
  }

  async function startIndex(e: FormEvent) {
    e.preventDefault()
    const root = folder.trim()
    if (!root) { setActionError('Enter a folder path or choose a folder first.'); return }
    if (!consented) { setActionError('Please confirm that Sift may read files in this folder to create a local index.'); return }
    if (busy || jobId) return
    const replacing = Boolean(summary?.root && summary.root !== root)
    if (replacing && !window.confirm(`This replaces the current index for “${summary?.root}” with “${root}”. Continue?`)) return
    setBusy(true); setActionError(''); setJob(null)
    try {
      const started = await api.startIndex(root, replacing)
      setJobId(started.job_id); setCancelRequested(false)
    } catch (e) { setActionError(message(e)) }
    finally { setBusy(false) }
  }

  async function cancelIndex() {
    if (!jobId) return
    try { await api.cancelIndex(jobId); setCancelRequested(true); setNotice('Cancellation requested. Sift will finish its current file first.') }
    catch (e) { setActionError(message(e)) }
  }

  async function doSearch(e: FormEvent) {
    e.preventDefault()
    const term = query.trim()
    if (!term) { setActionError('Describe what you remember to search your indexed files.'); return }
    if (term.length > 500) { setActionError('Searches can be up to 500 characters.'); return }
    const sequence = ++searchSeq.current
    setSearching(true); setActionError(''); setNotice('')
    try {
      const response = await api.search(term, selectedTypes)
      if (sequence !== searchSeq.current) return
      setResults(response.results)
      setSearchedTerm(term)
      setSearchInfo({ elapsed: response.elapsed_ms, count: response.searchable_files, indexing: response.index_in_progress })
    } catch (e) { if (sequence === searchSeq.current) setActionError(message(e)) }
    finally { if (sequence === searchSeq.current) setSearching(false) }
  }

  async function showPreview(item: SearchResult) {
    setActionError(''); setPreview(null)
    try { setPreview(await api.preview(item.file_id)) } catch (e) { setActionError(message(e)) }
  }

  async function fileAction(item: SearchResult, action: 'open' | 'reveal') {
    setActionError(''); setNotice('')
    try { await (action === 'open' ? api.openFile(item.file_id) : api.revealFile(item.file_id)); setNotice(action === 'open' ? `Opened ${item.name}.` : `Showing ${item.name} in its folder.`) }
    catch (e) { setActionError(message(e)) }
  }

  const indexed = Boolean(summary?.root)
  const setupRequired = health?.status === 'setup_required' || health?.embedding.ready === false

  return <div className="app-shell">
    {fixtureMode && <div className="fixture-banner" role="status"><strong>Development fixture mode is ON</strong><span>All displayed files and actions are synthetic. This mode is unavailable in production builds.</span></div>}
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Sift home"><span className="brand-mark">s</span><span>Sift</span></a>
      <div className="privacy"><span className="privacy-dot" /> Private by design <span className="privacy-sep">·</span> Files stay on this device</div>
      <button className="icon-button" aria-label="Retry connection" onClick={() => void refresh()} title="Refresh connection">↻</button>
    </header>

    <main id="top" className="chat-main">
      <section className="chat-hero">
        <div className="eyebrow"><span className="spark">✳</span> YOUR FILES, FOUND</div>
        <h1>What are you <em>looking for?</em></h1>
        <p>Search your own files by describing what you remember.</p>
      </section>

      <section className="conversation-shell" aria-label="Sift file search">
        <header className="conversation-header">
          <div className="assistant-identity"><span className="assistant-avatar">s</span><div><strong>Sift Search</strong><span>Local file search</span></div></div>
          <button className={`folder-chip ${indexed ? 'has-index' : ''}`} type="button" onClick={() => setControlsOpen(open => !open)} aria-expanded={controlsOpen} aria-controls="search-controls">
            <span aria-hidden="true">▤</span><span>{indexed ? summary?.searchable_files + ' files indexed' : 'Choose a folder'}</span><span className="chevron">{controlsOpen ? '⌃' : '⌄'}</span>
          </button>
        </header>

        <div className="conversation-feed" aria-live="polite">
          {healthError && <div className="alert error" role="alert"><strong>Can’t connect to Sift</strong><span>{healthError}</span><button className="text-button" onClick={() => void refresh()}>Try again</button></div>}
          {setupRequired && health && <section className="alert setup" role="status"><div className="alert-icon">!</div><div><strong>Local model setup needed</strong><p>Sift needs its embedding model before it can index and search. Your files stay on this computer.</p>{health.setup_steps.length > 0 && <ol>{health.setup_steps.map((step, i) => <li key={i}>{step}</li>)}</ol>}</div></section>}
          {health?.ocr.ready === false && <div className="alert warning" role="status"><strong>Screenshot search is unavailable</strong><span>Text documents can still be indexed. Set up local OCR to search screenshots.</span></div>}

          {controlsOpen && <section id="search-controls" className="controls-card" aria-label="Folder and search options">
            <div className="controls-heading"><div><span className="result-kicker">YOUR LOCAL LIBRARY</span><h2>Folder &amp; indexing</h2></div><button className="text-button" type="button" onClick={() => setControlsOpen(false)}>Done</button></div>
            <form onSubmit={startIndex}>
              <label htmlFor="folder-path">Folder path</label>
              <div className="path-row"><input id="folder-path" value={folder} onChange={e => setFolder(e.target.value)} placeholder={health?.platform === 'windows' ? 'C:\\Users\\you\\Documents' : '/Users/you/Documents'} autoComplete="off" /><button type="button" className="secondary-button" onClick={() => void chooseFolder()} disabled={!health?.capabilities.folder_picker}>Browse</button></div>
              {!health?.capabilities.folder_picker && <p className="field-hint">Folder picker unavailable. Enter the full path above.</p>}
              <label className="consent"><input type="checkbox" checked={consented} onChange={e => setConsented(e.target.checked)} /><span>I give Sift permission to read this folder and build a local search index. Originals are never changed or uploaded.</span></label>
              <button className="primary-button" type="submit" disabled={busy || Boolean(jobId) || setupRequired || !health}>{busy ? 'Starting…' : indexed && folder === summary?.root ? 'Scan for changes' : 'Index this folder'}<span aria-hidden="true">→</span></button>
            </form>
            {summary?.root && <div className="index-summary"><div className="summary-label">CURRENT FOLDER</div><div className="root-path" title={summary.root}>{summary.root}</div><div className="summary-stats"><span><strong>{summary.searchable_files}</strong> searchable</span><span><strong>{summary.total_chunks}</strong> passages</span></div>{summary.last_updated && <p>Last updated {prettyDate(summary.last_updated)}</p>}</div>}
            <div className="filter-settings"><span className="summary-label">SEARCH FILE TYPES</span><div className="search-meta">{['txt', 'md', 'pdf', 'png', 'jpg'].map(ext => <button key={ext} type="button" className={`filter-chip ${selectedTypes.includes(ext) ? 'active' : ''}`} aria-pressed={selectedTypes.includes(ext)} onClick={() => setSelectedTypes(prev => prev.includes(ext) ? prev.filter(x => x !== ext) : [...prev, ext])}>{ext.toUpperCase()}</button>)}<span className="filter-note">None selected searches all types</span></div></div>
          </section>}

          {!results && !jobId && <div className="welcome-message"><span className="assistant-avatar small-avatar">s</span><div className="welcome-copy"><strong>Hi, I can help you find a file.</strong><p>Describe what was in it, and I’ll show matching files with excerpts from their contents.</p><div className="suggestion-list"><button type="button" onClick={() => setQuery('A laptop repair receipt from last spring')}>“A laptop repair receipt”</button><button type="button" onClick={() => setQuery('Class notes about photosynthesis')}>“Class notes about photosynthesis”</button><button type="button" onClick={() => setQuery('A hotel booking confirmation in Cebu')}>“A hotel booking confirmation”</button></div></div></div>}

          {actionError && <p className="inline-error" role="alert">{actionError}</p>}
          {job && <div className="progress-card" role="status" aria-live="polite"><div className="progress-heading">{!terminal.has(job.state) && <span className="loader" />}<strong>{terminal.has(job.state) ? job.state === 'completed' ? 'Indexing complete' : `Index ${job.state}` : phaseLabel(job.phase)}</strong><span className="progress-count">{job.processed} processed · {job.searchable} searchable</span>{!terminal.has(job.state) && <button className="text-button" onClick={() => void cancelIndex()} disabled={cancelRequested}>{cancelRequested ? 'Cancel requested' : 'Cancel'}</button>}</div>{job.current_file && <div className="current-file">{job.current_file}</div>}{!terminal.has(job.state) && job.phase !== 'discovering' && <div className="progress-track"><span style={{ width: job.discovered ? `${Math.min(100, job.processed / job.discovered * 100)}%` : '8%' }} /></div>}<div className="progress-foot">{job.discovered > 0 ? `${job.discovered} files found so far` : 'Finding files…'}{job.skipped > 0 && ` · ${job.skipped} skipped`}{job.failed > 0 && ` · ${job.failed} failed`}</div>{terminal.has(job.state) && job.errors.length > 0 && <div className="job-terminal"><details><summary>{job.errors.length} file issue(s)</summary><ul>{job.errors.map((err, i) => <li key={i}>{err.relative_path}: {err.message}</li>)}</ul></details></div>}</div>}

          {searchInfo && results && <div className="search-turn">
            <div className="user-message"><span>You</span><p>{searchedTerm}</p></div>
            {searchInfo.indexing && <p className="indexing-note">Searching {searchInfo.count} indexed files while indexing continues.</p>}
            <div className="results-head"><div><span className="result-kicker">{results.length ? `${results.length} MATCH${results.length === 1 ? '' : 'ES'}` : 'NO MATCHES'}</span><h3>{results.length ? 'Files that match' : 'No matching files found'}</h3></div><span className="search-time">{searchInfo.elapsed} ms</span></div>
            {results.length === 0 && <div className="empty-state"><span className="empty-symbol">⌕</span><p>Try another detail, or check that this folder has been indexed.</p></div>}
            {results.length > 0 && <div className="results-list">{results.map(item => <article className="result-card" key={item.file_id}><div className="file-type">{item.file_type.slice(0, 4).toUpperCase()}</div><div className="result-main"><div className="result-title-row"><h3>{item.name}</h3><span className="match-pill">{item.match_kind}</span></div><p className="relative-path" title={item.relative_path}>{item.relative_path}</p><blockquote>{item.snippet}{item.location.page && <span className="page-label"> · page {item.location.page}</span>}</blockquote><div className="result-details"><span>{formatBytes(item.size_bytes)}</span><span>Modified {prettyDate(item.modified_at)}</span></div><div className="result-actions"><button className="primary-button small" onClick={() => void fileAction(item, 'open')} disabled={!health?.capabilities.open_file}>Open file <span>↗</span></button><button className="secondary-button small" onClick={() => void showPreview(item)}>Preview</button><button className="text-button" onClick={() => void fileAction(item, 'reveal')} disabled={!health?.capabilities.reveal_file}>Show in folder</button></div></div></article>)}</div>}
          </div>}
          {notice && <p className="success-note" role="status">{notice}</p>}
        </div>

        <form className="chat-composer" onSubmit={doSearch}>
          <label className="sr-only" htmlFor="search-message">Describe the file you want to find</label>
          <div className="composer-input-row"><input id="search-message" value={query} onChange={e => setQuery(e.target.value)} placeholder="Describe the file or detail you remember…" maxLength={500} /><button className="send-button" type="submit" aria-label="Search files" disabled={searching || !health || !indexed || setupRequired}>{searching ? <span className="loader" /> : '↑'}</button></div>
          <div className="composer-tools"><button type="button" className="tool-button" onClick={() => setControlsOpen(open => !open)} aria-expanded={controlsOpen}><span aria-hidden="true">＋</span> Folder &amp; filters</button><span>{indexed ? `Searching ${summary?.searchable_files} indexed files` : 'Choose a folder to get started'}</span><span className="composer-privacy"><span className="footer-dot" /> On-device</span></div>
        </form>
      </section>

      <footer><span><span className="footer-dot" /> LOCAL INDEX · NO CLOUD AI</span><span>Matching excerpts come from your files. Originals stay read-only.</span></footer>
    </main>

    {preview && <div className="modal-backdrop" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget) setPreview(null) }}><section className="preview-modal" role="dialog" aria-modal="true" aria-labelledby="preview-title"><div className="preview-header"><div><span className="result-kicker">SOURCE PREVIEW</span><h2 id="preview-title">{preview.name}</h2><p>{preview.relative_path}</p></div><button className="icon-button" aria-label="Close preview" onClick={() => setPreview(null)}>×</button></div><div className="preview-body">{preview.text ? <pre>{preview.text}</pre> : <p className="muted">No extracted text is available for preview. You can open the original file instead.</p>}</div>{preview.truncated && <p className="preview-truncated">Preview shortened. The full file remains unchanged.</p>}</section></div>}
  </div>
}

function message(error: unknown) { return error instanceof ApiFailure ? error.message : error instanceof Error ? error.message : 'Something went wrong. Please try again.' }
function phaseLabel(phase: IndexStatus['phase']) { return ({ discovering: 'Finding files', extracting: 'Reading content', embedding: 'Building local search', finished: 'Wrapping up' })[phase] }
