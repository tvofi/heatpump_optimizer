# usage: census.sh <review_carry.py path> ; run from worktree
RC=$1
git rev-list --merges --format='%H %P%x09%s' origin/main | grep -v '^commit' | awk -F'\t' '$2 ~ /^Merge (remote-tracking branch .origin\/main.|origin\/main|branch .main.)/ {print $1}' | head -n 200 | while read -r m p1 p2 rest; do [ -n "$rest" ] && continue; h=$(python3 -I $RC $p1 $m --main $p2 --verdict-only); a=$(bash tools/pr/app_approve.sh --carry $p1 $m $p2 >/dev/null 2>&1 && echo CARRY || echo FRESH-REVIEW); echo "$h $a $m"; done
