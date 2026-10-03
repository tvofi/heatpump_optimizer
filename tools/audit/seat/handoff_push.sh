#!/bin/bash
# handoff_push.sh <handoff-topic> <code-sha-full> "<title>" [merge-main]
# DRAFT=1 (default) turns the PR into a draft; merge_pr.sh marks it ready. Pushes a handoff branch's code head as the hpo-author App with the handoff body,
# retitles the PR, adds the PR's own delivery row, fixes ## Head, and re-pushes. The orchestrator writes that
# row here because it is the seat that learns N (.claude/rules/delivery-status-tracking.md).
# Round 9 opened and updated PRs with open_pr.sh and update_pr.sh, its successors; this stays while
# docs/HANDOVER.md names it.
set -uo pipefail
TOPIC=$1; CODE=$2; TITLE=$3; MM=${4:-}
# The main checkout is the one this script's checkout shares its object store with; a PR's
# worktree is its sibling (HPO_WT_ROOT overrides); the body copy goes to the state directory.
R=tvofi/heatpump_optimizer; M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd) || exit 1
BR=${BRNAME:-fix/$TOPIC}; WT=${HPO_WT_ROOT:-$(dirname "$M")}/${BRNAME:-fix/$TOPIC}; WT=${WT/fix\//fix-}
B=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/bodies/$TOPIC-body.md; mkdir -p "$(dirname "$B")"
cd $M
git fetch -q origin "handoff/$TOPIC" || { echo "no handoff/$TOPIC"; exit 1; }
T="origin/handoff/$TOPIC"
git merge-base --is-ancestor "$CODE" "$T" || { echo "code head $CODE is not under $T"; exit 1; }
CODE=$(git rev-parse "$CODE")
git diff --name-only "$CODE" "$T" | grep -vqE '^(tools/audit/handoff/|handoff/)' && echo "note: tip adds non-handoff files over $CODE (a later main merge?) -- pushing the code head only"
# The body: BODY.md at the tip of the orphan ref handoff-body/$TOPIC (body_push.sh), else the legacy
# transport commit above the code head, until no open handoff carries one.
if git fetch -q origin "refs/heads/handoff-body/$TOPIC" 2>/dev/null; then
  git show FETCH_HEAD:BODY.md > "$B" || { echo "no BODY.md at handoff-body/$TOPIC"; exit 1; }
else
bf=${BODYPATH:-$(git diff --name-only "$CODE" "$T" | grep -iE "^(tools/audit/handoff|handoff)/.*body[^/]*\.md$")}; [ "$(echo "$bf" | grep -c .)" = 1 ] || { echo "no single body .md in: $(git diff --name-only "$CODE" "$T")"; exit 1; }
git show "${T}:${bf}" > "$B"
fi
python3 - "$B" <<'E'
import re,sys
p=sys.argv[1]; s=open(p).read()
s=re.sub(r'(?m)^_Requested by .*$','_Requested by **tvofi**_',s)
s=re.sub(r' ?\[[^\]]*\]\(https://claude\.ai/[^)]*\)','',s)
s=re.sub(r' ?https://claude\.ai/\S+','',s)
f=s.find('\n## Friction')
if f>=0:
    t=s.find('\n---\n',f)
    if t>=0:
        tail=s[t+5:].strip('\n'); s=s[:t].rstrip('\n')+'\n'
        h=s.find('\n## ')
        if tail: s=s[:h]+'\n\n'+tail+'\n'+s[h:]
s=re.sub(r'(?<![/\w])www/heatpump-optimizer-card\.js','custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js',s)
if not s.startswith('<!-- ccr-projects-attribution'): s='<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->\n'+s
open(p,'w').write(s)
E
# intended closes: the body's own "Fixes/Closes #N" lines (the reviewer verifies them), unless ISSUES is given
[ -z "${ISSUES:-}" ] && ISSUES=$(grep -oiE '\b(fixes|closes|resolves) #[0-9]+' "$B" | grep -oE '[0-9]+' | sort -u | tr '\n' ' ')
echo "intended closes: ${ISSUES:-none}"
if [ -d "$WT" ] && gh pr view "$BR" --json number >/dev/null 2>&1; then  # update an open PR to a new code head
  N=$(gh pr view "$BR" --json number --jq .number)
  ( cd "$WT" && git fetch -q origin "$BR" && git reset -q --hard "origin/$BR" && GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com git merge --no-edit -q "$CODE" && git fetch -q origin main && git merge --no-edit -q origin/main && { python3 tests/env_drift.py --drop-inherited "$(git rev-parse origin/main)" >/dev/null 2>&1; git diff --quiet || git commit -qam "claims: drop the claims main already carries after the main merge"; } ) || { echo "MERGE of $CODE (or main) into $BR failed"; exit 1; }
  H=$(git -C "$WT" rev-parse HEAD)
  python3 - "$B" "$H" "$CODE" "$N" <<'E3'
import sys
p,H,C,N=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
s=s[:i]+"`%s` merges the authored code head `%s` into this PR's previous head, which carried its own row `docs/delivery/%s.md`. The PR tree is that code head plus the row.\n\n"%(H,C,N)+s[i:]
open(p,'w').write(s)
E3
  PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} bash tools/audit/app_push.sh $R "$WT" "$BR" "$B" ${ISSUES:-} 2>&1 | grep -E 'REFUSE|PUSHED' | tail -2 | cut -c1-200
  gh pr edit $N --title "$TITLE" >/dev/null
  echo "RESULT pr=$N head=$H (update)"; exit 0
