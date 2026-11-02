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
        self.integration_version = None
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
stamped = debugger.cycle_row(_coord(integration_version="7.0.0"), {"mode": "auto"}, T0, None)
R.check(
    "a cycle row carries the release that wrote it, and the debug store admits it (#2209)",
    stamped.get("version") == "7.0.0"
    and debugger._repair({**stamped}, "rows", NEEDS) == stamped
    and debugger._repair({**stamped, "version": 7}, "rows", NEEDS) is None,
    str(stamped),
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
    and button.available is False,
    f"dark={dark} lit={lit} available={available} final={held_collector.final}",
)
# #2809: a finished collection with the option on is dark for another reason
# than the option-off case -- it waits for the action's start, not the option
# it already has. Perturbation: the same collector not final names nothing.
final_reason = button.extra_state_attributes
held_collector.final = False
open_reason = button.extra_state_attributes
held_collector.final = True
R.check(
    "the finalize button on a finished collection names the action's start, "
    "not the option that is already on",
    final_reason == {"waiting_for": "debug_collect_start"}
    and final_reason != dark
    and open_reason == {},
    f"final={final_reason} open={open_reason} off={dark}",
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
SILENT_ROWS = [{**row, "weather_stale_h": 0.0} for row in SILENT]
holey = debugger.feed_health(SILENT_ROWS)
R.check(
    "the feed self-test names the hole the ring shows when cycles published nothing, "
    "where its price and forecast counters read clean",
    holey["row_gaps_h"] == {"n": 11, "min": 0.5, "median": 0.5, "max": 6.0}
    and holey["no_prices"] == 0 and holey["weather_stale_cycles"] == 0
    and holey["weather_stale_h_max"] == 0.0,
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
        bundle = await collector.async_bundle(
            coord, diagnostics_mod._coordinator_snapshot(coord), entry)
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

# -- the replay half (#2271): the export's document, from the recorder -------
import ast  # noqa: E402
import importlib.util  # noqa: E402
import re  # noqa: E402
import types  # noqa: E402

from homeassistant.components import recorder as ha_recorder  # noqa: E402
from homeassistant.components.recorder import history as ha_history  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from heatpump_optimizer import const as const_mod  # noqa: E402
from heatpump_optimizer import replay_doc  # noqa: E402
from heatpump_optimizer.const import PRICE_SOURCE_ENTITY  # noqa: E402

_export_spec = importlib.util.spec_from_file_location(
    "hpo_export_under_test", Path("tools/replay/export.py"))
export = importlib.util.module_from_spec(_export_spec)
_export_spec.loader.exec_module(export)
CONF = export.entry_keys(*export.default_const_paths())
TOKEN = "tibber-secret-0123456789abcdef"


def _state(value, at, attrs=None, reported=None):
    return types.SimpleNamespace(state=value, attributes=dict(attrs or {}), last_updated=at,
                                 last_reported=reported)


def _replay_install(*, recorder=True, price_source=PRICE_SOURCE_ENTITY, tibber=(), plant=None,
                    plant_entry=None, plant_state=None):
    """An entry reading two thermometers and a price entity, with a token, an exact
    coordinate and a family calendar in its config, a day of recorded states, and
    one entity it publishes."""
    hass = _disk_hass(tempfile.gettempdir())
    hass.config.time_zone = "Europe/Stockholm"
    if recorder:
        ha_recorder.install(hass)
    entry = FakeEntry(entry_id="rp", data={
        "tibber_token": TOKEN, "price_source": price_source,
        "price_entity": "sensor.nordpool", "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor", "solar_location": {"latitude": 59.334591,
                                                                   "longitude": 18.063240},
        "away_calendar": "calendar.family", **(plant_entry or {}),
    }, options={CONF_DEBUG_COLLECT: True})
    entry.minor_version = 1  # a real entry carries one; harness.FakeEntry does not
    reg = er.async_get(hass)
    reg.add("sensor.hpo_plan", unique_id="p", config_entry_id="rp", platform=DOMAIN)
    for entity_id, home in tibber:
        reg.add(entity_id, unique_id=home, platform="tibber", translation_key="electricity_price")
    # A minute past each hour: upstream returns a state stamped exactly at the
    # window's start in neither of its two queries.
    hours = [T0 + timedelta(hours=h, minutes=1) for h in range(24)]
    attrs = {"unit_of_measurement": "°C", "friendly_name": "Anna's room",
             "entity_picture": "/api/camera?token=abcdef0123456789"}
    ha_history.record(hass, "sensor.indoor", [
        _state(plant_state or str(20 + h % 3), at, {**attrs, **(plant or {})})
        for h, at in enumerate(hours)])
    ha_history.record(hass, "sensor.outdoor", [_state("-3.5", T0 - timedelta(days=1), attrs)])
    ha_history.record(hass, "sensor.nordpool", [_state("1.25", at) for at in hours])
    ha_history.record(hass, "calendar.family", [_state("on", T0)])
    ha_history.record(hass, "sensor.hpo_plan", [_state("auto", at) for at in hours])
    for entity_id, _home in tibber:
        ha_history.record(hass, entity_id, [_state("0.9", at) for at in hours])
    coord = FakeCoordinator()
    coord.integration_version = "7.0.0"
    entry.runtime_data = coord
    collector = debugger.DebugCollector(hass, "rp", lambda c: c.close())
    collector.started_at = T0
    collector.rows = [_row()]
    debugger._COLLECTORS[coord] = collector
    return hass, entry, coord, collector


async def _replay_download(cap=None, raw=False, **kw):
    """The download, or with ``raw`` the bundle as the cap measures it, before the
    download's own redaction."""
    hass, entry, coord, collector = _replay_install(**kw)
    dt_util.freeze(T0 + timedelta(days=1))
    saved = debugger.INLINE_CAP_BYTES
    debugger.INLINE_CAP_BYTES = saved if cap is None else cap
    try:
        if raw:
            return await collector.async_bundle(
                coord, diagnostics_mod._coordinator_snapshot(coord), entry)
        return await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    finally:
        debugger.INLINE_CAP_BYTES = saved
        debugger._COLLECTORS.pop(coord, None)
        dt_util.freeze(None)


def _check_download(replay):
    """``tests/replay.py``'s check mode -- ``export.check_file`` -- on the replay half
    as the download carries it."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, "replay.json")
        path.write_text(json.dumps(replay))
        return export.check_file(path, CONF)


download = asyncio.run(_replay_download())
replay = download["debug"]["replay"]
blob = json.dumps(download)
R.check(
    "Download diagnostics fills the bundle's replay half with an hpo-replay/1 document "
    "that the export's check mode passes",
    isinstance(replay, dict) and replay["format"] == replay_doc.FORMAT
    and _check_download(replay) == [],
    str(_check_download(replay) if isinstance(replay, dict) else download["debug"]["manifest"]),
)
R.check(
    "the replay half carries the entry's inputs and what it publishes, read through the "
    "recorder's history API: the state in force at the window's start, then the window; "
    "every id masked to its role, and what it publishes to the entry-keyed hash",
    set(replay["states"]) == {"sensor.indoor_temp", "sensor.outdoor_temp", "sensor.price",
                              replay_doc.hashed_id("sensor.hpo_plan", "rp")}
    and replay["published"] == [replay_doc.hashed_id("sensor.hpo_plan", "rp")]
    and replay["price_series_entity"] is None
    and [row[1] for row in replay["states"]["sensor.outdoor_temp"]] == ["-3.5"]
    and len(replay["states"]["sensor.indoor_temp"]) == 24
    and replay["recorder_schema"] == ha_recorder.Recorder.schema_version
    and replay["time_zone"] == "Europe/Stockholm",
    str({k: replay.get(k) for k in ("published", "price_series_entity", "window")}),
)
R.check(
    "the replay half's window is the collection's: from its start to the download",
    replay["window"] == {"start": T0.isoformat(), "end": (T0 + timedelta(days=1)).isoformat()}
    and download["debug"]["manifest"]["replay"] == (
        f"{T0.isoformat()} .. {(T0 + timedelta(days=1)).isoformat()}"),
    str(replay["window"]),
)
R.check(
    "the replay half drops the token, the friendly name and the tokenised picture, "
    "cuts the coordinate, and carries no person or calendar id anywhere",
    TOKEN not in blob and "Anna" not in blob and "abcdef0123456789" not in blob
    and "59.334591" not in blob and "calendar.family" not in blob
    and replay["entry"]["data"].get("away_calendar") is None,
    str(replay["entry"]),
)
import nightly_ha  # noqa: E402

a10 = nightly_ha.Checks()
nightly_ha.check_a10_payload(a10, download, (TOKEN,))
R.check(
    "nightly_ha's A10 rule passes the whole download the replay half rides in",
    not a10.failures(), str(a10.results),
)
planted = json.loads(json.dumps(replay))
planted["states"]["sensor.indoor_temp"][0][2] = {"access_token": TOKEN}
planted_found = export.violations(planted, CONF)
R.check(
    "the null control: a credential planted back into the generated replay half is "
    "refused by the same check",
    bool(planted_found) and _check_download(planted) != [],
    "; ".join(planted_found[:2]),
)


def _leak(name, values):
    """``values`` planted where ``tests/replay.py`` plants them: the entry, a recorded
    state, or a recorded state's attributes."""
    if name.startswith("entry_"):
        return asyncio.run(_replay_download(plant_entry=values))["debug"]
    if name.startswith("state_"):
        return asyncio.run(_replay_download(plant_state=values["state"]))["debug"]
    return asyncio.run(_replay_download(plant=values))["debug"]


import replay as replay_lane  # noqa: E402

probe_outcomes = {"written": 0, "refused": 0}
for name, values in replay_lane.LEAK_PROBES.items():
    probed = _leak(name, values)
    probed_blob = json.dumps(probed["replay"])
    texts = [t for t in replay_lane._probe_texts(values) if t in probed_blob]
    probe_outcomes["refused" if probed["replay"] is None else "written"] += 1
    R.check(
        f"the nightly leak probe {name} does not survive into the replay half, which "
        "is either written and passes check mode or refused with the reason in the manifest",
        not texts and (_check_download(probed["replay"]) == [] if probed["replay"] is not None
                       else bool(probed["manifest"]["replay"])),
        f"survived={texts} manifest={probed['manifest'].get('replay')}",
    )
print(f"RESULT leak_probes_through_download={len(replay_lane.LEAK_PROBES)} "
      f"written={probe_outcomes['written']} refused={probe_outcomes['refused']} unit=count")

refused = asyncio.run(_replay_download(recorder=False))
R.check(
    "with no recorder set up the replay half is empty and the manifest says why",
    refused["debug"]["replay"] is None
    and refused["debug"]["manifest"]["replay"] == "no recorder is set up",
    str(refused["debug"]["manifest"].get("replay")),
)
tibber = asyncio.run(_replay_download(
    price_source="tibber", tibber=[("sensor.electricity_price_home", "96a14971")]))
R.check(
    "with the Tibber source the replay half takes the price series from the Tibber "
    "price sensor, the export's own choice, masked as the price series (the entry's "
    "own price_entity holds sensor.price)",
    tibber["debug"]["replay"]["price_series_entity"] == "sensor.price_series"
    and "sensor.price_series" in tibber["debug"]["replay"]["states"]
    and "electricity_price_home" not in json.dumps(tibber["debug"]["replay"]),
    str(tibber["debug"]["manifest"].get("replay")),
)
# R10-REPLAY-REAL-DAY: the home's name or street address rides in entity ids (the
# Tibber price sensor's id is derived from the home's address), in friendly names
# and in text. Invented here; the sealed replay half must carry none of it.
street = asyncio.run(_replay_download(
    price_source="tibber", tibber=[("sensor.electricity_price_exempelgatan_12", "96a14971")],
    plant={"friendly_name": "Exempelgatan 12 vardagsrum"}, plant_state="Exempelgatan 12B"))
street_replay = street["debug"]["replay"]
R.check(
    "Download diagnostics seals a recorder holding an address-like home name masked: no "
    "id, name or text of it survives in the replay half, the Tibber series is the price "
    "series role, and the half passes the export's check mode",
    street_replay is not None
    and "exempelgatan" not in json.dumps(street_replay).lower()
    and street_replay["price_series_entity"] == "sensor.price_series"
    and _check_download(street_replay) == [],
    str(street["debug"]["manifest"].get("replay")),
)
no_price = asyncio.run(_replay_download(price_source="tibber"))
R.check(
    "with the Tibber source and no price sensor the replay half is refused as the export "
    "refuses, with the reason in the manifest",
    no_price["debug"]["replay"] is None
    and "Tibber price source needs a recorded price sensor"
    in no_price["debug"]["manifest"]["replay"],
    str(no_price["debug"]["manifest"].get("replay")),
)
whole = asyncio.run(_replay_download(raw=True))
whole_size = debugger.download_bytes(whole) + debugger.DOWNLOAD_HEADROOM_BYTES
short = asyncio.run(_replay_download(cap=whole_size - 1))
R.check(
    "a replay half that would take the download past the inline cap gives way to the "
    "newest shorter window that fits, and the bundle stays inline",
    "inline" not in short["debug"] and short["debug"]["replay"] is not None
    and short["debug"]["replay"]["window"]["start"] == (T0 + timedelta(hours=18)).isoformat()
    and len(short["debug"]["replay"]["states"]["sensor.indoor_temp"]) == 7
    and debugger.download_bytes(short["debug"]) + debugger.DOWNLOAD_HEADROOM_BYTES
    <= whole_size - 1,
    str(short["debug"].get("manifest", {}).get("replay")),
)
bare_size = debugger.download_bytes({**whole, "replay": None,
                                     "manifest": {**whole["manifest"],
                                                  "replay": "over the inline cap at every "
                                                  "window tried"}})
none_fit = asyncio.run(_replay_download(cap=bare_size + debugger.DOWNLOAD_HEADROOM_BYTES + 10))
R.check(
    "when no window fits the inline cap the replay half is empty, the manifest says so, "
    "and the rest of the bundle stays inline",
    "inline" not in none_fit["debug"] and none_fit["debug"]["replay"] is None
    and none_fit["debug"]["manifest"]["replay"] == "over the inline cap at every window tried",
    str(none_fit["debug"].get("manifest", {}).get("replay")),
)
at_cap = asyncio.run(_replay_download(cap=whole_size))
R.check(
    "a download landing exactly on the inline cap keeps the whole window",
    at_cap["debug"]["replay"] is not None
    and at_cap["debug"]["replay"]["window"]["start"] == T0.isoformat(),
    str(at_cap["debug"].get("manifest", {}).get("replay")),
)
R.check(
    "a person or calendar id leaves a list as well as a value, at any depth",
    debugger._public({"x": ["sensor.a", "calendar.family", "person.anna"],
                      "y": {"z": "person.anna"}, "n": 3})
    == {"x": ["sensor.a"], "y": {"z": None}, "n": 3},
)
_seen = T0 + timedelta(minutes=5)
R.check(
    "a recorded row carries last_reported only when it is later than last_updated",
    debugger._record(_state("1", T0, reported=T0))[3] is None
    and debugger._record(_state("1", T0, reported=_seen))[3] == _seen.isoformat()
    and debugger._record(_state("1", T0))[3] is None,
)
later = debugger.replay_window(T0, T0 + timedelta(days=30))
fresh = debugger.replay_window(None, T0)
R.check(
    "a finished collection's replay window is its own week, and one with no start is "
    "the week before the download",
    later == (T0, T0 + debugger.COLLECT_SPAN) and fresh == (T0 - debugger.REPLAY_SPAN, T0)
    and debugger.REPLAY_SPAN == timedelta(days=7),
    str((later, fresh)),
)
R.check(
    "one copy of the rules: the export's allowlist, sanitiser and violations are the "
    "integration's replay_doc, loaded from the package's own file",
    Path(export._doc.__file__).resolve() == Path(replay_doc.__file__).resolve()
    and export.violations.__code__.co_filename == replay_doc.violations.__code__.co_filename
    and not re.search(r"^def (violations|sanitise|text_ok|clean_value|tibber_price_candidates)\b",
                      Path("tools/replay/export.py").read_text(), re.M),
)
_tree = ast.parse(Path(replay_doc.__file__).read_text())
_imports = {(n.module if isinstance(n, ast.ImportFrom) else a.name).split(".")[0]
            for n in ast.walk(_tree) if isinstance(n, (ast.Import, ast.ImportFrom))
            for a in n.names} | {"." for n in ast.walk(_tree)
                                 if isinstance(n, ast.ImportFrom) and n.level}
R.check(
    "replay_doc imports the standard library alone, so the export loads it by path "
    "inside the Home Assistant container",
    _imports <= set(sys.stdlib_module_names) | {"__future__"}, str(sorted(_imports)),
)
R.check(
    "replay_doc's price-source literal is const's",
    replay_doc.PRICE_SOURCE_ENTITY == PRICE_SOURCE_ENTITY,
)
R.check(
    "the download's entry allowlist is the one the export reads out of const.py, values "
    "wrapped onto a second line included",
    replay_doc.conf_keys(vars(const_mod)) == CONF and len(CONF) > 50
    and {"heat_pump_capacity_limited_entity", "internal_gains_learning_enabled"} <= CONF,
    f"{len(replay_doc.conf_keys(vars(const_mod)))} against {len(CONF)}",
)


# -- replay_doc's rules, each at the inputs that separate its branches ----------
# The download above drives the rules with one install; these drive the edges it
# never reaches (a non-dict payload, a malformed series row, a refusal by
# ``seal``), so a rule changed in the one shared copy fails here, in the gate,
# and not only in the nightly lane's tests/replay.py.

_D = replay_doc._DROP


def _unrecorded(want: list, got: list) -> str:
    """A leak check's detail: which expected values, by position, were not recorded,
    and how many were recorded beyond them.

    Like ``seal``'s refusal it counts and never echoes a value: one expected under a
    credential key is a credential, and a check's detail is a CI log.
    """
    missing = [i for i, w in enumerate(want) if w not in got]
    extra = sum(1 for g in got if g not in want)
    return f"expected value(s) {missing} not recorded; {extra} recorded beyond them"


R.check(
    "replay_doc.numeric admits a number or its spelling and nothing else",
    [replay_doc.numeric(v) for v in ("1.5", 3, 2.5, "warm", None, ["1"])]
    == [True, True, True, False, False, False],
)
R.check(
    "replay_doc.json_decimal_places counts the JSON spelling's decimals, a string's as "
    "written, and answers None for a bool, a word or a non-number",
    [replay_doc.json_decimal_places(v) for v in
     (True, 1.25, 3, "59.334591", "5", "north", None, [1.5])]
    == [None, 2, 0, 6, 1, None, None, None],
)
_dropped: list = []
_cleaned = replay_doc.clean_value(
    {"api_key": "s3cret-value", "Bad Key": "x", "latitude": "north", "lat": "59.334591",
     "longitude": 18.063240, "rows": ["auto", "https://nas.example.se/cam", 7], "on": True},
    _dropped)
R.check(
    "replay_doc.clean_value drops a credential-named or malformed key, cuts a coordinate "
    "or nulls one that is no number, recurses into lists, and records what it dropped",
    _cleaned == {"latitude": None, "lat": 59.33, "longitude": 18.06,
                 "rows": ["auto", None, 7], "on": True}
    and _dropped == ["s3cret-value", "north", "https://nas.example.se/cam"],
    f"kept keys {sorted(_cleaned)}; "
    + _unrecorded(["s3cret-value", "north", "https://nas.example.se/cam"], _dropped),
)
_secret_drop: list = []
replay_doc.clean_value({"api_key": None, "password": True, "auth": {"user": "bob123456"},
                        "token": ["abc123456", 42]}, _secret_drop)
R.check(
    "everything under a credential-named key is recorded for the leak check, in a nested "
    "object or a list too, and a null or a bool under one is not",
    _secret_drop == ["bob123456", "abc123456", "42"],
    _unrecorded(["bob123456", "abc123456", "42"], _secret_drop),
)
_shape_drop: list = []
_shape_cut = replay_doc._keep_keys(
    {"x_entities": ["sensor.a", "https://nas.example.se/cam"]}, frozenset({"x_entities"}),
    _shape_drop, replay_doc._entry_shape)
R.check(
    "a value its shape cut down has what was cut recorded for the leak check",
    _shape_cut == {"x_entities": ["sensor.a"]} and _shape_drop == ["https://nas.example.se/cam"],
    f"{_shape_cut} dropped={_shape_drop}",
)
_series_in = [{"start": "2026-10-18T00:00:00+00:00", "value": 1.2, "note": "spot"},
              "junk", {"start": "2026-10-18T01:00:00+00:00"},
              {"starts_at": "2026-10-18", "total": True},
              {"end": "2026-10-18T02:00:00Z", "price": 3}]
R.check(
    "each attribute keeps only its shape: a number, a snake_case word, word-like "
    "options, a series of time-and-number rows, an ISO time",
    [replay_doc._number(v) for v in (None, 1.5, 2, True, "1")] == [None, 1.5, 2, _D, _D]
    and [replay_doc._snake(v) for v in (None, "heat", "Heat Mode", 4)] == [None, "heat", _D, _D]
    and [replay_doc._unit(v) for v in (None, "°C", "abcdefghijklmnop", "abcdefghijklmnopq", 3)]
    == [None, "°C", "abcdefghijklmnop", _D, _D]
    and replay_doc._options(None) is None and replay_doc._options("Eco") is _D
    and replay_doc._options(["Eco", "Mode 2", "x@y", 5]) == ["Eco"]
    and replay_doc._series(None) is None and replay_doc._series("x") is _D
    and replay_doc._series(_series_in) == [
        {"start": "2026-10-18T00:00:00+00:00", "value": 1.2},
        {"end": "2026-10-18T02:00:00Z", "price": 3}]
    and [replay_doc._time(v) for v in (None, "2026-10-18", "tomorrow", 5)]
    == [None, "2026-10-18", _D, _D],
    str(replay_doc._series(_series_in)),
)
R.check(
    "an entry key naming entities holds entity ids only: a bad id leaves the list, "
    "a single string or a name in an _entity key is refused, other keys pass as they are",
    replay_doc._entry_shape("x_entities", ["sensor.a", "Bad", 3]) == ["sensor.a"]
    and replay_doc._entry_shape("x_entities", "sensor.a") is _D
    and replay_doc._entry_shape("x_entity", "Anna") is _D
    and [replay_doc._entry_shape("x_entity", v) for v in (None, "", "sensor.a")]
    == [None, "", "sensor.a"]
    and replay_doc._entry_shape("mode", "Anna") == "Anna",
)
_bad = {"entry": {"data": {"not_a_conf_key": 1, "Bad Key": 2,
                           "indoor_temp_entity": "Anna's room"}, "options": None},
        "states": {"plainkey": [["t", "1", None, None]],
                   "sensor.a": [["t", "1", "attrs", None], ["t", "1", {"colour": "red"}, None],
                                ["t", "1", {"unit_of_measurement": 3}, None], "short"]},
        "loc": {"Latitude": 59.334591, "lon": 18.06}}
_found = replay_doc.violations(_bad, CONF)
R.check(
    "replay_doc.violations names each broken rule: a coordinate past two decimals, an "
    "entry key outside the allowlist or malformed, an entity key holding a name, a "
    "state key that is no entity id, attributes that are no object, outside the "
    "allowlist or the wrong shape",
    sorted(_found) == sorted([
        "loc.Latitude=59.334591: 6 decimals",
        "entry.data.not_a_conf_key: not an entry key of this integration",
        "entry.data.Bad Key: not an entry key of this integration",
        "entry.data.indoor_temp_entity: must hold entity ids only",
        "states.plainkey: not an entity id",
        "states.sensor.a[0]: attributes are not an object",
        "states.sensor.a[1].colour: attribute outside the allowlist",
        "states.sensor.a[2].unit_of_measurement: not the shape this attribute has",
        "entry.data.indoor_temp_entity: text outside the allowlist",
    ]) and replay_doc.violations(["auto", "https://nas.example.se/cam"]) == [
        "[1]: text outside the allowlist"]
    and "entry.data.not_a_conf_key: not an entry key of this integration"
    not in replay_doc.violations({"entry": {"data": {"not_a_conf_key": 1}}})
    and replay_doc.violations({"states": {"sensor.b": [["t", "1"]]}}) == [],
    "; ".join(_found),
)
R.check(
    "replay_doc.mapped_entities finds entity ids at any depth, in lists too",
    replay_doc.mapped_entities({"a": ["sensor.x", {"b": "climate.y"}], "c": "Anna",
                                "d": ("sensor.z",)}) == {"sensor.x", "climate.y"},
)


def _sealed(raw):
    try:
        return replay_doc.seal(raw, CONF)
    except replay_doc.Refused as err:
        return err


def _raw_doc(token="secretvalue123", **states):
    return replay_doc.document(
        time_zone="UTC", window=("a", "b"), recorder_schema=None,
        entry={"data": {"tibber_token": token}}, inputs=(), published=(),
        price_series_entity=None, states=states)


# A copy in a string is dropped with it; a number cannot be, so its copy refuses.
_copied = _sealed(_raw_doc(**{"sensor.a": [["t", "secretvalue123", None, None]]}))
_leaked = _sealed(_raw_doc(123456789, **{"sensor.a": [["t", 123456789, None, None]]}))
# Six characters is the shortest dropped value the leak check looks for again.
_leaked_six = _sealed(_raw_doc(123456, **{"sensor.a": [["t", 123456, None, None]]}))
_short = _sealed(_raw_doc(12345, **{"sensor.a": [["t", 12345, None, None]]}))
_unfit = _sealed(_raw_doc(plainkey=[["t", "1", None, None]]))
_ok = _sealed(_raw_doc(**{"sensor.a": [["t", "1", None, None]]}))
R.check(
    "replay_doc.seal drops a string copy of a dropped credential, refuses a document "
    "where a copy survives as a number (naming its place, not its value), and one whose "
    "sanitised form still breaks a rule, and writes a clean one",
    isinstance(_copied, dict) and "secretvalue123" not in json.dumps(_copied)
    and isinstance(_leaked, replay_doc.Refused) and "1 dropped credential value(s)" in str(_leaked)
    and ".state" in str(_leaked) and "123456789" not in str(_leaked)
    and isinstance(_leaked_six, replay_doc.Refused) and isinstance(_short, dict)
    and isinstance(_unfit, replay_doc.Refused)
    and "states.plainkey: not an entity id" in str(_unfit)
    and isinstance(_ok, dict) and _ok["entry"]["data"] == {}
    and _ok["states"] == {replay_doc.hashed_id("sensor.a", ""): [["t", "1", None, None]]},
    f"{_leaked if isinstance(_leaked, replay_doc.Refused) else type(_leaked).__name__} "
    f"{_unfit!r}",
)
_homes = [{"entity_id": f"sensor.price_{h}", "platform": "tibber", "unique_id": h,
           "translation_key": "electricity_price"} for h in ("home1", "home2")]
try:
    _none_chosen = replay_doc.choose_price_entity({}, _homes, lambda e: True)
except replay_doc.Refused as err:
    _none_chosen = err
R.check(
    "with two live Tibber homes the entry's own price_entity decides, and without one "
    "the choice is refused with both candidates listed",
    replay_doc.choose_price_entity({"price_entity": "sensor.price_home2"}, _homes,
                                   lambda e: True) == "sensor.price_home2"
    and replay_doc.choose_price_entity({"price_entity": "sensor.price_home2"}, _homes,
                                       lambda e: e.endswith("home1")) == "sensor.price_home1"
    and isinstance(_none_chosen, replay_doc.Refused)
    and "found 2 usable of 2" in str(_none_chosen)
    and "sensor.price_home1, sensor.price_home2" in str(_none_chosen),
    repr(_none_chosen),
)


# -- the nightly lane's judge of the same two downloads (A16) ----------------


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
# -- R10-DIAG-REDACT: a redacted value is redacted wherever else it reaches ---
# The download's redaction is keyed: ``tibber_token`` and ``name`` are blanked
# and ``latitude``/``longitude`` coarsened. D15's production triage found
# dropped credential values surviving elsewhere in the same payload, so each
# value the keyed passes remove is planted below in every section of the
# download -- under an unredacted key, inside a message, as a key, and as a
# number under a key the coarsening does not name -- and none may come back.
NAME = "Villa Solbacken"
EXACT = ("59.334591", "18.06324")  # the install's solar_location, as text
OPTIONS_TOKEN = "tibber-options-fedcba9876543210"  # a token reauth saved in options
PRIVATE = (TOKEN, OPTIONS_TOKEN, NAME, *EXACT)


def _leak_text(tag):
    return f"{tag}: {TOKEN} {OPTIONS_TOKEN} for {NAME} at {EXACT[0]},{EXACT[1]}"


def _value_pass(on):
    """``diagnostics._without_values`` as it is, or switched off (the control)."""
    saved = diagnostics_mod.__dict__.get("_without_values")
    if not on and saved is not None:
        diagnostics_mod._without_values = lambda value, private: value
    return saved


def _value_pass_restore(saved):
    if saved is not None:
        diagnostics_mod._without_values = saved


async def _planted_download(value_pass=True):
    """The replay install with every private value planted in every section."""
    hass, entry, coord, collector = _replay_install(plant_entry={
        "name": NAME, "ecl110_state_topic": f"ecl/{TOKEN}/state"})
    entry.options = {**entry.options, "tibber_token": OPTIONS_TOKEN}
    folder = tempfile.mkdtemp()
    (Path(folder) / ".storage").mkdir()
    hass.config.path = lambda *parts: str(Path(folder, *parts))
    (Path(folder) / ".storage" / debugger.store_keys("rp")["accuracy"]).write_text(
        json.dumps({"version": 1, "data": {"note": _leak_text("store"),
                                           "lat": float(EXACT[0])}}))
    coord.mode = _leak_text("mode")
    coord.data = {"insight": {"last_diagnosis": _leak_text("diagnosis")},
                  "problem_messages": [_leak_text("input")],
                  "current_action": _leak_text("plan"),
                  "dhw_cooling_rate": _leak_text("learning")}
    collector.rows = [_row(note=_leak_text("row"), lon=float(EXACT[1]), **{TOKEN: 1})]
    collector.snapshots = [{"t": T0.isoformat(), "cycle": 1,
                            "data": json.dumps({"msg": _leak_text("snapshot")})}]
    collector.self_tests = {"feeds": {"error": _leak_text("self-test")}}
    dt_util.freeze(T0 + timedelta(days=1))
    saved = _value_pass(value_pass)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    finally:
        _value_pass_restore(saved)
        debugger._COLLECTORS.pop(coord, None)
        dt_util.freeze(None)


async def _clean_download(value_pass):
    saved = _value_pass(value_pass)
    try:
        return await _replay_download()
    finally:
        _value_pass_restore(saved)


def _leaves(node, path=""):
    """``(path, key or value)`` for every key and every leaf of ``node``."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield f"{path}.{key}", key
            yield from _leaves(value, f"{path}.{key}")
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from _leaves(value, f"{path}[{i}]")
    else:
        yield path, node


def _private(text):
    return any(value in str(text) for value in PRIVATE)


def _carrying(download):
    """Every path of ``download`` whose key or value still holds a private value."""
    return sorted({path for path, leaf in _leaves(download) if _private(leaf)})


planted_dl = asyncio.run(_planted_download())
planted_open = asyncio.run(_planted_download(value_pass=False))
planted_paths = _carrying(planted_open)
# The census of sections is the download's own keys, and the bundle's, so a
# section a later change adds is refused here until the fixture plants in it.
# The exempt ones carry no text the install supplies: a constant, the names of
# config keys, the version stamps, the export's clock, and the replay half, which ``seal`` refuses
# rather than write with a dropped value in it (the checks above).
EXEMPT = {".exported_at", ".entry", ".config_overridden_by_options", ".domain",
          ".debug.schema", ".debug.replay"}
SECTIONS = {f".{key}" for key in planted_open if key != "debug"} | {
    f".debug.{key}" for key in planted_open["debug"]}
_unplanted = sorted(section for section in SECTIONS - EXEMPT if not any(
    path == section or path.startswith((f"{section}.", f"{section}[")) for path in planted_paths))
R.check(
    "the fixture plants a private value in every section of the download and of its "
    "debug bundle, bar the exempt ones, and every exempt one is still a section",
    _unplanted == [] and EXEMPT <= SECTIONS,
    f"unplanted={_unplanted} exempt-gone={sorted(EXEMPT - SECTIONS)}",
)
R.check(
    "Download diagnostics carries none of the values its redaction removes -- the "
    "token, the entry name, the exact coordinate -- in any section, under any key",
    _carrying(planted_dl) == [],
    "; ".join(_carrying(planted_dl)),
)
_untouched = {(path, repr(leaf)) for path, leaf in _leaves(planted_dl)}
_moved = [path for path, leaf in _leaves(planted_open)
          if not _private(path) and not _private(leaf) and (path, repr(leaf)) not in _untouched]
R.check(
    "the null control: every field of the planted download that holds no private value "
    "comes out as it would without the value pass",
    _moved == [],
    "; ".join(_moved[:5]),
)
R.check(
    "the null control: with nothing private planted elsewhere, the value pass leaves the "
    "download byte-identical",
    json.dumps(asyncio.run(_clean_download(True)), sort_keys=True)
    == json.dumps(asyncio.run(_clean_download(False)), sort_keys=True),
)

_six = "x" * replay_doc.LEAK_MIN_CHARS
R.check(
    "the value pass searches for a removed value at the leak check's shortest length and "
    "not one character under it, for a coordinate only when the coarsening cut it, and "
    "never for a flag",
    diagnostics_mod._private_values([{"name": _six, "x": [{"name": _six[1:]}],
                                      "tibber_token": True,
                                      "solar_location": {"latitude": -123.4,
                                                         "longitude": float(EXACT[1])}}])
    == {_six, EXACT[1]},
    str(diagnostics_mod._private_values([{"name": _six, "x": [{"name": _six[1:]}]}])),
)
R.check(
    "the value pass redacts a private value inside text, as a key, and as a number, in a "
    "tuple too, and leaves a flag and any other number alone",
    diagnostics_mod._without_values(
        {"a": ("x abcdef y", 18.06324, True, 7), "abcdef": 1}, frozenset({"abcdef", "18.06324"}))
    == {"a": ["x **REDACTED** y", "**REDACTED**", True, 7], "**REDACTED**": 1},
)
_stamp = T0 + timedelta(minutes=7)  # a leaf neither text nor a number
R.check(
    "a removed leaf of any other type is searched for and redacted by its text, as a "
    "number is, and a None, shorter than any value searched for, is left alone",
    diagnostics_mod._private_values({"name": _stamp, "tibber_token": None}) == {str(_stamp)}
    and diagnostics_mod._without_values({"at": _stamp, "none": None, "n": f"{_stamp}"},
                                        frozenset({str(_stamp)}))
    == {"at": "**REDACTED**", "none": None, "n": "**REDACTED**"},
    str(diagnostics_mod._private_values({"name": _stamp, "tibber_token": None})),
)

# -- #2814, P119: the download says when it was taken, and how old each part is --
# The payload's ``plan_age_minutes`` is the plan's age when the payload was
# built; the owner's bundle read 0.8 for a plan 14 minutes old at the export.
# The finished collection's rows are as old as the collection's end, which the
# manifest did not say: ``days`` is the configured length.
from heatpump_optimizer import drift  # noqa: E402

PUBLISHED = T0 + timedelta(days=10)


async def _aged_download(after, rows=()):
    """The download ``after`` past a plan solved at ``PUBLISHED`` whose payload
    still says 0.8 minutes, with ``rows`` in a finished collection."""
    coord = FakeCoordinator({"last_optimization": PUBLISHED, "plan_age_minutes": 0.8})
    coord.integration_version = "0.0.0"
    entry = FakeEntry(entry_id="aged", options={CONF_DEBUG_COLLECT: True})
    entry.runtime_data = coord
    hass = _disk_hass(tempfile.gettempdir())
    collector = debugger.DebugCollector(hass, "aged", lambda c: c.close())
    collector.started_at, collector.final, collector.rows = T0, True, list(rows)
    debugger._COLLECTORS[coord] = collector
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    finally:
        debugger._COLLECTORS.pop(coord, None)
        dt_util.freeze(None)


_rows = [{"t": (T0 + timedelta(hours=h)).isoformat(), "mode": "auto"} for h in (0, 3, 1)]
aged = asyncio.run(_aged_download(timedelta(minutes=14), _rows))
fresh = asyncio.run(_aged_download(timedelta(minutes=1)))
ahead = asyncio.run(_aged_download(timedelta(minutes=-5)))
R.check(
    "the download's plan age is measured at the export: 14 minutes after the solve it "
    "reads 14, whatever the payload said when it was published",
    aged["plan"]["plan_age_minutes"] == 14.0,
    str(aged["plan"]["plan_age_minutes"]),
)
R.check(
    "the null control: a plan solved a minute before the export reads 1",
    fresh["plan"]["plan_age_minutes"] == 1.0,
    str(fresh["plan"]["plan_age_minutes"]),
)
R.check(
    "a plan stamped ahead of the export clock has an unknowable age, never 0, and a "
    "payload with no solve has none",
    ahead["plan"]["plan_age_minutes"] is None
    and diagnostics_mod._plan_summary({}, PUBLISHED)["plan_age_minutes"] is None,
    f'{ahead["plan"]["plan_age_minutes"]}',
)
R.check(
    "the download carries its own export time, outside the debug half, read from the "
    "clock the debug manifest's generated_at reads",
    aged["exported_at"] == (PUBLISHED + timedelta(minutes=14)).isoformat()
    == aged["debug"]["manifest"]["generated_at"],
    f'{aged.get("exported_at")} / {aged["debug"]["manifest"]["generated_at"]}',
)
_manifest_window = {key: aged["debug"]["manifest"].get(key)
           for key in ("first_row_at", "last_row_at", "span_hours", "age_hours")}
R.check(
    "the manifest labels the finished collection: its first and last row, the 3 h the "
    "rows span, and the last row's age at the export, not the configured 7 days",
    _manifest_window == {"first_row_at": T0.isoformat(),
                "last_row_at": (T0 + timedelta(hours=3)).isoformat(),
                "span_hours": 3.0,
                "age_hours": round((timedelta(days=10, minutes=14)
                                    - timedelta(hours=3)).total_seconds() / 3600.0, 1)},
    str(_manifest_window),
)
R.check(
    "a collection with no row has no window, and a row stamped ahead of the export "
    "clock has an unknowable age, never 0",
    set(fresh["debug"]["manifest"][key] for key in _manifest_window) == {None}
    and debugger.collection_window(_rows, T0)["age_hours"] is None,
    str(debugger.collection_window(_rows, T0)),
)
R.check(
    "a stored instant's age is the seconds to now, none for text that does not parse, "
    "and none for an instant ahead of now",
    drift.stored_age_seconds(T0.isoformat(), T0 + timedelta(minutes=2)) == 120.0
    and drift.stored_age_seconds(T0, T0) == 0.0
    and drift.stored_age_seconds("garbage", T0) is None
    and drift.stored_age_seconds(T0 + timedelta(seconds=1), T0) is None,
)

# -- #2814's residue: the input ages, the stale flag and the self-tests' run time --
# The payload's input ages are their ages when the inputs were read and its
# ``plan_stale`` is judged then too; the stored self-test results carried no time.


async def _published_download(after, solved_before, interval=None):
    """The download ``after`` past a payload published at ``PUBLISHED``, for a plan
    solved ``solved_before`` that, and inputs read at the publish instant."""
    coord = FakeCoordinator({
        "last_optimization": PUBLISHED - solved_before, "plan_stale": False,
        "input_ages_minutes": {"indoor": 2.0}, "input_ages_at": PUBLISHED,
        "input_problems": [{"input": "indoor", "age_minutes": 2.0}],
    }, **({"_config": {"optimization_interval": interval}} if interval else {}))
    entry = FakeEntry(entry_id="published", options={})
    entry.runtime_data = coord
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(FakeHass(), entry)
    finally:
        dt_util.freeze(None)


from heatpump_optimizer.inputs import (  # noqa: E402
    InputHealth, InputReader, InputReading, health_summary, stale_summary,
)

R.check(
    "an input reader stamps its health with the instant its ages are measured from",
    InputReader(FakeHass(), {}, now=lambda: PUBLISHED).health.read_at == PUBLISHED,
)
_late = asyncio.run(_published_download(timedelta(minutes=14), timedelta(minutes=1)))
_at_publish = asyncio.run(_published_download(timedelta(0), timedelta(minutes=1)))
_overdue = asyncio.run(_published_download(timedelta(minutes=95), timedelta(minutes=1)))
# At a 15-minute interval three missed cycles are 45 minutes, under the
# 90-minute floor, so a plan solved 60 minutes ago is fresh: this tells the
# floor from the cycles (the default interval's 3 cycles are exactly the floor).
_at_floor = asyncio.run(_published_download(timedelta(0), timedelta(minutes=60), interval=15))
R.check(
    "the download's input ages are re-based to the export: read 2 minutes old and "
    "exported 14 minutes later, they read 16",
    _late["inputs"]["input_ages_minutes"] == {"indoor": 16.0}
    and _late["inputs"]["input_problems"][0]["age_minutes"] == 16.0,
    str(_late["inputs"]),
)
R.check(
    "the null control: a download taken at the publish instant reads the published ages",
    _at_publish["inputs"]["input_ages_minutes"] == {"indoor": 2.0}
    and _at_publish["inputs"]["input_problems"][0]["age_minutes"] == 2.0,
    str(_at_publish["inputs"]),
)
R.check(
    "input ages with no read instant, or one ahead of the export, stay as published",
    diagnostics_mod._inputs_at({"input_ages_minutes": {"x": 1.0}}, PUBLISHED)
    == {"input_ages_minutes": {"x": 1.0}}
    and diagnostics_mod._inputs_at(
        {"input_ages_minutes": {"x": 1.0}, "input_ages_at": PUBLISHED},
        PUBLISHED - timedelta(minutes=1))["input_ages_minutes"] == {"x": 1.0},
)

# One age, one input: the message is an age-bearing field too, and the two
# verdicts beside it are judged at the same instant as the numbers. A payload
# that said "20 min" and, exported 40 minutes later, reports a 60-minute age
# beside it states two ages for one input (#2873's fix review, R8b).

_WATCHDOG = {
    "input_ages_minutes": {"indoor": 20.0},
    "input_ages_at": PUBLISHED,
    "input_problems": [{"input": "indoor", "entity_id": "sensor.indoor",
                        "problem": "stale", "age_minutes": 20.0,
                        "max_age_minutes": 30.0}],
    "problem_inputs": [],
    "problem_messages": ["sensor.indoor: stale (last report 20 min)"],
    "input_health": "ok",
    "stale_inputs": [],
}


async def _watchdog_download(after):
    coord = FakeCoordinator(dict(_WATCHDOG))
    entry = FakeEntry(entry_id="watchdog", options={})
    entry.runtime_data = coord
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(FakeHass(), entry)
    finally:
        dt_util.freeze(None)


def _message_age(message):
    """The age a ``(last report N min)`` problem message states."""
    return float(message.rsplit("last report ", 1)[1].split(" min", 1)[0])


_crossed = asyncio.run(_watchdog_download(timedelta(minutes=40)))
_at_read = asyncio.run(_watchdog_download(timedelta(0)))
R.check(
    "one export states one age for one input: the problem message, the problem's "
    "age_minutes and input_ages_minutes all read 60 after a 40-minute-late "
    "export, and both verdicts are judged at that same instant",
    _message_age(_crossed["inputs"]["problem_messages"][0]) == 60.0
    and _crossed["inputs"]["input_problems"][0]["age_minutes"] == 60.0
    and _crossed["inputs"]["input_ages_minutes"] == {"indoor": 60.0}
    and _crossed["inputs"]["stale_inputs"] == ["indoor"]
    and _crossed["inputs"]["input_health"] == "1 stale",
    str(_crossed["inputs"]),
)
R.check(
    "the null control for the same payload: exported at the publish instant, the "
    "message reads the published 20 minutes, the ages do not move, and the "
    "verdicts stay as published",
    _message_age(_at_read["inputs"]["problem_messages"][0]) == 20.0
    and _at_read["inputs"]["input_problems"][0]["age_minutes"] == 20.0
    and _at_read["inputs"]["input_ages_minutes"] == {"indoor": 20.0}
    and _at_read["inputs"]["stale_inputs"] == []
    and _at_read["inputs"]["input_health"] == "ok",
    str(_at_read["inputs"]),
)
# The other direction: a reading that was a problem but not stale at publication
# crosses its own limit as the export slides away from it, so it becomes stale
# there and both its message and the verdicts follow. The boundary is the
# input's own limit exactly: at it the reading is fresh, a minute past it stale.
_UNIT_PROBLEM = {
    "input_ages_minutes": {"power": 29.0},
    "input_ages_at": PUBLISHED,
    "input_problems": [{"input": "power", "entity_id": "sensor.power",
                        "problem": "unknown_unit", "age_minutes": 29.0,
                        "max_age_minutes": 30.0}],
    "problem_messages": ["sensor.power: unknown unit"],
    "input_health": "1 missing",
    "stale_inputs": [],
}


async def _unit_download(after):
    coord = FakeCoordinator(dict(_UNIT_PROBLEM))
    entry = FakeEntry(entry_id="unit", options={})
    entry.runtime_data = coord
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(FakeHass(), entry)
    finally:
        dt_util.freeze(None)


_at_limit = asyncio.run(_unit_download(timedelta(minutes=1)))
_past_limit = asyncio.run(_unit_download(timedelta(minutes=2)))
R.check(
    "an input's own limit is the boundary: at it the reading is not stale, a "
    "minute past it the export makes it stale and its verdicts follow the age",
    _at_limit["inputs"]["input_problems"][0]["age_minutes"] == 30.0
    and _at_limit["inputs"]["stale_inputs"] == []
    and _at_limit["inputs"]["input_health"] == "1 missing"
    and _at_limit["inputs"]["problem_messages"] == ["sensor.power: unknown unit"]
    and _past_limit["inputs"]["input_problems"][0]["age_minutes"] == 31.0
    and _past_limit["inputs"]["input_problems"][0]["problem"] == "stale"
    and _past_limit["inputs"]["stale_inputs"] == ["power"]
    and _past_limit["inputs"]["input_health"] == "1 stale"
    and _past_limit["inputs"]["problem_messages"] == ["sensor.power: stale (last report 31 min)"],
    str([_at_limit["inputs"], _past_limit["inputs"]]),
)
# The verdict the export publishes is this summary, so its two classes and its
# empty case are pinned here too: the cheap driver for a shared function.
_health = InputHealth(readings={
    "a": InputReading(key="a", entity_id="sensor.a", problem="stale"),
    "b": InputReading(key="b", entity_id="sensor.b", problem="unavailable"),
})
_only_missing = InputHealth(readings={
    "b": InputReading(key="b", entity_id="sensor.b", problem="unavailable"),
})
R.check(
    "the diagnostic entity's summary counts each failure class, and reads ok with "
    "neither",
    stale_summary(_health) == "1 stale, 1 missing"
    and stale_summary(_only_missing) == "1 missing"
    and stale_summary(InputHealth()) == "ok",
    str([stale_summary(_health), stale_summary(_only_missing),
         stale_summary(InputHealth())]),
)
# The export renders its own `input_health` from the same function, off the two
# sets it judges, so all four combinations of the shared wording are pinned.
R.check(
    "the shared summary wording names each class present and ok for neither",
    health_summary(set(), set()) == "ok"
    and health_summary({"a"}, set()) == "1 stale"
    and health_summary(set(), {"b"}) == "1 missing"
    and health_summary({"a"}, {"b"}) == "1 stale, 1 missing",
    str([health_summary(set(), set()), health_summary({"a"}, set()),
         health_summary(set(), {"b"}), health_summary({"a"}, {"b"})]),
)
R.check(
    "the download judges plan_stale at the export with the coordinator's limit: at "
    "a 15-minute interval a plan solved 60 minutes ago is fresh, under the "
    "90-minute floor, and stale 96 minutes after it",
    _overdue["plan"]["plan_stale"] is True and _late["plan"]["plan_stale"] is False
    and _at_publish["plan"]["plan_stale"] is False
    and _at_floor["plan"]["plan_stale"] is False,
    f'{_overdue["plan"]["plan_stale"]} {_late["plan"]["plan_stale"]} {_at_floor["plan"]["plan_stale"]}',
)
# An instant ahead of the export cannot be dated, so the payload's verdict is
# the only evidence: re-judging it there would invent "fresh" from no age.
_ahead_plan = {"last_optimization": PUBLISHED + timedelta(minutes=5)}
R.check(
    "a plan the export clock cannot date keeps the payload's plan_stale, and one the "
    "payload never judged publishes none",
    diagnostics_mod._plan_summary({**_ahead_plan, "plan_stale": True}, PUBLISHED, 90.0)
    ["plan_stale"] is True
    and diagnostics_mod._plan_summary(_ahead_plan, PUBLISHED, 90.0)["plan_stale"] is None
    and diagnostics_mod._plan_summary(
        {"last_optimization": PUBLISHED - timedelta(minutes=95), "plan_stale": False},
        PUBLISHED, 90.0)["plan_stale"] is True,
    str([diagnostics_mod._plan_summary({**_ahead_plan, "plan_stale": True},
                                       PUBLISHED, 90.0)["plan_stale"],
         diagnostics_mod._plan_summary(_ahead_plan, PUBLISHED, 90.0)["plan_stale"]]),
)
with tempfile.TemporaryDirectory() as tmp:
    dt_util.freeze(T0 + timedelta(hours=5))
    try:
        _, _timed, _, _timed_reload, _ = asyncio.run(_finish(tmp))
        _timed_bundle = asyncio.run(_timed.async_bundle(_coord(integration_version="0")))
    finally:
        dt_util.freeze(None)
R.check(
    "the self-tests' run time is stored with them, survives a reload, and the manifest "
    "states it and its age at the export",
    _timed.self_tests_at == T0 + timedelta(hours=5)
    and _timed_reload.self_tests_at == _timed.self_tests_at
    and admitted("debug", _timed.as_dict())
    and _timed_bundle["manifest"]["self_tests_at"] == (T0 + timedelta(hours=5)).isoformat()
    and _timed_bundle["manifest"]["self_tests_age_hours"] == 0.0,
    f"{_timed.self_tests_at} {_timed_reload.self_tests_at}",
)
_cleared_at, _ = _collector()
_cleared_at.started_at, _cleared_at.final = T0, True
_cleared_at.self_tests, _cleared_at.self_tests_at = {"feeds": {"ms": 1.0}}, T0
_cleared_at.restart()
R.check(
    "starting a finished collection again clears its self-tests' run time",
    _cleared_at.self_tests_at is None and "self_tests_at" not in _cleared_at.as_dict(),
)
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402

_limit = coordinator_mod.plan_stale_limit_minutes
R.check(
    "a stale limit needs a numeric interval: a bool is no interval, a string is no "
    "interval, and zero is a number the 90-minute floor still lifts",
    _limit(types.SimpleNamespace(optimization_interval=True)) is None
    and _limit(types.SimpleNamespace(optimization_interval="15")) is None
    and _limit(types.SimpleNamespace(optimization_interval=0)) == 90.0,
    # Only the bool read is reported: the string read raises under a guard
    # that admits it, and a detail built from it would hide the check's name.
    f"{_limit(types.SimpleNamespace(optimization_interval=True))!r}",
)
# The coordinator's own predicate, called unbound over the two reads it makes:
# at three 30-minute cycles the limit is exactly 90 minutes, so an age exactly
# at it is the boundary the comparison owns.
_at_limit = types.SimpleNamespace(
    effective_config=types.SimpleNamespace(optimization_interval=30),
    _plan_age_minutes=lambda: 90.0,
)
_past_limit = types.SimpleNamespace(
    effective_config=_at_limit.effective_config,
    _plan_age_minutes=lambda: 90.1,
)
_stale = coordinator_mod.HeatPumpOptimizerCoordinator._plan_is_stale
R.check(
    "a plan exactly at the limit is not stale, and a tenth of a minute past it is",
    _stale(_at_limit) is False and _stale(_past_limit) is True,
    f"{_stale(_at_limit)} {_stale(_past_limit)}",
)
# The stored run time and the stored results travel together: a collector
# holding an instant without the results writes neither, rather than a
# timestamp with nothing it stamps.
_only_instant, _ = _collector()
_only_instant.self_tests, _only_instant.self_tests_at = None, T0
R.check(
    "a stored run time with no stored results is left out of the document: the two "
    "are written together or not at all",
    "self_tests_at" not in _only_instant.as_dict(),
    str(sorted(_only_instant.as_dict())),
)
R.check(
    "a plan exactly at the limit is fresh at the export, and one a minute past it "
    "is stale",
    diagnostics_mod._plan_summary(
        {"last_optimization": PUBLISHED - timedelta(minutes=90)}, PUBLISHED, 90.0
    )["plan_stale"] is False
    and diagnostics_mod._plan_summary(
        {"last_optimization": PUBLISHED - timedelta(minutes=91)}, PUBLISHED, 90.0
    )["plan_stale"] is True,
)

# -- The export re-judges staleness by the reader's own precedence (#2873, round 3) --
# A fault code outranks staleness at the reader (D1-s5-52): ``read`` records the
# age before it sets ``implausible``, so an implausible entry carries an age and
# a limit, and an export re-basing that age past the limit must not relabel it
# stale. Every other class a reader sets after its age gate defers to stale.
# Pinned as a census: each such class is read by the production reader, published
# by the coordinator's own view, exported a minute past its own limit, and compared
# with what the same reader says when it reads the same state at that instant.

_IMPLAUSIBLE = {
    "input_ages_minutes": {"indoor": 10.0},
    "input_ages_at": PUBLISHED,
    "input_problems": [{"input": "indoor", "entity_id": "sensor.indoor",
                        "problem": "implausible", "age_minutes": 10.0,
                        "max_age_minutes": 30.0}],
    "problem_messages": ["sensor.indoor: outside its plausible range"],
    "input_health": "1 missing",
    "stale_inputs": [],
}


async def _implausible_download(after):
    coord = FakeCoordinator(dict(_IMPLAUSIBLE))
    entry = FakeEntry(entry_id="implausible", options={})
    entry.runtime_data = coord
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(FakeHass(), entry)
    finally:
        dt_util.freeze(None)


def _renders_implausible(download, age):
    got = download["inputs"]
    return (
        got["input_problems"][0]["problem"] == "implausible"
        and got["input_problems"][0]["age_minutes"] == age
        and got["stale_inputs"] == []
        and got["input_health"] == "1 missing"
        and got["problem_messages"] == ["sensor.indoor: outside its plausible range"]
    )


_implausible_past = asyncio.run(_implausible_download(timedelta(minutes=40)))
_implausible_within = asyncio.run(_implausible_download(timedelta(minutes=10)))
R.check(
    "an implausible input re-based past its own limit stays implausible at the "
    "export: out of stale_inputs, counted missing, and worded as a fault, not an age",
    _renders_implausible(_implausible_past, 50.0),
    str(_implausible_past["inputs"]),
)
R.check(
    "the null control: the same implausible entry exported inside its limit reads "
    "the same, so the check above is about the age crossing the limit",
    _renders_implausible(_implausible_within, 20.0),
    str(_implausible_within["inputs"]),
)

from harness import FakeState  # noqa: E402
from heatpump_optimizer import inputs as inputs_mod  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    CONF_FLOW_METER_ENTITY, CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY,
    CONF_POWER_ENTITY, CONF_SOLAR_RADIATION_ENTITY,
)

# (published class, config key, state, unit, the reader call) -- one row per class
# a reader sets after its age gate. The reader runs at ``at``.
_PRECEDENCE_ROWS = [
    ("implausible", CONF_INDOOR_TEMP_ENTITY, "-127", "°C",
     lambda r, k: r.read(k)),
    ("implausible", CONF_FLOW_METER_ENTITY, "-1", "kg/s",
     lambda r, k: r.read_flow_kg_s(k)),
    ("unknown_unit", CONF_POWER_ENTITY, "2", "furlong",
     lambda r, k: r.read_power_kw(k)),
    ("unknown_value", CONF_OUTDOOR_TEMP_ENTITY, "banana", None,
     lambda r, k: r.read_state(k, valid={"heat"})),
    ("not_boolean", CONF_SOLAR_RADIATION_ENTITY, "maybe", None,
     lambda r, k: r.read_bool(k, strict=True)),
]
# A row whose key has no age limit cannot age at the export or at a re-read, so
# it is held to publishing no limit: the day it gains one, its comparison runs and
# it leaves this set. Every row above polls and has one.
_UNBOUNDED_ROWS: set[str] = set()
# Classes set before the age gate: their reading carries no age, so the export has
# nothing to re-base (``not_configured`` has no entity and is never published).
_PRE_GATE = {"not_configured", "missing_entity", "unavailable", "not_numeric"}
_REPORTED = PUBLISHED - timedelta(minutes=5)


def _published(key, state, unit, read, at):
    # A source that re-reports an unchanged value polls, so it is held to
    # ``INPUT_MAX_AGE_MINUTES``; its age runs from the last report.
    hass = FakeHass({f"sensor.{key}": FakeState(
        state, last_updated=_REPORTED - timedelta(hours=1), last_reported=_REPORTED,
        unit=unit)})
    reader = InputReader(hass, {key: f"sensor.{key}"}, now=lambda: at)
    read(reader, key)
    view = coordinator_mod.HeatPumpOptimizerCoordinator._input_health_view(
        types.SimpleNamespace(_input_health=reader.health, _learner_freeze_reason=None))
    return view


def _literal_classes(tree):
    """Every class literal ``inputs.py`` assigns to a reading's ``problem``."""
    found = set()
    for node in ast.walk(tree):
        values = []
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Attribute) and t.attr == "problem" for t in node.targets):
            values.append(node.value)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_set_problem":
            values.extend(node.args[1:])
        for value in values:
            found.update(c.value for c in ast.walk(value)
                         if isinstance(c, ast.Constant) and isinstance(c.value, str))
    return found


