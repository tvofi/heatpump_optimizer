#!/bin/bash
# exit when a new gate record lands in the wave dir, the driver ends, or a new inbox CMD arrives
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g13
n0=$(ls $W/gates/*.json 2>/dev/null | wc -l); c0=$(grep -c 'CMD' $HOME/comms_loop.log 2>/dev/null); e0=$(grep -c 'EXIT\|GATES-DONE' $HOME/gate_wave.log)
while true; do
  n=$(ls $W/gates/*.json 2>/dev/null | wc -l); c=$(grep -c 'CMD' $HOME/comms_loop.log 2>/dev/null); e=$(grep -c 'EXIT\|GATES-DONE' $HOME/gate_wave.log)
  if [ "$n" != "$n0" ] || [ "$c" != "$c0" ] || [ "$e" != "$e0" ]; then echo "EVENT gates=$n cmds=$c exits=$e"; tail -4 $HOME/gate_wave.log; exit 0; fi
  if ! pgrep -f gate_wave.sh >/dev/null; then echo "DRIVER-GONE"; tail -5 $HOME/gate_wave.log; exit 0; fi
  if ! pgrep -f 'box_comms.sh loop' >/dev/null; then echo "COMMS-LOOP-GONE"; tail -5 $HOME/comms_loop.log; exit 0; fi
  sleep 30
done
