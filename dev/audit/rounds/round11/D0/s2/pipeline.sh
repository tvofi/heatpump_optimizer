#!/usr/bin/env bash
# D0-s2 orchestration (not a harness): after a slot frees, run the store control, then the M6 queue.
# Usage: bash dev/audit/rounds/round11/D0/s2/pipeline.sh <wait-pid|-> <slot i>/<k>
set -u
D=dev/audit/rounds/round11/D0/s2
PY=$HOME/venv-ci/bin/python3
export PYTHONPATH=tests/hastub
[ "$1" != "-" ] && while kill -0 "$1" 2>/dev/null; do sleep 20; done
shard=$2
Q=$(mktemp -d)/m6q.txt
if [ "${shard%%/*}" = 0 ]; then
  $PY $D/mvb_nobuffer.py --all --out $D/results/mvb_cell.jsonl
fi
# M6: every queued cell, day-long loop at R16, plant == model; re-read the queue each pass (M4 may still grow it)
for pass in 1 2 3 4 5 6; do
  $PY $D/m6_queue.py > $Q
  $PY $D/mpc.py --days 1 --replan 16 --plant-error 1.0 --cells-file $Q --shard $shard --out $D/results/m6_loops.jsonl
  pgrep -f "race.py --cells-file" >/dev/null || [ $pass -ge 2 ] && ! pgrep -f "race.py --cells-file" >/dev/null && break
  sleep 300
done
