"""Design probe for R10-COP-GATE part D (the learned top reaching the plan).

Run: PYTHONPATH=tests/hastub:. python3 dev/programme/designs/R10-COP-GATE-D-probes/band_probe.py
from a worktree at the code under test. Reads production code; modifies nothing.

P1  the hub re-key: DrawRange keys its window and latch on the configured
    (min, max) the fold is handed; a learned top written into the hub that
    feeds the fold clears the window on the next fold.
P2  the arbiter band: flow_setpoint_for_level maps the plan's top step to the
    ceiling only when the band it maps against has the same top.
P3  the reader gap: planned_range and the diagnostics' effective_max_kw stay
    None for a window holding twelve ceiling-written samples (carry 12).
"""
from custom_components.heatpump_optimizer.draw_range import DrawRange, planned_range, diagnostics_view
from custom_components.heatpump_optimizer.thermal_model import flow_setpoint_for_level

CFG = (1.0, 5.0)
REAL_MAX = 3.0
HEAT_C, FLOOR_C = 55.0, 30.0


class Cap:
    def plan_writes_power(self):
        return False

    def can_duty_cycle(self):
        return True


class Params:
    def __init__(self, lo, hi):
        self.min_electrical_power, self.max_electrical_power = lo, hi


print("## P1 hub re-key")
d = DrawRange()
for _ in range(60):
    d.observe(1.5, 1.5, *CFG, None)
print(f"  configured key {CFG}: samples={len(d.samples)}")
d.observe(1.5, 1.5, CFG[0], REAL_MAX, None)
print(f"  one fold keyed on the learned top (1.0, {REAL_MAX}): samples={len(d.samples)} config={d.config}")
null = DrawRange()
for _ in range(61):
    null.observe(1.5, 1.5, *CFG, None)
print(f"  null, 61 folds all keyed on the configured figures: samples={len(null.samples)}")

print("## P2 arbiter band")
for label, band in (("configured band (1.0, 5.0)", CFG), (f"solve band (1.0, {REAL_MAX})", (CFG[0], REAL_MAX))):
    sp = flow_setpoint_for_level(REAL_MAX, band[0], band[1], HEAT_C, FLOOR_C)
    print(f"  plan step {REAL_MAX} kW mapped on {label}: {sp:.2f} degC (ceiling {HEAT_C})")
sp = flow_setpoint_for_level(CFG[1], *CFG, HEAT_C, FLOOR_C)
print(f"  null, plan step {CFG[1]} kW on the configured band: {sp:.2f} degC")

print("## P3 reader gap")
for n in (11, 12):
    d = DrawRange()
    for _ in range(288):
        d.observe(1.5, 1.5, *CFG, (40.0, HEAT_C))
    for _ in range(n):
        d.observe(REAL_MAX, CFG[1], *CFG, (HEAT_C, HEAT_C))
    v = diagnostics_view(d, Params(*CFG), Cap())
    print(f"  {n} ceiling samples in the window: observed={d.observed()} planned_range={planned_range(d, Params(*CFG), Cap())} "
          f"effective_max_kw={v['effective_max_kw']}")
