#!/usr/bin/env python3
# Metric: the step DhwPlanner._dhw_legionella_due places the cycle on (and reach_step's effect on it) when the
#   simulated flat-out ramp lands EXACTLY on the reach threshold `dhw_legionella_temp - 1e-6` at the end of step 0,
#   baseline vs mutant; count of searched inputs that are exact ties and of inputs whose arms differ.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_31c1881164f2dcdf.py
# EXPECTED RESULT tie_hits=6 count (3606 inputs tried)  moved_under_tie=6 count  moved_off_tie=0 count
# EXPECTED RESULT tie_step_baseline=0  tie_step_mutant=1  (cheapest price at step 0; the mutant calls step 0 unreachable)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due, line 626
#   `hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0]` (reach_step), consumed at lines 658-662.
# Perturbation: key 31c1881164f2dcdf (CMP_BOUND) -> `ramp[1:] > ...`, in memory (method recompiled,
#   mock.patch.object). Direction: at the exact tie reach_step moves 0 -> 1 and the placement window with it.
# Inputs: 200 L tank, 55/60 C, interval 7 d, hours_since 150 h (deadline step 72 of 96), price 0.1 at step 0 and
#   1.0 elsewhere; the initial tank temperature is bisected for the crossing and scanned +-300 floats; repeated
#   for outdoor -10/0/7 C and DHW run power 2/4 kW.
# Null control: initial temperatures off the tie (the scanned floats that are not exact ties).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_due", "hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0]",
              "hot = np.where(ramp[1:] > params.dhw_legionella_temp - 1e-6)[0]")
p = c.params()
T = float(p.dhw_legionella_temp) - 1e-6
n = 96
prices = np.ones(n)
prices[0] = 0.1
hits = moved = tried = mt = 0
sample = None
for out in (-10.0, 0.0, 7.0):
    for pr in (2.0, 4.0):
        pl = c.planner(p)

        def ramp1(x):
            h = c.horizon(n=n, dhw_temp=x, hours_since=150.0, outdoor=np.full(n, out))
            off = None
            return float(pl._dhw_plan_temps(c.dp._legionella_charge(n, pr, off), x, h.outdoor_temps,
                                            np.zeros(n), h.dt, None, None)[1])

        lo, hi = 30.0, T
        if not (ramp1(lo) < T <= ramp1(hi)):
            continue
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if mid in (lo, hi):
                break
            if ramp1(mid) < T:
                lo = mid
            else:
                hi = mid
        for x in c.ulps(hi, 300):
            h = c.horizon(n=n, dhw_temp=x, hours_since=150.0, outdoor=np.full(n, out))
            b = c.due(p, h, p_run=pr, prices=prices)
            m = c.due(p, h, p_run=pr, prices=prices, fn=fn)
            tried += 1
            hit = ramp1(x) == T
            hits += hit
            mv = b != m
            moved += mv
            mt += hit and mv
            if hit and mv and sample is None:
                sample = (x, out, pr, b, m)
print(f"RESULT threshold={T!r} C")
print(f"RESULT tie_inputs_tried={tried} count")
print(f"RESULT tie_hits={hits} count")
print(f"RESULT moved_under_tie={mt} count")
print(f"RESULT moved_off_tie={moved - mt} count")
if sample:
    x, out, pr, b, m = sample
    print(f"RESULT tie_input=dhw_temp {x!r} C, outdoor {out} C, run {pr} kW")
    print(f"RESULT tie_step_baseline={b[2]}  tie_step_mutant={m[2]}")
c.footer()
