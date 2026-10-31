#!/bin/sh
# unitcheck2.py static for P2b unit u10 (merge-main.yml) against BASE (default origin/main),
# under this directory's map; plus the no-map plant, which must read rc 1.
# The three changed rows are the job's ref guard, the one ci.yml dispatch per
# branch, and the approve step reading the four-field pushed.txt line.
# pr-contract-rerun.yml is retired by this unit: the last line checks it is absent.
# Instrument read from the approved design tag, never copied. Integration seat, P2b step 10.
set -u
BASE=${1:-origin/main}
TAG=archive/probe/design-ci-rev4
H=dev/audit/harnesses/r10_ci_layout_u10
W=.github/workflows/merge-main.yml
D=$(mktemp -d "${TMPDIR:-/tmp}/hpo-unitcheck-XXXXXX")
trap 'rm -rf "$D"' EXIT
git show "$TAG:measure/rev/unitcheck2.py" > "$D/unitcheck2.py" || exit 2
git show "$BASE:$W" > "$D/before.yml" || exit 2
U() { python3 -I "$D/unitcheck2.py" static "$@" 2>&1 | tail -1; }
echo "merge-main.yml head:        $(U "$D/before.yml" $W --map $H/map.json)"
echo "plant, no map (want rc 1):  $(U "$D/before.yml" $W)"
if test -e .github/workflows/pr-contract-rerun.yml; then echo "pr-contract-rerun.yml: present (want absent)"; else echo "pr-contract-rerun.yml: absent"; fi
