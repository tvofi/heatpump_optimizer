#!/bin/bash
# Poll the head's check-runs every 300s until `mutation` and `coverage` settle.
# Exits when both are terminal, or after 90 minutes.
set -u
SHA=bab0aeb8d4aa04a4c36b3bdfcfb2978b69cc9f85
OUT=/Users/timmalmstrom/hpo-seats/review-2024/evidence-r3/poll_head.log
for i in $(seq 1 18); do
  gh api "repos/tvofi/heatpump_optimizer/commits/$SHA/check-runs?per_page=100" --paginate \
    > /Users/timmalmstrom/hpo-seats/review-2024/evidence-r3/checkruns_poll_$i.json 2>>"$OUT" \
    || { echo "poll $i: api failed" >>"$OUT"; sleep 300; continue; }
  state=$(python3 -I -c "
import json,glob
f=sorted(glob.glob('/Users/timmalmstrom/hpo-seats/review-2024/evidence-r3/checkruns_poll_$i.json'))[-1]
runs=json.load(open(f))['check_runs']
want=('mutation','coverage')
out=[]
for w in want:
    rs=[r for r in runs if r['name']==w]
    if not rs: out.append(w+':ABSENT'); continue
    r=max(rs,key=lambda x:x['started_at'])
    out.append(w+':'+r['status']+':'+str(r.get('conclusion'))+':'+str(r['id']))
print(' '.join(out))
")
  echo "poll $i $(date -u +%H:%M:%S) $state" >> "$OUT"
  case "$state" in
    *in_progress*|*queued*) sleep 300 ;;
    *) echo "settled" >> "$OUT"; exit 0 ;;
  esac
done
echo "gave up after 18 polls" >> "$OUT"
