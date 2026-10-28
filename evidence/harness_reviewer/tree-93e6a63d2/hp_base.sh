#!/bin/bash
set -uo pipefail
_push=$1; R=; WT=; BR=; B=$2; ISSUES=
push_app() { # <tail count>: the push, filtered to its REFUSE/PUSHED lines
  PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} \
    bash "$_push" $R "$WT" "$BR" "$B" ${ISSUES:-} 2>&1 \
    | grep -E 'REFUSE|PUSHED' | tail -"$1" | cut -c1-200
}
push_app 1
echo RESULT
