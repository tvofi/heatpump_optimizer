#!/bin/bash
# Reviewer's own harness for R10-FLY-ABORT-OWN-MERGE: <repo> <sha> -> RESULT lines
R=$1; S=$2; t=$(mktemp -d); export GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=x GIT_AUTHOR_EMAIL=x@x GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@x
g() { git -c init.defaultBranch=main "$@"; }
o=$t/o; g init -q $o; cd $o; echo base > f; git add f; git commit -qm base
git branch pr; git branch prc
mkdir -p tools/pr; printf '#!/bin/bash\necho stub; exit 1\n' > tools/pr/app_push.sh; git add tools; git commit -qm stub
echo main > f; git commit -qam main
git checkout -q pr; echo pr > f; git commit -qam pr
git checkout -q prc; echo c > c; git add c; git commit -qm prc; git checkout -q main
g clone -q $o $t/m; mkdir -p $t/m/tools/audit/seat
for f in remerge_main.sh pr_args.sh; do git -C $R show $S:tools/audit/seat/$f > $t/m/tools/audit/seat/$f; done
cd $t/m
rm_case() { # <branch> <wt>
  git fetch -q origin $1; git worktree add -q -B $1 $2 origin/$1
  bash tools/audit/seat/remerge_main.sh 9 $2 $1 /dev/null > $t/out 2>&1; echo $?
}
# A: conflict
rc=$(rm_case pr $t/wa)
mh=$(git -C $t/wa rev-parse -q --verify MERGE_HEAD >/dev/null && echo yes || echo no)
st=$(git -C $t/wa status --porcelain | wc -l)
at=$( [ "$(git -C $t/wa rev-parse HEAD)" = "$(git rev-parse origin/pr)" ] && echo yes || echo no)
rel=$(git worktree remove $t/wa 2>/dev/null && echo yes || echo no)
echo "RESULT remerge-conflict rc=$rc named=$(grep -c 'MERGE CONFLICT 9' $t/out) merge_head=$mh dirty_lines=$st at_origin=$at unforced_release=$rel"
git worktree remove --force $t/wa 2>/dev/null; git worktree prune
# B: clean (null control)
rc=$(rm_case prc $t/wb)
p1=$( [ "$(git -C $t/wb rev-parse HEAD^1 2>/dev/null)" = "$(git rev-parse origin/prc)" ] && echo yes || echo no)
p2=$( [ "$(git -C $t/wb rev-parse HEAD^2 2>/dev/null)" = "$(git rev-parse origin/main)" ] && echo yes || echo no)
echo "RESULT remerge-clean named=$(grep -c 'MERGE CONFLICT' $t/out) parent1_branch=$p1 parent2_main=$p2 dirty_lines=$(git -C $t/wb status --porcelain | grep -vc '^??')"
git worktree remove --force $t/wb; git worktree prune
# C: fetch fails (origin gone) with an uncommitted edit in W
git fetch -q origin pr; git worktree add -q -B pr $t/wc origin/pr; echo user-edit > $t/wc/f
mv $o $o.gone; bash tools/audit/seat/remerge_main.sh 9 $t/wc pr /dev/null > $t/out 2>&1; rc=$?; mv $o.gone $o
echo "RESULT remerge-fetchfail rc=$rc user_edit_kept=$(grep -qx user-edit $t/wc/f && echo yes || echo no)"
git worktree remove --force $t/wc; git worktree prune
# D: the lock holder (update_pr's detach) on a conflicted run worktree, plain exit and SIGKILL
for mode in exit kill; do
  git fetch -q origin pr; git worktree add -q -B pr $t/wd origin/pr
  bash -c 'source tools/audit/seat/pr_args.sh >/dev/null 2>&1; pr_branch_lock "$1.lock" pr "$1" detach; git -C "$1" merge -q --no-edit origin/main >/dev/null 2>&1; [ "$2" = kill ] && kill -9 $$; exit 1' _ $t/wd $mode >/dev/null 2>&1
  for i in $(seq 50); do [ -n "$(cut -d' ' -f4 $t/wd.lock 2>/dev/null)" ] && ! pgrep -f "$t/wd.lock" >/dev/null && break; sleep 0.2; done
  mh=$(git -C $t/wd rev-parse -q --verify MERGE_HEAD >/dev/null && echo yes || echo no)
  det=$(git -C $t/wd symbolic-ref -q HEAD >/dev/null && echo no || echo yes)
  echo "RESULT holder-$mode merge_head=$mh detached=$det dirty_lines=$(git -C $t/wd status --porcelain | wc -l) at_origin=$([ "$(git -C $t/wd rev-parse HEAD)" = "$(git rev-parse origin/pr)" ] && echo yes || echo no)"
  git worktree remove --force $t/wd; git worktree prune; rm -f $t/wd.lock*
done
# E: holder null control: clean merge kept
git fetch -q origin prc; git worktree add -q -B prc $t/we origin/prc
bash -c 'source tools/audit/seat/pr_args.sh >/dev/null 2>&1; pr_branch_lock "$1.lock" prc "$1" detach; git -C "$1" merge -q --no-edit origin/main >/dev/null 2>&1; exit 0' _ $t/we >/dev/null 2>&1
for i in $(seq 50); do ! pgrep -f "$t/we.lock" >/dev/null && break; sleep 0.2; done
echo "RESULT holder-clean merge_kept=$([ "$(git -C $t/we rev-parse HEAD^2 2>/dev/null)" = "$(git rev-parse origin/main)" ] && echo yes || echo no) detached=$(git -C $t/we symbolic-ref -q HEAD >/dev/null && echo no || echo yes)"
# F: BUSY second holder does not touch the first's conflicted worktree
git worktree remove --force $t/we; git fetch -q origin pr; git worktree add -q -B pr $t/wf origin/pr
( bash -c 'source tools/audit/seat/pr_args.sh >/dev/null 2>&1; pr_branch_lock "$1.lock" pr "$1" detach; git -C "$1" merge -q --no-edit origin/main >/dev/null 2>&1; sleep 8; exit 1' _ $t/wf >/dev/null 2>&1 & )
sleep 2; bash -c 'source tools/audit/seat/pr_args.sh >/dev/null 2>&1; pr_branch_lock "$1.lock" pr "$1" detach; echo GOT' _ $t/wf > $t/busy 2>&1; brc=$?
sleep 1; mh=$(git -C $t/wf rev-parse -q --verify MERGE_HEAD >/dev/null && echo yes || echo no)
echo "RESULT holder-busy second_rc=$brc first_merge_still_in_progress=$mh"
for i in $(seq 60); do ! pgrep -f "$t/wf.lock" >/dev/null && break; sleep 0.2; done
echo "RESULT holder-busy-after-first-ends merge_head=$(git -C $t/wf rev-parse -q --verify MERGE_HEAD >/dev/null && echo yes || echo no)"
rm -rf $t
