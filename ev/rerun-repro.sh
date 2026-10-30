# What a re-run of open_pr.sh meets after a CLOSED exit: pr_release_wt (line 150) detaches and
# keeps $D/wt and keeps the local branch (origin holds it), so open_pr.sh line 37 / line 52
# `git worktree add -q -b $BR $WT $C` fails whichever name line 37 picks.
S=$(mktemp -d); cd $S && git init -q o && git -C o commit -q --allow-empty -m i && git clone -q o m && cd m
git worktree add -q -b fix/t ../wt HEAD && git -C ../wt commit -q --allow-empty -m p1 && git -C ../wt push -q origin fix/t && git -C ../wt checkout -q --detach
git worktree add -q -b fix/t-pr ../wt HEAD; echo "exit $?"   # BR_FIXED unset: line 37 renames
git worktree add -q -b fix/t ../wt HEAD; echo "exit $?"      # BR_FIXED set
