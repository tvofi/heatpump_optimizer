"""Room history and the identifiability report (#3616, phase 3a).

Phase 4 (a per-room model) and phase 5 (per-room control) rest on one question
this module answers from measurement: can a room be modelled apart from the
others? It keeps, per 30-minute period, each listed room's temperature, target
and share of samples calling for heat, beside the house's outdoor and floor
return temperatures, measured power and the share of cycles spent on space
heating -- and reads that ring into a per-room verdict and one house line, the
evidence the loop-capacity limit (phase 3b) will be fitted on.

The ring, the row builder and the report are pure (numpy only). The glue holds
one record per coordinator in a ``WeakKeyDictionary`` with its own
``QuarantiningStore`` (``duty_switch.py``'s pattern), loaded on first use and
saved every :data:`SAVE_EVERY_ROWS` closed rows and at unload. Nothing here is
read by the plan: the report goes to diagnostics and one sensor only.

An install with no room list makes no record, no store file and no row.
"""
from __future__ import annotations

import logging
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from weakref import WeakKeyDictionary

import numpy as np

from .accuracy import HISTORY_LENGTH
from .const import DOMAIN, FLOOR_WATER_RANGE_C, OUTDOOR_AIR_RANGE_C, ROOM_AIR_RANGE_C
from .rooms import RoomReading, usable_c
from .store import QuarantiningStore

_LOGGER = logging.getLogger(__name__)

ROOM_HISTORY_STORE_VERSION = 1
#: One row per half hour whatever the entry's interval (10 to 120 min), so the
#: row count, and the 14 days :data:`HISTORY_LENGTH` rows span, never depend on it.
PERIOD_MIN = 30
#: Saved every 12th closed row (6 h): a crash loses at most that much of a
#: 14-day record, and the Pi's card is written four times a day, not 48.
SAVE_EVERY_ROWS = 12

#: Every stored value is an integer in hundredths of its unit; a share is in
#: hundredths of a percent, so 10000 is "every sample".
SCALE = 100
FULL_SHARE = 100 * SCALE
#: A domestic heat pump draws well under 100 kW of electricity; above is a fault.
MEASURED_KW_RANGE = (0.0, 100.0)
_RANGES: dict[str, tuple[float, float]] = {
    "t": ROOM_AIR_RANGE_C, "target": ROOM_AIR_RANGE_C, "call": (0.0, 100.0),
    "outdoor": OUTDOOR_AIR_RANGE_C, "return": FLOOR_WATER_RANGE_C,
    "power": MEASURED_KW_RANGE, "space": (0.0, 100.0),
}
ROOM_FIELDS = ("t", "target", "call")
HOUSE_FIELDS = ("outdoor", "return", "power", "space")

# The report's thresholds, one reasoning and no measurement behind them, as
# duty_switch.py says of its own: they are where a verdict stops being noise.
#: Three days of half-hour pairs: enough nights and days to see a response.
MIN_PAIRS = 144
#: A period counts as "calling" when the room called in half its samples or more.
CALLING_SHARE = 50 * SCALE
#: Under 5 % or over 95 % of periods calling leaves the fit no contrast.
NEVER_FRACTION = 0.05
ALWAYS_FRACTION = 0.95
#: Two rooms whose calling moves together this closely cannot be told apart.
COLLINEAR_R = 0.9
#: The calling gain must stand three standard errors clear of zero.
MIN_T = 3.0
#: A pair of rows further apart than this is two separate stretches, not a step.
PAIR_GAP_MIN = 120
#: The house's calling fraction must move: its interquartile range at least this.
FLAT_IQR = 0.25


@dataclass(frozen=True)
class House:
    """The house values one cycle hands in; None where not measured."""

    outdoor_c: float | None
    floor_return_c: float | None
    measured_kw: float | None
    space_kw: float
    dhw_kw: float


@dataclass
class History:
    """The ring: row times (UTC epoch minutes) and centi-unit columns, None missing."""

    times: list[int] = field(default_factory=list)
    rooms: dict[str, dict[str, list[int | None]]] = field(default_factory=dict)
    house: dict[str, list[int | None]] = field(
        default_factory=lambda: {f: [] for f in HOUSE_FIELDS})


@dataclass
class _Period:
    """The open half hour's running tallies."""

    start: int
    rooms: dict[str, list[Any]] = field(default_factory=dict)  # [first t, last target, calls, samples]
    outdoor: float | None = None
    floor_return: float | None = None
    power: list[float] = field(default_factory=list)
    space: int = 0
    cycles: int = 0


