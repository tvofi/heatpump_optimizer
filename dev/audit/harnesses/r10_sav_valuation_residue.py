"""R10-SAV-VALUATION-RESIDUE: the part-load refill pricing, against the rule it owes.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_sav_valuation_residue.py

Synthetic throughout: ``r10_partload_pricing.solve``'s 16 installs on its
spread and flat price days, at ``d = 0`` and at the central plant's derate
(``r10_partload_residue.central_derate``). Three figures per solve, each the
production figure against the tree's own part-load inverse
(``thermal_model.power_for_heat_per_cop_kw``) applied to the same inputs:

1. ``lp``: every hot-water LP the solve runs (``dhw_planner.linprog``,
   wrapped). The LP's own valuation of the energy it bought,
   ``c[:energy] . x[:energy]``, against what that energy costs at the draw
   the planner publishes for it, ``sum(price * dt * P(h))`` with
   ``h = E / (cop * dt)`` and ``P`` the inverse. The largest gap over the
   solve's LPs, currency per day.
2. ``terminal``: ``_terminal_cost`` on the published end state, against
   ``refill_price * P(T_lin / refill_price, hours=H)``: ``T_lin`` the same
   call with the derate zeroed (the linear figure), ``H`` the refill hours
   (a quarter of the 24 h horizon, the hours the 25th-percentile refill
   price is drawn from), sign-symmetric.
3. ``deferred``: every ``_deferred_energy_cost`` call of the solve (wrapped),
   re-evaluated alike: its zero-derate figure through the same rule.

Null control: at ``d = 0`` all three must read 0 (``lp`` within 1e-9: the
two valuations multiply and divide by the COP in different orders); the
harness exits 1 otherwise. A tree that prices refill linearly reads the
``d > 0`` terminal and deferred gaps above 0; a tree pricing it at the rule
reads 0. ``lp`` reads the chord between segment breakpoints where the LP is
segmented, the whole secant where it is not.

Also printed per solve: ``predicted_savings``, so the flat-price day (no
timing saving to find) shows what the derated refill moves in the savings.
"""
from __future__ import annotations

import math
import sys

import numpy as np

sys.path.insert(0, "dev/audit/harnesses")

import r10_partload_pricing as pp  # noqa: E402
import r10_partload_residue as pr  # noqa: E402
import r10_setpoint_boost as sb  # noqa: E402
from heatpump_optimizer import dhw_planner as planner_mod  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.thermal_model import power_for_heat_per_cop_kw  # noqa: E402

REFILL_HOURS = 0.25 * 24.0
NULL_TOL = 1e-9


def rule(params, linear: float, refill_price: float) -> float:
    """The derated refill of a linear figure: the tree's own inverse at H."""
    # No derate: the inverse is the identity, and ``rp * (x / rp)`` need not
    # be ``x`` to the bit, so the rule returns the figure itself.
    if not params.cop_partload_derate or refill_price == 0.0 or linear == 0.0:
        return linear
    hpc = linear / refill_price
    return refill_price * math.copysign(
        float(power_for_heat_per_cop_kw(params, abs(hpc), hours=REFILL_HOURS)), hpc)


def zeroed(params):
    class _Z:
        def __enter__(self):
            self.d = params.cop_partload_derate
            params.cop_partload_derate = 0.0

        def __exit__(self, *exc):
            params.cop_partload_derate = self.d
    return _Z()


