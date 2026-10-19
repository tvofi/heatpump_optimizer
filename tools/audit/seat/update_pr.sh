#!/bin/bash
# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main (merge),
# prefix ## Head with what happened, push as hpo-author. Prints HEAD. Uses a private worktree
# $HPO_STATE_DIR/pr/upd-<branch> (default ~/.local/state/hpo); PATH as open_pr.sh's.
# A head without the PR's own delivery row gains it (delivery_row.sh's ensure_row, open_pr.sh's
# commit): open_pr.sh writes it only after its first push, so a refused second push left a PR with
# none (#2390, #2391). The PR number is read from GitHub for the branch, or PR_N overrides it.
# Checks as open_pr.sh's (pr_args.sh), before anything runs: a code sha other than `-` must be
# 40-hex and inside origin/handoff/<topic>, the topic being HANDOFF_TOPIC, else the branch less
# `fix/` and then less `-pr` (the first that origin holds). The body is a file here, so a missing
# handoff-body/<topic> is no refusal; its tip is what names a body sha as one.
# --self-test runs delivery_row.sh's self-test, then pr_args.sh's.
. "$(dirname -- "$0")/delivery_row.sh"; . "$(dirname -- "$0")/pr_args.sh"
[ "${1:-}" = --self-test ] && { bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
  bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }
PR_NAME=update_pr; pr_trap; unset GIT_AUTHOR_NAME; export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
pr_need_args 3 $# "update_pr.sh <branch> <code-sha|-> <body-file> [issues...]"
[ "$2" = - ] || pr_code_sha_shape "$2"
[ -f "$3" ] || pr_refuse "no body file at $3"
M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd); P=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr; mkdir -p "$P"
BR=$1; C=$2; B=$3; shift 3; ISS="$*"; R=tvofi/heatpump_optimizer
WT=$P/upd-${BR//\//-}
cd "$M"
if [ "$C" != - ]; then
  T=${HANDOFF_TOPIC:-${BR#fix/}}
  [ -n "${HANDOFF_TOPIC:-}" ] || [ -n "$(git ls-remote origin "refs/heads/handoff/$T")" ] || [ "$T" = "${T%-pr}" ] || T=${T%-pr}  # mut:prtopic
  pr_handoff_tips "$T" 0
  git fetch -q origin "refs/heads/handoff/$T"
  pr_code_in_handoff "$C" "$T"
fi
git fetch -q origin "$BR" main
OWN=$(git worktree list | grep -F "[$BR]" | awk '{print $1}' | grep "^$P/" || true); for o in $OWN; do [ "$o" = "$WT" ] || { [ -z "$(git -C $o status --porcelain)" ] && git -C $o checkout -q --detach; }; done
git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && { echo "branch $BR checked out elsewhere: $(git worktree list | grep -F "[$BR]")"; exit 1; }
[ -d $WT ] && git worktree remove --force $WT
git worktree add -q -B "$BR" $WT origin/$BR; cd $WT
G="git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com"
NOTE=""
if [ "$C" != "-" ]; then $G merge -q --no-edit $C; NOTE="merges the authored code head \`$C\`"; fi
OLD=$(git rev-parse HEAD)
$G merge -q --no-edit origin/main
N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}
[ -n "$N" ] || { echo "no open pull request at $BR, so no row to check"; exit 1; }
# ensure_row's own guard decides; its output names the row only when it added one.
# The title first, in an assignment: a failing `gh` inside an argument stops nothing.
TTL=$(gh pr view "$N" -R $R --json title -q .title)
_added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
[ "$(git log -1 --format=%an)" = tvofi ] || { echo "author wrong"; exit 1; }
PYTHONPATH="$PRT" python3 - $B $H "$NOTE" $M "$ROW" <<'E'
import sys; from head_note import prefix
p,H,N,M,R=sys.argv[1:6]; s=open(p).read()
pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head"%M + ((", and then "+R) if R else "") + ".\n\n"
s=prefix(s,pre); open(p,'w').write(s)
E
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $B $ISS > $WT.log 2>&1 || pr_push_failed $WT.log
echo "HEAD=$H"
