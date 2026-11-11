#!/bin/bash
# killed() rule against the measured baseline: rc!=0 and more FAIL lines than 1
out=$(PYTHONPATH=tests/hastub python3 tests/features.py 2>&1); rc=$?
n=$(printf '%s\n' "$out" | grep -c '^ *FAIL\|FAIL ' )
tail=$(printf '%s\n' "$out" | grep -E 'FEATURE CHECKS' | tail -1)
echo "killcmd rc=$rc failed_lines=$n $tail" >&2
printf '%s\n' "$out" | grep -E 'FAIL' | grep -v 'FEATURE CHECKS' | head -5 >&2
[ $rc -ne 0 ] && [ $n -gt 1 ] && exit 1
exit 0
