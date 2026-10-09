#!/bin/bash
# Reviewer's own mutants for PR #2075, planted on the head's own production
# lines in a throwaway worktree at the head SHA. Each mutant is restored before
# the next. Prints a RESULT line per mutant naming exactly which arms moved.
set -uo pipefail
MUT=/Users/timmalmstrom/hpo-seats/review-2075/mut
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence
SH="$MUT/tools/pr/app_approve.sh"
LINT="$MUT/tools/policy/policy_lint.mjs"
HEAD=094f2c0d2696b4bd04cd485b9e7fc3f144620053

restore() { git -C "$MUT" checkout -- tools/pr/app_approve.sh tools/policy/policy_lint.mjs; }
clean() { git -C "$MUT" status --porcelain; }

run_st() { # name -> runs the self-test, prints the summary and the FAIL arms
  local name=$1 out
  restore
  apply_$name
  out=$(cd "$MUT" && bash tools/pr/app_approve.sh --self-test 2>&1)
  printf '%s\n' "$out" > "$EV/mutant-$name.txt"
  echo "  summary: $(printf '%s\n' "$out" | tail -1)"
  echo "  red arms:"
  printf '%s\n' "$out" | grep '^FAIL' | sed 's/^/    /'
  local nfail
  nfail=$(printf '%s\n' "$out" | grep -c '^FAIL')
  echo "RESULT mutant $name: $nfail red arm(s); worktree dirty files: $(clean | wc -l | tr -d ' ')"
  restore
}

# ---------------------------------------------------------------- M-A (3-i)
# Widen the message narrowing: accept ANY of the three autofix messages.
apply_MA() {
  python3 - "$SH" <<'PY'
import sys, re
p = sys.argv[1]; s = open(p).read()
old = '''if m != "ci: pin killed mutants":
    print(repr(m) + " is an autofix commit, but not the mutation ledger pin commit")
    sys.exit(1)
'''
assert old in s, "M-A anchor not found"
s = s.replace(old, "")
open(p, "w").write(s)
PY
}

# ---------------------------------------------------------------- M-B (3-ii)
# Widen the exclusion to MODIFICATIONS as well as additions.
apply_MB() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = 'git diff --no-renames --diff-filter=A --name-only "$parent" "$sha"'
assert old in s, "M-B anchor not found"
s = s.replace(old, 'git diff --no-renames --name-only "$parent" "$sha"')
open(p, "w").write(s)
PY
}

# ---------------------------------------------------------------- M-C (mine)
# The maximal widening of the seam the diff opens: skip autofixCommit entirely
# and accept ANY single-parent `ci:` commit, excluding every path it adds.
apply_MC() {
  python3 - "$SH" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
start = s.index("bot_commit() {")
end = s.index("\n}\n", s.index('git diff --no-renames --diff-filter=A --name-only "$parent" "$sha"', start)) + 3
body = '''bot_commit() {
  local sha=$1
  git rev-parse --verify -q "$sha^" >/dev/null || { echo "no single parent"; return 1; }
  git diff --no-renames --diff-filter=A --name-only "$sha^" "$sha"
}
'''
s = s[:start] + body + s[end:]
open(p, "w").write(s)
PY
}

# ---------------------------------------------------------------- M-E (mine)
# Delete the `root` threading in policy_lint.mjs -- the half of this diff the
# body's four mutants never touch. If nothing goes red, that half is unjustified.
apply_ME() {
  python3 - "$LINT" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a1 = "function autofixCommit(sha, root = ROOT) {"
a2 = "{ allowFail: true, quiet: true, root })"
assert a1 in s, "M-E anchor 1 not found"
assert s.count(a2) == 3, f"M-E expected 3 threaded git() calls, found {s.count(a2)}"
s = s.replace(a1, "function autofixCommit(sha) {")
s = s.replace(a2, "{ allowFail: true, quiet: true })")
open(p, "w").write(s)
PY
}

for m in MA MB MC ME; do
  echo "########## mutant $m"
  run_st "$m"
  echo
done
restore
echo "RESULT worktree clean after all mutants: [$(clean)]"
