"""D0 verifier (round 10), independent V2 harness for D0-s2-01.

Metric: per two-zone+DHW 24 h cell, shipped_gain = (J(x_ship@ftol1e-6) - J(x_ship@ftol F)) / |J(x_ship@ftol1e-6)|,
  J = the production objective captured at the LAST _multi_start_minimize call of the default run, x_ship = that
  call's returned x in each arm (arm F re-runs the whole optimize with every scipy L-BFGS-B ftol inside
  optimizer.py forced to F via _scoped_minimize). Positive = tighter ftol ships a better plan. Also the bill
  delta sum(price*x[:n]*DT) when the call is the price-length space call. Not a polish from prod.x.
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
   dev/audit/rounds/round10/D0/verify_s2_shipped.py [--ftol 1e-10] [--prices ...]
Expected: see verify.md. Baseline 17f1c55fad1b, Apple Silicon macOS.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from unittest import mock
from datetime import datetime
import numpy as np
from profiles import prices, weather, house, DT, solve_inputs
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
ap = argparse.ArgumentParser(); ap.add_argument("--ftol", type=float, default=1e-10)
ap.add_argument("--prices", default="winter_typical,winter_extreme,winter_narrow,winter_moderate,flat")
ap.add_argument("--weather", default="winter_cold,winter_mild")
a = ap.parse_args()
ORIG, RSM = O._multi_start_minimize, O._scoped_minimize; START = datetime(2026, 1, 15)
def run(pp, wp, ftol):
    cfg = house(two_zone=True, dhw=True); p = ThermalParameters.from_config(cfg); p.dhw_enabled = True
    m = ThermalModel(p); opt = O.HeatPumpOptimizer(m, O.OptimizationConfig(horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(pp, START); ot, wi, ra, so = weather(wp, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
         upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    caps = []
    def cap(o, c, b, args=(), maxiter=300, **kw):
        r = ORIG(o, c, b, args, maxiter, **kw); caps.append((o, args, np.asarray(r.x, float))); return r
    def sm(*x, **kw):
        if ftol is not None and "options" in kw: kw["options"] = dict(kw["options"], ftol=ftol)
        return RSM(*x, **kw)
    with mock.patch.object(O, "_multi_start_minimize", cap), mock.patch.object(O, "_scoped_minimize", sm):
        opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
                     precipitation=ra, solar_radiation=so, start_time=START))
    return caps, pr
pt0, tt0 = time.process_time(), time.thread_time(); rows = []
for pp in a.prices.split(","):
    for wp in a.weather.split(","):
        c0, pr = run(pp, wp, None); c1, _ = run(pp, wp, a.ftol)
        for i, ((o, args, x0), (_, _, x1)) in enumerate(zip(c0, c1)):
            if x0.shape != x1.shape: continue
            J0 = float(o(x0, *args)); J1 = float(o(x1, *args)); g = (J0 - J1) / abs(J0)
            n = min(len(pr), len(x0)); db = float(np.sum(pr[:n] * (x0[:n] - x1[:n]) * DT))
            rows.append((pp, g)); print(f"cell {pp}/{wp}/call{i} J_1e-6={J0:.4f} J_F={J1:.4f} shipped_gain={100*g:.4f} pct dbill_proxy={db:.3f}", flush=True)
w = np.array([g for q, g in rows if q != "flat"]); f = np.array([g for q, g in rows if q == "flat"])
print(f"RESULT shipped_gain_winter_mean={100*w.mean():.4f} pct n={len(w)} max={100*w.max():.4f} min={100*w.min():.4f} drop_max_mean={100*np.sort(w)[:-1].mean():.4f}")
if len(f): print(f"RESULT shipped_gain_flat_mean={100*f.mean():.4f} pct max={100*f.max():.4f}")
print(f"RESULT thread_factor={(time.process_time()-pt0)/max(time.thread_time()-tt0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=n/a")
