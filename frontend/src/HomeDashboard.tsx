import { useState } from 'react'
import { fixtureMode, fixtureStorageFiles } from './api'
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
const formatBytes = (bytes: number) => bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(bytes < 10 * 1024 ? 1 : 0)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
const bubblePositions = [
  { left: '34%', top: '25%' }, { left: '3%', top: '26%' }, { left: '75%', top: '4%' },
  { left: '75%', top: '55%' }, { left: '24%', top: '67%' },
]

export default function HomeDashboard({ summary, history }: Props) {
  const [expanded, setExpanded] = useState<Panel | null>(null)
  const [sortBy, setSortBy] = useState<'age' | 'access'>('age')
  const sortedHistory = [...history].sort((a, b) => sortBy === 'age'
    ? Date.parse(a.modified_at) - Date.parse(b.modified_at)
    : Date.parse(a.last_accessed) - Date.parse(b.last_accessed))
  const storageFiles = fixtureMode ? fixtureStorageFiles : []
  const typeTotals = [...storageFiles.reduce((totals, file) => totals.set(file.file_type.toUpperCase(), (totals.get(file.file_type.toUpperCase()) ?? 0) + file.size_bytes), new Map<string, number>())]
    .map(([name, size]) => ({ name, size })).sort((a, b) => b.size - a.size)
  const folderTotals = [...storageFiles.reduce((totals, file) => {
    const separator = Math.max(file.relative_path.lastIndexOf('/'), file.relative_path.lastIndexOf('\\'))
    const folder = separator > 0 ? file.relative_path.slice(0, separator) : 'Root'
    totals.set(folder, (totals.get(folder) ?? 0) + file.size_bytes)
    return totals
  }, new Map<string, number>())].map(([name, size]) => ({ name, size })).sort((a, b) => b.size - a.size)
  const largestFolderSize = folderTotals[0]?.size ?? 0
  const toggle = (panel: Panel) => setExpanded(current => current === panel ? null : panel)

  return <section className="home-summaries" aria-label="Library overview">
    <article className={`summary-panel storage-panel ${expanded === 'storage' ? 'is-open' : ''}`}>
      <button className="summary-panel-toggle" type="button" onClick={() => toggle('storage')} aria-expanded={expanded === 'storage'}>
        <span><h2 className="summary-title">Available storage</h2></span><span className="panel-chevron" aria-hidden="true">{expanded === 'storage' ? '−' : '+'}</span>
      </button>
      <div className="storage-overview">
        <div className="storage-donut" role="img" aria-label="Storage capacity data is unavailable"><span>—</span></div>
        <div className="storage-breakdown">
          {['Documents', 'Photos', 'Other files'].map((label, index) => <div className="storage-row" key={label}><span><i className={`storage-swatch swatch-${index}`} />{label}</span><strong>—</strong></div>)}
        </div>
      </div>
      <p className="summary-caption">Free space and file breakdown aren’t available yet.</p>
      {expanded === 'storage' && <div className="storage-expanded">
        {fixtureMode && <p className="storage-fixture-note">Demo breakdown · {storageFiles.length} sample files</p>}
        <div className="storage-expanded-top">
          <section className="storage-size-section" aria-labelledby="storage-types-title">
            <h3 id="storage-types-title">File types <span>by size</span></h3>
            {typeTotals.length ? <div className="storage-size-list">{typeTotals.map(item => <div className="storage-size-row" key={item.name}><strong>{item.name}</strong><span className="storage-size-bar"><i style={{ width: `${Math.max(4, item.size / typeTotals[0].size * 100)}%` }} /></span><small>{formatBytes(item.size)}</small></div>)}</div> : <p className="storage-empty-detail">File type totals aren’t available from the local index yet.</p>}
          </section>
          <section className="storage-folder-section" aria-labelledby="largest-folders-title">
            <h3 id="largest-folders-title">Largest folders <span>map</span></h3>
            <div className="storage-folder-map" role="img" aria-label={folderTotals.length ? 'Largest indexed folders, sized by sample file bytes' : 'Folder size map unavailable from the local index'}>
              {folderTotals.length ? folderTotals.slice(0, 5).map((folder, index) => {
                const diameter = Math.round(48 + Math.sqrt(folder.size / largestFolderSize) * 62)
                return <span className={`folder-bubble folder-bubble-${index}`} key={folder.name} title={`${folder.name} · ${formatBytes(folder.size)}`} style={{ ...bubblePositions[index], width: diameter, height: diameter }}><span>{folder.name}</span><small>{formatBytes(folder.size)}</small></span>
              }) : <span className="folder-map-empty">Folder sizes<br />unavailable</span>}
            </div>
          </section>
        </div>
        <section className="storage-size-section storage-folders-list" aria-labelledby="storage-folders-title">
          <h3 id="storage-folders-title">Folders <span>by size</span></h3>
          {folderTotals.length ? <ol className="storage-folder-list">{folderTotals.map(folder => <li key={folder.name}><span>{folder.name}</span><i><b style={{ width: `${Math.max(4, folder.size / largestFolderSize * 100)}%` }} /></i><strong>{formatBytes(folder.size)}</strong></li>)}</ol> : <p className="storage-empty-detail">Folder size totals aren’t available from the local index yet.</p>}
        </section>
        <div className="summary-details"><p>{fixtureMode ? 'These size rankings use the five synthetic files in the preview; actual drive capacity is not represented.' : 'Sift’s local API does not currently expose total drive capacity or file and folder size rankings.'}</p>{summary?.root && <p className="summary-source">Current library: {summary.indexed_files} indexed files · {summary.searchable_files} searchable</p>}</div>
      </div>}
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
