#!/bin/bash
# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main (merge),
# prefix ## Head with what happened, push as hpo-author. Prints HEAD. Uses a private worktree
# $HPO_STATE_DIR/pr/upd-<branch> (default ~/.local/state/hpo); PATH as open_pr.sh's.
# A head without the PR's own delivery row gains it (delivery_row.sh's ensure_row, open_pr.sh's
# commit): open_pr.sh writes it only after its first push, so a refused second push left a PR with
# none (#2390, #2391). The PR number is read from GitHub for the branch, or PR_N overrides it.
. "$(dirname -- "$0")/delivery_row.sh"
[ "${1:-}" = --self-test ] && exec bash "$(dirname -- "$0")/delivery_row.sh" --self-test
set -eo pipefail; unset GIT_AUTHOR_NAME; export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd); P=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr; mkdir -p "$P"
BR=$1; C=$2; B=$3; shift 3; ISS="$*"; R=tvofi/heatpump_optimizer
WT=$P/upd-${BR//\//-}
cd "$M"; git fetch -q origin "$BR" main
OWN=$(git worktree list | grep -F "[$BR]" | awk '{print $1}' | grep "^$P/" || true); for o in $OWN; do [ "$o" = "$WT" ] || { [ -z "$(git -C $o status --porcelain)" ] && git -C $o checkout -q --detach; }; done
git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && { echo "branch $BR checked out elsewhere: $(git worktree list | grep -F "[$BR]")"; exit 1; }
[ -d $WT ] && git worktree remove --force $WT
git worktree add -q -B "$BR" $WT origin/$BR; cd $WT
G="git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com"
NOTE=""
if [ "$C" != "-" ]; then git fetch -q origin "$C" 2>/dev/null || true; $G merge -q --no-edit $C; NOTE="merges the authored code head \`$C\`"; fi
OLD=$(git rev-parse HEAD)
$G merge -q --no-edit origin/main
N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}
[ -n "$N" ] || { echo "no open pull request at $BR, so no row to check"; exit 1; }
# ensure_row's own guard decides; its output names the row only when it added one.
_added=$(ensure_row . "$N" "$(row_line "$N" $R "$(gh pr view "$N" -R $R --json title -q .title)")")
ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
[ "$(git log -1 --format=%an)" = tvofi ] || { echo "author wrong"; exit 1; }
python3 - $B $H "$NOTE" $M "$ROW" <<'E'
import sys
p,H,N,M,R=sys.argv[1:6]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head"%M + ((", and then "+R) if R else "") + ".\n\n"
s=s[:i]+pre+s[i:]; open(p,'w').write(s)
E
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $B $ISS > $WT.log 2>&1 || { grep REFUSE $WT.log; exit 1; }
echo "HEAD=$H"
