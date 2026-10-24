#!/bin/bash
set -uo pipefail
R=tvofi/heatpump_optimizer
merge_when_green() {
  local pr=$1 sha=$2
  for i in $(seq 1 60); do
    line=$(gh api "repos/$R/commits/$sha/check-runs?per_page=100" --jq '{p: [.check_runs[] | select(.status!="completed")] | length, f: [.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure" and .name!="nightly-status") | .name]}')
    echo "$(date -u +%T) #$pr $line"
    case "$line" in
      *'"p": 0'*'"f": []'*) gh pr merge $pr --repo $R --merge --match-head-commit $sha >/dev/null 2>&1 && { echo "#$pr MERGED"; return 0; } || { echo "#$pr merge refused"; return 1; } ;;
      *'"f": ['\''\''* ) echo "#$pr UNEXPECTED"; printf '%s' "$line"; return 1 ;;
    esac
    sleep 60
  done
  echo "#$pr TIMEOUT"; return 1
}
merge_when_green 1893 4b4c0f03366c50f70d07695db1af888ae8df0c09 || exit 1
merge_when_green 1894 d6c1f64de2965c04ffff07d5883043980da89ce3 || exit 1
# 1895: absorb latest main, update body, push, then merge
cd /Users/timmalmstrom/heatpump_optimizer
git fetch -q origin main
git worktree add -q --detach /tmp/w95 81cc117be09ca271f4f22fbbed23ed5157dc7359 2>/dev/null || true
cd /tmp/w95 && git merge origin/main --no-edit >/dev/null 2>&1 && H95=$(git rev-parse HEAD) && echo "1895 absorbed -> $H95"
cd /Users/timmalmstrom/heatpump_optimizer && git push origin $H95:refs/heads/fix/r9-fr-5 2>&1 | tail -1
gh pr edit 1895 --repo $R --body-file <(gh pr view 1895 --repo $R --json body --jq .body | sed "s/\`81cc117b[0-9a-f]*\`/\`$H95\` (extends 81cc117b by an automatic origin\/main absorb; tools\/audit\/prepr.sh is unchanged between the heads, so the verdict carries)/") >/dev/null
for i in $(seq 1 60); do
  line=$(gh api "repos/$R/commits/$H95/check-runs?per_page=100" --jq '{p: [.check_runs[] | select(.status!="completed")] | length, f: [.check_runs | group_by(.name)[] | sort_by(.started_at) | last | select(.conclusion=="failure" and .name!="nightly-status") | .name]}')
  echo "$(date -u +%T) #1895 $line"
  case "$line" in
    *'"p": 0'*'"f": []'*) gh pr merge 1895 --repo $R --merge --match-head-commit $H95 >/dev/null 2>&1 && { echo "#1895 MERGED"; break; } || echo "#1895 retry" ;;
  esac
  sleep 60
done
rm -rf /tmp/w95
echo "TRAIN-DRAIN COMPLETE"
