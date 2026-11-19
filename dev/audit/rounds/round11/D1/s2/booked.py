"""D1-s2 round 11, D1.M3: the published and booked value while a metering input is missing.

Metric (one line): for the electrical power and energy meter slots
(CONF_POWER_ENTITY, CONF_ENERGY_ENTITY), across (h) healthy, (u) unavailable for
two cycles, (r) back inside one interval, the number of cycles in (u) whose
published ``measured_power`` / ``measured_power_available`` or booked
``energy_totals`` delta claim a measurement the meter did not deliver
(a measured value published while the meter is unavailable); the energy totals keep integrating the modelled draw then, printed as booked_delta_kwh for the record.
Count key: the published payload (``measured_power``, ``measured_power_available``,
``measured_energy``) and the coordinator's energy totals (``_energy_totals``), not
the planted states.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/booked.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

C = L.const
PW, EN = "sensor.hp_power", "sensor.hp_energy"


def st(v, when, unit, dc, sc=None):
    a = {"unit_of_measurement": unit, "device_class": dc}
    if sc:
        a["state_class"] = sc
    return L.FakeState(v, attributes=a, last_updated=when, last_reported=when)


def totals(coord):
    t = getattr(coord, "_energy_totals", None)
    for name in ("total_energy_kwh", "space_energy_kwh"):
        v = getattr(t, name, None)
        if v is not None:
            return float(v)
    if isinstance(t, dict):
        return float(t.get("total_energy_kwh") or 0.0)
    return None


async def run(out):
    hass = L.SchedHass(L.base_states())
    cfg = L.base_config({C.CONF_POWER_ENTITY: PW, C.CONF_ENERGY_ENTITY: EN})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    plan = [("h", 0, "1500", "1000.0"), ("h", 15, "1500", "1000.4"), ("u", 30, "unavailable", "unavailable"),
            ("u", 45, "unavailable", "unavailable"), ("r", 60, "1500", "1001.5"), ("r", 75, "1500", "1001.9")]
    claims = 0
    prev = None
    for tag, m, pw, en in plan:
        now = L.T0 + timedelta(minutes=m)
        L.dtu.freeze(now)
        for k, v in L.base_states().items():
            hass.states.set(k, L.FakeState(v.state, last_updated=now, last_reported=now))
        hass.states.set(PW, st(pw, now, "W", "power"))
        hass.states.set(EN, st(en, now, "kWh", "energy", "total_increasing"))
        d = await coord._async_update_data()
        await L.drain(hass)
        tot = totals(coord)
        booked = None if (tot is None or prev is None) else round(tot - prev, 4)
        prev = tot
        mp, avail, me = d.get("measured_power"), d.get("measured_power_available"), d.get("measured_energy")
        print(f"BOOK {tag} t+{m}min: measured_power={mp} available={avail} measured_energy={str(me)[:60]} booked_delta_kwh={booked}")
        if tag == "u" and (mp is not None or avail or me is not None):
            claims += 1
    out["unavailable_cycles_claiming_measurement"] = claims
    await coord.async_shutdown()
    await L.drain(hass, 5)


def main():
    proc0, thr0 = time.process_time(), time.thread_time()
    out = {}
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    try:
        asyncio.run(run(out))
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