def _centi(value: float | None, name: str) -> int | None:
    """``value`` in hundredths, or None when missing, non-finite or out of range."""
    lo, hi = _RANGES[name]
    if value is None or not math.isfinite(value) or not lo <= value <= hi:
        return None
    return round(value * SCALE)


def _share(hits: int, samples: int) -> int | None:
    return round(FULL_SHARE * hits / samples) if samples else None


def _accumulate(period: _Period, readings: Sequence[RoomReading], house: House) -> None:
    for reading in readings:
        tally = period.rooms.setdefault(reading.entity_id, [None, None, 0, 0])
        if tally[0] is None:  # the period's first reading: its calling acts from there on
            tally[0] = _centi(usable_c(reading), "t")
        if (target := _centi(reading.target_c, "target")) is not None:
            tally[1] = target
        if reading.problem is None and reading.calling is not None:
            tally[2] += bool(reading.calling)
            tally[3] += 1
    if (outdoor := _centi(house.outdoor_c, "outdoor")) is not None:
        period.outdoor = outdoor
    if (floor_return := _centi(house.floor_return_c, "return")) is not None:
        period.floor_return = floor_return
    if (kw := _centi(house.measured_kw, "power")) is not None:
        period.power.append(kw)
    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0
    period.cycles += 1


def _append(history: History, start: int, rooms: Mapping[str, list[Any]] | None,
            house: Mapping[str, int | None] | None) -> None:
    """One row at ``start``; ``rooms`` None is a missing period (every cell null)."""
    width = len(history.times)
    history.times.append(start)
    if rooms is not None:
        for gone in set(history.rooms) - set(rooms):
            del history.rooms[gone]
        for entity in rooms:
            history.rooms.setdefault(entity, {f: [None] * width for f in ROOM_FIELDS})
    for entity, columns in history.rooms.items():
        tally = None if rooms is None else rooms[entity]
        columns["t"].append(None if tally is None else tally[0])
        columns["target"].append(None if tally is None else tally[1])
        columns["call"].append(None if tally is None else _share(tally[2], tally[3]))
    for name in HOUSE_FIELDS:
        history.house[name].append(None if house is None else house[name])


def _close(history: History, period: _Period) -> None:
    """The open period as a row, null rows for any half hour missed before it,
    then everything older than the ring's 14 days dropped."""
    cut = period.start - (HISTORY_LENGTH - 1) * PERIOD_MIN
    if history.times:
        for start in range(max(history.times[-1] + PERIOD_MIN, cut), period.start, PERIOD_MIN):
            _append(history, start, None, None)
    house = {
        "outdoor": period.outdoor, "return": period.floor_return,
        "power": round(sum(period.power) / len(period.power)) if period.power else None,
        "space": _share(period.space, period.cycles),
    }
    _append(history, period.start, period.rooms, house)
    keep = next(i for i, t in enumerate(history.times) if t >= cut)
    if keep:
        del history.times[:keep]
        for columns in (*history.rooms.values(), history.house):
            for name in columns:
                del columns[name][:keep]


def note(history: History, period: _Period | None, now_min: int,
         readings: Sequence[RoomReading], house: House) -> tuple[_Period | None, int]:
    """Fold one cycle in: ``(the open period, rows closed)``.

    A sample whose half hour lies before the open period, or at or before the
    ring's last row (a clock stepped back), is dropped: the ring's times never
    run backwards.
    """
    start = now_min - now_min % PERIOD_MIN
    floor = period.start if period is not None else (history.times[-1] + 1 if history.times else start)
    if start < floor:
        return period, 0
    closed = 0
    if period is not None and start > period.start:
        _close(history, period)
        period, closed = None, 1
    period = period or _Period(start)
    _accumulate(period, readings, house)
    return period, closed


# --- the store: one comma-joined string per column (a JSON list is three times the size)

def _pack(column: Sequence[int | None]) -> str:
    return ",".join("" if v is None else str(v) for v in column)


def _unpack(text: Any, name: str, width: int) -> list[int | None] | None:
    """A column, or None when any cell is unparsable, out of range or the length is wrong."""
    if not isinstance(text, str):
        return None
    lo, hi = _RANGES[name]
    try:
        cells = [None if c == "" else int(c) for c in text.split(",")] if width else []
    except ValueError:
        return None
    if len(cells) != width or any(c is not None and not lo * SCALE <= c <= hi * SCALE for c in cells):
        return None
    return cells


