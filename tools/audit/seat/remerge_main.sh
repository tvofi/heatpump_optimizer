#!/bin/bash
# remerge_main.sh <pr> <worktree> <branch> <body> [--head-repo <owner/repo>]: merge origin/main into an open PR (claimnotes driver), drop inherited claims, push as the App
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
#
# --head-repo <owner/repo> is a pull request whose head is NOT a branch of ours (decision 0017;
# merge_train.py passes it when tools/pr/outside.py reports the head cross-repository, with <branch>
# the fork's own branch name from the pulls API). Nothing of origin/<branch> is read then: a fork
# names its own branch, and ours of the same name is another head. The start is refs/pull/<pr>/head,
# the local merge only proves that main merges with no resolution (MERGE CONFLICT otherwise, which
# the train parks naming the fork), no claims commit is made (a non-merge commit after the verdict
# never carries on a head that is not ours, and a fork changes no claim file), and the head is moved
# by GitHub's own update-branch at the expected head, asked as the hpo-author App through its
# installation on OUR repository: app_push.sh mints for the repository it pushes to, where the App
# is not installed, and no personal token is used. The new head is read back and must be the
# 2-parent merge of the old head and a commit of main whose tree is git's own automatic merge.
set -uo pipefail
# A stopped run ends the whole tree it started (R10-PUSHER-REAP): pr_args.sh's EXIT
# trap reaps it, and the push runs asynchronously so an INT does not wait behind it.
. "$(dirname -- "$0")/pr_args.sh"
PR=$1; W=$2; BR=$3; B=$4; shift 4
R=tvofi/heatpump_optimizer; FORK=""; TIP="origin/$BR"; SRC=$BR
if [ "${1:-}" = --head-repo ]; then
  FORK=${2:-}; TIP="refs/remotes/pull/$PR/head"; SRC="+refs/pull/$PR/head:$TIP"
  argok=no; { [[ $FORK =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] && [ "$FORK" != "$R" ] && [[ $PR =~ ^[0-9]+$ ]]; } && argok=yes
  [ "$argok" = yes ] || { echo "REMERGE FAILED $PR at args (--head-repo '$FORK' is not another owner/repo)"; exit 1; }  # mut:remergeforkarg
fi
SEAT=$(cd "$(dirname -- "$0")" && pwd)
PL=$B.push.log; pr_exit_trap 'declare -F mint_cleanup >/dev/null && mint_cleanup; test -n "${KEEP:-}" || rm -f "$PL"'
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
( cd "$W" && python3 "$SEAT/gh_read.py" --git-retry git fetch -q origin main "$SRC" ) && step=reset \
  && git -C "$W" reset -q --hard "$TIP" && step=merge && git -C "$W" merge --no-edit -q origin/main
rc=$?
if [ "$rc" -ne 0 ]; then
  why="MERGE CONFLICT $PR"
  { [ "$step" = merge ] && [ -n "$(git -C "$W" diff --name-only --diff-filter=U)" ]; } || why="REMERGE FAILED $PR at $step (rc=$rc)"  # mut:remergeconflict
  git -C "$W" merge --abort 2>/dev/null || git -C "$W" reset -q --hard "$TIP" 2>/dev/null || :  # mut:remergeabort
  echo "$why"; exit 1
fi
if [ -n "$FORK" ]; then
  old=$(git -C "$W" rev-parse "$TIP")
  API=https://api.github.com; ACCEPT='Accept: application/vnd.github+json'
  die() { echo "REMERGE FAILED $PR at push (fork $FORK:$BR): $*"; exit 1; }
  # shellcheck source=../../pr/app_mint.sh
  MINT_NAME=remerge_main; MINT_TRAP=caller; . tools/pr/app_mint.sh
  mint_identity; mint_token "$R"
  curl -fsS -X PUT -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$R/pulls/$PR/update-branch" \
    --data "{\"expected_head_sha\":\"$old\"}" > "$PL" 2>&1 \
    || die "GitHub refused update-branch at the expected head $old ($(tail -1 "$PL" | cut -c1-200)); the fork must allow maintainer edits, or its owner merges main"
  new=$old
  for _ in $(seq 1 "${REMERGE_POLLS:-12}"); do
    new=$(curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$R/pulls/$PR" 2>/dev/null \
      | python3 -c 'import sys, json; print(json.load(sys.stdin)["head"]["sha"])' 2>/dev/null) || new=$old
    [ "$new" != "$old" ] && break
    sleep 5; done
  [[ $new =~ ^[0-9a-f]{40}$ ]] && [ "$new" != "$old" ] || die "the head did not move off $old after update-branch"
  ( cd "$W" && python3 "$SEAT/gh_read.py" --git-retry git fetch -q origin main "$SRC" ) || die "the new head $new could not be fetched"
  # The read-back: what GitHub made is the automatic merge and nothing else, or it is not PUSHED.
  read -r got p1 p2 p3 <<< "$(git -C "$W" rev-list --parents -n 1 "$TIP")"
  auto=no; { [ "$got" = "$new" ] && [ "$p1" = "$old" ] && [ -n "$p2" ] && [ -z "$p3" ] \
    && git -C "$W" rev-list --first-parent origin/main | grep -qx "$p2" \
    && [ "$(git -C "$W" merge-tree --write-tree "$old" "$p2" 2>/dev/null)" = "$(git -C "$W" rev-parse "$new^{tree}")" ]; } && auto=yes
  [ "$auto" = yes ] || die "the new head $new is not the automatic 2-parent merge of $old and main"  # mut:remergeforkback
  echo "RECARRY: fork head $FORK:$BR merged with main by GitHub's update-branch as the App, at the expected head $old; no prepr (no commit of ours is pushed)"
  echo "PUSHED $new to $FORK:$BR"; echo "RESULT pr=$PR head=$new"; exit 0
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
