import sys,json,subprocess,os
sys.path.insert(0,'tests'); sys.path.insert(0,'.')
from pathlib import Path
import mutation_table as mt
F=Path('custom_components/heatpump_optimizer/wood_fuel.py').resolve()
orig=F.read_text()
sites=mt.anchor_sites(orig,list(mt.candidates(F,mt.RATCHETED,orig)))
env=dict(os.environ,PYTHONPATH="tests/hastub:/tmp/claude-0/-home-user-heatpump-optimizer/7331d838-5084-598b-bd81-b25fab97f4c4/scratchpad/j2")
out=[]
for p in open('/tmp/claude-0/pins.txt').read().split():
    j=json.load(open(p)); a=j['anchor']; scr=j['killed_by']
    ms=[s for s in sites if s['anchor']==a]
    if not ms: out.append(f"RESULT {a}: NOT-APPLIED by {scr} rc=- no site"); continue
    for m in ms:
        L=orig.splitlines(keepends=True); i=m['line']-1
        assert L[i].rstrip('\n')==m['old']
        L[i]=m['new']+'\n'; F.write_text(''.join(L))
        try:
            r=subprocess.run(['python3',scr],env=env,capture_output=True,text=True,timeout=900)
            last=(r.stdout+r.stderr).strip().splitlines()[-1:] or ['']
            v='KILLED' if r.returncode else 'SURVIVED'
            out.append(f"RESULT {a}: {v} by {scr} rc={r.returncode} {last[0]} [line {m['line']}: {m['new'].strip()}]")
        finally: F.write_text(orig)
        print(out[-1],flush=True)
os.makedirs('/tmp/tmp.EnWWEHZucR/ev',exist_ok=True)
open('/tmp/tmp.EnWWEHZucR/ev/pins16.txt','w').write('\n'.join(out)+'\n')
