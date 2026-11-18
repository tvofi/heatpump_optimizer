#!/usr/bin/env bash
# T3 driver: full net (prescreen.py complete, no early stop) on the owed survivors, by source; checkpoint every 20 min and after each source.
# Command: bash dev/audit/rounds/round11/D3/s1/t3_drive.sh   (from the worktree root)
set -u
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub
S=dev/audit/rounds/round11/D3/s1
( while sleep 1200; do bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1; df -h $HOME | tail -1; done ) & CK=$!
for src in pre c2 c3c6; do
  while [ -f $S/state/STOP ]; do sleep 240; done
  echo "START $src $(date -u +%FT%TZ)"
  python3 $S/prescreen.py complete --src $src --workers 4 > $S/state/t3-$src.out 2>&1; echo "DONE $src rc=$? $(date -u +%FT%TZ)"
  bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
  bash $HOME/box_comms.sh heartbeat "T3 full net done: $src" >/dev/null 2>&1 || true
done
kill $CK
echo T3-DONE
