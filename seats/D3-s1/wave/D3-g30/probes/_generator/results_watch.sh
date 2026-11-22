#!/bin/bash
# box-local: write results/<key>.json the moment gates/<key>.json lands, then checkpoint
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g30
shopt -s nullglob
while [ ! -f $HOME/.results_watch_stop ]; do
  need=0
  for g in $W/gates/*.json; do k=$(basename $g .json); [ "$k" = null ] && continue; [ -f $W/results/$k.json ] || need=1; done
  if [ $need = 1 ]; then
    sleep 5
    /opt/hpo/venv-ci/bin/python3 $W/build_results.py 2>&1 | sed 's/^/BUILD /'
    bash $HOME/gate_wave.sh ckpt 2>&1 | sed 's/^/CKPT /'
    echo "CKPT done $(date -u +%FT%TZ)"
  fi
  sleep 60
done
