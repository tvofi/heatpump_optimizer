#!/bin/bash
# The group's mutation command: the two features_block.py blocks, at the reviewed head.
cd /tmp/tmp.I0JMrj4V2w/wt
export PYTHONPATH=tests/hastub
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/tmp.I0JMrj4V2w/preA.py").read())' 'R.section("supply switch at step boundaries (#2492, R10-SAV-ACTUATION)")' 'from heatpump_optimizer import duty_switch as _ds_mod  # noqa: E402' > /tmp/tmp.I0JMrj4V2w/blkA.out 2>&1; a=$?
python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/tmp.I0JMrj4V2w/preB.py").read())' 'R.section("early cut-off — a warm room stops a space-heating pump inside the interval")' 'R.section("°F set-points: one unit rule for every set-point write (D12-s3-01, L1, L2)")' > /tmp/tmp.I0JMrj4V2w/blkB.out 2>&1; b=$?
echo "A=$a B=$b $(tail -1 /tmp/tmp.I0JMrj4V2w/blkA.out) | $(tail -1 /tmp/tmp.I0JMrj4V2w/blkB.out)"
[ $a -eq 0 ] && [ $b -eq 0 ]
