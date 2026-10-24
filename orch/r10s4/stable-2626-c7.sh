#!/bin/bash
# Wait for origin/fix/audit-r10-roster-pr to reach c7fd0568..., then be unchanged 10 min (60s polls, up to 90 min).
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
LAST=""; SINCE=0
for i in $(seq 1 90); do
  H=$(git ls-remote origin refs/heads/fix/audit-r10-roster-pr | cut -f1)
  NOW=$(date +%s)
  if [ "$H" != "$LAST" ]; then LAST="$H"; SINCE=$NOW; echo "head $H at $(date -u +%H:%M:%SZ)"; fi
  case "$H" in c7fd0568*) if [ $((NOW-SINCE)) -ge 600 ]; then echo "STABLE $H"; exit 0; fi;; esac
  sleep 60
done
echo TIMEOUT-90MIN
