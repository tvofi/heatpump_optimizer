#!/bin/bash
# attack.sh <D> <arm: control|func>: the caller's environment, plus (func) one exported function named exec
D=$1; arm=$2; V=$D/victim-$arm.git; rm -rf "$V"; git init -q --bare "$V"
if [ "$arm" = func ]; then
  exec() { if [ "${1:-}" = /usr/bin/env ]; then echo "re-exec shadowed: $*" >> "$D/shadow-$arm.log"; return 0; fi; builtin exec "$@"; }
  export -f exec
fi
export D HPO_HEARTBEAT_REMOTE=$V TICK_RC=1
cd "$D"
bash "$D/src/tools/audit/seat/tick_loop.sh" --self-test > "$D/out-$arm.txt" 2>&1; echo "rc=$?" >> "$D/out-$arm.txt"
echo "victim refs after ($arm):"; git -C "$V" for-each-ref --format='%(refname) %(contents:subject)' || true
