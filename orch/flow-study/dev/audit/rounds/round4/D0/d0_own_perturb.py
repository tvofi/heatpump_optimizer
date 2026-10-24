"""VERIFIER-OWN perturbation probe (seat verify-0-1, round 4).

METRIC (one line): on four cells where the un-perturbed tree shows a nonzero
descent gap, the relative objective drop obtainable by descending (this
harness's own scipy L-BFGS-B call, options identical to production's dict
except ftol=1e-14) from the exact point ``_multi_start_minimize`` returned in
a real production solve -- run against whatever optimizer.py source is
currently in the tree.

The production edits are made OUTSIDE this script (sed + git checkout); the
script is constant so the three arms are directly comparable:

    arm shipped : git HEAD            -> gaps > 0 (the finding)
    arm tight   : ftol 1e-6 -> 1e-14  -> gaps must fall to ~0
    arm loose   : ftol 1e-6 -> 1e-4   -> gaps must grow

plus a D0-02 perturbation arm run with the same script (census mode):

    arm starve  : maxiter 300->3 and 200->3 (call sites optimizer.py:3004,
                  :3530) -> every solve terminates on the cap

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/d0_own_perturb.py [gap|census]

BASELINE SHA the finding was measured against: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402
from scipy.optimize import minimize as _scipy_minimize  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

START = datetime(2026, 1, 15)
# the four cells with the largest descent gaps in d0_own_D0-01.py's run,
# plus one zero-gap control cell.
GAP_CELLS = (
    ("summer_negative", "winter_cold", False, False),   # 1.1703 %
    ("flat", "winter_cold", True, False),               # 1.1233 %
    ("shoulder", "winter_cold", True, True),            # 0.8940 %
    ("winter_typical", "winter_cold", True, True),      # 0.3868 %
    ("winter_moderate", "winter_cold", False, False),   # 0.0000 % control
)
CENSUS_CELLS = (
    ("winter_typical", True), ("winter_typical", False),
    ("shoulder", False),
)


def emit(name, value, unit=""):
    print(f"RESULT {name}={value if not isinstance(value, float) else round(value, 6)} "
          f"{unit}".rstrip(), flush=True)


def build_cell(price_p, weather_p, two_zone, dhw):
    cfg = house(two_zone=two_zone, dhw=dhw)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    steps = int(round(24 / DT))
    pr, ot, wi, ra, so = (a[:steps] for a in (pr, ot, wi, ra, so))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=50.0)
    return o, m, pr, ot, wi, ra, so, st, START


def gap_mode() -> int:
    real_ms = O._multi_start_minimize
    real_scoped = O._scoped_minimize
    gaps = []
    ftol_seen = set()
    maxiter_seen = set()

    def scoped_probe(*a, **kw):
        opts = kw.get("options") or {}
        ftol_seen.add(opts.get("ftol"))
        maxiter_seen.add(opts.get("maxiter"))
        return real_scoped(*a, **kw)

    for price_p, weather_p, tz, dhw in GAP_CELLS:
        o, m, pr, ot, wi, ra, so, st, start = build_cell(price_p, weather_p, tz, dhw)
        ms_calls = []

        def ms_wrapper(objective, candidates, bounds, args=(), maxiter=300,
                       batch_objective=None, fd_eps=1e-4):
            res = real_ms(objective, candidates, bounds, args=args,
                          maxiter=maxiter, batch_objective=batch_objective,
                          fd_eps=fd_eps)
            ms_calls.append({
                "objective": objective, "args": args, "bounds": bounds,
                "maxiter": int(maxiter), "batch_objective": batch_objective,
                "fd_eps": float(fd_eps), "x": np.asarray(res.x, float)})
            return res

        with mock.patch.object(O, "_multi_start_minimize", ms_wrapper), \
                mock.patch.object(O, "_scoped_minimize", scoped_probe):
            o.optimize(st, pr, ot, wi, ra, so, start)
        cell_gaps = []
        for c in ms_calls:
            jac = None
            if c["batch_objective"] is not None:
                def jac(x, *a, c=c):
                    return O._batch_fd_gradient(
                        c["batch_objective"], a, np.asarray(x, float),
                        float(c["objective"](np.asarray(x, float), *a)),
                        c["fd_eps"], c["bounds"])
            res = _scipy_minimize(
                c["objective"], c["x"], args=c["args"], jac=jac,
                method="L-BFGS-B", bounds=c["bounds"],
                options={"maxiter": c["maxiter"], "ftol": 1e-14, "eps": 1e-4})
            j0 = float(c["objective"](c["x"], *c["args"]))
            j1 = float(c["objective"](np.asarray(res.x, float), *c["args"]))
            cell_gaps.append((j0 - j1) / max(abs(j0), 1e-12) * 100.0)
        g = max(cell_gaps) if cell_gaps else float("nan")
        gaps.append(g)
        print(f"CELL {price_p:16s} {weather_p:12s} tz={int(tz)} dhw={int(dhw)} "
              f"descent_gap={g:+.4f}%", flush=True)
    emit("perturb_mean_gap_pct", sum(gaps) / len(gaps), "%")
    emit("perturb_max_gap_pct", max(gaps), "%")
    emit("perturb_source_ftol_actually_passed", sorted(ftol_seen, key=str))
    emit("perturb_source_maxiter_actually_passed",
         sorted(maxiter_seen, key=lambda v: (v is None, v)))
    emit("load1", round(os.getloadavg()[0], 2))
    return 0


def census_mode() -> int:
    census = []

    def min_wrapper(*a, **kw):
        res = _scipy_minimize(*a, **kw)
        opts = kw.get("options") or {}
        census.append({"maxiter": opts.get("maxiter"), "nit": int(res.nit),
                       "status": int(res.status)})
        return res

    with mock.patch.object(O, "minimize", min_wrapper):
        for price_p, tz in CENSUS_CELLS:
            o, m, pr, ot, wi, ra, so, st, start = build_cell(
                price_p, "winter_cold", tz, True)
            o.optimize(st, pr, ot, wi, ra, so, start)
            print(f"CELL {price_p:16s} tz={int(tz)} solves={len(census)}",
                  flush=True)
    emit("perturb_solves", len(census))
    emit("perturb_solves_on_cap",
         sum(1 for c in census if c["status"] == 1
             or (c["maxiter"] is not None and c["nit"] >= c["maxiter"])))
    emit("perturb_maxiter_values",
         sorted({c["maxiter"] for c in census if c["maxiter"] is not None}))
    emit("load1", round(os.getloadavg()[0], 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(gap_mode() if "census" not in sys.argv else census_mode())
