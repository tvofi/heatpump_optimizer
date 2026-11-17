"""D2.M3 identities over every golden: predicted-cost-sum, penalty-scaling,
gradient-fd.

Metric definitions (one line each):
  cost_sum_err  = |predicted_cost - sum_k (p_raw[k]*P[k] - m[k]*min(P[k], s[k]))*dt|
                  with p_raw the INPUT import prices, P = published space+DHW
                  schedule, s the PV surplus, m = pv.import_margin; tolerance 1e-9.
  scaling_err   = max over k in {0,0.5,2,5} and x in {plan, 4 random points} of
                  |f_k(x) - comfort(x) - k*(f_1(x) - comfort(x))| / max(1,|f_1(x)|);
                  f_k the production objective rebuilt at price_weight=k; tol 1e-9.
  grad_relerr   = ||g_solver - g_central||_2 / ||g_central||_2 at 4 random interior
                  points + the plan, g_solver = optimizer._batch_fd_gradient (the
                  2-point step L-BFGS-B consumes), g_central = (f(x+h)-f(x-h))/2h, h=1e-4.
Count key: cost_sum_err is keyed on result.predicted_cost (the value the seam
delivers) against the solve's raw input prices.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m3_objective.py [--only NAME]
      add --perturb-risk0 to set price_risk_lambda=0 on every scenario (the
      cost_sum mismatch on price_risk must go to_zero).
Expected at baseline: cost_sum mismatches = 1 (price_risk, ~3.75 currency, the
risk premium lambda*sigma booked as spend); scaling_err <= 1e-9 on all 50;
grad_relerr reported (no tolerance; see REPORT).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared, 4 cores).
"""
import _common  # noqa: F401  (thread pin first)
from _common import footer, golden_names, solve_golden, np

