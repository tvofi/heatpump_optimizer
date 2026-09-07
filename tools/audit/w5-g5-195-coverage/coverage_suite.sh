#!/usr/bin/env bash
# W5-G5 (#195 tranche 1) coverage harness for climate.py / open_meteo.py / frontend.py.
#
# Metric: statement coverage of custom_components/heatpump_optimizer/*.py over the
# default-gate Python scripts whose MEASURED closure (tests/closures.json) touches
# climate.py, open_meteo.py or frontend.py -- same methodology as the #195 judge
# comment (2026-09-03), narrowed to this tranche's three modules to avoid the
# ~20+ min of validate/edge/backtest/optimality/rolling/stress that closures.json
# shows never import these three files.
#
# SCRIPTS is derived from tests/run.sh, not retyped:
#   grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh
# then the judge's own documented, symmetric exclusions (env_drift is the
# GOLDEN_MODE=drift *alternative* to golden.py -- run.sh runs one or the other,
# never both; rolling is SLOW-gated; stress and validate/edge/backtest/optimality
# do not appear in tests/closures.json's entries for climate.py, open_meteo.py or
# frontend.py -- confirmed by:
#   python3 -c "import json; d=json.load(open('tests/closures.json'))['closures']; \
#     print([k for k,v in d.items() if any(m in f for f in v for m in \
#     ('climate.py','open_meteo.py','frontend.py'))])"
# which returns exactly the SCRIPTS list below plus card.mjs/card_drift.mjs (node,
# not measured by coverage.py here).
#
# Command (from the export root):
#   PYTHON=python3 D10_COV_PREFIX=/tmp/d10-cov \
#     tools/audit/w5-g5-195-coverage/coverage_suite.sh
set -u
if [ ! -f custom_components/heatpump_optimizer/manifest.json ]; then
  echo "run from the export root" >&2; exit 2
fi
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}" OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}" NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"

PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
fi
COVPREFIX="${D10_COV_PREFIX:-/tmp/d10-cov}"
OUT="${W5G5_COV_OUT:-$PWD/tools/audit/w5-g5-195-coverage/coverage}"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/w5g5-cov-XXXXXX")
mkdir -p "$OUT/logs" "$TMP/site" "$TMP/data"
export HPO_PLANDATA="$TMP/plandata.json"

cat > "$TMP/site/sitecustomize.py" <<'PYEOF'
try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()
PYEOF
cat > "$TMP/coveragerc" <<RCEOF
[run]
parallel = True
relative_files = True
data_file = $TMP/data/.coverage
source = $PWD/custom_components/heatpump_optimizer
[report]
precision = 1
RCEOF
export COVERAGE_PROCESS_START="$TMP/coveragerc"
export PYTHONPATH="$COVPREFIX:$TMP/site:$PWD/tests/hastub"

if ! "$PY" -c "import coverage" 2>/dev/null; then
  echo "coverage not importable from $COVPREFIX" >&2; exit 2
fi

SCRIPTS="features entities config_flow_steps structure manual_plan open_meteo solar_alignment deployment_shape golden plan_view frontend"

: > "$OUT/scripts.tsv"
echo -e "script\texit\twall_s" >> "$OUT/scripts.tsv"
t0=$(date +%s)
for s in $SCRIPTS; do
  a=$(date +%s)
  if [ "$s" = "golden" ]; then
    # Strict mode: exact fixture comparison, ignored here -- coverage tracks
    # which lines ran regardless of whether the comparison passes, and drift
    # mode is not comparable to the judge's baseline run.
    GOLDEN_MODE=strict "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
  else
    "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
  fi
  rc=$?
  b=$(date +%s)
  echo -e "$s\t$rc\t$((b-a))" >> "$OUT/scripts.tsv"
  echo "ran tests/$s.py exit=$rc wall=$((b-a))s"
done
t1=$(date +%s)

"$PY" -m coverage combine --rcfile="$TMP/coveragerc" --keep > "$OUT/logs/combine.log" 2>&1
unset COVERAGE_PROCESS_START
"$PY" -m coverage report --rcfile="$TMP/coveragerc" > "$OUT/coverage_report.txt" 2>&1
"$PY" -m coverage json --rcfile="$TMP/coveragerc" -o "$OUT/coverage.json" >> "$OUT/logs/combine.log" 2>&1

"$PY" - "$OUT" "$((t1-t0))" <<'PYEOF' | tee "$OUT/RESULTS.txt"
import json, os, sys
out, wall = sys.argv[1], int(sys.argv[2])
d = json.load(open(os.path.join(out, "coverage.json")))
files = {os.path.basename(k): v["summary"] for k, v in d["files"].items()}
tot = d["totals"]
print(f"RESULT coverage_total_pct={tot['percent_covered']:.1f} pct")
print(f"RESULT coverage_statements={tot['num_statements']} count")
print(f"RESULT coverage_missing={tot['missing_lines']} count")
for name in ("climate.py", "open_meteo.py", "frontend.py"):
    s = files.get(name)
    if s:
        print(f"RESULT coverage_{name.replace('.py','')}_pct={s['percent_covered']:.1f} pct "
              f"({name} {s['num_statements']} statements, {s['missing_lines']} missed)")
    else:
        print(f"RESULT coverage_{name.replace('.py','')}_pct=MISSING")
print(f"RESULT wall_s={wall} s")
PYEOF
