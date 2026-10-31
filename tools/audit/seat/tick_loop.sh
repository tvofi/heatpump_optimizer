#!/bin/bash
# tick_loop.sh [--once] [--interval SECONDS] [--out FILE] [--sweep] [-- <orchestrator_tick.py args>]
# tick_loop.sh --self-test
#
# The tick's driver loop (the round-10 orchestrator, tvofi approved,
# 2026-10-18). Each pass, in order:
#   1. `cloud_relay.sh pass --confirm` (a relayed verdict is posted with no hand step), when the tree carries cloud_relay.sh (#2419). Before
#      that lands the step is skipped and the banner says so, so the tick still runs.
#      The relay runs detached under a holder of the flock <out>.relay.lock, so two
#      relay passes never overlap, and the pass waits for it at most
#      HPO_TICK_RELAY_WAIT seconds (default 30). A relay still in flight then is
#      left running, never killed (its update_pr.sh may be mid-push), and reported
#      relay=running; a pass that finds one in flight starts none. A relay pass that
#      ran 27+ min (update_pr.sh's prepr, #2525) left the board 66+ min stale while
#      this loop ran them serially (r10-tick-relay-decouple).
#   2. orchestrator_tick.py with the given args. The board goes to --out (default
#      $HPO_STATE_DIR/tick.txt, written whole then renamed, so a reader never sees
#      half a board).
#   0. Before both, the freshness check (P14, s5-batch1): `git fetch -q origin main` in
#      the checkout this script runs from, and behind = the commits in HEAD..origin/main
#      touching tools/audit/seat, tools/pr or tools/audit/carry_audit.py (the code the loop
#      runs). Past HPO_TICK_STALE_BOUND (default 25), or on any commit touching tick_loop.sh
#      or cloud_relay.sh, the loop restarts: with the relay lock free and the tree clean and
#      detached, it checks out origin/main detached, runs `bash -n` on the new tick_loop.sh
#      and execs it with the same arguments -- between passes, at most once per pass, never
#      a fast-forward in place (bash reads a running script as it goes). When it cannot, one
#        TICK-STALE <utc> code=<sha7> behind=<n>: <why>; the relay and sweep arms are skipped
#      line precedes the banner, the arms that act are skipped (relay=stale) and the board
#      is still written: never exit, never act from stale code. A failed fetch is
#      behind=unknown and the pass runs as before. HPO_TICK_CODE_DIR replaces the checkout.
# One banner line per pass on stdout:
#   TICK-PASS <utc> relay=<ok|rc=N|running|absent|stale> tick=<rc> code=<sha7|none> behind=<n|unknown> out=<file>
# The relay's output is printed when it is reaped; one that finished after its
# pass's wait is reaped by the next pass, with its own line before that banner:
#   TICK-RELAY <utc> relay=<ok|rc=N> started=<utc>
# A failing relay pass is reported and the tick still runs; a failing tick is
# reported and the loop goes on. The loop drives; the tick itself stays read-only.
#   3. --sweep only (R10-FLOW-AUTOTRAIN; off by default, and the first live sweep
#      runs with the orchestrator watching), the merge train's slow backstop: the
#      first pass, then the first pass HPO_TICK_SWEEP_EVERY seconds (default 1800)
#      after the last sweep, stamped in <out>.sweep.at. `merge_train.py sweep`
#      holds while the ledger holds an open train-stop, else `add`s every head the
#      queue builder admits that no sweep added at that head -- into the live
#      train's next batch, or a train.sh --bot-prs --approval-carry --pre-flight
#      it starts when none is live, never a second (merge_train.py's SWEEP block).
#      Loading is bus.sh's post's job, at each merge verdict; this catches a head
#      that missed it. Its output goes to <out>.sweep.log and one line follows the banner:
#        TICK-SWEEP <utc> rc=<rc> <the sweep's last line: SWEEP HELD|REFUSED|DONE ...>
#      HPO_SWEEP_MANDATE, when set, is passed as the train's --mandate; HPO_TICK_SWEEP_CMD
#      replaces the command (the self-test's stub).
# Then one `heartbeat.sh --once` pushes heartbeat/orchestrator with the pass line
# (no --out path), so a stop is visible off the host; a failed push prints
# `HEARTBEAT NOT PUSHED: <reason>` and the loop goes on (HPO_TICK_HEARTBEAT replaces it).
# --interval defaults to 300 (the five-minute GitHub poll). Run it detached
# (daemonize.py): a background task dies at two hours. HPO_TICK_RELAY and
# HPO_TICK_CMD replace the relay script and the tick command (the self-test's stubs).
set -uo pipefail
HERE=$(cd "$(dirname -- "$0")" && pwd)

