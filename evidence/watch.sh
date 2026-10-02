#!/bin/bash
H=b660da5528f359a375011497bee49e27ed561722
while :; do
  gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" --paginate -q '.check_runs[]|[.name,.status,(.conclusion//"-")]|@tsv' | sort > /Users/timmalmstrom/hpo-seats/1850-review/ev/checks_watch.tsv
  n=$(grep -c in_progress /Users/timmalmstrom/hpo-seats/1850-review/ev/checks_watch.tsv; true); q=$(grep -c queued /Users/timmalmstrom/hpo-seats/1850-review/ev/checks_watch.tsv; true)
  [ "$n" = 0 ] && [ "$q" = 0 ] && break
  sleep 60
done
cat /Users/timmalmstrom/hpo-seats/1850-review/ev/checks_watch.tsv
