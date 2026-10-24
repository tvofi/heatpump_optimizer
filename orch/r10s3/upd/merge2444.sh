cd ~/hpo-seats/r10s3/orch-wt; H=07e34f2a59a960713f9e662395cf52c3c869dba7
until s=$(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?check_name=pr-contract" -q '[.check_runs[]]|sort_by(.started_at)|last|"\(.status) \(.conclusion)"'); [ "${s%% *}" = completed ]; do sleep 120; done; echo "pr-contract $s"
[ "$s" = "completed success" ] || exit 1
D=~/hpo-orch/r10s3/train/b23; mkdir -p $D; echo '[{"pr":2444,"verdict":"8be64a110fa4e741889920c4eff2b6b4cb99cf3a"}]' > $D/q.json
tools/audit/seat/train.sh --queue $D/q.json --repo tvofi/heatpump_optimizer --state-dir $D --mandate 6175172275 --skip-bad --overlap --approval-carry --pre-flight --free-holders > $D/train.log 2>&1; echo "b23 rc=$?"; grep -E 'MERGED|SKIP|PARK' $D/train.log
