#!/usr/bin/env bash
#
# Re-record every test script's dependency closure and rewrite
# tests/closures.json.
#
#   ./tests/derive_closures.sh                 # everything, three lanes
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
  # The lane runner. `lane-plan` shards the list (balance over the recorded
  # seconds table, the ordering constraints kept inside one lane) and writes
  # one lane.<n> file per lane; each lane below is one background shell
  # recording its file's scripts in order, into the shared OUTDIR like the
  # full arm's lanes. A lane that dies without recording everything it was
  # handed is LOUD below: the serial loop's one-derive-per-script process
  # was reddened by the step's own -e, and a dropped recording that exits
  # quietly would leave the scoped check comparing nothing for that script.
  LANES_DIR=$(mktemp -d "${TMPDIR:-/tmp}/hpo-lanes-XXXXXX")
  $PYTHON tests/closure.py lane-plan \
    --scripts-from "$SCRIPTS_FROM" --out-dir "$LANES_DIR" || {
      rm -rf "$LANES_DIR"; exit 2; }
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
    echo "leave a scoped script silently unrecorded" >&2
    exit 1
  fi
  if [ "$dead" -ne 0 ]; then
    exit 1
  fi
  echo
  # A merge here is partial, exactly as --single's is: only the scripts this
  # run listed were re-derived, so overlaying them is the only honest merge.
  if [ "$MERGE" -eq 1 ]; then
    $PYTHON tests/closure.py merge --in-dir "$OUTDIR" --partial
    exit $?
  fi
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
  exit 0
fi

# Lane 1: the single longest script, alone.
( rec tests/stress.py ) &
p1=$!
# Lane 2 used to record tests/rolling.py. It no longer does: rolling is
# SLOW_GATED in tests/closure.py, so it is never selectable and its closure
# could not decide anything. Recording it cost 62 minutes under the audit
# hook -- more than every other script combined -- for an answer nothing
# reads. See the SLOW_GATED comment in tests/closure.py.
# Lane 2: features.py and entities.py, the two longest after stress. Neither
# reads anything a script of lane 3 writes (run.sh runs them beside the others
# for the same reason), and the recordings are one file per script under
# $OUTDIR, so which lane takes a script changes when it is recorded and not
# what it opens (R9-F10.15). Closures are measured as before; the proof is the
# `closures` job's UNDER-SCOPED check on this very lane layout.
(
  rec tests/features.py
  rec tests/entities.py
) &
p2=$!
# Lane 3: everything else, in one sequence. plan_view.py writes the payload
# card.mjs reads, so that pair keeps its order here exactly as in run.sh.
(
  # Block-switch mutants (R9-SW-5), in run.sh's lane order after entities.py.
  # A selectable script the lanes never recorded fails the closures job with
  # "NO recording this run" however complete the committed table is.
  rec tests/block_duty.py
  # #1413: the doc-claims-vs-code-facts detector. A selectable script the
  # lanes never recorded fails the closures job on main with "NO recording
  # this run" however complete the committed table is -- the same trap
  # config_flow_steps.py documents below.
  rec tests/doc_claims.py
  # #1674 (class N-markdown), in run.sh's lane order right after doc_claims.py:
  # a selectable script the lanes never recorded fails the closures job on
  # main with "NO recording this run" however complete the committed table is
  # -- the same trap doc_claims.py documents above.
  rec tests/md_tables.mjs
  rec tests/wood_advisor.py
  # The config-flow driver (#194), in lane order next to entities.py: a
  # selectable script the lanes never recorded reads as "no closure" and
  # fails the closures job on main (the card_drift.mjs trap above).
  rec tests/config_flow_steps.py
  # The structural ratchet (#193 PR-0): same lane-order position as in
  # run.sh. Reads the whole integration, so its closure is large on
  # purpose -- a change to any integration file must put it in scope.
  rec tests/structure.py
  # The architecture score's checks (R9-EG-A1), in run.sh's lane order. The
  # calibration is recorded with --smoke: it builds every planted tree without
  # measuring it, which reads every file the full run reads.
  rec tests/arch_score.py --smoke
  rec tests/arch_score_head.py
  # The typing ratchet's source-only half (#303), in run.sh's lane order next
  # to the structural ratchet. Same reason ha_contract.py is recorded here and
  # not only with --single: this job RE-DERIVES from these lanes, so a
  # selectable script the lanes never ran fails it with "NO recording this
  # run" however complete the committed table is. Its closure is the whole
  # integration on purpose -- it scans every module for type-ignore comments.
  rec tests/typing_ruler.py
  rec tests/edge.py
  rec tests/validate.py
  rec tests/backtest.py
  # #1935: in run.sh's lane order, right after backtest.py.
  rec tests/boost_drift_replay.py
  # What tests/hastub owes Home Assistant (#536), in run.sh's lane order. Its
  # closure is the whole stub on purpose: any change there must put this in
  # scope. Recorded HERE and not only with --single, because the closures job
  # re-derives from these lanes, and a selectable script the lanes never ran
  # fails it with "NO recording this run" however complete the committed table
  # is -- the same trap card_drift.mjs and config_flow_steps.py hit above.
  rec tests/ha_contract.py
  rec tests/manual_plan.py
  rec tests/open_meteo.py
  rec tests/solar_alignment.py
  rec tests/guard_pins.py
  # The debug collector's guards (#1939), in run.sh's lane order next to
  # guard_pins.py. Selectable, so a lane that never records it fails the
  # closures job with "NO recording this run" however complete the committed
  # table is -- the same trap finite_boundary.py documents below.
  rec tests/debug_collect.py
  # The finiteness sweep (#1408), in run.sh's lane order next to debug_collect.py.
  # Selectable -- not in NOT_A_TEST -- so a lane that never records it fails the
  # closures job on main with "selectable script with NO recording", the same
  # trap card_drift.mjs and config_flow_steps.py hit above. It derives the store
  # boundary set from the tree and drives a non-finite leaf through each real
  # loader, so its closure is the integration plus the stub, measured the same
  # way as any script here.
  rec tests/finite_boundary.py
  rec tests/harness_headers.py
  # R9-RO-1's layout barrier, in run.sh's lane order. run_always there, but a
  # script the lanes never recorded still fails the closures job on main with
  # "NO recording this run". It reads the index, not the worktree, so its
  # closure is the manifest and itself.
  rec tests/layout.py
  # The deployment-shape lane (#513), in run.sh's lane order. It copies the
  # tracked package into a temporary tree and drives it from a child
  # interpreter, so the audit hook sees the package files it reads plus the
  # git call that enumerates them; nothing here depends on that recording
  # being taken any particular way.
  rec tests/deployment_shape.py
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
  # The card's markup gate (v6.2.11, #143) is selectable -- it is not in
  # NOT_A_TEST -- but was never recorded here, so every `closures` job on
  # main since then failed with "selectable script with NO recording".
  # It reads the same payload card.mjs does and the comparison ref's card
  # via `git show`; GOLDEN_REF reaches it as an environment variable,
  # exactly as run.sh passes it.
  rec tests/card_drift.mjs
) &
p3=$!
wait $p1 $p2 $p3

echo
if [ "$MERGE" -eq 1 ]; then
  $PYTHON tests/closure.py merge --in-dir "$OUTDIR"
else
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
fi
