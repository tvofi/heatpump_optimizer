set -u
cd $HOME/ci
: > runs.tsv
for p in $(seq 1 12); do
  gh api "repos/tvofi/heatpump_optimizer/actions/workflows/389816862/runs?per_page=100&page=$p" --jq '.workflow_runs[] | [.id,.event,.head_sha,.created_at,.conclusion] | @tsv' >> runs.tsv || echo "page $p failed" >&2
done
for p in 1 2; do gh api "repos/tvofi/heatpump_optimizer/actions/workflows/392625081/runs?per_page=100&page=$p" --jq '.workflow_runs[] | [.id,.event,.head_sha,.created_at,.conclusion] | @tsv' >> runs.tsv; done
echo runs: $(wc -l < runs.tsv)
: > jobs.tsv
while IFS=$'\t' read id ev sha cr concl; do
  gh api "repos/tvofi/heatpump_optimizer/actions/runs/$id/jobs?per_page=100&filter=all" --paginate --jq ".jobs[] | select(.name|test(\"replay|slow\")) | [\"$id\",\"$ev\",\"$cr\",.id,.name,.conclusion] | @tsv" >> jobs.tsv 2>/dev/null
done < runs.tsv
echo jobs: $(wc -l < jobs.tsv)
mkdir -p logs
awk -F'\t' '$6=="success"||$6=="failure"' jobs.tsv | while IFS=$'\t' read r ev cr jid nm c; do
  [ -s logs/$jid.log ] || gh api repos/tvofi/heatpump_optimizer/actions/jobs/$jid/logs > logs/$jid.log 2>/dev/null
done
echo DONE logs: $(ls logs | wc -l)
