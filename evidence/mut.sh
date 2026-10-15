#!/bin/bash
# mut.sh <id> <relpath> <line> <from> <to> <block>: one-line edit, run block, restore
S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad
id=$1 f=$2 ln=$3 a=$4 b=$5 blk=$6
cd $S/revi1 || exit 9
python3 - "$f" "$ln" "$a" "$b" <<'PY' || exit 8
import sys
f, ln, a, b = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
L = open(f).read().split("\n")
assert L[ln-1].count(a) == 1, (L[ln-1], a)
L[ln-1] = L[ln-1].replace(a, b); open(f, "w").write("\n".join(L))
print("MUT", L[ln-1].strip())
PY
$S/rev/blk.sh $blk | tail -1 | sed "s/^/$id /"
grep -E "^\s+FAIL" $S/rev/blk-$blk.log | head -3 | cut -c1-200
git checkout -q -- "$f"; git status --porcelain | grep -v '^??' && echo DIRTY
