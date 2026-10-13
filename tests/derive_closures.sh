#!/usr/bin/env bash
#
# Re-record every test script's dependency closure and rewrite
# tests/closures.json.
#
#   ./tests/derive_closures.sh                 # everything, lane-planned
#   ./tests/derive_closures.sh --out-dir D     # keep the raw records in D
#   ./tests/derive_closures.sh --record-only   # record, do not rewrite the file
#   ./tests/derive_closures.sh --single S      # record just S, merge it in
#   ./tests/derive_closures.sh --single S --record-only --out-dir D
#                                              # record just S into D, merge nothing
#   ./tests/derive_closures.sh --scripts-from F --record-only --out-dir D
#                                              # record the scripts listed in F
#                                              # across lanes, merge nothing
#
# This runs the whole suite once, under instrumentation (see tests/closure.py):
# the closures are what the runs actually opened and imported, not what
# anybody thought they would. Expect it to take as long as a full gate.
#
# --single exists because that cost is the friction (#90): ~25 minutes to
# record one new script is what made people skip it, and the scoped gate
# silently ran full on every PR until main's closures job failed. One
# script, one recording, one merge into tests/closures.json.
#
# --scripts-from exists because the scoped arm used to loop --single over
# the list one script at a time, paying the SUM of the selected recordings
# (51m18s over 24 scripts on #2071's closures job) where the full arm pays
# a lane MAX (27m57s the same day) for more work. The list is sharded by
# `closure.py lane-plan` -- the ordering constraints (plan_view.py ahead of
# the card scripts that read its payload, a driven child with its driver)
# are kept inside one lane, and the recordings are the same recordings the
# serial loop took: which lane records a script changes WHEN it is
# recorded, never WHAT it opens (R9-F10.15). The lane count is bounded by
# the owner's standing rule, three on CI and four on a seat box, overridable
# downward with $DERIVE_LANES.
#
# The full arm plans through the same lane planner (round-9 C1): with no
# --single and no --scripts-from it derives its recording set from the tree
# (`lane-plan --all-scripts` -- every runnable test script but the
# SLOW_GATED ones, `merge`'s own expectation set) and shards it the way the
# scoped arm's list is sharded. Before C1 the layout was hard-coded here --
# `stress` alone, `features+entities`, everything else serially in one
# 2,706 s lane -- and every new selectable script needed a lane edit on
# pain of a red main ("selectable script with NO recording"); derived, the
# recording set follows the tree and the wall is the balanced MAX. Which
# lane records a script is still only WHEN, never WHAT (R9-F10.15, and the
# pre-study's measured byte-identical read sets under concurrency).
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
SINGLE=""
SCRIPTS_FROM=""
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir) OUTDIR="$2"; shift 2 ;;
    # Record only, leave tests/closures.json alone. This is what the gate on
    # main uses: merging here would OVERWRITE the committed file with what
    # this run just measured, and the check that follows would then compare
    # the file against itself and pass no matter how stale it was.
    --record-only) MERGE=0; shift ;;
    --single) SINGLE="$2"; shift 2 ;;
    --scripts-from) SCRIPTS_FROM="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ -n "$SINGLE" ] && [ -n "$SCRIPTS_FROM" ]; then
  echo "--single and --scripts-from are two different runs" >&2
  exit 2
fi
# The FULL arm: no --single, no --scripts-from. The recording set is
# derived from the tree, not named here -- `--all-scripts` plans every
# runnable test script but the SLOW_GATED ones (`merge`'s own expectation
# set: the selectable scripts plus the driven children whose closure folds
# into their driver's) -- and sharded by the same planner the scoped arm's
# list takes. The roster comes back in the plan dir's scripts.txt and feeds
# the same loud missing-recording check the scoped list gets, so a planner
# or lane that drops a script still fails the derive; the merge at the end
# stays a FULL merge, because this roster covers every script it checks.
FULL_DIR=""
PARTIAL_ARG="--partial"
if [ -z "$SINGLE" ] && [ -z "$SCRIPTS_FROM" ]; then
  PARTIAL_ARG=""
  FULL_DIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-full-lanes-XXXXXX")
  $PYTHON tests/closure.py lane-plan --all-scripts --out-dir "$FULL_DIR" || {
    rm -rf "$FULL_DIR"; exit 2; }
  SCRIPTS_FROM="$FULL_DIR/scripts.txt"
fi
if [ -z "$OUTDIR" ]; then
  OUTDIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-closure-XXXXXX")
  trap 'rm -rf "$OUTDIR"' EXIT
fi
mkdir -p "$OUTDIR"

