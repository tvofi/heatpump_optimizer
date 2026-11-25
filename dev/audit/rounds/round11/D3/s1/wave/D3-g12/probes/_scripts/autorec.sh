while true; do
  for j in /root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g12/gates/*.json; do k=$(basename $j .json); [ "$k" = null ] && continue
    [ -f /root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g12/results/$k.json ] && continue
    python3 -c "import json,sys;sys.exit(0 if 'verdict' in json.load(open('$j')) else 1)" || continue
    if out=$(python3 /tmp/claude-0/-home-user-heatpump-optimizer/d7e935bf-adb6-5015-892f-0e6341b12e1d/scratchpad/gen/record.py $k 2>&1); then echo "$(date -u +%FT%TZ) $out"; else echo "$(date -u +%FT%TZ) RECORD-ERROR $k $out"; bash $HOME/box_comms.sh heartbeat "record error $k"; fi
    c=$(bash $HOME/gate_wave.sh ckpt 2>&1); [ -n "$c" ] && { echo "CKPT-FAIL $c"; bash $HOME/box_comms.sh heartbeat "ckpt: $c"; }
  done; sleep 30; done
