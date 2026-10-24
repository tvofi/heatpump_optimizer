#!/bin/bash
# NOT EXECUTED by the prep seat. Run by the orchestrator, in order.
# Each step lints (brief_lint, fresh main) and, with --push, pushes the tmp branch; the
# next step resets onto origin/<tmp branch>, so edits accumulate. Final landing on
# handoff/audit-r10-roster follows the same convention as carry2447.sh.
set -euo pipefail
R=/Users/timmalmstrom/hpo-orch/r10s3/roster; P=$R/ci-prep
O=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
export PATH=/Users/timmalmstrom/hpo-seats/r10s3/shims:$PATH
cd $O; git fetch -q origin; git worktree prune
[ -d $R/lint-main ] && git worktree remove --force $R/lint-main || true
git worktree add -q --detach $R/lint-main origin/main
[ -d $R/wt ] || git worktree add -q -b roster-tmp-cilayout $R/wt origin/handoff/audit-r10-roster
cd $R/wt
COMMON="--lint-cwd $R/lint-main --worktree $R/wt --branch roster-tmp-cilayout --push --roster-ref handoff/audit-r10-roster"
RE="python3 $O/tools/audit/seat/roster_edit.py $COMMON"
CP="python3 $P/ci_prep_edit.py"

# ---- B2: fold RATCHET-RED into PR 0. 'done' is in roster_lib.DONE_STAGES, so the group is
# not open: the tick PLAN skips it and nothing offers a fixer. ('deferred' also skips but keeps
# the group open and blocking closure.) Its carry is empty, so nothing needs re-routing first.
$RE set-stage R10-CI-RATCHET-RED done
$RE set-resume R10-CI-RATCHET-RED --field note @$P/note-ratchet-red.txt

# ---- B1: one owner per carry (no roster_edit op removes a carry; ci_prep_edit.py drop-carry does)
# carry 5 (#2441 field-coverage pathspec): owner R10-SEAT-SELFTESTS-CI, paid by #2444 (merged).
#   Verify first: bash dev/audit/harnesses/r10_field_coverage_paths.sh origin/main  -> misread=0
$CP drop-carry R10-CI-LAYOUT "Source: #2441 Forward-carry (owned workflow, tvofi review)." $COMMON
# carry 6 (body_push/ci_predict): owner R10-CI-LAYOUT (PR 2, U9); #2447 does not pay it.
$CP drop-carry R10-PREPR-UNPINNED-RED "Source: #2441 Friction. body_push.sh: unenforced" $COMMON
# #2444's three forward-carries: owner R10-CI-LAYOUT PR G, via the controlled entries 12 and 13.
# Drop the three uncontrolled originals they supersede, and the census-cost routing (11 and 14):
# tvofi decided custom_components/ stays out of the pathspec; it owes no unit (recorded in the brief).
$CP drop-carry R10-CI-LAYOUT "Source: #2444 Forward-carry. The seven unwired self-tests outside" $COMMON
$CP drop-carry R10-CI-LAYOUT "Source: #2444 Forward-carry. \`merge_pr.sh\`'s path after its gates" $COMMON
$CP drop-carry R10-CI-LAYOUT "Source: #2444 Forward-carry. The field-coverage census copies" $COMMON
# KEPT (orchestrator): $CP drop-carry R10-CI-LAYOUT "Source: #2444 Forward-carry. Supersedes the uncontrolled #2444 entry at roster ebf81fc1d. Routing of a cost question" $COMMON

# ---- B6: CI-LAYOUT brief, owner_gate, next_step
$RE edit-brief R10-CI-LAYOUT @$P/brief-ci-layout.txt
$CP set-owner-gate R10-CI-LAYOUT @$P/owner-gate-ci-layout.txt $COMMON
$RE set-resume R10-CI-LAYOUT --field next_step @$P/next-step-ci-layout.txt
git log --oneline -12
