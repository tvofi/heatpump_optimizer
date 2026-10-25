#!/bin/bash
# same probe for the unbounded round-1 head: survivors are processes whose pgid was the killed group's
# or that descend from it (session = the caller's); count by the unique tmp dir the self-test made.
s=$1; t=$2
python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp("bash", sys.argv[1:])' bash "$s" --self-test >/dev/null 2>&1 & g=$!
sleep "$t"; ps -eo pid,ppid,pgid,sid,args > /tmp/claude-0/ps-b.txt
d=$(grep -o '/tmp/tmp\.[A-Za-z0-9]*/' /tmp/claude-0/ps-b.txt | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
echo "before kill: pgid $g has $(pgrep -g $g | wc -l) processes; fixture dir $d"
kill -KILL -- -$g; wait $g 2>/dev/null; sleep 3
echo "3 s after the group KILL: pgid $g has $(pgrep -g $g | wc -l) live; processes naming the fixture dir: $(ps -eo args | grep -c "$d" | awk '{print $1-1}')"
ps -eo pid,pgid,sid,etimes,args | grep "$d" | grep -v grep | cut -c1-150
