"""D9 round 8 seat s1 -- gradient evaluations the per-candidate polish spends and then discards.

Metric: over the 51 stress.sweep_combinations() solves, gradient evaluations (res.njev of every
L-BFGS-B run through optimizer._scoped_minimize) split by run kind -- "start" (a multi-start
candidate) or "polish" (inside optimizer._lbfgsb_restart) -- and, for polishes, by outcome:
adopted (_lbfgsb_restart returned the polished result, i.e. not the object it was given) or
discarded (returned its input). discarded_polish_share = discarded-polish njev / all njev.
Also: polishes that ended ABNORMAL at nit == 0 (line search failed on the first step).
Each gradient is one simulate_trajectory_batch of n rows (s1_gradient.py), so njev is the
solve's kernel work in n-row units.
Count key: njev as delivered by scipy through the production seam, and the identity of the
object _lbfgsb_restart returns.
Leave-one-out: per-scenario discarded share; min, max, and the pooled share with the single
highest-share scenario dropped.
Null control (--flat): the same sweep with every price series replaced by its mean (flat
profile); the discarded-polish share is a property of the restart, not of price structure,
so it must NOT vanish at flat prices.
Perturbation (--maxls N): pass options maxls=N to the polish's L-BFGS-B only (production
passes scipy's default 20); discarded njev must go DOWN, adopted polishes unchanged in count
if the line-search cap is not binding for them. (--skip-polish: _lbfgsb_restart returns its
input unrun -> discarded share to_zero; the upper bound of what the phenomenon costs.)
Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D9/s1_polish.py [--flat] [--maxls 5]
Expected (baseline cdf82da): counts exact on this box's BLAS (iterate paths may drift by
a few njev across BLAS builds; +-2 % on the share).
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import sys
import time

sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import stress  # noqa: E402

O = stress.optimizer_module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--maxls", type=int, default=0)
    ap.add_argument("--skip-polish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    sc0, rs0, pr0 = O._scoped_minimize, O._lbfgsb_restart, stress.prices
    ctx = {"polish": False, "runs": []}

    def sc(*a, **k):
        if ctx["polish"] and args.maxls:
            k["options"] = {**k.get("options", {}), "maxls": args.maxls}
        t0 = time.thread_time()
        r = sc0(*a, **k)
        ctx["runs"].append({"kind": "polish" if ctx["polish"] else "start",
                            "njev": int(r.njev), "nit": int(r.nit), "status": int(r.status),
                            "cpu": time.thread_time() - t0})
        return r

    def rs(best, *a, **k):
        if args.skip_polish:
            return best
        ctx["polish"] = True
        n0 = len(ctx["runs"])
        try:
            out = rs0(best, *a, **k)
        finally:
            ctx["polish"] = False
        for run in ctx["runs"][n0:]:
            run["adopted"] = out is not best
        return out

    def flat_prices(*a, **k):
        p = np.asarray(pr0(*a, **k), dtype=float)
        return np.full_like(p, float(np.mean(p)))

    O._scoped_minimize = sc
    stress.SolverWork._wrapped = sc
    O._lbfgsb_restart = rs
    if args.flat:
        stress.prices = flat_prices
    cpu0, th0 = time.process_time(), time.thread_time()
    per = []
    tot = {"start": 0, "adopted": 0, "discarded": 0, "abn0": 0, "abn0_njev": 0,
           "polishes": 0, "polish_discarded_n": 0, "cpu_all": 0.0, "cpu_discarded": 0.0}
    try:
        combos = stress.sweep_combinations()
        if args.limit:
            combos = combos[: args.limit]
        for spec in combos:
            spec = {k: v for k, v in spec.items() if k != "label"}
            ctx["runs"] = []
            stress.build_case(**spec)
            s = {"start": 0, "adopted": 0, "discarded": 0}
            for r in ctx["runs"]:
                tot["cpu_all"] += r["cpu"]
                if r["kind"] == "start":
                    s["start"] += r["njev"]
                    continue
                tot["polishes"] += 1
                key = "adopted" if r.get("adopted") else "discarded"
                s[key] += r["njev"]
                if key == "discarded":
                    tot["polish_discarded_n"] += 1
                    tot["cpu_discarded"] += r["cpu"]
                if r["nit"] == 0 and r["status"] == 2:
                    tot["abn0"] += 1
                    tot["abn0_njev"] += r["njev"]
            for k2 in ("start", "adopted", "discarded"):
                tot[k2] += s[k2]
            allj = s["start"] + s["adopted"] + s["discarded"]
            per.append(s["discarded"] / max(allj, 1))
    finally:
        O._scoped_minimize, O._lbfgsb_restart = sc0, rs0
        stress.SolverWork._wrapped = sc0
        stress.prices = pr0
    allj = tot["start"] + tot["adopted"] + tot["discarded"]
    tag = ("flat" if args.flat else "real") + (f".maxls{args.maxls}" if args.maxls else "") + \
        (".skip" if args.skip_polish else "")
    per_a = np.array(per)
    worst = int(np.argmax(per_a)) if per_a.size else 0
    print(f"RESULT {tag}.scenarios={len(per)} count")
    print(f"RESULT {tag}.njev_total={allj} count")
    print(f"RESULT {tag}.njev_start={tot['start']} count")
    print(f"RESULT {tag}.njev_polish_adopted={tot['adopted']} count")
    print(f"RESULT {tag}.njev_polish_discarded={tot['discarded']} count")
    print(f"RESULT {tag}.polishes={tot['polishes']} count")
    print(f"RESULT {tag}.polishes_discarded={tot['polish_discarded_n']} count")
    print(f"RESULT {tag}.polishes_abnormal_nit0={tot['abn0']} count")
    print(f"RESULT {tag}.njev_abnormal_nit0={tot['abn0_njev']} count")
    print(f"RESULT {tag}.discarded_polish_share={tot['discarded'] / max(allj, 1):.4f} ratio")
    print(f"RESULT {tag}.polish_share={(tot['adopted'] + tot['discarded']) / max(allj, 1):.4f} ratio")
    if per_a.size >= 5:
        # leave-one-out: drop the single scenario with the highest discarded share
        print(f"RESULT {tag}.loo.cells={per_a.size} count")
        print(f"RESULT {tag}.loo.min={per_a.min():.4f} ratio")
        print(f"RESULT {tag}.loo.max={per_a.max():.4f} ratio")
        print(f"RESULT {tag}.loo.median={float(np.median(per_a)):.4f} ratio")
        print(f"RESULT {tag}.loo.mean_drop_highest={float(np.mean(np.delete(per_a, worst))):.4f} ratio")
    print(f"RESULT {tag}.discarded_polish_cpu_share={tot['cpu_discarded'] / max(tot['cpu_all'], 1e-9):.4f} ratio (provisional)")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln.split()[1] for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
