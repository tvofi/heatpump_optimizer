#!/bin/bash
# The decisive null control for attack A5c: the SAME merge of main (which shifts
# the branch's own ledger-hunk CONTEXT, the #2010 class), with a pin commit on
# top whose added file has an ORDINARY name. If that refuses and the glob-named
# one carries, the pathspec metacharacter -- and nothing else -- is the cause.
# Also: does `:(exclude,literal)` restore the refusal? (the one-token remedy)
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence2
W=/Users/timmalmstrom/hpo-seats/review-2075/attack2
MAINCOPY=/Users/timmalmstrom/hpo-seats/review-2075/main2/tools/pr/app_approve.sh
FIXCOPY=/Users/timmalmstrom/hpo-seats/review-2075/wt2/tools/pr/app_approve.sh
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
g() { git -C "$W/clone" -c user.name=rev -c user.email=rev@example.invalid "$@"; }
as_bot() { GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" \
           GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" \
           g commit -q "$@"; }
V=$(g rev-parse fix~0 2>/dev/null); V=$(g log --format=%H --grep='fix: own work' -1 fix)
echo "V = $V"; echo "origin/main = $(g rev-parse origin/main)"

# rebuild the merge of main on top of V
g checkout -q --detach "$V"
g merge -q --no-edit -m "Merge origin/main into fix" origin/main
HM=$(g rev-parse HEAD); echo "merge head = $HM"

# N1: an ORDINARY pin row on top of that merge -> must REFUSE (same as A5b)
g checkout -q --detach "$HM"
mkdir -p "$W/clone/tests/mutation_ledger/killed_by"
printf '{"anchor":"n1","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/n1.json"
g add -A; as_bot -m "ci: pin killed mutants"; HN1=$(g rev-parse HEAD)
# N2: a GLOB-named pin file on top of the same merge -> A5c
g checkout -q --detach "$HM"
printf '{"anchor":"n2","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' \
  > "$W/clone/tests/mutation_ledger/*"
g add -A; as_bot -m "ci: pin killed mutants"; HN2=$(g rev-parse HEAD)

for spec in "N1-ordinary-pin-over-same-merge $HN1" "N2-glob-pin-over-same-merge $HN2"; do
  set -- $spec; id=$1; h=$2
  echo "########## $id  head=$h"
  g diff --no-renames --name-status "$h^" "$h" | sed 's/^/    commit-diff /'
  moout=$(cd "$W/clone" && bash "$MAINCOPY" --carry "$V" "$h" origin/main 2>&1); mo=$?
  foout=$(cd "$W/clone" && bash "$FIXCOPY" --carry "$V" "$h" origin/main 2>&1); rc2=$?
  echo "  [main-copy]  rc=$mo $moout"
  echo "  [fixed-copy] rc=$rc2 $foout"
  [ "$mo" = 0 ] && mv_=CARRY || mv_=REFUSE
  [ "$rc2" = 0 ] && fv_=CARRY || fv_=REFUSE
  echo "RESULT $id main-copy=$mv_ fixed-copy=$fv_"
done

echo
echo "=== the two heads differ ONLY in the added file's NAME ==="
echo "  N1 tree: $(g rev-parse "$HN1^{tree}")"
echo "  N2 tree: $(g rev-parse "$HN2^{tree}")"
g diff --no-renames --name-status "$HN1" "$HN2" | sed 's/^/    /'

echo
echo "=== remedy probe: is ':(exclude,literal)<path>' valid, and does it keep the"
echo "    deep paths visible while still excluding the one added file? ==="
g checkout -q --detach "$HN2"
printf 'probe\n' >> "$W/clone/tests/mutation_ledger/ctx.json"
g commit -qam "probe: a deep ledger edit" 2>/dev/null
HP=$(g rev-parse HEAD)
echo "  plain   :(exclude)tests/mutation_ledger/*  -> visible: [$(g diff --no-renames --name-only "$HN2" "$HP" -- . ':(exclude)tests/mutation_ledger/*' | tr '\n' ' ')]"
echo "  literal :(exclude,literal)tests/mutation_ledger/* -> visible: [$(g diff --no-renames --name-only "$HN2" "$HP" -- . ':(exclude,literal)tests/mutation_ledger/*' | tr '\n' ' ')]"
echo "  (the file literally named '*' exists in this tree: $(g ls-tree -r --name-only "$HN2" -- tests/mutation_ledger | tr '\n' ' '))"
g checkout -q fix 2>/dev/null || true
