"""D0-s1 round 9: the L-BFGS-B stop rule (ftol=1e-6) A/B on the shipped plan.

Metric (one line): per cell, drop = shipped objective (production) - shipped objective
(production with every L-BFGS-B call's ftol tightened to --ftol), both read from
OptimizationResult.objective_value; cost = total L-BFGS-B iterations (nit) and
function evaluations (nfev) summed over every production minimize call, both arms.
Count key: HeatPumpOptimizer.optimize(...).objective_value and scipy's own nit/nfev
as returned through optimizer:_scoped_minimize -- counts, contention-immune.

Command (from the repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/s1/stoprule_ab.py [--ftol 1e-9] [--flat] [--jobs 2]
Instrumented symbol: heatpump_optimizer.optimizer:_scoped_minimize (wrapped: the
options dict's ftol is replaced when it is production's 1e-6, everything else
passed through; both _multi_start_minimize and _lbfgsb_restart call it).
Perturbation = the arm itself (ftol 1e-6 -> --ftol); --ftol 1e-6 is the identity
control (drop exactly 0); --flat is the price null control.
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
from unittest import mock
import race
from race import om

REAL_SCOPED = om._scoped_minimize


def solve(tz, dhw, pp, wp, flat, ftol):
    o, m, pr, ot, wi, ra, so, st = race.build(tz, dhw, pp, wp, 24, flat)
    tally = {"nit": 0, "nfev": 0, "calls": 0}

    def scoped(*a, **kw):
        opts = dict(kw.get("options") or {})
        if ftol is not None and opts.get("ftol") == 1e-6:
            opts["ftol"] = ftol
            kw["options"] = opts
        r = REAL_SCOPED(*a, **kw)
        tally["nit"] += int(getattr(r, "nit", 0)); tally["nfev"] += int(getattr(r, "nfev", 0))
        tally["calls"] += 1
        return r

    with mock.patch.object(om, "_scoped_minimize", scoped):
        res = o.optimize(st, pr, ot, wi, ra, so, race.START)
    sp = np.asarray(res.power_schedule, float)
    dh = np.asarray(res.dhw_power_schedule, float) if dhw and res.dhw_power_schedule else np.zeros_like(pr)
    fl, ce = race.feas(m, st, ot, wi, ra, so, sp, tz)
    return {"obj": float(res.objective_value), "E": float(np.sum(pr * (sp + dh)) * 0.25),
            "floor": fl, "ceil": ce, "step0": float(sp[0]), **tally}


def one(args):
    tz, dhw, pp, wp, flat, ftol = args
    return args, solve(tz, dhw, pp, wp, flat, None), solve(tz, dhw, pp, wp, flat, ftol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ftol", type=float, default=1e-9)
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--weathers", default=",".join(race.WEATHERS))
    x = ap.parse_args()
    cells = [(tz, dh, pp, wp, x.flat, x.ftol) for tz in (False, True) for dh in (True, False)
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
    rel, worse, nit_a, nit_b, nf_a, nf_b, dE = [], 0, 0, 0, 0, 0, []
    for (tz, dh, pp, wp, fl_, ft), a, b in rows:
        d = a["obj"] - b["obj"]; rel.append(d / abs(a["obj"])); dE.append(a["E"] - b["E"])
        nit_a += a["nit"]; nit_b += b["nit"]; nf_a += a["nfev"]; nf_b += b["nfev"]
        if b["floor"] > a["floor"] + race.FEAS_TOL or b["ceil"] > a["ceil"] + race.FEAS_TOL:
            worse += 1
        print(f"CELL {'two' if tz else 'one'}|{'dhw' if dh else 'nodhw'}|{pp}|{wp}{'|FLAT' if x.flat else ''}: "
              f"obj {a['obj']:.6f} -> {b['obj']:.6f} drop={d:.4f} ({100*d/abs(a['obj']):.4f}%) "
              f"E {a['E']:.2f} -> {b['E']:.2f} floor {a['floor']:.4f} -> {b['floor']:.4f} "
              f"nit {a['nit']} -> {b['nit']} nfev {a['nfev']} -> {b['nfev']}")
    rel = np.array(rel)
    print(f"RESULT cells={len(rel)} count")
    print(f"RESULT cells_improved_over_0.1pct={int((rel > 1e-3).sum())} count")
    print(f"RESULT drop_rel_max={100*rel.max():.4f} %")
    print(f"RESULT drop_rel_min={100*rel.min():.4f} %")
    print(f"RESULT drop_rel_mean={100*rel.mean():.4f} %")
    print(f"RESULT drop_rel_mean_drop_best={100*np.delete(rel, rel.argmax()).mean():.4f} %")
    print(f"RESULT energy_sek_drop_sum={sum(dE):.4f} SEK")
    print(f"RESULT nit_ratio={nit_b / max(nit_a, 1):.4f} ratio")
    print(f"RESULT nfev_ratio={nf_b / max(nf_a, 1):.4f} ratio")
    print(f"RESULT cells_feasibility_worse={worse} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
