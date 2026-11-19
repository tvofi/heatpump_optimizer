#!/usr/bin/env bash
# D3-top6 local re-run, phase A: wait for the traced baselines, run the prescreen null and
# positive controls (marker commit HEAD^1 = baseline), checkpoint, then reset HEAD to the
# baseline and run T2: the full-gate null control and the six top survivors, in brief order.
set -u
. /Users/timmalmstrom/hpo-orch/r10s6/r11/D3-top6-env.sh
cd "$W" || exit 2
LOG=$P/state/phase_a.log
while kill -0 "${1:-0}" 2>/dev/null; do sleep 20; done
echo "$(date -u +%FT%TZ) baselines done; load1 $(sysctl -n vm.loadavg | awk '{print $2}')" >> $LOG
python3 "$P/prescreen.py" null > "$P/state/null-D3top6.out" 2>&1
python3 "$P/prescreen.py" run --anchors "$P/posctl_anchors.txt" --sub posctl-D3-top6-local --workers 2 > "$P/state/posctl-D3top6-local.out" 2>&1
echo "$(date -u +%FT%TZ) controls: $(tr '\n' ' ' < $P/state/null-D3top6.out) | $(grep -c KILLED $P/state/posctl-D3top6-local.out) of 2 posctl KILLED" >> $LOG
bash "$BC" heartbeat "R1 local: baselines re-taken; controls $(tr '\n' ' ' < $P/state/null-D3top6.out) posctl $(grep -c KILLED $P/state/posctl-D3top6-local.out)/2 KILLED" >/dev/null 2>&1
bash "$BC" checkpoint D3-s1 "$P" >/dev/null 2>&1
if ! grep -q "null_verdict=LIVES" "$P/state/null-D3top6.out" || [ "$(grep -c KILLED $P/state/posctl-D3top6-local.out)" != 2 ]; then
  echo "$(date -u +%FT%TZ) CONTROLS FAILED: halting" >> $LOG; exit 5; fi
git reset -q "$BASE"
[ "$(git rev-parse HEAD)" = "$BASE" ] || { echo "HEAD not baseline" >> $LOG; exit 6; }
bash "$P/gate_chain.sh" null pre:fb16c7b0cbbfc63d pre:4b3795aece73ba73 pre:bdcf7589b0a0a6df c2:0e172028a23d9372 c2:d931ab195b940b0c c2:8e82d7a0b3617003
echo "$(date -u +%FT%TZ) T2 done" >> $LOG
