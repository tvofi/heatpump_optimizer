#!/usr/bin/env bash
# Round-2 reviewer plants on a throwaway clone of the round-2 head.
set -u
SRC=/Users/timmalmstrom/hpo-seats/review-2030-r2/wt
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
git clone -q --shared "$SRC" "$D/r" && cd "$D/r" || exit 9
G="git -c user.name=r -c user.email=r@x -c commit.gpgsign=false"
P() { PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main; echo "rc=$?"; }
$G checkout -q --detach
echo "# planted on main" > tests/zz_main_unrecorded_check.py
$G add -A && $G commit -qm "main carries NO RECORDING"
git update-ref refs/remotes/origin/main HEAD
MAIN=$(git rev-parse HEAD)
echo "--- A. round-1 plant: branch only comments tests/wood_advisor.py, main carries the red"
$G checkout -q -b a $MAIN && echo "# a comment" >> tests/wood_advisor.py && $G commit -qam a && P
echo "--- B. branch only comments tests/derive_closures.sh, main carries the red"
$G checkout -q -b b $MAIN && echo "# a comment" >> tests/derive_closures.sh && $G commit -qam b && P
echo "--- C. control: the branch's own new unrecorded script still fires"
$G checkout -q -b c $MAIN && echo "# own" > tests/zz_own_check.py && $G add -A && $G commit -qm c && P
echo "--- D. mutation arm: a guard added, rc must be 0 (warn)"
$G checkout -q -b d $MAIN && printf '\n\ndef _zz(x):\n    if x > 3:\n        return 1\n    return 0\n' >> custom_components/heatpump_optimizer/away.py && $G commit -qam d && P | tee "$D/d.out"
sed -nE 's/^PREDICT mutation +ADDED UNPINNED ([^ ]+ [A-Z_]+): .*/\1/p' "$D/d.out" > "$D/sites"
echo "site keys:"; cat "$D/sites"
# step 7d's function, extracted verbatim from prepr.sh
eval "$(sed -n '/^unpinned_line() {/,/^}/p' tools/pr/prepr.sh)"
B() { printf 'Why.\n\n## Head\n\nx\n%s' "$1" > "$D/body.md"; unpinned_line "$D/body.md" "$D/sites"; echo "rc=$?"; }
all=$(sed 's/^/- /; s/$/: pinned by mutation-autofix/' "$D/sites")
echo "--- E1. section lists all keys"; B "$(printf '\n## Unpinned sites\n\n%s\n' "$all")"
echo "--- E2. heading with a count suffix"; B "$(printf '\n## Unpinned sites (3)\n\n%s\n' "$all")"
echo "--- E3. lower-case heading"; B "$(printf '\n## Unpinned Sites\n\n%s\n' "$all")"
echo "--- E4. keys in backticks"; B "$(printf '\n## Unpinned sites\n\n%s\n' "$(sed 's/^/- `/; s/$/`: pinned/' "$D/sites")")"
echo "--- E5. a 1-line shift after the body was written (merge from main above the site)"
$G checkout -q d && sed -i '' '1s/^/# shifted\n/' custom_components/heatpump_optimizer/away.py && $G commit -qam shift && P | tail -1
P | sed -nE 's/^PREDICT mutation +ADDED UNPINNED ([^ ]+ [A-Z_]+): .*/\1/p' > "$D/sites"
B "$(printf '\n## Unpinned sites\n\n%s\n' "$all")"
echo "--- E6. prefix collision: key for line 1 vs body naming line 10..19 only (substring?)"
printf 'custom_components/heatpump_optimizer/away.py:1 CONST\n' > "$D/sites"
B "$(printf '\n## Unpinned sites\n\n- custom_components/heatpump_optimizer/away.py:12 CONST: x\n')"
printf 'custom_components/heatpump_optimizer/away.py:12 CONST\n' > "$D/sites"
B "$(printf '\n## Unpinned sites\n\n- custom_components/heatpump_optimizer/away.py:12 CONST_X: x\n')"
