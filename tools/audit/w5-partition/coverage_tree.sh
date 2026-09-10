#!/usr/bin/env bash
# Whole-tree statement coverage of custom_components/heatpump_optimizer, over the
# default-gate Python scripts of tests/run.sh.
#
# This is the instrument for the #195 tranche partition (#505). It differs from
# tools/audit/w5-g5-195-coverage/coverage_suite.sh, which narrows the script list
# to the closures that touch one tranche's three modules: a partition is over the
# whole package, so it may not be measured against a script list chosen for part
# of it.
#
# The script list is DERIVED, never retyped:
#   grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh | sed 's#.*tests/##;s#\.py##'
# less two symmetric exclusions, both documented in tests/run.sh itself:
#   env_drift  -- the GOLDEN_MODE=drift alternative to golden.py; run.sh runs one
#                 or the other, never both, so including both double-counts
#   rolling    -- SLOW=1 only, so it is not in the default gate
#
# THE PATTERN ALSO DROPS ONE SCRIPT SILENTLY, named here so the next reader does
# not have to re-measure to learn it: tests/run.sh invokes
#   run_always "$PYTHON" tests/closure.py selftest
# and the substring `run "` does not occur in `run_always "`, so closure.py is in
# the default gate and not in DERIVED. Re-derive the dropped set with
#   grep -nE 'run_always "\$PYTHON" tests/' tests/run.sh
# which returns env_drift (already excluded above, symmetrically) and closure.
# Harmless here, measured rather than argued: run tests/closure.py selftest alone
# under this file's own coveragerc and `coverage report` shows every statement of
# custom_components/heatpump_optimizer still missed -- it covers none of them, so
# no module gains a covered line and the partition is unchanged by the drop. It
# is a gate-scoping selftest, not a package exercise, so widening the pattern to
# catch it would add a script and no coverage.
#
# WHAT THIS INSTRUMENT CANNOT MEASURE, established at both ends rather than argued:
# a timing check. tests/features.py passes every check at 44f914a when run bare, and
# reports two failures under this harness -- the #525 heartbeat pair, which reads ZERO
# ticks in BOTH arms, its own null control included, because the tracer removes the
# stall the check exists to see. The control is the same script at the same head with
# COVERAGE_PROCESS_START unset, which passes 2121 of 2121. So a failure of that pair
# in a coverage run is this instrument, not a regression: do not read it as one, and
# do not weaken the check to make a coverage run green. tests/golden.py is the same
# shape for a different reason and is deliberately run in strict mode -- coverage
# records which lines ran whatever the fixture comparison decides.
#
# Usage (from the worktree root):
#   W5P_WORK=$(mktemp -d) tools/audit/w5-partition/coverage_tree.sh [stage]
# Nothing is written inside the worktree: W5P_OUT defaults under W5P_WORK, so a
# measurement leaves no untracked evidence tree behind to go stale in the repo.
#     stage=fast   every default-gate script except the four end-to-end ones and stress
#     stage=e2e    validate edge backtest optimality
#     stage=stress tests/stress.py alone
#     stage=all    all three, in that order
# Stages accumulate into one coverage data set (parallel=True, combine --append
# --keep), so running fast then e2e is the same measurement as running all. The
# --append is load-bearing and was not there first: without it the second combine
# REPLACES the data file instead of merging into it, and the second stage
# silently reports its own scripts as the whole measurement -- a run that had
# climate.py at 100 pct came back at 0 pct with no error anywhere.
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the worktree root" >&2; exit 2; }
STAGE="${1:-all}"
PY="${PYTHON:-python3}"
WORK="${W5P_WORK:?set W5P_WORK to a private mktemp -d}"
OUT="${W5P_OUT:-$WORK/out}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$OUT/logs" "$WORK/site" "$WORK/data"
export HPO_PLANDATA="$WORK/plandata.json"

DERIVED=$(grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh \
          | sed 's#.*tests/##;s#\.py##' | awk '!seen[$0]++')
E2E="validate edge backtest optimality"
case "$STAGE" in
  fast)   SCRIPTS=$(echo "$DERIVED" | grep -vxE "env_drift|rolling|stress|validate|edge|backtest|optimality") ;;
  e2e)    SCRIPTS=$(echo "$DERIVED" | grep -vxE "env_drift|rolling|stress" | grep -xE "${E2E// /|}") ;;
  stress) SCRIPTS=$(echo "$DERIVED" | grep -xE "stress") ;;
  all)    SCRIPTS=$(echo "$DERIVED" | grep -vxE "env_drift|rolling") ;;
  *) echo "unknown stage $STAGE" >&2; exit 2 ;;
esac

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

[ -f "$OUT/scripts.tsv" ] || printf 'script\texit\twall_s\n' > "$OUT/scripts.tsv"
for s in $SCRIPTS; do
  a=$(date +%s)
  if [ "$s" = "golden" ]; then
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
