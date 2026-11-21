#!/usr/bin/env bash
# Box D3R launcher (Linux, 4 cores): re-take traced baselines, capture trace, null and positive controls on this machine.
set -u
cd "$HOME/audit-r11-D3-s1"
export PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
PY=$HOME/venv-ci/bin/python3; P=dev/audit/rounds/round11/D3/s1/prescreen.py; S=dev/audit/rounds/round11/D3/s1/state
echo "START $(date -u +%FT%TZ) nproc=$(nproc) load1=$(cut -d' ' -f1 /proc/loadavg)"
$PY $P baseline --workers 4 > $S/box-baseline.out 2>&1; echo "baseline rc=$? $(date -u +%FT%TZ)"
$PY $P trace-capture > $S/box-trace-cap.out 2>&1; echo "trace-capture rc=$? $(date -u +%FT%TZ)"
$PY $P null > $S/box-null.out 2>&1; echo "null rc=$? $(date -u +%FT%TZ)"; tail -3 $S/box-null.out
$PY $P run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl --workers 2 > $S/box-posctl.out 2>&1; echo "posctl rc=$? $(date -u +%FT%TZ)"; tail -3 $S/box-posctl.out
echo "DONE $(date -u +%FT%TZ) load1=$(cut -d' ' -f1 /proc/loadavg)"
