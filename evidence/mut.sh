#!/bin/bash
# usage: mut.sh <worktree> <evdir> MUTANT...   apply each, run app_push self-test, restore
wt=$1 ev=$2; shift 2; cd "$wt"
for m in "$@"; do
  python3 "$ev/mutants.py" "$m" || { echo "$m: APPLY-FAILED"; continue; }
  out=$(bash tools/pr/app_push.sh --self-test 2>&1)
  echo "$m: $(printf '%s\n' "$out" | grep 'app_push self-test:')"
  printf '%s\n' "$out" | grep -E '^ *(FAIL|not ok)' | sed "s/^/    $m /" | head -12
  git checkout -q -- tools/pr/app_push.sh
done
git status --porcelain; echo "restored to $(git rev-parse HEAD)"
