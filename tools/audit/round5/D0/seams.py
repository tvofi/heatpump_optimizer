#!/usr/bin/env python3
"""D0 round 5 -- the three sub-optimality homes that are NOT binding here.

METRIC (four numbers, all counts or exact objective spreads, no timings):
  RESULT solves_at_iteration_cap      count of L-BFGS-B solves whose nit reached
                                      the maxiter production passed it
  RESULT candidates_dropped_by_top4   count of candidates the `_MULTI_START_SOLVES`
                                      top-4-by-guess-score cut never refined
  RESULT resolve_delta_pct_max        max relative objective change when the
                                      captured call is re-run with identical
                                      kwargs (solver determinism)
  RESULT objective_purity_max_spread  max spread over five evaluations of the
                                      captured objective at one fixed point

Instrumented symbols (production):
  heatpump_optimizer.optimizer:_multi_start_minimize   (hooked)
  heatpump_optimizer.optimizer:_scoped_minimize        (hooked, for nit)
  heatpump_optimizer.optimizer:_MULTI_START_SOLVES     (read)

Expected (baseline eaa2a06, measured): cells_total 64; multi_start_calls 74;
lbfgsb_solves 340; solves_at_iteration_cap 0; calls_with_top4_truncation 0;
candidates_dropped_by_top4 0; resolve_delta_pct_max 0.000000;
objective_purity_max_spread 0.000e+00. Any non-zero in the last two means the
solver or the objective is not the pure function the rest of D0 assumes.

Command (from the export root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/seams.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/seams.py --quick

Findings harness (FROZEN EVIDENCE, deliberately no `live-header` marker).
"""
import os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
assert os.path.isdir(os.path.join(ROOT, "custom_components")), ROOT
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import argparse
import numpy as np
from datetime import datetime
from unittest import mock

from profiles import prices, weather, house, DT, N           # noqa: E402
from heatpump_optimizer.thermal_model import (               # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (                   # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer import optimizer as optmod           # noqa: E402

BASELINE_SHA = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"
MACHINE = "Apple M1, 8 GB, macOS 25.6.0, numpy 2.4.6, scipy 1.17.1"
PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow", "winter_moderate",
          "flat")
START = datetime(2026, 1, 15)


def mksetup(tz, price_p, weather_p, dhw, hours):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=hours, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return opt, m, pr, ot, wi, ra, so, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()
    weathers = ("winter_cold",) if a.quick else ("winter_cold", "winter_mild")

    cap = []
    scoped = []
    real_ms = optmod._multi_start_minimize
    real_scoped = optmod._scoped_minimize

    def rec(objective, candidates, bounds, *args, **kw):
        res = real_ms(objective, candidates, bounds, *args, **kw)
        cap.append(dict(objective=objective,
                        candidates=[np.array(c, dtype=float) for c in candidates],
                        bounds=list(bounds), kw=dict(kw), res=res))
        return res

    def sc(obj, x0, *args, **kw):
        r = real_scoped(obj, x0, *args, **kw)
        scoped.append((int(kw.get("options", {}).get("maxiter", -1)), int(r.nit),
                       int(r.status)))
        return r

    n_cells = n_calls = 0
    at_cap = 0
    n_solves = 0
    dropped = 0
    calls_trunc = 0
    resolve_pct = 0.0
    purity = 0.0
    t0 = time.monotonic()
    print(f"# baseline {BASELINE_SHA}  machine {MACHINE}")
    for pp in PRICES:
        for wp in weathers:
            for tz in (False, True):
                for dhw in (False, True):
                    n_cells += 1
                    cap.clear()
                    scoped.clear()
                    opt, m, pr, ot, wi, ra, so, st = mksetup(tz, pp, wp, dhw, a.hours)
                    with mock.patch.object(optmod, "_multi_start_minimize", rec), \
                         mock.patch.object(optmod, "_scoped_minimize", sc):
                        opt.optimize(st, pr, ot, wi, ra, so, START)
                    n_calls += len(cap)
                    n_solves += len(scoped)
                    for mx, nit, status in scoped:
                        if mx >= 0 and nit >= mx:
                            at_cap += 1
                    for c in cap:
                        n = len(c["candidates"])
                        if n > optmod._MULTI_START_SOLVES:
                            calls_trunc += 1
                            dropped += n - optmod._MULTI_START_SOLVES
                        obj = c["objective"]
                        kw = c["kw"]
                        args = kw.get("args", ())
                        bnds = c["bounds"]
                        lo = np.array([b[0] for b in bnds])
                        hi = np.array([b[1] for b in bnds])

                        def f(x):
                            return float(obj(np.clip(np.asarray(x, dtype=float), lo, hi), *args))

                        # determinism: re-run the identical production call
                        r2 = real_ms(obj, c["candidates"], c["bounds"], **kw)
                        f1 = f(c["res"].x)
                        f2 = f(r2.x)
                        resolve_pct = max(resolve_pct,
                                          100.0 * abs(f1 - f2) / max(abs(f1), 1e-12))
                        # purity: five evaluations at one fixed point
                        vals = [f(c["res"].x) for _ in range(5)]
                        purity = max(purity, max(vals) - min(vals))
                    print(f"CELL {pp} {wp} tz={int(tz)} dhw={int(dhw)} "
                          f"ncalls={len(cap)} nscoped={len(scoped)} "
                          f"[{time.monotonic() - t0:.0f}s]", flush=True)

    print("\n--- aggregates ---")
    print(f"RESULT cells_total={n_cells} count")
    print(f"RESULT multi_start_calls={n_calls} count")
    print(f"RESULT lbfgsb_solves={n_solves} count")
    print(f"RESULT solves_at_iteration_cap={at_cap} count")
    print(f"RESULT calls_with_top4_truncation={calls_trunc} count")
    print(f"RESULT candidates_dropped_by_top4={dropped} count")
    print(f"RESULT resolve_delta_pct_max={resolve_pct:.6f} percent")
    print(f"RESULT objective_purity_max_spread={purity:.3e} objective_units")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.4f} ratio")
    try:
        print(f"RESULT load1={float(os.getloadavg()[0]):.2f} count")
    except Exception:
        print("RESULT load1=-1 count")
    print("# swapins: not available on this host (psutil absent); no memory RESULT carried")
    print(f"# wall {time.monotonic() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
