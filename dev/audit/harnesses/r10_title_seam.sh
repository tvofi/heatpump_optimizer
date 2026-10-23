#!/usr/bin/env bash
# R10-POLICY-LINT-FAMILY (dev/audit/rca/R10-RCA-RAISE-GATE-GRAMMAR.md, the
# title seam): does any merged pull-request title fail the preflight.sh run the
# merge train applies to the title alone (merge_train.py `land`, merge_pr.sh)?
# No pre-train path runs it on the title, so an instance would be a title the
# train refused; this counts the titles that would have been.
#
#   bash dev/audit/harnesses/r10_title_seam.sh [<range>]   (default v7.0.0..origin/main)
#
# The title is the merge commit's body (GitHub writes `Merge pull request #N
# from ...`, a blank line, then the title), so no API read. Each is piped to
# tools/pr/preflight.sh with no intended issue, the strictest reading: a title
# clean with none is clean with any. Metric:
#   BAD <merge> <title>                  -- a title preflight refuses or never calls clean
#   RESULT titles=<n> refused=<n>        -- over every first-parent merge with a body
#   CONTROL refused=<0|1>                -- `Closes #1` as a title, which must refuse
# Limit: a title the train refused and someone then edited merges clean and is
# not seen; train Stop lines are not in the tree.
set -uo pipefail
ROOT=$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel) || exit 2
RANGE=${1:-v7.0.0..origin/main}
refused() { # title -> 0 when preflight refuses it
  local out
  out=$(printf '%s\n' "$1" | bash "$ROOT/tools/pr/preflight.sh" 2>&1)
  grep -qE '^\s*REFUSE\b' <<<"$out" || ! grep -qE '^\s*clean\b' <<<"$out"
}
n=0 bad=0
while IFS=$'\t' read -r sha title; do
  n=$((n + 1))
  if refused "$title"; then bad=$((bad + 1)); echo "BAD ${sha:0:9} $title"; fi
done < <(git -C "$ROOT" log --first-parent --merges --format='%H%x09%b' "$RANGE" | awk -F'\t' 'NF > 1 && $2 != ""')
echo "RESULT titles=$n refused=$bad"
if refused 'fix: a title. Closes #1'; then echo "CONTROL refused=1"; else echo "CONTROL refused=0"; fi
