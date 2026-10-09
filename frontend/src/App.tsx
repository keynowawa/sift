import { FormEvent, useCallback, useEffect, useRef, useState } from 'react'
import { flushSync } from 'react-dom'
import { api, ApiFailure, fixtureMode } from './api'
import { SiftLogo, SiftOrb, ThemeIcon } from './BrandArtwork'
import HomeDashboard from './HomeDashboard'
import type { FileHistoryItem } from './HomeDashboard'
import type { Health, IndexStatus, IndexSummary, Preview, SearchResult } from './types'

const terminal = new Set<IndexStatus['state']>(['completed', 'cancelled', 'failed', 'interrupted'])
const formatBytes = (n: number) => n < 1024 ? `${n} B` : n < 1024 * 1024 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 / 1024).toFixed(1)} MB`
const prettyDate = (value: string) => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))
const timeGreeting = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return 'Good morning'
  if (hour >= 12 && hour < 17) return 'Hello'
  return 'Good evening'
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [healthError, setHealthError] = useState('')
  const [summary, setSummary] = useState<IndexSummary | null>(null)
  const [job, setJob] = useState<IndexStatus | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [folder, setFolder] = useState('')
  const [consented, setConsented] = useState(false)
  const [userName, setUserName] = useState(() => { try { return localStorage.getItem('sift-user-name') ?? 'Gab' } catch { return 'Gab' } })
  const [onboardingComplete, setOnboardingComplete] = useState(() => { try { return localStorage.getItem('sift-onboarded') === 'true' } catch { return false } })
  // Keep access history in memory only; file names and paths can be sensitive.
  const [fileHistory, setFileHistory] = useState<FileHistoryItem[]>([])
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
  const [conversationStarted, setConversationStarted] = useState(false)
  const [panelExpanded, setPanelExpanded] = useState(false)
  const conversationRef = useRef<HTMLElement | null>(null)
  const themeButtonRef = useRef<HTMLButtonElement | null>(null)
  const previewDialogRef = useRef<HTMLElement | null>(null)
  const previewReturnRef = useRef<HTMLElement | null>(null)
  const [darkMode, setDarkMode] = useState(() => {
    try {
      const stored = localStorage.getItem('sift-theme')
      if (stored) return stored === 'dark'
      return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
    } catch { return false }
  })
  const searchSeq = useRef(0)

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
    try { localStorage.setItem('sift-theme', darkMode ? 'dark' : 'light') } catch { /* theme still applies for this session */ }
  }, [darkMode])

  useEffect(() => {
    try { localStorage.removeItem('sift-file-history') } catch { /* access history is session-only */ }
  }, [])

  useEffect(() => {
    if (!panelExpanded) return
    const collapseOnOutsideClick = (event: PointerEvent) => {
      if (event.target instanceof Node && !conversationRef.current?.contains(event.target)) {
        setPanelExpanded(false)
        setControlsOpen(false)
      }
    }
    document.addEventListener('pointerdown', collapseOnOutsideClick)
    return () => document.removeEventListener('pointerdown', collapseOnOutsideClick)
  }, [panelExpanded])

  useEffect(() => {
    if (!preview) {
      previewReturnRef.current?.focus()
      return
    }
    const dialog = previewDialogRef.current
    const closeButton = dialog?.querySelector<HTMLButtonElement>('.preview-header .icon-button')
    closeButton?.focus()
    const keepDialogAccessible = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setPreview(null); return }
      if (event.key !== 'Tab' || !dialog) return
      const focusable = [...dialog.querySelectorAll<HTMLElement>('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"])')]
      if (focusable.length === 0) { event.preventDefault(); dialog.focus(); return }
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', keepDialogAccessible)
    return () => document.removeEventListener('keydown', keepDialogAccessible)
  }, [preview])

  function toggleTheme() {
    const nextDarkMode = !darkMode
    const documentWithTransitions = document as Document & {
      startViewTransition?: (update: () => void) => { finished: Promise<void> }
    }
    const startViewTransition = documentWithTransitions.startViewTransition
    if (!startViewTransition) { setDarkMode(nextDarkMode); return }

    const buttonBounds = themeButtonRef.current?.getBoundingClientRect()
    if (buttonBounds) {
      document.documentElement.style.setProperty('--theme-origin-x', `${buttonBounds.left + buttonBounds.width / 2}px`)
      document.documentElement.style.setProperty('--theme-origin-y', `${buttonBounds.top + buttonBounds.height / 2}px`)
    }
    document.documentElement.dataset.themeTransition = nextDarkMode ? 'dark' : 'light'
    const transition = startViewTransition.call(document, () => flushSync(() => setDarkMode(nextDarkMode)))
    const clearTransition = () => {
      delete document.documentElement.dataset.themeTransition
      document.documentElement.style.removeProperty('--theme-origin-x')
      document.documentElement.style.removeProperty('--theme-origin-y')
    }
    void transition.finished.then(clearTransition, clearTransition)
  }

  const refresh = useCallback(async () => {
    try {
      const [h, i] = await Promise.all([api.health(), api.index()])
      setHealth(h); setHealthError(''); setSummary(i)
      setFolder(current => current || i.root || '')
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

  function finishOnboarding(e: FormEvent) {
    e.preventDefault()
    const name = userName.trim()
    const root = folder.trim()
    if (!name) { setActionError('Enter a name to personalize Sift.'); return }
    if (!root) { setActionError('Choose a folder for Sift to index.'); return }
    if (!consented) { setActionError('Confirm that Sift may read this folder to build a local index.'); return }
    try {
      localStorage.setItem('sift-user-name', name)
      localStorage.setItem('sift-onboarded', 'true')
    } catch { /* onboarding still completes for this session */ }
    setUserName(name)
    setFolder(root)
    setOnboardingComplete(true)
    setControlsOpen(true)
    setPanelExpanded(true)
    setActionError('')
  }

  function rememberFile(item: SearchResult, action: FileHistoryItem['action']) {
    setFileHistory(previous => [{ file_id: item.file_id, name: item.name, relative_path: item.relative_path, file_type: item.file_type, size_bytes: item.size_bytes, modified_at: item.modified_at, last_accessed: new Date().toISOString(), action }, ...previous.filter(file => file.file_id !== item.file_id)].slice(0, 100))
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
    setConversationStarted(true)
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
    if (document.activeElement instanceof HTMLElement) previewReturnRef.current = document.activeElement
    setActionError(''); setPreview(null)
    try { setPreview(await api.preview(item.file_id)); rememberFile(item, 'Previewed') } catch (e) { setActionError(message(e)) }
  }

  async function fileAction(item: SearchResult, action: 'open' | 'reveal') {
    setActionError(''); setNotice('')
    try {
      await (action === 'open' ? api.openFile(item.file_id) : api.revealFile(item.file_id))
      rememberFile(item, action === 'open' ? 'Opened' : 'Revealed')
      setNotice(fixtureMode ? `Sample ${action} action simulated for ${item.name}.` : action === 'open' ? `Opened ${item.name}.` : `Showing ${item.name} in its folder.`)
    }
    catch (e) { setActionError(message(e)) }
  }

  const indexed = Boolean(summary?.root)
  const setupRequired = health?.status === 'setup_required' || health?.embedding.ready === false

  return <div className="app-shell">
    {fixtureMode && <div className="fixture-banner" role="status"><strong>Development fixture mode is ON</strong><span>All displayed files and actions are synthetic. This mode is unavailable in production builds.</span></div>}
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Sift home"><span className="brand-mark"><SiftLogo /></span><span>Sift</span></a>
      <div className="header-actions">
        <button ref={themeButtonRef} className="theme-toggle" type="button" onClick={toggleTheme} aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'} title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}><ThemeIcon darkMode={darkMode} /></button>
        <button className="icon-button" aria-label="Retry connection" onClick={() => void refresh()} title="Refresh connection">↻</button>
      </div>
    </header>

    <main id="top" className="chat-main">
      {!onboardingComplete ? <section className="onboarding-page">
        <span className="onboarding-step">WELCOME TO SIFT · SETUP</span>
        <h1>Let’s make this yours.</h1>
        <p className="onboarding-intro">Choose a name and one folder to start. Sift searches locally and never changes your original files.</p>
        <form className="onboarding-form" onSubmit={finishOnboarding}>
          <label htmlFor="user-name">What should we call you?</label>
          <input id="user-name" value={userName} onChange={event => setUserName(event.target.value)} placeholder="Your name" autoComplete="given-name" maxLength={60} />
          <label htmlFor="onboarding-folder">Which folder may Sift access?</label>
          <div className="path-row"><input id="onboarding-folder" value={folder} onChange={event => setFolder(event.target.value)} placeholder={health?.platform === 'windows' ? 'C:\\Users\\you\\Documents' : '/Users/you/Documents'} autoComplete="off" /><button type="button" className="secondary-button" onClick={() => void chooseFolder()} disabled={!health?.capabilities.folder_picker}>Browse</button></div>
          {!health?.capabilities.folder_picker && <p className="field-hint">Enter the full folder path. The folder picker is unavailable.</p>}
          <label className="consent onboarding-consent"><input type="checkbox" checked={consented} onChange={event => setConsented(event.target.checked)} /><span>I allow Sift to read this folder to build a private, local index. I can change the folder later.</span></label>
          {actionError && <p className="inline-error" role="alert">{actionError}</p>}
          {healthError && <p className="inline-error" role="alert">{healthError}</p>}
          {setupRequired && health && <div className="onboarding-model-note"><strong>Local model setup needed before indexing</strong>{health.setup_steps.map((step, index) => <p key={index}>{step}</p>)}</div>}
          <button className="primary-button onboarding-continue" type="submit">Continue to Sift <span aria-hidden="true">→</span></button>
        </form>
        <p className="onboarding-privacy"><span className="footer-dot" /> Your name is saved on this device. Your files stay in the folder you choose.</p>
      </section> : <>
      <section className="chat-hero">
        <div className={`sift-orb${searching ? ' is-searching' : ''}`} role="img" aria-label={searching ? 'Sift is searching your files' : 'Sift search orb'}><SiftOrb /></div>
        <p className="greeting">{timeGreeting()}, {userName}!</p>
        <h1>Whatcha <em>lookin' at?</em></h1>
        <p>Describe what you want to see</p>
      </section>

      <section ref={conversationRef} className={`conversation-shell ${panelExpanded ? 'expanded' : 'compact'}`} aria-label="Sift file search" onClick={() => setPanelExpanded(true)}>
        <div className="conversation-feed">
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

          {!conversationStarted && !jobId && <div className="welcome-message"><span className="assistant-avatar small-avatar"><SiftLogo /></span><div className="welcome-copy"><strong>Describe a file you remember</strong><p>I’ll find matching files and show the excerpts that match.</p>{fixtureMode && <div className="sample-searches"><span>Synthetic samples · choose one to try</span><div className="suggestion-list">{['Laptop repair receipt', 'Biology study notes', 'Kyoto hotel booking', 'Monthly budget', 'Garden notes'].map(sample => <button key={sample} type="button" onClick={() => setQuery(sample)}>{sample}</button>)}</div></div>}</div></div>}

          {actionError && <p className="inline-error" role="alert">{actionError}</p>}
          {job && <div className="progress-card" role="status" aria-live="polite"><div className="progress-heading">{!terminal.has(job.state) && <span className="loader" />}<strong>{terminal.has(job.state) ? job.state === 'completed' ? 'Indexing complete' : `Index ${job.state}` : phaseLabel(job.phase)}</strong><span className="progress-count">{job.processed} processed · {job.searchable} searchable</span>{!terminal.has(job.state) && <button className="text-button" onClick={() => void cancelIndex()} disabled={cancelRequested}>{cancelRequested ? 'Cancel requested' : 'Cancel'}</button>}</div>{job.current_file && <div className="current-file">{job.current_file}</div>}{!terminal.has(job.state) && job.phase !== 'discovering' && <div className="progress-track"><span style={{ width: job.discovered ? `${Math.min(100, job.processed / job.discovered * 100)}%` : '8%' }} /></div>}<div className="progress-foot">{job.discovered > 0 ? `${job.discovered} files found so far` : 'Finding files…'}{job.skipped > 0 && ` · ${job.skipped} skipped`}{job.failed > 0 && ` · ${job.failed} failed`}</div>{terminal.has(job.state) && job.errors.length > 0 && <div className="job-terminal"><details><summary>{job.errors.length} file issue(s)</summary><ul>{job.errors.map((err, i) => <li key={i}>{err.relative_path}: {err.message}</li>)}</ul></details></div>}</div>}

          {searchInfo && results && <div className="search-turn">
            <div className="user-message"><span>You</span><p>{searchedTerm}</p></div>
            {searchInfo.indexing && <p className="indexing-note">Searching {searchInfo.count} indexed files while indexing continues.</p>}
            <div className="results-head" aria-live="polite" aria-atomic="true"><div><span className="result-kicker">{results.length ? `${results.length} MATCH${results.length === 1 ? '' : 'ES'}` : 'NO MATCHES'}</span><h3>{results.length ? 'Files that match' : 'No matching files found'}</h3></div><span className="search-time">{searchInfo.elapsed} ms</span></div>
            {results.length === 0 && <div className="empty-state"><span className="empty-symbol">⌕</span><p>Try another detail, or check that this folder has been indexed.</p></div>}
            {results.length > 0 && <div className="results-list">{results.map(item => <article className="result-card" key={item.file_id}><div className="file-type">{item.file_type.slice(0, 4).toUpperCase()}</div><div className="result-main"><div className="result-title-row"><h3>{item.name}</h3><span className="match-pill">{item.match_kind}</span></div><p className="relative-path" title={item.relative_path}>{item.relative_path}</p><blockquote>{item.snippet}{item.location.page && <span className="page-label"> · page {item.location.page}</span>}</blockquote><div className="result-details"><span>{formatBytes(item.size_bytes)}</span><span>Modified {prettyDate(item.modified_at)}</span></div><div className="result-actions"><button className="primary-button small" onClick={() => void fileAction(item, 'open')} disabled={!health?.capabilities.open_file}>Open file <span>↗</span></button><button className="secondary-button small" onClick={() => void showPreview(item)}>Preview</button><button className="text-button" onClick={() => void fileAction(item, 'reveal')} disabled={!health?.capabilities.reveal_file}>Show in folder</button></div></div></article>)}</div>}
          </div>}
          {notice && <p className="success-note" role="status">{notice}</p>}
        </div>

        <form className="chat-composer" onSubmit={doSearch}>
          <label className="sr-only" htmlFor="search-message">Describe the file you want to find</label>
          <div className="composer-input-row"><input id="search-message" value={query} onChange={e => setQuery(e.target.value)} placeholder="Describe the file or detail you remember…" maxLength={500} /><button className="send-button" type="submit" aria-label="Search files" disabled={searching || !health || !indexed || setupRequired}>{searching ? <span className="loader" /> : query.trim() ? <svg className="sieve-icon" viewBox="0 0 28 28" aria-hidden="true"><defs><clipPath id="sieve-bowl-clip"><path d="M3.5 10.5Q14 6.5 24.5 10.5L21.5 18Q14 22 6.5 18Z" /></clipPath></defs><g className="sieve-basket"><path className="sieve-bowl" d="M3.5 10.5Q14 6.5 24.5 10.5L21.5 18Q14 22 6.5 18Z" fill="currentColor" fillOpacity=".12" stroke="currentColor" strokeWidth="1.35" /><g className="sieve-grid" clipPath="url(#sieve-bowl-clip)" fill="none" stroke="currentColor" strokeWidth=".85"><path d="M7 8Q9 13 9 20M11 7Q13 13 13 21M16 7Q15 14 16 21M20 8Q18 14 20 20M4 12Q14 15 24 12M5 15Q14 18 23 15" /></g><path className="sieve-rim" d="M3.5 10.5Q14 6.5 24.5 10.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /><path className="sieve-rim-glint" d="M5.4 9.9Q11 7.8 16.2 8.1" fill="none" stroke="white" strokeOpacity=".68" strokeWidth=".65" strokeLinecap="round" /><g className="sieve-handle"><path d="M19.4 17.2 25.2 23" fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" /><path d="M20 17.8 24.8 22.6" fill="none" stroke="white" strokeOpacity=".5" strokeWidth=".8" strokeLinecap="round" /></g></g></svg> : <span className="send-arrow">↑</span>}</button></div>
          <div className="composer-tools"><button type="button" className="tool-button" onClick={() => setControlsOpen(open => !open)} aria-expanded={controlsOpen} aria-controls={controlsOpen ? 'search-controls' : undefined}><span aria-hidden="true">＋</span> Folder &amp; filters</button><span>{indexed ? `Searching ${summary?.searchable_files} indexed files` : 'Choose a folder to get started'}</span><span className="composer-privacy"><span className="footer-dot" /> On-device</span></div>
        </form>
      </section>

      <HomeDashboard summary={summary} history={fileHistory} />
      <footer><span className="footer-dot" aria-hidden="true" /><span>Private, on-device search</span></footer>
      </>}
    </main>

    {preview && <div className="modal-backdrop" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget) setPreview(null) }}><section ref={previewDialogRef} className="preview-modal" role="dialog" aria-modal="true" aria-labelledby="preview-title" tabIndex={-1}><div className="preview-header"><div><span className="result-kicker">SOURCE PREVIEW</span><h2 id="preview-title">{preview.name}</h2><p>{preview.relative_path}</p></div><button className="icon-button" aria-label="Close preview" onClick={() => setPreview(null)}>×</button></div><div className="preview-body">{preview.text ? <pre>{preview.text}</pre> : <p className="muted">No extracted text is available for preview. You can open the original file instead.</p>}</div>{preview.truncated && <p className="preview-truncated">Preview shortened. The full file remains unchanged.</p>}</section></div>}
  </div>
}

function message(error: unknown) { return error instanceof ApiFailure ? error.message : error instanceof Error ? error.message : 'Something went wrong. Please try again.' }
function phaseLabel(phase: IndexStatus['phase']) { return ({ discovering: 'Finding files', extracting: 'Reading content', embedding: 'Building local search', finished: 'Wrapping up' })[phase] }
