#!/bin/bash
# usage: drv.sh <script whose main flow is tested> <script holding arm 12>
P="$1"; A="${2:-$1}"
st_pass=0 st_fail=0
st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3"; else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s want %s)\n' "$3" "$1" "$2"; fi; }
ST_ROOT=$(mktemp -d)
flow=$(awk 'f{print} /^rc=0$/{f=1}' "$P")
arm=$(sed -n '/# (12) Summary-only stdout/,/rm -rf "\${SM:?}"/p' "$A")
eval "$arm"
echo "RESULT arm12 $(basename $P): $st_pass passed, $st_fail failed"
