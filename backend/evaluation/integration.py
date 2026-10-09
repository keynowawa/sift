"""Real HTTP/Ollama integration. Synthetic sources only; opens one TXT on macOS/Windows."""
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import httpx

REPO=Path(__file__).resolve().parents[2]
OUTPUT=Path(__file__).parent/'integration_results.json'

def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def main():
    root=(REPO/'backend/evaluation/generated').resolve()
    assert root.exists(), 'Run benchmark.py first'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',8765))
    before=hashes(root)
    with tempfile.TemporaryDirectory(prefix='sift-integration-') as data:
        env=dict(os.environ,SIFT_DATA_DIR=data)
        process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--app-dir','backend','--host','127.0.0.1','--port','8765'],cwd=REPO,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        responses=[]
        try:
            with httpx.Client(base_url='http://127.0.0.1:8765',trust_env=False,timeout=60) as client:
                for _ in range(100):
                    if process.poll() is not None:raise RuntimeError(process.stderr.read().decode())
                    try:
                        r=client.get('/api/index')
                        if r.status_code==200:break
                    except httpx.HTTPError:pass
                    time.sleep(.1)
                def call(method,path,body=None):
                    r=client.request(method,path,json=body) if body is not None else client.request(method,path)
                    responses.append({'method':method,'path':path,'request':body,'status':r.status_code,'response':r.json()})
                    assert r.is_success,(path,r.text)
                    return r.json()
                call('GET','/api/health')
                job=call('POST','/api/index/start',{'root':str(root),'replace_index':False})['job_id']
                for _ in range(600):
                    status=client.get('/api/index/status',params={'job_id':job}).json()
                    if status['state'] not in ('running','queued'):break
                    time.sleep(.1)
                assert status['state']=='completed',status
                call('GET','/api/index/status?job_id='+job)
                call('GET','/api/index')
                result=call('POST','/api/search',{'query':'proof I paid to fix my notebook computer','limit':3,'file_types':['txt']})
                assert result['results'] and result['results'][0]['name']=='item_001.txt',result
                fid=result['results'][0]['file_id']
                call('GET',f'/api/files/{fid}/preview')
                call('POST',f'/api/files/{fid}/open',{})
                call('POST',f'/api/files/{fid}/reveal',{})
                for query,name in [('electricity utility bill payment','IMG_004.png'),('where we are staying on our Cebu trip','item_003.pdf')]:
                    result=call('POST','/api/search',{'query':query,'limit':3,'file_types':[]})
                    assert name in [r['name'] for r in result['results']],result
                empty=call('POST','/api/search',{'query':'nuclear submarine reactor maintenance schematic','limit':3,'file_types':[]})
                assert empty['results']==[]
                activity=call('GET','/api/activity')
                calls=activity['embedding_calls']
                job=call('POST','/api/index/start',{'root':str(root),'replace_index':False})['job_id']
                for _ in range(600):
                    status=client.get('/api/index/status',params={'job_id':job}).json()
                    if status['state'] not in ('running','queued'):break
                    time.sleep(.05)
                call('GET','/api/index/status?job_id='+job)
                assert call('GET','/api/activity')['embedding_calls']==calls
            assert hashes(root)==before,'Source files were modified'
            OUTPUT.write_text(json.dumps({'synthetic':True,'source_hashes_unchanged':True,'responses':responses},indent=2))
            print(json.dumps({'source_hashes_unchanged':True,'indexed_status':responses[2]['response'],
                'first_search':responses[4]['response'],'request_count':len(responses)},indent=2))
        finally:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            process.stderr.close()

if __name__=='__main__':main()
