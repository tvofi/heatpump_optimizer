#!/usr/bin/env bash
# T3 driver: prescreen.py complete (full net, no early stop, no relaxation) over the owed survivors, by source.
# Command: bash dev/audit/rounds/round11/D3/s1/t3_drive.sh   (from the worktree root)
set -u
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
S=dev/audit/rounds/round11/D3/s1
for src in pre c2 c3c6; do
  echo "SRC $src $(date -u +%FT%TZ)"
  python3 $S/prescreen.py complete --src $src --workers 3 2>&1 | grep -E 'COMPLETE|RESULT|Traceback|Error'
  bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
  bash $HOME/box_comms.sh heartbeat "T3 complete net done: src=$src" >/dev/null 2>&1 || true
done
echo T3-DONE
