#!/bin/bash
# r10_fly_orphans_landed.sh -- drive a checkout's own `bus.sh orphans` over
# handoffs whose change is already on main (R10-FLY-ORPHANS-REWRITTEN).
#
#   bash dev/audit/harnesses/r10_fly_orphans_landed.sh <checkout> [<main sha>]
#
# Builds a throwaway bare remote borrowing this repository's objects, sets its
# main to <main sha> (default origin/main), pushes one handoff/<t> and
# handoff-body/<t> pair per case, and runs <checkout>/tools/audit/seat/bus.sh
# orphans --min-age-h 0 against it, so each end of a fix is measured by its
# own production classifier. One line per case:
#   RESULT <case>=<ORPHAN|SUPERSEDED|discharged> expect=<landed|stranded>
# then `MISREAD <n>`: the landed cases read ORPHAN plus the stranded read
# otherwise. Then the relay's level over the same refs, <checkout>'s own
# `ledger.py level`, given each pr<N> topic as `pr<N> merged=<merge commit
# time>` (what the relay reads from `gh pr list --state merged`; a checkout
# that predates that line ignores it): `LEVEL <case>=<owed|closed>`, and
# `LEVEL-MISREAD <n>` alike. The cases:
#   earlycutoff  ecaf178cb, the handoff #2397 landed by another commit, read
#                stranded 121.8 h (the brief's evidence)                landed
#   pr<N>        #2513 #2465 #2485 #2519 #2525, the five merged handoffs the
#                level owed until archived, SIMULATED: their refs are gone, so
#                each tip is the PR head's tree rewritten as one commit on the
#                merge base of the merge's parents (an App push's shape) landed
#   null         one commit adding a file main lacks, off main     stranded
# Needs a full clone (git fetch --unshallow) holding those commits.
set -u
CO=$(cd "${1:?usage: r10_fly_orphans_landed.sh <checkout> [<main sha>]}" && pwd)
SRC=$(git rev-parse --show-toplevel)
MAIN=${2:-$(git -C "$SRC" rev-parse origin/main)}
ROOT=$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel) || exit 2
# shellcheck source=tests/throwaway_git.sh
. "$ROOT/tests/throwaway_git.sh" # the one way a script builds a throwaway repository
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
throwaway_git_init "$W/o.git" -q --bare && throwaway_git_init "$W/seat" -q || exit 2
for r in "$W/o.git" "$W/seat/.git"; do
  echo "$(git -C "$SRC" rev-parse --path-format=absolute --git-common-dir)/objects" > "$r/objects/info/alternates"
done
g() { git -C "$W/seat" "$@"; }
g remote add origin "$W/o.git"
cases=() merged=() pushes=("$MAIN:refs/heads/main")
add() { [ -n "$2" ] || { echo "case $1: no tip built" >&2; exit 2; }; cases+=("$1 $2 $3"); pushes+=("$2:refs/heads/handoff/$1" "$2:refs/heads/handoff-body/$1"); }
add earlycutoff ecaf178cbd4eef5e3b30425bd4693bef8ceb4b24 landed
for n in 2513 2465 2485 2519 2525; do
  m=$(git -C "$SRC" log -1 --format=%H --grep="^Merge pull request #$n " "$MAIN") || exit 2
  [ -n "$m" ] || { echo "no merge of #$n on $MAIN" >&2; exit 2; }
  base=$(git -C "$SRC" merge-base "$m^1" "$m^2")
  merged+=("pr$n merged=$(git -C "$SRC" log -1 --format=%cI "$m")")
  add "pr$n" "$(GIT_AUTHOR_DATE="1790000000 +0000" GIT_COMMITTER_DATE="1790000000 +0000" g commit-tree "$m^2^{tree}" -p "$base" -m "#$n rewritten")" landed
done
b=$(printf 'r10-fly-orphans null control\n' | g hash-object -w --stdin)
GIT_INDEX_FILE=$W/idx g read-tree "$MAIN"
GIT_INDEX_FILE=$W/idx g update-index --add --cacheinfo "100644,$b,r10_fly_null.txt"
add null "$(GIT_AUTHOR_DATE="1790000000 +0000" GIT_COMMITTER_DATE="1790000000 +0000" g commit-tree "$(GIT_INDEX_FILE=$W/idx g write-tree)" -p "$MAIN" -m null)" stranded
g push -q origin "${pushes[@]}" || exit 2
out=$(cd "$W/seat" && HPO_BUS_STATE=$W/state bash "$CO/tools/audit/seat/bus.sh" orphans --min-age-h 0 2>&1)
echo "$out" | grep -q '^orphans: ' || { echo "$out" >&2; echo "no orphans summary line" >&2; exit 2; }
bad=0
for c in "${cases[@]}"; do
  set -- $c
  st=$(echo "$out" | awk -v t="$1" '($1 == "ORPHAN" || $1 == "SUPERSEDED") && $2 == t { print $1 }')
  echo "RESULT $1=${st:-discharged} expect=$3"
  case $3/${st:-discharged} in landed/ORPHAN|stranded/SUPERSEDED|stranded/discharged) bad=$((bad + 1)) ;; esac
done
echo "$out" | tail -n 1
echo "MISREAD $bad"
git -C "$W/seat" ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$W/hrefs"
printf '%s\n' "${merged[@]}" > "$W/topics"
lv=$(cd "$W/seat" && python3 -I "$CO/tools/audit/seat/ledger.py" --log "$W/lv/l" level "$W/hrefs" "$W/topics" 2>"$W/lv.err")
[ $? -le 1 ] || { cat "$W/lv.err" >&2; echo "the level could not be derived" >&2; exit 2; }
bad=0
for c in "${cases[@]}"; do
  set -- $c
  st=closed; echo "$lv" | grep -q " handoff-no-pr refs/heads/handoff[a-z-]*/$1 " && st=owed
  echo "LEVEL $1=$st expect=$3"
  case $3/$st in landed/owed|stranded/closed) bad=$((bad + 1)) ;; esac
done
echo "LEVEL-LINES $(echo "$lv" | grep -c handoff-no-pr) for ${#cases[@]} topics; $(cat "$W/lv.err")"
echo "LEVEL-MISREAD $bad"
