cd ~/hpo-seats/r10s3/orch-wt
gh run rerun 39268671139 --repo tvofi/heatpump_optimizer --failed && echo "rerun env-matrix"
until [ "$(gh run view 39268671139 --repo tvofi/heatpump_optimizer --json status -q .status)" = completed ]; do sleep 120; done
gh run view 39268671139 --repo tvofi/heatpump_optimizer --json conclusion -q '"env-matrix \(.conclusion)"'
gh run rerun 39272739691 --repo tvofi/heatpump_optimizer --failed && echo "rerun pr-contract"
