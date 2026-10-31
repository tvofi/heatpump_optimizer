"""Round-2 design probe for R10-COP-GATE part D (the band a plan is mapped by).

Run: PYTHONPATH=tests/hastub:. python3 dev/programme/designs/R10-COP-GATE-D-probes/band_probe_r2.py
from a worktree at the code under test. Reads production code; modifies nothing.

P4  the drift a recomputed band causes, both directions: a plan step mapped on
    a band other than the one it was solved on, at the twelfth probe sample
    (solved configured, mapped learned) and at lapse (solved learned, mapped
    configured).
P5  CEILING-PROBE item 2: an experiment's power mapped on the plan's learned
    band. A probe step at the configured top still writes the heat level; the
    fit's bisected step does not map the same on both bands.
"""
from custom_components.heatpump_optimizer.thermal_model import flow_setpoint_for_level

CFG = (1.0, 5.0)
LEARNED = (1.0, 3.0)
HEAT_C, FLOOR_C = 55.0, 30.0


def level(kw, band):
    return flow_setpoint_for_level(kw, band[0], band[1], HEAT_C, FLOOR_C)


print("## P4 recomputed band vs the plan's own band")
for label, solved, mapped in (
    ("twelfth sample (solved configured, mapped learned)", CFG, LEARNED),
    ("lapse (solved learned, mapped configured)", LEARNED, CFG),
):
    print(f"  {label}: 3.0 kW step on its own band {level(3.0, solved):.2f} degC, "
          f"on the recomputed band {level(3.0, mapped):.2f} degC")
print(f"  null, a band that did not change: {level(3.0, CFG):.2f} vs {level(3.0, CFG):.2f} degC")

print("## P5 experiment power on the plan's band")
print(f"  probe step at configured top 5.0 kW: learned band {level(5.0, LEARNED):.2f}, "
      f"configured band {level(5.0, CFG):.2f} degC")
print(f"  fit step 2.2583 kW (sysid sizer, F1): learned band {level(2.2583, LEARNED):.2f}, "
      f"configured band {level(2.2583, CFG):.2f} degC")
