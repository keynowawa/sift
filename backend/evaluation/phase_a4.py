"""New synthetic split; select only on tuning before embedding/evaluating held-out."""
import json
import time
from pathlib import Path
import numpy as np
from app.ai.ollama import Embedder
from app.config import MODEL
from app.retrieval import rank

DOCS = [
 ('a.txt', 'Astronomy observation log. Saturn rings visible through telescope. Jupiter moons tracked at midnight.'),
 ('b.txt', 'Plumbing invoice. Kitchen sink leaking pipe replaced by plumber. Labor cost 950 pesos.'),
 ('c.txt', 'Bicycle workshop receipt. Bent wheel straightened and brake cables replaced. Chain lubricated.'),
 ('d.txt', 'Garden watering plan. Tomatoes need irrigation twice weekly. Mulch retains soil moisture.'),
 ('e.txt', 'Chemistry laboratory safety. Wear goggles and gloves when handling hydrochloric acid. Neutralize spills.'),
 ('f.txt', 'Employee onboarding checklist. Submit bank account details and tax forms. Collect office access badge.'),
 ('g.txt', 'Scholarship application requirements. Academic transcript, recommendation letter and financial need statement.'),
 ('h.txt', 'Bread recipe. Mix flour yeast salt and water. Knead dough then allow it to rise before baking.'),
 ('i.txt', 'Car insurance policy. Collision damage covered subject to deductible. Roadside towing assistance included.'),
 ('j.txt', 'Piano practice schedule. Scales arpeggios and sight reading. Rehearse recital pieces daily.'),
 ('k.txt', 'Swimming lesson registration. Beginner pool class teaches breathing and floating. Saturday at aquatic center.'),
 ('l.txt', 'Passport renewal checklist. Bring current passport identity card and recent photographs to consular appointment.'),
 ('m.txt', 'Volcano geography notes. Magma rises through crust and erupts as lava. Ash deposits form fertile soil.'),
 ('n.txt', 'Warehouse inventory. Forty cardboard boxes and twelve packing tape rolls. Shipment labels stored beside loading dock.'),
 ('o.txt', 'Wedding invitation. Ceremony at Rose Chapel followed by dinner reception. Please confirm attendance.'),
 ('p.txt', 'Internet service outage report. Fiber cable damaged during road construction. Connection restored after repair.'),
 ('q.txt', 'Meditation journal. Ten minutes of slow breathing each morning. Notice thoughts without judgment.'),
 ('r.txt', 'Coffee machine care. Descale boiler monthly and rinse filter after brewing. Remove mineral buildup.'),
]
TUNING = [
 ('watching planets through my telescope','a.txt'), ('bill for fixing the water leak','b.txt'),
 ('repairing my cycle brakes','c.txt'), ('how often to irrigate tomato plants','d.txt'),
 ('protective equipment for acid experiments','e.txt'), ('paperwork for starting a new job','f.txt'),
 ('documents needed to get student financial aid','g.txt'), ('making a loaf with yeast','h.txt'),
 ('quantum computer error correction',None), ('invoice for repairing a helicopter engine',None),
 ('renewal of dog vaccination policy',None), ('underwater submarine navigation manual',None),
 ('transcript of a court murder trial',None),
]
EXPLORATORY = [
 ('help when my automobile crashes','i.txt'), ('daily keyboard instrument rehearsal','j.txt'),
 ('learning to stay afloat in a pool','k.txt'), ('papers for renewing my travel identity booklet','l.txt'),
 ('why mountains discharge molten rock','m.txt'), ('stock of packaging supplies','n.txt'),
 ('invite to a marriage ceremony','o.txt'), ('reason my broadband stopped working','p.txt'),
 ('calming my mind through breathing','q.txt'), ('removing scale from the espresso maker','r.txt'),
 ('insurance claim for a stolen yacht',None), ('brain tumor radiology diagnosis',None),
 ('application for a nuclear reactor permit',None), ('recipe for roasting a duck',None),
 ('telescope purchase warranty certificate',None),
]
HELD = [
 ('coverage for damage to my vehicle','i.txt'), ('exercises for playing the piano','j.txt'),
 ('signup for beginner swimming instruction','k.txt'), ('consular appointment renewal requirements','l.txt'),
 ('notes on volcanic eruptions','m.txt'), ('how many boxes are in the warehouse','n.txt'),
 ('where the bride and groom celebrate','o.txt'), ('fiber connection repair report','p.txt'),
 ('morning mindfulness routine','q.txt'), ('cleaning mineral deposits from a coffee boiler','r.txt'),
 ('wedding dress sewing pattern',None), ('telescope lens manufacturing specification',None),
 ('warehouse forklift operator license',None), ('insurance policy for an aircraft',None),
 ('dinosaur fossil excavation map',None),
]

