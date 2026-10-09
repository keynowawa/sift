import { useState } from 'react'
import type { IndexSummary } from './types'

export type FileHistoryItem = {
  file_id: string
  name: string
  relative_path: string
  file_type: string
  size_bytes: number
  modified_at: string
  last_accessed: string
  action: 'Opened' | 'Previewed' | 'Revealed'
}

type Props = { summary: IndexSummary | null; history: FileHistoryItem[] }
type Panel = 'storage' | 'recent' | 'older'

const dateLabel = (value: string) => new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value))
const timeLabel = (value: string) => new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(value))

export default function HomeDashboard({ summary, history }: Props) {
  const [expanded, setExpanded] = useState<Panel | null>(null)
  const [sortBy, setSortBy] = useState<'age' | 'access'>('age')
  const sortedHistory = [...history].sort((a, b) => sortBy === 'age'
    ? Date.parse(a.modified_at) - Date.parse(b.modified_at)
    : Date.parse(a.last_accessed) - Date.parse(b.last_accessed))
  const toggle = (panel: Panel) => setExpanded(current => current === panel ? null : panel)

  return <section className="home-summaries" aria-label="Library overview">
    <article className={`summary-panel ${expanded === 'storage' ? 'is-open' : ''}`}>
      <button className="summary-panel-toggle" type="button" onClick={() => toggle('storage')} aria-expanded={expanded === 'storage'}>
        <span><h2 className="summary-title">Available storage</h2></span><span className="panel-chevron" aria-hidden="true">{expanded === 'storage' ? '−' : '+'}</span>
      </button>
      <div className="storage-overview">
        <div className="storage-donut" role="img" aria-label="Storage breakdown is unavailable"><span>—</span></div>
        <div className="storage-breakdown">
          {['Documents', 'Photos', 'Other files'].map((label, index) => <div className="storage-row" key={label}><span><i className={`storage-swatch swatch-${index}`} />{label}</span><strong>—</strong></div>)}
        </div>
      </div>
      <p className="summary-caption">Free space and file breakdown aren’t available yet.</p>
      {expanded === 'storage' && <div className="summary-details"><p>Sift’s local API doesn’t report device free space or totals by file type yet, so this panel leaves the figures blank.</p>{summary?.root && <p className="summary-source">Current library: {summary.indexed_files} indexed files · {summary.searchable_files} searchable</p>}</div>}
    </article>

    <article className={`summary-panel ${expanded === 'recent' ? 'is-open' : ''}`}>
      <button className="summary-panel-toggle" type="button" onClick={() => toggle('recent')} aria-expanded={expanded === 'recent'}>
        <span><h2 className="summary-title">Recently accessed</h2></span><span className="panel-chevron" aria-hidden="true">{expanded === 'recent' ? '−' : '+'}</span>
      </button>
      {history.length ? <div className="history-list">{history.slice(0, expanded === 'recent' ? 20 : 3).map(file => <div className="history-row" key={file.file_id}><span className="history-file-icon">{file.file_type.slice(0, 3).toUpperCase()}</span><span className="history-file"><strong title={file.name}>{file.name}</strong><small>{file.action} · {timeLabel(file.last_accessed)}</small></span></div>)}</div> : <p className="summary-caption">Files you open or preview in Sift will appear here.</p>}
      {expanded === 'recent' && <div className="summary-details"><p>This session-only history records files opened, revealed, or previewed through Sift. It clears when you close or refresh the app.</p></div>}
    </article>

    <article className={`summary-panel ${expanded === 'older' ? 'is-open' : ''}`}>
      <button className="summary-panel-toggle" type="button" onClick={() => toggle('older')} aria-expanded={expanded === 'older'}>
        <span><h2 className="summary-title">Older files</h2></span><span className="panel-chevron" aria-hidden="true">{expanded === 'older' ? '−' : '+'}</span>
      </button>
      {expanded === 'older' && <label className="history-sort">Sort by <select value={sortBy} onChange={event => setSortBy(event.target.value as 'age' | 'access')}><option value="age">Oldest modified</option><option value="access">Least recently accessed</option></select></label>}
      {sortedHistory.length ? <div className="history-list">{sortedHistory.slice(0, expanded === 'older' ? 20 : 3).map(file => <div className="history-row" key={file.file_id}><span className="history-file-icon">{file.file_type.slice(0, 3).toUpperCase()}</span><span className="history-file"><strong title={file.name}>{file.name}</strong><small>Modified {dateLabel(file.modified_at)} · Last accessed {dateLabel(file.last_accessed)}</small></span></div>)}</div> : <p className="summary-caption">Older files will show here after you access them in Sift.</p>}
      {expanded === 'older' && <div className="summary-details"><p>This list uses file modification dates and Sift access history. Sift can only show files you’ve opened, revealed, or previewed here.</p></div>}
    </article>
  </section>
}
