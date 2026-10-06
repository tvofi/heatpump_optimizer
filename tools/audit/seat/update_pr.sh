#!/bin/bash
# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main (merge),
# prefix ## Head with what happened, push as hpo-author. Prints HEAD. Uses a private worktree
# $HPO_STATE_DIR/pr/upd-<branch> (default ~/.local/state/hpo); PATH as open_pr.sh's.
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
M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
[ "$(git log -1 --format=%an)" = tvofi ] || { echo "author wrong"; exit 1; }
python3 - $B $H "$NOTE" $M <<'E'
import sys
p,H,N,M=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head.\n\n"%M
s=s[:i]+pre+s[i:]; open(p,'w').write(s)
E
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub if test -f tools/audit/app_push.sh; then bash tools/audit/app_push.sh $R $WT $BR $B $ISS > $WT.log 2>&1; else bash tools/pr/app_push.sh $R $WT $BR $B $ISS > $WT.log 2>&1; fi|| { grep REFUSE $WT.log; exit 1; }
echo "HEAD=$H"
