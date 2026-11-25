#!/usr/bin/env bash
# record results/<key>.json for each newly gated key, then checkpoint
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g26; B=$W/probes/_box
while :; do
  for g in $W/gates/*.json; do k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    (cd $HOME/audit-r11-D3-s1 && /opt/hpo/venv-ci/bin/python3 $B/build_result.py $k) && bash $HOME/gate_wave.sh ckpt && echo "RECORDED $k $(date -u +%T)"
  done
  pgrep -f 'gate_wave.sh run' >/dev/null || { echo "DRIVER-EXITED $(bash $HOME/gate_wave.sh status)"; break; }
  sleep 60
done
