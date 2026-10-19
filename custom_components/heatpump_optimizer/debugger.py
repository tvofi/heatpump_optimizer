"""The debug collector: a week of what the install saw and did (R9-DBG-1, #1939).

An owner who turns on the learning page's debug-collection option gets an
``hpo-debug/1`` bundle in Home Assistant's own Download diagnostics: one slim
row per published payload, one whole payload a day, and this entry's own store
documents -- what a maintainer needs to see a week the owner says went wrong.
Like the notifier it listens to the coordinator's updates, so the coordinator
carries no line of it; the solve's wall time is the span between the two
listener calls the coordinator makes when ``optimization_running`` flips.

The ring is a store of its own, saved once an hour and flushed at unload, so a
reload mid-week keeps every row. The collection stops itself after seven days
and stays final until it is started again; turning the option off deletes it.

Ending it -- the seven days, the stop action or the finalize button -- runs the
pre-study's five self-tests once (#1940): read-only, no actuation, no network,
fifteen minutes between them at most. Their results are saved with the ring and
ride the bundle's manifest. Download diagnostics carries the bundle inline while
the download stays within ``INLINE_CAP_BYTES`` and, past it, the manifest and
where the ring is stored.

The bundle's replay half (#2271) is an ``hpo-replay/1`` document built at
download time: the collection's own window, at most ``REPLAY_SPAN``, read
through the recorder's history API in the recorder's executor, through the one
allowlist and sanitiser ``tools/replay/export.py`` uses (``replay_doc``). A
person or calendar entity is left out of it, as diagnostics redacts their ids.
A window too large for the inline cap gives way to the newest shorter one that
fits (``REPLAY_SPANS``); the manifest says which ran, or why there is none.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import statistics
import time
from collections.abc import Callable, Coroutine
from datetime import date, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder import history as recorder_history
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from . import const, replay_doc
from .accuracy import AccuracyTracker
from .const import CONF_DEBUG_COLLECT, DEFAULT_DEBUG_COLLECT, DOMAIN, PRIVATE_ENTITY_ID
from .drift import stored_instant
from .store import (
    DOMAINS,
    QuarantiningStore,
    admitted,
    load_mapping,
    off_domain,
    quarantines,
)

_LOGGER = logging.getLogger(__name__)

DEBUG_STORE_VERSION = 1
BUNDLE_SCHEMA = "hpo-debug/1"
COLLECT_SPAN = timedelta(days=7)
SAVE_EVERY = timedelta(hours=1)
SNAPSHOT_EVERY = timedelta(days=1)
DEBUG_ACTIONS = ("start", "stop", "status")
#: The owner's ceiling over all the self-tests together (pre-study section 4).
SELF_TEST_BUDGET = timedelta(minutes=15)
#: The largest diagnostics download that carries the bundle inline (pre-study
#: section 3, "8 MB"). Home Assistant writes the download as
#: ``json.dumps(..., indent=2)`` with the entry's payload under ``data``, so the
#: bundle is measured that way, at that depth (``download_bytes``), and
#: ``DOWNLOAD_HEADROOM_BYTES`` stands for the rest of the file: Home Assistant's
#: own system and custom-component sections and this entry's other keys.
INLINE_CAP_BYTES = 8 * 1024 * 1024
DOWNLOAD_HEADROOM_BYTES = 256 * 1024
#: The replay half's window, newest first: the collection's week, then the
#: shorter ones tried when it does not fit the inline cap (#2271).
REPLAY_SPAN = COLLECT_SPAN
REPLAY_SPANS = (REPLAY_SPAN, timedelta(days=3), timedelta(days=1), timedelta(hours=6))
_INPUTS = ("indoor_temp", "outdoor_temp", "dhw_temp")
_HEALTH = ("problem_inputs", "input_ages_minutes", "learners_frozen")

#: Keyed by the coordinator, as ``pump_arbiter`` keeps its state: the
#: collector holds no reference back, or the entry would never be freed.
_COLLECTORS: WeakKeyDictionary[Any, DebugCollector] = WeakKeyDictionary()

_IDLE = {"active": False, "final": False, "rows": 0, "bytes": 0, "started_at": None}


def _store(hass: HomeAssistant, entry_id: str) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(hass, DEBUG_STORE_VERSION, f"{DOMAIN}_{entry_id}_debug")


def store_keys(entry_id: str) -> dict[str, str]:
    """``DOMAINS`` name -> this entry's store key, the debug ring's own excluded."""
    return {name: f"{DOMAIN}_{entry_id}_{name}" for name in DOMAINS if name != "debug"}


def _wire(value: Any) -> Any:
    """The JSON form of what a payload carries that JSON has no type for."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (set, frozenset, tuple)):
        return list(value)
    return str(value)


