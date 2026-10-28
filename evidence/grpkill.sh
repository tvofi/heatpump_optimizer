#!/bin/bash
# reviewer's own instrument: SIGKILL a self-test's caller's whole process group (supervisor
# and watchdog both), then count the processes of the self-test that survive.
# usage: grpkill.sh <script> <seconds before the kill>
s=$1; t=$2
python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp("bash", sys.argv[1:])' bash "$s" --self-test >/dev/null 2>&1 & g=$!
sleep "$t"
echo "before kill: processes in pgid $g: $(pgrep -g $g | wc -l); bound sessions: $(ps -eo pid,sid,pgid,args | awk -v g=$g '$3==g && /PR_BOUND|import os, select/' | wc -l)"
ps -eo pid,ppid,pgid,sid,args > /tmp/claude-0/ps-before.txt
kill -KILL -- -$g; wait $g 2>/dev/null; sleep 3
# survivors: any process whose ancestry included the self-test: find by session ids created under it
sids=$(awk -v g=$g 'NR>1 && $2==g {print $1}' /tmp/claude-0/ps-before.txt)   # children of the supervisor
echo "sessions led by the supervisor's children: $sids"
for sid in $sids; do n=$(ps -eo sid= | awk -v s=$sid '$1==s' | wc -l); echo "session $sid: $n live process(es) 3 s after the group KILL"; ps -eo pid,sid,etimes,args | awk -v s=$sid '$2==s' | head -5; done
