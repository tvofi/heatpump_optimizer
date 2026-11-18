"""Shared rig for the D0 (price optimality) harnesses of audit round 3.

Not a harness itself: no RESULT lines, no __main__ measurement. It gives the
harnesses in this directory (a) the BLAS thread pin, (b) the environment
RESULT trio, (c) scenario construction over tests/profiles.py, and (d) the
capture/replace idiom around
``heatpump_optimizer.optimizer:_multi_start_minimize`` that every D0 number
rests on.

Import it from a harness run from the repository root with
PYTHONPATH=tests/hastub. Baseline SHA ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
import threading
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402

from profiles import prices as _prices, weather as _weather, house, DT, N  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer import optimizer as optimizer_module  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)

PRICE_PROFILES = ("winter_typical", "winter_extreme", "summer_typical",
                  "summer_negative", "shoulder", "winter_narrow",
                  "winter_moderate", "flat")
WEATHER_PROFILES = ("winter_cold", "winter_mild", "summer_warm",
                    "summer_cool", "shoulder")

START = datetime(2026, 1, 15)


# ----------------------------------------------------------------------
# environment RESULT lines (harness contract)
# ----------------------------------------------------------------------
def thread_factor():
    """process CPU / single-thread CPU over one fixed BLAS-heavy burn."""
    a = np.random.default_rng(3).standard_normal((320, 320))

    def burn():
        for _ in range(12):
            a @ a
    t0w, t0c = time.monotonic(), time.process_time()
    burn()
    w, c = time.monotonic() - t0w, time.process_time() - t0c
    return (c / w) if w > 0 else float("nan")


def load1():
    try:
        return os.getloadavg()[0]
    except OSError:  # pragma: no cover
        return float("nan")


def swapins():
    try:
        import subprocess
        out = subprocess.run(["sysctl", "-n", "vm.swapusage"],
                             capture_output=True, text=True, timeout=10).stdout
        return out.strip().replace(" ", "")
    except Exception:  # pragma: no cover
        return "unavailable"


def print_env():
    print(f"RESULT thread_factor={thread_factor():.3f}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    print(f"RESULT concurrent_python={_concurrent()}")


def _concurrent():
    try:
        import subprocess
        out = subprocess.run(["ps", "-axo", "comm"], capture_output=True,
                             text=True, timeout=10).stdout
        return sum(1 for line in out.splitlines() if "python" in line.lower())
    except Exception:  # pragma: no cover
        return -1


# ----------------------------------------------------------------------
# scenario construction
# ----------------------------------------------------------------------
def build(price_p="winter_typical", weather_p="winter_cold", two_zone=False,
          dhw=False, horizon_hours=24, start=START, **house_over):
    """One solvable cell: (optimizer, model, args-for-optimize, state)."""
    cfg = house(two_zone=two_zone, **house_over)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = bool(dhw)
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon_hours, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = _prices(price_p, start)
    ot, wi, ra, so = _weather(weather_p, start)
    n = int(round(horizon_hours / DT))
    if n > N:
        reps = int(np.ceil(n / N))
        pr = np.tile(pr, reps)[:n]
        ot, wi, ra, so = (np.tile(v, reps)[:n] for v in (ot, wi, ra, so))
    else:
        pr, ot, wi, ra, so = (v[:n] for v in (pr, ot, wi, ra, so))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return opt, m, (st, pr, ot, wi, ra, so, start), st


def comfort_of(m, power, st, ot, wi, ra, so, min_temp=17.0, max_temp=23.0):
    """Per-step comfort feasibility of a space-power schedule."""
    room, slab, up, lo, _, _, _ = m.simulate_trajectory(st, power, ot, wi, ra, so, DT)
    r = np.asarray(room[1:], dtype=float)
    return {
        "below_degree_steps": float(np.maximum(0.0, min_temp - r).sum()),
        "above_degree_steps": float(np.maximum(0.0, r - max_temp).sum()),
        "min": float(r.min()), "max": float(r.max()),
    }


# ----------------------------------------------------------------------
# the capture idiom (tests/optimality.py) around _multi_start_minimize
# ----------------------------------------------------------------------
class Capture:
    """Records every production ``_multi_start_minimize`` call verbatim."""

    def __init__(self):
        self.calls = []

    @contextmanager
    def record(self):
        real = optimizer_module._multi_start_minimize

        def spy(objective, candidates, bounds, args=(), maxiter=300,
                batch_objective=None, fd_eps=1e-4):
            res = real(objective, candidates, bounds, args=args,
                       maxiter=maxiter, batch_objective=batch_objective,
                       fd_eps=fd_eps)
            self.calls.append({
                "objective": objective,
                "candidates": [np.array(c, dtype=float) for c in candidates],
                "bounds": list(bounds),
                "args": args,
                "maxiter": maxiter,
                "batch_objective": batch_objective,
                "fd_eps": fd_eps,
                "result": res,
                "nit": int(getattr(res, "nit", -1)),
                "nfev": int(getattr(res, "nfev", -1)),
                "status": int(getattr(res, "status", -1)),
                "message": str(getattr(res, "message", "")),
                "fun": float(getattr(res, "fun", np.nan)),
                "batched": (batch_objective is not None
                            and optimizer_module._bounds_supported_by_batch(
                                list(bounds))),
            })
            return res

        with mock.patch.object(optimizer_module, "_multi_start_minimize", spy):
            yield self


@contextmanager
def solver(fn):
    """Replace the production multi-start with ``fn`` for one solve."""
    with mock.patch.object(optimizer_module, "_multi_start_minimize", fn):
        yield


@contextmanager
def all_candidates_refined():
    """Lift ``_MULTI_START_SOLVES`` so no scored candidate is discarded."""
    old = optimizer_module._MULTI_START_SOLVES
    optimizer_module._MULTI_START_SOLVES = 10**6
    try:
        yield old
    finally:
        optimizer_module._MULTI_START_SOLVES = old


def stronger(maxiter_mul=10, extra_seed_levels=(0.0, 0.25, 0.5, 0.75, 1.0),
             polish=True, counter=None):
    """A drop-in ``_multi_start_minimize`` that searches strictly harder.

    Identical closure, bounds, args, jac path and ``fd_eps`` -- it only ever
    calls the production ``_multi_start_minimize`` itself, so the batched
    gradient serves exactly the bound shapes production would serve.
    """
    real = optimizer_module._multi_start_minimize

    def fn(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4):
        lo = np.array([b[0] for b in bounds], dtype=float)
        hi = np.array([b[1] for b in bounds], dtype=float)
        seeds = [np.array(c, dtype=float) for c in candidates]
        for f in extra_seed_levels:
            seeds.append(np.clip(lo + f * (hi - lo), lo, hi))
        results = []
        with all_candidates_refined():
            results.append(real(objective, seeds, bounds, args=args,
                                maxiter=maxiter * maxiter_mul,
                                batch_objective=batch_objective,
                                fd_eps=fd_eps))
            if polish:
                best = min(results, key=lambda r: float(objective(r.x, *args)))
                results.append(real(objective, [np.array(best.x, dtype=float)],
                                    bounds, args=args,
                                    maxiter=maxiter * maxiter_mul,
                                    batch_objective=batch_objective,
                                    fd_eps=fd_eps))
        if counter is not None:
            counter["calls"] = counter.get("calls", 0) + 1
        return min(results, key=lambda r: float(objective(r.x, *args)))

    return fn


# ----------------------------------------------------------------------
# hot-water capture and replacement
# ----------------------------------------------------------------------
import dataclasses  # noqa: E402

from heatpump_optimizer.optimizer import HeatPumpOptimizer as _HPO  # noqa: E402


@contextmanager
def capture_dhw(store):
    """Record the last ``_plan_dhw_cheapest_first`` kwargs and the DhwPlan.

    ``requirement``, ``draw_rates``, ``max_temp``, ``min_run_power`` and
    ``p_dhw_max`` are exactly the arrays the shipped hot-water planner used,
    so a challenger scored against them is scored against production's own
    feasibility contract, not a re-derived one.
    """
    greedy = _HPO._plan_dhw_cheapest_first
    build = _HPO._build_dhw_requirements

    def spy_greedy(self, *a, **kw):
        store["greedy_kwargs"] = dict(kw)
        return greedy(self, *a, **kw)

    def spy_build(self, *a, **kw):
        plan = build(self, *a, **kw)
        store["plan"] = plan
        return plan

    with mock.patch.object(_HPO, "_plan_dhw_cheapest_first", spy_greedy), \
            mock.patch.object(_HPO, "_build_dhw_requirements", spy_build):
        yield store


@contextmanager
def force_dhw(schedule):
    """Run a solve with the INITIAL hot-water schedule replaced.

    Only the first plan is replaced -- the one ``_optimize_with_dhw`` hands to
    the space stage. ``_co_optimize``'s re-plan call (the one carrying
    ``space_demand``) is left entirely alone, so the co-optimisation pass still
    does its own work and can still reject the challenger. Replacing that call
    too would silently disable the pass and the comparison would be against a
    different pipeline, not a different hot-water schedule.
    """
    build = _HPO._build_dhw_requirements

    def forced(self, *a, **kw):
        plan = build(self, *a, **kw)
        if kw.get("space_demand") is not None:
            return plan
        return dataclasses.replace(plan, schedule=np.array(schedule, dtype=float))

    with mock.patch.object(_HPO, "_build_dhw_requirements", forced):
        yield


def dhw_feasible(model, schedule, kw, tol=1e-6):
    """Tank feasibility of a hot-water schedule against production's own arrays."""
    temps = np.asarray(model.simulate_dhw_only(
        initial_temp=kw["initial_temp"],
        dhw_power_schedule=np.asarray(schedule, dtype=float),
        outdoor_temps=kw["outdoor_temps"],
        draw_rates=kw["draw_rates"],
        dt_hours=kw["dt"],
    ), dtype=float)
    req = np.asarray(kw["requirement"], dtype=float)
    mx = np.asarray(kw["max_temp"], dtype=float)
    if mx.ndim == 0:
        mx = np.full(req.size, float(mx))
    short = float(np.maximum(0.0, req - temps[1:]).sum())
    over = float(np.maximum(0.0, temps[1:] - mx).sum())
    return temps, short, over


