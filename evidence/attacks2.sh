#!/bin/bash
# Reviewer's own attack fixture for PR #2075's carry widening -- built by the
# reviewer, NOT the fixer's --self-test fixture, and using main's REAL
# .gitattributes so the merge-driver set matches production.
#
# Every attack runs `--carry` twice: main's copy of tools/pr/app_approve.sh and
# the head's. Prints one RESULT line per attack.
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence2
W=/Users/timmalmstrom/hpo-seats/review-2075/attack2
MAINCOPY=/Users/timmalmstrom/hpo-seats/review-2075/main2/tools/pr/app_approve.sh
FIXCOPY=/Users/timmalmstrom/hpo-seats/review-2075/wt2/tools/pr/app_approve.sh
REPO=/Users/timmalmstrom/hpo-seats/review-2075/main2
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'

rm -rf "$W"; mkdir -p "$W"
git init -q --bare "$W/remote.git"
git init -q -b main "$W/clone"
g() { git -C "$W/clone" -c user.name=rev -c user.email=rev@example.invalid "$@"; }
g remote add origin "$W/remote.git"

# main's REAL driver set, so `carry`'s exclusion list is production's, not a
# one-file stub.
git -C "$REPO" show HEAD:.gitattributes > "$W/clone/.gitattributes"

mkdir -p "$W/clone/tests/mutation_ledger/killed_by" "$W/clone/custom_components/hpo"
printf 'def coordinator():\n    return 1\n' > "$W/clone/custom_components/hpo/coordinator.py"
printf '{"killed_by": {}}\n' > "$W/clone/tests/mutation_budgets.json"
printf '{"closures": {}}\n' > "$W/clone/tests/closures.json"
# A row that already exists at main, and a 20-line ledger file the branch will
# modify so its hunk carries context lines (the shape a glob exclusion hides).
printf '{"anchor":"mainrow","killed_by":"tests/real_check.py","old":"o","reason":"r"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/mainrow.json"
for i in $(seq 1 20); do echo "ctx line $i"; done > "$W/clone/tests/mutation_ledger/ctx.json"
g add -A; g commit -qm "m0: base"; g push -q origin main

g checkout -qb fix
printf 'def coordinator():\n    if x:\n        return 2\n    return 1\n' > "$W/clone/custom_components/hpo/coordinator.py"
# the branch's OWN reviewed ledger row
printf '{"anchor":"branchrow","killed_by":"tests/real_check.py","old":"o","reason":"branch"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/branchrow.json"
# and a reviewed modification of an existing ledger file, at line 10
python3 - "$W/clone/tests/mutation_ledger/ctx.json" <<'PY'
import sys
p = sys.argv[1]; L = open(p).read().split("\n")
L[9] = "ctx line 10 CHANGED BY BRANCH"
open(p, "w").write("\n".join(L))
PY
g add -A; g commit -qm "fix: own work, with a reviewed ledger row of its own"
V=$(g rev-parse HEAD)
g push -q origin fix
echo "V = $V"

as_bot() { GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" \
           GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" \
           g commit -q "$@"; }
rowfile() { # relpath anchor killed_by
  mkdir -p "$(dirname -- "$W/clone/$1")"
  printf '{"anchor":"%s","killed_by":"%s","old":"o","reason":"r"}\n' "$2" "$3" > "$W/clone/$1"
}

# main moves: rewrite ctx.json line 8 (2 lines from the branch's line 10, so the
# automatic merge is clean but the branch hunk's -U3 CONTEXT differs).
g checkout -q main
python3 - "$W/clone/tests/mutation_ledger/ctx.json" <<'PY'
import sys
p = sys.argv[1]; L = open(p).read().split("\n")
L[7] = "ctx line 8 REWRITTEN UPSTREAM BY MAIN"
open(p, "w").write("\n".join(L))
PY
g commit -qam "m1: main rewrites a ledger context line"
g push -q origin main
M1=$(g rev-parse main)
echo "M1 = $M1 (origin/main now here)"

