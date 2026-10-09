import threading
import time
import httpx
import numpy as np

class ModelUnavailable(Exception):
    pass

class Embedder:
    """Loopback only, no environment proxies, redirects, downloads or mock fallback."""
    def __init__(self, model):
        self.model = model
        self.client = httpx.Client(base_url='http://127.0.0.1:11434', trust_env=False, timeout=60, follow_redirects=False)
        self.lock = threading.Lock()
        self.embedding_calls = 0
        self.chunks_embedded = 0
        self.last_call_ms = None
        self.last_load_ms = None

    def ready(self):
        try:
            r = self.client.get('/api/tags')
            r.raise_for_status()
            return any(m['name'] == self.model for m in r.json()['models'])
        except (httpx.HTTPError, ValueError, KeyError):
            return False

    def embed(self, texts, query=False):
        prefix = 'search_query: ' if query else 'search_document: '
        with self.lock:
            start = time.perf_counter()
            try:
                r = self.client.post('/api/embed', json={
                    'model': self.model, 'input': [prefix + t for t in texts],
                    'truncate': False, 'options': {'num_ctx': 2048}, 'keep_alive': '5m'})
                r.raise_for_status()
                payload = r.json()
                self.last_load_ms = payload.get('load_duration', 0) / 1000000
                vectors = np.asarray(payload['embeddings'], dtype=np.float32)
                if vectors.ndim != 2 or vectors.shape[0] != len(texts) or not np.isfinite(vectors).all():
                    raise ValueError('Invalid embedding dimensions or values')
                norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                if (norms == 0).any():
                    raise ValueError('Empty embedding')
                vectors /= norms
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                raise ModelUnavailable('Local embedding call failed. Check Ollama and the installed model; no cloud or keyword fallback was used.') from exc
            self.embedding_calls += 1
            if not query:
                self.chunks_embedded += len(texts)
            self.last_call_ms = round((time.perf_counter() - start) * 1000)
            return vectors

    def close(self):
        self.client.close()