import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--perturb-risk0", action="store_true")
    ap.add_argument("--skip-grad", action="store_true")
    a = ap.parse_args()
    import golden  # noqa: F401  (puts the package on sys.path)
    from heatpump_optimizer import optimizer as om, pv

    names = [a.only] if a.only else golden_names()
    rng = np.random.default_rng(11)
    mism = 0
    worst_scale = 0.0
    grad_rows = []
    for name in names:
        patch = None
        if a.perturb_risk0:
            def patch(o):
                o.config.price_risk_lambda = 0.0
        rec = solve_golden(name, opt_patch=patch)
        opt, res, inp = rec["opt"], rec["result"], rec["inputs"]
        n = len(res.power_schedule)
        dt = opt.config.dt_hours
        raw = np.asarray(inp.forecast.prices, dtype=float)[:n]
        P = np.asarray(res.power_schedule, dtype=float)
        if res.dhw_power_schedule:
            P = P + np.asarray(res.dhw_power_schedule, dtype=float)
        s = np.asarray(opt._pv_surplus if opt._pv_surplus is not None else np.zeros(n), dtype=float)[:n]
        m = pv.import_margin(raw, opt.config.pv_export_price)
        cover = m * np.minimum(P, s) if np.any(s > 1e-6) else 0.0
        expect = float(np.sum(raw * P - cover) * dt)
        err = abs(res.predicted_cost - expect)
        pub = np.asarray(res.prices, dtype=float)
        pub_dev = float(np.max(np.abs(pub - raw)))
        bl = np.asarray(res.baseline_power_schedule, dtype=float)
        cover_b = m * np.minimum(bl, s) if np.any(s > 1e-6) else 0.0
        bl_err = abs(res.baseline_cost - float(np.sum(raw * bl - cover_b) * dt))
        if err > 1e-9:
            mism += 1
        print(f"CELL predicted-cost-sum golden={name} err={err:.3e} predicted={res.predicted_cost:.6f} "
              f"raw_sum={expect:.6f} published_price_dev={pub_dev:.3g} baseline_err={bl_err:.3e}")

        # --- penalty scaling (price_weight) ---
        h, closures = rec["horizons"][-1]
        x_plan = np.asarray(res.power_schedule, dtype=float)
        dhw = np.asarray(res.dhw_power_schedule, dtype=float) if res.dhw_power_schedule else None
        pmax = opt.model.params.max_electrical_power
        xs = [x_plan] + [rng.uniform(0, pmax * 0.7, n) for _ in range(4)]
        saved = opt.config.price_weight

        def f_at(k, x):
            opt.config.price_weight = k
            try:
                _, obj, _, _ = opt._solve_objectives(h)
                return float(obj(x, dhw))
            finally:
                opt.config.price_weight = saved

        def comfort(x):
            traj = closures[0](x)
            pen, cc = opt._comfort_terms(traj[0], traj[2], traj[3], h.comfort_targets,
                                         h.temp_min_bounds, h.temp_max_bounds,
                                         np.maximum(h.comfort_targets - h.temp_min_bounds, 1.0))
            return pen + cc
        cell_worst = 0.0
        for x in xs:
            f1 = f_at(1.0, x)
            c = comfort(x)
            for k in (0.0, 0.5, 2.0, 5.0):
                fk = f_at(k, x)
                e = abs(fk - c - k * (f1 - c)) / max(1.0, abs(f1))
                cell_worst = max(cell_worst, e)
        worst_scale = max(worst_scale, cell_worst)
        print(f"CELL penalty-scaling golden={name} scaling_err={cell_worst:.3e}")

        # --- gradient vs central FD ---
        if not a.skip_grad and rec["runs"]:
            obj, batch, x0, bounds, args = rec["runs"][-1]
            lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
            pts = [np.clip(x0, lb, ub)] + [lb + (ub - lb) * rng.uniform(0.1, 0.9, lb.size) for _ in range(4)]
            eps = om._LBFGSB_FD_EPS
            errs = []
            worst_i = None
            for x in pts:
                g_s = om._batch_fd_gradient(batch, args, x, None, eps, bounds)
                free = (ub - lb) > 2 * eps
                interior = free & (x - lb > eps) & (ub - x > eps)
                idx = np.flatnonzero(interior)
                if idx.size == 0:
                    continue
                rows_p = np.tile(x, (idx.size, 1)); rows_m = rows_p.copy()
                rows_p[np.arange(idx.size), idx] += eps
                rows_m[np.arange(idx.size), idx] -= eps
                fp = np.asarray(batch(rows_p, *args)); fm = np.asarray(batch(rows_m, *args))
                g_c = (fp - fm) / (2 * eps)
                d = np.abs(g_s[idx] - g_c)
                rel = float(np.linalg.norm(g_s[idx] - g_c) / max(np.linalg.norm(g_c), 1e-12))
                errs.append(rel)
                j = int(np.argmax(d))
                if worst_i is None or d[j] > worst_i[1]:
                    worst_i = (int(idx[j]), float(d[j]), float(g_c[j]), float(g_s[idx[j]]))
            if errs:
                grad_rows.append((name, max(errs), float(np.median(errs))))
                print(f"CELL gradient-fd golden={name} relerr_max={max(errs):.3e} relerr_median={np.median(errs):.3e} "
                      f"per_point=[{','.join(f'{e:.1e}' for e in errs)}] (point 0 = the solve's start x0) "
                      f"worst_step={worst_i[0]} |dg|={worst_i[1]:.3e} g_central={worst_i[2]:.4g} g_solver={worst_i[3]:.4g}")
        sys.stdout.flush()

    print(f"RESULT cost_sum_mismatches={mism} count")
    print(f"RESULT cells={len(names)} count")
    print(f"RESULT scaling_err_max={worst_scale:.3e} ratio")
    if grad_rows:
        mx = max(grad_rows, key=lambda r: r[1])
        print(f"RESULT grad_relerr_max={mx[1]:.3e} ratio (golden={mx[0]})")
        meds = sorted(r[2] for r in grad_rows)
        print(f"RESULT grad_relerr_median_of_medians={meds[len(meds)//2]:.3e} ratio")
    footer()


if __name__ == "__main__":
    main()
