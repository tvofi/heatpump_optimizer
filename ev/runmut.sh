#!/bin/bash
S=/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad
W=$HOME/wt-mut
cd $W && git checkout -q -- . 
python3 - <<'PY' > $S/rev/mutnames.txt
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad/rev")
from mutants import M
for m in M: print(m[0])
PY
echo "unmutated: $($S/block.sh $W | head -1)"
for name in $(cat $S/rev/mutnames.txt); do
  python3 - "$name" <<'PY'
import sys; sys.path.insert(0, "/tmp/claude-0/-home-user-heatpump-optimizer/fed31491-137c-5466-8393-3cd29f796565/scratchpad/rev")
from mutants import M
n = sys.argv[1]
for name, f, old, new in M:
    if name == n:
        s = open(f).read(); k = s.count(old)
        if k != 1: print(f"APPLY-FAIL {n} count={k}"); sys.exit(1)
        open(f, "w").write(s.replace(old, new))
PY
  if [ $? -ne 0 ]; then echo "MUTANT $name APPLY-FAIL"; git checkout -q -- .; continue; fi
  out=$($S/block.sh $W)
  rc=$(echo "$out" | head -1)
  first=$(echo "$out" | grep -m1 -E "^  FAIL|^FAIL|Traceback|^[A-Za-z]*Error" | cut -c1-160)
  if [ "$rc" = "rc=0" ]; then echo "MUTANT $name SURVIVED"; else echo "MUTANT $name KILLED ($rc) $first"; fi
  git checkout -q -- .
done
echo MUTANTS-DONE
