#!/bin/bash
# Run a pass every ~175 s for up to $1 seconds; return at the first pass with an event or when a watched PID ends.
D=/Users/timmalmstrom/hpo-orch/r10s5/dispatch-seat; MAX=${1:-1050}; shift; t=0
while [ $t -lt $MAX ]; do
  out=$(bash $D/wait.sh 175 "$@"); t=$((t+175))
  p=$(bash $D/pass.sh)
  ev=$(echo "$p" | awk '/^-- review moved/{s=1;next} /^-- to-main/{s=0} s && !/^--/')
  [ -n "$out$ev" ] && { echo "$out"; echo "$p" | head -1; echo "$ev"; exit 0; }
done
echo "$(date -u +%FT%H:%M:%SZ) quiet for ${MAX}s"
