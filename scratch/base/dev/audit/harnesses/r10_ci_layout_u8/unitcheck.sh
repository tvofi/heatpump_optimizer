#!/bin/sh
# R10-CI-LAYOUT P2b, unit U8: the design's static null control (DESIGN-P2
# section 10) over the called budget-raise-gate.yml, with its closed map, and
# the input control: every `with:` key ci.yml's caller passes is declared.
#   sh dev/audit/harnesses/r10_ci_layout_u8/unitcheck.sh [BASE]   (BASE default: origin/main)
# Prints the STATIC line (want rc 0), a plant where the map is withheld (want
# rc 1), the input control (want rc 0) and its plant, a deleted declaration
# (want rc 1). The instrument is read from the design's archived ref.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_u8
W=.github/workflows/budget-raise-gate.yml
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:$W" > "$D/before.yml" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "budget-raise-gate.yml head:           $(U "$D/before.yml" $W --map $H/map.json)"
echo "plant, no map (want rc 1):            $(U "$D/before.yml" $W)"
python3 -I - $W .github/workflows/ci.yml "$D" <<'PY'
import re, sys, yaml
callee, ci, d = sys.argv[1:4]
def undeclared(text):
    on = (lambda x: x.get(True, x.get("on")))(yaml.safe_load(open(callee).read() if text is None else text))
    caller = yaml.safe_load(open(ci).read())["jobs"]["budget-raise-gate"]
    return sorted(set(caller["with"]) - set(on["workflow_call"]["inputs"]))
head = open(callee).read()
cut = re.sub(r"      head:\n        type: string\n        default: \"\"\n", "", head)
a, b = undeclared(None), undeclared(cut)
print(f"input control, callee as it is:       undeclared={a} rc {1 if a else 0}")
print(f"plant, `head` declaration deleted:    undeclared={b} rc {1 if b else 0}")
PY
