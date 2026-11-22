"""R11-OUTSIDE-3849: what a solve prices a hot water to heating switch at before the latch.

    PYTHONPATH=tests/hastub:custom_components \\
        python3 dev/audit/harnesses/r11_outside_3849_unlatched_price.py

Synthetic; no private data. The finding is outside issue 3849 (Bankaifan),
which has no finder harness; this one reproduces its cases 2, 3 and 03:00 on
the tree it runs in, and runs on a tree before the fix (it reads only
``DutySwitchLearner.planner_pairs``, ``optimizer._switch_cost_fn`` and
``optimizer._leg_rule``, and sets ``duty_switch_unlatched`` only where the
configuration has it).

The record is the issue's: hot water to heating stopped 3, kept 0, n = 2,
unlatched; heating to hot water never seen. The plans are the issue's ledger
around 03:00, one hot-water charge split by a single heating step
(``split``), against the same steps with the charge whole (``whole``): hot
water 2.0 kW, heating 1.0 kW, a 3.0 kW pump with a 0.53 kW floor, one start
priced 1.0. The combined draw of both is on at every step, so the start term
sees neither switch; the switch term is all that separates them.

Printed per learner: the read (stop pair, off pair, mask), the leg rule the
solve serves a both step by, the switch term of each plan and the split's
excess. Null control: an empty learner prices nothing on either tree, and
its leg rule is ``DEFAULT_RULE``; the harness exits 1 if it reads otherwise.
"""
from __future__ import annotations

import dataclasses
import sys
from datetime import date

import numpy as np

import heatpump_optimizer.optimizer as om
from heatpump_optimizer import duty_legs, duty_switch
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

DHW_KW, SPACE_KW, P_MAX, P_MIN, START = 2.0, 1.0, 3.0, 0.53, 1.0
#: 02:30 02:45 03:00 03:15 03:30 03:45 04:00, the ledger's duties.
SPLIT = ("dhw", "dhw", "space", "dhw", "dhw", "space", "space")
WHOLE = ("dhw", "dhw", "dhw", "dhw", "space", "space", "space")


def _plan(duties: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    space = np.array([SPACE_KW if d == "space" else 0.0 for d in duties])
    dhw = np.array([DHW_KW if d == "dhw" else 0.0 for d in duties])
    return space, dhw


def _learners() -> dict[str, duty_switch.DutySwitchLearner]:
    day = date(2026, 11, 21)
    issue = duty_switch.Direction(k=2.0, kept_w=0.0, first_day=day, last_day=day, usable=False,
                                  off_s=[455.0, 483.0, 450.0], stopped=3)
    return {
        "empty (null control)": duty_switch.DutySwitchLearner(),
        "issue 3849 (stopped 3, kept 0, n = 2, unlatched)": duty_switch.DutySwitchLearner(
            {"dhw_space": issue, "space_dhw": duty_switch.Direction()}),
    }


def _opt(learner: duty_switch.DutySwitchLearner) -> om.HeatPumpOptimizer:
    params = ThermalParameters()
    params.min_electrical_power, params.max_electrical_power = P_MIN, P_MAX
    params.dhw_enabled = True
    stops, off = learner.planner_pairs()
    fields = {"cycling_cost": START, "duty_switch_stop_probability": stops,
              "duty_switch_off_seconds": off}
    names = {f.name for f in dataclasses.fields(om.OptimizationConfig)}
    if "duty_switch_unlatched" in names:
        fields["duty_switch_unlatched"] = learner.unlatched()
    return om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig(**fields))


def main() -> int:
    bad = 0
    for label, learner in _learners().items():
        opt = _opt(learner)
        term = om._switch_cost_fn(opt)
        cost = {}
        for name, duties in (("split", SPLIT), ("whole", WHOLE)):
            value = term(*_plan(duties))
            cost[name] = 0.0 if value is None else float(value)
        rule = om._leg_rule(opt)
        print(f"{label}: read {learner.planner_pairs()} mask "
              f"{getattr(opt.config, 'duty_switch_unlatched', 'absent')} leg rule {rule}")
        print(f"  switch term split {cost['split']:.4f} whole {cost['whole']:.4f} "
              f"split excess {cost['split'] - cost['whole']:.4f} (start price {START})")
        if label.startswith("empty") and (any(cost.values()) or rule != duty_legs.DEFAULT_RULE):
            print("  NULL CONTROL FAILED: an empty learner priced a switch or moved the legs")
            bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
