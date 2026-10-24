#!/bin/bash
# tick_loop.sh [--once] [--interval SECONDS] [--out FILE] [--pitch] [-- <orchestrator_tick.py args>]
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
# One banner line per pass on stdout:
#   TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc> out=<file>
# The relay's output is printed when it is reaped; one that finished after its
# pass's wait is reaped by the next pass, with its own line before that banner:
#   TICK-RELAY <utc> relay=<ok|rc=N> started=<utc>
# A failing relay pass is reported and the tick still runs; a failing tick is
# reported and the loop goes on. The loop drives; the tick itself stays read-only.
#   3. --pitch only (R10-FLOW-AUTOTRAIN; off by default, and the first live pitch runs
#      with the orchestrator watching), on the hourly pitch: the first pass, then the
#      first pass HPO_TICK_PITCH_EVERY seconds (default 3600) after the last pitch,
#      stamped in <out>.pitch.at. `merge_train.py pitch --once` holds while a train's
#      pidfile is live or the ledger holds an open train-stop, else writes the queue
#      from the verdict bus, runs
#      queue_pre_flight.py on it and starts one detached train.sh --bot-prs
#      --approval-carry --pre-flight (merge_train.py's PITCH block says why each). Its
#      output goes to <out>.pitch.log and one line follows the banner:
#        TICK-PITCH <utc> rc=<rc> <the pitch's last line: PITCH HELD|EMPTY|STARTED|REFUSED ...>
#      HPO_PITCH_MANDATE, when set, is passed as the train's --mandate; HPO_TICK_PITCH_CMD
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

pitch_pass() { # <out>: one merge pitch when one is due; prints its TICK-PITCH line
  local log=$1.pitch.log at=$1.pitch.at prc last every=${HPO_TICK_PITCH_EVERY:-3600}
  case $every in ''|*[!0-9]*) every=3600 ;; esac
  last=$(cat "$at" 2>/dev/null); case $last in ''|*[!0-9]*) last=0 ;; esac
  [ $(( $(date +%s) - last )) -ge "$every" ] || return 0  # mut:due
  date +%s > "$at"
  if [ -n "${HPO_TICK_PITCH_CMD:-}" ]; then $HPO_TICK_PITCH_CMD > "$log" 2>&1; prc=$?
  else python3 "$HERE/merge_train.py" pitch --once ${HPO_PITCH_MANDATE:+--mandate "$HPO_PITCH_MANDATE"} > "$log" 2>&1; prc=$?; fi
  printf 'TICK-PITCH %s rc=%s %s\n' "$(date -u +%FT%TZ)" "$prc" "$(tail -n 1 "$log")"
}

tick_pass() { # <out> [tick args...]: one pass; prints the banner
  local out=$1 relay rrc trc tmp now; shift
  relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
  mkdir -p "$(dirname -- "$out")"
  if [ -f "$relay" ]; then
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
  printf 'TICK-PASS %s relay=%s tick=%s out=%s\n' "$now" "$rrc" "$trc" "$out"
  [ -z "$pitch" ] || pitch_pass "$out"  # mut:pitch
  # The andon: one heartbeat push per pass, bounded, its failure printed and never fatal.
  timeout 60 bash "${HPO_TICK_HEARTBEAT:-$HERE/heartbeat.sh}" --once --message "TICK-PASS $now relay=$rrc tick=$trc"  # mut:heartbeat
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
  out=$(HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt" -- --only PRS)
  [ "$(cat "$t/order")" = "relay pass --confirm
tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
    && printf '%s\n' "$out" | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=ok tick=0 out=' && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]
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
    && grep -Eq '^hb --once --message TICK-PASS [0-9T:-]+Z relay=absent tick=0$' "$t/hb"
  ck "each pass calls the heartbeat once, with the pass line (no --out path)" $?
  out=$(HB_RC=1 HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt"); rc=$?
  [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "a failing heartbeat is printed, never silent, and the loop still exits cleanly" $?
  # --pitch (R10-FLOW-AUTOTRAIN): one pitch per pass, after the banner; never without the flag.
  printf '#!/bin/bash\necho pitch >> "%s/order"; echo "  #7 PASS"; echo "PITCH ${PITCH_WORD:-STARTED}: x"; exit "${PITCH_RC:-0}"\n' "$t" > "$t/pitch.sh"
  rm -f "$t/order"
  out=$(HPO_TICK_PITCH_CMD="bash $t/pitch.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --pitch --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick 
pitch" ] && printf '%s\n' "$out" | sed -n 2p | grep -Eq '^TICK-PITCH [0-9T:-]+Z rc=0 PITCH STARTED: x$' \
    && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 2 ] && grep -q '#7 PASS' "$t/b.txt.pitch.log"
  ck "--pitch: one pitch after the tick, its last line after the banner, its whole output in <out>.pitch.log" $?
  rm -f "$t/order"
  out=$(HPO_TICK_PITCH_CMD="bash $t/pitch.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --pitch --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && ! printf '%s\n' "$out" | grep -q TICK-PITCH
  ck "--pitch: the next pass inside the hour pitches nothing (the hourly pitch)" $?
  rm -f "$t/order"
  out=$(HPO_TICK_PITCH_EVERY=0 HPO_TICK_PITCH_CMD="bash $t/pitch.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --pitch --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick 
pitch" ] && printf '%s\n' "$out" | grep -q '^TICK-PITCH '
  ck "null control: a pass once the interval has passed pitches again" $?
  rm -f "$t/order"
  out=$(HPO_TICK_PITCH_CMD="bash $t/pitch.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && ! printf '%s\n' "$out" | grep -q TICK-PITCH
  ck "null control: without --pitch no pitch runs (the default loop starts no train)" $?
  out=$(HPO_TICK_PITCH_EVERY=0 PITCH_WORD="REFUSED queue" PITCH_RC=2 HPO_TICK_PITCH_CMD="bash $t/pitch.sh" HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --pitch --out "$t/b.txt"); rc=$?
  [ $rc = 0 ] && printf '%s\n' "$out" | grep -q '^TICK-PITCH .* rc=2 PITCH REFUSED queue: x$' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "a refused pitch is reported with its rc and the pass still completes" $?
  # The real script against a bare remote: a pass moves the ref.
  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || return 1
  throwaway_git_init "$t/remote.git" -q --bare && throwaway_git_init "$t/w" -q -b main
  git -C "$t/w" remote add origin "$t/remote.git"; mkdir -p "$t/w/seat"
  cp "$HERE/heartbeat.sh" "$HERE/ref_privacy.py" "$t/w/seat/"
  out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  git -C "$t/remote.git" log -1 --format=%s heartbeat/orchestrator | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=absent tick=0$' \
    && ! printf '%s\n' "$out" | grep -q 'NOT PUSHED'
  ck "a real pass moves heartbeat/orchestrator on the remote" $?
  git -C "$t/w" remote set-url origin "$t/nowhere.git"
  out=$(HPO_TICK_HEARTBEAT=$t/w/seat/heartbeat.sh HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  printf '%s\n' "$out" | grep -q '^HEARTBEAT NOT PUSHED: ' && printf '%s\n' "$out" | grep -q 'tick=0'
  ck "null control: a refused push is printed with its reason and the pass still completes" $?
  rm -rf "$t"
  echo "tick_loop self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

once=; pitch=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
while [ $# -gt 0 ]; do
  case $1 in
    --self-test) tick_loop_self_test; exit ;;
    --once) once=1; shift ;;
    --pitch) pitch=1; shift ;;
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
  [ -n "$once" ] && exit 0
  sleep "$every"
done
