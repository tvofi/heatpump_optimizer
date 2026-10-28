#!/bin/bash
set -uo pipefail
. "$(dirname -- "$0")/pr_args.sh"; pr_exit_trap
_push=$1; R=; WT=; BR=; B=$2; ISSUES=
push_app() { # <tail count>: the push, asynchronously into its log, filtered to its REFUSE/PUSHED lines
  PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} bash "$_push" $R "$WT" "$BR" "$B" ${ISSUES:-} > "$B.push.log" 2>&1 &
  wait $! || :  # a stop signal interrupts the wait; the EXIT trap reaps the push (R10-PUSHER-REAP)
  grep -E 'REFUSE|PUSHED' "$B.push.log" | tail -"$1" | cut -c1-200
}
push_app 1
echo RESULT
