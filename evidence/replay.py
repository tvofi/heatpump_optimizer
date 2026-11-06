# Replay real API runs/jobs on the production grader, as of a chosen instant T.
import sys, json, datetime as dt; sys.path.insert(0, sys.argv[1])
import nightly_status as ns
D="/tmp/rp"
def at(rid, T):
    r=json.load(open(f"{D}/run-{rid}.json")); j=json.load(open(f"{D}/jobs-{rid}.json"))["jobs"]
    done=lambda x: x.get("completed_at") and ns.parse_ts(x["completed_at"])<=T
    r=dict(r); 
    if not (r.get("updated_at") and ns.parse_ts(r["updated_at"])<=T and r["status"]=="completed"):
        r["status"],r["conclusion"]="in_progress",None
    jobs=[dict(x, conclusion=x["conclusion"] if done(x) else None, status=x["status"] if done(x) else "in_progress") for x in j]
    return r, jobs
def grade(T, rids):
    T=dt.datetime.fromisoformat(T)
    runs=[at(r,T) for r in rids if ns.parse_ts(json.load(open(f"{D}/run-{r}.json"))["created_at"])<=T]
    c,f=ns.pick_runs([r for r,_ in runs])
    jobs={r["id"]:jb for r,jb in runs}
    import inspect
    kw={}
    if "in_flight_jobs" in inspect.signature(ns.verdict).parameters and f and c and ns.failing_jobs(jobs[c["id"]]):
        kw["in_flight_jobs"]=jobs[f["id"]]
    s,code,lines=ns.verdict(c,f,jobs[c["id"]] if c else [],T,**kw)
    return f"{s} exit={code} concluded={c and c['id']} in_flight={f and f['id']}"
cases=[("2026-11-06T18:30:00+00:00",[42235215315,42242870295,42247578523],"stale-failure window (fix target)"),
       ("2026-11-06T19:00:00+00:00",[42235215315,42242870295,42247578523],"stale-failure window, later"),
       ("2026-11-04T01:00:00+00:00",[41555367389,41749544997],"NULL: real failure, newer run's slow still pending"),
       ("2026-11-04T06:00:00+00:00",[41555367389,41749544997],"NULL: real failure, newer run's slow FAILED")]
for T,rids,label in cases: print(f"{label} @ {T}: {grade(T,rids)}")
