#!/usr/bin/env bash
# Reviewer's own instrument (not the fixer's, not the finder's): runs
# tools/release/stamp.py --self-test under a REAL git 2.55.0 built from
# git/git tag v2.55.0, at a given tree.  arm=forced injects
# maintenance.geometric-repack.auto=-1 through GIT_CONFIG_PARAMETERS (the -c
# channel, distinct from the GIT_CONFIG_COUNT channel the fix uses) so the
# geometric repack fires on every commit/merge; arm=natural injects nothing.
# usage: realgit_race.sh <tree> <runs> <natural|forced>
set -u
TREE=$1 RUNS=$2 ARM=$3
G=/Users/timmalmstrom/hpo-seats/review-2051/git255/bin
export PATH="$G:$PATH"
[ "$ARM" = forced ] && export GIT_CONFIG_PARAMETERS="'maintenance.geometric-repack.auto'='-1'"
race=0 fail=0 last=
for i in $(seq 1 "$RUNS"); do
  out="$(cd "$TREE" && python3 tools/release/stamp.py --self-test 2>&1)"; rc=$?
  case "$out" in *"Directory not empty"*) race=$((race+1)); last="$(grep -m1 'Directory not empty' <<<"$out")";; esac
  [ $rc -ne 0 ] && fail=$((fail+1))
done
sleep 3
[ -n "$last" ] && echo "last: $last"
echo "RESULT tree=$(cd $TREE && git rev-parse --short HEAD) arm=$ARM git=$(git --version|cut -d' ' -f3) runs=$RUNS directory_not_empty=$race nonzero_exit=$fail"
