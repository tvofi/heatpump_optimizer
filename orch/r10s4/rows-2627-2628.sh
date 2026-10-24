#!/bin/bash
# Poll origin heads of PR 2627 and 2628 every 5 min (up to 30 min) for dev/programme/delivery/<pr>.md at the current head.
cd /Users/timmalmstrom/hpo-seats/r10s4/gc-main || exit 1
for i in $(seq 1 6); do
  for pair in "2627 fix/r10-nightly-absent-new" "2628 fix/r10-flow-pull"; do
    set -- $pair; PR=$1; BR=$2
    H=$(git ls-remote origin "refs/heads/$BR" | cut -f1)
    git fetch -q origin "$H" 2>/dev/null
    if git cat-file -e "${H}:dev/programme/delivery/${PR}.md" 2>/dev/null; then echo "ROW-OK $PR $H"; fi
  done
  echo "poll $i $(date -u +%H:%M:%SZ) done-check"
  [ "$i" -lt 6 ] && sleep 300
done
echo END
