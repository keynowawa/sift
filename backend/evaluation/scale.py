"""300-file real-model reliability test. No personal source files or desktop actions."""
import hashlib
import json
import resource
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app.ai.ollama import Embedder
from app.config import Config
from app.main import create_app
from benchmark import DOCS, pdf
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).parent/'scale_results.json'

def snapshots(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def wait(c,j):
    for _ in range(2400):
        status=c.get('/api/index/status',params={'job_id':j}).json()
        if status['state'] not in ('queued','running'):return status
        time.sleep(.05)
    raise RuntimeError('Job exceeded two-minute polling budget')

def start(c,root):
    r=c.post('/api/index/start',json={'root':str(root),'replace_index':False})
    assert r.status_code==202,r.text
    return r.json()['job_id']

def main():
    report={'synthetic':True,'files':300,'composition':{},'distinct_base_topics':20,
        'limitations':'15 variants of each of 20 hand-authored base documents; not 300 independent real-world documents.'}
    with tempfile.TemporaryDirectory(prefix='sift-scale-') as temp:
        temp=Path(temp).resolve();root=temp/'corpus';root.mkdir()
        for copy in range(15):
            for i,(name,text) in enumerate(DOCS):
                ext=Path(name).suffix;folder=root/f'batch_{copy:02d}';folder.mkdir(exist_ok=True)
                path=folder/f'IMG_{i:04d}{ext}'
                content=text+f'\nSynthetic record number {copy:02d}-{i:02d}. Reference ZX{copy:02d}{i:02d}. Amount variant {copy*317+i*23}.'
                if ext=='.pdf':pdf(path,content.replace('\n',' '))
                elif ext=='.png':
                    img=Image.new('RGB',(1100,600),'white')
                    ImageDraw.Draw(img).multiline_text((30,30),content,font=ImageFont.load_default(size=23),fill='black',spacing=12)
                    img.save(path)
                else:path.write_text(content)
                report['composition'][ext]=report['composition'].get(ext,0)+1
        before=snapshots(root)
        config=Config(data_dir=temp/'index');model=Embedder(config.model)
        with TestClient(create_app(config,model),base_url='http://127.0.0.1:8765') as c:
            t=time.perf_counter();status=wait(c,start(c,root))
            report['initial']={'wall_ms':round((time.perf_counter()-t)*1000),'status':status,'activity':c.get('/api/activity').json()}
            assert status['state']=='completed' and status['searchable']==300 and status['failed']==0,status
            assert snapshots(root)==before
            queries=['proof I paid to fix my notebook computer','where we are staying on our Cebu trip',
                     'notes about how plants make food','nuclear submarine reactor maintenance schematic',
                     'Synthetic record reference ZX1400']
            report['searches']=[]
            for query in queries:
                t=time.perf_counter();r=c.post('/api/search',json={'query':query,'limit':3,'file_types':[]})
                assert r.status_code==200,r.text
                if query=='nuclear submarine reactor maintenance schematic':
                    assert r.json()['results']==[], 'Unrelated query returned false-positive files'
                report['searches'].append({'query':query,'wall_ms':round((time.perf_counter()-t)*1000),
                    'response':r.json()})
            calls=c.get('/api/activity').json()['embedding_calls']
            t=time.perf_counter();status=wait(c,start(c,root))
            report['unchanged_rescan']={'wall_ms':round((time.perf_counter()-t)*1000),'new_embedding_calls':c.get('/api/activity').json()['embedding_calls']-calls,'status':status}
            assert report['unchanged_rescan']['new_embedding_calls']==0
            changed=root/'batch_00/IMG_0000.txt';changed.write_text('Laptop service invoice: new screen, synthetic reference CHANGE001.')
            (root/'batch_00/IMG_0006.txt').unlink()
            added=root/'fresh.txt';added.write_text('Synthetic fresh receipt. Violin bridge replaced at instrument workshop. Reference FRESH900.')
            before=snapshots(root);calls=c.get('/api/activity').json()['embedding_calls']
            t=time.perf_counter();status=wait(c,start(c,root))
            report['changed_rescan']={'wall_ms':round((time.perf_counter()-t)*1000),'new_embedding_calls':c.get('/api/activity').json()['embedding_calls']-calls,'status':status}
            assert status['searchable']==300 and report['changed_rescan']['new_embedding_calls']==2
            assert snapshots(root)==before
            # Fresh root with 100 new TXT files: cancel after the first committed file and resume.
            for i in range(100):(root/f'new_{i:03d}.txt').write_text(f'Synthetic astronomy notes record {i}: observing Jupiter moons with a telescope.')
            before=snapshots(root);job=start(c,root)
            for _ in range(2000):
                status=c.get('/api/index/status',params={'job_id':job}).json()
                if status['processed']>0 or status['state'] not in ('queued','running'):break
                time.sleep(.002)
            cancel=c.post('/api/index/cancel',json={'job_id':job})
            report['cancel_request_status']=cancel.status_code
            assert cancel.status_code==200,cancel.text
            report['cancelled_job']=wait(c,job)
            assert report['cancelled_job']['state']=='cancelled'
            t=time.perf_counter();status=wait(c,start(c,root))
            report['resumed']={'wall_ms':round((time.perf_counter()-t)*1000),'status':status}
            assert status['searchable']==400 and snapshots(root)==before
            report['source_hashes_unchanged']=True
        report['process_peak_rss_mb']=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024,2)
        report['memory_scope']='Python process including OCR and TestClient; excludes the separate Ollama process. macOS ru_maxrss byte units.'
    OUT.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['searches','initial','unchanged_rescan','changed_rescan','resumed','cancelled_job']},indent=2))
    for name in ['initial','unchanged_rescan','changed_rescan','resumed']:
        r=report[name];print(name,{'wall_ms':r['wall_ms'],'new_embedding_calls':r.get('new_embedding_calls'),'searchable':r['status']['searchable']})
    for r in report['searches']:print('search',r['query'],r['wall_ms'],[x['relative_path'] for x in r['response']['results']])

if __name__=='__main__':main()
