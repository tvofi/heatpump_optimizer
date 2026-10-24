#!/bin/bash
set -u
E="python3 -I tools/audit/seat/roster_edit.py"
CO=/Users/timmalmstrom/heatpump_optimizer
WT=/Users/timmalmstrom/hpo-seats/r10s3/roster-r10
L=/Users/timmalmstrom/hpo-orch/r10s3/lint-main
cd /Users/timmalmstrom/hpo-seats/r10s3/orch-wt
git -C "$L" fetch -q origin main && git -C "$L" checkout -q --detach origin/main

r() { echo "--- $* $(date -u +%FT%TZ)"; $E "$@" --checkout "$CO" --worktree "$WT" --lint-cwd "$L" --push; echo "rc=$?"; }

r set-resume R10-ROSTER-OPS --field next_step --value "open the ops handoff at 9969e3ca (set-after, drop-carry, mutant driver) as a draft PR; then dispatch the brief's second deliverable at a new head: the roster-sync reconciler in state_docs.py beat (--apply, dry run by default), deriving merged->done and open->in-progress from the repository and appending a merged body's Carry through carry_audit.py's parser, never overwriting deferred/refused."
r set-resume R10-ORCH-MACHINERY --field note --value "Build gate (orchestrator, 2026-10-20): the build is gated on R10-ROSTER-OPS' roster-sync reconciler (state_docs.py beat --apply), which the design allocates to that group at section 6.4. Do not dispatch the build until it merges or the seam is explicitly re-cut in the design."
echo "DONE $(date -u +%FT%TZ)"
