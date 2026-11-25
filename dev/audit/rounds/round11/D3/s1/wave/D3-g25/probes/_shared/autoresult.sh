#!/usr/bin/env bash
# step 3 automation: write results/<key>.json the moment gates/<key>.json lands, then checkpoint
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g25
export PATH="/opt/hpo/venv-ci/bin:$PATH"
while true; do
  for g in $W/gates/*.json; do [ -e "$g" ] || continue; k0=$(basename $g .json); [ -f $W/results/$k0.failed ] && continue
    k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    if python3 $HOME/scratch/write_result.py $k; then bash $HOME/gate_wave.sh ckpt; echo "RESULT-WRITTEN $k"
    else echo "RESULT-FAILED $k"; bash $HOME/box_comms.sh heartbeat "result write failed: $k" >/dev/null 2>&1; touch $W/results/$k.failed; fi
  done
  [ "$(ls $W/results/*.json 2>/dev/null | wc -l)" -ge 16 ] && { echo ALL-RESULTS; exit 0; }
  sleep 30
done
