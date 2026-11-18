"""D0 round 4 -- which solver knob actually binds the shipped space solve.

METRIC (one line): the relative objective change
``(J_prod - J_arm)/|J_prod|`` when exactly one L-BFGS-B option in
``optimizer.py:_multi_start_minimize``'s ``options={"maxiter": maxiter,
"ftol": 1e-6, "eps": 1e-4}`` is loosened at a time -- ``maxiter`` x15,
``gtol`` 1e-5 (scipy's default) -> 1e-12, ``ftol`` 1e-6 -> 1e-14 -- plus a
census of how many L-BFGS-B calls terminate on the iteration cap.

Why it exists: the repository treats the ITERATION budget as the solution
quality control (``_MULTI_START_SOLVES``, ``maxiter=200``/``300``, and
``tests/optimality.py``'s challenger 3, which starves ``maxiter`` to 3 and
asserts the production budget buys a materially better plan).  This measures
whether that knob is ever the binding one.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/budget_knobs.py

EXPECTED (baseline 7dd68dd, this machine, +/- 0.02 pp):

    max_gain_maxiter_x15_priced_pct   0.0  (exactly: no solve reaches the cap)
    max_gain_gtol_1e-12_priced_pct    0.0  (exactly)
    max_gain_ftol_1e-14_priced_pct    0.795787  +/- 0.02
    mean_gain_ftol_1e-14_priced_pct   0.164503  +/- 0.02
    mean_gain_ftol_1e-14_flat_pct     0.284989  +/- 0.02  (null control)
    lbfgsb_solves_observed            68
    solves_terminating_on_maxiter     0    (exact)
    max_nit_observed                  52   (against caps of 200 and 300)
    median_nit_observed               8

Runtime on this box: about 4 minutes.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/optimizer.py
:_scoped_minimize (hooked) and :_multi_start_minimize (hooked, for the
per-solve ``nit``/``status`` census), driving
``optimizer.py:HeatPumpOptimizer.optimize``.

PERTURBATION: cut production's ``maxiter`` from 200/300 to 3 (the cut
``tests/optimality.py`` challenger 3 makes).  ``max_gain_maxiter_x15_pct``
must then become large and ``solves_terminating_on_maxiter`` must become
equal to the solve count -- i.e. the metric does move, it is simply zero at
the shipped budget.

NULL CONTROL: the ``flat`` price rows, reported separately.
LEAVE-ONE-OUT: priced aggregates printed with the largest-gain cell dropped.

CONTENTION: objective values, ratios and iteration counts only.
Contention-immune.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D0"))

import d0lib as L  # noqa: E402

import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import optimizer as O  # noqa: E402

PRICE_SUBSET = ("winter_typical", "winter_extreme", "shoulder",
                "summer_negative", "winter_moderate")

_real_scoped = O._scoped_minimize


def arm(opts):
    def scoped(*a, **kw):
        kw = dict(kw)
        o = dict(kw.get("options") or {})
        for k, v in opts.items():
            o[k] = v(o) if callable(v) else v
        kw["options"] = o
        return _real_scoped(*a, **kw)
    return scoped


ARMS = {
    "maxiter_x15": {"maxiter": lambda o: int(o.get("maxiter", 300) * 15)},
    "gtol_1e-12": {"gtol": 1e-12},
    "ftol_1e-14": {"ftol": 1e-14},
}


def main() -> int:
    cond = L.Conditions()
    rows = []
    solves = 0
    on_cap = 0
    nits = []
    for price_p in PRICE_SUBSET + (L.FLAT,):
        for tz in (False, True):
            cell = L.build_cell(price_p, "winter_cold", two_zone=tz, dhw=True)
            starts = []
            with L.capture_starts(starts):
                base = L.solve(cell)
            for e in starts:
                for s in e["solves"]:
                    solves += 1
                    nits.append(s["nit"])
                    if s["status"] == 1 or s["nit"] >= e["prod_maxiter"]:
                        on_cap += 1
            j0 = float(base.objective_value)
            row = {"price": price_p, "tz": tz, "J": j0}
            for name, opts in ARMS.items():
                with mock.patch.object(O, "_scoped_minimize", arm(opts)):
                    j = float(L.solve(cell).objective_value)
                row[name] = (j0 - j) / abs(j0) * 100.0
            rows.append(row)
            print(f"CELL {price_p:16s} tz={int(tz)} J={j0:.5f}  " + "  ".join(
                f"{n}={row[n]:+.4f}%" for n in ARMS), flush=True)

    priced = [r for r in rows if r["price"] != L.FLAT]
    flat = [r for r in rows if r["price"] == L.FLAT]
    for name in ARMS:
        m, lo_, hi_, loo_ = L.loo([r[name] for r in priced])
        L.emit(f"mean_gain_{name.replace('.', 'p')}_priced_pct", m, "%")
        L.emit(f"max_gain_{name.replace('.', 'p')}_priced_pct", hi_, "%")
        L.emit(f"loo_mean_gain_{name.replace('.', 'p')}_priced_pct", loo_, "%")
        mf, lof, hif, loof = L.loo([r[name] for r in flat])
        L.emit(f"mean_gain_{name.replace('.', 'p')}_flat_pct", mf, "%")
        L.emit(f"max_gain_{name.replace('.', 'p')}_flat_pct", hif, "%")
    L.emit("cells_priced", len(priced))
    L.emit("cells_flat_null_control", len(flat))
    L.emit("lbfgsb_solves_observed", solves)
    L.emit("solves_terminating_on_maxiter", on_cap)
    L.emit("max_nit_observed", max(nits))
    L.emit("median_nit_observed", float(np.median(nits)))
    L.emit("shipped_maxiter_space_only", 200)
    L.emit("shipped_maxiter_dhw_path", 300)
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
