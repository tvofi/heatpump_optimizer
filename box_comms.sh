#!/usr/bin/env bash
# PROTOTYPE (out of tree): the two-way channel between a cloud finder box and the
# orchestrator (owner ruling tvofi 2026-11-16: "establish a communication protocol
# with the cloud dispatches ... to minimize the risk of lost work").
#
# Box side (run in the container; env BOX, ROUND, COMMS_REPO = the box checkout):
#   box_comms.sh init                  restore state from the wip ref if one exists (RESUME after a re-fire);
#                                      prints `reported <seat>` per seat already reported
#   box_comms.sh heartbeat <text>      one PROGRESS line, an inbox poll, one push
#   box_comms.sh loop <secs>           heartbeat every <secs> until DONE; prints `CMD <n> <command>`
#                                      on stdout for each new inbox command (run under Monitor)
#   box_comms.sh poll                  read the inbox; ack and print each new command
#   box_comms.sh gate <seat>           exit 0 start it (prints any NOTE lines to append to its brief),
#                                      1 skip it (reported or SKIPped), 3 the box is STOPped
#   box_comms.sh status <seat> <running|reported|refused|skipped>
#   box_comms.sh checkpoint <seat> <seat dir>   copy the seat's dir (REPORT.json, findings/, harnesses)
#                                      into the wip tree and push it, fast-forward
#   box_comms.sh collect <return ref>  the result commit: CHECK.txt, reports-<box>.json and the reported
#                                      seats' directories ONLY; parentless, or on the return tip if one exists
#   box_comms.sh done                  final heartbeat `DONE`
# Orchestrator side (any checkout):
#   box_comms.sh send <box> <STOP|RESUME|SKIP <seat>|NOTE <text>>   append one numbered command to the inbox ref
#   box_comms.sh --self-test
#
# Refs (round-scoped so round 12 never reads round 11's):
#   refs/heads/handoff-wip/finder-r<ROUND>-<BOX>   the box's wip tree: PROGRESS.log, ACK.log, status/<seat>,
#                                                  seats/<seat>/... ; every push fast-forwards
#   refs/heads/inbox/finder-r<ROUND>-<BOX>         INBOX, one line per command: `<n> <epoch> <command>`
# Every push builds its tree from the box's local state, which init restored from the
# remote, so the tree is always a superset and a push never needs a merge; concurrent
# writers in one container serialise on a mkdir lock and retry a rejected push.
# Times are epoch seconds, so the watch reads them identically on macOS and Linux.
set -euo pipefail
SEAT_NAME=hpo-fixer; SEAT_EMAIL=70032254+tvofi@users.noreply.github.com

_refs() {
  # A Bash call in a cloud session (or a subagent's) is a fresh shell: the box seat writes
  # its identity once to $HOME/.boxcomms.env and every call reads it when BOX is unset.
  if [ -z "${BOX:-}" ] && [ -f "$HOME/.boxcomms.env" ]; then . "$HOME/.boxcomms.env"; fi
  : "${BOX:?BOX}" "${ROUND:?ROUND}" "${COMMS_REPO:?COMMS_REPO}"
  WIP="refs/heads/handoff-wip/finder-r${ROUND}-${BOX}"; INBOX="refs/heads/inbox/finder-r${ROUND}-${BOX}"
  ST="${COMMS_STATE:-$HOME/.boxcomms-r${ROUND}-${BOX}}"; T="$ST/tree"; mkdir -p "$T/status" "$T/seats"
  GD=$(git -C "$COMMS_REPO" rev-parse --absolute-git-dir)
}
_g() { git -C "$COMMS_REPO" "$@"; }
_tip() { _g ls-remote origin "$1" | awk 'NR==1{print $1}'; }
_lock() { local i=0; until mkdir "$ST/lock" 2>/dev/null; do i=$((i+1)); [ $i -lt 600 ] || { echo "comms: lock stuck" >&2; exit 4; }; sleep 0.1; done; }
_unlock() { rmdir "$ST/lock" 2>/dev/null || true; }

_push() { # <message>: commit the state tree on top of the remote tip and push, fast-forward
  _lock; local try tip tree commit ok=1
  for try in 1 2 3 4 5 6; do
    tip=$(_tip "$WIP"); [ -z "$tip" ] || _g fetch -q origin "$tip"
    tree=$(cd "$T" && GIT_DIR="$GD" GIT_INDEX_FILE="$ST/idx" GIT_WORK_TREE="$T" sh -c 'git add -A -f . && git write-tree')
    if [ -n "$tip" ] && [ "$(_g rev-parse "$tip^{tree}")" = "$tree" ]; then ok=0; break; fi
    commit=$(_g -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${tip:+-p "$tip"} -m "$1")
    if _g push -q origin "$commit:$WIP" 2>/dev/null; then ok=0; break; fi
    sleep $((try))
  done
  _unlock; [ $ok = 0 ] || { echo "comms: push to $WIP failed" >&2; return 4; }
}

