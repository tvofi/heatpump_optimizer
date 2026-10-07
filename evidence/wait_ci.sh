#!/bin/bash
H=957c9cd08b520fd07a68a648921d44afbcbe270f
for i in $(seq 1 90); do
  n=$(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" --jq '[.check_runs[]|select(.status!="completed")]|length' 2>/dev/null)
  [ "$n" = 0 ] && break
  sleep 60
done
gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" --jq '.check_runs[]|[.name,.status,(.conclusion//"-"),.completed_at]|@tsv' | sort > /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029-evidence/checkruns-final.tsv
echo done
