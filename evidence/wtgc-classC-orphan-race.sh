#!/bin/bash
# Reviewer-built (not the finder's): sibling shape of the round-3 finder harness
# (origin/verdict/3085:evidence/wtgc-detached-race.sh). worktree_gc.sh class C,
# an ORPHANED seat (seats/<s>/wt not registered to this repo: here a separate clone,
# e.g. a seat worktree of another checkout) DETACHED at a merged sha. A seat commits
# in it between the class-C read (`git -C <wt> rev-parse HEAD`) and `rm -rf <seat>`.
# usage: wtgc-classC-orphan-race.sh <worktree_gc.sh> <race:1|0>
set -u
GC=$1; RACE=$2; T=$(mktemp -d); REAL_GIT=$(command -v git)
mkdir -p $T/bin $T/seats/seat-a
git init -q --bare $T/origin.git
git init -q -b main $T/repo; cd $T/repo
git -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
git remote add origin $T/origin.git; git push -q origin main
git clone -q $T/repo $T/seats/seat-a/wt; git -C $T/seats/seat-a/wt checkout -q --detach
git -c user.name=t -c user.email=t@t commit -q --allow-empty -m next; git push -q origin main; git fetch -q origin
find $T/seats -exec touch -h -d '2020-01-01' {} + 2>/dev/null
cat > $T/bin/gh <<G
#!/bin/sh
case "\$1" in auth) exit 0;; pr) echo '[{"state":"MERGED"}]'; exit 0;; esac; exit 9
G
cat > $T/bin/git <<G
#!/bin/sh
if [ "$RACE" = 1 ] && [ "\$1 \$3 \$4" = "-C rev-parse HEAD" ] && [ ! -e $T/raced ]; then
  out=\$($REAL_GIT "\$@"); rc=\$?
  touch $T/raced
  $REAL_GIT -C $T/seats/seat-a/wt -c user.name=s -c user.email=s@s commit -q --allow-empty -m "seat commit after the read"
  $REAL_GIT -C $T/seats/seat-a/wt rev-parse HEAD > $T/moved-tip
  printf '%s\n' "\$out"; exit \$rc
fi
exec $REAL_GIT "\$@"
G
chmod +x $T/bin/*
PATH=$T/bin:$PATH WORKTREE_GC_SEATS_ROOT=$T/seats WORKTREE_GC_TMP_ROOT=$T/tmp HPO_STATE_DIR=$T/state \
  bash $GC o/r > $T/out 2>&1; echo "gc rc=$?"
sed 's/^/  gc| /' $T/out
moved=$(cat $T/moved-tip 2>/dev/null || echo none)
echo "moved tip=$moved seat wt now: $([ -d $T/seats/seat-a/wt ] && echo present || echo removed)"
lost=0
if [ "$moved" != none ]; then
  if [ -d $T/seats/seat-a/wt ] && $REAL_GIT -C $T/seats/seat-a/wt cat-file -e $moved 2>/dev/null; then :
  elif $REAL_GIT -C $T/repo cat-file -e $moved 2>/dev/null || $REAL_GIT -C $T/origin.git cat-file -e $moved 2>/dev/null; then :
  else lost=1; fi
fi
echo "RESULT race=$RACE orphan-detached-moved-head-lost=$lost"
rm -rf $T
