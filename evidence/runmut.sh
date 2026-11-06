# usage: runmut.sh <sha> <tag> <mutant>
sha=$1; tag=$2; m=$3; d=/tmp/mut/$tag-$m; O=/tmp/tmp.xPygWLqPPc/ev
rm -rf $d; git -C /home/user/heatpump_optimizer worktree add -q --detach $d $sha
python3 /tmp/mut/mutate.py $d $m > $O/mut-$tag-$m.log 2>&1 || { echo "$tag $m MUTATE-FAIL"; exit 0; }
git -C $d diff > $O/mutant-$tag-$m.diff
cd $d && PYTHONPATH=tests/hastub timeout 5400 python3 tests/features.py >> $O/mut-$tag-$m.log 2>&1; rc=$?
echo "$tag $m rc=$rc $(grep -E 'FEATURE CHECKS' $O/mut-$tag-$m.log | tail -1)"
git -C /home/user/heatpump_optimizer worktree remove --force $d
