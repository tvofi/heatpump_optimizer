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
from heatpump_optimizer.store import Domain, _scalar_domain, admitted, stored_fields

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
# ``debugger.time`` is the process's one ``time`` module, and asyncio's loop
# clock reads its ``monotonic``: the real one is put back after this check.
real_monotonic = debugger.time.monotonic
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
debugger.time.monotonic = real_monotonic
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

# -- the self-tests (R9-DBG-2, #1940) -----------------------------------------
from heatpump_optimizer import diagnostics as diagnostics_mod
from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker


def _sample(minutes, predicted, actual):
    # A cost is always written: the domain declares predicted_cost not nullable.
    return AccuracySample(when=T0 + timedelta(minutes=minutes), predicted_cost=1.0,
                          predicted_temp=predicted, actual_temp=actual).as_dict()


acc_key = debugger.store_keys("dbg")["accuracy"]
clean = {acc_key: (1, {"accuracy": {"samples": [_sample(0, 21.0, 20.5)]}})}
nan = {acc_key: (1, {"accuracy": {"samples": [
    {**_sample(0, 21.0, 20.5), "predicted_temp": float("nan")}]}})}
off = {acc_key: (1, {"accuracy": {"samples": [_sample(0, 21.0, 20.5)]}, "junk": 1})}
reports = [debugger.store_report(s)[acc_key] for s in (clean, nan, off)]
R.check(
    "the store self-test names a field off its domain and a leaf the quarantine scrubs, "
    "and reports neither on a clean document",
    reports[0]["off_domain"] == [] and reports[0]["quarantined"] is False
    and reports[1]["quarantined"] is True
    and reports[2]["off_domain"] == ["junk"] and reports[2]["quarantined"] is False,
    str(reports),
)
live = AccuracyTracker()
for minutes in range(3):
    live.samples.append(AccuracySample.from_dict(_sample(minutes, 21.0, 21.0)))
stored_acc = {"accuracy": {"samples": [
    _sample(0, 21.0, 20.0), _sample(15, 21.0, 20.0), {"t": "nope"}]}}
monitor = debugger.accuracy_report(stored_acc, live)
R.check(
    "the monitor self-test re-derives bias from the stored window beside the live one, "
    "and counts the stored samples the loader drops",
    monitor["store"]["temperature_bias"] == 1.0 and monitor["live"]["temperature_bias"] == 0.0
    and monitor["stored_samples"] == 3 and monitor["restored_samples"] == 2,
    str(monitor),
)
R.check(
    "the monitor self-test of an install with no accuracy store reads an empty tracker",
    debugger.accuracy_report(None, live)["stored_samples"] == 0,
)
R.check(
    "a spread is count, min, median and max, and nothing for no values",
    debugger.spread([3.0, 1.0, 2.0]) == {"n": 3, "min": 1.0, "median": 2.0, "max": 3.0}
    and debugger.spread([]) is None,
)
week = [_row(indoor_temp=21.0, prices_rows=96, solve_failures=1),
        _row(indoor_temp=21.0, prices_rows=0, weather_stale_h=3.0, solve_failures=1),
        _row(indoor_temp=21.0, prices_rows=96, solve_failures=3),
        _row(indoor_temp=20.5, prices_rows=96, weather_stale_h=0.0, solve_failures=3),
        _row(prices_rows=96, solve_failures=3)]
