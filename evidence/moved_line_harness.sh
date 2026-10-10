#!/bin/bash
# REVIEWER'S OWN harness (not the fixer's). Drives the production function
# `moved_line` from a given prepr.sh over a throwaway repo, with the layout
# guard's real tests/layout.py + tests/layout.json copied in.
#
# Usage: moved_line_harness.sh <prepr.sh path> [label]
# Prints RESULT lines. rc 0 always (a harness reports, it does not gate).
set -u
PREPR="$1"
LABEL="${2:-head}"
WT=/Users/timmalmstrom/hpo-seats/r9-review-2072/head2
LR=$(mktemp -d "${TMPDIR:-/tmp}/mlh.XXXXXX")
trap 'rm -rf "$LR"' EXIT
# extract just the moved_line function
awk '/^moved_line\(\) \{/{p=1} p{print} p&&/^\}/{exit}' "$PREPR" > "$LR/moved_line.sh"
if ! grep -q 'python3 -I tests/layout.py --guard' "$LR/moved_line.sh"; then
  echo "NOTE: moved_line body mutated or not found in $PREPR"
fi
. "$LR/moved_line.sh"
mkdir -p "$LR/repo/tests" "$LR/repo/dev/audit/harnesses"
cp "$WT/tests/layout.py" "$WT/tests/layout.json" "$LR/repo/tests/"
echo "# h" > "$LR/repo/dev/audit/harnesses/seed.py"
lg() { git -C "$LR/repo" -c user.name=t -c user.email=t@t -c commit.gpgsign=false "$@"; }
( cd "$LR/repo" && lg init -q && lg checkout -q -b main && lg add -A && lg commit -qm base ) >/dev/null 2>&1
LB=$(lg rev-parse HEAD)

# ARM A (the defect): a branch adds a file under the RETIRED dir
RD=tools/audit; RD="$RD/harnesses"
lg checkout -q -b retired >/dev/null 2>&1
mkdir -p "$LR/repo/$RD"; echo "# h" > "$LR/repo/$RD/new.py"
lg add -A >/dev/null 2>&1; lg commit -qm retired >/dev/null 2>&1
outA=$(moved_line "$LR/repo" "$LB"); rA=$?
echo "RESULT [$LABEL] armA_retired_dir rc=$rA (want 1) :: $(printf '%s' "$outA" | head -c 200)"

# ARM B (null control): the SAME file at the NEW home
lg checkout -q main >/dev/null 2>&1; lg checkout -q -b clean >/dev/null 2>&1
echo "# h" > "$LR/repo/dev/audit/harnesses/new.py"
lg add -A >/dev/null 2>&1; lg commit -qm clean >/dev/null 2>&1
outB=$(moved_line "$LR/repo" "$LB"); rB=$?
echo "RESULT [$LABEL] armB_new_home rc=$rB (want 0) :: $(printf '%s' "$outB" | head -c 120)"

# ARM C: a line CITING the retired path (new-reference)
lg checkout -q main >/dev/null 2>&1; lg checkout -q -b cite >/dev/null 2>&1
printf '# see %s/x.py\n' "$RD" >> "$LR/repo/dev/audit/harnesses/seed.py"
lg add -A >/dev/null 2>&1; lg commit -qm cite >/dev/null 2>&1
outC=$(moved_line "$LR/repo" "$LB"); rC=$?
echo "RESULT [$LABEL] armC_retired_citation rc=$rC (want 1) :: $(printf '%s' "$outC" | head -c 200)"

# ARM D: a tree with no tests/layout.py -> skip rc 3
rm -f "$LR/repo/tests/layout.py"
outD=$(moved_line "$LR/repo" "$LB"); rD=$?
echo "RESULT [$LABEL] armD_no_guard rc=$rD (want 3) :: $(printf '%s' "$outD" | head -c 120)"
