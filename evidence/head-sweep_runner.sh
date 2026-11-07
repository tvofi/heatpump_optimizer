#!/bin/bash
# The sweep's mechanical steps as one loop (tvofi 2026-10-31: mechanical seat work goes into the sweep
# script). Runs the actionable-line steps of tools/audit/seat/sweep_template.md and writes ONLY actionable
# lines to $SWEEP_STATE_DIR/sweep-runner/new.txt (+ new.stamp), which the orchestrator's one wake reads.
#
#   SWEEP_STATE_DIR=<dir> SWEEP_CHECKOUT=<checkout> SWEEP_REPO=<owner/name> bash tools/audit/seat/sweep_runner.sh
#
# Required: SWEEP_STATE_DIR (the orchestrator state dir; exported as HPO_STATE_DIR), SWEEP_CHECKOUT (a
# checkout fetched fresh by the session; NEVER the one tick_loop.sh / cloud_relay.sh run from: bash reads
# scripts incrementally), SWEEP_REPO. Optional: SWEEP_ONCE=1 (one pass, no sleep), SWEEP_SLEEP (900 s),
# SWEEP_FIRED_LEDGER (the fire ledger, `<UTC stamp> FIRED ...` lines), SWEEP_ROSTER_QUEUE (+ SWEEP_ROSTER_EDIT,
# SWEEP_ROSTER_WT, SWEEP_ROSTER_LINT: the manual roster-drain path), SWEEP_TRAIN_GLOB (merge-train logs),
# SWEEP_ROSTER_REF (default handoff/audit-r10-roster), SWEEP_DISK_FLOOR_GIB (15), SWEEP_PLAN_SLOTS (16),
# SWEEP_PLAN_SEATS (16), SWEEP_PY (python3). Every state file lives under SWEEP_STATE_DIR.
set -u
if [ "${1:-}" = "--self-test" ]; then exec "${SWEEP_PY:-python3}" -I "$(dirname "$0")/sweep_runner_selftest.py" --self-test; fi
: "${SWEEP_STATE_DIR:?SWEEP_STATE_DIR is required}" "${SWEEP_CHECKOUT:?SWEEP_CHECKOUT is required}" "${SWEEP_REPO:?SWEEP_REPO is required}"
O=$SWEEP_STATE_DIR; W=$SWEEP_CHECKOUT; REPO=$SWEEP_REPO; PY=${SWEEP_PY:-python3}
R=$O/sweep-runner; G=$O/gantt; mkdir -p "$R" "$G"
REF=${SWEEP_ROSTER_REF:-handoff/audit-r10-roster}; LEDGER=${SWEEP_FIRED_LEDGER:-}
export PATH=$W/tools/audit/seat/shims:$PATH HPO_STATE_DIR=$O
n=0
emit(){ printf '%s\n' "$@" >> "$R/new.tmp"; }
while :; do
  n=$((n+1)); : > "$R/new.tmp"; cd "$W" || exit 1
  # roster queue drain (the manual path; the beat's roster-drain row is the unattended one): refusals and unrun lines only
  if [ -n "${SWEEP_ROSTER_QUEUE:-}" ]; then
    timeout 3700 $PY -I tools/audit/seat/roster_drain.py --queue "$SWEEP_ROSTER_QUEUE" --work-dir "$R" \
      --edit-checkout "${SWEEP_ROSTER_EDIT:?}" --worktree "${SWEEP_ROSTER_WT:?}" --lint-clone "${SWEEP_ROSTER_LINT:?}" --branch "$REF" >> "$R/new.tmp" 2>&1
  fi
  # (1b) pulse: STOPPED / UNREADABLE only
  timeout 200 $PY -I tools/audit/seat/pulse.py --repo "$REPO" > "$R/pulse.txt" 2>&1
  grep -E 'STOPPED|UNREADABLE' "$R/pulse.txt" | sed 's/^/PULSE: /' >> "$R/new.tmp"
  # (4e) cancel superseded runs; report only if it cancelled something or failed
  timeout 200 $PY -I tools/pr/cancel_superseded.py sweep --repo "$REPO" > "$R/cancel.txt" 2>&1 || emit "CANCEL-SWEEP failed: $(tail -1 "$R/cancel.txt")"
  grep -q 'cancelled [1-9]' "$R/cancel.txt" && grep 'CANCEL-SWEEP' "$R/cancel.txt" >> "$R/new.tmp"
  # (8) disk floor
  free=$(df -Pk / | awk 'NR==2{print int($4/1048576)}'); floor=${SWEEP_DISK_FLOOR_GIB:-15}
  [ "${free:-99}" -lt "$floor" ] && { emit "DISK: ${free} GiB free (<$floor); running worktree_gc"; bash tools/audit/worktree_gc.sh "$REPO" > "$R/gc.txt" 2>&1; }
  # every 2nd pass (~30 min): (4b) plan render, gantt drift, verdict audit, state docs, owed_unactioned
  if [ $((n % 2)) -eq 1 ]; then
    git fetch -q origin "$REF" 2>/dev/null
    timeout 300 $PY tools/plan/replan.py --out "$O/plan-live.json" --slots "${SWEEP_PLAN_SLOTS:-16}" --seats "${SWEEP_PLAN_SEATS:-16}" > "$R/replan.txt" 2>&1 || emit "REPLAN failed: $(tail -1 "$R/replan.txt")"
    timeout 150 $PY tools/audit/seat/plan_page.py --plan "$O/plan-live.json" --html "$O/plan-live.html" > "$R/plan_page.txt" 2>&1 || emit "PLAN-PAGE failed: $(tail -1 "$R/plan_page.txt")"
    grep -q "refused" "$R/plan_page.txt" && emit "PLAN-PAGE refused: $(grep -m1 refused "$R/plan_page.txt" | cut -c1-200)"
    # tvofi 2026-11-06: every sweep updates the plan artifact; a re-render that differs from the published page owes a republish
    cmp -s "$O/plan-live.html" "$O/plan.html" || { cp "$O/plan-live.html" "$O/plan.html" && emit "PLAN MOVED: plan.html re-rendered; republish owed"; }
    # tvofi 2026-11-01: each plan render is compared against the Gantt baseline; every unacked slip is owed act|defer|accept
    git show "origin/$REF:dev/programme/rosters/wave-r10-groups.json" > "$G/roster.json" 2>/dev/null
    # a handoff already in main is not work in flight; sweep_gantt.py keeps only tips committed in the last 12 h,
    # and only fire lines from the last 12 h (both filters are its own, so this runner holds no second copy)
    git fetch -q origin '+refs/heads/handoff/*:refs/gantt/handoff/*' '+refs/heads/handoff-wip/*:refs/gantt/handoff-wip/*' 2>/dev/null
    git for-each-ref --format='%(objectname)%09%(refname)%09%(committerdate:unix)' refs/gantt/ | sed 's#\trefs/gantt/#\trefs/heads/#' > "$G/handoff-rows.tsv"
    [ -n "$LEDGER" ] && [ -f "$LEDGER" ] && cp "$LEDGER" "$G/fired.txt" || : > "$G/fired.txt"
    gh pr list --repo "$REPO" --state open --limit 100 --json number,title > "$G/prs.json" 2>/dev/null || echo '[]' > "$G/prs.json"
    timeout 120 $PY -I tools/audit/seat/sweep_gantt.py --plan "$O/plan-live.json" --baseline "$G/baseline.json" --acks "$G/acks.txt" \
      --roster "$G/roster.json" --open-prs "$G/prs.json" --handoff-rows "$G/handoff-rows.tsv" --fired "$G/fired.txt" > "$R/gantt.txt" 2>&1 || emit "GANTT-DRIFT failed: $(tail -1 "$R/gantt.txt")"
    grep -E '^GANTT-(SLIP|BASELINE)' "$R/gantt.txt" | sed 's/^/GANTT: /' >> "$R/new.tmp"
    # tvofi 2026-11-06: no PR waits unheld; every open PR is mapped to its verdict and holder
    timeout 300 $PY -I tools/audit/seat/verdict_audit.py --repo "$REPO" --fired "$G/fired.txt" --train-glob "${SWEEP_TRAIN_GLOB:-}" --skip "$G/unheld-skip.txt" > "$R/unheld.txt" 2>&1 || emit "VERDICT-AUDIT failed: $(tail -1 "$R/unheld.txt")"
    grep '^UNHELD' "$R/unheld.txt" >> "$R/new.tmp"
    timeout 900 $PY -u tools/audit/seat/state_docs.py --push --mirror "$O/state-mirror" --plan "$O/plan-live.json" > "$R/state.txt" 2>&1; src=$?
    [ $src -ne 0 ] && emit "STATE-DOCS rc=$src (124 = timeout): $(grep -i -E 'refus|unavail|error' "$R/state.txt" | tail -1)"
    grep -h '^summary:' "$R/replan.txt" > "$R/plan-summary.txt"
    $PY -I tools/audit/seat/owed_unactioned.py --tick "$O/tick.txt" --state "$O/owed-unactioned.json" --acks "$O/seat-ledger.md" > "$R/unact.txt" 2>&1; rc=$?
    [ $rc -eq 1 ] && grep -E '^\s+-> |^\s+ack:' "$R/unact.txt" | sed 's/^ */UNACTIONED: /' >> "$R/new.tmp"
    [ $rc -eq 2 ] && emit "UNACTIONED-UNREADABLE: $(tail -1 "$R/unact.txt")"
  fi
  if [ -s "$R/new.tmp" ]; then mv "$R/new.tmp" "$R/new.txt"; date -u +%FT%TZ > "$R/new.stamp"; else rm -f "$R/new.tmp"; fi
  echo "$(date -u +%FT%TZ) pass $n new=$( [ -f "$R/new.stamp" ] && cat "$R/new.stamp" || echo -) $(cut -c1-60 "$R/plan-summary.txt" 2>/dev/null)"
  [ -n "${SWEEP_ONCE:-}" ] && exit 0
  sleep "${SWEEP_SLEEP:-900}"
done
