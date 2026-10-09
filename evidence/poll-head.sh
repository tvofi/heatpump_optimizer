#!/bin/bash
# Poll PR 2075 head until it becomes the expected re-cut sha, or until deadline.
# Rate limit: one gh call per 300 s (owner rule: <= once per 5 minutes).
TARGET=cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2
LOG=/Users/timmalmstrom/hpo-seats/review-2075/evidence2/poll-head.log
DEADLINE=$(( $(date +%s) + 6300 ))   # 105 min, under the 2h background limit
: > "$LOG"
n=0
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  n=$((n+1))
  out=$(gh pr view 2075 -R tvofi/heatpump_optimizer --json headRefOid,mergeable,updatedAt 2>&1)
  rc=$?
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  if [ "$rc" -ne 0 ]; then
    echo "$ts poll#$n rc=$rc FAILED: $out" >> "$LOG"
    sleep 300; continue
  fi
  sha=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["headRefOid"])' 2>/dev/null)
  echo "$ts poll#$n head=$sha $out" >> "$LOG"
  if [ "$sha" = "$TARGET" ]; then
    echo "$ts LANDED: head == $TARGET" >> "$LOG"
    exit 0
  fi
  sleep 300
done
echo "DEADLINE: head never became $TARGET" >> "$LOG"
exit 1
