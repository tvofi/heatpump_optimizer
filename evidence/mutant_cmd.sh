#!/bin/bash
cd /tmp/tmp.d3CAK05dTp/wt
export PYTHONPATH=tests/hastub
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/tmp.d3CAK05dTp/preA.py").read())' 'R.section("supply switch at step boundaries (#2492, R10-SAV-ACTUATION)")' '# --- R10-CEILING-PROBE' > /tmp/tmp.d3CAK05dTp/blkA.out 2>&1; a=$?
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/tmp.d3CAK05dTp/preB.py").read())' 'R.section("early cut-off — a warm room stops a space-heating pump inside the interval")' 'R.section("°F set-points: one unit rule for every set-point write (D12-s3-01, L1, L2)")' > /tmp/tmp.d3CAK05dTp/blkB.out 2>&1; b=$?
echo "A=$a B=$b $(tail -1 /tmp/tmp.d3CAK05dTp/blkA.out) | $(tail -1 /tmp/tmp.d3CAK05dTp/blkB.out)"
[ $a -eq 0 ] && [ $b -eq 0 ]
