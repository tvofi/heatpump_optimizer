#!/usr/bin/env bash
# D3-top6 T2/T3 driver (local macOS re-run): full gate, one mutant at a time, via fullgate.py.
# Usage: gate_chain.sh <src:key> [<src:key> ...]   (or "null" for the comment-only null control)
# Each gate: HEAD must be the baseline (fullgate.py refuses otherwise); after each, the report
# directory is checkpointed to refs/heads/handoff-wip/finder-r11-D3-top6 through box_comms.sh.
set -u
. /Users/timmalmstrom/hpo-orch/r10s6/r11/D3-top6-env.sh
cd "$W" || exit 2
for item in "$@"; do
  if [ -f "$P/state/STOP" ]; then echo "STOP present; halting before $item"; break; fi
  if [ "$item" = null ]; then
    out=$(python3 "$P/fullgate.py" null 2>&1)
  else
    out=$(python3 "$P/fullgate.py" run --src "${item%%:*}" --key "${item#*:}" 2>&1)
  fi
  echo "$(date -u +%FT%TZ) GATE $item :: $(echo "$out" | tr '\n' ' ')" | tee -a "$P/state/gates/chain.log"
  bash "$BC" heartbeat "gate done: $item $(echo "$out" | grep -E '^VERDICT|gate_rc' | tr '\n' ' ')" >/dev/null 2>&1 || true
  bash "$BC" checkpoint D3-s1 "$P" >/dev/null 2>&1 || echo "checkpoint failed after $item" >> "$P/state/gates/chain.log"
  df -h "$HOME" | tail -1 >> "$P/state/gates/chain.log"
done
