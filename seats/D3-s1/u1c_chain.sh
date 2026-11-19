#!/bin/bash
# box D3-u1c driver chain: K1 pre-screen then K2 full net; resumable (done keys skipped)
cd /root/audit-r11-D3-s1
S=dev/audit/rounds/round11/D3/s1
export PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
PY=/root/venv-ci/bin/python3
clean() { for i in 0 1 2 3 4 5 6 7; do git worktree remove --force /tmp/d3s1-workers/w$i 2>/dev/null; rm -rf /tmp/d3s1-workers/w$i; done; git worktree prune; }
clean
echo "$(date -u +%FT%TZ) K1 start" >> $S/state/u1c-chain.log
$PY $S/prescreen.py run --anchors $S/state/keys-D3-u1c.txt --sub pre --workers 4 >> $S/state/u1c-k1.out 2>&1
echo "$(date -u +%FT%TZ) K1 exit $?" >> $S/state/u1c-chain.log
[ -e $S/state/STOP ] && exit 0
$PY $S/u1c_slice.py --write-surv > $S/state/u1c-slice-k1.out 2>&1
clean
echo "$(date -u +%FT%TZ) K2 start $(wc -l < $S/state/keys-D3-u1c-surv.txt)" >> $S/state/u1c-chain.log
$PY $S/prescreen.py complete --src pre --keys $S/state/keys-D3-u1c-surv.txt --workers 4 >> $S/state/u1c-k2.out 2>&1
echo "$(date -u +%FT%TZ) K2 exit $?" >> $S/state/u1c-chain.log
clean
echo "$(date -u +%FT%TZ) CHAIN DONE" >> $S/state/u1c-chain.log
