#!/usr/bin/env bash
# PROTOTYPE (out of tree; proposal P-R11-36): the two-way channel between ANY cloud seat and the
# orchestrator, generalised from box_comms.sh (CAP2, passed 2026-11-16). Owner ruling 2026-11-16:
# the protocol is standard for every cloud seat.
#
# Seat side (env ROUND, default 11; run from the seat's checkout or set COMMS_REPO):
#   seat_comms.sh init <topic>        once at start; restores ACK/PROGRESS from the comms ref if a
#                                     previous fire left one (prints `resumed <sha12>` and, when it
#                                     holds a work snapshot, `snapshot <sha>`)
#   seat_comms.sh hb [text]           one heartbeat line, pushed
#   seat_comms.sh ckpt <msg>          heartbeat + a snapshot of the working tree (tracked and
#                                     untracked, .gitignore honoured) as the comms commit's 2nd parent
#   seat_comms.sh inbox               print `CMD <n> <command>` per new orchestrator command and ack it
#   seat_comms.sh loop [secs=600]     hb + inbox every <secs> until done (run under Monitor: each
#                                     CMD line is an event)
#   seat_comms.sh done [text]         the final line; stops a loop
# Orchestrator side:
#   seat_comms.sh send <topic> <STOP|RESUME|SKIP <what>|NOTE <text>>
#   seat_comms.sh --self-test
#
# Refs, round-scoped: <T> is the topic, prefixed `r<ROUND>-` unless it already starts r<digits>-
#   refs/heads/handoff-wip/<T>-comms   the seat writes: PROGRESS.log, ACK.log; fast-forward only
#   refs/heads/inbox/<T>               the orchestrator writes: INBOX, `<n> <epoch> <command>` lines
# It NEVER writes handoff/<topic> or handoff-wip/<topic>: those are the fixer contract's.
# Every Bash call is a fresh shell: init writes $HOME/.seatcomms.env, and every later call reads it.
set -euo pipefail
SEAT_NAME=hpo-fixer; SEAT_EMAIL=70032254+tvofi@users.noreply.github.com

