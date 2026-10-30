#!/bin/bash
# pr_args.sh -- the argument checks, the stop report and the signal reap
# open_pr.sh and update_pr.sh share, so neither can stop without saying why,
# and a stopped one ends the work it started.
#
#   . tools/audit/seat/pr_args.sh       (open_pr.sh, update_pr.sh; PR_NAME first)
#   tools/audit/seat/pr_args.sh --self-test
#
# WHY IT EXISTS (R10-OPENPR-SILENT, 2026-10-18). open_pr.sh runs under
# `set -eo pipefail`. Twice the orchestrator passed the handoff-BODY sha where
# the CODE sha belongs; `git merge-base --is-ancestor` returned non-zero, prints
# nothing when it does, and the script exited -- the daemonize log held only
# its banner and read as a hang for 40 minutes. Two layers close it:
#   - the checks below refuse a wrong argument up front, naming it, and name a
#     body sha as one ("that is the BODY sha; pass the CODE sha");
#   - pr_trap's ERR trap reports every other stop errexit makes -- the failing
#     command, its line and its status -- so no stop is silent. `-E` carries the
#     trap into functions and substitutions; it reports from the top-level shell
#     only, where the failure reaches the assignment or command that stops it.
# Every line is "<PR_NAME>: REFUSE: ..." or "<PR_NAME>: STOPPED: ...", on stderr.
#
# THE MUTANTS. A line ending in `# mut:<name>` is the predicate one self-test
# arm pins. The self-test runs each arm on copies of the scripts and again on
# copies without that line, and the arm must fail there: a check that passed
# both ways would pin nothing. Sourcing defines functions only; it runs nothing.

pr_refuse() { printf '%s: REFUSE: %s\n' "${PR_NAME:-pr}" "$*" >&2; exit 1; }
pr_stopped() { # <status> <line> <command>: the ERR trap's report
  [ "${BASH_SUBSHELL:-0}" = 0 ] || return 0
  printf '%s: STOPPED: line %s exited %s: %s\n' "${PR_NAME:-pr}" "$2" "$1" "$3" >&2
  # 75 is BUSY to a caller (cloud_relay.sh retries it and records nothing), and only pr_lock_busy
  # says it: a step that happens to exit 75 under errexit is a stop like any other (#2469).
  [ "$1" != 75 ] || exit 1  # mut:busy75
}
pr_trap() { # errexit, and the report of every stop it makes
  set -Eeo pipefail
  trap 'pr_stopped $? $LINENO "$BASH_COMMAND"' ERR  # mut:trap
}
pr_need_args() { # <min> <got> <usage>
  [ "$2" -ge "$1" ] || pr_refuse "$2 argument(s), at least $1 needed: $3"  # mut:arity
}
pr_code_sha_shape() { # <sha>: a full sha, not an abbreviation or a ref name
  local re='^[0-9a-f]{40}$'
  [[ $1 =~ $re ]] || pr_refuse "code sha '$1' is not 40 lowercase hex characters"  # mut:hex
}
pr_handoff_tips() { # <topic> <need-body: 1|0>: sets PR_HT and PR_BT from what origin answers
  local out
  out=$(git ls-remote origin "refs/heads/handoff/$1" "refs/heads/handoff-body/$1") \
    || pr_refuse "could not list handoff/$1 and handoff-body/$1 on origin"
  PR_HT=$(printf '%s\n' "$out" | awk -v r="refs/heads/handoff/$1" '$2 == r { print $1 }')
  PR_BT=$(printf '%s\n' "$out" | awk -v r="refs/heads/handoff-body/$1" '$2 == r { print $1 }')
  [ -n "$PR_HT" ] || pr_refuse "origin has no handoff/$1 (the code ref)"  # mut:noref
  [ "$2" = 0 ] || [ -n "$PR_BT" ] || pr_refuse "origin has no handoff-body/$1 (the body ref)"  # mut:nobody
}
pr_code_in_handoff() { # <sha> <topic>: after the fetch of handoff/<topic>; PR_HT and PR_BT set
  git cat-file -e "$1^{commit}" 2>/dev/null || pr_refuse "code sha $1 does not resolve to a commit here, after fetching handoff/$2"  # mut:resolve
  git merge-base --is-ancestor "$1" "$PR_HT" && return 0
  [ "$1" != "$PR_BT" ] || pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT); it is the tip of handoff-body/$2: that is the BODY sha; pass the CODE sha"  # mut:body
  pr_refuse "code sha $1 is not an ancestor of origin/handoff/$2 ($PR_HT), and it is not the tip of handoff-body/$2 (${PR_BT:-absent})"  # mut:ancestor
}
pr_lock_busy() { # <lock-file> <branch> <worktree>: the holder did not take the lock: BUSY (75) when another holder has it
  local rc=0 o
  kill -0 "$LKP" 2>/dev/null && pr_refuse "the lock holder for $1 did not report within 20 s"
  wait "$LKP" || rc=$?; o=$(cut -d' ' -f1 "$1" 2>/dev/null || :)
  [ "$rc" = 75 ] || pr_refuse "could not take the per-branch lock $1 (its holder exited $rc)"
  if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then o="another open_pr.sh or update_pr.sh run (pid $o)"
  elif [ "$(cut -d' ' -f4 "$1" 2>/dev/null || :)" = drain ]; then o="the push of run $o (the run has ended, the push has not)"
  else o="the lock holder of run ${o:-unknown}, which has ended,"; fi
  echo "${PR_NAME:-pr}: BUSY: $o holds $2's worktree $3; nothing was changed, run again when it ends" >&2; exit 75
}
pr_branch_lock() { # <lock-file> <branch> <worktree> [detach]: hold the branch's lock until the run and its push end, or exit 75 BUSY
  # One run per branch: open_pr.sh and update_pr.sh both take it, so neither moves a branch the other
  # is pushing (R10-OPENPR-ROW-PUSH). $WT and $WT.log of update_pr.sh are fixed per branch, and the
  # line there that removes $WT force-removed a concurrent run's live worktree under its prepr
  # (2026-10-19/20: the orchestrator's update and cloud_relay.sh's handoff arm on one PR). The lock is
  # flock(2) held by one holder process; this shell holds no fd on it, so nothing the run starts can (a
  # detached `git gc --auto` kept an inherited one).
  # The holder lets go when the run ends -- USR1 from PR_AFTER_REAP, which the caller's pr_exit_trap
  # runs after its reap, or its parent gone, as a SIGKILL leaves it -- and then not before the push's
  # own lock (<lock-file>.push, pr_push_hold) is free: that lock belongs to an fd every process of the
  # push inherits, so the kernel frees it when the last of them has exited, a zombie included, with
  # no `ps` and no process-group walk (R10-UPDATE-PR-SIGNALS: #2469's round-4 drain counted the
  # zombies a late-reaping PID 1 leaves, and failed 7 of 7). It ignores TERM, INT and HUP, so a
  # signal to the run's whole process group does not end it beside the push it guards; a stopped
  # run's own reap ends that push. The file reads `<run pid> <holder pid> <start epoch>`, the epoch
  # the holder's own clock when it took the lock (cloud_relay.sh's STUCK andon ages it), and a fourth
  # field `drain` once the run has ended. With
  # `detach` it then leaves <worktree> detached, still holding the lock: never under a push and never
  # under the next run, and a SIGKILLed run's too, whose own trap never runs (#2513, #2544, #2547).
  # A merge the run left stopped on a conflict is aborted first, since `checkout --detach` refuses a
  # conflicted index and the worktree kept the branch (P276, #2917): the run's merges start at
  # origin/<branch> and merge only remote refs, so the abort loses nothing.
  local k=$(($(date +%s) + 20))
  PR_PUSH_LOCK=$1.push
  python3 -I -c 'import fcntl, os, signal, subprocess, sys, time
os.closerange(3, 1024)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, signal.SIG_IGN)  # mut:holdsig
end = []
signal.signal(signal.SIGUSR1, lambda *a: end.append(1))
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(75)
p = os.getppid(); start = int(time.time())
f.truncate(0); f.write("%d %d %d\n" % (p, os.getpid(), start)); f.flush()
while os.getppid() == p and not end: time.sleep(0.2)  # mut:watch
f.truncate(0); f.write("%d %d %d drain\n" % (p, os.getpid(), start)); f.flush()
fcntl.flock(open(sys.argv[1] + ".push", "a"), fcntl.LOCK_EX)  # mut:drain
det = sys.argv[2:] and sys.argv[2] == "detach" and os.path.isdir(sys.argv[3])
if det and subprocess.call(["git", "-C", sys.argv[3], "rev-parse", "-q", "--verify", "MERGE_HEAD"], stdout=subprocess.DEVNULL) == 0: subprocess.call(["git", "-C", sys.argv[3], "merge", "--abort"])  # mut:holdabort
if det: subprocess.call(["git", "-C", sys.argv[3], "checkout", "-q", "--detach"])  # mut:detach
sys.exit(0)' "$1" ${4:+"$4" "$3"} </dev/null >/dev/null 2>&1 & LKP=$!
  PR_REAP_SPARE=$LKP
  PR_AFTER_REAP='{ kill -USR1 "$LKP"; wait "$LKP"; } 2>/dev/null || :'  # mut:unlock
  # Taken is these two pids with no `drain` mark (fields 1, 2 and 4; the start epoch between them is
  # the holder's). A wall-clock deadline, so the 20 s pr_lock_busy names is 20 s whatever the load.
  while kill -0 "$LKP" 2>/dev/null && [ "$(cut -d' ' -f1,2,4 "$1" 2>/dev/null)" != "$$ $LKP" ] && [ "$(date +%s)" -lt "$k" ]; do sleep 0.05; done
  [ "$(cut -d' ' -f1,2,4 "$1" 2>/dev/null)" = "$$ $LKP" ] || pr_lock_busy "$1" "$2" "$3"  # mut:lock
}
pr_push_hold() { # inside `{ pr_push_hold; <push> & } 9>>"$PR_PUSH_LOCK"`: lock fd 9, which the push inherits
  # The redirection is this shell's, opened before the fork, so a SIGKILL at any point leaves the
  # lock either with the push or with nobody; the shell's copy closes when the group ends. It waits
  # for this run's earlier push (open_pr.sh's first), which only a detached child of it still holds.
  # git's auto-maintenance runs in the foreground from here on: a `git fetch` in the push otherwise
  # daemonizes `git gc --auto`, which keeps fd 9 (daemonize closes 0-2 only), outlives the push as a
  # child of PID 1 that no reap reaches, and holds the lock in `drain` for the whole gc (#2825 round
  # 1). In the foreground it is part of the push: reaped with it, and named by its BUSY line.
  local rc=0 n=${GIT_CONFIG_COUNT:-0}
  [ -n "${PR_FG_GC:-}" ] || export "GIT_CONFIG_KEY_$n=gc.autoDetach" "GIT_CONFIG_VALUE_$n=false" "GIT_CONFIG_KEY_$((n + 1))=maintenance.autoDetach" "GIT_CONFIG_VALUE_$((n + 1))=false" GIT_CONFIG_COUNT=$((n + 2)) PR_FG_GC=1  # mut:fggc
  python3 -I -c 'import fcntl; fcntl.flock(9, fcntl.LOCK_EX)' || rc=$?  # mut:pushhold
  [ "$rc" = 0 ] || pr_refuse "could not lock $PR_PUSH_LOCK"
}
# ---- the opener's release: its last act, under the branch lock -------------
# WHY IT EXISTS (R10-FLY-OPENPR-ATOMIC: P-D, P64, P72). open_pr.sh's worktree kept its branch
# checked out after every run: a STOPPED one left it for the merge train, whose recarry reads a
# branch checked out elsewhere as busy (2026-10-26 05:15:57Z, train s47); a prepr-refused open left
# it and its local branch, so the next open of the topic STOPPED at `git worktree add -b` (P72: 7
# of 8 instances). pr_release_wt is the run's last act, once its pushes have ended:
#   - a worktree that is dirty is kept on its branch and named: it holds work no push carried;
#   - one whose HEAD is the sha the run last pushed is detached, the branch free on origin;
#   - otherwise, one whose branch origin holds is kept and named (work origin lacks, or origin
#     could not be asked), and one origin never had is removed with its local branch.
# Detached only at the end, never between two pushes: app_push.sh's committed-tip gate passes a
# worktree detached at the branch tip, so a detach before a later push would go unrefused
# (#2738 round 4). update_pr.sh's own worktree is detached by its lock holder (pr_branch_lock's
# `detach`); handoff_push.sh, which takes no lock, calls this after its last push.
pr_release_wt() { # <worktree> <branch> <pushed sha|''>: detach, remove or keep (naming it) the run's worktree
  local wt=$1 br=$2 sha=$3 on c
  [ -d "$wt" ] && [ "$(git -C "$wt" symbolic-ref -q HEAD 2>/dev/null)" = "refs/heads/$br" ] || return 0
  if [ -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ]; then pr_kept "$wt" "$br" "it is dirty"; return 0; fi  # mut:reldirty
  if [ -n "$sha" ] && [ "$(git -C "$wt" rev-parse HEAD)" = "$sha" ]; then git -C "$wt" checkout -q --detach; return 0; fi  # mut:release
  on=$(git -C "$wt" ls-remote origin "refs/heads/$br" 2>/dev/null) || { pr_kept "$wt" "$br" "origin could not be asked whether it holds $br"; return 0; }
  if [ -n "$on" ]; then pr_kept "$wt" "$br" "origin holds $br and HEAD $(git -C "$wt" rev-parse --short HEAD) is not this run's pushed head"; return 0; fi  # mut:relorigin
  c=$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir) && cd "$c"  # the run's cwd may be the worktree itself
  git worktree remove "$wt" 2>/dev/null || { pr_kept "$wt" "$br" "git worktree remove refused it"; return 0; }  # mut:reltidy
  git branch -q -D "$br" 2>/dev/null || :
  printf '%s: removed %s and its local branch %s, which origin never had\n' "${PR_NAME:-pr}" "$wt" "$br" >&2
}
pr_kept() { printf '%s: KEPT %s on %s: %s\n' "${PR_NAME:-pr}" "$1" "$2" "$3" >&2; }

