#!/usr/bin/env python3
"""Pins four #805 survivors that do not live in coordinator.py or optimizer.py.

The judge-corrected sample left ten consequential mutants. #806 and #807
already kill the two sensor None-returns and the NaN price-shape admission.
These four are the rest that can be reached without editing those two
production files, or the two test scripts other seats hold.

    PYTHONPATH=tests/hastub python3 tests/guard_pins.py
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, Results
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.price_model import PriceShapeModel
from heatpump_optimizer.thermal_model import ThermalParameters
from heatpump_optimizer import topology
from heatpump_optimizer.wood_fuel import wood_slots_to_kw
from homeassistant.util import dt as dt_util


class _Learner(DhwProfileLearner):
    """The learner, with persistence stubbed so a cooling fold is visible."""

    def __init__(self) -> None:
        super().__init__(
            FakeHass(),
            "guard-pins",
            ThermalParameters(),
            frozen=lambda *_: None,
            heating_active=lambda: False,
            external_heat_active=lambda: False,
        )

    async def async_save_profile(self) -> None:
        return None


def _idle_cooling_learned() -> bool:
    now = datetime(2026, 1, 5, 12, 0, 0)
    dt_util.freeze(now)
    try:
        learner = _Learner()
        learner.last_temp_sample = 55.0
        learner.last_sample_time = now - timedelta(hours=1)
        learner.heating_since_sample = False
        before = learner.cooling_samples
        asyncio.run(learner.async_learn_dynamics(53.0))
        return learner.cooling_samples > before
    finally:
        dt_util.freeze(None)


def _coil_caption_present() -> bool:
    setup = topology.describe_setup(
        {
            "upper_floor_thermal_mass": 2.0,
            "mixing_valve_mode": "manual",
            "wood_tank_top_entity": "sensor.wood_top",
            "dhw_tank_volume": 200.0,
            "dhw_wood_coil_enabled": True,
        }
    )
    return "refilled through a coil in the wood tank" in topology.render_text_summary(
        setup
    )


def _aware_slot_on_naive_stamps() -> bool:
    stamps = [datetime(2026, 1, 1, hour) for hour in range(4)]
    start = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 3, tzinfo=timezone.utc)
    try:
        kw = wood_slots_to_kw(
            [{"start": start.isoformat(), "end": end.isoformat(), "liters": 50.0}],
            stamps,
            1.0,
            "birch",
            "packed",
            75.0,
        )
    except TypeError:
        return False
    return kw[0] == 0.0 and kw[1] > 0.0 and kw[2] > 0.0 and kw[3] == 0.0


def _spike_rail_holds() -> bool:
    """A 10-to-1 day is a data-error spike; the rail must flatten it.

    After the profile is re-normalised to mean 1, a rail of 3 leaves the
    peak/floor near 4; doubling the rail leaves it near 8. Five sits
    between those and does not name the constant.
    """
    model = PriceShapeModel()
    if not model.observe_day(datetime(2026, 1, 5), [1.0] * 23 + [10.0]):
        return False
    peak, floor = max(model.shapes[0]), min(model.shapes[0])
    return floor > 0.0 and peak / floor < 5.0


def main() -> int:
    R = Results("Guard pins (#805 non-coordinator)")
    R.check(
        "an idle interval teaches the tank cooling rate",
        _idle_cooling_learned(),
        "async_learn_cooling must run when the tank was not heated",
    )
    R.check(
        "a wood-coil install captions the hot-water tank",
        _coil_caption_present(),
    )
    R.check(
        "a tz-aware wood slot against naive stamps still places energy",
        _aware_slot_on_naive_stamps(),
        "aware-vs-naive comparison raises unless the stamp is stripped",
    )
    R.check(
        "a tenfold hour does not remain tenfold in the learned shape",
        _spike_rail_holds(),
        "the rail must flatten a data-error spike",
    )
    return R.close("GUARD PIN CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
