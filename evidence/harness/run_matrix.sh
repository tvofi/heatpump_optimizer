#!/bin/bash
# Reviewer-built runner for PR #2075 round 4.
# usage: run_matrix.sh <label> <app_approve.sh copy> <heads.env>
set -uo pipefail
LABEL=${1:?label}; SCRIPT=$(cd "$(dirname -- "$2")" && pwd)/$(basename -- "$2"); ENVF=$3
[ -f "$SCRIPT" ] || { echo "RESULT $LABEL FATAL: no such script $2"; exit 2; }
# shellcheck disable=SC1090
. "$ENVF"
ATTACKS="A2 A3 A9 DELREADD DELADD BUDGET OUTSIDE FORGE OKADD OKGLOB"
for a in $ATTACKS; do
  eval "h=\$$a"
  out=$(cd "$CLONE" && bash "$SCRIPT" --carry "$V" "$h" origin/main 2>&1)
  rc=$?
  # rc 0 = carry, 1 = a named refusal. Anything else is the harness itself
  # broken, and must not be recorded as a refusal (a silently dead arm).
  if [ "$rc" -gt 1 ]; then printf 'RESULT %-10s %-9s HARNESS-ERROR rc=%s :: %s\n' "$LABEL" "$a" "$rc" "$(printf '%s' "$out" | head -1)"; continue; fi
  if [ "$rc" -eq 0 ]; then verdict=CARRY; else verdict=REFUSE; fi
  printf 'RESULT %-10s %-9s %-6s rc=%s :: %s\n' "$LABEL" "$a" "$verdict" "$rc" "$(printf '%s' "$out" | sed 's/^CARRY: [a-z]* [0-9a-f]* -> [0-9a-f]*: //' | head -1)"
done
