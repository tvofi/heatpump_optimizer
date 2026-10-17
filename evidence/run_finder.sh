#!/bin/bash
# run_finder.sh <repo-root> <tag>  -- the round-1 reviewer's arm.py, driven with
# its own plants.py as ARM_EXTRA (the finder's harness), and bare (no ARM_EXTRA).
ROOT="$1"; TAG="$2"
cd "$ROOT" || exit 99
EV=/private/tmp/rev-2344-ev
echo "### $TAG root=$ROOT head=$(git rev-parse HEAD)"
echo "--- bare (no ARM_EXTRA): the arm's own checks ---"
python3 "$EV/finder_arm.py" 2>&1 | tail -8
echo "--- with the round-1 plants.py as ARM_EXTRA ---"
ARM_EXTRA="$(cat "$EV/finder_plants.py")" python3 "$EV/finder_arm.py" 2>&1 | tail -25
