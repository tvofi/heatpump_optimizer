#!/bin/bash
# updatepr.sh <branch> <code-sha|-> <body-file> [issues...]: bring the PR branch to: its current head + code-sha (merge) + origin/main
# (merged only when the PR is DIRTY or `git merge-tree --write-tree origin/main HEAD` conflicts: ruling R4, K12),
# prefix ## Head with what happened, push as hpo-author. Prints HEAD. Uses a private worktree
# $HPO_STATE_DIR/pr/upd-<branch> (default ~/.local/state/hpo); PATH as open_pr.sh's.
# A head without the PR's own delivery row gains it (delivery_row.sh's ensure_row, open_pr.sh's
# commit): open_pr.sh writes it only after its first push, so a refused second push left a PR with
# none (#2390, #2391). The PR number is read from GitHub for the branch, or PR_N overrides it.
# Checks as open_pr.sh's (pr_args.sh), before anything runs: a code sha other than `-` must be
# 40-hex and inside origin/handoff/<topic>, the topic being HANDOFF_TOPIC, else the branch less
# `fix/` and then less `-pr` (the first that origin holds). The body is a file here, so a missing
# handoff-body/<topic> is no refusal; its tip is what names a body sha as one.
# One run per branch, open_pr.sh's included (pr_args.sh's pr_branch_lock): a second run while one holds
# the branch's lock ($WT.lock) exits 75, BUSY, having changed nothing (cloud_relay.sh retries it on its next pass); no
# other stop exits 75. A stopped (TERM/INT/HUP, to the run or its whole group) run reaps its push's whole tree and ends
# (pr_args.sh's pr_exit_trap); the lock is freed only once that push has ended, a SIGKILLed run's too (pr_push_hold).
# The lock's holder leaves $WT detached once that push has ended, not holding the branch, a SIGKILLed
# run's too; a merge the run left stopped on a conflict is aborted first (P276).
# A head that is exactly the live head plus one commit asks app_push.sh for --row-only
# (R10-ROW-ONLY-UPDATE): app_push.sh's own verdict replaces the full prepr with the body contract
# when the push is exactly this PR's row added onto its live head under the body plus this run's
# note, and runs prepr otherwise; its `app_push: ROW-ONLY:` line, naming which and why, is printed
# here. A head that merges new code, or main, never asks.
# BODY-ONLY (R10-FLOW-BODY-ONLY): when the merges and the row leave the head exactly the live head
# (the code sha already in it, or `-`; main clean; the row present), nothing is pushed:
# body_patch.sh runs the body contract at that head from this run's worktree and PATCHes the body,
# and `update_pr: BODY-ONLY:` says so. With `-`, a handoff/<topic> tip the head lacks refuses
# (pass it as the code sha). pr-contract re-runs on the `edited` event. HPO_BODY_PATCH replaces
# body_patch.sh (the self-test's stub).
# --self-test runs delivery_row.sh's self-test, then pr_args.sh's, under pr_args.sh's self-test bound.
. "$(dirname -- "$0")/delivery_row.sh"; . "$(dirname -- "$0")/pr_args.sh"
[ "${1:-}" = --self-test ] && { [ -n "${PR_BOUND:-}" ] || pr_bounded update_pr bash "$0" --self-test  # pr_args.sh's bound
  bash "$(dirname -- "$0")/delivery_row.sh" --self-test; r=$?
  bash "$(dirname -- "$0")/pr_args.sh" --self-test || exit 1; exit $r; }
