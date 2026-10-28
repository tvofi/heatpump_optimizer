#!/bin/bash
# Two real concurrent fetches (design-verdict 810697a5a evidence/reflock_two_fetchers.sh),
# fetch B run through the shim, with and without the beat's lock-timeout env; null: no shim.
set -u
SH=$(cd "$(dirname "$0")/beatd_shims" && pwd)
T=(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.filesRefLockTimeout GIT_CONFIG_VALUE_0=30000)
one() { # $1 label, $2 shim|none, $3 env|noenv, $4 retries
  d=$(mktemp -d); cd "$d"
  git init -q -b main up && git -C up commit -q --allow-empty -m a && git clone -q up c
  printf '#!/bin/sh\n[ "$1" = prepared ] && [ -n "${SLOW:-}" ] && sleep 3\nexit 0\n' > c/.git/hooks/reference-transaction
  chmod +x c/.git/hooks/reference-transaction
  git -C up commit -q --allow-empty -m r
  ( SLOW=1 git -C c fetch -q origin ) & sleep 1
  p=$PATH; [ "$2" = shim ] && p=$SH:$PATH
  e=(); [ "$3" = env ] && e=("${T[@]}")
  env ${e[@]+"${e[@]}"} PATH="$p" HPO_GIT_RETRIES=$4 HPO_GIT_SHIM_LOG=$d/log git -C c fetch -q origin 2>/dev/null; rc=$?
  wait
  echo "$1: B rc=$rc origin/main=$(git -C c rev-parse --short origin/main) up=$(git -C up rev-parse --short main) retries=$(cat $d/log 2>/dev/null | wc -l)"
  cd /; rm -rf "$d"
}
git --version
one "fix: shim, no env"            shim noenv 2
one "fix: shim + lock-timeout env" shim env   2
one "null: no shim, no env"        none noenv 2
one "null: no shim, env (round 2)" none env   2
one "mutant: shim, retries=0"      shim noenv 0
one "mutant: shim, retries=0, env" shim env   0
