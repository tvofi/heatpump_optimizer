"""D0-s1 round 9: the DHW path's seed set against the space-only path's, A/B.

Metric (one line): per cell, drop = shipped objective (production) - shipped objective
(production with the space-only path's missing seeds handed to _solve_space's
cold-start multi-start), both read from OptimizationResult.objective_value, i.e.
production's own objective at production's own returned plan.
Count key: HeatPumpOptimizer.optimize(...).objective_value (the value the seam
delivers), not any input attribute.

Command (from the repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/s1/seeds_ab.py [--flat] [--perturb space_seeds_dhw|deep_anchor_dhw] [--dhw off]
Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize (wrapped;
the real function refines every candidate) on the HeatPumpOptimizer._solve_space
cold-start call.
Control arms: --dhw off (the space-only path, where the perturbation is a no-op by
construction: drop must be exactly 0), --flat (flat prices: the null control).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box B1 (4 vCPU Linux, CPython
3.14.0rc2, numpy 2.4.6, scipy 1.17.1). Expected: see REPORT.md, tolerance +/-0.05 pp.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import race


def one(args):
    tz, dhw, pp, wp, flat, pert = args
    a = race.shipped_only(tz, dhw, pp, wp, 24, flat, None)
    b = race.shipped_only(tz, dhw, pp, wp, 24, flat, pert)
    return (tz, dhw, pp, wp, a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--perturb", default="space_seeds_dhw")
    ap.add_argument("--dhw", default="on")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--weathers", default=",".join(race.WEATHERS))
    x = ap.parse_args()
    dhw = x.dhw == "on"
    cells = [(tz, dhw, pp, wp, x.flat, x.perturb) for tz in (False, True)
             for pp in (race.PRICES[:1] if x.flat else race.PRICES) for wp in x.weathers.split(",")]
    # --flat: every price profile collapses to profiles.prices('flat'), so one
    # profile per (topology, weather) is the whole null-control grid.
    t0p, t0t = time.process_time(), time.thread_time()
    if x.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(x.jobs) as pool:
            rows = pool.map(one, cells)
    else:
        rows = [one(c) for c in cells]
    drops, rel, sek, worse = [], [], [], 0
    for tz, dh, pp, wp, a, b in rows:
        d = a["obj"] - b["obj"]
        drops.append(d); rel.append(d / abs(a["obj"])); sek.append(a["energy_sek"] - b["energy_sek"])
        if b["floor"] > a["floor"] + race.FEAS_TOL or b["ceil"] > a["ceil"] + race.FEAS_TOL:
            worse += 1
        print(f"CELL {'two' if tz else 'one'}|{'dhw' if dh else 'nodhw'}|{pp}|{wp}{'|FLAT' if x.flat else ''}: "
              f"obj {a['obj']:.6f} -> {b['obj']:.6f} drop={d:.4f} ({100*d/abs(a['obj']):.4f}%) "
              f"energy {a['energy_sek']:.2f} -> {b['energy_sek']:.2f} SEK floor {a['floor']:.4f} -> {b['floor']:.4f} "
              f"step0 {a['step0']:.3f} -> {b['step0']:.3f} ncand {a['ncand']} -> {b['ncand']} "
              f"minDHW {a['min_dhw_T']} -> {b['min_dhw_T']}")
    rel = np.array(rel); drops = np.array(drops); sek = np.array(sek)
    print(f"RESULT cells={len(rel)} count")
    print(f"RESULT cells_improved_over_0.01pct={int((rel > 1e-4).sum())} count")
    print(f"RESULT drop_rel_max={100*rel.max():.4f} %")
    print(f"RESULT drop_rel_min={100*rel.min():.4f} %")
    print(f"RESULT drop_rel_mean={100*rel.mean():.4f} %")
    print(f"RESULT drop_rel_mean_drop_best={100*np.delete(rel, rel.argmax()).mean():.4f} %")
    print(f"RESULT drop_obj_sum={drops.sum():.4f} objective-units")
    print(f"RESULT energy_sek_drop_sum={sek.sum():.4f} SEK")
    print(f"RESULT cells_feasibility_worse={worse} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
