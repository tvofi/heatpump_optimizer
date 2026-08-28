#!/usr/bin/env bash
#
# Re-record every test script's dependency closure and rewrite
# tests/closures.json.
#
#   ./tests/derive_closures.sh                 # everything, three lanes
#   ./tests/derive_closures.sh --out-dir D     # keep the raw records in D
#   ./tests/derive_closures.sh --record-only   # record, do not rewrite the file
#
# This runs the whole suite once, under instrumentation (see tests/closure.py):
# the closures are what the runs actually opened and imported, not what
# anybody thought they would. Expect it to take as long as a full gate.
#
# Two scripts are recorded with cheap arguments on purpose:
#
#   golden.py    --only __no_such_scenario__
#   env_drift.py --cache-key <ref> --all
#
# Both import their whole module graph either way, and both have their closure
# widened by rule to the ENTIRE integration plus every file in tests/golden/ --
# they compare behaviour between two checkouts, so no file-name argument can
# ever justify skipping them. Running their full comparison here would take an
# hour and teach the closure nothing it is not already given.
set -u
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/tests/hastub:${PYTHONPATH:-}"
PYTHON="${PYTHON:-python3}"
GOLDEN_REF="${GOLDEN_REF:-origin/main}"

OUTDIR=""
MERGE=1
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir) OUTDIR="$2"; shift 2 ;;
    # Record only, leave tests/closures.json alone. This is what the gate on
    # main uses: merging here would OVERWRITE the committed file with what
    # this run just measured, and the check that follows would then compare
    # the file against itself and pass no matter how stale it was.
    --record-only) MERGE=0; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ -z "$OUTDIR" ]; then
  OUTDIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-closure-XXXXXX")
  trap 'rm -rf "$OUTDIR"' EXIT
fi
mkdir -p "$OUTDIR"

rec() {
  local script="$1"; shift
  echo "  [$(date +%H:%M:%S)] record $script $*"
  $PYTHON tests/closure.py record "$script" --out-dir "$OUTDIR" --args "$@" \
    > "$OUTDIR/$(basename "$script").out" 2>&1
  echo "  [$(date +%H:%M:%S)] done   $script (exit $?)"
}

# Lane 1: the single longest script, alone.
( rec tests/stress.py ) &
p1=$!
# Lane 2: the SLOW closed-loop simulation.
( rec tests/rolling.py ) &
p2=$!
# Lane 3: everything else, in one sequence. plan_view.py writes the payload
# card.mjs reads, so that pair keeps its order here exactly as in run.sh.
(
  rec tests/features.py
  rec tests/entities.py
  rec tests/edge.py
  rec tests/validate.py
  rec tests/backtest.py
  rec tests/manual_plan.py
  rec tests/open_meteo.py
  rec tests/solar_alignment.py
  rec tests/optimality.py
  # features.py runs this one in a subprocess with HASTUB_TZ set, because the
  # stub's DEFAULT_TIME_ZONE is fixed at import. Recorded the same way: without
  # it the script fails, and a failed run records only what it reached.
  HASTUB_TZ=Europe/Stockholm rec tests/dst_checks.py
  rec tests/golden.py --only __no_such_scenario__
  rec tests/env_drift.py --cache-key "$GOLDEN_REF" --all
  rec tests/plan_view.py
  rec tests/frontend.py
  rec tests/card.mjs
) &
p3=$!
wait $p1 $p2 $p3

echo
if [ "$MERGE" -eq 1 ]; then
  $PYTHON tests/closure.py merge --in-dir "$OUTDIR"
else
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
fi
