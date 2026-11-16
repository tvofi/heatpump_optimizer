#!/bin/bash
# R11-PRE-RELAY-REBUILD carry 5 (RELAY-NOBODY-OWED): one copy's noreturn_arm, replayed
# against the live origin's dispatch/fixer-*, handoff/, handoff-wip/ and handoff-body/ refs.
#   bash dev/audit/harnesses/r11_relay_nobody_replay.sh [<cloud_relay.sh>]
# The arm alone, extracted from the named copy (default this tree's), with a scratch state
# dir and log; HERE is that copy's directory, so its topic_grammar.py reads the family refs.
# The reviewer branch's PR-head read is /bin/false, so no gh call is made and no reviewer
# line prints. Pushes nothing. Prints each fixer line, then:
#   RESULT no_body=<SEAT NO BODY lines> no_return_fixer=<fixer SEAT ENDED NO RETURN lines>
# The refs move, so the counts are a reading at the moment it runs, never a header value.
# The base copy (before the carry) prints no_body=0 on any refs: it has no such line.
set -uo pipefail
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
f=${1:-tools/audit/seat/cloud_relay.sh}; [ -f "$f" ] || { echo "no $f" >&2; exit 2; }
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
export HPO_STATE_DIR=$d LOG=$d/r.log HPO_RELAY_PRHEAD=/bin/false
HERE=$(cd "$(dirname -- "$f")" && pwd)
eval "$(sed -n '/^relay_log() {/p; /^level_line() {/p; /^level_set() {/,/^}/p; /^blocked_kinds() {/,/; }$/p; /^noreturn_arm() {/,/^}/p' "$f")"
out=$(noreturn_arm 2>&1)
printf '%s\n' "$out" | grep -E '^cloud_relay: SEAT (NO BODY|ENDED NO RETURN) ' | grep -v ' reviewer '
echo "RESULT no_body=$(grep -c '^cloud_relay: SEAT NO BODY ' <<< "$out") no_return_fixer=$(grep '^cloud_relay: SEAT ENDED NO RETURN ' <<< "$out" | grep -vc ' reviewer ')"
