"""Verifier 3's OWN harness for D0-01 (finder harness re-run separately).

METRIC (one line): per grid cell on a grid the finder did NOT cover
(horizons 6 h and 48 h -- profiles tiled to the horizon, unlike the finder's
24 h-only grid -- DHW OFF cells, a warm-weather 48 h cell and single-zone 48 h
cells), three numbers: (a) the two-arm relative objective gap
``(J_prod - J_ftol14)/|J_prod|`` where the only change is L-BFGS-B ``ftol``
1e-6 -> 1e-14 forced at ``optimizer._scoped_minimize``; (b) the POLISH drop
``(J_prod - J_polish)/|J_prod|`` where ``_lbfgsb_restart`` is replaced by a
replica of itself with ``ftol`` 1e-14 and ANY strict improvement adopted --
i.e. how much objective plain continued descent from production's own stopping
point still finds, no new seed, no re-solve of the multi-start; (c) comfort
parity of both challengers against production (degree-steps below the 17 C
floor over the room trajectory).  ``J`` is ``OptimizationResult.objective_value``,
which production re-evaluates on the final schedule.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/own_v3_D0_01.py

EXPECTED (verifier 3, tree 3e91f85 == baseline 7dd68dd for optimizer.py and
tests/profiles.py): a non-empty set of cells with gap > 0.01 % on BOTH arms,
zero cells with a negative gap, zero cells where either challenger is worse on
comfort, and the wiring checks at the end both passing (ftol forced on both
arms -> gap exactly 0; ftol 1e-4 on the challenger arm -> gap grows).  No
tolerance is asserted by the harness itself; the numbers are the evidence.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (measured at tree
3e91f85, identical for the files this hooks)
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_scoped_minimize (ftol arm) and :_lbfgsb_restart (polish arm), both driving
``optimizer.py:HeatPumpOptimizer.optimize``.

PERTURBATION: the wiring section at the end forces ``ftol`` 1e-14 into BOTH
arms (gap must collapse to exactly 0) and 1e-4 into the challenger arm (gap
must grow), on four cells.

NULL CONTROL: the ``flat`` price rows, aggregated separately.

CONTENTION: objective values and ratios only; no wall/CPU/RSS claim.
"""
from __future__ import annotations

import os

# Thread pin FIRST (harness contract).
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
MIN_TEMP = 17.0
_real_scoped = O._scoped_minimize


def emit(name, value, unit=""):
    if isinstance(value, float):
        print(f"RESULT {name}={value:.6g} {unit}".rstrip())
    else:
        print(f"RESULT {name}={value} {unit}".rstrip())


def tile(a, steps):
    s = np.asarray(a, dtype=float)
    if len(s) >= steps:
        return s[:steps]
    return np.tile(s, int(np.ceil(steps / len(s))))[:steps]


def build(price_p, weather_p, tz, dhw, horizon_h):
    """My own cell builder: profiles TILED to the horizon, not truncated."""
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
    return (o, pr, ot, wi, ra, so, st)


def solve(cell):
    o, pr, ot, wi, ra, so, st = cell
    return o.optimize(st, pr, ot, wi, ra, so, START)


def scoped_ftol(ftol):
    def arm(*a, **kw):
        kw = dict(kw)
        opts = dict(kw.get("options") or {})
        opts["ftol"] = ftol
        kw["options"] = opts
        return _real_scoped(*a, **kw)
    return arm


def tight_restart(best, objective, bounds, args, maxiter, batch_objective,
                  fd_eps):
    """Replica of production's ``_lbfgsb_restart`` with ftol 1e-14 and ANY
    strict improvement adopted (production demands > 2 % relative).  No new
    seed: it starts from the exact point production's own stop returned."""
    jac = None
    if batch_objective is not None and O._bounds_supported_by_batch(bounds):
        def jac(x, *a):
            return O._batch_fd_gradient(
                batch_objective, a, x, float(objective(x, *a)), fd_eps, bounds)
    try:
        polished = _real_scoped(
            objective, np.asarray(best.x, dtype=float), args=args, jac=jac,
            method="L-BFGS-B", bounds=bounds,
            options={"maxiter": maxiter, "ftol": 1e-14, "eps": 1e-4})
    except Exception:
        return best
    score = float(objective(polished.x, *args))
    prior = float(objective(best.x, *args))
    if np.isfinite(score) and score < prior - 1e-12:
        return polished
    return best


def comfort(result):
    room = np.asarray(result.room_temp_trajectory, dtype=float)[1:]
    return float(np.maximum(0.0, MIN_TEMP - room).sum())


def loo(vals):
    v = sorted(float(x) for x in vals)
    mean = sum(v) / len(v)
    drop = sum(v[:-1]) / (len(v) - 1) if len(v) > 1 else float("nan")
    return mean, v[0], v[-1], drop


