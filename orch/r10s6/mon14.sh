export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
prev="__prime__"
while true; do
  git fetch -q origin 2>/dev/null
  cur=$( { gh pr list --state open --json number,headRefOid --jq '.[]|"PR \(.number) \(.headRefOid[0:9])"'
    for t in ratio-anchor thermal-power-option config-notices mutant-skip rca-codescan-wait fly-cloud-setup-toolchain fly-cipredict-layout structure-alias merge-subject-harden codeql-dependabot; do echo "HO $t $(git rev-parse --short=9 origin/handoff/r10-$t 2>/dev/null)"; done
    for p in 41010 44714; do kill -0 $p 2>/dev/null && echo "alive $p" || echo "DEAD-opener $p"; done
    for b in $(gh pr list --state open --json number,headRefName --jq '.[]|"\(.number):\(.headRefName)"'); do n=${b%%:*}; r=${b#*:}; git ls-tree -r --name-only origin/$r dev/programme/delivery/ 2>/dev/null | grep -q "/$n.md" && echo "ROW $n"; done
  } | sort)
  [ "$prev" != "__prime__" ] && comm -13 <(echo "$prev") <(echo "$cur")
  prev="$cur"; sleep 300
done