rec() {
  local script="$1"; shift
  # C1 (round-9 heavy-script consolidation): a script the closures job
  # already consumed from this run's composed recording (the coverage job's
  # traced execution of the same tree, verified by `closure.py
  # composed-verify`) is not re-recorded bare -- one instrumented execution
  # yields both artifacts. COMPOSED_CONSUMED is set by the workflow step that
  # verified the composed record; unset, or a script not on it, records as
  # before. Fail-closed: the consume step itself refuses on any doubt, so an
  # entry here means a verified record for THIS tree is already on disk.
  case " ${COMPOSED_CONSUMED:-} " in
    *" $script "*)
      echo "  [$(date +%H:%M:%S)] composed: $script consumed from this run's coverage job; no bare re-record"
      return 0
      ;;
  esac
  echo "  [$(date +%H:%M:%S)] record $script $*"
  $PYTHON tests/closure.py record "$script" --out-dir "$OUTDIR" --args "$@" \
    > "$OUTDIR/$(basename "$script").out" 2>&1
  # Captured on its own line: inside the echo below, $? would already be the
  # $(date) substitution's status, and every script read "exit 0" -- a stress.py
  # recording that exited 1 included, the one skip-failed-recording names.
  local rc=$?
  echo "  [$(date +%H:%M:%S)] done   $script (exit $rc)"
  REC_RC=$rc
  # CI-cost metrics (tests/ci_ratchet.py): one line per instrumented script
  # execution this re-derivation paid, classed full or scoped by the caller's
  # HPO_CI_SCOPE (the workflow sets it from the same case closure-scope
  # derived), carrying the runner's event and run id so a ratchet window can
  # group one run's lane artifacts together. No file, no line: a local run
  # emits nothing.
  if [ -n "${HPO_CI_METRICS:-}" ]; then
    printf 'closures\t%s\t%s\t%s\t0\t%s\t%s\n' "$script" \
      "${HPO_CI_SCOPE:-full}" "$rc" "${GITHUB_EVENT_NAME:-local}" \
      "${GITHUB_RUN_ID:-local}" >> "$HPO_CI_METRICS"
  fi
}

# One script with the cheap arguments and environment the full lanes record
# it with -- the same two differential guards, the calibration's --smoke and
# dst_checks.py's lane timezone, whichever path records it: --single and the
# --scripts-from lanes both come through here, so a scoped re-derivation
# takes the identical invocation the serial loop took.
rec_special() {
  case "$1" in
    tests/golden.py) rec "$1" --only __no_such_scenario__ ;;
    # The calibration builds every planted tree and measures none of them.
    tests/arch_score.py) rec "$1" --smoke ;;
    tests/env_drift.py) rec "$1" --cache-key "$GOLDEN_REF" --all ;;
    # Its lane's environment, below: the scoped `closures` job re-derives it
    # beside features.py, its driver (R9-F10.9).
    tests/dst_checks.py) HASTUB_TZ=Europe/Stockholm rec "$1" ;;
    *) rec "$1" ;;
  esac
}

if [ -n "$SINGLE" ]; then
  rec_special "$SINGLE"
  echo
  # --record-only applies here too. The scoped path of the `closures` job
  # records one script at a time into a shared out-dir and then CHECKS the
  # committed file against those records; merging first would overwrite the
  # committed closure with what this run just measured, and the check would
  # compare the file against itself -- the same trap the full path documents
  # above. Before this, --single ignored --record-only and always merged.
  if [ "$MERGE" -eq 1 ]; then
    $PYTHON tests/closure.py merge --in-dir "$OUTDIR" --partial
    exit $?
  fi
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
  exit 0
fi

if [ -n "$SCRIPTS_FROM" ]; then
  # The lane runner, both arms. `lane-plan` shards the list (balance over
  # the recorded seconds table, the ordering constraints kept inside one
  # lane) and writes one lane.<n> file per lane; each lane below is one
  # background shell recording its file's scripts in order, into the shared
  # OUTDIR. A lane that dies without recording everything it was handed is
  # LOUD below: the serial loop's one-derive-per-script process was
  # reddened by the step's own -e, and a dropped recording that exits
  # quietly would leave the check comparing nothing for that script.
  LANES_DIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-lanes-XXXXXX")
  $PYTHON tests/closure.py lane-plan \
    --scripts-from "$SCRIPTS_FROM" --out-dir "$LANES_DIR" || {
      rm -rf "$LANES_DIR"; [ -z "$FULL_DIR" ] || rm -rf "$FULL_DIR"; exit 2; }
  pids=""
  for lane in "$LANES_DIR"/lane.*; do
    [ -f "$lane" ] || continue
    (
      while IFS= read -r s; do
        [ -n "$s" ] || continue
        rec_special "$s"
      done < "$lane"
    ) &
    pids="$pids $!"
  done
  dead=0
  for p in $pids; do
    wait "$p" || { echo "a recording lane died (exit $?)" >&2; dead=1; }
  done
  rm -rf "$LANES_DIR"
  missing=""
  while IFS= read -r s; do
    [ -n "$s" ] || continue
    [ -f "$OUTDIR/$(basename "$s").json" ] || missing="$missing $s"
  done < "$SCRIPTS_FROM"
  if [ -n "$missing" ]; then
    echo "no recording this run for:$missing -- the lane runner will not" >&2
    echo "leave a script silently unrecorded" >&2
    rm -rf "$LANES_DIR" "$FULL_DIR"
    exit 1
  fi
  if [ "$dead" -ne 0 ]; then
    rm -rf "$LANES_DIR" "$FULL_DIR"
    exit 1
  fi
  echo
  # A merge here is partial for the scoped arm, exactly as --single's is:
  # only the scripts that arm listed were re-derived, so overlaying them is
  # the only honest merge. The full arm's roster covers every script the
  # check expects, so its merge is the full one -- the same merge the
  # hard-coded lanes ended with.
  if [ "$MERGE" -eq 1 ]; then
    $PYTHON tests/closure.py merge --in-dir "$OUTDIR" $PARTIAL_ARG
    exit $?
  fi
  [ -z "$FULL_DIR" ] || rm -rf "$FULL_DIR"
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
  exit 0
fi
# NOT REACHED: --single and --scripts-from above both exit; reaching this
# line means the full arm's guard failed to route. The full arm is the
# planner run in the SCRIPTS_FROM branch (round-9 C1); there is no
# hard-coded lane layout left to fall through to, and a silent fall-through
# would record nothing and let the job's check compare nothing.
echo "derive_closures: no arm routed; refusing to record nothing" >&2
exit 2
