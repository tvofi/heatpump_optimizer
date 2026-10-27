#!/bin/bash
HEAD=8c4bec5c27cf4c46af6b572c00dc33a4feffba90
OUT=/Users/timmalmstrom/hpo-orch/r10s6/s7/ev/checkruns_final.json
for i in $(seq 1 24); do
  gh api "repos/tvofi/heatpump_optimizer/commits/$HEAD/check-runs?per_page=100" > "$OUT.tmp" 2>/dev/null
  if python3 - "$OUT.tmp" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
runs=d.get("check_runs",[])
live=[r for r in runs if r.get("status")!="completed"]
if live: sys.exit(1)
bad=[(r["name"],r.get("conclusion")) for r in runs if r.get("conclusion") not in ("success","skipped","neutral")]
print("ALL_CONCLUDED", len(runs), "bad:", bad)
sys.exit(0)
PY
  then mv "$OUT.tmp" "$OUT"; echo "settled at $(date -u +%H:%M:%SZ)"; exit 0; fi
  sleep 300
done
echo "TIMEOUT after 2h"; exit 2
