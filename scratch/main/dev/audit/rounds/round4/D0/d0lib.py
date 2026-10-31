"""Shared scaffolding for the round-4 D0 (price optimality) harnesses.

Not a harness itself: it is imported by the harnesses in this directory and
prints nothing on import.  What it carries:

  * the BLAS thread pin, applied at import time *before* numpy is imported by
    anything downstream (every harness imports this module first);
  * ``build_cell`` -- one optimizer/model/state/inputs tuple per grid cell,
    built from ``tests/profiles.py`` exactly as ``tests/optimality.py:setup``
    does, extended with dhw on/off and horizon;
  * ``capture_restarts`` / ``capture_starts`` -- ``mock.patch.object`` wrappers
    around the two production symbols the D0 findings hook,
    ``optimizer:_lbfgsb_restart`` and ``optimizer:_multi_start_minimize``;
  * ``emit`` -- the ``RESULT`` line printer, and ``emit_conditions`` which
    prints ``thread_factor``, ``load1`` and ``swapins`` as the harness
    contract in tools/audit/README.md requires.

baseline: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
machine:  8-core Apple M1, 8 GB, macOS 25.6.0, numpy on OpenBLAS
"""
from __future__ import annotations

import os

# Thread pin FIRST, before any numpy import anywhere in the process.
for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from contextlib import contextmanager  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402

from profiles import DT, N, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

BASELINE_SHA = "7dd68dd327fe3dbfb09f3bd0fe38910c58877697"
MACHINE = "8-core Apple M1, 8 GB, macOS 25.6.0, OpenBLAS, python 3.11"

PRICE_PROFILES = (
    "winter_typical", "winter_extreme", "summer_typical", "summer_negative",
    "shoulder", "winter_narrow", "winter_moderate",
)
FLAT = "flat"
WEATHER_PROFILES = (
    "winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder",
)

START = datetime(2026, 1, 15)


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------
def build_cell(price_p, weather_p, two_zone=False, dhw=False, horizon=24,
               start=START):
    """One grid cell: (opt, model, prices, ot, wind, rain, solar, state, start).

    Same construction as tests/optimality.py:setup, with dhw and horizon
    opened up.  The horizon is applied by truncating the 96-step profile
    arrays, which is what the optimizer's own horizon handling does.
    """
    cfg = house(two_zone=two_zone)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, start)
    ot, wi, ra, so = weather(weather_p, start)
    steps = int(round(horizon / DT))
    pr, ot, wi, ra, so = (a[:steps] for a in (pr, ot, wi, ra, so))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=50.0)
    return o, m, pr, ot, wi, ra, so, st, start


def solve(cell):
    o, m, pr, ot, wi, ra, so, st, start = cell
    return o.optimize(st, pr, ot, wi, ra, so, start)


def energy_cost(power, pr, dt=DT):
    return float(np.sum(np.asarray(pr) * np.asarray(power)) * dt)


# --------------------------------------------------------------------------
# instrumentation
# --------------------------------------------------------------------------
@contextmanager
def capture_restarts(record, keep_rel=None):
    """Hook ``optimizer:_lbfgsb_restart``.

    Appends one dict per call: the prior objective at the point L-BFGS-B
    returned, the objective at the restarted (polished) point, the relative
    drop, and whether production adopted it.  ``keep_rel`` (optional)
    temporarily replaces ``optimizer._LBFGSB_RESTART_KEEP_REL`` -- the
    perturbation arm.
    """
    real = opt_mod._lbfgsb_restart
    saved = opt_mod._LBFGSB_RESTART_KEEP_REL

    def wrapper(best, objective, bounds, args, maxiter, batch_objective,
                fd_eps):
        prior = float(objective(np.asarray(best.x, dtype=float), *args))
        out = real(best, objective, bounds, args, maxiter, batch_objective,
                   fd_eps)
        after = float(objective(np.asarray(out.x, dtype=float), *args))
        adopted = out is not best
        # Re-derive the polished score even when it was rejected, by asking
        # the same question production asked: run the restart with the keep
        # threshold at zero so the polished point is always returned.
        if adopted:
            polished = after
        else:
            opt_mod._LBFGSB_RESTART_KEEP_REL = 0.0
            try:
                probe = real(best, objective, bounds, args, maxiter,
                             batch_objective, fd_eps)
                polished = float(
                    objective(np.asarray(probe.x, dtype=float), *args))
            finally:
                opt_mod._LBFGSB_RESTART_KEEP_REL = (
                    saved if keep_rel is None else keep_rel)
        scale = max(abs(prior), 1e-12)
        record.append({
            "prior": prior,
            "polished": polished,
            "returned": after,
            "rel": (prior - polished) / scale,
            "adopted": adopted,
        })
        return out

    if keep_rel is not None:
        opt_mod._LBFGSB_RESTART_KEEP_REL = keep_rel
    with mock.patch.object(opt_mod, "_lbfgsb_restart", wrapper):
        try:
            yield record
        finally:
            opt_mod._LBFGSB_RESTART_KEEP_REL = saved


