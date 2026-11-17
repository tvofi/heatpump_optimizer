import json, sys, tempfile, pathlib
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import loop_ledger as L
def run(i, hour, c="failure", attempt=1, sha=None, event="pull_request", branch="b", pr=None):
    return {"id": i, "t": f"2026-11-01T{hour:02d}:00:00Z", "c": c, "attempt": attempt, "head_sha": sha, "event": event, "head_branch": branch, "pr": pr}
def jobs(*gates, extra=()):
    return {"attempt": len(gates), "jobs": [{"name": "gate", "conclusion": c, "run_attempt": k + 1} for k, c in enumerate(gates)] + list(extra)}
def show(title, runs, listed, subj=None):
    d = pathlib.Path(tempfile.mkdtemp()); (d / "jobs").mkdir()
    (d / "ci_runs.json").write_text(json.dumps(runs))
    for i, doc in listed.items(): (d / "jobs" / f"jobs_{i}.json").write_text(json.dumps(doc))
    print("##", title)
    try:
        for ln in L.red_lines(d, (subj or {}).get): print("   ", ln[:230])
    except Exception as e: print("    RAISED", type(e).__name__, e)
A, B, M, N = "a"*40, "b"*40, "d"*40, "e"*40
MAIN = {"event": "push", "branch": "main"}
show("P1 window left edge: the first main run in the window is already red, no green before it (spell opener unobserved)",
     [run(11, 1, sha=M, **MAIN), run(12, 2, sha=A, pr=9)], {11: jobs("failure"), 12: jobs("failure")},
     {M: "Merge pull request #41 from o/fix/x"})
show("P2 main red at attempts 1,2 then green at 3; a head red between",
     [run(11, 1, "success", attempt=3, sha=M, **MAIN), run(12, 2, sha=A, pr=9)], {11: jobs("failure", "failure", "success"), 12: jobs("failure")},
     {M: "Merge pull request #41 from o/fix/x"})
show("P3 narrow rows (a ci_runs.json written before this PR: no head_sha/event/pr keys)",
     [{"id": 1, "t": "2026-11-01T01:00:00Z", "c": "failure", "attempt": 1}, {"id": 2, "t": "2026-11-01T02:00:00Z", "c": "success", "attempt": 1}], {1: jobs("failure")})
show("P4 listing at the latest attempt with no gate job, run concluded failure (e.g. prelude failed, gate never listed)",
     [run(1, 1, sha=A, pr=5)], {1: {"attempt": 1, "jobs": [{"name": "prelude", "conclusion": "failure", "run_attempt": 1}]}})
show("P5 gate skipped/cancelled at the latest attempt on a head, run concluded cancelled",
     [run(1, 1, "cancelled", sha=A, pr=5)], {1: jobs("cancelled")})
show("P6 head red while main red; the PR's later commit green after main fixed (design: main's PR, not own)",
     [run(10, 1, "success", sha=B, **MAIN), run(11, 2, sha=M, **MAIN), run(12, 3, sha=A, pr=9), run(13, 4, "success", sha=N, **MAIN), run(14, 5, "success", sha="f"*40, pr=9)],
     {11: jobs("failure"), 12: jobs("failure")}, {M: "Merge pull request #41 from o/fix/x"})
show("P7 squash-merge subject on main's first red run",
     [run(10, 1, "success", sha=B, **MAIN), run(11, 2, sha=M, **MAIN)], {11: jobs("failure")}, {M: "loop_ledger: something (#41)"})
show("P8 a listing with jobs: null / malformed row",
     [run(1, 1, sha=A, pr=5)], {1: {"attempt": 1, "jobs": None}})
show("P9 a run row with pr as string",
     [run(1, 1, sha=A, pr="5"), run(2, 2, "success", sha=B, pr="5")], {1: jobs("failure"), 2: jobs("success")})
