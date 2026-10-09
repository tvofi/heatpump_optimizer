#!/bin/bash
# A13: the realistic composite -- one bot pin commit that BOTH adds a fresh row
# AND rewrites a row the branch's own diff already carried. `autofixCommit`
# accepts it (adds under the dir, modifies its files); `carry` must still refuse,
# because only the ADDED path is excluded.
set -uo pipefail
W=/Users/timmalmstrom/hpo-seats/review-2075/attack
MAINCOPY=/private/tmp/r9-main/tools/pr/app_approve.sh
FIXCOPY=/Users/timmalmstrom/hpo-seats/review-2075/wt/tools/pr/app_approve.sh
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
g() { git -C "$W/clone" -c user.name=rev -c user.email=rev@example.invalid "$@"; }
as_bot() { GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" \
           GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" g commit -q "$@"; }
V=$(g log --format=%H --grep='fix: own work' -1 fix)
echo "V = $V  origin/main = $(g rev-parse origin/main)"

g checkout -q --detach "$V"
mkdir -p "$W/clone/tests/mutation_ledger/killed_by"
printf '{"anchor":"fresh","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/fresh.json"
printf '{"anchor":"branchrow","killed_by":"tests/SOMETHING_ELSE.py","old":"o","reason":"bot rewrite of a reviewed row"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/branchrow.json"
g add -A; as_bot -m "ci: pin killed mutants"; H=$(g rev-parse HEAD)
echo "########## A13-adds-one-row-and-rewrites-a-reviewed-one  head=$H"
g diff --no-renames --name-status "$H^" "$H" | sed 's/^/    commit-diff /'
moout=$(cd "$W/clone" && bash "$MAINCOPY" --carry "$V" "$H" origin/main 2>&1); mo=$?
foout=$(cd "$W/clone" && bash "$FIXCOPY" --carry "$V" "$H" origin/main 2>&1); rc2=$?
echo "  [main-copy]  rc=$mo $moout"
echo "  [fixed-copy] rc=$rc2 $foout"
[ "$mo" = 0 ] && mv_=CARRY || mv_=REFUSE
[ "$rc2" = 0 ] && fv_=CARRY || fv_=REFUSE
echo "RESULT A13 expect=REFUSE main-copy=$mv_ fixed-copy=$fv_"
g checkout -q fix 2>/dev/null || true
