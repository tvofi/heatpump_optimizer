#!/usr/bin/env bash
# T3 second half: full gate (T2's procedure, fullgate.py) down the full-net survivors by consequence:
# guards first, then the behaviour-gating constant, then the R10 C2 and C3C6 operator mutants. Checkpoint after each.
# Command: bash dev/audit/rounds/round11/D3/s1/t3_gate_drive.sh   (from the worktree root)
set -u
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub
S=dev/audit/rounds/round11/D3/s1
for item in pre:121362d48b408236 pre:050fdc4a20eba212 pre:3885e472b8297a90 pre:460217277822d5bd pre:65f121eb047174ad pre:0c3e91a6a349409a \
            c2:2719aef4cbb8b464 c2:95779f9d6d71c50d c2:a0b3b28854fa500c c2:c38d53ab787ddbfa \
            c3c6:0911281eca895664 c3c6:22b5ec8775d5bd50 c3c6:5cc84148fa68bda1 c3c6:5e8d48eff7e4fa8d c3c6:a4b00ac3ca662eec; do
  k=${item#*:}
  [ -f $S/state/gates/$k.json ] && { echo "SKIP done $k"; continue; }
  while [ -f $HOME/.boxcomms-r11-D3-top6/stop ] || [ -f $S/state/STOP ]; do echo "STOPPED waiting"; sleep 240; done
  [ "$(git rev-parse HEAD)" = 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 ] && [ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "REFUSE tree not clean baseline"; exit 1; }
  echo "START $item $(date -u +%FT%TZ)"
  python3 $S/fullgate.py run --src ${item%%:*} --key $k 2>&1 | grep -E 'RESULT|VERDICT|REFUSE|Error'
  bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
  bash $HOME/box_comms.sh heartbeat "T3 full gate done: $item" >/dev/null 2>&1 || true
done
echo T3G-DONE
