#!/bin/bash
# counters on every corpus tree (package only, via git archive)
RT=/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/archscore/redteam
for sha in $(tail -n +2 $RT/../a2/corpus.tsv | cut -f1,2 | tr '\t' '\n' | sort -u); do
  out=$RT/corpus/$sha.counters.json
  [ -s $out ] && continue
  d=$RT/corpus/tree_$sha; rm -rf $d; mkdir -p $d
  git -C /home/user/heatpump_optimizer archive $sha custom_components | tar -x -C $d
  python3 $RT/counters/counters.py $d > $out 2> $RT/corpus/$sha.err || echo "{}" > $out
  rm -rf $d
done
echo done
