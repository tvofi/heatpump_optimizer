"""VERIFIER-OWN harness for D0-02 (seat verify-0-1, round 4).

METRIC (one line): over a grid covering BOTH ``_multi_start_minimize`` call
sites (dhw=True -> the maxiter=300 DHW path at optimizer.py:3003, dhw=False ->
the maxiter=200 space-only path at optimizer.py:3529), the number of L-BFGS-B
calls (observed at the scipy boundary, ``optimizer.minimize`` -- one level
below the finder's ``_scoped_minimize`` hook) that terminate on the iteration
cap (scipy status==1 or nit >= the maxiter production passed), together with
max/median nit and the objective change from (a) capping maxiter at the
TIGHTEST value the census says is safe (the grid-wide max nit, rounded up --
sharper than the finder's x15 probe: if even that changes no plan, the
headroom is exactly max_nit/cap) and (b) the maxiter=3 starvation
tests/optimality.py challenger 3 uses, replicated here to confirm the
existing gate fires on starvation while the budget has slack.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/d0_own_D0-02.py

BASELINE SHA the finding was measured against: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOLS: custom_components/heatpump_optimizer/optimizer.py
:minimize (observed at the scipy boundary) and :_multi_start_minimize (its
``maxiter`` argument overridden per arm), driving
``HeatPumpOptimizer.optimize``.

PERTURBATION (executed inside this harness): override the ``maxiter``
``_multi_start_minimize`` receives, 200/300 -> 3 -- the exact cut
tests/optimality.py's challenger 3 makes.  The census must flip to
all-solves-on-cap and the objective must worsen; the metric moves, it is
simply zero at the shipped budget.

NULL CONTROL: the ``flat`` price rows, reported separately.
CONTENTION: objective values, ratios and iteration counts only; no timing
claim.  thread_factor/load1/swapins/concurrent-process count printed for the
record.
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

PRICE_SUBSET = ("winter_typical", "winter_extreme", "summer_negative",
                "shoulder")
FLAT = "flat"
START = datetime(2026, 1, 15)
WEATHER = "winter_cold"


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


def build_cell(price_p, two_zone, dhw):
    cfg = house(two_zone=two_zone, dhw=dhw)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(WEATHER, START)
    steps = int(round(24 / DT))
    pr, ot, wi, ra, so = (a[:steps] for a in (pr, ot, wi, ra, so))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=50.0)
    return o, m, pr, ot, wi, ra, so, st, START


census = []


@contextmanager
def observe_scipy(maxiter_override=None):
    """Observe every scipy-level minimize call; optionally starve maxiter.

    The override is applied to the options dict the production call carries
    (the same place a one-line production edit of the ``maxiter`` constants
    would land); observed, passed through, and counted.
    """
    def min_wrapper(*a, **kw):
        if maxiter_override is not None:
            opts = dict(kw.get("options") or {})
            if "maxiter" in opts:
                opts["maxiter"] = maxiter_override
                kw["options"] = opts
        res = _scipy_minimize(*a, **kw)
        try:
            opts = kw.get("options") or {}
            census.append({
                "ftol_opt": opts.get("ftol"), "eps_opt": opts.get("eps"),
                "maxiter_passed": opts.get("maxiter"),
                "nit": int(res.nit), "status": int(res.status),
            })
        except Exception:
            census.append({"nit": -1, "status": -1, "maxiter_passed": None,
                           "ftol_opt": None, "eps_opt": None})
        return res

    with mock.patch.object(O, "minimize", min_wrapper):
        yield


def run(price_p, tz, dhw, maxiter_override=None):
    cell = build_cell(price_p, tz, dhw)
    o, m, pr, ot, wi, ra, so, st, start = cell
    with observe_scipy(maxiter_override):
        r = o.optimize(st, pr, ot, wi, ra, so, start)
    return float(r.objective_value)


def main() -> int:
    cond = Conditions()
    grid = [(p, tz, dhw)
            for p in PRICE_SUBSET + (FLAT,)
            for tz in (False, True)
            for dhw in (True, False)]

    # -- arm 0: shipped budget, full census at the scipy boundary ----------
    base = {}
    n0 = len(census)
    for p, tz, dhw in grid:
        base[(p, tz, dhw)] = run(p, tz, dhw)
        print(f"CELL base {p:16s} tz={int(tz)} dhw={int(dhw)} "
              f"J={base[(p, tz, dhw)]:.5f} solves_so_far={len(census) - n0}",
              flush=True)
    ship = census[:]

    on_cap_ship = sum(1 for c in ship
                      if c["status"] == 1 or (c["maxiter_passed"] is not None
                                              and c["nit"] >= c["maxiter_passed"]))
    max_nit = max(c["nit"] for c in ship)
    tight_cap = max_nit  # tightest cap the census says cannot bind

    # -- arm 1: maxiter pinned to the observed max nit (tightest safe cap) --
    arm1 = {}
    n1 = len(census)
    for p, tz, dhw in grid:
        arm1[(p, tz, dhw)] = run(p, tz, dhw, maxiter_override=tight_cap)
    cap1 = census[n1:]
    on_cap1 = sum(1 for c in cap1
                  if c["status"] == 1 or (c["maxiter_passed"] is not None
                                          and c["nit"] >= c["maxiter_passed"]))
    gaps1 = {k: (base[k] - arm1[k]) / max(abs(base[k]), 1e-12) * 100.0
             for k in base}

    # -- arm 2: the optimality.py challenger-3 starvation, maxiter = 3 ------
    arm2 = {}
    n2 = len(census)
    for p, tz, dhw in grid:
        arm2[(p, tz, dhw)] = run(p, tz, dhw, maxiter_override=3)
    cap2 = census[n2:]
    on_cap2 = sum(1 for c in cap2 if c["status"] == 1)
    gaps2 = {k: (base[k] - arm2[k]) / max(abs(base[k]), 1e-12) * 100.0
             for k in base}

    priced = [k for k in base if k[0] != FLAT]
    flat = [k for k in base if k[0] == FLAT]

    emit("own_cells_total", len(grid))
    emit("own_cells_priced", len(priced))
    emit("own_cells_flat_null_control", len(flat))
    # census, shipped budget, both call sites
    emit("own_solves_observed_scipy_boundary", len(ship))
    emit("own_solves_on_cap_shipped", on_cap_ship)
    emit("own_max_nit_shipped", max_nit)
    emit("own_median_nit_shipped", float(np.median([c["nit"] for c in ship])))
    emit("own_maxiter_values_seen",
         sorted({c["maxiter_passed"] for c in ship if c["maxiter_passed"]}))
    emit("own_max_nit_dhw_path_300",
         max((c["nit"] for c in ship if c["maxiter_passed"] == 300),
             default=-1))
    emit("own_max_nit_space_path_200",
         max((c["nit"] for c in ship if c["maxiter_passed"] == 200),
             default=-1))
    # arm 1: tightest safe cap
    emit("own_tight_cap_used", tight_cap)
    emit("own_solves_on_cap_tight", on_cap1)
    emit("own_max_abs_gap_tightcap_priced_pct",
         max(abs(gaps1[k]) for k in priced), "%")
    emit("own_max_abs_gap_tightcap_flat_pct",
         max(abs(gaps1[k]) for k in flat), "%")
    emit("own_cells_plan_changed_tightcap",
         sum(1 for k in base if abs(gaps1[k]) > 1e-9))
    # arm 2: starvation (the existing gate's cut)
    emit("own_solves_on_cap_starved3", on_cap2)
    emit("own_solves_observed_starved3", len(cap2))
    emit("own_mean_gap_starved3_priced_pct",
         sum(gaps2[k] for k in priced) / len(priced), "%")
    emit("own_max_gap_starved3_priced_pct", max(gaps2[k] for k in priced), "%")
    emit("own_min_gap_starved3_priced_pct", min(gaps2[k] for k in priced), "%")
    emit("own_mean_gap_starved3_flat_pct",
         sum(gaps2[k] for k in flat) / len(flat), "%")
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