sensors = debugger.sensor_sanity(week, {"problem_inputs": ["sensor.x"], "mode": "auto"})
R.check(
    "the sensor self-test counts a missing reading and the longest unchanged run per input, "
    "and reads the live input-health view",
    sensors["indoor_temp"]["missing"] == 1 and sensors["indoor_temp"]["longest_flat"] == 3
    and sensors["outdoor_temp"]["missing"] == 5 and sensors["outdoor_temp"]["longest_flat"] == 0
    and sensors["now"] == {"problem_inputs": ["sensor.x"], "input_ages_minutes": None,
                           "learners_frozen": None},
    str(sensors),
)
feeds = debugger.feed_health(week)
R.check(
    "the feed self-test counts cycles with no prices, cycles with a stale forecast, and the "
    "solve failures the week added",
    feeds["cycles"] == 5 and feeds["no_prices"] == 1 and feeds["weather_stale_cycles"] == 1
    and feeds["weather_stale_h_max"] == 3.0 and feeds["solve_failures_added"] == 2,
    str(feeds),
)
R.check(
    "the feed self-test of an empty ring adds no failures",
    debugger.feed_health([])["solve_failures_added"] == 0,
)
# A week whose price feed failed for twelve cycles: the fetch raises, so the
# coordinator publishes nothing and the ring simply has a hole in it (#1940).
SILENT = [_row(t=(T0 + timedelta(minutes=30 * i)).isoformat(), prices_rows=96)
          for i in range(6)]
SILENT += [_row(t=(T0 + timedelta(hours=8, minutes=30 + 30 * i)).isoformat(),
                prices_rows=96) for i in range(6)]
holey = debugger.feed_health(SILENT)
R.check(
    "the feed self-test names the hole the ring shows when cycles published nothing, "
    "where its price and forecast counters read clean",
    holey["row_gaps_h"] == {"n": 11, "min": 0.5, "median": 0.5, "max": 6.0}
    and holey["no_prices"] == 0 and holey["weather_stale_cycles"] == 0,
    str(holey),
)
R.check(
    "the feed self-test of an even ring reports its cadence, not a hole",
    feeds["row_gaps_h"] == {"n": 4, "min": 0.0, "median": 0.0, "max": 0.0},
    str(feeds),
)
R.check(
    "the feed self-test reports the outage streak the collection ended in, and none "
    "when it was not told",
    debugger.feed_health(SILENT, outage_cycles=12)["tibber_outage_cycles"] == 12
    and holey["tibber_outage_cycles"] is None,
    str(debugger.feed_health(SILENT, outage_cycles=12)),
)
R.check(
    "the feed self-test of a ring whose stamps do not parse reports no gaps",
    debugger.feed_health([])["row_gaps_h"] is None
    and debugger.feed_health([{"mode": "auto"}, _row(t="not a stamp")])["row_gaps_h"] is None,
)


async def _boom():
    raise RuntimeError("bad store")


async def _slow():
    await asyncio.sleep(5)


async def _fine():
    return {"ok": True}


ran = asyncio.run(debugger.run_self_tests(
    [("boom", _boom), ("fine", _fine), ("slow", _slow), ("late", _fine)], 0.2))
R.check(
    "a self-test that raises is recorded and the next still runs; one past the budget is "
    "cut off, and those after it are skipped",
    "bad store" in ran["boom"]["error"] and ran["fine"]["result"] == {"ok": True}
    and ran["slow"]["error"] == "timeout" and ran["late"] == {"skipped": "budget"},
    str(ran),
)
# A frozen clock reaches the budget's boundary exactly; restored at once,
# because asyncio's loop clock reads the same ``time.monotonic``.
debugger.time.monotonic = lambda: 100.0
try:
    spent = asyncio.run(debugger.run_self_tests([("fine", _fine)], 0.0))
finally:
    debugger.time.monotonic = real_monotonic
R.check(
    "a budget with exactly nothing left starts no further self-test",
    spent == {"fine": {"skipped": "budget"}},
    str(spent),
)
R.check(
    "the self-tests' budget is the owner's fifteen minutes",
    debugger.SELF_TEST_BUDGET == timedelta(minutes=15),
)


class _SimCoord(_Coord):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.accuracy = live
        self.simulated = []
        self.integration_version = "0.0.0"
        self.outage = 12

    async def async_simulate(self, overrides, *, limited=True, base=None):
        self.simulated.append((overrides, limited))
        return {"cost_delta": 0.0, "baseline_cost": 12.5}

    def diagnostics_state(self):
        """The published view (#1739): the caller names no private member."""
        return type("V", (), {"tibber_outage_cycles": self.outage})()


