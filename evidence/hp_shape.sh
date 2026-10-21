#!/bin/bash
set -uo pipefail
_push=$1
PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} bash "$_push" 2>&1 | grep -E 'REFUSE|PUSHED' | tail -1 | cut -c1-200
echo "RESULT"
