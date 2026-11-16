"""The room list (#3616): what a list of room thermometers says now.

An install may name the thermometers of its rooms -- room thermostats
(``climate``) or plain temperature sensors -- beside the one indoor sensor the
model runs on. This module owns that list's reading record, its summary (the
mean, and the spread between the coldest and the warmest room) and the payload
block the room sensors publish. The read itself is ``inputs.read_room``'s.

Module state: one per-coordinator side table holding the last cycle's readings,
``boost.py``'s ``WeakKeyDictionary`` pattern, so the coordinator gains no
attribute. A room reading never enters ``InputHealth``: one dead thermostat
among twenty is this list's to report, as a dropped room, and never an input
problem or a stale input.

Free of Home Assistant imports: the coordinator passes the readings in.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from weakref import WeakKeyDictionary

from .payload import Room, Rooms, RoomsView

#: The longest list the options page stores: a large house's thermostats, and
#: a bound on one cycle's reads.
ROOMS_MAX = 32


@dataclass(frozen=True)
class RoomReading:
    """One room thermometer, read once.

    ``temperature_c`` is kept on a stale reading, as ``InputReading.value``
    is, and withheld on an implausible one; :func:`usable_c` is what the summary uses.
    ``target_c``, ``calling`` and ``hvac_mode`` are a ``climate``'s, None for
    a sensor; ``calling`` is None where the thermostat reports no action.
    """

    entity_id: str
    temperature_c: float | None
    target_c: float | None = None
    calling: bool | None = None
    hvac_mode: str | None = None
    problem: str | None = None


def usable_c(reading: RoomReading) -> float | None:
    """The temperature the summary may use: None for a room with a problem."""
    return reading.temperature_c if reading.problem is None else None


@dataclass(frozen=True)
class RoomSummary:
    """The readable rooms' mean, degC, and spread, K, with the rooms that set them."""

    mean_c: float
    spread_c: float
    coldest_entity: str
    warmest_entity: str
    valid_count: int


def summarize(readings: Sequence[RoomReading]) -> RoomSummary | None:
    """The summary, or None under the quorum: fewer than half the list
    readable, minimum one -- a mean of two rooms out of twenty is not the
    house's."""
    valid = [(t, r.entity_id) for r in readings if (t := usable_c(r)) is not None]
    if not valid or 2 * len(valid) < len(readings):
        return None
    coldest, warmest = min(valid), max(valid)
    return RoomSummary(
        mean_c=sum(t for t, _ in valid) / len(valid),
        spread_c=warmest[0] - coldest[0],
        coldest_entity=coldest[1],
        warmest_entity=warmest[1],
        valid_count=len(valid),
    )


_READINGS: WeakKeyDictionary[Any, tuple[RoomReading, ...]] = WeakKeyDictionary()


def record(owner: Any, readings: Sequence[RoomReading]) -> None:
    """Keep ``owner``'s (a coordinator's) readings of this cycle."""
    _READINGS[owner] = tuple(readings)


def readings_of(owner: Any) -> tuple[RoomReading, ...]:
    """``owner``'s last readings; () before the first cycle or with no list."""
    return _READINGS.get(owner, ())


def published(readings: Sequence[RoomReading]) -> RoomsView:
    """The payload's ``rooms`` block; no key at all with no list, so an
    install that configures none publishes exactly what it did before."""
    if not readings:
        return {}
    summary = summarize(readings)
    block: Rooms = {
        "configured_count": len(readings),
        "valid_count": 0 if summary is None else summary.valid_count,
        "average": None if summary is None else round(summary.mean_c, 2),
        "spread": None if summary is None else round(summary.spread_c, 2),
        "coldest_entity": None if summary is None else summary.coldest_entity,
        "warmest_entity": None if summary is None else summary.warmest_entity,
        "per_room": {r.entity_id: _room(r, t) for r in readings if (t := usable_c(r)) is not None},
        "dropped": {r.entity_id: str(r.problem) for r in readings if usable_c(r) is None},
    }
    return {"rooms": block}


def _room(reading: RoomReading, temperature_c: float) -> Room:
    """One readable room as published: a thermostat's target and state beside it."""
    return {
        "temperature": round(temperature_c, 2),
        "target": None if reading.target_c is None else round(reading.target_c, 2),
        "calling": reading.calling,
        "hvac_mode": reading.hvac_mode,
    }
