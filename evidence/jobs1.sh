id=$1; ev=$2; cr=$3
gh api "repos/tvofi/heatpump_optimizer/actions/runs/$id/jobs?per_page=100&filter=all" --paginate --jq ".jobs[] | select(.name|test(\"replay|slow\")) | [\"$id\",\"$ev\",\"$cr\",.id,.name,.conclusion] | @tsv" > jobs.d/$id.tsv 2>/dev/null || echo "FAILED $id" >&2
