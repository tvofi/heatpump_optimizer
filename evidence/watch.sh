#!/bin/bash
H=c4311a4629a88260a16eb49db4ae8616db671b7e
while :; do
  gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" --paginate -q '.check_runs[]|[.name,.status,(.conclusion//"-")]|@tsv' | sort > /Users/timmalmstrom/hpo-seats/1847-review/ev3/checks_watch.tsv
  n=$(grep -c in_progress /Users/timmalmstrom/hpo-seats/1847-review/ev3/checks_watch.tsv; true); q=$(grep -c queued /Users/timmalmstrom/hpo-seats/1847-review/ev3/checks_watch.tsv; true)
  [ "$n" = 0 ] && [ "$q" = 0 ] && break
  sleep 60
done
cat /Users/timmalmstrom/hpo-seats/1847-review/ev3/checks_watch.tsv
