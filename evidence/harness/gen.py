import json, sys, os, random
from pathlib import Path
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 7)
S = Path(sys.argv[1]); d = S/"scorecard"; (d/"jobs").mkdir(parents=True, exist_ok=True)
(S/"study"/"work").mkdir(parents=True, exist_ok=True)
runs=[]
concl=["success","failure","failure","cancelled","success","cancelled","cancelled","success","failure","skipped"]
for i in range(60):
    c=random.choice(concl); runs.append({"id":1000+i,"t":f"2026-11-{1+i//6:02d}T{(i%6)*3:02d}:00:00Z","c":c})
random.shuffle(runs)
json.dump(runs,open(d/"runs.json","w"))
for r in runs:
    if r["c"]=="failure" and random.random()<0.7:
        g=random.choice(["success","failure"])
        json.dump({"jobs":[{"name":"gate","conclusion":g},{"name":"governance / instrument-self-tests","conclusion":"failure"}]},open(d/"jobs"/f"jobs_{r['id']}.json","w"))
fams=[("carry-bookkeeping",r"carry"),("body-bookkeeping",r"body"),("ci-state",r"ci-"),("product",r"wrong|class-open|metric")]
open(S/"study"/"work"/"yield.py","w").write("import re\nFAMILY = [\n"+"".join(f"    ({a!r}, {b!r}),\n" for a,b in fams)+"]\n\ndef fam(c):\n    pass\n")
V=[]
for p in range(3000,3080):
    t0=random.randint(0,10**6)
    for k in range(random.randint(1,3)):
        kind=random.choice(["merge","blocked","blocked"])
        cls="" if kind=="merge" else random.choice(["carry-missing","body-x","ci-red","wrong-number","class-open","unknown"])
        V.append({"pr":str(p),"head":f"h{p}{k%2}","kind":kind,"cls":cls,"t":f"2026-10-{1+(t0+k)//40000:02d}T{(t0+k)%24:02d}:00:00Z"})
        if random.random()<0.2: V.append(dict(V[-1]))
V.sort(key=lambda v:v["t"])
json.dump({"verdicts":V},open(d/"verdicts.json","w"))
rows=["pr\tct\tclass\ttokens"]
for i,p in enumerate(range(3000,3090)):
    cl=random.choice(["production","instrument","policy","record"]); tok=random.choice(["fix","hotfix-x","feat","hotfix"])
    rows.append(f"{p if random.random()>.05 else ''}\t{1700000000+i*100}\t{cl}\t{tok}")
open(d/"merges.tsv","w").write("\n".join(rows)+"\n")
L=[]
for p in range(3000,3090):
    x=random.random()
    if x<.6: L.append(f"MERGED #{p} ok")
    elif x<.75: L.append(f"SKIP #{p} red"); L.append(f"MERGED #{p}")
    elif x<.85: L.append(f"PARK #{p} #{p+1} reason")
open(S/"train.log","w").write("\n".join(L)+"\n")
G=[]
for i in range(30):
    g={"group":random.choice(["G","HOTFIX-A","R10-X"])+str(i),"kind":random.choice(["bug","feat","hotfix",None]),
       "files":random.choice([["custom_components/a.py"],["tools/x.py"],[]]),"resume":{"stage":random.choice(["done","fix"])}}
    if random.random()<.3: g["source"]="outside"
    G.append(g)
json.dump({"groups":G},open(d/"roster.json","w"))
rec=["standing-dispatch recycle at 10:00","standing-triage: recycle","fixer recycle","dispatch seat recycled","standing dispatch alive","triage recycle"]
open(S/"sweep.rec","w").write("\n".join(rec)+"\n")
