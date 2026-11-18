#!/bin/bash
# Milestone watcher: one line per 100 pre-screened sites, per PROGRESS.log line,
# a disk guard (STOP file below 10 GB free) and the chain's exit.
P=/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1
S=$P/state
LOCALCOPY=/Users/timmalmstrom/hpo-orch/r10s6/r11/local-reports/D3-s1.REPORT.json
last=$(( $(ls $S/results/pre | wc -l) / 100 ))
seen=$(wc -l < $P/r2/PROGRESS.log 2>/dev/null || echo 0)
while true; do
  n=$(ls $S/results/pre | wc -l | tr -d ' ')
  b=$(( n / 100 ))
  if [ "$b" -gt "$last" ]; then
    last=$b
    k=$(grep -l '"verdict": "KILLED"' $S/results/pre/*.json | wc -l | tr -d ' ')
    echo "MILESTONE pre=$n killed=$k free=$(df -g / | tail -1 | awk '{print $4}')G load1=$(sysctl -n vm.loadavg | awk '{print $2}')"
    cp $P/REPORT.json $LOCALCOPY 2>/dev/null
  fi
  cur=$(wc -l < $P/r2/PROGRESS.log)
  if [ "$cur" -gt "$seen" ]; then sed -n "$((seen+1)),${cur}p" $P/r2/PROGRESS.log | grep -v '^slot\|^/tmp' ; seen=$cur; fi
  free=$(df -g / | tail -1 | awk '{print $4}')
  if [ "$free" -lt 10 ] && [ ! -f $S/STOP ]; then touch $S/STOP; echo "DISKSTOP free=${free}G STOP written"; fi
  if ! pgrep -f "r2/chain_" > /dev/null; then echo "CHAIN-GONE pre=$n"; fi
  sleep 60
done
