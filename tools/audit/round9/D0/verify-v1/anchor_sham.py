"""Round 9 D0 verifier V1: is D0-s1-01's gain the 0.20x anchor, or any extra seed?

Metric (one line): per cell and arm, drop = (objective_value shipped by production
- objective_value shipped with ONE extra candidate appended to HeatPumpOptimizer.
_solve_space's cold-start _multi_start_minimize call) / |shipped| in %, read from
HeatPumpOptimizer.optimize(...).objective_value. Count key: that objective_value.
Arms: deep020 (the finding's 0.20x baseline-energy bang-bang anchor), dup0 (a sham:
a copy of production's own first candidate), frac050 / frac010 (the same anchor
at 0.50x / 0.10x baseline energy).

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/verify-v1/anchor_sham.py [--flat] [--jobs 2]
Instrumented symbol: heatpump_optimizer.optimizer:_multi_start_minimize (wrapped,
first multi-candidate call on the DHW path only; the real function refines).
Perturbation: the arm itself (the appended seed); dup0 is the sham control, which
must NOT reproduce deep020's drop if the finding's attribution holds.
Expected: deep020 two|dhw|winter_narrow|winter_cold 0.2507 % (+-0.05 pp), as seeds_ab.py.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence tree 6f51db2c);
machine: 4 vCPU cloud container, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, argparse, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "s1"))
import numpy as np
from unittest import mock
import race  # D0-s1's harness module: build(), START, om, HeatPumpOptimizer

om = race.om
HPO = race.HeatPumpOptimizer
REAL_MS = om._multi_start_minimize
CELLS = [("winter_narrow", "winter_cold"), ("winter_narrow", "winter_mild"),
         ("winter_extreme", "winter_cold"), ("winter_typical", "winter_cold")]
ARMS = ("none", "deep020", "dup0", "frac050", "frac010")


def shipped(pp, wp, flat, arm):
    tz, dhw = True, True
    base = {}
    if arm not in ("none", "dup0"):
        o2, _m2, pr2, ot2, wi2, ra2, so2, st2 = race.build(tz, dhw, pp, wp, 24, flat)
        real_base = HPO._compute_baseline_power

        def bp(self, *a, **kw):
            out = real_base(self, *a, **kw)
            base.setdefault("p", np.asarray(out[0], float).copy())
            return out
        with mock.patch.object(HPO, "_compute_baseline_power", bp):
            o2.optimize(st2, pr2, ot2, wi2, ra2, so2, race.START)
    o, m, pr, ot, wi, ra, so, st = race.build(tz, dhw, pp, wp, 24, flat)
    done = []

    def rec(objective, candidates, bounds, *a, **kw):
        c = [np.asarray(x, float).copy() for x in candidates]
        if arm != "none" and len(c) > 1 and not done:
            ub = np.array([b[1] for b in bounds])
            if arm == "dup0":
                c.append(c[0].copy())
            else:
                f = {"deep020": om._DEEP_LOW_ENERGY_START_FRACTION,
                     "frac050": 0.50, "frac010": 0.10}[arm]
                e = float(np.sum(base["p"]) * 0.25)
                pm = float(m.params.max_electrical_power)
                c.append(np.minimum(om._price_ranked_start(pr, e * f, pm, 0.25), ub))
        done.append(len(c))
        return REAL_MS(objective, c, bounds, *a, **kw)

    with mock.patch.object(om, "_multi_start_minimize", rec):
        r = o.optimize(st, pr, ot, wi, ra, so, race.START)
    return float(r.objective_value)


def one(args):
    pp, wp, flat = args
    return pp, wp, {arm: shipped(pp, wp, flat, arm) for arm in ARMS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    x = ap.parse_args()
    cells = [(pp, wp, x.flat) for pp, wp in CELLS]
    t0p, t0t = time.process_time(), time.thread_time()
    if x.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(x.jobs) as pool:
            rows = pool.map(one, cells)
    else:
        rows = [one(c) for c in cells]
    worst = {a: 0.0 for a in ARMS[1:]}
    for pp, wp, v in rows:
        base = v["none"]
        s = " ".join(f"{a}={100*(base-v[a])/abs(base):+.4f}%" for a in ARMS[1:])
        print(f"CELL two|dhw|{pp}|{wp}{'|FLAT' if x.flat else ''}: obj {base:.6f} {s}")
        for a in ARMS[1:]:
            worst[a] = max(worst[a], 100 * (base - v[a]) / abs(base))
    for a in ARMS[1:]:
        print(f"RESULT drop_rel_max_{a}={worst[a]:.4f} %")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
