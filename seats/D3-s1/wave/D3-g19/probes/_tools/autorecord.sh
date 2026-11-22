#!/usr/bin/env bash
# For each gated key with no results/<key>.json yet: build it, checkpoint. Ends when all keys have records.
. $HOME/.boxcomms.env
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g19
S=$(dirname "$0")
while true; do
  left=0
  for k in $(tail -n +2 $W/keys.tsv | cut -f1); do
    [ -f $W/results/$k.json ] && continue
    left=$((left+1))
    [ -f $W/gates/$k.json ] || continue
    if out=$(PYTHONPATH= python3 $S/build_result.py $k 2>&1); then
      echo "$out" | tail -1
      cp $S/analysis.py $S/build_result.py $W/probes/_tools/ 2>/dev/null
      bash $HOME/gate_wave.sh ckpt || echo "CKPT-FAILED $k"
      left=$((left-1))
    else
      echo "BUILD-FAILED $k: $(echo "$out" | tail -3 | tr '\n' ' ')"; sleep 600
    fi
  done
  [ $left -eq 0 ] && { echo "ALL-RECORDED"; exit 0; }
  sleep 60
done
