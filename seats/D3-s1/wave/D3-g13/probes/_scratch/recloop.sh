#!/bin/bash
# write results/<key>.json the moment a key's gate record lands, then checkpoint (brief step 3)
. $HOME/.boxcomms.env
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g13
while true; do
  for g in $W/gates/*.json; do
    k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    out=$(cd $HOME/audit-r11-D3-s1 && python3 $W/build_records.py --key $k 2>&1 | tail -3)
    echo "$(date -u +%FT%TZ) $out"
    c=$(bash $HOME/gate_wave.sh ckpt 2>&1); [ -n "$c" ] && echo "ckpt: $c" && bash $HOME/box_comms.sh heartbeat "ckpt after $k: $c" >/dev/null 2>&1
  done
  sleep 60
done
