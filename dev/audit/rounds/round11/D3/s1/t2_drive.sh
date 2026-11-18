#!/usr/bin/env bash
# T2 driver: full-gate null control, then the six top survivors, one at a time, checkpointing after each.
# Command: bash dev/audit/rounds/round11/D3/s1/t2_drive.sh   (from the worktree root)
set -u
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub
S=dev/audit/rounds/round11/D3/s1
for item in null pre:fb16c7b0cbbfc63d pre:4b3795aece73ba73 pre:bdcf7589b0a0a6df c2:0e172028a23d9372 c2:d931ab195b940b0c c2:8e82d7a0b3617003; do
  k=${item#*:}; [ "$item" = null ] && k=null
  [ -f $S/state/gates/$k.json ] && { echo "SKIP done $k"; continue; }
  while [ -f $HOME/.boxcomms-r11-D3-top6/stop ] || [ -f $S/state/STOP ]; do echo "STOPPED waiting"; sleep 240; done
  echo "START $item $(date -u +%FT%TZ)"
  if [ "$item" = null ]; then python3 $S/fullgate.py null; else python3 $S/fullgate.py run --src ${item%%:*} --key $k; fi 2>&1 | grep -E 'RESULT|VERDICT|REFUSE|Error'
  bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
  bash $HOME/box_comms.sh heartbeat "T2 gate done: $item" >/dev/null 2>&1 || true
done
echo T2-DONE
