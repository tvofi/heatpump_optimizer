#!/usr/bin/env python3
"""ARCH3-s6 (round 10, D7): does the pump-duty arbiter write a set-point in the unit it reads it in?

Two owners of one rule. ``setpoint_check._setpoint_and_unit`` (#1513) reads a climate set-point
entity's target from its ``temperature`` attribute in the INSTANCE's unit system, and the DHW
repair flow writes in that same unit. ``pump_arbiter._write`` converts with
``temperature_from_c(value, state_unit(state))`` -- the entity's ``unit_of_measurement``, which a
climate entity does not carry -- so on a degF instance it writes degC digits to a degF target.

Metric:   roundtrip_error_K = |read_back_C - commanded_C| after the arbiter commands 55.0 degC to
          the DHW set-point slot and the fake entity adopts the written value; read back through
          the package's own set-point reader. Summed over the cases of one arm.
Arms:     defect  -- climate.dhw on a degF instance (attribute target, no unit_of_measurement)
          null    -- climate.dhw on a degC instance, and number.dhw declaring degF: both must read
                     0.0 on every tree (the conversion is exercised, only the climate rule differs)
Instrumented symbols: pump_arbiter._write (driven), the package set-point reader
          (setpoint_check._read_setpoint on main, inputs.read_setpoint once P2 lands).
Command:  PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round10/D7/arch3-s6/setpoint_unit.py
Perturbation: the tree. Expected origin/main d749c986d: defect 42.222 K (55 written as 55 degF =
          12.78 degC), null 0.000; with P2: defect 0.000, null 0.000 (expected_direction to_zero).
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path[:0] = ["tests/hastub", "tests", "custom_components"]

from harness import FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import pump_arbiter as pa  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

try:
    from heatpump_optimizer.inputs import read_setpoint  # P2
except ImportError:
    from heatpump_optimizer.setpoint_check import _read_setpoint as read_setpoint  # main


class _Coord(SimpleNamespace):
    """A weak-referenceable coordinator stand-in (the arbiter keys its state weakly)."""

    __hash__ = object.__hash__


def roundtrip(entity: str, state: FakeState, instance_unit: str) -> float:
    hass = FakeHass({entity: state})
    hass.config.units = SimpleNamespace(temperature_unit=instance_unit)
    cfg = EntryConfig.from_mapping({"pump_duty_mode": "control", "dhw_setpoint_entity": entity})
    coord = _Coord(hass=hass, entry=SimpleNamespace(entry_id=f"s6{id(hass)}"))
    inp = SimpleNamespace(hass=hass, config=cfg)
    now = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
    asyncio.run(pa._write(coord, inp, "dhw_setpoint", 55.0, now))
    calls = [c for c in hass.services.calls if (c[2] or {}).get("entity_id") == entity]
    if not calls:
        return float("nan")
    data = calls[-1][2]
    written = data.get("temperature", data.get("value"))
    if entity.startswith("climate."):
        state.attributes["temperature"] = written
    else:
        state.state = str(written)
    back = read_setpoint(hass, entity)
    return abs(float(back) - 55.0)


def main() -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    defect = roundtrip("climate.dhw", FakeState("heat", attributes={"temperature": 122.0}), "°F")
    null = (roundtrip("climate.dhw", FakeState("heat", attributes={"temperature": 50.0}), "°C")
            + roundtrip("number.dhw", FakeState("122", unit="°F"), "°C"))
    print(f"RESULT roundtrip_error_defect_K={defect:.3f}")
    print(f"RESULT roundtrip_error_null_K={null:.3f}")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
