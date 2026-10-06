"""D1-s3-02 queued window: apply waiting on held.lock when unload or Off happens.

The suite's latch-before-apply check stays green if ArbiterInputs is snapshotted
before those waits. This file is the window the guard's comment names.

    PYTHONPATH=tests/hastub:tests python3 tools/audit/harnesses/d1_s3_02_queued_apply.py
"""
from __future__ import annotations

import asyncio
import itertools
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeHass, FakeState
from homeassistant.util import dt as dt_util

from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer.const import MODE_AUTO, MODE_OFF

T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
IDS = itertools.count()


def _plan(duties):
    return NS(
        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(len(duties))],
        power_schedule=[1.5 if c in "sb" else 0.0 for c in duties],
        dhw_power_schedule=[2.0 if c in "db" else 0.0 for c in duties],
        optimal_setpoints=[21.0 for _ in duties],
    )


class _Coord:
    def __init__(self, duties="dds-"):
        self.hass = FakeHass({
            "select.pump_mode": FakeState("Heating + DHW", attributes={"options": list(TUYA)}),
            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
        })
        self._config = {
            "pump_duty_mode": "control",
            "heat_pump_mode_entity": "select.pump_mode",
            "dhw_setpoint_entity": "number.dhw_set",
            "space_setpoint_entity": "number.water_set",
            "space_setpoint_unit": "flow",
        }
        self._mode = MODE_AUTO
        self.stale = False
        self._current_action = {"mode": "eco"}
        self._optimization_result = _plan(duties)
        self._thermal_model = NS(
            params=NS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2)
        self._thermal_params = NS(dhw_setpoint=48.0)
        self._current_state = NS(outdoor_temperature=2.0)
        self.entry = NS(entry_id=f"rq{next(IDS)}")
        self._entry_released = False

    def _plan_is_stale(self):
        return self.stale

    @property
    def effective_config(self):
        return self._config

    @property
    def thermal_params(self):
        return self._thermal_params

    def arbiter_inputs(self):
        return pa.ArbiterInputs(
            hass=self.hass, config=self._config, mode=self._mode,
            plan=self._optimization_result, plan_stale=self.stale,
            entry_released=getattr(self, "_entry_released", False),
            state=self._current_state, thermal=self._thermal_model,
            params=self._thermal_params, action=self._current_action,
            measured_power_kw=getattr(self, "_measured_power", None),
            disinfecting=False,
        )

    async def async_set_mode(self, mode):
        self._mode = mode

    def writes(self):
        return [(d, s, (data or {}).get("option", (data or {}).get("value")))
                for d, s, data in self.hass.services.calls]


async def queued(arm):
    coord = _Coord()
    await pa.apply(coord, T0 + timedelta(minutes=1))
    held = pa.state_for(coord)
    await held.lock.acquire()
    task = asyncio.ensure_future(pa.apply(coord, T0 + timedelta(minutes=16)))
    for _ in range(5):
        await asyncio.sleep(0)
    if arm == "unload":
        coord._entry_released = True
        await pa.release(coord)
    elif arm == "off":
        await coord.async_set_mode(MODE_OFF)
    coord.hass.services.calls.clear()
    held.lock.release()
    await task
    return len(held.unsubs), len(coord.writes())


def main():
    dt_util.freeze(T0 + timedelta(minutes=10))
    try:
        for arm in ("unload", "off", "null"):
            listeners, writes = asyncio.run(queued(arm))
            print(f"RESULT queued_apply arm={arm} listeners_armed={listeners} writes_after={writes}")
    finally:
        dt_util.freeze(None)


if __name__ == "__main__":
    main()
