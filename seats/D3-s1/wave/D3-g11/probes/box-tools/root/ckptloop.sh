W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g11; last=""
while pgrep -f 'gate_wave.sh run' >/dev/null || pgrep -f recorder.sh >/dev/null; do
  sleep 600
  cur=$(find $W -type f -newer $HOME/.lastckpt 2>/dev/null | head -1)
  if [ -n "$cur" ] || [ ! -f $HOME/.lastckpt ]; then
    if out=$(bash $HOME/gate_wave.sh ckpt 2>&1) && ! echo "$out" | grep -q failed; then touch $HOME/.lastckpt; echo "CKPT $(date -u +%T)";
    else echo "checkpoint failed $(date -u +%T)"; bash $HOME/box_comms.sh heartbeat "checkpoint failed (periodic)" >/dev/null 2>&1; fi
  fi
done
