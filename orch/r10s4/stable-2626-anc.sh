#!/bin/bash
# Wait for a head of origin/fix/audit-r10-roster-pr whose ancestry contains c7fd05680bbf56c7d3ce420981cc9f4461114c65,
# then require that head unchanged for 10 min. 60s polls, up to 90 min.
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
TARGET=c7fd05680bbf56c7d3ce420981cc9f4461114c65
LAST=""; SINCE=0
for i in $(seq 1 90); do
  H=$(git ls-remote origin refs/heads/fix/audit-r10-roster-pr | cut -f1)
  NOW=$(date +%s)
  if [ "$H" != "$LAST" ]; then
    LAST="$H"; SINCE=$NOW
    git fetch -q origin "$H" 2>/dev/null || git fetch -q origin refs/heads/fix/audit-r10-roster-pr
    if git merge-base --is-ancestor "$TARGET" "$H" 2>/dev/null; then ANC=yes; else ANC=no; fi
    echo "head $H ancestor-of-c7fd0568=$ANC at $(date -u +%H:%M:%SZ)"
  fi
  if [ "$(git merge-base --is-ancestor "$TARGET" "$H" 2>/dev/null && echo y)" = y ] && [ $((NOW-SINCE)) -ge 600 ]; then
    echo "STABLE $H"; exit 0
  fi
  sleep 60
done
echo TIMEOUT-90MIN
