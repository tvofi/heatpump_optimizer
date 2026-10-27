#!/usr/bin/env bash
# R10-996-RUNNER-CLAIMS: the shape claim's real-capture controls, on this
# host. Three `env_drift.py --all` runs against BASE, each in a throwaway
# worktree with this checkout's tests/env_drift.py copied in and one claim
# line appended to tests/golden/claimed_drift.txt (scratch commits, never
# pushed; the worktree is removed on exit):
#
#   after   ARM + the shape claim                     -> rc=0, every mover SHAPED
#   narrow  ARM + the claim without dhw_reasons[*]    -> rc=1, the dhw leaves unclaimed
#   null    BASE + a comment-only production line     -> rc=1, the claim STALE
#           + the shape claim
#
#   bash dev/audit/harnesses/r10_shape_claim_controls.sh [ARM] [BASE] [OUT_DIR]
#
# ARM defaults to park/r10-arch-shapes-classifier's 996b54cf1 (the parked
# D8-s1-01 classifier arm) and BASE to its parent a1d56b66f. Each run's full
# output lands in OUT_DIR/<arm>.txt; one `RESULT <arm>_rc=<n>` line per run
# goes to stdout. Which fixtures move is this host's basin (numeric_probe and
# numpy_build are printed in each run's cache banner); the verdicts above are
# the claim's, on any host where the arm moves a reason leaf at all.
set -u
ROOT=$(git rev-parse --show-toplevel)
ARM=${1:-996b54cf15ea3c7693383165ae2f080d2e04971b}
BASE=${2:-a1d56b66fb057e093d5ba2a6deee49d58d313dfa}
OUT=${3:-$(mktemp -d)}
mkdir -p "$OUT"
SHAPE="space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'"
CLAIM="shape: $SHAPE  # the classifier arm idles a share the plan runs no pump at"
NARROW="shape: space_reasons[*] * -> 'idle_coasting'|'idle'  # control: dhw leaves left out"
WT=$(mktemp -d)/controls
git -C "$ROOT" worktree add -q --detach "$WT" "$ARM" || exit 2
trap 'git -C "$ROOT" worktree remove --force "$WT"' EXIT
G="git -C $WT -c user.name=controls -c user.email=controls@invalid"

arm() { # name commit claim-line [extra-production-line]
  $G checkout -q --detach "$2" || return 2
  cp "$ROOT/tests/env_drift.py" "$WT/tests/env_drift.py"
  printf '%s\n' "$3" >> "$WT/tests/golden/claimed_drift.txt"
  [ -n "${4:-}" ] && printf '%s\n' "$4" >> "$WT/custom_components/heatpump_optimizer/optimizer.py"
  $G commit -qam "controls: $1" || return 2
  (cd "$WT" && PYTHONPATH=tests/hastub python3 tests/env_drift.py --all "$BASE") > "$OUT/$1.txt" 2>&1
  echo "RESULT $1_rc=$?"
}

arm after "$ARM" "$CLAIM"
arm narrow "$ARM" "$NARROW"
arm null "$BASE" "$CLAIM" "# controls: a comment moves no golden"
echo "outputs in $OUT"
