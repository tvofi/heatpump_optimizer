#!/usr/bin/env python3
"""Can the heat-loss learners' per-interval rate limit bind? (R10-DEAD-RATE-LIMIT)

Written by the R10-DEAD-RATE-LIMIT fixer. ``learner_newton_step`` used to end
in a rate limit, ``clip(updated, current +- current * max_step_fraction)``,
fed ``HOUSE_LOSS_MAX_STEP`` at both call sites. Once the trust region is a
fraction of the current estimate (#2252), the EWMA moves a sample by
``alpha * (target - current)`` with ``|target - current| <= trust_region *
current``, so no sample can move the estimate further than ``alpha *
trust_region`` of it, inside the limit.

This drives the production step over a grid of every input the two call
sites can reach -- ``current`` across the ``_apply_*`` clamps (the same
[0.3, 3.0] for the scale and the ratio), residuals across the accepted
range and far past it, every gated delta-T and interval length -- and per
point compares the step to the same step with the limit applied on top of
it (at a tree whose step still takes ``max_step_fraction``, the step with
an unbounded fraction). It prints:

  * ``points``      -- grid points evaluated, and ``none`` those with no step;
  * ``binds``       -- points where the limit changes the step (rule: the
    clipped and unclipped ``updated`` differ by more than 1e-15);
  * ``max_moved_fraction`` -- max over the grid of |updated - current| / current;
  * ``bound``       -- ``alpha * trust_region``, the derived ceiling;
  * ``digest``      -- sha1 over every point's production (target, updated)
    reprs -- the limit at ``--limit`` applied where the step still takes it --
    so two trees whose production steps are bit-identical print one digest.

Expected at the shipped constants: binds=0 at the pre-#2252 base, the
#2252 merge and the fix head alike, max_moved_fraction == bound after #2252.
Null controls, each reading binds > 0 at any tree where the limit is a
fraction of the estimate: ``--alpha 1.0`` (an EWMA that outruns it), and
``--current-min 0.05 --current-max 0.2`` at the pre-#2252 base (a fixed
trust-region offset is a larger fraction of a small estimate; unreachable
under the clamps). Run from a worktree root:

    PYTHONPATH=tests/hastub:custom_components \\
        python3 dev/audit/harnesses/r10_dead_rate_limit.py
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools

import numpy as np

from heatpump_optimizer import coordinator as coord_mod
from heatpump_optimizer.const import (
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    LOWER_FLOOR_LOSS_RATIO_MAX,
    LOWER_FLOOR_LOSS_RATIO_MIN,
)
from heatpump_optimizer.thermal_model import learner_newton_step


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, default=coord_mod.HOUSE_LOSS_ALPHA)
    ap.add_argument("--trust-region", type=float, default=coord_mod._LEARNER_TRUST_REGION)
    ap.add_argument("--limit", type=float, default=coord_mod.HOUSE_LOSS_MAX_STEP,
                    help="the rate-limit fraction probed (default: HOUSE_LOSS_MAX_STEP)")
    ap.add_argument("--current-min", type=float,
                    default=min(HOUSE_HEAT_LOSS_SCALE_MIN, LOWER_FLOOR_LOSS_RATIO_MIN))
    ap.add_argument("--current-max", type=float,
                    default=max(HOUSE_HEAT_LOSS_SCALE_MAX, LOWER_FLOOR_LOSS_RATIO_MAX))
    a = ap.parse_args()

    takes_limit = "max_step_fraction" in inspect.signature(learner_newton_step).parameters
    kw = {"trust_region": a.trust_region, "alpha": a.alpha}
    if takes_limit:
        kw["max_step_fraction"] = float("inf")

    max_res = coord_mod.HOUSE_LOSS_MAX_RESIDUAL
    currents = np.unique(np.concatenate([
        np.linspace(a.current_min, a.current_max, 28), [a.current_min, a.current_max, 1.0]]))
    residuals = np.concatenate([np.linspace(-max_res, max_res, 41), [-1e6, -50.0, 50.0, 1e6]])
    delta_ts = [coord_mod.HOUSE_LOSS_MIN_DELTA, 10.0, 20.0, 40.0]
    dts = [coord_mod.HOUSE_LOSS_MIN_SAMPLE_HOURS, 0.25, 0.5, coord_mod.HOUSE_LOSS_MAX_SAMPLE_HOURS]
    base_us = [0.02, 0.15, 0.4]
    capacities = [2.0, 10.0, 30.0]

    points = none = binds = 0
    moved = 0.0
    digest = hashlib.sha1()
    for cur, res, d_t, dt, bu, cap in itertools.product(
            currents, residuals, delta_ts, dts, base_us, capacities):
        points += 1
        cur = float(cur)
        step = learner_newton_step(cur, bu, cap, float(res), d_t, dt, **kw)
        if step is None:
            digest.update(b"None")
            none += 1
            continue
        updated = step[1]
        lim = cur * a.limit
        clipped = float(np.clip(updated, cur - lim, cur + lim))
        # What production returns: the limit applied where the step takes it.
        digest.update(repr((step[0], clipped if takes_limit else updated)).encode())
        if abs(clipped - updated) > 1e-15:
            binds += 1
        moved = max(moved, abs(updated - cur) / cur)

    print(f"takes_max_step_fraction={takes_limit} alpha={a.alpha} "
          f"trust_region={a.trust_region} limit={a.limit} "
          f"current=[{a.current_min}, {a.current_max}]")
    print(f"RESULT points={points}")
    print(f"RESULT none={none}")
    print(f"RESULT binds={binds}")
    print(f"RESULT max_moved_fraction={moved:.12f}")
    print(f"RESULT bound={a.alpha * a.trust_region:.12f}")
    print(f"RESULT digest={digest.hexdigest()}")


if __name__ == "__main__":
    main()
