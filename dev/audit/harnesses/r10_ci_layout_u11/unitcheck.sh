#!/bin/sh
# unitcheck2.py static for P2b unit u11 (kernel-points.yml) against BASE (default origin/main),
# under this directory's map; plus the no-map plant, which must read rc 1.
# Instrument read from the approved design tag, never copied. Integration seat, P2b step 10.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_u11
W=.github/workflows/kernel-points.yml
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:$W" > "$D/before.yml" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "kernel-points.yml head:            $(U "$D/before.yml" $W --map $H/map.json)"
echo "plant, no map (want rc 1):  $(U "$D/before.yml" $W)"
