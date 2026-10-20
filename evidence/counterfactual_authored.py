import json, os, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
ROOT = Path.home()/"hpo-seats/r10s3/rev-2488"
BASE = "a2b25bbc5518b5cb212429fdd623b5d33634fd08"
TREE = "5fd7fbdfb87051270d66fec0ef2ed860ce12f6a9"
LIVE = ["custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js","tests/features.py",
        "tools/audit/seat/handover_prompt.py","tools/audit/seat/roster_lib.py"]
RECORDS = ["dev/audit/config/bugclasses.json","dev/programme/plan-2026-09-open-issues.md"]
sys.path.insert(0, str(ROOT/"tests")); import layout
fd,name = tempfile.mkstemp(prefix="hpo-idx-"); os.close(fd); idx=Path(name)
env={**os.environ,"GIT_INDEX_FILE":str(idx)}
subprocess.run(["git","read-tree",TREE],cwd=ROOT,env=env,check=True)
m=json.loads(subprocess.run(["git","show",":tests/layout.json"],cwd=ROOT,env=env,check=True,capture_output=True).stdout)
m.pop("ref_namespaces",None)
subprocess.run(["git","restore","--source="+BASE,"--staged","--",*LIVE,*RECORDS],cwd=ROOT,env=env,check=True)
m["historical"]=[h for h in m["historical"] if h not in RECORDS]
data=json.dumps(m,indent=1).encode()
blob=subprocess.run(["git","hash-object","-w","--stdin"],cwd=ROOT,input=data,check=True,capture_output=True).stdout.decode().strip()
subprocess.run(["git","update-index","--cacheinfo",f"100644,{blob},tests/layout.json"],cwd=ROOT,env=env,check=True)
os.environ["GIT_INDEX_FILE"]=str(idx)
found=layout.guard(ROOT,m,BASE)
c=Counter()
for f in found:
    if "handoff/round9/, " in f or "handoff/round9/:" in f: c["round9"]+=1
    elif "handoff/, " in f or "handoff/:" in f: c["handoff"]+=1
    else: c["other"]+=1
files={f.split(":")[1] for f in found if f.startswith("unswept:")}
import collections
print("RESULT authored-base counterfactual: total",len(found),dict(c),"unswept files",len(files))
k=collections.Counter()
for f in found:
    kind=f.split(":")[0]
    old="round9" if "handoff/round9/" in f else ("handoff" if "handoff/" in f else "other")
    k[(kind,old)]+=1
print("RESULT kinds:",dict(k))
for f in found:
    if f.startswith("new-reference"): print("  NEWREF",f[:160])
idx.unlink(missing_ok=True)
