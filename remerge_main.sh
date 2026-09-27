#!/bin/bash
# remerge_main.sh <pr> <worktree> <branch> <body>: merge origin/main into an open PR (claimnotes driver), drop inherited claims, push as the App
set -uo pipefail
PR=$1; W=$2; BR=$3; B=$4; shift 4
cd /Users/timmalmstrom/heatpump_optimizer
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
( cd $W && git fetch -q origin main $BR && git reset -q --hard origin/$BR && git merge --no-edit -q origin/main ) || { echo "MERGE CONFLICT $PR"; exit 1; }
( cd $W && python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge" )
H=$(git -C $W rev-parse HEAD); M=$(git rev-parse --short origin/main)
python3 - "$B" "$H" "$M" <<'E'
import sys
p,H,M=sys.argv[1:4]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
s=s[:i]+"`%s` merges main `%s` into the previous head (a claim-file conflict for GitHub, which cannot run the claimnotes driver; clean locally). The reviewed code is unchanged.\n\n"%(H,M)+s[i:]
open(p,'w').write(s)
E
ISS=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')
PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tools/audit/app_push.sh tvofi/heatpump_optimizer $W $BR $B $ISS 2>&1 | grep -E 'REFUSE|PUSHED' | tail -1 | cut -c1-120
sleep 5; echo "RESULT pr=$PR head=$(gh pr view $PR --json headRefOid --jq .headRefOid)"
