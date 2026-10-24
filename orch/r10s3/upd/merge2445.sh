cd ~/hpo-seats/r10s3/orch-wt; H=40c4e1194dfd23371403f874e9a8a1abd45da162; T=$(date -u +%Y-%m-%dT%H:%M)
sleep 60
until s=$(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?check_name=pr-contract" -q "[.check_runs[]|select(.started_at>\"$T\")]|sort_by(.started_at)|last|\"\(.status) \(.conclusion)\""); [ "${s%% *}" = completed ]; do sleep 120; done; echo "pr-contract $s"
[ "$s" = "completed success" ] || exit 1
D=~/hpo-orch/r10s3/train/b22; mkdir -p $D; echo '[{"pr":2445,"verdict":"40c4e1194dfd23371403f874e9a8a1abd45da162"}]' > $D/q.json
tools/audit/seat/train.sh --queue $D/q.json --repo tvofi/heatpump_optimizer --state-dir $D --mandate 6175172275 --skip-bad --overlap --approval-carry --pre-flight --free-holders > $D/train.log 2>&1; echo "b22 rc=$?"; grep -E 'MERGED|SKIP|PARK' $D/train.log
