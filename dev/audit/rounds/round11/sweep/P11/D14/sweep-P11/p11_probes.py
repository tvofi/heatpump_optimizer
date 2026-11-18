#!/usr/bin/env python3
"""Round-11 class sweep P11: probes for the write-record seams beyond D16-s1-05.

  PYTHONPATH=tests/hastub:. python3 p11_probes.py [--double fake] [--perturb]

Each arm drives one production writer through a services double that behaves as Home
Assistant's entity service call does (homeassistant/helpers/service.py
entity_service_call skips an entity that is not available: no error, no write), with
the target unavailable on the first cycle and available again on the next. It counts
writes the writer booked as made that never reached the entity AND were not re-sent
once the entity came back (a lost command).

  --double fake   the null: the double behaves as tests/harness.py:FakeServices does
                  (every call lands), so no write is lost -> 0.
  --perturb       each writer is wrapped so it returns before the call when the target
                  reads 'unavailable' (the fix shape D16-s1-05's --perturb applies) -> 0.

Arms: set_pump   coordinator.HeatPumpOptimizerCoordinator._async_set_pump (homeassistant.turn_on)
      frequency  coordinator.HeatPumpOptimizerCoordinator._command_frequency (number.set_value)
      valve      coordinator.HeatPumpOptimizerCoordinator._command_valve_target (write_setpoint_c)
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from custom_components.heatpump_optimizer import coordinator as co_mod
from custom_components.heatpump_optimizer.freq_control import FrequencyWatchdog


class States:
    def __init__(self):
        self.s = {}

    def get(self, eid):
        v = self.s.get(eid)
        return None if v is None else SimpleNamespace(state=v, attributes={})


class Services:
    """HA's entity-service skip (ha=True) or FakeServices' land-everything (ha=False)."""

    def __init__(self, states, ha=True):
        self.states, self.ha, self.landed = states, ha, []

    async def async_call(self, domain, service, data, blocking=False, **_):
        eid = data.get("entity_id")
        st = self.states.get(eid)
        if self.ha and st is not None and st.state == "unavailable":
            return None
        self.landed.append((domain, service, dict(data)))
        return None


def _hass(ha):
    states = States()
    return SimpleNamespace(states=states, services=Services(states, ha))


def _skip_unavailable(fn, eid_of):
    async def wrapped(self, *a, **k):
        st = self.hass.states.get(eid_of(self, *a))
        if st is not None and st.state == "unavailable":
            return None
        return await fn(self, *a, **k)
    return wrapped


async def arm_set_pump(ha, perturb):
    C = co_mod.HeatPumpOptimizerCoordinator
    fn = C._async_set_pump
    if perturb:
        fn = _skip_unavailable(fn, lambda self, eid, *_: eid)
    c = C.__new__(C)
    c.hass = _hass(ha)
    c._pump_commanded, c._mode = {}, "auto"
    eid = "switch.circ_pump"
    c.hass.states.s[eid] = "unavailable"
    await fn(c, eid, True, "probe cycle 1")
    c.hass.states.s[eid] = "off"
    await fn(c, eid, True, "probe cycle 2")
    turned_on = any(s == "turn_on" for _, s, _d in c.hass.services.landed)
    return 0 if turned_on else 1


async def arm_frequency(ha, perturb):
    C = co_mod.HeatPumpOptimizerCoordinator
    fn = C._command_frequency
    eid = "number.compressor_hz"
    if perturb:
        fn = _skip_unavailable(fn, lambda self, *_: eid)
    c = C.__new__(C)
    c.hass = _hass(ha)
    c._ctx = SimpleNamespace(_config=SimpleNamespace(compressor_freq_entity=eid))
    c._freq_mode = lambda: co_mod.FREQ_MODE_CONTROL
    c._mode = "auto"
    c._freq_entity_reading = lambda: (None, 20.0, 90.0, "probe")
    c._freq_map = SimpleNamespace(recommend=lambda *_: 55.0)
    c._commanded_power = lambda: 3.0
    c._freq_last_write = None
    c._freq_watchdog = FrequencyWatchdog()
    t0 = dt_util.now()
    c.hass.states.s[eid] = "unavailable"
    orig_now = dt_util.now
    try:
        dt_util.now = lambda *_a, **_k: t0
        await fn(c)
        c.hass.states.s[eid] = "40.0"
        dt_util.now = lambda *_a, **_k: t0 + timedelta(minutes=30)
        await fn(c)
    finally:
        dt_util.now = orig_now
    landed = [d for d in c.hass.services.landed if d[2].get("value") == 55.0]
    return 0 if landed else 1


async def arm_valve(ha, perturb):
    from custom_components.heatpump_optimizer import mixing_valve
    C = co_mod.HeatPumpOptimizerCoordinator
    fn = C._command_valve_target
    eid = "number.valve_target"
    if perturb:
        fn = _skip_unavailable(fn, lambda self, *_: eid)
    c = C.__new__(C)
    c.hass = _hass(ha)
    params = SimpleNamespace(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE, mixing_valve_target=21.0,
                             comfort_ceiling=22.0, two_zone_enabled=False)
    cfg = SimpleNamespace(mixing_valve_write_entity=eid, mixing_valve_write_target_kind="indoor")
    c._ctx = SimpleNamespace(_thermal_params=params, _config=cfg)
    c._mode, c._current_action, c._valve_commanded_target = "auto", None, None
    c.hass.states.s[eid] = "unavailable"
    await fn(c)
    c.hass.states.s[eid] = "20.0"
    await fn(c)
    landed = [d for d in c.hass.services.landed if d[2].get("entity_id") == eid]
    return 0 if landed else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--double", choices=["ha", "fake"], default="ha")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    ha = a.double == "ha"
    for name, arm in (("set_pump", arm_set_pump), ("frequency", arm_frequency), ("valve", arm_valve)):
        print(f"RESULT {name}_lost_command={asyncio.run(arm(ha, a.perturb))} (double={a.double}, perturb={a.perturb})")


if __name__ == "__main__":
    main()
