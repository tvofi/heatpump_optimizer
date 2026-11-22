# waitnext.sh: return when the gated count in the wave dir grows, or the run exits
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g01
n0=$(ls $W/gates/*.json | grep -vc null.json)
while :; do
  n=$(ls $W/gates/*.json | grep -vc null.json)
  [ "$n" -gt "$n0" ] && break
  grep -q 'RUN-EXIT' $HOME/logs/run.log && break
  pgrep -f 'gate_wave.sh run' >/dev/null || { echo "RUN PROCESS GONE"; break; }
  sleep 60
done
sleep 20; tail -4 $HOME/logs/run.log; cat $HOME/logs/loop.log | tail -3
