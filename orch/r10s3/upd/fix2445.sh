cd ~/hpo-seats/r10s3/orch-wt
H=40c4e1194dfd23371403f874e9a8a1abd45da162
runs=$(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" -q '.check_runs[]|select(.conclusion=="failure" and (.name=="env-matrix" or .name=="validate-hacs"))|.html_url' | sed -E 's#.*/runs/([0-9]+)/.*#\1#' | sort -u)
for r in $runs; do gh api repos/tvofi/heatpump_optimizer/actions/runs/$r/jobs -q '.jobs[]|select(.conclusion=="failure")|.id' | head -1 | while read j; do gh api repos/tvofi/heatpump_optimizer/actions/jobs/$j/logs 2>/dev/null | grep -m1 -oiE 'rate limit[^"]{0,60}|unreachable'; done; gh run rerun $r --repo tvofi/heatpump_optimizer --failed && echo "rerun $r"; done
for r in $runs; do until [ "$(gh run view $r --repo tvofi/heatpump_optimizer --json status -q .status)" = completed ]; do sleep 120; done; gh run view $r --repo tvofi/heatpump_optimizer --json conclusion -q "\"$r \(.conclusion)\""; done
D=~/hpo-orch/r10s3/train/b20; mkdir -p $D; echo '[{"pr":2445,"verdict":"40c4e1194dfd23371403f874e9a8a1abd45da162"}]' > $D/q.json
tools/audit/seat/train.sh --queue $D/q.json --repo tvofi/heatpump_optimizer --state-dir $D --mandate 6175172275 --skip-bad --overlap --approval-carry --pre-flight --free-holders > $D/train.log 2>&1; echo "b20 rc=$?"; grep -E 'MERGED|SKIP|PARK' $D/train.log
