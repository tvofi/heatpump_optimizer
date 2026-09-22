#!/usr/bin/env python3
"""D0-c fixer arms: what each shipping knob actually buys, arm by arm.

METRIC (one line): per cell, gap_pct = 100*(J_arm - J_prod)/|J_arm| where
J_prod is the production objective of a fresh ``optimize()`` (no warm start)
and J_arm is the same solve driven through the SAME production seam with one
knob reverted:

  prefix   the pre-fix configuration -- the appended seed dropped (the last
           candidate of a list long enough to hold it, ``len >= 5``) and
           ``_MULTI_START_SOLVES`` back at 4;
  prefix0  the same, but dropping the last candidate of EVERY call -- the arm
           that reads as the pre-fix configuration and is not one: on a path
           that makes a second, single-candidate repair call it empties that
           call and the arm fails with "no usable starting point";
  seed     the shipped cut kept at 6, only the appended seed dropped: the
           seed's own remaining effect;
  cut4     the cut knob alone -- every candidate kept, the cut back at 4.

COMMAND (from the tree root):
  PYTHONPATH=tests/hastub python3 \
      tools/audit/round5/D0/seat-c/arms.py [--probe prefix|seed|cutnull]

EXPECTED at head 6.6.8 + this branch, and the reason each check in
``tests/optimality.py`` is written the way it is:

  prefix   the 0.85 seed is NOT load-bearing on tz=1,dhw=1,summer_negative,
           winter_cold: prod 19.4353 against a faithful arm's 19.4353
           (+0.0000%), while the arm that empties the repair call prints
           19.6801 (+1.2440%) -- a gap that is the arm's structural failure,
           not the seed.  Across the seed's mover cells the faithful arm sits
           within 0.0999%, inside the band the suite calls noise, so no
           behavioural check pins the seed itself.
  seed     same conclusion at the shipped cut: the seed's own effect is
           <= 0.0999% on every probed cell.
  cutnull  a cut-null cell must be inert at BOTH stop rules -- at ftol 1e-6
           the seeds-kept/cut-4 arm moves by +0.0681% on
           tz=1,dhw=0,shoulder,winter_cold, so that cell cannot be the null;
           tz=0,dhw=0,winter_extreme,winter_cold reads 80.7406 both ways at
           both stop rules and is the cell the check uses.

Nothing here re-derives a cost: every number is an objective value the
production seam returned.  (Artifacts of this seat at head: the PR body's
Figures table.)
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
if not os.path.isdir(os.path.join(ROOT, "custom_components")):
    raise SystemExit(f"{ROOT} is not a checkout root (no custom_components)")
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

from datetime import datetime                                    # noqa: E402
from unittest import mock                                        # noqa: E402
from profiles import prices, weather, house                      # noqa: E402
from heatpump_optimizer.thermal_model import (                   # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (                       # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
import heatpump_optimizer.optimizer as om                        # noqa: E402

START = datetime(2026, 1, 15)
_REAL = om._multi_start_minimize
_CUT_KEEP = om._MULTI_START_SOLVES


def inputs_for(tz, dhw, pp, wp):
    """Fresh optimizer + inputs, so no prior plan and no warm start."""
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(pp, START)
    ot, wi, ra, so = weather(wp, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, pr, ot, wi, ra, so, st


def _cut(cut):
    """A wrapper that runs the seam with ``_MULTI_START_SOLVES`` at ``cut``."""
    def arm(objective, candidates, bounds, *a, **kw):
        om._MULTI_START_SOLVES = cut
        try:
            return _REAL(objective, candidates, bounds, *a, **kw)
        finally:
            om._MULTI_START_SOLVES = _CUT_KEEP
    return arm


def _drop_seed(cut, every_call):
    """The seed dropped, the cut at ``cut``; ``every_call`` drops from every
    call and empties a single-candidate repair call."""
    def arm(objective, candidates, bounds, *a, **kw):
        cands = list(candidates)
        if every_call or len(cands) >= 5:
            cands = cands[:-1]
        om._MULTI_START_SOLVES = cut
        try:
            return _REAL(objective, cands, bounds, *a, **kw)
        finally:
            om._MULTI_START_SOLVES = _CUT_KEEP
    return arm


def solve(tz, dhw, pp, wp, arm=None, ftol=None):
    o, pr, ot, wi, ra, so, st = inputs_for(tz, dhw, pp, wp)
    stack = []
    if ftol is not None:
        stack.append(mock.patch.object(om, "_LBFGSB_FTOL", ftol))
    if arm is not None:
        stack.append(mock.patch.object(om, "_multi_start_minimize", arm))
    for ctx in stack:
        ctx.start()
    try:
        return float(o.optimize(st, pr, ot, wi, ra, so, START).objective_value)
    finally:
        for ctx in reversed(stack):
            ctx.stop()


def probe_prefix():
    cells = [
        (1, 1, "summer_negative", "winter_cold"),
        (1, 1, "shoulder", "winter_cold"),
        (0, 1, "flat", "shoulder"),
        (0, 0, "winter_typical", "summer_cool"),
    ]
    print(f"{'cell':42s} {'prod':>9s} {'faithful':>9s} {'gap%':>8s} "
          f"{'emptying':>9s} {'gap%':>8s}")
    for tz, dhw, pp, wp in cells:
        cid = f"tz={tz},dhw={dhw},{pp},{wp}"
        prod = solve(tz, dhw, pp, wp)
        good = solve(tz, dhw, pp, wp, arm=_drop_seed(4, False))
        bad = solve(tz, dhw, pp, wp, arm=_drop_seed(4, True))
        g1 = 100.0 * (good - prod) / abs(good)
        g2 = 100.0 * (bad - prod) / abs(bad)
        print(f"{cid:42s} {prod:9.4f} {good:9.4f} {g1:+8.4f} "
              f"{bad:9.4f} {g2:+8.4f}")


def probe_seed():
    cells = [
        (1, 1, "summer_negative", "winter_cold"),
        (1, 1, "shoulder", "winter_cold"),
        (1, 1, "summer_negative", "shoulder"),
        (1, 1, "winter_narrow", "winter_mild"),
        (1, 1, "winter_moderate", "winter_mild"),
        (0, 1, "flat", "shoulder"),
        (0, 1, "winter_typical", "winter_cold"),
        (0, 0, "winter_typical", "summer_cool"),
        (0, 0, "shoulder", "winter_mild"),
        (0, 0, "winter_extreme", "winter_mild"),
    ]
    helps = worse = 0
    print(f"{'cell':42s} {'prod':>9s} {'no-seed':>9s} {'gap%':>8s}")
    for tz, dhw, pp, wp in cells:
        cid = f"tz={tz},dhw={dhw},{pp},{wp}"
        prod = solve(tz, dhw, pp, wp)
        seedless = solve(tz, dhw, pp, wp, arm=_drop_seed(6, False))
        g = 100.0 * (seedless - prod) / abs(seedless)
        helps += g > 1e-4
        worse += g < -1e-4
        print(f"{cid:42s} {prod:9.4f} {seedless:9.4f} {g:+8.4f}")
    print(f"seeds help (> +0.01%) on {helps} of {len(cells)}; "
          f"hurt (< -0.01%) on {worse}")


def probe_cutnull():
    cells = [
        (1, 1, "winter_extreme", "shoulder"),
        (1, 1, "winter_typical", "summer_cool"),
        (0, 1, "flat", "winter_mild"),
        (0, 1, "winter_narrow", "winter_mild"),
        (1, 0, "shoulder", "winter_cold"),
        (0, 0, "winter_typical", "winter_cold"),
        (0, 0, "winter_extreme", "winter_cold"),
        (1, 1, "winter_moderate", "winter_cold"),
        (0, 0, "winter_narrow", "summer_cool"),
        (1, 0, "winter_typical", "shoulder"),
    ]
    print(f"{'cell':42s} {'9: prod':>9s} {'9: cut4':>9s} {'9: gap%':>8s} "
          f"{'6: prod':>9s} {'6: cut4':>9s} {'6: gap%':>8s}")
    for tz, dhw, pp, wp in cells:
        cid = f"tz={tz},dhw={dhw},{pp},{wp}"
        p9 = solve(tz, dhw, pp, wp, ftol=1e-9)
        c9 = solve(tz, dhw, pp, wp, ftol=1e-9, arm=_cut(4))
        p6 = solve(tz, dhw, pp, wp, ftol=1e-6)
        c6 = solve(tz, dhw, pp, wp, ftol=1e-6, arm=_cut(4))
        g9 = 100.0 * (c9 - p9) / abs(c9)
        g6 = 100.0 * (c6 - p6) / abs(c6)
        print(f"{cid:42s} {p9:9.4f} {c9:9.4f} {g9:+8.4f} "
              f"{p6:9.4f} {c6:9.4f} {g6:+8.4f}")


PROBES = {"prefix": probe_prefix, "seed": probe_seed, "cutnull": probe_cutnull}

if __name__ == "__main__":
    want = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--probe" else None
    for name, fn in PROBES.items():
        if want in (None, name):
            print(f"===== {name}")
            fn()
