"""Verifier 3's OWN harness for D0-02 (finder harness re-run separately).

METRIC (one line): over a WIDER configuration grid than the finder's
(horizons 6/24/48 h with profiles tiled to the horizon, DHW on AND off,
single- and two-zone, three price profiles including the flat null control),
(a) the census of every L-BFGS-B call production makes -- how many terminate
on the iteration cap (scipy ``status == 1`` or ``nit >= maxiter`` passed),
the max and median ``nit`` against the caps 200/300 -- and (b) the relative
objective change ``(J_prod - J_x15)/|J_prod|`` from multiplying production's
``maxiter`` by 15 at ``_scoped_minimize``; plus (c) a wiring check that the
census metric MOVES: with production's ``maxiter`` cut to 3 (the cut
``tests/optimality.py`` challenger 3 makes) the cap must bind on every solve.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/own_v3_D0_02.py

EXPECTED (verifier 3, tree 3e91f85 == baseline 7dd68dd for the hooked files):
``solves_terminating_on_maxiter=0`` across the whole wider grid, max ``nit``
far under 200, ``max_gain_maxiter_x15_priced_pct`` exactly 0, and the
starved wiring check binding on every solve.  The numbers are the evidence.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (measured at tree
3e91f85, identical for the files this hooks)
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_multi_start_minimize (census; per-solve nit/status captured at
``_scoped_minimize``) driving ``HeatPumpOptimizer.optimize``.

PERTURBATION: cut production's ``maxiter`` to 3 -> the census must report
every solve on the cap and the objective must worsen (this is the metric's
movement proof); multiply ``maxiter`` by 15 -> no plan may change.

NULL CONTROL: the ``flat`` price rows, aggregated separately.

CONTENTION: iteration counts and objective ratios only; no timing claim.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

START = datetime(2026, 1, 15)
_real_ms = O._multi_start_minimize
_real_scoped = O._scoped_minimize


def emit(name, value, unit=""):
    if isinstance(value, float):
        print(f"RESULT {name}={value:.6g} {unit}".rstrip())
    else:
        print(f"RESULT {name}={value} {unit}".rstrip())


def tile(a, steps):
    s = np.asarray(a, dtype=float)
    return s[:steps] if len(s) >= steps else np.tile(
        s, int(np.ceil(steps / len(s))))[:steps]


def build(price_p, weather_p, tz, dhw, horizon_h):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon_h, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    steps = int(round(horizon_h / DT))
    pr = tile(prices(price_p, START), steps)
    ot, wi, ra, so = (tile(a, steps) for a in weather(weather_p, START))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=50.0)
    return o, pr, ot, wi, ra, so, st


def solve(cell):
    o, pr, ot, wi, ra, so, st = cell
    return o.optimize(st, pr, ot, wi, ra, so, START)


def census(cell, sink, maxiter_factor=1.0):
    """Solve one cell recording every L-BFGS-B call's nit/status/nfev/maxiter."""
    def ms(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4):
        cap = int(maxiter * maxiter_factor)
        entry = {"prod_maxiter": int(maxiter), "cap": cap, "solves": []}
        sink.append(entry)

        def scoped(*a, **kw):
            res = _real_scoped(*a, **kw)
            try:
                entry["solves"].append({
                    "nit": int(res.nit), "nfev": int(res.nfev),
                    "status": int(res.status), "maxiter": int(
                        (kw.get("options") or {}).get("maxiter", -1))})
            except Exception:
                pass
            return res

        with mock.patch.object(O, "_scoped_minimize", scoped):
            return _real_ms(objective, candidates, bounds, args=args,
                            maxiter=cap, batch_objective=batch_objective,
                            fd_eps=fd_eps)

    with mock.patch.object(O, "_multi_start_minimize", ms):
        return solve(cell)


# Wider than the finder's grid: horizons, DHW off, both topologies.
CELLS = (
    ("winter_typical", "winter_cold", True,  True,  6),
    ("summer_negative", "winter_cold", True,  True,  6),
    ("flat",            "winter_cold", True,  True,  6),
    ("winter_typical", "winter_cold", False, True,  6),
    ("winter_typical", "winter_cold", True,  True,  24),
    ("summer_negative", "winter_cold", True,  True,  24),
    ("flat",            "winter_cold", True,  True,  24),
    ("winter_typical", "winter_cold", False, True,  24),
    ("winter_typical", "winter_cold", True,  False, 24),
    ("winter_typical", "winter_cold", True,  True,  48),
    ("winter_extreme", "winter_cold", True,  True,  48),
    ("summer_negative", "winter_cold", True,  True,  48),
    ("flat",            "winter_cold", True,  True,  48),
    ("winter_typical", "winter_cold", False, True,  48),
    ("winter_typical", "winter_cold", True,  False, 48),
)


