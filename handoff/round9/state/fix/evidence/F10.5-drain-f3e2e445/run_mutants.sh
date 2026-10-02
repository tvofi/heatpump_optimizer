#!/bin/bash
# usage: run_mutants.sh <head-sha>; one worktree per mutant, entities.py on each
set -u
HEAD_SHA=$1; OUT=${OUT:-/tmp/claude-0/mutants}; mkdir -p $OUT
export PATH=/tmp/claude-0/venv313/bin:$PATH
cd /home/user/heatpump_optimizer
for name in ${NAMES:-$(python3 -c 'import sys; sys.path.insert(0,"/tmp/claude-0"); import mutants; print(" ".join(mutants.MUTANTS))') M0_null}; do
  (
  W=$OUT/wt-$name; git worktree add -q --detach $W $HEAD_SHA
  cd $W
  python3 - "$name" <<'PY'
import sys; sys.path.insert(0,"/tmp/claude-0"); import mutants
n=sys.argv[1]; p="tests/mutation_table.py"; s=open(p).read()
if n=="M0_null":
    s=s.replace("# ---------------------------------------------------------------- --drain\n","# ---------------------------------------------------------------- --drain (null)\n",1)
else:
    a,b=mutants.MUTANTS[n]; assert s.count(a)==1,n; s=s.replace(a,b)
open(p,"w").write(s)
PY
  PYTHONPATH=tests/hastub python3 tests/entities.py > $OUT/$name.log 2>&1; echo "rc=$?" >> $OUT/$name.log
  cd /home/user/heatpump_optimizer; git worktree remove --force $W
  ) &
done
wait
for f in $OUT/*.log; do echo "== $(basename $f .log): $(tail -2 $f | head -1)"; grep -E "^\s*FAIL" $f | grep -vE " a[0-9]+:" | cut -c1-140; done > $OUT/summary.txt