fi
if [ -d "$WT" ]; then git worktree remove --force "$WT"; git branch -D "$BR" >/dev/null 2>&1; fi  # a refused earlier attempt, no PR
git worktree add -q -b "$BR" "$WT" "$CODE" || exit 1
if [ -n "$MM" ]; then
  git fetch -q origin main
  ( cd "$WT" && GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com git merge --no-edit -q origin/main ) || { echo "MERGE CONFLICT merging origin/main"; exit 1; }
  ( cd "$WT" && python3 tests/env_drift.py --drop-inherited "$(git -C "$WT" rev-parse origin/main)" >/dev/null 2>&1; if ! git diff --quiet; then GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com git commit -qam "claims: drop the claims main already carries after the main merge"; fi )
  MH=$(git -C "$WT" rev-parse HEAD)
  python3 - "$B" "$MH" "$CODE" "$(git rev-parse origin/main)" <<'E2'
import sys
p,H,C,M=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
s=s[:i]+"`%s` merges origin/main `%s` into the authored head `%s`, with no hand resolution.\n\n"%(H,M[:8],C)+s[i:]
open(p,'w').write(s)
E2
fi
out=$(PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} bash tools/audit/app_push.sh $R "$WT" "$BR" "$B" ${ISSUES:-} 2>&1 | grep -E 'REFUSE|PUSHED' | tail -2); echo "$out" | cut -c1-200
N=$(echo "$out" | grep -oE 'pull request #[0-9]+' | head -1 | grep -oE '[0-9]+'); [ -n "$N" ] || exit 1
gh pr edit $N --title "$TITLE" >/dev/null
[ -n "${DRAFT:-1}" ] && gh pr ready $N --undo >/dev/null 2>&1
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
( cd "$WT" && echo "- [#$N](https://github.com/$R/pull/$N) — **open**, $TITLE" > docs/delivery/$N.md && git add docs/delivery/$N.md && git commit -qm "record: the delivery row for #$N" ) || exit 1
H=$(git -C "$WT" rev-parse HEAD)
python3 - "$B" "$H" "$CODE" "$N" <<'E'
import sys
p,H,C,N=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
s=s[:i]+"`%s` adds one commit to the previous head, containing only this PR's own row, `docs/delivery/%s.md`. The authored code head is `%s`.\n\n"%(H,N,C)+s[i:]
open(p,'w').write(s)
E
PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} bash tools/audit/app_push.sh $R "$WT" "$BR" "$B" ${ISSUES:-} 2>&1 | grep -E 'REFUSE|PUSHED' | tail -1 | cut -c1-200
echo "RESULT pr=$N head=$H"
