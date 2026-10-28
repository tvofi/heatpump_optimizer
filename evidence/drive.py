import json,sys,glob
from pathlib import Path
sites=json.load(open('$HOME/w2745/sites.json'))
pins={}
for f in glob.glob('$HOME/rev2745/tests/mutation_ledger/killed_by/*/*.json'):
    d=json.load(open(f)); pins[d['anchor']]=d['killed_by']
k,n=int(sys.argv[1]),int(sys.argv[2])
wt=Path(f'$HOME/mw{k}')
sys.path.insert(0,str(wt/'tests')); import mutation_table as mt
jobs=[s for s in sites if s['kind']!='CONST']+[None]
for s in jobs[k-1::n]:
    if s is None:
        r=mt.run_script('tests/plan_view.py',wt,3600); print(f"RESULT BASELINE tests/plan_view.py unmutated rc={r.rc if hasattr(r,'rc') else r[0]} failed={r.failed} {r[2]:.0f}s",flush=True); continue
    p=wt/s['file']; orig=p.read_text(); lines=orig.split('\n')
    assert lines[s['line']-1]==s['old'], s
    lines[s['line']-1]=s['new']; p.write_text('\n'.join(lines))
    try: r=mt.run_script(pins[s['anchor']],wt,3600)
    finally: p.write_text(orig)
    print(f"RESULT {s['anchor'].split(':',1)[1]} line={s['line']} new={s['new'].strip()!r} driver={pins[s['anchor']]} rc={r[0]} failed={r.failed} {r[2]:.0f}s",flush=True)
