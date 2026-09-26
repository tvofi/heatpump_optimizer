"""D9 verify-v3 (round 9, lens V3) for D9-s1-02: CPU of scalar objective
evaluations that L-BFGS-B requests at a point whose batched gradient is taken
immediately after (the evaluations a fused f-from-row-0 would replace).

Metric (one line): fusable_share = thread CPU of real (memo-missing) scalar
objective evaluations made inside optimizer._scoped_minimize whose x equals the
x0 of the very next optimizer._batch_fd_gradient call / thread CPU of the whole
optimize(), per stress.build_case cell; net_share subtracts one extra batch row
per fused evaluation at this solve's own measured ms-per-batch-row.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s1_02_scalar.py
Instrumented symbols: optimizer._multi_start_minimize (objective and
batch_objective wrapped), optimizer._scoped_minimize, optimizer._batch_fd_gradient.
Perturbation: --maxiter-scale 0.02 (in memory: _multi_start_minimize's maxiter
x0.02, ~6 iterations per run) -> fusable evaluation COUNT must go down (fewer iterates).
Expected: fusable_share 0.10-0.20 on two-zone DHW winter (+-0.03, provisional);
counts exact per machine.  Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, time
import numpy as np
import stress
from heatpump_optimizer import optimizer as om

ORIG_MSM = om._multi_start_minimize
ORIG_SM = om._scoped_minimize
ORIG_BFD = om._batch_fd_gradient

S = {}


def reset():
    S.update(in_sp=0, evals=[], pending=None, fusable=0, fusable_cpu=0.0,
             scalar_cpu=0.0, scalar_n=0, batch_cpu=0.0, batch_rows=0, grads=0)


def sm(*a, **k):
    S["in_sp"] += 1
    try:
        return ORIG_SM(*a, **k)
    finally:
        S["in_sp"] -= 1


def bfd(batch_objective, args, x0, f0, eps, bounds):
    S["grads"] += 1
    p = S["pending"]
    if p is not None and p[0] == np.asarray(x0, float).tobytes():
        S["fusable"] += 1
        S["fusable_cpu"] += p[1]
    S["pending"] = None
    return ORIG_BFD(batch_objective, args, x0, f0, eps, bounds)


def msm(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    def obj(x, *a):
        t0 = time.thread_time()
        v = objective(x, *a)
        dt = time.thread_time() - t0
        S["scalar_cpu"] += dt; S["scalar_n"] += 1
        S["pending"] = (np.asarray(x, float).tobytes(), dt) if S["in_sp"] else None
        return v
    bobj = None
    if batch_objective is not None:
        def bobj(X, *a):
            t0 = time.thread_time()
            v = batch_objective(X, *a)
            S["batch_cpu"] += time.thread_time() - t0
            S["batch_rows"] += np.shape(X)[0]
            return v
    return ORIG_MSM(obj, candidates, bounds, args, max(1, int(maxiter * SCALE)), bobj, fd_eps)


SCALE = 1.0
CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),
}


def main():
    global SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxiter-scale", type=float, default=1.0)
    a = ap.parse_args()
    SCALE = a.maxiter_scale
    tag0 = "" if SCALE == 1.0 else f"mi{SCALE}_"
    om._multi_start_minimize = msm; om._scoped_minimize = sm; om._batch_fd_gradient = bfd
    # stress.SolverWork re-installs its own counter at om._scoped_minimize and calls
    # its class-level _wrapped: route that through ours too.
    orig_wr = stress.SolverWork._wrapped; stress.SolverWork._wrapped = sm
    try:
        for cell, spec in CELLS.items():
            reset()
            r = stress.build_case(**spec)
            solve = r["solve_thread_ms"] / 1000.0
            row = S["batch_cpu"] / max(S["batch_rows"], 1)
            t = tag0 + cell
            V.R(f"{t}.scalar_evals", S["scalar_n"], "count")
            V.R(f"{t}.grads", S["grads"], "count")
            V.R(f"{t}.fusable_evals", S["fusable"], "count")
            V.R(f"{t}.scalar_share", round(S["scalar_cpu"] / solve, 4), "ratio")
            V.R(f"{t}.fusable_share", round(S["fusable_cpu"] / solve, 4), "ratio")
            V.R(f"{t}.net_share", round((S["fusable_cpu"] - S["fusable"] * row) / solve, 4), "ratio")
            V.R(f"{t}.scalar_over_row", round((S["scalar_cpu"] / max(S['scalar_n'], 1)) / row, 1), "ratio")
            V.R(f"{t}.solve_thread_ms", round(solve * 1000, 1), "ms (provisional)")
            V.R(f"{t}.thread_factor", V.tf_now())
    finally:
        om._multi_start_minimize = ORIG_MSM; om._scoped_minimize = ORIG_SM; om._batch_fd_gradient = ORIG_BFD
        stress.SolverWork._wrapped = orig_wr
    V.trailer()


if __name__ == "__main__":
    main()
