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
# The worktree may be detached: it is reset to origin/<branch> before the merge.
set -uo pipefail
PR=$1; W=$2; BR=$3; B=$4; shift 4
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
( cd "$W" && git fetch -q origin main "$BR" && git reset -q --hard "origin/$BR" && git merge --no-edit -q origin/main ) || { echo "MERGE CONFLICT $PR"; exit 1; }
( cd "$W" && python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge" )
ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')
# shellcheck disable=SC2086 # $ISS is a word list of issue numbers
# Every REFUSE line, not the last 120 characters. app_push's die is the last
# line and does not name the prepr step; the step line is the one before it.
# tail -1 | cut -c1-120 kept only the die (measured on #1974 and #1975).
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
push_out=$(PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash "$_push" --recarry tvofi/heatpump_optimizer "$W" "$BR" "$B" $ISS 2>&1 || true)
printf '%s\n' "$push_out" | grep -E 'RECARRY|REFUSE|PUSHED' || true
sleep 5; echo "RESULT pr=$PR head=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)"
