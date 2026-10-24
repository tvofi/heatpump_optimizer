cd ~/hpo-seats/r10s3/orch-wt; H=40c4e1194dfd23371403f874e9a8a1abd45da162
until s=$(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?check_name=budget-raise-gate" -q '[.check_runs[]]|sort_by(.started_at)|last|"\(.status) \(.conclusion)"'); [ "${s%% *}" = completed ]; do sleep 90; done; echo "budget-raise-gate $s"
[ "$s" = "completed success" ] || exit 1
gh pr merge 2445 --repo tvofi/heatpump_optimizer --merge --match-head-commit $H --body "R10-SETPOINT-POWER (Fix review: merge 40c4e119, comment by bus 95c28f91). Merged under mandate 6175172275. Leaves #201 open." && gh pr view 2445 --repo tvofi/heatpump_optimizer --json mergeCommit -q '"MERGED \(.mergeCommit.oid)"'
