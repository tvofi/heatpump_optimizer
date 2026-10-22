#!/bin/bash
# heartbeat.sh --once --message TEXT      push the liveness ref
# heartbeat.sh --watch [--max-age SECONDS]  the off-host watcher's command
# heartbeat.sh --self-test
#
# The andon (Lean flow study K8, R10-FLOW-ANDON; the countermeasure whose cost
# test R10-RCA-ORCH-CONTINUITY runs: two orchestrator stops went unnoticed for
# 6 h and 16 h because no loop wrote a signal readable off the host).
#
# --once: force-push ONE ref, heartbeat/orchestrator, to a parentless commit of
#   the empty tree whose message is TEXT (tick_loop.sh passes the pass's
#   `TICK-PASS <utc> relay=<..> tick=<rc>`), with the seat's own credential
#   (`git push`, as wt_sync.sh does) and -f --no-verify. The message goes through
#   ref_privacy.py's guard first, as wt_sync.sh's does. A refused or failed push
#   prints `HEARTBEAT NOT PUSHED: <reason>` and exits 1; the caller's loop goes on.
#   This is a job script, not a loop: tick_loop.sh calls it once per pass and the
#   orchestrator machinery registers it later as the beat's heartbeat job. Run the
#   loop that calls it detached (daemonize.py), never as an agent turn.
# --watch: fetch the ref and compare its committer date with now. Prints
#   `HEARTBEAT FRESH age=<s>s` (exit 0) or `HEARTBEAT STALE: <why>` (exit 1);
#   --max-age defaults to 1200 (20 min). The owner schedules a cloud task that runs
#   it every 15 min and notifies the owner on exit 1; the schedule is not in the repo.
# HPO_HEARTBEAT_REMOTE names the remote (default origin).
set -uo pipefail
HERE=$(cd "$(dirname -- "$0")" && pwd)
REF=heartbeat/orchestrator
remote=${HPO_HEARTBEAT_REMOTE:-origin}

hb_push() { # <message>
  local msg=$1 c err
  python3 -I "$HERE/ref_privacy.py" guard --ref "$REF" --message "$msg" >/dev/null 2>&1 \
    || { echo "HEARTBEAT NOT PUSHED: ref_privacy guard refused the message"; return 1; }
  c=$(git -C "$HERE" commit-tree "$(git -C "$HERE" hash-object -t tree /dev/null)" -m "$msg" 2>&1) \
    || { echo "HEARTBEAT NOT PUSHED: commit-tree failed: $c"; return 1; }
  err=$(git -C "$HERE" push -q --no-verify -f "$remote" "$c:refs/heads/$REF" 2>&1) \
    || { echo "HEARTBEAT NOT PUSHED: $(printf '%s' "$err" | tr '\n' ' ')"; return 1; }
}

hb_watch() { # <max-age>
  local max=$1 err ts now age
  err=$(git -C "$HERE" fetch -q --no-tags "$remote" "+refs/heads/$REF:refs/hb/watch" 2>&1) \
    || { echo "HEARTBEAT STALE: no $REF on $remote ($(printf '%s' "$err" | tr '\n' ' '))"; return 1; }
  ts=$(git -C "$HERE" log -1 --format=%ct refs/hb/watch) || { echo "HEARTBEAT STALE: unreadable ref"; return 1; }
  now=$(date -u +%s); age=$((now - ts))
  if [ "$age" -gt "$max" ]; then
    echo "HEARTBEAT STALE: $REF is ${age}s old, limit ${max}s: $(git -C "$HERE" log -1 --format=%s refs/hb/watch)"
    return 1
  fi
  echo "HEARTBEAT FRESH age=${age}s"
}

