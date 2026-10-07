"""D0-02 harness: the bang-bang seed LADDER against the two rungs production seeds.

METRIC (one line): objective gap = (production objective_value - challenger
objective_value) / |production objective_value|, in percent, where the
challenger is the SAME production ``_multi_start_minimize`` on the SAME
objective closure, bounds, args, maxiter, ftol, fd_eps and jac path, given
``_price_ranked_start(prices, E*f, p_max, dt)`` for f in 0.2 .. 1.5 as extra
starting points -- the family production samples at exactly two points
(f = 1.0, and f = _LOW_ENERGY_START_FRACTION = 0.35).

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/price_seed_race.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    cells                    = 32
    gap_max_pct              = 1.1087 +/- 0.15
    gap_mean_pct             = 0.1812 +/- 0.05
    cells_with_gap           = 13     +/- 2
    gap_mean_structured_pct  = 0.1616 +/- 0.05
    null_flat_gap_mean_pct   = 0.3187 +/- 0.10   (the effect does NOT vanish
                               at flat prices -- it is LARGER there)
    loo_structured_mean_drop_best_pct = 0.1265 +/- 0.04
    comfort_regressions      = 0      (exact)
    step0_differs_where_gap  = 9/13   +/- 2
The finding rests on the sign, on the flat-vs-structured comparison and on
comfort parity, not on the third decimal: L-BFGS-B basin selection is
BLAS-sensitive.

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(replaced), heatpump_optimizer.optimizer:_price_ranked_start (driven),
heatpump_optimizer.optimizer:_MULTI_START_SOLVES (lifted).

PERTURBATION (the judge runs it): D0_FRACTIONS="1.0,0.35" restricts the
ladder to the two rungs production already seeds. Every gap must collapse to
0.0000%, since the challenger then adds nothing production does not have.
Direction: removing the extra rungs removes the gap.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402

FRACTIONS = tuple(
    float(x) for x in os.environ.get(
        "D0_FRACTIONS", "0.2,0.4,0.6,0.8,1.0,1.2,1.5").split(",")
)

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")
CONFIGS = (("single", False, False), ("two_zone", True, False),
           ("single+dhw", False, True), ("two_zone+dhw", True, True))
WEATHER = "winter_cold"


def run():
    rows = []
    for price_p in PRICES:
        for name, tz, dhw in CONFIGS:
            opt, m, a, st = L.build(price_p, WEATHER, two_zone=tz, dhw=dhw)
            prod = opt.optimize(*a)
            opt2, m2, a2, st2 = L.build(price_p, WEATHER, two_zone=tz, dhw=dhw)
            pmax = float(m2.params.max_electrical_power)
            with L.solver(L.stronger_price_seeds(a2[1], pmax, 0.25,
                                                 fractions=FRACTIONS)):
                chal = opt2.optimize(*a2)
            o0, o1 = float(prod.objective_value), float(chal.objective_value)
            gap = (o0 - o1) / abs(o0) * 100.0 if np.isfinite(o0) and o0 else 0.0
            p0 = np.asarray(prod.power_schedule, dtype=float)
            p1 = np.asarray(chal.power_schedule, dtype=float)
            c0 = L.comfort_of(m, p0, a[0], *a[2:6])
            c1 = L.comfort_of(m2, p1, a2[0], *a2[2:6])
            rows.append({"price": price_p, "config": name, "two_zone": tz,
                         "gap": gap, "cost_prod": float(prod.predicted_cost),
                         "cost_chal": float(chal.predicted_cost),
                         "below_prod": c0["below_degree_steps"],
                         "below_chal": c1["below_degree_steps"],
                         "above_prod": c0["above_degree_steps"],
                         "above_chal": c1["above_degree_steps"],
                         "step0_prod": float(p0[0]),
                         "step0_chal": float(p1[0])})
            print(f"CELL {price_p:16s} {name:12s} obj {o0:11.5f} -> {o1:11.5f} "
                  f"gap {gap:+8.4f}%  cost {prod.predicted_cost:8.3f} -> "
                  f"{chal.predicted_cost:8.3f}  below "
                  f"{c0['below_degree_steps']:.4f}->{c1['below_degree_steps']:.4f}"
                  f"  above {c0['above_degree_steps']:.4f}->"
                  f"{c1['above_degree_steps']:.4f}  step0 {p0[0]:.3f}->{p1[0]:.3f}",
                  flush=True)
    return rows


def summarise(rows):
    g = np.array([r["gap"] for r in rows])
    flat = np.array([r["price"] == "flat" for r in rows])
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT gap_max_pct={g.max():.4f} percent")
    print(f"RESULT gap_mean_pct={g.mean():.4f} percent")
    print(f"RESULT cells_with_gap={int((g > 1e-4).sum())} count")
    print(f"RESULT null_flat_gap_mean_pct={g[flat].mean():.4f} percent")
    print(f"RESULT null_flat_gap_max_pct={g[flat].max():.4f} percent")
    print(f"RESULT gap_mean_structured_pct={g[~flat].mean():.4f} percent")
    s = np.sort(g[~flat])[::-1]
    print(f"RESULT loo_structured_cells={s.size} count")
    print(f"RESULT loo_structured_range_pct={s.min():.4f}..{s.max():.4f} percent")
    print(f"RESULT loo_structured_mean_drop_best_pct={s[1:].mean():.4f} percent")
    worse = sum(1 for r in rows
                if r["below_chal"] > r["below_prod"] + 1e-9
                or r["above_chal"] > r["above_prod"] + 1e-9)
    print(f"RESULT comfort_regressions={worse} count")
    moved = sum(1 for r in rows if r["gap"] > 1e-4
                and abs(r["step0_chal"] - r["step0_prod"]) > 1e-3)
    withgap = sum(1 for r in rows if r["gap"] > 1e-4)
    print(f"RESULT step0_differs_where_gap={moved}/{withgap} count")
    for r in rows:
        if r["gap"] > 1e-4:
            print(f"RESULT money_{r['price']}_{r['config']}="
                  f"{r['cost_prod'] - r['cost_chal']:.3f} "
                  f"SEK_per_day_on_{r['cost_prod']:.2f}_bill")


if __name__ == "__main__":
    rows = run()
    summarise(rows)
    L.print_env()
