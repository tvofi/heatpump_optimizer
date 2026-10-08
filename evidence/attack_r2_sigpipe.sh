#!/bin/bash
# review-2069 round 2: the PRODUCTION recarry_verdict (extracted from the given
# app_push.sh) under app_push.sh's own `set -uo pipefail`, against a local clone
# of the real repository (real first-parent history length), honest recarry.
set -uo pipefail
SELF=${1:?app_push.sh}; SRC=${2:?repo}
R=$(mktemp -d "${TMPDIR:-/tmp}/rv2069b.XXXXXX")
G() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -c user.name=t -c user.email=t@example.test "$@" >/dev/null 2>&1; }
eval "$(sed -n '/^recarry_verdict() {/,/^}/p' "$SELF")"
G clone -q --branch main "$SRC" "$R/wt" || { echo "clone failed"; exit 2; }
cd "$R/wt"
echo "first-parent commits on origin/main: $(git rev-list --first-parent origin/main | wc -l | tr -d ' ')"
G checkout -q -b fix "$(git rev-list --first-parent origin/main | sed -n 6p)"
printf 'f\n' > recarry-probe.txt; G add recarry-probe.txt; G commit -qm fix
LIVE=$(git rev-parse HEAD)
G merge -q --no-edit origin/main
printf 'b\n' > "$R/body.md"
L=$(python3 -c 'import json,sys; print(json.dumps([{"number":7,"head":{"sha":sys.argv[1]},"body":"b"}]))' "$LIVE")
for i in 1 2 3; do
  out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" "$L" "$R/body.md"); rc=$?
  echo "RESULT run=$i honest-recarry-real-history pipefail=on rc=$rc verdict=$out"
done
set +o pipefail
out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" "$L" "$R/body.md"); rc=$?
echo "RESULT control pipefail=off rc=$rc verdict=$out"
cd /; rm -rf "$R"