def _disk_hass(folder):
    hass = FakeHass()
    hass.config.path = lambda *parts: str(Path(folder, *parts))
    return hass


async def _finish(folder):
    storage._DISK.clear()
    storage._VERSIONS.clear()
    (Path(folder) / ".storage").mkdir()
    (Path(folder) / ".storage" / acc_key).write_text(
        json.dumps({"version": 1, "data": stored_acc}), encoding="utf-8")
    pending: list = []
    collector = debugger.DebugCollector(_disk_hass(folder), "dbg", pending.append)
    coord = _SimCoord(data={"problem_inputs": []})
    collector.record(coord, {"mode": "auto"}, T0)
    collector.rows[-1]["payload_solve_time_ms"] = 40.0
    collector.finalize(coord)
    final_now = collector.final
    for coro in pending:
        await coro
    reloaded = debugger.DebugCollector(_disk_hass(folder), "dbg", lambda c: c.close())
    await reloaded.async_load()
    bundle = await collector.async_bundle(coord)
    return final_now, collector, coord, reloaded, bundle


with tempfile.TemporaryDirectory() as tmp:
    final_now, finished, sim_coord, reloaded, bundle = asyncio.run(_finish(tmp))
tests = finished.self_tests or {}
R.check(
    "finalizing stops the collection at once and runs the five self-tests after it",
    final_now and set(tests) == {"stores", "accuracy", "solver", "sensors", "feeds"}
    and all("result" in tests[name] for name in tests),
    str(tests),
)
R.check(
    "the solver self-test solves once without the user's limiter and reports the week's "
    "solve times beside it",
    sim_coord.simulated == [({}, False)]
    and tests["solver"]["result"]["cost_delta"] == 0.0
    and tests["solver"]["result"]["week_solve_ms"]["max"] == 40.0,
    str(tests.get("solver")),
)
R.check(
    "the self-tests read the entry's own store documents from disk",
    acc_key in tests["stores"]["result"]
    and tests["accuracy"]["result"]["stored_samples"] == 3,
    str(tests.get("stores")),
)
R.check(
    "the self-test results survive a reload and ride the bundle's manifest",
    reloaded.self_tests == json.loads(json.dumps(tests))
    and bundle["manifest"]["self_tests"] is finished.self_tests,
    str(reloaded.self_tests)[:200],
)
R.check(
    "a ring carrying its self-test results is inside the debug store's domain",
    admitted("debug", finished.as_dict()),
)
R.check(
    "the feed self-test reads the outage streak through the coordinator's published view",
    tests["feeds"]["result"]["tibber_outage_cycles"] == 12,
    str(tests.get("feeds"))[:200],
)


async def _stale_finish():
    pending: list = []
    collector = debugger.DebugCollector(FakeHass(), "dbg", pending.append)
    collector._read = lambda: _no_stores()
    coord = _SimCoord()
    collector.record(coord, {"mode": "auto"}, T0)
    collector.finalize(coord)
    collector.restart()
    for coro in pending:
        await coro
    return collector


async def _no_stores():
    return {}


stale = asyncio.run(_stale_finish())
R.check(
    "self-test results that finish after the collection restarted are discarded",
    stale.self_tests is None and stale.final is False,
    str(stale.self_tests)[:200],
)


async def _no_view_finish():
    pending: list = []
    collector = debugger.DebugCollector(FakeHass(), "dbg", pending.append)
    collector._read = lambda: _no_stores()
    coord = _Coord()
    collector.record(coord, {"mode": "auto"}, T0)
    collector.finalize(coord)
    for coro in pending:
        await coro
    return collector


