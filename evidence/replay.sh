# Own instrument (reviewer-built): the delivered guard's predicate over live origin.
# For each probe/rev-<pr>-<n8> with an ev/ and verdict.md, build the tree as verdict_tree does
# (VERDICT.md + evidence/) and ask whether review/<pr>'s history carries it.
set -u
W=/tmp/tmp.GlmdineIud; cd /home/user/heatpump_optimizer
git fetch -q origin '+refs/heads/probe/rev-*:refs/rp/probe/rev-*' '+refs/heads/review/*:refs/rp/review/*' || { echo FETCH-FAILED; exit 2; }
gd=$(git rev-parse --absolute-git-dir); carried=0; notc=0; norev=0; skip=0
git for-each-ref --format='%(refname:strip=3) %(objectname)' refs/rp/probe/ | while read -r name sha; do
  k=${name#rev-}; pr=${k%%-*}
  s=$(mktemp -d); mkdir -p $s/w/evidence $s/x
  if ! git archive "$sha" | tar -x -C $s/x 2>/dev/null || [ ! -f $s/x/verdict.md ] || [ ! -d $s/x/ev ]; then echo "SKIP $name"; rm -rf $s; continue; fi
  cp $s/x/verdict.md $s/w/VERDICT.md; cp -R $s/x/ev/. $s/w/evidence/
  t=$(cd $s/w && GIT_DIR=$gd GIT_INDEX_FILE=$s/idx GIT_WORK_TREE=$s/w git add -A -f . && GIT_DIR=$gd GIT_INDEX_FILE=$s/idx git write-tree); rm -rf $s
  if ! git rev-parse -q --verify refs/rp/review/$pr >/dev/null; then echo "NOREVIEW $name"; continue; fi
  if git log --format=%T refs/rp/review/$pr | grep -qxF "$t"; then echo "CARRIED $name"; else echo "NOTCARRIED $name"; fi
done > $W/ev/replay-control.lines
{ echo "reviewer-built instrument, live origin $(date -u +%FT%TZ)"; awk '{print $1}' $W/ev/replay-control.lines | sort | uniq -c; } > $W/ev/replay-control.txt
git for-each-ref --format='%(refname)' refs/rp/ | xargs -r -n1 git update-ref -d
touch $W/mut/replay.done
