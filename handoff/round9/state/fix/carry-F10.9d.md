# Carry from R9-F10.9d (#1812)

F10.9d made the `unrecorded` refusal in tools/audit/merge_fastpath.py specific to files a run_always script may read.
Measured at origin/main 3bd6f122 over main's last 120 first-parent merges, 50 pairs where main had moved:
`unrecorded` fell from 50 to 30 pairs and no `docs/delivery` row is among the remaining 32.
ELIGIBLE (main moved, no refusal) stays 0, because every moved pair also carries `full` (43), `claim` (29), `grader` (27), `workflow` (17) or `overlap` (7).
Any later stage that wants the fast path to fire on real pairs must price those classes, `full` first: it is the PR's own selection being FULL,
usually because the PR edits a gate file (tests/closure.py, tests/run.sh, tests/closures.json) which every F10 PR does.
Destination: the brief of whichever F10/PROC group owns merge_fastpath next (orchestrator to place).