# ---- the tools' freshness (P-P) ----------------------------------------------
# open_pr.sh and update_pr.sh run the tools of whatever checkout invokes them, and a stale main
# checkout once wrote a Co-Authored-By delivery row (#2664). After each script's fetch of
# origin/main, the checkout holding these files refuses when origin/main has commits it lacks
# under the two tool directories; any other path is no refusal. No pull: the caller decides.
# HPO_ALLOW_STALE_TOOLS=1 names the staleness and goes on.
# Top-relative (`:/`): git runs in the tools' own directory, where a bare path would be read below it.
PR_FRESH_PATHS=(:/tools/audit/seat :/tools/pr)  # mut:freshpaths
pr_tools_fresh() { # after `git fetch origin main`: refuse when this file's checkout is behind it in PR_FRESH_PATHS
  local d n h o why
  d=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  h=$(git -C "$d" rev-parse --short=12 HEAD 2>/dev/null) && o=$(git -C "$d" rev-parse --short=12 origin/main 2>/dev/null) \
    && n=$(git -C "$d" rev-list --count HEAD..origin/main -- "${PR_FRESH_PATHS[@]}" 2>/dev/null) \
    || pr_refuse "could not count what origin/main adds over the checkout holding $d"
  [ "$n" != 0 ] || return 0
  why="STALE CHECKOUT $h behind origin/main $o by $n commit(s) touching tools/audit/seat tools/pr"
  [ -n "${HPO_ALLOW_STALE_TOOLS:-}" ] || pr_refuse "$why: update the checkout holding $d, or set HPO_ALLOW_STALE_TOOLS=1"  # mut:stale
  printf '%s: NOTICE: %s; HPO_ALLOW_STALE_TOOLS is set, so this run goes on\n' "${PR_NAME:-pr}" "$why" >&2
}
pr_push_failed() { # <log>: a refused push names its refusal, or its log's tail
  grep -E 'REFUSE' "$1" >&2 || tail -n 20 "$1" >&2 || true
  pr_refuse "the push failed; its log is $1"
}

# ---- the stop: reap the whole descendant tree -------------------------------
# WHY IT EXISTS (R10-PUSHER-REAP, 2026-10-20). A pusher stopped with TERM left
# its whole subtree running: a shell does not forward a signal to a foreground
# child, so the child reparented to launchd and kept burning CPU -- six
# survivors aged 26 to 62 minutes on a box already at load 77 on eight cores,
# each needing a kill two levels further down.
#
# The reap is the EXIT trap (pr_exit_trap): bash runs it when TERM, INT or HUP
# ends the shell, and on every other exit. A signal trap would be DEFERRED while
# a foreground command runs, and an untrapped INT waits for the foreground child
# too, so each pusher runs its push asynchronously and `wait`s on it, which every
# one of the three signals interrupts.
#
# The reap walks children by parent pid and signals each by pid -- never
# `pkill -f`, which on a shared box reaches other seats' processes. The walk
# appends to PR_REAP_PIDS in a function called from this shell, so the pgrep in
# its `for` list is the only child each step forks -- a wrapping subshell would
# itself be listed as a descendant of this shell.
pr_descendants() { # <pid>: append every live descendant to PR_REAP_PIDS, a parent before its children
  local k
  for k in $(pgrep -P "$1" 2>/dev/null); do
    [ "$k" != "${PR_REAP_SPARE:-}" ] || continue  # the branch lock's holder: PR_AFTER_REAP ends it
    PR_REAP_PIDS[${#PR_REAP_PIDS[@]}]=$k
    pr_descendants "$k"
  done
}
pr_kill() { # <signal> <pid>: one numeric pid above 1 -- never a pattern, never a group
  case $2 in ''|0|1|*[!0-9]*) return 0 ;; esac
  kill -"$1" "$2" 2>/dev/null || :  # mut:stop
}
# A runner whose child is itself a runner names that child PR_REAP_LEAD. The lead
# stops its own tree in its own order -- update_pr.sh frees its branch lock only
# after its push has ended, merge_train.py TERMs its tool and runs its `finally`
# -- so it is TERMed alone and given PR_REAP_LEAD_TENTHS to end. A reap that
# TERMed the whole tree at once would end a lock holder beside the push it
# guards. The walk is taken first, while the tree is still attached: whatever
# the lead leaves, orphans included, is reaped after it by those pids. Only a
# lead the walk returned is signalled: a stale PR_REAP_LEAD, whose pid a later
# process may hold, is never one.
pr_lead_stop() { # TERM the lead alone, if the walk returned it, and wait for it at most PR_REAP_LEAD_TENTHS
  local n=0
  [ -n "${PR_REAP_LEAD:-}" ] || return 0
  case " ${PR_REAP_PIDS[*]} " in *" $PR_REAP_LEAD "*) ;; *) return 0 ;; esac  # mut:leadwalk
  pr_kill TERM "$PR_REAP_LEAD"
  while [ "$n" -lt "${PR_REAP_LEAD_TENTHS:-300}" ] && kill -0 "$PR_REAP_LEAD" 2>/dev/null; do sleep 0.1; n=$((n + 1)); done
}
pr_reap() { # TERM every descendant of this shell, then KILL whatever outlives a bounded grace
  local p alive n=0
  # A second stop signal must not end the shell mid-reap, before the KILL below.
  trap '' TERM INT HUP  # mut:sigign
  PR_REAP_PIDS=()
  command -v pgrep >/dev/null || printf '%s: STOPPED: no pgrep on PATH, so the tree this run started is not reaped; the branch lock stays held until its push ends\n' "${PR_NAME:-pr}" >&2  # mut:nopgrep
  pr_descendants $$
  [ "${#PR_REAP_PIDS[@]}" -gt 0 ] || return 0
  pr_lead_stop  # mut:lead
  for p in "${PR_REAP_PIDS[@]}"; do pr_kill TERM "$p"; done
  while [ "$n" -lt "${PR_REAP_TENTHS:-20}" ]; do
    alive=()
    for p in "${PR_REAP_PIDS[@]}"; do kill -0 "$p" 2>/dev/null && alive[${#alive[@]}]=$p; done
    [ "${#alive[@]}" -gt 0 ] || return 0
    PR_REAP_PIDS=("${alive[@]}")
    sleep 0.1
    n=$((n + 1))
  done
  for p in "${PR_REAP_PIDS[@]}"; do pr_kill KILL "$p"; done  # mut:grace
  return 0
}
pr_exit_trap() { # [<command>]: on every exit, a stop signal's included, run <command>, reap the tree, run PR_TIDY, then PR_AFTER_REAP
  # PR_TIDY runs once the tree is reaped and while the branch lock is still held: open_pr.sh's
  # pr_release_wt, which must not race an update_pr.sh that detaches the same worktree (P-D).
  local first=${1:+$1; }
  trap "${first}"'pr_reap; eval "${PR_TIDY:-:}"; eval "${PR_AFTER_REAP:-:}"' EXIT  # mut:exitreap
}
pr_own_group() { # <command...>: exec <command> as the leader of a process group of its own
  exec python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp(sys.argv[1], sys.argv[1:])' "$@"
}
pr_wait() { # <pid> <log>: wait for the asynchronous pusher -- a stop signal interrupts it
  local rc=0
  wait "$1" || rc=$?
  [ "$rc" = 0 ] || pr_push_failed "$2"
}

# ---- the self-test bound: a session of its own, a deadline, reaped on exit --
# WHY IT EXISTS (Revision 12, 2026-10-21). An orphaned update_pr.sh self-test
# spun 8.6 h at about 67% CPU. pr_bounded runs a self-test as a session of its
# own, so its fixtures' process groups (sigrun's included) stay inside it, and
# ends that whole session -- every process whose session id is its own, by pid,
# never a pattern -- when the self-test exits, when the bound
# PR_SELFTEST_SECONDS (default 1200) passes, or once the supervisor is gone, a
# SIGKILLed one too: a watchdog outside the session reads a pipe only the
# supervisor holds, whose EOF says so. The watchdog is a session of its own as
# well, so a SIGKILL to the caller's group, which takes the supervisor, never takes
# it too (round 2 left 11 unbounded survivors that way). A group or session kill is safe here and
# only here: the session is the self-test's own (pr_kill's never-a-group is for a
# pusher's tree, which shares its group with its caller). A self-test re-execs
# itself through it once (PR_BOUND guards the second entry), so `--self-test`
# keeps its name; a bound that ends one prints `<name>: BOUND: ...` and exits 124.
PR_BOUND_PY='import os, select, signal, sys, time
lim, name, cmd = float(sys.argv[1]), sys.argv[2], sys.argv[3:]
def members(sid):  # live pids of the session; a zombie is no member, it holds nothing
  if not os.path.isdir("/proc"):
    import subprocess
    return [int(x) for x in subprocess.run(["pgrep", "-s", str(sid)], capture_output=True, text=True).stdout.split()]
  out = []
  for d in os.listdir("/proc"):
    try:
      st = open("/proc/%s/stat" % d).read().rsplit(")", 1)[1].split()
      if int(st[3]) == sid and st[0] != "Z": out.append(int(d))
    except (OSError, IndexError, ValueError): pass
  return out
def end(sid):  # KILL the whole session, by pid, in rounds, for a child forked mid-sweep: how many
  n = 0
  for _ in range(20):
    ps = members(sid)
    if not ps: break
    for p in ps:
      try: os.kill(p, signal.SIGKILL); n += 1
      except OSError: pass
    time.sleep(0.05)
  return n
r, w = os.pipe(); tr, tw = os.pipe()  # the supervisor alive, to the watchdog; the deadline passed, back
kid = os.fork()
if kid == 0:
  for f in (r, w, tr, tw): os.close(f)
  os.setsid(); os.environ["PR_BOUND"] = "1"; os.execvp(cmd[0], cmd)
dog = os.fork()
if dog == 0:  # outside the session: at the deadline, or at EOF once the supervisor is gone, a SIGKILLed one too
  os.close(w); os.close(tr)
  os.setsid()  # mut:dogsid
  if not select.select([r], [], [], lim)[0]:
    sys.stderr.write("%s: BOUND: the self-test passed %d s, so its whole session is ended\n" % (name, lim)); os.write(tw, b"T")
  end(kid)  # mut:dogend
  os._exit(0)
os.close(r); os.close(tw)
def stop(sig, _):
  end(kid); os._exit(128 + sig)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, stop)
code = os.waitstatus_to_exitcode(os.waitpid(kid, 0)[1])
os.kill(dog, signal.SIGKILL); os.waitpid(dog, 0)
if select.select([tr], [], [], 0)[0] and os.read(tr, 1) == b"T": end(kid); os._exit(124)
left = end(kid)  # mut:boundreap
if left: sys.stderr.write("%s: BOUND: the self-test left %d process(es) of its session, now ended\n" % (name, left))
os._exit(128 - code if code < 0 else code)'
pr_bounded() { # <name> <command...>: exec <command> under the self-test bound, PR_BOUND set inside it
  exec python3 -I -c "$PR_BOUND_PY" "${PR_SELFTEST_SECONDS:-1200}" "$@"
}

# ---- the class: every pusher reaps its tree (R10-PUSHER-REAP) ---------------
# The rule that enumerates the class's seams: a PUSHER is a tracked tools/ script
# naming app_push.sh or push.sh, found by the git grep below, so a new one cannot
# land undispositioned: the self-test runs this census on the tree. Each path the
# grep returns has one disposition in PR_PUSHERS:
#   runner     runs a push or prepr: it installs pr_exit_trap, and every line
#              running "$_push" or "$prepr" runs it asynchronously (`&`); one
#              that takes pr_branch_lock runs each such line under pr_push_hold,
#              so the lock outlives that push (R10-UPDATE-PR-SIGNALS);
#   runner-py  a Python runner: a stop TERMs, never SIGKILLs, the tool whose own
#              EXIT trap reaps the tree (`.terminate()`), and its entry calls
#              stop_on_signal(), so a TERM/HUP to it unwinds to that handler;
#   retired    push.sh: decision 0011's retired author path, run by no runner;
#   mention    names one and runs none (the reason follows).
# A returned path with no entry, an entry the grep no longer returns, and a
# runner missing either property each print OPEN, and the census exits 1.
# Usage: pr_args.sh --pushers [<rev>] (the tree at <rev>; default the worktree).
PR_PUSHER_RULE='(^|[^A-Za-z0-9_])(app_)?push\.sh'
PR_PUSHERS='tools/audit/seat/handoff_push.sh runner
tools/audit/seat/open_pr.sh runner
tools/audit/seat/update_pr.sh runner
tools/audit/seat/remerge_main.sh runner
tools/pr/app_push.sh runner
tools/audit/seat/merge_train.py runner-py
tools/pr/push.sh retired
tools/audit/seat/pr_args.sh mention: this census and its self-test stubs
tools/audit/seat/handover_prompt.py mention: a prompt string naming the author path
tools/audit/seat/ref_privacy.py mention: its guard table keys the two paths
tools/pr/app_approve.sh mention: a self-test fixture file list
tools/pr/approve_held_runs.sh mention: comments
tools/pr/head_note.py mention: its docstring
tools/policy/check-wave-script.mjs mention: a test title
tools/policy/friction_issues.mjs mention: comments
tools/audit/seat/gh_read.py mention: its docstring cites the read-back rule of app_push.sh; it runs no subprocess
tools/audit/seat/body_patch.sh mention: comments; it PATCHes a body through app_mint.sh and runs no push
tools/pr/app_mint.sh mention: comments; sourced by app_push.sh, it launches nothing
tools/policy/policy_lint.mjs mention: a refusal message'
pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any OPEN
  local root=${1:-$(cd "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)} rev=${2:-} f kind txt bad=0
  local found
  if [ -n "$rev" ]; then
    found=$(git -C "$root" grep -lE "$PR_PUSHER_RULE" "$rev" -- 'tools/*.sh' 'tools/*.py' 'tools/*.mjs' 'tools/*.js' | sed "s|^$rev:||")
  else
    found=$(git -C "$root" grep -lE "$PR_PUSHER_RULE" -- 'tools/*.sh' 'tools/*.py' 'tools/*.mjs' 'tools/*.js')
  fi
  for f in $found; do
    kind=$(printf '%s\n' "$PR_PUSHERS" | awk -v f="$f" '$1 == f { print $2; exit }')
    if [ -n "$rev" ]; then txt=$(git -C "$root" show "$rev:$f"); else txt=$(cat "$root/$f"); fi
    txt=$(printf '%s\n' "$txt" | grep -vE '^[[:space:]]*#')  # a comment runs nothing
    case $kind in
      '') echo "OPEN $f: undispositioned -- it names a pusher; give it an entry in PR_PUSHERS"; bad=1 ;;
      runner)
        if ! printf '%s\n' "$txt" | grep -qE '(^|[;{[:space:]])pr_exit_trap([[:space:]]|$)'; then
          echo "OPEN $f runner: no pr_exit_trap, so a stop leaves its tree"; bad=1
        elif printf '%s\n' "$txt" | grep -E 'bash "\$(_push|prepr)"' \
             | sed -E 's/[0-9]*[<>]&[0-9-]*//g; s/&>//g; s/&&//g' | grep -qv '&'; then  # `2>&1` and `&&` background nothing
          echo "OPEN $f runner: a push runs in the foreground, so an INT waits behind it"; bad=1
        elif printf '%s\n' "$txt" | grep -qE '(^|[;{[:space:]])pr_branch_lock[[:space:]]' \
             && printf '%s\n' "$txt" | grep -E 'bash "\$(_push|prepr)"' | grep -qv 'pr_push_hold'; then
          echo "OPEN $f runner: a push under the branch lock holds no push lock, so the lock can end before it"; bad=1
        else echo "ok   $f runner"; fi ;;
      runner-py)
        if printf '%s\n' "$txt" | grep -qF '.terminate()' && printf '%s\n' "$txt" | grep -qE '^[[:space:]]+stop_on_signal\(\)'; then
          echo "ok   $f runner-py"
        else echo "OPEN $f runner-py: a stop SIGKILLs or orphans its tool"; bad=1; fi ;;
      *) echo "ok   $f $kind" ;;
    esac
  done
  for f in $(printf '%s\n' "$PR_PUSHERS" | awk '{ print $1 }'); do
    printf '%s\n' $found | grep -qxF "$f" || { echo "OPEN $f: stale -- the rule no longer returns it"; bad=1; }
  done
  [ "$bad" = 0 ]
}

