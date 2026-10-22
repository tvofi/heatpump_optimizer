#!/bin/bash
# run.sh <script> <signal> : TERM/INT/HUP the pusher once its stub tree (4 pids) is up; count non-zombie survivors
S=$1; SIG=$2; export REAP_DIR=$(mktemp -d); : > $REAP_DIR/pids
sleep 300 & BY=$!
setsid python3 -c "import signal,os,sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])" bash "$S" "$(dirname "$0")/stub.sh" "$REAP_DIR/b" > $REAP_DIR/out 2>&1 & P=$!
k=0; while [ "$(wc -l < $REAP_DIR/pids)" -lt 4 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k+1)); done
n=$(wc -l < $REAP_DIR/pids)
kill -$SIG $P; sleep 4
pg=$(kill -0 $P 2>/dev/null && echo alive || echo gone)
live=0; for p in $(cat $REAP_DIR/pids); do st=$(ps -o stat= -p $p 2>/dev/null); [ -n "$st" ] && [ "${st:0:1}" != Z ] && live=$((live+1)); done
by=$(kill -0 $BY 2>/dev/null && echo alive || echo dead)
echo "RESULT $(basename $S) sig=$SIG tree=$n pusher=$pg survivors=$live/$n bystander=$by"
for p in $(cat $REAP_DIR/pids) $P $BY; do kill -KILL $p 2>/dev/null; done; rm -rf $REAP_DIR
