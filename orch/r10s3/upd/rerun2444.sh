sleep 1500
H=8be64a110fa4e741889920c4eff2b6b4cb99cf3a
for r in $(gh api "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" -q '.check_runs[]|select(.conclusion=="failure" and (.name=="arch-score" or .name=="validate-hacs"))|.html_url' | sed -E 's#.*/runs/([0-9]+)/.*#\1#' | sort -u); do gh run rerun $r --repo tvofi/heatpump_optimizer --failed && echo "rerun $r"; done
