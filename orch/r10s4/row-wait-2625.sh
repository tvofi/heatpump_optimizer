#!/bin/bash
# Recheck dev/programme/delivery/2625.md at PR 2625 head every 5 min, up to 30 min.
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
H=10a490f9bc77f1bf148b3774eb6b830eadd3d4c8
for i in $(seq 1 6); do
  git fetch -q origin "$H" 2>/dev/null
  if git cat-file -e "${H}:dev/programme/delivery/2625.md" 2>/dev/null; then echo ROW-OK; exit 0; fi
  echo "poll $i $(date -u +%H:%M:%SZ) row-missing"
  [ "$i" -lt 6 ] && sleep 300
done
echo ROW-MISSING-30MIN