def evaluate(queries, vectors, rows, mode, weight, cutoff):
    records=[]
    for (query,target), vector in zip(queries,vectors):
        names=[h[1]['file_id'] for h in rank(query,vector,rows,.53,mode,keyword_weight=weight,min_fused_score=cutoff)[:3]]
        records.append(dict(query=query,target=target,top3=names,correct=target in names if target else not names))
    return dict(hits=sum(r['correct'] for r in records if r['target']), positives=sum(bool(r['target']) for r in records),
                abstentions=sum(r['correct'] for r in records if not r['target']), negatives=sum(not r['target'] for r in records), queries=records)

def main():
    model=Embedder(MODEL)
    try:
        vectors=model.embed([text for _,text in DOCS])
        rows=[dict(file_id=name,text=text,page=None,vector=v) for (name,text),v in zip(DOCS,vectors)]
        tuning_vectors=model.embed([q for q,_ in TUNING],query=True)
        candidates=[]
        for weight in [.20,.35,.50]:
            for cutoff in [.35,.40,.45,.50,.55,.60]:
                r=evaluate(TUNING,tuning_vectors,rows,'hybrid',weight,cutoff)
                candidates.append(dict(weight=weight,cutoff=cutoff,hits=r['hits'],abstentions=r['abstentions'],
                    objective=r['hits']/r['positives']+2*r['abstentions']/r['negatives']))
        # Prefer original weight, then smallest cutoff on an objective tie.
        selected=max(candidates,key=lambda c:(c['objective'],-abs(c['weight']-.20),-c['cutoff']))
        weight,cutoff=selected['weight'],selected['cutoff']
        # Frozen before the held-out queries are embedded or inspected.
        held_vectors=model.embed([q for q,_ in HELD],query=True)
        exploratory_vectors=model.embed([q for q,_ in EXPLORATORY],query=True)
        results={split:{mode:evaluate(q,v,rows,mode,weight,cutoff) for mode in ['keyword','semantic','hybrid']}
                 for split,q,v in [('tuning',TUNING,tuning_vectors),('held_out',HELD,held_vectors),('exploratory',EXPLORATORY,exploratory_vectors)]}
        # Isolate ranking cost using repeated real vectors, not simulated embeddings.
        scale=[]
        for count in [300,1200]:
            large=[dict(rows[i%len(rows)],file_id=f'file-{i%300}') for i in range(count)]
            timings=[]
            for _ in range(30):
                t=time.perf_counter(); rank(TUNING[0][0],tuning_vectors[0],large,keyword_weight=weight,min_fused_score=cutoff)
                timings.append((time.perf_counter()-t)*1000)
            scale.append(dict(files=300,chunks=count,median_ms=round(float(np.median(timings)),2),p95_ms=round(float(np.percentile(timings,95)),2)))
        report=dict(model=MODEL,files=len(rows),selected=selected,candidates=candidates,results=results,ranking_only=scale)
        Path('backend/evaluation/phase_a4_results.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(dict(selected=selected,ranking_only=scale,results={s:{m:{k:v for k,v in r.items() if k!='queries'} for m,r in modes.items()} for s,modes in results.items()}),indent=2))
    finally: model.close()

if __name__=='__main__': main()