def _dumps(value: Any) -> str:
    return json.dumps(value, default=_wire)


def cycle_row(
    coordinator: Any, data: Any, now: datetime, solve_wall_ms: float | None
) -> dict[str, Any]:
    """The pre-study's slim row for one published payload; absent fields are omitted."""
    action = data.get("current_action") or {}
    samples = coordinator.accuracy.samples
    row = {
        "t": now.isoformat(),
        "mode": data.get("mode"),
        "action_mode": action.get("mode"),
        "action_kw": action.get("power"),
        "heat_pump_on": action.get("heat_pump_on"),
        "solve_wall_ms": solve_wall_ms,
        "payload_solve_time_ms": data.get("solve_time_ms"),
        "solve_failures": coordinator.solve_failures,
        "prices_rows": len(coordinator.prices or ()),
        "weather_stale_h": data.get("weather_forecast_stale_hours"),
        "indoor_temp": data.get("indoor_temperature"),
        "outdoor_temp": data.get("outdoor_temperature"),
        "dhw_temp": data.get("dhw_temperature"),
        "accuracy_sample": samples[-1].as_dict() if samples else None,
        # The release that wrote the row (#2209's forward-carry): attribution
        # by the gap a restart leaves needs no inference from it.
        "version": coordinator.integration_version,
    }
    return {key: value for key, value in row.items() if value is not None}


def _aware(raw: Any) -> str | None:
    """A stored instant as aware text, or ``None`` when it does not parse.

    The domain accepts a naive stamp (it parses), and a loader that keeps that
    text installs a naive instant the next ``now - stamp`` cannot subtract.
    """
    when = stored_instant(raw)
    return None if when is None else when.isoformat()


def _repair(item: dict[str, Any], field: str, needs: set[str]) -> dict[str, Any] | None:
    """``item`` inside its domain, instants rewritten aware; ``None`` when it is not.

    A sample that is not a sample dict is the same refusal as a row outside
    its domain. The stamp is stored aware so a naive one cannot reach a
    subtraction against ``now``.
    """
    if not needs <= item.keys() or not admitted("debug", {field: [item]}):
        return None
    stamp = _aware(item.get("t"))
    if stamp is None:
        return None
    fixed = {**item, "t": stamp}
    sample = fixed.get("accuracy_sample")
    if sample is None:
        return fixed
    if not isinstance(sample, dict):
        return None
    sample_t = _aware(sample.get("t"))
    if sample_t is None:
        return None
    fixed["accuracy_sample"] = {**sample, "t": sample_t}
    return fixed


def _kept(raw: dict[str, Any], field: str, needs: set[str]) -> list[dict[str, Any]]:
    """The stored items of ``field``; each bad one dropped alone."""
    items = raw.get(field)
    return [
        fixed for item in items
        if isinstance(item, dict) and (fixed := _repair(item, field, needs)) is not None
    ] if isinstance(items, list) else []


def _read_stores(folder: Path, keys: list[str]) -> dict[str, tuple[Any, Any]]:
    """``key -> (version, data)`` of each store document on disk (executor)."""
    found: dict[str, tuple[Any, Any]] = {}
    for key in keys:
        try:
            doc = json.loads((folder / key).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict):
            found[key] = (doc.get("version"), doc.get("data"))
    return found


