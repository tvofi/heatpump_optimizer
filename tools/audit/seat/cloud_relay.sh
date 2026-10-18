#!/bin/bash
# cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>    relay one cloud reviewer's verdict
# cloud_relay.sh --watch [--interval N] [--once] [--confirm] [--log FILE]
# cloud_relay.sh --self-test
#
# WHY. A cloud reviewer cannot run `bus.sh push-verdict`: the dispatch record
# `push-verdict` checks lives on the orchestrator's machine, so it refuses
# "unknown nonce" there. The cloud reviewer instead commits verdict.md (first
# line in fix-review.md's grammar, then a blank line and `bus-nonce: <nonce>`)
# plus ev/ to a fresh repository and pushes it to
# refs/heads/probe/rev-<pr>-<nonce first 8>; this script, run by the
# orchestrator where the record is, fetches that ref, grades it, and runs
# `bus.sh push-verdict` locally. `bus.sh confirm` follows, as for any verdict.
#
# REFUSES (exit 2, push-verdict not run):
#   * a head that is not 40 lowercase hex, or a nonce that is not 32 hex;
#   * no probe ref for <pr> and <nonce>;
#   * a verdict whose `bus-nonce:` line is not exactly <nonce>;
#   * a verdict whose first line names a head other than <head40>;
#   * a ref whose commit subject (`verdict <pr> <head>`) names another PR or
#     head than the arguments (a verdict relayed onto the wrong PR);
#   * a ref already relayed: the ledger keys on `<ref> <sha>`, so a second
#     relay of the same push is refused and a re-pushed ref relays again.
# NORMALISES one thing, and says so. A reviewer that read the old brief wraps a
# blocked verdict's tail in brackets: `Fix review: blocked <head> [class: reason]`.
# bus.sh's grammar is `blocked <head> <class>: <reason>` (class `[a-z-]+`), and
# dropping exactly the one outer bracket pair loses nothing, so the relay rewrites
# the first line in its temp copy and prints `normalised first line: A -> B`.
# Anything else (a bracketed merge suffix, unbalanced brackets, a bracketed
# tail whose class is not `[a-z-]+: <reason>`) is refused unchanged: dropping a
# suffix from a merge would be lossy, and push-verdict's own refusal names the rest.
#
# --watch is the orchestrator's poll loop: every N seconds (default 120) it runs
# `git ls-remote origin 'refs/heads/probe/rev-*'` and relays each ref+sha once.
# The dispatch record ($HPO_BUS_STATE or ~/.zcode/bus, field order `pr head
# thread nonce`) supplies the head and full nonce for a ref's pr and nonce8; a ref
# with no record is logged and left for a later pass. A refused ref+sha is noted
# in `<ledger>.refused` and not retried, so a loop does not repeat one refusal
# every interval; a re-pushed ref has a new sha and is tried again. --once makes
# one pass (the self-test's and cron's shape). Run it detached via daemonize.py.
#
# --confirm does not stop at push-verdict (two verdicts once sat relayed and
# unposted for 20 minutes): after a push-verdict that PASSED it runs
# `bus.sh confirm <pr> <review-sha>`, the sha being the one push-verdict printed
# (`review/<pr> <sha>`), and appends one line to the log (--log FILE, default
# <state>/cloud-relay.log, which the orchestrator reads):
#   POSTED <utc> <pr> <review-sha>          confirm succeeded
#   OWED   <utc> <pr> <review-sha|-> <why>  push-verdict passed, the verdict is not posted
# confirm never runs after a refused relay or a failed push-verdict, and writes
# nothing for them (a refusal prints its reason, and --watch's .refused file
# holds it). HPO_RELAY_CONFIRM replaces the confirm command (the self-test's stub).
#
# The ledger is ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed and is
# written only after push-verdict succeeded. HPO_RELAY_PUSH replaces the
# push-verdict command (the self-test's stub; it takes <pr> <verdict> <ev>).
set -uo pipefail
HERE=$(cd "$(dirname -- "$0")" && pwd)

