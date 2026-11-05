#!/bin/bash
# run.sh <shimdir> <label> <expect: refuse|pass> -- gh args...   ; offline, clean env
O=$(cd "$(dirname "$0")" && pwd); S=$1; L=$2; E=$3; shift 4
log=$O/logs/$(echo "$L" | tr -c 'A-Za-z0-9' _).log; mkdir -p $O/logs; : > "$log"
env -i HOME=$O/home HPO_STATE_DIR=$O/state STUBLOG="$log" PATH=$S:$O/stub:/opt/hpo/venv-ci/bin:/usr/bin:/bin gh "$@" >/dev/null 2>$log.err; rc=$?
n=$(wc -l < "$log")
if [ "$E" = refuse ]; then [ $rc -ne 0 ] && [ $n = 0 ] && r=OK || r=FAIL; else [ $rc = 0 ] && [ $n = 1 ] && r=OK || r=FAIL; fi
echo "$r expect=$E rc=$rc stublines=$n :: $L"
