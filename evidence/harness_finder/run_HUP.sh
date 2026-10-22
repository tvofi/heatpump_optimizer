#!/bin/bash
# run_train.sh <train.sh> : TERM the train launcher (the pid its pidfile names) once the train's tree is up
T=$1; export REAP_DIR=$(mktemp -d) STUB=$(dirname "$0")/../stub.sh HPO_STATE_DIR=$(dirname "$0")/hs; : > $REAP_DIR/pids
st=$REAP_DIR/state
setsid python3 -c "import signal,os,sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])" bash "$T" --queue $(dirname "$0")/q.json --repo o/r --state-dir $st --checkout $(dirname "$0")/C > $REAP_DIR/out 2>&1 & P=$!
k=0; while [ "$(wc -l < $REAP_DIR/pids)" -lt 5 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k+1)); done
n=$(wc -l < $REAP_DIR/pids); pf=$(cat $st/train.pid 2>/dev/null)
kill -HUP "$pf"; sleep 4
live=0; for p in $(cat $REAP_DIR/pids); do s=$(ps -o stat= -p $p 2>/dev/null); [ -n "$s" ] && [ "${s:0:1}" != Z ] && live=$((live+1)); done
echo "RESULT train.sh HUP(pidfile pid $pf == launcher $P: $([ "$pf" = "$P" ] && echo yes || echo no)) tree=$n launcher=$(kill -0 $P 2>/dev/null && echo alive || echo gone) pidfile=$([ -f $st/train.pid ] && echo present || echo removed) survivors=$live/$n"
for p in $(cat $REAP_DIR/pids) $P; do kill -KILL $p 2>/dev/null; done; rm -rf $REAP_DIR
