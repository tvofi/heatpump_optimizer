"""D0 probe: does the guard that SKIPS the hot-water re-plan cost anything?

``HeatPumpOptimizer._co_optimize`` re-plans hot water against the solved space
profile, and adopts the result only when it scores strictly better on the same
objective -- so the pass itself can never make a plan worse. It is nevertheless
skipped entirely unless
``pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)`` has at least
one True (or the wood coil re-plans).

METRIC (one line): coopt_gate_gap = (production objective_value - objective_value
with that early return removed) / |production objective_value| in percent, plus
how many cells the gate skips (``gate_skipped``) and how many of the forced
re-plans the pass then actually adopts (``forced_adoptions``).

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/coopt_gate.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    cells                = 8
    coopt_gate_gap_max_pct -- reported; the claim rests on whether it is 0
    forced_adoptions       -- reported
Tolerance +/- 0.02 percentage points on any non-zero gap.

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize
(the ``pinned``/``coil_replan`` early return is bypassed by re-implementing the
method's body with that one branch removed and everything else called through
production: ``_dhw_coil_wood_forecast``, ``_build_dhw_requirements``,
``solve_space``).

PERTURBATION (the judge runs it): D0_COOPT_GATE_KEEP=1 restores the early
return in the challenger arm, so the challenger becomes production and every
gap must be exactly 0.0000 %.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer as HPO  # noqa: E402

KEEP = os.environ.get("D0_COOPT_GATE_KEEP") == "1"
STATS = {"skipped": 0, "forced_adoptions": 0, "calls": 0}

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")


def ungated(self, h, *, space_power, dhw_power, status, best_score,
            solve_space, p_max):
    """``_co_optimize`` with the skip-the-re-plan branch removed."""
    STATS["calls"] += 1
    try:
        headroom = np.maximum(0.0, p_max - dhw_power)
        pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)
        wood_temps = self._dhw_coil_wood_forecast(h, space_power)
        coil_replan = False
        if wood_temps is not None:
            hours = np.asarray(h.step_hours, dtype=float) % 24.0
            raw = self.model.dhw_draw_rates(hours)
            credited = self._dhw_planner_draws(raw, wood_temps)
            coil_replan = not np.allclose(credited, raw, atol=1e-9)
        gated_out = not bool(np.any(pinned)) and not coil_replan
        if gated_out:
            STATS["skipped"] += 1
            if KEEP:
                return space_power, dhw_power, status
        replanned = self._build_dhw_requirements(
            initial_state=h.initial_state, prices=h.prices,
            outdoor_temps=h.outdoor_temps, step_hours=h.step_hours,
            n_steps=h.n_steps, dt=h.dt, p_max=p_max,
            space_demand=np.where(pinned, p_max, space_power),
            dhw_pins=h.dhw_pins,
            p_run_cap=(float(np.min(h.power_caps_extra))
                       if h.power_caps_extra is not None else None),
            step_weekdays=h.step_weekdays, holiday_flags=h.holiday_flags,
            wood_temps=wood_temps,
        ).schedule
        if np.allclose(replanned, dhw_power, atol=1e-4):
            return space_power, dhw_power, status
        candidate_space, candidate_status, score = solve_space(
            replanned, space_power)
        if score < best_score - 1e-9:
            if gated_out:
                STATS["forced_adoptions"] += 1
            return candidate_space, replanned, candidate_status
    except Exception:
        pass
    return space_power, dhw_power, status


def main():
    gaps = []
    for price_p in PRICES:
        opt, m, a, st = L.build(price_p, "winter_cold", two_zone=False, dhw=True)
        prod = opt.optimize(*a)
        o0 = float(prod.objective_value)
        opt2, m2, a2, st2 = L.build(price_p, "winter_cold", two_zone=False,
                                    dhw=True)
        with mock.patch.object(HPO, "_co_optimize", ungated):
            chal = opt2.optimize(*a2)
        o1 = float(chal.objective_value)
        g = (o0 - o1) / abs(o0) * 100.0
        gaps.append(g)
        c0 = L.comfort_of(m, np.asarray(prod.power_schedule, dtype=float),
                          a[0], *a[2:6])
        c1 = L.comfort_of(m2, np.asarray(chal.power_schedule, dtype=float),
                          a2[0], *a2[2:6])
        print(f"CELL {price_p:16s} obj {o0:10.5f} -> {o1:10.5f} gap {g:+7.4f}% "
              f" bill {prod.predicted_cost:7.3f} -> {chal.predicted_cost:7.3f}"
              f"  below {c0['below_degree_steps']:.4f}->"
              f"{c1['below_degree_steps']:.4f}", flush=True)
    v = np.array(gaps)
    flat = np.array([p == "flat" for p in PRICES])
    print(f"RESULT cells={len(PRICES)} count")
    print(f"RESULT coopt_gate_gap_max_pct={v.max():.4f} percent")
    print(f"RESULT coopt_gate_gap_mean_pct={v.mean():.4f} percent")
    print(f"RESULT cells_with_gap={int((v > 1e-4).sum())} count")
    print(f"RESULT null_flat_gap_pct={v[flat][0]:.4f} percent")
    print(f"RESULT gate_skipped={STATS['skipped']}/{STATS['calls']} count")
    print(f"RESULT forced_adoptions={STATS['forced_adoptions']} count")
    s = np.sort(v[~flat])[::-1]
    print(f"RESULT loo_structured_cells={s.size} count")
    print(f"RESULT loo_structured_range_pct={s.min():.4f}..{s.max():.4f} percent")
    print(f"RESULT loo_structured_mean_drop_best_pct={s[1:].mean():.4f} percent")
    L.print_env()


if __name__ == "__main__":
    main()
