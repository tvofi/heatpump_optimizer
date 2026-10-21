#!/usr/bin/env bash
# The roster push race (R10-ROSTER-PUSH-RACE): two `roster_edit.py --push`
# runs editing one roster branch from one parent, against a throwaway bare
# origin. A brief_lint stub sleeps LINT_S seconds, widening the window between
# a run's prepare and its push that the real lint (~40 s) opens.
#
#   bash dev/audit/harnesses/r10_roster_push_race.sh <tree> [shared|separate|solo]
#
# <tree> is the checkout whose tools/audit/seat/roster_edit.py runs.
#   shared   both runs use ONE --checkout repository (two worktrees of it):
#            the 2026-10-21 shape, where every worktree shares local branches
#   separate each run has its own clone of origin
#   solo     run A alone: the null control (one edit, one push)
# Per run it prints rc, the sha the run reported pushed, whether origin's tip
# contains that sha, and whether the run's edit is in origin's roster; then
#   silent_losses   runs with rc 0 whose edit is NOT on origin
#   false_reports   runs that printed "pushed ... at <sha>" for a sha origin
#                   does not contain
#   refused_edits   runs with rc != 0 (loud; the edit did not land)
#   pushes          commits origin's branch gained during the race
set -u
TREE=${1:?usage: r10_roster_push_race.sh <tree> [shared|separate|solo]}
MODE=${2:-shared}
LINT_S=${LINT_S:-3}
PY=${PYTHON:-python3}
# shellcheck source=tests/throwaway_git.sh
. "$(cd "$(dirname "$0")/../../.." && pwd)/tests/throwaway_git.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
race() {
throwaway_git_env
R=dev/programme/rosters/wave-r9-groups.json
throwaway_git_init "$T/seed" -q -b main
mkdir -p "$T/seed/tools/policy" "$T/seed/dev/programme/rosters"
printf "await new Promise(r => setTimeout(r, %d));\nconsole.log('TOTAL: 0 error(s) across 1 file(s)');\n" \
  "$((LINT_S * 1000))" > "$T/seed/tools/policy/brief_lint.mjs"
"$PY" - "$T/seed/$R" <<'PYS'
import json, sys
g = lambda n: {"group": n, "lane": "L1", "issues": [], "fixes": [], "after": [],
               "brief": n, "resume": {"stage": "not-started", "branch": "handoff/x"}}
open(sys.argv[1], "w").write(json.dumps({"repo": "x", "groups": [g("R9-A"), g("R9-B")]}, indent=1))
PYS
git -C "$T/seed" add -A && git -C "$T/seed" commit -qm seed
throwaway_git_clone -q --bare "$T/seed" "$T/origin.git"
throwaway_git_clone -q "$T/origin.git" "$T/drvA"
throwaway_git_clone -q "$T/origin.git" "$T/drvB"
CHK_B=$T/drvB
[ "$MODE" = shared ] && CHK_B=$T/drvA
edit() { # checkout worktree op group value
  "$PY" "$TREE/tools/audit/seat/roster_edit.py" "$3" "$4" "$5" --checkout "$1" \
    --roster-ref main --branch handoff/roster --worktree "$2" --lint-cwd "$T/seed" --push
}
# the branch exists first: both racers then share its tip as their parent
edit "$T/drvA" "$T/wtA" set-stage R9-A seeded >/dev/null 2>&1 || { echo "setup edit failed"; exit 1; }
before=$(git -C "$T/origin.git" rev-parse handoff/roster)
edit "$T/drvA" "$T/wtA" append-carry R9-A carry-from-A >"$T/A.log" 2>&1 & PA=$!
if [ "$MODE" != solo ]; then
  edit "$CHK_B" "$T/wtB" set-stage R9-B stage-from-B >"$T/B.log" 2>&1 & PB=$!
fi
wait $PA; RA=$?
RB=
[ "$MODE" != solo ] && { wait $PB; RB=$?; }
tip=$(git -C "$T/origin.git" rev-parse handoff/roster)
roster=$(git -C "$T/origin.git" show "handoff/roster:$R")
silent=0 false=0 refused=0
report() { # name rc log needle
  local sha on edit
  sha=$(sed -n 's/^pushed [^ ]* at \([0-9a-f]\{40\}\)$/\1/p' "$3" | tail -1)
  on=n/a
  if [ -n "$sha" ]; then
    if git -C "$T/origin.git" merge-base --is-ancestor "$sha" "$tip" 2>/dev/null; then on=yes; else on=no; false=$((false + 1)); fi
  fi
  if printf '%s' "$roster" | grep -q "$4"; then edit=yes; else edit=no; fi
  [ "$2" -eq 0 ] && [ "$edit" = no ] && silent=$((silent + 1))
  [ "$2" -ne 0 ] && refused=$((refused + 1))
  echo "$1 rc=$2 reported=${sha:-none} reported_on_origin=$on edit_on_origin=$edit"
  sed "s/^/  $1| /" "$3"
}
report A "$RA" "$T/A.log" carry-from-A
[ "$MODE" != solo ] && report B "$RB" "$T/B.log" stage-from-B
echo "mode=$MODE silent_losses=$silent false_reports=$false refused_edits=$refused pushes=$(git -C "$T/origin.git" rev-list --count "$before..$tip")"
}
( race )
