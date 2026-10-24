#!/bin/bash
# poll every 300s up to 2h for the 2622 reviewer probe ref or new handoff-body returns
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
for i in $(seq 1 24); do
  OUT=$(git ls-remote origin 'refs/heads/probe/rev-2622-*' 2>/dev/null)
  if echo "$OUT" | grep -q 'probe/rev-2622-dcdc5654'; then
    echo "PROBE-HIT $OUT"; exit 0
  fi
  git ls-remote origin 'refs/heads/handoff-body/*' 2>/dev/null | grep -E 'r10-(currency|scores|loop-cpu|fly-gh-read-retry-2|record-api-budget|nightly-absent-new)' | sed 's/^\(.\{8\}\).*refs\/heads\/handoff-body\//RETURN-CANDIDATE \1 /' > /Users/timmalmstrom/hpo-orch/r10s4/returns-now.txt
  sleep 300
done
echo TIMEOUT
