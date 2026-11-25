#!/usr/bin/env bash
# usage: mkres.sh <key> [cpu]   -- runs the step-4 probe in the baseline scratch tree, never the gate's tree
set -u
key=$1; cpu=${2:-Intel(R) Xeon(R) Processor @ 2.30GHz}
S1=dev/audit/rounds/round11/D3/s1
G=$HOME/audit-r11-D3-s1; P=$HOME/probe-tree
rm -rf $P/$S1; mkdir -p $P/dev/audit/rounds/round11/D3; cp -R $G/$S1 $P/$S1
git -C $P diff --quiet HEAD -- custom_components || { echo "probe tree not at baseline"; exit 1; }
while pgrep -f tests/stress.py >/dev/null; do sleep 20; done
cd $P && GATE_CPU="$cpu" PYTHONPATH=tests/hastub PYTHONDONTWRITEBYTECODE=1 /opt/hpo/venv-ci/bin/python3 $S1/wave/D3-g20/tools/mkresult.py $key && cp $P/$S1/wave/D3-g20/results/$key.json $G/$S1/wave/D3-g20/results/
