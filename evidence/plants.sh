#!/bin/bash
# plants.sh <verdict head> <outfile>: plant each driver-file seam on <verdict head>, run each carry script
set -u
V=$1; OUT=$2; R=/home/user/heatpump_optimizer; S=/tmp/claude-0/scripts
WT=$(mktemp -d)/wt; git -C $R worktree add -q --detach $WT $V; cd $WT
g() { git -c user.name=t -c user.email=t@t "$@"; }
gb() { git -c user.name=bot -c user.email='41898282+github-actions[bot]@users.noreply.github.com' "$@"; }
bump() { python3 - "$1" <<'P'
import sys,re
p=sys.argv[1]; s=open(p).read()
m=re.search(r'(:\s*)(\d+)', s); s=s[:m.end()]+'1'+s[m.end():]; open(p,'w').write(s)
P
}
mk() { git checkout -q --detach $V; }
# main2: origin/main plus one unrelated commit, for the merge seam
git checkout -q --detach origin/main; echo "plant" >> README.md; g commit -qam "docs: plant"; MAIN2=$(git rev-parse HEAD)
declare -A H MAINREF
mk; bump tests/structure_budgets.json; g commit -qam "fix: tidy wording"; H[own-budget]=$(git rev-parse HEAD)
mk; echo "planted claim line" >> tests/golden/claimed_drift.txt; g commit -qam "fix: tidy wording"; H[own-claim]=$(git rev-parse HEAD)
mk; g commit -q --allow-empty -m "fix: nothing"; H[own-empty-NULL]=$(git rev-parse HEAD)
mk; bump tests/closures.json; g commit -qam "ci: tidy"; H[ci-bare-closures]=$(git rev-parse HEAD)
mk; g commit -q --allow-empty -m "ci: tidy"; H[ci-bare-empty-NULL]=$(git rev-parse HEAD)
mk; bump tests/structure_budgets.json; gb commit -qam "ci: re-record closures"; H[bot-outside-paths]=$(git rev-parse HEAD)
mk; bump tests/closures.json; gb commit -qam "ci: re-record closures"; H[bot-own-path-NULL]=$(git rev-parse HEAD)
mk; g merge -q --no-ff --no-commit $MAIN2 >/dev/null 2>&1; bump tests/structure_budgets.json; git add -A; g commit -q -m "Merge main2"; H[merge-hand-budget]=$(git rev-parse HEAD); MAINREF[merge-hand-budget]=$MAIN2
mk; g merge -q --no-ff -m "Merge main2" $MAIN2 >/dev/null 2>&1; H[merge-auto-NULL]=$(git rev-parse HEAD); MAINREF[merge-auto-NULL]=$MAIN2
{
echo "verdict head $V; main2 $MAIN2 (origin/main $(git rev-parse origin/main) + one README line)"
for k in own-budget own-claim own-empty-NULL ci-bare-closures ci-bare-empty-NULL bot-outside-paths bot-own-path-NULL merge-hand-budget merge-auto-NULL; do
  m=${MAINREF[$k]:-origin/main}
  echo "== $k  head ${H[$k]}  main $m  files: $(git diff --name-only $V ${H[$k]} --not 2>/dev/null | tr '\n' ' ')"
  for s in r1 head M1 M8; do
    r=$(bash $S/aa-$s.sh --carry $V ${H[$k]} $m 2>&1 | grep -m1 '^CARRY')
    echo "  [$s] $r"
  done
done
} > $OUT 2>&1
cd $R; git worktree remove --force $WT
