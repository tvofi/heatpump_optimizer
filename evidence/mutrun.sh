#!/bin/bash
# mutrun.sh <worktree> <id> <python-replace-old> <new> : plant, run self-test, restore
d=$1 id=$2 old=$3 new=$4 f=$1/tools/audit/seat/cloud_relay.sh
cp "$f" "$f.orig"
python3 - "$f" "$old" "$new" <<'PY' || { echo "$id NOT-PLANTED"; mv "$f.orig" "$f"; exit; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read()
assert s.count(o)>=1, "pattern missing"
# plant in production only: first occurrence before 'self_test() {'
i=s.index(o); assert i < s.index('self_test() {'), "pattern only in self-test"
open(p,'w').write(s[:i]+n+s[i+len(o):])
PY
out=$(cd "$d" && bash tools/audit/seat/cloud_relay.sh --self-test 2>&1); rc=$?
last=$(tail -1 <<< "$out")
if [ $rc -ne 0 ] || grep -q ' [1-9][0-9]* failed' <<< "$last"; then v=KILLED; else v=SURVIVED; fi
echo "$id $v rc=$rc :: $last"
grep "  FAIL" <<< "$out" | head -3 | sed "s/^/   $id /"
mv "$f.orig" "$f"
