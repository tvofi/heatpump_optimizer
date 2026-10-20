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
# One run per branch. $WT and $WT.log are fixed per branch, and the line below that removes $WT
# force-removed a second run's live worktree under its prepr: "Unable to read current working
# directory", tools/ files missing, the other run's body in the shared log (2026-10-19/20: the
# orchestrator's update and cloud_relay.sh's handoff arm on one PR). The lock is flock(2) held by
# ONE holder process, never by an fd of this shell: every command the run starts inherits such an
# fd, and a `git gc --auto` git detached kept it after the run ended (#2469 round 1). The holder's
# file is non-inheritable (PEP 446). The lock is freed only when nothing this run started can
# still be in $WT (#2469 round 2: `kill <pid>`, daemonize.py's stop, freed it under a live push):
#   - a normal end: the EXIT trap ends the holder;
#   - TERM, INT or HUP: upd_stop asks the holder, which reads the run's process tree while it is
#     whole, TERMs it, and holds the lock until every one of those processes has exited;
#   - SIGKILL, which no trap sees: the holder re-reads the tree each second, and once its parent
#     is gone it holds the lock until the last tree it read has exited.
python3 -I -c 'import fcntl, os, signal, subprocess, sys, time
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(75)
p, me = os.getppid(), os.getpid()
f.truncate(0); f.write("%d %d\n" % (p, me)); f.flush()
signal.signal(signal.SIGINT, signal.SIG_IGN); signal.signal(signal.SIGHUP, signal.SIG_IGN)
def tree(roots):
    try: w = subprocess.run(["ps", "-A", "-o", "pid=", "-o", "ppid="], capture_output=True, text=True).stdout.split()
    except OSError: return set(roots)
    up, out, todo = {}, set(), list(roots)
    for a, b in zip(w[0::2], w[1::2]): up.setdefault(int(b), []).append(int(a))
    while todo:
        for c in up.get(todo.pop(), []):
            if c != me and c not in out: out.add(c); todo.append(c)
    return out
def live(xs):
    r = set()
    for x in xs:
        try: os.kill(x, 0); r.add(x)
        except ProcessLookupError: pass
        except PermissionError: r.add(x)
    return r
seen, stop = set(), []
def on_stop(*_):
    s = tree([p])
    for x in s:
        try: os.kill(x, signal.SIGTERM)
        except OSError: pass
    seen.update(s); stop.append(1)
    with open(sys.argv[1] + ".stopping", "w") as g: g.write("%d\n" % len(s))
signal.signal(signal.SIGUSR2, on_stop)
while os.getppid() == p and not stop:
    s = tree([p])
    if not stop: seen.clear(); seen.update(s)
    time.sleep(1)
while True:
    seen = live(seen)
    if not seen: break  # mut:drain
    seen |= tree(seen); time.sleep(0.3)' "$WT.lock" </dev/null >/dev/null 2>&1 & LKP=$!
trap '{ [ -n "${UPD_STOPPING:-}" ] || { kill "$LKP"; wait "$LKP"; }; } 2>/dev/null || :' EXIT  # mut:unlock
k=0; while kill -0 "$LKP" 2>/dev/null && [ "$(cat "$WT.lock" 2>/dev/null)" != "$$ $LKP" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
upd_unlocked() { # the holder did not take the lock: BUSY (75) when another holder has it
  local rc=0 o; kill -0 "$LKP" 2>/dev/null && pr_refuse "the lock holder for $WT.lock did not report within 20 s"
  wait "$LKP" || rc=$?; o=$(cut -d' ' -f1 "$WT.lock" 2>/dev/null || :)
  [ "$rc" = 75 ] || pr_refuse "could not take the per-branch lock $WT.lock (its holder exited $rc)"
  if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then o="another update_pr.sh run (pid $o)"; else o="the lock holder of run ${o:-unknown}, which has ended but started processes that have not,"; fi
  echo "update_pr: BUSY: $o holds $BR's worktree $WT; nothing was changed, run again when it ends" >&2; exit 75
}
[ "$(cat "$WT.lock" 2>/dev/null)" = "$$ $LKP" ] || upd_unlocked  # mut:lock
upd_stop() { # TERM/INT/HUP: the holder ends what this run started and keeps the lock until it has
  local k=0; trap '' TERM INT HUP; UPD_STOPPING=1
  kill -USR2 "$LKP" 2>/dev/null || exit 143
  while [ ! -e "$WT.lock.stopping" ] && [ $k -lt 100 ]; do sleep 0.05; k=$((k + 1)); done
  exit 143
}
rm -f "$WT.lock.stopping"; trap upd_stop TERM INT HUP  # mut:stop
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
# In the background and waited for: a trapped TERM interrupts `wait` at once, where it would
# wait for a foreground push to finish first.
PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash "$_push" $R $WT $BR $B $ISS > $WT.log 2>&1 & PUSHP=$!
wait "$PUSHP" || pr_push_failed $WT.log
echo "HEAD=$H"
