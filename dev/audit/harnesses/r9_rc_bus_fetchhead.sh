#!/bin/bash
# r9_rc_bus_fetchhead.sh -- the two bus.sh defects, measured on whatever bus.sh
# you name, so the red and the green are both reproducible without a worktree
# per round. (R9-RC-BUS-FETCHHEAD, 2026-10-09: #2071's round-4 reviewer's first
# push-verdict was built parented on main's tip, and #2074's confirm signed and
# pushed verdict/2074 (7c64dd213) and THEN failed at the post.)
#
#   r9_rc_bus_fetchhead.sh <path to bus.sh> race    # the intervening fetch
#   r9_rc_bus_fetchhead.sh <path to bus.sh> append  # the null control, no plant
#   r9_rc_bus_fetchhead.sh <path to bus.sh> ootree  # the out-of-tree copy
#   r9_rc_bus_fetchhead.sh <body_push.sh>    bodypush    # the sibling: the parent
#   r9_rc_bus_fetchhead.sh <handoff_push.sh> handoffpush # the sibling: the body
#
# `race` appends a second verdict onto an existing review/<pr> while a fetch of
# an UNRELATED ref lands in the window between the script's own fetch of the ref
# and its read of the tip. It injects the window with a git wrapper on PATH that
# performs the unrelated fetch right after the first `fetch` it sees -- measured
# (probe, 2026-10-09) that `git fetch` rewrites FETCH_HEAD even when the ref is
# unchanged, so a plant placed BEFORE the script's own fetch is read by nothing
# and would be green on the very bug it is meant to catch.
#
# It then reports the PARENT OF THE BUILT COMMIT, never whether the push
# succeeded: a refused push is already today's behaviour, so an arm that passes
# on refusal proves nothing. Exit 0 when that parent is the ref's previous tip.
#
# `ootree` runs `confirm` from a copy parked outside any checkout, where the
# script's ROOT resolves above the tree and its default poster is a path that
# cannot exist, and reports whether the verdict ref moved anyway -- the
# half-applied bus operation. Exit 0 only when nothing was pushed and nothing
# was posted.
#
# Hermetic: a bare origin and a seat clone in a throwaway tree through
# tests/throwaway_git.sh; the poster is a stub that only records its calls; no
# network and no real pull request. Plain variables: macOS /bin/bash 3.2.
set -uo pipefail

HERE=$(cd "$(dirname -- "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
BUS=${1:-}
MODE=${2:-race}
[ -f "$BUS" ] || { echo "usage: $0 <bus.sh> [race|append|ootree]  (no bus.sh at '$BUS')" >&2; exit 2; }
# Absolute: every run below cds into the seat clone first.
BUS=$(cd "$(dirname -- "$BUS")" && pwd)/$(basename -- "$BUS")
[ -f "$ROOT/tests/throwaway_git.sh" ] \
  || { echo "no tests/throwaway_git.sh under $ROOT" >&2; exit 2; }

W=$(mktemp -d) || exit 2
PR=21
H1=1111111111111111111111111111111111111111
H2=2222222222222222222222222222222222222222
REAL=$(command -v git)          # before the shim is on PATH, or the wrapper recurses
# The timestamps are pinned for the whole run so every sha printed here is a
# measurement that can be DIFFED, not a claim that the output "looks the same":
# run `append` against the pre-fix and the fixed bus.sh and the two outputs must
# be identical, byte for byte, or the fix changed an append that already worked.
# CEST+0200, the zone this box runs in, never labelled Z.
export GIT_AUTHOR_DATE='2026-10-09T12:00:00+02:00' GIT_COMMITTER_DATE='2026-10-09T12:00:00+02:00'
. "$ROOT/tests/throwaway_git.sh"
throwaway_git_env
throwaway_git_init "$W/origin.git" -q --bare
throwaway_git_init "$W/seat" -q
git -C "$W/seat" remote add origin "$W/origin.git"
git -C "$W/seat" -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
git -C "$W/seat" push -q origin HEAD:refs/heads/main
MAIN=$(git -C "$W/origin.git" rev-parse refs/heads/main)

mkdir -p "$W/state" "$W/ev1" "$W/ev2" "$W/ap" "$W/calls"
printf 'measured at %s\n' "$H1" > "$W/ev1/run.log"
printf 'round two at %s\n' "$H1" > "$W/ev2/run.log"
openssl genrsa -out "$W/ap/identity-approver.pem" 2048 2>/dev/null \
  || { echo "no openssl: the arm needs the approver key" >&2; exit 2; }
cat > "$W/poster" <<'P'
#!/bin/bash
printf 'CALL %s %s\n' "$1" "$2" >> "$BUS_RACE_CALLS"
P
chmod +x "$W/poster"
export BUS_RACE_CALLS=$W/calls/log
: > "$W/calls/log"
calls() { local n; n=$(grep -c . "$W/calls/log" 2>/dev/null) || n=0; printf '%s\n' "$n"; }
bus() { (cd "$W/seat" && HPO_BUS_STATE=$W/state HPO_BUS_POSTER=$W/poster \
          HPO_IDENTITY_DIR=$W/ap bash "$BUS" "$@") 2>&1; }
tip() { git -C "$W/origin.git" rev-parse --verify -q "$1"; }
ref_exists() { git -C "$W/origin.git" show-ref -q --verify "$1"; }

# THE PLANT, for every mode that needs a fetch inside the window: a git wrapper
# that, after the FIRST fetch whose arguments name $BUS_ST_PLANT_MATCH, performs
# one more fetch of $BUS_ST_PLANT_REF in this same checkout -- the state any
# other writer in the checkout leaves behind, in the exact window the instrument
# reads in next. It must go INSIDE the window: measured (probe, 2026-10-09) that
# `git fetch` rewrites FETCH_HEAD even when the ref is unchanged, so a plant
# placed BEFORE the instrument's own fetch is overwritten by it and the arm
# would be green on the very bug it pins.
mkdir -p "$W/shim"
cat > "$W/shim/git" <<'S'
#!/bin/bash
if [ "${1:-}" = fetch ] && [ ! -e "$BUS_ST_WINDOW" ]; then
  case " $* " in
    *" $BUS_ST_PLANT_MATCH "*)
      : > "$BUS_ST_WINDOW"
      "$BUS_ST_REAL" "$@"
      rc=$?
      "$BUS_ST_REAL" -C "$PWD" fetch -q origin "$BUS_ST_PLANT_REF" >/dev/null 2>&1
      exit $rc
      ;;
  esac
