# $1 = tree, $2 = mode (real|base)
r=$(mktemp); python3 -I $(dirname $0)/batch_swallow.py $r $2 $1/tools/audit/seat & p=$!
for i in $(seq 100); do grep -q UNWINDING $r 2>/dev/null && break; sleep 0.1; done
sleep 0.3; kill -TERM $p; wait $p; echo "== mode=$2"; cat $r