# The relay holder: takes <out>.relay.lock (flock, non-blocking; 75 when held), runs
# the relay with its output in <out>.relay.log, then writes "<rc> <started-utc>" to
# <out>.relay.rc. Only this process holds the lock fd, so it frees on the holder's
# exit however that comes. 76: a finished relay's rc is not yet reaped; start none.
RELAY_HOLDER='import fcntl, os, subprocess, sys, time
r = sys.argv[1]
f = open(r + ".lock", "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(75)
if os.path.exists(r + ".rc"): sys.exit(76)
t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(r + ".log", "w") as log:
    rc = subprocess.call(sys.argv[2:], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
with open(r + ".rc.part", "w") as o: o.write("%d %s\n" % (rc, t))
os.replace(r + ".rc.part", r + ".rc")'

# The relay lock is free: rc 0 (the holder's flock, tried and released at once).
LOCK_FREE='import fcntl, sys
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(1)'
CODE_PATHS=(tools/audit/seat tools/pr tools/audit/carry_audit.py)
SELF_PATHS=(tools/audit/seat/tick_loop.sh tools/audit/seat/cloud_relay.sh)

behind_count() { # <checkout> <paths...>: the commits in HEAD..origin/main touching the paths
  local d=$1; shift
  git -C "$d" rev-list --count HEAD..origin/main -- "$@" 2>/dev/null
}

fresh_check() { # <out>: sets code, behind and stale (the acting arms are skipped); may exec the new loop
  local top self why bound=${HPO_TICK_STALE_BOUND:-25}
  case $bound in ''|*[!0-9]*) bound=25 ;; esac
  code=none behind=unknown stale=
  top=$(git -C "${HPO_TICK_CODE_DIR:-$HERE}" rev-parse --show-toplevel 2>/dev/null) || return 0
  code=$(git -C "$top" rev-parse --short=7 HEAD 2>/dev/null) || code=none
  git -C "$top" fetch -q origin main 2>/dev/null || return 0
  behind=$(behind_count "$top" "${CODE_PATHS[@]}") || { behind=unknown; return 0; }  # mut:paths
  [ "$behind" -gt 0 ] || return 0
  self=$(behind_count "$top" "${SELF_PATHS[@]}") || self=1
  [ "$behind" -gt "$bound" ] || [ "$self" -gt 0 ] || return 0  # mut:bound
  stale=1
  if [ -n "${HPO_TICK_RESTARTED:-}" ]; then why="restarted once this pass"
  elif ! python3 -I -c "$LOCK_FREE" "$1.relay.lock"; then why="a relay is in flight (the lock is held)"  # mut:lock
  elif git -C "$top" symbolic-ref -q HEAD >/dev/null; then why="a branch is checked out, not a detached head"
  elif [ -n "$(git -C "$top" status --porcelain --untracked-files=no)" ]; then why="the tree is dirty"  # mut:dirty
  elif ! git -C "$top" show origin/main:tools/audit/seat/tick_loop.sh | bash -n 2>/dev/null; then  # mut:syntax
    why="bash -n refuses origin/main's tick_loop.sh"
  elif ! git -C "$top" checkout -q --detach origin/main; then why="the checkout failed"
  else
    printf 'TICK-RESTART %s code=%s behind=%s -> %s\n' "$(date -u +%FT%TZ)" "$code" "$behind" \
      "$(git -C "$top" rev-parse --short=7 HEAD)"
    HPO_TICK_RESTARTED=1 exec bash "$top/tools/audit/seat/tick_loop.sh" "${ARGV[@]}"  # mut:exec
  fi
  printf 'TICK-STALE %s code=%s behind=%s: %s; the relay and sweep arms are skipped\n' \
    "$(date -u +%FT%TZ)" "$code" "$behind" "$why"
}

relay_reap() { # <r> [late]: print a finished relay's output; sets rrc. 1: nothing to reap
  local r=$1 st
  [ -f "$r.rc" ] || return 1
  read -r rrc st < "$r.rc"
  cat "$r.log" 2>/dev/null; rm -f "$r.rc"
  [ "$rrc" = 0 ] && rrc=ok || rrc="rc=$rrc"
  [ -z "${2:-}" ] || printf 'TICK-RELAY %s relay=%s started=%s\n' "$(date -u +%FT%TZ)" "$rrc" "$st"
}

relay_start() { # <r> <relay>: start the relay detached, wait for it at most the bound; sets rrc
  local r=$1 relay=$2 hp hrc k=0 wait=${HPO_TICK_RELAY_WAIT:-30}
  case $wait in ''|*[!0-9]*) wait=30 ;; esac
  python3 -I -c "$RELAY_HOLDER" "$r" bash "$relay" pass --confirm </dev/null >/dev/null 2>&1 & hp=$!  # mut:confirm
  while kill -0 "$hp" 2>/dev/null && [ $k -lt $((wait * 10)) ]; do sleep 0.1; k=$((k + 1)); done
  if kill -0 "$hp" 2>/dev/null; then rrc=running; return 0; fi  # mut:detach
  wait "$hp"; hrc=$?
  case $hrc in
    0) relay_reap "$r" || rrc="rc=lost" ;;
    75) rrc=running ;;
    *) rrc="rc=holder-$hrc" ;;
  esac
}

