#!/usr/bin/env python3
"""The debug collector's guards, driven without the feature suite (#1939).

tests/features.py already runs this behaviour at the end of a suite whose
baseline is red on this host (R9-F2.1 P3) and whose recorded cost, with every
other driver that imports the package, is more than the mutation job's
35-minute pin budget. CI's pin drive therefore started none of the new sites
(run 37473761833: "52 not started for --budget-minutes"). This script is the
driver that kills them: one check per guard, on the production functions.

    PYTHONPATH=tests/hastub python3 tests/debug_collect.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import homeassistant.helpers.storage as storage
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
from harness import FakeCoordinator, FakeEntry, FakeHass, Results
from heatpump_optimizer import button as button_mod
from heatpump_optimizer import debugger
from heatpump_optimizer.const import CONF_DEBUG_COLLECT, DOMAIN
from heatpump_optimizer.store import Domain, _scalar_domain, stored_fields

R = Results("debug collection guards (#1939)")
T0 = datetime(2026, 1, 12, tzinfo=timezone.utc)
NEEDS = {"t"}


class _Coord:
    """A coordinator stand-in the collector can key a weak reference on."""

    def __init__(self, **kw):
        self.accuracy = type("A", (), {"samples": []})()
        self.solve_failures = 0
        self.prices = ()
        self.optimization_running = False
        self.data = None
        for key, value in kw.items():
            setattr(self, key, value)


def _coord(**kw):
    return _Coord(**kw)


def _collector():
    spawned: list = []

    def spawn(coro):
        spawned.append(coro)
        coro.close()

    return debugger.DebugCollector(FakeHass(), "dbg", spawn), spawned


def _row(**extra):
    return {"t": T0.isoformat(), "mode": "auto", **extra}


# -- wire, row, repair -------------------------------------------------------
R.check(
    "the debug store opens at version 1",
    debugger.DEBUG_STORE_VERSION == 1
    and debugger._store(FakeHass(), "dbg")._major == 1,
)
when = datetime(2026, 1, 12, 3, 4, tzinfo=timezone.utc)
R.check(
    "a datetime in a payload is its ISO text, and a set is a list",
    json.loads(debugger._dumps(when)) == when.isoformat()
    and json.loads(debugger._dumps({1})) == [1]
    and json.loads(debugger._dumps(Path("x"))) == "x",
)
bare = debugger.cycle_row(_coord(), {"mode": "auto"}, T0, None)
R.check(
    "a cycle row omits fields the cycle did not carry",
    bare == {"t": T0.isoformat(), "mode": "auto", "solve_failures": 0, "prices_rows": 0},
    str(bare),
)
good = _row(prices_rows=5)
R.check(
    "a stored row inside its domain is kept, and one outside it is dropped",
    debugger._repair(good, "rows", NEEDS) == good
    and debugger._repair({**good, "prices_rows": -1}, "rows", NEEDS) is None
    and debugger._repair(_row(), "rows", NEEDS) is not None,
)
R.check(
    "a row whose only field is its stamp is inside the domain",
    debugger._repair({"t": T0.isoformat()}, "rows", NEEDS) == {"t": T0.isoformat()},
)
R.check(
    "a row whose stamp does not parse is dropped",
    debugger._repair({"t": "nope", "mode": "auto"}, "rows", NEEDS) is None,
)
absent = debugger._repair(_row(), "rows", NEEDS)
empty_sample = debugger._repair(_row(accuracy_sample={}), "rows", NEEDS)
listed = debugger._repair(_row(accuracy_sample=[]), "rows", NEEDS)
kept_sample = debugger._repair(
    _row(accuracy_sample={"t": T0.isoformat(), "predicted_cost": 1.0}), "rows", NEEDS)
R.check(
    "a row with no accuracy sample is kept; an empty or non-dict sample is dropped; "
    "a sample's stamp is stored aware",
    absent is not None and "accuracy_sample" not in absent
    and empty_sample is None and listed is None
    and kept_sample["accuracy_sample"]["t"] == T0.isoformat()
    and kept_sample["accuracy_sample"]["predicted_cost"] == 1.0,
    f"absent={absent} empty={empty_sample} listed={listed} kept={kept_sample}",
)
kept = debugger._kept({"rows": [1, good]}, "rows", NEEDS)
R.check(
    "a stored item that is not a dict is dropped and does not stop the ring loading",
    kept == [good],
    str(kept),
)
with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    (folder / "k").write_text(
        json.dumps({"version": 1, "data": {"a": 1}}), encoding="utf-8")
    (folder / "bad").write_text("not-json", encoding="utf-8")
    found = debugger._read_stores(folder, ["k", "bad", "missing"])
R.check(
    "a store document on disk is its version and data; a bad file is skipped",
    found == {"k": (1, {"a": 1})},
    str(found),
)


# -- the ring: span, snapshot, save, solve wall ------------------------------
def _arm(running, data, stamp):
    coord = _coord(optimization_running=running, data=data)
    collector, spawned = _collector()
    debugger._COLLECTORS[coord] = collector
    return coord, collector, spawned


coord, collector, spawned = _arm(False, {"mode": "auto"}, T0)
dt_util.freeze(T0)
collector.observe(coord)
idle_started = collector._solve_started
R.check(
    "an update that is not a running solve does not start the solve clock",
    idle_started is None and len(collector.rows) == 1,
    f"started={idle_started} rows={len(collector.rows)}",
)
clock = {"t": 0.0}
debugger.time.monotonic = lambda: clock["t"]
coord.optimization_running = True
collector.observe(coord)
clock["t"] = 10.0
collector.observe(coord)
clock["t"] = 30.0
coord.optimization_running = False
coord.data = {"mode": "heat"}
dt_util.freeze(T0 + timedelta(minutes=30))
collector.observe(coord)
wall = collector.rows[-1].get("solve_wall_ms")
R.check(
    "a solve's wall is the span from the running edge to the stopped edge",
    wall == 30000.0 and len(collector.rows) == 2,
    f"wall={wall} rows={len(collector.rows)}",
)
same = len(collector.rows)
collector.observe(coord)
R.check(
    "a listener call that publishes no new payload adds no row",
    len(collector.rows) == same,
)
none_data = _coord(data=None)
none_collector, _ = _collector()
none_collector.observe(none_data)
R.check(
    "a listener call with no payload adds no row",
    none_collector.rows == [],
)
collector.final = True
frozen_rows = len(collector.rows)
coord.data = {"mode": "off"}
collector.observe(coord)
R.check(
    "a final collection records nothing more",
    len(collector.rows) == frozen_rows and collector.final,
)

span, span_spawned = _collector()
span.record(_coord(), {"mode": "auto"}, T0)
span.record(_coord(), {"mode": "heat"}, T0 + debugger.COLLECT_SPAN)
R.check(
    "a collection stops at exactly seven days and does not store the row past the span",
    span.final and len(span.rows) == 1,
    f"final={span.final} rows={len(span.rows)}",
)
shot, _ = _collector()
shot.record(_coord(), {"mode": "auto"}, T0)
shot.record(_coord(), {"mode": "heat"}, T0 + debugger.SNAPSHOT_EVERY)
R.check(
    "a payload snapshot is taken on the first row and again at exactly one day",
    len(shot.snapshots) == 2 and shot.snapshots[1]["cycle"] == 1,
    str([s["cycle"] for s in shot.snapshots]),
)
saved, save_spawned = _collector()
saved.record(_coord(), {"mode": "auto"}, T0)
first_save = len(save_spawned)
saved.record(_coord(), {"mode": "heat"}, T0 + debugger.SAVE_EVERY)
R.check(
    "the ring is saved on the first row and again at exactly one hour",
    first_save == 1 and len(save_spawned) == 2,
    f"saves={len(save_spawned)}",
)


async def _load_without_start():
    storage._DISK.clear()
    storage._VERSIONS.clear()
    key = f"{DOMAIN}_dbg_debug"
    storage._DISK[key] = json.dumps({"final": True, "rows": [_row()], "snapshots": []})
    storage._VERSIONS[key] = 1
    collector, _ = _collector()
    await collector.async_load()
    return collector.final, collector.rows, collector.started_at


no_start = asyncio.run(_load_without_start())
R.check(
    "a ring with no start stays empty even when the document says it is final",
    no_start == (False, [], None),
    str(no_start),
)


async def _option_off():
    storage._DISK.clear()
    storage._VERSIONS.clear()
    key = f"{DOMAIN}_off_debug"
    storage._DISK[key] = json.dumps({"started_at": T0.isoformat(), "final": False,
                                      "rows": [], "snapshots": []})
    storage._VERSIONS[key] = 1
    entry = FakeEntry(entry_id="off", options={CONF_DEBUG_COLLECT: False})
    coord = FakeCoordinator()
    await debugger.async_setup_debugger(FakeHass(), entry, coord)
    return debugger.collector_for(coord), key in storage._DISK


off = asyncio.run(_option_off())
R.check(
    "with the option off nothing collects and a stored ring is deleted",
    off == (None, False),
    str(off),
)


async def _unload():
    collector, _ = _collector()
    coord = FakeCoordinator()
    debugger._COLLECTORS[coord] = collector
    await debugger.async_unload_debugger(coord)
    return collector._closed, debugger.collector_for(coord)


unloaded = asyncio.run(_unload())
R.check(
    "unload closes the collector and drops it",
    unloaded == (True, None),
    str(unloaded),
)


# -- the action and the finalize button --------------------------------------
def _bound(entry_id, rows=0, final=False):
    coord = FakeCoordinator()
    entry = FakeEntry(entry_id=entry_id, options={CONF_DEBUG_COLLECT: True})
    entry.runtime_data = coord
    collector, spawned = _collector()
    collector._entry_id = entry_id
    collector.rows = [_row()] * rows
    collector.final = final
    collector.started_at = T0
    debugger._COLLECTORS[coord] = collector
    return entry, collector, spawned


hass = FakeHass()
live, live_collector, _ = _bound("live", rows=2)
hass.config_entries.entries.append(live)
absent_entry = FakeEntry(entry_id="absent", options={CONF_DEBUG_COLLECT: False})
absent_entry.runtime_data = FakeCoordinator()
status_idle = debugger.async_command(hass, absent_entry, "status")
started = debugger.async_command(hass, absent_entry, "start")
live_status = debugger.async_command(hass, live, "status")
R.check(
    "status with no collection is idle, and start on that entry turns the option on",
    status_idle == {"active": False, "final": False, "rows": 0, "bytes": 0, "started_at": None}
    and started["active"] is True and started["rows"] == 0
    and absent_entry.options[CONF_DEBUG_COLLECT] is True,
    f"idle={status_idle} started={started}",
)
R.check(
    "status of a live collection reports its rows",
    live_status["active"] is True and live_status["rows"] == 2 and live_status["final"] is False,
    str(live_status),
)
final_entry, final_collector, _ = _bound("final", rows=3, final=True)
final_status = debugger.async_command(hass, final_entry, "status")
R.check(
    "status of a final collection reports it and does not clear it",
    final_status["final"] is True and final_status["rows"] == 3 and len(final_collector.rows) == 3,
    str(final_status),
)
stopped = debugger.async_command(hass, live, "stop")
R.check(
    "stop finalizes the live collection",
    stopped["final"] is True and live_collector.final,
    str(stopped),
)
restarted = debugger.async_command(hass, live, "start")
R.check(
    "start on a final collection clears it",
    restarted["final"] is False and restarted["rows"] == 0 and live_collector.rows == [],
    str(restarted),
)
try:
    debugger.async_command(hass, absent_entry, "stop")
    refused = None
except ServiceValidationError as err:
    refused = err.translation_key
R.check(
    "stop with no collection is refused",
    refused == "debug_collect_inactive",
    str(refused),
)

button_coord = FakeCoordinator()
button_entry = FakeEntry(entry_id="btn")
button = button_mod.DebugFinalizeButton(button_coord, button_entry)
dark = button.extra_state_attributes
held, held_collector, _ = _bound("btn", rows=1)
# The button reads the collector for its own coordinator, not the bound entry's.
debugger._COLLECTORS.pop(held.runtime_data, None)
debugger._COLLECTORS[button_coord] = held_collector
lit = button.extra_state_attributes
available = button.available
asyncio.run(button.async_press())
R.check(
    "the finalize button is available while a collection is open, names why it is "
    "dark otherwise, and a press finalizes",
    dark == {"waiting_for": "debug_collect"}
    and lit == {}
    and available is True
    and held_collector.final
    and button.available is False
    and button.extra_state_attributes == {"waiting_for": "debug_collect"},
    f"dark={dark} lit={lit} available={available} final={held_collector.final}",
)


# -- a scalar domain is one value, not a container walked in its place --------
flag = Domain("flag")
R.check(
    "a node that declares one value is that domain, and one with another key is not",
    _scalar_domain({"": flag}) is flag
    and _scalar_domain({"": flag, "extra": {}}) is None,
)
fields = stored_fields("debug", {"final": {"nested": True}})
R.check(
    "a dict stored where one value belongs is that value, not a walk of its keys",
    any(path == ("final",) and domain is not None and value == {"nested": True}
        for path, _key, domain, value in fields),
    str(fields),
)
walked = stored_fields("debug", {"final": True})
R.check(
    "a real flag still reaches its declared domain",
    any(path == ("final",) and value is True for path, _key, _domain, value in walked),
    str(walked),
)

dt_util.freeze(None)
debugger._COLLECTORS.clear()
sys.exit(R.close("DEBUG COLLECT CHECKS"))
