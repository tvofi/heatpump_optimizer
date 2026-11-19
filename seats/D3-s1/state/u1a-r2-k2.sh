#!/usr/bin/env bash
# box D3-u1a re-fire: K2 full net on the slice's pre-screen survivors (done keys skipped)
cd $HOME/audit-r11-D3-s1; S=dev/audit/rounds/round11/D3/s1/state
for d in /tmp/d3s1-workers/w*; do git -C $d checkout -q -- . ; done
echo "K2R START $(date -u +%FT%TZ) load1=$(cut -d' ' -f1 /proc/loadavg)"
PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1 $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/prescreen.py complete --src pre --keys $S/keys-D3-u1a-surv.txt --workers 4
echo "K2R rc=$? $(date -u +%FT%TZ) load1=$(cut -d' ' -f1 /proc/loadavg)"
