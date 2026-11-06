cd $HOME/ci
for spec in "41878084088 1" "41831302984 2"; do
  set -- $spec
  ln=$(awk -F'\t' -v r=$1 '$1==r{print $2, $4}' runs.tsv); set -- $1 $2 $ln
  for t in 1 2 3 4; do
    gh api "repos/tvofi/heatpump_optimizer/actions/runs/$1/jobs?per_page=100&filter=all&page=$2" --jq ".jobs[] | select(.name|test(\"replay|slow\")) | [\"$1\",\"$3\",\"$4\",(.id|tostring),.name,(.conclusion // \"none\")] | @tsv" >> jobs.d/$1.tsv && { echo "ok $1 p$2"; break; }
    sleep $((t*3))
  done
done
cat jobs.d/*.tsv | awk -F'\t' 'NF==6' | sort -u > jobs.tsv
awk -F'\t' '{print $5, $6}' jobs.tsv | sort | uniq -c
awk -F'\t' '$6=="success"||$6=="failure" {print $4}' jobs.tsv > want.txt
for t in 1 2 3; do
  cat want.txt | xargs -P 8 -I{} sh -c '[ -s logs/{}.log ] || gh api repos/tvofi/heatpump_optimizer/actions/jobs/{}/logs > logs/{}.log 2>/dev/null'
done
echo "logs wanted $(wc -l < want.txt), non-empty $(find logs -size +0 | wc -l)"
python3 parse.py
