#!/bin/bash
# Logs P1-PR once the r10-ci-layout-p1 PR opens.
D=/Users/timmalmstrom/hpo-orch/r10s4
cd /Users/timmalmstrom/hpo-seats/r10s3/orch-wt || exit 1
while true; do
  n=$(gh pr list --repo tvofi/heatpump_optimizer --head r10-ci-layout-p1 --state open --json number --jq '.[0].number' 2>/dev/null)
  if [ -n "$n" ] && [ "$n" != "null" ]; then echo "$(date -u +%H:%M:%SZ) P1-PR-OPENED r10-ci-layout-p1 #$n" >> "$D/coord-loop.log"; exit 0; fi
  sleep 120
done
