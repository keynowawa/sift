import hashlib
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .ai.ollama import ModelUnavailable
from .db import now
from .extractors import Unsupported, chunks, file_type
from .security import ApiError, scoped_file, validate_root

class JobCancelled(Exception):
    """Stop between batches without committing a partially embedded file."""


class Scanner:
    def __init__(self, config, db, embedder, extractor):
        self.config, self.db, self.embedder, self.extractor = config, db, embedder, extractor
        self.lock = threading.RLock()
        self.cancel_event = threading.Event()
        self.thread = None

    def start(self, root, replace):
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise ApiError('INDEX_BUSY', 'An indexing job is already active.', 409)
            root = validate_root(root, self.config.data_dir)
            old = self.db.meta('root')
            if old and old != str(root) and not replace:
                raise ApiError('ROOT_CONFIRMATION_REQUIRED', 'Confirm replacement before changing the indexed folder.', 409)
            if not self.embedder.ready():
                raise ApiError('MODEL_UNAVAILABLE', 'Ollama or the embedding model is unavailable.', 503, True)
            if old != str(root):
                self.db.reset()
                self.db.set_meta('root', str(root))
            self.cancel_event.clear()
            body = dict(job_id=uuid.uuid4().hex, state='queued', phase='discovering', discovered=0,
                processed=0, searchable=0, skipped=0, failed=0, current_file=None, elapsed_ms=0, errors=[])
            self.db.save_job(body)
            self.thread = threading.Thread(target=self.run, args=(root, body), daemon=True, name='sift-indexer')
            self.thread.start()
            return body['job_id']

    def cancel(self, job_id):
        with self.lock:
            job = self.db.job(job_id)
            if job is None:
                raise ApiError('JOB_NOT_FOUND', 'Indexing job not found.', 404)
            if job['state'] not in ('queued', 'running'):
                raise ApiError('JOB_NOT_ACTIVE', 'This indexing job is no longer active.', 409)
            self.cancel_event.set()

    def reset(self):
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise ApiError('INDEX_BUSY', 'Cancel indexing and wait for completion before resetting.', 409)
            self.db.reset()
            with self.embedder.lock:
                self.embedder.embedding_calls = self.embedder.chunks_embedded = 0
                self.embedder.last_call_ms = None
            self.extractor.ocr_files = 0

    def run(self, root, body):
        start = time.perf_counter()
        def save():
            body['elapsed_ms'] = round((time.perf_counter() - start) * 1000)
            self.db.save_job(body)
        def error(relative, message):
            self.db.save_job_error(body['job_id'], relative, message)
            if len(body['errors']) < 100:
                body['errors'].append(dict(relative_path=relative, message=message))
        try:
            body['state'] = 'running'; save()
            found = []
            discovery_error = False
            def walk_error(exc):
                nonlocal discovery_error
                discovery_error = True
                error(str(Path(exc.filename).relative_to(root)), str(exc))
            for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
                if self.cancel_event.is_set():
                    break
                folder = Path(directory)
                dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not (folder/d).is_symlink()
                    and not (folder/d).resolve().is_relative_to(self.config.data_dir)
                    and d.lower() not in {'node_modules', '__pycache__', '$recycle.bin', 'system volume information'})
                for name in sorted(names):
                    if not name.startswith('.') and not (folder/name).is_symlink():
                        found.append((folder/name).relative_to(root).as_posix())
                body['discovered'] = len(found); save()
            # Never prune on incomplete discovery or a cancelled job.
            if not self.cancel_event.is_set() and not discovery_error:
                self.db.prune(set(found))
            for relative in found:
                if self.cancel_event.is_set():
                    break
                body['current_file'] = relative
                body['phase'] = 'extracting'; save()
                path = root / relative
                old = self.db.by_path(relative)
                record = dict(id=old['id'] if old else uuid.uuid4().hex, rel_path=relative, name=path.name,
                    kind=file_type(path), size=0, mtime_ns=0, modified_at=now(),
                    sha256='', signature=self.config.signature, status='skipped', error=None, text='', truncated=0)
                parts = []
                aborted = False
                try:
                    path = scoped_file(root, relative)
                    stat = path.stat()
                    record.update(size=stat.st_size, mtime_ns=stat.st_mtime_ns,
                        modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace('+00:00','Z'))
                    if stat.st_size > self.config.max_file_bytes:
                        raise Unsupported('File exceeds the 25 MB extraction limit')
                    digest = hashlib.sha256()
                    with path.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024*1024), b''):
                            digest.update(block)
                    record['sha256'] = digest.hexdigest()
                    if old and old['sha256'] == record['sha256'] and old['signature'] == self.config.signature and old['status'] == 'indexed':
                        body['searchable'] += 1
                        with self.db.connect() as con:
                            con.execute('UPDATE files SET size=?,mtime_ns=?,modified_at=? WHERE id=?',
                                (stat.st_size, stat.st_mtime_ns, record['modified_at'], old['id']))
                        continue
                    if old:
                        self.db.invalidate(old['id'])
                    pages = self.extractor.extract(path, self.config.max_text_chars + 1)
                    joined = '\n'.join(text for _,text in pages)
                    record['truncated'] = int(len(joined) > self.config.max_text_chars)
                    record['text'] = joined[:self.config.max_text_chars]
                    remaining = self.config.max_text_chars
                    bounded = []
                    for page,text in pages:
                        bounded.append((page,text[:remaining])); remaining -= len(text[:remaining])
                        if remaining <= 0: break
                    pieces = list(chunks(bounded, self.config.chunk_chars, self.config.chunk_overlap))
                    body['phase'] = 'embedding'; save()
                    for offset in range(0, len(pieces), 8):
                        if self.cancel_event.is_set():
                            raise JobCancelled()
                        batch = pieces[offset:offset+8]
                        vectors = self.embedder.embed([text for _,text in batch])
                        parts.extend((page,text,vec) for (page,text),vec in zip(batch,vectors))
                    after = path.stat()
                    if (after.st_size,after.st_mtime_ns) != (stat.st_size,stat.st_mtime_ns):
                        raise OSError('File changed while being indexed; rescan it')
                    record['status'] = 'indexed'
                    body['searchable'] += 1
                except JobCancelled:
                    aborted = True
                    break
                except Unsupported as exc:
                    record['status'], record['error'] = 'skipped', str(exc)
                    body['skipped'] += 1; error(relative,str(exc)); parts = []
                except Exception as exc:
                    record['status'], record['error'], record['text'] = 'failed', str(exc), ''
                    body['failed'] += 1; error(relative,str(exc)); parts = []
                    if isinstance(exc,ModelUnavailable):
                        self.db.save_file(record,parts)
                        body['processed'] += 1
                        body['state'] = 'failed'
                        break
                finally:
                    # Cached files also count as processed; fatal model failure handled above.
                    if body['state'] != 'failed' and not aborted:
                        body['processed'] += 1
                    save()
                self.db.save_file(record,parts)
                self.db.set_meta('last_updated',now())
            if body['state'] != 'failed':
                body['state'] = 'cancelled' if self.cancel_event.is_set() else 'completed'
        except Exception as exc:
            body['state'] = 'failed'
            error(body['current_file'] or '',str(exc))
        finally:
            body['phase'] = 'finished'; body['current_file'] = None; save()

    def close(self):
        self.cancel_event.set()
        if self.thread:
            self.thread.join(timeout=65)
