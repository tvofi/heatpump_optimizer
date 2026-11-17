"""The room history's record (#3616, phase 3a): one ring per coordinator, its store.

The glue around ``room_history.py``'s pure ring and report: one record per
coordinator in a ``WeakKeyDictionary`` with its own ``QuarantiningStore``
(``duty_switch.py``'s pattern), loaded on first use, saved every
:data:`SAVE_EVERY_ROWS` closed rows and at unload. An install with no room list
makes no record, no store file and no row.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .room_history import History, House, Period, loaded, note, report, stored
from .rooms import RoomReading
from .store import QuarantiningStore

__all__ = ["House", "async_flush", "async_note_cycle", "record_of", "report_of"]

_LOGGER = logging.getLogger(__name__)

ROOM_HISTORY_STORE_VERSION = 1
#: Saved every 12th closed row (6 h): a crash loses at most that much of a
#: 14-day record, and the Pi's card is written four times a day, not 48.
SAVE_EVERY_ROWS = 12


@dataclass
class _Record:
    hass: HomeAssistant
    store: QuarantiningStore
    history: History = field(default_factory=History)
    period: Period | None = None
    loaded: bool = False
    unsaved: int = 0
    cached: tuple[tuple[int, int], dict[str, Any]] | None = None


_RECORDS: WeakKeyDictionary[Any, _Record] = WeakKeyDictionary()


def record_of(coord: Any) -> _Record | None:
    """The record, None until a cycle with a room list made one."""
    return _RECORDS.get(coord)


def _record_for(coord: Any) -> _Record:
    rec = _RECORDS.get(coord)
    if rec is None:
        rec = _RECORDS[coord] = _Record(coord.hass, QuarantiningStore(
            coord.hass, ROOM_HISTORY_STORE_VERSION, f"{DOMAIN}_{coord.entry.entry_id}_room_history"))
    return rec


async def _load(rec: _Record) -> None:
    try:
        raw = await rec.store.async_load()
    except Exception as err:  # noqa: BLE001 - an unreadable record starts empty
        _LOGGER.debug("Could not load the room history: %s", err)
        raw = None
    rec.history, rec.loaded = loaded(raw), True


async def _persist(rec: _Record) -> None:
    try:
        await rec.store.async_save(stored(rec.history))
    except Exception as err:  # noqa: BLE001 - still unsaved: saved on the next pass
        _LOGGER.debug("Could not persist the room history: %s", err)
        return
    rec.unsaved = 0


async def async_note_cycle(coord: Any, now: datetime, readings: Sequence[RoomReading], house: House) -> None:
    """One cycle's step: nothing at all without a room list."""
    if not readings:
        return
    rec = _record_for(coord)
    if not rec.loaded:
        await _load(rec)
    rec.period, closed = note(rec.history, rec.period, int(now.timestamp()) // 60, readings, house)
    rec.unsaved += closed
    if rec.unsaved >= SAVE_EVERY_ROWS:
        await _persist(rec)


async def async_flush(coord: Any) -> None:
    """Save what the last save missed (unload, a Home Assistant stop included)."""
    rec = _RECORDS.get(coord)
    if rec is not None and rec.loaded and rec.unsaved:
        await _persist(rec)


def report_of(coord: Any) -> dict[str, Any] | None:
    """The report of ``coord``'s ring, recomputed only when the ring has grown."""
    rec = _RECORDS.get(coord)
    if rec is None or not rec.loaded:
        return None
    key = (len(rec.history.times), rec.history.times[-1] if rec.history.times else 0)
    if rec.cached is None or rec.cached[0] != key:
        rec.cached = (key, report(rec.history))
    return rec.cached[1]
