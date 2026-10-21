#!/bin/bash
# openpr.sh [--over-cap <reason>] <topic> <code-sha> <title> <group> [intended-issue...]: open a draft PR from handoff/<topic> as hpo-author,
# add its own delivery row, re-push, print N and the final head. Body from handoff-body/<topic>:BODY.md.
# The PR worktree and body live under $HPO_STATE_DIR/pr/<topic> (default ~/.local/state/hpo), and the
# seat venv seat_venv.sh builds there comes first on PATH.
# Successor of handoff_push.sh's open path: always merges origin/main, names the roster group in the row.
# The row is written and committed by delivery_row.sh's commit_row, the one
# function update_pr.sh's ensure_row also calls (its header says why).
# The arguments are checked before anything runs and every other stop reports
# itself (pr_args.sh: a body sha passed as the code sha once stopped this script
# silently). --self-test runs delivery_row.sh's self-test, then pr_args.sh's.
. "$(dirname -- "$0")/delivery_row.sh"; . "$(dirname -- "$0")/pr_args.sh"
[ "${1:-}" = --self-test ] && { bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
  bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }
PR_NAME=open_pr; pr_trap; unset GIT_AUTHOR_NAME; SEAT=$(cd "$(dirname -- "$0")" && pwd)
PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
# The open-PR soft cap (pr_cap.py; tvofi, 2026-10-18): --over-cap "<reason>" first overrides it.
OVER=; OVER_SET=; if [ "${1:-}" = --over-cap ]; then [ $# -ge 2 ] || pr_refuse "--over-cap needs a reason"; OVER=$2; OVER_SET=1; shift 2; fi
pr_need_args 4 $# "open_pr.sh [--over-cap <reason>] <topic> <code-sha> <title> <group> [intended-issue...]"
pr_code_sha_shape "$2"
export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd)
T=$1; C=$2; TITLE=$3; G=$4; shift 4; ISS="$*"
D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_optimizer
git -C "$M" show-ref -q --verify refs/heads/$BR && [ -z "${BR_FIXED:-}" ] && BR=$BR-pr  # a seat often holds a local branch of the default name
mkdir -p "$D"; cd "$M"
# The branch's lock, update_pr.sh's own, held to the end: cloud_relay's update_pr.sh detached this worktree
# between the two pushes below and left the PR without its row (#2547, #2548); it now answers BUSY.
pr_branch_lock "$(dirname -- "$D")/upd-${BR//\//-}.lock" "$BR" "$WT"  # mut:oplock
pr_handoff_tips "$T" 1
git fetch -q origin handoff/$T handoff-body/$T
pr_code_in_handoff "$C" "$T"
git cat-file -e "$PR_BT:BODY.md" 2>/dev/null || pr_refuse "handoff-body/$T ($PR_BT) holds no BODY.md"
git show "$PR_BT:BODY.md" > $D/body.md
if [ -n "$OVER_SET" ]; then python3 -I "$SEAT/pr_cap.py" gate --repo $R --over-cap "$OVER" || exit 1  # mut:capcall
else python3 -I "$SEAT/pr_cap.py" gate --repo $R || exit 1; fi  # mut:capcall
git worktree add -q -b $BR $WT $C
cd $WT
git fetch -q origin main; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com merge -q --no-edit origin/main
PYTHONPATH="$PRT" python3 - $D/body.md $(git rev-parse HEAD) $C $(git rev-parse --short origin/main) <<'E0'
import sys; from head_note import prefix
p,H,C,M=sys.argv[1:5]; s=open(p).read()
if H!=C: s=prefix(s,"`%s` merges origin/main `%s` into the authored code head `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below).\n\n"%(H,M,C))
open(p,'w').write(s)
E0
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1 || pr_push_failed $D/p1.log
N=$(grep -oE 'pull request #[0-9]+' $D/p1.log | head -1 | grep -oE '[0-9]+')
gh pr edit $N --title "$TITLE" >/dev/null; gh pr ready $N --undo >/dev/null 2>&1 || true
commit_row . $N "$(row_line $N $R "$TITLE" "$G")" >/dev/null
H=$(git rev-parse HEAD)
PYTHONPATH="$PRT" python3 - $D/body.md $H $N $C <<'E'
import sys; from head_note import prefix
p,H,N,C=sys.argv[1:5]; s=open(p).read()
s=prefix(s,"`%s` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/%s.md`. The authored code head is `%s`.\n\n"%(H,N,C))
open(p,'w').write(s)
E
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $D/body.md $ISS > $D/p2.log 2>&1 || pr_push_failed $D/p2.log
echo "PR=$N HEAD=$H AUTHOR=$(git log -1 --format='%an')"