@contextmanager
def capture_starts(record, maxiter_factor=1):
    """Hook ``optimizer:_multi_start_minimize``.

    Records, per call: how many candidates were handed in, how many were
    scored, how many were actually refined (``_MULTI_START_SOLVES``), the
    production ``maxiter``, and per refined start the scipy ``nit``/``nfev``/
    ``status``.  ``maxiter_factor`` multiplies the budget -- the perturbation
    arm for the iteration-budget finding.
    """
    real = opt_mod._multi_start_minimize
    real_scoped = opt_mod._scoped_minimize

    def wrapper(objective, candidates, bounds, args=(), maxiter=300,
                batch_objective=None, fd_eps=1e-4):
        entry = {
            "candidates": len(candidates),
            "maxiter": int(maxiter * maxiter_factor),
            "prod_maxiter": maxiter,
            "solves": [],
        }
        record.append(entry)

        def scoped(*a, **kw):
            res = real_scoped(*a, **kw)
            try:
                entry["solves"].append({
                    "nit": int(res.nit), "nfev": int(res.nfev),
                    "status": int(res.status), "fun": float(res.fun),
                })
            except Exception:
                pass
            return res

        with mock.patch.object(opt_mod, "_scoped_minimize", scoped):
            return real(objective, candidates, bounds, args=args,
                        maxiter=int(maxiter * maxiter_factor),
                        batch_objective=batch_objective, fd_eps=fd_eps)

    with mock.patch.object(opt_mod, "_multi_start_minimize", wrapper):
        yield record


# --------------------------------------------------------------------------
# RESULT plumbing
# --------------------------------------------------------------------------
def emit(name, value, unit=""):
    if isinstance(value, float):
        print(f"RESULT {name}={value:.6g} {unit}".rstrip())
    else:
        print(f"RESULT {name}={value} {unit}".rstrip())


def _swapins():
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        for line in out.splitlines():
            if line.strip().startswith("Swapins"):
                return int(line.split(":")[1].strip().rstrip("."))
    except Exception:
        pass
    return -1


class Conditions:
    """Measures the thread factor over the measured section itself."""

    def __init__(self):
        self.cpu = time.process_time()
        self.thr = time.thread_time()

    def emit(self):
        cpu = time.process_time() - self.cpu
        thr = time.thread_time() - self.thr
        factor = cpu / thr if thr > 0 else float("nan")
        emit("thread_factor", round(factor, 4))
        emit("load1", round(os.getloadavg()[0], 2))
        emit("swapins", _swapins())


def loo(values):
    """(mean, min, max, mean with the single most favourable cell dropped).

    'Most favourable' = the largest value, since every D0 aggregate here is a
    gap that a finding wants to be large.
    """
    v = sorted(float(x) for x in values)
    if not v:
        return float("nan"), float("nan"), float("nan"), float("nan")
    mean = sum(v) / len(v)
    drop = sum(v[:-1]) / (len(v) - 1) if len(v) > 1 else float("nan")
    return mean, v[0], v[-1], drop
