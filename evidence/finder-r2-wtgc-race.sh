#!/bin/bash
# worktree_gc.sh class A: a branch that moves between the unpushed read and `git branch -D`.
# usage: wtgc-race.sh <worktree_gc.sh> <race:1|0>
set -u
GC=$1; RACE=$2; T=$(mktemp -d); REAL_GIT=$(command -v git)
mkdir -p $T/bin $T/seats/seat-a
git init -q --bare $T/origin.git
git init -q -b main $T/repo; cd $T/repo
git -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
git remote add origin $T/origin.git; git push -q origin main
git branch fix/merged; git push -q origin fix/merged
git worktree add -q $T/seats/seat-a/wt fix/merged
cat > $T/bin/gh <<G
#!/bin/sh
case "\$1" in auth) exit 0;; pr) echo '[{"state":"MERGED"}]'; exit 0;; esac; exit 9
G
cat > $T/bin/git <<G
#!/bin/sh
if [ "$RACE" = 1 ] && [ "\$1 \$2" = "worktree remove" ] && [ ! -e $T/raced ]; then
  touch $T/raced
  $REAL_GIT -C $T/seats/seat-a/wt -c user.name=s -c user.email=s@s commit -q --allow-empty -m "seat commit after the read"
  $REAL_GIT -C $T/repo rev-parse fix/merged > $T/moved-tip
fi
exec $REAL_GIT "\$@"
G
chmod +x $T/bin/*
before=$(git rev-parse fix/merged)
PATH=$T/bin:$PATH WORKTREE_GC_SEATS_ROOT=$T/seats WORKTREE_GC_TMP_ROOT=$T/tmp HPO_STATE_DIR=$T/state \
  bash $GC o/r > $T/out 2>&1; echo "gc rc=$?"
sed 's/^/  gc| /' $T/out
moved=$(cat $T/moved-tip 2>/dev/null || echo none)
echo "planned/read tip=$before moved tip=$moved"
echo "local branch now: $(git rev-parse -q --verify refs/heads/fix/merged || echo deleted)"
lost=0
if [ "$moved" != none ]; then
  if git branch -a --contains $moved 2>/dev/null | grep -q .; then :; elif git tag --contains $moved 2>/dev/null | grep -q .; then :; else lost=1; fi
fi
echo "RESULT race=$RACE moved-tip-deleted-unpushed=$lost"
rm -rf $T
