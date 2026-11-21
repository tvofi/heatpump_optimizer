#!/bin/bash
# usage: run.sh <detector: block|edge>
cd $HOME/mut/base; export PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1
K='R.section("#3616 R11-OUTSIDE-ROOMS-3B'
det() { if [ "$1" = block ]; then timeout 600 python3 tools/audit/seat/features_block.py --prelude "exec(open('$HOME/mut/P').read())" "$K" >/tmp/o.$$ 2>&1; else timeout 1200 python3 tests/edge.py > /tmp/o.$$ 2>&1; fi; echo $?; }
echo "UNMUTATED $1 rc=$(det $1)"
for m in ${MLIST:-$(python3 $HOME/mut/mutants.py --list)}; do
  git -C . init -q 2>/dev/null; cp -a custom_components /tmp/cc.$$
  python3 $HOME/mut/mutants.py $m || { echo "$m APPLY-FAIL"; rm -rf /tmp/cc.$$; continue; }
  rc=$(det $1); f=$(grep -m1 -E "^ *FAIL|Error|Traceback" /tmp/o.$$ | cut -c1-140)
  [ "$rc" = 0 ] && echo "$m SURVIVED ($1)" || echo "$m KILLED rc=$rc ($1) $f"
  rm -rf custom_components && mv /tmp/cc.$$ custom_components
done
