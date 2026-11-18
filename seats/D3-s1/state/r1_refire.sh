#!/usr/bin/env bash
# R1 on a re-fire: baselines, null control, positive control; then checkpoint.
export PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
S=dev/audit/rounds/round11/D3/s1
python3 $S/prescreen.py baseline --workers 4 > $S/state/box-baseline-r2.out 2>&1; echo "baseline rc=$?"
python3 $S/prescreen.py null > $S/state/box-null-r2.out 2>&1; echo "null rc=$?"; tail -3 $S/state/box-null-r2.out
rm -rf "${S:?}/state/results/posctl-D3-top6-r2"
python3 $S/prescreen.py run --anchors $S/posctl_anchors.txt --sub posctl-D3-top6-r2 > $S/state/box-posctl-r2.out 2>&1; echo "posctl rc=$?"; tail -3 $S/state/box-posctl-r2.out
bash $HOME/box_comms.sh checkpoint D3-s1 $PWD/$S >/dev/null 2>&1 || echo "checkpoint failed"
echo R1-DONE