attack() { # id expect headsha
  local id=$1 expect=$2 h=$3 mo rc2 moout foout mverdict fverdict
  moout=$(cd "$W/clone" && bash "$MAINCOPY" --carry "$V" "$h" origin/main 2>&1); mo=$?
  foout=$(cd "$W/clone" && bash "$FIXCOPY" --carry "$V" "$h" origin/main 2>&1); rc2=$?
  printf '%s\n' "########## $id  (expect: $expect)"
  printf '%s\n' "  head $h  $(g log -1 --format='%an <%ae> | %s' "$h")"
  g diff --no-renames --name-status "$h^" "$h" 2>/dev/null | sed 's/^/    commit-diff /'
  printf '%s\n' "  [main-copy]  rc=$mo  $moout"
  printf '%s\n' "  [fixed-copy] rc=$rc2 $foout"
  local mverdict fverdict
  [ "$mo" = 0 ] && mverdict=CARRY || mverdict=REFUSE
  [ "$rc2" = 0 ] && fverdict=CARRY || fverdict=REFUSE
  echo "RESULT $id expect=$expect main-copy=$mverdict fixed-copy=$fverdict"
}

# A1 positive control: bot pin commit ADDS a fresh row.
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/newrow.json newrow tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"; attack A1-adds-fresh-row CARRY "$(g rev-parse HEAD)"

# A2 bot pin commit MODIFIES the branch's own already-reviewed row.
g checkout -q --detach "$V"
printf '{"anchor":"branchrow","killed_by":"tests/OTHER.py","old":"o","reason":"bot rewrite of reviewed content"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/branchrow.json"
g add -A; as_bot -m "ci: pin killed mutants"; attack A2-modifies-reviewed-row REFUSE "$(g rev-parse HEAD)"

# A3 bot pin commit MODIFIES a row that came from main.
g checkout -q --detach "$V"
printf '{"anchor":"mainrow","killed_by":"tests/OTHER.py","old":"o","reason":"bot rewrite"}\n' \
  > "$W/clone/tests/mutation_ledger/killed_by/mainrow.json"
g add -A; as_bot -m "ci: pin killed mutants"; attack A3-modifies-main-row REFUSE "$(g rev-parse HEAD)"

# A4 THE DOCTORED ROW: bot pin commit ADDS a row whose killing check names a
# script that does not exist anywhere in the tree.
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/bogus.json bogus tests/THIS_SCRIPT_DOES_NOT_EXIST.py
g add -A; as_bot -m "ci: pin killed mutants"; attack A4-adds-row-bogus-killed_by MEASURE "$(g rev-parse HEAD)"

# A5 THE GLOB ROW: bot pin commit ADDS a file literally named `*` under
# tests/mutation_ledger/ -- the path carry turns into `:(exclude)<path>`, which
# git wildmatches across `/`, so it excludes the WHOLE ledger subtree.
g checkout -q --detach "$V"; rowfile 'tests/mutation_ledger/*' glob tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"; H_GLOB=$(g rev-parse HEAD)
attack A5-adds-glob-named-file MEASURE "$H_GLOB"

# A5b the glob made to matter: merge main (whose line-8 rewrite shifts the
# branch's own line-10 hunk CONTEXT inside tests/mutation_ledger/ctx.json), then
# the glob pin commit on top. Without the glob this is the #2010 context-shift
# class and must refuse; with it, the ledger subtree is excluded from BOTH sides.
g checkout -q --detach "$V"; g merge -q --no-edit -m "Merge origin/main into fix" origin/main
g merge-tree --write-tree --no-messages "$V" origin/main >/dev/null 2>&1
H_MERGECTX=$(g rev-parse HEAD)
attack A5b-merge-then-no-glob MEASURE "$H_MERGECTX"
rowfile 'tests/mutation_ledger/*' glob tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"
attack A5c-merge-then-glob-pin MEASURE "$(g rev-parse HEAD)"

# A6 same subject and paths, NOT the bot's identity.
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/newrow.json newrow tests/real_check.py
g add -A; g commit -qm "ci: pin killed mutants"; attack A6-forged-identity REFUSE "$(g rev-parse HEAD)"

# A7 bot identity and pin subject, but the commit also reaches into prod code.
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/newrow.json newrow tests/real_check.py
echo "    return 999" >> "$W/clone/custom_components/hpo/coordinator.py"
g add -A; as_bot -m "ci: pin killed mutants"; attack A7-reaches-prod-code REFUSE "$(g rev-parse HEAD)"

