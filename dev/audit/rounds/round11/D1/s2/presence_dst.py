"""D1-s2 round 11, D1.M3: presence changing between updates; the age readings under DST and clock jumps.

Metric (one line): (A) of presence/holiday changes fired between two
scheduled updates through the listener ``away.watch_away_inputs`` registers,
how many request no refresh, or leave the next cycle's published
``away_active`` at the old meaning; (B) over DST spring/autumn steps in
Europe/Stockholm and host-clock jumps (-2 h, +3 h), how many published age
readings (``input_ages_minutes`` of a probe that last reported before the
step, ``plan_age_minutes``, ``weather_forecast_stale_hours``) are negative or
differ from the true elapsed time by more than 1 minute.
Count key: the coordinator's published payload and the refresh callable the
production listener calls, never the planted states.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/presence_dst.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

C = L.const
PRES = "binary_sensor.home_occupied"
CAL = "calendar.holiday"
PROBE = "sensor.tank"
OCC = {"device_class": "occupancy"}  # on = somebody home


def st(state, when, attrs=None):
    return L.FakeState(state, attributes=dict(attrs or {}), last_updated=when, last_reported=when)


async def presence_arm(out):
    hass = L.SchedHass(L.base_states())
    hass.states.set(PRES, st("on", L.T0, OCC))
    hass.states.set(CAL, st("off", L.T0))
    cfg = L.base_config({"away_enabled": True, C.CONF_AWAY_PRESENCE_ENTITY: PRES, C.CONF_HOLIDAY_CALENDAR_ENTITY: CAL})
    entry = L.FakeEntry(data=cfg)
    coord = L.HeatPumpOptimizerCoordinator(hass, entry)
    await L.drain(hass)
    asked = {"n": 0}

    async def _refresh():
        asked["n"] += 1
    coord.async_request_refresh = _refresh
    # rewire the listener's refresh: it captured the bound method at construction
    from heatpump_optimizer import away as away_mod
    for ents, _a in list(getattr(hass, "state_listeners", [])):
        pass
    hass.state_listeners = [x for x in getattr(hass, "state_listeners", []) if PRES not in x[0] and CAL not in x[0]]
    away_mod.watch_away_inputs(hass, entry, coord._ctx._config, _refresh)
    d0 = await coord._async_update_data()
    await L.drain(hass)
    misses = 0
    cases = [("presence home->away", PRES, st("on", L.T0, OCC), st("off", L.T0 + timedelta(minutes=3), OCC), True),
             ("presence away->home", PRES, st("off", L.T0, OCC), st("on", L.T0 + timedelta(minutes=6), OCC), False),
             ("holiday off->on", CAL, st("off", L.T0), st("on", L.T0 + timedelta(minutes=9),
                                                         {"start_time": "2026-01-20 00:00:00",
                                                          "end_time": "2026-01-25 00:00:00"}), True)]
    print(f"PRES baseline away_active={d0.get('away_active')}")
    for tag, eid, old, new, want_away in cases:
        before = asked["n"]
        hass.states.set(eid, new)
        L.dtu.freeze(new.last_updated)
        ev = SimpleNamespace(data={"entity_id": eid, "old_state": old, "new_state": new})
        for ents, action in list(hass.state_listeners):
            if eid in ents:
                r = action(ev)
                if asyncio.iscoroutine(r):
                    await r
        await L.drain(hass)
        d = await coord._async_update_data()
        await L.drain(hass)
        got = d.get("away_active")
        miss = (asked["n"] == before) or (eid == PRES and bool(got) != want_away)
        misses += miss
        print(f"PRES {tag}: refresh_requests={asked['n'] - before} away_active={got} "
              f"holiday={str(d.get('away_source'))[:30]} miss={miss}")
    out["presence_missed"] = misses
    out["presence_cases"] = len(cases)
    await coord.async_shutdown()
    await L.drain(hass, 5)


async def age_arm(out):
    zone = ZoneInfo("Europe/Stockholm")
    saved = L.dtu.DEFAULT_TIME_ZONE
    L.dtu.DEFAULT_TIME_ZONE = zone
    bad = cells = 0
    try:
        # (label, the probe's last report, now) -- true elapsed = now - report
        spring = datetime(2026, 3, 29, 0, 50, tzinfo=timezone.utc)   # 01:50 CET; 02:00 CET -> 03:00 CEST at 01:00Z
        autumn = datetime(2026, 10, 25, 0, 50, tzinfo=timezone.utc)  # 02:50 CEST; 03:00 CEST -> 02:00 CET at 01:00Z
        steps = [("spring +20min", spring, spring + timedelta(minutes=20)),
                 ("spring +70min", spring, spring + timedelta(minutes=70)),
                 ("autumn +20min", autumn, autumn + timedelta(minutes=20)),
                 ("autumn +70min", autumn, autumn + timedelta(minutes=70)),
                 ("host clock -2h", L.T0, L.T0 - timedelta(hours=2)),
                 ("host clock +3h", L.T0, L.T0 + timedelta(hours=3))]
        for tag, report, now in steps:
            L.reset_globals()
            L.dtu.freeze(report)
            hass = L.SchedHass({**L.base_states(), PROBE: st("50.0", report,
                                                             {"unit_of_measurement": "°C", "device_class": "temperature"})})
            for k in ("sensor.indoor", "sensor.outdoor"):
                hass.states.set(k, st(hass.states.get(k).state, report))
            coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({C.CONF_DHW_TEMP_ENTITY: PROBE})))
            await L.drain(hass)
            await coord._async_update_data()
            await L.drain(hass)
            L.dtu.freeze(now)
            for k in ("sensor.indoor", "sensor.outdoor"):  # the core keeps reporting at the new clock
                hass.states.set(k, st(hass.states.get(k).state, now))
            d = await coord._async_update_data()
            await L.drain(hass)
            true_min = (now - report).total_seconds() / 60.0
            ages = d.get("input_ages_minutes") or {}
            probe_age = ages.get(C.CONF_DHW_TEMP_ENTITY)
            plan_age = d.get("plan_age_minutes")
            wx = d.get("weather_forecast_stale_hours")
            vals = {"probe_age": probe_age, "plan_age_minutes": plan_age, "weather_stale_hours": wx}
            wrong = []
            for name, v in vals.items():
                if isinstance(v, (int, float)) and v < 0:
                    wrong.append(f"{name}<0")
            if isinstance(probe_age, (int, float)) and true_min >= 0 and abs(probe_age - true_min) > 1.0:
                wrong.append("probe_age!=elapsed")
            cells += 1
            bad += bool(wrong)
            print(f"AGE {tag}: true_elapsed_min={true_min:.0f} {vals} "
                  f"probe_problem={[p.get('problem') for p in d.get('input_problems') or [] if p.get('input') == C.CONF_DHW_TEMP_ENTITY]} wrong={wrong}")
            await coord.async_shutdown()
            await L.drain(hass, 5)
    finally:
        L.dtu.DEFAULT_TIME_ZONE = saved
    out["age_cells"] = cells
    out["age_cells_wrong"] = bad


def main():
    proc0, thr0 = time.process_time(), time.thread_time()
    out = {}
    for arm in (presence_arm, age_arm):
        L.reset_globals()
        ps = L.patches() + L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(L.T0)
        try:
            asyncio.run(arm(out))
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
