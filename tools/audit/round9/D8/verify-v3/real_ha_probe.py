#!/usr/bin/env python3
"""D8 verifier V3 (round 9): reachability of D8-s1-01, D8-s2-01/02/03 in REAL Home Assistant.

METRIC (one line each; every count is taken off the real HA state machine or
real HA service dispatch, never off tests/hastub):
  s1_01_wrong_quarters     of 96 instants (7 min into each quarter of a Stockholm
                           day, real homeassistant.util.dt), how often production
                           HeatPumpOptimizerCoordinator._current_spot_price returns a
                           price other than the entry whose [start, next start) holds
                           now; rows built by production prices_from_entity_state
                           from a 96-row Nord Pool raw_today (the entity source).
  s2_01_calls_reaching     of 3 climate service calls (set_hvac_mode off,
                           set_temperature 22, turn_off) dispatched through real
                           hass.services.async_call, how many reach the entity,
                           with no indoor reading (reading_ok False); state string.
  s2_02_hvac_action        real state machine hvac_action while the payload says mode
                           off and the action says heat_pump_on True at 5 kW.
  s2_03_split_writes       of 4 mode transitions (climate off, climate auto, switch
                           off, switch on) dispatched as real services, how many leave
                           a real state-machine state whose live mode field disagrees
                           with a payload-mode field before the refresh lands.
COMMAND (repository root; the shim only re-adds typing.ByteString, which
  mashumaro in this HA venv still reads on CPython 3.14.0rc2, and appends the
  suite venv's site-packages for numpy/scipy):
  PYTHONPATH=tools/audit/round9/D8/verify-v3/hashim /home/claude/havenv/bin/python \
      tools/audit/round9/D8/verify-v3/real_ha_probe.py [--perturb]
  --perturb: reading_ok True (s2-01 -> 3 of 3), payload mode read live (s2-02 ->
  heating, s2-03 -> 0), entries cover [start, next start) (s1-01 -> 0).
EXPECTED at baseline 1936d5ca (exact): s1_01=95, s2_01 calls_reaching=0 state
  unavailable, s2_02 hvac_action=off, s2_03 split_writes=4 (3 is also a pass if
  the reverse direction is consistent); perturbed: 0, 3, heating, 0.
MACHINE: G2-V3 cloud container, 4 CPU, CPython 3.14.0rc2, homeassistant 2026.2.3.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import sys
import tempfile
import time
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, "custom_components")
PERTURB = "--perturb" in sys.argv

import homeassistant.const as ha_const  # noqa: E402
from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.helpers import entity_registry as er, device_registry as dr  # noqa: E402
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator  # noqa: E402
from homeassistant.helpers.device_registry import DeviceInfo  # noqa: E402

assert "hastub" not in (ha_const.__file__ or ""), ha_const.__file__
print(f"INFO homeassistant {ha_const.__version__} from {os.path.dirname(ha_const.__file__)}")

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import climate as climate_mod  # noqa: E402
from heatpump_optimizer import switch as switch_mod  # noqa: E402
from heatpump_optimizer import price_model  # noqa: E402

TZ = "Europe/Stockholm"
REFRESH_DELAY = 1.0  # the fake coordinator's refresh time; a real one is the cycle


def s1_01() -> int:
    dt_util.set_default_time_zone(dt_util.get_time_zone(TZ))
    day = datetime(2026, 1, 15, tzinfo=dt_util.get_time_zone(TZ))
    raw = []
    for q in range(96):
        start = day + timedelta(minutes=15 * q)
        raw.append({"start": start.isoformat(), "end": (start + timedelta(minutes=15)).isoformat(),
                    "value": round(0.5 + 0.01 * q, 4)})
    state = SimpleNamespace(state="0.5", attributes={"raw_today": raw, "raw_tomorrow": []})
    rows = price_model.prices_from_entity_state(state, 1.0, 0.0)
    assert not isinstance(rows, str), rows
    print(f"INFO entity rows parsed={len(rows)} (15-minute rows kept, not resampled)")
    print(f"INFO tibber quarter query asks QUARTER_HOURLY: "
          f"{'QUARTER_HOURLY' in str(price_model.TIBBER_PRICE_QUERY_QUARTER)}")
    starts = [datetime.fromisoformat(r["starts_at"]) for r in rows]
    fake = SimpleNamespace(_prices=rows)
    wrong = 0
    for q in range(96):
        now = day + timedelta(minutes=15 * q + 7)
        want = rows[max(i for i, s in enumerate(starts) if s <= now)]["total"]
        with mock.patch.object(coord_mod.dt_util, "now", return_value=now):
            if PERTURB:
                got = next(r["total"] for i, r in enumerate(rows)
                           if starts[i] <= now < (starts[i + 1] if i + 1 < len(starts) else starts[i] + timedelta(minutes=15)))
            else:
                got = coord_mod.HeatPumpOptimizerCoordinator._current_spot_price(fake)
        wrong += abs(got - want) > 1e-9
    return wrong


class Coord(DataUpdateCoordinator):
    def __init__(self, hass, flag, mode):
        super().__init__(hass, logging.getLogger("d8v3"), name="d8v3", update_interval=None,
                         config_entry=None)
        self.mode = mode
        self.target_temperature = 21.0
        self.device_info = DeviceInfo(identifiers={("heatpump_optimizer", "d8v3")}, name="Heat Pump Optimizer")
        self.calls: list[str] = []
        self.data = {
            "mode": mode,
            "current_action": {"heat_pump_on": True, "power": 5.0, "power_normalized": 1.0, "mode": "boost"},
            "reading_ok": {"upper_floor_temperature": flag},
            "indoor_temperature": 21.3,
            "upper_floor_temperature": 21.3,
        }

    async def async_set_mode(self, mode, *, refresh=True):
        self.calls.append(f"mode:{mode}")
        self.mode = mode

    async def async_set_target_temperature(self, t):
        self.calls.append(f"target:{t}")

    def record_setpoint_override(self, *a, **k):
        pass

    async def async_publish_current_action(self, *a, **k):
        pass

    async def _async_update_data(self):
        await asyncio.sleep(REFRESH_DELAY)
        return {**self.data, "mode": self.mode,
                "current_action": {**self.data["current_action"],
                                   "heat_pump_on": self.mode != "off",
                                   "power": 5.0 if self.mode != "off" else 0.0}}


async def real_ha() -> dict:
    out: dict = {}
    tmp = tempfile.mkdtemp(prefix="d8v3_ha_")
    hass = HomeAssistant(tmp)
    await hass.config.async_set_time_zone(TZ)
    await er.async_load(hass)
    await dr.async_load(hass)
    from homeassistant.helpers import area_registry as ar, floor_registry as fr, label_registry as lr
    for reg in (ar, fr, lr):
        if hasattr(reg, "async_load"):
            await reg.async_load(hass)
    from homeassistant.components import climate as ha_climate, switch as ha_switch
    await ha_climate.async_setup(hass, {})
    await ha_switch.async_setup(hass, {})
    comp_c = hass.data[ha_climate.DATA_COMPONENT]
    comp_s = hass.data[ha_switch.DATA_COMPONENT]

    def entry(eid):
        return SimpleNamespace(
            entry_id=eid, data={}, options={},
            async_create_background_task=lambda h, coro, name: h.async_create_background_task(coro, name),
        )

    # ---- s2-01: no indoor reading
    c1 = Coord(hass, PERTURB, "auto")
    e1 = climate_mod.HeatPumpOptimizerClimate(c1, entry("e1"))
    e1.entity_id = "climate.d8v3_nothermo"
    await comp_c.async_add_entities([e1])
    await hass.async_block_till_done()
    st = hass.states.get(e1.entity_id)
    out["s2_01_state"] = st.state
    out["s2_01_attr_count"] = len(st.attributes)
    for svc, data in (("set_hvac_mode", {"hvac_mode": "off"}),
                      ("set_temperature", {"temperature": 22}),
                      ("turn_off", {})):
        try:
            await hass.services.async_call("climate", svc, {"entity_id": e1.entity_id, **data}, blocking=True)
        except Exception as err:  # noqa: BLE001
            print(f"INFO s2-01 {svc} raised {type(err).__name__}: {err}")
    await hass.async_block_till_done()
    out["s2_01_calls_reaching"] = len(c1.calls)

    # ---- s2-02: payload mode off, boost action runs the pump
    c2 = Coord(hass, True, "off")
    c2.data = {**c2.data, "mode": "off"}
    if PERTURB:
        c2.data["mode"] = "auto"  # the live-action read, emulated: mode label not consulted
    e2 = climate_mod.HeatPumpOptimizerClimate(c2, entry("e2"))
    e2.entity_id = "climate.d8v3_boost_off"
    await comp_c.async_add_entities([e2])
    await hass.async_block_till_done()
    st = hass.states.get(e2.entity_id)
    out["s2_02_state"] = st.state
    out["s2_02_hvac_action"] = st.attributes.get("hvac_action")

    # ---- s2-03: mode transitions through real services
    c3 = Coord(hass, True, "auto")
    e3 = climate_mod.HeatPumpOptimizerClimate(c3, entry("e3"))
    e3.entity_id = "climate.d8v3_modes"
    e3._async_publish_displace_from_current_action = lambda *a, **k: asyncio.sleep(0)
    s3 = switch_mod.OptimizerEnableSwitch(c3, entry("e3"))
    s3.entity_id = "switch.d8v3_active"
    await comp_c.async_add_entities([e3])
    await comp_s.async_add_entities([s3])
    await hass.async_block_till_done()
    if PERTURB:
        # payload-mode readers read the live mode (the finder's --perturb-live-mode)
        orig_ha = climate_mod.HeatPumpOptimizerClimate.hvac_action.fget
        def live_action(self):
            saved = self.coordinator.data
            self.coordinator.data = {**saved, "mode": self.coordinator.mode}
            try:
                return orig_ha(self)
            finally:
                self.coordinator.data = saved
        climate_mod.HeatPumpOptimizerClimate.hvac_action = property(live_action)
        switch_mod.OptimizerEnableSwitch.extra_state_attributes = property(
            lambda self: {"mode": self.coordinator.mode})

    def split(ent_id):
        st = hass.states.get(ent_id)
        if ent_id.startswith("climate."):
            return (st.state == "off") != (st.attributes.get("hvac_action") == "off"), (st.state, st.attributes.get("hvac_action"))
        return (st.state == "on") == (st.attributes.get("mode") == "off"), (st.state, st.attributes.get("mode"))

    splits = 0
    windows = []
    for domain, svc, data, ent in (
        ("climate", "set_hvac_mode", {"hvac_mode": "off"}, e3.entity_id),
        ("climate", "set_hvac_mode", {"hvac_mode": "auto"}, e3.entity_id),
        ("switch", "turn_off", {}, s3.entity_id),
        ("switch", "turn_on", {}, s3.entity_id),
    ):
        t0 = time.monotonic()
        await hass.services.async_call(domain, svc, {"entity_id": ent, **data}, blocking=True)
        bad, snap = split(ent)
        splits += bad
        # wait for the background refresh to land and the state to agree
        while split(ent)[0] and time.monotonic() - t0 < 30:
            await asyncio.sleep(0.05)
        windows.append(round(time.monotonic() - t0, 2))
        print(f"INFO s2-03 {domain}.{svc}{data}: immediate write {snap} split={bad}; consistent after {windows[-1]} s")
        await asyncio.sleep(0.1)
    out["s2_03_split_writes"] = splits
    out["s2_03_windows_s"] = windows
    await hass.async_stop(force=True)
    return out


def main() -> int:
    t0p, t0t = time.process_time(), time.thread_time()
    n = s1_01()
    print(f"RESULT s1_01_wrong_quarters={n} count (of 96)")
    res = asyncio.run(real_ha())
    print(f"RESULT s2_01_state={res['s2_01_state']} state")
    print(f"RESULT s2_01_attr_count={res['s2_01_attr_count']} count")
    print(f"RESULT s2_01_calls_reaching={res['s2_01_calls_reaching']} count (of 3)")
    print(f"RESULT s2_02_hvac_action={res['s2_02_hvac_action']} state (climate state {res['s2_02_state']})")
    print(f"RESULT s2_03_split_writes={res['s2_03_split_writes']} count (of 4)")
    print(f"RESULT s2_03_windows={res['s2_03_windows_s']} s (fake refresh delay {REFRESH_DELAY} s)")
    pt, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            sw = next(int(l.split()[1]) for l in f if l.startswith("pswpin"))
    except Exception:  # noqa: BLE001
        sw = 0
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
