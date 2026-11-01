import json,sys,statistics,copy,datetime as dt
sys.path.insert(0, sys.argv[2]+"/tests")
import ci_ratchet as c
runs=json.load(open(sys.argv[1]))["workflow_runs"]
def med(xs):
    xs=sorted(xs);n=len(xs);m=n//2
    return xs[m] if n%2 else (xs[m-1]+xs[m])/2
def analyse(runs,label):
    ms=[(r["created_at"],c.run_minutes(r)) for r in runs]
    ms=[(t,m) for t,m in ms if m is not None]
    ms.sort()  # oldest first
    vals=[m for _,m in ms]
    center=med(vals)
    m8=[med(vals[i:i+8]) for i in range(len(vals)-7)]
    print(f"{label}: n={len(vals)} span={ms[0][0]}..{ms[-1][0]} median={center:.3f} m8={min(m8):.3f}..{max(m8):.3f} maxabsdev={max(abs(x-center) for x in m8):.3f} up={max(m8)-center:.3f} newest8={med(vals[-8:]):.3f}")
    return vals
def cut(runs,sec,name="tests / ci-ratchet"):
    out=copy.deepcopy(runs)
    for r in out:
        for j in r.get("jobs") or []:
            if j.get("name")==name and j.get("completed_at") and j.get("started_at"):
                t=dt.datetime.fromisoformat(j["completed_at"].replace("Z","+00:00"))-dt.timedelta(seconds=sec)
                s=dt.datetime.fromisoformat(j["started_at"].replace("Z","+00:00"))
                if t<s: t=s
                j["completed_at"]=t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out
cutoff=sys.argv[3] if len(sys.argv)>3 else None
sel=[r for r in runs if not cutoff or r["created_at"]<=cutoff]
analyse(sel,"window")
for s in (0,28,36):
    analyse(cut(sel,s),f"cut{s}s")
