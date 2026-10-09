#!/bin/bash
# Reviewer's own mutants for PR #2075 ROUND 2, planted on the re-cut head's own
# production lines in a throwaway worktree at cfa0f3d00. Round 1's MA/MB/MC/ME
# targeted the old shape (a `bot_commit()` function and a policy_lint.mjs `root`
# parameter); neither exists at this head, so these are new mutants for the two
# production changes that do:
#   (a) the additions-only narrowing of main's `bot_paths` accumulation
#   (b) `:(exclude,literal)$p` in place of `:(exclude)$p`
# Each mutant is restored before the next. Prints a RESULT line per mutant
# naming exactly which arms moved.
set -uo pipefail
MUT=/Users/timmalmstrom/hpo-seats/review-2075/mut2
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence2
SH="$MUT/tools/pr/app_approve.sh"
HEAD=cfa0f3d00a6fa8bd3604f02a066088fc3f07aba2

restore() { git -C "$MUT" checkout -- tools/pr/app_approve.sh; }
clean() { git -C "$MUT" status --porcelain; }

run_st() { # name
  local name=$1 out nfail
  restore
  apply_$name
  local dirty_after_plant
  dirty_after_plant=$(clean | wc -l | tr -d ' ')
  out=$(cd "$MUT" && bash tools/pr/app_approve.sh --self-test 2>&1)
  printf '%s\n' "$out" > "$EV/mutant-$name.txt"
  echo "  summary: $(printf '%s\n' "$out" | tail -1)"
  echo "  red arms:"
  printf '%s\n' "$out" | grep '^FAIL' | sed 's/^/    /'
  nfail=$(printf '%s\n' "$out" | grep -c '^FAIL')
  echo "RESULT mutant $name: $nfail red arm(s); files dirtied by the plant: $dirty_after_plant"
  restore
}

# ------------------------------------------------------------------- MNL
# The carry file's named mutation `no_literal` -- it does not exist in the tree
# (the only `no_literal` is an unrelated local in tests/structure.py), so plant
# it from the carry's own description: drop `literal` from the exclude pathspec.
# CLAIM UNDER TEST: "re-carries exactly the glob-named arm and nothing else".
apply_MNL() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = 'x[${#x[@]}]=":(exclude,literal)$p"'
assert s.count(old) == 1, f"MNL anchor count {s.count(old)} != 1"
s = s.replace(old, 'x[${#x[@]}]=":(exclude)$p"')
open(p, "w").write(s)
PY
}

# ------------------------------------------------------------------- MAF
# Drop `--diff-filter=A` from the accumulation's added-paths read, so a row the
# bot REWROTE or DELETED is hidden exactly as an added one is. This is the
# narrowing's own mechanism; if nothing goes red the narrowing is not load-bearing.
apply_MAF() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = 'ba=$(git diff --no-renames --diff-filter=A --name-only "$c^" "$c")'
assert s.count(old) == 1, f"MAF anchor count {s.count(old)} != 1"
s = s.replace(old, 'ba=$(git diff --no-renames --name-only "$c^" "$c")')
open(p, "w").write(s)
PY
}

# ------------------------------------------------------------------- MCO
# The maximal reversion: replace the whole additions-only block with main's
# landed one-liner, i.e. go back to the coarse whole-subtree exclusion.
# CLAIM UNDER TEST (carry file): "the planted regression, 6 failed arms".
apply_MCO() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
start_anchor = '        ba=$(git diff --no-renames --diff-filter=A --name-only "$c^" "$c")'
end_anchor = '        done <<<"$b"\n'
i = s.index(start_anchor)
j = s.index(end_anchor, i) + len(end_anchor)
s = s[:i] + '        bots="$bots$b"$\'\\n\'\n' + s[j:]
open(p, "w").write(s)
PY
}

# ------------------------------------------------------------------- MEX
# Remove the exact-file arm of the new conditional, so EVERY `bot_paths` entry
# goes through the additions-only subtree walk. `tests/mutation_budgets.json` is
# a FILE entry, so a pin commit that legitimately rewrites it would stop being
# excluded -- this tests that the conditional's first branch is load-bearing
# too, not only its else.
apply_MEX() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = '          if printf \'%s\\n\' "$bt" | grep -qxF "$e"; then\n            bots="$bots$e"$\'\\n\'\n          else\n'
assert old in s, "MEX anchor not found"
new = '          if false; then\n            bots="$bots$e"$\'\\n\'\n          else\n'
s = s.replace(old, new)
open(p, "w").write(s)
PY
}

for m in MNL MAF MCO MEX; do
  echo "########## mutant $m"
  run_st "$m"
  echo
done
restore
echo "RESULT worktree clean after all mutants: [$(clean)]"
echo "RESULT head under mutation: $HEAD"
