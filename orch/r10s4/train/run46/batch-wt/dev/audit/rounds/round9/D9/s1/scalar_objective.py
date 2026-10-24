"""D9-s1 H3: share of a solve's CPU spent in the SCALAR objective that
optimizer._multi_start_minimize hands L-BFGS-B, against the batched objective
it already holds, and the per-row cost of the two.

Metric: thread CPU inside the `objective` callable passed to
optimizer._multi_start_minimize (candidate scoring + every fun(x) scipy asks
for + restart score/prior evaluations) / thread CPU of optimize(), per cell;
plus ms per scalar call over ms per batched row (rows of
`batch_objective` calls), ratio.
Count key: the float the objective RETURNS; parity is bitwise between
objective(x) and batch_objective(x[None, :])[0] on every call.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/scalar_objective.py [--via-batch] [--only CELL]
Perturbation: --fused hands L-BFGS-B jac=True with ONE batch per iterate
whose extra row 0 is x itself (f from that row, the gradient from
production _batch_fd_gradient on the other rows), so scipy never asks the
scalar objective for fun(x); the scalar share must go DOWN and the plan sha
must stay identical (row parity is checked bitwise on every fused call).
--via-batch (a one-row batch per scalar call) is a recorded NEGATIVE arm:
the batch kernel's per-call overhead makes it dearer, share goes UP.
Expected at baseline (provisional): share ~0.15-0.25 on two-zone cells,
per-call ratio >10x; mismatches 0 (exact).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import hashlib
import time

import numpy as np

import stress
from heatpump_optimizer import optimizer as opt_mod

CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
    "two_zone_nodhw_winter_mild": dict(season="winter_mild", two_zone=True, dhw=False),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", two_zone=False, dhw=True),
    "single_zone_fuse_3p68": dict(season="winter", two_zone=False, dhw=True, power_cap_kw=3.68),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),  # null control
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--via-batch", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--no-parity", action="store_true")
    ap.add_argument("--fused", action="store_true")
    args = ap.parse_args()
    global VIA_BATCH, NO_PARITY
    VIA_BATCH, NO_PARITY = args.via_batch, args.no_parity
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    orig_msm = opt_mod._multi_start_minimize
    # build_case's stress.SolverWork re-binds optimizer._scoped_minimize to its
    # counter, which calls SolverWork._wrapped at call time: swap THAT.
    orig_sm = stress.SolverWork._wrapped
    fz = {"calls": 0, "mism": 0, "parity_t": 0.0}

    def fused_scoped_minimize(fun, x0, args=(), jac=None, **kw):
        if not callable(jac):
            return orig_sm(fun, x0, args=args, jac=jac, **kw)
        cells = dict(zip(jac.__code__.co_freevars, (c.cell_contents for c in jac.__closure__)))
        bobj, eps, bnds = cells["batch_objective"], cells["fd_eps"], cells["bounds"]

        def fg(x, *a):
            x = np.asarray(x, dtype=float)
            cap = {}

            def capture(mat, *_a):
                cap["m"] = mat.copy()
                return np.zeros(mat.shape[0])
            opt_mod._batch_fd_gradient(capture, a, x, 0.0, eps, bnds)
            out = bobj(np.vstack([x[None, :], cap["m"]]), *a)
            f0 = float(out[0])
            g = opt_mod._batch_fd_gradient(lambda m, *_a: out[1:], a, x, f0, eps, bnds)
            fz["calls"] += 1
            if not NO_PARITY:
                p0 = time.thread_time()
                if np.float64(f0).view(np.int64) != np.float64(float(fun(x, *a))).view(np.int64):
                    fz["mism"] += 1
                fz["parity_t"] += time.thread_time() - p0
            return f0, g
        return orig_sm(fg, x0, args=args, jac=True, **kw)
    shares = {}
    worst_tf = 1.0
    for cell, spec in CELLS.items():
        if args.only and cell != args.only:
            continue
        st = {"obj_t": 0.0, "obj_n": 0, "b_t": 0.0, "b_rows": 0, "mism": 0, "parity_t": 0.0}

        def msm(objective, candidates, bounds, args=(), maxiter=300,
                batch_objective=None, fd_eps=1e-4, _st=st):
            def batch_wrapped(mat, *a):
                t0 = time.thread_time()
                out = batch_objective(mat, *a)
                _st["b_t"] += time.thread_time() - t0
                _st["b_rows"] += int(np.asarray(mat).shape[0])
                return out

            def obj(x, *a):
                t0 = time.thread_time()
                if VIA_BATCH and batch_objective is not None:
                    v = float(batch_objective(np.asarray(x, dtype=float)[None, :], *a)[0])
                else:
                    v = float(objective(x, *a))
                _st["obj_t"] += time.thread_time() - t0
                _st["obj_n"] += 1
                if batch_objective is not None and not NO_PARITY:
                    p0 = time.thread_time()
                    other = (float(objective(x, *a)) if VIA_BATCH else
                             float(batch_objective(np.asarray(x, dtype=float)[None, :], *a)[0]))
                    if np.float64(v).view(np.int64) != np.float64(other).view(np.int64):
                        _st["mism"] += 1
                    _st["parity_t"] += time.thread_time() - p0
                return v
            return orig_msm(obj, candidates, bounds, args, maxiter,
                            batch_wrapped if batch_objective is not None else None, fd_eps)

        opt_mod._multi_start_minimize = msm
        fz.update(calls=0, mism=0, parity_t=0.0)
        if args.fused:
            stress.SolverWork._wrapped = fused_scoped_minimize
        try:
            with C.Clock() as clk:
                run = stress.build_case(**spec)
        finally:
            opt_mod._multi_start_minimize = orig_msm
            stress.SolverWork._wrapped = orig_sm
        worst_tf = max(worst_tf, clk.thread_factor)
        solve = run["solve_thread_ms"] / 1000.0 - st["parity_t"] - fz["parity_t"]
        tag = cell + ("_viabatch" if args.via_batch else "") + ("_fused" if args.fused else "")
        if args.fused:
            C.result(f"{tag}.fused_calls", fz["calls"], "count")
            C.result(f"{tag}.fused_row0_mismatches", fz["mism"], "calls (exact)")
        plan = np.asarray(run["result"].power_schedule, dtype=float)
        share = st["obj_t"] / solve
        shares[cell] = share
        C.result(f"{tag}.scalar_objective_calls", st["obj_n"], "count")
        C.result(f"{tag}.batch_rows", st["b_rows"], "rows")
        C.result(f"{tag}.scalar_objective_share_of_solve", round(share, 4), "ratio")
        C.result(f"{tag}.batch_share_of_solve", round(st["b_t"] / solve, 4), "ratio")
        if st["obj_n"] and st["b_rows"]:
            C.result(f"{tag}.ms_per_scalar_call", round(st["obj_t"] * 1000 / st["obj_n"], 3), "ms (provisional)")
            C.result(f"{tag}.ms_per_batch_row", round(st["b_t"] * 1000 / st["b_rows"], 4), "ms (provisional)")
            C.result(f"{tag}.scalar_call_over_batch_row", round((st["obj_t"] / st["obj_n"]) / (st["b_t"] / st["b_rows"]), 1), "ratio")
        C.result(f"{tag}.parity_mismatches", st["mism"], "calls (exact)")
        C.result(f"{tag}.plan_sha", hashlib.sha1(plan.tobytes()).hexdigest()[:16])
        C.result(f"{tag}.solve_thread_ms_ex_parity", round(solve * 1000, 1), "ms (provisional)")
        C.result(f"{tag}.solve_over_reference", round(solve * 1000 / ref, 2), "x reference_solve")
        C.result(f"{tag}.thread_factor", clk.thread_factor)
    grid = {k: v for k, v in shares.items() if k != "two_zone_dhw_flat"}
    if len(grid) >= 5:
        vals = sorted(grid.values())
        C.result("loo.cells", len(vals))
        C.result("loo.min", round(vals[0], 4))
        C.result("loo.max", round(vals[-1], 4))
        C.result("loo.mean", round(sum(vals) / len(vals), 4))
        C.result("loo.mean_drop_max", round(sum(vals[:-1]) / (len(vals) - 1), 4))
    C.result("reference_solve_cpu_ms", round(ref, 2), "ms (provisional)")
    C.trailer(worst_tf)


if __name__ == "__main__":
    main()
