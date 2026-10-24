#!/bin/bash
# Relay mrbatch probes (no --confirm: the coordinator runs bus.sh confirm). Writes to coord-loop.log.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
LOG=$D/coord-loop.log
DONE=$D/mrbatch-relay.done
touch "$DONE"
export PATH="$R/tools/audit/seat/shims:$PATH"
cd "$R" || exit 1
TARGETS="2571 56cafa79188c2e5e20f1b4065ee02f3b cb48de247b39b47ffe9e010689f8ff4f971b7e32
2580 59942ae7eea0b6867213ae5094c34126 a54aed8b9e756aaa47ea18e9a13bf33a06878a0b
2578 054b1614a42cb0e88d11ee0686849089 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20
2569 f516a337d7a8b35ec4420848109661f3 8c008227a25192fc542bca64abbd4098a2862d1a"
while [ ! -f "$D/coord-loop.stop" ]; do
  refs=$(git ls-remote origin 'refs/heads/probe/rev-*' 2>/dev/null | cut -f2)
  echo "$TARGETS" | while read pr nonce head; do
    [ -z "$pr" ] && continue
    grep -q "^$pr $nonce" "$DONE" 2>/dev/null && continue
    if echo "$refs" | grep -q "probe/rev-$pr-${nonce:0:8}\$"; then
      out=$(bash tools/audit/seat/cloud_relay.sh "$pr" "$nonce" "$head" 2>&1); rc=$?
      if [ $rc -eq 0 ]; then
        rev=$(echo "$out" | grep -o 'relayed refs/heads/probe/[^ ]* [0-9a-f]\{40\}' | awk '{print $3}')
        echo "$(date -u +%H:%M:%SZ) MRBATCH-RELAYED $pr nonce=$nonce head=${head:0:8} review_commit=${rev:-unknown}" >> "$LOG"
        echo "$pr $nonce" >> "$DONE"
      else
        echo "$(date -u +%H:%M:%SZ) MRBATCH-REFUSED $pr nonce=$nonce head=${head:0:8} rc=$rc: $(echo "$out" | tail -2 | tr '\n' ' ')" >> "$LOG"
        echo "$pr $nonce" >> "$DONE"
      fi
    fi
  done
  sleep 120
done
