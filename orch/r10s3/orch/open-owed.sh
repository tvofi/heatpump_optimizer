#!/bin/bash
# Open the four older owed handoffs as drafts, sequentially; each merges origin/main first.
set -u
R=/Users/timmalmstrom/heatpump_optimizer
open() {
  t=$1; sha=$2; title=$3; group=$4; shift 4
  echo "===== $t $(date -u +%FT%TZ)"
  bash "$R/tools/audit/seat/open_pr.sh" "$t" "$sha" "$title" "$group" "$@"
  echo "open_pr rc=$? for $t $(date -u +%FT%TZ)"
}
open r10-roster-ops 9969e3ca80bd6255cd1231b1b4e53410a6fbeb88 \
     "roster-edit: set-after and drop-carry ops, with a mutant driver" R10-ROSTER-OPS 2496
open r10-i5-docs 7a7102eb844cf4f549d52af241b7bdc8e5a74797 \
     "docs: pin the drifted labels, banner sample and service counts in doc_claims" R10-I5-DOCS 2222 2298
open r10-rca-harness-friction d1611efe6b7d7bd0d6fdb1651924d015aed3f74d \
     "rca: harness friction - one step-6 refusal under two keys; role contracts corrected" R10-RCA-FRICTION \
     2331 2353 2409 2428 2429 2436 2437 2438
open r10-merge-pr-mandate 6219325ca20928f82c80880b1ed7fadf3e1c93b2 \
     "fix(merge_pr): read the budget gate at its one path and refuse before any write" R10-MERGE-PR-MANDATE 2497
echo "ALL DONE $(date -u +%FT%TZ)"
