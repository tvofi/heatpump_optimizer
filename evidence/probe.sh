#!/bin/bash
# usage: probe.sh <prepr copy> <signal> <target: parent|pgrp>
P=$(dirname "$0"); PREPR=$1; SIG=$2; TGT=$3
: > "$P/sleeper.pid"
cat > "$P/drv.sh" <<EOD
#!/bin/bash
cd "$P/r" || exit 9
eval "\$(awk '/^rc=0\$/{exit} {print}' '$PREPR')"
uname() { printf 'Linux\n'; }
if [ -n "${PROBE_TRAPS:-}" ]; then trap "echo EXIT-trap-ran" EXIT; trap "exit 130" INT; trap "exit 143" TERM; trap "exit 129" HUP; fi
export PREPR_RECORD="$P/sleeper.sh"
X=\$(closures_line b18052f664039d36da73ef745a2a8423f82d2c46)
echo "drv finished: \$X"
EOD
setsid bash "$P/drv.sh" > "$P/drv.out" 2>&1 & d=$!
for i in $(seq 1 300); do [ -s "$P/sleeper.pid" ] && break; sleep 0.1; done
s=$(cat "$P/sleeper.pid"); [ -n "$s" ] || { echo "RESULT recorder-never-started"; cat "$P/drv.out"; kill -- -$d; exit 2; }
sleep 0.5
if [ "$TGT" = parent ]; then kill -$SIG $d; else kill -$SIG -- -$d; fi
alive=1; for i in $(seq 1 50); do kill -0 $s 2>/dev/null || { alive=0; break; }; sleep 0.1; done
echo "RESULT parent_alive_after_5s=$(kill -0 $d 2>/dev/null && echo 1 || echo 0) prepr=$(basename $PREPR) sig=$SIG target=$TGT recorder_alive_after_5s=$alive"
[ $alive = 1 ] && kill $s 2>/dev/null; pkill -f "$P/drv.sh" 2>/dev/null; true
