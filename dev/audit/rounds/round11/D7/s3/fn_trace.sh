#!/usr/bin/env bash
# D7-s3 round 11: run one tests/ script under the function-entry sentinel.
#   bash dev/audit/rounds/round11/D7/s3/fn_trace.sh <outdir> tests/<script>.py [args...]
# Writes <outdir>/<script>.<pid>.json (entered production functions) and <outdir>/<script>.log.
# Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Run from the export root.
set -u
out=$1; shift
tag=$(basename "$1" .py)
mkdir -p "$out"
here=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-/Users/<owner-home>/.local/state/hpo/venv-ci/bin/python3}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
start=$(date +%s)
HPO_FN_TRACE="$out" HPO_FN_TRACE_TAG="$tag" HPO_PLANDATA="$out/plandata-$tag.json" \
  PYTHONPATH="$here/trace_site:tests/hastub" "$PY" "$@" > "$out/$tag.log" 2>&1
rc=$?
echo "$tag rc=$rc seconds=$(( $(date +%s) - start ))" >> "$out/_done.txt"
