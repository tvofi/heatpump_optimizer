#!/usr/bin/env python3
"""R10-HOTFIX-AWAY-PRESENCE: does a presence or holiday-calendar flip reach the plan before the next update?

WHY IT EXISTS. Probe r10-live-away-heating (code chain, step 3) found no state
listener on ``away_presence_entity``: an away flag from a person, calendar or
presence entity reached the plan only at the next scheduled update, one
``optimization_interval`` later. Its own harness (r10_live_away_heating.py)
drives the solve and reads flat across this fix; this companion drives the
production coordinator's construction and the listener it registers.

Arms (one RESULT line each), for each a fresh ``HeatPumpOptimizerCoordinator``
over the suite's FakeHass, with ``away_presence_entity`` configured:

  flip_<case>     a change that flips the interpreted away state, or the
                  holiday calendar's dates (``holiday_calendar_entity``)
  hold_<case>     a change that leaves either as it was (the null control)
  unconfigured    no presence entity: listener count

  listeners  subscriptions on the entity after construction
  refreshes  coordinator refreshes the change hands Home Assistant as a task
  wait_min   minutes until the flip can reach the plan: 0 when a refresh is
             requested (Home Assistant's debouncer runs it), else the update
             interval (the next scheduled refresh)

A last arm reads the reload handover: minutes until ``next_optimization`` on
the first publish after a reload, for a plan solved 10 min before with its
next solve 20 min ahead.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_away_presence_listener.py
"""
from __future__ import annotations

import asyncio
from datetime import timedelta

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

OCC = {"device_class": "occupancy"}
HOL = "holiday_calendar_entity"
SPAN = {"start_time": "2026-12-24 00:00:00", "end_time": "2026-12-27 00:00:00"}
LONGER = {"start_time": "2026-12-24 00:00:00", "end_time": "2026-12-28 00:00:00"}


class _Hass(FakeHass):
    def async_create_task(self, coro):
        self.asked = getattr(self, "asked", []) + [coro.cr_code.co_name]
        coro.close()


class _Event:
    def __init__(self, old, new, attrs=None):
        self.data = {k: None if v is None else FakeState(v, attributes=attrs)
                     for k, v in (("old_state", old), ("new_state", new))}


def arm(name, entity, old, new, attrs=None, slot="away_presence_entity", new_attrs=None) -> dict:
    cfg = {"tibber_token": "x", "weather_entity": "weather.home"}
    if entity:
        cfg[slot] = entity
    coord = Coord(_Hass({}), FakeEntry(data=cfg))
    coord.hass.asked = []
    regs = [a for ids, a in getattr(coord.hass, "state_listeners", []) if ids == [entity]]
    event = _Event(old, new, attrs)
    if new_attrs is not None:
        event.data["new_state"] = FakeState(new, attributes=new_attrs)
    for action in regs:
        action(event)
    refreshes = coord.hass.asked.count("async_request_refresh")
    interval = coord.update_interval.total_seconds() / 60.0
    out = {"arm": name, "listeners": len(regs), "refreshes": refreshes,
           "wait_min": 0.0 if refreshes else interval}
    print("RESULT " + " ".join(f"{k}={v}" for k, v in out.items()), flush=True)
    return out


async def handover() -> float:
    hass = _Hass({})
    data = {"tibber_token": "x", "weather_entity": "weather.home"}
    old = Coord(hass, FakeEntry(data=data))
    published = old._build_data_dict()
    published["last_optimization"] = dt_util.now() - timedelta(minutes=10)
    published["next_optimization"] = dt_util.now() + timedelta(minutes=20)
    new = Coord(hass, FakeEntry(data=data), skip_first_solve=True, reload_handover=published)
    import heatpump_optimizer.boost as boost

    async def _restored(_c):
        return None

    saved, boost.session_restored = boost.session_restored, _restored
    try:
        first = await new._async_update_data()
    finally:
        boost.session_restored = saved
    due = (first["next_optimization"] - dt_util.now()).total_seconds() / 60.0
    print(f"RESULT arm=reload_handover same_payload={first is published} "
          f"next_solve_in_min={round(due, 1) + 0.0} plan_age_min={first.get('plan_age_minutes')}", flush=True)
    return due


def main() -> int:
    flips = [
        arm("flip_person_leaves", "person.tim", "home", "not_home"),
        arm("flip_person_returns", "person.tim", "not_home", "home"),
        arm("flip_calendar_on", "calendar.holiday", "off", "on"),
        arm("flip_input_boolean_on", "input_boolean.away", "off", "on"),
        arm("flip_occupancy_clears", "binary_sensor.occ", "on", "off", OCC),
        arm("flip_holiday_starts", "calendar.hol", "off", "on", SPAN, HOL),
        arm("flip_holiday_extended", "calendar.hol", "on", "on", SPAN, HOL, new_attrs=LONGER),
    ]
    holds = [
        arm("hold_zone_to_zone", "person.tim", "work", "school"),
        arm("hold_attributes_only", "person.tim", "home", "home"),
        arm("hold_unavailable_to_home", "person.tim", "unavailable", "home"),
        arm("hold_occupancy_on", "binary_sensor.occ", "on", "on", OCC),
        arm("hold_holiday_same_span", "calendar.hol", "on", "on", SPAN, HOL),
        arm("hold_holiday_off_new_span", "calendar.hol", "off", "off", SPAN, HOL, new_attrs=LONGER),
    ]
    arm("unconfigured", None, "home", "not_home")
    due = asyncio.run(handover())
    worst = max(f["wait_min"] for f in flips)
    print(f"VERDICT presence flip reaches the plan within {worst} min "
          f"({'next scheduled update' if worst else 'debounced refresh'})")
    print(f"VERDICT null control: {sum(h['refreshes'] for h in holds)} refresh(es) "
          f"from {len(holds)} changes that keep the interpreted state")
    print(f"VERDICT reload handover publishes the next solve {round(due, 1) + 0.0} min ahead")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
