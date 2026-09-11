"""D0-01 harness: how much objective the shipped multi-start leaves on the table.

METRIC (one line): objective gap = (production objective_value - challenger
objective_value) / |production objective_value|, in percent, where the
challenger is the SAME production ``_multi_start_minimize`` on the SAME
objective closure, bounds, args, ``fd_eps`` and jac path, given five extra
constant-power starting points (lo + f*(hi-lo), f in 0, .25, .5, .75, 1) and
with ``_MULTI_START_SOLVES`` lifted so no scored candidate is discarded.
Budget (maxiter), tolerance (ftol) and the batched-gradient path are untouched.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/seed_race.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    gap_max_pct            = 0.5618  +/- 0.02   (two_zone flat winter_cold)
    gap_mean_two_zone_pct  = 0.2107  +/- 0.02
    gap_mean_single_zone_pct = 0.0000 +/- 0.0005
    cells_with_gap         = 8       +/- 1  (of 32)
    comfort_regressions    = 0       (exact)
    null_control_gap_pct   = the flat-price rows are NOT smaller than the
                             structured-price rows; see RESULT null_* below.
Tolerance is set by BLAS-to-BLAS solver noise; the sign and the flat-vs-
structured comparison are what the finding rests on, not the third decimal.

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(replaced) and heatpump_optimizer.optimizer:_MULTI_START_SOLVES (lifted).

PERTURBATION (the judge runs it): set ``extra_seed_levels=()`` in the
challenger (env D0_NO_EXTRA_SEEDS=1) -- every gap must collapse to 0.0000%,
because the only thing the challenger adds is those starting points.
Direction: removing the seeds removes the gap.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402  (pins BLAS threads before numpy)
import numpy as np  # noqa: E402

LEVELS = () if os.environ.get("D0_NO_EXTRA_SEEDS") else (0.0, 0.25, 0.5, 0.75, 1.0)

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")
CONFIGS = (("single", False, False), ("single+dhw", False, True),
           ("two_zone", True, False), ("two_zone+dhw", True, True))
WEATHER = "winter_cold"


def run():
    rows = []
    for price_p in PRICES:
        for name, tz, dhw in CONFIGS:
            opt, m, a, st = L.build(price_p, WEATHER, two_zone=tz, dhw=dhw)
            prod = opt.optimize(*a)
            opt2, m2, a2, st2 = L.build(price_p, WEATHER, two_zone=tz, dhw=dhw)
            with L.solver(L.stronger(maxiter_mul=1, extra_seed_levels=LEVELS,
                                     polish=False)):
                chal = opt2.optimize(*a2)
            o0 = float(prod.objective_value)
            o1 = float(chal.objective_value)
            gap = (o0 - o1) / abs(o0) * 100.0 if np.isfinite(o0) and o0 else 0.0
            p0 = np.asarray(prod.power_schedule, dtype=float)
            p1 = np.asarray(chal.power_schedule, dtype=float)
            c0 = L.comfort_of(m, p0, a[0], *a[2:6])
            c1 = L.comfort_of(m2, p1, a2[0], *a2[2:6])
            rows.append({
                "price": price_p, "config": name, "two_zone": tz, "dhw": dhw,
                "obj_prod": o0, "obj_chal": o1, "gap": gap,
                "cost_prod": float(prod.predicted_cost),
                "cost_chal": float(chal.predicted_cost),
                "below_prod": c0["below_degree_steps"],
                "below_chal": c1["below_degree_steps"],
                "above_prod": c0["above_degree_steps"],
                "above_chal": c1["above_degree_steps"],
                "step0_prod": float(p0[0]), "step0_chal": float(p1[0]),
            })
            print(f"CELL {price_p:16s} {name:12s} obj {o0:11.5f} -> {o1:11.5f} "
                  f"gap {gap:+8.4f}%  cost {prod.predicted_cost:8.3f} -> "
                  f"{chal.predicted_cost:8.3f}  below {c0['below_degree_steps']:.4f}"
                  f"->{c1['below_degree_steps']:.4f}  above "
                  f"{c0['above_degree_steps']:.4f}->{c1['above_degree_steps']:.4f}"
                  f"  step0 {p0[0]:.3f}->{p1[0]:.3f}", flush=True)
    return rows


def summarise(rows):
    gaps = np.array([r["gap"] for r in rows])
    tz = np.array([r["two_zone"] for r in rows])
    flat = np.array([r["price"] == "flat" for r in rows])
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT gap_max_pct={gaps.max():.4f} percent")
    print(f"RESULT gap_mean_pct={gaps.mean():.4f} percent")
    print(f"RESULT gap_mean_two_zone_pct={gaps[tz].mean():.4f} percent")
    print(f"RESULT gap_mean_single_zone_pct={gaps[~tz].mean():.4f} percent")
    print(f"RESULT cells_with_gap={int((gaps > 1e-4).sum())} count")
    # leave-one-out over the two-zone cells (the arm that carries the effect)
    g = np.sort(gaps[tz])[::-1]
    print(f"RESULT loo_two_zone_cells={g.size} count")
    print(f"RESULT loo_two_zone_range_pct={g.min():.4f}..{g.max():.4f} percent")
    print(f"RESULT loo_two_zone_mean_drop_best_pct={g[1:].mean():.4f} percent")
    # the null control: the same race at profiles.prices("flat")
    print(f"RESULT null_flat_gap_mean_pct={gaps[flat].mean():.4f} percent")
    print(f"RESULT null_structured_gap_mean_pct={gaps[~flat].mean():.4f} percent")
    print(f"RESULT null_flat_two_zone_gap_max_pct="
          f"{gaps[flat & tz].max():.4f} percent")
    # feasibility parity
    worse = sum(1 for r in rows
                if r["below_chal"] > r["below_prod"] + 1e-9
                or r["above_chal"] > r["above_prod"] + 1e-9)
    print(f"RESULT comfort_regressions={worse} count")
    # MPC masking: does the step-0 action move where there is a gap?
    moved = sum(1 for r in rows if r["gap"] > 1e-4
                and abs(r["step0_chal"] - r["step0_prod"]) > 1e-3)
    withgap = sum(1 for r in rows if r["gap"] > 1e-4)
    print(f"RESULT step0_differs_where_gap={moved}/{withgap} count")
    # money, only beside the flat arm, as a share of the daily bill
    for r in rows:
        if r["gap"] > 1e-4:
            d = r["cost_prod"] - r["cost_chal"]
            print(f"RESULT money_{r['price']}_{r['config']}="
                  f"{d:.3f} SEK_per_day_on_{r['cost_prod']:.2f}_bill")


if __name__ == "__main__":
    rows = run()
    summarise(rows)
    L.print_env()
