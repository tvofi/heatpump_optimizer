#!/bin/bash
cd $HOME/wt; export PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1
K='R.section("#3616 R11-OUTSIDE-ROOMS-P2'
blk(){ timeout 900 python3 tools/audit/seat/features_block.py --prelude "exec(open('$HOME/w/P2').read())" "$K" 'R.section("R10-DRAW-MAP-EVIDENCE part A' > $HOME/w/out.$1 2>&1; echo "$1 rc=$? $(grep -cE '^ *FAIL' $HOME/w/out.$1) FAIL lines"; grep -E '^ *FAIL' $HOME/w/out.$1 | cut -c1-200; tail -2 $HOME/w/out.$1; }
blk unmutated
for m in both sched whatif whatif_cfg; do
  cp custom_components/heatpump_optimizer/coordinator.py /tmp/coord.bak
  python3 $HOME/w/c1.py $m && blk C1_$m
  cp /tmp/coord.bak custom_components/heatpump_optimizer/coordinator.py
done
git -C $HOME/wt status --short
echo DONE
