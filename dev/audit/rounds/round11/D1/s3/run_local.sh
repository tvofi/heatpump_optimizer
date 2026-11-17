#!/usr/bin/env bash
# D1-s3 M5 second arm: run local_inject.py over test scripts in three chains. A script an
# escaped injection aborts is re-run with every handler already recorded excluded, until it
# finishes or a run fires nothing new (at most 25 runs per script).
# Usage (from the export root): bash dev/audit/rounds/round11/D1/s3/run_local.sh OUTDIR [scripts...]
set -u
export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
P=<HOME>/.local/state/hpo/venv-ci/bin/python3
D="$1"; shift
mkdir -p "$D"
L=dev/audit/rounds/round11/D1/s3/local_inject.py
one() {
  s="$1"; b=$(basename "$s" .py)
  for k in $(seq 1 25); do
    "$P" "$L" --script "$s" --out "$D/$b.jsonl" --exclude-from "$D/$b.jsonl" > "$D/$b.$k.log" 2>&1
    st=$(grep '^STATUS' "$D/$b.$k.log" | head -1)
    n=$(grep '^RESULT fired=' "$D/$b.$k.log" | sed 's/RESULT fired=\([0-9]*\).*/\1/')
    echo "$s run $k: $st fired=${n:-?}" >> "$D/progress"
    case "$st" in "STATUS finished"*) break;; esac
    [ "${n:-0}" = "0" ] && break
  done
}
chain() { for s in "$@"; do one "$s"; done; }
if [ "$#" -gt 0 ]; then chain "$@"; echo ALLDONE >> "$D/progress"; exit 0; fi
chain tests/features.py &
chain tests/entities.py tests/open_meteo.py tests/manual_plan.py &
chain tests/config_flow_steps.py tests/debug_collect.py tests/finite_boundary.py tests/guard_pins.py tests/replay.py tests/dst_checks.py tests/block_duty.py &
wait
echo ALLDONE >> "$D/progress"
