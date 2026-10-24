#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/r10s3/orch-wt || exit 1
start=$(date +%s); H=01d7ac8c75533bf9e4eff9cbc73d5205a65d6f1f
while true; do
  git fetch -q origin fix/r10-rca-orch-continuity 2>/dev/null
  if git cat-file -e $H:dev/programme/delivery/2557.md 2>/dev/null; then echo "EVENT row-2557 present at $H"; exit 0; fi
  if [ $(( $(date +%s) - start )) -ge 1800 ]; then echo "EVENT row-missing 2557 after 30 min at $H"; exit 0; fi
  echo "tick $(date -u +%H:%M:%SZ) row-missing"; sleep 300
done
