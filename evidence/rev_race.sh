#!/bin/bash
# Reviewer's own reproduction (not the fixer's harness): two concurrent
# roster_edit.py --push edits of one branch in a scratch bare repo, the real
# r10 roster and the real brief_lint as the lint window.
# usage: rev_race.sh <tree> <shared|separate|solo> <delayB-seconds> <run-id>
set -u
TREE=$1 MODE=$2 DELAY=$3 ID=$4
REPO=${REPO:?checkout}
S=$(mktemp -d -p "${SCR:?}" race-XXXX)
git init -q --bare "$S/o.git"
git -C "$REPO" push -q "$S/o.git" origin/main:refs/heads/main origin/handoff/audit-r10-roster:refs/heads/R
git clone -q "$S/o.git" "$S/c1"
if [ "$MODE" = separate ]; then git clone -q "$S/o.git" "$S/c2"; CB=$S/c2; else CB=$S/c1; fi
L=$S/lint; git -C "$REPO" worktree add -q --detach "$L" origin/main
G=R10-ROSTER-PUSH-RACE
B0=$(git -C "$S/o.git" rev-parse R)
python "$TREE/tools/audit/seat/roster_edit.py" append-carry $G "reviewer carry A $ID" \
  --checkout "$S/c1" --branch R --worktree "$S/wtA" --lint-cwd "$L" --push >"$S/A.out" 2>&1 &
PA=$!
rcB=skip
if [ "$MODE" != solo ]; then
  sleep "$DELAY"
  python "$TREE/tools/audit/seat/roster_edit.py" set-stage $G "rev-stage-B-$ID" \
    --checkout "$CB" --branch R --worktree "$S/wtB" --lint-cwd "$L" --push >"$S/B.out" 2>&1; rcB=$?
fi
wait $PA; rcA=$?
git -C "$S/o.git" show R:dev/programme/rosters/wave-r10-groups.json > "$S/final.json"
TIP=$(git -C "$S/o.git" rev-parse R)
hasA=$(jq --arg g $G --arg c "reviewer carry A $ID" '[.groups[]|select(.group==$g)|.carry[]?|select(.==$c)]|length' "$S/final.json")
hasB=$(jq -r --arg g $G '.groups[]|select(.group==$g)|.resume.stage' "$S/final.json")
[ "$hasB" = "rev-stage-B-$ID" ] && hasB=1 || hasB=0
false_rep=0
for x in A B; do
  [ -f "$S/$x.out" ] || continue
  for sha in $(sed -n 's/^pushed R at \([0-9a-f]\{40\}\)$/\1/p' "$S/$x.out"); do
    git -C "$S/o.git" merge-base --is-ancestor "$sha" "$TIP" 2>/dev/null || false_rep=$((false_rep+1))
  done
done
lost=0
[ $rcA = 0 ] && [ $hasA = 0 ] && lost=$((lost+1))
[ "$rcB" = 0 ] && [ $hasB = 0 ] && lost=$((lost+1))
refused=0; [ $rcA != 0 ] && refused=$((refused+1)); [ "$rcB" != 0 ] && [ "$rcB" != skip ] && refused=$((refused+1))
pushes=$(git -C "$S/o.git" rev-list --count $B0..$TIP)
raced=$(cat "$S"/*.out | grep -c "lost a race")
echo "RESULT tree=$(git -C $TREE rev-parse --short=9 HEAD) mode=$MODE delay=$DELAY id=$ID rcA=$rcA rcB=$rcB hasA=$hasA hasB=$hasB silent_losses=$lost false_reports=$false_rep refused=$refused pushes=$pushes lost_race_said=$raced"
git -C "$REPO" worktree remove --force "$L"
cp "$S/A.out" "$SCR/out-$ID-A.txt"; [ -f "$S/B.out" ] && cp "$S/B.out" "$SCR/out-$ID-B.txt"
rm -rf "$S"