def _parsed(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return None


# -- the self-tests (pre-study section 4); each reads, none actuates -----------
def store_report(stores: dict[str, tuple[Any, Any]]) -> dict[str, Any]:
    """Per store document: its fields off their declared domain, and whether the
    quarantine would scrub a leaf of it on the next load."""
    report = {}
    for key, (version, data) in stores.items():
        off = list(dict.fromkeys(off_domain(key, data)))
        report[key] = {"version": version, "off_domain": off[:10], "off_count": len(off),
                       "quarantined": quarantines(data)}
    return report


def accuracy_report(document: Any, live: AccuracyTracker) -> dict[str, Any]:
    """The monitor re-derived from the accuracy store's window beside the live deque's."""
    stored = document.get("accuracy") if isinstance(document, dict) else None
    restored = AccuracyTracker.from_dict(stored if isinstance(stored, dict) else None)
    raw = stored.get("samples") if isinstance(stored, dict) else None
    return {
        "window": "the store keeps the newest 192 samples; the live tracker more",
        "stored_samples": len(raw) if isinstance(raw, list) else 0,
        "restored_samples": len(restored.samples),
        "store": _monitor(restored),
        "live": _monitor(live),
    }


def _monitor(tracker: AccuracyTracker) -> dict[str, Any]:
    summary = tracker.summary()
    return {"samples": summary["samples"], "temperature_bias": summary["temperature_bias"],
            "temperature_mae": summary["temperature_mae"], "trust": summary["trust"]}


def spread(values: list[float]) -> dict[str, Any] | None:
    if not values:
        return None
    return {"n": len(values), "min": min(values), "median": statistics.median(values),
            "max": max(values)}


def _longest_flat(values: list[Any]) -> int:
    """The longest run of one unchanged reading: a sensor that stopped updating."""
    longest = run = 0
    previous: Any = object()
    for value in values:
        run = run + 1 if value == previous else 1
        longest, previous = max(longest, run), value
    return longest


def sensor_sanity(rows: list[dict[str, Any]], data: Any) -> dict[str, Any]:
    """Per input: readings missing and its longest unchanged run; and the live health view."""
    out: dict[str, Any] = {}
    for field in _INPUTS:
        present = [row[field] for row in rows if field in row]
        out[field] = {"missing": len(rows) - len(present), "range": spread(present),
                      "longest_flat": _longest_flat(present)}
    view = data if isinstance(data, dict) else {}
    out["now"] = {key: view.get(key) for key in _HEALTH}
    return out


def feed_health(
    rows: list[dict[str, Any]], outage_cycles: int | None = None
) -> dict[str, Any]:
    """Whether a feed starved the week: price rows, forecast staleness, solve
    failures, the holes the ring itself shows, and the outage streak it ended in.

    A failed fetch publishes no payload, so it adds no row: the silence of the
    feed is in the stamps, where every counter here reads clean, and the
    coordinator's own streak resets the moment the feed recovers. Both halves
    are needed, and neither is derivable from the other.
    """
    stale = [row["weather_stale_h"] for row in rows if "weather_stale_h" in row]
    failures = [row.get("solve_failures", 0) for row in rows]
    stamps = [seen for row in rows if (seen := stored_instant(row.get("t"))) is not None]
    return {
        "cycles": len(rows),
        "no_prices": sum(1 for row in rows if not row.get("prices_rows")),
        "weather_stale_cycles": sum(1 for hours in stale if hours > 0),
        "weather_stale_h_max": max(stale, default=None),
        "solve_failures_added": max(failures) - min(failures) if failures else 0,
        "row_gaps_h": spread([
            (later - earlier).total_seconds() / 3600.0
            for earlier, later in zip(stamps, stamps[1:])
        ]),
        "tibber_outage_cycles": outage_cycles,
    }


async def _solver_smoke(coordinator: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """One what-if solve with no override, which the live plan should equal."""
    began = time.monotonic()
    result = await coordinator.async_simulate({}, limited=False)
    return {
        "wall_ms": round((time.monotonic() - began) * 1000.0, 1),
        "error": result.get("error"),
        "cost_delta": result.get("cost_delta"),
        "week_solve_ms": spread(
            [row["payload_solve_time_ms"] for row in rows if "payload_solve_time_ms" in row]),
    }


async def run_self_tests(
    checks: list[tuple[str, Callable[[], Any]]], budget: float
) -> dict[str, Any]:
    """Each check in turn inside what is left of ``budget`` seconds; one failing stops none.

    A check returns its result, or an awaitable of it; only an awaited one can
    be cut off at the budget.
    """
    deadline = time.monotonic() + budget
    out: dict[str, Any] = {}
    for name, check in checks:
        left = deadline - time.monotonic()
        if left <= 0:
            out[name] = {"skipped": "budget"}
            continue
        began = time.monotonic()
        try:
            async with asyncio.timeout(left):
                result = check()
                outcome = {"result": await result if inspect.isawaitable(result) else result}
        except TimeoutError:
            outcome = {"error": "timeout"}
        except Exception as err:  # noqa: BLE001 - one broken self-test must not hide the rest
            outcome = {"error": repr(err)}
        out[name] = {**outcome, "ms": round((time.monotonic() - began) * 1000.0, 1)}
    return out


def download_bytes(bundle: dict[str, Any]) -> int:
    """The bytes ``bundle`` takes in the diagnostics download, as that file writes it."""
    return len(json.dumps({"data": {"debug": bundle}}, indent=2, default=_wire).encode())


def capped(bundle: dict[str, Any], store_key: str, cap: int | None = None) -> dict[str, Any]:
    """``bundle`` when its download fits the inline cap; else its manifest and where
    the ring is stored."""
    limit = INLINE_CAP_BYTES if cap is None else cap
    size = download_bytes(bundle) + DOWNLOAD_HEADROOM_BYTES
    if size <= limit:
        return bundle
    return {"schema": bundle.get("schema"), "manifest": bundle.get("manifest"),
            "inline": False, "bytes": size, "cap_bytes": limit,
            "store_file": f".storage/{store_key}"}


# -- the replay half (#2271): ``replay_doc``'s document from the recorder ------
def replay_window(started_at: datetime | None, now: datetime) -> tuple[datetime, datetime]:
    """The collection's own window, at most ``REPLAY_SPAN`` long and ending by ``now``."""
    end = now if started_at is None else min(now, started_at + COLLECT_SPAN)
    start = end - REPLAY_SPAN
    return (start if started_at is None else max(start, started_at)), end


def _public(node: Any) -> Any:
    """``node`` with every value naming a person or a calendar dropped, at any depth."""
    if isinstance(node, str):
        return None if PRIVATE_ENTITY_ID.search(node) else node
    if isinstance(node, dict):
        return {key: _public(value) for key, value in node.items()}
    if isinstance(node, list):
        return [item for item in map(_public, node) if item is not None]
    return node


def registry_rows(registry: Any) -> list[dict[str, Any]]:
    """The entity registry as the rows ``replay_doc`` reads, the export's shape."""
    return [{"entity_id": e.entity_id, "platform": e.platform, "unique_id": e.unique_id,
             "config_entry_id": e.config_entry_id, "translation_key": e.translation_key,
             "disabled_by": e.disabled_by} for e in registry.entities.values()]


def replay_entities(entry: dict[str, Any], registry: list[dict[str, Any]]) -> dict[str, Any]:
    """What the replay half reads for ``entry``: its configuration with no person or
    calendar in it, the inputs that names, what it publishes, and the Tibber price
    sensors to choose from when it fetches its own prices."""
    data, options = _public(entry["data"]), _public(entry["options"])
    config = {**data, **options}
    tibber = config.get("price_source") != replay_doc.PRICE_SOURCE_ENTITY
    return {
        "entry": {**entry, "data": data, "options": options}, "config": config,
        "inputs": replay_doc.mapped_entities(data) | replay_doc.mapped_entities(options),
        "published": sorted(r["entity_id"] for r in registry if r["platform"] == DOMAIN
                            and r["config_entry_id"] == entry["entry_id"]),
        "candidates": replay_doc.tibber_price_candidates(registry) if tibber else None,
    }


def _since(states: list[Any], start: datetime) -> list[Any]:
    """The state in force at ``start``, then every one after it."""
    before = [s for s in states if s.last_updated < start]
    return before[-1:] + [s for s in states if s.last_updated >= start]


def _record(state: Any) -> tuple[str, Any, dict[str, Any], str | None]:
    # A recorder older than its ``last_reported_ts`` column (2024.3) has none.
    reported = getattr(state, "last_reported", None)
    return (state.last_updated.isoformat(), state.state, dict(state.attributes),
            reported.isoformat() if reported and reported > state.last_updated else None)


def replay_document(
    wants: dict[str, Any], registry: list[dict[str, Any]], history: dict[str, list[Any]],
    window: tuple[datetime, datetime], time_zone: str, schema: int | None,
    conf: frozenset[str],
) -> dict[str, Any]:
    """The sealed ``hpo-replay/1`` document over ``window``; ``replay_doc.Refused``
    when it may not leave the install."""
    start, end = window
    states = {eid: replay_doc.state_rows(_record(s) for s in _since(rows, start))
              for eid, rows in history.items()}
    inputs, price = set(wants["inputs"]), None
    if wants["candidates"] is not None:
        price = replay_doc.choose_price_entity(
            wants["config"], registry,
            lambda eid: any(replay_doc.numeric(row[1]) for row in states.get(eid, ())))
        inputs.add(price)
    raw = replay_doc.document(
        time_zone=time_zone, window=(start.isoformat(), end.isoformat()),
        recorder_schema=schema, entry=wants["entry"], inputs=inputs,
        published=wants["published"], price_series_entity=price,
        states={eid: states.get(eid, []) for eid in sorted(inputs | set(wants["published"]))},
    )
    return replay_doc.seal(raw, conf)


def fit_replay(bundle: dict[str, Any], build: Callable[[datetime], dict[str, Any]],
               end: datetime, start: datetime) -> tuple[dict[str, Any] | None, str]:
    """The longest of ``REPLAY_SPANS`` (none starting before ``start``) whose document
    keeps ``bundle``'s download inside the inline cap, and what ran (executor)."""
    for since in dict.fromkeys(max(start, end - span) for span in REPLAY_SPANS):
        doc = build(since)
        ran = f"{doc['window']['start']} .. {doc['window']['end']}"
        whole = {**bundle, "replay": doc, "manifest": {**bundle["manifest"], "replay": ran}}
        if download_bytes(whole) + DOWNLOAD_HEADROOM_BYTES <= INLINE_CAP_BYTES:
            return doc, ran
    return None, "over the inline cap at every window tried"


class DebugCollector:
    """One entry's ring: its rows, its daily payload snapshots, and whether it is final."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        spawn: Callable[[Coroutine[Any, Any, None]], object],
    ) -> None:
        self._hass = hass
        self._entry_id = entry_id
        self._spawn = spawn
        self._store = _store(hass, entry_id)
        self.started_at: datetime | None = None
        self.final = False
        self.rows: list[dict[str, Any]] = []
        self.snapshots: list[dict[str, Any]] = []
        self._saved_at: datetime | None = None
        self._seen: Any = None
        self._solve_started: float | None = None
        self._solve_wall_ms: float | None = None
        self._closed = False
        self.self_tests: dict[str, Any] | None = None

    async def async_load(self) -> None:
        raw = await load_mapping(self._store, "the debug collection") or {}
        self.started_at = stored_instant(raw.get("started_at"))
        if self.started_at is None:  # a ring with no start cannot be bounded to a week
            return
        self.final = raw.get("final") is True
        self.rows = _kept(raw, "rows", {"t"})
        self.snapshots = _kept(raw, "snapshots", {"t", "cycle", "data"})
        tests = raw.get("self_tests")
        self.self_tests = _parsed(tests) if isinstance(tests, str) else None

    def as_dict(self) -> dict[str, Any]:
        start = {"started_at": self.started_at.isoformat()} if self.started_at else {}
        tests = {"self_tests": _dumps(self.self_tests)} if self.self_tests is not None else {}
        return {**start, "final": self.final, "rows": list(self.rows),
                "snapshots": list(self.snapshots), **tests}

    async def async_save(self) -> None:
        try:
            await self._store.async_save(self.as_dict())
        except Exception as err:  # noqa: BLE001 - a lost save costs at most an hour of rows
            _LOGGER.debug("Could not persist the debug collection: %s", err)

    def observe(self, coordinator: Any) -> None:
        """One listener call: time a solve's edges, record a newly published payload."""
        if self._closed or self.final:
            return
        running = coordinator.optimization_running
        if running and self._solve_started is None:
            self._solve_started = time.monotonic()
        elif not running and self._solve_started is not None:
            self._solve_wall_ms = round((time.monotonic() - self._solve_started) * 1000.0, 1)
            self._solve_started = None
        data = coordinator.data
        if data is None or data is self._seen:
            return
        self._seen = data
        self.record(coordinator, data, dt_util.utcnow())

    def record(self, coordinator: Any, data: Any, now: datetime) -> None:
        if self.started_at is None:
            self.started_at = now
        if now - self.started_at >= COLLECT_SPAN:
            self.finalize(coordinator)
            return
        last = stored_instant(self.snapshots[-1]["t"]) if self.snapshots else None
        if last is None or now - last >= SNAPSHOT_EVERY:
            self.snapshots.append({"t": now.isoformat(), "cycle": len(self.rows), "data": _dumps(data)})
        self.rows.append(cycle_row(coordinator, data, now, self._solve_wall_ms))
        self._solve_wall_ms = None
        if self._saved_at is None or now - self._saved_at >= SAVE_EVERY:
            self._saved_at = now
            self._spawn(self.async_save())

    async def async_close(self) -> None:
        self._closed = True
        await self.async_save()

    def finalize(self, coordinator: Any) -> None:
        """Stop collecting now; the self-tests then run in the background and save."""
        self.final = True
        self._spawn(self._async_finish(coordinator, self.started_at))

    async def _async_finish(self, coordinator: Any, started_at: datetime | None) -> None:
        rows = list(self.rows)
        stores: dict[str, tuple[Any, Any]] = {}
        accuracy_key = store_keys(self._entry_id)["accuracy"]
        # The feed's outage streak, through the view the coordinator publishes
        # (#1739): this module names no private member, as ``diagnostics.py``
        # does not. A coordinator publishing no view -- a duck-typed harness --
        # has no streak to report.
        state = getattr(coordinator, "diagnostics_state", None)
        streak = state().tibber_outage_cycles if state is not None else None

        async def read_stores() -> dict[str, Any]:
            stores.update(await self._read())
            return store_report(stores)

        tests = await run_self_tests([
            ("stores", read_stores),
            ("accuracy", lambda: accuracy_report(
                stores.get(accuracy_key, (None, None))[1], coordinator.accuracy)),
            ("solver", lambda: _solver_smoke(coordinator, rows)),
            ("sensors", lambda: sensor_sanity(rows, coordinator.data)),
            ("feeds", lambda: feed_health(rows, streak)),
        ], SELF_TEST_BUDGET.total_seconds())
        # Unless the collection restarted meanwhile:
        if self.final and self.started_at == started_at:
            self.self_tests = tests
        await self.async_save()

    async def _read(self) -> dict[str, tuple[Any, Any]]:
        return await self._hass.async_add_executor_job(
            _read_stores, Path(self._hass.config.path(".storage")),
            list(store_keys(self._entry_id).values()),
        )

    def restart(self) -> None:
        self.started_at, self.final, self.rows, self.snapshots = None, False, [], []
        self._saved_at, self.self_tests = None, None
        self._spawn(self.async_save())

    def status(self) -> dict[str, Any]:
        return {
            "active": not self.final, "final": self.final, "rows": len(self.rows),
            "bytes": len(_dumps(self.as_dict()).encode()),
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

    async def async_bundle(
        self, coordinator: Any, diagnostics: Any = None, entry: Any = None
    ) -> dict[str, Any]:
        """The ``hpo-debug/1`` bundle; with ``entry``, its replay half filled."""
        stores = await self._read()
        bundle = {
            "schema": BUNDLE_SCHEMA,
            "manifest": {
                "generated_at": dt_util.utcnow().isoformat(),
                "generator": __name__,
                "integration_version": coordinator.integration_version,
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "final": self.final,
                "days": COLLECT_SPAN.days,
                "cycles": len(self.rows),
                "replay_verdict": None,
                "replay": None,
                "store_versions": {key: version for key, (version, _d) in stores.items()},
                "self_tests": self.self_tests,
            },
            "replay": None,
            "cycle_rows": list(self.rows),
            "payload_snapshots": [{**s, "data": _parsed(s["data"])} for s in self.snapshots],
            "stores": {key: data for key, (_v, data) in stores.items()},
            "diagnostics": diagnostics,
        }
        if entry is not None:
            bundle["replay"], bundle["manifest"]["replay"] = await self._async_replay(
                entry, bundle)
        return bundle

    async def _async_replay(self, entry: Any, bundle: dict[str, Any]) -> tuple[Any, str]:
        """The replay half and what the manifest says of it; never raises."""
        if "recorder" not in self._hass.config.components:
            return None, "no recorder is set up"
        start, end = replay_window(self.started_at, dt_util.utcnow())
        registry = registry_rows(er.async_get(self._hass))
        wants = replay_entities({
            "entry_id": entry.entry_id, "version": entry.version,
            "minor_version": entry.minor_version,
            "data": dict(entry.data), "options": dict(entry.options)}, registry)
        entity_ids = sorted(wants["inputs"] | set(wants["published"])
                            | set(wants["candidates"] or ()))
        try:
            instance = get_instance(self._hass)
            # Nothing to read asks nothing: an empty list is not relied on upstream.
            history = await instance.async_add_executor_job(partial(
                recorder_history.get_significant_states, self._hass, start, end, entity_ids,
                include_start_time_state=True, significant_changes_only=False,
            )) if entity_ids else {}
            build = partial(replay_document, wants, registry, history,
                            time_zone=self._hass.config.time_zone,
                            schema=instance.schema_version,
                            conf=replay_doc.conf_keys(vars(const)))
            return await self._hass.async_add_executor_job(
                fit_replay, bundle, lambda since: build((since, end)), end, start)
        except replay_doc.Refused as err:
            return None, str(err)
        except Exception as err:  # noqa: BLE001 - diagnostics never breaks
            return None, f"the recorder could not be read: {err!r}"


def collector_for(coordinator: Any) -> DebugCollector | None:
    return _COLLECTORS.get(coordinator)


async def async_setup_debugger(hass: HomeAssistant, entry: Any, coordinator: Any) -> None:
    """Start the entry's collection when its option is on; delete it when off."""
    if not entry.options.get(CONF_DEBUG_COLLECT, DEFAULT_DEBUG_COLLECT):
        await _store(hass, entry.entry_id).async_remove()
        return
    collector = DebugCollector(
        hass,
        entry.entry_id,
        lambda coro: entry.async_create_background_task(
            hass, coro, name="heatpump_optimizer_debug_save"
        ),
    )
    await collector.async_load()
    _COLLECTORS[coordinator] = collector
    entry.async_on_unload(coordinator.async_add_listener(lambda: collector.observe(coordinator)))


async def async_unload_debugger(coordinator: Any) -> None:
    """Flush the rows written since the last hourly save; record nothing more."""
    collector = _COLLECTORS.pop(coordinator, None)
    if collector is not None:
        await collector.async_close()


def async_command(hass: HomeAssistant, entry: Any, action: str) -> dict[str, Any]:
    """The ``debug_collect`` action for one entry: its status after ``action``."""
    collector = collector_for(entry.runtime_data)
    if collector is None and action == "start":
        # The options listener reloads the entry, and the reload starts it.
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_DEBUG_COLLECT: True}
        )
        return {**_IDLE, "active": True}
    if collector is None or (action == "stop" and collector.final):
        if action == "status":
            return dict(_IDLE)
        raise ServiceValidationError(
            f"No debug collection is running for {entry.entry_id}",
            translation_domain=DOMAIN,
            translation_key="debug_collect_inactive",
            translation_placeholders={"entry_id": entry.entry_id},
        )
    if action == "stop":
        collector.finalize(entry.runtime_data)
    elif action == "start" and collector.final:
        collector.restart()
    return collector.status()
