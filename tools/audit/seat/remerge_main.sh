#!/bin/bash
# remerge_main.sh <pr> <worktree> <branch> <body>: merge origin/main into an open PR (claimnotes driver), drop inherited claims, push as the App
#
# The note it prefixes under the body's `## Head` says what happened and nothing
# more: an automatic merge by the orchestrator, with no resolution, so the
# reviewed code is unchanged. Set REMERGE_WHY to add the occasion in one clause
# (for example "GitHub reported a claim-file conflict it cannot resolve without
# the claimnotes driver"); the default states none. merge_train.py calls this.
# The worktree may be detached: it is reset to origin/<branch> before the merge.
set -uo pipefail
PR=$1; W=$2; BR=$3; B=$4; shift 4
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
( cd "$W" && git fetch -q origin main "$BR" && git reset -q --hard "origin/$BR" && git merge --no-edit -q origin/main ) || { echo "MERGE CONFLICT $PR"; exit 1; }
( cd "$W" && python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge" )
H=$(git -C "$W" rev-parse HEAD); M=$(git -C "$W" rev-parse --short origin/main)
python3 - "$B" "$H" "$M" "${REMERGE_WHY:-}" <<'E'
import sys
p,H,M,why=sys.argv[1:5]; s=open(p).read()
i=s.index('\n',s.index('## Head'))+1
while s[i:i+1]=='\n': i+=1
why=" (%s)"%why if why else ""
s=s[:i]+"`%s` merges main `%s` into the previous head: an automatic merge by the orchestrator, no resolution%s. The reviewed code is unchanged.\n\n"%(H,M,why)+s[i:]
open(p,'w').write(s)
E
ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')
# shellcheck disable=SC2086 # $ISS is a word list of issue numbers
# Every REFUSE line, not the last 120 characters. app_push's die is the last
# line and does not name the prepr step; the step line is the one before it.
# tail -1 | cut -c1-120 kept only the die (measured on #1974 and #1975).
push_out=$(PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tools/audit/app_push.sh tvofi/heatpump_optimizer "$W" "$BR" "$B" $ISS 2>&1 || true)
printf '%s\n' "$push_out" | grep -E 'REFUSE|PUSHED' || true
sleep 5; echo "RESULT pr=$PR head=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)"
