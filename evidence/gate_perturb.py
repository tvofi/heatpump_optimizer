"""Reviewer-built harness (not the finder's): every name gate owes, perturbed to
failure/skipped/cancelled/absent/pending, must FAIL and name it; all-green PASSes."""
import sys; sys.path.insert(0, sys.argv[1])
import gate
from prelude import context
repo, head = "o/r", "H"
env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": repo, "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
ev = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": head}}}
pull = {"state": "open", "head": {"sha": head, "repo": {"full_name": repo}}, "base": {"ref": "main"}}
def fake(jobs):
    def get(path, params=None):
        if path.endswith("/pulls/7"): return 200, {}, pull
        if path.endswith("/runs/100/jobs"): return 200, {}, {"jobs": jobs}
        if path.endswith("ci.yml/runs"): return 200, {}, {"workflow_runs": []}
        return 404, {}, None
    return get
bad = 0; n = 0
for cls, cc in (("pr", False), ("pr-cc", True)):
    ctx = context("pull_request", ev, env)
    names = gate.REQUIRED[cls]
    green = [{"name": "prelude", "status": "completed", "conclusion": "success"}] + [
        {"name": x, "status": "completed", "conclusion": "success"} for x in names]
    o = gate.judge(ctx, {"kind": "code", "pr": "7"}, fake(green), lambda b, h: cc)[0]
    print(f"RESULT null {cls}: {o}"); n += 1; bad += o != "PASS"
    for x in names:
        for mode in ("failure", "skipped", "cancelled", "timed_out", "absent", "pending"):
            if mode == "absent": js = [j for j in green if j["name"] != x]
            elif mode == "pending": js = [dict(j, status="in_progress", conclusion=None) if j["name"] == x else j for j in green]
            else: js = [dict(j, conclusion=mode) if j["name"] == x else j for j in green]
            o = gate.judge(ctx, {"kind": "code", "pr": "7"}, fake(js), lambda b, h: cc)[0]
            n += 1
            if not (o.startswith("FAIL") and x in o):
                bad += 1; print(f"HOLE {cls} {x} {mode}: {o}")
# push class
pctx = context("push", {"ref": "refs/heads/main", "after": "M"}, env)
names = gate.REQUIRED["push"]
green = [{"name": "prelude", "status": "completed", "conclusion": "success"}] + [
    {"name": x, "status": "completed", "conclusion": "success"} for x in names]
try:
    o = gate.judge(pctx, {"kind": "code", "pr": ""}, fake(green))[0]; print("RESULT null push:", o); n += 1; bad += o != "PASS"
    for x in names:
        js = [dict(j, conclusion="failure") if j["name"] == x else j for j in green]
        o = gate.judge(pctx, {"kind": "code", "pr": ""}, fake(js))[0]; n += 1
        if not (o.startswith("FAIL") and x in o): bad += 1; print("HOLE push", x, o)
except Exception as e: print("push arm error", repr(e))
print(f"RESULT perturb: {n} cases, {bad} holes; pr={len(gate.REQUIRED['pr'])} pr-cc={len(gate.REQUIRED['pr-cc'])} push={len(gate.REQUIRED['push'])}")
sys.exit(1 if bad else 0)
