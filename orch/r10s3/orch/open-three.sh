#!/bin/bash
# Open the three handed-off PRs sequentially; each runs its own prepr.
set -u
R=/Users/timmalmstrom/heatpump_optimizer
open() {
  t=$1; wt=$2
  echo "===== $t $(date -u +%FT%TZ)"
  bash "$R/tools/pr/app_push.sh" tvofi/heatpump_optimizer "$wt" "handoff/$t" \
       "/Users/timmalmstrom/hpo-orch/r10s3/orch/body/$t.md"
  echo "app_push rc=$? for $t $(date -u +%FT%TZ)"
}
open r10-sav-reasons   /Users/timmalmstrom/hpo-seats/r10s3/r10-sav-reasons/wt
open r10-codeql-cap    /Users/timmalmstrom/hpo-seats/r10s3/codeql-cap/wt
open r10-night-folds   /Users/timmalmstrom/hpo-seats/r10s3/r10-night-folds/wt
echo "ALL DONE $(date -u +%FT%TZ)"
