import json,sys,copy
from datetime import datetime,timedelta
sys.path.insert(0,"tests"); import ci_ratchet as c
runs=sorted(json.load(open(sys.argv[1]))["workflow_runs"],key=lambda r:r["created_at"],reverse=True)
def shift(t,s): 
    d=datetime.fromisoformat(t.replace("Z","+00:00"))+timedelta(seconds=s); return d.strftime("%Y-%m-%dT%H:%M:%SZ")
def grow(r,job,sec,mult=None):
    r=copy.deepcopy(r)
    P=lambda t:datetime.fromisoformat(t.replace("Z","+00:00"))
    tgt=[j for j in r["jobs"] if j["name"]==job and j.get("conclusion")!="skipped" and j.get("completed_at")]
    if not tgt: return r
    j=tgt[0]
    if mult: sec=(P(j["completed_at"])-P(j["started_at"])).total_seconds()*(mult-1)
    frontier=[(P(j["completed_at"]),sec)]; j["completed_at"]=shift(j["completed_at"],sec); done={id(j)}
    while frontier:
        end,s=frontier.pop()
        for k in r["jobs"]:
            if id(k) in done or not k.get("created_at"): continue
            if end <= P(k["created_at"]) <= end+timedelta(seconds=c.QUEUE_EPS+5):
                old=P(k["completed_at"]) if k.get("completed_at") else None
                for f in ("created_at","started_at","completed_at"):
                    if k.get(f): k[f]=shift(k[f],s)
                done.add(id(k))
                if old: frontier.append((old,s))
    return r
def g(rs): return c.window_work_minutes(rs[:16])
base=g(runs); print("base grade",base)
for job in ["tests / closures","tests / fast (3.14)","tests / arch-instrument","tests / coverage"]:
    out=[]
    for k in [1,4,8,12,15,16]:
        rs=[grow(r,job,300) if i<k else r for i,r in enumerate(runs)]
        out.append(f"k={k}:{g(rs)}")
    print("+300s",job," ".join(out))
# slow-host: x1.9 on heavy lanes in newest k runs
for job in ["tests / closures","tests / fast (3.14)","tests / arch-instrument"]:
    out=[]
    for k in [8,15,16]:
        rs=[grow(r,job,0,mult=1.9) if i<k else r for i,r in enumerate(runs)]
        out.append(f"k={k}:{g(rs)}")
    print("slow x1.9",job," ".join(out))
# gradual: closures +20s per push for newest 16 (oldest +20, newest +320)
rs=[grow(r,"tests / closures",20*(16-i)) if i<16 else r for i,r in enumerate(runs)]
print("gradual +20s/push closures (newest +320s):",g(rs))
# cancelled partial: closures in newest run cut to 45% (cancelled)
r0=copy.deepcopy(runs[0])
for j in r0["jobs"]:
    if j["name"]=="tests / closures":
        st=datetime.fromisoformat(j["started_at"].replace("Z","+00:00")); en=datetime.fromisoformat(j["completed_at"].replace("Z","+00:00"))
        j["completed_at"]=shift(j["started_at"],0.45*(en-st).total_seconds()); j["conclusion"]="cancelled"
print("one cancelled closures at 45%:",g([r0]+runs[1:]))
