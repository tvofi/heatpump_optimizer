"""VERIFIER-0-2 OWN HARNESS for D0-02 (independent of d0lib.py).

METRIC (one line): a census, taken by wrapping the ``scipy.optimize.minimize``
symbol imported into ``optimizer.py`` (one level closer to scipy than the
finder's hooks, so it catches every L-BFGS-B call whatever the path), of
every L-BFGS-B call's ``nit``, ``status`` and the ``maxiter`` option it was
handed, over a price x weather x topology grid at horizons 6 h, 24 h and
48 h with DHW on (the shipped default) -- the finder only ran 24 h, so the
48 h arm attacks the "never binding" claim's scope; plus the relative
objective change of multiplying production's ``maxiter`` by 15 on the 48 h
cells (if any solve there is near the cap the arm must move).

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/v02_own_D0-02.py

BASELINE SHA the finding was measured at: 7dd68dd (optimizer.py unchanged
between that and this tree, 3e91f85).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy 2.4.6 / scipy 1.17.1.

CONTENTION: iteration counts, statuses and objective ratios only.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_real_minimize = O.minimize

CENSUS: list[dict] = []


def _census_minimize(fun, x0, *a, **kw):
    res = _real_minimize(fun, x0, *a, **kw)
    try:
        opts = kw.get("options") or {}
        CENSUS.append({
            "method": kw.get("method"),
            "maxiter": int(opts.get("maxiter", -1)),
            "ftol": float(opts.get("ftol", float("nan"))),
            "nit": int(res.nit), "status": int(res.status),
            "n": int(np.asarray(x0).size),
        })
    except Exception:
        pass
    return res


def _maxiter_x15(fun, x0, *a, **kw):
    opts = dict(kw.get("options") or {})
    if "maxiter" in opts:
        opts["maxiter"] = int(opts["maxiter"]) * 15
        kw["options"] = opts
    return _real_minimize(fun, x0, *a, **kw)


def tile(arr, k):
    a = np.asarray(arr, dtype=float)
    return np.tile(a, int(np.ceil(k / len(a))))[:k]


def build(price_p, weather_p, tz, horizon_h):
    steps = int(round(horizon_h / DT))
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon_h, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    start = datetime(2026, 1, 15)
    pr = tile(prices(price_p, start), steps)
    ot, wi, ra, so = (tile(x, steps) for x in weather(weather_p, start))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=50.0)
    return o, st, pr, ot, wi, ra, so, start


def emit(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def main() -> int:
    cpu0, thr0 = time.process_time(), time.thread_time()
    mark0 = len(CENSUS)
    grid = []
    for horizon in (6.0, 24.0, 48.0):
        for pp in ("winter_typical", "winter_extreme", "summer_negative",
                   "flat"):
            for tz in (False, True):
                grid.append((pp, tz, horizon))
    for pp, tz, horizon in grid:
        o, st, pr, ot, wi, ra, so, start = build(pp, "winter_cold", tz,
                                                 horizon)
        with mock.patch.object(O, "minimize", _census_minimize):
            res = o.optimize(st, pr, ot, wi, ra, so, start)
        j0 = float(res.objective_value)
        j15 = float("nan")
        if horizon == 48.0:  # attack arm on the longest horizon only
            with mock.patch.object(O, "minimize", _maxiter_x15):
                j15 = float(o.optimize(st, pr, ot, wi, ra, so, start)
                            .objective_value)
        mine = CENSUS[mark0:]
        mark0 = len(CENSUS)
        nits = [c["nit"] for c in mine]
        caps = [c["maxiter"] for c in mine]
        print(f"CELL {pp:16s} tz={int(tz)} h={horizon:4.0f}  "
              f"solves={len(mine)}  nit max={max(nits)} "
              f"med={float(np.median(nits)):.0f}  caps={sorted(set(caps))}  "
              f"on_cap={sum(1 for c in mine if c['status'] == 1 or c['nit'] >= c['maxiter'])}"
              f"  x15gap={(j0 - j15) / abs(j0) * 100 if np.isfinite(j15) else float('nan'):+.4f}%",
              flush=True)

    lb = [c for c in CENSUS if c["method"] == "L-BFGS-B"]
    allcalls = len(CENSUS)
    nits = np.array([c["nit"] for c in lb])
    frac_of_cap = np.array([c["nit"] / c["maxiter"] for c in lb])
    emit("minimize_calls_total", allcalls)
    emit("lbfgsb_calls", len(lb))
    emit("distinct_maxiter_values", sorted(set(c["maxiter"] for c in lb)))
    emit("calls_status_1", sum(1 for c in lb if c["status"] == 1))
    emit("calls_nit_ge_maxiter", sum(1 for c in lb if c["nit"] >= c["maxiter"]))
    emit("max_nit", int(nits.max()))
    emit("median_nit", float(np.median(nits)))
    emit("p99_nit", float(np.percentile(nits, 99)))
    emit("max_fraction_of_cap",
         round(float(frac_of_cap.max()), 4))
    emit("calls_above_half_cap", int((frac_of_cap > 0.5).sum()))
    emit("calls_above_quarter_cap", int((frac_of_cap > 0.25).sum()))
    emit("max_nit_at_48h_cells",
         int(max(c["nit"] for c in lb if c["n"] == 192)) if any(
             c["n"] == 192 for c in lb) else -1)
    emit("non_lbfgsb_calls", allcalls - len(lb))
    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    emit("thread_factor", round(cpu / thr if thr > 0 else float("nan"), 4))
    emit("load1", round(os.getloadavg()[0], 2))
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        emit("swapins", next(int(l.split(":")[1].strip().rstrip("."))
                             for l in out.splitlines()
                             if l.strip().startswith("Swapins")))
    except Exception:
        emit("swapins", -1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
