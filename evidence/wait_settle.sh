#!/bin/bash
# Settle waiter for PR 2066 head 6308498975f49b3ed0f152700ee7c23b242387f8
# Polls the commit's check-runs every 300s until pending==0. Exit 0 = settled, 3 = still pending at cap.
SHA=6308498975f49b3ed0f152700ee7c23b242387f8
OUT=/Users/timmalmstrom/hpo-seats/review-2066/evidence/settle.log
cd /Users/timmalmstrom/hpo-seats/review-2066 || exit 1
for i in $(seq 1 21); do
  gh api "repos/tvofi/heatpump_optimizer/commits/$SHA/check-runs?per_page=100" \
     --jq '.check_runs[] | [.name, .status, (.conclusion // "-"), .id] | @tsv' > /tmp/r2066-poll-$i.tsv 2>/tmp/r2066-poll-err-$i.txt
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "[waiter] iter $i: gh api rc=$rc (backing off)" >> "$OUT"
    errcount=$((errcount+1))
    sleep 300
    continue
  fi
  if [ -s /tmp/r2066-poll-err-$i.txt ]; then
    echo "[waiter] iter $i: api stderr:" >> "$OUT"; cat /tmp/r2066-poll-err-$i.txt >> "$OUT"
  fi
  pend=$(awk -F'\t' '$2!="completed" && $2!="skipped"' /tmp/r2066-poll-$i.tsv | grep -c '' )
  tot=$(grep -c '' /tmp/r2066-poll-$i.tsv)
  echo "[waiter] iter $i $(date -u +%H:%M:%SZ): total=$tot pending=$pend" >> "$OUT"
  awk -F'\t' '$2!="completed"{print "  pending: "$1" "$2" run "$4}' /tmp/r2066-poll-$i.tsv >> "$OUT"
  if [ "$pend" -eq 0 ]; then
    echo "[waiter] SETTLED at iter $i" >> "$OUT"
    cp /tmp/r2066-poll-$i.tsv /Users/timmalmstrom/hpo-seats/review-2066/evidence/checkruns-settled.tsv
    sort /Users/timmalmstrom/hpo-seats/review-2066/evidence/checkruns-settled.tsv >> "$OUT"
    exit 0
  fi
  sleep 300
done
echo "[waiter] CAP REACHED, still pending -> re-dispatch" >> "$OUT"
exit 3