fi
exec "$BUS_ST_REAL" "$@"
S
chmod +x "$W/shim/git"
export BUS_ST_REAL=$REAL
planted() { # <fetch that opens the window> <ref to fetch after it> <command...>
  local m=$1 r=$2
  shift 2
  rm -f "$W/window"
  PATH="$W/shim:$PATH" BUS_ST_WINDOW=$W/window BUS_ST_PLANT_MATCH=$m BUS_ST_PLANT_REF=$r "$@"
}
planted_here() { # the same, run from the seat clone
  local m=$1 r=$2
  shift 2
  ( cd "$W/seat" && planted "$m" "$r" "$@" )
}
# A commit whose tree is BODY.md only, with the given marker text: the body
# fixtures for the two sibling instruments, built without those instruments.
bodycommit() { # <marker> <message>
  local b tr
  b=$(printf 'BODY MARKER %s\n' "$1" | git -C "$W/seat" hash-object -w --stdin)
  tr=$(printf '100644 blob %s\tBODY.md\n' "$b" | git -C "$W/seat" mktree)
  printf '%s' "$2" | git -C "$W/seat" commit-tree "$tr"
}

if [ "$MODE" = race ]; then
  N=$(bus dispatch 21 "$H1" cmsg_race | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/v1.md"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/v2.md"
  out=$(bus push-verdict 21 "$W/v1.md" "$W/ev1") || { echo "round 1 failed: $out" >&2; exit 2; }
  A=$(tip refs/heads/review/21)
  [ -n "$A" ] || { echo "no review/21 after round 1" >&2; exit 2; }

  rm -f "$W/window"
  out=$(planted refs/heads/review/21 refs/heads/main bus push-verdict 21 "$W/v2.md" "$W/ev2")
  rc=$?
  B=$(tip refs/heads/review/21)
  FH=$(git -C "$W/seat" rev-parse FETCH_HEAD 2>/dev/null || echo unreadable)
  echo "== race =="
  echo "main tip (the unrelated ref) ....... $MAIN"
  echo "review/21 before (the real parent) . $A"
  echo "FETCH_HEAD the script could read ... $FH"
  echo "push-verdict rc .................... $rc"
  echo "review/21 after .................... ${B:-absent}"
  PARENT=""
  if [ -n "$B" ] && [ "$B" != "$A" ]; then
    # The push landed: read the built commit's parent off the ref.
    PARENT=$(git -C "$W/origin.git" rev-parse "refs/heads/review/21^")
    echo "built commit ....................... $B"
    echo "its parent ......................... $PARENT   (asserted)"
  else
    # The push was refused: the commit still exists in the seat's object store.
    echo "output: $out"
    for c in $(git -C "$W/seat" fsck --no-reflogs --unreachable 2>/dev/null \
                 | awk '$2 == "commit" { print $3 }'); do
      p=$(git -C "$W/seat" rev-parse -q --verify "$c^" 2>/dev/null || echo none)
      tr=$(git -C "$W/seat" rev-parse "$c^{tree}" 2>/dev/null)
      [ "$tr" = "$(git -C "$W/seat" rev-parse "$A^{tree}" 2>/dev/null)" ] && continue
      echo "built commit (unreachable) ......... $c"
      echo "its parent ......................... $p   (asserted)"
      PARENT=$p
    done
  fi
  echo "verdict: parent == ref's previous tip? $([ "$PARENT" = "$A" ] && echo yes || echo no)"
  [ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
  [ "$PARENT" = "$A" ] || exit 1
  exit 0
fi

# ---- bodypush: the same predicate in body_push.sh ----
# body_push.sh appends a body commit onto handoff-body/<topic> and read that
# ref's tip back through FETCH_HEAD to parent it. The arm plants a fetch of the
# OTHER topic's body ref in the window, so FETCH_HEAD names the wrong ref exactly
# when the instrument reads it, and asserts the built commit's parent.
if [ "$MODE" = bodypush ]; then
  a1=$(bodycommit A "body: A round 1")
  b1=$(bodycommit B "body: B round 1")
  git -C "$W/seat" push -q origin "$a1:refs/heads/handoff-body/A"
  git -C "$W/seat" push -q origin "$b1:refs/heads/handoff-body/B"
  A1=$(tip refs/heads/handoff-body/A)
  B1=$(tip refs/heads/handoff-body/B)
  printf 'a body for topic A\n' > "$W/bodysrc.md"
  out=$(planted_here refs/heads/handoff-body/A refs/heads/handoff-body/B \
        bash "$BUS" A "$W/bodysrc.md")
  rc=$?
  B2=$(tip refs/heads/handoff-body/A)
  FH=$(git -C "$W/seat" rev-parse FETCH_HEAD 2>/dev/null || echo unreadable)
  echo "== sibling: body_push.sh =="
  echo "handoff-body/A before .............. $A1"
  echo "handoff-body/B (the decoy) ......... $B1"
  echo "FETCH_HEAD the script could read ... $FH"
  echo "body_push.sh rc .................... $rc"
  echo "handoff-body/A after ............... ${B2:-absent}"
  PARENT=""
  if [ -n "$B2" ] && [ "$B2" != "$A1" ]; then
    PARENT=$(git -C "$W/origin.git" rev-parse refs/heads/handoff-body/A^)
    echo "built commit ....................... $B2"
  else
    echo "output: $out"
    for c in $(git -C "$W/seat" fsck --no-reflogs --unreachable 2>/dev/null \
                 | awk '$2 == "commit" { print $3 }'); do
      [ "$(git -C "$W/seat" rev-parse "$c^{tree}")" = "$(git -C "$W/seat" rev-parse "$A1^{tree}")" ] && continue
      echo "built commit (unreachable) ......... $c"
      PARENT=$(git -C "$W/seat" rev-parse -q --verify "$c^" 2>/dev/null || echo none)
    done
  fi
  echo "its parent ......................... ${PARENT:-none}   (asserted)"
  echo "verdict: parent == handoff-body/A's tip? $([ "$PARENT" = "$A1" ] && echo yes || echo no)"
  [ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
  [ "$PARENT" = "$A1" ] || exit 1
  exit 0
fi

# ---- handoffpush: the same predicate in handoff_push.sh, with a worse outcome ----
# It reads the pull request's BODY.md out of handoff-body/<topic> through
# FETCH_HEAD, from the MAIN checkout where fetches are constant. An intervening
# fetch of another topic's body ref therefore publishes ANOTHER TOPIC'S body as
# this pull request's -- a wrong artifact, not a refusal. The arm plants exactly
# that and asserts on the body file the instrument wrote.
if [ "$MODE" = handoffpush ]; then
  a1=$(bodycommit A "body: A round 1")
  b1=$(bodycommit B "body: B round 1")
  git -C "$W/seat" push -q origin "$a1:refs/heads/handoff-body/A"
  git -C "$W/seat" push -q origin "$b1:refs/heads/handoff-body/B"
  C=$(git -C "$W/seat" rev-parse HEAD)
  git -C "$W/seat" push -q origin "HEAD:refs/heads/handoff/A"
  # A copy inside the throwaway checkout, so the script's own M and its
  # worktree, branch and push all stay in the throwaway repository.
  mkdir -p "$W/seat/tools/audit/seat"
  cp "$BUS" "$W/seat/tools/audit/seat/handoff_push.sh"
  out=$(planted_here refs/heads/handoff-body/A refs/heads/handoff-body/B \
        env HPO_STATE_DIR=$W/state HPO_WT_ROOT=$W/wt \
        bash "$W/seat/tools/audit/seat/handoff_push.sh" A "$C" "T")
  rc=$?
  BODYPUB=$W/state/bodies/A-body.md
  echo "== sibling: handoff_push.sh =="
  echo "handoff-body/A BODY.md ............. $(git -C "$W/origin.git" show refs/heads/handoff-body/A:BODY.md)"
  echo "handoff-body/B BODY.md (the decoy) . $(git -C "$W/origin.git" show refs/heads/handoff-body/B:BODY.md)"
  echo "handoff_push.sh rc ................. $rc"
  if [ -f "$BODYPUB" ]; then
    echo "published body ..................... $(grep -m1 'BODY MARKER' "$BODYPUB" || echo 'no marker line')"
    if grep -q 'BODY MARKER A' "$BODYPUB" && ! grep -q 'BODY MARKER B' "$BODYPUB"; then
      echo "verdict: the published body is topic A's: yes"
      [ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
      exit 0
    fi
    echo "verdict: the published body is NOT topic A's"
  else
    echo "verdict: no body written at $BODYPUB -- the arm never reached the read"
  fi
  [ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
  exit 1
fi

# ---- append: the null control ----
# No plant at all: the ordinary two-round append that already worked. Printed
# with the timestamps pinned, so running this mode against the pre-fix and the
# fixed bus.sh and diffing the two outputs IS the null control -- a changed
# parent, tree or message shows up as a different sha, and nothing else here
# depends on the working directory.
if [ "$MODE" = append ]; then
  # A fixed nonce, not one `dispatch` mints: the verdict file's bytes are part
  # of the commit, so a random nonce would change every sha below and the two
  # runs would differ for a reason that has nothing to do with the fix.
  N=0123456789abcdef0123456789abcdef
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/n1.md"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/n2.md"
  out=$(bus push-verdict 30 "$W/n1.md" "$W/ev1") || { echo "round 1 failed: $out" >&2; exit 2; }
  A=$(tip refs/heads/review/30)
  out=$(bus push-verdict 30 "$W/n2.md" "$W/ev2") || { echo "round 2 failed: $out" >&2; exit 2; }
  echo "== append (no intervening fetch) =="
  echo "round-1 commit ...................... $A"
  echo "round-2 commit ...................... $(tip refs/heads/review/30)"
  echo "round-2 parent ...................... $(git -C "$W/origin.git" rev-parse refs/heads/review/30^)"
  echo "review/30 tree ...................... $(git -C "$W/origin.git" rev-parse 'refs/heads/review/30^{tree}')"
  echo "round-2 message ..................... $(git -C "$W/origin.git" log -1 --format=%s refs/heads/review/30)"
  [ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
  exit 0
fi

# ---- ootree ----
# Three levels under $W, so ROOT resolves to $W itself, which is not a checkout.
mkdir -p "$W/a/b/c"
cp "$BUS" "$W/a/b/c/bus.sh"
N=$(bus dispatch 21 "$H1" cmsg_ootree | sed -n 's/^bus-nonce: //p')
printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/v1.md"
out=$(bus push-verdict 21 "$W/v1.md" "$W/ev1") || { echo "proposal failed: $out" >&2; exit 2; }
R=$(tip refs/heads/review/21)
echo "== ootree =="
echo "script copy under ................... $W/a/b/c (its ROOT is not a checkout)"
echo "verdict/21 before confirm ........... $(ref_exists refs/heads/verdict/21 && echo exists || echo absent)"
out=$(cd "$W/seat" && HPO_BUS_STATE=$W/state HPO_IDENTITY_DIR=$W/ap bash "$W/a/b/c/bus.sh" confirm 21 "$R" 2>&1)
rc=$?
echo "confirm rc .......................... $rc"
echo "confirm output ...................... $out"
echo "poster calls ........................ $(calls)"
MOVED=no
ref_exists refs/heads/verdict/21 && MOVED=yes
echo "verdict/21 after confirm ............ $([ "$MOVED" = yes ] && echo exists || echo absent)"
[ -n "${BUS_RACE_KEEP:-}" ] || rm -rf "$W"
if [ "$MOVED" = no ] && [ "$(calls)" = 0 ]; then
  echo "verdict: nothing pushed, nothing posted -- the refusal lands before the push"
  exit 0
fi
echo "verdict: HALF-APPLIED -- the verdict ref moved ($MOVED) with $(calls) poster call(s)"
exit 1
