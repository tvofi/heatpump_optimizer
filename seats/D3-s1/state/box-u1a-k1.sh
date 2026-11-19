#!/usr/bin/env bash
# Box D3-u1a K1: pre-screen this box's 309 keys on the fast net, 4 workers; checkpoint every 25 driven; STOP below 10 GB free.
set -u
cd "$HOME/audit-r11-D3-s1"
export PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
PY=$HOME/venv-ci/bin/python3; D=dev/audit/rounds/round11/D3/s1; S=$D/state
KEYS=$S/keys-D3-u1a.txt
mine() { comm -12 <(ls $S/results/pre | sed 's/\.json$//' | sort) <(sort $KEYS) | wc -l; }
echo "START $(date -u +%FT%TZ) load1=$(cut -d' ' -f1 /proc/loadavg) done=$(mine)"
$PY $D/prescreen.py run --anchors $KEYS --sub pre --workers 4 > $S/u1a-k1.out 2>&1 &
PID=$!; last=$(mine)
while kill -0 $PID 2>/dev/null; do
  sleep 60
  n=$(mine); free=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9)
  [ "$free" -lt 10 ] && { touch $S/STOP; echo "DISK LOW ${free}G: STOP $(date -u +%FT%TZ)"; }
  if [ $((n/25)) -ne $((last/25)) ]; then bash $HOME/box_comms.sh checkpoint D3-s1 $HOME/audit-r11-D3-s1/$D >/dev/null 2>&1; bash $HOME/box_comms.sh heartbeat "K1 pre $n/309 free=${free}G load1=$(cut -d' ' -f1 /proc/loadavg)" >/dev/null 2>&1; echo "CKPT $n/309 free=${free}G $(date -u +%FT%TZ)"; last=$n; fi
done
wait $PID; echo "k1 rc=$? done=$(mine) $(date -u +%FT%TZ)"
bash $HOME/box_comms.sh checkpoint D3-s1 $HOME/audit-r11-D3-s1/$D >/dev/null 2>&1; echo "FINAL CKPT rc=$?"
