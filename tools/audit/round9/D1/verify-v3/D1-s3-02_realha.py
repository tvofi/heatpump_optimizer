"""V3 reach for D1-s3-02 (pump-duty arbiter re-arms its listeners on an unloaded coordinator) under real HA.

Metric: live arbiter registrations (production pump_arbiter._listen's calls into the
REAL async_track_time_interval / async_track_state_change_event, recorded by a
pass-through wrapper, whose unsub has not been called) after the REAL coordinator's
async_shutdown on a real hass and a drained loop; plus pump writes (real
select.select_option / number.set_value service calls, counted by registered
handlers that also set the state) issued after the unload when each live tick
callback fires once. Pump state changes are real hass.states.async_set calls, so
real HA's event bus dispatches pump_arbiter._changed and real hass.async_create_task
(eager_start=True in HA >= 2024.x) runs apply().
Arms: default -- the finder's sequence (a pump state change, one loop iteration for real
HA to dispatch it, then the unload; lock free); --lock-held -- the same, but an
arbitration pass holds the arbiter lock when the state change is dispatched and
releases it after the unload; --slow-device -- no manual lock: the pump's service
calls take 0.3 s, a real arbitration pass is started as a task (its own writes
dispatch state changes into _changed while it holds the lock) and the unload lands
--unload-at seconds (default 0.45, after its first write, during its second) into it; --null -- no state change, lock free. Count key: the recorded registrations' unsub state.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-02_realha.py [--lock-held|--slow-device [--unload-at 0.45]|--null]
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
from datetime import timedelta
from unittest import mock

logging.disable(logging.CRITICAL)
LOCK = "--lock-held" in sys.argv
SLOW = "--slow-device" in sys.argv
UNLOAD_AT = float(sys.argv[sys.argv.index("--unload-at") + 1]) if "--unload-at" in sys.argv else 0.45
NULL = "--null" in sys.argv
REGS = []
WRITES = []


async def main():
    hass = await make_hass()
    from homeassistant.core import callback
    from heatpump_optimizer import pump_arbiter
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import MODE_AUTO
    real_ti, real_sc = pump_arbiter.async_track_time_interval, pump_arbiter.async_track_state_change_event

    def wrap(real, kind):
        def _w(h, *a, **k):
            unsub = real(h, *a, **k)
            rec = {"kind": kind, "action": a[0] if kind == "interval" else a[1], "live": True}
            REGS.append(rec)

            def _u():
                rec["live"] = False
                unsub()
            return _u
        return _w

    opts = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]
    hass.states.async_set("sensor.indoor", "21.4", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.outdoor", "-3.0", {"unit_of_measurement": "°C"})
    hass.states.async_set("select.pump_mode", "Heating + DHW", {"options": opts})
    hass.states.async_set("number.dhw_set", "40", {"min": 40, "max": 63, "unit_of_measurement": "°C"})
    hass.states.async_set("number.water_set", "25", {"min": 25, "max": 63, "unit_of_measurement": "°C"})

    async def sel(call):
        if SLOW:
            await asyncio.sleep(0.3)
        WRITES.append(("select", call.data.get("option")))
        hass.states.async_set(call.data["entity_id"], call.data["option"], {"options": opts})

    async def num(call):
        if SLOW:
            await asyncio.sleep(0.3)
        WRITES.append(("number", call.data.get("value")))
        st = hass.states.get(call.data["entity_id"])
        hass.states.async_set(call.data["entity_id"], str(call.data["value"]), dict(st.attributes))
    hass.services.async_register("select", "select_option", sel)
    hass.services.async_register("number", "set_value", num)
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
           "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
           "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0}
    with mock.patch.object(pump_arbiter, "async_track_time_interval", wrap(real_ti, "interval")), \
         mock.patch.object(pump_arbiter, "async_track_state_change_event", wrap(real_sc, "state")):
        coord = HeatPumpOptimizerCoordinator(hass, make_entry(cfg, entry_id="d1s3_unload"))
        coord._mode = MODE_AUTO
        await asyncio.sleep(0.1)
        await pump_arbiter.apply(coord)
        await asyncio.sleep(0.05)
        armed = sum(r["live"] for r in REGS)
        held = pump_arbiter.state_for(coord)
        if LOCK:
            await held.lock.acquire()
        pass_task = None
        if SLOW:
            # The pass must write: the pump reports its own defaults and the ownership
            # record is empty (a restart after the pump reset), so all three slots are written.
            hass.states.async_set("number.dhw_set", "40", {"min": 40, "max": 63, "unit_of_measurement": "°C"})
            hass.states.async_set("number.water_set", "25", {"min": 25, "max": 63, "unit_of_measurement": "°C"})
            hass.states.async_set("select.pump_mode", "Heating", {"options": opts})
            await asyncio.sleep(0.05)
            await held.lock.acquire(); pump_arbiter._forget(held); held.lock.release()
            n_pre = len(WRITES)
            pass_task = hass.async_create_task(pump_arbiter.apply(coord))
            await asyncio.sleep(UNLOAD_AT)
        elif not NULL:
            hass.states.async_set("select.pump_mode", "Cooling", {"options": opts})
            await asyncio.sleep(0)          # one loop iteration: real HA dispatches the event
        if SLOW:
            print(f"# writes landed before unload: {len(WRITES) - n_pre}")
        await coord.async_shutdown()
        n_at_unload = len(WRITES)
        if LOCK:
            held.lock.release()
        for _ in range(30):
            await asyncio.sleep(0.01)
        if pass_task is not None:
            await asyncio.sleep(3.0)
        live = [r for r in REGS if r["live"]]
        hass.states.async_set("select.pump_mode", "Heating", {"options": opts})
        # One tick of each live timer as HA fires it a minute later; the clock is moved
        # 2 min on (as the finder's harness does) so the arbiter's retry window has passed.
        from homeassistant.util import dt as dt_util
        _later = dt_util.now() + timedelta(minutes=2)
        with mock.patch.object(pump_arbiter.dt_util, "now", lambda *a, **k: _later):
            for r in list(live):
                if r["kind"] == "interval":
                    await r["action"](None)
        await asyncio.sleep(0.05)
        after = len(WRITES) - n_at_unload
    arm = "lock-held" if LOCK else "slow-device" if SLOW else "null" if NULL else "default"
    print(f"# arm={arm} armed_before_unload={armed} regs_total={len(REGS)}")
    print(f"RESULT live_registrations_after_unload={len(live)} count")
    print(f"RESULT writes_after_unload={after} count")

asyncio.run(main())
tail()
os._exit(0)
