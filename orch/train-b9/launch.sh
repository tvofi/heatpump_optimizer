#!/bin/bash
S=~/hpo-orch/train-b9
until grep -q TRAIN_RC= ~/hpo-orch/train-b8b/train.log && ! pgrep -f merge_train.py >/dev/null; do sleep 60; done
cd ~/heatpump_optimizer && git fetch -q && git merge -q --ff-only origin/main
export PATH=$PWD/tools/audit/seat/shims:$PATH
seat-python3 tools/audit/seat/queue_pre_flight.py --repo tvofi/heatpump_optimizer --checkout ~/heatpump_optimizer $S/queue.json > $S/preflight.txt 2>&1
tools/audit/seat/train.sh --queue $S/queue.json --repo tvofi/heatpump_optimizer --state-dir $S --checkout ~/heatpump_optimizer --mandate "mandate 6175172275" --ignore-red nightly-status --ignore-red delivery-status --skip-bad --overlap
