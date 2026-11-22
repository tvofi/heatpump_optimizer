"""The pump's fault record (R11-OWNER-FAULT-TEXT): each fault's code, start and end.

One record per config entry, in a ``WeakKeyDictionary`` keyed by the entry
(``off_restore``'s precedent), with its own ``QuarantiningStore``. The source is
one rule per install:

* ``text``: the fault-text slot, 1 to 4 entities whose state is ``OK`` or a
  comma list of codes. A member is healthy when its state is in
  :data:`HEALTHY`; every other text is recorded as the code, because the slot
  exists for vocabularies this integration does not know.
* ``bitmap`` / ``flag``: no text slot, so the fault-alarm flag slot, read as
  ``InputReader.read_bool`` reads it. An integral number is kept as hex (the
  register), anything else as a time span with no code.
* neither: no record, no listener, no store.

A state-change listener stamps every change with the state's ``last_changed``,
so a fault that clears inside an update cycle is still a row. The record is
saved on every row opened or closed, at most once per :data:`SAVE_MIN_S`: a
save asked for inside that window is deferred to its end, never dropped.

Only ``__init__`` (setup, unload) and ``diagnostics`` (the view) import this.
The pure core -- :func:`note`, :func:`code_text`, :func:`flag_text`,
:func:`loaded`, :func:`stored` -- runs without Home Assistant.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event

from .const import (
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES,
    DOMAIN,
    FAULT_TEXT_ENTITIES_MAX,
)
from .inputs import AMBIGUOUS_ACTIVITY_TOKENS, BOOL_FALSE, is_flag_domain, parse_bool
from .store import QuarantiningStore, admitted, load_mapping

__all__ = ["async_close", "async_setup", "diagnostics_view"]

_LOGGER = logging.getLogger(__name__)

FAULT_LOG_STORE_VERSION = 1
#: Closed rows kept, oldest evicted first (a row is at most ~361 B in memory).
EPISODES_MAX = 200
#: Distinct code texts tallied; the rest fold into :data:`OTHER`.
CODES_MAX = 32
OTHER = "other"
#: A row's code text keeps whole items within this many characters.
TEXT_MAX_CHARS = 160
#: At most one save per this many seconds; a 1 Hz flap writes once a minute.
SAVE_MIN_S = 60.0
#: A member reading one of these, stripped and case-folded, reports no fault.
HEALTHY: frozenset[str] = frozenset(
    {"ok", "none", "normal", "no fault", ""} | BOOL_FALSE | AMBIGUOUS_ACTIVITY_TOKENS
)
#: A flag-slot fault with no code: recorded as a span, shown with a null code.
NO_CODE = ""
_UNREAD = ("unavailable", "unknown")


@dataclass
class Log:
    """The pure record: closed rows, the open one, the per-code tally."""

    since_s: int
    source: str | None = None
    #: ``[start_s, end_s, text, late]``, oldest first.
    episodes: list[list[Any]] = field(default_factory=list)
    dropped: int = 0
    #: ``[start_s, text]`` while a fault is open.
    open: list[Any] | None = None
    #: ``text -> [count, total_s, last_end_s]``.
    codes: dict[str, list[int]] = field(default_factory=dict)


def _tally(log: Log, text: str, start_s: int, end_s: int) -> None:
    if text == NO_CODE:
        return
    key = text if text in log.codes or len(log.codes) < CODES_MAX else OTHER
    row = log.codes.setdefault(key, [0, 0, 0])
    row[0] += 1
    row[1] += end_s - start_s
    row[2] = end_s


def note(log: Log, now_s: int, text: str | None, *, late: bool = False) -> bool:
    """Apply one reading: ``text`` is the fault's code text, ``None`` healthy.

    Whether a row opened or closed. A change of text while open closes the row
    and opens the next at the same instant. ``late`` marks the row this
    reading closes as one that ended while nothing was watching.
    """
    if log.open is not None and log.open[1] == text:
        return False
    if log.open is None and text is None:
        return False
    if log.open is not None:
        start_s, was = log.open
        end_s = max(now_s, start_s)
        log.episodes.append([start_s, end_s, was, late])
        _tally(log, was, start_s, end_s)
        if len(log.episodes) > EPISODES_MAX:
            del log.episodes[0]
            log.dropped += 1
        log.open = None
    if text is not None:
        log.open = [now_s, text]
    return True


def _clip(item: str) -> str:
    """An item longer than the cap keeps its tail: GCHV names end in the code."""
    return item if len(item) <= TEXT_MAX_CHARS else "…" + item[-TEXT_MAX_CHARS:]


def code_text(states: Sequence[str | None]) -> str | None:
    """The fault members' items in slot order, or ``None`` when every member is healthy.

    ``None`` members (never read) count as healthy. Items are kept whole while
    the text stays within :data:`TEXT_MAX_CHARS`; `` +N`` counts those dropped.
    """
    items = [
        part.strip()
        for state in states
        if state is not None and state.strip().casefold() not in HEALTHY
        for part in state.split(",")
        if part.strip()
    ]
    if not items:
        return None
    kept: list[str] = []
    length = 0
    for item in map(_clip, items):
        add = len(item) + (2 if kept else 0)
        if kept and length + add > TEXT_MAX_CHARS:
            break
        kept.append(item)
        length += add
    dropped = len(items) - len(kept)
    return ", ".join(kept) + (f" +{dropped}" if dropped else "")


def flag_text(entity_id: str, state: str) -> tuple[str, str | None] | None:
    """The flag slot's reading as ``(source, text)``, or ``None`` when it is no reading.

    The canonical strict read: free text that only names an activity is no
    evidence. A fault reading an integral number is the register, in hex.
    """
    flag = parse_bool(state, strict=not is_flag_domain(entity_id))
    if flag is None:
        return None
    if not flag:
        return ("flag", None)
    try:
        number = float(state)
    except (TypeError, ValueError):
        return ("flag", NO_CODE)
    if number.is_integer() and number >= 0:
        return ("bitmap", f"0x{int(number):04X}")
    return ("flag", NO_CODE)


def stored(log: Log) -> dict[str, Any]:
    """The record as its store document, copied: the store serialises it off the loop."""
    return {
        "since_s": log.since_s, "source": log.source, "episodes": [list(r) for r in log.episodes],
        "dropped": log.dropped, "open": None if log.open is None else list(log.open),
        "codes": {k: list(v) for k, v in log.codes.items()},
    }


def loaded(raw: Any, now_s: int) -> Log:
    """A store document as a record; one outside its declaration starts afresh at ``now_s``."""
    if not isinstance(raw, Mapping) or not raw or not admitted("fault_log", raw):
        return Log(now_s)
    episodes = [list(row) for row in raw.get("episodes") or () if len(row) == 4][-EPISODES_MAX:]
    opened = raw.get("open")
    return Log(
        since_s=int(raw.get("since_s", now_s)),
        source=raw.get("source"),
        episodes=episodes,
        dropped=int(raw.get("dropped") or 0),
        open=list(opened) if isinstance(opened, list) and len(opened) == 2 else None,
        codes={k: list(v) for k, v in (raw.get("codes") or {}).items() if len(v) == 3},
    )


def sources(config: Mapping[str, Any]) -> tuple[str, list[str]] | None:
    """``("text", members)`` or ``("flag", [slot])`` from the config, else ``None``."""
    members = [e for e in config.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or () if e]
    if members:
        return ("text", members[:FAULT_TEXT_ENTITIES_MAX])
    flag = config.get(CONF_HEAT_PUMP_FAULT_ENTITY)
    return ("flag", [flag]) if flag else None


@dataclass
class _Record:
    hass: HomeAssistant
    store: QuarantiningStore[dict[str, Any]]
    kind: str
    entities: list[str]
    log: Log
    #: Each text member's last readable state; an unavailable one keeps it.
    last: dict[str, str] = field(default_factory=dict)
    #: True until the first reading after load decides the restored open row.
    fresh: bool = True
    closed: bool = False
    unsub: Callable[[], None] | None = None
    timer: Callable[[], None] | None = None
    saved_at: float | None = None


_RECORDS: WeakKeyDictionary[Any, _Record] = WeakKeyDictionary()


def _seconds(state: Any) -> int:
    stamp = getattr(state, "last_changed", None)
    if not isinstance(stamp, datetime):
        stamp = datetime.now(timezone.utc)
    return int(stamp.timestamp())


def _reading(rec: _Record, entity_id: str, state: Any) -> tuple[bool, str | None]:
    """``(readable, text)`` after ``entity_id`` reads ``state``."""
    raw = getattr(state, "state", None)
    if raw is None or str(raw).strip().lower() in _UNREAD:
        return (False, None)
    raw = str(raw)
    if rec.kind == "text":
        rec.last[entity_id] = raw
        rec.log.source = "text"
        return (True, code_text([rec.last.get(e) for e in rec.entities]))
    read = flag_text(entity_id, raw)
    if read is None:
        return (False, None)
    rec.log.source = read[0]
    return (True, read[1])


def _apply(rec: _Record, changes: Sequence[tuple[str, Any]]) -> None:
    """Note what ``changes`` leave the source reading, stamped by the latest of them.

    Setup hands every member at once, so a restored open row is decided on the
    whole slot, never on its first member alone.
    """
    read = [(_seconds(state), text) for entity_id, state in changes
            for ok, text in [_reading(rec, entity_id, state)] if ok]
    if not read:
        return
    late, rec.fresh = rec.fresh, False
    note(rec.log, max(s for s, _t in read), read[-1][1], late=late)


def _request_save(rec: _Record) -> None:
    """Save now, or once the window since the last save has passed."""
    if rec.closed or rec.timer is not None:
        return
    wait = 0.0 if rec.saved_at is None else rec.saved_at + SAVE_MIN_S - time.monotonic()
    if wait <= 0:
        rec.hass.async_create_task(_save(rec))
        return

    @callback
    def _due(_now: Any) -> None:
        rec.timer = None
        rec.hass.async_create_task(_save(rec))

    rec.timer = async_call_later(rec.hass, wait, _due)


async def _save(rec: _Record) -> None:
    rec.saved_at = time.monotonic()
    try:
        await rec.store.async_save(stored(rec.log))
    except Exception as err:  # noqa: BLE001 - the next open or close saves again
        _LOGGER.debug("Could not save the fault record: %s", err)


async def async_setup(hass: HomeAssistant, entry: Any, config: Mapping[str, Any]) -> None:
    """Build the entry's record afresh, load it, read once, subscribe, hook the stop."""
    _RECORDS.pop(entry, None)
    source = sources(config)
    if source is None:
        return
    kind, entities = source
    store: QuarantiningStore[dict[str, Any]] = QuarantiningStore(
        hass, FAULT_LOG_STORE_VERSION, f"{DOMAIN}_{entry.entry_id}_fault_log")
    raw = await load_mapping(store, "the fault record")
    rec = _RECORDS[entry] = _Record(
        hass, store, kind, entities, loaded(raw, int(datetime.now(timezone.utc).timestamp())))
    _apply(rec, [(e, s) for e in entities if (s := hass.states.get(e)) is not None])

    @callback
    def _changed(event: Any) -> None:
        if not rec.closed:
            _apply(rec, [(event.data.get("entity_id"), event.data.get("new_state"))])

    rec.unsub = async_track_state_change_event(hass, entities, _changed)

    async def _stop(_event: Any) -> None:
        await async_close(entry)

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _stop))