PR_NAME=update_pr; pr_trap; unset GIT_AUTHOR_NAME; export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
SEAT=$(cd "$(dirname -- "$0")" && pwd); PRT=$(cd "$(dirname -- "$0")/../../pr" && pwd)  # head_note.py: each ## Head note goes under the heading, not a quote of it
pr_need_args 3 $# "update_pr.sh <branch> <code-sha|-> <body-file> [issues...]"
[ "$2" = - ] || pr_code_sha_shape "$2"
[ -f "$3" ] || pr_refuse "no body file at $3"
M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd); P=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr; mkdir -p "$P"
BR=$1; C=$2; B=$3; shift 3; ISS="$*"; R=tvofi/heatpump_optimizer
WT=$P/upd-${BR//\//-}
# The EXIT trap goes first, so the lock (pr_branch_lock) is freed by it after the reap: bash runs it
# when TERM/INT/HUP end the shell too, so a stopped run ends its push rather than leaving it to burn
# on after the shell (R10-PUSHER-REAP), and only then frees the branch.
pr_exit_trap
# Held now, so the worktree is this run's: the lock's holder leaves it detached, never holding the
# branch, which the merge train's recarry would read as checked out elsewhere (#2513, #2544, #2547).
pr_branch_lock "$WT.lock" "$BR" "$WT" detach  # one run per branch, with open_pr.sh (pr_args.sh)
cd "$M"
if [ "$C" != - ]; then
  T=${HANDOFF_TOPIC:-${BR#fix/}}
  [ -n "${HANDOFF_TOPIC:-}" ] || [ -n "$(git ls-remote origin "refs/heads/handoff/$T")" ] || [ "$T" = "${T%-pr}" ] || T=${T%-pr}  # mut:prtopic
  pr_handoff_tips "$T" 0
  git fetch -q origin "refs/heads/handoff/$T"
  pr_code_in_handoff "$C" "$T"
fi
git fetch -q origin "$BR" main
pr_tools_fresh  # the checkout holding these tools, against the main just fetched (pr_args.sh)
OWN=$(git worktree list | grep -F "[$BR]" | awk '{print $1}' | grep "^$P/" || true); for o in $OWN; do  # another instrument's clean worktree on the branch is detached, never one holding work origin lacks
  [ "$o" = "$WT" ] && continue; [ -z "$(git -C $o status --porcelain)" ] || continue
  git merge-base --is-ancestor "$(git -C $o rev-parse HEAD)" "origin/$BR" || pr_refuse "worktree $o holds commits of $BR that origin/$BR lacks (unpushed work, e.g. a PR's row): not detaching it"  # mut:unpushed
  git -C $o checkout -q --detach
done
git worktree list | grep -F "[$BR]" | grep -vqF "$WT " && { echo "branch $BR checked out elsewhere: $(git worktree list | grep -F "[$BR]")"; exit 1; }
[ -d $WT ] && git worktree remove --force $WT
git worktree add -q -B "$BR" $WT origin/$BR; cd $WT
G="git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com"
LIVE=$(git rev-parse HEAD)  # the pull request's head as origin holds it
N=${PR_N:-$(gh pr list -R $R --head "$BR" --state open --json number -q '.[0].number')}
[ -n "$N" ] || { echo "no open pull request at $BR, so no row to check"; exit 1; }
NOTE=""
if [ "$C" != "-" ]; then $G merge -q --no-edit $C; NOTE="merges the authored code head \`$C\`"; fi
OLD=$(git rev-parse HEAD)
# Ruling R4 (Lean flow K12): origin/main is merged only when the pull request is DIRTY or the merge
# would conflict; a clean head is not moved to absorb main (fixer.md step 6, nudge.md step 9). An
# unread merge state is not DIRTY: the merge-tree reading below is the local proof either way.
ST=$(gh pr view "$N" -R $R --json mergeStateStatus -q .mergeStateStatus 2>/dev/null) || ST=unread
MAIN=""
git merge-tree --write-tree origin/main HEAD >/dev/null 2>&1 || MAIN=1
[ "$ST" != DIRTY ] || MAIN=1
[ -z "$MAIN" ] || $G merge -q --no-edit origin/main
# Keys taken at the code sha, or at the previous head when none was given, re-keyed where the merges
# only shifted their lines (ci_predict.py --rekey-body; open_pr.sh's why).
python3 "$PRT/ci_predict.py" --rekey-body "$B" --from "$([ "$C" = - ] && echo "$OLD" || echo "$C")" || echo "update_pr: the unpinned-site re-key did not run; prepr reads the body as written" >&2
# ensure_row's own guard decides; its output names the row only when it added one.
# The title first, in an assignment: a failing `gh` inside an argument stops nothing.
TTL=$(gh pr view "$N" -R $R --json title -q .title)
_added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
# BODY-ONLY (R10-FLOW-BODY-ONLY part (b)): nothing to commit -- the code sha, if any, is already in the
# head, main needs no merge and the row exists -- so the head stays where it is and the body goes to
# body_patch.sh, which runs the body contract at that head and PATCHes the body with no push. Run from
# this worktree, the head's own checkout, so the contract resolves the paths the head adds (V115).
if [ "$H" = "$LIVE" ]; then
  if [ "$C" = - ]; then
    T=${HANDOFF_TOPIC:-${BR#fix/}}; [ -n "$(git ls-remote origin "refs/heads/handoff/$T")" ] || T=${T%-pr}
    HT=$(git ls-remote origin "refs/heads/handoff/$T" | cut -f1)
    if [ -n "$HT" ]; then git fetch -q origin "refs/heads/handoff/$T"
      git merge-base --is-ancestor "$HT" "$H" || pr_refuse "handoff/$T ($HT) is not in the head $H: pass it as the code sha, not -"; fi
  fi
  PYTHONPATH="$PRT" python3 - "$B" "$H" <<'E'
import sys; from head_note import prefix
p,H=sys.argv[1:3]; s=open(p).read()
s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
E
  rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
  cat $WT.log
  [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
  echo "update_pr: BODY-ONLY: #$N at $H, the head unmoved"
  echo "HEAD=$H"; exit 0
fi
[ "$(git log -1 --format=%an)" = tvofi ] || { echo "author wrong"; exit 1; }
PYTHONPATH="$PRT" python3 - $B $H "$NOTE" $M "$ROW" "$MAIN" <<'E'
import sys; from head_note import prefix
p,H,N,M,R,MM=sys.argv[1:7]; s=open(p).read()
if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below) into this PR's previous head"%M + ((", and then "+R) if R else "") + ".\n\n"
else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
s=prefix(s,pre); open(p,'w').write(s)
E
if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
# Asynchronous, so a stop signal interrupts the `wait` and the EXIT trap reaps
# the tree (pr_args.sh's why).
{ pr_push_hold; PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $RO $R $WT $BR $B $ISS > $WT.log 2>&1 & } 9>>"$PR_PUSH_LOCK"
pr_wait $! $WT.log
grep -h '^app_push: ROW-ONLY:' $WT.log || :
echo "HEAD=$H"
