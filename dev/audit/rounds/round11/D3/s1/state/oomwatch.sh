#!/bin/bash
# oomwatch.sh <out>: append every cgroup OOM kill dmesg reports, with its UTC time, to <out> (dedup by kernel timestamp)
B=$(python3 -c "import time;print(time.time()-float(open('/proc/uptime').read().split()[0]))")
while true; do
  dmesg | grep "Killed process" | while read -r l; do
    t=$(echo "$l" | sed 's/^\[ *\([0-9.]*\)\].*/\1/'); grep -q "^$t " "$1" 2>/dev/null && continue
    echo "$t $(date -u -d @$(python3 -c "print(int($B+$t))") +%FT%TZ) $l" >> "$1"
  done; sleep 5
done