_line() { printf '%s %s\n' "$(date -u +%s)" "$*" >> "$T/PROGRESS.log"; }

poll() { # ack and print each inbox command newer than the last acked one
  local tip last n ep cmd arg res
  tip=$(_tip "$INBOX"); [ -n "$tip" ] || return 0
  _g fetch -q origin "$tip"
  last=$(awk '{n=$2} END{print n+0}' "$T/ACK.log" 2>/dev/null || echo 0)
  while read -r n ep cmd arg; do
    [ -n "$n" ] && [ "$n" -gt "$last" ] 2>/dev/null || continue
    case "$cmd" in
      STOP) touch "$ST/stop"; res=stopped;;
      RESUME) rm -f "$ST/stop"; res=resumed;;
      SKIP) if [ -n "$arg" ]; then echo "$arg" >> "$T/skip"; res="skip $arg"; else res="refused: SKIP needs a seat"; fi;;
      NOTE) if [ -n "$arg" ]; then printf '%s\n' "$arg" >> "$ST/notes"; res=noted; else res="refused: empty NOTE"; fi;;
      *) res="refused: unknown command";;
    esac
    printf 'ack %s %s %s %s\n' "$n" "$(date -u +%s)" "$cmd" "$res" >> "$T/ACK.log"
    echo "CMD $n $cmd${arg:+ $arg} -> $res"
  done < <(_g show "$tip:INBOX")
}

