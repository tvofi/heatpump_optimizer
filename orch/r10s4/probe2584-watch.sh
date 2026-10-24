#!/bin/bash
# Logs PROBE-SEEN 2584 once when probe/rev-2584-ee2cfa33 appears on origin; relay needs the full 32-hex nonce, sent by the coordinator.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
cd "$R" || exit 1
while true; do
  t=$(git ls-remote origin refs/heads/probe/rev-2584-ee2cfa33 | cut -f1)
  if [ -n "$t" ]; then echo "$(date -u +%H:%M:%SZ) PROBE-SEEN 2584 probe/rev-2584-ee2cfa33 at ${t:0:8} (nonce 32-hex needed to relay)" >> "$D/coord-loop.log"; exit 0; fi
  sleep 60
done
