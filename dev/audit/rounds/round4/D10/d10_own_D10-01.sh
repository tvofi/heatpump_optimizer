#!/usr/bin/env bash
# D10-01 (seat 1 own harness) — config_flow.py coverage over the register row's
# OWN claimed script set.
#
# METRIC (own): the shipped quality_scale.yaml row config-flow-test-coverage
# claims "100% statement coverage (661 statements, 0 missed) over
# config_flow_steps, entities, golden, features and deployment_shape". This
# harness runs coverage over EXACTLY those five scripts (its own coveragerc,
# its own sitecustomize, its own combine --append) and reports
# statements / missed / percent for config_flow.py from that run alone.
# Any missed > 0 falsifies the row on the row's own terms.
#
# RUN (from the worktree root):
#   D10_OWN_WORK=$(mktemp -d /private/tmp/hpo-v-D10-own1cXXXX) \
#     tools/audit/round4/D10/d10_own_D10-01.sh
#   then feed $D10_OWN_WORK/out/coverage.json to d10_own_D10-01.py as
#   OWN5_JSON.
#
# EXPECTED (if the finding holds): config_flow.py missed > 0 (finder's
#   superset-of-20-scripts number: 21 missed; a five-script subset must be
#   >= that, by monotonicity of coverage).
# BASELINE 7dd68dd; run at branch head 0855277 (custom_components unchanged).
# MACHINE: 8-core Apple M1, macOS 25.6.0. Counts, not timings.
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the worktree root" >&2; exit 2; }
WORK="${D10_OWN_WORK:?set D10_OWN_WORK to a private mktemp -d}"
OUT="$WORK/out"
PY="${PYTHON:-/Library/Frameworks/Python.framework/Versions/3.11/bin/python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$OUT/logs" "$WORK/site" "$WORK/data"
export HPO_PLANDATA="$WORK/plandata.json"

cat > "$WORK/site/sitecustomize.py" <<'PYEOF'
try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()
PYEOF
cat > "$WORK/coveragerc" <<RCEOF
[run]
parallel = True
relative_files = True
data_file = $WORK/data/.coverage
source = $PWD/custom_components/heatpump_optimizer
[report]
precision = 1
RCEOF
export COVERAGE_PROCESS_START="$WORK/coveragerc"
export PYTHONPATH="$WORK/site:$PWD/tests/hastub"
"$PY" -c "import coverage" || { echo "coverage not importable" >&2; exit 2; }

printf 'script\texit\twall_s\n' > "$OUT/scripts.tsv"
for s in config_flow_steps entities golden features deployment_shape; do
  a=$(date +%s)
  if [ "$s" = "golden" ]; then
    # strict matches the tree instrument's choice for golden.py
    GOLDEN_MODE=strict "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
  else
    "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
  fi
  rc=$?; b=$(date +%s)
  printf '%s\t%s\t%s\n' "$s" "$rc" "$((b-a))" >> "$OUT/scripts.tsv"
  echo "ran tests/$s.py exit=$rc wall=$((b-a))s"
done

"$PY" -m coverage combine --rcfile="$WORK/coveragerc" --append --keep > "$OUT/logs/combine.log" 2>&1
unset COVERAGE_PROCESS_START
"$PY" -m coverage json --rcfile="$WORK/coveragerc" -o "$OUT/coverage.json" >> "$OUT/logs/combine.log" 2>&1
"$PY" -m coverage report --rcfile="$WORK/coveragerc" > "$OUT/coverage_report.txt" 2>&1
echo "wrote $OUT/coverage.json"
echo "RESULT load1=$(uptime | sed 's/.*load averages*: //' | awk '{print $1}')"
echo "RESULT thread_factor=n/a (counts, not timings)"
