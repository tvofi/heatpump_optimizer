#!/bin/bash
# Snapshot every worktree whose state is not already on origin (unpushed commits,
# or uncommitted/untracked files) to origin/wip-sync/<slug>, without touching the
# worktree or its index. Also snapshots the orchestrator scratch dir.
set -uo pipefail
# Usage: tools/audit/seat/wt_sync.sh [--scratch <dir>]
#   run from any checkout of the repo; loop it detached, e.g. every 15 min.
# A session crash loses only what no ref holds: this pushes, without touching
# the worktree or its index, one snapshot commit per such worktree.
# A ref name and message never carry a host path (#2310): the slug is
# ref_privacy.py's, and its guard refuses a push that would publish the host.
# This script never runs from a stale tree (dev/audit/rca/R11-RCA-PLAN-OBJECTIVE-MISSING.md: round 10's
# loop ran 314 policy and instrument files behind main). base_fresh.py ensure moves a checkout that
# holds no work to origin/main, and the script then starts again from the new file; a checkout it
# cannot move (a commit of its own, a dirty tree, an unread origin) is refused, exit 4, with the repair.
HERE=$(cd "$(dirname "$0")" && pwd)
if [ -z "${HPO_WT_SYNC_FRESH:-}" ]; then
  BF=$(python3 -I "$HERE/base_fresh.py" ensure --dir "$HERE" 2>&1) || {  # mut:fresh
    printf '%s\n' "$BF" >&2; echo "wt_sync: REFUSE BASE-STALE: this script's tree is not origin/main's (above); nothing snapshotted" >&2; exit 4; }
  case $BF in BASE-RESET*) echo "wt_sync: ${BF%%:*}; restarting from the moved tree"; HPO_WT_SYNC_FRESH=1 exec bash "$0" "$@" ;; esac
fi
RP="$HERE/ref_privacy.py"
R=$(git rev-parse --path-format=absolute --git-common-dir)/..; R=$(cd "$R" && pwd)
S=""; [ "${1:-}" = "--scratch" ] && S=$(cd "$2" && pwd)
snap() { # $1 worktree dir (git), $2 slug, [$3 alt work-tree]
  local w=$1 slug=$2 wt=${3:-$1} idx; idx=$(mktemp)
  local head; head=$(git -C "$w" rev-parse HEAD) || return
  GIT_INDEX_FILE=$idx git -C "$w" read-tree HEAD
  GIT_INDEX_FILE=$idx git -C "$w" --work-tree="$wt" add -A . 2>/dev/null
  local tree; tree=$(GIT_INDEX_FILE=$idx git -C "$w" write-tree); rm -f "$idx"
  local msg; msg="wip-sync $slug $(date -u +%FT%TZ)"
  local c; c=$(git -C "$w" commit-tree "$tree" -p "$head" -m "$msg") || return
  python3 -I "$RP" guard --ref "wip-sync/$slug" --message "$msg" --commits "$head" -C "$w" || return
  git -C "$w" push -q --no-verify -f origin "$c:refs/heads/wip-sync/$slug" && echo "synced $slug ${c:0:8}"
}
git -C $R fetch -q origin
git -C $R worktree list --porcelain | awk '/^worktree /{print substr($0,10)}' | while read -r w; do
  [ -d "$w" ] || continue; [ "$w" = "$R" ] && continue
  dirty=$(git -C "$w" status --porcelain | wc -l | tr -d ' ')
  onremote=$(git -C "$w" branch -r --contains HEAD 2>/dev/null | head -1)
  [ "$dirty" = 0 ] && [ -n "$onremote" ] && continue
  slug=$(python3 -I "$RP" slug "$w" --root repo="$R") || continue
  snap "$w" "$slug"
done
[ -n "$S" ] || exit 0
# orchestrator scratch (scripts, bodies, notes) as a parentless snapshot
idx=$(mktemp); GIT_INDEX_FILE=$idx git -C $R read-tree --empty
(cd "$S" && find . -type f -size -2M -not -path '*/wt*' -not -path './wtstamp/*' -not -path '*/.git/*' -print0) | \
 while IFS= read -r -d '' f; do h=$(git -C $R hash-object -w "$S/$f"); printf '100644 %s\t%s\n' "$h" "orch/${f#./}"; done | GIT_INDEX_FILE=$idx git -C $R update-index --index-info
t=$(GIT_INDEX_FILE=$idx git -C $R write-tree); rm -f $idx
msg="wip-sync orchestrator scratch $(date -u +%FT%TZ)"; c=$(git -C $R commit-tree "$t" -m "$msg")
python3 -I "$RP" guard --ref wip-sync/orchestrator-scratch --message "$msg" || exit 3
git -C $R push -q --no-verify -f origin "$c:refs/heads/wip-sync/orchestrator-scratch" && echo "synced orch scratch ${c:0:8}"
