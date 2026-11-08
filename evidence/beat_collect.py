"""Reviewer's harness: drive nightly_status.collect over a listing with an older
schedule nightly and a newer main dispatch titled by evaluating that tree's
nightly.yml run-name. Cases: dispatch lanes=beat completed, lanes=beat in flight,
lanes=all (null control). Prints the graded run and verdict."""
import sys, re, datetime as dt
sys.path.insert(0, sys.argv[2]); sys.path.insert(0, "tests")
from fns import _workflow_job, _gh_if, _gh_eval
import nightly_status as ns
yml = open(sys.argv[1]).read()
body = yml.split("\njobs:", 1)[1]
ids = re.findall(r"^  ([A-Za-z][\w-]*):$", body, re.M)
m = re.search(r"^run-name: \$\{\{ (.*) \}\}$", yml, re.M)
def title(l):
    if not m: return "Nightly"
    return eval(m.group(1).replace("inputs.lanes", repr(l)).replace("&&"," and ").replace("||"," or "), {"__builtins__": {}})
def jobs_for(ev, l):
    ctx = {"github.event_name": ev, "github.ref": "refs/heads/main", "inputs.lanes": l, **{f"needs.{x}.result": "success" for x in ids}}
    return [{"name": n, "status": "completed", "conclusion": "success" if _gh_eval(_gh_if(_workflow_job(body, n)), ctx) else "skipped"} for n in ids]
now = dt.datetime(2026, 11, 8, 12, 0, tzinfo=dt.timezone.utc)
for case, l, st in (("beat-done","beat","completed"),("beat-inflight","beat","in_progress"),("all-done","all","completed")):
    runs = {1: {"id":1,"event":"schedule","head_branch":"main","status":"completed","conclusion":"success","created_at":"2026-11-08T00:40:00Z","display_title":title("")},
            2: {"id":2,"event":"workflow_dispatch","head_branch":"main","status":st,"conclusion":"success" if st=="completed" else None,"created_at":"2026-11-08T09:00:00Z","display_title":title(l)}}
    jobs = {1: jobs_for("schedule",""), 2: jobs_for("workflow_dispatch", l)}
    def get(url,_t):
        if "/jobs" in url:
            rid=int(url.split("/runs/")[1].split("/")[0]); return {"total_count":len(jobs[rid]),"jobs":jobs[rid]}
        if re.search(r"/runs/\d+$", url.split("?")[0]):
            return runs[int(url.split("?")[0].rsplit("/",1)[1])]
        ev=url.split("event=")[1].split("&")[0]; return {"workflow_runs":[r for r in runs.values() if r["event"]==ev]}
    ns._get, ns._sleep = get, lambda s: None
    try:
        c,f,j,rec = ns.collect("o/r","nightly.yml",None,None,now=now)
        state, rc, _ = ns.verdict(c,f,j,now)
        print(f"RESULT case={case} title={title(l)!r} graded={c and c['id']} in_flight={f and f['id']} nightly_status={state} rc={rc}")
    except Exception as e:
        print(f"RESULT case={case} ERR {type(e).__name__}: {e}")
