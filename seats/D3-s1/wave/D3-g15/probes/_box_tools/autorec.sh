#!/usr/bin/env bash
# Box D3-g15: write results/<key>.json + checkpoint the moment each gate record lands.
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g15
while [ ! -f $HOME/.boxcomms-r11-D3-g15/done ]; do
  for k in $(tail -n +2 $W/keys.tsv | cut -f1); do
    if [ -f $W/gates/$k.json ] && [ ! -f $W/results/$k.json ]; then
      sleep 5
      (cd $HOME && python3 build_g15.py key $k) && bash $HOME/gate_wave.sh ckpt && echo "RECORDED $k $(python3 -c "import json;d=json.load(open('$W/results/$k.json'));print(d['gate']['verdict'],d['class'])")"
    fi
  done
  sleep 60
done
