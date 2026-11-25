#!/usr/bin/env bash
# Box D3-u1a K2: after K1, full net (prescreen.py complete, no early stop) on this box's K1 survivors, 4 workers;
# checkpoint after each full-net drive; STOP below 10 GB free.
set -u
cd "$HOME/audit-r11-D3-s1"
export PYTHONPATH=tests/hastub
PY=$HOME/venv-ci/bin/python3; D=dev/audit/rounds/round11/D3/s1; S=$D/state
# A container restart can kill a drive mid-mutation and leave a worker tree mutated: start from fresh trees.
for d in /tmp/d3s1-workers/w*; do [ -d "$d" ] && git worktree remove --force "$d"; done; rm -rf /tmp/d3s1-workers; git worktree prune
until grep -q 'FINAL CKPT' $S/u1a-k1-launcher.log; do sleep 30; done
$PY - <<'P' > $S/keys-D3-u1a-surv.txt
import json,os
S='dev/audit/rounds/round11/D3/s1/state'
for k in [l.strip() for l in open(S+'/keys-D3-u1a.txt') if l.strip()]:
    p=f'{S}/results/pre/{k}.json'
    if os.path.exists(p) and json.load(open(p))['verdict']=='SURVIVED': print(k)
P
N=$(grep -c . $S/keys-D3-u1a-surv.txt)
mine() { comm -12 <(ls $S/results/complete 2>/dev/null | sed 's/\.json$//' | sort) <(sort $S/keys-D3-u1a-surv.txt) | wc -l; }
echo "START $(date -u +%FT%TZ) survivors=$N done=$(mine) load1=$(cut -d' ' -f1 /proc/loadavg)"
$PY $D/prescreen.py complete --src pre --keys $S/keys-D3-u1a-surv.txt --workers 4 > $S/u1a-k2.out 2>&1 &
PID=$!; last=$(mine)
while kill -0 $PID 2>/dev/null; do
  sleep 60
  n=$(mine); free=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9)
  [ "$free" -lt 10 ] && { touch $S/STOP; echo "DISK LOW ${free}G: STOP $(date -u +%FT%TZ)"; }
  if [ "$n" -ne "$last" ]; then bash $HOME/box_comms.sh checkpoint D3-s1 $HOME/audit-r11-D3-s1/$D >/dev/null 2>&1; bash $HOME/box_comms.sh heartbeat "K2 full net $n/$N free=${free}G load1=$(cut -d' ' -f1 /proc/loadavg)" >/dev/null 2>&1; echo "CKPT2 $n/$N free=${free}G $(date -u +%FT%TZ)"; last=$n; fi
done
wait $PID; echo "k2 rc=$? done=$(mine)/$N $(date -u +%FT%TZ)"
bash $HOME/box_comms.sh checkpoint D3-s1 $HOME/audit-r11-D3-s1/$D >/dev/null 2>&1; echo "FINAL2 CKPT rc=$?"
