"""D0-s1 round 9: capture every production multi-start call and race challengers.

Metric (one line): per cell, gap = (shipped objective - best feasible challenger
objective) / |shipped objective|, both scored with the exact captured production
objective (optimizer:_multi_start_minimize's `objective` + `args`), challenger
feasibility (floor/ceiling degree-steps, DHW schedule fixed by args) no worse.

Count key: the objective value production's own captured objective returns for
the plan the call returned (res.x) -- never an input attribute.

Command (from the repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/s1/race.py [--cells tz:dhw:price:weather,...] [--jobs 2]
    [--perturb deep_anchor_dhw] [--horizon 24]
Expected: see REPORT.md per cell table (tolerance: gaps +/-0.05 pp across BLAS builds).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B1 (4 vCPU Linux,
CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1).

Challengers per captured call (cheapest first):
  polish   -- L-BFGS-B from production's returned x, same jac path, ftol 1e-12,
              maxiter 3000, maxfun 1e6
  seeds    -- each production candidate refined ALONE through the real seam
              (which one wins), and each bang-bang anchor at energy fractions
              LADDER of the baseline thermostat energy, refined alone through the
              real seam; the best is then tight-polished (warm start)
Perturbations (in memory, on the DHW path's cold-start seam call only):
  --perturb space_seeds_dhw : append the seeds _optimize_space_only builds and
      _solve_space does not -- the baseline thermostat power, and bang-bang anchors
      at 1.0x / 0.35x (and, two-zone, 0.20x) of the BASELINE energy -- to the
      DHW path's candidates. The DHW-on shipped objective must move down.
  --perturb deep_anchor_dhw : the 0.20x two-zone anchor alone.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, json, time, argparse, tempfile
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from unittest import mock
from profiles import prices as P_prices, weather as P_weather, house
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig

LADDER = (0.0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
PRICES = ("winter_typical", "winter_extreme", "winter_narrow", "winter_moderate")
WEATHERS = ("winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder")
START = datetime(2026, 1, 15)
TMIN, TMAX = 17.0, 23.0
# Feasibility parity tolerance, degree-steps (K x 15-min steps) summed over
# zones: a challenger may not breach the floor/ceiling by more than production
# plus this. 0.01 = one hundredth of a kelvin for one step.
FEAS_TOL = 0.01


def build(tz, dhw, pp, wp, horizon=24, flat=False):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=TMIN, max_temp=TMAX))
    pr = P_prices("flat" if flat else pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    reps = int(np.ceil(horizon / 24.0))
    n = int(horizon * 4)
    pr, ot, wi, ra, so = (np.tile(a, reps)[:n] for a in (pr, ot, wi, ra, so))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st


def make_jac(cap):
    bounds = cap["bounds"]
    if cap["batch"] is None or not om._bounds_supported_by_batch(bounds):
        return None
    obj = cap["objective"]

    def jac(x, *a):
        return om._batch_fd_gradient(cap["batch"], a, x, float(obj(x, *a)),
                                     cap["fd_eps"], bounds)
    return jac


def tight(cap, x0):
    obj, args, bounds = cap["objective"], cap["args"], cap["bounds"]
    r = om._scoped_minimize(obj, np.asarray(x0, float), args=args, jac=make_jac(cap),
                            method="L-BFGS-B", bounds=bounds,
                            options={"maxiter": 3000, "maxfun": 1000000,
                                     "ftol": 1e-12, "gtol": 1e-9, "eps": 1e-4})
    return np.asarray(r.x, float), float(obj(np.asarray(r.x, float), *args)), int(r.nit)


def seam(cap, seeds):
    r = REAL_MS(cap["objective"], [np.asarray(s, float) for s in seeds], cap["bounds"],
                args=cap["args"], maxiter=cap["maxiter"],
                batch_objective=cap["batch"], fd_eps=cap["fd_eps"])
    x = np.asarray(r.x, float)
    return x, float(cap["objective"](x, *cap["args"]))


REAL_MS = om._multi_start_minimize


def feas(m, st, ot, wi, ra, so, space, tz):
    room, slab, up, lo, *_ = m.simulate_trajectory(st, space, ot, wi, ra, so, 0.25)
    zones = [np.asarray(up[1:]), np.asarray(lo[1:])] if tz else [np.asarray(room[1:])]
    fl = sum(float(np.maximum(0, TMIN - z).sum()) for z in zones)
    ce = sum(float(np.maximum(0, z - TMAX).sum()) for z in zones)
    return fl, ce


def run_cell(tz, dhw, pp, wp, horizon=24, flat=False, perturb=None):
    o, m, pr, ot, wi, ra, so, st = build(tz, dhw, pp, wp, horizon, flat)
    caps = []
    base = {}
    real_base = HeatPumpOptimizer._compute_baseline_power

    def base_rec(self, *a, **kw):
        out = real_base(self, *a, **kw)
        base["energy"] = float(np.sum(out[0]) * 0.25)
        return out

    def rec(objective, candidates, bounds, *a, **kw):
        cands = [np.asarray(c, float).copy() for c in candidates]
        if perturb and dhw and len(cands) > 1 and not caps:
            # the DHW path's cold-start call: hand it the seeds the space-only
            # path builds (_optimize_space_only), keyed on the same baseline
            # thermostat energy, clipped to this call's bounds.
            ub = np.array([b[1] for b in bounds])
            bp_prod = base["power_prod"]
            e = float(np.sum(bp_prod) * 0.25)
            pm = float(m.params.max_electrical_power)
            fr = []
            if perturb in ("space_seeds_dhw",):
                cands.append(np.minimum(np.clip(bp_prod, 0.0, pm), ub))
                fr += [1.0, om._LOW_ENERGY_START_FRACTION]
            if perturb in ("space_seeds_dhw", "deep_anchor_dhw") and tz:
                fr += [om._DEEP_LOW_ENERGY_START_FRACTION]
            for f in fr:
                cands.append(np.minimum(om._price_ranked_start(pr, e * f, pm, 0.25), ub))
            candidates = cands
        cap = {"objective": objective, "candidates": cands,
               "bounds": [tuple(float(v) for v in b) for b in bounds],
               "args": tuple(kw.get("args", a[0] if a else ())),
               "maxiter": kw.get("maxiter", 300), "batch": kw.get("batch_objective"),
               "fd_eps": kw.get("fd_eps", 1e-4)}
        kw2 = dict(kw)
        res = REAL_MS(objective, candidates, bounds, *a, **kw2)
        cap["x"] = np.asarray(res.x, float).copy()
        cap["f"] = float(objective(cap["x"], *cap["args"]))
        caps.append(cap)
        return res

    if perturb:
        # pre-pass: production's own baseline thermostat power (it is computed
        # inside optimize with the comfort-target series), from an identical
        # fresh optimizer, so the perturbed seeds use exactly its reference.
        o2, *_rest = build(tz, dhw, pp, wp, horizon, flat)
        st2 = _rest[-1]
        def bp_rec(self, *a, **kw):
            out = real_base(self, *a, **kw)
            base.setdefault("power_prod", np.asarray(out[0], float).copy())
            return out
        with mock.patch.object(HeatPumpOptimizer, "_compute_baseline_power", bp_rec):
            o2.optimize(st2, pr, ot, wi, ra, so, START)
    t0 = time.process_time()
    with mock.patch.object(om, "_multi_start_minimize", rec), \
            mock.patch.object(HeatPumpOptimizer, "_compute_baseline_power", base_rec):
        res = o.optimize(st, pr, ot, wi, ra, so, START)
    t_prod = time.process_time() - t0
    shipped_space = np.asarray(res.power_schedule, float)
    shipped_dhw = np.asarray(getattr(res, "dhw_power_schedule", None) or np.zeros_like(pr), float) \
        if dhw else np.zeros_like(pr)
    pmax = float(m.params.max_electrical_power)
    out = {"cell": f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|h{horizon}"
                   + ("|FLAT" if flat else ""),
           "n_calls": len(caps), "base_energy_kwh": base["energy"],
           "shipped_obj": float(res.objective_value), "calls": []}
    fl0, ce0 = feas(m, st, ot, wi, ra, so, shipped_space, tz)
    out["shipped_floor_viol"], out["shipped_ceil_viol"] = fl0, ce0
    out["shipped_energy_sek"] = float(np.sum(pr * (shipped_space + shipped_dhw)) * 0.25)
    best_overall = (np.inf, None, None)
    for ci, cap in enumerate(caps):
        ub = np.array([b[1] for b in cap["bounds"]])
        rec_c = {"call": ci, "n_cand": len(cap["candidates"]), "f_prod": cap["f"],
                 "maxiter": cap["maxiter"], "jac_batched": make_jac(cap) is not None}
        xp, fp, nitp = tight(cap, cap["x"])
        rec_c["f_polish"], rec_c["polish_nit"] = fp, nitp
        trials = [("polish", xp, fp)]
        per = {}
        for k, c in enumerate(cap["candidates"]):
            x, f = seam(cap, [c])
            per[f"cand{k}"] = f
            trials.append((f"cand{k}", x, f))
        for fr in LADDER:
            s = np.minimum(om._price_ranked_start(pr, base["energy"] * fr, pmax, 0.25), ub)
            x, f = seam(cap, [s])
            per[f"anchor{fr}"] = f
            trials.append((f"anchor{fr}", x, f))
        rec_c["per_seed"] = per
        # feasibility filter, then tight polish of the best feasible trial
        feas_trials = []
        for name, x, f in trials:
            fl, ce = feas(m, st, ot, wi, ra, so, x, tz)
            if fl <= fl0 + FEAS_TOL and ce <= ce0 + FEAS_TOL:
                feas_trials.append((f, name, x))
        feas_trials.sort(key=lambda t: t[0])
        fbest, nbest, xbest = feas_trials[0]
        xw, fw, _ = tight(cap, xbest)
        flw, cew = feas(m, st, ot, wi, ra, so, xw, tz)
        if fw < fbest and flw <= fl0 + FEAS_TOL and cew <= ce0 + FEAS_TOL:
            fbest, nbest, xbest = fw, nbest + "+tight", xw
        rec_c["f_best"], rec_c["best_name"] = fbest, nbest
        rec_c["best_floor_viol"], rec_c["best_ceil_viol"] = feas(m, st, ot, wi, ra, so, xbest, tz)
        rec_c["best_energy_frac"] = float(np.sum(xbest) * 0.25 / base["energy"]) if base["energy"] else 0.0
        rec_c["prod_energy_frac"] = float(np.sum(cap["x"]) * 0.25 / base["energy"]) if base["energy"] else 0.0
        rec_c["step0_prod"], rec_c["step0_best"] = float(cap["x"][0]), float(xbest[0])
        dhwarg = np.asarray(cap["args"][0], float) if cap["args"] else np.zeros_like(pr)
        rec_c["best_energy_sek"] = float(np.sum(pr * (xbest + dhwarg)) * 0.25)
        out["calls"].append(rec_c)
        if fbest < best_overall[0]:
            best_overall = (fbest, ci, nbest)
    f0 = out["shipped_obj"]
    out["best_obj"], out["best_call"], out["best_name"] = best_overall
    out["gap_rel"] = (f0 - best_overall[0]) / abs(f0) if f0 else 0.0
    out["gap_abs"] = f0 - best_overall[0]
    out["prod_cpu_s"] = t_prod
    return out


def shipped_only(tz, dhw, pp, wp, horizon=24, flat=False, perturb=None):
    """Production's shipped plan only (no challengers), optionally perturbed."""
    o, m, pr, ot, wi, ra, so, st = build(tz, dhw, pp, wp, horizon, flat)
    base = {}
    real_base = HeatPumpOptimizer._compute_baseline_power
    ncand = []
    if perturb:
        o2, *_rest = build(tz, dhw, pp, wp, horizon, flat)
        def bp_rec(self, *a, **kw):
            out = real_base(self, *a, **kw)
            base.setdefault("power_prod", np.asarray(out[0], float).copy())
            return out
        with mock.patch.object(HeatPumpOptimizer, "_compute_baseline_power", bp_rec):
            o2.optimize(_rest[-1], pr, ot, wi, ra, so, START)

    def rec(objective, candidates, bounds, *a, **kw):
        cands = [np.asarray(c, float).copy() for c in candidates]
        if perturb and dhw and len(cands) > 1 and not ncand:
            ub = np.array([b[1] for b in bounds])
            bp_prod = base["power_prod"]
            e = float(np.sum(bp_prod) * 0.25)
            pm = float(m.params.max_electrical_power)
            fr = []
            if perturb == "space_seeds_dhw":
                cands.append(np.minimum(np.clip(bp_prod, 0.0, pm), ub))
                fr += [1.0, om._LOW_ENERGY_START_FRACTION]
            if perturb in ("space_seeds_dhw", "deep_anchor_dhw") and tz:
                fr += [om._DEEP_LOW_ENERGY_START_FRACTION]
            for f in fr:
                cands.append(np.minimum(om._price_ranked_start(pr, e * f, pm, 0.25), ub))
        ncand.append(len(cands))
        return REAL_MS(objective, cands, bounds, *a, **kw)

    with mock.patch.object(om, "_multi_start_minimize", rec):
        res = o.optimize(st, pr, ot, wi, ra, so, START)
    sp = np.asarray(res.power_schedule, float)
    dh = np.asarray(res.dhw_power_schedule, float) if dhw and res.dhw_power_schedule \
        else np.zeros_like(pr)
    fl, ce = feas(m, st, ot, wi, ra, so, sp, tz)
    return {"obj": float(res.objective_value), "energy_sek": float(np.sum(pr * (sp + dh)) * 0.25),
            "floor": fl, "ceil": ce, "step0": float(sp[0]), "ncand": ncand,
            "min_dhw_T": float(np.min(res.dhw_temp_trajectory)) if dhw and res.dhw_temp_trajectory else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.cells:
        cells = []
        for c in a.cells.split(","):
            tz, dh, pp, wp = c.split(":")
            cells.append((tz == "two", dh == "dhw", pp, wp))
    else:
        cells = [(tz, dh, pp, wp) for tz in (False, True) for dh in (True, False)
                 for pp in PRICES for wp in WEATHERS]
    t0p, t0t = time.process_time(), time.thread_time()
    args = [(c[0], c[1], c[2], c[3], a.horizon, a.flat, a.perturb) for c in cells]
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool:
            results = pool.starmap(run_cell, args)
    else:
        results = [run_cell(*x) for x in args]
    outp = a.out or os.path.join(tempfile.mkdtemp(prefix="d0s1_"), "race.json")
    with open(outp, "w") as fh:
        json.dump(results, fh, indent=1, default=float)
    for r in results:
        print(f"CELL {r['cell']}: shipped={r['shipped_obj']:.6f} best={r['best_obj']:.6f} "
              f"gap={100*r['gap_rel']:.4f}% abs={r['gap_abs']:.4f} via call{r['best_call']}:{r['best_name']} "
              f"floor={r['shipped_floor_viol']:.4f} E={r['shipped_energy_sek']:.2f}SEK calls={r['n_calls']}")
        for c in r["calls"]:
            print(f"   call{c['call']} n_cand={c['n_cand']} f_prod={c['f_prod']:.6f} polish={c['f_polish']:.6f} "
                  f"best={c['f_best']:.6f} ({c['best_name']}) Efrac prod={c['prod_energy_frac']:.3f} "
                  f"best={c['best_energy_frac']:.3f} step0 {c['step0_prod']:.3f}->{c['step0_best']:.3f} "
                  f"Esek best={c['best_energy_sek']:.2f} floor best={c['best_floor_viol']:.4f}")
    gaps = np.array([r["gap_rel"] for r in results])
    print(f"RESULT cells={len(results)} count")
    print(f"RESULT gap_rel_max={100*gaps.max():.4f} %")
    print(f"RESULT gap_rel_mean={100*gaps.mean():.4f} %")
    print(f"RESULT cells_gap_over_0.1pct={int((gaps > 1e-3).sum())} count")
    if len(gaps) >= 2:
        print(f"RESULT gap_rel_mean_drop_max={100*np.delete(gaps, gaps.argmax()).mean():.4f} %")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")
    print(f"json: {outp}")


if __name__ == "__main__":
    main()
