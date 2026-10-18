#!/bin/bash
# reviewer's mutation table for #2374; run from the review worktree
W=/Users/timmalmstrom/hpo-seats/r10s3/review-2374/wt
cd $W || exit 9
F=.claude/workflows/audit-find.js
C=tools/policy/check-wave-script.mjs
cp $F ../audit-find.js.orig; cp $C ../check.head
git show 52f698905:$C > ../check.base
run() { node $C > ../out.txt 2>&1; rc=$?; echo "rc=$rc $(grep -E '[0-9]+ (passed|failed)|failed' ../out.txt | tail -1)"; grep -E '^\s*(FAIL|✗)' ../out.txt | head -4; }
for which in base head; do
  cp ../check.$which $C
  echo "== check=$which, driver unmodified"; run
  for m in "s/^const BUNDLE_DIMS = new Set(\[[^]]*\])/const BUNDLE_DIMS = new Set([])/" \
           "s/^const BUNDLE_DIMS = new Set(\[[^]]*\])/const BUNDLE_DIMS = new Set(['D14'])/" \
           "s/^const BUNDLE_DIMS = new Set(\[[^]]*\])/const BUNDLE_DIMS = new Set(['D15', 'D14'])/" \
           "41s/^if (\[debugBundle/if (false \&\& [debugBundle/" \
           "s/^const ROUND_DIR =/let ROUND_DIR =/" \
           "s/^const CURRENT = \[/let CURRENT = [/" ; do
    cp ../audit-find.js.orig $F; sed -i '' "$m" $F
    echo "== check=$which mutant: $m  (changed lines: $(git diff --numstat -- $F | cut -f1))"; run
  done
  cp ../audit-find.js.orig $F
done
cp ../check.head $C; cp ../audit-find.js.orig $F
git status --porcelain
