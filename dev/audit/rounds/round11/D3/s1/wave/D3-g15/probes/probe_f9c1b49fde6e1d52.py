#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' outputs (max_temp, lp_max_temp, runup_temps) differ between
#   baseline and mutant: count of inputs that differ, over the cycle step, cooling rate, everyday limit, the
#   combi store and an everyday limit BELOW the 20 C room ambient (the only case where the coast-down could stay
#   above the limit forever).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f9c1b49fde6e1d52.py
# EXPECTED RESULT inputs_tried=147 count  moved=0 count  coast_steps_written_baseline=3375 count = mutant (lp entries above everyday)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 807
#   `if temp <= everyday:` (its `break`).
# Perturbation: key f9c1b49fde6e1d52 (GUARD_OFF) -> `if False:`, in memory (method recompiled, mock.patch.object).
#   Direction: none expected: once temp <= everyday, max(lp_max_temp[m], temp) keeps lp_max_temp[m] (= everyday
#   after the cycle step), and the recursion decays monotonically toward the room ambient, so the break only
#   saves iterations.
# Null control: the baseline itself on the same inputs (identity of both arms is the claim).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if temp <= everyday:", "if False:")
moved = tried = 0
cb = cm = 0
for setpoint in (15.0, 40.0, 55.0, 59.0):
    for rate in (0.05, 0.3, 3.0):
        p = c.params(dhw_setpoint=setpoint, dhw_cooling_rate=rate)
        for n, dt in ((96, 0.25), (192, 0.25), (24, 1.0)):
            h = c.horizon(n=n, dt=dt)
            for step in (0, n // 2, n - 2, n - 1):
                b, m = c.ceilings(p, h, step=step), c.ceilings(p, h, step=step, fn=fn)
                tried += 1
                moved += c.differs(b, m)
                E = float(p.dhw_store.charge_max_temp)
                cb += sum(1 for x in b[1][step + 1:] if x > E)
                cm += sum(1 for x in m[1][step + 1:] if x > E)
# combi store (the buffer's capacity and loss)
from custom_components.heatpump_optimizer import mixing_valve as mv  # noqa: E402
pc = c.params(dhw_combi_tank_enabled=True, mixing_valve_mode=sorted(mv.THROTTLING_MODES)[0], buffer_tank_volume=300.0)
assert pc.dhw_store.combi, "combi store not active"
if True:
    h = c.horizon(n=96)
    for step in (10, 48, 90):
        tried += 1
        moved += c.differs(c.ceilings(pc, h, step=step), c.ceilings(pc, h, step=step, fn=fn))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved={moved} count")
print(f"RESULT coast_steps_written_baseline={cb} count  mutant={cm} count")
c.footer()
