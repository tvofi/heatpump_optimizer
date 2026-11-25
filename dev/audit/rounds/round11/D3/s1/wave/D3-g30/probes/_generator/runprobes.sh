#!/bin/bash
# run every probe from the clean baseline worktree $HOME/probe-base (never the gate's tree)
SP=/tmp/claude-0/-home-user-heatpump-optimizer/45093cdc-18e6-5d18-aa26-c41214203af5/scratchpad
P=dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes
mkdir -p $HOME/probe-base/$P $SP/clean
cp $HOME/audit-r11-D3-s1/$P/probe_*.py $HOME/probe-base/$P/
cd $HOME/probe-base
[ -z "$(git status --short custom_components)" ] || { echo "probe-base not clean"; exit 1; }
for f in $P/probe_*.py; do k=$(basename $f .py); k=${k#probe_}
  PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 $f > $SP/clean/$k.out 2>&1
  grep '^RESULT' $SP/clean/$k.out | grep -vE 'thread_factor|load1|swapins' | diff -q - <(grep '^RESULT' $SP/runs/$k.out | grep -vE 'thread_factor|load1|swapins') >/dev/null && echo "same $k" || echo "DIFF $k"
done
