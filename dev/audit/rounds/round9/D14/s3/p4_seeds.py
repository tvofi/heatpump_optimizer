#!/usr/bin/env python3
"""P4 detector (D14.M3): the optimizer seed set or stop tolerance does not bracket the optimum.

Metric (one line): per production call of optimizer:_multi_start_minimize (a *seam call*,
labelled by its caller: _optimize_space_only or _solve_space, cold = structural seeds, warm =
the co-optimisation re-solve), gap = (production score - best score the SAME
_multi_start_minimize reaches from a dense seed ladder on the identical objective, bounds, args,
maxiter and batch jac) / |production score|; tgap = the same against production's OWN
candidates re-solved at a tight stop (ftol 1e-12, gtol 1e-9, maxiter 3000: the stop-tolerance
arm; --no-tight skips it); RESULT p4_bracket_misses counts seam calls with
gap > 1e-3 (0.1 % of the objective), p4_tol_misses those with tgap > 1e-3; p4_max_gap_pct /
p4_max_tgap_pct are the largest.

Count key: the objective value the production seam's own returned x scores on the production
objective closure, against the dense ladder's; a fix must lower the shipped score, it cannot
relabel.

Dense ladder: _price_ranked_start at energy fractions LADDER of E_ub = sum(ub)*dt (ub = the
seam's own upper bounds; bang-bang on the raw horizon prices captured from optimize()), clipped
to the seam's bounds, plus ub * {0.1, 0.3, 0.6}.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s3/p4_seeds.py
    [--cells quick|full|<one|two>|<dhw|nodhw>|<profile>]  # quick: 8 cells, full: 24 (default)
    [--perturb deep_dhw]        # in-memory: the with-DHW cold seam also gets the 0.20x deep seed
    [--perturb no_deep]         # in-memory: _DEEP_LOW_ENERGY_START_FRACTION -> 0.35 (seed removed)
    [--ref-fixture]             # clean fixture: production candidates := dense ladder (gap must be 0)
Price null control: each topology is also run once at a flat 1.20 SEK/kWh price; the gap must vanish there
for a price-bracketing miss (reported as RESULT p4_bracket_misses_flat).
Expected: numbers printed by the run, exact to +-1 cell on a different BLAS; perturbations move
p4_bracket_misses in the stated direction.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B8 (4 cores, 15 GB).
Instrumented symbol: optimizer:_multi_start_minimize (wrapped by mock.patch.object; the original
is called for both arms).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect
import json
import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from profiles import prices as price_profile  # noqa: E402

LADDER = (0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.25, 0.30, 0.40, 0.50, 0.65, 0.80)
UNIFORM = (0.1, 0.3, 0.6)
GAP_TOL = 1e-3

_orig = O._multi_start_minimize
_orig_scoped = O._scoped_minimize
TIGHT = dict(ftol=1e-12, gtol=1e-9, maxiter=3000, maxfun=200000)


def _tight_scoped(*a, **k):
    k["options"] = dict(k.get("options", {}), **TIGHT)
    return _orig_scoped(*a, **k)
STATE = {"prices": None, "records": [], "perturb": None, "fixture": False}


def _dense(bounds, dt, prices):
    ub = np.array([hi for _, hi in bounds], dtype=float)
    lb = np.array([lo for lo, _ in bounds], dtype=float)
    e_ub = float(np.sum(ub) * dt)
    p_max = float(np.max(ub)) if ub.size else 0.0
    out = []
    for f in LADDER:
        out.append(np.clip(O._price_ranked_start(prices, f * e_ub, p_max, dt), lb, ub))
    for u in UNIFORM:
        out.append(np.clip(ub * u, lb, ub))
    return out


def _caller():
    for fr in inspect.stack()[2:8]:
        if fr.function in ("_optimize_space_only", "_solve_space"):
            return fr.function
    return "other"


def wrapped(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    seam = _caller()
    kind = "cold" if len(candidates) > 1 else "warm"
    dt = STATE["dt"]
    prices = STATE["prices"][: len(bounds)]
    cands = list(candidates)
    if STATE["perturb"] == "deep_dhw" and seam == "_solve_space" and kind == "cold":
        ub = np.array([hi for _, hi in bounds])
        energy = float(np.sum(cands[-1]) * dt) / O._LOW_ENERGY_START_FRACTION
        cands.append(np.minimum(O._price_ranked_start(
            prices, energy * O._DEEP_LOW_ENERGY_START_FRACTION, float(np.max(ub)), dt), ub))
    dense = _dense(bounds, dt, prices)
    if STATE["fixture"]:
        cands = list(dense)
    res = _orig(objective, cands, bounds, args=args, maxiter=maxiter,
                batch_objective=batch_objective, fd_eps=fd_eps)
    prod = float(objective(res.x, *args))
    ref = _orig(objective, dense, bounds, args=args, maxiter=maxiter,
                batch_objective=batch_objective, fd_eps=fd_eps)
    dscore = float(objective(ref.x, *args))
    gap = (prod - dscore) / max(abs(prod), 1e-9)
    tscore = float("nan")
    if STATE["tight"]:
        with mock.patch.object(O, "_scoped_minimize", _tight_scoped):
            tres = _orig(objective, cands, bounds, args=args, maxiter=3000,
                         batch_objective=batch_objective, fd_eps=fd_eps)
        tscore = float(objective(tres.x, *args))
    tgap = (prod - tscore) / max(abs(prod), 1e-9)
    e_prod = float(np.sum(res.x) * dt)
    e_ref = float(np.sum(ref.x) * dt)
    STATE["records"].append({"seam": seam, "kind": kind, "n_cand": len(cands), "prod": prod,
                             "dense": dscore, "gap": gap, "tight": tscore, "tgap": tgap, "e_prod": e_prod, "e_dense": e_ref})
    return res


def cells(which):
    prices_ = ["winter_typical", "winter_extreme", "shoulder", "winter_moderate", "summer_negative", "winter_narrow"]
    out = []
    for two in (False, True):
        for dhw in (False, True):
            for pp in prices_:
                out.append(dict(two_zone=two, dhw=dhw, price_profile=pp, weather_profile="winter_cold"))
    if which.count("|") == 2:  # one named cell, e.g. two|nodhw|winter_typical
        t, d, pp = which.split("|")
        return [c for c in out if c["two_zone"] == (t == "two") and c["dhw"] == (d == "dhw")
                and c["price_profile"] == pp]
    if which == "quick":
        out = [c for c in out if c["price_profile"] in ("winter_typical", "winter_extreme")]
    return out


def run_cell(spec, flat):
    built = golden.make(**spec)
    if flat:
        built["prices"] = np.full_like(built["prices"], 1.20)
    opt = built["optimizer"]
    STATE["prices"] = np.asarray(built["prices"], dtype=float)
    STATE["dt"] = opt.config.time_step_minutes / 60.0
    STATE["records"] = []
    opt.optimize(built["state"], built["prices"], built["outdoor"], built["wind"],
                 built["rain"], built["solar"], golden.START)
    return list(STATE["records"])


def main():
    a = sys.argv[1:]
    which = a[a.index("--cells") + 1] if "--cells" in a else "full"
    STATE["perturb"] = a[a.index("--perturb") + 1] if "--perturb" in a else None
    STATE["fixture"] = "--ref-fixture" in a
    STATE["tight"] = "--no-tight" not in a
    t0 = time.process_time(); tt0 = time.thread_time(); w0 = time.time()
    patches = [mock.patch.object(O, "_multi_start_minimize", wrapped)]
    if STATE["perturb"] == "no_deep":
        patches.append(mock.patch.object(O, "_DEEP_LOW_ENERGY_START_FRACTION", 0.35))
    for p in patches:
        p.start()
    rows = []
    try:
        seen_flat = set()
        for spec in cells(which):
            topo = (spec["two_zone"], spec["dhw"])
            arms = [False] if topo in seen_flat else [False, True]
            seen_flat.add(topo)
            for flat in arms:
                for rec in run_cell(spec, flat):
                    rec.update(cell=f"{'two' if spec['two_zone'] else 'one'}|{'dhw' if spec['dhw'] else 'nodhw'}|{spec['price_profile']}", flat=flat)
                    rows.append(rec)
                    print(f"CELL {rec['cell']:34s} flat={int(flat)} {rec['seam']:22s} {rec['kind']} n={rec['n_cand']} "
                          f"prod={rec['prod']:.6f} dense={rec['dense']:.6f} gap={100*rec['gap']:.4f}% "
                          f"tight={rec['tight']:.6f} tgap={100*rec['tgap']:.4f}% "
                          f"E={rec['e_prod']:.2f}/{rec['e_dense']:.2f}", flush=True)
    finally:
        for p in patches:
            p.stop()
    priced = [r for r in rows if not r["flat"]]
    flat = [r for r in rows if r["flat"]]
    miss = [r for r in priced if r["gap"] > GAP_TOL]
    missf = [r for r in flat if r["gap"] > GAP_TOL]
    print(f"RESULT p4_seam_calls={len(priced)} count")
    print(f"RESULT p4_bracket_misses={len(miss)} count")
    print(f"RESULT p4_bracket_misses_flat={len(missf)} count")
    tmiss = [r for r in priced if r["tgap"] > GAP_TOL]
    tmissf = [r for r in flat if r["tgap"] > GAP_TOL]
    print(f"RESULT p4_tol_misses={len(tmiss)} count")
    print(f"RESULT p4_tol_misses_flat={len(tmissf)} count")
    print(f"RESULT p4_max_tgap_pct={100*max((r['tgap'] for r in priced), default=0):.4f} %")
    print(f"RESULT p4_max_tgap_flat_pct={100*max((r['tgap'] for r in flat), default=0):.4f} %")
    print(f"RESULT p4_max_gap_pct={100*max((r['gap'] for r in priced), default=0):.4f} %")
    print(f"RESULT p4_max_gap_flat_pct={100*max((r['gap'] for r in flat), default=0):.4f} %")
    for seam in ("_optimize_space_only", "_solve_space"):
        for kind in ("cold", "warm"):
            sub = [r for r in priced if r["seam"] == seam and r["kind"] == kind]
            print(f"RESULT p4_misses_{seam.strip('_')}_{kind}={sum(r['gap'] > GAP_TOL for r in sub)}/{len(sub)} count")
    # leave-one-out over cells (max gap per cell)
    per_cell = {}
    for r in priced:
        per_cell[r["cell"]] = max(per_cell.get(r["cell"], -1), r["gap"])
    vals = sorted(per_cell.values())
    if len(vals) >= 5:
        print(f"RESULT p4_cells={len(vals)} count")
        print(f"RESULT p4_cell_gap_min_pct={100*vals[0]:.4f} %")
        print(f"RESULT p4_cell_gap_max_pct={100*vals[-1]:.4f} %")
        print(f"RESULT p4_cell_gap_mean_drop_best_pct={100*np.mean(vals[:-1]):.4f} %")
        print(f"RESULT p4_cells_missing={sum(v > GAP_TOL for v in vals)} count")
        print(f"RESULT p4_cells_missing_drop_best={sum(v > GAP_TOL for v in vals[:-1])} count")
    out = os.environ.get("P4_JSON")
    if out:
        with open(out, "w") as fh:
            json.dump(rows, fh, indent=1)
    pc = time.process_time() - t0; tc = time.thread_time() - tt0
    print(f"RESULT wall_s={time.time()-w0:.1f} s provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
