"""D0 round 4 -- two leads that did NOT hold, with the numbers that closed them.

Both are recorded here so the next round does not re-open them.

LEAD 1 -- the restart keep threshold.  ``optimizer.py:_lbfgsb_restart``
re-runs L-BFGS-B from the point the solve returned and KEEPS the restarted
point only when it beats the prior by more than
``_LBFGSB_RESTART_KEEP_REL = 2e-2`` relative.  A strictly better point that
misses that bar is thrown away.  METRIC: the relative objective gain from
running that restart to convergence and keeping every improvement
(``_LBFGSB_RESTART_KEEP_REL = 0.0``, looped until no further drop),
``(J_prod - J_polished)/|J_prod|``.

LEAD 2 -- the single co-optimization pass.
``optimizer.py:HeatPumpOptimizer._co_optimize`` re-plans hot water against
the solved space profile exactly once.  METRIC: the relative objective gain
from iterating that pass up to 4 times, adopting only strict improvements.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/nonfindings.py

EXPECTED (baseline 7dd68dd, this machine, +/- 0.02 pp):

    mean_gain_restart_priced_pct   0.014006   +/- 0.02
    max_gain_restart_priced_pct    0.134817   +/- 0.02
    loo_mean_gain_restart_priced_pct 0.00058258 +/- 0.02
    mean_gain_restart_flat_pct     0.0116836  +/- 0.02   (null control)
    max_gain_coopt_priced_pct      0.0        (exactly: the single guarded
                                               pass already reaches the fixed
                                               point on every cell here)
    cells_coopt_iter_worse_than_production  0

Runtime on this box: about 3 minutes.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy/OpenBLAS, python 3.11

INSTRUMENTED SYMBOLS: ``optimizer.py:_lbfgsb_restart`` and
``optimizer.py:HeatPumpOptimizer._co_optimize``, both hooked, driving
``optimizer.py:HeatPumpOptimizer.optimize``.

PERTURBATION: raise ``_LBFGSB_RESTART_KEEP_REL`` to 1.0 (never keep a
restart); ``max_gain_restart_to_convergence_pct`` must grow.  Delete the
``score < best_score`` guard in ``_co_optimize``;
``max_gain_coopt_iterated_pct`` must then be able to go negative by more.

NULL CONTROL: the ``flat`` price rows, reported separately.
CONTENTION: objective values and ratios only.  Contention-immune.
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

_real_restart = O._lbfgsb_restart
_real_coopt = O.HeatPumpOptimizer._co_optimize


def polish_loop(best, objective, bounds, args, maxiter, batch_objective,
                fd_eps, rounds=25):
    saved = O._LBFGSB_RESTART_KEEP_REL
    O._LBFGSB_RESTART_KEEP_REL = 0.0
    try:
        cur = best
        prior = float(objective(np.asarray(cur.x, dtype=float), *args))
        for _ in range(rounds):
            nxt = _real_restart(cur, objective, bounds, args, maxiter,
                                batch_objective, fd_eps)
            if nxt is cur:
                break
            s = float(objective(np.asarray(nxt.x, dtype=float), *args))
            if not np.isfinite(s) or s >= prior - 1e-12 * max(abs(prior), 1.0):
                cur = nxt
                break
            cur, prior = nxt, s
        return cur
    finally:
        O._LBFGSB_RESTART_KEEP_REL = saved


def iter_coopt(self, h, *, space_power, dhw_power, status, best_score,
               solve_space, p_max, rounds=4):
    sp, dw, st, bs = space_power, dhw_power, status, best_score
    for _ in range(rounds):
        try:
            wood = self._dhw_coil_wood_forecast(h, sp)
            pinned = (dw > 1e-6) & (sp >= np.maximum(0.0, p_max - dw) - 1e-3)
            replanned = self._build_dhw_requirements(
                initial_state=h.initial_state, prices=h.prices,
                outdoor_temps=h.outdoor_temps, step_hours=h.step_hours,
                n_steps=h.n_steps, dt=h.dt, p_max=p_max,
                space_demand=np.where(pinned, p_max, sp),
                dhw_pins=h.dhw_pins,
                p_run_cap=(float(np.min(h.power_caps_extra))
                           if h.power_caps_extra is not None else None),
                step_weekdays=h.step_weekdays, holiday_flags=h.holiday_flags,
                wood_temps=wood).schedule
            if np.allclose(replanned, dw, atol=1e-4):
                break
            cs, cst, score = solve_space(replanned, sp)
            if score < bs - 1e-9:
                sp, dw, st, bs = cs, replanned, cst, score
            else:
                break
        except Exception:
            break
    return sp, dw, st


def main() -> int:
    cond = L.Conditions()
    rows = []
    for price_p in PRICE_SUBSET + (L.FLAT,):
        for tz in (False, True):
            cell = L.build_cell(price_p, "winter_cold", two_zone=tz, dhw=True)
            j0 = float(L.solve(cell).objective_value)
            with mock.patch.object(O, "_lbfgsb_restart", polish_loop):
                j1 = float(L.solve(cell).objective_value)
            with mock.patch.object(O.HeatPumpOptimizer, "_co_optimize",
                                   iter_coopt):
                j2 = float(L.solve(cell).objective_value)
            rows.append({
                "price": price_p, "tz": tz, "J": j0,
                "restart": (j0 - j1) / abs(j0) * 100.0,
                "coopt": (j0 - j2) / abs(j0) * 100.0,
            })
            print(f"CELL {price_p:16s} tz={int(tz)} J={j0:.5f}  "
                  f"restart={(j0 - j1) / abs(j0) * 100:+.4f}%  "
                  f"coopt_iter={(j0 - j2) / abs(j0) * 100:+.4f}%", flush=True)

    priced = [r for r in rows if r["price"] != L.FLAT]
    flat = [r for r in rows if r["price"] == L.FLAT]
    for key in ("restart", "coopt"):
        m, lo_, hi_, loo_ = L.loo([r[key] for r in priced])
        L.emit(f"mean_gain_{key}_priced_pct", m, "%")
        L.emit(f"max_gain_{key}_priced_pct", hi_, "%")
        L.emit(f"min_gain_{key}_priced_pct", lo_, "%")
        L.emit(f"loo_mean_gain_{key}_priced_pct", loo_, "%")
        mf, lof, hif, loof = L.loo([r[key] for r in flat])
        L.emit(f"mean_gain_{key}_flat_pct", mf, "%")
        L.emit(f"max_gain_{key}_flat_pct", hif, "%")
    L.emit("cells_priced", len(priced))
    L.emit("cells_flat_null_control", len(flat))
    L.emit("cells_restart_gain_zero",
           sum(1 for r in rows if abs(r["restart"]) < 1e-6))
    L.emit("cells_coopt_iter_worse_than_production",
           sum(1 for r in rows if r["coopt"] < -1e-6))
    cond.emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
