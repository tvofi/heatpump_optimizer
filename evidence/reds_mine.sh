#!/bin/bash
# My own enumeration of every red check-run over the range, per fix-review step 11.
set -uo pipefail
WT=/Users/timmalmstrom/hpo-seats/r9rev-2066/wt
OUT=/Users/timmalmstrom/hpo-seats/r9rev-2066/ev/reds_mine.tsv
cd "$WT" || exit 1
BASE=$(git merge-base origin/main HEAD)
echo "range base $BASE"
: > "$OUT"; n=0; fails=0
for sha in $(git rev-list "$BASE..HEAD"); do
  short=$(git rev-parse --short "$sha"); n=$((n+1))
  body=$(gh api --paginate "repos/tvofi/heatpump_optimizer/commits/$sha/check-runs" \
    --jq '.check_runs[] | select(.status=="completed" and .conclusion=="failure") | select(.name!="pr-contract") | .name + "\t" + (.id|tostring)')
  rc=$?
  if [ $rc -ne 0 ]; then echo "READ FAILED at $short rc=$rc"; fails=$((fails+1)); continue; fi
  while IFS=$(printf '\t') read -r name id; do
    [ -n "$name" ] && printf '%s\t%s\t%s\n' "$short" "$name" "$id" >> "$OUT"
  done <<< "$body"
done
echo "commits read: $n   read failures: $fails"
echo "rows: $(grep -c . "$OUT")"
cut -f2 "$OUT" | sort | uniq -c | sort -rn
