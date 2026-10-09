import hashlib
import json
import threading
import time
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.ai.ollama import ModelUnavailable
from app.config import Config
from app.db import Database
from app.main import create_app
from app.security import ApiError, validate_root, scoped_file
from app import desktop

class StubEmbedder:
    """Only injected by tests; no runtime configuration enables this stub."""
    def __init__(self):
        self.embedding_calls=0; self.chunks_embedded=0; self.last_call_ms=None
        self.lock=threading.Lock(); self.available=True; self.fail=False; self.delay=0
    def ready(self): return self.available
    def embed(self,texts,query=False):
        if self.fail: raise ModelUnavailable('Test dependency failure')
        time.sleep(self.delay)
        self.embedding_calls+=1
        if not query: self.chunks_embedded+=len(texts)
        self.last_call_ms=1
        values=[]
        for text in texts:
            v=np.array([1.,0.,0.] if any(t in text.lower() for t in ['laptop','computer','keyboard']) else [0.,1.,0.])
            values.append(v)
        return np.stack(values)
    def close(self): pass

@pytest.fixture
def env(tmp_path):
    cfg=Config(data_dir=tmp_path/'index'); model=StubEmbedder()
    with TestClient(create_app(cfg,model),base_url='http://127.0.0.1:8765') as client:
        yield client,model,tmp_path,cfg

def wait(client,job):
    for _ in range(300):
        body=client.get('/api/index/status',params={'job_id':job}).json()
        if body['state'] not in ('queued','running'): return body
        time.sleep(.01)
    raise AssertionError('Job timed out')

def index(client,root,replace=False):
    response=client.post('/api/index/start',json={'root':str(root),'replace_index':replace})
    assert response.status_code==202,response.text
    return wait(client,response.json()['job_id'])

def test_real_text_roundtrip_cache_changed_deleted_readonly(env):
    c,m,p,cfg=env; folder=p/'files'; folder.mkdir(); source=folder/'odd ü name.txt'
    source.write_text('Laptop keyboard replacement paid PHP 2500.'); original=source.read_bytes()
    job=index(c,folder); assert job['state']=='completed' and job['searchable']==1
    result=c.post('/api/search',json={'query':'repair my computer'}).json()['results'][0]
    assert result['snippet']==original.decode()
    assert set(result)=={'file_id','name','relative_path','file_type','size_bytes','modified_at','snippet','location','match_kind'}
    assert c.get(f"/api/files/{result['file_id']}/preview").json()['text']==original.decode()
    calls=m.embedding_calls
    index(c,folder); assert m.embedding_calls==calls
    source.write_text('Biology plant growth')
    assert c.post('/api/search',json={'query':'computer'}).json()['results']==[]
    assert c.get(f"/api/files/{result['file_id']}/preview").status_code==409
    index(c,folder); assert m.embedding_calls==calls+2
    source.unlink(); index(c,folder); assert c.get('/api/index').json()['indexed_files']==0
    # All writes above are test actions; scanner did not alter source before them.
    assert original==b'Laptop keyboard replacement paid PHP 2500.'

def test_no_match_and_uncached_query(env):
    c,m,p,_=env; folder=p/'files';folder.mkdir();(folder/'a.txt').write_text('Laptop keyboard')
    index(c,folder); before=m.embedding_calls
    for _ in range(2): assert c.post('/api/search',json={'query':'submarine'}).json()['results']==[]
    assert m.embedding_calls==before+2

def test_failures_visible_and_bad_file_isolated(env):
    c,m,p,_=env; folder=p/'files';folder.mkdir()
    (folder/'a.txt').write_bytes(b'\xffinvalid'); (folder/'b.txt').write_text('Laptop')
    (folder/'c.exe').write_text('not executable'); job=index(c,folder)
    assert job['state']=='completed' and job['failed']==1 and job['skipped']==1 and job['searchable']==1
    assert job['processed']==3
    m.fail=True
    r=c.post('/api/search',json={'query':'computer'})
    assert r.status_code==503 and r.json()['error']['code']=='MODEL_UNAVAILABLE'
    (folder/'b.txt').write_text('Keyboard update')
    job=index(c,folder); assert job['state']=='failed' and job['errors']
    assert c.get('/api/index').json()['searchable_files']==0

def test_root_replace_reset_and_path_guards(env):
    c,m,p,cfg=env; a=p/'a';b=p/'b';a.mkdir();b.mkdir();(a/'x.txt').write_text('Laptop')
    index(c,a)
    assert c.post('/api/index/start',json={'root':str(b),'replace_index':False}).status_code==409
    r=c.post('/api/index/start',json={'root':str(p/'missing'),'replace_index':True})
    assert r.status_code==400 and c.get('/api/index').json()['root']==str(a)
    link=p/'link';link.symlink_to(a,target_is_directory=True)
    with pytest.raises(ApiError):validate_root(str(link),cfg.data_dir)
    with pytest.raises(ApiError):scoped_file(a,'../outside.txt')
    assert c.post('/api/index/reset',json={'confirm':False}).status_code==400
    assert c.post('/api/index/reset',json={'confirm':True}).status_code==200
    assert (a/'x.txt').read_text()=='Laptop' and c.get('/api/index').json()['root'] is None

def test_symlink_and_hidden_skip(env):
    c,_,p,_=env; folder=p/'files';folder.mkdir()
    outside=p/'outside.txt';outside.write_text('Laptop')
    (folder/'link.txt').symlink_to(outside);(folder/'.hidden.txt').write_text('Laptop')
    (folder/'normal.txt').write_text('Laptop')
    job=index(c,folder);assert job['discovered']==1

