#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' outputs differ between baseline and mutant when the walk's first
#   `need` lands EXACTLY on the everyday charge limit (the `need > everyday` boundary): count of searched inputs
#   that are exact ties, and of inputs whose two arms differ.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_1d455987c970dfde.py
# EXPECTED RESULT tie_hits=374 count (30 in-range configurations, draw bisected +-50 floats)  moved_under_tie=0  moved_near_tie=0
# EXPECTED RESULT moved_random=0 count  (60 seeded random draws and cycle steps)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 790
#   `if need > everyday:` (then `max_temp[m] = min(boost_top, need)`).
# Perturbation: key 1d455987c970dfde (CMP_BOUND) -> `if need >= everyday:`, in memory (method recompiled,
#   mock.patch.object). Direction: none expected: at need == everyday the mutant writes min(boost_top, everyday)
#   = everyday into a ceiling that already holds everyday (each m is visited once, max_temp starts at everyday).
# Null control: the random draws off the tie, identical by construction.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if need > everyday:", "if need >= everyday:")
hits = moved = tried = mt = 0
cfgs = []
for rate in (0.05, 0.1, 0.3, 1.0, 3.0):
    for out in (-10.0, 0.0, 7.0):
        for pr in (2.0, 4.0):
            p = c.params(dhw_cooling_rate=rate)
            h = c.horizon(n=96, outdoor=np.full(96, out))
            E = float(p.dhw_store.charge_max_temp)
            r = c.walk_tie(p, h, 40, E, fn, k=50, p_run=pr)
            hits, moved, tried, mt = hits + r[0], moved + r[1], tried + r[2], mt + r[3]
            cfgs.append(f"{rate}/{out}/{pr}:{r[0]}")
print(f"RESULT everyday={E} C")
print(f"RESULT configs_tried={len(cfgs)} count (cooling C/h / outdoor C / DHW run kW : ties)")
print(f"RESULT tie_inputs_tried={tried} count")
print(f"RESULT tie_hits={hits} count")
print(f"RESULT moved_near_tie={moved} count")
print(f"RESULT moved_under_tie={mt} count")
p = c.params()
h = c.horizon(n=96)
rng = np.random.default_rng(790)
mr = 0
for _ in range(60):
    dr = rng.uniform(0.0, 6.0, 96)
    step = int(rng.integers(1, 96))
    mr += c.differs(c.ceilings(p, h, step=step, draw=dr), c.ceilings(p, h, step=step, draw=dr, fn=fn))
print(f"RESULT moved_random={mr} count")
c.footer()
