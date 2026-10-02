#!/bin/bash
# Reviewer's mutants of the precursor pieces (07b0704b), at head 1517fa2d; each restored.
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH
cd /Users/timmalmstrom/hpo-seats/1850-review/wt
echo "== null: policy_lint fixture and check-wave-script unmutated"
node .claude/workflows/policy_lint.mjs >/dev/null 2>&1; echo "policy_lint rc=$?"
node .claude/workflows/check-wave-script.mjs 2>&1 | tail -1
echo "== P1: resolvePrFromCommit loses the squash alternative (D13-s1-01 back)"
perl -pi -e 's{\Q || MERGE_SUBJECT_RE.exec(String(subject))\E}{}' .claude/workflows/policy_lint.mjs; git diff --stat | tail -1
node .claude/workflows/policy_lint.mjs 2>&1 | grep -E 'VACUOUS|squash' | head -2; echo "policy_lint rc=${PIPESTATUS[0]}"
git checkout -q -- .claude/workflows/policy_lint.mjs
echo "== P2: rulePaths dropped from the export"
perl -pi -e 's{resolvePrFromCommit, rulePaths \}}{resolvePrFromCommit \}}' .claude/workflows/policy_lint.mjs; git diff --stat | tail -1
node .claude/workflows/check-wave-script.mjs 2>&1 | grep -E 'FAIL|passed, ' | head -3
git checkout -q -- .claude/workflows/policy_lint.mjs
echo "== P3: rulePaths returns [] (reader alive, wrong answer)"
perl -0pi -e 's{(function rulePaths\([^)]*\)\s*\{)}{$1 return [];}' .claude/workflows/policy_lint.mjs; git diff --stat | tail -1
node .claude/workflows/check-wave-script.mjs 2>&1 | grep -E 'FAIL|passed, ' | head -3
git checkout -q -- .claude/workflows/policy_lint.mjs
git status --short
