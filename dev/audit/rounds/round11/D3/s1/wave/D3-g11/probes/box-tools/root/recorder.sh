W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g11
while true; do
  for g in $W/gates/*.json; do
    k=$(basename $g .json); [ "$k" = null ] && continue
    [ -f $W/results/$k.json ] && continue
    grep -q '"verdict"' $g || continue
    if python3 $HOME/probes/build_result.py $k; then
      bash $HOME/gate_wave.sh ckpt && echo "RECORDED $k ckpt-ok"
    else
      echo "RECORD-FAILED $k"; touch $W/results/.$k.failed
    fi
  done
  grep -q GATES-DONE $HOME/run.log && [ $(ls $W/results/*.json 2>/dev/null | wc -l) -ge 16 ] && { echo RECORDER-DONE; exit 0; }
  sleep 30
done
