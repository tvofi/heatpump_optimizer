import sys, json, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import beat_jobs as bj
TRIP="GUARDRAIL all last 30 PRs (first verdict 10-20T01:00Z..11-01T02:00Z): incidence 3/30; P(X<=3|30,0.28) = 0.01 -> would-trip: audit (report-only)"
OK="GUARDRAIL all last 30 PRs (first verdict 10-21T01:00Z..11-02T02:00Z): incidence 11/30; P = 0.9 -> ok (report-only)"
seq=[("trip",(0,TRIP+"\n","")),("fail",(2,"","boom")),("recover-same-cut",(0,TRIP+"\n","")),("recover-ok",(0,OK+"\n","")),("ok-again",(0,OK+"\n",""))]
s=Path(tempfile.mkdtemp())
ans=[None]
c=bj.Ctx(s,Path(sys.argv[2]),run=lambda argv,cwd,env: ans[0],now=1_800_000_000.0)
for name,a in seq:
    ans[0]=a; bj.audit_dispatch(c)
    print(f"RESULT after {name}: digest={bj.read(c.digest/'digest.txt')!r} memory={bj.read(c.digest/'state'/'audit-dispatch.json')!r}")