sweep_pass() { # <out>: one merge-train sweep when one is due; prints its TICK-SWEEP line
  local log=$1.sweep.log at=$1.sweep.at src last every=${HPO_TICK_SWEEP_EVERY:-1800}
  case $every in ''|*[!0-9]*) every=1800 ;; esac
  last=$(cat "$at" 2>/dev/null); case $last in ''|*[!0-9]*) last=0 ;; esac
  [ $(( $(date +%s) - last )) -ge "$every" ] || return 0  # mut:due
  date +%s > "$at"
  if [ -n "${HPO_TICK_SWEEP_CMD:-}" ]; then $HPO_TICK_SWEEP_CMD > "$log" 2>&1; src=$?
  else python3 "$HERE/merge_train.py" sweep ${HPO_SWEEP_MANDATE:+--mandate "$HPO_SWEEP_MANDATE"} > "$log" 2>&1; src=$?; fi
  printf 'TICK-SWEEP %s rc=%s %s\n' "$(date -u +%FT%TZ)" "$src" "$(tail -n 1 "$log")"
}

tick_pass() { # <out> [tick args...]: one pass; prints the banner
  local out=$1 relay rrc trc tmp now code behind stale; shift
  relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
  mkdir -p "$(dirname -- "$out")"
  fresh_check "$out"
  if [ -n "$stale" ]; then
    rrc=stale  # mut:skip
  elif [ -f "$relay" ]; then
    relay_start "$out.relay" "$relay"
    # 76: an earlier pass's relay finished after its wait; reap it, then start this pass's.
    [ "$rrc" = rc=holder-76 ] && { relay_reap "$out.relay" late; relay_start "$out.relay" "$relay"; }  # mut:reap
  else
    rrc=absent
  fi
  tmp="$out.part.$$"
  if [ -n "${HPO_TICK_CMD:-}" ]; then $HPO_TICK_CMD "$@" > "$tmp" 2>&1; trc=$?
  else python3 "$HERE/orchestrator_tick.py" "$@" > "$tmp" 2>&1; trc=$?; fi
  mv -f "$tmp" "$out"
  now=$(date -u +%FT%TZ)
  printf 'TICK-PASS %s relay=%s tick=%s code=%s behind=%s out=%s\n' "$now" "$rrc" "$trc" "$code" "$behind" "$out"
  [ -z "$sweep" ] || [ -n "$stale" ] || sweep_pass "$out"  # mut:sweep
  # The andon: one heartbeat push per pass, bounded, its failure printed and never fatal.
  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc code=$code behind=$behind"  # mut:heartbeat
  [ $? = 0 ] || echo "HEARTBEAT NOT PUSHED: heartbeat.sh did not finish cleanly"
}

