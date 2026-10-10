#!/bin/bash
# bus_fetchhead_race.sh -- the two bus.sh defects, measured on whatever bus.sh
# you name, so the red and the green are both reproducible without a worktree
# per round. (R9-RC-BUS-FETCHHEAD, 2026-10-09: #2071's round-4 reviewer's first
# push-verdict was built parented on main's tip, and #2074's confirm signed and
# pushed verdict/2074 (7c64dd213) and THEN failed at the post.)
#
#   bus_fetchhead_race.sh <path to bus.sh> race    # the intervening fetch
#   bus_fetchhead_race.sh <path to bus.sh> append  # the null control, no plant
#   bus_fetchhead_race.sh <path to bus.sh> ootree  # the out-of-tree copy
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

if [ "$MODE" = race ]; then
  # A git wrapper that plants the unrelated fetch inside the window: after the
  # script's own fetch of the bus ref returned, before it reads the tip back.
  mkdir -p "$W/shim"
  cat > "$W/shim/git" <<'S'
#!/bin/bash
if [ "${1:-}" = fetch ] && [ ! -e "$BUS_RACE_WINDOW" ]; then
  : > "$BUS_RACE_WINDOW"
  "$BUS_RACE_REAL_GIT" "$@"
  rc=$?
  "$BUS_RACE_REAL_GIT" -C "$PWD" fetch -q origin refs/heads/main >/dev/null 2>&1
  exit $rc
fi
exec "$BUS_RACE_REAL_GIT" "$@"
S
  chmod +x "$W/shim/git"
  export BUS_RACE_REAL_GIT=$REAL

  N=$(bus dispatch 21 "$H1" cmsg_race | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/v1.md"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$H1" "$N" > "$W/v2.md"
  out=$(bus push-verdict 21 "$W/v1.md" "$W/ev1") || { echo "round 1 failed: $out" >&2; exit 2; }
  A=$(tip refs/heads/review/21)
  [ -n "$A" ] || { echo "no review/21 after round 1" >&2; exit 2; }

  rm -f "$W/window"
  out=$(PATH="$W/shim:$PATH" BUS_RACE_WINDOW=$W/window bus push-verdict 21 "$W/v2.md" "$W/ev2")
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
