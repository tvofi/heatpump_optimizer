#!/bin/bash
# Companion to the finder's yield_rounds.mjs (M1b): applies the tree's own carry
# rule (app_approve.sh --carry) to the same 22 re-verification rounds, and as the
# null control re-tests every carried round against a synthetic merge from main
# that changes one byte of a file in the branch's own diff.
# Main for each round is the first parent of the PR's own merge into main: the
# main a branch head sat on before it merged (today's main contains the heads,
# which would make every diff against its merge base empty).
# usage: carry_rounds.sh <app_approve.sh> <pairs.txt>   (run in a full clone)
set -u
tool=$1 pairs=$2 n=0 yes=0 ctl=0 ctlno=0
while read -r pr v h word msha; do
  n=$((n+1)); main=$(git rev-parse "$msha^1")
  git merge-base --is-ancestor "$h" "$main" && { echo "SETUP DEFECT: #$pr head $h already on $main"; exit 2; }
  if out=$(bash "$tool" --carry "$v" "$h" "$main" 2>&1); then
    yes=$((yes+1)); echo "carried #$pr ${v:0:10}->${h:0:10}"
    mb=$(git merge-base "$main" "$h"); f=$(git diff --name-only --no-renames "$mb" "$h" | head -1)
    blob=$( { git cat-file -p "$h:$f"; printf 'x'; } | git hash-object -w --stdin)
    mode=$(git ls-tree "$h" -- "$f" | awk '{print $1}')
    idx=$(mktemp); rm -f "$idx"
    GIT_INDEX_FILE=$idx git read-tree "$h" && GIT_INDEX_FILE=$idx git update-index --cacheinfo "$mode,$blob,$f"
    tree=$(GIT_INDEX_FILE=$idx git write-tree); rm -f "$idx"
    evil=$(git commit-tree "$tree" -p "$h" -p "$mb" -m "Merge origin/main (null control: one byte appended to $f)")
    ctl=$((ctl+1))
    if bash "$tool" --carry "$v" "$evil" "$main" >/dev/null 2>&1; then echo "  CONTROL CARRIED (defect): $f"; else ctlno=$((ctlno+1)); fi
  else
    echo "re-review #$pr ${v:0:10}->${h:0:10}: $(printf '%s' "$out" | head -1 | cut -c1-120)"
  fi
done < "$pairs"
echo "RESULT carry_rounds=$n"
echo "RESULT carry_carried=$yes"
echo "RESULT carry_rereviewed=$((n-yes))"
echo "RESULT carry_null_control_rounds=$ctl"
echo "RESULT carry_null_control_refused=$ctlno"
