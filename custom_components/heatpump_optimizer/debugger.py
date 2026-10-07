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
"""
from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable, Coroutine
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from .const import CONF_DEBUG_COLLECT, DEFAULT_DEBUG_COLLECT, DOMAIN
from .drift import stored_instant
from .store import DOMAINS, QuarantiningStore, admitted, load_mapping

_LOGGER = logging.getLogger(__name__)

DEBUG_STORE_VERSION = 1
BUNDLE_SCHEMA = "hpo-debug/1"
COLLECT_SPAN = timedelta(days=7)
SAVE_EVERY = timedelta(hours=1)
SNAPSHOT_EVERY = timedelta(days=1)
DEBUG_ACTIONS = ("start", "stop", "status")

#: Keyed by the coordinator, as ``pump_arbiter`` keeps its state: the
#: collector holds no reference back, or the entry would never be freed.
_COLLECTORS: WeakKeyDictionary[Any, DebugCollector] = WeakKeyDictionary()

_IDLE = {"active": False, "final": False, "rows": 0, "bytes": 0, "started_at": None}


def _store(hass: HomeAssistant, entry_id: str) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(hass, DEBUG_STORE_VERSION, f"{DOMAIN}_{entry_id}_debug")


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

    async def async_load(self) -> None:
        raw = await load_mapping(self._store, "the debug collection") or {}
        self.started_at = stored_instant(raw.get("started_at"))
        if self.started_at is None:  # a ring with no start cannot be bounded to a week
            return
        self.final = raw.get("final") is True
        self.rows = _kept(raw, "rows", {"t"})
        self.snapshots = _kept(raw, "snapshots", {"t", "cycle", "data"})

    def as_dict(self) -> dict[str, Any]:
        start = {"started_at": self.started_at.isoformat()} if self.started_at else {}
        return {**start, "final": self.final, "rows": list(self.rows),
                "snapshots": list(self.snapshots)}

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
            self.finalize()
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

    def finalize(self) -> None:
        self.final = True
        self._spawn(self.async_save())

    def restart(self) -> None:
        self.started_at, self.final, self.rows, self.snapshots = None, False, [], []
        self._saved_at = None
        self._spawn(self.async_save())

    def status(self) -> dict[str, Any]:
        return {
            "active": not self.final, "final": self.final, "rows": len(self.rows),
            "bytes": len(_dumps(self.as_dict()).encode()),
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

    async def async_bundle(self, coordinator: Any, diagnostics: Any = None) -> dict[str, Any]:
        """The ``hpo-debug/1`` bundle; ``replay`` is the repo-side harness's to fill."""
        keys = [f"{DOMAIN}_{self._entry_id}_{name}" for name in DOMAINS if name != "debug"]
        stores = await self._hass.async_add_executor_job(
            _read_stores, Path(self._hass.config.path(".storage")), keys
        )
        return {
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
                "store_versions": {key: version for key, (version, _d) in stores.items()},
            },
            "replay": None,
            "cycle_rows": list(self.rows),
            "payload_snapshots": [{**s, "data": _parsed(s["data"])} for s in self.snapshots],
            "stores": {key: data for key, (_v, data) in stores.items()},
            "diagnostics": diagnostics,
        }


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
        collector.finalize()
    elif action == "start" and collector.final:
        collector.restart()
    return collector.status()
