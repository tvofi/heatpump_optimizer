#!/bin/bash
# For every merge commit on origin/main since the file existed, replay the merge
# with merge-tree and report whether bugclasses.json conflicted.
cd "$(git rev-parse --show-toplevel)" || exit 2
n=0; c=0; fail=0
for m in $(git rev-list --merges --since=2026-09-23 origin/main); do
  p1=$(git rev-parse $m^1); p2=$(git rev-parse $m^2)
  b=$(git merge-base $p1 $p2) || continue
  touched=0
  for side in $p1 $p2; do
    if [ -n "$(git diff --name-only $b $side -- tools/audit/bugclasses.json dev/audit/config/bugclasses.json)" ]; then touched=$((touched+1)); fi
  done
  [ $touched -lt 2 ] && continue
  n=$((n+1))
  out=$(git merge-tree --write-tree --name-only $p1 $p2 2>&1); rc=$?
  if [ $rc -gt 1 ]; then fail=$((fail+1)); echo "FAIL $m"; continue; fi
  if [ $rc -eq 1 ] && echo "$out" | grep -q 'bugclasses.json'; then
    c=$((c+1)); echo "CONFLICT $(git log -1 --format='%h %ad %s' --date=iso $m)"
  else
    echo "clean    $(git log -1 --format='%h %ad %s' --date=iso $m)"
  fi
done
echo "both-sides-touched merges: $n  conflicted on bugclasses: $c  merge-tree failures: $fail"
