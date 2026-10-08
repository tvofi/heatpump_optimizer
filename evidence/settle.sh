#!/bin/bash
R=/Users/timmalmstrom/hpo-seats/review-2054/r2
while true; do
  sleep 300
  out=$(gh api -i "repos/tvofi/heatpump_optimizer/commits/b34eaf56ded7cc1eff6d62bc0663cb13386b28f7/check-runs?per_page=100" 2>&1)
  if echo "$out" | head -1 | grep -qE ' 40[39]| 429'; then
    reset=$(echo "$out" | grep -i '^x-ratelimit-reset:' | tr -dc 0-9); now=$(date +%s)
    echo "rate-limited until $reset" >> $R/settle.log; [ -n "$reset" ] && [ "$reset" -gt "$now" ] && sleep $((reset-now+5)); continue
  fi
  echo "$out" | sed -n '/^{/,$p' | python3 -c '
import json,sys;d=json.load(sys.stdin)
for c in d["check_runs"]: print("\t".join([c["name"],c["status"],c["conclusion"] or "-",str(c["id"])]))' > $R/checkruns-final.tsv
  date -u >> $R/settle.log
  grep -q in_progress\\\|queued $R/checkruns-final.tsv || { echo SETTLED >> $R/settle.log; break; }
done