no_view = asyncio.run(_no_view_finish())
R.check(
    "the feed self-test of a coordinator that publishes no view reports no streak, "
    "not an error",
    "result" in no_view.self_tests["feeds"]
    and no_view.self_tests["feeds"]["result"]["tibber_outage_cycles"] is None,
    str(no_view.self_tests.get("feeds"))[:200],
)
async def _overtaken():
    pending: list = []
    collector = debugger.DebugCollector(FakeHass(), "dbg", pending.append)
    collector._read = lambda: _no_stores()
    coord = _SimCoord()
    collector.record(coord, {"mode": "auto"}, T0)
    collector.finalize(coord)
    first = pending[-1]
    collector.restart()
    collector.record(coord, {"mode": "auto"}, T0 + timedelta(days=1))
    collector.finalize(coord)
    await first
    for coro in pending:
        if coro is not first:
            coro.close()
    return collector


overtaken = asyncio.run(_overtaken())
R.check(
    "the first collection's self-tests, finishing after a second collection was also "
    "finalized, are discarded",
    overtaken.final and overtaken.self_tests is None,
    str(overtaken.self_tests)[:200],
)
cleared, _ = _collector()
cleared.started_at, cleared.final, cleared.self_tests = T0, True, {"feeds": {"ms": 1.0}}
cleared.restart()
R.check(
    "starting a finished collection again clears its self-test results",
    cleared.self_tests is None and "self_tests" not in cleared.as_dict(),
)
R.check(
    "a loaded ring whose self-test text does not parse carries no results",
    debugger._parsed("{") is None,
)

# -- the inline cap -----------------------------------------------------------
small = {"schema": debugger.BUNDLE_SCHEMA, "manifest": {"cycles": 1}, "cycle_rows": [_row()]}
size = debugger.download_bytes(small) + debugger.DOWNLOAD_HEADROOM_BYTES
inline = debugger.capped(small, "k", cap=size)
summary = debugger.capped(small, "k", cap=size - 1)
R.check(
    "a bundle at the cap is carried inline, and one byte over it is the summary",
    inline is small
    and summary == {"schema": debugger.BUNDLE_SCHEMA, "manifest": {"cycles": 1},
                    "inline": False, "bytes": size, "cap_bytes": size - 1,
                    "store_file": ".storage/k"},
    str(summary),
)
R.check(
    "the inline cap is the pre-study's 8 MB",
    debugger.INLINE_CAP_BYTES == 8 * 1024 * 1024,
)


async def _download(cap):
    coord = FakeCoordinator()
    coord.integration_version = "0.0.0"
    entry = FakeEntry(entry_id="dl", options={CONF_DEBUG_COLLECT: True})
    entry.runtime_data = coord
    hass = _disk_hass(tempfile.gettempdir())
    collector = debugger.DebugCollector(hass, "dl", lambda c: c.close())
    collector.started_at = T0
    collector.rows = [_row()] * 50
    debugger._COLLECTORS[coord] = collector
    saved = debugger.INLINE_CAP_BYTES
    debugger.INLINE_CAP_BYTES = cap
    try:
        return (await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry))["debug"]
    finally:
        debugger.INLINE_CAP_BYTES = saved
        debugger._COLLECTORS.pop(coord, None)


def _ha_download(payload):
    """The diagnostics file as Home Assistant 2025.2.0 writes it: ``json.dumps``
    with ``indent=2`` of its own sections and the entry's payload under ``data``."""
    return len(json.dumps({"home_assistant": {"installation_type": "Home Assistant OS",
                                              "version": "2025.2.0"},
                           "custom_components": {}, "integration_manifest": {},
                           "setup_times": {}, "data": payload},
                          indent=2, default=str).encode())


