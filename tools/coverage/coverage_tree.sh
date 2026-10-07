#!/usr/bin/env bash
# Whole-tree statement coverage of custom_components/heatpump_optimizer, over the
# default-gate Python scripts of tests/run.sh.
#
# This is the instrument for the #195 tranche partition (#505). It differs from
# dev/audit/waves/w5-g5-195-coverage/coverage_suite.sh, which narrows the script list
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
# and a third, for cost and not for double-counting (R9-F10.14):
#   arch_score, arch_score_head -- they parse custom_components as TEXT (AST,
#                 from git for the first, from the tree for the second) and
#                 import none of it, so they execute no package line and add
#                 nothing to this measurement. They cost the most here: the
#                 pure-Python AST walk is the tracer's worst case, 23.8 min
#                 median of a 45-50 min job traced against 9.4 min bare in
#                 `fast`, where run.sh still runs them. coverage.json is
#                 byte-identical with and without them (the proof is in the
#                 pull request body). A future script of that kind that does
#                 import the package must NOT be added here.
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
#
# PER-SCRIPT DATA, AND REUSING IT (R9-F10.9b, #1812). Each script's processes
# write under their own data directory and are combined into
# $OUT/per/.coverage.<name> (or $OUT/per/<name>.nodata, for a script that
# executed no package line) before the final combine, which reads $OUT/per/:
# a union of line sets, so the per-script detour measures what one combine
# over every raw file did. The push to main keeps $OUT/per/ as the next pull
# request's base. With W5P_SCOPE (the gate's scope.json for the diff) and
# W5P_REUSE (that base's per/ directory) both set, a script the plan skips
# and the base measured is not re-run: its base file is copied into per/.
# `tests/closure.py coverage-split` decides, and `closure.py selftest` pins
# it. Either variable unset measures every script, as before.
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the worktree root" >&2; exit 2; }
STAGE="${1:-all}"
PY="${PYTHON:-python3}"
WORK="${W5P_WORK:?set W5P_WORK to a private mktemp -d}"
OUT="${W5P_OUT:-$WORK/out}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$OUT/logs" "$OUT/per" "$WORK/site" "$WORK/data"
export HPO_PLANDATA="$WORK/plandata.json"

DERIVED=$(grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh \
          | sed 's#.*tests/##;s#\.py##' | awk '!seen[$0]++' \
          | grep -vxE "arch_score|arch_score_head")
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

# Decided BEFORE COVERAGE_PROCESS_START is exported, so the decision itself
# is not traced. A split that fails measures every script.
if [ -n "${W5P_SCOPE:-}" ] && [ -n "${W5P_REUSE:-}" ]; then
  PLAN=$(echo "$SCRIPTS" | env -u COVERAGE_PROCESS_START PYTHONPATH="$PWD/tests/hastub" \
           "$PY" tests/closure.py coverage-split --plan "$W5P_SCOPE" --reuse-dir "$W5P_REUSE") \
    || PLAN=""
fi
[ -n "${PLAN:-}" ] || PLAN=$(echo "$SCRIPTS" | sed 's/^/measure\t/')

# One lane: measure the plan lines it is given, in order. A script's processes
# write under their own data directory and combine into their own per/ file, and
# the appends to scripts.tsv and combine.log are single lines, so two lanes share
# no file they write -- which is what lets the lanes below run side by side.
measure() {
  while IFS=$'\t' read -r verb s; do
    [ -n "$s" ] || continue
    rm -f "$OUT/per/.coverage.$s" "$OUT/per/$s.nodata"
    if [ "$verb" = "reuse" ]; then
      for f in ".coverage.$s" "$s.nodata"; do
        [ -f "$W5P_REUSE/$f" ] && cp "$W5P_REUSE/$f" "$OUT/per/$f"
      done
      printf '%s\treused\t0\n' "$s" >> "$OUT/scripts.tsv"
      echo "reused tests/$s.py's coverage from the base: no changed file is in its closure"
      continue
    fi
    sed "s#^data_file = .*#data_file = $WORK/data/$s/.coverage#" "$WORK/coveragerc" > "$WORK/coveragerc.$s"
    mkdir -p "$WORK/data/$s"
    a=$(date +%s)
    if [ "$s" = "golden" ]; then
      COVERAGE_PROCESS_START="$WORK/coveragerc.$s" GOLDEN_MODE=strict "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
    else
      COVERAGE_PROCESS_START="$WORK/coveragerc.$s" "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
    fi
    rc=$?; b=$(date +%s)
    printf '%s\t%s\t%s\n' "$s" "$rc" "$((b-a))" >> "$OUT/scripts.tsv"
    echo "ran tests/$s.py exit=$rc wall=$((b-a))s"
    if ls "$WORK/data/$s"/.coverage.* > /dev/null 2>&1; then
      COVERAGE_PROCESS_START= "$PY" -m coverage combine --rcfile="$WORK/coveragerc.$s" \
        >> "$OUT/logs/combine.log" 2>&1 \
        && mv "$WORK/data/$s/.coverage" "$OUT/per/.coverage.$s" \
        || { echo "could not combine tests/$s.py's data; see $OUT/logs/combine.log" >&2; return 1; }
    else
      : > "$OUT/per/$s.nodata"
    fi
  done <<< "$1"
}

# TWO LANES (R9-F10.15). tests/features.py is the longest script by a wide margin
# (822 s traced in the CI sweep of 2026-10-03, against about 570 s for every other
# script of the stage together); run beside each other the stage costs the longer
# lane and not the sum. The lanes only decide WHEN a script runs: every script still runs
# with the same arguments under its own coveragerc, and the final combine below
# reads the same per/ directory whichever order its files were written in, so
# coverage.json is the union it was serially. W5P_LANES=1 is that serial run, kept
# as the reference the byte-identity proof compares against.
# plan_view.py writes the payload doc_claims.py reads (HPO_PLANDATA, one file for
# the stage), so those two stay in one lane in plan order; features.py does not use
# it, and goes alone.
[ -f "$OUT/scripts.tsv" ] || printf 'script\texit\twall_s\n' > "$OUT/scripts.tsv"
case "${W5P_LANES:-2}" in
  1) measure "$PLAN" || exit 1 ;;
  2)
    FEAT=$(echo "$PLAN" | awk -F'\t' '$2=="features"')
    REST=$(echo "$PLAN" | awk -F'\t' '$2!="features"')
    measure "$FEAT" & lane_a=$!
    measure "$REST" & lane_b=$!
    rc=0
    wait "$lane_a" || rc=1
    wait "$lane_b" || rc=1
    [ "$rc" -eq 0 ] || exit 1
    ;;
  *) echo "W5P_LANES must be 1 or 2" >&2; exit 2 ;;
esac

"$PY" -m coverage combine --rcfile="$WORK/coveragerc" --append --keep "$OUT/per" >> "$OUT/logs/combine.log" 2>&1
unset COVERAGE_PROCESS_START
"$PY" -m coverage json --rcfile="$WORK/coveragerc" -o "$OUT/coverage.json" >> "$OUT/logs/combine.log" 2>&1
"$PY" -m coverage report --rcfile="$WORK/coveragerc" > "$OUT/coverage_report.txt" 2>&1
echo "wrote $OUT/coverage.json"
