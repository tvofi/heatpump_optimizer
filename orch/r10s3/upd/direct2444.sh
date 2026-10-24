cd ~/hpo-seats/r10s3/orch-wt
for i in $(seq 1 40); do st=$(gh pr view 2444 --repo tvofi/heatpump_optimizer --json state,mergeStateStatus,headRefOid -q '"\(.state) \(.mergeStateStatus) \(.headRefOid)"'); echo "$(date -u +%H:%MZ) $st"; set -- $st
 [ "$1" = MERGED ] && { echo MERGED; exit 0; }
 [ "$3" != 0f6fc6c9560a5b465c70cf55ec8dc5894d0c921e ] && { echo "HEAD MOVED $3"; exit 2; }
 case "$2" in CLEAN|UNSTABLE) gh pr merge 2444 --repo tvofi/heatpump_optimizer --merge --match-head-commit $3 --body "R10-SEAT-SELFTESTS-CI (Fix review: merge 8be64a11; head 0f6fc6c9 = clean main merges, named in ## Head). Merged under mandate 6175172275. Leaves #201 open." && { gh pr view 2444 --repo tvofi/heatpump_optimizer --json mergeCommit -q '"MERGED \(.mergeCommit.oid)"'; exit 0; };; esac
 sleep 120; done; echo TIMEOUT
