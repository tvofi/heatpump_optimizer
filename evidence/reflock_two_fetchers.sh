#!/bin/bash
# Two REAL concurrent fetches of one remote-tracking ref in one ref store.
# Fetch A holds refs/remotes/origin/main.lock for 3 s (a reference-transaction
# hook sleeps in its "prepared" state, i.e. while the lock is held), then
# commits the new value. Fetch B starts 1 s later.
#   arm "beat env": B carries the note's GIT_CONFIG_COUNT=2 lock timeouts.
#   arm "null"    : B carries no timeout (today).
# A third arm is the note's own fixture: the lock is freed with the ref unchanged.
set -u
d=$(mktemp -d); cd "$d"
git init -q -b main up && git -C up commit -q --allow-empty -m a && git clone -q up c
printf '#!/bin/sh\n[ "$1" = prepared ] && [ -n "${SLOW:-}" ] && sleep 3\nexit 0\n' > c/.git/hooks/reference-transaction
chmod +x c/.git/hooks/reference-transaction
T=(GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.filesRefLockTimeout GIT_CONFIG_VALUE_0=30000 GIT_CONFIG_KEY_1=core.packedRefsTimeout GIT_CONFIG_VALUE_1=30000)
race() { # $1 label, $2 env-for-B (beat|none)
  git -C up commit -q --allow-empty -m "$1"
  ( SLOW=1 git -C c fetch origin >A.out 2>&1; echo "A rc=$?" >>A.out ) &
  sleep 1
  if [ "$2" = beat ]; then ( env "${T[@]}" git -C c fetch origin >B.out 2>&1; echo "B rc=$?" >>B.out ) &
  else ( git -C c fetch origin >B.out 2>&1; echo "B rc=$?" >>B.out ) & fi
  wait; echo "== $1"; grep -E 'rc=|cannot lock|->' A.out B.out | sed 's/Unable to create.*/Unable to create <lock>: File exists./'
}
git --version
race "two fetchers, B with the beat's env" beat
race "two fetchers, B without it (null)" none
echo "== the note's fixture (a)6: lock freed at 1 s, ref unchanged, B with the beat's env"
git -C up commit -q --allow-empty -m f; touch c/.git/refs/remotes/origin/main.lock; ( sleep 1; rm -f c/.git/refs/remotes/origin/main.lock ) &
env "${T[@]}" git -C c fetch -q origin; echo "B rc=$?"; wait
rm -rf "$d"
# Appended: the same two-fetcher race, B retried once after its rc 1 (a candidate fix, not the note's).
d=$(mktemp -d); cd "$d"
git init -q -b main up && git -C up commit -q --allow-empty -m a && git clone -q up c
printf '#!/bin/sh\n[ "$1" = prepared ] && [ -n "${SLOW:-}" ] && sleep 3\nexit 0\n' > c/.git/hooks/reference-transaction; chmod +x c/.git/hooks/reference-transaction
git -C up commit -q --allow-empty -m r
( SLOW=1 git -C c fetch -q origin ) & sleep 1
git -C c fetch -q origin 2>/dev/null; r1=$?; wait; git -C c fetch -q origin; echo "== retry-once arm: B first rc=$r1, retry rc=$?, origin/main=$(git -C c rev-parse --short origin/main) up=$(git -C up rev-parse --short main)"
rm -rf "$d"