_census = []
for _cls, _key, _state, _unit, _read in _PRECEDENCE_ROWS:
    _pub = _published(_key, _state, _unit, _read, PUBLISHED)
    _entry = (_pub["input_problems"] or [{}])[0]
    _limit = _entry.get("max_age_minutes")
    _row = f"{_cls}/{_key}"
    _bounded = isinstance(_limit, (int, float))
    _ok_pre = (_entry.get("problem") == _cls and _entry.get("age_minutes") == 5.0
               and _bounded == (_row not in _UNBOUNDED_ROWS))
    if not _bounded:
        _census.append({"row": _row, "pre": _ok_pre, "unbounded": True})
        continue
    _at = PUBLISHED + timedelta(minutes=(_limit if _ok_pre else 0) - 5 + 1)
    _exported = diagnostics_mod._inputs_at(_pub, _at)
    _reread = _published(_key, _state, _unit, _read, _at)
    _at_read = diagnostics_mod._inputs_at(_pub, PUBLISHED)
    _census.append({
        "row": _row, "pre": _ok_pre, "unbounded": False,
        "exported": _exported["input_problems"][0]["problem"] if _ok_pre else None,
        "reread": _reread["input_problems"][0]["problem"] if _ok_pre else None,
        "stale_agree": _ok_pre and _exported["stale_inputs"] == _reread["stale_inputs"],
        "health_agree": _ok_pre and _exported["input_health"] == _reread["input_health"],
        "null": _ok_pre and _at_read["input_problems"][0]["problem"] == _cls,
    })
