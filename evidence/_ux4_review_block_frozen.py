"""Unit tests for the v2.8.0 feature modules.

    PYTHONPATH=tests/hastub python tests/features.py

Each module is driven directly rather than through a full optimization run.
The end-to-end scripts already cover "does the plan come out sensible"; what
they cannot cover is a detector that never fires, a watchdog that lets a
flatline through, or a tariff term that charges a month's fee once per hour.
Those failures produce a *plausible* plan, which is exactly why they need
tests that look at the mechanism rather than at the outcome.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeState, Results, UTC, minutes_ago

R = Results("UX4 block")
from homeassistant.util import dt as _rv_dt
_rv_dt.freeze(datetime(2026, 10, 3, 7, 0, tzinfo=timezone.utc))
# R9-UX-4 (#1795): documented events for what an owner wants to be told about,
# and the blueprint that routes them. The notifier diffs the coordinator's typed
# payload on each update and fires one event per occurrence; what it has sent
# survives a restart. Each event is driven on its signal, on a repeat of that
# signal (nothing more fires: the null control), after the signal clears (it
# re-arms) and through a restart.
import asyncio as _ux4_aio
import re as _ux4_re
from pathlib import Path as _ux4_Path

import homeassistant.helpers.storage as _ux4_storage
from heatpump_optimizer import notifier as _ux4_mod

_UX4_ROOT = _ux4_Path(__file__).resolve().parent.parent


class _Ux4Bus:
    def __init__(self):
        self.fired = []

    def async_fire(self, event_type, event_data=None):
        self.fired.append((event_type, dict(event_data or {})))


class _Ux4Hass:
    def __init__(self):
        self.bus = _Ux4Bus()


class _Ux4Rig:
    """A notifier over a recording bus; persistence tasks are awaited in line."""

    def __init__(self, entry_id="ux4"):
        self.hass = _Ux4Hass()
        self.entry_id = entry_id
        self.pending = []
        self.notifier = _ux4_mod.Notifier(self.hass, entry_id, self.pending.append)

    async def load(self):
        await self.notifier.async_load()

    async def feed(self, payload):
        before = len(self.hass.bus.fired)
        self.notifier.handle(payload)
        while self.pending:
            await self.pending.pop(0)
        return self.hass.bus.fired[before:]


def _ux4_payload(**over):
    quiet = {
        "insight": {},
        "savings_months": [],
        "min_temperature": 19.0,
        "schedule": [
            {"time": "2026-10-03T02:00:00+02:00", "room_temp": 20.4},
            {"time": "2026-10-03T06:00:00+02:00", "room_temp": 20.1},
        ],
        "input_problems": [],
        "plan_stale": False,
        "plan_age_minutes": 12.0,
        "currency": "SEK",
    }
    quiet.update(over)
    return quiet


def _ux4_cold(low, floor=19.0):
    return _ux4_payload(
        min_temperature=floor,
        schedule=[
            {"time": "2026-10-03T02:00:00+02:00", "room_temp": 20.4},
            {"time": "2026-10-03T06:00:00+02:00", "room_temp": low},
        ],
    )


def _ux4_receipt(month, total=612.0):
    return _ux4_payload(
        insight={"monthly_report": {"month": month, "total_sek": total}},
        savings_months=[{"month": month, "savings_sek": 148.0, "savings_pct": 19.0}],
    )


def _ux4_stale(*names, age=190.0, limit=60.0, problem="stale"):
    return _ux4_payload(input_problems=[
        {"input": n, "entity_id": f"sensor.{n}", "problem": problem,
         "age_minutes": age, "max_age_minutes": limit}
        for n in names
    ])


def _ux4_released(expires="2026-10-03T08:00:00+02:00", space=(3, 4), dhw=()):
    return _ux4_payload(manual_plan={
        "active": True, "expires_at": expires,
        "released_space": [{"step": i, "reason": "safety"} for i in space],
        "released_dhw": [{"step": i, "reason": "safety"} for i in dhw],
    })


async def _ux4_scenarios():
    out = {}
    E = _ux4_mod

    # -- monthly receipt: baseline, fire on a new month, quiet on a repeat ----
    rig = _Ux4Rig("ux4_receipt")
    await rig.load()
    out["receipt_none"] = await rig.feed(_ux4_payload())
    out["receipt_first"] = await rig.feed(_ux4_receipt("2026-09"))
    out["receipt_repeat"] = [await rig.feed(_ux4_receipt("2026-09")) for _ in range(3)]
    out["receipt_next"] = await rig.feed(_ux4_receipt("2026-10", total=700.0))

    # an install that already holds a receipt when the notifier first runs
    # adopts it silently; the next month's is announced
    rig = _Ux4Rig("ux4_upgrade")
    await rig.load()
    out["upgrade_existing"] = await rig.feed(_ux4_receipt("2026-09"))
    out["upgrade_next"] = await rig.feed(_ux4_receipt("2026-10"))

    # -- comfort at risk -------------------------------------------------------
    rig = _Ux4Rig("ux4_comfort")
    await rig.load()
    out["comfort_ok"] = await rig.feed(_ux4_payload())
    out["comfort_at_floor"] = await rig.feed(_ux4_cold(19.0))
    out["comfort_below"] = await rig.feed(_ux4_cold(18.6))
    out["comfort_repeat"] = [await rig.feed(_ux4_cold(18.6)) for _ in range(3)]
    out["comfort_deeper"] = await rig.feed(_ux4_cold(18.2))
    out["comfort_clear"] = await rig.feed(_ux4_payload())
    out["comfort_again"] = await rig.feed(_ux4_cold(18.8))

    # -- input stale -----------------------------------------------------------
    rig = _Ux4Rig("ux4_inputs")
    await rig.load()
    out["input_other_problem"] = await rig.feed(_ux4_stale("indoor", problem="unavailable"))
    out["input_one"] = await rig.feed(_ux4_stale("indoor"))
    out["input_repeat"] = [await rig.feed(_ux4_stale("indoor")) for _ in range(3)]
    out["input_second"] = await rig.feed(_ux4_stale("indoor", "price"))
    out["input_clear"] = await rig.feed(_ux4_payload())
    out["input_again"] = await rig.feed(_ux4_stale("indoor"))

    # -- plan stale ------------------------------------------------------------
    rig = _Ux4Rig("ux4_plan")
    await rig.load()
    out["plan_fresh"] = await rig.feed(_ux4_payload())
    out["plan_stale"] = await rig.feed(_ux4_payload(plan_stale=True, plan_age_minutes=95.0))
    out["plan_repeat"] = [
        await rig.feed(_ux4_payload(plan_stale=True, plan_age_minutes=95.0 + k))
        for k in range(3)
    ]
    out["plan_clear"] = await rig.feed(_ux4_payload())
    out["plan_again"] = await rig.feed(_ux4_payload(plan_stale=True))

    # -- manual plan released --------------------------------------------------
    rig = _Ux4Rig("ux4_manual")
    await rig.load()
    out["manual_none"] = await rig.feed(_ux4_payload())
    out["manual_space"] = await rig.feed(_ux4_released())
    out["manual_repeat"] = [await rig.feed(_ux4_released(space=(3, 4, 5))) for _ in range(3)]
    out["manual_dhw"] = await rig.feed(_ux4_released(space=(3, 4), dhw=(9,)))
    out["manual_over"] = await rig.feed(_ux4_payload())
    out["manual_new"] = await rig.feed(_ux4_released(expires="2026-10-04T08:00:00+02:00"))

    # -- a payload that carries none of the signals neither fires nor re-arms -
    rig = _Ux4Rig("ux4_light")
    await rig.load()
    await rig.feed(_ux4_payload(plan_stale=True))
    out["light_between"] = await rig.feed({})
    out["light_after"] = await rig.feed(_ux4_payload(plan_stale=True))

    # -- a restart remembers what was sent -------------------------------------
    rig = _Ux4Rig("ux4_restart")
    await rig.load()
    await rig.feed(_ux4_payload())
    every = _ux4_payload(
        insight={"monthly_report": {"month": "2026-09", "total_sek": 612.0}},
        savings_months=[{"month": "2026-09", "savings_sek": 148.0, "savings_pct": 19.0}],
        min_temperature=19.0,
        schedule=[{"time": "2026-10-03T06:00:00+02:00", "room_temp": 18.5}],
        input_problems=_ux4_stale("indoor")["input_problems"],
        plan_stale=True,
        manual_plan=_ux4_released()["manual_plan"],
    )
    # the signals arrive one at a time, each added to the ones before it
    stage = _ux4_payload()
    sent = []
    for keys in (("insight", "savings_months"), ("schedule",), ("input_problems",),
                 ("plan_stale",), ("manual_plan",)):
        stage = {**stage, **{k: every[k] for k in keys}}
        sent.append(await rig.feed(stage))
    out["restart_first_run"] = sent
    rebooted = _Ux4Rig("ux4_restart")
    await rebooted.load()
    out["restart_same"] = await rebooted.feed(every)
    out["restart_clear"] = await rebooted.feed(_ux4_payload())
    rebooted_again = _Ux4Rig("ux4_restart")
    await rebooted_again.load()
    out["restart_after_clear"] = await rebooted_again.feed(every)
    # -- a plan with no readable room temperature fires nothing and does not crash
    rig = _Ux4Rig("ux4_blank")
    await rig.load()
    out["blank_steps"] = await rig.feed(_ux4_payload(
        schedule=[{"time": "2026-10-03T02:00:00+02:00", "room_temp": None}, {"time": "x"}]))
    out["blank_none"] = await rig.feed(_ux4_payload(schedule=[]))

    # -- what the store holds: its version, and only text read back from it ----
    rig = _Ux4Rig("ux4_disk")
    key = f"{_ux4_mod.DOMAIN}_ux4_disk_notifier"
    _ux4_storage._DISK[key] = _ux4_storage.json.dumps(
        {"sent": {"junk": 5, "plan_stale": "stale"}})
    _ux4_storage._VERSIONS[key] = 1
    await rig.load()
    await rig.feed(_ux4_payload())
    out["disk_after"] = _ux4_storage.json.loads(_ux4_storage._DISK[key])
    out["disk_version"] = _ux4_storage._VERSIONS[key]
    return out


_ux4 = _ux4_aio.run(_ux4_scenarios())


def _ux4_types(events):
    return [t for t, _d in events]


_ux4_recv = _ux4["receipt_first"]
R.check(
    "UX-4 receipt: a closed month is announced once, with the month, the "
    "total and the saving against the plain thermostat",
    _ux4_types(_ux4["receipt_none"]) == []
    and _ux4_types(_ux4_recv) == [_ux4_mod.EVENT_MONTHLY_RECEIPT]
    and _ux4_recv[0][1].get("month") == "2026-09"
    and _ux4_recv[0][1].get("total_sek") == 612.0
    and _ux4_recv[0][1].get("saving_sek") == 148.0
    and _ux4_recv[0][1].get("saving_pct") == 19.0
    and _ux4_recv[0][1].get("currency") == "SEK",
    str(_ux4["receipt_first"]),
)
R.check(
    "UX-4 receipt: the same month on later refreshes fires nothing (null "
    "control), and the next month fires again",
    _ux4["receipt_repeat"] == [[], [], []]
    and _ux4_types(_ux4["receipt_next"]) == [_ux4_mod.EVENT_MONTHLY_RECEIPT]
    and _ux4["receipt_next"][0][1]["month"] == "2026-10",
    str((_ux4["receipt_repeat"], _ux4["receipt_next"])),
)
R.check(
    "UX-4 receipt: a receipt already held when the notifier first runs is "
    "adopted silently, the next month's is announced",
    _ux4["upgrade_existing"] == []
    and _ux4_types(_ux4["upgrade_next"]) == [_ux4_mod.EVENT_MONTHLY_RECEIPT],
    str((_ux4["upgrade_existing"], _ux4["upgrade_next"])),
)

_ux4_cmf = _ux4["comfort_below"]
R.check(
    "UX-4 comfort: a plan whose coldest step is below the floor fires once "
    "with the predicted minimum, when, and the floor; a plan at the floor "
    "and a comfortable plan fire nothing",
    _ux4["comfort_ok"] == [] and _ux4["comfort_at_floor"] == []
    and _ux4_types(_ux4_cmf) == [_ux4_mod.EVENT_COMFORT_AT_RISK]
    and _ux4_cmf[0][1].get("predicted_min_c") == 18.6
    and _ux4_cmf[0][1].get("at") == "2026-10-03T06:00:00+02:00"
    and _ux4_cmf[0][1].get("floor_c") == 19.0,
    str((_ux4["comfort_at_floor"], _ux4["comfort_below"])),
)
R.check(
    "UX-4 comfort: the same risk on later refreshes, even a deeper one, "
    "fires nothing; once it clears a new risk fires again",
    _ux4["comfort_repeat"] == [[], [], []] and _ux4["comfort_deeper"] == []
    and _ux4["comfort_clear"] == []
    and _ux4_types(_ux4["comfort_again"]) == [_ux4_mod.EVENT_COMFORT_AT_RISK],
    str((_ux4["comfort_repeat"], _ux4["comfort_deeper"], _ux4["comfort_again"])),
)

_ux4_inp = _ux4["input_one"]
R.check(
    "UX-4 input stale: a stale input fires once with its name, age and limit; "
    "an input with another problem fires nothing",
    _ux4["input_other_problem"] == []
    and _ux4_types(_ux4_inp) == [_ux4_mod.EVENT_INPUT_STALE]
    and _ux4_inp[0][1].get("input") == "indoor"
    and _ux4_inp[0][1].get("age_minutes") == 190.0
    and _ux4_inp[0][1].get("max_age_minutes") == 60.0,
    str((_ux4["input_other_problem"], _ux4["input_one"])),
)
R.check(
    "UX-4 input stale: a repeat fires nothing, a second input fires on its "
    "own, and a recovered input fires again when it goes stale again",
    _ux4["input_repeat"] == [[], [], []]
    and [d.get("input") for _t, d in _ux4["input_second"]] == ["price"]
    and _ux4["input_clear"] == []
    and [d.get("input") for _t, d in _ux4["input_again"]] == ["indoor"],
    str((_ux4["input_second"], _ux4["input_again"])),
)

R.check(
    "UX-4 plan stale: fires once with the age, nothing on a repeat (null "
    "control), and again after the plan was fresh in between",
    _ux4["plan_fresh"] == []
    and _ux4_types(_ux4["plan_stale"]) == [_ux4_mod.EVENT_PLAN_STALE]
    and _ux4["plan_stale"][0][1].get("age_minutes") == 95.0
    and _ux4["plan_repeat"] == [[], [], []] and _ux4["plan_clear"] == []
    and _ux4_types(_ux4["plan_again"]) == [_ux4_mod.EVENT_PLAN_STALE],
    str((_ux4["plan_stale"], _ux4["plan_repeat"], _ux4["plan_again"])),
)

_ux4_man = _ux4["manual_space"]
R.check(
    "UX-4 manual plan released: fires once per channel for an override, with "
    "the channel, the steps and the reason; none while nothing is released",
    _ux4["manual_none"] == []
    and _ux4_types(_ux4_man) == [_ux4_mod.EVENT_MANUAL_PLAN_RELEASED]
    and _ux4_man[0][1].get("channel") == "space"
    and _ux4_man[0][1].get("steps") == [3, 4]
    and _ux4_man[0][1].get("reason") == "safety"
    and _ux4["manual_repeat"] == [[], [], []]
    and [d.get("channel") for _t, d in _ux4["manual_dhw"]] == ["dhw"],
    str((_ux4["manual_space"], _ux4["manual_repeat"], _ux4["manual_dhw"])),
)
R.check(
    "UX-4 manual plan released: a later override fires again once the first "
    "is over",
    _ux4["manual_over"] == []
    and [d.get("channel") for _t, d in _ux4["manual_new"]] == ["space"],
    str(_ux4["manual_new"]),
)

R.check(
    "UX-4 a plan with no readable room temperature fires nothing; a stored "
    "value that is not text is dropped on load and the store stays at version 1",
    _ux4["blank_steps"] == [] and _ux4["blank_none"] == []
    and _ux4["disk_after"] == {"sent": {}} and _ux4["disk_version"] == 1,
    str((_ux4["blank_steps"], _ux4["disk_after"], _ux4["disk_version"])),
)
R.check(
    "UX-4 a payload carrying none of the signals fires nothing and does not "
    "re-arm what was sent (an unchanged refresh stays silent)",
    _ux4["light_between"] == [] and _ux4["light_after"] == [],
    str((_ux4["light_between"], _ux4["light_after"])),
)

R.check(
    "UX-4 restart: the first run fires all five events, a notifier rebuilt "
    "over the same store fires none of them for the same signals, and one "
    "that saw them clear fires them again",
    [len(e) for e in _ux4["restart_first_run"]] == [1, 1, 1, 1, 1]
    and _ux4["restart_same"] == [] and _ux4["restart_clear"] == []
    and sorted(_ux4_types(_ux4["restart_after_clear"])) == sorted([
        _ux4_mod.EVENT_COMFORT_AT_RISK, _ux4_mod.EVENT_INPUT_STALE,
        _ux4_mod.EVENT_PLAN_STALE, _ux4_mod.EVENT_MANUAL_PLAN_RELEASED]),
    str((_ux4["restart_same"], _ux4["restart_after_clear"])),
)

_ux4_fired_keys = {}
for _ux4_group in [v for k, v in _ux4.items() if not k.startswith("disk_")]:
    for _ux4_item in (_ux4_group if _ux4_group and isinstance(_ux4_group[0], list) else [_ux4_group]):
        for _ux4_t, _ux4_d in _ux4_item:
            _ux4_fired_keys.setdefault(_ux4_t, set()).add(tuple(_ux4_d))
R.check(
    "UX-4 each event carries exactly the data keys the module declares for it, "
    "and all five were seen firing",
    set(_ux4_fired_keys) == set(tuple(_ux4_mod.EVENT_DATA))
    and all(keys == {tuple(_ux4_mod.EVENT_DATA[t])} for t, keys in _ux4_fired_keys.items()),
    str(_ux4_fired_keys),
)

# -- the registered surface: wiring, documentation, blueprint ------------------
_ux4_init = (_UX4_ROOT / "custom_components/heatpump_optimizer/__init__.py").read_text()
R.check(
    "UX-4 the entry sets the notifier up beside the coordinator it listens to "
    "(and coordinator.py names no notifier)",
    "notifier" in _ux4_init
    and "async_setup_notifier" in _ux4_init
    and "notifier" not in (
        _UX4_ROOT / "custom_components/heatpump_optimizer/coordinator.py"
    ).read_text(),
    "async_setup_notifier is not called from __init__.py, or coordinator.py grew a notifier",
)


def _ux4_wiring():
    class _Coord:
        def __init__(self):
            self.listeners = []
            self.data = _ux4_payload()

        def async_add_listener(self, cb, context=None):
            self.listeners.append(cb)
            return lambda: self.listeners.remove(cb)

    class _Entry:
        entry_id = "ux4_wire"

        def __init__(self):
            self.unloads = []
            self.tasks = []

        def async_on_unload(self, fn):
            self.unloads.append(fn)

        def async_create_background_task(self, hass, coro, name, eager_start=True):
            self.tasks.append(name)
            coro.close()

    async def go():
        hass, coord, entry = _Ux4Hass(), _Coord(), _Entry()
        await _ux4_mod.async_setup_notifier(hass, entry, coord)
        registered = len(coord.listeners)
        coord.data = _ux4_payload(plan_stale=True)
        for cb in list(coord.listeners):
            cb()
        fired = list(hass.bus.fired)
        for fn in entry.unloads:
            fn()
        return registered, fired, len(coord.listeners)

    return _ux4_aio.run(go())


_ux4_reg, _ux4_wfired, _ux4_left = _ux4_wiring()
R.check(
    "UX-4 setup subscribes to coordinator updates, fires on one, and the "
    "subscription is dropped when the entry unloads",
    _ux4_reg == 1 and _ux4_types(_ux4_wfired) == [_ux4_mod.EVENT_PLAN_STALE]
    and _ux4_left == 0,
    str((_ux4_reg, _ux4_wfired, _ux4_left)),
)

_ux4_docs = (_UX4_ROOT / "docs/automations.md").read_text()
_ux4_bp = (_UX4_ROOT / "blueprints/automation/notifications.yaml").read_text()
R.check(
    "UX-4 every event the notifier can fire is documented in "
    "docs/automations.md with each key of its data, and routed by the blueprint",
    len(tuple(_ux4_mod.EVENT_DATA)) == 5
    and all(f"`{ev}`" in _ux4_docs and f"event_type: {ev}" in _ux4_bp
            for ev in tuple(_ux4_mod.EVENT_DATA))
    and all(f"`{key}`" in _ux4_docs
            for keys in _ux4_mod.EVENT_DATA.values() for key in keys),
    "an event or one of its data keys is missing from the docs or the blueprint",
)
R.check(
    "UX-4 the blueprint takes a notify target, one toggle per event and quiet "
    "hours that the comfort alert passes through",
    "notify_entity:" in _ux4_bp
    and _ux4_bp.count("selector:\n        boolean") >= 5
    and "quiet_start:" in _ux4_bp and "quiet_end:" in _ux4_bp
    and _ux4_mod.EVENT_COMFORT_AT_RISK in _ux4_bp,
    "blueprints/automation/notifications.yaml lacks an input",
)


sys.exit(R.close("UX4"))