async def _near_cap():
    """A bundle carried inline at exactly its cap, with the headroom set to the
    size of the rest of the file: the downloaded file must then fit the cap."""
    dt_util.freeze(T0)
    coord = FakeCoordinator()
    coord.integration_version = "0.0.0"
    entry = FakeEntry(entry_id="near", options={CONF_DEBUG_COLLECT: True})
    entry.runtime_data = coord
    hass = _disk_hass(tempfile.gettempdir())
    collector = debugger.DebugCollector(hass, "near", lambda c: c.close())
    collector.started_at = T0
    collector.rows = [_row(indoor_temp=21.0, prices_rows=96, accuracy_sample=_sample(0, 21.0, 20.5))
                      for _ in range(300)]
    debugger._COLLECTORS[coord] = collector
    saved = debugger.INLINE_CAP_BYTES, debugger.DOWNLOAD_HEADROOM_BYTES
    try:
        debugger._COLLECTORS.pop(coord)
        rest = _ha_download(await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry))
        debugger._COLLECTORS[coord] = collector
        bundle = await collector.async_bundle(coord, diagnostics_mod._coordinator_snapshot(coord))
        debugger.DOWNLOAD_HEADROOM_BYTES = rest
        debugger.INLINE_CAP_BYTES = debugger.download_bytes(bundle) + rest
        payload = await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
        return payload["debug"], _ha_download(payload), debugger.INLINE_CAP_BYTES
    finally:
        debugger.INLINE_CAP_BYTES, debugger.DOWNLOAD_HEADROOM_BYTES = saved
        debugger._COLLECTORS.pop(coord, None)
        dt_util.freeze(None)


near, near_file, near_cap = asyncio.run(_near_cap())
R.check(
    "a bundle carried inline at exactly its cap gives a download, written with indent=2 "
    "as Home Assistant writes it, that fits the cap",
    "inline" not in near and len(near["cycle_rows"]) == 300 and near_file <= near_cap,
    f"download {near_file}B against the cap {near_cap}B",
)
R.check(
    "the headroom for the rest of the download is 256 KiB",
    debugger.DOWNLOAD_HEADROOM_BYTES == 256 * 1024,
)

big = asyncio.run(_download(40000))
whole = asyncio.run(_download(debugger.INLINE_CAP_BYTES))
R.check(
    "Download diagnostics carries the summary and the store file when the bundle is over "
    "the cap, and the whole bundle under it",
    big.get("inline") is False and big["store_file"] == f".storage/{DOMAIN}_dl_debug"
    and "cycle_rows" not in big
    and len(whole["cycle_rows"]) == 50 and "inline" not in whole,
    str(big)[:300],
)

# -- the nightly lane's judge of the same two downloads (A16) ----------------
import nightly_ha  # noqa: E402


def _a16(inline_payload, capped_payload,
         encode=lambda o: json.dumps({"data": o}, indent=2).encode(), cap=40000):
    checks = nightly_ha.Checks()
    nightly_ha.check_a16(checks, {"debug": inline_payload}, {"debug": capped_payload},
                         cap, encode)
    return {name: ok for name, (ok, _detail) in checks.results.items()}


def _refuse(_obj):
    raise TypeError("not serializable")


R.check(
    "the nightly A16 judge passes a whole bundle and a summary past the cap, and fails "
    "each swapped, and a bundle its serializer refuses",
    _a16(whole, big) == {"a16:debug_inline": True, "a16:debug_capped": True}
    and _a16(big, whole) == {"a16:debug_inline": False, "a16:debug_capped": False}
    and _a16(whole, big, _refuse) == {"a16:debug_inline": False, "a16:debug_capped": False},
)
R.check(
    "the nightly A16 judge fails a bundle carried whole whose download is over the cap",
    _a16(whole, big, cap=100)["a16:debug_inline"] is False,
)
R.check(
    "the nightly A16 judge fails a download over the cap that does not say it is a summary",
    _a16(whole, {k: v for k, v in big.items() if k != "inline"})["a16:debug_capped"] is False,
)
R.check(
    "the nightly lane demands both A16 checks by name",
    {"a16:debug_inline", "a16:debug_capped"} <= set(nightly_ha.INSIDE_CHECKS),
)

