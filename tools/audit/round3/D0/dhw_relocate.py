"""D0-03 harness: can hot-water energy be moved to a cheaper hour the shipped
planner left unused, without weakening the tank's own availability contract?

METRIC (one line): dhw_cost_gap = (sum(prices*d_prod) - sum(prices*d_chal))*dt
/ sum(prices*d_prod)*dt, in percent, where d_chal is reached from the SHIPPED
hot-water schedule by single-block relocations to strictly cheaper steps, each
accepted only if ``ThermalModel.simulate_dhw_only`` on production's own
``requirement``/``draw_rates``/``max_temp`` arrays leaves the shortfall and the
over-temperature no worse than the shipped schedule's, and every non-zero power
stays within [min_run_power, p_dhw_max]. ``obj_gap`` is then the end-to-end
production objective_value with that schedule forced in, so the space solve and
the co-optimisation pass both run against it.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/dhw_relocate.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    cells                    = 8
    dhw_cost_gap_max_pct     = 0.92 +/- 0.15
    null_flat_dhw_gap_pct    = 0.0000 (exact -- no step is strictly cheaper on
                               a flat curve, so the search cannot move)
    dhw_shortfall_regressions = 0 (exact)
    identity_control_max_abs_pct = 0.000000 (exact -- forcing production's own
                               schedule back in reproduces its objective)

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:HeatPumpOptimizer.
_build_dhw_requirements (captured, then its ``schedule`` field replaced) and
HeatPumpOptimizer._plan_dhw_cheapest_first (captured for the feasibility arrays).

PERTURBATION (the judge runs it): D0_DHW_REQUIRE_CHEAPER=0 relaxes the
"strictly cheaper step" test to "any step", so the search may also move energy
to a DEARER hour -- the reported gap must then be no larger and the flat-price
arm must still be 0.0000 because the acceptance test is on cost.
Direction: the gap is bounded by the price spread; on a flat curve it is zero.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")
WEATHER = "winter_cold"
DT = 0.25
STRICT = os.environ.get("D0_DHW_REQUIRE_CHEAPER", "1") != "0"


def relocate(model, plan, kw, prices, rounds=40):
    d = np.array(plan, dtype=float)
    mn, mx = float(kw["min_run_power"]), float(kw["p_dhw_max"])
    _, short0, over0 = L.dhw_feasible(model, d, kw)
    best = float(np.sum(prices * d) * DT)
    moves = 0
    for _ in range(rounds):
        winner, winner_cost = None, best
        cheap_order = np.argsort(prices)
        for i in np.where(d > 1e-9)[0]:
            for j in cheap_order:
                if STRICT and prices[j] >= prices[i] - 1e-12:
                    continue
                amount = min(d[i], mx - d[j])
                if amount <= 1e-9:
                    continue
                nj, ni = d[j] + amount, d[i] - amount
                if nj < mn - 1e-9:
                    continue
                if 1e-9 < ni < mn - 1e-9:
                    continue
                cand = d.copy()
                cand[i] = ni if ni > 1e-9 else 0.0
                cand[j] = nj
                cost = float(np.sum(prices * cand) * DT)
                if cost >= winner_cost - 1e-9:
                    continue
                _, short, over = L.dhw_feasible(model, cand, kw)
                if short > short0 + 1e-9 or over > over0 + 1e-9:
                    continue
                winner, winner_cost = cand, cost
        if winner is None:
            break
        d, best, moves = winner, winner_cost, moves + 1
    return d, best, moves, short0, over0


def main():
    rows = []
    for price_p in PRICES:
        opt, m, a, st = L.build(price_p, WEATHER, two_zone=False, dhw=True)
        store = {}
        with L.capture_dhw(store):
            prod = opt.optimize(*a)
        kw = store["greedy_kwargs"]
        prices = np.asarray(a[1], dtype=float)
        d0 = np.asarray(prod.dhw_power_schedule, dtype=float)
        c0 = float(np.sum(prices * d0) * DT)
        d1, c1, moves, short0, over0 = relocate(m, d0, kw, prices)
        _, short1, over1 = L.dhw_feasible(m, d1, kw)
        # Identity control: forcing production's OWN schedule back in must
        # reproduce production's objective exactly, or the replacement itself
        # -- not the relocation -- is what moved the number.
        opt3, m3, a3, st3 = L.build(price_p, WEATHER, two_zone=False, dhw=True)
        with L.force_dhw(d0):
            ident = opt3.optimize(*a3)
        opt2, m2, a2, st2 = L.build(price_p, WEATHER, two_zone=False, dhw=True)
        with L.force_dhw(d1):
            chal = opt2.optimize(*a2)
        o0, o1 = float(prod.objective_value), float(chal.objective_value)
        ident_gap = abs(float(ident.objective_value) - o0) / abs(o0) * 100.0
        dgap = (c0 - c1) / c0 * 100.0 if c0 > 1e-9 else 0.0
        ogap = (o0 - o1) / abs(o0) * 100.0 if np.isfinite(o0) and o0 else 0.0
        p0 = np.asarray(prod.power_schedule, dtype=float)
        p1 = np.asarray(chal.power_schedule, dtype=float)
        cm0 = L.comfort_of(m, p0, a[0], *a[2:6])
        cm1 = L.comfort_of(m2, p1, a2[0], *a2[2:6])
        rows.append({"price": price_p, "dgap": dgap, "ogap": ogap,
                     "ident_gap": ident_gap,
                     "moves": moves, "short0": short0, "short1": short1,
                     "over0": over0, "over1": over1,
                     "cost_prod": float(prod.predicted_cost),
                     "cost_chal": float(chal.predicted_cost),
                     "below_prod": cm0["below_degree_steps"],
                     "below_chal": cm1["below_degree_steps"]})
        print(f"CELL {price_p:16s} dhw_cost {c0:8.4f} -> {c1:8.4f} "
              f"({dgap:+6.3f}%) moves={moves}  obj {o0:10.5f} -> {o1:10.5f} "
              f"({ogap:+7.4f}%)  short {short0:.5f}->{short1:.5f}  "
              f"over {over0:.5f}->{over1:.5f}  bill {prod.predicted_cost:7.3f}"
              f" -> {chal.predicted_cost:7.3f}  identity={ident_gap:.6f}%",
              flush=True)
    d = np.array([r["dgap"] for r in rows])
    o = np.array([r["ogap"] for r in rows])
    flat = np.array([r["price"] == "flat" for r in rows])
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT dhw_cost_gap_max_pct={d.max():.4f} percent")
    print(f"RESULT dhw_cost_gap_mean_pct={d.mean():.4f} percent")
    print(f"RESULT obj_gap_max_pct={o.max():.4f} percent")
    print(f"RESULT cells_with_gap={int((d > 1e-4).sum())} count")
    print(f"RESULT null_flat_dhw_gap_pct={d[flat][0]:.4f} percent")
    print(f"RESULT null_flat_obj_gap_pct={o[flat][0]:.4f} percent")
    s = np.sort(d[~flat])[::-1]
    print(f"RESULT loo_structured_cells={s.size} count")
    print(f"RESULT loo_structured_range_pct={s.min():.4f}..{s.max():.4f} percent")
    print(f"RESULT loo_structured_mean_drop_best_pct={s[1:].mean():.4f} percent")
    reg = sum(1 for r in rows if r["short1"] > r["short0"] + 1e-9
              or r["over1"] > r["over0"] + 1e-9
              or r["below_chal"] > r["below_prod"] + 1e-9)
    print(f"RESULT dhw_shortfall_regressions={reg} count")
    print(f"RESULT identity_control_max_abs_pct="
          f"{max(r['ident_gap'] for r in rows):.6f} percent")
    for r in rows:
        if r["dgap"] > 1e-4:
            print(f"RESULT money_{r['price']}="
                  f"{r['cost_prod'] - r['cost_chal']:.3f} "
                  f"SEK_per_day_on_{r['cost_prod']:.2f}_bill")
    L.print_env()


if __name__ == "__main__":
    main()
