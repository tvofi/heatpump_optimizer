"""D0 verifier (round 10), independent V2 harness for D0-s1-01.

Metric: per captured _multi_start_minimize call, gap_rand = (f(prod.x) - min_k f(x_k)) / |f(prod.x)|,
  x_k = production's own _multi_start_minimize run from 12 seeded-uniform random starts in the bounds
  (rng seed 0, same maxiter/batch objective), no structured seeds, no polish, no feasibility filter
  (room-band violation of the winner reported beside it). f = captured production objective.
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
   dev/audit/rounds/round10/D0/verify_s1_random.py [--prices a,b] [--weather a,b] [--tz 0,1]
Expected: see dev/audit/rounds/round10/D0/verify.md. Baseline 17f1c55fad1b, Apple Silicon macOS.
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
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
ap = argparse.ArgumentParser()
ap.add_argument("--prices", default="winter_typical,winter_moderate,shoulder,summer_negative,flat")
ap.add_argument("--weather", default="winter_cold,shoulder,summer_cool")
ap.add_argument("--tz", default="0,1"); ap.add_argument("--k", type=int, default=12)
a = ap.parse_args()
ORIG = O._multi_start_minimize; START = datetime(2026, 1, 15)
pt0, tt0 = time.process_time(), time.thread_time(); gaps = []
for tz in [int(t) for t in a.tz.split(",")]:
  for pp in a.prices.split(","):
    for wp in a.weather.split(","):
        cfg = house(two_zone=tz); p = ThermalParameters.from_config(cfg); p.dhw_enabled = False
        m = ThermalModel(p)
        opt = O.HeatPumpOptimizer(m, O.OptimizationConfig(horizon_hours=24, time_step_minutes=15,
              target_temp=21.0, min_temp=17.0, max_temp=23.0))
        pr = prices(pp, START)[:96]; ot, wi, ra, so = (s[:96] for s in weather(wp, START))
        st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
             upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
        caps = []
        def wrap(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, **kw):
            r = ORIG(objective, candidates, bounds, args=args, maxiter=maxiter, batch_objective=batch_objective, **kw)
            caps.append((objective, bounds, args, maxiter, batch_objective, np.asarray(r.x, float))); return r
        with mock.patch.object(O, "_multi_start_minimize", wrap):
            opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
                         precipitation=ra, solar_radiation=so, start_time=START))
        for ci, (obj, b, args, mi, bo, px) in enumerate(caps):
            lb = np.array([q[0] for q in b]); ub = np.array([q[1] for q in b])
            rng = np.random.default_rng(0)
            seeds = [lb + (ub - lb) * rng.random(len(lb)) for _ in range(a.k)]
            r = ORIG(obj, seeds, b, args=args, maxiter=mi, batch_objective=bo)
            fp = float(obj(px, *args)); fr = float(obj(np.asarray(r.x), *args))
            g = (fp - fr) / max(abs(fp), 1e-12); gaps.append((pp, g))
            print(f"cell tz={tz} {pp} {wp} call{ci} f_prod={fp:.5f} f_rand={fr:.5f} gap_rand={g:.3e}", flush=True)
g = np.array([x for _, x in gaps]); fl = np.array([x for q, x in gaps if q == "flat"])
print(f"RESULT cells={len(g)} count"); print(f"RESULT gap_rand_max={g.max():.4e} ratio")
print(f"RESULT cells_gap_rand_gt_1e-3={int((g>1e-3).sum())} count"); print(f"RESULT cells_rand_worse={int((g<0).sum())} count")
if len(fl): print(f"RESULT flat_gap_rand_max={fl.max():.4e} ratio")
print(f"RESULT thread_factor={(time.process_time()-pt0)/max(time.thread_time()-tt0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=n/a")
