"""Reviewer's own harness (not the finder's; none committed): does a lanes=beat
dispatch, the newest concluded nightly run, read green in tests/nightly_status.py?"""
import sys, re, datetime as dt
sys.path.insert(0, sys.argv[2]); sys.path.insert(0, "tests")
from fns import _workflow_job, _gh_if, _gh_eval
import nightly_status as ns
yml = open(sys.argv[1]).read()
body = yml.split("\njobs:", 1)[1]
ids = re.findall(r"^  ([A-Za-z][\w-]*):$", body, re.M)
now = dt.datetime(2026, 11, 8, 2, 0, tzinfo=dt.timezone.utc)
for lanes in ("beat", "all"):
    ctx = {"github.event_name": "workflow_dispatch", "github.ref": "refs/heads/main",
           "inputs.lanes": lanes, **{f"needs.{m}.result": "success" for m in ids}}
    try:
        runs = {n: _gh_eval(_gh_if(_workflow_job(body, n)), ctx) for n in ids}
    except Exception as e:
        print("EVAL-ERR", e); continue
    jobs = [{"name": n, "conclusion": "success" if r else "skipped"} for n, r in runs.items()]
    run = {"id": 1, "event": "workflow_dispatch", "head_branch": "main", "status": "completed",
           "conclusion": "success", "created_at": "2026-11-08T01:00:00Z",
           "run_started_at": "2026-11-08T01:00:00Z", "updated_at": "2026-11-08T01:02:00Z"}
    state, rc, lines = ns.verdict(run, None, jobs, now)
    print(f"RESULT lanes={lanes} nightly_status={state} rc={rc} ran={sorted(n for n,r in runs.items() if r)}")
    print("   ", lines[0])
