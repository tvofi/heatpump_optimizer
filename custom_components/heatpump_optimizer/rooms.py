"""The room list (#3616): what a list of room thermometers says now.

An install may name the thermometers of its rooms -- room thermostats
(``climate``) or plain temperature sensors -- beside the one indoor sensor the
model runs on. This module owns that list's reading record, its summary (the
mean, and the spread between the coldest and the warmest room) and the payload
block the room sensors publish. The read itself is ``inputs.read_room``'s.

Phase 2 adds the floor lift: a room short of its own target raises the
solve's comfort floor, through the margin array the solver already takes, by
no more than the house's own band (:func:`resolve`, :func:`lifted`).

Module state: two per-coordinator side tables, the last cycle's readings and
the lift the last solve was given, ``boost.py``'s ``WeakKeyDictionary``
pattern, so the coordinator gains no attribute. A room reading never enters ``InputHealth``: one dead thermostat
among twenty is this list's to report, as a dropped room, and never an input
problem or a stale input.

Free of Home Assistant imports: the coordinator passes the readings in.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

import numpy as np

from .drift import utc_step_starts
from .payload import Room, RoomLift, Rooms, RoomsView

if TYPE_CHECKING:
    from .optimizer import OptimizationConfig

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


def published(readings: Sequence[RoomReading], lift: HeldLift | None = None) -> RoomsView:
    """The payload's ``rooms`` block; no key at all with no list, so an
    install that configures none publishes exactly what it did before.
    ``lift`` is the last solve's (:func:`lift_of`), None before the first."""
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
        "lift": None if lift is None else _lift(lift),
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


def _lift(held: HeldLift) -> RoomLift:
    """The held lift as published: its size, the room that set it, and the
    gate that zeroed it."""
    return {
        "size": round(held.lift_c, 2),
        "entity": held.entity_id if held.lift_c > 0.0 else None,
        "gate": held.gate,
    }


# -- The floor lift (phase 2) ------------------------------------------------

#: The most a room may raise the floor, K: a second bound under the house's
#: band, for a band wider than a room's reading can be trusted to move.
ROOM_LIFT_CAP_C = 1.0
#: How fast the lift may rise from where the house is now, K per hour. The
#: floor penalty has no grace for a state below it, so a lift that starts
#: above the house drives the first steps to full power; at this rate the
#: design's measured mild day stays off the power bound.
ROOM_LIFT_RAMP_C_PER_H = 0.25
#: The held lift moves only when the rooms ask for this much more or less, K:
#: a thermostat reports in tenths, and a floor that follows each tenth
#: re-plans every solve.
ROOM_LIFT_DEADBAND_C = 0.2
#: The HVAC modes in which a thermostat's target is a heating target. A room
#: switched off, or cooling, has a target the plan must not chase.
TARGET_COUNTS_IN = frozenset({"heat", "auto"})


@dataclass(frozen=True)
class HeldLift:
    """What one solve was given: the lift, K, before its per-step clip; the
    room that set it; the gate that zeroed it; and the house's margin over
    its comfort floor at that solve, K (negative under it), which the ramp
    starts from."""

    lift_c: float = 0.0
    entity_id: str | None = None
    gate: str | None = None
    anchor_c: float = 0.0


_LIFTS: WeakKeyDictionary[Any, HeldLift] = WeakKeyDictionary()


def lift_of(owner: Any) -> HeldLift | None:
    """The lift ``owner``'s last solve was given; None before the first."""
    return _LIFTS.get(owner)


def hold(owner: Any, held: HeldLift) -> HeldLift:
    """Keep ``held`` as the lift ``owner``'s (a coordinator's) solve is given."""
    _LIFTS[owner] = held
    return held


def gate(
    *, enabled: bool, economy: bool, open_window: bool, away: bool,
    manual_pin: bool, two_zone: bool,
) -> str | None:
    """The first of the coordinator's signals under which no room lifts the
    floor, by name, or None.

    Economy and away chose a lower floor, and a room does not undo the
    choice; with a window open the coldest room is the one with the window;
    a manual pin's release is judged against the floor, which a lift must not
    move; and a two-zone model applies one margin to both floors while the
    list does not say which floor a room is on.
    """
    fired = {
        "disabled": not enabled, "economy": economy, "open_window": open_window,
        "away": away, "manual_pin": manual_pin, "two_zone": two_zone,
    }
    return next((name for name, on in fired.items() if on), None)