tick_loop_self_test() (
  local t f=0 n=0 out
  t=$(mktemp -d) || { echo "tick_loop self-test: no temporary directory"; return 1; }
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  printf '#!/bin/bash\necho "relay $*" >> "%s/order"; exit "${RELAY_RC:-0}"\n' "$t" > "$t/relay.sh"
  printf '#!/bin/bash\necho "tick $*" >> "%s/order"; echo BOARD; exit "${TICK_RC:-0}"\n' "$t" > "$t/tick.sh"
  chmod +x "$t/tick.sh"
  printf '#!/bin/bash\necho "hb $*" >> "%s/hb"; exit "${HB_RC:-0}"\n' "$t" > "$t/hb.sh"
  export HPO_TICK_HEARTBEAT=$t/hb.sh
  # The rows before the freshness rows run from no checkout: never the real one, whose
  # fetch and checkout a restart would move.
  mkdir "$t/nogit"; export HPO_TICK_CODE_DIR=$t/nogit GIT_CEILING_DIRECTORIES=$t
  out=$(HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt" -- --only PRS)
  [ "$(cat "$t/order")" = "relay pass --confirm
tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
    && printf '%s\n' "$out" | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=ok tick=0 code=none behind=unknown out=' && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]
  ck "--once: one pass, cloud_relay.sh pass --confirm first, then the tick with its args; one banner" $?
  rm -f "$t/order"
  out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && printf '%s\n' "$out" | grep -q 'relay=absent tick=0'
  ck "null control: no cloud_relay.sh in the tree (before #2419) skips the relay and still ticks" $?
  rm -f "$t/order"
  out=$(RELAY_RC=3 TICK_RC=1 HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  grep -q '^tick' "$t/order" && printf '%s\n' "$out" | grep -q 'relay=rc=3 tick=1'
  ck "a failing relay pass is reported and the tick still runs; the tick's status is reported" $?
  # A relay slower than the interval (update_pr.sh's prepr, #2525) must not hold the board.
  printf '#!/bin/bash\necho start >> "%s/slow"; sleep "${RELAY_SLEEP:-0}"; echo done >> "%s/slow"; echo SLOW-LOG\n' "$t" "$t" > "$t/slow.sh"
  rm -f "$t/order" "$t/b.txt"; s0=$SECONDS
  out=$(RELAY_SLEEP=6 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval 3 --out "$t/b.txt")
  [ $((SECONDS - s0)) -lt 3 ] && [ "$(cat "$t/b.txt" 2>/dev/null)" = BOARD ] && printf '%s\n' "$out" | grep -q 'relay=running tick=0'
  ck "a relay slower than the interval does not delay the board; the banner says relay=running" $?
  out=$(RELAY_SLEEP=6 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(cat "$t/slow")" = start ] && printf '%s\n' "$out" | grep -q 'relay=running tick=0' && [ "$(grep -c '^tick' "$t/order")" = 2 ]
  ck "a pass that finds the relay in flight starts none (no overlap) and still ticks" $?
  k=0; while [ "$(tail -n 1 "$t/slow")" != done ] && [ $k -lt 150 ]; do sleep 0.1; k=$((k + 1)); done
  [ "$(cat "$t/slow")" = "start
done" ]
  ck "the in-flight relay was left to finish after its loop exited, never killed" $?
  k=0; while [ ! -f "$t/b.txt.relay.rc" ] && [ $k -lt 50 ]; do sleep 0.1; k=$((k + 1)); done
  out=$(HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  printf '%s\n' "$out" | grep -Eq '^TICK-RELAY [0-9T:-]+Z relay=ok started=[0-9T:-]+Z$' \
    && [ "$(printf '%s\n' "$out" | grep -c SLOW-LOG)" = 2 ] && printf '%s\n' "$out" | grep -q 'relay=ok tick=0' \
    && [ "$(grep -c start "$t/slow")" = 2 ] && [ ! -f "$t/b.txt.relay.rc" ]
  ck "null control: the late relay is reaped with its log next pass, and a fast relay reports ok" $?
  # Stubbed and --once, so a mutant that accepts the interval cannot loop on the real tick.
  HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval x --out "$t/b.txt" > "$t/e" 2>&1
  [ $? = 2 ] && grep -q 'interval' "$t/e"
  ck "a non-numeric --interval refuses" $?
  rm -f "$t/hb"
  out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(wc -l < "$t/hb" | tr -d ' ')" = 1 ] \
    && grep -Eq '^hb --once --message TICK-PASS [0-9T:-]+Z relay=absent tick=0 code=none behind=unknown$' "$t/hb"
  ck "each pass calls the heartbeat once, with the pass line (no --out path)" $?
  out=$(HB_RC=1 HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt"); rc=$?
  [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "a failing heartbeat is printed, never silent, and the loop still exits cleanly" $?
  # --sweep (R10-FLOW-AUTOTRAIN): one sweep per due pass, after the banner; never without the flag.
  printf '#!/bin/bash\necho sweep >> "%s/order"; echo "  ADDED #7"; echo "SWEEP ${SWEEP_WORD:-DONE}: x"; exit "${SWEEP_RC:-0}"\n' "$t" > "$t/sweep.sh"
  rm -f "$t/order"
  out=$(HPO_TICK_SWEEP_CMD="bash $t/sweep.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --sweep --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick 
sweep" ] && printf '%s\n' "$out" | sed -n 2p | grep -Eq '^TICK-SWEEP [0-9T:-]+Z rc=0 SWEEP DONE: x$' \
    && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 2 ] && grep -q 'ADDED #7' "$t/b.txt.sweep.log"
  ck "--sweep: one sweep after the tick, its last line after the banner, its whole output in <out>.sweep.log" $?
  rm -f "$t/order"
  out=$(HPO_TICK_SWEEP_CMD="bash $t/sweep.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --sweep --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && ! printf '%s\n' "$out" | grep -q TICK-SWEEP
  ck "--sweep: the next pass inside the interval sweeps nothing (the slow backstop)" $?
  rm -f "$t/order"
  out=$(HPO_TICK_SWEEP_EVERY=0 HPO_TICK_SWEEP_CMD="bash $t/sweep.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --sweep --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick 
sweep" ] && printf '%s\n' "$out" | grep -q '^TICK-SWEEP '
  ck "null control: a pass once the interval has passed sweeps again" $?
  rm -f "$t/order"
  out=$(HPO_TICK_SWEEP_CMD="bash $t/sweep.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && ! printf '%s\n' "$out" | grep -q TICK-SWEEP
  ck "null control: without --sweep no sweep runs (the default loop adds nothing and starts no train)" $?
  out=$(HPO_TICK_SWEEP_EVERY=0 SWEEP_WORD="REFUSED queue" SWEEP_RC=2 HPO_TICK_SWEEP_CMD="bash $t/sweep.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --sweep --out "$t/b.txt"); rc=$?
  [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^TICK-SWEEP .* rc=2 SWEEP REFUSED queue: x$' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "a refused sweep is reported with its rc and the pass still completes" $?
  # The real script against a bare remote: a pass moves the ref.
  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || return 1
  throwaway_git_init "$t/remote.git" -q --bare && throwaway_git_init "$t/w" -q -b main
  git -C "$t/w" remote add origin "$t/remote.git"; mkdir -p "$t/w/seat"
  cp "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/w/seat/"
  out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  git -C "$t/remote.git" log -1 --format=%s heartbeat/orchestrator | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=absent tick=0 code=none behind=unknown$' \
    && ! printf '%s\n' "$out" | grep -q 'NOT PUSHED'
  ck "a real pass moves heartbeat/orchestrator on the remote" $?
  git -C "$t/w" remote set-url origin "$t/nowhere.git"
  out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED: ' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "null control: a refused push is printed with its reason and the pass still completes" $?
  # The freshness check (P14): a clone of a scratch origin, detached, holding this script.
  unset HPO_TICK_HEARTBEAT; export HPO_TICK_HEARTBEAT=$t/hb.sh
  throwaway_git_init "$t/o.git" -q --bare -b main && throwaway_git_init "$t/s" -q -b main
  mkdir -p "$t/s/tools/audit/seat" "$t/s/tools/pr"
  cp "$0" "$t/s/tools/audit/seat/tick_loop.sh"; echo 1 > "$t/s/tools/pr/x"; echo r > "$t/s/README"
  git -C "$t/s" add -A && git -C "$t/s" commit -qm base && git -C "$t/s" push -q "$t/o.git" main
  git -C "$t" clone -q "$t/o.git" c && git -C "$t/c" checkout -q --detach
  land() { # <path> <content>: one commit on the scratch origin's main
    printf '%s\n' "$2" > "$t/s/$1"; git -C "$t/s" commit -qam "$1" && git -C "$t/s" push -q "$t/o.git" main; }
  fr() { rm -f "$t/order"; HPO_TICK_CODE_DIR=$t/c HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" \
    bash "$0" --once --out "$t/f.txt" "$@" 2>&1; }
  at0=$(git -C "$t/c" rev-parse --short=7 HEAD)
  out=$(fr); rm -f "$t/hb"
  printf '%s\n' "$out" | grep -q "relay=ok tick=0 code=$at0 behind=0 out=" && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ] \
    && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
  ck "freshness null control: behind 0 is silent (code=<sha7> behind=0 on the banner) and does not exec" $?
  land README r2; out=$(fr)
  printf '%s\n' "$out" | grep -q "code=$at0 behind=0 " && ! printf '%s\n' "$out" | grep -q 'TICK-STALE\|TICK-RESTART'
  ck "freshness: a commit outside the loop's code paths is not counted (the path filter)" $?
  land tools/pr/x 2; out=$(fr); fr >/dev/null; cat "$t/hb" > "$t/hb1" 2>/dev/null
  printf '%s\n' "$out" | grep -q "relay=ok tick=0 code=$at0 behind=1 " && ! printf '%s\n' "$out" | grep -q 'TICK-RESTART\|TICK-STALE' \
    && grep -q "^relay pass --confirm" "$t/order" && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ] \
    && grep -q "code=$at0 behind=1$" "$t/hb1"
  ck "freshness: behind within the bound and no change to the loop's own files relays, restarts nothing; the heartbeat says behind=1" $?
  printf '#!/bin/bash\necho "NEW-LOOP $*"\n' > "$t/new.sh"
  land tools/audit/seat/tick_loop.sh "$(cat "$t/new.sh")"
  python3 -I -c 'import fcntl, sys, time
f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".up", "w").close(); time.sleep(30)' "$t/f.txt.relay.lock" & lp=$!
  k=0; while [ ! -f "$t/f.txt.relay.lock.up" ] && [ $k -lt 100 ]; do sleep 0.1; k=$((k + 1)); done
  out=$(fr)
  kill "$lp" 2>/dev/null; wait "$lp" 2>/dev/null
  printf '%s\n' "$out" | grep -q '^TICK-STALE .* behind=2: a relay is in flight' && printf '%s\n' "$out" | grep -q 'relay=stale tick=0' \
    && [ "$(cat "$t/order")" = "tick " ] && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ] && [ "$(cat "$t/f.txt")" = BOARD ]
  ck "freshness: a held relay lock does not restart, skips the relay and still writes the board under TICK-STALE" $?
  echo dirty >> "$t/c/tools/pr/x"; out=$(fr); git -C "$t/c" checkout -q -- tools/pr/x
  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: the tree is dirty' && printf '%s\n' "$out" | grep -q 'relay=stale' \
    && [ "$(cat "$t/order")" = "tick " ] && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
  ck "freshness: a dirty tree prints the banner, skips the relay and is never moved" $?
  git -C "$t/c" checkout -q -b local; out=$(fr); git -C "$t/c" checkout -q --detach; git -C "$t/c" branch -qD local
  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: a branch is checked out' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
  ck "freshness: a checked-out branch is never moved (restart needs a detached head)" $?
  out=$(HPO_TICK_RESTARTED=1 fr)
  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: restarted once this pass' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
  ck "freshness: a pass already restarted does not exec again (at most once per pass)" $?
  land tools/audit/seat/tick_loop.sh 'if then ('; out=$(fr)
  printf '%s\n' "$out" | grep -q "^TICK-STALE .*: bash -n refuses" && printf '%s\n' "$out" | grep -q 'relay=stale tick=0' \
    && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
  ck "freshness: origin/main's tick_loop.sh failing bash -n is never checked out or exec'd" $?
  land tools/audit/seat/tick_loop.sh "$(cat "$t/new.sh")"; out=$(fr --sweep)
  printf '%s\n' "$out" | grep -q "^TICK-RESTART .* code=$at0 behind=4 -> " \
    && printf '%s\n' "$out" | grep -qx "NEW-LOOP --once --out $t/f.txt --sweep" \
    && [ "$(git -C "$t/c" rev-parse HEAD)" = "$(git -C "$t/c" rev-parse origin/main)" ] && [ ! -f "$t/order" ]
  ck "freshness: a loop-file change with a free lock and a clean detached tree checks out origin/main and execs it with the same args" $?
  rm -rf "$t"
  echo "tick_loop self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

ARGV=("$@")  # a restart execs the new loop with these
once=; sweep=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
while [ $# -gt 0 ]; do
  case $1 in
    --self-test) tick_loop_self_test; exit ;;
    --once) once=1; shift ;;
    --sweep) sweep=1; shift ;;
    --interval) every=${2:-}; shift 2 || shift ;;
    --out) out=${2:-}; shift 2 || shift ;;
    --) shift; break ;;
    *) echo "tick_loop: unknown option '$1'" >&2; sed -n '2,3p' "$0" >&2; exit 2 ;;
  esac
done
case $every in ''|*[!0-9]*) echo "tick_loop: --interval needs whole seconds, got '$every'" >&2; exit 2 ;; esac
[ -n "$out" ] || { echo "tick_loop: --out needs a file" >&2; exit 2; }
while :; do
  tick_pass "$out" "$@"
  unset HPO_TICK_RESTARTED  # once per pass: the next pass may restart again
  [ -n "$once" ] && exit 0
  sleep "$every"
done
