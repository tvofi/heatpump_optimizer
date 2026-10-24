# fix.sh <topic> <head> <pr> <brief> : delete claim, render+publish fixer ref, append to pool-s6, read back, report
set -e
export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
O=/Users/timmalmstrom/hpo-orch/r10s6; W=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt
t=$1; h=$2; pr=$3; b=$4
git -C $W ls-remote origin "refs/heads/claim/s6/$t" | grep -q . && git -C $W push -q origin --delete "claim/s6/$t"
python3 $O/repair/render.py $t $h "$pr" $b
python3 $O/scratch/pool.py pool-s6 dispatch/fixer-$t
git -C $W fetch -q origin
git -C $W show origin/dispatch/pool-s6:POOL.txt | grep -qx "dispatch/fixer-$t" && echo "pool read back OK for dispatch/fixer-$t"
