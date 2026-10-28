#!/bin/bash
# Reviewer's own harness (local-reviewer-s10, #2910): head ci_predict.py dropped into
# detached worktrees of #2883's heads, SELF-TEST READS arm alone and the full flagged run,
# against #2883's base 00ab2e97b^1 = 6349205b6.
set -u
REPO=/Users/timmalmstrom/heatpump_optimizer
HEAD_TREE=/Users/timmalmstrom/hpo-seats/r10s6/rev-2910
WT=/Users/timmalmstrom/hpo-seats/r10s6/rev-2910-wt
EV=/Users/timmalmstrom/hpo-seats/r10s6/rev-2910-out/ev
mkdir -p "$WT"
for c in 8f05b74d4 71987ff1e 7b071dbd7; do
  d=$WT/$c
  [ -d "$d" ] || git -C "$REPO" worktree add --detach "$d" "$c" >/dev/null 2>&1
  cp "$HEAD_TREE/tools/pr/ci_predict.py" "$d/tools/pr/ci_predict.py"
  for mode in arm noflag; do
    case $mode in
      arm) args="--only self-test-reads" ;;
      noflag) args="--only under-scoped" ;;
    esac
    s=$(date +%s)
    (cd "$d" && PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 6349205b6 $args) > "$EV/detect-$c-$mode.txt" 2>&1
    r=$?
    echo "RESULT head=$c mode=$mode rc=$r secs=$(( $(date +%s) - s ))" | tee -a "$EV/detect-results.txt"
  done
  git -C "$d" checkout -- tools/pr/ci_predict.py
done
