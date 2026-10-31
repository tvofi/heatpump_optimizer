#!/bin/bash
# R10-FLY-ENVMATRIX-NOREMOTE: run governance.yml's env-matrix job in CI's shape
# at a pull-request head, and print the matrix's own report.
#   bash dev/audit/harnesses/r10_envmatrix_noremote.sh <head> <base> [--no-live]
# CI's shape: a full clone detached at <head>, origin/main at <base>, the job's
# own "Restore the check source" step (read from governance.yml at <head>) run
# with PINNED=<base> and committed, then the driver that checkout holds.
# --no-live puts a `gh` that always fails first on PATH, so the one live input
# the arms read (counts.mjs liveRequiredContexts, via `gh api`) is unreachable
# and its class skips. That is the null control for a live-ruleset cause: with
# the input withdrawn, the no-remote rows hold or fail on the shape alone.
# Needs python3 with PyYAML, node and git. Exits with the driver's status.
set -uo pipefail
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
HEAD_SHA=$(git rev-parse --verify "${1:?head}^{commit}") || exit 2
BASE_SHA=$(git rev-parse --verify "${2:?base}^{commit}") || exit 2
LIVE=1; [ "${3:-}" = --no-live ] && LIVE=0
. tests/throwaway_git.sh
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
throwaway_git_clone -q "$PWD" "$T/src" || exit 2
(
  throwaway_git_env
  cd "$T/src" || exit 2
  git checkout -q --detach "$HEAD_SHA" || exit 2
  git update-ref refs/remotes/origin/main "$BASE_SHA"
  git show "$HEAD_SHA:.github/workflows/governance.yml" | python3 -c '
import sys, yaml
for s in yaml.safe_load(sys.stdin)["jobs"]["env-matrix"]["steps"]:
    if s.get("name", "").startswith("Restore the check source"): print(s["run"])
' > "$T/restore.sh"
  test -s "$T/restore.sh" || { echo "no restore step in env-matrix at $HEAD_SHA"; exit 2; }
  RUNNER_TEMP=$T PINNED=$BASE_SHA bash -e "$T/restore.sh" || exit 2
) || exit 2
if [ "$LIVE" = 0 ]; then
  mkdir -p "$T/bin"; printf '#!/bin/sh\necho "gh: withdrawn by --no-live" >&2\nexit 1\n' > "$T/bin/gh"
  chmod +x "$T/bin/gh"; PATH="$T/bin:$PATH"
fi
echo "head $HEAD_SHA base $BASE_SHA live=$LIVE"
cd "$T/src" && node tools/policy/policy_lint_envmatrix.mjs "$PWD" "$T/envmatrix" "$(git rev-parse HEAD)"
