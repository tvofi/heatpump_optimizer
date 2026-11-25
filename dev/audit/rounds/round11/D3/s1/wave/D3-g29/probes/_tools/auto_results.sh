#!/usr/bin/env bash
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g29
while [ ! -f $HOME/.auto_stop ]; do
  for k in $(awk -F'\t' 'NR>1{print $1}' $W/keys.tsv); do
    if [ -f $W/gates/$k.json ] && [ ! -f $W/results/$k.json ]; then
      python3 /tmp/claude-0/-home-user-heatpump-optimizer/832c17c0-253b-5ead-9c0a-65b544be7325/scratchpad/build_result.py $k && bash $HOME/gate_wave.sh ckpt && echo "RESULT-WRITTEN $k $(python3 -c "import json;r=json.load(open('$W/results/$k.json'));print(r['gate']['verdict'],r['class'])")" || echo "RESULT-ERROR $k"
    fi
  done
  sleep 60
done
