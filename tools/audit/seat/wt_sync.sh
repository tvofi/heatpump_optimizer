#!/bin/bash
# Snapshot every worktree whose state is not already on origin (unpushed commits,
# or uncommitted/untracked files) to origin/wip-sync/<slug>, without touching the
# worktree or its index. Also snapshots the orchestrator scratch dir.
set -uo pipefail
# Usage: tools/audit/seat/wt_sync.sh [--scratch <dir>]
#   run from any checkout of the repo; loop it detached, e.g. every 15 min.
# A session crash loses only what no ref holds: this pushes, without touching
# the worktree or its index, one snapshot commit per such worktree.
R=$(git rev-parse --path-format=absolute --git-common-dir)/..; R=$(cd "$R" && pwd)
S=""; [ "${1:-}" = "--scratch" ] && S=$(cd "$2" && pwd)
snap() { # $1 worktree dir (git), $2 slug, [$3 alt work-tree]
  local w=$1 slug=$2 wt=${3:-$1} idx; idx=$(mktemp)
  local head; head=$(git -C "$w" rev-parse HEAD) || return
  GIT_INDEX_FILE=$idx git -C "$w" read-tree HEAD
  GIT_INDEX_FILE=$idx git -C "$w" --work-tree="$wt" add -A . 2>/dev/null
  local tree; tree=$(GIT_INDEX_FILE=$idx git -C "$w" write-tree); rm -f "$idx"
  local c; c=$(git -C "$w" commit-tree "$tree" -p "$head" -m "wip-sync $slug $(date -u +%FT%TZ)") || return
  git -C "$w" push -q --no-verify -f origin "$c:refs/heads/wip-sync/$slug" && echo "synced $slug ${c:0:8}"
}
git -C $R fetch -q origin
git -C $R worktree list --porcelain | awk '/^worktree /{print substr($0,10)}' | while read -r w; do
  [ -d "$w" ] || continue; [ "$w" = "$R" ] && continue
  dirty=$(git -C "$w" status --porcelain | wc -l | tr -d ' ')
  onremote=$(git -C "$w" branch -r --contains HEAD 2>/dev/null | head -1)
  [ "$dirty" = 0 ] && [ -n "$onremote" ] && continue
  slug=$(echo "${w#$HOME/}" | sed 's#^/##; s#[^A-Za-z0-9._-]#-#g')
  snap "$w" "$slug"
done
[ -n "$S" ] || exit 0
# orchestrator scratch (scripts, bodies, notes) as a parentless snapshot
idx=$(mktemp); GIT_INDEX_FILE=$idx git -C $R read-tree --empty
(cd "$S" && find . -type f -size -2M -not -path '*/wt*' -not -path './wtstamp/*' -not -path '*/.git/*' -print0) | \
 while IFS= read -r -d '' f; do h=$(git -C $R hash-object -w "$S/$f"); printf '100644 %s\t%s\n' "$h" "orch/${f#./}"; done | GIT_INDEX_FILE=$idx git -C $R update-index --index-info
t=$(GIT_INDEX_FILE=$idx git -C $R write-tree); rm -f $idx
c=$(git -C $R commit-tree "$t" -m "wip-sync orchestrator scratch $(date -u +%FT%TZ)")
git -C $R push -q --no-verify -f origin "$c:refs/heads/wip-sync/orchestrator-scratch" && echo "synced orch scratch ${c:0:8}"
