#!/usr/bin/env python3
"""Lost writes: a command booked as made while Home Assistant skipped it (class P11).

WHY IT EXISTS. Round 11's P11 probe (`dev/audit/rounds/round11/sweep/P11/D14/sweep-P11/p11_probes.py`)
drives each step-derived writer at an unavailable target, then at the same target available again,
and counts a command the writer booked as made that never reached the entity and was not sent again.
Its pump arm names `_async_set_pump`, which R11-SEAM-actuation-release moved to
`circulation.command`, and its valve arm sets `_valve_commanded_target`, which that group replaced by
`mixing_valve.ValveTarget`; so at main the probe raises before its valve arm. This is the port, each
arm driving the writer main has, with the same double and the same null.

    PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/r11_actuation_lost_writes.py [--double fake]

`--double ha` (default) skips a call to an unavailable entity, as Home Assistant's entity service call
does (`homeassistant/helpers/service.py` `entity_service_call`); `--double fake` lands every call, as
`tests/harness.py`'s `FakeServices` did, the null: no command can be lost, so every arm reads 0.
Each arm prints `RESULT <arm>_lost_command=<0|1>`; the exit status is the sum.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from custom_components.heatpump_optimizer import circulation, mixing_valve
from custom_components.heatpump_optimizer import coordinator as co_mod
from custom_components.heatpump_optimizer.freq_control import FrequencyWatchdog


class States:
    def __init__(self):
        self.s = {}

    def get(self, eid):
        v = self.s.get(eid)
        return None if v is None else SimpleNamespace(state=v, attributes={})


class Services:
    """Home Assistant's entity-service skip (``ha``) or a double that lands every call."""

    def __init__(self, states, ha=True):
        self.states, self.ha, self.landed = states, ha, []

    async def async_call(self, domain, service, data, blocking=False, **_):
        st = self.states.get(data.get("entity_id"))
        if self.ha and st is not None and st.state == "unavailable":
            return None
        self.landed.append((domain, service, dict(data)))
        return None


def _hass(ha):
    states = States()
    return SimpleNamespace(states=states, services=Services(states, ha))


class _Entry:
    """A weak-referenceable config entry: ``circulation`` keys its record on it."""


async def arm_set_pump(ha):
    hass, entry, eid = _hass(ha), _Entry(), "switch.vvc_pump"
    config = {"vvc_pump_entity": eid}
    hass.states.s[eid] = "unavailable"
    await circulation.command(hass, entry, config, circulation.DHW, True, "probe cycle 1")
    hass.states.s[eid] = "off"
    await circulation.command(hass, entry, config, circulation.DHW, True, "probe cycle 2")
    return 0 if any(s == "turn_on" for _d, s, _x in hass.services.landed) else 1


def _bare(cls, ha):
    c = cls.__new__(cls)
    c.hass, c.entry, c._mode = _hass(ha), _Entry(), "auto"
    c._plan_is_stale = lambda: False
    return c


async def _armed(*_a, **_k):
    return True


async def arm_frequency(ha):
    c, eid = _bare(co_mod.HeatPumpOptimizerCoordinator, ha), "number.compressor_hz"
    c._ctx = SimpleNamespace(_config=SimpleNamespace(compressor_freq_entity=eid))
    c._freq_mode = lambda: co_mod.FREQ_MODE_CONTROL
    c._freq_entity_reading = lambda: (None, 20.0, 90.0, "probe")
    c._freq_map = SimpleNamespace(recommend=lambda *_: 55.0)
    c._commanded_power = lambda: 3.0
    c._freq_last_write, c._freq_watchdog = None, FrequencyWatchdog()
    t0, orig_now, orig_arm = dt_util.now(), dt_util.now, co_mod.off_restore.async_arm
    c.hass.states.s[eid] = "unavailable"
    try:
        co_mod.off_restore.async_arm = _armed
        dt_util.now = lambda *_a, **_k: t0
        await c._command_frequency()
        c.hass.states.s[eid] = "40.0"
        dt_util.now = lambda *_a, **_k: t0 + timedelta(minutes=30)
        await c._command_frequency()
    finally:
        dt_util.now, co_mod.off_restore.async_arm = orig_now, orig_arm
    return 0 if any(d[2].get("value") == 55.0 for d in c.hass.services.landed) else 1


async def arm_valve(ha):
    c, eid = _bare(co_mod.HeatPumpOptimizerCoordinator, ha), "number.valve_target"
    params = SimpleNamespace(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE, mixing_valve_target=21.0,
                             comfort_ceiling=22.0, two_zone_enabled=False)
    cfg = SimpleNamespace(mixing_valve_write_entity=eid, mixing_valve_write_target_kind="indoor")
    c._ctx = SimpleNamespace(_thermal_params=params, _config=cfg)
    c._current_action, c._valve_target = None, mixing_valve.ValveTarget(0.1)
    orig_arm = co_mod.off_restore.async_arm
    c.hass.states.s[eid] = "unavailable"
    try:
        co_mod.off_restore.async_arm = _armed
        await c._command_valve_target()
        c.hass.states.s[eid] = "20.0"
        await c._command_valve_target()
    finally:
        co_mod.off_restore.async_arm = orig_arm
    return 0 if any(d[2].get("entity_id") == eid for d in c.hass.services.landed) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--double", choices=["ha", "fake"], default="ha")
    a = ap.parse_args()
    lost = 0
    for name, arm in (("set_pump", arm_set_pump), ("frequency", arm_frequency), ("valve", arm_valve)):
        n = asyncio.run(arm(a.double == "ha"))
        lost += n
        print(f"RESULT {name}_lost_command={n} (double={a.double})")
    raise SystemExit(lost)


if __name__ == "__main__":
    main()
