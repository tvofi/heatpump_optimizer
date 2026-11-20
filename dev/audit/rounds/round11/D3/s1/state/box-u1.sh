#!/usr/bin/env bash
# Box D3R launcher: re-drive C3C6 M22, then U1 (every not-yet-driven unpinned inventory mutant) on the fast net, 4 workers.
set -u
cd "$HOME/audit-r11-D3-s1"
export PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1
PY=$HOME/venv-ci/bin/python3; D=dev/audit/rounds/round11/D3/s1; P=$D/prescreen.py; S=$D/state
echo "START $(date -u +%FT%TZ) nproc=$(nproc) load1=$(cut -d' ' -f1 /proc/loadavg)"
$PY $P run --mutants $D/c3c6_mutants.json --sub c3c6 --workers 1 > $S/box-m22.out 2>&1; echo "m22 rc=$? $(date -u +%FT%TZ)"
$PY $P run --anchors $S/u1_keys.txt --sub pre --workers 4 > $S/box-u1.out 2>&1; echo "u1 rc=$? $(date -u +%FT%TZ)"
echo DONE