_norm() { local t=$1; [[ $t =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || { echo "comms: bad topic '$t'" >&2; exit 2; }
          if [[ $t =~ ^[rR][0-9]+- ]]; then echo "$t"; else echo "r${ROUND:-11}-$t"; fi; }
_env() {
  if [ -z "${SEAT_TOPIC:-}" ] && [ -f "$HOME/.seatcomms.env" ]; then . "$HOME/.seatcomms.env"; fi
  : "${SEAT_TOPIC:?no topic: run seat_comms.sh init <topic> first}"
  COMMS_REPO=${COMMS_REPO:-$(git rev-parse --show-toplevel)}
  WIP="refs/heads/handoff-wip/${SEAT_TOPIC}-comms"; INBOX="refs/heads/inbox/${SEAT_TOPIC}"
  ST="${COMMS_STATE:-$HOME/.seatcomms-${SEAT_TOPIC}}"; T="$ST/tree"; mkdir -p "$T"
  GD=$(git -C "$COMMS_REPO" rev-parse --absolute-git-dir)
}
_g() { git -C "$COMMS_REPO" "$@"; }
_tip() { _g ls-remote origin "$1" | awk 'NR==1{print $1}'; }
_line() { printf '%s %s\n' "$(date -u +%s)" "$*" >> "$T/PROGRESS.log"; }
_lock() { local i=0; until mkdir "$ST/lock" 2>/dev/null; do i=$((i+1)); [ $i -lt 600 ] || { echo "comms: lock stuck" >&2; exit 4; }; sleep 0.1; done; }
_unlock() { rmdir "$ST/lock" 2>/dev/null || true; }

_push() { # <message> [<snapshot commit>]: the state tree on the remote tip, fast-forward
  _lock; local try tip tree commit ok=1
  for try in 1 2 3 4 5 6; do
    tip=$(_tip "$WIP"); [ -z "$tip" ] || _g fetch -q origin "$tip"
    rm -f "$ST/idx"
    tree=$(cd "$T" && GIT_DIR="$GD" GIT_INDEX_FILE="$ST/idx" GIT_WORK_TREE="$T" sh -c 'git add -A -f . && git write-tree')
    if [ -z "${2:-}" ] && [ -n "$tip" ] && [ "$(_g rev-parse "$tip^{tree}")" = "$tree" ]; then ok=0; break; fi
    commit=$(_g -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${tip:+-p "$tip"} ${2:+-p "$2"} -m "$1")
    if _g push -q origin "$commit:$WIP" 2>/dev/null; then ok=0; break; fi
    sleep "$try"
  done
  _unlock; [ $ok = 0 ] || { echo "comms: push to $WIP failed" >&2; return 4; }
}

_snapshot() { # the working tree as a commit on HEAD: tracked + untracked, .gitignore honoured
  local wt idx tree head; wt=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
  idx="$ST/snapidx"; rm -f "$idx"
  cp "$(git -C "$wt" rev-parse --path-format=absolute --git-path index)" "$idx" 2>/dev/null || true   # warm: only changed files rehash
  head=$(git -C "$wt" rev-parse -q --verify HEAD || true)
  tree=$(cd "$wt" && GIT_INDEX_FILE="$idx" sh -c 'git add -A . && git write-tree')
  git -C "$wt" -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${head:+-p "$head"} -m "comms snapshot"
}

inbox() {
  local tip last n ep cmd arg
  tip=$(_tip "$INBOX"); [ -n "$tip" ] || return 0
  _g fetch -q origin "$tip"
  last=$(awk '{n=$2} END{print n+0}' "$T/ACK.log" 2>/dev/null || echo 0)
  local new=0
  while read -r n ep cmd arg; do
    [ -n "$n" ] && [ "$n" -gt "$last" ] 2>/dev/null || continue
    printf 'ack %s %s %s\n' "$n" "$(date -u +%s)" "$cmd${arg:+ $arg}" >> "$T/ACK.log"
    echo "CMD $n $cmd${arg:+ $arg}"; new=1
  done < <(_g show "$tip:INBOX")
  [ $new = 0 ] || { _line "INBOX acked through $(awk '{n=$2} END{print n}' "$T/ACK.log")"; _push "comms: ack ${SEAT_TOPIC}"; }
}

init() {
  [ $# -ge 1 ] || { echo "usage: seat_comms.sh init <topic>" >&2; exit 2; }
  SEAT_TOPIC=$(_norm "$1"); COMMS_REPO=${COMMS_REPO:-$(git rev-parse --show-toplevel)}
  printf 'SEAT_TOPIC=%s\nCOMMS_REPO=%s\nROUND=%s\n' "$SEAT_TOPIC" "$COMMS_REPO" "${ROUND:-11}" > "$HOME/.seatcomms.env"
  _env; local tip snap
  tip=$(_tip "$WIP")
  if [ -n "$tip" ]; then
    _g fetch -q origin "$tip"; _g archive "$tip" | tar -x -C "$T"; echo "resumed ${tip:0:12}"
    snap=$(_g log -1 --format=%P "$tip" | awk '{print $2}')
    [ -z "$snap" ] || echo "snapshot $snap"
    [ -n "$snap" ] || { snap=$(_g log --format='%P' "$tip" | awk 'NF>1{print $2; exit}'); [ -z "$snap" ] || echo "snapshot $snap"; }
  fi
  _line "INIT ${SEAT_TOPIC}"; _push "comms: init ${SEAT_TOPIC}"
}
hb() { _env; _line "HB ${*:-alive}"; _push "comms: hb ${SEAT_TOPIC}"; }
ckpt() { _env; local snap; snap=$(_snapshot); _line "CKPT ${*:-checkpoint}${snap:+ snapshot ${snap:0:12}}"; _push "comms: ckpt ${SEAT_TOPIC}" "$snap"; }
loop() { _env; local secs=${1:-600}; while [ ! -f "$ST/done" ]; do _line "HB alive"; _push "comms: hb ${SEAT_TOPIC}" || true; inbox || true; sleep "$secs"; done; }
done_() { _env; touch "$ST/done"; _line "DONE ${*:-}"; _push "comms: done ${SEAT_TOPIC}"; }

send() { # <topic> <command...>
  [ $# -ge 2 ] || { echo "usage: seat_comms.sh send <topic> <command>" >&2; return 2; }
  SEAT_TOPIC=$(_norm "$1"); shift; COMMS_REPO=${COMMS_REPO:-$(git rev-parse --show-toplevel)}
  case "$1" in STOP|RESUME) ;; SKIP|NOTE) [ $# -ge 2 ] || { echo "send: $1 needs an argument" >&2; return 2; };; *) echo "send: unknown command $1" >&2; return 2;; esac
  INBOX="refs/heads/inbox/${SEAT_TOPIC}"; GD=$(git -C "$COMMS_REPO" rev-parse --absolute-git-dir)
  local W tip n tree commit try; W=$(mktemp -d)
  for try in 1 2 3 4 5; do
    tip=$(_tip "$INBOX"); : > "$W/INBOX"
    if [ -n "$tip" ]; then _g fetch -q origin "$tip"; _g show "$tip:INBOX" > "$W/INBOX"; fi
    n=$(awk '{n=$1} END{print n+1}' "$W/INBOX"); echo "$n $(date -u +%s) $*" >> "$W/INBOX"
    rm -f "$W/.idx"
    tree=$(cd "$W" && GIT_DIR="$GD" GIT_INDEX_FILE="$W/.idx" GIT_WORK_TREE="$W" sh -c 'git add -f INBOX && git write-tree')
    commit=$(_g -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${tip:+-p "$tip"} -m "inbox: $n $1")
    if _g push -q origin "$commit:$INBOX" 2>/dev/null; then echo "SENT $n $* -> $INBOX"; rm -rf "${W:?}"; return 0; fi
    sleep "$try"
  done
  rm -rf "${W:?}"; return 4
}

self_test() {
  local R O fail=0 out H
  R=$(mktemp -d); O="$R/o.git"; git init -q --bare "$O"
  mk() { git init -q -b main "$R/$1"; git -C "$R/$1" remote add origin "$O"; }
  mk seat; mk orch; mk seat2
  echo base > "$R/seat/f.txt"; git -C "$R/seat" add f.txt; git -C "$R/seat" -c user.name=t -c user.email=t@e commit -qm base
  git -C "$R/seat" push -q origin HEAD:refs/heads/main HEAD:refs/heads/handoff/r11-fx HEAD:refs/heads/handoff-wip/r11-fx
  owned=$(git -C "$R/seat" ls-remote origin refs/heads/handoff/r11-fx refs/heads/handoff-wip/r11-fx)
  t() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fail=1; fi; }
  H="$R/home"; mkdir -p "$H"
  S() { (cd "$R/seat" && HOME="$H" ROUND=11 bash "$SELF" "$@"); }
  O_() { (cd "$R/orch" && ROUND=11 bash "$SELF" "$@"); }
  t "null: before init, no comms ref" '[ -z "$(git -C $R/seat ls-remote origin refs/heads/handoff-wip/r11-fx-comms)" ]'
  S init fx >/dev/null
  t "init: the topic is round-scoped (fx -> r11-fx) and the comms ref exists" '[ -n "$(git -C $R/seat ls-remote origin refs/heads/handoff-wip/r11-fx-comms)" ]'
  S hb "step 1 tests written" >/dev/null
  t "hb: the line lands" 'git -C $R/seat fetch -q origin refs/heads/handoff-wip/r11-fx-comms && git -C $R/seat show FETCH_HEAD:PROGRESS.log | grep -q "HB step 1 tests written"'
  echo edit >> "$R/seat/f.txt"; echo new > "$R/seat/untracked.txt"; echo junk > "$R/seat/ignored.log"; echo '*.log' > "$R/seat/.gitignore"
  S ckpt "mutant proof done" >/dev/null
  git -C "$R/seat" fetch -q origin refs/heads/handoff-wip/r11-fx-comms
  snap=$(git -C "$R/seat" log -1 --format=%P FETCH_HEAD | awk '{print $2}')
  t "ckpt: the snapshot holds the edit and the untracked file" '[ -n "$snap" ] && git -C $R/seat show $snap:f.txt | grep -q edit && git -C $R/seat cat-file -e $snap:untracked.txt'
  t "ckpt null: an ignored file is not in the snapshot" '! git -C $R/seat cat-file -e $snap:ignored.log 2>/dev/null'
  t "ckpt: the seat's own index is untouched (nothing staged)" '[ -z "$(git -C $R/seat diff --cached --name-only)" ]'
  t "never touches handoff/<topic> or handoff-wip/<topic>" '[ "$(git -C $R/seat ls-remote origin refs/heads/handoff/r11-fx refs/heads/handoff-wip/r11-fx)" = "$owned" ]'
  out=$(S inbox)
  t "inbox null: no inbox ref prints nothing" '[ -z "$out" ]'
  O_ send fx STOP >/dev/null; O_ send fx NOTE re-run the darwin lane >/dev/null; O_ send fx FROB >/dev/null 2>&1 || true
  t "send: an unknown command is refused, two land" '[ "$(git -C $R/orch fetch -q origin refs/heads/inbox/r11-fx && git -C $R/orch show FETCH_HEAD:INBOX | wc -l | tr -d " ")" = 2 ]'
  out=$(S inbox)
  t "inbox planted: both commands print in order" '[ "$out" = "$(printf "CMD 1 STOP\nCMD 2 NOTE re-run the darwin lane")" ]'
  t "inbox: acks land on the comms ref" 'git -C $R/seat fetch -q origin refs/heads/handoff-wip/r11-fx-comms && [ "$(git -C $R/seat show FETCH_HEAD:ACK.log | wc -l | tr -d " ")" = 2 ]'
  t "inbox replay: nothing is re-acked" '[ -z "$(S inbox)" ]'
  rm -rf "${H:?}/.seatcomms-r11-fx" "${H:?}/.seatcomms.env"
  out=$(cd "$R/seat2" && HOME="$H" ROUND=11 bash "$SELF" init fx)
  t "resume: a re-fired seat restores its ACK log and finds its snapshot" 'echo "$out" | grep -q "^resumed" && echo "$out" | grep -q "^snapshot $snap" && [ -z "$(cd $R/seat2 && HOME=$H ROUND=11 bash $SELF inbox)" ]'
  (cd "$R/seat2" && HOME="$H" bash "$SELF" done "handed off") >/dev/null
  t "done: the final line lands, and the env file carried the topic into a fresh shell" 'git -C $R/seat fetch -q origin refs/heads/handoff-wip/r11-fx-comms && git -C $R/seat show FETCH_HEAD:PROGRESS.log | tail -1 | grep -q "DONE handed off"'
  t "fast-forward throughout: init's first commit is an ancestor of the tip" 'git -C $R/seat rev-list --first-parent FETCH_HEAD | tail -1 | xargs -I{} git -C $R/seat merge-base --is-ancestor {} FETCH_HEAD'
  t "a topic already round-scoped is kept (R11-VALVE-REFERENCE), a bare one is prefixed (rev-3659)" '[ "$(ROUND=11 bash $SELF --norm R11-VALVE-REFERENCE)" = "R11-VALVE-REFERENCE" ] && [ "$(ROUND=11 bash $SELF --norm rev-3659)" = "r11-rev-3659" ]'
  t "a bad topic is refused" '! ROUND=11 bash $SELF --norm "../handoff" 2>/dev/null'
  rm -rf "${R:?}"; [ $fail = 0 ] && echo "RESULT seat_comms self-test ok" || { echo "RESULT seat_comms self-test FAILED"; return 1; }
}

SELF=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
case "${1:-}" in
  --self-test) self_test;;
  --norm) _norm "$2";;
  send) shift; send "$@";;
  init) shift; init "$@";;
  hb|ckpt|inbox|loop) c=$1; shift; _env; "$c" "$@";;
  done) shift; done_ "$@";;
  *) sed -n '2,30p' "$0"; exit 2;;
esac
