"""Real HTTP/Ollama integration. Synthetic sources only; opens one TXT on macOS/Windows."""
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
import httpx
from benchmark import generate, pdf
from PIL import Image, ImageDraw, ImageFont

REPO=Path(__file__).resolve().parents[2]
OUTPUT=Path(__file__).parent/'integration_results.json'

def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def fresh_corpus(root):
    """Unique source text and files for each empty-index proof, no downloads."""
    root.mkdir();nonce=uuid.uuid4().hex
    (root/'receipt ü.txt').write_text(f'Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic. Synthetic run {nonce}.')
    (root/'notes.md').write_text(f'Biology lecture notes: photosynthesis converts sunlight water and carbon dioxide into glucose. Synthetic run {nonce}.')
    pdf(root/'reservation.pdf',f'Hotel reservation confirmation. Two nights at Seaside Lodge in Cebu. Booking reference {nonce}.')
    for name,text in [('bill.png','Payment successful\nElectricity utility bill\nAmount PHP 1800'),('ticket.jpg','Concert admission\nIndie music festival\nGate opens 6 PM')]:
        image=Image.new('RGB',(1100,500),'white')
        ImageDraw.Draw(image).multiline_text((30,30),text+f'\nRun {nonce[:12]}',font=ImageFont.load_default(size=30),fill='black',spacing=15)
        image.save(root/name)
    (root/'new instrument.txt').write_text(f'Bassoon service receipt. Replaced the reed and repaired a damaged key on the woodwind instrument. Paid PHP 3200. Synthetic run {nonce}.')
    (root/'bad.txt').write_bytes(b'\xffinvalid UTF-8 without BOM')
    (root/'manifest.json').write_text(json.dumps({'synthetic':True,'nonce':nonce}))
    return nonce

def main(port=8766,fresh=False,desktop=False,hold_seconds=0,traffic=False):
    root=(REPO/'backend/evaluation/generated').resolve()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',port))
    with tempfile.TemporaryDirectory(prefix='sift-integration-') as data:
        nonce=fresh_corpus(Path(data).resolve()/'unseen corpus ü') if fresh else None
        if fresh:root=Path(data).resolve()/'unseen corpus ü'
        else:generate()
        before=hashes(root)
        env=dict(os.environ,SIFT_DATA_DIR=str(Path(data)/'index'),SIFT_PORT=str(port))
        process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--app-dir','backend','--host','127.0.0.1','--port',str(port)],cwd=REPO,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        responses=[]
        traffic_process=None;traffic_stream=None;traffic_file=Path(data)/'nettop.csv'
        print(json.dumps({'backend_pid':process.pid,'port':port,'fresh':fresh,'nonce':nonce}),flush=True)
        try:
            with httpx.Client(base_url=f'http://127.0.0.1:{port}',trust_env=False,timeout=60) as client:
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
                empty_index=call('GET','/api/index');assert empty_index['indexed_files']==0
                empty_activity=call('GET','/api/activity')
                empty_search=call('POST','/api/search',{'query':'bassoon repair receipt','limit':3,'file_types':[]})
                assert empty_search['results']==[]
                assert call('GET','/api/activity')['embedding_calls']==empty_activity['embedding_calls']+1
                if traffic:
                    traffic_stream=traffic_file.open('w')
                    traffic_process=subprocess.Popen(['/usr/bin/nettop','-n','-L','120','-p',str(process.pid),'-p','ollama','-p','llama-server','-J','bytes_in,bytes_out'],stdout=traffic_stream,stderr=subprocess.STDOUT)
                    time.sleep(2)
                print('READY_FOR_TRAFFIC_CAPTURE',flush=True)
                if hold_seconds:time.sleep(hold_seconds)
                job=call('POST','/api/index/start',{'root':str(root),'replace_index':False})['job_id']
                for _ in range(600):
                    status=client.get('/api/index/status',params={'job_id':job}).json()
                    if status['state'] not in ('running','queued'):break
                    time.sleep(.1)
                assert status['state']=='completed',status
                assert status['searchable']==(6 if fresh else 20) and status['failed']==(1 if fresh else 0),status
                call('GET','/api/index/status?job_id='+job)
                call('GET','/api/index')
                result=call('POST','/api/search',{'query':'proof I paid to fix my notebook computer','limit':3,'file_types':['txt']})
                assert result['results'] and result['results'][0]['name']==('receipt ü.txt' if fresh else 'item_001.txt'),result
                fid=result['results'][0]['file_id']
                call('GET',f'/api/files/{fid}/preview')
                if desktop:
                    call('POST',f'/api/files/{fid}/open',{})
                    call('POST',f'/api/files/{fid}/reveal',{})
                pairs=[('electricity utility bill payment','bill.png' if fresh else 'IMG_004.png'),('where we are staying on our Cebu trip','reservation.pdf' if fresh else 'item_003.pdf')]
                if fresh:pairs.extend([('indie music concert admission','ticket.jpg'),('invoice for repairing my woodwind instrument','new instrument.txt')])
                for query,name in pairs:
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
                picker=client.post('/api/folder/pick',json={})
                responses.append({'method':'POST','path':'/api/folder/pick','request':{},'status':picker.status_code,'response':picker.json()})
                assert picker.status_code==503
                unknown=client.get('/api/files/nonexistent/preview')
                responses.append({'method':'GET','path':'/api/files/nonexistent/preview','request':None,'status':unknown.status_code,'response':unknown.json()})
                assert unknown.status_code==404
                invalid=client.post('/api/search',json={'query':' '})
                responses.append({'method':'POST','path':'/api/search','request':{'query':' '},'status':invalid.status_code,'response':invalid.json()})
                assert invalid.status_code==400
                other=Path(data).resolve()/'other root';other.mkdir()
                conflict_body={'root':str(other),'replace_index':False}
                conflict=client.post('/api/index/start',json=conflict_body)
                responses.append({'method':'POST','path':'/api/index/start','request':conflict_body,'status':conflict.status_code,'response':conflict.json()})
                assert conflict.status_code==409
                if hold_seconds:
                    print('READY_FOR_BROWSER_CHECK',flush=True)
                    time.sleep(hold_seconds)
                # Record reset on this disposable index, never on user data.
                call('POST','/api/index/reset',{'confirm':True})
                reset=call('GET','/api/index');assert reset['indexed_files']==0
            assert hashes(root)==before,'Source files were modified'
            if traffic_process:
                traffic_process.terminate();traffic_process.wait(timeout=10);traffic_stream.close()
                traffic_process=None
            capture=traffic_file.read_text() if traffic else None
            OUTPUT.write_text(json.dumps({'synthetic':True,'fresh':fresh,'nonce':nonce,'backend_pid':process.pid,'port':port,'source_hashes_unchanged':True,'os_nettop':capture,'responses':responses},indent=2))
            print(json.dumps({'source_hashes_unchanged':True,'indexed_status':status,'request_count':len(responses)},indent=2))
        finally:
            if traffic_process:
                traffic_process.terminate();traffic_process.wait(timeout=10);traffic_stream.close()
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            process.stderr.close()

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8766)
    parser.add_argument('--fresh',action='store_true')
    parser.add_argument('--desktop',action='store_true')
    parser.add_argument('--hold-seconds',type=float,default=0)
    parser.add_argument('--traffic',action='store_true',help='macOS nettop socket metadata, no packet payloads')
    args=parser.parse_args();main(args.port,args.fresh,args.desktop,args.hold_seconds,args.traffic)
