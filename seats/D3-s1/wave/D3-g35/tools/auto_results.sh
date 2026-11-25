#!/bin/bash
# step 3 driver: write results/<key>.json the moment gates/<key>.json is recorded, then checkpoint
. $HOME/.boxcomms.env
SP=/tmp/claude-0/-home-user-heatpump-optimizer/7d8210e3-06a0-5026-9403-56518ba5807c/scratchpad
TREE=$HOME/audit-r11-D3-s1; W=$TREE/dev/audit/rounds/round11/D3/s1/wave/D3-g35
while true; do
  done_all=1
  for k in $(tail -n +2 $W/keys.tsv | cut -f1); do
    [ -f $W/results/$k.json ] && continue
    done_all=0
    [ -f $W/gates/$k.json ] || continue
    (cd $TREE && python3 $SP/write_result.py $k $SP/out/$k.txt) && echo "RESULT-WRITTEN $k $(python3 -c "import json;d=json.load(open('$W/gates/$k.json'));print(d.get('verdict'),d.get('killed_by'),d.get('gate_rc'))")" && (bash $HOME/gate_wave.sh ckpt >/dev/null 2>&1 && echo "CKPT ok $k" || echo "CKPT FAILED $k")
  done
  [ $done_all = 1 ] && { echo ALL-RESULTS; exit 0; }
  pgrep -f "gate_wave.sh run" >/dev/null || { sleep 60; pgrep -f "gate_wave.sh run" >/dev/null || { echo "GATE-WAVE-NOT-RUNNING"; }; }
  sleep 60
done
