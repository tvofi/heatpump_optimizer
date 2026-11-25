#!/bin/bash
# box D3-u1c checkpoint loop: checkpoint every 25 pre-screened keys of this box, after every full-net result, and at chain end
D=/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1
lastp=-1; lastc=-1
while true; do
  read p c < <(cd $D && python3 -c "import os;k=[l.strip() for l in open('state/keys-D3-u1c.txt') if l.strip()];print(sum(os.path.exists('state/results/pre/'+x+'.json') for x in k), sum(os.path.exists('state/results/complete/'+x+'.json') for x in k))")
  done=0; grep -q 'CHAIN DONE' $D/state/u1c-chain.log 2>/dev/null && done=1
  if [ $lastp -lt 0 ] || [ $((p/25)) -gt $((lastp/25)) ] || [ $c -gt $lastc ] || [ $done = 1 ]; then
    av=$(df -BG --output=avail /root | tail -1 | tr -d ' ')
    bash /root/box_comms.sh checkpoint D3-s1 $D >/dev/null 2>&1; rc=$?
    echo "$(date -u +%FT%TZ) pre=$p complete=$c avail=$av load=$(cut -d' ' -f1 /proc/loadavg) checkpoint_rc=$rc" >> $D/state/u1c-ckloop.log
    lastp=$p; lastc=$c
  fi
  [ $done = 1 ] && exit 0
  sleep 120
done
