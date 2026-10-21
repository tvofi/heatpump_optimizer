#!/bin/bash
# runs in the head worktree; applies each mutant, runs the owning self-test, restores
cd "$1"; shift
for m in M0 "$@"; do
  if [ $m = M0 ]; then f=tools/pr/app_push.sh; else f=$(python3 "$EVD/mutants.py" $m) || { echo "$m APPLY-FAILED"; continue; }; fi
  case $f in *update_pr.sh) out=$(bash tools/audit/seat/update_pr.sh --self-test 2>&1); tally=$(printf '%s\n' "$out" | grep -E '^(pr_args|delivery_row) self-test:' | paste -sd' ');;
             *) out=$(bash tools/pr/app_push.sh --self-test 2>&1); tally=$(printf '%s\n' "$out" | grep -E '^app_push self-test:');; esac
  echo "$m: $tally"; printf '%s\n' "$out" | grep -E '^\s*(FAIL|not ok|✗)' | sed 's/^/    /' | head -12
  git checkout -q -- tools/
done
