#!/bin/bash
# Does main's CURRENT copy (#2059's landed bot-subject carry) hold the two
# boundaries PR #2075 says it protects -- a reviewed row rewritten, and a
# pathspec metacharacter in an added path? If main's copy also refuses both,
# #2075 adds nothing at current main; if it accepts either, #2075's narrowing
# has value and should be re-cut as a TIGHTENING of main's mechanism.
set -uo pipefail
W=/Users/timmalmstrom/hpo-seats/review-2075/attack
MAINNOW=/Users/timmalmstrom/hpo-seats/review-2075/mainnow/tools/pr/app_approve.sh
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
g() { git -C "$W/clone" -c user.name=rev -c user.email=rev@example.invalid "$@"; }
as_bot() { GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" \
           GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" g commit -q "$@"; }
V=$(g log --format=%H --grep='fix: own work' -1 fix)

probe() { # id head expect
  local id=$1 h=$2 expect=$3 out rc verdict
  out=$(cd "$W/clone" && bash "$MAINNOW" --carry "$V" "$h" origin/main 2>&1); rc=$?
  [ "$rc" = 0 ] && verdict=CARRY || verdict=REFUSE
  echo "  [$id] expect=$expect  main-now=$verdict  rc=$rc"
  printf '%s\n' "$out" | sed 's/^/      /'
  echo "RESULT main-now $id expect=$expect got=$verdict"
}

echo "V = $V   origin/main = $(g rev-parse origin/main)"

# A2' bot pin commit MODIFIES the branch's own reviewed row
g checkout -q --detach "$V"
printf '{"anchor":"branchrow","killed_by":"tests/OTHER.py","old":"o","reason":"bot rewrite of reviewed content"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/branchrow.json"
g add -A; as_bot -m "ci: pin killed mutants"; probe A2-modifies-reviewed-row "$(g rev-parse HEAD)" REFUSE

# A3' bot pin commit MODIFIES a row that came from main
g checkout -q --detach "$V"
printf '{"anchor":"mainrow","killed_by":"tests/OTHER.py","old":"o","reason":"bot rewrite"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/mainrow.json"
g add -A; as_bot -m "ci: pin killed mutants"; probe A3-modifies-main-row "$(g rev-parse HEAD)" REFUSE

# A9' bot pin commit DELETES a reviewed row
g checkout -q --detach "$V"; g rm -q tests/mutation_ledger/killed_by/branchrow.json
as_bot -m "ci: pin killed mutants"; probe A9-deletes-reviewed-row "$(g rev-parse HEAD)" REFUSE

# A7' bot pin subject reaching into prod code
g checkout -q --detach "$V"; mkdir -p "$W/clone/tests/mutation_ledger/killed_by"
printf '{"anchor":"x","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' > "$W/clone/tests/mutation_ledger/killed_by/x.json"
echo "    return 999" >> "$W/clone/custom_components/hpo/coordinator.py"
g add -A; as_bot -m "ci: pin killed mutants"; probe A7-reaches-prod-code "$(g rev-parse HEAD)" REFUSE

# A6' forged identity, correct subject and paths
g checkout -q --detach "$V"
printf '{"anchor":"y","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' > "$W/clone/tests/mutation_ledger/killed_by/y.json"
g add -A; g commit -qm "ci: pin killed mutants"; probe A6-forged-identity "$(g rev-parse HEAD)" REFUSE

# A5c' the glob, over the same merge, at main's current copy
g checkout -q --detach "$V"; g merge -q --no-edit -m "Merge origin/main into fix" origin/main
HM=$(g rev-parse HEAD)
probe A5b-merge-only "$(g rev-parse HEAD)" REFUSE
printf '{"anchor":"g","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' > "$W/clone/tests/mutation_ledger/*"
g add -A; as_bot -m "ci: pin killed mutants"; probe A5c-merge-then-glob-pin "$(g rev-parse HEAD)" REFUSE
# and the ordinary-name control over the same merge
g checkout -q --detach "$HM"
printf '{"anchor":"n","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' > "$W/clone/tests/mutation_ledger/killed_by/n.json"
g add -A; as_bot -m "ci: pin killed mutants"; probe N1-merge-then-ordinary-pin "$(g rev-parse HEAD)" REFUSE
g checkout -q fix 2>/dev/null || true
