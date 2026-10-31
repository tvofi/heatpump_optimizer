#!/bin/sh
# R10-CI-LAYOUT P2b, unit U0c: the design's static null control
# (DESIGN-P2 section 10) over ci.yml and gate-sweep.yml, with their closed maps.
#   sh dev/audit/harnesses/r10_ci_layout_u0c/unitcheck.sh [BASE]   (BASE default: origin/main)
# BEFORE is BASE's ci.yml (PR 0's stub) and, for gate-sweep.yml, which BASE
# lacks, an empty document: both are mapped as new files. The instrument is
# read from the design's archived ref, never copied. Prints the STATIC line
# for each head file (want rc 0) and for three plants. A file mapped as new
# has every row `gained`, so the instrument refuses only an UNMAPPED gain: a
# job added reads rc 1, while a gained row deleted (gate's checkout) and a
# caller's `with:` changed (a key unitcheck2 does not hash) both read rc 0.
# Those two blind lines are the instrument's limit on this unit, measured;
# tests/entities.py's umbrella pin is the control that refuses both.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_u0c
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:.github/workflows/ci.yml" > "$D/ci_before.yml" || exit 2
echo '{}' > "$D/empty.yml"
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "ci.yml head:        $(U "$D/ci_before.yml" .github/workflows/ci.yml --map "$H/ci_map.json")"
echo "gate-sweep.yml head: $(U "$D/empty.yml" .github/workflows/gate-sweep.yml --map "$H/sweep_map.json")"
python3 -I - .github/workflows/ci.yml "$D" <<'PY'
import sys
s = open(sys.argv[1]).read()
i = s.index("  gate:\n")
k = "      - uses: actions/checkout@"
j = s.index(k, i); e = s.index("      - name: ", j)
open(sys.argv[2] + "/p1.yml", "w").write(s[:j] + s[e:])
k = "      head: ${{ needs.prelude.outputs.head }}\n    permissions:\n      contents: read\n  arch-score:"
assert s.count(k) == 1
open(sys.argv[2] + "/p2.yml", "w").write(s.replace(k, k.replace("outputs.head", "outputs.base"), 1))
k = "  # <<< units\n"
open(sys.argv[2] + "/p0.yml", "w").write(s.replace(k, "  extra:\n    runs-on: ubuntu-latest\n    steps:\n      - run: \"true\"\n" + k, 1))
PY
echo "plant, an unmapped job added (want rc 1): $(U "$D/ci_before.yml" "$D/p0.yml" --map "$H/ci_map.json")"
echo "plant, gate's checkout deleted (blind, reads rc 0): $(U "$D/ci_before.yml" "$D/p1.yml" --map "$H/ci_map.json")"
echo "plant, a caller's with: changed (blind, reads rc 0): $(U "$D/ci_before.yml" "$D/p2.yml" --map "$H/ci_map.json")"
