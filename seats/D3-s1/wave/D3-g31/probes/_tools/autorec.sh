#!/usr/bin/env bash
# on each new gate record: write results/<key>.json from the precomputed step-4 spec, then checkpoint
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g31
while [ ! -f $HOME/.box_done ]; do
  for g in $W/gates/*.json; do
    k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    out=$(python3 $HOME/boxtools/build_results.py 2>&1)
    bash $HOME/gate_wave.sh ckpt >/dev/null 2>&1 && c=ok || { c=FAILED; bash $HOME/box_comms.sh heartbeat "checkpoint failed after $k" >/dev/null 2>&1; }
    echo "RECORDED $(echo $out | tr '\n' ' ') ckpt=$c"
  done
  sleep 60
done
