"""V2 (independent) check of D9-s1-02: L-BFGS-B's scalar f(x) evaluations
in optimizer._multi_start_minimize.

Metric A (own definition, narrower than the finder's): thread CPU of the RAW
scalar objective calls made while scipy's minimize is on the stack (the seam
stress.SolverWork._wrapped = optimizer._scoped_minimize), i.e. f(x) evaluations
that reach the objective past the #288 memo, over optimize() thread CPU. The
finder's metric also counts candidate scoring and restart score/prior; this
one excludes them (reported separately as outside_share).
Metric B: 1 - median(solve_fused)/median(solve_prod) end to end, interleaved
A/B/A/B, where the fused arm (written here) hands scipy jac=True and takes f
from an extra row 0 of the gradient batch; plan sha and nfev compared.
Count key: calls delivered to the objective callable production passes to
_multi_start_minimize; result.power_schedule bytes.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_scalar_fun.py [--pairs 2]
Perturbation: the fused arm (inside-minimize scalar calls must go to ~0 and
solve CPU DOWN, plan identical); null: flat-price cell, and prod-vs-prod spread.
Expected (1936d5ca, this box, provisional): inside share 0.08-0.2; saved
fraction of the same order; plan sha equal.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import hashlib
import statistics
import time

import numpy as np

import stress
from heatpump_optimizer import optimizer as om

ORIG_MSM = om._multi_start_minimize
ORIG_SEAM = stress.SolverWork._wrapped
ST = {"depth": 0, "in_t": 0.0, "in_n": 0, "out_t": 0.0, "out_n": 0, "ctx": None,
      "fused": False, "check": False, "mism": 0, "fused_calls": 0}


def msm(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    def timed(x, *a):
        t0 = time.thread_time()
        v = objective(x, *a)
        dt = time.thread_time() - t0
        if ST["depth"]:
            ST["in_t"] += dt; ST["in_n"] += 1
        else:
            ST["out_t"] += dt; ST["out_n"] += 1
        return v
    prev = ST["ctx"]
    ST["ctx"] = (objective, batch_objective, fd_eps, bounds)
    try:
        return ORIG_MSM(timed, candidates, bounds, args, maxiter, batch_objective, fd_eps)
    finally:
        ST["ctx"] = prev


def seam(fun, x0, args=(), jac=None, **kw):
    ctx = ST["ctx"]
    if ST["fused"] and callable(jac) and ctx is not None and ctx[1] is not None:
        raw, bobj, eps, bounds = ctx

        def fg(x, *a):
            x = np.asarray(x, dtype=float)
            held = []
            om._batch_fd_gradient(lambda m, *_: held.append(m.copy()) or np.zeros(len(m)),
                                  a, x, 0.0, eps, bounds)
            vals = bobj(np.vstack([x[None, :], held[0]]), *a)
            f = float(vals[0])
            g = om._batch_fd_gradient(lambda m, *_: vals[1:], a, x, f, eps, bounds)
            ST["fused_calls"] += 1
            if ST["check"]:
                s = float(raw(x, *a))
                ST["mism"] += int(np.float64(s).view(np.int64) != np.float64(f).view(np.int64))
            return f, g
        ST["depth"] += 1
        try:
            return ORIG_SEAM(fg, x0, args=args, jac=True, **kw)
        finally:
            ST["depth"] -= 1
    ST["depth"] += 1
    try:
        return ORIG_SEAM(fun, x0, args=args, jac=jac, **kw)
    finally:
        ST["depth"] -= 1


CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", two_zone=False, dhw=True),
    "single_zone_fuse_3p68": dict(season="winter", two_zone=False, dhw=True, power_cap_kw=3.68),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),  # null: flat prices
}


def solve(spec, fused, check=False):
    for k in ("in_t", "out_t"):
        ST[k] = 0.0
    for k in ("in_n", "out_n", "mism", "fused_calls"):
        ST[k] = 0
    ST["fused"], ST["check"] = fused, check
    om._multi_start_minimize = msm
    stress.SolverWork._wrapped = seam
    try:
        run = stress.build_case(**spec)
    finally:
        om._multi_start_minimize = ORIG_MSM
        stress.SolverWork._wrapped = ORIG_SEAM
    sha = hashlib.sha1(np.asarray(run["result"].power_schedule, float).tobytes()).hexdigest()[:16]
    return run, sha, dict(ST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=2)
    args = ap.parse_args()
    for cell, spec in CELLS.items():
        a, b, sa, sb = [], [], set(), set()
        for i in range(args.pairs):
            run, s, st = solve(spec, False)
            a.append(run["solve_thread_ms"]); sa.add(s)
            if i == 0:
                solve_s = run["solve_thread_ms"] / 1000
                V.result(f"{cell}.inside_minimize_scalar_calls", st["in_n"], "count")
                V.result(f"{cell}.outside_scalar_calls", st["out_n"], "count (scoring/restart score)")
                V.result(f"{cell}.inside_share_of_solve", round(st["in_t"] / solve_s, 4), "ratio")
                V.result(f"{cell}.outside_share_of_solve", round(st["out_t"] / solve_s, 4), "ratio")
                V.result(f"{cell}.ms_per_scalar_call", round(1000 * st["in_t"] / max(st["in_n"], 1), 3), "ms (provisional)")
                evals_a = run["solver_evals"]
            run, s, st = solve(spec, True)
            b.append(run["solve_thread_ms"]); sb.add(s)
            if i == 0:
                V.result(f"{cell}.fused_inside_minimize_scalar_calls", st["in_n"], "count")
                V.result(f"{cell}.fused_calls", st["fused_calls"], "count")
                V.result(f"{cell}.solver_evals_equal", int(run["solver_evals"] == evals_a), "bool")
        run, s, st = solve(spec, True, check=True)
        V.result(f"{cell}.fused_row0_vs_scalar_mismatches", st["mism"], f"of {st['fused_calls']} (exact)")
        V.result(f"{cell}.prod_solve_thread_ms_median", round(statistics.median(a), 1), "ms (provisional)")
        V.result(f"{cell}.fused_solve_thread_ms_median", round(statistics.median(b), 1), "ms (provisional)")
        V.result(f"{cell}.saved_fraction_of_solve", round(1 - statistics.median(b) / statistics.median(a), 4), "ratio")
        V.result(f"{cell}.null_prod_vs_prod_spread", round(max(a) / min(a) - 1, 4), "ratio")
        V.result(f"{cell}.plan_sha_equal", int(sa == sb and len(sa) == 1 and s in sa), "bool (exact)")
    V.trailer()


if __name__ == "__main__":
    main()
