#!/bin/bash
# reviewer's own runner: one script under one zone, HASTUB_TZ and TZ both set; "gate" = TZ=UTC, HASTUB_TZ unset
# usage: runz.sh <worktree> <script> <zone> <outlog>
wt=$1; s=$2; z=$3; out=$4
cd "$wt" || exit 9
if [ "$z" = gate ]; then env -u HASTUB_TZ TZ=UTC PYTHONPATH=tests/hastub timeout 3000 python3 "$s" >"$out" 2>&1
else HASTUB_TZ="$z" TZ="$z" PYTHONPATH=tests/hastub timeout 3000 python3 "$s" >"$out" 2>&1; fi
echo "rc=$?" >>"$out"
