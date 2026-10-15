#!/bin/bash
# lenflip.sh: for every LEN site, replace `<idx> < len(<seq>)` (or `<idx> + 1 < len`) with True; run its block
S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad
cd $S/revi1 || exit 9
while IFS=: read f l; do
  case "$f:$l" in *optimizer.py:54[7-9]*|*optimizer.py:55[0-6]*) blk=C;; *) blk=D;; esac
  python3 - "$f" "$l" <<'PY' || { echo "SKIP $f:$l"; continue; }
import re, sys
f, ln = sys.argv[1], int(sys.argv[2])
L = open(f).read().split("\n")
new, n = re.subn(r"\b\w+(?: \+ 1)? < len\([\w.]+\)", "True", L[ln-1])
assert n == 1, L[ln-1]
L[ln-1] = new; open(f, "w").write("\n".join(L))
PY
  out=$($S/rev/blk.sh $blk | tail -1)
  rc=${out##*=}
  echo "$(basename $f):$l block=$blk rc=$rc $( [ "$rc" != 0 ] && echo KILLED || echo SURVIVED)"
  git checkout -q -- "$f"
done < $S/rev/len_sites.txt
git status --porcelain | grep -v '^??' && echo DIRTY || echo CLEAN
