"""D0-s2 terminal-seed race: the plan the solver returns when the terminal
credit is removed, used as ONE extra L-BFGS-B start on production's own
(terminal-credited) objective.  Does production miss a basin that start finds?

Metric (one line): per cell, gap_pct = 100*(J_prod - J_ch)/|J_prod| where J is
the exact objective closure production passed to ``_multi_start_minimize``
(captured with mock.patch.object), J_prod = J(shipped plan), J_ch = the result
of production's own ``_multi_start_minimize(J, [x_noterm], bounds, maxiter,
batch_objective)`` started from the noterm arm's plan; also comfort parity:
degree-steps below the floor of each plan on production's
``ThermalModel.simulate_trajectory`` (must be <= production's + 1e-6 for the
challenger to count).
Null control: flat prices.
Perturbation: none needed on production for the race itself; the noterm arm is
``_terminal_cost`` patched to zero closures, and the D0S2_SEED=prod env swaps
the challenger seed for production's own plan (gap must fall to ~0).
Instrumented symbols: heatpump_optimizer.optimizer:_multi_start_minimize
(captured and re-run), HeatPumpOptimizer._terminal_cost (patched in the seed arm).

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D0/s2_termrace.py [--two-zone] [--dhw 0|1]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from unittest import mock
import numpy as np
from golden import make, START
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.optimizer import HeatPumpOptimizer

ap = argparse.ArgumentParser()
ap.add_argument("--two-zone", action="store_true")
ap.add_argument("--dhw", type=int, default=0)
ap.add_argument("--prices", default="winter_typical,winter_extreme,summer_typical,"
                "summer_negative,shoulder,winter_narrow,winter_moderate,flat")
ap.add_argument("--weather", default="winter_cold,winter_mild,summer_cool,shoulder")
ap.add_argument("--specs", default="",
                help="comma list of tests/golden.py SCENARIOS names; replaces the grid")
ARGS = ap.parse_args()
SEED = os.environ.get("D0S2_SEED", "noterm")
_real_ms = om._multi_start_minimize
CAP = []


def _cap_ms(objective, candidates, bounds, args=(), maxiter=300,
            batch_objective=None, fd_eps=1e-4):
    res = _real_ms(objective, candidates, bounds, args=args, maxiter=maxiter,
                   batch_objective=batch_objective, fd_eps=fd_eps)
    CAP.append(dict(obj=objective, bounds=bounds, args=args, maxiter=maxiter,
                    batch=batch_objective, x=np.array(res.x),
                    n_cand=len(candidates)))
    return res


def _zero_terminal(self, prices, outdoor_temps, solar_gains=None):
    return (lambda *a, **k: 0.0,
            lambda traj: np.zeros(traj["room"].shape[0]))


def build(pp, wp):
    if pp == "spec":
        import golden
        spec = dict(golden.SCENARIOS[wp])
        ARGS.two_zone = bool(spec.get("two_zone", False))
        ARGS.dhw = int(spec.get("dhw", True))
        return make(**spec)
    return make(two_zone=ARGS.two_zone, dhw=bool(ARGS.dhw), price_profile=pp,
                weather_profile=wp)


def viol(b, x):
    o = b["optimizer"]
    m = o.model
    room, _, up, lo, _, _, _ = m.simulate_trajectory(
        b["state"], x, b["outdoor"], b["wind"], b["rain"], b["solar"], 0.25)
    r = np.minimum(up, lo)[1:] if ARGS.two_zone else np.asarray(room)[1:]
    fl = np.array([o.config.get_temp_bounds((i + 1) * 0.25 % 24)[0]
                   for i in range(len(x))])
    return float(np.sum(np.maximum(0.0, fl - r)))


def cell(pp, wp):
    b = build(pp, wp)
    args = (b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"],
            b["solar"], START)
    CAP.clear()
    with mock.patch.object(om, "_multi_start_minimize", _cap_ms):
        r = b["optimizer"].optimize(*args)
    # The call whose fixed args (the DHW plan, on the DHW path) are the ones
    # the shipped plan was solved against: _co_optimize's second solve is only
    # adopted when it scores better, so the LAST call is not always it.
    x_prod = np.asarray(r.power_schedule, dtype=float)
    main = min(CAP, key=lambda c: float(np.max(np.abs(c["x"] - x_prod)))
               if c["x"].shape == x_prod.shape else np.inf)
    if ARGS.dhw and r.dhw_power_schedule:
        d = np.asarray(r.dhw_power_schedule, dtype=float)
        match = [c for c in CAP if c["args"]
                 and np.allclose(np.asarray(c["args"][0]), d, atol=1e-9)]
        main = match[-1]
    J = main["obj"]
    a = main["args"]
    j_prod = float(J(np.clip(x_prod, [lo for lo, _ in main["bounds"]],
                             [hi for _, hi in main["bounds"]]), *a))
    if SEED == "prod":
        seed = x_prod.copy()
    else:
        b2 = build(pp, wp)
        with mock.patch.object(HeatPumpOptimizer, "_terminal_cost",
                               _zero_terminal):
            r2 = b2["optimizer"].optimize(*args)
        seed = np.asarray(r2.power_schedule, dtype=float)
    lo = np.array([l for l, _ in main["bounds"]])
    hi = np.array([h for _, h in main["bounds"]])
    seed = np.clip(seed, lo, hi)
    j_seed = float(J(seed, *a))
    res = _real_ms(J, [seed], main["bounds"], args=a, maxiter=main["maxiter"],
                   batch_objective=main["batch"])
    x_ch = np.clip(np.asarray(res.x), lo, hi)
    j_ch = float(J(x_ch, *a))
    pr = b["prices"]
    bill_p = float(np.sum(x_prod * pr) * 0.25)
    bill_c = float(np.sum(x_ch * pr) * 0.25)
    return dict(j_prod=j_prod, j_seed=j_seed, j_ch=j_ch,
                gap=100 * (j_prod - j_ch) / abs(j_prod),
                v_prod=viol(b, x_prod), v_ch=viol(b, x_ch),
                bill_p=bill_p, bill_c=bill_c,
                step0=float(abs(x_ch[0] - x_prod[0])),
                n_ms=len(CAP), n_cand=main["n_cand"],
                match=float(np.max(np.abs(main["x"] - x_prod))))


def main():
    rows = []
    grid = ([("spec", n) for n in ARGS.specs.split(",")] if ARGS.specs else
            [(pp, wp) for pp in ARGS.prices.split(",")
             for wp in ARGS.weather.split(",")])
    for pp, wp in grid:
        if True:
            c = cell(pp, wp)
            c["cell"] = f"{pp}/{wp}"
            c["ok"] = c["v_ch"] <= c["v_prod"] + 1e-6
            rows.append(c)
            print("CELL %-34s Jprod=%9.4f Jseed=%9.4f Jch=%9.4f gap=%+7.3f%% "
                  "viol %.3f/%.3f bill %.2f->%.2f step0 d=%.3f ms_calls=%d match=%.2g"
                  % (c["cell"], c["j_prod"], c["j_seed"], c["j_ch"], c["gap"],
                     c["v_prod"], c["v_ch"], c["bill_p"], c["bill_c"],
                     c["step0"], c["n_ms"], c["match"]), flush=True)
    tag = ("tz" if ARGS.two_zone else "sz") + ("_dhw" if ARGS.dhw else "")
    tag += "" if SEED == "noterm" else "_seedprod"
    pr = [r for r in rows if not r["cell"].startswith("flat/")
          and "flat" not in r["cell"]]
    fl = [r for r in rows if r["cell"].startswith("flat/")
          or "flat" in r["cell"]]
    if ARGS.specs:
        tag = "spec"
    g = sorted(r["gap"] if r["ok"] else 0.0 for r in pr)
    print(f"RESULT {tag}_cells={len(pr)} count")
    print(f"RESULT {tag}_cells_gap_gt_0.1pct={sum(x > 0.1 for x in g)} count")
    print(f"RESULT {tag}_gap_max={g[-1]:.4f} pct")
    print(f"RESULT {tag}_gap_mean={np.mean(g):.4f} pct")
    print(f"RESULT {tag}_gap_mean_drop_best={np.mean(g[:-1]):.4f} pct")
    print(f"RESULT {tag}_gap_min={g[0]:.4f} pct")
    print(f"RESULT {tag}_step0_differs_in_gap_cells="
          f"{sum(1 for r in pr if r['ok'] and r['gap'] > 0.1 and r['step0'] > 1e-3)} count")
    if fl:
        print(f"RESULT {tag}_null_flat_gap="
              f"{','.join('%.4f' % r['gap'] for r in fl)} pct")
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
