#!/bin/bash
# Drive the head's own prepr-11 row (extracted verbatim, lines 2996-3002) with
# the genuine CLAIMS_INPUTS and with the mutant's renamed entry.
set -u
cd /tmp/rev-2853-1 || exit 2
CLAIMS_GEN=dev/audit/rounds/round4/D6/claims.py
st(){ if [ "$1" = "$2" ]; then echo "  ok   $3"; else echo "  FAIL $3 (got '$1', wanted '$2')"; fi; }
for arm in genuine renamed; do
  if [ "$arm" = genuine ]; then
    CLAIMS_INPUTS='README.md
DISCLAIMER.md
LICENSE
NOTICE'
  else
    CLAIMS_INPUTS='README.md
DISCLAIMER.md
LICENSE
NOTICE_MOVED'
  fi
  WF=$(mktemp -d)
  echo "== arm: $arm"
  . /tmp/rev2853-tools/row11.sh
  rm -rf "$WF"
done
