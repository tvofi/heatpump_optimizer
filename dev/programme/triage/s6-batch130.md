# Proposal triage, session s12, batch 130 (P401)

The rolling batch after batch 129. Facts were re-read at origin/main `b07627250`, which carries `1e994e484` ("pr_args.sh fixes its directory at source time"). The proposal was filed against `294a880da`, a main without that commit.

## P401: update-pr-tools-root, the freshness check measures the main checkout

Verdict: REJECT, a duplicate of P362 (`dev/programme/triage/s6-batch105.md#P362`, carried to R10-OPENER-REUSE). The defect it reports no longer reproduces: `1e994e484` landed the fix P362 asked for, and the carry this proposal would add asks for the same lines, which are already in the tree. No carry, no roster op.

Source: the orchestrator's queue line `s12-update-pr-tools-root`, 2026-11-07.

Instances:
- **The mechanism is P362's.** `pr_tools_fresh` resolved its directory from `${BASH_SOURCE[0]}` at call time. `update_pr.sh` and `open_pr.sh` run `cd "$M"` to the main checkout first, so a relative invocation measured the main checkout. The proposal's mechanism and its fix (an absolute `PR_ARGS_DIR` fixed at source time) are P362's.
- **It landed before this ruling was drafted.** `git merge-base --is-ancestor 1e994e484 origin/main` succeeds. `git grep -c PR_ARGS_DIR origin/main -- tools/audit/seat/pr_args.sh` prints a count above zero; the same command at `294a880da`, the base the first ruling read, finds none. That is why the first ruling measured a defect that the head had already fixed.
- **Reproduction at `b07627250`, with its null control.** Two detached worktrees: a fresh one at origin/main and a stale sibling reset behind it. A probe sources `pr_args.sh` from the fresh worktree by a relative path, then `cd`s into the sibling and calls `pr_tools_fresh`:
  - the tree as it is: `rc=0`, FRESH. The defect does not reproduce;
  - the mutant, `pr_args.sh` with its `# mut:argsdir` line deleted (call-time resolution restored): `REFUSE: STALE CHECKOUT ... behind origin/main`. The probe can detect the defect, so the clean run is a result.
- **The pin is in the tree.** `pr_args.sh`'s self-test `fresh` block carries the `# P362/P401` arms: a relative source followed by a `cd` into a stale sibling passes, the `mut:argsdir` mutant refuses, a stale clone still refuses, and `update_pr.sh` run by a relative path from a fresh worktree whose common checkout lags passes.
- **Counts dropped.** The first ruling's 175-commit lag and 77 STALE-CHECKOUT notices were taken on a base without `1e994e484`. They describe the old call-time resolution and no current tree, and are not carried.

What is not a repo change: the dispatch seat's update scripts exported `HPO_ALLOW_STALE_TOOLS=1` to get past the old refusal, and can drop it now that the refusal no longer fires on a relative invocation. That is the seat's own script state, outside the tree. Carry: dismissed: not a repository change; the orchestrator drops the export from its host-local scripts.

Cost: none. Nothing is built.