init() {
  local tip; tip=$(_tip "$WIP")
  if [ -n "$tip" ]; then _g fetch -q origin "$tip"; _g archive "$tip" | tar -x -C "$T"; _line "RESUMED from ${tip:0:12}"; fi
  [ -f "$T/stop" ] && touch "$ST/stop" || true
  for f in "$T"/status/*; do [ -f "$f" ] || continue; [ "$(cat "$f")" = reported ] && echo "reported $(basename "$f")"; done
  _line "INIT box ${BOX}"; poll >/dev/null; _push "comms: init ${BOX}"
}

heartbeat() { _line "HB $*"; poll; _push "comms: heartbeat ${BOX}"; }

status() { echo "$2" > "$T/status/$1"; _line "SEAT $1 $2"; _push "comms: $1 $2"; }

checkpoint() { # <seat> <dir>
  [ -d "$2" ] || { echo "comms: no seat dir $2" >&2; return 2; }
  mkdir -p "$T/seats/$1"; cp -R "$2/." "$T/seats/$1/"
  _line "CKPT $1 $(find "$T/seats/$1" -type f | wc -l | tr -d ' ') file(s)"; _push "comms: checkpoint $1"
}

gate() { # <seat>
  poll >/dev/null
  [ ! -f "$ST/stop" ] || { _line "GATE $1 stopped"; _push "comms: gate $1"; return 3; }
  if [ "$(cat "$T/status/$1" 2>/dev/null)" = reported ] || grep -qx "$1" "$T/skip" 2>/dev/null; then
    _line "GATE $1 skip"; _push "comms: gate $1"; return 1; fi
  if [ -s "$ST/notes" ]; then cat "$ST/notes"; : > "$ST/notes"; fi
  return 0
}

loop() { local secs=${1:-600}; while [ ! -f "$ST/done" ]; do heartbeat "alive" || true; sleep "$secs"; done; }

done_() { touch "$ST/done"; _line "DONE"; _push "comms: done ${BOX}"; }

collect() { # <return ref>: the box's result commit, RESULT FILES ONLY, built from the state tree
  # Layout: CHECK.txt at the root, dev/audit/rounds/round<N>/reports-<box>.json, and each seat's
  # checkpointed directory at dev/audit/rounds/round<N>/<dim>/<key>/. Never the repository tree.
  # Parent: the return ref's tip when one exists (the orchestrator's local seats landed first;
  # reports are unioned), else none (parentless). Refuses with 2 when CHECK.txt is missing.
  local ret=$1 tip W tree commit try
  [ -s "$T/CHECK.txt" ] || { echo "collect: $T/CHECK.txt is missing: run the report check (step 4) first" >&2; return 2; }
  for try in 1 2 3 4 5; do
    W=$(mktemp -d); tip=$(_tip "$ret")
    if [ -n "$tip" ]; then _g fetch -q origin "$tip"; _g archive "$tip" | tar -x -C "$W"; fi
    python3 -I - "$T" "$W" "$ROUND" "$BOX" <<'PY'
import json, shutil, sys
from pathlib import Path
t, w, rnd, box = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
rd = w / f"dev/audit/rounds/round{rnd}"
rj = rd / f"reports-{box}.json"
doc = json.loads(rj.read_text()) if rj.exists() else {"box": box, "missing": [], "reports": {}}
missing = set(doc.get("missing", []))
for st in sorted((t / "status").glob("*")):
    seat, state = st.name, st.read_text().strip()
    rep = t / "seats" / seat / "REPORT.json"
    if state == "reported" and rep.is_file():
        dim, key = seat.split("-", 1)
        dst = rd / dim / key
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copytree(t / "seats" / seat, dst, dirs_exist_ok=True)
        doc["reports"][seat] = json.loads(rep.read_text())
    elif state != "running":
        missing.add(seat)
doc["missing"] = sorted(missing - set(doc["reports"]))
rd.mkdir(parents=True, exist_ok=True)
rj.write_text(json.dumps(doc, indent=2) + "\n")
shutil.copy(t / "CHECK.txt", w / "CHECK.txt")
print(f"collect: {len(doc['reports'])} reported, {len(doc['missing'])} missing")
PY
    rm -f "$ST/ridx"
    tree=$(cd "$W" && GIT_DIR="$GD" GIT_INDEX_FILE="$ST/ridx" GIT_WORK_TREE="$W" sh -c 'git add -A -f . && git write-tree')
    commit=$(_g -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${tip:+-p "$tip"} -m "audit(r${ROUND}): box ${BOX} result")
    rm -rf "${W:?}"
    if _g push -q origin "$commit:$ret" 2>/dev/null; then echo "RETURNED $commit $ret"; _line "RETURN ${commit:0:12}"; _push "comms: returned ${BOX}"; return 0; fi
    sleep "$try"
  done
  echo "collect: $ret moved under five tries" >&2; return 4
}

send() { # <box> <command...>   (orchestrator side; ROUND, COMMS_REPO in env)
  BOX=$1; shift; _refs; local tip n tree commit W; W=$(mktemp -d)
  case "$1" in STOP|RESUME) ;; SKIP|NOTE) [ $# -ge 2 ] || { echo "send: $1 needs an argument" >&2; return 2; };; *) echo "send: unknown command $1" >&2; return 2;; esac
  for try in 1 2 3 4 5; do
    tip=$(_tip "$INBOX"); : > "$W/INBOX"
    if [ -n "$tip" ]; then _g fetch -q origin "$tip"; _g show "$tip:INBOX" > "$W/INBOX"; fi
    n=$(awk '{n=$1} END{print n+1}' "$W/INBOX"); echo "$n $(date -u +%s) $*" >> "$W/INBOX"
    tree=$(cd "$W" && GIT_DIR="$GD" GIT_INDEX_FILE="$W/idx" GIT_WORK_TREE="$W" sh -c 'git add -f INBOX && git write-tree')
    commit=$(_g -c user.name=$SEAT_NAME -c user.email=$SEAT_EMAIL commit-tree "$tree" ${tip:+-p "$tip"} -m "inbox: $n $1")
    if _g push -q origin "$commit:$INBOX" 2>/dev/null; then echo "SENT $n $*"; rm -rf "${W:?}"; return 0; fi
    sleep "$try"
  done
  rm -rf "${W:?}"; return 4
}

self_test() {
  local R O A B fail=0 out
  R=$(mktemp -d); O="$R/origin.git"; git init -q --bare "$O"
  for c in A B C; do git init -q "$R/$c"; git -C "$R/$c" remote add origin "$O"; done
  export ROUND=99 COMMS_REPO="$R/A"
  ok() { echo "ok   $1"; }; bad() { echo "FAIL $1"; fail=1; }
  t() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
  # (a) heartbeat
  t "a-null: no heartbeat, no wip ref" '[ -z "$(git -C $R/A ls-remote origin refs/heads/handoff-wip/finder-r99-X1)" ]'
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; init >/dev/null; heartbeat "seat D1-s2 started" >/dev/null )
  t "a-planted: heartbeat lands on the wip ref" 'git -C $R/A fetch -q origin refs/heads/handoff-wip/finder-r99-X1 && git -C $R/A show FETCH_HEAD:PROGRESS.log | grep -q "HB seat D1-s2 started"'
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; ( loop 1 >/dev/null ) & lp=$!; sleep 3.5; touch "$ST/done"; wait $lp )
  t "a-loop: periodic heartbeats (>=2 in 3.5 s at 1 s)" '[ "$(git -C $R/A fetch -q origin refs/heads/handoff-wip/finder-r99-X1 && git -C $R/A show FETCH_HEAD:PROGRESS.log | grep -c "HB alive")" -ge 2 ]'
  # (b) checkpoint
  mkdir -p "$R/seat/findings"; echo '{"id":"D1-s2-01"}' > "$R/seat/findings/D1-s2-01.json"
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; rm -f "$ST/done"; checkpoint D1-s2 "$R/seat" )
  t "b-planted: a written finding is on the wip ref" 'git -C $R/A fetch -q origin refs/heads/handoff-wip/finder-r99-X1 && git -C $R/A cat-file -e FETCH_HEAD:seats/D1-s2/findings/D1-s2-01.json'
  echo '{"id":"D1-s2-02"}' > "$R/seat/findings/D1-s2-02.json"
  t "b-null: a finding not yet checkpointed is absent" '! git -C $R/A cat-file -e FETCH_HEAD:seats/D1-s2/findings/D1-s2-02.json 2>/dev/null'
  prev=$(git -C "$R/A" rev-parse FETCH_HEAD)
  mkdir -p "$R/seat2/findings"; echo '{"id":"D1-s3-01"}' > "$R/seat2/findings/D1-s3-01.json"
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; checkpoint D1-s2 "$R/seat" & checkpoint D1-s3 "$R/seat2" & wait )
  t "b-concurrent: two seats checkpointing at once both land, fast-forward" 'git -C $R/A fetch -q origin refs/heads/handoff-wip/finder-r99-X1 && git -C $R/A cat-file -e FETCH_HEAD:seats/D1-s2/findings/D1-s2-02.json && git -C $R/A cat-file -e FETCH_HEAD:seats/D1-s3/findings/D1-s3-01.json && git -C $R/A merge-base --is-ancestor $prev FETCH_HEAD'
  # (c) inbox
  out=$(export BOX=X1 COMMS_STATE="$R/sA"; _refs; poll)
  t "c-null: empty inbox prints nothing and acks nothing" '[ -z "$out" ] && ! grep -q . "$R/sA/tree/ACK.log" 2>/dev/null'
  ( export COMMS_REPO="$R/B"; send X1 STOP >/dev/null; send X1 SKIP D1-s3 >/dev/null; send X1 NOTE check the boost path first >/dev/null; send X1 FROB >/dev/null 2>&1 || true )
  t "c-send: unknown command refused at send" '[ "$(git -C $R/B fetch -q origin refs/heads/inbox/finder-r99-X1 && git -C $R/B show FETCH_HEAD:INBOX | wc -l | tr -d " ")" = 3 ]'
  out=$(export BOX=X1 COMMS_STATE="$R/sA"; _refs; poll; _push "t")
  t "c-planted: three commands acked in order" 'echo "$out" | grep -q "CMD 1 STOP -> stopped" && echo "$out" | grep -q "CMD 2 SKIP D1-s3" && echo "$out" | grep -q "CMD 3 NOTE check the boost path first -> noted"'
  t "c-ack on the progress ref" 'git -C $R/A fetch -q origin refs/heads/handoff-wip/finder-r99-X1 && [ "$(git -C $R/A show FETCH_HEAD:ACK.log | wc -l | tr -d " ")" = 3 ]'
  t "c-replay: a second poll re-acks nothing" '[ -z "$(export BOX=X1 COMMS_STATE=$R/sA; _refs; poll)" ]'
  t "c-STOP: gate refuses with 3" '(export BOX=X1 COMMS_STATE=$R/sA; _refs; set +e; gate D2-s1 >/dev/null; [ $? = 3 ])'
  ( export COMMS_REPO="$R/B"; send X1 RESUME >/dev/null )
  out=$(export BOX=X1 COMMS_STATE="$R/sA"; _refs; set +e; gate D2-s1; echo "rc=$?")
  t "c-RESUME + NOTE: gate starts the seat and hands it the note once" 'echo "$out" | grep -q "check the boost path first" && echo "$out" | grep -q "rc=0"'
  t "c-NOTE consumed: the next seat gets no note" '[ "$(export BOX=X1 COMMS_STATE=$R/sA; _refs; gate D2-s2)" = "" ]'
  t "c-SKIP: the skipped seat is refused with 1" '(export BOX=X1 COMMS_STATE=$R/sA; _refs; set +e; gate D1-s3 >/dev/null; [ $? = 1 ])'
  # (d) resume
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; status D1-s2 reported >/dev/null )
  out=$(export BOX=X1 COMMS_STATE="$R/sFresh" COMMS_REPO="$R/C"; _refs; init)
  t "d-planted: a re-fired box restores its reported seat" 'echo "$out" | grep -qx "reported D1-s2"'
  t "d-planted: and gate skips it" '(export BOX=X1 COMMS_STATE=$R/sFresh COMMS_REPO=$R/C; _refs; set +e; gate D1-s2 >/dev/null; [ $? = 1 ])'
  t "d-planted: its checkpointed findings came back" '[ -f "$R/sFresh/tree/seats/D1-s2/findings/D1-s2-02.json" ]'
  out=$(export BOX=X2 COMMS_STATE="$R/sX2" COMMS_REPO="$R/C"; _refs; init)
  t "d-null: a box with no wip ref restores nothing" '[ -z "$out" ]'
  # (f) collect: the result commit is result-only
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; set +e; collect refs/heads/handoff-wip/finder-r99-X1-result >/dev/null 2>&1; [ $? = 2 ] ) \
    && echo "ok   f-null: collect refuses without CHECK.txt" || { echo "FAIL f-null: collect without CHECK.txt"; fail=1; }
  echo "x" > "$R/A/README"; git -C "$R/A" add README; git -C "$R/A" -c user.name=t -c user.email=t@e commit -qm repo; git -C "$R/A" push -q origin HEAD:refs/heads/main
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; echo "ok D1-s2" > "$T/CHECK.txt"; status D1-s3 missing >/dev/null; collect refs/heads/handoff-wip/finder-r99-X1-result >/dev/null )
  git -C "$R/A" fetch -q origin refs/heads/handoff-wip/finder-r99-X1-result
  files=$(git -C "$R/A" ls-tree -r --name-only FETCH_HEAD | sort | tr '\n' ' ')
  t "f-planted: result-only tree (CHECK.txt and the reports json), parentless" \
    '[ "$files" = "CHECK.txt dev/audit/rounds/round99/reports-X1.json " ] && [ -z "$(git -C $R/A log -1 --format=%P FETCH_HEAD)" ]'
  t "f-planted: the repository tree is not on it (README absent)" '! git -C $R/A cat-file -e FETCH_HEAD:README 2>/dev/null'
  t "f-planted: a seat marked reported with no REPORT.json is missing, never reported" \
    'git -C $R/A show FETCH_HEAD:dev/audit/rounds/round99/reports-X1.json | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d[\"missing\"]==[\"D1-s2\",\"D1-s3\"] and d[\"reports\"]=={} else 1)"'
  first=$(git -C "$R/A" rev-parse FETCH_HEAD)
  echo '{"findings": []}' > "$R/seat/REPORT.json"
  ( export BOX=X1 COMMS_STATE="$R/sA"; _refs; checkpoint D1-s2 "$R/seat" >/dev/null; status D1-s2 reported >/dev/null; collect refs/heads/handoff-wip/finder-r99-X1-result >/dev/null )
  git -C "$R/A" fetch -q origin refs/heads/handoff-wip/finder-r99-X1-result
  t "f-planted: a second collect lands on the return tip, D1-s2 reported with its findings, D1-s3 still missing" \
    '[ "$(git -C $R/A log -1 --format=%P FETCH_HEAD)" = "$first" ] && git -C $R/A cat-file -e FETCH_HEAD:dev/audit/rounds/round99/D1/s2/findings/D1-s2-02.json && ! git -C $R/A cat-file -e FETCH_HEAD:README 2>/dev/null && git -C $R/A show FETCH_HEAD:dev/audit/rounds/round99/reports-X1.json | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if list(d[\"reports\"])==[\"D1-s2\"] and d[\"missing\"]==[\"D1-s3\"] else 1)"'
  rm -rf "${R:?}"; [ $fail = 0 ] && echo "RESULT box_comms self-test ok" || { echo "RESULT box_comms self-test FAILED"; return 1; }
}

case "${1:-}" in
  --self-test) self_test;;
  send) shift; send "$@";;
  init|heartbeat|loop|poll|gate|status|checkpoint|collect) c=$1; shift; _refs; "$c" "$@";;
  done) _refs; done_;;
  *) sed -n '2,24p' "$0"; exit 2;;
esac
