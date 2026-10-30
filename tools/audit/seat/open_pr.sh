#!/bin/bash
# openpr.sh [--over-cap <reason>] <topic> <code-sha> <title> <group> [intended-issue...]: open a draft PR from handoff/<topic> as hpo-author,
# add its own delivery row, re-push, print N and the final head. Body from handoff-body/<topic>:BODY.md.
# The PR worktree and body live under $HPO_STATE_DIR/pr/<topic> (default ~/.local/state/hpo), and the
# seat venv seat_venv.sh builds there comes first on PATH.
# Successor of handoff_push.sh's open path: always merges origin/main, names the roster group in the row.
# The row push (p2) asks app_push.sh for --row-only, so an open runs one full prepr, not two (P53),
# and lands seconds after the PR rather than a prepr later, before CI on p1 can report a red the body
# was never asked to answer (#2625, #2629). A refused row push returns the worktree to the pushed head
# and closes the PR with a comment saying why, so no PR stays open without its row (CLOSED; a close
# that fails says ROWLESS, and update_pr.sh's ensure_row adds the row). Every exit's last act,
# under the branch lock, is pr_release_wt (pr_args.sh): the worktree is detached at the pushed head,
# removed with its branch when origin never had it, or kept and named (P-D, P64, P72).
# The tools are refused when origin/main is ahead of their checkout under tools/ (pr_tools_fresh).
# The row is written and committed by delivery_row.sh's commit_row, the one
# function update_pr.sh's ensure_row also calls (its header says why).
# The arguments are checked before anything runs and every other stop reports
# itself (pr_args.sh: a body sha passed as the code sha once stopped this script
# silently). --self-test runs delivery_row.sh's self-test, then pr_args.sh's.
. "$(dirname -- "$0")/delivery_row.sh"; . "$(dirname -- "$0")/pr_args.sh"
[ "${1:-}" = --self-test ] && { bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
  bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }
PR_NAME=open_pr; pr_trap; unset GIT_AUTHOR_NAME; SEAT=$(cd "$(dirname -- "$0")" && pwd)
pr_exit_trap  # every exit, a stop signal's included, ends the tree this run started
PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
# The soft cap gates DISPATCH, not opening (pr_cap.py; tvofi, 2026-10-20):
# opening is how work leaves work-in-progress. --over-cap "<reason>" is still
# accepted so existing callers do not break; it says it is advisory and is
# otherwise ignored. The open count below is information.
OVER=; OVER_SET=; if [ "${1:-}" = --over-cap ]; then [ $# -ge 2 ] || pr_refuse "--over-cap needs a reason"; OVER=$2; OVER_SET=1; shift 2; fi
[ -z "$OVER_SET" ] || printf '%s: --over-cap is advisory: %s (the cap gates dispatch, not opening)\n' "$PR_NAME" "$OVER" >&2  # mut:overadvisory
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
PR_TIDY='pr_release_wt "$WT" "$BR" "${PR_PUSHED:-}"'  # set once the lock is this run's: a BUSY exit touches nothing
pr_handoff_tips "$T" 1
# The attempt is the ledger's (R10-ORCH-LEDGER): `started` now, and on every exit, a stop
# signal's included, `opened,PR=<n>` or `unopened` (bash's $? in an EXIT trap after a TERM is the
# last command's, so it names no signal), so a killed opener shows on its handoff-no-pr line.
python3 -I "$SEAT/ledger.py" attempt "refs/heads/handoff/$T" "$PR_HT" started || true
pr_exit_trap 'python3 -I "$SEAT/ledger.py" attempt "refs/heads/handoff/$T" "$PR_HT" "${PR_ATTEMPT:-unopened}" || :'
git fetch -q origin handoff/$T handoff-body/$T main
pr_tools_fresh
pr_code_in_handoff "$C" "$T"
git cat-file -e "$PR_BT:BODY.md" 2>/dev/null || pr_refuse "handoff-body/$T ($PR_BT) holds no BODY.md"
git show "$PR_BT:BODY.md" > $D/body.md
python3 -I "$SEAT/pr_cap.py" info --repo $R  # mut:openinfo
git worktree add -q -b $BR $WT $C
cd $WT
git fetch -q origin main; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com merge -q --no-edit origin/main
PYTHONPATH="$PRT" python3 - $D/body.md $(git rev-parse HEAD) $C $(git rev-parse --short origin/main) <<'E0'
import sys; from head_note import prefix
p,H,C,M=sys.argv[1:5]; s=open(p).read()
if H!=C: s=prefix(s,"`%s` merges origin/main `%s` into the authored code head `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below).\n\n"%(H,M,C))
open(p,'w').write(s)
E0
# A disposed `## Unpinned sites` key the merge only shifted is re-keyed in place (P70, P125): prepr's
# step 7d, inside the push below, then reads the moved line; anything else it still refuses.
python3 "$PRT/ci_predict.py" --rekey-body $D/body.md --from $C || echo "open_pr: the unpinned-site re-key did not run; prepr reads the body as written" >&2
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
# Asynchronous, so a stop signal interrupts the `wait` and the EXIT trap reaps
# the tree (pr_args.sh's why).
{ pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $D/body.md $ISS > $D/p1.log 2>&1 & } 9>>"${PR_PUSH_LOCK:-/dev/null}"
pr_wait $! $D/p1.log
PR_PUSHED=$(git rev-parse HEAD)
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
RO=--row-only  # mut:oprowonly
{ pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $RO $R $WT $BR $D/body.md $ISS > $D/p2.log 2>&1 & } 9>>"${PR_PUSH_LOCK:-/dev/null}"
rc=0; wait $! || rc=$?
if [ "$rc" != 0 ]; then
  git reset -q --hard "$PR_PUSHED"  # mut:rowreset
  # A PR the row push left without its row is closed, not left open for the tick to find (#2625,
  # #2629): its comment, read back by gh_comment.py, says why; re-running open_pr.sh once the body
  # answers the refusal opens it afresh. Only a close that fails leaves it ROWLESS and open.
  { grep -E 'REFUSE' $D/p2.log || tail -n 20 $D/p2.log; } > $D/p2.why 2>/dev/null || :
  printf 'Closed by open_pr.sh: the push of this pull request'\''s own delivery row (`dev/programme/delivery/%s.md`) was refused, so it would stay open without its row. The refusal:\n\n```\n%s\n```\n\nRe-run `open_pr.sh %s` once the handoff body answers it.\n' \
    "$N" "$(cat $D/p2.why)" "$T" > $D/close.md
  python3 "$PRT/gh_comment.py" post --repo $R --issue "$N" --body-file $D/close.md >&2 \
    || echo "$PR_NAME: the closing comment on #$N was not read back; the close goes ahead" >&2
  closed=0; gh pr close "$N" -R $R >/dev/null && closed=1  # mut:rowclose
  if [ "$closed" = 1 ]; then
    PR_ATTEMPT=closed,PR=$N
    printf '%s: CLOSED: #%s at %s, its row push refused; re-run open_pr.sh once the body answers it\n' "$PR_NAME" "$N" "$PR_PUSHED" >&2
  else
    printf '%s: ROWLESS: #%s is open at %s without its row, and closing it failed; update_pr.sh %s - <body> adds it (delivery_row.sh ensure_row)\n' "$PR_NAME" "$N" "$PR_PUSHED" "$BR" >&2
  fi
  pr_push_failed $D/p2.log
fi
PR_PUSHED=$H
PR_ATTEMPT=opened,PR=$N
echo "PR=$N HEAD=$H AUTHOR=$(git log -1 --format='%an')"
