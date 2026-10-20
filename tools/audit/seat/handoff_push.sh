#!/bin/bash
# handoff_push.sh <handoff-topic> <code-sha-full> "<title>" [merge-main]
# DRAFT=1 (default) turns the PR into a draft; merge_pr.sh marks it ready. Pushes a handoff branch's code head as the hpo-author App with the handoff body,
# retitles the PR, adds the PR's own delivery row, fixes ## Head, and re-pushes. The orchestrator writes that
# row here because it is the seat that learns N (dev/governance/rules/delivery-status-tracking.md).
# Round 9 opened and updated PRs with open_pr.sh and update_pr.sh, its successors; this stays while
# dev/programme/HANDOVER.md names it.
# --self-test runs delivery_row.sh's self-test and this script's own offline
# one: the three push calls are driven over a scratch origin with a stub
# app_push, so a push line replaced by `true` reddens it (#2444).
set -uo pipefail
PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
# The row is written and committed by delivery_row.sh (commit_row, ensure_row), the one
# writer open_pr.sh and update_pr.sh also source; its self-test is this script's.
. "$(dirname -- "$0")/delivery_row.sh"

# The three push calls' own fixtures (#2444's fourth forward-carry). A scratch
# origin carries handoff/g (open) and handoff/h (update, with fix/h on origin);
# the clone holds this script, the row writer and head_note.py, and its
# tools/pr/app_push.sh is a stub that records every call. The open path must
# push twice -- the pull request, then its row -- and the update path once.
# This self-test copies THIS file into the clone, so the mutant proof is a
# push line replaced by `true` in the real file: the null control then finds
# a call missing and the step exits 1.
handoff_push_self_test() (
  local src t f=0 n=0 o m code base body i
  src=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  t=$(mktemp -d) || { echo "handoff_push self-test: no temporary directory"; return 1; }
  . "$src/../../../tests/throwaway_git.sh" && throwaway_git_env
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  o=$t/o; m=$t/m
  { throwaway_git_init "$o" -q -b main \
    && printf 'a\n' > "$o/a" && git -C "$o" add a && git -C "$o" commit -q -m base \
    && base=$(git -C "$o" rev-parse HEAD) \
    && printf 'b\n' > "$o/b" && git -C "$o" add b && git -C "$o" commit -q -m code \
    && code=$(git -C "$o" rev-parse HEAD) \
    && git -C "$o" branch handoff/g "$code" && git -C "$o" branch handoff/h "$code" \
    && git -C "$o" branch fix/h "$base" \
    && printf '## Head\n\nthe body\n' > "$t/body.md" \
    && body=$(git -C "$o" commit-tree "$(printf '100644 blob %s\tBODY.md\n' \
         "$(git -C "$o" hash-object -w "$t/body.md")" | git -C "$o" mktree)" -m "body") \
    && git -C "$o" update-ref refs/heads/handoff-body/g "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/h "$body" \
    && throwaway_git_clone -q "$o" "$m" \
    && mkdir -p "$m/tools/audit/seat" "$m/tools/pr" "$t/bin" \
    && cp "$src/handoff_push.sh" "$src/delivery_row.sh" "$m/tools/audit/seat/" \
    && cp "$src/../../pr/head_note.py" "$m/tools/pr/head_note.py" \
    && printf '#!/bin/bash\nprintf "%%s\\n" "$*" >> "$PUSH_LOG"\necho "PUSHED pull request #42"\n' > "$m/tools/pr/app_push.sh" \
    && chmod +x "$m/tools/pr/app_push.sh" \
    && printf '#!/bin/bash\ncase "$*" in\n  "pr view "*"--json number --jq .number") [ -e "$PR_EXISTS" ] && echo 42 || exit 1 ;;\n  "pr view "*"--json number") [ -e "$PR_EXISTS" ] && echo 42 || exit 1 ;;\n  "pr edit "*|"pr ready "*) exit 0 ;;\n  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;\nesac\n' > "$t/bin/gh" \
    && chmod +x "$t/bin/gh"; } || { echo "  FAIL fixture"; rm -rf "$t"; return 1; }
  # run <open|update>: a fresh state and worktree root per case; the clone's
  # copy of this file is the program under test.
  run() {
    i=$((i + 1))
    local wr=$t/wt$i st=$t/st$i topic=g exists=$t/no-pr w
    [ "$1" = update ] && { topic=h; exists=$t/pr-exists; }
    rm -rf "$wr" "$st"; mkdir -p "$wr" "$st" "$m/tools/audit/seat"
    for w in $(git -C "$m" worktree list --porcelain | awk '/^worktree /{print $2}' | grep -vxF "$m"); do
      git -C "$m" worktree remove --force "$w" 2>/dev/null
    done
    git -C "$m" branch -D "fix/$topic" >/dev/null 2>&1
    cp "$src/handoff_push.sh" "$src/delivery_row.sh" "$m/tools/audit/seat/"
    [ "$topic" = h ] && git -C "$m" worktree add -q -b fix/h "$wr/fix-h" origin/fix/h
    [ "$exists" = "$t/pr-exists" ] && : > "$exists"
    : > "$t/push"
    HPO_STATE_DIR=$st HPO_WT_ROOT=$wr PATH="$t/bin:$PATH" PUSH_LOG=$t/push \
      PR_EXISTS=$exists bash "$m/tools/audit/seat/handoff_push.sh" "$topic" "$code" "a title" \
      > "$t/out" 2>&1
    echo $? > "$t/rc"
  }
  run open
  [ "$(cat "$t/rc")" = 0 ] && [ "$(wc -l < "$t/push" | tr -d ' ')" = 2 ] \
    && grep -q 'RESULT pr=42 head=' "$t/out"
  ck "null control: the open path pushes the pull request, then its row" $?
  run update
  [ "$(cat "$t/rc")" = 0 ] && [ "$(wc -l < "$t/push" | tr -d ' ')" = 1 ] \
    && grep -q 'RESULT pr=42' "$t/out"
  ck "null control: the update path pushes its head once" $?
  rm -rf "$t"
  echo "handoff_push self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

if [ "${1:-}" = --self-test ]; then
  bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
  handoff_push_self_test; h=$?
  [ "$r" = 0 ] && [ "$h" = 0 ]; exit $?
fi
TOPIC=$1; CODE=$2; TITLE=$3; MM=${4:-}
# The main checkout is the one this script's checkout shares its object store with; a PR's
# worktree is its sibling (HPO_WT_ROOT overrides); the body copy goes to the state directory.
R=tvofi/heatpump_optimizer; M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd) || exit 1
BR=${BRNAME:-fix/$TOPIC}; WT=${HPO_WT_ROOT:-$(dirname "$M")}/${BRNAME:-fix/$TOPIC}; WT=${WT/fix\//fix-}
B=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/bodies/$TOPIC-body.md; mkdir -p "$(dirname "$B")"
cd $M
# The App push, resolved once (the three calls were two lines each before
# #2444's seam): the live pusher, behind the pre-move location a checkout may
# still carry (tests/layout.json maps that path to this one).
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
push_app() { # <tail count>: the push, filtered to its REFUSE/PUSHED lines
  PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=${PREPR_SKIP_CLOSURES:-} \
    bash "$_push" $R "$WT" "$BR" "$B" ${ISSUES:-} 2>&1 \
    | grep -E 'REFUSE|PUSHED' | tail -"$1" | cut -c1-200
}
git fetch -q origin "handoff/$TOPIC" || { echo "no handoff/$TOPIC"; exit 1; }
T="origin/handoff/$TOPIC"
git merge-base --is-ancestor "$CODE" "$T" || { echo "code head $CODE is not under $T"; exit 1; }
CODE=$(git rev-parse "$CODE")
git diff --no-renames --name-only "$CODE" "$T" | grep -vqE '^handoff/' && echo "note: tip adds non-handoff files over $CODE (a later main merge?) -- pushing the code head only"
# The body: BODY.md at the tip of the orphan ref handoff-body/$TOPIC (body_push.sh), else the legacy
# transport commit above the code head, until no open handoff carries one.
# The body is read from the sha origin ANSWERED for the ref, never FETCH_HEAD.
# This runs in the MAIN checkout, where fetches are constant, so an intervening
# fetch -- another seat publishing its own body -- makes `git show
# FETCH_HEAD:BODY.md` publish ANOTHER TOPIC'S body as this pull request's
# (R9-RC-BUS-FETCHHEAD: the predicate bus.sh carried, with a wrong artifact
# instead of a refusal).
tip=$(git ls-remote origin "refs/heads/handoff-body/$TOPIC" 2>/dev/null | awk 'NF { print $1; exit }') || tip=""
if [ -n "$tip" ] && git fetch -q origin "refs/heads/handoff-body/$TOPIC" 2>/dev/null; then
  git show "$tip:BODY.md" > "$B" || { echo "no BODY.md at handoff-body/$TOPIC"; exit 1; }
else
bf=${BODYPATH:-$(git diff --no-renames --name-only "$CODE" "$T" | grep -iE "^(tools/audit/handoff|handoff)/.*body[^/]*\.md$")}; [ "$(echo "$bf" | grep -c .)" = 1 ] || { echo "no single body .md in: $(git diff --no-renames --name-only "$CODE" "$T")"; exit 1; }  # layout:old=tools/audit/handoff (a transport root prepr.sh still reads)
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
  # A previous head with no row (a refused second push below) gains it here, or it never would.
  _added=$(ensure_row "$WT" "$N" "$(row_line "$N" $R "$TITLE")") || { echo "ROW commit for #$N failed"; exit 1; }
  H=$(git -C "$WT" rev-parse HEAD)
  PYTHONPATH="$PRT" python3 - "$B" "$H" "$CODE" "$N" "$_added" <<'E3'
import sys; from head_note import prefix
p,H,C,N,A=sys.argv[1:6]; s=open(p).read()
how="then adds one commit containing only its own row" if A else "which carried its own row"
s=prefix(s,"`%s` merges the authored code head `%s` into this PR's previous head, %s `dev/programme/delivery/%s.md`. The PR tree is that code head plus the row.\n\n"%(H,C,how,N))
open(p,'w').write(s)
E3
  push_app 2  # mut:push-update
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
  PYTHONPATH="$PRT" python3 - "$B" "$MH" "$CODE" "$(git rev-parse origin/main)" <<'E2'
import sys; from head_note import prefix
p,H,C,M=sys.argv[1:5]; s=open(p).read()
s=prefix(s,"`%s` merges origin/main `%s` into the authored head `%s`, with no hand resolution.\n\n"%(H,M[:8],C))
open(p,'w').write(s)
E2
fi
out=$(push_app 2)  # mut:push-open
echo "$out" | cut -c1-200
N=$(echo "$out" | grep -oE 'pull request #[0-9]+' | head -1 | grep -oE '[0-9]+'); [ -n "$N" ] || exit 1
gh pr edit $N --title "$TITLE" >/dev/null
[ -n "${DRAFT:-1}" ] && gh pr ready $N --undo >/dev/null 2>&1
export GIT_AUTHOR_NAME=tvofi GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=tvofi GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com
commit_row "$WT" "$N" "$(row_line "$N" $R "$TITLE")" >/dev/null || exit 1
H=$(git -C "$WT" rev-parse HEAD)
PYTHONPATH="$PRT" python3 - "$B" "$H" "$CODE" "$N" <<'E'
import sys; from head_note import prefix
p,H,C,N=sys.argv[1:5]; s=open(p).read()
s=prefix(s,"`%s` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/%s.md`. The authored code head is `%s`.\n\n"%(H,N,C))
open(p,'w').write(s)
E
push_app 1  # mut:push-row
echo "RESULT pr=$N head=$H"
