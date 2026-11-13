#!/bin/bash
# step-order repro: scratch clone, detached at $1, origin/main = $2; run the two run: commands in the order $3
set -u
SRC=/home/user/heatpump_optimizer; H=$1; M=$2; ORDER=$3
S=$(mktemp -d); git init -q --bare "$S/o.git"
git -C "$SRC" push -q "$S/o.git" "$M:refs/heads/main" "$H:refs/heads/pr"
git clone -q "$S/o.git" "$S/c" 2>/dev/null; cd "$S/c" && git checkout -q --detach "$H"
echo "order=$ORDER head=$H origin/main=$(git rev-parse origin/main)"
echo "loop-file commits head..main: $(git rev-list --count $H..origin/main -- tools/audit/seat/tick_loop.sh tools/audit/seat/cloud_relay.sh)"
for s in $ORDER; do
  echo "--- before $s HEAD=$(git rev-parse HEAD)"
  if [ $s = outside ]; then python3 -I tools/pr/outside.py --self-test 2>&1 | tail -1; echo "rc=${PIPESTATUS[0]}"
  else env -u BASH_ENV bash tools/audit/seat/tick_loop.sh --self-test 2>&1 | tail -1; echo "rc=${PIPESTATUS[0]}"; fi
done
echo "--- end HEAD=$(git rev-parse HEAD)"
rm -rf "$S"
