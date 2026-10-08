#!/bin/bash
# Reviewer's harness for the #2062 delta: prepr --self-test at head, and three planted variants.
cd /Users/timmalmstrom/hpo-seats/review-2062/wt || exit 9
export PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH
E=/Users/timmalmstrom/hpo-seats/review-2062/evidence2
P=tools/pr/prepr.sh
run() { bash $P --self-test > $E/st_$1.out 2>&1; rc=$?
  echo "RESULT $1 rc=$rc"; grep -E "delivery row|edits a row the base had" $E/st_$1.out | cut -c1-160; tail -2 $E/st_$1.out | cut -c1-160; }
run head
python3 - <<'PY'
p='tools/pr/prepr.sh';s=open(p).read();a='    args+=(--existing-file "$ex")\n';assert s.count(a)==1;open(p,'w').write(s.replace(a,'    :\n'))
PY
run M_fix_removed; git checkout -q -- $P
git show af5560f81:$P > $P; run at_af5560f8_test_only; git checkout -q -- $P
python3 - <<'PY'
p='tools/pr/prepr.sh';s=open(p).read();a='"$CLM/rowpaths" delivery-status';assert s.count(a)==1;open(p,'w').write(s.replace(a,'"$CLM/rowpaths"'))
PY
run M_null_no_red; git checkout -q -- $P
git status --short
