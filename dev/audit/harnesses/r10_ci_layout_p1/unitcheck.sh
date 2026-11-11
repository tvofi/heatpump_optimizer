#!/bin/sh
# R10-CI-LAYOUT PR 1: the design's static null control (DESIGN-P1 section 4)
# over this tree, with its closed map, and a planted control.
#   sh dev/audit/harnesses/r10_ci_layout_p1/unitcheck.sh [BASE]   (BASE default: origin/main)
# BEFORE is BASE's tests.yml; AFTER is tests.yml+nightly.yml+the nightly-ha
# composite action in the working tree. The instrument is read from the
# design's archived ref, never copied. Prints the instrument's STATIC line for
# the head (want rc 0) and for one plant -- a step deleted from nightly.yml's
# record-autofix, which a verbatim move must keep (want rc 1).
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:.github/workflows/tests.yml" > "$D/before.yml" || exit 2
MAP=dev/audit/harnesses/r10_ci_layout_p1/unitcheck_map.json
AFTER=.github/workflows/tests.yml+.github/workflows/nightly.yml+.github/actions/nightly-ha/action.yml
python3 -I "$D/unitcheck2.py" static "$D/before.yml" "$AFTER" --map "$MAP" > "$D/head.txt" 2>&1
echo "head:  $(tail -1 "$D/head.txt")"
mkdir -p "$D/w"
python3 -I - .github/workflows/nightly.yml "$D/w/nightly.yml" <<'PY'
import sys
s = open(sys.argv[1]).read()
k = "      - name: Enumerate the window's merges\n"
assert s.count(k) == 1
i = s.index(k); j = s.index("      - name: ", i + len(k))
open(sys.argv[2], "w").write(s[:i] + s[j:])
PY
python3 -I "$D/unitcheck2.py" static "$D/before.yml" \
  ".github/workflows/tests.yml+$D/w/nightly.yml+.github/actions/nightly-ha/action.yml" \
  --map "$MAP" > "$D/plant.txt" 2>&1
echo "plant: $(tail -1 "$D/plant.txt")  ($(grep -c 'LOST' "$D/plant.txt") LOST row(s))"
