#!/bin/bash
# Hygiene, budgets, merge simulation and a cleaner `literal`-pathspec probe for
# the review of PR #2075. Read-only except inside the reviewer's own fixture.
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence
WT=/Users/timmalmstrom/hpo-seats/review-2075/wt
BASEWT=/Users/timmalmstrom/hpo-seats/review-2075/base
HEAD=094f2c0d2696b4bd04cd485b9e7fc3f144620053
BASE=b2b6acd64cde652676a568e93c05f021571ebe5e
PY3="$HOME/.local/state/hpo/venv-ci/bin/python3"
cd "$WT" || exit 9

echo "=== git version (the pathspec magic must be this git's) ==="
git --version

echo
echo "=== 1. claims files byte-equal to origin/main's? ==="
for f in tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt; do
  a=$(git rev-parse "origin/main:$f" 2>/dev/null || echo MISSING)
  b=$(git rev-parse "HEAD:$f" 2>/dev/null || echo MISSING)
  if [ "$a" = "$b" ]; then echo "RESULT claim-file $f IDENTICAL to origin/main ($a)"; else echo "RESULT claim-file $f DIFFERS origin/main=$a head=$b"; fi
done

echo
echo "=== 2. VERSION / manifest version / RELEASE_NOTES heading untouched? ==="
for f in VERSION manifest.json RELEASE_NOTES.md; do
  if git diff --quiet "$BASE" HEAD -- "$f"; then echo "RESULT $f untouched"; else echo "RESULT $f TOUCHED"; git diff --stat "$BASE" HEAD -- "$f"; fi
done
echo "  any file in the diff besides the two named? "
git diff --name-only "$BASE"...HEAD | sed 's/^/    /'
echo "RESULT files changed = $(git diff --name-only "$BASE"...HEAD | wc -l | tr -d ' ')"

echo
echo "=== 3. delivery row for this PR ==="
ls docs/delivery/ 2>/dev/null | tail -5
if [ -f docs/delivery/2075.md ]; then echo "RESULT docs/delivery/2075.md present at head"; else echo "RESULT docs/delivery/2075.md ABSENT at head"; fi
git log --oneline -1 origin/main -- docs/delivery/ | sed 's/^/  last delivery change on main: /'

echo
echo "=== 4. structure ratchet, head vs baseline ==="
( cd "$WT"     && "$PY3" -I tests/structure.py > "$EV/structure-head.txt" 2>&1 ); echo "  head     rc=$?  $(tail -1 "$EV/structure-head.txt")"
( cd "$BASEWT" && "$PY3" -I tests/structure.py > "$EV/structure-base.txt" 2>&1 ); echo "  baseline rc=$?  $(tail -1 "$EV/structure-base.txt")"
echo "  diff of the two runs (empty = no metric moved):"
diff <(sed 's/[0-9a-f]\{7,\}//g' "$EV/structure-base.txt") <(sed 's/[0-9a-f]\{7,\}//g' "$EV/structure-head.txt") | sed 's/^/    /'
echo "RESULT structure: head rc and baseline rc above; diff lines = $(diff "$EV/structure-base.txt" "$EV/structure-head.txt" | wc -l | tr -d ' ')"

echo
echo "=== 5. policy budgets, head vs baseline ==="
( cd "$WT"     && node tools/policy/policy_lint.mjs --budgets > "$EV/budgets-head.txt" 2>&1 ); echo "  head     rc=$?"
( cd "$BASEWT" && node tools/policy/policy_lint.mjs --budgets > "$EV/budgets-base.txt" 2>&1 ); echo "  baseline rc=$?"
echo "  diff (empty = no cap moved):"
diff "$EV/budgets-base.txt" "$EV/budgets-head.txt" | sed 's/^/    /'
echo "RESULT policy-budgets diff lines = $(diff "$EV/budgets-base.txt" "$EV/budgets-head.txt" | wc -l | tr -d ' ')"
grep -i "app_approve\|policy_lint" "$EV/budgets-head.txt" | sed 's/^/    budget-row /' | head

echo
echo "=== 6. policy_lint plain run, baseline for comparison ==="
( cd "$BASEWT" && node tools/policy/policy_lint.mjs > "$EV/policy_lint-base-plain.txt" 2>&1 ); echo "  baseline rc=$?"
tail -4 "$EV/policy_lint-base-plain.txt" | sed 's/^/    /'
echo "  head vs baseline, the two summary lines:"
grep -h "^TOTAL:\|^FIXTURE ok:\|^KNOWN-BAD:" "$EV/policy_lint-base-plain.txt" | sed 's/^/    base /'
grep -h "^TOTAL:\|^FIXTURE ok:\|^KNOWN-BAD:" "$EV/policy_lint-head-plain.txt" | sed 's/^/    head /'

echo
echo "=== 7. merge simulation: git merge-tree --write-tree origin/main HEAD ==="
git merge-tree --write-tree origin/main "$HEAD" > "$EV/mergetree.txt" 2>"$EV/mergetree.err"; mt=$?
echo "  exit=$mt"; echo "  stdout:"; sed 's/^/    /' "$EV/mergetree.txt" | head -20; echo "  stderr:"; sed 's/^/    /' "$EV/mergetree.err" | head -20
echo "  driver markers in stderr: $(grep -c 'MERGE-CLAIM:' "$EV/mergetree.err")"
grep -n 'MERGE-CLAIM:' "$EV/mergetree.err" | sed 's/^/    /'
echo "RESULT merge-tree exit=$mt markers=$(grep -c 'MERGE-CLAIM:' "$EV/mergetree.err")"
echo "  same against the branch base $BASE:"
git merge-tree --write-tree "$BASE" "$HEAD" >/dev/null 2>&1; echo "    exit=$?"

echo
echo "=== 8. the literal-pathspec remedy, probed cleanly ==="
W=/Users/timmalmstrom/hpo-seats/review-2075/attack
g() { git -C "$W/clone" -c user.name=rev -c user.email=rev@example.invalid "$@"; }
HN2=5118a2523d19ed9658ff527448a83a0a16fdb0f1
g checkout -q --detach "$HN2"
printf 'probe2\n' >> "$W/clone/tests/mutation_ledger/ctx.json"
printf 'probe2\n' >> "$W/clone/tests/mutation_ledger/*"
g add -A; g commit -qm "probe: change BOTH the glob-named file and a deep ledger file"
HP2=$(g rev-parse HEAD)
echo "  changed paths, no exclusion      : [$(g diff --no-renames --name-only "$HN2" "$HP2" | tr '\n' ' ')]"
echo "  with :(exclude)tests/mutation_ledger/*         : [$(g diff --no-renames --name-only "$HN2" "$HP2" -- . ':(exclude)tests/mutation_ledger/*' | tr '\n' ' ')]"
echo "  with :(exclude,literal)tests/mutation_ledger/* : [$(g diff --no-renames --name-only "$HN2" "$HP2" -- . ':(exclude,literal)tests/mutation_ledger/*' | tr '\n' ' ')]"
echo "RESULT literal-pathspec: plain hides $(g diff --no-renames --name-only "$HN2" "$HP2" | wc -l | tr -d ' ') -> $(g diff --no-renames --name-only "$HN2" "$HP2" -- . ':(exclude)tests/mutation_ledger/*' | wc -l | tr -d ' '); literal hides $(g diff --no-renames --name-only "$HN2" "$HP2" | wc -l | tr -d ' ') -> $(g diff --no-renames --name-only "$HN2" "$HP2" -- . ':(exclude,literal)tests/mutation_ledger/*' | wc -l | tr -d ' ')"
g checkout -q fix 2>/dev/null || true
