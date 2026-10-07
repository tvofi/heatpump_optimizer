"""D9 round 8 verifier v1 -- kernel work spent inside per-candidate polishes whose result is not used.

Metric (v1, one line): simulation-kernel step-equivalents (stress.SolverWork's convention:
  rows x steps per ThermalModel.simulate_trajectory_batch, 1 per simulate_step and per
  simulate_dhw_step) executed while optimizer._lbfgsb_restart is on the stack and that call
  returned an object other than the scipy result its own minimize() produced (i.e. the polish
  was dropped by the keep rule), divided by all kernel step-equivalents of the optimize() call,
  pooled over the 51 stress.sweep_combinations() solves.
Secondary: the same numerator widened to polishes whose result did not ship (dropped by the
  keep rule, OR adopted but beaten by another candidate in the cross-candidate minimum), and
  polish runs that ended ABNORMAL at nit 0, read from scipy's own OptimizeResult.
Hook point differs from the finder's on purpose: scipy.optimize.minimize as bound in
  optimizer's namespace (not _scoped_minimize), and the kernel (not njev).
Perturbation: --maxls N passes options maxls=N to the polish's minimize only -> numerator DOWN.
  --flat: every price series replaced by its mean (a property of the restart, so it persists).
  --no-polish: _lbfgsb_restart returns its input -> numerator 0; also prints the shipped
  objective per scenario so the D0 side of dropping the polish can be read.
Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D9/v1_polish_kernel.py [--flat|--maxls 5|--no-polish]
Expected: counts exact on one BLAS build; ratio +-2 % relative. Baseline cdf82daa; 4-vCPU shared container.
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import json
import sys
import time

sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import stress  # noqa: E402

O = stress.optimizer_module
SW = stress.SolverWork


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--maxls", type=int, default=0)
    ap.add_argument("--no-polish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dump", default="")
    args = ap.parse_args()

    st = {"polish_depth": 0, "steps": 0, "polish_rec": None}
    orig = dict(minimize=O.minimize, restart=O._lbfgsb_restart, msm=O._multi_start_minimize,
                batch=SW._batch_wrapped, step=SW._step_wrapped, dhw=SW._dhw_step_wrapped,
                prices=stress.prices)

    def k_batch(*a, **k):
        m = a[2] if len(a) > 2 else k["power_matrix"]
        st["steps"] += int(m.shape[0] * m.shape[1])
        return orig["batch"](*a, **k)

    def k_step(*a, **k):
        st["steps"] += 1
        return orig["step"](*a, **k)

    def k_dhw(*a, **k):
        st["steps"] += 1
        return orig["dhw"](*a, **k)

    def mini(*a, **k):
        rec = st["polish_rec"]
        if rec is not None and args.maxls:
            k["options"] = {**k.get("options", {}), "maxls": args.maxls}
        r = orig["minimize"](*a, **k)
        if rec is not None:
            rec["res"] = r
            rec["nit"], rec["status"], rec["njev"] = int(r.nit), int(r.status), int(r.njev)
        return r

    msm_log = []   # per _multi_start_minimize call: list of polish records

    def restart(best, *a, **k):
        if args.no_polish:
            return best
        rec = {"s0": st["steps"]}
        st["polish_rec"] = rec
        try:
            out = orig["restart"](best, *a, **k)
        finally:
            st["polish_rec"] = None
        rec["steps"] = st["steps"] - rec["s0"]
        rec["dropped"] = out is not rec.get("res")
        rec["out"] = out
        if msm_log:
            msm_log[-1]["polishes"].append(rec)
        return out

    def msm(*a, **k):
        msm_log.append({"polishes": []})
        best = orig["msm"](*a, **k)
        msm_log[-1]["best"] = best
        return best

    def flat_prices(*a, **k):
        p = np.asarray(orig["prices"](*a, **k), dtype=float)
        return np.full_like(p, float(np.mean(p)))

    O.minimize = mini
    O._lbfgsb_restart = restart
    O._multi_start_minimize = msm
    SW._batch_wrapped, SW._step_wrapped, SW._dhw_step_wrapped = k_batch, k_step, k_dhw
    if args.flat:
        stress.prices = flat_prices
    cpu0, th0 = time.process_time(), time.thread_time()
    tot = dict(all=0, dropped=0, unshipped=0, polishes=0, n_dropped=0, n_unshipped=0,
               abn0=0, abn0_steps=0)
    per, costs = [], {}
    try:
        combos = stress.sweep_combinations()
        if args.limit:
            combos = combos[: args.limit]
        for spec in combos:
            label = spec.get("label", str(spec))
            spec = {k2: v for k2, v in spec.items() if k2 != "label"}
            st["steps"] = 0
            msm_log.clear()
            case = stress.build_case(**spec)
            all_steps = st["steps"]
            d = u = 0
            for call in msm_log:
                for p in call["polishes"]:
                    tot["polishes"] += 1
                    if p["dropped"]:
                        d += p["steps"]
                        tot["n_dropped"] += 1
                    if p["dropped"] or p["out"] is not call.get("best"):
                        u += p["steps"]
                        tot["n_unshipped"] += 1
                    if p.get("nit") == 0 and p.get("status") == 2:
                        tot["abn0"] += 1
                        tot["abn0_steps"] += p["steps"]
            tot["all"] += all_steps
            tot["dropped"] += d
            tot["unshipped"] += u
            per.append(d / max(all_steps, 1))
            r = case["result"]
            costs[label] = [float(r.predicted_cost),
                            [float(getattr(c.get("best"), "fun", float("nan"))) for c in msm_log]]
    finally:
        O.minimize, O._lbfgsb_restart, O._multi_start_minimize = (
            orig["minimize"], orig["restart"], orig["msm"])
        SW._batch_wrapped, SW._step_wrapped, SW._dhw_step_wrapped = (
            orig["batch"], orig["step"], orig["dhw"])
        stress.prices = orig["prices"]
    tag = ("flat" if args.flat else "real") + (f".maxls{args.maxls}" if args.maxls else "") + \
        (".nopolish" if args.no_polish else "")
    pa = np.array(per)
    print(f"RESULT {tag}.scenarios={len(per)} count")
    print(f"RESULT {tag}.kernel_steps_all={tot['all']} step-equivalents")
    print(f"RESULT {tag}.kernel_steps_dropped_polish={tot['dropped']} step-equivalents")
    print(f"RESULT {tag}.kernel_steps_unshipped_polish={tot['unshipped']} step-equivalents")
    print(f"RESULT {tag}.polishes={tot['polishes']} count")
    print(f"RESULT {tag}.polishes_dropped={tot['n_dropped']} count")
    print(f"RESULT {tag}.polishes_unshipped={tot['n_unshipped']} count")
    print(f"RESULT {tag}.polishes_abnormal_nit0={tot['abn0']} count")
    print(f"RESULT {tag}.kernel_steps_abnormal_nit0={tot['abn0_steps']} step-equivalents")
    print(f"RESULT {tag}.dropped_polish_kernel_share={tot['dropped'] / max(tot['all'], 1):.4f} ratio")
    print(f"RESULT {tag}.unshipped_polish_kernel_share={tot['unshipped'] / max(tot['all'], 1):.4f} ratio")
    print(f"RESULT {tag}.abn0_kernel_share={tot['abn0_steps'] / max(tot['all'], 1):.4f} ratio")
    if pa.size:
        srt = np.sort(pa)
        print(f"RESULT {tag}.per_scenario.min={srt[0]:.4f} max={srt[-1]:.4f} median={float(np.median(pa)):.4f} ratio")
        print(f"RESULT {tag}.scenarios_with_zero_dropped={int((pa == 0).sum())} count")
    if args.dump:
        with open(args.dump, "w") as fh:
            json.dump({"costs": costs, "per": per, "tot": tot}, fh, indent=1)
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
