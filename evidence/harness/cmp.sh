S=$1
D=$S/scorecard
echo "== head"; python3 -I $HOME/wt/tools/audit/seat/scorecard.py report --dir $D --train-log $S/train.log --sweep-record $S/sweep.rec
echo "== study reference"; SW=$S/study/work/ python3 -I $HOME/h/ref.py --runs $D/runs.json --jobs $D/jobs --verdicts $D/verdicts.json --merges $D/merges.tsv --train $S/train.log --roster $D/roster.json
