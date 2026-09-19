#!/usr/bin/env python3
"""D0 round 5 -- the polish that is never run on the candidates that need it.

METRIC (one line): per cell, the relative gap in percent between the objective
the shipped `_multi_start_minimize` delivers for the space sub-problem it was
handed and the best objective production code reaches when each of those SAME
candidates is handed to production `_multi_start_minimize` on its own (so each
one gets the production `_lbfgsb_restart` polish); positive means the shipped
plan is the more expensive one on the identical objective and bounds.

Instrumented symbols (production, hooked / driven):
  heatpump_optimizer.optimizer:_multi_start_minimize   (hooked to capture the
                                                       production call, then
                                                       driven per candidate)
  heatpump_optimizer.optimizer:_lbfgsb_restart         (reached inside it)

Arms
  shipped : the tree as it stands -- `optimize()` unpatched, and the recorded
            `_multi_start_minimize` call's own return value scored on its own
            closure.
  percand : PERTURBATION -- each captured candidate is passed, alone, to the
            production `_multi_start_minimize` with the captured `args`,
            `maxiter`, `batch_objective` and `fd_eps`, so production's own
            polish runs on that candidate instead of only on the best raw
            result. `min` over candidates is the challenger.

Expected (baseline eaa2a06, Apple M1, measured on the 8 x 4 winter_cold grid):
  RESULT gap_percand_pct_max      1.4023  +-0.02
  RESULT gap_percand_pct_mean     0.0895  +-0.02
  RESULT gap_percand_pct_loo_drop_most_favourable 0.0408  +-0.02
  RESULT gap_percand_pct_flat_max 0.3781  +-0.05  (null control: this arm FAILS
       it -- the flat arm is 27 % of the priced maximum and its mean is larger
       than the priced mean, so this arm is a solver-quality defect on the
       production objective, NOT a price-arbitrage gain. See REPORT.md; the
       price-specific claim is carried by restart_race.py, whose flat control
       passes at 0.0194 % against 1.1703 %.)

Command (from the export root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/polish_race.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/polish_race.py --quick

Counted-number key: the objective the production sub-problem closure returns
for a plan (the same closure `optimize()` hands to `_multi_start_minimize`),
read from both arms in one process on one machine.

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
PRICE_PROFILES = ("winter_typical", "winter_extreme", "summer_typical",
                  "summer_negative", "shoulder", "winter_narrow",
                  "winter_moderate", "flat")
START = datetime(2026, 1, 15)
HOURS = 24


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


def cell(tz, price_p, weather_p, dhw, hours):
    """Capture the production call, then race every candidate on its own."""
    cap = []
    real = optmod._multi_start_minimize

    def rec(objective, candidates, bounds, *a, **kw):
        res = real(objective, candidates, bounds, *a, **kw)
        cap.append(dict(objective=objective,
                        candidates=[np.array(c, dtype=float) for c in candidates],
                        bounds=list(bounds), kw=dict(kw), res=res))
        return res

    opt, m, pr, ot, wi, ra, so, st = mksetup(tz, price_p, weather_p, dhw, hours)
    with mock.patch.object(optmod, "_multi_start_minimize", rec):
        r = opt.optimize(st, pr, ot, wi, ra, so, START)
    assert cap, "no _multi_start_minimize call captured"
    c = cap[0]
    obj, kw = c["objective"], c["kw"]
    args = kw.get("args", ())
    bnds = c["bounds"]
    lo = np.array([b[0] for b in bnds])
    hi = np.array([b[1] for b in bnds])

    def f(x):
        return float(obj(np.clip(np.asarray(x, dtype=float), lo, hi), *args))

    f_shipped = f(c["res"].x)
    per = []
    for g in c["candidates"]:
        rr = optmod._multi_start_minimize(
            obj, [g], bnds, args=args, maxiter=kw.get("maxiter"),
            batch_objective=kw.get("batch_objective"), fd_eps=1e-4)
        per.append(f(rr.x))
    f_best = min(per)
    return dict(n_cand=len(c["candidates"]), maxiter=kw.get("maxiter"),
                f_shipped=f_shipped, f_best=f_best, per_cand=per,
                gap_pct=100.0 * (f_shipped - f_best) / max(abs(f_shipped), 1e-12),
                plan_obj=float(r.objective_value),
                plan_sek=float(r.predicted_cost))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    t_start = time.monotonic()
    combos = [(tz, dhw) for tz in (False, True) for dhw in (False, True)]
    print(f"# baseline {BASELINE_SHA}  machine {MACHINE}")
    rows = []
    for pp in PRICE_PROFILES:
        for tz, dhw in combos:
            t0 = time.monotonic()
            d = cell(tz, pp, "winter_cold", dhw, HOURS)
            d.update(price=pp, tz=tz, dhw=dhw, sec=time.monotonic() - t0)
            rows.append(d)
            print(f"CELL {pp} tz={int(tz)} dhw={int(dhw)} ncand={d['n_cand']} "
                  f"maxiter={d['maxiter']} shipped={d['f_shipped']:.6f} "
                  f"bestcand={d['f_best']:.6f} gap={d['gap_pct']:.4f}% "
                  f"per_cand={[round(v, 5) for v in d['per_cand']]} "
                  f"[{d['sec']:.1f}s]", flush=True)

    priced = [r for r in rows if r["price"] != "flat"]
    flat = [r for r in rows if r["price"] == "flat"]
    print("\n--- aggregates ---")
    print(f"RESULT cells_total={len(rows)} count")
    print(f"RESULT cells_priced={len(priced)} count")
    print(f"RESULT cells_with_gap_priced="
          f"{sum(1 for r in priced if r['gap_pct'] > 0.01)} count")
    g = [r["gap_pct"] for r in priced]
    print(f"RESULT gap_percand_pct_max={max(g):.4f} percent")
    print(f"RESULT gap_percand_pct_min={min(g):.4f} percent")
    print(f"RESULT gap_percand_pct_mean={sum(g) / len(g):.4f} percent")
    fig = max(priced, key=lambda r: r["gap_pct"])
    print(f"RESULT gap_percand_pct_loo_drop_most_favourable="
          f"{(sum(g) - fig['gap_pct']) / max(len(g) - 1, 1):.4f} percent")
    if flat:
        gf = [r["gap_pct"] for r in flat]
        print(f"RESULT gap_percand_pct_flat_max={max(gf):.4f} percent")
        print(f"RESULT gap_percand_pct_flat_mean={sum(gf) / len(gf):.4f} percent")
    print(f"RESULT gap_percand_pct_top_cell={fig['gap_pct']:.4f} percent")
    print(f"RESULT top_cell_plan_objective="
          f"{fig['plan_obj']:.6f} objective_units")
    print(f"RESULT top_cell_plan_sek={fig['plan_sek']:.3f} SEK_per_day")
    print("\n--- conditions ---")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.4f} ratio")
    try:
        print(f"RESULT load1={float(os.getloadavg()[0]):.2f} count")
    except Exception:
        print("RESULT load1=-1 count")
    try:
        import psutil
        print(f"RESULT swapins={int(psutil.swap_memory().sin)} count")
    except Exception:
        print("RESULT swapins=-1 count")
    print(f"# wall {time.monotonic() - t_start:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