def stored(history: History) -> dict[str, Any]:
    """The store document."""
    return {
        "times": _pack(history.times),
        "rooms": {e: {f: _pack(c[f]) for f in ROOM_FIELDS} for e, c in history.rooms.items()},
        "house": {f: _pack(history.house[f]) for f in HOUSE_FIELDS},
    }


def _times(text: Any) -> list[int] | None:
    """The row times, or None unless each is a half hour on from the last at least."""
    try:
        times = [int(t) for t in text.split(",")] if text else []
    except (AttributeError, ValueError):
        return None
    if any(b - a < PERIOD_MIN or b % PERIOD_MIN for a, b in zip([t - PERIOD_MIN for t in times[:1]] + times, times)):
        return None
    return times


def _columns(columns: Any, fields: Sequence[str], width: int) -> dict[str, list[int | None]] | None:
    """One room's (or the house's) columns, or None when any of them is bad."""
    parsed = {f: _unpack(columns.get(f), f, width) for f in fields} if isinstance(columns, Mapping) else {}
    if len(parsed) != len(fields) or any(c is None for c in parsed.values()):
        return None
    return parsed  # type: ignore[return-value]


def loaded(raw: Any) -> History:
    """The ring a store document holds. A bad times column empties it; a bad
    room cell drops that room's ring whole, a bad house cell the house columns
    (left null), never one cell."""
    times = _times(raw.get("times")) if isinstance(raw, Mapping) else None
    if times is None:
        return History()
    rooms = raw.get("rooms") if isinstance(raw.get("rooms"), Mapping) else {}
    parsed = {str(e): _columns(c, ROOM_FIELDS, len(times)) for e, c in rooms.items()}
    house = _columns(raw.get("house"), HOUSE_FIELDS, len(times))
    return History(times, {e: c for e, c in parsed.items() if c is not None},
                   house or {f: [None] * len(times) for f in HOUSE_FIELDS})


# --- the report

def _pairs(history: History, column: Sequence[int | None]) -> list[tuple[int, int]]:
    """Successive rows both holding ``column``, outdoor and the first row's calling share,
    at most :data:`PAIR_GAP_MIN` apart: a 60-minute entry's pairs skip its null rows."""
    outdoor = history.house["outdoor"]
    rows = [i for i, v in enumerate(column) if v is not None and outdoor[i] is not None]
    return [(i, j) for i, j in zip(rows, rows[1:])
            if history.times[j] - history.times[i] <= PAIR_GAP_MIN]


def _fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    """Least squares coefficients and their t-statistics, or None when degenerate."""
    if len(y) <= x.shape[1]:
        return None
    coef, _res, rank, _sv = np.linalg.lstsq(x, y, rcond=None)
    if rank < x.shape[1]:
        return None
    resid = y - x @ coef
    sigma2 = float(resid @ resid) / (len(y) - x.shape[1])
    se = np.sqrt(np.maximum(np.diag(np.linalg.inv(x.T @ x)) * sigma2, 1e-300))
    return coef, coef / se


def _calls(column: Sequence[int | None]) -> np.ndarray:
    return np.array([np.nan if v is None else v / FULL_SHARE for v in column], dtype=float)


def _correlations(calls: Mapping[str, np.ndarray]) -> np.ndarray:
    """|r| of every pair of rooms' calling shares over the rows both hold, NaN
    where fewer than three rows are common or a share does not move there."""
    held = np.array([~np.isnan(c) for c in calls.values()], dtype=float).reshape(len(calls), -1)
    x = np.nan_to_num(np.array(list(calls.values()), dtype=float).reshape(len(calls), -1))
    n = held @ held.T
    with np.errstate(divide="ignore", invalid="ignore"):
        mean_i, mean_sq_i = (x @ held.T) / n, (x * x @ held.T) / n
        cov = (x @ x.T) / n - mean_i * mean_i.T
        var = mean_sq_i - mean_i ** 2
        r = np.abs(cov / np.sqrt(var * var.T))
    r[(n < 3) | ~(var > 1e-12) | ~(var.T > 1e-12)] = np.nan
    np.fill_diagonal(r, np.nan)
    return r


def _collinear(index: int, names: Sequence[str], r: np.ndarray) -> tuple[str, float] | None:
    """The other room whose calling moves most with room ``index``'s, at or above
    :data:`COLLINEAR_R`; None when none does."""
    row = np.where(np.isnan(r[index]), -1.0, r[index])
    best = int(np.argmax(row)) if len(row) else 0
    return (names[best], float(row[best])) if len(row) and row[best] >= COLLINEAR_R else None


