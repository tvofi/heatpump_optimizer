#!/usr/bin/env python3
"""D7-b: the curve learner's freeze gate is one cycle stale under defrost.

METRIC (one line): number of comfort-miss resets of the learned curve bias
booked on an interval whose defrost flag the shared learner gate refuses
(``_learning_frozen`` answers "defrosting"), on a real coordinator driven
through ``_update_current_state``; the same dip without the flag is the
null control (a genuine miss must still reset), and the same dip with the
flag visible to the tracker (the world after the one-line reorder) is the
perturbation control (no reset).

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/seat-b/curve_gate.py

EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1,
macOS, python3.11):
  RESULT defrost_dip_resets=1 count
  RESULT genuine_miss_resets=1 count        (null control: unchanged)
  RESULT gate_visible_resets=0 count        (perturbation: 1 -> 0)
  RESULT defrost_refused_by_shared_gate=1   (the gate itself does refuse)
with tolerance 0 on each.

KEY OF THE COUNTED NUMBER: the reset is counted on the learner's own state
move (``CurveLearner.bias`` returning to 0.0 and ``resets`` incrementing),
never on an input attribute.
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
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const as hpo_const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

T0 = datetime(2026, 1, 15, 6, 0, 0)


def build():
    cfg = {
        hpo_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        hpo_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        hpo_const.CONF_DHW_TANK_VOLUME: 180.0,
        hpo_const.CONF_CURVE_LEARNING_ENABLED: True,
        hpo_const.CONF_HEAT_PUMP_DEFROST_ENTITY: "sensor.defrost",
    }
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("2.0"))
    hass.states.set("sensor.defrost", FakeState("off"))
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    return hass, coord


def cycle(coord):
    asyncio.run(coord._update_current_state())


def arm(defrost_on, seed_signal):
    """One defrost-dip interval; returns (resets, gate_refused, booked_worst).

    ``seed_signal`` pre-seeds last cycle's PumpSignals with defrosting=True,
    which is what the tracker would see if it ran after the signal read
    instead of before it (the perturbation).
    """
    dt_util.freeze(T0)
    hass, coord = build()
    cycle(coord)
    # The learned bias is negative (the state a working learner holds
    # after a few comfortable weeks), so a booked miss surrenders it.
    coord._curve_learner.bias = -0.6
    coord._curve_learner.comfortable_days = 2
    if seed_signal:
        # Post-reorder world: last cycle's signals already carry the flag,
        # which is what the tracker would consult if it ran after the
        # signal read instead of before it.
        coord._pump_signals = replace(coord._pump_signals, defrosting=True)
    floor = coord._ctx._opt_config.get_temp_bounds(7.0)[0]
    dt_util.freeze(T0 + timedelta(hours=1))
    if defrost_on:
        hass.states.set("sensor.defrost", FakeState("on"))
    # The defrost dip: the zone under the floor the plan was holding.
    hass.states.set("sensor.indoor", FakeState(f"{floor - 0.4:.2f}"))
    coord._curve_day_worst = None
    cycle(coord)
    # The interval IS one the shared gate refuses: cycle 2's own signal
    # read carries the flag, and every other learner froze on it (the
    # learner_gates.py matrix shows house/cop/buffer at 0 under defrost).
    gate_refused = coord._pump_signals.defrosting is True
    resets = coord._curve_learner.resets
    surrendered = coord._curve_learner.bias == 0.0
    return resets, gate_refused, coord._curve_day_worst, surrendered


def main():
    resets, gate, worst, surrendered = arm(defrost_on=True, seed_signal=False)
    print(f"RESULT defrost_dip_resets={resets} count")
    print(f"RESULT defrost_dip_bias_surrendered={1 if surrendered else 0} count")
    print(f"RESULT defrost_refused_by_shared_gate={1 if gate else 0} count")
    print(f"INFO defrost-dip day-worst margin booked: {worst}")

    resets_c, gate_c, worst_c, surrendered_c = arm(
        defrost_on=False, seed_signal=False
    )
    print(f"RESULT genuine_miss_resets={resets_c} count")
    print(f"INFO control day-worst margin booked: {worst_c}")

    resets_p, gate_p, worst_p, surrendered_p = arm(
        defrost_on=True, seed_signal=True
    )
    print(f"RESULT gate_visible_resets={resets_p} count")
    print(f"INFO perturbation day-worst margin booked: {worst_p}")

    proc_cpu = time.process_time()
    thread_cpu = time.thread_time()
    print(
        "RESULT thread_factor="
        f"{(proc_cpu / thread_cpu if thread_cpu else 1.0):.2f}"
    )
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1.00")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
