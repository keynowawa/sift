"""Synthetic retrieval proof. Run from repository root with PYTHONPATH=backend."""
import json
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.ai.ollama import Embedder
from app.config import MODEL
from app.extractors import Extractor, chunks
from app.retrieval import rank

BASE = Path('backend/evaluation/generated')
DOCS = [
 ('item_001.txt','Laptop service invoice. Replaced damaged keyboard and cleaned cooling fan. Paid PHP 2500 at Metro Computer Clinic.'),
 ('item_002.md','Biology lecture notes: photosynthesis converts sunlight, water and carbon dioxide into glucose. Chlorophyll absorbs light in plant leaves.'),
 ('item_003.pdf','Hotel reservation confirmation. Two nights at Seaside Lodge in Cebu. Guest arrival June 12. Booking reference SL-482.'),
 ('IMG_004.png','Payment successful\nElectricity utility bill\nAmount PHP 1800\nAccount 440012'),
 ('item_005.txt','Rental agreement. Tenant occupies apartment unit 4B. Monthly rent PHP 15000. Landlord handles structural repairs.'),
 ('IMG_006.png','Concert admission\nIndie music festival\nGate opens 6 PM\nSeat section B'),
 ('item_007.txt','Cooking instructions: simmer tomatoes and onions, add pasta, season with basil. Dinner serves four people.'),
 ('item_008.md','Networking class: DNS translates domain names into IP addresses. Routers forward packets across networks.'),
 ('item_009.txt','Dental appointment reminder. Teeth cleaning and checkup scheduled Tuesday morning at Bright Smile Clinic.'),
 ('item_010.txt','Warranty certificate for washing machine. Manufacturer covers defective parts for two years. Keep purchase invoice.'),
 ('item_011.txt','Bus passenger ticket. Travel from Manila to Baguio. Departure 7 AM, platform three, seat 12.'),
 ('item_012.md','Meeting minutes: design team agreed to simplify navigation and revise the onboarding screen. Next review Friday.'),
 ('item_013.txt','Parcel delivery notification. Books shipped by courier. Tracking code PK882. Estimated delivery tomorrow.'),
 ('item_014.txt','Bank transfer confirmation. Tuition payment to university registrar. PHP 22000. Transaction reference TU721.'),
 ('item_015.txt','Gym membership plan. Includes treadmill access, strength equipment and weekly yoga class. Renewal every month.'),
 ('item_016.txt','Pet vaccination record. Dog received rabies vaccine at animal clinic. Next booster due next year.'),
 ('item_017.txt','Resume: software engineer with Python and JavaScript experience. Built inventory dashboard and order tracking tools.'),
 ('item_018.txt','Travel packing checklist: passport, charger, jacket, toiletries, headphones and travel adapter.'),
 ('item_019.txt','Grocery receipt. Rice, eggs, milk and bread. Total PHP 640. Paid cash at neighborhood supermarket.'),
 ('item_020.txt','Research notes: ocean coral bleaching caused by rising water temperature. Marine ecosystems lose biodiversity.')]
TUNING = [
 ('proof I paid to fix my notebook computer','item_001.txt'),
 ('notes about how plants make food','item_002.md'),
 ('where we are staying on our Cebu trip','item_003.pdf'),
 ('payment for keeping the lights on','IMG_004.png'),
 ('instructions for making spaghetti','item_007.txt'),
 ('galactic spaceship engine repair manual',None),
 ('archaeological excavation report of ancient pyramids',None)]
HELD = [
 ('agreement for the place I live','item_005.txt'),
 ('pass to see bands perform live','IMG_006.png'),
 ('how web addresses become numerical network locations','item_008.md'),
 ('when I get my teeth checked','item_009.txt'),
 ('coverage if my laundry appliance breaks','item_010.txt'),
 ('trip north by road to Baguio','item_011.txt'),
 ('money sent for school enrollment','item_014.txt'),
 ('record of my canine getting immunized','item_016.txt'),
 ('my professional experience and programming skills','item_017.txt'),
 ('why reefs lose their color in warm seas','item_020.txt'),
 ('nuclear submarine reactor maintenance schematic',None),
 ('medieval sword metallurgy laboratory experiment',None)]

