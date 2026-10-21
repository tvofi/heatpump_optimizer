#!/bin/bash
# reviewer's own mutants: <name> <file> <python-replace old> <new>; runs the file's self-test, prints tally+FAIL lines
cd "$WT" || exit 2
name=$1 f=$2 old=$3 new=$4
python3 - "$f" "$old" "$new" <<'P' || { echo "$name: PATTERN NOT FOUND"; exit 2; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read()
if s.count(o)!=1: sys.exit(1)
open(p,'w').write(s.replace(o,n))
P
case $f in tools/pr/app_push.sh) out=$(bash tools/pr/app_push.sh --self-test 2>&1);; *) out=$(bash tools/audit/seat/update_pr.sh --self-test 2>&1);; esac
git checkout -q -- "$f"
echo "== $name"; printf '%s\n' "$out" | grep -E 'checks,|FAIL' | cut -c1-200
