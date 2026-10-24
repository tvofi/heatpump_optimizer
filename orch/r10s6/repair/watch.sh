#!/bin/bash
# exits when carry landed, or any w6 opener log newly ends (STOPPED/REFUSE/opened)
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
K=$(head -c 60 /Users/timmalmstrom/hpo-orch/r10s6/carries/carry-ci-graph-tidy.md)
for i in $(seq 1 80); do
  git fetch -q origin handoff/audit-r10-roster 2>/dev/null
  if git show FETCH_HEAD:dev/programme/rosters/wave-r10-groups.json | python3 -c "
import json,sys
k=sys.argv[1]
sys.exit(0 if any(g['group']=='R10-CI-LAYOUT-P2' and any(k in c for c in g['carry']) for g in json.load(sys.stdin)['groups']) else 1)" "$K"; then echo CARRY-LANDED; exit 0; fi
  if grep -lE "STOPPED|REFUSE|^PR=.*HEAD.*final|OPENED|opened" /Users/timmalmstrom/hpo-orch/r10s6/logs/open-*-w6*.log >/tmp/w6-ended.txt 2>/dev/null && [ -s /tmp/w6-ended.txt ]; then echo OPENER-ENDED; cat /tmp/w6-ended.txt; exit 0; fi
  sleep 90
done
echo TIMEOUT
