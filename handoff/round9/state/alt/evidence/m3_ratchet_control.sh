#!/usr/bin/env bash
# M3 two-arm control: does tests/structure.py price private coordinator reads made OUTSIDE the class?
# Run inside a throwaway detached worktree at origin/main (31394964): it edits and restores source files.
set -u
F=custom_components/heatpump_optimizer
READS='(X._away_state, X._mode, X._thermal_model, X._entity_state, X._optimization_result, X._current_action)'
ins() { python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys
path, anchor, indent, reads = sys.argv[1:]
s = open(path).read(); i = s.index(anchor) + len(anchor)
s = s[:i] + f"{indent}if False:  # probe\n{indent}    _ = {reads}\n" + s[i:]
open(path, "w").write(s)
PY
}
echo "ARM A: six private coordinator reads inside pump_arbiter.state_for"
ins $F/pump_arbiter.py 'def state_for(coord: Any) -> ArbiterState:'$'\n' '    ' "${READS//X/coord}"
python3 tests/structure.py > /tmp/m3a.out 2>&1; echo "structure.py rc=$?"; grep -E "FAIL|IMPROVED" /tmp/m3a.out || echo "no metric moved"
git checkout -q -- $F
echo "ARM B (control): the same reads inside the coordinator's dhw-seam method _dhw_current_hour"
ins $F/coordinator.py '    def _dhw_current_hour(self) -> float:'$'\n' '        ' "${READS//X/self}"
python3 tests/structure.py > /tmp/m3b.out 2>&1; echo "structure.py rc=$?"; grep -E "FAIL|IMPROVED" /tmp/m3b.out
git checkout -q -- $F