# A8 bot identity, a REAL autofix shape, a DIFFERENT autofix message.
g checkout -q --detach "$V"; printf '{"closures": {"x": 1}}\n' > "$W/clone/tests/closures.json"
g add -A; as_bot -m "ci: re-record closures"; attack A8-other-autofix-message REFUSE "$(g rev-parse HEAD)"

# A9 bot pin commit DELETES a reviewed row.
g checkout -q --detach "$V"; g rm -q tests/mutation_ledger/killed_by/branchrow.json
as_bot -m "ci: pin killed mutants"; attack A9-deletes-reviewed-row REFUSE "$(g rev-parse HEAD)"

# A10 bot pin commit that is a MERGE (two parents).
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/newrow.json newrow tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"; H_ONE=$(g rev-parse HEAD)
g merge -q --no-edit -m "ci: pin killed mutants" origin/main 2>/dev/null
GIT_AUTHOR_NAME="$BOT_NAME" GIT_AUTHOR_EMAIL="$BOT_EMAIL" GIT_COMMITTER_NAME="$BOT_NAME" GIT_COMMITTER_EMAIL="$BOT_EMAIL" \
  g commit -q --amend --no-edit --reset-author 2>/dev/null
attack A10-pin-commit-as-merge MEASURE "$(g rev-parse HEAD)"

# A11 two chained bot pin commits.
g checkout -q --detach "$V"; rowfile tests/mutation_ledger/killed_by/r1.json r1 tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"
rowfile tests/mutation_ledger/killed_by/r2.json r2 tests/real_check.py
g add -A; as_bot -m "ci: pin killed mutants"; attack A11-two-chained-pins CARRY "$(g rev-parse HEAD)"

# A12 bot pin commit adding a row whose content is not JSON at all.
g checkout -q --detach "$V"
printf '#!/bin/sh\nrm -rf /\n' > "$W/clone/tests/mutation_ledger/killed_by/exec.sh"
g add -A; as_bot -m "ci: pin killed mutants"; attack A12-adds-nonrow-content MEASURE "$(g rev-parse HEAD)"

g checkout -q fix 2>/dev/null
echo
echo "=== is a literal file named '*' accepted as a ledger row, and does its"
echo "    pathspec exclude the WHOLE subtree? (measured, not assumed) ==="
echo "  paths the glob pin commit ADDED (this is exactly what bx collects):"
g diff --no-renames --diff-filter=A --name-only "$H_GLOB^" "$H_GLOB" | sed 's/^/    /'
echo "  files present under tests/mutation_ledger/ at $V:"
g ls-tree -r --name-only "$V" -- tests/mutation_ledger | sed 's/^/    /'
echo "  of those, how many survive the pathspec ':(exclude)tests/mutation_ledger/*'?"
echo "    (answered by the direct probe below, which is the measurement that matters)"
echo "  direct probe -- a change to a DEEP ledger path, with and without the glob:"
g checkout -q --detach "$V"
printf 'probe\n' >> "$W/clone/tests/mutation_ledger/killed_by/branchrow.json"
printf 'probe\n' >> "$W/clone/tests/mutation_ledger/ctx.json"
g add -A; g commit -qm "probe: two deep ledger edits"
H_PROBE=$(g rev-parse HEAD)
echo "    no glob   -> visible paths: $(g diff --no-renames --name-only "$V" "$H_PROBE" -- . | tr '\n' ' ')"
echo "    with glob -> visible paths: $(g diff --no-renames --name-only "$V" "$H_PROBE" -- . ':(exclude)tests/mutation_ledger/*' | tr '\n' ' ')"
echo "RESULT glob-pathspec: an exclude of 'tests/mutation_ledger/*' hides $(g diff --no-renames --name-only "$V" "$H_PROBE" -- . | wc -l | tr -d ' ') -> $(g diff --no-renames --name-only "$V" "$H_PROBE" -- . ':(exclude)tests/mutation_ledger/*' | wc -l | tr -d ' ') visible ledger path(s)"
g checkout -q fix 2>/dev/null || true
