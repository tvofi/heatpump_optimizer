#!/bin/bash
# Wait until origin/fix/audit-r10-roster-pr is unchanged for 10 min (checked every 60s, up to 60 min).
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
LAST=""; SINCE=0
for i in $(seq 1 60); do
  H=$(git ls-remote origin refs/heads/fix/audit-r10-roster-pr | cut -f1)
  NOW=$(date +%s)
  if [ "$H" != "$LAST" ]; then LAST="$H"; SINCE=$NOW; echo "head $H at $(date -u +%H:%M:%SZ)"; fi
  if [ $((NOW-SINCE)) -ge 600 ]; then echo "STABLE $H"; exit 0; fi
  sleep 60
done
echo UNSTABLE-60MIN
