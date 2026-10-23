#!/bin/sh
# R10-CI-LAYOUT P2b, unit U4: the design's static null control (DESIGN-P2
# section 10) over the called governance.yml, with its closed map, and the
# input control: the caller passes no `with:` and no `secrets:`, so the callee
# must declare no input a caller can leave out.
#   sh dev/audit/harnesses/r10_ci_layout_u4/unitcheck.sh [BASE]   (BASE default: origin/main)
# Prints the STATIC line (want rc 0), a plant where the map is withheld (want
# rc 1), a plant that edits the `instrument-self-tests` step (want rc 1: plan
# section 8's move-PR silent revert), the input control (want rc 0) and its
# plant, a caller given a `with:` key the callee does not declare (want rc 1).
# The instrument is read from the design's archived ref.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_u4
W=.github/workflows/governance.yml
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:$W" > "$D/before.yml" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "governance.yml head:                  $(U "$D/before.yml" $W --map $H/map.json)"
echo "plant, no map (want rc 1):            $(U "$D/before.yml" $W)"
python3 -I - $W .github/workflows/ci.yml "$D" <<'PY'
import sys, yaml
callee, ci, d = sys.argv[1:4]
s = open(callee).read()
i = s.index("  instrument-self-tests:\n")
k = "        run: "
j = s.index(k, i)
open(d + "/p1.yml", "w").write(s[:j] + "        run: true #" + s[j + len(k):])
def undeclared(text, with_extra):
    on = (lambda x: x.get(True, x.get("on")))(yaml.safe_load(text))
    caller = yaml.safe_load(open(ci).read())["jobs"]["governance"]
    passed = set(caller.get("with", {})) | with_extra
    return sorted(passed - set((on["workflow_call"] or {}).get("inputs", {})))
a, b = undeclared(s, set()), undeclared(s, {"pr"})
print(f"input control, caller as it is:       undeclared={a} rc {1 if a else 0}")
print(f"plant, caller passes `pr`:            undeclared={b} rc {1 if b else 0}")
PY
echo "plant, instrument-self-tests edited (want rc 1): $(U "$D/before.yml" "$D/p1.yml" --map $H/map.json)"
