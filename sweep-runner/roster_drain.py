#!/usr/bin/env python3
"""Local stand-in for the retired roster seat (tvofi 2026-10-31). Tracked form owed: R10-ORCH-LEDGER beat job
roster-drain (+ census-10's roster_queue loop). Drains pending queue lines through tools/audit/seat/roster_queue.py
exactly as the seat's STATE-HANDOFF section 1 states, marks each line #done/#refused by exact-line match, and
prints one ROSTER-REFUSED line per refusal (the runner forwards them to the digest). Never releases a #held line."""
import os, subprocess, sys
Q = "<STATE_DIR>/s7/roster-queue-s7.txt"
R = "<STATE_DIR>/s9/sweep-runner"
EC = "<SEATS_DIR>/roster-s8/main"
WT = "<SEATS_DIR>/roster-s8/wt-run"
LC = "<SEATS_DIR>/roster-s8/main-lint"
env = dict(os.environ, PATH=os.path.expanduser("~/.local/state/hpo/venv-ci/bin") + ":" + os.environ["PATH"])
lines = open(Q).read().split("\n")
pend = [l for l in lines if l.strip() and not l.startswith("#")]
if not pend:
    sys.exit(0)
for l in pend:
    if " #" in l: print("ROSTER-SKIPPED: ' #' in the line, parse_line would cut it; rewrite it: " + l[:120])
pend = [l for l in pend if " #" not in l] or sys.exit(0)  # a trailing comment breaks parse_line: left for hand handling
def sh(*a, **k): return subprocess.run(a, env=env, text=True, capture_output=True, **k)
sh("git", "-C", EC, "fetch", "-q", "origin"); sh("git", "-C", EC, "checkout", "-q", "-B", "roster-s9-main", "origin/main")
sh("git", "-C", EC, "worktree", "remove", "--force", WT); sh("git", "-C", EC, "worktree", "prune")
qcopy, rep = f"{R}/roster-q.txt", f"{R}/roster-rep.txt"
open(qcopy, "w").write("\n".join(pend) + "\n")
before = len(open(rep).read().splitlines()) if os.path.exists(rep) else 0
sh("python3", "-I", "tools/audit/seat/roster_queue.py", "run", "1", str(len(pend)), "--queue", qcopy, "--report", rep,
   "--edit-checkout", EC, "--worktree", WT, "--lint-clone", LC, "--branch", "handoff/audit-r10-roster",
   "--alive", "<STATE_DIR>/s7/roster.alive", cwd=EC, timeout=3600)
new = open(rep).read().splitlines()[before:] if os.path.exists(rep) else []
cur = open(Q).read().split("\n")
cascade = 0
for op, res in zip(pend, new):
    if op not in cur:
        continue
    i = cur.index(op)
    if " pushed " in res:
        cur[i:i + 1] = ["#done " + op, "#note " + res.split(" | ")[0].replace("roster: ", "") + " (sweep runner)"]
    elif "is on no origin ref" in res:
        cascade += 1  # an earlier refusal left wt-run detached: not this op's refusal; left pending for the next pass
    else:
        cur[i:i + 1] = ["#refused " + op, "#note " + res]
        print("ROSTER-REFUSED: " + op[:120] + " :: " + res[-200:])
open(Q, "w").write("\n".join(cur))
if cascade:
    print(f"ROSTER-CASCADE: {cascade} line(s) left pending behind an earlier refusal's detached wt-run")
for op in pend[len(new):]:
    print("ROSTER-UNRUN: " + op[:120] + " (no report line; the run stopped early)")
