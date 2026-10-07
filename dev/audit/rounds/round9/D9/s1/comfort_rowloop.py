"""D9-s1 H2: share of a solve's CPU spent in the per-row Python loop of
optimizer.HeatPumpOptimizer._comfort_terms_batch, and whether a row-vectorized
twin (elementwise ops on the [B, n] batch, reductions with axis=1) is bit-for-bit
equal to it.

Metric: thread CPU inside HeatPumpOptimizer._comfort_terms_batch / thread CPU of
the whole optimize() call, per scenario (stress.build_case), ratio; also the
count of numpy reductions it issues per gradient (hooked, not derived).
Count key: the (penalty, comfort_cost) arrays the production method RETURNS,
compared with numpy array_equal (bitwise for finite floats) against the
vectorized twin on the same inputs, every call; and the shipped plan's power
schedule bytes with and without the swap.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/comfort_rowloop.py [--vectorize] [--only CELL]
Perturbation: --vectorize swaps the method for the vectorized twin below;
the share must go DOWN (toward ~0.02) and solve CPU/reference must drop.
Expected at baseline (this box, provisional): share 0.12-0.30 on two-zone
cells; rows mismatched 0 (exact); plan bytes identical (exact).
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
from heatpump_optimizer.optimizer import HeatPumpOptimizer, _COMFORT_FLOOR_L1, \
    _COMFORT_PULL_SINGLE_ZONE, _COMFORT_PULL_TWO_ZONE

PROD = HeatPumpOptimizer._comfort_terms_batch


def vectorized(self, room_temps, upper_temps, lower_temps, comfort_targets,
               temp_min_bounds, temp_max_bounds, comfort_band):
    weight = self.config.comfort_weight
    if self.model.params.two_zone_enabled:
        U = upper_temps[:, 1:]
        L = lower_temps[:, 1:]
        uu = np.maximum(0, temp_min_bounds - U)
        ou = np.maximum(0, U - temp_max_bounds)
        ul = np.maximum(0, temp_min_bounds - L)
        ol = np.maximum(0, L - temp_max_bounds)
        penalty = 0.5 * weight * (
            np.sum(uu ** 2, axis=1) * 10.0
            + np.sum(ou ** 2, axis=1) * 5.0
            + np.sum(ul ** 2, axis=1) * 10.0
            + np.sum(ol ** 2, axis=1) * 5.0
            + (np.sum(uu, axis=1) + np.sum(ul, axis=1)) * _COMFORT_FLOOR_L1
        )
        du = U - comfort_targets
        dl = L - comfort_targets
        comfort = _COMFORT_PULL_TWO_ZONE * weight * (
            np.sum((du / comfort_band) ** 2, axis=1)
            + np.sum((dl / comfort_band) ** 2, axis=1)
        )
        return penalty, comfort
    R = room_temps[:, 1:]
    un = np.maximum(0, temp_min_bounds - R)
    ov = np.maximum(0, R - temp_max_bounds)
    penalty = weight * (
        np.sum(un ** 2, axis=1) * 10.0
        + np.sum(ov ** 2, axis=1) * 5.0
        + np.sum(un, axis=1) * _COMFORT_FLOOR_L1
    )
    dev = R - comfort_targets
    comfort = _COMFORT_PULL_SINGLE_ZONE * weight * np.sum((dev / comfort_band) ** 2, axis=1)
    return penalty, comfort


CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
    "two_zone_dhw_summer": dict(season="summer", two_zone=True, dhw=True),
    "two_zone_nodhw_winter_mild": dict(season="winter_mild", two_zone=True, dhw=False),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", two_zone=False, dhw=True),
    "single_zone_fuse_3p68": dict(season="winter", two_zone=False, dhw=True, power_cap_kw=3.68),
    # null control: flat prices -- the loop is structural, not price-driven
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),
}


class Hook:
    def __init__(self, swap: bool):
        self.swap = swap
        self.cpu = 0.0
        self.calls = 0
        self.rows = 0
        self.mismatch_rows = 0
        self.nsum = 0

    def __call__(self, opt_self, *a):
        t0 = time.thread_time()
        if self.swap:
            out = vectorized(opt_self, *a)
        else:
            out = PROD(opt_self, *a)
        self.cpu += time.thread_time() - t0
        self.calls += 1
        self.rows += a[0].shape[0]
        # parity check, outside the timed window
        other = PROD(opt_self, *a) if self.swap else vectorized(opt_self, *a)
        for x, y in zip(out, other):
            self.mismatch_rows += int(np.count_nonzero(
                (x.view(np.int64) != y.view(np.int64))))
        return out


def count_sums_per_call(run_spec):
    """numpy.sum invocations per production _comfort_terms_batch call (hooked)."""
    calls = {"n": 0}
    orig = np.sum

    def counting(*a, **k):
        calls["n"] += 1
        return orig(*a, **k)
    return calls, counting


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vectorize", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]
    shares = {}
    worst_tf = 1.0
    for cell, spec in CELLS.items():
        if args.only and cell != args.only:
            continue
        hook = Hook(args.vectorize)

        def method(self, *a, _h=hook):
            return _h(self, *a)
        HeatPumpOptimizer._comfort_terms_batch = method
        try:
            with C.Clock() as clk:
                run = stress.build_case(**spec)
        finally:
            HeatPumpOptimizer._comfort_terms_batch = PROD
        worst_tf = max(worst_tf, clk.thread_factor)
        solve_ms = run["solve_thread_ms"]
        # the parity check's own cost ran inside the solve window: remove it
        # by re-timing it -- simplest: subtract nothing, but report the hook
        # CPU against solve-minus-parity via a second timed arm below.
        tag = cell + ("_vec" if args.vectorize else "")
        plan = np.asarray(run["result"].power_schedule, dtype=float)
        C.result(f"{tag}.comfort_batch_calls", hook.calls, "count")
        C.result(f"{tag}.comfort_batch_rows", hook.rows, "rows")
        C.result(f"{tag}.rows_mismatched_vs_twin", hook.mismatch_rows, "values (exact)")
        C.result(f"{tag}.plan_sha", hashlib.sha1(plan.tobytes()).hexdigest()[:16])
        shares[cell] = (hook.cpu * 1000, solve_ms)
        C.result(f"{tag}.comfort_batch_thread_ms", round(hook.cpu * 1000, 1), "ms (provisional)")
        C.result(f"{tag}.thread_factor", clk.thread_factor)
    # Clean timing arm: no parity check inside the window.
    for cell, spec in CELLS.items():
        if args.only and cell != args.only:
            continue
        acc = {"t": 0.0}

        def method(self, *a, _acc=acc):
            t0 = time.thread_time()
            out = vectorized(self, *a) if args.vectorize else PROD(self, *a)
            _acc["t"] += time.thread_time() - t0
            return out
        HeatPumpOptimizer._comfort_terms_batch = method
        try:
            run = stress.build_case(**spec)
        finally:
            HeatPumpOptimizer._comfort_terms_batch = PROD
        tag = cell + ("_vec" if args.vectorize else "")
        share = acc["t"] * 1000 / run["solve_thread_ms"]
        shares[cell] = share
        C.result(f"{tag}.clean_solve_thread_ms", round(run["solve_thread_ms"], 1), "ms (provisional)")
        C.result(f"{tag}.clean_solve_over_reference", round(run["solve_thread_ms"] / ref, 2), "x reference_solve")
        C.result(f"{tag}.comfort_share_of_solve", round(share, 4), "ratio")
    grid = {k: v for k, v in shares.items() if k != "two_zone_dhw_flat" and isinstance(v, float)}
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
