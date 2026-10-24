#!/bin/bash
# Poll origin every 300s for probe/rev-2628-ba85b07c, up to 100 min (20 polls).
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
for i in $(seq 1 20); do
  OUT=$(git ls-remote origin 'refs/heads/probe/rev-2628-ba85b07c' 2>/dev/null)
  if [ -n "$OUT" ]; then echo "PROBE-HIT $OUT"; exit 0; fi
  echo "poll $i $(date -u +%H:%M:%SZ) no-probe"
  [ "$i" -lt 20 ] && sleep 300
done
echo TIMEOUT