def _room_verdict(history: History, entity: str, calls: Mapping[str, np.ndarray],
                  r: np.ndarray) -> dict[str, Any]:
    columns = history.rooms[entity]
    share = calls[entity]
    if np.isnan(share).all():
        return {"code": "no_action"}
    pairs = [(i, j) for i, j in _pairs(history, columns["t"]) if columns["call"][i] is not None]
    if len(pairs) < MIN_PAIRS:
        return {"code": "short_history", "pairs": len(pairs)}
    on = float(np.mean(share[~np.isnan(share)] >= CALLING_SHARE / FULL_SHARE))
    if on < NEVER_FRACTION:
        return {"code": "never_calling", "calling_fraction": round(on, 3)}
    if on > ALWAYS_FRACTION:
        return {"code": "always_calling", "calling_fraction": round(on, 3)}
    if (twin := _collinear(list(calls).index(entity), list(calls), r)) is not None:
        return {"code": "collinear", "with": twin[0], "r": round(twin[1], 3)}
    temp, outdoor = columns["t"], history.house["outdoor"]
    dt_h = np.array([(history.times[j] - history.times[i]) / 60.0 for i, j in pairs])
    rate = np.array([(temp[j] - temp[i]) / SCALE for i, j in pairs]) / dt_h  # type: ignore[operator]
    x = np.array([[(outdoor[i] - temp[i]) / SCALE, share[i], 1.0] for i, _j in pairs])  # type: ignore[operator]
    fitted = _fit(x, rate)
    if fitted is None or fitted[1][1] < MIN_T:  # t carries b's sign: a cooling gain fails here
        return {"code": "no_response", "pairs": len(pairs),
                "t": None if fitted is None else round(float(fitted[1][1]), 2)}
    coef, t = fitted
    return {"code": "separable", "pairs": len(pairs), "a_per_h": round(float(coef[0]), 4),
            "b_k_per_h": round(float(coef[1]), 3), "t": round(float(t[1]), 2)}


def _house_line(history: History, calls: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """Measured power against the calling fraction of the rooms that report one,
    over periods spent mostly on space heating: the curve phase 3b fits."""
    power, space = history.house["power"], history.house["space"]
    if all(p is None for p in power):
        return {"verdict": "no_power_meter"}
    stack = np.array(list(calls.values())) if calls else np.full((1, len(power)), np.nan)
    reported = (~np.isnan(stack)).sum(axis=0)
    fraction = np.divide(np.nansum(stack, axis=0), reported, out=np.full(len(power), np.nan), where=reported > 0)
    rows = [i for i, p in enumerate(power)
            if p is not None and space[i] is not None and space[i] >= CALLING_SHARE and reported[i]]
    if len(rows) < MIN_PAIRS:
        return {"verdict": "short_history", "rows": len(rows)}
    xs = fraction[rows]
    q1, q3 = np.percentile(xs, [25, 75])
    if q3 - q1 < FLAT_IQR:
        return {"verdict": "calling_fraction_flat", "rows": len(rows)}
    fitted = _fit(np.column_stack([xs, np.ones(len(rows))]), np.array([power[i] / SCALE for i in rows]))  # type: ignore[operator]
    if fitted is None:
        return {"verdict": "calling_fraction_flat", "rows": len(rows)}
    return {"verdict": "enough", "rows": len(rows), "slope_kw": round(float(fitted[0][0]), 3),
            "t": round(float(fitted[1][0]), 2)}


def report(history: History) -> dict[str, Any]:
    """Per room the first verdict that applies, in the order the codes are tried,
    and the house line."""
    calls = {e: _calls(c["call"]) for e, c in history.rooms.items()}
    r = _correlations(calls)
    return {
        "rows": len(history.times),
        "rooms": {e: _room_verdict(history, e, calls, r) for e in history.rooms},
        "house": _house_line(history, calls),
    }


# --- the glue

@dataclass
class _Record:
    store: QuarantiningStore
    history: History = field(default_factory=History)
    period: _Period | None = None
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
        rec = _RECORDS[coord] = _Record(QuarantiningStore(
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


def separable_count(view: Mapping[str, Any] | None) -> int | None:
    """The sensor's state: how many rooms read separable."""
    if view is None:
        return None
    return sum(v["code"] == "separable" for v in view["rooms"].values())
