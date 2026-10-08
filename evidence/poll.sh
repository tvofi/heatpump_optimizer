#!/bin/bash
# one API call per 5-minute poll; exit when no required run is pending
cd /Users/timmalmstrom/hpo-seats/review-2057
H=4ff6152ea166d6e11db880ae9fa70727efcaa547
while :; do
  sleep 300
  gh api -i "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100&filter=all" > ev3/cr_head_raw.txt 2>&1
  code=$(head -1 ev3/cr_head_raw.txt)
  if echo "$code" | grep -q ' 403\| 429'; then
    reset=$(grep -i '^x-ratelimit-reset' ev3/cr_head_raw.txt | tr -dc 0-9); now=$(date +%s)
    [ -n "$reset" ] && [ "$reset" -gt "$now" ] && sleep $((reset-now+5)); continue
  fi
  awk 'BEGIN{b=0} /^\r?$/{b=1;next} b' ev3/cr_head_raw.txt > ev3/cr_head.json
  pend=$(python3 -c "
import json;d=json.load(open('ev3/cr_head.json'))
skip={'coverage','delivery-status','nightly-status'}
print(sum(1 for r in d['check_runs'] if r['status']!='completed' and r['name'] not in skip))")
  echo "$(date -u +%FT%TZ) pending_required=$pend total=$(python3 -c "import json;print(json.load(open('ev3/cr_head.json'))['total_count'])")" >> ev3/poll.log
  [ "$pend" = "0" ] && exit 0
done