def solve_recording(cell, prices, d):
    lps, defers = [], []
    real_lp = planner_mod.linprog
    real_plan = planner_mod.DhwPlanner._plan_dhw_min_cost
    real_cop = planner_mod.DhwPlanner._dhw_cop_profile
    real_defer = opt_mod.HeatPumpOptimizer._deferred_energy_cost
    seen: dict = {}

    def plan(self, ctx, *a, **k):
        seen["ctx"], seen["params"] = ctx, self.model.params
        return real_plan(self, ctx, *a, **k)

    def cop_profile(self, *a, **k):
        seen["cop"] = out = real_cop(self, *a, **k)
        return out

    def lp(c, *a, **k):
        res = real_lp(c, *a, **k)
        if res.success and res.x is not None and "ctx" in seen:
            ctx, cop = seen["ctx"], np.asarray(seen["cop"], float)
            x, cv = np.asarray(res.x, float), np.asarray(c, float)
            lps.append((cv, x, ctx.n_steps, ctx.dt, cop, np.asarray(ctx.prices, float), seen["params"]))
        return res

    def defer(self, *a, **k):
        out = real_defer(self, *a, **k)
        with zeroed(self.model.params):
            lin = real_defer(self, *a, **k)
        prices = a[2] if len(a) > 2 else k["prices"]
        refill = float(np.percentile(prices, 25))
        defers.append((out, rule(self.model.params, lin, refill)))
        return out

    planner_mod.linprog = lp
    planner_mod.DhwPlanner._plan_dhw_min_cost = plan
    planner_mod.DhwPlanner._dhw_cop_profile = cop_profile
    opt_mod.HeatPumpOptimizer._deferred_energy_cost = defer
    try:
        opt, res = pp.solve(cell, prices, d)
    finally:
        planner_mod.linprog = real_lp
        planner_mod.DhwPlanner._plan_dhw_min_cost = real_plan
        planner_mod.DhwPlanner._dhw_cop_profile = real_cop
        opt_mod.HeatPumpOptimizer._deferred_energy_cost = real_defer
    return opt, res, lps, defers


def lp_gap(entry) -> float:
    cv, x, n, dt, cop, prices, params = entry
    # Energy columns are the leading n-wide blocks priced below the
    # shortfall slack, which ``_plan_dhw_min_cost`` prices at
    # 1000 * (max |price| + 1): one block unsegmented, one per segment else.
    slack = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)
    blocks = 0
    while (blocks + 1) * n <= len(cv) and np.all(cv[blocks * n:(blocks + 1) * n] < 0.5 * slack):
        blocks += 1
    n_e = blocks * n
    lp_value = float(cv[:n_e] @ x[:n_e])
    energy = x[:n_e].reshape(blocks, n).sum(axis=0)
    draw = np.asarray(power_for_heat_per_cop_kw(params, energy / (cop * dt)), float)
    return float((prices * draw).sum() * dt) - lp_value


def main() -> int:
    derate = pr.central_derate()
    print(f"central plant derate {derate}; refill hours {REFILL_HOURS}")
    null_bad = failures = 0
    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
        for d in (0.0, derate):
            rows = []
            for cell in sb.CELLS:
                try:
                    opt, res, lps, defers = solve_recording(cell, prices, d)
                except Exception as err:  # counted, never dropped
                    failures += 1
                    print(f"  {tag} {cell} d={d} failed: {err!r}")
                    continue
                params = opt.model.params
                lp = max((lp_gap(e) for e in lps), default=0.0)
                term = pp.terminal_figure(opt, res)
                with zeroed(params):
                    term_lin = pp.terminal_figure(opt, res)
                refill = float(np.percentile(np.asarray(res.prices, float), 25)) * opt.config.price_weight
                term_gap = rule(params, term_lin, refill) - term
                defer_gap = max((abs(r - o) for o, r in defers), default=0.0)
                sav = float(res.predicted_savings)
                rows.append((abs(lp), abs(term_gap), defer_gap))
                print(f"  {tag} {cell} d={d} lp {lp:+.6f} ({len(lps)} LPs)"
                      f" | terminal {term:.4f} gap {term_gap:+.6f}"
                      f" | deferred calls {len(defers)} gap max {defer_gap:.6f}"
                      f" | predicted_savings {sav:.4f}")
                if d == 0.0 and (abs(lp) > NULL_TOL or term_gap != 0.0 or defer_gap != 0.0):
                    null_bad += 1
                    print(f"    null row off: lp {lp!r} terminal {term_gap!r} deferred {defer_gap!r}")
            if rows:
                a = np.array(rows, float)
                print(f"{tag} d={d}: cells {len(rows)} lp gap max {a[:, 0].max():.6f}"
                      f" terminal gap max {a[:, 1].max():.6f} deferred gap max {a[:, 2].max():.6f}")
    print(f"null rows not zero {null_bad}")
    print(f"failures {failures}")
    return 1 if null_bad or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
