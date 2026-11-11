#!/bin/bash
# blocked verdicts of CLASS (regex) on review/* and verdict/* in a commit-date window; one row per (pr, head)
FROM=$1; UNTIL=$2; CLASS=$3
for r in $(git for-each-ref --format='%(refname)' refs/bus/review refs/bus/verdict); do
  pr=${r##*/}; kind=$(basename $(dirname $r))
  git log --format='%H %cI' --since="$FROM" --until="$UNTIL" "$r" | while read c d; do
    l=$(git show "$c:VERDICT.md" 2>/dev/null | head -1)
    echo "$l" | grep -Eq "^Fix review: blocked [0-9a-f]{40} ($CLASS):" && echo "$pr $kind $c $d $(echo "$l" | cut -d' ' -f4) $(echo "$l" | cut -d' ' -f5)"
  done
done
