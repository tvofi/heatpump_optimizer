#!/bin/bash
# usage: mut1.sh <evdir> <head> <mutant>: own detached worktree, apply, run the owning self-test, discard
ev=$1 h=$2 m=$3 wt=$(mktemp -d)/wt
git -C /home/user/heatpump_optimizer worktree add -q --detach "$wt" "$h" && cd "$wt" || exit 1
if python3 "$ev/mutants.py" "$m"; then
  git diff --stat | tail -1 | sed "s/^/$m diff: /"
  case $m in W6*) out=$(bash tools/audit/seat/update_pr.sh --self-test 2>&1); pat='pr_args self-test:';; *) out=$(bash tools/pr/app_push.sh --self-test 2>&1); pat='app_push self-test:';; esac
  echo "$m: $(printf '%s\n' "$out" | grep "$pat")"
  printf '%s\n' "$out" | grep -E '^ *(FAIL|not ok)' | sed "s/^/    $m /" | head -12
else echo "$m: APPLY-FAILED"; fi
cd /; git -C /home/user/heatpump_optimizer worktree remove --force "$wt"
