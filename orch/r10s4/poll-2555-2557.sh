#!/bin/bash
# Polls every 300 s. Exits on the first event: probe ref for 2555 appears, 2557 row lands at head, or 30 min elapse.
cd /Users/timmalmstrom/hpo-seats/r10s3/orch-wt || exit 1
start=$(date +%s)
H2557=01d7ac8c75533bf9e4eff9cbc73d5205a65d6f1f
while true; do
  refs=$(git ls-remote origin 'refs/heads/probe/rev-2555-*' 2>/dev/null)
  if echo "$refs" | grep -q 'probe/rev-2555-c4e633e0'; then echo "EVENT probe-2555 $(echo "$refs" | grep 'probe/rev-2555-c4e633e0')"; exit 0; fi
  git fetch -q origin fix/r10-rca-orch-continuity 2>/dev/null
  if git cat-file -e $H2557:dev/programme/delivery/2557.md 2>/dev/null; then echo "EVENT row-2557 present at $H2557"; exit 0; fi
  if [ $(( $(date +%s) - start )) -ge 1800 ]; then echo "EVENT row-missing 2557 after 30 min at $H2557"; exit 0; fi
  echo "tick $(date -u +%H:%M:%SZ) no event"
  sleep 300
done
