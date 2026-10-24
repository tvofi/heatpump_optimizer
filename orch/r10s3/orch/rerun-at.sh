#!/bin/bash
# Re-run failed jobs on main and given PR heads after the Actions installation rate limit resets.
until [ "$(date -u +%s)" -ge "$(date -u -j -f %Y-%m-%dT%H:%M:%SZ "$RERUN_AT" +%s)" ]; do sleep 30; done
R=tvofi/heatpump_optimizer
for sha in $(gh api repos/$R/commits/main -q .sha) "$@"; do
  for run in $(gh api "repos/$R/commits/$sha/check-runs?per_page=100" -q '.check_runs[]|select(.conclusion=="failure")|.details_url' | sed -E 's#.*/runs/([0-9]+)/.*#\1#' | sort -u); do
    gh run rerun "$run" -R $R --failed >/dev/null 2>&1 && echo "rerun $sha $run" || echo "rerun-fail $sha $run"
  done
done