def stronger_price_seeds(prices, p_max, dt, fractions=(0.2, 0.4, 0.6, 0.8,
                                                       1.0, 1.2, 1.5),
                         maxiter_mul=1):
    """A ``_multi_start_minimize`` given the bang-bang seed FAMILY.

    Production seeds two members of this family: the baseline energy and
    ``_LOW_ENERGY_START_FRACTION`` (0.35) of it. This hands the same
    ``_price_ranked_start`` builder the whole ladder, clipped into the same
    bounds. Everything else -- closure, bounds, args, maxiter, ftol, fd_eps,
    the batched jac -- is production's.
    """
    real = optimizer_module._multi_start_minimize
    ranked = optimizer_module._price_ranked_start

    def fn(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4):
        lo = np.array([b[0] for b in bounds], dtype=float)
        hi = np.array([b[1] for b in bounds], dtype=float)
        n = lo.size
        pr = np.asarray(prices, dtype=float)[:n]
        seeds = [np.array(c, dtype=float) for c in candidates]
        base_energy = max(
            float(np.sum(np.asarray(c, dtype=float)) * dt) for c in candidates
        )
        for f in fractions:
            s = ranked(pr, base_energy * f, p_max, dt)
            seeds.append(np.clip(np.minimum(s, hi), lo, hi))
        with all_candidates_refined():
            return real(objective, seeds, bounds, args=args,
                        maxiter=maxiter * maxiter_mul,
                        batch_objective=batch_objective, fd_eps=fd_eps)

    return fn
