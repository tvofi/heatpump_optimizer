#!/usr/bin/env bash
# box D3-u1a re-fire R1: re-take traced baselines, trace env_drift's capture child, null and positive controls
cd $HOME/audit-r11-D3-s1; S=dev/audit/rounds/round11/D3/s1/state; P=dev/audit/rounds/round11/D3/s1/prescreen.py
export PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1; PY=$HOME/venv-ci/bin/python3
echo "REFIRE START $(date -u +%FT%TZ) nproc=$(nproc) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$(grep -m1 'model name' /proc/cpuinfo|cut -d: -f2)"
$PY $P baseline --workers 4 > $S/u1a-r2-baseline.out 2>&1; echo "baseline rc=$? $(date -u +%FT%TZ)"
$PY $P trace-capture > $S/u1a-r2-trace-cap.out 2>&1; echo "trace-capture rc=$? $(date -u +%FT%TZ)"
$PY $P null > $S/u1a-r2-null.out 2>&1; echo "null rc=$? $(date -u +%FT%TZ)"
$PY $P run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-D3-u1a-r2 > $S/u1a-r2-posctl.out 2>&1; echo "posctl rc=$? $(date -u +%FT%TZ)"
echo "DONE $(date -u +%FT%TZ) load1=$(cut -d' ' -f1 /proc/loadavg)"
