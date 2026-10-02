#!/bin/bash
# List tests.yml pull_request runs since the pin date; for each, jobs closures + closures-autofix.
R=tvofi/heatpump_optimizer
: > runs.tsv; fails=0
for page in 1 2 3 4 5 6 7 8 9 10; do
  out=$(gh api "repos/$R/actions/workflows/tests.yml/runs?event=pull_request&created=>=2026-09-26&per_page=100&page=$page" --jq '.workflow_runs[]|[.id,.head_sha,.head_branch,.created_at]|@tsv' 2>err.txt) || { fails=$((fails+1)); cat err.txt; }
  [ -z "$out" ] && break
  echo "$out" >> runs.tsv
done
echo "runs: $(wc -l < runs.tsv)  list-failures: $fails"
: > jobs.tsv; jf=0
while IFS=$'\t' read id sha br ts; do
  j=$(gh api "repos/$R/actions/runs/$id/jobs?per_page=100&filter=latest" --jq '.jobs[]|select(.name=="closures" or .name=="closures-autofix")|[.name,.conclusion,.id]|@tsv' 2>>err.txt) || { jf=$((jf+1)); continue; }
  c=$(echo "$j" | awk -F'\t' '$1=="closures"{print $2"\t"$3}')
  a=$(echo "$j" | awk -F'\t' '$1=="closures-autofix"{print $2"\t"$3}')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$sha" "$br" "$ts" "${c:-none	-}" "${a:-none	-}" >> jobs.tsv
done < runs.tsv
echo "job-list failures: $jf"
