set -u
E=/tmp/seat/rev2441/ev; W=/tmp/seat/rev2441/wt; F=tools/policy/field_coverage.mjs
export PYTHONPATH=tests/hastub
r(){ name=$1; shift; ( "$@" ) > $E/$name.txt 2>&1; echo "rc=$?" >> $E/$name.txt; tail -3 $E/$name.txt | sed "s/^/[$name] /"; }
cd $W
r selftest-head node $F --self-test
# R2: registry dropped from RUNS.census, + M3 card census deleted
sed -i 's/=> { censusRegistry(report, censuses, rows); run(report, censuses) }/=> { run(report, censuses) }/' $F; git diff --stat; r R2-selftest node $F --self-test; git checkout -- $F
# R6: planted runs dropped from census arm
sed -i 's/=> { censusRegistry(report, censuses, rows); run(report, censuses) }/=> { censusRegistry(report, censuses, rows) }/' $F; git diff --stat; r R6-selftest node $F --self-test; git checkout -- $F
# R7: census arm removed from RUNS (main would never run it)
sed -i '/^  census: (report, { run = censusRun/d' $F; git diff --stat; r R7-selftest node $F --self-test; git checkout -- $F
git status --short | wc -l
r null-head-census node $F --only census
r bogus node $F --only bogus
for a in hooks ruleset budgets approvals registry; do r only-$a node $F --only $a; done
cd /tmp/seat/rev2441/base; r null-base-census node $F --only census
echo DONE