# My grid: horizons the finder did not cover, DHW OFF, warm weather, 1-zone.
CELLS = (
    # (price, weather, tz, dhw, horizon_h)
    ("winter_typical", "winter_cold", True, True, 6),
    ("winter_extreme", "winter_cold", True, True, 6),
    ("summer_negative", "winter_cold", True, True, 6),
    ("flat", "winter_cold", True, True, 6),
    ("winter_typical", "winter_cold", False, True, 6),
    ("summer_negative", "winter_cold", False, True, 6),
    ("winter_typical", "winter_cold", True, True, 48),
    ("winter_extreme", "winter_cold", True, True, 48),
    ("summer_negative", "winter_cold", True, True, 48),
    ("flat", "winter_cold", True, True, 48),
    ("winter_typical", "winter_cold", True, False, 48),
    ("summer_negative", "winter_cold", True, False, 48),
    ("flat", "winter_cold", True, False, 48),
    ("winter_typical", "summer_warm", True, True, 48),
    ("shoulder", "summer_warm", True, True, 48),
    ("winter_extreme", "winter_cold", False, True, 48),
    ("summer_negative", "winter_cold", False, True, 48),
    ("flat", "winter_cold", False, True, 48),
)


def main() -> int:
    cpu0, thr0 = time.process_time(), time.thread_time()
    rows = []
    for price_p, weather_p, tz, dhw, h in CELLS:
        cell = build(price_p, weather_p, tz, dhw, h)
        a = solve(cell)                                # production
        with mock.patch.object(O, "_scoped_minimize", scoped_ftol(1e-14)):
            b = solve(cell)                            # ftol arm
        with mock.patch.object(O, "_lbfgsb_restart", tight_restart):
            c = solve(cell)                            # polish arm
        ja, jb, jc = (float(r.objective_value) for r in (a, b, c))
        row = {
            "cell": f"{price_p}/{weather_p}/tz{int(tz)}/dhw{int(dhw)}/h{h}",
            "priced": price_p != "flat", "Ja": ja, "Jb": jb, "Jc": jc,
            "gap_ftol": (ja - jb) / abs(ja) * 100.0,
            "gap_polish": (ja - jc) / abs(ja) * 100.0,
            "va": comfort(a), "vb": comfort(b), "vc": comfort(c),
            "p0a": float(a.power_schedule[0]),
            "p0b": float(b.power_schedule[0]),
        }
        rows.append(row)
        print(f"CELL {row['cell']:46s} J={ja:.5f}  "
              f"ftol14={row['gap_ftol']:+.4f}%  polish={row['gap_polish']:+.4f}%  "
              f"viol {row['va']:.4f}/{row['vb']:.4f}/{row['vc']:.4f}  "
              f"p0 {row['p0a']:.4f}->{row['p0b']:.4f}", flush=True)

    for arm in ("gap_ftol", "gap_polish"):
        for scope in ("priced", "flat"):
            v = [r[arm] for r in rows if r["priced"] == (scope == "priced")]
            m, lo_, hi_, drop = loo(v)
            emit(f"own_{arm}_{scope}_mean_pct", m, "%")
            emit(f"own_{arm}_{scope}_max_pct", hi_, "%")
            emit(f"own_{arm}_{scope}_min_pct", lo_, "%")
            emit(f"own_{arm}_{scope}_loo_mean_pct", drop, "%")
            emit(f"own_{arm}_{scope}_cells_above_0p01pct",
                 sum(1 for x in v if x > 0.01))
            emit(f"own_{arm}_{scope}_cells_negative",
                 sum(1 for x in v if x < -1e-9))
        emit(f"own_{arm}_cells_challenger_worse_comfort",
             sum(1 for r in rows
                 if (r["vb"] if arm == "gap_ftol" else r["vc"])
                 > r["va"] + 1e-6))
    emit("own_cells_total", len(rows))
    emit("own_cells_step0_differs_gt_0p01kW",
         sum(1 for r in rows if r["priced"]
             and abs(r["p0a"] - r["p0b"]) > 0.01))

    # ---- wiring / perturbation checks on a 4-cell subset -----------------
    wired = 0
    both_zero = True
    grew = 0
    for price_p, weather_p, tz, dhw, h in CELLS[:2] + CELLS[9:11]:
        cell = build(price_p, weather_p, tz, dhw, h)
        with mock.patch.object(O, "_scoped_minimize", scoped_ftol(1e-14)):
            x1 = solve(cell)
            x2 = solve(cell)          # both arms tight -> must be identical
        a = solve(cell)               # production
        with mock.patch.object(O, "_scoped_minimize", scoped_ftol(1e-4)):
            loose = solve(cell)       # looser stop -> J must not be lower
        jx1, jx2 = float(x1.objective_value), float(x2.objective_value)
        both_zero = both_zero and (jx1 == jx2)
        if (float(loose.objective_value) - float(a.objective_value)) >= -1e-9:
            grew += 1
        wired += 1
    emit("own_wiring_both_tight_identical", int(both_zero))
    emit("own_wiring_loose_not_better_cells", grew, f"of {wired}")

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
