#!/bin/bash
# watch-green.sh <held-regex>: every 120 s; exit when main's latest push CI run is success,
# the queue file changes, or the window ends.
D=/Users/timmalmstrom/hpo-orch/r10s5; END=1792820700; Q0=$(md5 -q $D/merge-queue.txt)
export PATH=/Users/timmalmstrom/hpo-seats/r10s5/orch-wt/tools/audit/seat/shims:$PATH
while :; do
  [ "$(md5 -q $D/merge-queue.txt)" != "$Q0" ] && { echo "QUEUE CHANGED $(date -u +%FT%TZ)"; tail -3 $D/merge-queue.txt; exit 0; }
  m=$(gh run list --repo tvofi/heatpump_optimizer --branch main --event push --workflow CI --limit 1 --json headSha,status,conclusion,databaseId -q '.[]|"\(.headSha) \(.status) \(.conclusion) \(.databaseId)"')
  case "$m" in *" completed success "*) echo "MAIN GREEN $(date -u +%FT%TZ) $m"; exit 0;; esac
  [ $(date +%s) -ge $END ] && { echo "WINDOW END $(date -u +%FT%TZ) main: $m"; exit 0; }
  sleep 120
done