_bounded_rows = [row for row in _census if not row["unbounded"]]
_found = _literal_classes(ast.parse(Path(inputs_mod.__file__).read_text()))
_driven = {row[0] for row in _PRECEDENCE_ROWS}
R.check(
    "the precedence census covers every class inputs.py sets: each is driven past "
    "its age gate, set before it, or stale itself, and PROBLEM_WORDS, which the "
    "card enumerates its wording by, names exactly the published ones",
    _found == _driven | _PRE_GATE | {"stale"}
    and set(inputs_mod.PROBLEM_WORDS) == _found - {"not_configured"}
    and all(row["pre"] for row in _census),
    str([sorted(_found), sorted(set(inputs_mod.PROBLEM_WORDS) ^ (_found - {"not_configured"})),
         [row["row"] for row in _census if not row["pre"]]]),
)
R.check(
    "exported a minute past its own limit, every class reads what the reader says "
    "re-reading the same state then: a fault code stays itself, every other class "
    "ages into stale, and stale_inputs and input_health agree with the re-read",
    all(row["exported"] == row["reread"] and row["stale_agree"] and row["health_agree"]
        for row in _bounded_rows)
    and {row["exported"] for row in _bounded_rows} == {"implausible", "stale"},
    str([row for row in _bounded_rows
         if not (row["exported"] == row["reread"] and row["stale_agree"]
                 and row["health_agree"])]),
)
R.check(
    "the census's null control: exported at the publish instant, every class reads "
    "as published",
    all(row["null"] for row in _bounded_rows),
    str([row["row"] for row in _bounded_rows if not row["null"]]),
)
sys.exit(R.close("DEBUG COLLECT CHECKS"))
