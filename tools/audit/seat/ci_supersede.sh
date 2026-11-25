#!/usr/bin/env bash
# The cancel-sweep on a beat (CI-6, P-R11-CI-SCOPED-RERUN): this tree's
# `tools/pr/cancel_superseded.py sweep`, once or every INTERVAL seconds.
#
#   tools/audit/seat/ci_supersede.sh [--dry-run]          one sweep (DRY=1 too)
#   tools/audit/seat/ci_supersede.sh --loop [SECONDS]     one sweep per SECONDS (300)
#   tools/audit/seat/ci_supersede.sh --self-test
#
# The sweep's rule is cancel_superseded.py's alone: an active pull_request or
# workflow_dispatch run at a head its PR no longer has, never a run on main, a
# push run, a run at the live head or one on a branch whose live head the bot
# authored. This file adds the clock: each pass prints one UTC stamp line and
# the sweep's own lines, and a sweep that fails is printed and the loop goes on.
# The loop ends at its next 10-second slice once $HPO_STATE_DIR/ci-supersede.STOP
# exists (no HPO_STATE_DIR: the loop refuses to start, so it can be stopped).
# CI_SUPERSEDE_PY replaces the program (the self-test's stub).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
REPO=tvofi/heatpump_optimizer

sweep() { # $1: --dry-run or empty
  echo "ci_supersede: $(date -u +%Y-%m-%dT%H:%M:%SZ) ${1:-LIVE}"
  ${CI_SUPERSEDE_PY:-python3 -I "$ROOT/tools/pr/cancel_superseded.py"} sweep --repo "$REPO" ${1:+"$1"} \
    || echo "ci_supersede: the sweep failed (rc $?); the next pass retries"
}

loop() { # $1: seconds between passes
  [ -n "${HPO_STATE_DIR:-}" ] || { echo "ci_supersede: --loop needs HPO_STATE_DIR (its STOP file lives there)"; return 2; }
  [[ "$1" =~ ^[1-9][0-9]*$ ]] || { echo "ci_supersede: --loop SECONDS must be a positive integer, got '$1'"; return 2; }
  local stop="$HPO_STATE_DIR/ci-supersede.STOP" i
  while [ ! -e "$stop" ]; do
    sweep ""
    i=0
    while [ "$i" -lt "$1" ] && [ ! -e "$stop" ]; do sleep "${CI_SUPERSEDE_SLICE:-10}"; i=$((i + 10)); done
  done
  echo "ci_supersede: stopped $(date -u +%Y-%m-%dT%H:%M:%SZ) ($stop)"
}

self_test() {
  local d n=0 f=0 out
  d=$(mktemp -d) || return 1
  trap 'rm -rf "$d"' RETURN
  printf '#!/bin/sh\necho "ARGS $*" >> "%s/calls"\n[ -e "%s/fail" ] && exit 3\nexit 0\n' "$d" "$d" > "$d/py"
  chmod +x "$d/py"
  chk() { n=$((n + 1)); if [ "$2" = "$3" ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1: got '$2', want '$3'"; fi; }
  export CI_SUPERSEDE_PY="$d/py" CI_SUPERSEDE_SLICE=0
  bash "$0" >/dev/null
  chk "one sweep runs the program's sweep arm on this repository" "$(cat "$d/calls")" "ARGS sweep --repo $REPO"
  : > "$d/calls"; bash "$0" --dry-run >/dev/null
  chk "--dry-run reaches the sweep as --dry-run" "$(cat "$d/calls")" "ARGS sweep --repo $REPO --dry-run"
  : > "$d/calls"; DRY=1 bash "$0" >/dev/null
  chk "DRY=1 is --dry-run" "$(cat "$d/calls")" "ARGS sweep --repo $REPO --dry-run"
  printf '#!/bin/sh\necho "PY $*" > "%s/py-calls"\n' "$d" > "$d/python3"; chmod +x "$d/python3"
  (unset CI_SUPERSEDE_PY; PATH="$d:$PATH" bash "$0" >/dev/null)
  chk "null: without the stub it runs this tree's cancel_superseded.py" "$(cat "$d/py-calls")" \
    "PY -I $ROOT/tools/pr/cancel_superseded.py sweep --repo $REPO"
  out=$(HPO_STATE_DIR= bash "$0" --loop 1); chk "--loop without HPO_STATE_DIR refuses (rc 2)" "$?" "2"
  : > "$d/calls"; touch "$d/fail"
  (sleep 1; touch "$d/ci-supersede.STOP") &
  out=$(HPO_STATE_DIR="$d" timeout 20 bash "$0" --loop 10 2>&1); wait
  chk "--loop goes on past a failed sweep and stops on the STOP file" \
    "$([ "$(grep -c '^ARGS sweep' "$d/calls")" -ge 2 ] && echo yes)$(grep -c 'sweep failed (rc 3)' <<< "$out" | sed 's/^[1-9][0-9]*$/+/')$(grep -c '^ci_supersede: stopped' <<< "$out")" "yes+1"
  echo "ci_supersede self-test: $n checks, $f failed"
  [ "$f" -eq 0 ]
}

case "${1:-}" in
  --self-test) self_test ;;
  --loop) loop "${2:-300}" ;;
  --dry-run) sweep --dry-run ;;
  "") if [ "${DRY:-}" = 1 ]; then sweep --dry-run; else sweep ""; fi ;;
  *) sed -n '5,7p' "$0"; exit 2 ;;
esac
