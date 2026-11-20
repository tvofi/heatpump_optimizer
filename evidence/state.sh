#!/usr/bin/env bash
cd /Users/timmalmstrom/hpo-seats/r11/rev3736-r4
export HPO_STATE_DIR=/Users/timmalmstrom/hpo-orch/r10s6 PATH=/Users/timmalmstrom/.local/state/hpo/bin:/Users/timmalmstrom/.local/state/hpo/venv-ci/bin:/opt/homebrew/bin:$PATH
EV=/Users/timmalmstrom/hpo-seats/r11/rev3736-r4-ev
H=$(cat "$EV/HEAD.txt")
git fetch -q origin
git merge-tree --write-tree origin/main "$H" > "$EV/merge-tree.txt" 2>&1; echo "merge-tree rc=$?"; tail -5 "$EV/merge-tree.txt"
echo "main=$(git rev-parse origin/main) behind=$(git rev-list --count "$H"..origin/main)"
MB=$(git merge-base origin/main "$H")
for f in tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt; do
  echo "== $f"
  echo "head: $(git show "${H}:${f}" | grep claims-for)"
  echo "main: $(git show "origin/main:${f}" | grep claims-for)"
  echo "mb:   $(git show "${MB}:${f}" | grep claims-for)"
done
echo "VERSION head=$(git show "${H}:VERSION") main=$(git show origin/main:VERSION) mb=$(git show "${MB}:VERSION")"
git diff --stat "$MB" "$H" -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md
echo "untouched-check done"
