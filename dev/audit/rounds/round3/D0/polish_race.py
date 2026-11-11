"""D0-02 harness: does L-BFGS-B stop short of its own basin's floor?

METRIC (one line): objective gap = (production objective_value - challenger
objective_value)/|production objective_value| in percent, where the challenger
adds ONE thing to production's search: after the multi-start finishes, L-BFGS-B
is restarted from the winning point itself, with the SAME objective closure,
bounds, args, maxiter, ftol, eps, fd_eps and jac path. No new starting point,
no bigger budget, no different tolerance -- only a fresh limited-memory history
from the answer production already had.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/polish_race.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    cells                   = 32
    gap_max_pct             = 1.1703 +/- 0.15  (summer_negative, single zone)
    gap_mean_pct            = 0.0462 +/- 0.02
    cells_with_gap          = 9      +/- 2
    null_flat_gap_mean_pct  = 0.0051 +/- 0.005
    gap_mean_structured_pct = 0.0521 +/- 0.02
    loo_mean_drop_best_pct  = 0.0100 +/- 0.01  (the aggregate is carried by
                              one cell -- read the max, not the mean)
    comfort_regressions     = 0 (exact)
    step0_differs_where_gap = 2/9    +/- 1
The sign and the flat-vs-structured comparison carry the finding, not the
third decimal.

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(replaced with a wrapper that calls it, then calls it again from its own result).

PERTURBATION (the judge runs it): D0_NO_POLISH=1 drops the restart, so the
challenger becomes production -- every gap must collapse to 0.0000 %.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402

POLISH = os.environ.get("D0_NO_POLISH") != "1"

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")
CONFIGS = (("single", False, False), ("two_zone", True, False),
           ("single+dhw", False, True), ("two_zone+dhw", True, True))


def main():
    rows = []
    for price_p in PRICES:
        for name, tz, dhw in CONFIGS:
            opt, m, a, st = L.build(price_p, "winter_cold", two_zone=tz, dhw=dhw)
            prod = opt.optimize(*a)
            opt2, m2, a2, st2 = L.build(price_p, "winter_cold", two_zone=tz,
                                        dhw=dhw)
            with L.solver(L.stronger(maxiter_mul=1, extra_seed_levels=(),
                                     polish=POLISH)):
                chal = opt2.optimize(*a2)
            o0, o1 = float(prod.objective_value), float(chal.objective_value)
            gap = (o0 - o1) / abs(o0) * 100.0 if np.isfinite(o0) and o0 else 0.0
            p0 = np.asarray(prod.power_schedule, dtype=float)
            p1 = np.asarray(chal.power_schedule, dtype=float)
            c0 = L.comfort_of(m, p0, a[0], *a[2:6])
            c1 = L.comfort_of(m2, p1, a2[0], *a2[2:6])
            rows.append({"price": price_p, "config": name, "gap": gap,
                         "cost_prod": float(prod.predicted_cost),
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
                  f"  step0 {p0[0]:.3f}->{p1[0]:.3f}", flush=True)
    g = np.array([r["gap"] for r in rows])
    flat = np.array([r["price"] == "flat" for r in rows])
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT gap_max_pct={g.max():.4f} percent")
    print(f"RESULT gap_mean_pct={g.mean():.4f} percent")
    print(f"RESULT cells_with_gap={int((g > 1e-4).sum())} count")
    print(f"RESULT null_flat_gap_mean_pct={g[flat].mean():.4f} percent")
    print(f"RESULT gap_mean_structured_pct={g[~flat].mean():.4f} percent")
    s = np.sort(g)[::-1]
    print(f"RESULT loo_cells={s.size} count")
    print(f"RESULT loo_range_pct={s.min():.4f}..{s.max():.4f} percent")
    print(f"RESULT loo_mean_drop_best_pct={s[1:].mean():.4f} percent")
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
    L.print_env()


if __name__ == "__main__":
    main()
