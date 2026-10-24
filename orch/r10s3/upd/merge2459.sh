cd ~/hpo-seats/r10s3/orch-wt
for i in $(seq 1 30); do st=$(gh pr view 2459 --repo tvofi/heatpump_optimizer --json state,mergeStateStatus,headRefOid -q '"\(.state) \(.mergeStateStatus) \(.headRefOid)"'); echo "$(date -u +%H:%MZ) $st"; set -- $st
 [ "$1" = MERGED ] && { echo MERGED; exit 0; }
 case "$2" in CLEAN|UNSTABLE) gh pr merge 2459 --repo tvofi/heatpump_optimizer --merge --match-head-commit $3 --body "Record rows for #2456, #2458. Leaves #201 open." && { echo MERGED; exit 0; };; esac
 sleep 120; done; echo TIMEOUT
