#!/usr/bin/env bash
# Run the whole tests/features.py under one textual mutant of thermal_model.py, then restore.
# usage: full_mut.sh <name> <old> <new>
set -u
S=/Users/timmalmstrom/hpo-seats/r10s6/rev-3879-local
cd "$S/wt" || exit 9
F=custom_components/heatpump_optimizer/thermal_model.py
cp "$F" "$S/tm.$1.orig"
trap 'cp "$S/tm.$1.orig" "$F"; rm -f "$S/tm.$1.orig"' EXIT
python3 - "$F" "$2" "$3" <<'EOF'
import sys
p, a, b = sys.argv[1:4]
s = open(p).read()
assert s.count(a) == 1, s.count(a)
open(p, "w").write(s.replace(a, b))
EOF
start=$(date +%s)
PYTHONPATH=tests/hastub python3 tests/features.py > "$S/ev/full.$1.txt" 2>&1
rc=$?
echo "$1 rc=$rc secs=$(( $(date +%s) - start )) $(grep -c 'FAIL' "$S/ev/full.$1.txt") FAIL-lines; $(tail -1 "$S/ev/full.$1.txt")"
