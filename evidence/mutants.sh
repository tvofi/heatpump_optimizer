#!/bin/bash
# Reviewer's own mutants (round 2), run in the head worktree; each restored with git checkout.
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH
cd /Users/timmalmstrom/hpo-seats/1847-review/wt
E=/Users/timmalmstrom/hpo-seats/1847-review/ev
lane() { python3 -I .claude/workflows/agreement_py.py --out $E/m.json >/dev/null 2>&1 && node .claude/workflows/agreement.mjs --py-json $E/m.json 2>&1 | grep -E 'divergent [1-9]|REFUSED|RESULT'; echo "rc=${PIPESTATUS[0]}"; }
run() { echo "== $1"; perl -0pi -e "$3" "$2"; git diff --stat | tail -1; lane; git checkout -q -- "$2"; }
run "D14-s2-03 CLASS_GUESS grammar" .claude/workflows/audit-find.js 's{const CLASS_GUESS = /\^\(I1\|[^\n]*}{const CLASS_GUESS = /^([PI][0-9]+|new)\$/}'
run "D13-s1-01 merge-commit shape only" .claude/workflows/policy_lint.mjs 's{\Q|| MERGE_SUBJECT_RE.exec(String(subject))\E}{}'
run "D11-s1-72 _GOV_FILES one file" tests/entities.py 's{_GOV_FILES = \[_GOV_WF, [^\]]*\]}{_GOV_FILES = [_GOV_WF]}s'
run "D7-s3-02 reader gone: dead = []" tests/structure.py 's{dead = sorted\(\(members\[k\]\[0\], k\[1\], k\[2\], members\[k\]\[1\]\) for k in members if k not in live\)}{dead = []}'
git status --short