def largest_shortfall(readings: Sequence[RoomReading]) -> tuple[float, str] | None:
    """The readable room furthest under its own target, K, and its entity;
    None where no room has a target that counts (:data:`TARGET_COUNTS_IN`)."""
    short = [
        (r.target_c - t, r.entity_id) for r in readings
        if (t := usable_c(r)) is not None and r.target_c is not None
        and r.hvac_mode in TARGET_COUNTS_IN
    ]
    return max(short) if short else None


def _comfort_at(config: OptimizationConfig, when: datetime) -> tuple[bool, float, float]:
    """For a step starting at ``when``: whether it falls on a holiday date,
    its comfort target and its comfort floor, degC.

    Read from ``config``'s own two methods at the step's hour of day, the
    calls the solver's bound build makes: the day and night rule is not
    restated here.
    """
    hour = when.hour + when.minute / 60.0
    return (
        when.date() in config.holiday_dates,
        config.get_comfort_temp(hour, when=when),
        config.get_temp_bounds(hour, when=when)[0],
    )


def _margins(base: np.ndarray | None, n_steps: int) -> np.ndarray:
    """``base`` as the solver reads it: clipped at zero, fitted to the horizon."""
    fitted = np.zeros(n_steps)
    if base is not None:
        head = np.clip(np.asarray(base, dtype=float)[:n_steps], 0.0, None)
        fitted[:head.size] = head
    return fitted


def resolve(
    readings: Sequence[RoomReading], previous: HeldLift | None, gated: str | None,
    config: OptimizationConfig, house_c: float, start_time: datetime,
) -> HeldLift:
    """The lift a scheduled solve starting at ``start_time`` is given.

    Zero under ``gated`` (:func:`gate`'s word), on a holiday date, and where
    the list has no rooms, no quorum, or no target that counts. Else the
    largest room shortfall less the house's own against step 0's comfort
    target of ``config``, clipped to the cap; ``previous``'s lift is kept
    while the two differ by less than the deadband.
    """
    holiday, target_c, floor_c = _comfort_at(config, start_time)
    worst = largest_shortfall(readings)
    if gated is None:
        gated = (
            "holiday" if holiday
            else "no_rooms" if not readings
            else "quorum" if summarize(readings) is None
            else "no_target" if worst is None
            else None if math.isfinite(house_c) else "house_unknown"
        )
    if gated is not None or worst is None:
        return HeldLift(gate=gated)
    raw_c = min(max(worst[0] - (target_c - house_c), 0.0), ROOM_LIFT_CAP_C)
    kept_c = 0.0 if previous is None else previous.lift_c
    lift_c = raw_c if abs(raw_c - kept_c) >= ROOM_LIFT_DEADBAND_C else kept_c
    return HeldLift(lift_c, worst[1], None, house_c - floor_c)


def lifted(
    held: HeldLift | None, base: np.ndarray | None, config: OptimizationConfig,
    start_time: datetime, n_steps: int,
) -> np.ndarray | None:
    """A solve's floor margins: ``base`` (the confidence margins, or None)
    plus ``held``, and ``base`` itself where no step is lifted.

    Per step the lift is the smallest of the held lift, the ramp, and what
    the step's band leaves over ``base`` under its comfort target, so the
    lifted floor never passes the target the same solve pulls towards. The
    ramp starts at the house's margin over the floor ``base`` already
    raised, never under zero. A step on a holiday date takes no lift, as a
    house that is away takes none.

    A what-if passes the lift its baseline was given (:func:`lift_of`) with
    its own ``config``: a lift resolved afresh would put the rooms' drift
    since the baseline into the difference the what-if reports.
    """
    if held is None or not held.lift_c:
        return base
    margins = _margins(base, n_steps)
    # ``drift.utc_step_starts`` is the one horizon clock: the solver's steps.
    steps = utc_step_starts(start_time, n_steps, timedelta(hours=config.dt_hours))
    band = np.array([
        0.0 if holiday else target_c - floor_c
        for holiday, target_c, floor_c in (_comfort_at(config, t) for t in steps)
    ]) - margins
    ramp = max(held.anchor_c - float(margins[0]), 0.0) \
        + ROOM_LIFT_RAMP_C_PER_H * config.dt_hours * np.arange(n_steps)
    lift = np.clip(np.minimum(np.minimum(band, ramp), held.lift_c), 0.0, None)
    return margins + lift if lift.any() else base
