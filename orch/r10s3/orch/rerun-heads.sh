#!/bin/bash
# rerun-heads.sh: at RERUN_AT, rerun failed runs on main and on every open PR's CURRENT head.
until [ "$(date -u +%s)" -ge "$(date -u -j -f %Y-%m-%dT%H:%M:%SZ "$RERUN_AT" +%s)" ]; do sleep 30; done
R=tvofi/heatpump_optimizer
for sha in $(gh api repos/$R/commits/main -q .sha) $(gh pr list -R $R --json headRefOid -q '.[].headRefOid'); do
  for run in $(gh api "repos/$R/commits/$sha/check-runs?per_page=100" -q '.check_runs[]|select(.conclusion=="failure" or .conclusion=="cancelled")|.details_url' | sed -E 's#.*/runs/([0-9]+)/.*#\1#' | sort -u); do
    gh run rerun "$run" -R $R --failed >/dev/null 2>&1 && echo "rerun ${sha:0:8} $run" || echo "rerun-fail ${sha:0:8} $run"
  done
done
