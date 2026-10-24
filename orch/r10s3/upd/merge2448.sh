S=4c9dc5d92fade9e622fa56a86fd07e8ca98d60b1
for i in $(seq 1 60); do
  sleep 120
  st=$(gh pr view 2448 --repo tvofi/heatpump_optimizer --json mergeStateStatus,reviewDecision -q '"\(.mergeStateStatus) \(.reviewDecision)"' 2>/dev/null)
  echo "$(date -u +%H:%MZ) $st"
  case "$st" in CLEAN*|UNSTABLE*) gh pr merge 2448 --repo tvofi/heatpump_optimizer --merge --match-head-commit $S --body "R10-DEAD-RATE-LIMIT. Leaves #201 open." && echo MERGED && exit 0;; esac
done; echo TIMEOUT