async def async_close(entry: Any) -> None:
    """Unsubscribe, cancel the deferred save, then save; a second call does nothing."""
    rec = _RECORDS.get(entry)
    if rec is None or rec.closed:
        return
    rec.closed = True
    for release in (rec.unsub, rec.timer):
        if release is not None:
            release()
    rec.unsub = rec.timer = None
    await _save(rec)


def _iso(seconds: int) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def diagnostics_view(entry: Any) -> dict[str, Any] | None:
    """The download's section: ``None`` with no source configured."""
    rec = _RECORDS.get(entry)
    if rec is None:
        return None
    log = rec.log
    now_s = int(datetime.now(timezone.utc).timestamp())
    return {
        "source": log.source,
        "entities": list(rec.entities),
        "open": None if log.open is None else {
            "start": _iso(log.open[0]), "seconds": max(0, now_s - log.open[0]),
            "code": log.open[1] or None},
        "episodes": [
            {"start": _iso(s), "end": _iso(e), "seconds": e - s, "code": t or None, "late": late}
            for s, e, t, late in log.episodes
        ],
        "dropped": log.dropped,
        "codes": {k: {"count": n, "seconds": total, "last_end": _iso(end)} for k, (n, total, end) in log.codes.items()},
        "since": _iso(log.since_s),
    }
