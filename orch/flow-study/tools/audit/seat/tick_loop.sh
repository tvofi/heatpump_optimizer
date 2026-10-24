#!/bin/bash
# tick_loop.sh [--once] [--interval SECONDS] [--out FILE] [-- <orchestrator_tick.py args>]
# tick_loop.sh --self-test
#
# The tick's driver loop (the round-10 orchestrator, tvofi approved,
# 2026-10-18). Each pass, in order:
#   1. `cloud_relay.sh pass`, when the tree carries cloud_relay.sh (#2419). Before
#      that lands the step is skipped and the banner says so, so the tick still runs.
#   2. orchestrator_tick.py with the given args. The board goes to --out (default
#      $HPO_STATE_DIR/tick.txt, written whole then renamed, so a reader never sees
#      half a board).
# One banner line per pass on stdout:
#   TICK-PASS <utc> relay=<ok|rc=N|absent> tick=<rc> out=<file>
# A failing relay pass is reported and the tick still runs; a failing tick is
# reported and the loop goes on. The loop drives; the tick itself stays read-only.
# --interval defaults to 300 (the five-minute GitHub poll). Run it detached
# (daemonize.py): a background task dies at two hours. HPO_TICK_RELAY and
# HPO_TICK_CMD replace the relay script and the tick command (the self-test's stubs).
set -uo pipefail
HERE=$(cd "$(dirname -- "$0")" && pwd)

tick_pass() { # <out> [tick args...]: one pass; prints the banner
  local out=$1 relay rrc trc tmp; shift
  relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
  if [ -f "$relay" ]; then
    bash "$relay" pass; rrc=$?
    [ "$rrc" = 0 ] && rrc=ok || rrc="rc=$rrc"
  else
    rrc=absent
  fi
  mkdir -p "$(dirname -- "$out")"; tmp="$out.part.$$"
  if [ -n "${HPO_TICK_CMD:-}" ]; then $HPO_TICK_CMD "$@" > "$tmp" 2>&1; trc=$?
  else python3 "$HERE/orchestrator_tick.py" "$@" > "$tmp" 2>&1; trc=$?; fi
  mv -f "$tmp" "$out"
  printf 'TICK-PASS %s relay=%s tick=%s out=%s\n' "$(date -u +%FT%TZ)" "$rrc" "$trc" "$out"
}

tick_loop_self_test() (
  local t f=0 n=0 out
  t=$(mktemp -d) || { echo "tick_loop self-test: no temporary directory"; return 1; }
  ck() { n=$((n + 1)); if [ "$2" = 0 ]; then echo "  ok   $1"; else f=$((f + 1)); echo "  FAIL $1"; fi; }
  printf '#!/bin/bash\necho "relay $*" >> "%s/order"; exit "${RELAY_RC:-0}"\n' "$t" > "$t/relay.sh"
  printf '#!/bin/bash\necho "tick $*" >> "%s/order"; echo BOARD; exit "${TICK_RC:-0}"\n' "$t" > "$t/tick.sh"
  chmod +x "$t/tick.sh"
  out=$(HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt" -- --only PRS)
  [ "$(cat "$t/order")" = "relay pass
tick --only PRS" ] && [ "$(cat "$t/b.txt")" = BOARD ] \
    && printf '%s\n' "$out" | grep -Eq '^TICK-PASS [0-9T:-]+Z relay=ok tick=0 out=' && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]
  ck "--once: one pass, cloud_relay.sh pass first, then the tick with its args; one banner" $?
  rm -f "$t/order"
  out=$(HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  [ "$(cat "$t/order")" = "tick " ] && printf '%s\n' "$out" | grep -q 'relay=absent tick=0'
  ck "null control: no cloud_relay.sh in the tree (before #2419) skips the relay and still ticks" $?
  rm -f "$t/order"
  out=$(RELAY_RC=3 TICK_RC=1 HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/b.txt")
  grep -q '^tick' "$t/order" && printf '%s\n' "$out" | grep -q 'relay=rc=3 tick=1'
  ck "a failing relay pass is reported and the tick still runs; the tick's status is reported" $?
  # Stubbed and --once, so a mutant that accepts the interval cannot loop on the real tick.
  HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval x --out "$t/b.txt" > "$t/e" 2>&1
  [ $? = 2 ] && grep -q 'interval' "$t/e"
  ck "a non-numeric --interval refuses" $?
  rm -rf "$t"
  echo "tick_loop self-test: $n checks, $f failed"
  [ "$f" = 0 ]
)

once=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
while [ $# -gt 0 ]; do
  case $1 in
    --self-test) tick_loop_self_test; exit ;;
    --once) once=1; shift ;;
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
