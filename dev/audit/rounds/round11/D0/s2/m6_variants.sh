#!/usr/bin/env bash
# D0-s2 M6 variants (orchestration, not a harness): the carried C3/C5 runs on results/m6_variant_cells.txt
# (the four high-bill cells whose day-long R16 loop realised a positive gap) and the loop's flat null.
# Usage: bash dev/audit/rounds/round11/D0/s2/m6_variants.sh <worker 0|1>
D=dev/audit/rounds/round11/D0/s2; PY=$HOME/venv-ci/bin/python3; export PYTHONPATH=tests/hastub
if [ "$1" = 0 ]; then
  $PY $D/mpc.py --days 2 --replan 16 --plant-error 1.0 --cells-file $D/results/m6_variant_cells.txt --out $D/results/m6_multiday.jsonl
  $PY $D/mpc.py --days 1 --replan 16 --plant-error 1.0 --cells-file $D/results/m6_flat_cells.txt --out $D/results/m6_flatnull.jsonl
else
  $PY $D/mpc.py --days 1 --replan 16 --plant-error 1.25 --cells-file $D/results/m6_variant_cells.txt --out $D/results/m6_plant125.jsonl
fi