# -- A16's download writer, against Home Assistant's two writer signatures ----
# Run 37753990323 at 816547ef: 2025.2.0's writer returns a StringPayload body,
# which has no len(); stable's inserts data_issues before filename, so the
# five positional arguments left d_id unbound. Both stand-ins below copy those
# two shapes; the body type is aiohttp's: bytes reach it only through write().
import threading  # noqa: E402
import types  # noqa: E402


class _StringPayload:
    def __init__(self, text: str):
        self._bytes = text.encode()

    async def write(self, writer) -> None:
        await writer.write(self._bytes)


class _Response:
    def __init__(self, body, status: int = 200):
        self.body, self.status = body, status


async def _writer_2025_2(hass, data, filename, domain, d_id, sub_id=None):
    return _Response(_StringPayload(json.dumps({"data": data}, indent=2)))


async def _writer_2025_10(hass, data, data_issues, filename, domain, d_id, sub_id=None):
    body = {"data": data} if data_issues is None else {"data": data, "issues": data_issues}
    return _Response(_StringPayload(json.dumps(body, indent=2)))


async def _writer_bytes(hass, data, filename, domain, d_id, sub_id=None):
    return _Response(json.dumps({"data": data}).encode())


async def _writer_500(hass, data, filename, domain, d_id, sub_id=None):
    return _Response(None, status=500)


async def _writer_unknown(hass, data, filename, domain, d_id, mystery):
    return _Response(_StringPayload("{}"))


def _written(fn, payload=None):
    """``ha_download_writer``'s bytes with ``fn`` as HA's writer, or the refusal."""
    import homeassistant.components.diagnostics as ha_diag

    helpers_json = types.ModuleType("homeassistant.helpers.json")
    helpers_json.ExtendedJSONEncoder = json.JSONEncoder
    saved = sys.modules.get("homeassistant.helpers.json")
    sys.modules["homeassistant.helpers.json"] = helpers_json
    ha_diag._async_get_json_file_response = fn
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        writer, name = nightly_ha.ha_download_writer(
            types.SimpleNamespace(loop=loop), DOMAIN, "e1")
        return writer({"k": 1} if payload is None else payload), name
    except Exception as exc:  # noqa: BLE001 - the refusal is the result
        return exc, None
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(5)
        loop.close()
        del ha_diag._async_get_json_file_response
        if saved is None:
            sys.modules.pop("homeassistant.helpers.json", None)
        else:
            sys.modules["homeassistant.helpers.json"] = saved


for _label, _fn in (("2025.2.0", _writer_2025_2), ("2025.10", _writer_2025_10)):
    _got, _name = _written(_fn)
    R.check(
        f"A16's download writer returns the bytes of HA's {_label} writer, whose "
        "body is a payload with no len()",
        isinstance(_got, bytes) and json.loads(_got)["data"] == {"k": 1}
        and _name == "diagnostics._async_get_json_file_response",
        repr(_got)[:200],
    )
_got, _ = _written(_writer_2025_10)
R.check(
    "A16 passes data_issues as the list HA passes, so the file carries its issues section",
    isinstance(_got, bytes) and json.loads(_got).get("issues") == [],
    repr(_got)[:200],
)
_got, _ = _written(_writer_bytes)
R.check(
    "A16's download writer returns a bytes body as it is",
    _got == json.dumps({"data": {"k": 1}}).encode(),
    repr(_got)[:200],
)
_got, _ = _written(_writer_500)
R.check(
    "A16's download writer refuses a response HA's writer failed (status 500, no body)",
    isinstance(_got, Exception) and "500" in str(_got),
    repr(_got)[:200],
)
_got, _ = _written(_writer_unknown)
R.check(
    "A16's download writer refuses a writer parameter it cannot bind, naming it",
    isinstance(_got, Exception) and "mystery" in str(_got),
    repr(_got)[:200],
)

dt_util.freeze(None)
debugger._COLLECTORS.clear()
sys.exit(R.close("DEBUG COLLECT CHECKS"))
