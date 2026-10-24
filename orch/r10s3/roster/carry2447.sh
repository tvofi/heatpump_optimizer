#!/bin/bash
set -euo pipefail
R=~/hpo-orch/r10s3/roster; O=~/hpo-seats/r10s3/orch-wt
cd $O; git fetch -q origin
git worktree prune
[ -d $R/lint-main ] && git worktree remove --force $R/lint-main || true
git worktree add -q --detach $R/lint-main origin/main
if [ ! -d $R/wt ]; then git worktree add -q -b roster-tmp-2447 $R/wt origin/handoff/audit-r10-roster; fi
ls $R/c2447
cd $R/wt
for x in "R10-POLICY-FIXER-MD 1" "R10-POLICY-FIXER-MD 2" "R10-BRIEFS-FOLD 3" "R10-CI-LAYOUT 4" "R10-CI-LAYOUT 5"; do
  g=${x% *}; n=${x#* }
  python3 $O/tools/audit/seat/roster_edit.py --lint-cwd $R/lint-main --worktree $R/wt --branch roster-tmp-2447 --push --roster-ref handoff/audit-r10-roster append-carry $g @$R/c2447/$n
done
git log --oneline -6
