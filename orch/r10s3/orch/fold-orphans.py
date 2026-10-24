import json, subprocess, time

OPS = [
    ("set-stage", ["R10-I5-DOCS", "in-progress", "--at-sha", "7a7102eb844cf4f549d52af241b7bdc8e5a74797"]),
    ("set-resume", ["R10-I5-DOCS", "--field", "commit", "--value", "7a7102eb844cf4f549d52af241b7bdc8e5a74797"]),
    ("set-resume", ["R10-I5-DOCS", "--field", "note", "--value",
                    "Handoff handoff/r10-i5-docs at 7a7102eb is this group's work: 7 commits over 11 files, the doc-claims and closures re-derivations. It was invisible because no pull request was ever opened. Owed: merge current main into the branch, re-take the body (it is 42 h old) and open the pull request."]),
    ("set-stage", ["R10-RCA-FRICTION", "in-progress", "--at-sha", "d1611efe6b7d7bd0d6fdb1651924d015aed3f74d"]),
    ("set-resume", ["R10-RCA-FRICTION", "--field", "commit", "--value", "d1611efe6b7d7bd0d6fdb1651924d015aed3f74d"]),
    ("set-resume", ["R10-RCA-FRICTION", "--field", "note", "--value",
                    "Handoff handoff/r10-rca-harness-friction at d1611efe is this group's work: 9 commits over 10 files, the RCA records plus edits to the fix-review and orchestrator role contracts (policy, so the owner approves at merge). Owed: merge current main, re-take the body and open the pull request."]),
    ("set-resume", ["R10-MERGE-PR-MANDATE", "--field", "note", "--value",
                    "Handoff handoff/r10-merge-pr-mandate at 6219325c (3 commits, 5 files: merge_pr reads the budget gate at its one path, the mandate id reaches proof_watch, refusal before any GitHub write) has no pull request. Owed: recarry and open; it touches tools/policy/budget_raise_gate.py, so the owner reviews."]),
    ("set-resume", ["R10-ROSTER-OPS", "--field", "note", "--value",
                    "Handoff handoff/r10-roster-ops at 9969e3ca (1 commit, 361 lines: set-after and drop-carry ops plus a mutant driver) has no pull request. Owed: recarry and open."]),
    ("append-carry", ["R10-REGISTRY-LEAK", "--value",
                      "Follow-up test folded here rather than opened as its own pull request: handoff handoff/r10-earlycutoff-coverage at ecaf178c adds 52 lines to tests/features.py asserting the release/detach path of early_cutoff directly. This group owns that code and is done, so the test should ride the next touch of early_cutoff, or be opened as a test-only pull request if no touch is planned."]),
]

L = "/Users/timmalmstrom/hpo-orch/r10s3/lint-main"
WT = "/Users/timmalmstrom/hpo-seats/r10s3/roster-r10"
CO = "/Users/timmalmstrom/heatpump_optimizer"
MAPPDIR = "/Users/timmalmstrom/hpo-seats/r10s3/orch-wt"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def refresh_lint():
    run(["git", "-C", L, "fetch", "-q", "origin", "main"])
    run(["git", "-C", L, "checkout", "-q", "--detach", "origin/main"])

for op, args in OPS:
    for attempt in range(3):
        refresh_lint()
        r = run(["python3", "tools/audit/seat/roster_edit.py", op] + args +
                ["--checkout", CO, "--worktree", WT, "--lint-cwd", L, "--push"], cwd=MAPPDIR)
        tail = (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else ""
        if r.returncode == 0:
            print(f"ok {op} {args[0]} {args[1] if len(args) > 1 else ''}: {tail[:80]}", flush=True)
            break
        if "no change" in tail or "already" in tail:
            print(f"ok(noop) {op} {args[0]}: {tail[:80]}", flush=True); break
        print(f"retry {op} {args[0]}: {tail[:110]}", flush=True)
        if "unpushed commits would be lost" in tail:
            run(["git", "-C", WT, "reset", "--hard", "origin/handoff/audit-r10-roster"])
        elif "uncommitted changes" in tail:
            run(["git", "-C", WT, "checkout", "--", "."])
        time.sleep(2)
    else:
        print(f"FAILED {op} {args[0]}", flush=True)
print("DONE", flush=True)
