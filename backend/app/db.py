import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

class Database:
    def __init__(self, data_dir):
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / 'sift.sqlite3'
        self.lock = threading.RLock()
        with self.connect() as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY, rel_path TEXT UNIQUE, name TEXT, kind TEXT,
                    size INTEGER, mtime_ns INTEGER, modified_at TEXT, sha256 TEXT,
                    signature TEXT, status TEXT, error TEXT, text TEXT, truncated INTEGER);
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY, file_id TEXT REFERENCES files(id) ON DELETE CASCADE,
                    page INTEGER, text TEXT, vector TEXT);
                CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, body TEXT);
                CREATE TABLE IF NOT EXISTS job_errors (job_id TEXT, relative_path TEXT, message TEXT);
            ''')
            for row in con.execute('SELECT id, body FROM jobs').fetchall():
                body = json.loads(row['body'])
                if body['state'] in ('running', 'queued'):
                    body['state'] = 'interrupted'
                    con.execute('UPDATE jobs SET body=? WHERE id=?', (json.dumps(body), row['id']))

    @contextmanager
    def connect(self):
        with self.lock:
            con = sqlite3.connect(self.path, timeout=10)
            con.row_factory = sqlite3.Row
            con.execute('PRAGMA foreign_keys=ON')
            try:
                yield con
                con.commit()
            except Exception:
                con.rollback()
                raise
            finally:
                con.close()

    def meta(self, key):
        with self.connect() as con:
            row = con.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
            return row['value'] if row else None

    def set_meta(self, key, value):
        with self.connect() as con:
            con.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, value))

    def summary(self, signature):
        with self.connect() as con:
            indexed = con.execute('SELECT COUNT(*) FROM files').fetchone()[0]
            searchable = con.execute("SELECT COUNT(*) FROM files WHERE status='indexed' AND signature=?", (signature,)).fetchone()[0]
            chunks = con.execute("SELECT COUNT(*) FROM chunks JOIN files ON files.id=chunks.file_id WHERE signature=? AND status='indexed'", (signature,)).fetchone()[0]
            jobs = [json.loads(r[0]) for r in con.execute('SELECT body FROM jobs')]
        active = next((j['job_id'] for j in jobs if j['state'] in ('queued', 'running')), None)
        return dict(root=self.meta('root'), indexed_files=indexed, searchable_files=searchable,
                    total_chunks=chunks, last_updated=self.meta('last_updated'), active_job_id=active)

    def save_job(self, body):
        with self.connect() as con:
            con.execute('INSERT OR REPLACE INTO jobs VALUES (?,?)', (body['job_id'], json.dumps(body)))

    def save_job_error(self, job_id, relative_path, message):
        with self.connect() as con:
            con.execute('INSERT INTO job_errors VALUES (?,?,?)', (job_id, relative_path, message))

    def job(self, job_id):
        with self.connect() as con:
            row = con.execute('SELECT body FROM jobs WHERE id=?', (job_id,)).fetchone()
            return json.loads(row['body']) if row else None

    def file(self, file_id):
        with self.connect() as con:
            row = con.execute('SELECT * FROM files WHERE id=?', (file_id,)).fetchone()
            return dict(row) if row else None

    def by_path(self, relative):
        with self.connect() as con:
            row = con.execute('SELECT * FROM files WHERE rel_path=?', (relative,)).fetchone()
            return dict(row) if row else None

    def save_file(self, record, parts):
        with self.connect() as con:
            # DELETE/INSERT is one transaction; old vectors cannot coexist with new content.
            con.execute('DELETE FROM files WHERE rel_path=?', (record['rel_path'],))
            columns = tuple(record)
            con.execute('INSERT INTO files ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')', tuple(record.values()))
            con.executemany('INSERT INTO chunks(file_id,page,text,vector) VALUES (?,?,?,?)',
                [(record['id'], page, text, json.dumps(vector.tolist())) for page, text, vector in parts])

    def invalidate(self, file_id):
        with self.connect() as con:
            con.execute('DELETE FROM chunks WHERE file_id=?', (file_id,))
            con.execute("UPDATE files SET status='pending', text='' WHERE id=?", (file_id,))

    def prune(self, existing):
        with self.connect() as con:
            for row in con.execute('SELECT id,rel_path FROM files').fetchall():
                if row['rel_path'] not in existing:
                    con.execute('DELETE FROM files WHERE id=?', (row['id'],))

    def search_rows(self, signature, kinds):
        with self.connect() as con:
            rows = con.execute('''SELECT files.*, chunks.text AS chunk_text, chunks.page, chunks.vector
                FROM chunks JOIN files ON files.id=chunks.file_id
                WHERE files.status='indexed' AND files.signature=?''', (signature,)).fetchall()
        return [dict(file_id=r['id'], name=r['name'], relative_path=r['rel_path'],
            file_type=r['kind'], size_bytes=r['size'], modified_at=r['modified_at'], mtime_ns=r['mtime_ns'],
            text=r['chunk_text'], page=r['page'], vector=json.loads(r['vector']))
            for r in rows if not kinds or r['kind'] in kinds]

    def reset(self):
        # DELETE journal mode, close each connection; no WAL sidecars are created.
        with self.connect() as con:
            con.execute('DELETE FROM chunks')
            con.execute('DELETE FROM files')
            con.execute('DELETE FROM jobs')
            con.execute('DELETE FROM job_errors')
            con.execute('DELETE FROM meta')
        with self.connect() as con:
            con.execute('VACUUM')
