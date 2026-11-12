"""Reviewer's driver: plant a ratchet breach on a pull-request and a push event; judge with gate.judge at the tree given."""
import sys, time
sys.path.insert(0, sys.argv[1] + "/tools/ci")
import gate
from prelude import context
repo, head = "o/r", "H"
env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": repo, "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
ev = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": head}}}
pull = {"state": "open", "head": {"sha": head, "repo": {"full_name": repo}}, "base": {"ref": "main"}}
ALL = sorted(set(gate.gate_required()) | {"tests / ci-ratchet", "tests / coverage-ratchet", "tests / coverage"})
def fake(jobs):
    def get(path, params=None):
        if path.endswith("/pulls/7"): return 200, {}, pull
        if path.endswith("/runs/100/jobs"): return 200, {}, {"jobs": jobs}
        if "/runs/" in path and path.endswith("/jobs"):
            return 200, {}, {"jobs": [{"name": "gate", "status": "completed", "conclusion": "success", "id": 9}]}
        if path.endswith("ci.yml/runs"): return 200, {}, {"workflow_runs": []}
        return 404, {}, None
    return get
def jobs(names, red):
    return [{"name": "prelude", "status": "completed", "conclusion": "success"}] + [
        {"name": n, "status": "completed", "conclusion": "failure" if n == red else "success", "id": 1} for n in names]
cc = lambda b, h: True
pr_names = [n for n in ALL if n not in ("tests / ci-ratchet", "tests / coverage")]  # ci-ratchet/coverage do not run on a PR
push_names = [n for n in ALL if "closure-scope" not in n and n.split(" / ")[0] not in gate.BODY and n not in ("tests / budget-raise-gate",)]
for evname, names in (("pull_request", pr_names), ("push", push_names)):
    ctx = context(evname, ev if evname == "pull_request" else {}, env if evname == "pull_request" else {**env, "GITHUB_SHA": head})
    claim = {"kind": "code", "pr": "7" if evname == "pull_request" else ""}
    for red in (None, "tests / ci-ratchet", "tests / coverage-ratchet", "tests / fast (3.14)"):
        names2 = names + ([red] if red and red not in names else [])
        out, why, notes = gate.judge(ctx, claim, fake(jobs(names2, red)), cc, sleep=lambda s: None)
        print(f"RESULT event={evname} red={red} outcome={out!r} notes={notes}")
print("REQUIRED", {k: sorted(v) for k, v in gate.REQUIRED.items()})
