#!/bin/bash
# Block until the next D3-s1 event: a new PROGRESS.log line, a 100-site
# pre-screen milestone, a disk guard trip, or no chain process left. Prints it, exits.
# Also refreshes the local report copy at each milestone.
P=/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1
S=$P/state
SUB=${1:-pre}
MAX=${2:-0}; T0=$(date +%s)
cnt() { ls $S/results/$SUB 2>/dev/null | wc -l | tr -d ' '; }
last=$(( $(cnt) / 100 ))
seen=$(wc -l < $P/r2/PROGRESS.log)
while true; do
  n=$(cnt)
  free=$(df -g / | tail -1 | awk '{print $4}')
  if [ $(( n / 100 )) -gt "$last" ]; then
    k=$(grep -l '"verdict": "KILLED"' $S/results/$SUB/*.json | wc -l | tr -d ' ')
    echo "MILESTONE $SUB=$n killed=$k free=${free}G load1=$(sysctl -n vm.loadavg | awk '{print $2}')"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) MILESTONE $SUB=$n killed=$k free=${free}G" >> $P/r2/PROGRESS.log
    exit 0
  fi
  cur=$(wc -l < $P/r2/PROGRESS.log)
  if [ "$cur" -gt "$seen" ]; then
    new=$(sed -n "$((seen+1)),${cur}p" $P/r2/PROGRESS.log | grep -v '^taken\|^released\|^slot')
    seen=$cur
    if [ -n "$new" ]; then echo "$new"; exit 0; fi
  fi
  if [ "$free" -lt 10 ] && [ ! -f $S/STOP ]; then touch $S/STOP; echo "DISKSTOP free=${free}G"; exit 0; fi
  if ! pgrep -f "D3/s1/r2/chain_|r2/chain_|prescreen.py" > /dev/null; then echo "NO-CHAIN $SUB=$n"; exit 0; fi
  if [ "$MAX" -gt 0 ] && [ $(( $(date +%s) - T0 )) -ge "$MAX" ]; then echo "QUIET pre=$n free=${free}G load1=$(sysctl -n vm.loadavg | awk "{print \$2}")"; exit 0; fi
  sleep 30
done
