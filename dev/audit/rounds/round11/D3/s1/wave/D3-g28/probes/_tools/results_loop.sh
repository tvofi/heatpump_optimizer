#!/usr/bin/env bash
# Box D3-g28: write results/<key>.json the moment gates/<key>.json is recorded, then checkpoint.
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g28
B=/tmp/claude-0/-home-user-heatpump-optimizer/614877ca-0447-5e86-b38e-3e0cf80ee5e1/scratchpad/build_result.py
while true; do
  for k in $(tail -n +2 $W/keys.tsv | cut -f1); do
    [ -f $W/gates/$k.json ] && [ ! -f $W/results/$k.json ] || continue
    last=""
    [ -f $W/gates/$k.log ] && last=$(grep -o '^########## [^#]* ##########' $W/gates/$k.log | tail -1 | sed 's/#//g; s/^ *//; s/ *$//')
    if python3 $B $k "$last"; then
      echo "RESULT-WRITTEN $k $(python3 -c "import json;d=json.load(open('$W/results/$k.json'));print(d['gate']['verdict'],d['class'])")"
      bash $HOME/gate_wave.sh ckpt || bash $HOME/box_comms.sh heartbeat "checkpoint failed after results/$k.json"
      bash $HOME/box_comms.sh heartbeat "results/$k.json written and checkpointed" >/dev/null 2>&1
    else
      echo "RESULT-BUILD-FAILED $k"
    fi
  done
  grep -q "RUN-EXIT" $HOME/gate_wave.log && [ "$(ls $W/results | wc -l)" -ge "$(tail -n +2 $W/keys.tsv | grep -c .)" ] && { echo RESULTS-ALL-DONE; exit 0; }
  sleep 60
done
