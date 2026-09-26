#!/usr/bin/env python3
"""V3 (round 9, D2-s3-02): money the import_margin floor costs, judged by the piecewise tariff.

Metric (one line): per (price profile, weather, export price E) cell, solve the same scenario twice with
HeatPumpOptimizer.optimize and a PV surplus (golden.pv_surplus_for of the scenario's irradiance): the
production plan (pv.import_margin floored) and a plan solved with the floor removed in memory; score
BOTH plans' total electrical draw (space + DHW) with the tariff itself,
sum_i dt*(E*min(P_i, s_i) + I_i*max(P_i - s_i, 0)); report production - unfloored (currency/day,
positive = the floor costs the user money) and the production plan's published predicted_cost minus
its own tariff score (the published error).
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s3_02_realized_cost.py
Perturbation: the unfloored arm IS the perturbation (mock.patch.object(pv, "import_margin")); null control:
winter_typical / E = 0 (import >= export on every surplus step) must read 0.
Caveat recorded in the report: comfort outcomes differ between the plans; only the tariff score is compared.
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
from heatpump_optimizer import pv
import golden

t0p, t0t = time.process_time(), time.thread_time()
_orig = pv.import_margin
unfloored = lambda prices, e: np.asarray(prices, float) - float(e)

def solve(price_profile, weather, E, floor):
    built = golden.make(price_profile=price_profile, weather_profile=weather,
                        opt_overrides={"pv_export_price": E})
    n = len(built["prices"])
    s = golden.pv_surplus_for(n, built["solar"])
    with mock.patch.object(pv, "import_margin", _orig if floor else unfloored):
        r = built["optimizer"].optimize(built["state"], built["prices"], built["outdoor"], built["wind"],
                                        built["rain"], built["solar"], golden.START, None, s)
    P = np.asarray(r.power_schedule, float) + np.asarray(r.dhw_power_schedule, float)
    I = np.asarray(built["prices"], float)
    tariff = float(np.sum(E * np.minimum(P, s) + I * np.maximum(P - s, 0.0)) * 0.25)
    return r, tariff

for prof, wx, E in (("winter_typical", "winter_cold", 0.0), ("summer_negative", "summer_cool", 0.0),
                    ("summer_negative", "summer_warm", 0.0), ("summer_typical", "summer_warm", 0.30),
                    ("summer_negative", "summer_cool", 0.30), ("shoulder", "shoulder", 0.30)):
    rp, tp = solve(prof, wx, E, True)
    ru, tu = solve(prof, wx, E, False)
    tag = f"{prof}_{wx}_E{E:.2f}"
    print(f"RESULT {tag}_tariff_prod_minus_unfloored={tp - tu:.4f} currency_per_day")
    print(f"RESULT {tag}_published_minus_tariff_prod={rp.predicted_cost - tp:.4f} currency")
    print(f"RESULT {tag}_tariff_prod={tp:.4f} currency")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