def pdf(path, text):
    # Tiny valid text-layer PDF, avoiding an extra generation dependency.
    text = text.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
    stream = f'BT /F1 12 Tf 50 740 Td ({text}) Tj ET'.encode()
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1200 800] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>', b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    out=b'%PDF-1.4\n'; offsets=[0]
    for i, obj in enumerate(objects,1):
        offsets.append(len(out)); out+=f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(out); out+=f'xref\n0 6\n0000000000 65535 f \n'.encode()
    out+=b''.join(f'{o:010d} 00000 n \n'.encode() for o in offsets[1:])
    out+=f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode()
    path.write_bytes(out)

def generate():
    BASE.mkdir(parents=True, exist_ok=True)
    for name,text in DOCS:
        path=BASE/name
        if path.suffix=='.pdf': pdf(path,text)
        elif path.suffix=='.png':
            img=Image.new('RGB',(1000,450),'white')
            ImageDraw.Draw(img).multiline_text((40,40),text,font=ImageFont.load_default(size=30),fill='black',spacing=20)
            img.save(path)
        else: path.write_text(text)
    (BASE/'manifest.json').write_text(json.dumps({'synthetic':True,'documents':DOCS,'tuning':TUNING,'held_out':HELD},indent=2))

def evaluate(queries, rows, vectors, threshold, mode):
    records=[]
    for (query,target),vector in zip(queries,vectors):
        hits=rank(query,vector,rows,threshold,mode)[:3]
        names=[h[1]['file_id'] for h in hits]
        records.append({'query':query,'target':target,'top3':names,'correct':target in names if target else not names})
    positives=[r for r in records if r['target']]
    negatives=[r for r in records if not r['target']]
    return {'top3_hits':sum(r['correct'] for r in positives),'positive_queries':len(positives),
        'no_match_correct':sum(r['correct'] for r in negatives),'no_match_queries':len(negatives),'queries':records}

def main():
    generate(); embedder=Embedder(MODEL); extractor=Extractor()
    unload = embedder.client.post('/api/embed',json={'model':MODEL,'input':[],'keep_alive':0})
    unload.raise_for_status()
    t=time.perf_counter(); embedder.embed(['warmup'],query=True); cold_ms=round((time.perf_counter()-t)*1000)
    load_ms=round(embedder.last_load_ms,2)
    t=time.perf_counter(); rows=[]; errors=[]
    for name,_ in DOCS:
        try:
            parts=list(chunks(extractor.extract(BASE/name)))
            vectors=embedder.embed([text for _,text in parts])
            rows.extend({'file_id':name,'text':text,'vector':vector,'page':page} for (page,text),vector in zip(parts,vectors))
        except Exception as exc: errors.append({'file':name,'error':str(exc)})
    indexing_ms=round((time.perf_counter()-t)*1000)
    queries=TUNING+HELD; timings=[]; vectors=[]
    for query,_ in queries:
        t=time.perf_counter(); vectors.append(embedder.embed([query],query=True)[0]); timings.append((time.perf_counter()-t)*1000)
    tune_vec=vectors[:len(TUNING)]; held_vec=vectors[len(TUNING):]
    # Choose only on tuning, maximizing equal-weight positive and no-match success.
    candidates=[round(x,2) for x in np.arange(.35,.76,.025)]
    def quality(th):
        r=evaluate(TUNING,rows,tune_vec,th,'hybrid')
        return r['top3_hits']/r['positive_queries']+r['no_match_correct']/r['no_match_queries']
    threshold=max(candidates,key=lambda th:(quality(th),-th))
    report={'synthetic':True,'model':MODEL,'cold_request_ms':cold_ms,'ollama_load_ms':load_ms,'indexing_ms':indexing_ms,
        'search_embedding_mean_ms':round(sum(timings)/len(timings),2),'threshold':threshold,'files':len(DOCS),'chunks':len(rows),
        'errors':errors,'results':{split:{mode:evaluate(q,rows,v,threshold,mode) for mode in ['keyword','semantic','hybrid']}
            for split,q,v in [('tuning',TUNING,tune_vec),('held_out',HELD,held_vec)]}}
    (BASE.parent/'results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    for split, modes in report['results'].items():
        print(split,{mode:{k:v for k,v in values.items() if k!='queries'} for mode,values in modes.items()})
    embedder.close()

if __name__=='__main__': main()
