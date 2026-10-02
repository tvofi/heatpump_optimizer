#!/bin/bash
H=1517fa2d6363cba80335a1db35623682aad177e4
while :; do
  gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" --paginate -q '.check_runs[]|[.name,.status,(.conclusion//"-")]|@tsv' | sort > /Users/timmalmstrom/hpo-seats/1847-review/ev2/checks_watch.tsv
  n=$(grep -c in_progress /Users/timmalmstrom/hpo-seats/1847-review/ev2/checks_watch.tsv; true); q=$(grep -c queued /Users/timmalmstrom/hpo-seats/1847-review/ev2/checks_watch.tsv; true)
  [ "$n" = 0 ] && [ "$q" = 0 ] && break
  sleep 60
done
cat /Users/timmalmstrom/hpo-seats/1847-review/ev2/checks_watch.tsv
