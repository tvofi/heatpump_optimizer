#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
go() { # pr sha dir
  for i in $(seq 1 60); do s=$(gh pr view $1 --json mergeStateStatus -q .mergeStateStatus); [ "$s" = CLEAN ] && break; sleep 30; done
  tools/audit/seat/merge_pr.sh $1 $2 $3 owner --mandate 6329234399 --ready
}
go 2704 879dd65becbc34403458628b0614ccdb43063e9f /Users/timmalmstrom/.zcode/bus/verdicts/2704/3d37a2f198719bfc45afe5a58dfb94abbc0d78a9
echo CHAIN_DONE
