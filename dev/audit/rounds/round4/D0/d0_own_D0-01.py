"""VERIFIER-OWN harness for D0-01 (seat verify-0-1, round 4).

METRIC (one line): per grid cell, the relative drop of the production
objective obtainable by running L-BFGS-B MYSELF, started AT the exact point
``optimizer._multi_start_minimize`` returned during a real production
``HeatPumpOptimizer.optimize`` call, with bounds/args/jac/options captured
live from that call and identical to production's dict
``{"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4}`` except ``ftol`` -> 1e-14:
``own_gap = (J(x_shipped) - J(x_descended)) / |J(x_shipped)|`` in %.

This is a deliberately DIFFERENT method from the finder's ftol_gap.py, which
re-runs the whole multi-start pipeline under a patched option.  Here nothing
in the production solve is patched at all: the shipped point is captured,
taken out, and descended from by this harness's own scipy call.  A positive
gap therefore proves "the shipped plan is not a minimum of its own objective"
from production's own output, with no seeding/basin question involved.

Two extra pieces of evidence this harness adds:
  * the census is taken at the scipy boundary (``optimizer.minimize``, the
    module-level symbol imported from scipy.optimize) -- one level BELOW the
    finder's ``_scoped_minimize`` hook -- so any L-BFGS-B call that does not
    go through the funnel the finder hooked would appear here as an
    "unexpected path" (options without the production maxiter/ftol/eps);
  * the grid covers BOTH ``_multi_start_minimize`` call sites: dhw=True runs
    the maxiter=300 DHW path (optimizer.py:3003) and dhw=False the maxiter=200
    space-only path (optimizer.py:3529).  The finder's 80 cells were all
    dhw=True.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/d0_own_D0-01.py

BASELINE SHA the finding was measured against: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
(production custom_components/heatpump_optimizer/optimizer.py is byte-identical
at this branch head; verified by git diff --stat 7dd68dd..HEAD).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOLS: custom_components/heatpump_optimizer/optimizer.py
:_multi_start_minimize (captured, not replaced) and :minimize (captured, not
replaced), driving ``HeatPumpOptimizer.optimize``.

NULL CONTROL: the ``flat`` price rows, reported separately, never folded in.
LEAVE-ONE-OUT: the priced aggregate is printed with its largest-gap cell dropped.
CONTENTION: objective values, ratios and iteration counts only; no timing
claim.  thread_factor/load1/swapins/concurrent-process count printed for the
record per the harness contract.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

# Thread pin FIRST, before any numpy import anywhere in the process
# (the tests/stress.py idiom the harness contract requires).
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

PRICE_PROFILES = (
    "winter_typical", "winter_extreme", "summer_typical", "summer_negative",
    "shoulder", "winter_narrow", "winter_moderate",
)
FLAT = "flat"
WEATHERS = ("winter_cold", "summer_warm")
START = datetime(2026, 1, 15)


def emit(name, value, unit=""):
    if isinstance(value, float):
        print(f"RESULT {name}={value:.6g} {unit}".rstrip(), flush=True)
    else:
        print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def concurrent_procs():
    try:
        out = subprocess.run(["ps", "axo", "comm,args"], capture_output=True,
                             text=True, timeout=10).stdout
        return sum(1 for ln in out.splitlines()
                   if "python3" in ln and ("tools/audit" in ln or "tests/" in ln))
    except Exception:
        return -1


class Conditions:
    def __init__(self):
        self.cpu = time.process_time()
        self.thr = time.thread_time()

    def emit(self):
        cpu = time.process_time() - self.cpu
        thr = time.thread_time() - self.thr
        emit("thread_factor", round(cpu / thr if thr > 0 else float("nan"), 4))
        emit("load1", round(os.getloadavg()[0], 2))
        try:
            out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                                 timeout=10).stdout
            for line in out.splitlines():
                if line.strip().startswith("Swapins"):
                    emit("swapins", int(line.split(":")[1].strip().rstrip(".")))
        except Exception:
            emit("swapins", -1)
        emit("concurrent_python_procs", concurrent_procs())


def loo(values):
    v = sorted(float(x) for x in values)
    if not v:
        return (float("nan"),) * 4
    mean = sum(v) / len(v)
    drop = sum(v[:-1]) / (len(v) - 1) if len(v) > 1 else float("nan")
    return mean, v[0], v[-1], drop


def build_cell(price_p, weather_p, two_zone, dhw):
    """tests/optimality.py:setup's shape, with dhw and weather opened up."""
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


# --------------------------------------------------------------------------
# capture at BOTH levels: the scipy boundary and _multi_start_minimize
# --------------------------------------------------------------------------
census = []          # one dict per scipy-level minimize call
unexpected = []      # scipy-level calls not carrying the production options


@contextmanager
def capture_all(ms_calls):
    """Patch nothing's behaviour: observe and pass through.

    ``O.minimize`` is the module-level scipy symbol; every L-BFGS-B call in
    optimizer.py resolves through it (the finder hooked ``_scoped_minimize``
    one level up).  ``_multi_start_minimize`` is observed for its arguments
    and its returned point.
    """
    real_ms = O._multi_start_minimize

    def min_wrapper(*a, **kw):
        res = _scipy_minimize(*a, **kw)
        try:
            opts = kw.get("options") or {}
            entry = {
                "method": kw.get("method"),
                "maxiter_opt": opts.get("maxiter"),
                "ftol_opt": opts.get("ftol"),
                "eps_opt": opts.get("eps"),
                "nit": int(res.nit), "status": int(res.status),
                "message": str(res.message),
            }
            census.append(entry)
            if not (kw.get("method") == "L-BFGS-B"
                    and entry["ftol_opt"] == 1e-6
                    and entry["eps_opt"] == 1e-4):
                unexpected.append(entry)
        except Exception:
            unexpected.append({"error": "unreadable"})
        return res

    def ms_wrapper(objective, candidates, bounds, args=(), maxiter=300,
                   batch_objective=None, fd_eps=1e-4):
        res = real_ms(objective, candidates, bounds, args=args, maxiter=maxiter,
                      batch_objective=batch_objective, fd_eps=fd_eps)
        ms_calls.append({
            "objective": objective, "args": args, "bounds": bounds,
            "maxiter": int(maxiter), "batch_objective": batch_objective,
            "fd_eps": float(fd_eps), "x_shipped": np.asarray(res.x, float),
        })
        return res

    with mock.patch.object(O, "minimize", min_wrapper), \
            mock.patch.object(O, "_multi_start_minimize", ms_wrapper):
        yield


