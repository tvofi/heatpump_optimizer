#!/usr/bin/env python3
"""V3 (round 9, D2-s1-02): how much coil heat vanishes on a real solved plan, and how often.

Metric (one line): on the golden wood_coil scenario solved by HeatPumpOptimizer.optimize
(DHW start S C, start clock START+OFF h, cells (35,0),(50,0),(35,7),(30,7),(38,18),(50,7)), over the published plan's final simulate_trajectory_with_dhw
replay, sum_i q_coil_i*(1 - scale_i)*dt kWh, where q_coil_i is what production
thermal_model.dhw_coil_draw_reduction returned at step i and scale_i =
min(1, max(0, T_dhw_i - inlet)/(DHW_MIXED_USE_TEMP - inlet)) is the draw scale
simulate_dhw_step applies to that step's tank temperature (captured by hooking both
symbols); plus the count of steps with q_coil>0 and T_dhw<40 C.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s1_02_coil_reach.py [--perturb]
Perturbation (--perturb): thermal_model.DHW_MIXED_USE_TEMP -> inlet + 1e-3 in memory; vanished kWh -> 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from unittest import mock
from heatpump_optimizer import thermal_model as tm
import golden

PERTURB = "--perturb" in sys.argv
t0p, t0t = time.process_time(), time.thread_time()

import datetime as _dt
for S, OFF in ((35.0, 0), (50.0, 0), (35.0, 7), (30.0, 7), (38.0, 18), (50.0, 7)):
    spec = dict(golden.SCENARIOS["wood_coil"])
    so = dict(spec.get("state_overrides", {})); so["dhw_temperature"] = S
    spec["state_overrides"] = so
    built = golden.make(**spec)
    opt = built["optimizer"]
    inlet = opt.model.params.dhw_inlet_reference
    ctx = [mock.patch.object(tm, "DHW_MIXED_USE_TEMP", inlet + 1e-3)] if PERTURB else []
    for c in ctx: c.start()
    log = []
    orig_red = tm.dhw_coil_draw_reduction
    orig_step = tm.ThermalModel.simulate_dhw_step
    pending = {}
    def red(draw, wood, sp, inlet_temp=tm.DHW_COLD_WATER_TEMP):
        out = orig_red(draw, wood, sp, inlet_temp)
        pending["q"] = out[1]
        return out
    def step(self, *a, **k):
        T = k.get("dhw_temp", a[0] if a else None)
        if "q" in pending:
            log.append((pending.pop("q"), T))
        return orig_step(self, *a, **k)
    # capture only the last trajectory call (the published replay)
    orig_traj = tm.ThermalModel.simulate_trajectory_with_dhw
    def traj(self, *a, **k):
        log.clear(); pending.clear()
        return orig_traj(self, *a, **k)
    with mock.patch.object(tm, "dhw_coil_draw_reduction", red), \
         mock.patch.object(tm.ThermalModel, "simulate_dhw_step", step), \
         mock.patch.object(tm.ThermalModel, "simulate_trajectory_with_dhw", traj):
        res = opt.optimize(built["state"], built["prices"], built["outdoor"], built["wind"],
                           built["rain"], built["solar"], golden.START + _dt.timedelta(hours=OFF), None, None)
    span = max(tm.DHW_MIXED_USE_TEMP - inlet, 1e-6)
    lost = 0.0; nlow = 0; coil_tot = 0.0
    for q, T in log:
        sc = min(1.0, max(0.0, T - inlet) / span)
        lost += q * (1 - sc) * 0.25
        coil_tot += q * 0.25
        if q > 0 and T < 40.0: nlow += 1
    dhw = np.asarray(res.dhw_temp_trajectory, float)
    tag = f"S{int(S)}_h{OFF}"
    print(f"RESULT {tag}_replay_steps={len(log)} count")
    print(f"RESULT {tag}_coil_steps_dhw_below_40={nlow} count")
    print(f"RESULT {tag}_coil_heat_total={coil_tot:.4f} kWh")
    print(f"RESULT {tag}_vanished_heat={lost:.4f} kWh")
    print(f"RESULT {tag}_published_dhw_min={dhw.min():.3f} degC")
    print(f"RESULT {tag}_published_dhw_steps_below_40={int((dhw < 40).sum())} of {len(dhw)}")
    for c in ctx: c.stop()
print(f"RESULT perturbed={int(PERTURB)}")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
