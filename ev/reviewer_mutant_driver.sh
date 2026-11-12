#!/bin/bash
# run.sh <mutant>...: one worktree per mutant at the head, mutate the page, run the harness, keep FAIL/RESULT lines
R=/home/user/heatpump_optimizer; H=438d15f1926d713925c2b00f2fcbd0dcf20b5a72
for m in "$@"; do
  d=$HOME/mw/$m; rm -rf $d; git -C $R worktree add -q --detach $d $H || exit 9
  python3 $HOME/rv/drv/mut.py $m $d/docs/index.html || { echo "$m MUTATE-FAILED" > $HOME/rv/ev/mut_$m.txt; continue; }
  { echo "== mutant $m at $H; diff:"; git -C $d diff -U0 -- docs/index.html | grep '^[+-]' | cut -c1-260
    (cd $d && node dev/audit/harnesses/r10_product_page.mjs 2>&1 | grep -v '^ok' | cut -c1-900); echo "rc=${PIPESTATUS[0]}"; } > $HOME/rv/ev/mut_$m.txt 2>&1
  git -C $R worktree remove --force $d
done
echo done "$@"
