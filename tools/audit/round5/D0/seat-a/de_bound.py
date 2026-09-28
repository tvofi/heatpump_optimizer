#!/usr/bin/env python3
"""D0-a outer bound: differential_evolution on the recorded space objective.

METRIC (one line): de_gap_pct = 100*(J_ship - J_DE)/|J_ship| where J_ship is
the production objective at the shipped plan (the value the seam
``optimizer._multi_start_minimize`` delivered) and J_DE is the best objective
``scipy.optimize.differential_evolution`` reaches on the SAME recorded
objective/bounds/args within a fixed evaluation budget (counted, so the
number is contention-immune), reported only when the DE winner's comfort
violation (degree-steps vs the per-step floor/ceiling) is no worse than the
shipped plan's.

COMMAND (from the tree root):
  PYTHONPATH=tests/hastub python3 \
      tools/audit/round5/D0/seat-a/de_bound.py [--maxiter 60] [--popsize 12]

EXPECTED at baseline 1cc89e0 (exact): every de_gap_pct is ≤ 0 (DE does not
undercut production at this budget); parity-passing winter cells land 6-7 %
above production, low-load cells fail comfort parity. See de_bound2.log.

Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0; 8-core Apple M1.
Root rule: resolves everything from the tree it is run in (cwd), per
tools/audit/README.md.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import json
import argparse
from datetime import datetime
from unittest import mock

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
sys.path.insert(0, os.path.join(os.getcwd(),
                                "tools/audit/round5/D0/seat-a"))

import numpy as np  # noqa: E402
from scipy.optimize import differential_evolution  # noqa: E402
from profiles import prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

import race  # noqa: E402  (seat harness; builders reused)

TMP = os.environ.get("HPO_D0A_TMP", "/tmp/audit-5/tmp/d0a")


def de_cell(cell, maxiter, popsize):
    tz, dhw, pp, wp, h = (cell["tz"], cell["dhw"], cell["pp"], cell["wp"],
                          cell.get("h", 24.0))
    opt, m, pr, ot, wi, ra, so, st = race.build_cell(
        tz, dhw, pp, wp, h, cell.get("over"), cell.get("param_over"),
        cell.get("state_over"))
    calls = []
    real_ms = opt_mod._multi_start_minimize

    def rec_ms(objective, candidates, bounds, *a, **kw):
        res = real_ms(objective, candidates, bounds, *a, **kw)
        calls.append(dict(objective=objective, args=tuple(kw.get("args") or a),
                          bounds=[tuple(b) for b in bounds],
                          x=np.asarray(res.x, float).copy(),
                          fun=float(res.fun)))
        return res

    with mock.patch.object(opt_mod, "_multi_start_minimize", rec_ms):
        result = opt.optimize(st, pr, ot, wi, ra, so, race.START)
    shipped = np.asarray(result.power_schedule, float)
    two_zone = bool(m.params.two_zone_enabled)
    ship_idx = None
    for i, c in enumerate(calls):
        cb = np.array([b[0] for b in c["bounds"]])
        cu = np.array([b[1] for b in c["bounds"]])
        if (np.allclose(np.clip(c["x"], cb, cu), shipped, atol=1e-9)
                or np.allclose(c["x"], shipped, atol=1e-9)):
            ship_idx = i
            break
    if ship_idx is None:
        return None
    c = calls[ship_idx]
    obj, args, bounds = c["objective"], c["args"], c["bounds"]
    cl = race.closure_of(obj)
    lo, hi = cl["temp_min_bounds"], cl["temp_max_bounds"]
    traj_fn = cl["_space_traj"]
    j_ship = float(obj(c["x"], *args))
    v_ship = race.viol_degsteps(traj_fn(c["x"]), two_zone, lo, hi)

    n_eval = [0]

    def de_obj(x):
        n_eval[0] += 1
        return float(obj(np.asarray(x, float), *args))

    t0 = time.process_time()
    res = differential_evolution(
        de_obj, bounds, maxiter=maxiter, popsize=popsize, tol=1e-10,
        seed=20260920, polish=False, workers=1, init="latinhypercube",
        updating="immediate")
    cpu = time.process_time() - t0
    x = np.asarray(res.x, float)
    j_de = float(obj(x, *args))
    v_de = race.viol_degsteps(traj_fn(x), two_zone, lo, hi)
    return dict(
        cell=cell["id"], j_ship=j_ship, j_de=j_de, v_ship=v_ship, v_de=v_de,
        de_gap_pct=100.0 * (j_ship - j_de) / max(abs(j_ship), 1e-12),
        feasible_no_worse=bool(v_de <= v_ship + 1e-6),
        nfev=int(res.nfev), nit=int(res.nit), n_eval=n_eval[0],
        cpu_de=cpu, cpu_budget_provisional=True,
        message=str(res.message),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxiter", type=int, default=60)
    ap.add_argument("--popsize", type=int, default=12)
    args = ap.parse_args()
    # chosen after the core race: worst non-flat gap cells + a flat null +
    # a short-horizon cell; edit here to point the bound at other cells.
    cells = [
        dict(id="topSEK:tz=1,dhw=0,winter_moderate,winter_cold,h24",
             tz=True, dhw=False, pp="winter_moderate", wp="winter_cold"),
        dict(id="topSEK2:tz=1,dhw=1,winter_moderate,winter_cold,h24",
             tz=True, dhw=True, pp="winter_moderate", wp="winter_cold"),
        dict(id="worstgap:tz=0,dhw=0,summer_negative,shoulder,h24",
             tz=False, dhw=False, pp="summer_negative", wp="shoulder"),
        dict(id="null:tz=1,dhw=1,flat,shoulder,h24",
             tz=True, dhw=True, pp="flat", wp="shoulder"),
        dict(id="short:tz=1,dhw=1,winter_typical,winter_cold,h6",
             tz=True, dhw=True, pp="winter_typical", wp="winter_cold", h=6.0),
    ]
    out = []
    for cell in cells:
        try:
            rec = de_cell(cell, args.maxiter, args.popsize)
        except Exception as err:
            print(f"# cell {cell['id']} raised {err!r}")
            continue
        if rec is None:
            continue
        out.append(rec)
        print(f"  {rec['cell']:55s} J {rec['j_ship']:9.3f} -> DE "
              f"{rec['j_de']:9.3f}  gap {rec['de_gap_pct']:7.3f}%  "
              f"feas_parity={rec['feasible_no_worse']} nfev={rec['nfev']}")
    os.makedirs(TMP, exist_ok=True)
    with open(os.path.join(TMP, "de_bound.json"), "w") as f:
        json.dump(out, f)
    proc = time.process_time()
    thread = time.thread_time()
    print(f"RESULT de_cells={len(out)} count")
    for rec in out:
        print(f"RESULT de_gap_pct[{rec['cell'].split(':')[0]}]="
              f"{rec['de_gap_pct']:.4f} percent "
              f"feasible_no_worse={rec['feasible_no_worse']}")
        print(f"RESULT de_nfev[{rec['cell'].split(':')[0]}]={rec['nfev']} count")
    print(f"RESULT thread_factor={proc / max(thread, 1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
