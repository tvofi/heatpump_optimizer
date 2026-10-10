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
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir) OUTDIR="$2"; shift 2 ;;
    # Record only, leave tests/closures.json alone. This is what the gate on
    # main uses: merging here would OVERWRITE the committed file with what
    # this run just measured, and the check that follows would then compare
    # the file against itself and pass no matter how stale it was.
    --record-only) MERGE=0; shift ;;
    --single) SINGLE="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ -n "$SINGLE" ]; then
  # One script, recorded and merged into the committed file. The two
  # cheap-argument special cases in the lanes below apply here too, for
  # the same reasons. Parsed here, executed after rec() exists.
  case "$SINGLE" in
    tests/golden.py) set -- "--only" "__no_such_scenario__" ;;
    # The calibration builds every planted tree and measures none of them.
    tests/arch_score.py) set -- "--smoke" ;;
    tests/env_drift.py) set -- "--cache-key" "$GOLDEN_REF" "--all" ;;
    # Its lane's environment, below: the scoped `closures` job re-derives it
    # beside features.py, its driver (R9-F10.9).
    tests/dst_checks.py) export HASTUB_TZ=Europe/Stockholm; set -- ;;
    *) set -- ;;
  esac
else
  set --
fi
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
  # Captured on its own line: inside the echo below, $? would already be the
  # $(date) substitution's status, and every script read "exit 0" -- a stress.py
  # recording that exited 1 included, the one skip-failed-recording names.
  local rc=$?
  echo "  [$(date +%H:%M:%S)] done   $script (exit $rc)"
}

if [ -n "$SINGLE" ]; then
  rec "$SINGLE" "$@"
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

# Lane layout (option (e) of the round-9 closures pre-study): the recorded
# seconds below are the committed tests/closures.json `recorded` table at
# 6be88834e8 (2026-10-10), quoted per lane. The old three-lane layout put
# boost_drift_replay.py (1489.6 s recorded; 29 m 26 s measured on job
# 114258919874, 55% of that push-to-main job's wall) in the middle of one
# 53-minute lane while lanes 1-2 sat idle after 15 and 21 minutes, so the
# job's wall was lane 3's serial sum, not any single recording. boost now
# has a lane of its own and is the floor; the rest of that lane keeps its
# order (1239.2 s recorded) beside it, and every other lane already finishes
# under the floor. Same recordings, same checks, same outputs -- only which
# background shell records what, and that a script's lane changes WHEN it is
# recorded, never WHAT it opens, is the established R9-F10.15 result the
# lane-2 comment below cites. The wall-clock acceptance (<= 35 min on the
# push-to-main closures job, two runs) is CI's own measurement: a full
# derive is Linux-only (gate-scoping.md).
#
# Lane 1: the longest of the ordinary scripts, alone (760.6 s).
( rec tests/stress.py ) &
p1=$!
# Lane 2 used to record tests/rolling.py. It no longer does: rolling is
# SLOW_GATED in tests/closure.py, so it is never selectable and its closure
# could not decide anything. Recording it cost 62 minutes under the audit
# hook -- more than every other script combined -- for an answer nothing
# reads. See the SLOW_GATED comment in tests/closure.py.
# Lane 2: features.py and entities.py, the two longest after stress (730.5 s
# and 259.6 s recorded). Neither reads anything a script of another lane
# writes (run.sh runs them beside the others for the same reason), and the
# recordings are one file per script under
# $OUTDIR, so which lane takes a script changes when it is recorded and not
# what it opens (R9-F10.15). Closures are measured as before; the proof is the
# `closures` job's UNDER-SCOPED check on this very lane layout.
(
  rec tests/features.py
  rec tests/entities.py
) &
p2=$!
# Lane 3: boost_drift_replay.py, ALONE (1489.6 s recorded, 24 m 50 s -- the
# single longest recording in the table and the wall-clock floor of the whole
# job). It used to sit mid-sequence in the old lane 3; #1935 put it in
# run.sh's lane order right after backtest.py, and backtest.py keeps that
# relative position as the first of its old neighbours below. Sharing a lane
# with it could only ever add to the floor, and giving it one costs the job
# nothing: three other lanes are recording meanwhile.
(
  rec tests/boost_drift_replay.py
) &
p3=$!
# Lane 4: everything else the old lane 3 held, in exactly its order
# (1239.2 s recorded, summed from the same table). plan_view.py writes the
# payload card.mjs reads, so that pair keeps its order here exactly as in
# run.sh -- and as it had it before the rebalance.
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
p4=$!
wait $p1 $p2 $p3 $p4

echo
if [ "$MERGE" -eq 1 ]; then
  $PYTHON tests/closure.py merge --in-dir "$OUTDIR"
else
  echo "recorded into $OUTDIR; tests/closures.json left untouched (--record-only)"
fi
