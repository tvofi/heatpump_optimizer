#!/bin/bash
# Wait up to $1 seconds (25 s steps, alive touched each step), returning early when a watched PID ends.
R=/Users/timmalmstrom/hpo-orch/r10s5; MAX=${1:-175}; shift; PIDS="$*"; t=0
while [ $t -lt $MAX ]; do
  sleep 25; t=$((t+25)); touch $R/dispatch.alive
  for p in $PIDS; do kill -0 $p 2>/dev/null || { echo "PID $p ENDED"; exit 0; }; done
done
