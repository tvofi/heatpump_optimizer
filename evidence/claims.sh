#!/usr/bin/env bash
cd /Users/timmalmstrom/hpo-seats/r11/rev3736-r4
export PATH=/Users/timmalmstrom/.local/state/hpo/bin:/Users/timmalmstrom/.local/state/hpo/venv-ci/bin:/opt/homebrew/bin:$PATH
EV=/Users/timmalmstrom/hpo-seats/r11/rev3736-r4-ev
H=$(cat "$EV/HEAD.txt")
MB=$(git merge-base origin/main "$H")
T=$(head -1 "$EV/merge-tree.txt")
echo "== three-dot claim diff (branch's own)"
git diff "$MB...$H" -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
echo "== merged tree vs main, claim files"
git diff origin/main "$T" -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
echo "== env_drift --claims-only at head"
python3 tests/env_drift.py --claims-only > "$EV/env_drift-claims.log" 2>&1; echo "rc=$?"; tail -5 "$EV/env_drift-claims.log"
