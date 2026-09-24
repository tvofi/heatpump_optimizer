"""D9 round 8 seat s1 -- full solves per optimize() by path, over the stress sweep.

Metric: entries into optimizer._multi_start_minimize per HeatPumpOptimizer.optimize call,
classified by the production caller on the stack at entry: "coopt" when
HeatPumpOptimizer._co_optimize is on the stack (the DHW re-plan's second space solve),
"throttle" for _repair_throttled_buffer_caps, otherwise "optimize:L<line>" -- the line in
HeatPumpOptimizer.optimize that called _solve (first solve, safety-release re-solve, hold
candidate). For the co-opt path, whether _co_optimize adopted the second solve (it returns
the replanned DHW array object instead of the one it was given). njev of every L-BFGS-B run
is attributed to the same path, so the co-opt path's share of the sweep's gradient work is
printed, with its adopted/discarded split.
Count key: _multi_start_minimize entries and scipy njev delivered through
optimizer._scoped_minimize; adoption keyed on the object _co_optimize returns.
Leave-one-out: per-scenario discarded-co-opt njev share; min, max, mean with the highest dropped.
Null control (--flat): prices flattened to their mean.
Perturbation (--no-coopt): HeatPumpOptimizer._co_optimize returns its inputs unrun ->
coopt entries to_zero (the discarded share is what an adoption-predicting guard could save).
Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D9/s1_solves.py [--flat] [--no-coopt]
Expected (baseline cdf82da): counts exact on this box's BLAS.
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import sys
import time
from collections import Counter

sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import stress  # noqa: E402

O = stress.optimizer_module
H = stress.HeatPumpOptimizer


def classify() -> str:
    f = sys._getframe(2)
    line = None
    while f is not None:
        n = f.f_code.co_name
        if n == "_co_optimize":
            return "coopt"
        if n == "_repair_throttled_buffer_caps":
            return "throttle"
        if n == "optimize" and f.f_code.co_filename.endswith("optimizer.py"):
            line = f.f_lineno
            break
        f = f.f_back
    return f"optimize:L{line}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--no-coopt", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    msm0, sc0, co0, pr0 = O._multi_start_minimize, O._scoped_minimize, H._co_optimize, stress.prices
    st = {"path": None, "coopt_pending": []}
    entries = Counter()
    njev = Counter()

    def msm(*a, **k):
        p = classify()
        entries[p] += 1
        prev, st["path"] = st["path"], p
        try:
            return msm0(*a, **k)
        finally:
            st["path"] = prev

    def sc(*a, **k):
        r = sc0(*a, **k)
        njev[st["path"] or "other"] += int(r.njev)
        if st["path"] == "coopt":
            st["coopt_pending"].append(int(r.njev))
        return r

    coopt = Counter()

    def co(self, h, **k):
        if args.no_coopt:
            return k["space_power"], k["dhw_power"], k["status"]
        st["coopt_pending"] = []
        out = co0(self, h, **k)
        ran = bool(st["coopt_pending"])
        adopted = out[1] is not k["dhw_power"]
        if ran:
            key = "adopted" if adopted else "discarded"
            coopt[key] += 1
            coopt["njev_" + key] += sum(st["coopt_pending"])
        return out

    def flat_prices(*a, **k):
        p = np.asarray(pr0(*a, **k), dtype=float)
        return np.full_like(p, float(np.mean(p)))

    O._multi_start_minimize = msm
    O._scoped_minimize = sc
    stress.SolverWork._wrapped = sc
    H._co_optimize = co
    if args.flat:
        stress.prices = flat_prices
    cpu0, th0 = time.process_time(), time.thread_time()
    per = []
    n_opt = 0
    try:
        combos = stress.sweep_combinations()
        if args.limit:
            combos = combos[: args.limit]
        for spec in combos:
            spec = {k: v for k, v in spec.items() if k != "label"}
            before_n = sum(njev.values())
            before_d = coopt["njev_discarded"]
            stress.build_case(**spec)
            n_opt += 1
            allj = sum(njev.values()) - before_n
            per.append((coopt["njev_discarded"] - before_d) / max(allj, 1))
    finally:
        O._multi_start_minimize, O._scoped_minimize, H._co_optimize = msm0, sc0, co0
        stress.SolverWork._wrapped = sc0
        stress.prices = pr0
    tag = ("flat" if args.flat else "real") + (".nocoopt" if args.no_coopt else "")
    tot = sum(njev.values())
    print(f"RESULT {tag}.optimize_calls={n_opt} count")
    print(f"RESULT {tag}.msm_entries_total={sum(entries.values())} count")
    print(f"RESULT {tag}.msm_entries_per_optimize={sum(entries.values()) / max(n_opt, 1):.3f} ratio")
    for p, c in sorted(entries.items()):
        print(f"RESULT {tag}.msm_entries[{p}]={c} count")
        print(f"RESULT {tag}.njev[{p}]={njev[p]} count")
    print(f"RESULT {tag}.coopt_resolves_adopted={coopt['adopted']} count")
    print(f"RESULT {tag}.coopt_resolves_discarded={coopt['discarded']} count")
    print(f"RESULT {tag}.njev_total={tot} count")
    print(f"RESULT {tag}.coopt_discarded_njev_share={coopt['njev_discarded'] / max(tot, 1):.4f} ratio")
    print(f"RESULT {tag}.coopt_adopted_njev_share={coopt['njev_adopted'] / max(tot, 1):.4f} ratio")
    per_a = np.array(per)
    if per_a.size >= 5:
        w = int(np.argmax(per_a))
        print(f"RESULT {tag}.loo.cells={per_a.size} count")
        print(f"RESULT {tag}.loo.min={per_a.min():.4f} ratio")
        print(f"RESULT {tag}.loo.max={per_a.max():.4f} ratio")
        print(f"RESULT {tag}.loo.cells_nonzero={int((per_a > 0).sum())} count")
        print(f"RESULT {tag}.loo.mean_drop_highest={float(np.mean(np.delete(per_a, w))):.4f} ratio")
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
