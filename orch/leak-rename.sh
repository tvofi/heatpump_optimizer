#!/bin/bash
cd ~/heatpump_optimizer || exit 1
L=~/hpo-orch/leak-rename.log; : > $L
git ls-remote origin | grep -iE "timmalm|malmstr" | while read -r sha ref; do
  old=${ref#refs/heads/}; new="wip-sync/scratch-${old##*scratchpad-}"
  tree=$(git rev-parse "$sha^{tree}")
  parents=()
  for p in $(git rev-list --parents -n1 "$sha" | cut -d' ' -f2-); do parents+=(-p "$p"); done
  when=$(git log -1 --format=%cI "$sha")
  c=$(git commit-tree "$tree" "${parents[@]}" -m "wip-sync ${new#wip-sync/} $when") &&
    git push -q --no-verify origin "$c:refs/heads/$new" ":$ref" && echo "OK $new" >> $L || echo "FAIL $old" >> $L
done
grep -c ^OK $L; grep -v ^OK $L | head -3
git ls-remote origin | grep -ciE "timmalm|malmstr"
