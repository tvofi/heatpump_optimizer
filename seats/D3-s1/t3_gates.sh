#!/usr/bin/env bash
# T3 tail: the full gate (fullgate.py, T2's procedure) down the complete-net survivors, by consequence:
# behaviour-gating guards and constants first, then comparison/operator mutants.
# Command: bash dev/audit/rounds/round11/D3/s1/t3_gates.sh   (from the worktree root)
set -u
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub
S=dev/audit/rounds/round11/D3/s1
for k in 5e8d48eff7e4fa8d 121362d48b408236 3885e472b8297a90 460217277822d5bd 65f121eb047174ad 050fdc4a20eba212 0c3e91a6a349409a 0911281eca895664 22b5ec8775d5bd50 2719aef4cbb8b464 c38d53ab787ddbfa a4b00ac3ca662eec a0b3b28854fa500c 95779f9d6d71c50d 5cc84148fa68bda1; do
  [ -f $S/state/gates/$k.json ] && { echo "SKIP done $k"; continue; }
  while [ -f $HOME/.boxcomms-r11-D3-top6/stop ] || [ -f $S/state/STOP ]; do echo "STOPPED waiting"; sleep 240; done
  echo "START $k $(date -u +%FT%TZ)"
  python3 $S/fullgate.py run --src complete --key $k 2>&1 | grep -E 'RESULT|VERDICT|REFUSE|Error'
  bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
  bash $HOME/box_comms.sh heartbeat "T3 gate done: $k" >/dev/null 2>&1 || true
done
echo GATES-DONE
