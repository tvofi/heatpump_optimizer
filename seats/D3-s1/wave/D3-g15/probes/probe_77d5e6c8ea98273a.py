#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' outputs differ between baseline and mutant (count of inputs),
#   the tank decay (_tank_decay: clip(1 - UA*dt/C, 0, 1)) at which they separate, and the smallest decay a
#   production configuration can produce (separate tank: cooling rate clipped to DHW_COOLING_RATE_MAX; combi
#   store: buffer_cooling_rate_bounds' upper rate) at the longest step the integration plans with.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_77d5e6c8ea98273a.py
# EXPECTED RESULT moved_in_range=0 count  (cooling rate 0.05 / 0.3 / 3.0 C/h at dt 0.25 and 1.0 h, draws 0 and heavy)
# EXPECTED RESULT decay0_baseline=returned (run-up min -2.44e+08)  decay0_mutant=raises ZeroDivisionError (dt 9 h, rate 3 C/h:
#   UA*dt/C = 1.08 -> decay 0.0, the separating input)
# EXPECTED RESULT reach_min_decay_tank_dt1h=0.88  reach_min_decay_combi_dt1h=0.8077 (decay 0 needs UA*dt/C >= 1)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 783
#   `need = (need + drawn - gain - rise) / max(decay, 1e-6)`.
# Perturbation: key 77d5e6c8ea98273a (CLAMP_DROP) -> `/ (decay)`, in memory (method recompiled, mock.patch.object).
#   Direction: identical while decay >= 1e-6; at decay 0 the baseline's huge need breaks the walk, the mutant
#   divides a Python float by zero.
# Null control: every in-range decay (>= 0.88 here), identical arrays.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "need = (need + drawn - gain - rise) / max(decay, 1e-6)",
              "need = (need + drawn - gain - rise) / (decay)")
moved = tried = 0
for rate in (0.05, 0.3, 3.0):
    p = c.params(dhw_cooling_rate=rate)
    for dt, n in ((0.25, 96), (1.0, 24)):
        h = c.horizon(n=n, dt=dt)
        for draw in (np.zeros(n), np.full(n, 3.0)):
            for step in (n // 2, n - 1):
                tried += 1
                moved += c.differs(c.ceilings(p, h, step=step, draw=draw), c.ceilings(p, h, step=step, draw=draw, fn=fn))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_in_range={moved} count")
p = c.params(dhw_cooling_rate=3.0)
h = c.horizon(n=4, dt=9.0)
st = p.dhw_store
decay, _gain = c.dp._tank_decay(st.ua_kw_per_c, 9.0, st.capacity_kwh_per_c)
b, m = c.ceilings(p, h, step=3), c.ceilings(p, h, step=3, fn=fn)
print(f"RESULT decay_at_dt9h_rate3={decay}")
print(f"RESULT decay0_baseline={'returned, run-up min %.3g' % min(b[2]) if isinstance(b, tuple) else b}")
print(f"RESULT decay0_mutant={m if isinstance(m, str) else 'returned'}")
# Reach: the smallest decay production parameters allow at dt = 1 h (the step is config time_step_minutes; 15 min default).
tank = 1.0 - const.DHW_COOLING_RATE_MAX * 1.0 / const.DHW_COOLING_REFERENCE_DELTA
combi = min(1.0 - const.buffer_cooling_rate_bounds(v)[1] * 1.0 / const.DHW_COOLING_REFERENCE_DELTA
            for v in (10.0, 20.0, 35.0, 50.0, 100.0, 300.0, 1000.0))
print(f"RESULT reach_min_decay_tank_dt1h={tank:.4f}")
print(f"RESULT reach_min_decay_combi_dt1h={combi:.4f}")
c.footer()
