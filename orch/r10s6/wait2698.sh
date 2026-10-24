export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
for i in $(seq 1 40); do
  s=$(gh pr view 2698 --json headRefOid,statusCheckRollup --jq '.headRefOid[0:9]+" "+([.statusCheckRollup[]|select(.name=="codeql / Analyze (python)")|.status]|join(","))')
  echo "$s" | grep -q COMPLETED && { echo "CODEQL DONE $s"; exit 0; }
  echo "$s" | grep -q '^3383fb2' || { echo "HEAD MOVED $s"; exit 0; }
  sleep 300
done; echo TIMEOUT
