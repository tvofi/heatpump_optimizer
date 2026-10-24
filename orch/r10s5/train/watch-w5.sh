#!/bin/bash
# watch-w5.sh <held-pr-regex> <parked-pr> <parked-line>: every 120 s; exit on a queue line not held,
# a changed queue line for <parked-pr>, the parked PR's carry audit clean (every 2nd pass), or window end.
D=/Users/timmalmstrom/hpo-orch/r10s5; W=/Users/timmalmstrom/hpo-seats/r10s5/orch-wt; HELD=$1; PP=$2; PL=$3; END=1792820700; i=0
export PATH=$W/tools/audit/seat/shims:$PATH
while :; do
  new=$(grep -E '[0-9]' $D/merge-queue.txt | grep -vE "^(direct )?($HELD|$PP) ")
  [ -n "$new" ] && { echo "NEW QUEUE $(date -u +%FT%TZ)"; echo "$new"; exit 0; }
  pl=$(grep -E "^(direct )?$PP " $D/merge-queue.txt | tail -1)
  [ "$pl" != "$PL" ] && { echo "NEW QUEUE (parked PR line changed) $(date -u +%FT%TZ)"; echo "$pl"; exit 0; }
  if [ $((i % 2)) = 0 ]; then
    a=$(cd $W && python3 tools/audit/carry_audit.py pr $PP 2>&1 | tail -1)
    case $a in *" 0 unrouted, 0 bad"*) echo "PARK CURED $(date -u +%FT%TZ) $a"; exit 0;; esac
  fi
  [ $(date +%s) -ge $END ] && { echo "WINDOW END $(date -u +%FT%TZ)"; exit 0; }
  i=$((i+1)); sleep 120
done
