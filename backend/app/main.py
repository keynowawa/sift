import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, JSONResponse
from . import desktop
from .ai.ollama import Embedder, ModelUnavailable
from .config import Config
from .db import Database
from .extractors import Extractor
from .retrieval import rank
from .scanner import Scanner
from .security import ApiError, check_request, scoped_file

class Body(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Empty(Body):
    pass

class Start(Body):
    root: str = Field(min_length=1)
    replace_index: StrictBool

class Cancel(Body):
    job_id: str

class Search(Body):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=20, strict=True)
    file_types: list[Literal['txt','md','pdf','png','jpg','jpeg']] = Field(default_factory=list)

    @field_validator('query')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('Query must contain text')
        return value.strip()

class Reset(Body):
    confirm: Literal[True]


def create_app(config=None, embedder=None, extractor=None):
    config = config or Config()
    @asynccontextmanager
    async def lifespan(app):
        app.state.config = config
        app.state.db = Database(config.data_dir)
        app.state.embedder = embedder or Embedder(config.model)
        app.state.extractor = extractor or Extractor()
        app.state.scanner = Scanner(config, app.state.db, app.state.embedder, app.state.extractor)
        yield
        app.state.scanner.close()
        app.state.embedder.close()

    app = FastAPI(title='Sift Local Search', lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware('http')
    async def local_only(request, call_next):
        try:
            check_request(request, config)
        except ApiError as exc:
            return JSONResponse(exc.body(), status_code=exc.status)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.exception_handler(ApiError)
    async def api_error(request, exc):
        return JSONResponse(exc.body(), status_code=exc.status)

    @app.exception_handler(ModelUnavailable)
    async def model_error(request, exc):
        return JSONResponse(ApiError('MODEL_UNAVAILABLE', str(exc),503,True).body(), status_code=503)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(ApiError('INVALID_INPUT','Invalid request fields or values.').body(),status_code=400)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse(ApiError('NOT_FOUND' if exc.status_code == 404 else 'HTTP_ERROR',str(exc.detail),exc.status_code).body(),status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        logging.exception('Unexpected backend error')
        return JSONResponse(ApiError('INTERNAL_ERROR','Unexpected backend error. Consult the local backend log.',500,True).body(),status_code=500)

    def state(request):
        return request.app.state

    def get_file(request, file_id):
        s = state(request)
        row = s.db.file(file_id)
        root = s.db.meta('root')
        if row is None or root is None:
            raise ApiError('FILE_NOT_FOUND','File not found in the active index.',404)
        path = scoped_file(root,row['rel_path'])
        return row,path

    @app.get('/api/health')
    def health(request: Request):
        s=state(request); ready=s.embedder.ready(); ocr=s.extractor.ocr_ready()
        steps=[]
        if not ready:
            steps=['Install Ollama from https://ollama.com/download if missing.', 'Start Ollama (ollama serve).', f'ollama pull {config.model}']
        if not ocr:
            steps.append('Install backend/requirements.txt to enable bundled local OCR. Text files remain supported.')
        return dict(status='ready' if ready else 'setup_required',platform=config.platform,
            embedding=dict(ready=ready,model=config.model),ocr=dict(ready=ocr),
            capabilities=dict(folder_picker=desktop.FOLDER_PICKER,open_file=config.platform!='other',reveal_file=config.platform!='other'),setup_steps=steps)

    @app.get('/api/index')
    def index(request: Request):
        return state(request).db.summary(config.signature)

    @app.post('/api/folder/pick')
    def pick(body: Empty):
        return {'path':desktop.pick_folder()}

    @app.post('/api/index/start', status_code=202)
    def start(body: Start, request: Request):
        return {'job_id':state(request).scanner.start(body.root, body.replace_index)}

    @app.get('/api/index/status')
    def status(job_id: str, request: Request):
        body=state(request).db.job(job_id)
        if body is None:
            raise ApiError('JOB_NOT_FOUND','Indexing job not found.',404)
        return body

    @app.post('/api/index/cancel')
    def cancel(body: Cancel, request: Request):
        state(request).scanner.cancel(body.job_id)
        return {'accepted':True}

    @app.post('/api/search')
    def search(body: Search, request: Request):
        s=state(request); start=time.perf_counter()
        # Always a genuine uncached local query call, including empty indexes.
        vector=s.embedder.embed([body.query],query=True)[0]
        rows=s.db.search_rows(config.signature,{'jpg' if t=='jpeg' else t for t in body.file_types})
        root=s.db.meta('root')
        eligible=[]
        for row in rows:
            try:
                path=scoped_file(root,row['relative_path'])
                stat=path.stat()
                if stat.st_size==row['size_bytes'] and stat.st_mtime_ns==row['mtime_ns']:
                    eligible.append(row)
            except (ApiError,OSError):
                continue
        hits=rank(body.query,vector,eligible,config.semantic_threshold)[:body.limit]
        results=[]
        for _,row,kind,_,_ in hits:
            results.append(dict(file_id=row['file_id'],name=row['name'],relative_path=row['relative_path'],
                file_type=row['file_type'],size_bytes=row['size_bytes'],modified_at=row['modified_at'],
                snippet=row['text'],location={'page':row['page']},match_kind=kind))
        summary=s.db.summary(config.signature)
        return dict(results=results,elapsed_ms=round((time.perf_counter()-start)*1000),
            searchable_files=summary['searchable_files'],index_in_progress=summary['active_job_id'] is not None)

    @app.get('/api/files/{file_id}/preview')
    def preview(file_id: str, request: Request):
        row,path=get_file(request,file_id)
        st=path.stat()
        if st.st_size!=row['size'] or st.st_mtime_ns!=row['mtime_ns']:
            raise ApiError('FILE_CHANGED','File changed since indexing. Rescan to refresh its preview.',409)
        return dict(file_id=row['id'],name=row['name'],relative_path=row['rel_path'],file_type=row['kind'],
            text=row['text'],truncated=bool(row['truncated']))

    @app.post('/api/files/{file_id}/open')
    def open_file(file_id: str, body: Empty, request: Request):
        s=state(request)
        with s.scanner.lock:
            _,path=get_file(request,file_id)
            desktop.act(path,root=s.db.meta('root'))
        return {'ok':True}

    @app.post('/api/files/{file_id}/reveal')
    def reveal(file_id: str, body: Empty, request: Request):
        s=state(request)
        with s.scanner.lock:
            _,path=get_file(request,file_id)
            desktop.act(path,reveal=True,root=s.db.meta('root'))
        return {'ok':True}

    @app.get('/api/activity')
    def activity(request: Request):
        s=state(request)
        return dict(embedding_model=config.model,embedding_calls=s.embedder.embedding_calls,ocr_files=s.extractor.ocr_files,
            chunks_embedded=s.embedder.chunks_embedded,last_call_ms=s.embedder.last_call_ms)

    @app.post('/api/index/reset')
    def reset(body: Reset, request: Request):
        if body.confirm is not True:
            raise ApiError('CONFIRMATION_REQUIRED','Confirm index reset.')
        state(request).scanner.reset()
        return {'ok':True}

    @app.api_route('/api/{path:path}', methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS'])
    def unknown_api(path: str):
        raise ApiError('NOT_FOUND','API endpoint not found.',404)

    @app.get('/{path:path}')
    def frontend(path: str):
        root=config.frontend_dist.resolve()
        target=(root/path).resolve()
        if target.is_relative_to(root) and target.is_file():
            return FileResponse(target)
        if (root/'index.html').is_file() and target.is_relative_to(root):
            return FileResponse(root/'index.html')
        raise ApiError('FRONTEND_UNAVAILABLE','Frontend build is not available. Backend API is ready.',404)

    return app

app=create_app()
