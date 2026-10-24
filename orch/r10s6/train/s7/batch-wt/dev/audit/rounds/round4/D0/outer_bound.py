"""D0 round 4 -- where the objective the shipped solver leaves on the table sits.

METRIC (one line): three objective values per grid cell on the SAME
production objective, bounds and inputs -- A = the shipped plan, B = the same
solve with only L-BFGS-B's ``ftol`` tightened 1e-6 -> 1e-14, C = B plus 12
extra structural starting points and every candidate refined
(``_MULTI_START_SOLVES`` 4 -> 16) -- reported as the relative gaps
``A->B`` (the stopping rule), ``B->C`` (basin selection, i.e. seeding), and
``A->C`` (the total gap to this outer bound).

The 12 extra starts are structural and derived from the bounds and the
production guess alone -- level schedules at 0/15/30/50/70/85/100 % of each
step's upper bound, and the production guess scaled by 0.25/0.5/0.75/1.25/1.5
-- so C is a strictly wider search over the identical feasible set, never a
different problem.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/outer_bound.py

EXPECTED (baseline 7dd68dd, this machine, +/- 0.02 pp per cell):

    mean_gap_A_to_B_priced_pct   ~0.2
    mean_gap_B_to_C_priced_pct   ~0.0   (seeding buys little once the stop
                                         rule is fixed -- that is the point)
    mean_gap_A_to_C_priced_pct   ~0.2

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_multi_start_minimize (hooked, to widen the candidate list) and
:_scoped_minimize (hooked, to set ftol), driving
``optimizer.py:HeatPumpOptimizer.optimize``.

PERTURBATION: set production's ``ftol`` to 1e-14 -- ``gap_A_to_B`` must fall
to 0.  Set ``_MULTI_START_SOLVES`` to 16 and add the same seeds in
``_solve_space`` -- ``gap_B_to_C`` must fall to 0.

NULL CONTROL: the ``flat`` price rows, reported separately.
LEAVE-ONE-OUT: priced aggregates printed with the largest-gap cell dropped.

CONTENTION: objective values and their ratios only.  Contention-immune.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D0"))

import d0lib as L  # noqa: E402

import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402

from profiles import DT  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

_real_scoped = O._scoped_minimize
_real_ms = O._multi_start_minimize


def tight_scoped(*a, **kw):
    kw = dict(kw)
    opts = dict(kw.get("options") or {})
    opts["ftol"] = 1e-14
    kw["options"] = opts
    return _real_scoped(*a, **kw)


def wide_ms(objective, candidates, bounds, args=(), maxiter=300,
            batch_objective=None, fd_eps=1e-4):
    hi = np.array([b[1] for b in bounds], dtype=float)
    lo = np.array([b[0] for b in bounds], dtype=float)
    base = np.asarray(candidates[0], dtype=float)
    extra = [np.clip(hi * f, lo, hi)
             for f in (0.0, 0.15, 0.3, 0.5, 0.7, 0.85, 1.0)]
    extra += [np.clip(base * f, lo, hi) for f in (0.25, 0.5, 0.75, 1.25, 1.5)]
    return _real_ms(objective, list(candidates) + extra, bounds, args=args,
                    maxiter=maxiter, batch_objective=batch_objective,
                    fd_eps=fd_eps)


def main() -> int:
    cond = L.Conditions()
    rows = []
    for price_p in L.PRICE_PROFILES + (L.FLAT,):
        for tz in (False, True):
            cell = L.build_cell(price_p, "winter_cold", two_zone=tz, dhw=True)
            a = float(L.solve(cell).objective_value)
            with mock.patch.object(O, "_scoped_minimize", tight_scoped):
                b = float(L.solve(cell).objective_value)
            saved = O._MULTI_START_SOLVES
            O._MULTI_START_SOLVES = 16
            try:
                with mock.patch.object(O, "_scoped_minimize", tight_scoped), \
                        mock.patch.object(O, "_multi_start_minimize", wide_ms):
                    c = float(L.solve(cell).objective_value)
            finally:
                O._MULTI_START_SOLVES = saved
            rows.append({
                "price": price_p, "tz": tz, "A": a, "B": b, "C": c,
                "ab": (a - b) / abs(a) * 100.0,
                "bc": (b - c) / abs(b) * 100.0,
                "ac": (a - c) / abs(a) * 100.0,
            })
            print(f"CELL {price_p:16s} tz={int(tz)} A={a:.5f} B={b:.5f} "
                  f"C={c:.5f}  A->B={(a - b) / abs(a) * 100:+.4f}%  "
                  f"B->C={(b - c) / abs(b) * 100:+.4f}%  "
                  f"A->C={(a - c) / abs(a) * 100:+.4f}%", flush=True)

    priced = [r for r in rows if r["price"] != L.FLAT]
    flat = [r for r in rows if r["price"] == L.FLAT]
    for key, label in (("ab", "A_to_B"), ("bc", "B_to_C"), ("ac", "A_to_C")):
        m, lo_, hi_, loo_ = L.loo([r[key] for r in priced])
        L.emit(f"mean_gap_{label}_priced_pct", m, "%")
        L.emit(f"max_gap_{label}_priced_pct", hi_, "%")
        L.emit(f"min_gap_{label}_priced_pct", lo_, "%")
        L.emit(f"loo_mean_gap_{label}_priced_pct", loo_, "%")
        mf, lof, hif, loof = L.loo([r[key] for r in flat])
        L.emit(f"mean_gap_{label}_flat_pct", mf, "%")
        L.emit(f"max_gap_{label}_flat_pct", hif, "%")
    L.emit("cells_priced", len(priced))
    L.emit("cells_flat_null_control", len(flat))
    L.emit("cells_wider_search_worse_than_B",
           sum(1 for r in rows if r["bc"] < -1e-9))
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