# ---- self-test -------------------------------------------------------------
# One scratch origin (a plain repository: no push anywhere) and a clone of it
# holding copies of the scripts, so the scripts' own `origin` is the scratch
# one. Offline: `gh` is a stub (its open list is $t/prs.json; $t/gh.fail makes
# it fail), and app_push.sh is absent from the clone, so a
# run that passes every check stops at its push, which pr_push_failed reports.
# The clone also carries tools/pr/head_note.py, which open_pr.sh and
# update_pr.sh resolve (`PRT`) before their first check: without it every run
# stopped in the ERR trap there, and 25 arms failed (#2444's CI, after #2442).
# copyin carries ref_privacy.py for the same reason: handoff_push.sh's guard
# fails closed without it, so its reap arms never reached a push (#2668's CI).
pr_args_self_test() (
  local src t f=0 n=0 o m base code side body i reapsha UNREL
  src=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
  # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
  REAP_DIR=$t; export REAP_DIR
  # A stopped pusher's stub app_push: it records itself and a two-level sleep
  # tree by pid, then blocks, so the survivors of a signal can be counted. A
  # successful run (`ok`) leaves nothing behind; a later run (`fast`) exits at once.
  cat > "$t/reap-stub.sh" <<'STUB'
#!/bin/bash
echo $$ > "$REAP_DIR/started"
echo $$ >> "$REAP_DIR/pids"
[ -e "$REAP_DIR/fast" ] && exit 1
[ -e "$REAP_DIR/stubborn" ] && trap '' TERM HUP  # the whole push, children included, outlives TERM and HUP: only the reap's KILL ends it
if [ -e "$REAP_DIR/ok" ]; then
  bash -c 'sleep 1' reap-child "$REAP_DIR/mark" & echo $! >> "$REAP_DIR/pids"
  wait; exit 0
fi
bash -c 'sleep 30; :' reap-parent "$REAP_DIR/mark" & echo $! >> "$REAP_DIR/pids"
bash -c 'sleep 30 & echo $! >> "$0"; wait' "$REAP_DIR/pids" & echo $! >> "$REAP_DIR/pids"
wait
exit 1
STUB
  . "$src/../../../tests/throwaway_git.sh" && throwaway_git_env
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  o=$t/o; m=$t/m
  { throwaway_git_init "$o" -q -b main && printf 'a\n' > "$o/a" && git -C "$o" add a \
    && git -C "$o" commit -q -m base && base=$(git -C "$o" rev-parse HEAD) \
    && printf 'b\n' > "$o/b" && git -C "$o" add b && git -C "$o" commit -q -m code \
    && code=$(git -C "$o" rev-parse HEAD) && git -C "$o" branch handoff/x "$code" \
    && git -C "$o" branch handoff/y "$code" \
    && git -C "$o" checkout -q -b reapup "$code" && mkdir -p "$o/tools/pr" \
    && cp "$REAP_DIR/reap-stub.sh" "$o/tools/pr/app_push.sh" \
    && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m "reap stub" \
    && git -C "$o" checkout -q main && git -C "$o" branch handoff/reap reapup \
    && git -C "$o" checkout -q -b side "$base" && printf 'c\n' > "$o/c" && git -C "$o" add c \
    && git -C "$o" commit -q -m side && side=$(git -C "$o" rev-parse HEAD) \
    && git -C "$o" checkout -q main && git -C "$o" reset -q --hard "$base" \
    && git -C "$o" branch fix/x "$base" \
    && printf '## Head\n\nthe body\n' > "$t/body.md" \
    && body=$(git -C "$o" commit-tree "$(printf '100644 blob %s\tBODY.md\n' \
         "$(git -C "$o" hash-object -w "$t/body.md")" | git -C "$o" mktree)" -m "body: x") \
    && git -C "$o" update-ref refs/heads/handoff-body/x "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/z "$body" \
    && git -C "$o" update-ref refs/heads/handoff-body/reap "$body" \
    && throwaway_git_clone -q "$o" "$m" && mkdir -p "$t/bin" "$m/tools/audit/seat" "$m/tools/pr" \
    && cp "$src/../../pr/head_note.py" "$m/tools/pr/head_note.py" \
    && printf '#!/bin/sh\n[ -e "%s/gh.fail" ] && { echo "HTTP 403" >&2; exit 1; }\ncase "$*" in *--head*) echo 5 ;; "pr list"*) cat "%s/prs.json" ;; "pr view"*) [ -e "%s/gh.75" ] && exit 75; echo "a title" ;; *) exit 99 ;; esac\n' "$t" "$t" "$t" > "$t/bin/gh" \
    && echo '[]' > "$t/prs.json" \
    && chmod +x "$t/bin/gh"; } || { echo "  FAIL fixture"; rm -rf "$t"; return 1; }
  reapsha=$(git -C "$o" rev-parse reapup)
  export PATH="$t/bin:$PATH"; unset HANDOFF_TOPIC PR_N
  # run <mutant|-> <script> <args...>: copies of the scripts (less the mutant's
  # line), a fresh state root, the output in $t/out and the status in $t/rc.
  copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
    local g
    for g in open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh pr_cap.py ref_privacy.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
  }
  i=0
  run() {
    local mu=$1 sc=$2; shift 2; i=$((i + 1))
    # The last run's worktrees go, so a branch it checked out is free again.
    rm -rf "$t/s$((i - 1))"; git -C "$m" worktree prune
    copyin "$mu"
    HPO_STATE_DIR=$t/s$i BR=fix/x-$i BR_FIXED=1 bash "$m/tools/audit/seat/$sc" "$@" > "$t/out" 2>&1
    echo $? > "$t/rc"
  }
  # arm <name> <mutant> <expected text> <script> <args...>: refuses, naming it;
  # and the mutant without that line no longer prints the text.
  arm() {
    local nm=$1 mu=$2 want=$3; shift 3
    run - "$@"; [ "$(cat "$t/rc")" != 0 ] && grep -qF -- "$want" "$t/out"
    ck "$nm" $?
    run "$mu" "$@"; ! grep -qF -- "$want" "$t/out"
    ck "  mutant mut:$mu (its line deleted) fails that arm" $?
  }
  arm "open_pr: three arguments refuse, naming the count" arity \
    "open_pr: REFUSE: 3 argument(s), at least 4 needed" open_pr.sh x "$code" T
  arm "open_pr: an abbreviated code sha refuses as not 40-hex" hex \
    "open_pr: REFUSE: code sha '${code:0:12}' is not 40" open_pr.sh x "${code:0:12}" T G
  arm "open_pr: a 40-hex sha that names no commit refuses as unresolved" resolve \
    "open_pr: REFUSE: code sha 0123456789012345678901234567890123456789 does not resolve" \
    open_pr.sh x 0123456789012345678901234567890123456789 T G
  arm "open_pr: the body sha in the code slot refuses, naming it the BODY sha" body \
    "that is the BODY sha; pass the CODE sha" open_pr.sh x "$body" T G
  arm "open_pr: a non-ancestor refuses, saying it is not the body tip" ancestor \
    "open_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code), and it is not the tip of handoff-body/x" \
    open_pr.sh x "$side" T G
  arm "open_pr: a topic with no handoff/<topic> refuses, naming the ref" noref \
    "open_pr: REFUSE: origin has no handoff/z" open_pr.sh z "$code" T G
  arm "open_pr: a topic with no handoff-body/<topic> refuses, naming the ref" nobody \
    "open_pr: REFUSE: origin has no handoff-body/y" open_pr.sh y "$code" T G
  mkdir -p "$t/s$((i + 1))/pr/x/wt" "$t/s$((i + 2))/pr/x/wt"
  touch "$t/s$((i + 1))/pr/x/wt/f" "$t/s$((i + 2))/pr/x/wt/f"
  arm "open_pr: a failing step past the checks (worktree add) reports itself through the ERR trap" trap \
    "open_pr: STOPPED: line" open_pr.sh x "$code" T G
  # The soft cap gates dispatch, not opening (pr_cap.py; tvofi, 2026-10-20):
  # a twenty-strong open board is information, and --over-cap is advisory.
  prs() { # <counted> [extra json objects]: the stub's open list
    local k=0 j=""
    while [ $k -lt "$1" ]; do j="$j{\"number\":$k,\"title\":\"t\",\"author\":{\"login\":\"app/hpo-author\",\"is_bot\":true}},"; k=$((k + 1)); done
    printf '[%s%s]\n' "$j" "${2:-}" | sed 's/,]$/]/' > "$t/prs.json"
  }
  # passes <name> <mutant> <expected text> <args...>: the run opens (stops only
  # at the absent push), printing the text and no cap refusal; on a copy
  # without the mutant's line the text is gone and the run did not crash (a
  # deleted line that only tracebacks pins no behaviour).
  passes() {
    local nm=$1 mu=$2 want=$3; shift 3
    run - open_pr.sh "$@"; grep -qF -- "$want" "$t/out" \
      && ! grep -q 'REFUSE: open-PR cap\|REFUSE: WIP cap' "$t/out" \
      && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
    ck "$nm" $?
    run "$mu" open_pr.sh "$@"; ! grep -qF -- "$want" "$t/out" && ! grep -q Traceback "$t/out"
    ck "  mutant mut:$mu (its line deleted) no longer prints it" $?
  }
  prs 20
  passes "open_pr: twenty open pull requests do not stop an open; the count is information" openinfo \
    "open_pr: 20 open PRs; the cap gates dispatch, not opening" x "$code" T G
  passes "open_pr: --over-cap is still accepted, and says it is advisory" overadvisory \
    "open_pr: --over-cap is advisory: the train is draining (the cap gates dispatch, not opening)" \
    --over-cap "the train is draining" x "$code" T G
  touch "$t/gh.fail"
  run - open_pr.sh x "$code" T G
  grep -qF "open_pr: open pull requests could not be read (gh exited 1" "$t/out" \
    && ! grep -q 'REFUSE: open-PR cap\|REFUSE: WIP cap' "$t/out" \
    && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
  ck "open_pr: an open count gh cannot read says so and still opens" $?
  run inforead open_pr.sh x "$code" T G
  ! grep -qF "could not be read" "$t/out" && ! grep -q Traceback "$t/out"
  ck "  mutant mut:inforead (its line deleted) reports the unreadable board as a count" $?
  rm -f "$t/gh.fail"
  prs 5 '{"number":90,"title":"record: rows","author":{"login":"app/hpo-author","is_bot":true}},{"number":91,"title":"bump","author":{"login":"app/dependabot","is_bot":true}}'
  passes "open_pr: a record: title and another bot's pull request are not in the open count" caprecord \
    "open_pr: 5 open PRs; the cap gates dispatch, not opening" x "$code" T G
  passes "open_pr: the same board, the bot pull request uncounted" capbot \
    "open_pr: 5 open PRs; the cap gates dispatch, not opening" x "$code" T G
  echo '[]' > "$t/prs.json"
  run - open_pr.sh x "$code" T G
  [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
    && grep -qF "open_pr: REFUSE: the push failed; its log is $t/s$i/pr/x/p1.log" "$t/out" \
    && ! grep -q STOPPED "$t/out"
  ck "null control: open_pr with the code sha passes every check, and its failed push names its log" $?
  # A refused or stopped open tidies its worktree (P72): one whose branch origin never had is
  # removed with its local branch, so the next open of the topic can add both again; one that is
  # dirty, or whose branch origin holds, is kept on its branch and named (pr_release_wt).
  [ ! -e "$t/s$i/pr/x/wt" ] && ! git -C "$m" show-ref -q --verify "refs/heads/fix/x-$i" && ! grep -qF 'open_pr: KEPT' "$t/out"
  ck "open_pr: a refused open whose branch origin never had leaves no worktree and no local branch (P72)" $?
  run reltidy open_pr.sh x "$code" T G
  [ -d "$t/s$i/pr/x/wt" ] && git -C "$m" show-ref -q --verify "refs/heads/fix/x-$i"
  ck "  mutant mut:reltidy (its line deleted): the refused open's worktree still holds its branch" $?
  # handoff/k carries a push stub that leaves an untracked file in the worktree (k=dirt) or pushes
  # the branch to origin (k=orig), then fails: the two worktrees the tidy must keep.
  for k in dirt orig; do
    [ -e "$t/fix$k" ] && continue
    git -C "$o" checkout -q -b "handoff/$k" "$base" && mkdir -p "$o/tools/pr" && printf 'b\n' > "$o/b" \
      && if [ "$k" = dirt ]; then printf '#!/bin/bash\n: > "$2/dirt"; exit 1\n'; else printf '#!/bin/bash\ngit -C "$2" push -q origin "$3"; exit 1\n'; fi > "$o/tools/pr/app_push.sh" \
      && git -C "$o" add b tools/pr/app_push.sh && git -C "$o" commit -q -m "code $k" \
      && git -C "$o" update-ref "refs/heads/handoff-body/$k" "$body" && git -C "$o" checkout -q main && touch "$t/fix$k"
  done
  kept() { # <mutant> <k>: open_pr on handoff/<k>; rc 0 when its worktree is kept on its branch and named
    run "$1" open_pr.sh "$2" "$(git -C "$o" rev-parse "handoff/$2")" T G
    git -C "$t/s$i/pr/$2/wt" symbolic-ref -q HEAD >/dev/null 2>&1 && grep -qF "open_pr: KEPT $t/s$i/pr/$2/wt on fix/x-$i" "$t/out"
  }
  kept - dirt; ck "null control: a refused open whose worktree is dirty is kept on its branch and named" $?
  kept reldirty dirt; ! grep -qF 'it is dirty' "$t/out"
  ck "  mutant mut:reldirty (its line deleted): the dirty worktree is not named as dirty" $?
  kept - orig; ck "null control: a refused open whose branch origin holds is kept on its branch and named" $?
  git -C "$o" branch -qD "fix/x-$i"
  kept relorigin orig; git -C "$o" branch -qD "fix/x-$i"; [ ! -e "$t/s$i/pr/orig/wt" ]
  ck "  mutant mut:relorigin (its line deleted): the worktree of a branch origin holds is removed" $?
  # pr_tools_fresh (P-P): the checkout holding these tools refuses when origin/main has commits it
  # lacks under tools/audit/seat or tools/pr; any other path is no refusal (null control), and
  # HPO_ALLOW_STALE_TOOLS=1 says so and goes on. A commit on the scratch origin's main makes the
  # clone's tools stale for one run, then main returns to base.
  fresh() { # <mutant> <path committed on origin main> <script> <args...>
    local mu=$1 p=$2; shift 2
    mkdir -p "$o/$(dirname "$p")" && printf 's\n' > "$o/$p" && git -C "$o" add "$p" && git -C "$o" commit -q -m "main: $p"
    run "$mu" "$@"
    git -C "$o" reset -q --hard "$base"; git -C "$m" fetch -q origin main
  }
  fresh - tools/audit/seat/zz open_pr.sh x "$code" T G
  [ "$(cat "$t/rc")" != 0 ] && grep -qE "open_pr: REFUSE: STALE CHECKOUT [0-9a-f]{12} behind origin/main [0-9a-f]{12} by 1 commit\(s\) touching tools/audit/seat tools/pr" "$t/out" \
    && ! grep -qF "the push failed" "$t/out"
  ck "open_pr: tools behind origin/main under tools/audit/seat refuse, naming the count" $?
  fresh stale tools/audit/seat/zz open_pr.sh x "$code" T G; ! grep -qF "REFUSE: STALE CHECKOUT" "$t/out" && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
  ck "  mutant mut:stale (its line deleted): the stale tools open" $?
  fresh - docs/zz open_pr.sh x "$code" T G
  ! grep -qF "STALE CHECKOUT" "$t/out" && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
  ck "null control: origin/main ahead only under docs/ is no refusal; the run reaches its push" $?
  fresh freshpaths docs/zz open_pr.sh x "$code" T G; grep -qF "STALE CHECKOUT" "$t/out"
  ck "  mutant mut:freshpaths (its line deleted): a docs/-only difference refuses" $?
  HPO_ALLOW_STALE_TOOLS=1 fresh - tools/pr/zz open_pr.sh x "$code" T G
  grep -qF "open_pr: NOTICE: STALE CHECKOUT" "$t/out" && grep -qF "open_pr: REFUSE: the push failed" "$t/out"
  ck "open_pr: HPO_ALLOW_STALE_TOOLS=1 names the stale tools and goes on to the push" $?
  cp "$t/body.md" "$t/b.md"; fresh - tools/pr/zz update_pr.sh fix/x - "$t/b.md"
  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: STALE CHECKOUT" "$t/out" && ! grep -qF "the push failed" "$t/out"
  ck "update_pr: tools behind origin/main under tools/pr refuse too" $?
  # ---- a stopped pusher reaps its whole descendant tree (R10-PUSHER-REAP) ----
  # The stub app_push above leaves a two-level sleep tree recorded by pid, so
  # each arm counts what is still alive after the signal. The bystander sleeper
  # started here descends from no pusher: it is the null control for "kills only
  # what it started", and the arm the by-pid rule is mutated against.
  ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"
  "$REAP_DIR/unrelated-sleep" "${PR_SELFTEST_SECONDS:-1200}" & UNREL=$!  # the bound's session ends it at the latest
  ralive() { # <pids file> -> how many of its pids are alive; polled, since a killed child can be a zombie for a moment
    local p n k=0
    while :; do
      n=0
      for p in $(cat "$1" 2>/dev/null); do kill -0 "$p" 2>/dev/null && n=$((n + 1)); done
      if [ "$n" = 0 ] || [ "$k" -ge 30 ]; then echo "$n"; return; fi
      sleep 0.1; k=$((k + 1))
    done
  }
  rclean() { # end this fixture's recorded pids and their children, by pid (never a pattern): a child
    # left alive would hold the push's lock (pr_push_hold) until its own sleep ends
    local p all q
    all=$(cat "$REAP_DIR/pids" 2>/dev/null); q=$all
    while [ -n "$q" ]; do q=$(for p in $q; do pgrep -P "$p" 2>/dev/null; done); all="$all $q"; done  # all of them first: a killed parent's child is reparented
    for p in $all; do
      case $p in ''|0|1|*[!0-9]*) ;; *) kill -KILL "$p" 2>/dev/null ;; esac
    done
    : > "$REAP_DIR/pids"
  }
  # stopreap <script> <args...>: signal a pusher (TERM, or $STOPSIG) once its
  # push's tree is recorded (four pids), then record whether it is gone, what of
  # the tree survives it, and whether the bystander does; the scripts are copyin's.
  stopreap() {
    local sc=$1 up k=0; shift
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok"; : > "$REAP_DIR/pids"
    # A background job here starts with INT ignored, which bash cannot undo; the
    # exec resets it, as a terminal's foreground job has it.
    python3 -I -c 'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp("bash", sys.argv[1:])' \
      bash "$m/tools/audit/seat/$sc" "$@" > "$t/out" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    wc -l < "$REAP_DIR/pids" | tr -d ' ' > "$t/treen"
    kill -"${STOPSIG:-TERM}" "$up"; k=0
    while kill -0 "$up" 2>/dev/null && [ $k -lt 40 ]; do sleep 0.1; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    rclean; wait "$up" 2>/dev/null
  }
  # Each verdict first asks that the push's tree started, so a run that stopped
  # short of its push cannot pass an arm with nothing to reap.
  reaped() { [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/pusher")" = gone ] && [ "$(cat "$t/survivors")" = 0 ] && echo 0 || echo 1; }
  survived() { [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/survivors")" -gt 0 ] && echo 0 || echo 1; }
  reapopen() { # <mutant>: TERM open_pr.sh mid-push
    local sd=$t/ropen
    git -C "$m" worktree prune; rm -rf "$sd"; copyin "$1"
    HPO_STATE_DIR=$sd stopreap open_pr.sh reap "$reapsha" T G
    { [ -e "$sd/pr/reap/wt" ] || git -C "$m" show-ref -q --verify refs/heads/fix/reap; } && echo kept > "$t/ropenwt" || echo gone > "$t/ropenwt"
    git -C "$m" worktree remove --force "$sd/pr/reap" 2>/dev/null
    git -C "$m" branch -D fix/reap fix/reap-pr >/dev/null 2>&1; rm -rf "$sd"
  }
  reapopen -
  ck "open_pr: TERM reaps the whole descendant tree, and the pusher is gone" "$(reaped)"
  ck "open_pr: and the stopped open, its branch never pushed, leaves no worktree and no local branch (P-D, P72)" \
     "$( [ "$(cat "$t/ropenwt")" = gone ] && echo 0 || echo 1 )"
  ck "open_pr: the null control -- an unrelated sleeper survives" \
     "$( [ "$(cat "$t/unrel")" = alive ] && echo 0 || echo 1 )"
  STOPSIG=INT reapopen -
  ck "open_pr: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it" "$(reaped)"
  reapopen stop
  ck "  mutant mut:stop (the reap's kill line deleted): the pusher dies and its tree survives" "$(survived)"
  reapopen exitreap
  ck "  mutant mut:exitreap (pr_exit_trap's trap line deleted): the pusher dies and its tree survives" "$(survived)"
  # handoff_push.sh and remerge_main.sh run app_push from the main checkout, so
  # the stub stands there for these arms alone.
  cp "$REAP_DIR/reap-stub.sh" "$m/tools/pr/app_push.sh"
  reaphandoff() { # <mutant>: TERM handoff_push.sh mid-push (the new-PR route, on a branch of its own)
    local sd=$t/rhand
    git -C "$m" worktree prune; rm -rf "$sd"; copyin "$1"
    HPO_STATE_DIR=$sd HPO_WT_ROOT=$sd BRNAME=fix/rhand stopreap handoff_push.sh reap "$reapsha" T
    git -C "$m" worktree remove --force "$sd/fix-rhand" 2>/dev/null
    git -C "$m" branch -D fix/rhand >/dev/null 2>&1; rm -rf "$sd"
  }
  reaphandoff -
  ck "handoff_push: TERM reaps the whole descendant tree, and the pusher is gone" "$(reaped)"
  STOPSIG=INT reaphandoff -
  ck "handoff_push: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it" "$(reaped)"
  reaphandoff exitreap
  ck "  mutant mut:exitreap: handoff_push dies and its tree survives" "$(survived)"
  reapremerge() { # <mutant>: TERM remerge_main.sh mid-push
    local w=$t/rrem
    git -C "$m" worktree prune; rm -rf "$w"; copyin "$1"
    git -C "$m" worktree add -q --detach "$w" "$reapsha" 2>/dev/null
    cp "$t/body.md" "$t/rbody.md"
    stopreap remerge_main.sh 7 "$w" handoff/reap "$t/rbody.md"
    git -C "$m" worktree remove --force "$w" 2>/dev/null
  }
  reapremerge -
  ck "remerge_main: TERM reaps the whole descendant tree, and the pusher is gone" "$(reaped)"
  STOPSIG=INT reapremerge -
  ck "remerge_main: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it" "$(reaped)"
  reapremerge exitreap
  ck "  mutant mut:exitreap: remerge_main dies and its tree survives" "$(survived)"
  rm -f "$m/tools/pr/app_push.sh"
  # The reap's own bounds, on a host that sources pr_args.sh and starts a child
  # that ignores TERM: only the KILL past the grace ends it, and a second TERM
  # during the grace must not end the host before that KILL.
  printf '. "$1"; pr_exit_trap\nbash -c '"'"'trap "" TERM; sleep 30 & echo $! >> "$0"; echo $$ >> "$0"; wait'"'"' "$REAP_DIR/pids" &\nwait $!\n' > "$t/host.sh"
  stubborn() { # <mutant>
    local hp k=0
    : > "$REAP_DIR/pids"; copyin "$1"
    bash "$t/host.sh" "$m/tools/audit/seat/pr_args.sh" & hp=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 2 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done
    kill -TERM "$hp"; sleep 0.5; kill -TERM "$hp" 2>/dev/null
    wait "$hp" 2>/dev/null; echo $? > "$t/rc"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    for k in $(cat "$REAP_DIR/pids"); do case $k in ''|*[!0-9]*) ;; *) kill -KILL "$k" 2>/dev/null ;; esac; done
  }
  stubborn -
  ck "the reap KILLs a child that ignores TERM once the grace is spent, through a second TERM; the host exits 143" \
     "$( [ "$(cat "$t/survivors")" = 0 ] && [ "$(cat "$t/rc")" = 143 ] && echo 0 || echo 1 )"
  stubborn grace
  ck "  mutant mut:grace (the KILL line deleted): the TERM-proof child survives" "$(survived)"
  stubborn sigign
  ck "  mutant mut:sigign (its line deleted): the second TERM ends the host mid-reap and the child survives" "$(survived)"
  # The lead (train.sh's merge_train.py, cloud_relay.sh's update_pr.sh) stops its own tree
  # first. The lead's child G stands for update_pr.sh's lock holder: G marks a TERM it gets;
  # the lead, TERMed, waits 0.5 s and writes "early" when G was TERMed beside it, then ends G.
  printf '. "$1"; pr_exit_trap\nbash "$0.lead" & PR_REAP_LEAD=$!\nwait $!\n' > "$t/lhost.sh"
  printf 'echo $$ >> "$REAP_DIR/pids"\nbash -c '"'"'trap "echo G >> \"$0\"; exit 0" TERM; while :; do sleep 0.1; done'"'"' "$REAP_DIR/marks" & g=$!; echo $g >> "$REAP_DIR/pids"\ntrap '"'"'sleep 0.5; grep -q G "$REAP_DIR/marks" && echo early >> "$REAP_DIR/marks"; kill $g 2>/dev/null; wait $g; exit 143'"'"' TERM\nwait\n' > "$t/lhost.sh.lead"
  leadrun() { # <mutant>
    local hp k=0
    : > "$REAP_DIR/pids"; : > "$REAP_DIR/marks"; copyin "$1"
    bash "$t/lhost.sh" "$m/tools/audit/seat/pr_args.sh" & hp=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 2 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done
    kill -TERM "$hp"; wait "$hp" 2>/dev/null
    ralive "$REAP_DIR/pids" > "$t/survivors"
    for k in $(cat "$REAP_DIR/pids"); do case $k in ''|*[!0-9]*) ;; *) kill -KILL "$k" 2>/dev/null ;; esac; done
  }
  leadrun -
  ck "a lead (PR_REAP_LEAD) is TERMed alone and stops its own child first; nothing of its tree survives" \
     "$( [ "$(cat "$t/survivors")" = 0 ] && grep -qx G "$REAP_DIR/marks" && ! grep -q early "$REAP_DIR/marks" && echo 0 || echo 1 )"
  leadrun lead
  ck "  mutant mut:lead (its line deleted): the lead's child is TERMed beside the lead" \
     "$( grep -q early "$REAP_DIR/marks" && echo 0 || echo 1 )"
  # A stale PR_REAP_LEAD -- a pid outside the walk, as a reused one is -- is never signalled.
  printf '. "$1"; pr_exit_trap; PR_REAP_LEAD=$2\nsleep 30 & echo $! >> "$REAP_DIR/pids"\nwait $!\n' > "$t/shost.sh"
  staleld() { # <mutant>
    local hp bp k=0
    : > "$REAP_DIR/pids"; copyin "$1"
    sleep 30 & bp=$!
    bash "$t/shost.sh" "$m/tools/audit/seat/pr_args.sh" "$bp" & hp=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 1 ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done
    kill -TERM "$hp"; wait "$hp" 2>/dev/null
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$bp" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    kill "$bp" 2>/dev/null; wait "$bp" 2>/dev/null; rclean
  }
  staleld -
  ck "a PR_REAP_LEAD outside the walk (a stale or reused pid) is never signalled; the host's own tree is reaped" \
     "$( [ "$(cat "$t/unrel")" = alive ] && [ "$(cat "$t/survivors")" = 0 ] && echo 0 || echo 1 )"
  staleld leadwalk
  ck "  mutant mut:leadwalk (its line deleted): the stale lead's process is TERMed" \
     "$( [ "$(cat "$t/unrel")" = gone ] && echo 0 || echo 1 )"
  # The census (the class rule): every path the rule returns is dispositioned and
  # every runner reaps. Its own null control is a scratch tree holding copies of
  # the entries plus one seam the census must refuse.
  ( pr_pushers > "$t/census" ); [ $? = 0 ] && ! grep -q '^OPEN' "$t/census" \
    && [ "$(grep -c '^ok ' "$t/census")" = "$(printf '%s\n' "$PR_PUSHERS" | grep -c .)" ]
  ck "the pusher census: the rule returns exactly the dispositioned paths, and every runner reaps" $?
  census() { # <extra file> <its text> [<entry> [<sed script applied to it; default: its pr_exit_trap line goes>]]
    local c=$t/census-tree f r
    rm -rf "$c"; throwaway_git_init "$c" -q
    r=$(cd "$src/../../.." && pwd)
    for f in $(printf '%s\n' "$PR_PUSHERS" | awk '{ print $1 }'); do
      mkdir -p "$c/$(dirname "$f")"; cp "$r/$f" "$c/$f"
    done
    [ -z "${3:-}" ] || sed -i "${4:-/^[^#]*pr_exit_trap/d}" "$c/$3"
    [ -z "$1" ] || { mkdir -p "$c/$(dirname "$1")"; printf '%s\n' "$2" > "$c/$1"; }
    git -C "$c" add -A; ( pr_pushers "$c" > "$t/census" ); echo $? > "$t/rc"
  }
  census "" ""; [ "$(cat "$t/rc")" = 0 ]
  ck "  the census on the scratch copy passes as it does on the tree" $?
  census tools/audit/seat/new_pusher.sh 'bash tools/pr/app_push.sh "$@"'
  [ "$(cat "$t/rc")" = 1 ] && grep -qF "OPEN tools/audit/seat/new_pusher.sh: undispositioned" "$t/census"
  ck "  a new script that runs app_push.sh is refused as undispositioned" $?
  census "" "" tools/audit/seat/handoff_push.sh
  [ "$(cat "$t/rc")" = 1 ] && grep -qF "OPEN tools/audit/seat/handoff_push.sh runner: no pr_exit_trap" "$t/census"
  ck "  a runner without pr_exit_trap is refused" $?
  census "" "" tools/audit/seat/handoff_push.sh '/bash "\$_push"/s/ &$//'
  [ "$(cat "$t/rc")" = 1 ] && grep -qF "OPEN tools/audit/seat/handoff_push.sh runner: a push runs in the foreground" "$t/census"
  ck "  a runner whose push runs in the foreground is refused (its \`2>&1\` backgrounds nothing)" $?
  census "" "" tools/audit/seat/update_pr.sh 's/{ pr_push_hold; //'
  [ "$(cat "$t/rc")" = 1 ] && grep -qF "OPEN tools/audit/seat/update_pr.sh runner: a push under the branch lock holds no push lock" "$t/census"
  ck "  a runner under the branch lock whose push holds no push lock is refused" $?
  census "" "" tools/audit/seat/update_pr.sh '/^pr_branch_lock /d; s/{ pr_push_hold; //'
  [ "$(cat "$t/rc")" = 0 ]
  ck "  null control: the same runner without its branch lock needs no push lock" $?
  arm "update_pr: two arguments refuse, naming the count" arity \
    "update_pr: REFUSE: 2 argument(s), at least 3 needed" update_pr.sh fix/x "$code"
  arm "update_pr: an abbreviated code sha refuses as not 40-hex" hex \
    "update_pr: REFUSE: code sha '${code:0:12}' is not 40" update_pr.sh fix/x "${code:0:12}" "$t/body.md"
  arm "update_pr: the body sha in the code slot refuses, naming it the BODY sha" body \
    "that is the BODY sha; pass the CODE sha" update_pr.sh fix/x "$body" "$t/body.md"
  arm "update_pr: a non-ancestor refuses, saying it is not the body tip" ancestor \
    "update_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code), and it is not the tip of handoff-body/x" \
    update_pr.sh fix/x "$side" "$t/body.md"
  arm "update_pr: a branch whose topic has no handoff/<topic> refuses, naming the ref" noref \
    "update_pr: REFUSE: origin has no handoff/q" update_pr.sh fix/q "$code" "$t/body.md"
  arm "update_pr: branch fix/x-pr, with no handoff/x-pr on origin, is checked against handoff/x" prtopic \
    "update_pr: REFUSE: code sha $side is not an ancestor of origin/handoff/x ($code)" \
    update_pr.sh fix/x-pr "$side" "$t/body.md"
  arm "update_pr: a failing step past the checks (fetching an absent branch) reports itself through the ERR trap" trap \
    "update_pr: STOPPED: line" update_pr.sh fix/x-absent - "$t/body.md"
  # Only the lock says BUSY: a step that exits 75 under errexit (here `gh pr view`) is a stop, which
  # cloud_relay.sh records, never a 75 it would retry unrecorded (#2469's round-4 carry).
  touch "$t/gh.75"; cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x - "$t/b.md"
  [ "$(cat "$t/rc")" = 1 ] && grep -qF "update_pr: STOPPED: line" "$t/out" && grep -qF "exited 75" "$t/out" && ! grep -qF BUSY "$t/out"
  ck "update_pr: a step exiting 75 is reported as a stop and exits 1, never 75 (BUSY)" $?
  cp "$t/body.md" "$t/b.md"; run busy75 update_pr.sh fix/x - "$t/b.md"; [ "$(cat "$t/rc")" = 75 ]
  ck "  mutant mut:busy75 (its line deleted): that step's 75 reaches the caller, which would read it as BUSY" $?
  rm -f "$t/gh.75"
  # reap: end every lock holder a fixture run recorded under $t (a mutant's may never exit), by
  # the holder pid its lock file names -- never pid 0 or 1, which kill reads as a group.
  reap() {
    local l h
    for l in $(find "$t" -name 'upd-*.lock' 2>/dev/null); do
      h=$(cut -d' ' -f2 "$l" 2>/dev/null); case $h in ''|0|1|*[!0-9]*) ;; *) kill "$h" 2>/dev/null ;; esac
    done
  }
  # One run per branch (the 2026-10-19/20 worktree vanish): update_pr.sh's fixed per-branch
  # worktree was force-removed under a concurrent run's prepr. lockrun <mutant> <hold: 1|0>
  # registers that worktree with a file in it (the in-flight run's), holds -- or, at 0, leaves
  # behind a dead pid in -- the branch's lock, and runs update_pr.sh on the branch.
  lockrun() {
    local s=$t/s$((i + 1)) hp="" k=0
    rm -f "$t/held"; mkdir -p "$s/pr"
    git -C "$m" worktree add -q --detach "$s/pr/upd-fix-x" && touch "$s/pr/upd-fix-x/live"
    if [ "$2" = 1 ]; then
      python3 -I -c 'import fcntl, os, sys, time; f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); f.write("%d 0\n" % os.getpid()); f.flush(); open(sys.argv[2], "w").close(); time.sleep(120)' \
        "$s/pr/upd-fix-x.lock" "$t/held" & hp=$!
      while [ ! -e "$t/held" ] && [ $k -lt 200 ]; do sleep 0.1; k=$((k + 1)); done
    else echo 99999 > "$s/pr/upd-fix-x.lock"; fi
    cp "$t/body.md" "$t/b.md"; run "$1" update_pr.sh fix/x - "$t/b.md"
    [ -z "$hp" ] || { kill "$hp" 2>/dev/null; wait "$hp" 2>/dev/null; }
    reap
    [ -e "$s/pr/upd-fix-x/live" ] && echo 1 > "$t/live" || echo 0 > "$t/live"
  }
  lockrun - 1
  [ "$(cat "$t/rc")" = 75 ] && grep -qF "update_pr: BUSY: another open_pr.sh or update_pr.sh run" "$t/out" \
    && [ "$(cat "$t/live")" = 1 ] && ! grep -q STOPPED "$t/out"
  ck "update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place" $?
  lockrun lock 1
  ! grep -qF "update_pr: BUSY" "$t/out" && [ "$(cat "$t/live")" = 0 ]
  ck "  mutant mut:lock (its line deleted) removes the in-flight run's worktree" $?
  lockrun - 0
  [ "$(cat "$t/rc")" != 0 ] && ! grep -qF "update_pr: BUSY" "$t/out" \
    && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
  ck "null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push" $?
  # The lock dies with the run, whatever the run started (#2469's round-1 review: an fd of the
  # run's shell was inherited by a `git gc --auto` git detached, which held the lock afterwards).
  # detrun <mutant>: two runs on fix/x in ONE state directory, one after the other; during the
  # first, a post-checkout hook (git runs it at `worktree add`) leaves a detached child behind.
  detrun() {
    local sd=$t/sd-$1 hk=$m/.git/hooks/post-checkout
    rm -rf "$t/s$i"; git -C "$m" worktree prune  # the last run's worktree holds fix/x
    copyin "$1"
    printf '#!/bin/sh\nsleep 30 </dev/null >/dev/null 2>&1 &\necho $! >> "%s/sleepers"\n' "$t" > "$hk"; chmod +x "$hk"
    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out1" 2>&1
    if kill -0 "$(cut -d' ' -f2 "$sd/pr/upd-fix-x.lock")" 2>/dev/null; then echo 1 > "$t/hold1"; else echo 0 > "$t/hold1"; fi
    rm -f "$hk"; git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null
    cp "$t/body.md" "$t/b.md"; HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/x - "$t/b.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
    [ -s "$t/sleepers" ] && kill $(cat "$t/sleepers") 2>/dev/null; rm -f "$t/sleepers"
    reap
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-x" 2>/dev/null; rm -rf "$sd"
  }
  detrun -
  grep -qF "update_pr: REFUSE: the push failed" "$t/out1" && ! grep -qF "update_pr: BUSY" "$t/out" \
    && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
  ck "update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push" $?
  [ "$(cat "$t/hold1")" = 0 ]
  ck "update_pr: the lock holder has exited by the time a run returns" $?
  detrun unlock; [ "$(cat "$t/hold1")" = 1 ]
  ck "  mutant mut:unlock (its line deleted): the holder is still alive when the run returns" $?
  # A stopped run reaps its whole descendant tree (R10-PUSHER-REAP): branch fix/t
  # carries the same stub app_push, so a TERM is judged by what survives it.
  # SIGKILL runs no trap, so sigrun below judges that case by the lock alone.
  # Every wait is on a condition with a bound, and the lock is read by trying it
  # (lockstate), never by a holder pid, which a late-reaped zombie still answers.
  # stoprun <mutant> <signal>: run 1 gets the signal mid-push.
  if [ ! -e "$t/fixt" ]; then
    git -C "$o" checkout -q -b fix/t "$base" && mkdir -p "$o/tools/pr" \
      && cp "$REAP_DIR/reap-stub.sh" "$o/tools/pr/app_push.sh" \
      && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m stub && git -C "$o" checkout -q main && touch "$t/fixt"
  fi
  lockstate() { # <lock file>: "held" or "free", by trying it -- the kernel frees a flock at exit, not at reap
    python3 -I -c 'import fcntl, sys
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: print("held"); sys.exit()
print("free")' "$1"
  }
  untilfree() { # <lock file> [seconds]: wait for the lock to be free; a bound, not a window: the arm fails past it
    # A wall-clock deadline (date +%s), not a count of ticks: each tick forks lockstate's Python, so
    # a count's length grows with the load (#2825 round 4: 200 ticks took 15.4 s under 6-way load).
    local end=$(($(date +%s) + ${2:-30}))
    while [ "$(lockstate "$1")" = held ] && [ "$(date +%s)" -lt "$end" ]; do sleep 0.05; done
  }
  updt() { cp "$t/body.md" "$t/b$1.md"; HPO_STATE_DIR=$2 bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b$1.md" > "$t/out$1" 2>&1; }
  stoprun() { # <mutant> <signal>
    local sd=$t/st-$1-$2 up k=0 hp t0
    rm -rf "$t/s$i"; git -C "$m" worktree prune
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok" "$t/out2" "$t/out3"; : > "$REAP_DIR/pids"
    copyin "$1"
    cp "$t/body.md" "$t/b1.md"  # run 1 is update_pr.sh itself, so the signal reaches it, not a subshell
    t0=$(date +%s)
    # The exec resets the INT a background job starts with ignored (stopreap's why).
    HPO_STATE_DIR=$sd python3 -I -c 'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp("bash", sys.argv[1:])' \
      bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b1.md" > "$t/out1" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    wc -l < "$REAP_DIR/pids" | tr -d ' ' > "$t/treen"
    [ "$(lockstate "$sd/pr/upd-fix-t.lock")" = held ] && echo 1 > "$t/held" || echo 0 > "$t/held"
    echo "$t0 $(cut -d' ' -f3 "$sd/pr/upd-fix-t.lock" 2>/dev/null) $(date +%s)" > "$t/start"  # the epoch between launch and now
    kill -"$2" "$up" 2>/dev/null
    k=0; while kill -0 "$up" 2>/dev/null && [ $k -lt 40 ]; do sleep 0.1; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    touch "$REAP_DIR/fast"  # every later run's stub exits at once
    updt 2 "$sd"; rclean; wait "$up" 2>/dev/null; updt 3 "$sd"
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  took_lock() { ! grep -qF "update_pr: BUSY" "$t/out3" && grep -qF "update_pr: REFUSE: the push failed" "$t/out3"; }
  stoprun - TERM
  ck "update_pr: TERM reaps the whole descendant tree, and the pusher is gone" "$(reaped)"
  ck "update_pr: the lock is held while the push runs" \
     "$( [ "$(cat "$t/held")" = 1 ] && echo 0 || echo 1 )"
  ck "update_pr: the held lock records its holder's start epoch beside the pids (cloud_relay.sh's STUCK andon ages it)" \
     "$(read -r a e z < "$t/start"; [ -n "$e" ] && [ "$a" -le "$e" ] && [ "$e" -le "$z" ] && echo 0 || echo 1)"
  ck "update_pr: after the stop the lock is free, so the next run takes it" \
     "$( ! grep -qF "update_pr: BUSY" "$t/out2" && took_lock && echo 0 || echo 1 )"
  stoprun - INT
  ck "update_pr: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it" "$(reaped)"
  stoprun stop TERM
  ck "  mutant mut:stop (the reap's kill line deleted): the pusher dies and its tree survives" "$(survived)"
  ck "  mutant mut:stop: and the lock stays held while that push runs, so the next run is BUSY (the drain, not the reap, guards it)" \
     "$( grep -qF "update_pr: BUSY" "$t/out2" && echo 0 || echo 1 )"
  # The lock outlives the push, whatever stops the run (R10-UPDATE-PR-SIGNALS). sigrun <mutant>
  # <how>: run 1, in a process group of its own, is stopped mid-push by <how>: KILL to the run
  # alone, or TERM or HUP to its whole group, which reaches the holder too. For a group signal the
  # push ignores TERM and HUP, so it outlives the signal until the reap's KILL.
  # The wait is for the condition the run must reach: the holder's `drain` mark, or the lock free.
  # The mark is written before the drain, so one read after that wait tells which came first.
  sigrun() {
    local sd=$t/sg-$1-$2 lf up k=0 sig=${2#grp} w0
    rm -rf "$t/s$i" "$sd"; git -C "$m" worktree prune; lf=$sd/pr/upd-fix-t.lock
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok" "$REAP_DIR/stubborn" "$t/out2" "$t/out3"; : > "$REAP_DIR/pids"
    [ "$sig" = "$2" ] || : > "$REAP_DIR/stubborn"
    copyin "$1"; cp "$t/body.md" "$t/b1.md"
    # A group of its own, not a session: the self-test's bound (pr_bounded) ends its session's members.
    HPO_STATE_DIR=$sd python3 -I -c 'import os, signal, sys; os.setpgid(0, 0); signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp("bash", sys.argv[1:])' \
      bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b1.md" > "$t/out1" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    wc -l < "$REAP_DIR/pids" | tr -d ' ' > "$t/treen"
    if [ "$sig" = "$2" ]; then kill -"$sig" "$up"; else kill -"$sig" -- "-$up"; fi 2>/dev/null
    k=0; while [ "$(cut -d' ' -f4 "$lf" 2>/dev/null)" != drain ] && [ "$(lockstate "$lf")" = held ] && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    # Those two mutants' holders free the lock only after the detach that follows the mark, so their
    # arms wait for the lock free, bounded at 10 s of wall clock, a third of the stub's 30 s push: held
    # at the bound is a holder that drains (#2825 round 3: one read at the mark was red in 4 of 6 runs
    # under load). BOUNDED=1 takes the same wait for an unmutated run, the bound's null control.
    w0=$(date +%s)
    case ${BOUNDED:-}$1 in 1* | drain | pushhold) untilfree "$lf" 10 ;; esac
    echo $(($(date +%s) - w0)) > "$t/waited"
    lockstate "$lf" > "$t/state"; cut -d' ' -f4 "$lf" 2>/dev/null > "$t/mark" || :; wtstate > "$t/wt1"
    [ "$sig$1" != KILL- ] || { touch "$REAP_DIR/fast"; updt 2 "$sd"; }  # every later run's stub exits at once
    rclean; untilfree "$lf"; lockstate "$lf" > "$t/after"; wtstate > "$t/wt2"
    k=0; while kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    touch "$REAP_DIR/fast"; wait "$up" 2>/dev/null; updt 3 "$sd"
    rm -f "$REAP_DIR/stubborn"; rclean
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  wtstate() { git -C "$sd/pr/upd-fix-t" symbolic-ref -q HEAD >/dev/null 2>&1 && echo branch || echo detached; }
  sigheld() { [ "$(cat "$t/treen")" -ge 4 ] && [ "$(cat "$t/mark")" = drain ] && [ "$(cat "$t/state")" = held ] && echo 0 || echo 1; }
  sigfreed() { [ "$(cat "$t/after")" = free ] && [ "$(cat "$t/pusher")" = gone ] && took_lock && echo 0 || echo 1; }
  sigrun - KILL 2>/dev/null  # the killed run's job notice
  ck "update_pr: a SIGKILLed run's lock stays held while its push runs" "$(sigheld)"
  ck "update_pr: and a run meanwhile is BUSY, naming that push" \
     "$( grep -qF "update_pr: BUSY: the push of run" "$t/out2" && echo 0 || echo 1 )"
  ck "update_pr: once that push ends the lock is free, and a later run takes it" "$(sigfreed)"
  ck "update_pr: the SIGKILLed run's worktree holds the branch while its push runs, and its lock's holder leaves it detached once the push has ended" \
     "$( [ "$(cat "$t/wt1") $(cat "$t/wt2")" = "branch detached" ] && echo 0 || echo 1 )"
  BOUNDED=1 sigrun - KILL 2>/dev/null
  ck "null control: an unmutated SIGKILLed run's lock still reads held after the mutants' 10 s wall-clock wait" \
     "$( [ "$(cat "$t/waited")" -ge 10 ] && [ "$(sigheld)" = 0 ] && echo 0 || echo 1 )"
  sigrun detach KILL 2>/dev/null
  ck "  mutant mut:detach (its line deleted): the SIGKILLed run's worktree still holds fix/t" \
     "$( [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/wt2")" = branch ] && echo 0 || echo 1 )"
  sigrun drain KILL 2>/dev/null
  ck "  mutant mut:drain (its line deleted): the holder lets go once the run is gone, while the push runs" \
     "$( [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/state")" = free ] && echo 0 || echo 1 )"
  sigrun pushhold KILL 2>/dev/null
  ck "  mutant mut:pushhold (its line deleted): the push holds no lock, so the holder lets go while it runs" \
     "$( [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/state")" = free ] && echo 0 || echo 1 )"
  for g in grpTERM grpHUP; do
    sigrun - $g 2>/dev/null
    ck "update_pr: ${g#grp} to the run's whole group: the holder outlives it and drains, letting go once nothing of the push holds its lock" \
       "$( [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/mark")" = drain ] && echo 0 || echo 1 )"
    ck "update_pr: and then the lock is free, and a later run takes it" "$(sigfreed)"
  done
  sigrun holdsig grpTERM 2>/dev/null
  ck "  mutant mut:holdsig (its line deleted): the group's TERM ends the holder, which never drains" \
     "$( [ "$(cat "$t/mark")" != drain ] && [ "$(cat "$t/state")" = free ] && echo 0 || echo 1 )"
  stoprun watch TERM
  ck "  mutant mut:watch (the holder's wait line deleted): the holder lets go at once, so the run never holds the lock and refuses" \
     "$( [ "$(cat "$t/held")" = 0 ] && grep -qF "update_pr: REFUSE: could not take the per-branch lock" "$t/out1" && echo 0 || echo 1 )"
  # With no ps and no pgrep (the R10-ROSTER-OPS carry from #2469 round 3: a host without ps re-execed
  # forever there): a PATH of links to every command but those two. A TERMed run says it cannot reap,
  # and its lock stays held until the push it could not end has ended; nothing hangs past that.
  if [ ! -d "$t/nops" ]; then
    mkdir -p "$t/nops"
    for g in $(printf '%s\n' "$PATH" | tr ':' ' '); do
      for k in "$g"/*; do
        case ${k##*/} in ps|pgrep) continue ;; esac
        [ -x "$k" ] && [ ! -e "$t/nops/${k##*/}" ] && ln -s "$k" "$t/nops/${k##*/}"
      done
    done 2>/dev/null
  fi
  nopsrun() { # <mutant>
    local sd=$t/np-$1 lf up k=0
    rm -rf "$t/s$i" "$sd"; git -C "$m" worktree prune; lf=$sd/pr/upd-fix-t.lock
    rm -f "$REAP_DIR/started" "$REAP_DIR/fast" "$REAP_DIR/ok" "$t/out3"; : > "$REAP_DIR/pids"
    copyin "$1"; cp "$t/body.md" "$t/b1.md"
    PATH=$t/nops HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b1.md" > "$t/out1" 2>&1 & up=$!
    while [ "$(wc -l < "$REAP_DIR/pids")" -lt 4 ] && kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    wc -l < "$REAP_DIR/pids" | tr -d ' ' > "$t/treen"
    kill -TERM "$up"
    k=0; while ! grep -qF "no pgrep" "$t/out1" && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    lockstate "$lf" > "$t/state"
    rclean; untilfree "$lf"; lockstate "$lf" > "$t/after"
    k=0; while kill -0 "$up" 2>/dev/null && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
    kill -0 "$up" 2>/dev/null && echo alive > "$t/pusher" || echo gone > "$t/pusher"
    touch "$REAP_DIR/fast"; wait "$up" 2>/dev/null; updt 3 "$sd"; rclean
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  nopsrun -
  ck "update_pr: with no ps or pgrep a TERMed run says it cannot reap, and keeps the lock while its push runs" \
     "$( grep -qF "update_pr: STOPPED: no pgrep on PATH" "$t/out1" && [ "$(cat "$t/treen")" = 4 ] && [ "$(cat "$t/state")" = held ] && echo 0 || echo 1 )"
  ck "update_pr: and once that push ends the run is gone, the lock free, and a later run takes it" "$(sigfreed)"
  nopsrun nopgrep
  ck "  mutant mut:nopgrep (its line deleted): the run stops without saying its tree was not reaped" \
     "$( ! grep -qF "no pgrep" "$t/out1" && echo 0 || echo 1 )"
  stopok() { # the null control: a run that succeeds leaves nothing behind
    local sd=$t/okrun
    rm -rf "$sd"; git -C "$m" worktree prune; rm -f "$REAP_DIR/started" "$REAP_DIR/fast"
    : > "$REAP_DIR/pids"; : > "$REAP_DIR/ok"; cp "$t/body.md" "$t/b.md"
    copyin -
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/t - "$t/b.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
    rm -f "$REAP_DIR/ok"
    ralive "$REAP_DIR/pids" > "$t/survivors"
    kill -0 "$UNREL" 2>/dev/null && echo alive > "$t/unrel" || echo gone > "$t/unrel"
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-t" 2>/dev/null; rm -rf "$sd"
  }
  stopok
  ck "null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start" \
     "$( [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/survivors")" = 0 ] && [ "$(cat "$t/unrel")" = alive ] && echo 0 || echo 1 )"
  # The branch a pull request is opened on belongs to one instrument at a time (R10-OPENPR-ROW-PUSH,
  # 2026-10-21, #2547 #2548 #2549). open_pr.sh commits the PR's own row in its worktree and pushes
  # it second; update_pr.sh (cloud_relay's arm, minutes later) detached any clean worktree holding
  # the branch and reset the branch to origin's, so the second push found HEAD detached and not
  # the branch's tip, and the PR kept no row. The stub app_push.sh is the real push's HEAD check:
  # call 1 pushes and "opens" #5, call 2 (the row's push) waits for $t/release, then refuses unless
  # HEAD is the branch's tip, and pushes. racerun <mutant>: open_pr.sh is in its second push when
  # update_pr.sh starts on the same branch. Expected: update_pr.sh is BUSY, the row reaches origin.
  if [ ! -e "$t/fixr" ]; then
    git -C "$o" checkout -q -b handoff/r "$base" && mkdir -p "$o/tools/pr" && printf 'b\n' > "$o/b" \
      && cat > "$o/tools/pr/app_push.sh" <<'STUB'