def test_security_and_validation(env):
    c,_,_,_=env
    for headers in [{'origin':'https://evil.example'},{'origin':'null'},{'host':'evil.example'},{'sec-fetch-site':'cross-site'}]:
        r=c.post('/api/index/reset',json={'confirm':True},headers=headers)
        assert r.status_code==400 and 'error' in r.json()
    assert c.post('/api/index/reset',content='{}',headers={'content-type':'text/plain'}).status_code==400
    for body in [{'query':' '},{'query':'x','limit':21},{'query':'x','file_types':['exe']},{'query':'x','extra':1}]:
        assert c.post('/api/search',json=body).status_code==400
    assert c.get('/api/missing').status_code==404
    assert c.get('/api/missing').headers['content-type'].startswith('application/json')

def test_cancel_conflict_reload_and_restart(env):
    c,m,p,cfg=env;folder=p/'files';folder.mkdir()
    for i in range(8):(folder/f'{i}.txt').write_text('Laptop keyboard '+str(i))
    m.delay=.03
    r=c.post('/api/index/start',json={'root':str(folder),'replace_index':False});job=r.json()['job_id']
    assert c.get('/api/index').json()['active_job_id']==job
    assert c.post('/api/index/start',json={'root':str(folder),'replace_index':False}).status_code==409
    assert c.post('/api/index/reset',json={'confirm':True}).status_code==409
    while c.get('/api/index/status',params={'job_id':job}).json()['processed']==0:time.sleep(.01)
    assert c.post('/api/index/cancel',json={'job_id':job}).json()=={'accepted':True}
    body=wait(c,job);assert body['state']=='cancelled' and 0<body['processed']<8
    assert c.get('/api/index').json()['searchable_files']>=1
    index(c,folder);assert c.get('/api/index').json()['searchable_files']==8
    db=Database(cfg.data_dir); interrupted=dict(body,job_id='interrupt',state='running')
    db.save_job(interrupted);db2=Database(cfg.data_dir)
    assert db2.job('interrupt')['state']=='interrupted'

def test_desktop_safe_args_and_missing_file(env):
    c,_,p,_=env;folder=p/'files';folder.mkdir();f=folder/'name $(literal).txt';f.write_text('Laptop')
    index(c,folder);record=c.post('/api/search',json={'query':'computer'}).json()['results'][0]
    with patch('app.desktop.sys.platform','darwin'),patch('app.desktop.subprocess.run') as run:
        assert c.post(f"/api/files/{record['file_id']}/open",json={}).status_code==200
        assert run.call_args.args[0]==['/usr/bin/open',str(f)]
        assert c.post(f"/api/files/{record['file_id']}/reveal",json={}).status_code==200
        assert run.call_args.args[0]==['/usr/bin/open','-R',str(f)]
    with pytest.raises(ApiError):desktop.act(folder/'unknown.exe')
    f.unlink();assert c.post(f"/api/files/{record['file_id']}/open",json={}).status_code==404

def test_model_missing_health_and_picker(env):
    c,m,p,_=env;m.available=False
    assert c.get('/api/health').json()['status']=='setup_required'
    folder=p/'files';folder.mkdir()
    assert c.post('/api/index/start',json={'root':str(folder),'replace_index':False}).status_code==503
    assert c.get('/api/health').json()['capabilities']['folder_picker'] is False
    assert c.post('/api/folder/pick',json={}).status_code==503

def test_frontend_serving_cannot_swallow_api_errors(tmp_path):
    dist=tmp_path/'frontend';dist.mkdir();(dist/'index.html').write_text('<html>Sift test shell</html>')
    cfg=Config(data_dir=tmp_path/'data',frontend_dist=dist)
    with TestClient(create_app(cfg,StubEmbedder()),base_url='http://127.0.0.1:8765') as c:
        assert c.get('/').text=='<html>Sift test shell</html>'
        assert c.get('/some/browser/route').status_code==200
        assert c.get('/api/typo').status_code==404
        assert c.get('/api/typo').json()['error']['code']=='NOT_FOUND'
        assert c.post('/api/typo',json={}).status_code==404

def test_duplicate_names_filters_and_source_readonly(env):
    c,m,p,_=env;folder=p/'files';folder.mkdir()
    (folder/'one').mkdir();(folder/'two').mkdir()
    for sub in ['one','two']:(folder/sub/'same.txt').write_text('Laptop keyboard in '+sub)
    (folder/'notes.md').write_text('Laptop keyboard notes')
    before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.rglob('*') if f.is_file()}
    index(c,folder)
    results=c.post('/api/search',json={'query':'computer','file_types':['txt']}).json()['results']
    assert len(results)==2 and len({r['file_id'] for r in results})==2
    assert before=={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.rglob('*') if f.is_file()}
    assert c.post('/api/search',json={'query':'computer','file_types':['jpg']}).json()['results']==[]

def test_model_configuration_change_requires_reindex(tmp_path):
    folder=tmp_path/'files';folder.mkdir();(folder/'a.txt').write_text('Laptop keyboard')
    cfg=Config(data_dir=tmp_path/'data')
    with TestClient(create_app(cfg,StubEmbedder()),base_url='http://127.0.0.1:8765') as c:index(c,folder)
    cfg.chunk_chars=900
    m=StubEmbedder()
    with TestClient(create_app(cfg,m),base_url='http://127.0.0.1:8765') as c:
        assert c.get('/api/index').json()['searchable_files']==0
        assert c.post('/api/search',json={'query':'computer'}).json()['results']==[]
        index(c,folder)
        assert c.get('/api/index').json()['searchable_files']==1
        assert m.chunks_embedded==1
