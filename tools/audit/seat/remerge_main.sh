#!/bin/bash
# remerge_main.sh <pr> <worktree> <branch> <body>: merge origin/main into an open PR (claimnotes driver), drop inherited claims, push as the App
#
# It pushes with `app_push.sh --recarry`, which prefixes the body's `## Head`
# with the note naming the new head (an automatic merge by the orchestrator, no
# resolution, the reviewed code unchanged) and skips prepr only on a clean
# 2-parent merge of the live head and main under the live body; its header
# states the rule. <body> must be the live body: the train writes it from the
# API. Set REMERGE_WHY to add the occasion to the note in one clause (for
# example "GitHub reported a claim-file conflict it cannot resolve without the
# claimnotes driver"); the default states none. merge_train.py calls this.
# The worktree may be detached: it is reset to origin/<branch> before the merge, and left clean there
# when the merge fails (MERGE CONFLICT, or REMERGE FAILED <pr> at <step> when no conflict caused it).
set -uo pipefail
# A stopped run ends the whole tree it started (R10-PUSHER-REAP): pr_args.sh's EXIT
# trap reaps it, and the push runs asynchronously so an INT does not wait behind it.
. "$(dirname -- "$0")/pr_args.sh"
PR=$1; W=$2; BR=$3; B=$4; shift 4
SEAT=$(cd "$(dirname -- "$0")" && pwd)
PL=$B.push.log; pr_exit_trap 'test -n "${KEEP:-}" || rm -f "$PL"'
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
# A failed merge is aborted before the stop (P276: #2935, #2936): left conflicted, the worktree kept
# the branch, merge_train.py's unforced release_worktrees could not remove it, and the next recarry's
# `worktree add -B` found the branch checked out. The merge started at origin/$BR and merged only
# origin/main, so the abort, or the reset when no merge is in progress, loses nothing.
# The fetch rides git's own transient stderr out on gh_read.py's rule, the train's own
# (R10-TRAIN-MERGE-LOOP-2): unretried, one 502 read as MERGE CONFLICT and stopped the train.
# MERGE CONFLICT is printed only for a merge that left unmerged paths (carry f7d2bf7c): a fetch that
# spent its transient budget or git rejected, a refused reset, or a merge stopped for another reason
# is REMERGE FAILED naming its step, with git's own words above it, and owes no fixer a resolution.
step=fetch
( cd "$W" && python3 "$SEAT/gh_read.py" --git-retry git fetch -q origin main "$BR" ) && step=reset \
  && git -C "$W" reset -q --hard "origin/$BR" && step=merge && git -C "$W" merge --no-edit -q origin/main
rc=$?
if [ "$rc" -ne 0 ]; then
  why="MERGE CONFLICT $PR"
  { [ "$step" = merge ] && [ -n "$(git -C "$W" diff --name-only --diff-filter=U)" ]; } || why="REMERGE FAILED $PR at $step (rc=$rc)"  # mut:remergeconflict
  git -C "$W" merge --abort 2>/dev/null || git -C "$W" reset -q --hard "origin/$BR" 2>/dev/null || :  # mut:remergeabort
  echo "$why"; exit 1
fi
( cd "$W" && python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge" )
ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')
# shellcheck disable=SC2086 # $ISS is a word list of issue numbers
# Every REFUSE line, not the last 120 characters. app_push's die is the last
# line and does not name the prepr step; the step line is the one before it.
# tail -1 | cut -c1-120 kept only the die (measured on #1974 and #1975).
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash "$_push" --recarry tvofi/heatpump_optimizer "$W" "$BR" "$B" $ISS > "$PL" 2>&1 &
wait $! || :; push_out=$(cat "$PL")
# FAIL lines name the failing arms and prepr's `full log:` line names its log (carry 16).
printf '%s\n' "$push_out" | grep -E 'RECARRY|REFUSE|PUSHED|^ *FAIL |full log:' || true  # mut:remergegrep
# No PUSHED: keep the log, as pr_push_failed does, and name it.
pushed=1; case $push_out in *PUSHED*) pushed=0 ;; *) KEEP=1; echo "remerge: push log kept: $PL" ;; esac
sleep 5; echo "RESULT pr=$PR head=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)"
# A refused push (app_push on a detached or untipped worktree) is a failed remerge, not RESULT's success (carry 15).
if [ "$pushed" -ne 0 ]; then echo "REMERGE FAILED $PR at push"; exit 1; fi  # mut:remergepush
