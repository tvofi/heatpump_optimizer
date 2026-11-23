#!/usr/bin/env bash
# write results/<key>.json as each gate record lands, checkpoint, exit when attention is needed
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g10
while true; do
  for g in $W/gates/*.json; do
    k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    v=$(python3 -c "import json;print(json.load(open('$g')).get('verdict','?'))")
    if [ "$k" = f68e6ba7e28b251a ] && [ "$v" != TIMEOUT ]; then echo "ATTN f68e6ba7e28b251a verdict $v (needs a probe)"; exit 0; fi
    python3 $HOME/pgen/mkrec.py $k || { echo "ATTN mkrec failed $k"; exit 0; }
    out=$(bash $HOME/gate_wave.sh ckpt 2>&1); echo "$out" | grep -q "checkpoint failed" && bash $HOME/box_comms.sh heartbeat "checkpoint failed after $k" >/dev/null 2>&1
    echo "REC $k $v"
    [ "$v" = KILLED ] && { echo "ATTN KILLED $k"; exit 0; }
  done
  n=$(ls $W/results/*.json 2>/dev/null | wc -l)
  [ $n -ge 16 ] && { echo "ALL-RECORDED $n"; exit 0; }
  if ! pgrep -f "gate_wave.sh run" >/dev/null; then echo "ATTN driver not running; $(tail -1 $HOME/gate_wave.log)"; exit 0; fi
  sleep 60
done
