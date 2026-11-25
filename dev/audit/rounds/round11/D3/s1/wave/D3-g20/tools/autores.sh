#!/usr/bin/env bash
# write results/<key>.json for every newly gated key (probe in the scratch tree), checkpoint; exit when the driver ends
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g20
while :; do
  for g in $W/gates/*.json; do k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    $HOME/mkres.sh $k && echo "RESULT-WRITTEN $k $(python3 -c "import json;print(json.load(open('$W/results/$k.json'))['class'])")" || echo "RESULT-FAILED $k"
    bash $HOME/gate_wave.sh ckpt
  done
  pgrep -f 'gate_wave.sh run' >/dev/null || { echo "DRIVER-DONE $(tail -1 $HOME/gate_run.log)"; break; }
  sleep 60
done