hb_self_test() (
  local t f=0 n=0 out
  t=$(mktemp -d) || { echo "heartbeat self-test: no temporary directory"; return 1; }
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || return 1
  throwaway_git_init "$t/remote.git" -q --bare
  throwaway_git_init "$t/w" -q -b main
  git -C "$t/w" remote add origin "$t/remote.git"
  mkdir -p "$t/w/tools/audit/seat"
  cp "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/w/tools/audit/seat/"
  local hb=$t/w/tools/audit/seat/heartbeat.sh
  out=$(bash "$hb" --once --message "TICK-PASS 2026-10-21T10:00:00Z relay=ok tick=0")
  [ -z "$out" ] && [ "$(git -C "$t/remote.git" log -1 --format=%s heartbeat/orchestrator)" = "TICK-PASS 2026-10-21T10:00:00Z relay=ok tick=0" ]
  ck "--once moves heartbeat/orchestrator to a commit carrying the pass line" $?
  a=$(git -C "$t/remote.git" rev-parse heartbeat/orchestrator); sleep 1
  bash "$hb" --once --message "TICK-PASS 2026-10-21T10:05:00Z relay=rc=3 tick=1" >/dev/null
  b=$(git -C "$t/remote.git" rev-parse heartbeat/orchestrator)
  [ "$a" != "$b" ] && [ "$(git -C "$t/remote.git" rev-list --count heartbeat/orchestrator)" = 1 ]
  ck "a second pass force-moves the same ref (one parentless commit, no history)" $?
  out=$(bash "$hb" --once --message "TICK-PASS $HOME/x"); rc=$?
  [ $rc = 1 ] && printf '%s\n' "$out" | grep -q 'ref_privacy guard refused' \
    && [ "$(git -C "$t/remote.git" rev-parse heartbeat/orchestrator)" = "$b" ]
  ck "a message carrying the host's home directory is refused and the reachable ref does not move" $?
  out=$(bash "$hb" --watch --max-age 600); rc=$?
  [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT FRESH'
  ck "watcher: a fresh ref does not alert" $?
  old=$(GIT_COMMITTER_DATE="@$(( $(date +%s) - 1800 )) +0000" git -C "$t/w" commit-tree "$(git -C "$t/w" hash-object -t tree /dev/null)" -m "TICK-PASS old")
  git -C "$t/w" push -q -f origin "$old:refs/heads/heartbeat/orchestrator"
  out=$(bash "$hb" --watch --max-age 1200); rc=$?
  [ $rc = 1 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT STALE: .*TICK-PASS old'
  ck "watcher: a ref older than the limit alerts, naming its message" $?
  git -C "$t/remote.git" update-ref -d refs/heads/heartbeat/orchestrator
  out=$(bash "$hb" --watch); rc=$?
  [ $rc = 1 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT STALE: no heartbeat/orchestrator'
  ck "watcher: an absent ref alerts" $?
  git -C "$t/w" remote set-url origin "$t/nowhere.git"
  out=$(bash "$hb" --once --message "TICK-PASS x"); rc=$?
  [ $rc = 1 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED: .'
  ck "a refused push is printed with its reason and exits 1, never silent" $?
  rm -rf "$t"
  echo "heartbeat self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

mode=; msg=; max=1200
while [ $# -gt 0 ]; do
  case $1 in
    --self-test) hb_self_test; exit ;;
    --once) mode=once; shift ;;
    --watch) mode=watch; shift ;;
    --message) msg=${2:-}; shift 2 || shift ;;
    --max-age) max=${2:-}; shift 2 || shift ;;
    *) echo "heartbeat: unknown option '$1'" >&2; sed -n '2,4p' "$0" >&2; exit 2 ;;
  esac
done
case $max in ''|*[!0-9]*) echo "heartbeat: --max-age needs whole seconds, got '$max'" >&2; exit 2 ;; esac
case $mode in
  once) [ -n "$msg" ] || { echo "heartbeat: --once needs --message" >&2; exit 2; }; hb_push "$msg" ;;
  watch) hb_watch "$max" ;;
  *) echo "heartbeat: say --once or --watch" >&2; sed -n '2,4p' "$0" >&2; exit 2 ;;
esac