def main() -> int:
    cpu0, thr0 = time.process_time(), time.thread_time()
    solves = 0
    on_cap = 0
    nits = []
    rows = []
    for price_p, weather_p, tz, dhw, h in CELLS:
        cell = build(price_p, weather_p, tz, dhw, h)
        sink = []
        base = census(cell, sink)
        for e in sink:
            for s in e["solves"]:
                solves += 1
                nits.append(s["nit"])
                if s["status"] == 1 or s["nit"] >= s["maxiter"]:
                    on_cap += 1
        # x15 arm on the same cell
        sink15 = []
        big = census(cell, sink15, maxiter_factor=15)
        j0 = float(base.objective_value)
        j15 = float(big.objective_value)
        gain = (j0 - j15) / abs(j0) * 100.0
        rows.append({"cell": f"{price_p}/tz{int(tz)}/dhw{int(dhw)}/h{h}",
                     "priced": price_p != "flat", "gain": gain})
        print(f"CELL {rows[-1]['cell']:40s} J={j0:.5f} x15 {gain:+.6f}%  "
              f"max_nit_here={max(s['nit'] for e in sink for s in e['solves'])}"
              f"/cap {max(e['cap'] for e in sink)}", flush=True)

    for scope in ("priced", "flat"):
        v = [r["gain"] for r in rows if r["priced"] == (scope == "priced")]
        emit(f"own_max_gain_maxiter_x15_{scope}_pct", max(v), "%")
        emit(f"own_mean_gain_maxiter_x15_{scope}_pct",
             sum(v) / len(v), "%")
        emit(f"own_cells_maxiter_x15_changed_{scope}",
             sum(1 for x in v if abs(x) > 1e-9))
    emit("own_cells_total", len(rows))
    emit("own_lbfgsb_solves_observed", solves)
    emit("own_solves_terminating_on_maxiter", on_cap)
    emit("own_max_nit_observed", max(nits))
    emit("own_median_nit_observed", float(np.median(nits)))
    emit("own_p95_nit_observed", float(np.percentile(nits, 95)))

    # Wiring: starve maxiter to 3 on two cells; the cap MUST bind everywhere
    # and the objective MUST worsen -- the census metric moves.
    starved_on_cap = 0
    starved_solves = 0
    worse = 0
    for price_p, weather_p, tz, dhw, h in CELLS[4:6] + CELLS[9:11]:
        cell = build(price_p, weather_p, tz, dhw, h)
        sink = []
        base = census(cell, sink)
        sink3 = []

        # census() multiplies PRODUCTION's maxiter by a factor; to hit 3 we
        # patch _multi_start_minimize's maxiter argument directly instead.
        def ms3(objective, candidates, bounds, args=(), maxiter=300,
                batch_objective=None, fd_eps=1e-4, _cell=cell):
            entry = {"prod_maxiter": int(maxiter), "cap": 3, "solves": []}
            sink3.append(entry)

            def scoped(*a, **kw):
                res = _real_scoped(*a, **kw)
                entry["solves"].append({
                    "nit": int(res.nit), "nfev": int(res.nfev),
                    "status": int(res.status), "maxiter": int(
                        (kw.get("options") or {}).get("maxiter", -1))})
                return res

            with mock.patch.object(O, "_scoped_minimize", scoped):
                return _real_ms(objective, candidates, bounds, args=args,
                                maxiter=3, batch_objective=batch_objective,
                                fd_eps=fd_eps)

        with mock.patch.object(O, "_multi_start_minimize", ms3):
            starved = solve(cell)
        for e in sink3:
            for s in e["solves"]:
                starved_solves += 1
                if s["status"] == 1 or s["nit"] >= s["maxiter"]:
                    starved_on_cap += 1
        if float(starved.objective_value) > float(base.objective_value) + 1e-9:
            worse += 1
    emit("own_starved_solves_observed", starved_solves)
    emit("own_starved_solves_on_cap", starved_on_cap)
    emit("own_starved_cells_objective_worse", worse, "of 4")

    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    emit("thread_factor", round(cpu / thr if thr > 0 else float("nan"), 4))
    emit("load1", round(os.getloadavg()[0], 2))
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        swapins = next(int(l.split(":")[1].strip().rstrip("."))
                       for l in out.splitlines()
                       if l.strip().startswith("Swapins"))
    except Exception:
        swapins = -1
    emit("swapins", swapins)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