def my_descent(call, ftol=1e-14):
    """Run L-BFGS-B MYSELF from the shipped point; identical options but ftol."""
    obj, args, bounds = call["objective"], call["args"], call["bounds"]
    jac = None
    if call["batch_objective"] is not None:
        def jac(x, *a):
            return O._batch_fd_gradient(
                call["batch_objective"], a, np.asarray(x, float),
                float(obj(np.asarray(x, float), *a)), call["fd_eps"], bounds)
    res = _scipy_minimize(
        obj, call["x_shipped"], args=args, jac=jac, method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": call["maxiter"], "ftol": ftol, "eps": 1e-4})
    x_new = np.asarray(res.x, dtype=float)
    j_old = float(obj(call["x_shipped"], *args))
    j_new = float(obj(x_new, *args))
    return (j_old, j_new)


def main() -> int:
    cond = Conditions()
    rows = []
    for price_p in PRICE_PROFILES + (FLAT,):
        for weather_p in WEATHERS:
            for tz in (False, True):
                for dhw in (True, False):
                    cell = build_cell(price_p, weather_p, tz, dhw)
                    o, m, pr, ot, wi, ra, so, st, start = cell
                    ms_calls = []
                    with capture_all(ms_calls):
                        result = o.optimize(st, pr, ot, wi, ra, so, start)
                    gaps = []
                    for c in ms_calls:
                        j_old, j_new = my_descent(c)
                        g = (j_old - j_new) / max(abs(j_old), 1e-12) * 100.0
                        gaps.append(g)
                    gap = max(gaps) if gaps else float("nan")
                    rows.append({
                        "price": price_p, "weather": weather_p, "tz": tz,
                        "dhw": dhw, "gap": gap,
                        "ms_calls": len(ms_calls),
                        "J": float(result.objective_value),
                    })
                    print(f"CELL {price_p:16s} {weather_p:12s} tz={int(tz)} "
                          f"dhw={int(dhw)}  ms_calls={len(ms_calls)}  "
                          f"own_descent_gap={gap:+.4f}%  "
                          f"J_result={float(result.objective_value):.5f}",
                          flush=True)

    priced = [r for r in rows if r["price"] != FLAT]
    flat = [r for r in rows if r["price"] == FLAT]
    dhw_on = [r for r in rows if r["dhw"] and r["price"] != FLAT]
    dhw_off = [r for r in rows if not r["dhw"] and r["price"] != FLAT]

    gp = [r["gap"] for r in priced]
    gf = [r["gap"] for r in flat]
    m_p, lo_p, hi_p, loo_p = loo(gp)
    m_f, lo_f, hi_f, loo_f = loo(gf)

    emit("own_cells_total", len(rows))
    emit("own_cells_priced", len(priced))
    emit("own_cells_flat_null_control", len(flat))
    emit("own_mean_descent_gap_priced_pct", m_p, "%")
    emit("own_max_descent_gap_priced_pct", hi_p, "%")
    emit("own_min_descent_gap_priced_pct", lo_p, "%")
    emit("own_loo_mean_descent_gap_priced_pct", loo_p, "%")
    emit("own_mean_descent_gap_flat_pct", m_f, "%")
    emit("own_max_descent_gap_flat_pct", hi_f, "%")
    emit("own_cells_gap_above_0p01pct", sum(1 for r in priced if r["gap"] > 0.01))
    emit("own_cells_gap_above_0p1pct", sum(1 for r in priced if r["gap"] > 0.1))
    emit("own_cells_negative_gap", sum(1 for r in rows if r["gap"] < -1e-9))
    # call-site split (new: the finder's grid was entirely dhw=True)
    emit("own_mean_gap_dhw_path_priced_pct",
         sum(r["gap"] for r in dhw_on) / len(dhw_on), "%")
    emit("own_mean_gap_spaceonly_path_priced_pct",
         sum(r["gap"] for r in dhw_off) / len(dhw_off), "%")
    emit("own_cells_dhw_path", len(dhw_on))
    emit("own_cells_spaceonly_path", len(dhw_off))
    # census at the scipy boundary
    emit("own_scipy_minimize_calls", len(census))
    emit("own_unexpected_scipy_paths", len(unexpected))
    msgs = Counter((c["status"], c["message"][:60]) for c in census)
    for (status, msg), n in sorted(msgs.items(), key=lambda kv: -kv[1]):
        print(f"CENSUS status={status} n={n} msg={msg!r}", flush=True)
    emit("own_census_status1_maxiter", sum(1 for c in census if c["status"] == 1))
    emit("own_census_max_nit", max(c["nit"] for c in census))
    emit("own_census_median_nit", float(np.median([c["nit"] for c in census])))
    emit("own_census_maxiter_options_seen",
         sorted({c["maxiter_opt"] for c in census}))
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
