# fix-2873-s8b state (round-3 repair of #2873, R10-DIAG-AGES)
- worktree: wt/ (branch s8b/r10-diag-ages, locked), code head da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46 on df1ee7b43
- body: body-recut.md (## Re-cut); RUNS_PLACEHOLDER filled from runs/summary.txt
- mutants: mutants.py, mut/results-head.txt, mut/results-oldprod.txt
- harness runs: harness-*.txt
- remaining: prepr.sh (PREPR_SKIP_CLOSURES=1), push handoff/r10-diag-ages, body_push.sh, update_pr.sh fix/r10-diag-ages <code> body
