#!/bin/bash
# Reviewer-built variant of the round-2 finder harness (wtgc-race.sh, sha1 0fe381af):
# worktree_gc.sh class B, a DETACHED worktree whose HEAD moves (a seat commits on it)
# between the classify read and `git worktree remove --force`.
# usage: wtgc-detached-race.sh <worktree_gc.sh> <race:1|0>
set -u
GC=$1; RACE=$2; T=$(mktemp -d); REAL_GIT=$(command -v git)
mkdir -p $T/bin $T/seats/seat-a
git init -q --bare $T/origin.git
git init -q -b main $T/repo; cd $T/repo
git -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
git remote add origin $T/origin.git; git push -q origin main
git worktree add -q --detach $T/seats/seat-a/wt main
git -c user.name=t -c user.email=t@t commit -q --allow-empty -m next; git push -q origin main; git fetch -q origin
# old enough for every age guard
find $T/seats $T/repo/.git/worktrees -exec touch -h -d '2020-01-01' {} + 2>/dev/null
cat > $T/bin/gh <<G
#!/bin/sh
case "\$1" in auth) exit 0;; pr) echo '[{"state":"MERGED"}]'; exit 0;; esac; exit 9
G
cat > $T/bin/git <<G
#!/bin/sh
if [ "$RACE" = 1 ] && [ "\$1 \$2" = "worktree remove" ] && [ ! -e $T/raced ]; then
  touch $T/raced
  $REAL_GIT -C $T/seats/seat-a/wt -c user.name=s -c user.email=s@s commit -q --allow-empty -m "seat commit after the read"
  $REAL_GIT -C $T/seats/seat-a/wt rev-parse HEAD > $T/moved-tip
fi
exec $REAL_GIT "\$@"
G
chmod +x $T/bin/*
PATH=$T/bin:$PATH WORKTREE_GC_SEATS_ROOT=$T/seats WORKTREE_GC_TMP_ROOT=$T/tmp HPO_STATE_DIR=$T/state \
  bash $GC o/r > $T/out 2>&1; echo "gc rc=$?"
sed 's/^/  gc| /' $T/out
moved=$(cat $T/moved-tip 2>/dev/null || echo none)
echo "moved tip=$moved worktree now: $([ -d $T/seats/seat-a/wt ] && echo present || echo removed)"
lost=0
if [ "$moved" != none ]; then
  if git for-each-ref --contains $moved 2>/dev/null | grep -q .; then :; else
     # any surviving worktree HEAD holding it?
     if git worktree list --porcelain | grep -q "HEAD $moved"; then :; else lost=1; fi
  fi
fi
echo "RESULT race=$RACE detached-moved-head-lost=$lost"
rm -rf $T
