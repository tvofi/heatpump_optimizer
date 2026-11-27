#!/bin/bash
cd /tmp/hpo-rev-3869-delta || exit 1
for m in $(git rev-list --merges --first-parent 4ab51be4..HEAD); do
  p1=$(git rev-parse "$m^1"); p2=$(git rev-parse "$m^2")
  auto=$(git merge-tree --write-tree "$p1" "$p2" 2>/dev/null | head -1)
  real=$(git rev-parse "$m^{tree}")
  if [ "$auto" = "$real" ]; then echo "$m clean"; else echo "$m HAND:"; git diff --stat "$auto" "$real" | tail -5; fi
done
echo "merge into main:"; git merge-tree --write-tree origin/main HEAD >/dev/null; echo "rc $?"
echo "three-dot version files:"; git diff --stat "$(git merge-base origin/main HEAD)"...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json
python3 tests/structure.py 2>&1 | grep -E 'module_excess_loc|PASSED|FAIL' | head
