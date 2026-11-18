#!/usr/bin/env python3
"""R10-FAHRENHEIT: every set-point write, counted in the unit Home Assistant reads it in.

Written by the R10-FAHRENHEIT fixer (D12-s3-01, ARCH3-s6 P2, catch-up leads L1
and L2). The finders' harnesses each read one seam through a private symbol
the fix moves (``setpoint_check._read_setpoint``, ``pump_arbiter._bounded``'s
old signature, ``_command_valve_target``'s old source), so this drives only
entry points both trees share and compares against the physical conversion,
never a reader's round trip:

- ``write_cells``: ``pump_arbiter._write`` for the two set-point slots x
  {climate, number, input_number}; a cell is wrong when the service value is
  not the intended degC in the entity's unit (a climate: the instance's; a
  number: its declared one). Arms: degF instance (6 cells), degC (6, null).
- ``no_target``: the same write to a degF climate whose target attribute is
  absent or None (2 cells): the unit is the domain's, not the reading's.
- ``valve``: ``HeatPumpOptimizerCoordinator._command_valve_target`` in
  smart_write, the comfort ceiling 23.5 degC, to a degF climate and a number
  declaring degF (2 cells), and their degC twins (2 cells, null).
- ``range``: ``pump_arbiter.desired`` for duty dhw with the dhw slot a climate
  ranged [7, 50] degC, over hot-water set-points {3, 10, 55, 70} degC: a
  command outside the range counts. Arms: degF instance (range stated as
  44.6/122 degF), degC instance; null: a number ranged min/max [7, 50] degC.

``--perturb`` (a head carrying ``inputs.setpoint_unit``) puts the old rule
back in memory -- the entity's declared unit for every domain. It moves
what the domain rule alone decides (``no_target`` and ``range_climate_degF``
back to 2 of 2 and 2 of 4); a climate whose target is present is still read
in the instance's unit by the reading's own fallback, so ``write_cells`` and
``valve`` stay 0 under it. The degC nulls stay 0 on every tree.

Expected, merge base 5603ee319: 2, 0, 2, 2, 0, 3, 3, 0 in the order printed;
the fix's head: all 0.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/r10_fahrenheit_setpoints.py [--perturb]
"""
from __future__ import annotations

import asyncio
import itertools
import sys
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path[:0] = ["tests/hastub", "tests", "custom_components"]

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import inputs, pump_arbiter  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

F, C = "°F", "°C"
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
_IDS = itertools.count()


def in_unit(value_c: float, unit: str) -> float:
    return round(value_c * 9 / 5 + 32, 1) if unit == F else value_c


class _Coord:
    """The arbiter keys its per-coordinator state weakly."""


def _hass(states: dict, instance: str) -> FakeHass:
    hass = FakeHass(states)
    hass.config.units = SimpleNamespace(temperature_unit=instance)
    return hass


def write(slot: str, entity: str, state: FakeState, instance: str, value_c: float):
    hass = _hass({entity: state}, instance)
    coord = _Coord()
    coord.hass, coord.entry = hass, SimpleNamespace(entry_id=f"f{next(_IDS)}")
    inp = SimpleNamespace(hass=hass, config={f"{slot}_entity": entity})
    asyncio.run(pump_arbiter._write(coord, inp, slot, value_c, T0))
    data = [c[2] for c in hass.services.calls if (c[2] or {}).get("entity_id") == entity]
    return data[-1].get("temperature", data[-1].get("value")) if data else None


def write_cells(instance: str) -> int:
    wrong = 0
    for slot, value_c in (("dhw_setpoint", 50.0), ("space_setpoint", 21.0)):
        want = in_unit(value_c, instance)
        got = [write(slot, f"climate.{slot}",
                     FakeState("heat", attributes={"temperature": want - 5}), instance, value_c)]
        got += [write(slot, f"{dom}.{slot}", FakeState(str(want - 5), unit=instance),
                      instance, value_c) for dom in ("number", "input_number")]
        wrong += sum(g != want for g in got)
    return wrong


def no_target() -> int:
    return sum(
        write("dhw_setpoint", "climate.dhw", FakeState("off", attributes=attrs), F, 50.0) != 122.0
        for attrs in ({}, {"temperature": None})
    )


def valve(entity: str, state: FakeState, instance: str) -> int:
    hass = _hass({entity: state}, instance)
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "max_temperature": 23.5, "mixing_valve_mode": "smart_write",
        "mixing_valve_write_entity": entity,
    }))
    asyncio.run(coord._command_valve_target())
    data = hass.services.calls[-1][2]
    unit = instance if entity.startswith("climate.") else state.attributes.get("unit_of_measurement")
    return int(data.get("temperature", data.get("value")) != in_unit(23.5, unit))


def out_of_range(entity: str, state: FakeState, instance: str) -> int:
    count = 0
    for setpoint_c in (3.0, 10.0, 55.0, 70.0):
        inp = pump_arbiter.ArbiterInputs(
            hass=_hass({entity: state}, instance),
            config=EntryConfig.from_mapping({"dhw_setpoint_entity": entity}),
            mode="auto", plan=None, plan_stale=False, entry_released=False,
            state=SimpleNamespace(outdoor_temperature=2.0), thermal=None,
            params=SimpleNamespace(dhw_setpoint=setpoint_c), action={},
            measured_power_kw=None, disinfecting=False,
        )
        command = pump_arbiter.desired(None, inp, "dhw", T0).dhw_setpoint
        count += int(command is None or not 7.0 <= command <= 50.0)
    return count


def main() -> None:
    if "--perturb" in sys.argv:
        inputs.setpoint_unit = lambda _hass, _entity, state: inputs.state_unit(state)
        print("PERTURB setpoint_unit -> the entity's declared unit for every domain")
    print(f"RESULT write_cells_degF={write_cells(F)} of 6")
    print(f"RESULT write_cells_degC_null={write_cells(C)} of 6")
    print(f"RESULT no_target_degF={no_target()} of 2")
    print("RESULT valve_degF={} of 2".format(
        valve("climate.valve", FakeState("heat", attributes={"temperature": 70.0}), F)
        + valve("number.valve", FakeState("70", unit=F), C)))
    print("RESULT valve_degC_null={} of 2".format(
        valve("climate.valve", FakeState("heat", attributes={"temperature": 21.0}), C)
        + valve("number.valve", FakeState("21", unit=C), C)))
    ranged = {"min_temp": 44.6, "max_temp": 122.0}
    print(f"RESULT range_climate_degF={out_of_range('climate.dhw', FakeState('heat', attributes=ranged), F)} of 4")
    print("RESULT range_climate_degC={} of 4".format(out_of_range(
        "climate.dhw", FakeState("heat", attributes={"min_temp": 7, "max_temp": 50}), C)))
    print("RESULT range_number_degC_null={} of 4".format(out_of_range(
        "number.dhw", FakeState("45", unit=C, attributes={"min": 7, "max": 50}), C)))


if __name__ == "__main__":
    main()
