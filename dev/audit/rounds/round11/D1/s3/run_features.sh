#!/usr/bin/env bash
# D1-s3 M5 second arm for tests/features.py: its keystone check exits the script early when an
# injection breaks it, so "finished" is not the end; re-run until a run fires nothing new.
# Usage (from the export root): bash dev/audit/rounds/round11/D1/s3/run_features.sh OUTDIR [script]
set -u
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=<HOME>/.local/state/hpo/venv-ci/bin/python3
D="$1"; S="${2:-tests/features.py}"; b=$(basename "$S" .py)
L=dev/audit/rounds/round11/D1/s3/local_inject.py
for k in $(seq 10 60); do
  "$P" "$L" --script "$S" --out "$D/$b.jsonl" --exclude-from "$D/$b.jsonl" ${EXTRA_EXCLUDE:-} > "$D/$b.$k.log" 2>&1
  st=$(grep '^STATUS' "$D/$b.$k.log" | head -1)
  n=$(grep '^RESULT fired=' "$D/$b.$k.log" | sed 's/RESULT fired=\([0-9]*\).*/\1/')
  echo "$S run $k: $st fired=${n:-?}" >> "$D/progress"
  [ "${n:-0}" = "0" ] && break
done
echo "$S LOOPDONE" >> "$D/progress"
