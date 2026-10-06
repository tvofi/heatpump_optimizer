#!/bin/bash
# openpr.sh <topic> <code-sha> <title> <group> [intended-issue...]: open a draft PR from handoff/<topic> as hpo-author,
# add its own delivery row, re-push, print N and the final head. Body from handoff-body/<topic>:BODY.md.
# The PR worktree and body live under $HPO_STATE_DIR/pr/<topic> (default ~/.local/state/hpo), and the
# seat venv seat_venv.sh builds there comes first on PATH.
# Successor of handoff_push.sh's open path: always merges origin/main, names the roster group in the row.
set -eo pipefail; unset GIT_AUTHOR_NAME
export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd)
T=$1; C=$2; TITLE=$3; G=$4; shift 4; ISS="$*"
D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_optimizer
git -C "$M" show-ref -q --verify refs/heads/$BR && [ -z "${BR_FIXED:-}" ] && BR=$BR-pr  # a seat often holds a local branch of the default name
mkdir -p "$D"; cd "$M"
git fetch -q origin handoff/$T handoff-body/$T
git merge-base --is-ancestor $C origin/handoff/$T
git show origin/handoff-body/$T:BODY.md > $D/body.md
git worktree add -q -b $BR $WT $C
cd $WT
git fetch -q origin main; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com merge -q --no-edit origin/main
python3 - $D/body.md $(git rev-parse HEAD) $C $(git rev-parse --short origin/main) <<'E0'
import sys
p,H,C,M=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
if H!=C: s=s[:i]+"`%s` merges origin/main `%s` into the authored code head `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below).\n\n"%(H,M,C)+s[i:]
open(p,'w').write(s)
E0
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub if test -f tools/audit/app_push.sh; then bash tools/audit/app_push.sh $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1; else bash tools/pr/app_push.sh $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1; fi|| { grep -E 'REFUSE' $D/p1.log; exit 1; }
N=$(grep -oE 'pull request #[0-9]+' $D/p1.log | head -1 | grep -oE '[0-9]+')
gh pr edit $N --title "$TITLE" >/dev/null; gh pr ready $N --undo >/dev/null 2>&1 || true
printf -- '- [#%s](https://github.com/%s/pull/%s) — **open**, %s (%s)\n' $N $R $N "$TITLE" "$G" > docs/delivery/$N.md
git add docs/delivery/$N.md
git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com commit -q --author='tvofi <70032254+tvofi@users.noreply.github.com>' -m "record: the delivery row for #$N

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
H=$(git rev-parse HEAD)
python3 - $D/body.md $H $N $C <<'E'
import sys
p,H,N,C=sys.argv[1:5]; s=open(p).read()
i=s.index('## Head\n\n')+len('## Head\n\n')
s=s[:i]+"`%s` adds one commit to the previous head, containing only this PR's own row, `docs/delivery/%s.md`. The authored code head is `%s`.\n\n"%(H,N,C)+s[i:]
open(p,'w').write(s)
E
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub if test -f tools/audit/app_push.sh; then bash tools/audit/app_push.sh $R $WT $BR $D/body.md $ISS > $D/p2.log 2>&1; else bash tools/pr/app_push.sh $R $WT $BR $D/body.md $ISS > $D/p2.log 2>&1; fi|| { grep -E 'REFUSE' $D/p2.log; exit 1; }
echo "PR=$N HEAD=$H AUTHOR=$(git log -1 --format='%an')"
