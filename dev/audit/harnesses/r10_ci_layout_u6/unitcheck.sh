#!/bin/sh
# R10-CI-LAYOUT P2b, unit U6: the design's static null control (DESIGN-P2
# section 10) over pr-contract.yml, with its closed map.
#   sh dev/audit/harnesses/r10_ci_layout_u6/unitcheck.sh [BASE]   (BASE default: origin/main)
# BEFORE is BASE's pr-contract.yml. The instrument is read from the design's
# archived ref, never copied. Prints the STATIC line for the head file under
# the map (want rc 0), for the same pair without it (want rc 1: the edits are
# real), and for three plants. The two blind lines are the instrument's limit,
# measured: a row the map admits as `changed` or `gained` is not compared past
# its being admitted, so a step gutted under an admitted key, or a gained step
# deleted, reads rc 0. tests/entities.py's
# red-filter, wait-step and callee pins are the controls that refuse those.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
F=.github/workflows/pr-contract.yml
M=dev/audit/harnesses/r10_ci_layout_u6/pc_map.json
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:$F" > "$D/before.yml" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "head, under the map (want rc 0):     $(U "$D/before.yml" "$F" --map "$M")"
echo "head, no map (want rc 1):            $(U "$D/before.yml" "$F")"
python3 -I - "$F" "$D" <<'PY'
import sys
s = open(sys.argv[1]).read()
k = "      - name: Wait for code scanning and list its open alerts\n"
i = s.index(k)
e = s.index("      # #956:", i)
open(sys.argv[2] + "/p0.yml", "w").write(s[:i] + s[e:])
k = '                   | select(.name != "gate")\n'
assert s.count(k) == 1
open(sys.argv[2] + "/p1.yml", "w").write(s.replace(k, "", 1))
k = "      - name: Every figure's command resolves at this head\n"
j = s.index(k)
open(sys.argv[2] + "/p2.yml", "w").write(s[:j] + '      - name: Extra\n        run: "true"\n\n' + s[j:])
PY
echo "plant, the wait step deleted (blind, rc 0):        $(U "$D/before.yml" "$D/p0.yml" --map "$M")"
echo "plant, the gate exclusion deleted (blind, rc 0):  $(U "$D/before.yml" "$D/p1.yml" --map "$M")"
echo "plant, an unmapped step added (want rc 1):       $(U "$D/before.yml" "$D/p2.yml" --map "$M")"
