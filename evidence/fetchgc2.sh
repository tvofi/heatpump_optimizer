#!/bin/bash
# reviewer's own instrument (round 2): does a `git fetch` inside pr_push_hold's
# `{ pr_push_hold; <push> & } 9>>lock` leave a detached gc holding the lock?
# usage: fetchgc2.sh <pr_args.sh> <mode: hold|fggc-off>
# fggc-off presets PR_FG_GC=1, so pr_push_hold skips its foreground-gc export (the mut:fggc behaviour, unedited file)
set -u
PA=$1; MODE=$2; d=$(mktemp -d); cd "$d"
git init -q --bare origin.git; git init -q -b main src; git -C src commit -q --allow-empty -m a; git -C src push -q ../origin.git main
git clone -q origin.git wt 2>/dev/null
mkdir -p wt/big; for k in $(seq 1 3000); do head -c 20000 /dev/urandom > wt/big/f$k; done; git -C wt add big; git -C wt commit -q -m big   # reachable loose objects, so the repack takes seconds
git -C wt config gc.auto 1; git -C wt config maintenance.auto true
git -C src commit -q --allow-empty -m b; git -C src push -q ../origin.git main
. "$PA"; PR_NAME=probe; PR_PUSH_LOCK=$d/lock.push
[ "$MODE" = hold ] || export PR_FG_GC=1
{ pr_push_hold; git -C wt fetch origin main > fetch.out 2>&1 & } 9>>"$PR_PUSH_LOCK"; P=$!
wait $P; echo "the push (git fetch) exited rc=$?"
cat fetch.out | sed 's/^/  fetch: /'
if python3 -I -c 'import fcntl,sys; fcntl.flock(open(sys.argv[1],"a"), fcntl.LOCK_EX|fcntl.LOCK_NB)' "$PR_PUSH_LOCK" 2>/dev/null; then echo "FREE after the push exited"; else echo "HELD after the push exited"; pgrep -af "git.*gc" | sed 's/^/  holder: /'; fi
k=0; while pgrep -f "gc --auto" >/dev/null && [ $k -lt 200 ]; do sleep 0.1; k=$((k+1)); done
echo "loose objects left: $(git -C wt count-objects | cut -d' ' -f1)"
rm -rf "$d"
