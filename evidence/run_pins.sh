#!/bin/bash
# Re-drive every pin PR #2873 adds, each with the driver its ledger row names.
# Run from the PR head worktree. One job, so the tree clone fits the disk.
set -u
cd /Users/timmalmstrom/hpo-seats/r10s6/review-2873-r1/wt || exit 1
OUT=/Users/timmalmstrom/hpo-seats/r10s6/review-2873-r1/evidence
mkdir -p "$OUT/mutants"
export PYTHONDONTWRITEBYTECODE=1
for f in $(git diff --name-only 524c1896b...HEAD -- tests/mutation_ledger/); do
  row=$(basename "$f" .json)
  anchor=$(python3 -c "import json;print(json.load(open('$f'))['anchor'])")
  driver=$(python3 -c "import json;print(json.load(open('$f'))['killed_by'])")
  safe=$(echo "$row.$driver" | tr -c 'A-Za-z0-9._-' '_')
  echo "===== $row  [$anchor]  driver=$driver"
  python3 tests/mutation_table.py --anchor "$anchor" --scripts "$driver" --jobs 1 \
    > "$OUT/mutants/$safe.log" 2>&1
  rc=$?
  echo "rc=$rc"
  grep -E "PIN RE-VERIFICATION|killed by|survived|SURVIVED|baseline .*rc=|NOT REPRODUCED" \
    "$OUT/mutants/$safe.log" | tail -6
done
echo "DONE"
