"""D2-s3 (round 9, D2.M4): the PV export price applied piecewise.

Metric (one line): for each (price profile, export price) cell, the number of
steps (of 96) where the production cost closure
``HeatPumpOptimizer._energy_cost_fn(prices, dt)`` prices a draw P differently
from the stated piecewise identity ``export·min(P,s) + import·max(P−s,0)``
(pv.py's module docstring and the closure's own docstring), plus the signed
total error (production − identity, currency) summed over the day at a fixed
3 kW draw, and the same signed error on a REAL solve's published
``OptimizationResult.predicted_cost``. Key: the value the production closure
returns / the published predicted_cost, against an independent formula.

Command:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D2/s3/pv_piecewise.py [--perturb]

Expected (baseline 1936d5ca): breach steps = the surplus steps where
import < export: summer_negative @ export 0.0 (the shipped default,
DEFAULT_PV_EXPORT_PRICE) = 16 steps, the 11:00-15:00 negative block; any
profile @ export 0.30 breaches wherever import < 0.30 under the sun. Null
controls: every cell where import >= export on every surplus step (winter
profiles @ 0.0, flat @ 0.0) = 0, and no-surplus = 0. With --perturb
(``pv.import_margin``'s zero floor removed, in memory) every cell reads 0.
Real solve (summer_negative, summer_cool weather, export 0.0 default):
published predicted_cost -0.608961 against an identity cost of 0.0 (all draw
surplus-covered), and 5.07 kWh drawn from surplus in negative-price steps
(2.27 kWh under --perturb). Second seam: pv.blended_block_prices breaches on
the same 16 steps. Tolerance: exact (counts); currency sums ±1e-6 (the solve
is BLAS-sensitive in its last digits).
Machine: B7 audit container (linux). Root rule: cwd (run from repo root).
"""
import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import sys
import time
from datetime import datetime
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from profiles import prices, weather, house, DT, N  # noqa: E402
from heatpump_optimizer import pv  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)

PERTURB = "--perturb" in sys.argv
START = datetime(2026, 6, 15)
PROFILES = ["summer_negative", "summer_typical", "shoulder", "winter_typical",
            "winter_moderate", "flat"]
EXPORTS = [0.0, 0.30]


def surplus_kw() -> np.ndarray:
    """A clear-sky 6 kWp day minus a 0.4 kW house: surplus 06:00-18:00."""
    h = np.arange(N) * DT + DT / 2
    prod = np.clip(6.0 * 0.8 * np.sin(np.pi * (h - 6.0) / 12.0), 0.0, None)
    return pv.surplus_kw(prod, np.full(N, 0.4))


def identity(pr, P, s, export):
    return (export * np.minimum(P, s) + pr * np.maximum(P - s, 0.0)) * DT


def make_opt(export):
    cfg = house(two_zone=False)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    opt.config.pv_export_price = export
    return opt, m


def unfloored_margin(import_prices, export_price):
    return np.asarray(import_prices, dtype=float) - float(export_price)


def run():
    s = surplus_kw()
    rows = {}
    for prof in PROFILES:
        pr = prices(prof, START)
        for export in EXPORTS:
            opt, _ = make_opt(export)
            opt._pv_surplus = s
            fn = opt._energy_cost_fn(pr, DT)
            breach = 0
            for i in range(N):
                P = np.zeros(N)
                P[i] = 3.0
                got = fn(P)
                want = float(np.sum(identity(pr, P, s, export)))
                if abs(got - want) > 1e-9:
                    breach += 1
            P = np.full(N, 3.0)
            signed = fn(P) - float(np.sum(identity(pr, P, s, export)))
            rows[(prof, export)] = (breach, signed)
    # Null control: no surplus at all -> the grid-only closure.
    opt, _ = make_opt(0.0)
    opt._pv_surplus = np.zeros(N)
    pr = prices("summer_negative", START)
    fn = opt._energy_cost_fn(pr, DT)
    null_nosun = abs(fn(np.full(N, 3.0)) - float(np.sum(pr * 3.0 * DT)))
    # Published figure on a real solve: summer_negative, shipped default 0.0.
    opt, m = make_opt(0.0)
    pr = prices("summer_negative", START)
    ot, wi, ra, so = weather("summer_cool", START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0,
                      buffer_tank_temperature=40.0)
    res = opt.optimize(st, pr, ot, wi, ra, so, start_time=START,
                       pv_surplus=s)
    P = np.asarray(res.power_schedule, dtype=float)
    solve_err = res.predicted_cost - float(np.sum(identity(pr[:P.size], P, s[:P.size], 0.0)))
    base_kwh_neg = float(np.sum(np.minimum(P, s)[pr[:P.size] < 0.0]) * DT)
    # Second seam: the DHW planners' blended block rate (pv.blended_block_prices,
    # a 3 kW block): per-kWh rate vs identity/(block·dt) at export 0.0.
    blend = pv.blended_block_prices(pr, s, 0.0, 3.0)
    blk = np.full(N, 3.0)
    want = identity(pr, blk, s, 0.0) / (3.0 * DT)
    blend_breach = int(np.sum(np.abs(blend - want) > 1e-9))
    return rows, null_nosun, solve_err, base_kwh_neg, res.predicted_cost, blend_breach


def main():
    c0, t0 = time.process_time(), time.thread_time()
    if PERTURB:
        with mock.patch.object(pv, "import_margin", unfloored_margin):
            out = run()
    else:
        out = run()
    c1, t1 = time.process_time(), time.thread_time()
    rows, null_nosun, solve_err, kwh_neg, pc, blend_breach = out
    for (prof, ex), (b, sg) in rows.items():
        print(f"RESULT breach_steps_{prof}_export{ex:.2f}={b} steps_of_96")
        print(f"RESULT signed_err_3kw_{prof}_export{ex:.2f}={sg:.6f} currency_per_day")
    d0 = [rows[(p, 0.0)][1] for p in PROFILES]
    d3 = [rows[(p, 0.30)][1] for p in PROFILES]
    print(f"RESULT cells={len(rows)}")
    print(f"RESULT signed_err_range_export0.30={min(d3):.6f}..{max(d3):.6f} currency_per_day")
    worst = sorted(d3)  # most negative = most favourable to the claim
    print(f"RESULT signed_err_mean_export0.30={np.mean(d3):.6f}")
    print(f"RESULT signed_err_mean_export0.30_leave_most_negative_out={np.mean(worst[1:]):.6f}")
    nulls = sum(rows[(p, 0.0)][0] for p in PROFILES if p != "summer_negative")
    print(f"RESULT null_export0_nonnegative_profiles_breach={nulls} steps")
    print(f"RESULT null_no_surplus_abs_err={null_nosun:.3e} currency")
    print(f"RESULT solve_predicted_cost={pc:.6f} currency")
    print(f"RESULT solve_predicted_cost_minus_identity={solve_err:.6f} currency")
    print(f"RESULT solve_surplus_kwh_in_negative_steps={kwh_neg:.4f} kWh")
    print(f"RESULT blended_block_breach_summer_negative_export0.00={blend_breach} steps_of_96")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
