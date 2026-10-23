"""Reviewer-built probe (not the finder's): gate.gate() when an edit run NEWER than the
code run carries a fail-closed pr-contract (codescan_wait found no finished codeql)."""
import sys
sys.path.insert(0, "tools/ci")
import gate as g

env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
ev = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": "H"}}}
ctx = g.context("pull_request", ev, env)
green = {n: ("completed", "success") for n in g.REQUIRED["pr"]}
green["prelude"] = ("completed", "success")
green["gate"] = ("completed", "failure")
api = {"prelude": {"conclusion": "success", "kind": "code", "pr": "7"}, "reaches_cc": False,
       "open_pr_heads": set(), "jobs": green,
       "live_pr": {"head_sha": "H", "base_ref": "main", "state": "open", "same_repo": True}}
body = {k: v for k, v in green.items() if k.split(" / ")[0] in g.BODY}


def edit_run(prc):
    return {"id": 200, "title": g.title("edit", "7", "main"), "status": "completed",
            "jobs": {**body, "pr-contract / pr-contract": ("completed", prc), "gate": ("completed", "failure"),
                     "prelude": ("completed", "success")}}


print("RESULT code-run gate, newer edit run pr-contract failure:", g.gate(ctx, {**api, "runs_at_head": [edit_run("failure")]}))
print("RESULT null: newer edit run pr-contract success:", g.gate(ctx, {**api, "runs_at_head": [edit_run("success")]}))
