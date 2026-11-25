#!/bin/bash
# run a probe from the clean baseline worktree $HOME/probe-tree (never from the gate's tree)
k=$1; R=dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_$k.py
mkdir -p $HOME/probe-tree/$(dirname $R); cp $HOME/audit-r11-D3-s1/$R $HOME/probe-tree/$R
cd $HOME/probe-tree && PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 $R
