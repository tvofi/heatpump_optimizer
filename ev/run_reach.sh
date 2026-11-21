#!/bin/bash
# run_reach.sh: the reach block at the red commit, the fix, and the round-5 head; then the mutant.
cd $HOME/hpo-orch/r10s6/r11/fix3729-r6 || exit 1
E=$HOME/hpo-seats/r11/fix3729-r6/ev
PY=$HOME/hpo-orch/r10s6/venv-ci/bin/python
for c in 148254e8 c790dc5372 1a2240cfc3; do git show "${c}:tests/entities.py" > "$E/ent-${c}.py"; done
echo "== fix 1a2240cf"; "$PY" "$E/reach.py" "$E/ent-1a2240cfc3.py" 2>&1 | cut -c1-400
echo "== red c790dc53"; "$PY" "$E/reach.py" "$E/ent-c790dc5372.py" 2>&1 | cut -c1-2500
echo "== mutant: fix's tests, round-5 function"; "$PY" "$E/reach.py" "$E/ent-1a2240cfc3.py" "$E/ent-148254e8.py" 2>&1 | cut -c1-2500