die() { echo "cloud_relay: refused: $*" >&2; return 2; }

logline() { mkdir -p "$(dirname -- "${LOG:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relay.log}")" && printf '%s %s\n' "$1" "$(date -u +%FT%TZ) $2" >> "${LOG:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relay.log}"; }
posted() { logline POSTED "$1 $2"; echo "cloud_relay: POSTED #$1 $2"; }
owed() { logline OWED "$1 $2 $3"; echo "cloud_relay: OWED #$1: $3" >&2; }

relay() {
  local pr=$1 nonce=$2 head=$3 ref sha d subj first state led
  case $pr in ''|*[!0-9]*) die "pr '$pr' is not a number"; return;; esac
  printf '%s' "$head" | grep -Eq '^[0-9a-f]{40}$' || { die "head must be 40 lowercase hex"; return; }
  printf '%s' "$nonce" | grep -Eq '^[0-9a-f]{32}$' || { die "nonce must be 32 hex"; return; }
  ref=refs/heads/probe/rev-$pr-$(printf '%s' "$nonce" | cut -c1-8)
  sha=$(git ls-remote origin "$ref" | awk 'NF { print $1; exit }')
  [ -n "$sha" ] || { die "no $ref on origin"; return; }
  state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}; led=$state/cloud-relayed
  if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then die "$ref at $sha was already relayed"; return; fi
  git fetch -q origin "$ref" || { die "could not fetch $ref"; return; }
  d=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay.XXXXXX") || return 1
  git archive "$sha" | tar -x -C "$d" || { die "could not read $sha"; return; }
  subj=$(git log -1 --format=%s "$sha")
  [ "$subj" = "verdict $pr $head" ] || { die "the ref's commit says '$subj', not 'verdict $pr $head': another PR or head"; return; }
  [ -f "$d/verdict.md" ] || { die "no verdict.md in the ref"; return; }
  first=$(head -n 1 "$d/verdict.md")
  if [[ $first =~ ^(Fix\ review:\ blocked\ [0-9a-f]{40})\ \[([a-z-]+:\ [^][]+)\]$ ]]; then
    local fixed="${BASH_REMATCH[1]} ${BASH_REMATCH[2]}"
    { printf '%s\n' "$fixed"; tail -n +2 "$d/verdict.md"; } > "$d/verdict.new" && mv "$d/verdict.new" "$d/verdict.md"
    echo "cloud_relay: normalised first line: $first -> $fixed"
    first=$fixed
  fi
  # bus.sh's grammar (verdict_sha): merge has no tail; blocked has `<class>: <reason>`.
  if [ "$first" = "Fix review: merge $head" ]; then :
  elif [[ $first == "Fix review: blocked $head "* ]] && [[ ${first#"Fix review: blocked $head "} =~ ^[a-z-]+:\ .+$ ]]; then :
  else die "the first line is not 'Fix review: merge $head' or 'Fix review: blocked $head <class>: <reason>': '$first'"; return; fi
  grep -qx "bus-nonce: $nonce" "$d/verdict.md" || { die "nonce mismatch: no 'bus-nonce: $nonce' line"; return; }
  [ -d "$d/ev" ] || { die "no ev/ directory in the ref"; return; }
  local out sha2
  if [ -n "${HPO_RELAY_PUSH:-}" ]; then out=$("$HPO_RELAY_PUSH" "$pr" "$d/verdict.md" "$d/ev") || { printf '%s\n' "$out"; return 1; }
  else out=$(bash "$HERE/bus.sh" push-verdict "$pr" "$d/verdict.md" "$d/ev") || { printf '%s\n' "$out"; return 1; }; fi
  printf '%s\n' "$out"
  mkdir -p "$state" && echo "$ref $sha" >> "$led"
  if [ -n "${CONFIRM:-}" ]; then
    sha2=$(printf '%s\n' "$out" | tail -n 1 | awk '{ print $NF }')
    if ! printf '%s' "$sha2" | grep -Eq '^[0-9a-f]{40}$'; then owed "$pr" - "push-verdict printed no 40-hex review commit"
    elif [ -n "${HPO_RELAY_CONFIRM:-}" ]; then
      "$HPO_RELAY_CONFIRM" "$pr" "$sha2" >/dev/null 2>&1 && posted "$pr" "$sha2" || owed "$pr" "$sha2" "confirm failed"
    else bash "$HERE/bus.sh" confirm "$pr" "$sha2" >/dev/null 2>&1 && posted "$pr" "$sha2" || owed "$pr" "$sha2" "bus.sh confirm failed; run it by hand"; fi
  fi
  echo "cloud_relay: relayed $ref $sha; next: bus.sh confirm $pr <review commit>"
}

watch_once() { # one pass over probe/rev-*; relays each unseen ref+sha
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref k pr n8 rec nonce head rc
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  git ls-remote origin 'refs/heads/probe/rev-*' > "${TMPDIR:-/tmp}/cloud_relay_ls.$$" || { echo "cloud_relay: ls-remote failed; will retry" >&2; rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"; return 0; }
  while read -r sha ref; do
    [ -n "$ref" ] || continue
    if { [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; } || { [ -f "$led.refused" ] && grep -qxF "$ref $sha" "$led.refused"; }; then continue; fi
    k=${ref#refs/heads/probe/rev-}; pr=${k%%-*}; n8=${k#*-}
    rec=$(awk -v p="$pr" -v n="$n8" '$1 == p && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
    if [ -z "$rec" ]; then echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no dispatch record in $bus; leaving it" >&2; continue; fi
    head=${rec%% *}; nonce=${rec#* }
    echo "$(date -u +%FT%TZ) cloud_relay: relaying $ref $sha"
    relay "$pr" "$nonce" "$head"; rc=$?
    if [ $rc -ne 0 ]; then mkdir -p "$state" && echo "$ref $sha" >> "$led.refused"; fi
  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
}

watch() { # [--interval N] [--once]
  local every=120 once=""
  while [ $# -gt 0 ]; do case $1 in
    --interval) every=${2:-}; shift 2;; --once) once=1; shift;; --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) echo "cloud_relay: unknown watch option '$1'" >&2; return 2;; esac; done
  case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
  while :; do watch_once; [ -n "$once" ] && return 0; sleep "$every"; done
}

self_test() {
  local t ok=0 bad=0 c=0 h n stub
  t=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay_st.XXXXXX") || exit 1
  # Every scratch repository comes from the shared helper (tests/throwaway_git.sh, #2051).
  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || exit 1
  throwaway_git_init "$t/o.git" -q --bare; throwaway_git_init "$t/w" -q; cd "$t/w" || exit 1
  git remote add origin "$t/o.git"
  h=0123456789abcdef0123456789abcdef01234567; n=0123456789abcdef0123456789abcdef
  export HPO_STATE_DIR=$t/state
  stub=$t/stub.sh; printf '#!/bin/sh\necho "$1" >> "%s/pushed"\necho "review/$1 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n' "$t" > "$stub"; chmod +x "$stub"; export HPO_RELAY_PUSH=$stub
  mk() { # mk <pr> <subject-head> <verdict-head> <nonce-in-verdict> : push a probe ref for nonce n
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1))" > "$t/pr/ev/e"
    printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$3" "$4" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict $1 $2"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-$1-${n:0:8}"; }
  chk() { # chk <name> <want-rc> <cmd...>
    local name=$1 want=$2; shift 2; "$@" >/dev/null 2>&1; local rc=$?
    if [ "$rc" = "$want" ]; then ok=$((ok+1)); echo "  ok   $name"; else bad=$((bad+1)); echo "  FAIL $name (rc=$rc, want $want)"; fi; }
  chk "no ref is refused" 2 relay 7 $n $h
  mk 7 $h $h $n;           chk "a clean ref relays (null control)" 0 relay 7 $n $h
  chk "the stub saw the push" 0 test "$(cat "$t/pushed")" = 7
  chk "the same push relayed twice is refused" 2 relay 7 $n $h
  mk 7 $h $h $n;           chk "a re-pushed ref relays again" 0 relay 7 $n $h
  mk 7 $h $h ffffffffffffffffffffffffffffffff; chk "a nonce mismatch is refused" 2 relay 7 $n $h
  mk 7 $h ${h%?}0 $n;     chk "a verdict naming another head is refused" 2 relay 7 $n $h
  mk 8 $h $h $n;           chk "a ref pushed for PR 8 leaves PR 7 with no ref" 2 relay 7 $n $h
  git -C "$t/o.git" update-ref refs/heads/probe/rev-7-${n:0:8} "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-8-${n:0:8})"
  chk "a commit subject naming PR 8 under PR 7's ref is refused" 2 relay 7 $n $h
  chk "a short head is refused" 2 relay 7 $n ${h%?}
  chk "a short nonce is refused" 2 relay 7 abc $h
  chk "a non-numeric PR is refused" 2 relay x $n $h
  # normalisation of a bracketed blocked tail
  bl() { # bl <first line>: push a probe ref for PR 9 with that first line
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1))" > "$t/pr/ev/e"
    printf '%s\n\nbus-nonce: %s\n' "$1" "$n" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict 9 $h"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-9-${n:0:8}"; }
  : > "$t/seen"; vstub=$t/vstub.sh
  printf '#!/bin/sh\nhead -n 1 "$2" > "%s/seen"\n' "$t" > "$vstub"; chmod +x "$vstub"; HPO_RELAY_PUSH=$vstub
  bl "Fix review: blocked $h [mutation: a fix line deleted]"
  chk "a bracketed blocked tail relays" 0 relay 9 $n $h
  chk "it was rewritten losslessly" 0 test "$(cat "$t/seen")" = "Fix review: blocked $h mutation: a fix line deleted"
  bl "Fix review: blocked $h [mutation: a fix line deleted]"
  out=$(relay 9 $n $h 2>&1); chk "the log line names the rewrite" 0 test "${out#*normalised first line}" != "$out"
  bl "Fix review: blocked $h mutation: a fix line deleted"
  chk "an unbracketed blocked line relays unchanged (null control)" 0 relay 9 $n $h
  chk "and is seen unchanged" 0 test "$(cat "$t/seen")" = "Fix review: blocked $h mutation: a fix line deleted"
  bl "Fix review: merge $h [class: none]"
  chk "a bracketed merge suffix is refused, not stripped" 2 relay 9 $n $h
  bl "Fix review: blocked $h [mutation: [nested] reason]"
  chk "a nested bracket is refused" 2 relay 9 $n $h
  bl "Fix review: blocked $h [Mutation: x]"
  chk "a bracketed class outside [a-z-]+ is refused" 2 relay 9 $n $h
  # --confirm: confirm runs only after a passed push-verdict, and logs POSTED or OWED
  cstub=$t/cstub.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/confirmed"\n' "$t" > "$cstub"; chmod +x "$cstub"
  fstub=$t/fstub.sh; printf '#!/bin/sh\nexit 1\n' > "$fstub"; chmod +x "$fstub"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$cstub; LOG=$t/relay.log; rm -f "$t/confirmed" "$LOG"
  mk 7 $h $h $n; CONFIRM=1
  chk "relay --confirm succeeds" 0 relay 7 $n $h
  chk "confirm ran with the review sha push-verdict printed" 0 test "$(cat "$t/confirmed")" = "7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  chk "the log has a POSTED line" 0 grep -q "^POSTED .* 7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa$" "$LOG"
  mk 7 $h $h ffffffffffffffffffffffffffffffff; rm -f "$t/confirmed"
  chk "a refused relay does not confirm" 2 relay 7 $n $h
  chk "and logs nothing new" 0 test "$(wc -l < "$LOG" | tr -d ' ')" = 1
  failpush=$t/failpush.sh; printf '#!/bin/sh\necho nope >&2\nexit 1\n' > "$failpush"; chmod +x "$failpush"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$failpush
  chk "a failed push-verdict does not confirm" 1 relay 7 $n $h
  chk "confirm did not run after it" 0 test ! -f "$t/confirmed"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$fstub
  chk "a failing confirm leaves the relay itself passed" 0 relay 7 $n $h
  chk "and logs OWED with the review sha" 0 grep -q "^OWED .* 7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa confirm failed$" "$LOG"
  nosha=$t/nosha.sh; printf '#!/bin/sh\necho done\n' > "$nosha"; chmod +x "$nosha"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$nosha; HPO_RELAY_CONFIRM=$cstub
  chk "a push-verdict that printed no review sha logs OWED" 0 relay 7 $n $h
  chk "and the OWED line carries a dash" 0 grep -q "^OWED .* 7 - " "$LOG"
  CONFIRM=; HPO_RELAY_PUSH=$stub; unset HPO_RELAY_CONFIRM; : > "$LOG"; rm -f "$t/confirmed"
  mk 7 $h $h $n
  chk "without --confirm, relay logs nothing" 0 relay 7 $n $h
  chk "and the log stayed empty" 0 test ! -s "$LOG"
  # the watch pass
  HPO_RELAY_PUSH=$stub; rm -f "$t/pushed" "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused"
  export HPO_BUS_STATE=$t/bus; mkdir -p "$t/bus"
  git -C "$t/o.git" for-each-ref --format='%(refname)' 'refs/heads/probe/' | while read -r r; do git -C "$t/o.git" update-ref -d "$r"; done
  mk 5 $h $h $n; mk 6 $h $h $n; git -C "$t/o.git" update-ref -d refs/heads/probe/rev-6-${n:0:8}
  watch_once >/dev/null 2>&1
  chk "a ref with no dispatch record is left alone" 0 test ! -s "$t/pushed"
  printf '5 %s thread %s\n' "$h" "$n" > "$t/bus/dispatched"
  watch_once >/dev/null 2>&1
  chk "a watch pass relays a dispatched ref once" 0 test "$(cat "$t/pushed")" = 5
  watch_once >/dev/null 2>&1
  chk "a second pass relays nothing" 0 test "$(wc -l < "$t/pushed" | tr -d ' ')" = 1
  mk 5 $h $h ffffffffffffffffffffffffffffffff
  watch_once >/dev/null 2>&1; watch_once >/dev/null 2>&1
  chk "a refused ref is noted once and not retried" 0 test "$(wc -l < "$t/state/cloud-relayed.refused" | tr -d ' ')" = 1
  chk "--interval 0 is refused" 2 watch --interval 0
  chk "--once makes one pass and returns" 0 watch --once
  mk 5 $h $h $n; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused"; : > "$LOG"; CONFIRM=1; HPO_RELAY_CONFIRM=$cstub
  watch_once >/dev/null 2>&1
  chk "a watch pass with --confirm confirms and logs POSTED" 0 grep -q "^POSTED .* 5 " "$LOG"
  CONFIRM=
  rm -rf "$t"
  echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
}

case ${1:-} in
  --self-test) self_test; exit $?;;
  --watch) shift; watch "$@"; exit $?;;
  --confirm|--log) while [ $# -gt 0 ]; do case $1 in --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) break;; esac; done
    [ $# = 3 ] || { echo "usage: cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
  ''|-*) echo "usage: cloud_relay.sh <pr> <nonce> <head40> | --watch [--interval N] [--once] [--confirm] [--log FILE] | --self-test" >&2; exit 2;;
  *) [ $# = 3 ] || { echo "usage: cloud_relay.sh <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
esac
