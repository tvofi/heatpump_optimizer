#!/bin/bash
# Relays probe/rev-2584-ee2cfa33 to review/2584 (no --confirm: coordinator runs bus.sh confirm). Logs to coord-loop.log.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
LOG=$D/coord-loop.log
export PATH="$R/tools/audit/seat/shims:$PATH"
cd "$R" || exit 1
PR=2563; NONCE=7e7638c43a22772a346ee4c2283f8832; HEAD=2f47581094ad66bd76ccfa6efff92aef90036aeb
while true; do
  t=$(git ls-remote origin refs/heads/probe/rev-$PR-${NONCE:0:8} | cut -f1)
  if [ -n "$t" ]; then
    out=$(bash tools/audit/seat/cloud_relay.sh "$PR" "$NONCE" "$HEAD" 2>&1); rc=$?
    tip=$(git ls-remote origin refs/heads/review/$PR | cut -f1)
    if [ $rc -eq 0 ]; then
      echo "$(date -u +%H:%M:%SZ) MRBATCH-RELAYED $PR nonce=$NONCE head=${HEAD:0:8} review_tip=${tip:0:8}" >> "$LOG"
    else
      echo "$(date -u +%H:%M:%SZ) MRBATCH-REFUSED $PR nonce=$NONCE head=${HEAD:0:8} rc=$rc review_tip=${tip:0:8}: $(echo "$out" | tail -2 | tr '\n' ' ')" >> "$LOG"
    fi
    exit 0
  fi
  sleep 60
done
