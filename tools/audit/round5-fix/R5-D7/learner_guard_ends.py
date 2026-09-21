#!/usr/bin/env python3
"""R5-D7 null control: the two learner guards at BOTH ends of their state.

METRIC (one line): for each (learner, state-end, interval) cell, 1 if the
learner's own state moved on the interval -- a ``CurveLearner`` bias reset
(``bias`` -> 0.0 and ``resets`` incrementing) or a ``ComfortLearner``
``evidence`` move -- and 0 if it refused; each learner is driven with its
state at ZERO EVIDENCE and pinned ON ITS CLAMP, once on the defrost interval
the shared gate refuses and once on the same interval clean.

The clean cells are the null control: fixer.md step 3 asks a learner or
guard change to be measured at both ends of its input range, so this is the
instrument for "the fix refuses the contamination and nothing else, with
nothing to learn (a fresh install) and with the state pinned on its clamp".

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5-fix/R5-D7/learner_guard_ends.py

EXPECTED at head 4f0c9d3 (Apple M1, macOS, python3.11): the defrost cells are
0 and the clean cells are 1 at BOTH ends, with one documented exception --
``curve_clean_zero`` is 0 in EITHER tree, because ``CurveLearner.record_miss``
returns early unless a bias is already below zero (``bias >= BIAS_MAX``), so
a fresh install cannot reset. A reverted tree reds the four defrost cells
(they fold/reset and print 1); the clean cells are the control and do not
move either way. Tolerance 0 on each.

KEY OF THE COUNTED NUMBER: the move is counted on the learner's own state
(``CurveLearner.bias``/``resets``, ``ComfortLearner.evidence``), never on an
input attribute.
"""
import os
import sys

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const as hpo_const  # noqa: E402
from heatpump_optimizer.comfort_learning import (  # noqa: E402
    COMFORT_WEIGHT_MIN,
    EVIDENCE_THRESHOLD,
)
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer.curve_learning import BIAS_MIN  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

T0 = datetime(2026, 1, 15, 6, 0, 0)

# The flat, swinging-price plan the quiet learner folds, with a real spread,
# enough planned heating to be a "held flat" cost, and a flat trajectory.
QUIET_PLAN = (0.10, 0.30, 0.20, 0.40)
QUIET_POWER = (3.0, 3.0, 3.0, 3.0)
QUIET_TRAJ = (20.9, 21.0, 20.9, 21.0)


class _Plan:
    """The three fields ``_record_quiet_comfort_period`` reads off a solve."""

    def __init__(self):
        self.prices = list(QUIET_PLAN)
        self.power_schedule = list(QUIET_POWER)
        self.room_temp_trajectory = list(QUIET_TRAJ)


def build(curve=True, defrost_entity=True, comfort=False):
    cfg = {
        hpo_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        hpo_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        hpo_const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    if curve:
        cfg[hpo_const.CONF_CURVE_LEARNING_ENABLED] = True
    if comfort:
        cfg[hpo_const.CONF_COMFORT_LEARNING_ENABLED] = True
    if defrost_entity:
        cfg[hpo_const.CONF_HEAT_PUMP_DEFROST_ENTITY] = "sensor.defrost"
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("2.0"))
    hass.states.set("sensor.defrost", FakeState("off"))
    return hass, HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))


def cycle(coord):
    asyncio.run(coord._update_current_state())


def curve_cell(seed_bias, defrost_on):
    """One defrost-or-clean dip; 1 if the bias reset, else 0."""
    dt_util.freeze(T0)
    hass, coord = build()
    cycle(coord)
    coord._curve_learner.bias = seed_bias
    coord._curve_learner.comfortable_days = 2
    floor = coord._opt_config.get_temp_bounds(7.0)[0]
    dt_util.freeze(T0 + timedelta(hours=1))
    if defrost_on:
        hass.states.set("sensor.defrost", FakeState("on"))
    hass.states.set("sensor.indoor", FakeState(f"{floor - 0.4:.2f}"))
    before = coord._curve_learner.resets
    cycle(coord)
    dt_util.freeze(None)
    return 1 if coord._curve_learner.resets > before else 0


def quiet_cell(seed_evidence, defrost_on):
    """One defrost-or-clean interval, then the quiet fold; 1 if evidence moved."""
    dt_util.freeze(T0)
    hass, coord = build(curve=False, comfort=True)
    cycle(coord)
    dt_util.freeze(T0 + timedelta(hours=1))
    if defrost_on:
        hass.states.set("sensor.defrost", FakeState("on"))
    cycle(coord)
    coord._comfort_learner.evidence = seed_evidence
    coord._comfort_learner.learned_weight = COMFORT_WEIGHT_MIN
    coord._optimization_result = _Plan()
    before = coord._comfort_learner.evidence
    coord._record_quiet_comfort_period()
    dt_util.freeze(None)
    return 1 if coord._comfort_learner.evidence != before else 0


def main():
    # The curve tracker: zero evidence, and the clamp.
    print(f"RESULT curve_defrost_zero={curve_cell(0.0, True)} count")
    print(f"RESULT curve_defrost_clamp={curve_cell(BIAS_MIN, True)} count")
    print(f"RESULT curve_clean_zero={curve_cell(0.0, False)} count")
    print(f"RESULT curve_clean_clamp={curve_cell(BIAS_MIN, False)} count")
    # The quiet learner: zero evidence, and the clamp (weight at its floor,
    # evidence one fold short of the threshold).
    print(f"RESULT quiet_defrost_zero={quiet_cell(0.0, True)} count")
    print(
        "RESULT quiet_defrost_clamp="
        f"{quiet_cell(-(EVIDENCE_THRESHOLD - 0.005), True)} count"
    )
    print(f"RESULT quiet_clean_zero={quiet_cell(0.0, False)} count")
    print(
        "RESULT quiet_clean_clamp="
        f"{quiet_cell(-(EVIDENCE_THRESHOLD - 0.005), False)} count"
    )

    proc_cpu = time.process_time()
    thread_cpu = time.thread_time()
    print(f"RESULT thread_factor={(proc_cpu / thread_cpu if thread_cpu else 1.0):.2f}")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
