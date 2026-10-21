#!/bin/bash
set -uo pipefail
. $W/wt/tools/audit/seat/pr_args.sh; pr_signal_traps
_push=$1
bash "$_push" > log 2>&1 &
wait $!
echo RESULT
