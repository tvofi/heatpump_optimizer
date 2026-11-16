import json,sys
from pathlib import Path
sys.path.insert(0,'tools/ci')
import selftest_scope as s
steps=s.workflow_steps()
art=json.load(open(sys.argv[1]))['steps']
for name in sys.argv[2:]:
    t=s.load_table(Path(name))
    r,n=s.drift(t,art,steps)
    print(name, "refusals=",len(r),"notes=",len(n),"stale=",repr(s.stale(t,steps)))
    for x in r: print("  ",x[:200])
b=json.load(open(sys.argv[2]))['steps']; h=json.load(open(sys.argv[3]))['steps']
lost=[(k,kind,x) for k,v in b.items() for kind in s.LIST_KINDS for x in v.get(kind,()) if x not in h.get(k,{}).get(kind,())]
added=sum(len(set(h[k].get(kind,()))-set(b.get(k,{}).get(kind,()))) for k in h for kind in s.LIST_KINDS)
print("entries lost base->head:",len(lost),"entries added:",added, "steps base/head:",len(b),len(h))
