#!/bin/bash
# Re-derive the body's #2010 `norm()` figures with carry's own pipeline.
set -uo pipefail
cd /Users/timmalmstrom/hpo-seats/review-2075-r4/head
V1=d67d8a44ec6e6a2c93e2cedf126ba10ea00b2470
H1=87849cd277485bd28bc85d64bc104293c5c7e6de
for MREF in f5fb67077eb1f351a904329cb387a01bbc937f97 origin/main; do
  mv=$(git merge-base "$MREF" "$V1"); mh=$(git merge-base "$MREF" "$H1")
  x=()
  while IFS= read -r p; do [ -z "$p" ] || x[${#x[@]}]=":(exclude)$p"; done \
    <<<"$(git show "$MREF:.gitattributes" 2>/dev/null | awk '!/^#/ && / merge=/ {print $1}')"
  d=(git -c core.quotepath=off diff --binary --no-renames --no-color --no-ext-diff --no-textconv --diff-algorithm=myers -U3)
  norm() { "${d[@]}" "$1" "$2" -- . ${x[@]+"${x[@]}"} | sed -e '/^index /d' -e 's/^@@ .*/@@/'; }
  norm "$mv" "$V1" > /tmp/r4-2010-left.txt
  norm "$mh" "$H1" > /tmp/r4-2010-right.txt
  nl=$(wc -l < /tmp/r4-2010-left.txt | tr -d ' ')
  nr=$(wc -l < /tmp/r4-2010-right.txt | tr -d ' ')
  diff /tmp/r4-2010-left.txt /tmp/r4-2010-right.txt > /tmp/r4-2010-diff.txt
  dl=$(wc -l < /tmp/r4-2010-diff.txt | tr -d ' ')
  lt=$(grep -c '^<' /tmp/r4-2010-diff.txt || true)
  gt=$(grep -c '^>' /tmp/r4-2010-diff.txt || true)
  ar=$(grep -cE '^[<>] *[+-]' /tmp/r4-2010-diff.txt || true)
  printf 'RESULT 2010-norm main=%.12s mv=%.9s mh=%.9s left=%s right=%s diff_lines=%s (<%s >%s, of which +/- lines: %s)\n' \
    "$MREF" "$mv" "$mh" "$nl" "$nr" "$dl" "$lt" "$gt" "$ar"
  grep -E '^[<>]' /tmp/r4-2010-diff.txt | head -4
done
