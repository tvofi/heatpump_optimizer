#!/usr/bin/env python3
# Metric: the run-up DhwPlanner._dhw_legionella_ceilings leaves when the walk's first `need` lands EXACTLY on the
#   boost top (the `need > boost_top` boundary): count of searched inputs whose two arms differ, and at a tie the
#   number of run-up steps set and the ceiling at the step before the cycle, baseline vs mutant.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_a1ebeff0870dfa76.py
# EXPECTED RESULT tie_hits=16 count  (draw at the cycle step bisected to the crossing, +-300 floats; 200 L tank, 55/60 C,
#   cooling 0.1 C/h, 4 kW DHW run power, 0 C outdoor -- every parameter in its configurable range)
# EXPECTED RESULT moved_under_tie=16 count, moved_near_tie=16 count  (every exact tie separates; no non-tie draw does)
# EXPECTED RESULT tie_runup_steps_baseline=6  tie_runup_steps_mutant=0; step-39 ceiling 60 vs 55 C, requirement 60 vs 20 C
# EXPECTED RESULT moved_random=0 count  (60 seeded random draw/price inputs off the tie)
# EXPECTED RESULT sweep_configs_with_ties=16/30 count  (cooling 0.05..3 C/h x outdoor -10/0/7 C x run 2/4 kW; every tie moves)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 784
#   `if need > boost_top:`.
# Perturbation: key a1ebeff0870dfa76 (CMP_BOUND) -> `if need >= boost_top:`, in memory (method recompiled,
#   mock.patch.object). Direction: at need == boost_top the baseline keeps walking (run-up and ceilings set
#   before the cycle), the mutant stops (no run-up at all).
# Null control: draws off the tie (seeded random), where both arms agree.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if need > boost_top:", "if need >= boost_top:")
p = c.params(dhw_cooling_rate=0.1)  # in range: DHW_COOLING_RATE_MIN 0.05 .. MAX 3.0 C/h
h = c.horizon(n=96)
B = min(70.0, float(p.dhw_store.rating_max_temp))
hits, moved, tried, mt, sample = c.walk_tie(p, h, 40, B, fn)
print(f"RESULT boost_top={B} C")
print(f"RESULT tie_inputs_tried={tried} count")
print(f"RESULT tie_hits={hits} count")
print(f"RESULT moved_near_tie={moved} count")
print(f"RESULT moved_under_tie={mt} count")
if sample:
    d, b, m = sample
    print(f"RESULT tie_draw_kw={d!r}")
    print(f"RESULT tie_runup_steps_baseline={sum(1 for x in b[2] if x)} count")
    print(f"RESULT tie_runup_steps_mutant={sum(1 for x in m[2] if x)} count")
    print(f"RESULT tie_ceiling_step39_baseline={b[0][39]} C  tie_ceiling_step39_mutant={m[0][39]} C")
    print(f"RESULT tie_requirement_step39_baseline={c.requirement(b, np.full(96, 20.0))[39]:.4f} C  "
          f"mutant={c.requirement(m, np.full(96, 20.0))[39]:.4f} C")
rng = np.random.default_rng(784)
mr = 0
for _ in range(60):
    dr = rng.uniform(0.0, 6.0, 96)
    step = int(rng.integers(1, 96))
    mr += c.differs(c.ceilings(p, h, step=step, draw=dr), c.ceilings(p, h, step=step, draw=dr, fn=fn))
print(f"RESULT moved_random={mr} count")
# Reach sweep: in-range configurations (cooling C/h x outdoor C x DHW run kW), ties per configuration.
cw = sw = 0
for rate in (0.05, 0.1, 0.3, 1.0, 3.0):
    for out in (-10.0, 0.0, 7.0):
        for pr in (2.0, 4.0):
            r = c.walk_tie(c.params(dhw_cooling_rate=rate), c.horizon(n=96, outdoor=np.full(96, out)), 40, B, fn,
                           k=50, p_run=pr)
            cw += r[0] > 0
            sw += r[3]
print(f"RESULT sweep_configs_with_ties={cw}/30 count")
print(f"RESULT sweep_ties_moved={sw} count")
c.footer()
