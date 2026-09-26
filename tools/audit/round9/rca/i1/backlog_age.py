"""RCA I1: the unpinned backlog, split by whether the site's line was born
before or after the ratchet (#1426 merge 43dd4c34)."""
import subprocess, sys, collections, time
from pathlib import Path
ROOT = Path.cwd(); sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt
RATCHET = "43dd4c34"
t=time.time(); inv = mt.inventory(); t_inv=time.time()-t
unp = mt.unpinned_sites(mt.load_budgets(), inv)
print(f"RESULT inventory={len(inv)} unpinned={len(unp)} inventory_seconds={t_inv:.2f}")
blame = {}
for f in sorted({s['file'] for s in unp}):
    out = subprocess.run(["git","blame","--line-porcelain","HEAD","--",f],capture_output=True,text=True).stdout
    ln = 0; cur=None
    for row in out.splitlines():
        p=row.split()
        if len(p)>=3 and len(p[0])==40 and p[1].isdigit():
            cur=p[0]; ln=int(p[2]); blame[(f,ln)]=cur
anc = {}
def after(sha):
    if sha not in anc:
        anc[sha]= subprocess.run(["git","merge-base","--is-ancestor",RATCHET,sha]).returncode==0
    return anc[sha]
c = collections.Counter(); post=[]
for s in unp:
    a = after(blame[(s['file'],s['line'])]); c[(a,s['kind'])]+=1
    if a: post.append(s)
print("RESULT unpinned_born_after_ratchet=", sum(v for (a,k),v in c.items() if a))
print("RESULT unpinned_born_before_ratchet=", sum(v for (a,k),v in c.items() if not a))
print(dict(c))
for s in post: print("  POST", s['file'], s['line'], s['kind'], blame[(s['file'],s['line'])][:8], s['old'].strip()[:70])
