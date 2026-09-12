"""D0 round 4 -- how much objective the shipped L-BFGS-B stop leaves on the table.

METRIC (one line): per grid cell, the relative objective gap
``(J_prod - J_ftol)/|J_prod|`` between the plan ``HeatPumpOptimizer.optimize``
returns and the plan the SAME solve returns when the only change is
L-BFGS-B's ``ftol``, 1e-6 -> 1e-14, in
``optimizer.py:_multi_start_minimize``'s ``options`` dict (same seeds, same
``_MULTI_START_SOLVES``, same bounds, same batched jac, same ``maxiter``,
same ``eps``).  ``J`` is the production objective, read off
``OptimizationResult.objective_value``.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/ftol_gap.py

EXPECTED (baseline 7dd68dd, this machine, +/- 0.02 pp per cell; the arithmetic
is deterministic given one BLAS build, so the tolerance is for a different
BLAS, not for run-to-run noise):

    mean_gap_priced_pct       0.16   +/- 0.02
    max_gap_priced_pct        0.80   +/- 0.02
    mean_gap_flat_pct         0.08   +/- 0.02   (the null control)
    cells_with_gap            (of 80)
    maxiter_binding_solves    0

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_scoped_minimize (hooked; it is the single funnel every L-BFGS-B call in the
optimizer goes through), driving
``optimizer.py:HeatPumpOptimizer.optimize``.

PERTURBATION: edit ``optimizer.py:_multi_start_minimize``'s
``options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4}`` to ``"ftol":
1e-14`` (and the identical dict in ``_lbfgsb_restart``).  Every gap RESULT
must fall to 0.0.  Raising ``ftol`` to 1e-4 must make them grow.

NULL CONTROL: the ``flat`` price rows, printed separately and never folded
into the priced aggregate.

LEAVE-ONE-OUT: the priced aggregate is printed with its single most
favourable (largest-gap) cell dropped.

CONTENTION: every number here is an objective value or a ratio of two
objective values computed in the same process; none is a wall, CPU or RSS
figure, so none is contention-sensitive.  ``thread_factor``/``load1``/
``swapins`` are printed for the record as the harness contract requires.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D0"))

import d0lib as L  # noqa: E402  (applies the BLAS thread pin before numpy)

import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import optimizer as O  # noqa: E402

MIN_TEMP = 17.0
_real_scoped = O._scoped_minimize


def tight_scoped(*a, **kw):
    kw = dict(kw)
    opts = dict(kw.get("options") or {})
    opts["ftol"] = 1e-14
    kw["options"] = opts
    return _real_scoped(*a, **kw)


def comfort(result):
    room = np.asarray(result.room_temp_trajectory, dtype=float)[1:]
    return (float(np.maximum(0.0, MIN_TEMP - room).sum()), float(room.min()))


def cost(result):
    pw = np.asarray(result.power_schedule, dtype=float)
    dhw = np.asarray(result.dhw_power_schedule, dtype=float)
    if dhw.size == pw.size:
        pw = pw + dhw
    return L.energy_cost(pw, result.prices)


def main() -> int:
    cond = L.Conditions()
    rows = []
    maxiter_binding = 0
    solves_seen = 0
    for price_p in L.PRICE_PROFILES + (L.FLAT,):
        for weather_p in L.WEATHER_PROFILES:
            for tz in (False, True):
                cell = L.build_cell(price_p, weather_p, two_zone=tz, dhw=True)
                starts = []
                with L.capture_starts(starts):
                    a = L.solve(cell)
                for e in starts:
                    for s in e["solves"]:
                        solves_seen += 1
                        if s["status"] == 1 or s["nit"] >= e["prod_maxiter"]:
                            maxiter_binding += 1
                with mock.patch.object(O, "_scoped_minimize", tight_scoped):
                    b = L.solve(cell)
                ja, jb = float(a.objective_value), float(b.objective_value)
                gap = (ja - jb) / abs(ja) * 100.0 if np.isfinite(ja) else float("nan")
                va, mna = comfort(a)
                vb, mnb = comfort(b)
                ca, cb = cost(a), cost(b)
                p0a = float(a.power_schedule[0])
                p0b = float(b.power_schedule[0])
                rows.append({
                    "price": price_p, "weather": weather_p, "tz": tz,
                    "gap": gap, "Ja": ja, "Jb": jb,
                    "cost_a": ca, "cost_b": cb, "dcost": ca - cb,
                    "viol_a": va, "viol_b": vb, "minT_a": mna, "minT_b": mnb,
                    "p0a": p0a, "p0b": p0b, "dp0": abs(p0a - p0b),
                })
                print(
                    f"CELL {price_p:16s} {weather_p:12s} tz={int(tz)} "
                    f"gap={gap:+.4f}%  J {ja:.5f}->{jb:.5f}  "
                    f"cost {ca:.3f}->{cb:.3f} ({ca - cb:+.4f} SEK)  "
                    f"viol {va:.4f}->{vb:.4f}  minT {mna:.3f}->{mnb:.3f}  "
                    f"p0 {p0a:.4f}->{p0b:.4f}"
                )

    priced = [r for r in rows if r["price"] != L.FLAT]
    flat = [r for r in rows if r["price"] == L.FLAT]

    gp = [r["gap"] for r in priced]
    gf = [r["gap"] for r in flat]
    mean_p, min_p, max_p, loo_p = L.loo(gp)
    mean_f, min_f, max_f, loo_f = L.loo(gf)

    L.emit("cells_total", len(rows))
    L.emit("cells_priced", len(priced))
    L.emit("cells_flat_null_control", len(flat))
    L.emit("mean_gap_priced_pct", mean_p, "%")
    L.emit("max_gap_priced_pct", max_p, "%")
    L.emit("min_gap_priced_pct", min_p, "%")
    L.emit("loo_mean_gap_priced_pct", loo_p, "%")
    L.emit("mean_gap_flat_pct", mean_f, "%")
    L.emit("max_gap_flat_pct", max_f, "%")
    L.emit("loo_mean_gap_flat_pct", loo_f, "%")
    L.emit("cells_gap_above_0p01pct",
           sum(1 for r in priced if r["gap"] > 0.01))
    L.emit("cells_gap_above_0p1pct",
           sum(1 for r in priced if r["gap"] > 0.1))
    L.emit("cells_negative_gap", sum(1 for r in rows if r["gap"] < -1e-9))
    # Feasibility parity: the challenger may never be worse on comfort.
    L.emit("cells_challenger_worse_comfort",
           sum(1 for r in rows if r["viol_b"] > r["viol_a"] + 1e-6))
    L.emit("max_comfort_violation_either_arm",
           max(max(r["viol_a"], r["viol_b"]) for r in rows))
    # MPC masking: does the gap reach the actuator this cycle?
    L.emit("cells_step0_differs_gt_0p01kW",
           sum(1 for r in priced if r["dp0"] > 0.01))
    L.emit("max_step0_delta_kW", max(r["dp0"] for r in priced), "kW")
    # SEK/day, priced arm only, reported beside the bill.
    dc = [r["dcost"] for r in priced]
    L.emit("mean_energy_cost_delta_priced_SEK_per_day", sum(dc) / len(dc), "SEK")
    L.emit("max_energy_cost_delta_priced_SEK_per_day", max(dc), "SEK")
    L.emit("mean_bill_priced_SEK_per_day",
           sum(r["cost_a"] for r in priced) / len(priced), "SEK")
    dcf = [r["dcost"] for r in flat]
    L.emit("mean_energy_cost_delta_flat_SEK_per_day", sum(dcf) / len(dcf), "SEK")
    # The budget the codebase treats as the control is never the binder.
    L.emit("lbfgsb_solves_observed", solves_seen)
    L.emit("maxiter_binding_solves", maxiter_binding)
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
