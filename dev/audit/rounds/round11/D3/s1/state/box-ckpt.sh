#!/usr/bin/env bash
# Box D3R: checkpoint the report dir after every 100 new pre results; refuse (touch STOP) below 10 GB free.
D=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1; last=-1
while pgrep -f box-u1.sh >/dev/null || [ "$1" = once ]; do
  n=$(ls $D/state/results/pre | wc -l); free=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9)
  [ "$free" -lt 10 ] && { touch $D/state/STOP; echo "DISK LOW ${free}G: STOP"; }
  if [ $((n/100)) -ne $((last/100)) ]; then bash $HOME/box_comms.sh checkpoint D3-s1 $D >/dev/null 2>&1; bash $HOME/box_comms.sh heartbeat "U1 pre results=$n free=${free}G load1=$(cut -d' ' -f1 /proc/loadavg)" >/dev/null 2>&1; echo "CKPT pre=$n free=${free}G $(date -u +%FT%TZ)"; last=$n; fi
  [ "$1" = once ] && break; sleep 120
done
