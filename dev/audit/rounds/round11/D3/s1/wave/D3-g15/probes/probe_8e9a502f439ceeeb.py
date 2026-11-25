#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' LP coast-down ceilings (lp_max_temp) differ between baseline
#   and mutant when the decaying post-cycle temperature lands EXACTLY on the everyday charge limit (the
#   `temp <= everyday` boundary): the everyday limit (dhw_setpoint -> charge_max_temp) is set to the exact coast-down
#   value at k = 1..8 steps after the cycle; count of ties whose arms differ.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_8e9a502f439ceeeb.py
# EXPECTED RESULT ties_exact=8 count  ties_moved=0 count  random_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 807
#   `if temp <= everyday:` (its `break`, then `lp_max_temp[m] = max(lp_max_temp[m], temp)`).
# Perturbation: key 8e9a502f439ceeeb (CMP_BOUND) -> `if temp < everyday:`, in memory (method recompiled,
#   mock.patch.object). Direction: none expected: at temp == everyday the mutant writes max(everyday, everyday)
#   into a ceiling that already holds everyday, and the next decay step (fixed point = room ambient 20 C, below
#   everyday) breaks.
# Null control: seeded random cycle steps and cooling rates off the tie.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if temp <= everyday:", "if temp < everyday:")
n, step = 96, 40
h = c.horizon(n=n)
ref = c.ceilings(c.params(dhw_setpoint=55.0), h, step=step)
exact = moved = 0
for k in range(1, 9):
    t = ref[1][step + k]  # coast-down temperature k steps after the cycle (independent of the everyday limit)
    p = c.params(dhw_setpoint=float(t))
    exact += float(p.dhw_store.charge_max_temp) == t
    moved += c.differs(c.ceilings(p, h, step=step), c.ceilings(p, h, step=step, fn=fn))
print(f"RESULT ties_exact={exact} count")
print(f"RESULT ties_moved={moved} count")
rng = np.random.default_rng(807)
rm = 0
for _ in range(40):
    p = c.params(dhw_cooling_rate=float(rng.uniform(0.05, 3.0)), dhw_setpoint=float(rng.uniform(45.0, 59.0)))
    s = int(rng.integers(0, n))
    rm += c.differs(c.ceilings(p, h, step=s), c.ceilings(p, h, step=s, fn=fn))
print(f"RESULT random_moved={rm} count")
c.footer()
