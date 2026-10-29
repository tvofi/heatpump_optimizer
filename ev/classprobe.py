import sys, re
sys.path[:0]=['tools/pr','tests','tests/hastub']
from pathlib import Path
import ci_predict as c
root=Path('.').resolve()
home=next(d for d in (".claude/workflows","tools/policy") if (root/d/"agreement_py.py").is_file())
sys.path.insert(0,str(root/home)); import agreement_py
text=(root/agreement_py.WORKFLOW).read_text()
tracked=c.tracked_files(root)
byname={}
for t in tracked:
    if t.endswith(('.py','.mjs','.sh','.js','.json','.md','.txt','.yml')): byname.setdefault(Path(t).name,[]).append(t)
out=set()
for job,_,mark,homes,whole,_ in c.GRADERS:
    entry=next(p for p in homes if (root/p).is_file())
    specs=agreement_py.restore_specs(text,job)
    key=c.mjs_closure(root,entry,imports=whole)
    for src in sorted(key):
        named={f for _,_,f in c.named_loads(root,src)}
        s=(root/src).read_text()
        for n,line in enumerate(s.splitlines(),1):
            for tok in set(re.findall(r"[\w.-]+\.(?:py|mjs|sh|js|json)\b",line)):
                for f in byname.get(tok,[]):
                    if f in key or f in named: continue
                    if not any(agreement_py.covers(sp,f) for sp in specs): continue
                    out.add((mark,src,n,f,line.strip()[:150]))
for o in sorted(out): print(*o,sep=' | ')