#!/bin/bash
D=$STUB_DIR; printf '%s\n' "$*" >> "$D/argv"; [ "$1" != --row-only ] || shift
wt=$2; br=$3; n=$(( $(cat "$D/n" 2>/dev/null || echo 0) + 1 )); echo $n > "$D/n"
case $n in
  1) git -C "$wt" push -q origin "$br" || exit 1; echo "app_push: PUSHED to $br; pull request #5 is open"; exit 0 ;;
  2) [ ! -e "$D/p2fail" ] || { echo "app_push: REFUSE: the body did not pass tools/pr/prepr.sh"; exit 1; }
     : > "$D/p2started"; k=0; while [ ! -e "$D/release" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
     [ "$(git -C "$wt" rev-parse HEAD)" = "$(git -C "$wt" rev-parse --verify "refs/heads/$br" 2>/dev/null)" ] \
       || { echo "app_push: REFUSE: worktree HEAD is not the committed tip of '$br'"; exit 1; }
     git -C "$wt" push -q origin "$br" || exit 1; echo "app_push: PUSHED the row"; exit 0 ;;
  *) [ -e "$D/p3ok" ] || exit 1; git -C "$wt" push -q origin "$br" || exit 1; echo "app_push: PUSHED the row"; exit 0 ;;
esac
STUB
    git -C "$o" add b tools/pr/app_push.sh && git -C "$o" commit -q -m "code r" \
      && git -C "$o" update-ref refs/heads/handoff-body/r "$body" && git -C "$o" checkout -q main \
      && git -C "$o" branch fix/u "$base" && touch "$t/fixr"
  fi
  codeR=$(git -C "$o" rev-parse handoff/r)
  printf '#!/bin/sh\n[ -e "%s/gh.fail" ] && { echo "HTTP 403" >&2; exit 1; }\ncase "$*" in *--head*) echo 5 ;; "pr list"*) cat "%s/prs.json" ;; "pr view"*) echo "a title" ;; "pr edit"*|"pr ready"*) exit 0 ;; *) exit 99 ;; esac\n' "$t" "$t" > "$t/bin/gh"
  racerun() {
    local sd=$t/race-${1//+/_} sdir=$t/race-${1//+/_}-stub g k=0 op
    rm -rf "$sd" "$sdir" "$t/s$i"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)  # git lists worktrees by physical path
    git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null
    git -C "$o" branch -qD fix/r 2>/dev/null
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
    done
    cp "$t/body.md" "$t/bR.md"
    HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
    while [ ! -e "$sdir/p2started" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
    HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/update_pr.sh" fix/r - "$t/bR.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
    touch "$sdir/release"; wait "$op"; echo $? > "$t/rco"
    git -C "$o" cat-file -e fix/r:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/rowpushed" || echo 0 > "$t/rowpushed"
    git -C "$sd/pr/r/wt" symbolic-ref -q HEAD >/dev/null 2>&1 && echo branch > "$t/opwt" || echo detached > "$t/opwt"
    cp "$sdir/argv" "$t/argv" 2>/dev/null || : > "$t/argv"
    reap; git -C "$m" worktree remove --force "$sd/pr/r/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-r" 2>/dev/null; true
  }
  racerun -
  [ "$(cat "$t/rcu")" = 75 ] && grep -qF "update_pr: BUSY" "$t/outu" && [ "$(cat "$t/rco")" = 0 ] \
    && grep -q '^PR=5 ' "$t/outo" && [ "$(cat "$t/rowpushed")" = 1 ]
  ck "open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin" $?
  # The opener releases the branch once, at the end (P64, P-D): a worktree level with its last push
  # is left detached, so no worktree holds the branch for the merge train's recarry.
  [ "$(cat "$t/opwt")" = detached ]
  ck "open_pr: a successful open leaves its worktree detached at the pushed head" $?
  # The row push asks app_push.sh for --row-only (P53): one full prepr per open, not two; the
  # code push never asks (null control).
  [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = --row-only ] && [ "$(sed -n 1p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
  ck "open_pr: its row push passes --row-only, and its code push does not" $?
  racerun release; [ "$(cat "$t/opwt")" = branch ] && [ "$(cat "$t/rowpushed")" = 1 ]
  ck "  mutant mut:release (its line deleted): the opened PR's worktree still holds its branch" $?
  racerun oprowonly; [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
  ck "  mutant mut:oprowonly (its line deleted): the row push runs the full prepr" $?
  # A refused row push (#2625, #2629: prepr refused p2 on a red CI reported after p1) left the row
  # commit unpushed in the opener's worktree, on the branch, and update_pr.sh refused it as unpushed
  # work; the PR stayed open without its row. The opener now returns its worktree to the pushed head,
  # releases it, and closes the PR with a read-back comment saying why, so the tick never finds an
  # open PR without its row. This arm's gh records the close and answers gh_comment.py's post and
  # read-back; `pr list` finds the PR only while it is open, as the real `--state open` does.
  cat > "$t/rowless-gh" <<'GH'
#!/usr/bin/env python3
import json, os, sys
d = os.environ["STUB_DIR"]; a = sys.argv[1:]; j = " ".join(a)
if a[:2] == ["pr", "close"]:
    open(os.path.join(d, "closed"), "w").write(j + "\n"); sys.exit(0)
if a[:2] == ["pr", "list"]:
    print("" if os.path.exists(os.path.join(d, "closed")) else 5); sys.exit(0)
if a[:2] == ["pr", "view"]: print("a title"); sys.exit(0)
if a[:2] in (["pr", "edit"], ["pr", "ready"]): sys.exit(0)
if "--head" in a: print(5); sys.exit(0)
if a[:1] == ["api"] and "--input" in a:
    body = json.load(open(a[a.index("--input") + 1]))["body"]
    open(os.path.join(d, "comment"), "w").write(body); print(json.dumps({"id": 1, "html_url": "u"})); sys.exit(0)
if a[:1] == ["api"] and a[1].endswith("/issues/comments/1"):
    print(json.dumps({"id": 1, "body": open(os.path.join(d, "comment")).read()})); sys.exit(0)
sys.exit(99)
GH
  mkdir -p "$t/rowless-bin" && cp "$t/rowless-gh" "$t/rowless-bin/gh" && chmod +x "$t/rowless-bin/gh"
  cp "$src/../../pr/gh_comment.py" "$m/tools/pr/gh_comment.py"
  rowless() { # <mutant>
    local sd=$t/rowless-$1 sdir=$t/rowless-$1-stub g
    rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
    git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null; git -C "$o" branch -qD fix/r 2>/dev/null
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
    touch "$sdir/p2fail" "$sdir/p3ok"; cp "$t/body.md" "$t/bR.md"
    PATH="$t/rowless-bin:$PATH" HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1; echo $? > "$t/rco"
    git -C "$sd/pr/r/wt" symbolic-ref -q HEAD >/dev/null 2>&1 && echo branch > "$t/opwt" || echo detached > "$t/opwt"
    [ -e "$sdir/closed" ] && echo 1 > "$t/closed" || echo 0 > "$t/closed"
    grep -qF 'was refused' "$sdir/comment" 2>/dev/null && grep -qF 'did not pass tools/pr/prepr.sh' "$sdir/comment" && echo 1 > "$t/why" || echo 0 > "$t/why"
    PATH="$t/rowless-bin:$PATH" HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/update_pr.sh" fix/r - "$t/bR.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
    git -C "$o" cat-file -e fix/r:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/rowpushed" || echo 0 > "$t/rowpushed"
    reap; git -C "$m" worktree remove --force "$sd/pr/r/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-r" 2>/dev/null; true
  }
  rowless -
  [ "$(cat "$t/rco")" != 0 ] && grep -qF "open_pr: CLOSED: #5 at" "$t/outo" && grep -qF "identical=True" "$t/outo" \
    && [ "$(cat "$t/closed")" = 1 ] && [ "$(cat "$t/why")" = 1 ] && [ "$(cat "$t/opwt")" = detached ] \
    && ! grep -qF ROWLESS "$t/outo" && grep -qF "no open pull request at fix/r" "$t/outu" && [ "$(cat "$t/rowpushed")" = 0 ]
  ck "open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree" $?
  rowless rowclose
  [ "$(cat "$t/closed")" = 0 ] && grep -qF "open_pr: ROWLESS: #5 is open" "$t/outo" && [ "$(cat "$t/opwt")" = detached ] \
    && [ "$(cat "$t/rcu")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
  ck "  mutant mut:rowclose (its line deleted): the PR stays open without its row (the defect); the next update_pr.sh lands it" $?
  rowless rowreset
  [ "$(cat "$t/opwt")" = branch ] && [ "$(cat "$t/rowpushed")" = 0 ]
  ck "  mutant mut:rowreset (its line deleted): the row commit stays unpushed on the branch in the opener's worktree (the defect)" $?
  racerun oplock; [ "$(cat "$t/rcu")" != 75 ] && ! grep -qF "update_pr: BUSY" "$t/outu" && [ "$(cat "$t/rco")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
  ck "  mutant mut:oplock (its line deleted): update_pr.sh takes the branch (not BUSY); the unpushed-work refusal alone keeps the row" $?
  racerun oplock+unpushed; [ "$(cat "$t/rco")" != 0 ] && grep -qF "is not the committed tip" "$t/outo" && [ "$(cat "$t/rowpushed")" = 0 ]
  ck "  mutants mut:oplock and mut:unpushed (both deleted): the row's push is refused, HEAD detached under it, and the PR keeps no row (the defect)" $?
  # Only committed work is detached from a worktree: one holding commits origin lacks is refused
  # (the old reset would have dropped them); one whose HEAD origin has is detached as before.
  unpushed() { # <mutant> <commit: 1|0>
    local sd=$t/unp-$1-$2 g
    rm -rf "$sd" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
    done
    git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
    [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
    cp "$t/body.md" "$t/bU.md"
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/u - "$t/bU.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
    git -C "$sd/pr/u/wt" symbolic-ref -q HEAD > "$t/attached" 2>&1 || echo detached > "$t/attached"
    reap; git -C "$m" worktree remove --force "$sd/pr/u/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-u" 2>/dev/null; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; true
  }
  unpushed - 1
  [ "$(cat "$t/rcu")" != 0 ] && grep -qF "update_pr: REFUSE: worktree" "$t/outu" && grep -qF "(unpushed work" "$t/outu" \
    && [ "$(cat "$t/attached")" = refs/heads/fix/u ]
  ck "update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch" $?
  unpushed unpushed 1; [ "$(cat "$t/attached")" = detached ] && ! grep -qF "(unpushed work" "$t/outu"
  ck "  mutant mut:unpushed (its line deleted): the worktree is detached under its unpushed commit" $?
  unpushed - 0
  [ "$(cat "$t/attached")" = detached ] && grep -qF "update_pr: REFUSE: the push failed" "$t/outu" && ! grep -qF "(unpushed work" "$t/outu"
  ck "null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push" $?
  # The row-only arm (R10-ROW-ONLY-UPDATE): with code sha `-` update_pr.sh asks app_push.sh for
  # --row-only, whose own verdict decides whether a full prepr is owed; a code sha never asks.
  # Branch fix/w carries an app_push.sh stub that records its arguments, then fails the push.
  if [ ! -e "$t/fixw" ]; then
    git -C "$o" checkout -q -b fix/w "$base" && mkdir -p "$o/tools/pr" \
      && printf '#!/bin/bash\necho "$*" > "%s/argv"; exit 1\n' "$t" > "$o/tools/pr/app_push.sh" \
      && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m stub && git -C "$o" checkout -q main && touch "$t/fixw"
  fi
  rowrun() { # <mutant> <code-sha|->: update_pr.sh on fix/w; the stub's arguments in $t/argv
    rm -f "$t/argv"; cp "$t/body.md" "$t/b.md"; HANDOFF_TOPIC=x run "$1" update_pr.sh fix/w "$2" "$t/b.md"; }
  rowrun - -; [[ $(cat "$t/argv" 2>/dev/null) == "--row-only tvofi/heatpump_optimizer "* ]]
  ck "update_pr: code sha '-' asks app_push.sh for --row-only, whose verdict decides the prepr" $?
  rowrun rowonly -; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
  ck "  mutant mut:rowonly (its line deleted): code sha '-' runs the full prepr" $?
  rowrun - "$code"; [[ $(cat "$t/argv" 2>/dev/null) == "tvofi/heatpump_optimizer "* ]]
  ck "null control: a code sha never asks for --row-only, so its push runs the full prepr" $?
  for c in "$code" -; do
    cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$c" "$t/b.md"
    [ "$(cat "$t/rc")" != 0 ] && ! grep -q 'REFUSE: code sha\|REFUSE: origin has\|argument(s)' "$t/out" \
      && grep -qF "update_pr: REFUSE: the push failed" "$t/out" && ! grep -q STOPPED "$t/out"
    ck "null control: update_pr with code sha '${c:0:7}' passes every check, and its failed push names its log" $?
  done
  # The run leaves its worktree detached (the merge train parked #2513, #2544 and #2547 on it).
  ! git -C "$t/s$i/pr/upd-fix-x" symbolic-ref -q HEAD >/dev/null && [ -z "$(git -C "$m" worktree list | grep -F '[fix/x]')" ]
  ck "update_pr: the run leaves its worktree detached, so no worktree holds the branch" $?
  cp "$t/body.md" "$t/b.md"; run detach update_pr.sh fix/x - "$t/b.md"
  git -C "$t/s$i/pr/upd-fix-x" symbolic-ref -q HEAD >/dev/null
  ck "  mutant mut:detach (its line deleted): the worktree still holds fix/x" $?
  # A run whose merge stops on a conflict leaves no merge behind (R10-FLY-ABORT-OWN-MERGE, P276:
  # #2935's half-merge, #2936's conflicted 106-file merge held their branches). fix/k and
  # handoff/k both change `a` from base, so update_pr.sh's merge of the code sha stops conflicted;
  # the holder aborts that merge, then detaches. Nothing is lost: the merge started from
  # origin/fix/k and merged only remote refs.
  if [ ! -e "$t/fixk" ]; then
    git -C "$o" checkout -q -b fix/k "$base" && printf 'k-branch\n' > "$o/a" && git -C "$o" commit -qam k-branch \
      && git -C "$o" checkout -q -b handoff/k "$base" && printf 'k-code\n' > "$o/a" && git -C "$o" commit -qam k-code \
      && git -C "$o" checkout -q main && touch "$t/fixk"
  fi
  kmerge() { # <mutant>: update_pr.sh on fix/k with the conflicting code sha; its worktree in $t/kwt
    cp "$t/body.md" "$t/b.md"; HANDOFF_TOPIC=k run "$1" update_pr.sh fix/k "$(git -C "$o" rev-parse handoff/k)" "$t/b.md"
    echo "$t/s$i/pr/upd-fix-k" > "$t/kwt"; git -C "$m" fetch -q origin fix/k; rm -rf "$t/kadd"
  }
  kclean() { # the worktree clean, detached at origin/fix/k, and a second worktree add -B fix/k elsewhere succeeds
    local w; w=$(cat "$t/kwt")
    [ "$(cat "$t/rc")" != 0 ] && [ -z "$(git -C "$w" status --porcelain)" ] && ! git -C "$w" symbolic-ref -q HEAD >/dev/null \
      && [ "$(git -C "$w" rev-parse HEAD)" = "$(git -C "$m" rev-parse origin/fix/k)" ] \
      && git -C "$m" worktree add -q -B fix/k "$t/kadd" origin/fix/k 2>/dev/null \
      && git -C "$m" worktree remove "$t/kadd"
  }
  kmerge -; kclean
  ck "update_pr: a run whose merge stops conflicted leaves its worktree clean, detached at origin/fix/k, and fix/k free for a second worktree" $?
  kmerge holdabort; ! kclean
  ck "  mutant mut:holdabort (its line deleted): the conflicted merge stays, and the worktree still holds fix/k" $?
  cp "$t/body.md" "$t/b.md"; run - update_pr.sh fix/x "$code" "$t/b.md"
  git -C "$t/s$i/pr/upd-fix-x" merge-base --is-ancestor "$code" HEAD && [ -z "$(git -C "$t/s$i/pr/upd-fix-x" status --porcelain)" ]
  ck "null control: a run whose merge is clean keeps the merged code head under its HEAD, nothing aborted or reset" $?
  # remerge_main.sh, the merge train's recarry, the same way: a conflicting main leaves its worktree
  # clean at origin/<branch>, so the train's unforced release_worktrees removes it. Its own origin,
  # since main must move: rk at base changes `a` one way, main the other; rc merges cleanly.
  if [ ! -e "$t/rmo" ]; then
    { throwaway_git_init "$t/rmo" -q -b main && printf 'a\n' > "$t/rmo/a" && git -C "$t/rmo" add a && git -C "$t/rmo" commit -qm base \
      && git -C "$t/rmo" branch rk && git -C "$t/rmo" branch rc && mkdir -p "$t/rmo/tools/pr" \
      && printf '#!/bin/bash\necho stub-push-refused; exit 1\n' > "$t/rmo/tools/pr/app_push.sh" \
      && git -C "$t/rmo" add tools && git -C "$t/rmo" commit -qm stub && printf 'main\n' > "$t/rmo/a" && git -C "$t/rmo" commit -qam main \
      && git -C "$t/rmo" checkout -q rk && printf 'rk\n' > "$t/rmo/a" && git -C "$t/rmo" commit -qam rk \
      && git -C "$t/rmo" checkout -q rc && printf 'c\n' > "$t/rmo/c" && git -C "$t/rmo" add c && git -C "$t/rmo" commit -qm rc \
      && git -C "$t/rmo" checkout -q main && throwaway_git_clone -q "$t/rmo" "$t/rmm" && mkdir -p "$t/rmm/tools/audit/seat" \
      && touch "$t/rmo-ok"; } >/dev/null 2>&1
  fi
  rmrun() { # <mutant|-> <branch>: remerge_main.sh on <branch> in worktree $t/rmw; the output in $t/out
    local g; git -C "$t/rmm" worktree remove --force "$t/rmw" 2>/dev/null; rm -rf "$t/rmw"; git -C "$t/rmm" worktree prune
    for g in remerge_main.sh pr_args.sh; do grep -v "# mut:$1\$" "$src/$g" > "$t/rmm/tools/audit/seat/$g"; done
    git -C "$t/rmm" fetch -q origin "$2" && git -C "$t/rmm" worktree add -q -B "$2" "$t/rmw" "origin/$2" \
      && bash "$t/rmm/tools/audit/seat/remerge_main.sh" 7 "$t/rmw" "$2" "$t/body.md" > "$t/out" 2>&1
    echo $? > "$t/rc"
  }
  rmfree() { # MERGE CONFLICT named, the worktree clean at origin/rk, removed unforced, and rk free for a second worktree
    grep -qF "MERGE CONFLICT 7" "$t/out" && [ -z "$(git -C "$t/rmw" status --porcelain)" ] \
      && [ "$(git -C "$t/rmw" rev-parse HEAD)" = "$(git -C "$t/rmm" rev-parse origin/rk)" ] \
      && git -C "$t/rmm" worktree remove "$t/rmw" 2>/dev/null \
      && git -C "$t/rmm" worktree add -q -B rk "$t/rmadd" origin/rk 2>/dev/null && git -C "$t/rmm" worktree remove "$t/rmadd"
  }
  [ -e "$t/rmo-ok" ]; ck "remerge_main fixture: an origin whose main conflicts with rk" $?
  rmrun - rk; rmfree
  ck "remerge_main: a conflicting main is named MERGE CONFLICT and leaves the worktree clean at origin/rk, released unforced, rk free" $?
  rmrun remergeabort rk; ! rmfree
  ck "  mutant mut:remergeabort (its line deleted): the conflicted merge stays, and the worktree is not released" $?
  rmrun - rc; ! grep -qF "MERGE CONFLICT" "$t/out" && [ "$(git -C "$t/rmw" rev-parse HEAD^2)" = "$(git -C "$t/rmm" rev-parse origin/main)" ] \
    && [ "$(git -C "$t/rmw" rev-parse HEAD^1)" = "$(git -C "$t/rmm" rev-parse origin/rc)" ]
  ck "null control: remerge_main on a clean merge keeps that merge (HEAD's parents origin/rc and origin/main), nothing aborted" $?
  # The push's auto-maintenance runs in the foreground (#2825 round 1: a `git fetch` in the push
  # daemonized `git gc --auto`, which kept the push's fd 9, and so its lock, after the push). The
  # fixture's git has auto-maintenance off (throwaway_git); fix/g's stub push turns gc.auto back on
  # and runs real `git gc --auto` with its threshold met (two loose objects under objects/17), and
  # git prints "in background" exactly when it detaches.
  if [ ! -e "$t/fixg" ]; then
    git -C "$o" checkout -q -b fix/g "$base" && mkdir -p "$o/tools/pr" \
      && printf '#!/bin/bash\ngit -C "$REAP_DIR/gcrepo" -c gc.auto=1 gc --auto > "$REAP_DIR/gc.out" 2>&1\nexit 1\n' > "$o/tools/pr/app_push.sh" \
      && git -C "$o" add tools/pr/app_push.sh && git -C "$o" commit -q -m "gc stub" && git -C "$o" checkout -q main && touch "$t/fixg"
  fi
  gcrun() { # <mutant>
    local sd=$t/gc-$1 k
    rm -rf "$t/s$i" "$sd" "$REAP_DIR/gcrepo" "$REAP_DIR/gc.out"; git -C "$m" worktree prune
    throwaway_git_init "$REAP_DIR/gcrepo" -q
    for k in 212 650; do printf 'gc%s\n' "$k" | git -C "$REAP_DIR/gcrepo" hash-object -w --stdin >/dev/null; done  # blobs 17b370cc, 17e74e1d
    copyin "$1"; cp "$t/body.md" "$t/b1.md"
    HPO_STATE_DIR=$sd bash "$m/tools/audit/seat/update_pr.sh" fix/g - "$t/b1.md" > "$t/out1" 2>&1
    git -C "$m" worktree remove --force "$sd/pr/upd-fix-g" 2>/dev/null; rm -rf "$sd"
  }
  gcrun -
  grep -qF 'Auto packing the repository for optimum performance' "$REAP_DIR/gc.out" && grep -qF "update_pr: REFUSE: the push failed" "$t/out1"
  ck "update_pr: the push's git gc --auto runs in the foreground, as part of the push, so nothing it starts outlives the push holding its lock" $?
  gcrun fggc
  grep -qF 'Auto packing the repository in background' "$REAP_DIR/gc.out"
  ck "  mutant mut:fggc (its line deleted): git detaches that gc, which keeps the push's fd 9 once the push has ended" $?
  # The self-test bound (Revision 12). Each arm runs pr_bounded from a copy of this file; its child
  # holds a lock and marks it, so "ended" is read by trying the lock, never by a pid.
  cat > "$t/bchild.sh" <<'BCHILD'
#!/bin/bash
# <lock> <mark> <exit command>: a child holding <lock>, marked with its pid once it holds it
python3 -I -c 'import fcntl, os, sys, time
f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[2], "w").write("%d\n" % os.getpid()); time.sleep(20)' "$1" "$2" &
k=0; while [ ! -s "$2" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
eval "$3"
BCHILD
  bndend() { # the child, by its pid, whatever the arm left
    local p; p=$(cat "$t/bm" 2>/dev/null); case $p in ''|*[!0-9]*) ;; *) kill -KILL "$p" 2>/dev/null ;; esac; untilfree "$t/bl"
  }
  bnd() { # <mutant> <seconds> <exit command>: pr_bounded, from a copy of this file, over bchild.sh
    copyin "$1"; rm -f "$t/bl" "$t/bm" "$t/berr"
    PR_SELFTEST_SECONDS=$2 bash -c 'p=$1; shift; . "$p"; pr_bounded bt bash "$@"' bnd "$m/tools/audit/seat/pr_args.sh" \
      "$t/bchild.sh" "$t/bl" "$t/bm" "$3" 2> "$t/berr"
    echo $? > "$t/brc"; lockstate "$t/bl" > "$t/bstate"; bndend
  }
  rm -f "$t/blate"; bnd - 1 "sleep 3; touch $t/blate"
  ck "pr_bounded: a self-test past its bound is ended, its whole session with it, and exits 124 saying so" \
     "$( [ "$(cat "$t/brc") $(cat "$t/bstate")" = "124 free" ] && [ ! -e "$t/blate" ] && grep -qF 'bt: BOUND: the self-test passed 1 s' "$t/berr" && echo 0 || echo 1 )"
  rm -f "$t/blate"; bnd dogend 1 "sleep 3; touch $t/blate"
  ck "  mutant mut:dogend (its line deleted): the bound passes and nothing ends the self-test, which runs on" \
     "$( [ -e "$t/blate" ] && echo 0 || echo 1 )"
  bnd - 60 'exit 3'
  ck "pr_bounded: a self-test that exits leaving a child is reaped on exit, keeping its status" \
     "$( [ "$(cat "$t/brc") $(cat "$t/bstate")" = "3 free" ] && grep -qF 'bt: BOUND: the self-test left 1 process(es)' "$t/berr" && echo 0 || echo 1 )"
  bnd boundreap 60 'exit 3'
  ck "  mutant mut:boundreap (its line deleted): the child outlives the self-test" "$( [ "$(cat "$t/bstate")" = held ] && echo 0 || echo 1 )"
  # A SIGKILLed supervisor runs nothing; the watchdog reads its pipe's EOF and ends the session.
  bndkill() { # <mutant>
    local up k=0
    copyin "$1"; rm -f "$t/bl" "$t/bm"
    PR_SELFTEST_SECONDS=60 bash -c 'p=$1; shift; . "$p"; pr_bounded bt bash "$@"' bnd "$m/tools/audit/seat/pr_args.sh" \
      "$t/bchild.sh" "$t/bl" "$t/bm" wait 2>/dev/null & up=$!
    while [ ! -s "$t/bm" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
    [ -s "$t/bm" ] && echo up > "$t/bup" || echo none > "$t/bup"  # the child ran, so a free lock is an ending, not an absence
    kill -KILL "$up"; wait "$up" 2>/dev/null
    # A bound below the child's 20 s sleep, so a session nothing ends still reads held: 5 s of wall
    # clock (untilfree), not a count of ticks whose length grows with the load.
    untilfree "$t/bl" 5
    lockstate "$t/bl" > "$t/bstate"; bndend
  }
  bndkill - 2>/dev/null  # the killed supervisor's job notice
  ck "pr_bounded: a SIGKILLed supervisor's self-test is ended all the same, by its watchdog" "$( [ "$(cat "$t/bup") $(cat "$t/bstate")" = "up free" ] && echo 0 || echo 1 )"
  bndkill dogend 2>/dev/null
  ck "  mutant mut:dogend (its line deleted): the SIGKILLed supervisor's self-test runs on" "$( [ "$(cat "$t/bstate")" = held ] && echo 0 || echo 1 )"
  # A SIGKILL to the caller's whole group (a stopped loop, a daemonizer, a reap by group) takes the
  # supervisor with it; the watchdog, a session of its own, is out of its reach and ends the self-test.
  # The caller is a session of its own here, so the group kill reaches nothing of this self-test's.
  sidlive() { # <sid>: how many live processes the session holds; a zombie holds nothing
    python3 -I -c 'import os, sys
n = 0
for d in os.listdir("/proc"):
  try:
    st = open("/proc/%s/stat" % d).read().rsplit(")", 1)[1].split()
    n += int(st[3]) == int(sys.argv[1]) and st[0] != "Z"
  except (OSError, IndexError, ValueError): pass
print(n)' "$1"
  }
  bndgrp() { # <mutant>: writes the child's session survivors and the caller's to $t/bgrp
    local up k=0 csid
    copyin "$1"; rm -f "$t/bl" "$t/bm"
    PR_SELFTEST_SECONDS=60 python3 -I -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
      bash -c 'p=$1; shift; . "$p"; pr_bounded bt bash "$@"' bnd "$m/tools/audit/seat/pr_args.sh" \
      "$t/bchild.sh" "$t/bl" "$t/bm" wait 2>/dev/null & up=$!
    while [ ! -s "$t/bm" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
    [ -s "$t/bm" ] && echo up > "$t/bup" || echo none > "$t/bup"
    csid=$(python3 -I -c 'import os, sys; print(os.getsid(int(sys.argv[1])))' "$(cat "$t/bm")" 2>/dev/null)
    kill -KILL -- "-$up"; wait "$up" 2>/dev/null
    untilfree "$t/bl" 5  # below the child's 20 s sleep, as bndkill's
    lockstate "$t/bl" > "$t/bstate"; echo "$(sidlive "${csid:-0}") $(sidlive "$up")" > "$t/bgrp"; bndend
  }
  if [ -d /proc ]; then
    bndgrp - 2>/dev/null
    ck "pr_bounded: a SIGKILL to its caller's whole group still ends the self-test, 0 survivors in either session" \
       "$( [ "$(cat "$t/bup") $(cat "$t/bstate") $(cat "$t/bgrp")" = "up free 0 0" ] && echo 0 || echo 1 )"
    bndgrp dogsid 2>/dev/null
    ck "  mutant mut:dogsid (its line deleted): the group kill takes the watchdog too and the self-test runs on" \
       "$( [ "$(cat "$t/bstate")" = held ] && echo 0 || echo 1 )"
  else
    echo "  skip pr_bounded: the group-KILL arm counts a session through /proc, which this host lacks"
  fi
  # A `# mut:` line is a whole statement: copyin deletes one line, so a predicate continued from the
  # line above leaves that line running on into the next (round 2's first mut:fggc did, and its arm
  # read the broken copy as a pass). mutshape <files...>: exit 1 naming each such line.
  mutshape() { awk 'prev ~ /\\$/ && /# mut:[A-Za-z0-9]+$/ { print FILENAME ":" FNR; bad = 1 } { prev = $0 } END { exit bad }' "$@"; }
  (cd "$src" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
  ck "every # mut: line is a whole statement, never one continued from the line above" $?
  printf 'a \\\n  b  # mut:x\n' > "$t/mutshape.sh"; ! mutshape "$t/mutshape.sh" >/dev/null
  ck "null control: a # mut: line continued from the line above is named" $?
  # The cap's own counting rule, which orchestrator_tick.py imports too.
  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
  ck "pr_cap.py --self-test: its tally says 0 failed" $?
  reap
  kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :
  rm -rf "$t"
  echo "pr_args self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  case ${1:-} in
    --self-test) [ -n "${PR_BOUND:-}" ] || pr_bounded pr_args bash "$0" --self-test; pr_args_self_test; exit ;;
    --pushers) pr_pushers "" "${2:-}"; exit ;;
    *) sed -n '2,6p' "$0" >&2; exit 2 ;;
  esac
fi
