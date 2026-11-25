#!/usr/bin/env bash
# box-local: record each newly gated key (record.py) and checkpoint it
. $HOME/.boxcomms.env
export PYTHONPATH=tests/hastub
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g04
while true; do
  for k in $(tail -n +2 $W/keys.tsv | cut -f1); do
    if [ -f $W/gates/$k.json ] && [ ! -f $W/results/$k.json ]; then
      (cd $HOME/pgen && python3 record.py $k) > $HOME/wavelogs/rec_$k.log 2>&1
      echo "RECORDED $k rc=$? class=$(python3 -c "import json;print(json.load(open('$W/results/$k.json'))['class'])" 2>&1)"
      bash $HOME/gate_wave.sh ckpt
    fi
  done
  [ "$(ls $W/results/*.json | wc -l)" -ge 16 ] && { echo ALLRECORDED; exit 0; }
  sleep 60
done
