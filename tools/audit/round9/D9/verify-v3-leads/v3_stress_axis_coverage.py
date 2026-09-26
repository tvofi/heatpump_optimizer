"""V3 independent check for D9-s2-71: does tests/stress.py's sweep vary topology_layout at all,
independent of the finder's harness (which only counts mixing_valve_mode via is_throttling)?
Uses the same sentinel trick as the finder's harness (raise before optimize() actually solves)
to make this cheap.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D9/verify-v3-leads/v3_stress_axis_coverage.py
"""
import sys
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import stress  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402


class _Stop(Exception):
    pass


def sentinel(self, *a, **k):
    raise _Stop((self.model.params.mixing_valve_mode, getattr(self.model.params, "topology_layout", "<none>")))


om.HeatPumpOptimizer.optimize = sentinel
combos = stress.sweep_combinations()
valve_modes = set()
topology_layouts = set()
seen = 0
for spec in combos:
    try:
        stress.build_case(**{k: v for k, v in spec.items() if k != "label"})
    except _Stop as e:
        seen += 1
        vm, tl = e.args[0]
        valve_modes.add(vm)
        topology_layouts.add(tl)

print(f"RESULT n_cases={len(combos)} seen={seen}")
print(f"RESULT mixing_valve_mode values seen across the sweep = {sorted(str(v) for v in valve_modes)}")
print(f"RESULT topology_layout values seen across the sweep = {sorted(str(v) for v in topology_layouts)}")
print(f"RESULT topology_layout axis varies = {len(topology_layouts) > 1}")
