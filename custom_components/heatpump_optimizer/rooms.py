"""The room list (#3616): what a list of room thermometers says now.

An install may name the thermometers of its rooms -- room thermostats
(``climate``) or plain temperature sensors -- beside the one indoor sensor the
model runs on. This module owns that list's reading record, its summary (the
mean, and the spread between the coldest and the warmest room) and the payload
block the room sensors publish. The read itself is ``inputs.read_room``'s.

Phase 2 adds the floor lift: a room short of its own target raises the
solve's comfort floor, through the margin array the solver already takes, by
no more than the house's own band (:func:`lifted_margins`).

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
from datetime import datetime
from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

import numpy as np

from .optimizer import _padded_nonneg, _step_clock
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
    its floor at that solve, K, where the ramp starts."""

    lift_c: float = 0.0
    entity_id: str | None = None
    gate: str | None = None
    anchor_c: float = 0.0


_LIFTS: WeakKeyDictionary[Any, HeldLift] = WeakKeyDictionary()


def lift_of(owner: Any) -> HeldLift | None:
    """The lift ``owner``'s last solve was given; None before the first."""
    return _LIFTS.get(owner)


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


def _held(
    readings: Sequence[RoomReading], gated: str | None, house_short_c: float,
    anchor_c: float, previous: HeldLift | None,
) -> HeldLift:
    """This solve's lift: zero under a gate, else the largest room shortfall
    less the house's own, clipped to the cap and held inside the deadband."""
    worst = largest_shortfall(readings)
    if gated is None:
        gated = (
            "no_rooms" if not readings
            else "quorum" if summarize(readings) is None
            else "no_target" if worst is None
            else None if math.isfinite(house_short_c) else "house_unknown"
        )
    if gated is not None or worst is None:
        return HeldLift(gate=gated)
    raw_c = min(max(worst[0] - house_short_c, 0.0), ROOM_LIFT_CAP_C)
    kept_c = 0.0 if previous is None else previous.lift_c
    lift_c = raw_c if abs(raw_c - kept_c) >= ROOM_LIFT_DEADBAND_C else kept_c
    return HeldLift(lift_c, worst[1], None, max(anchor_c, 0.0))


def _lifted(
    held: HeldLift | None, base: np.ndarray | None, config: OptimizationConfig,
    start_time: datetime, n_steps: int,
) -> np.ndarray | None:
    """``base`` plus the held lift, per step the smallest of the lift, the
    ramp from the anchor, and what the step's band leaves under its comfort
    target; ``base`` itself where no step is lifted.

    The band is read from ``config``'s own two methods at the solve's step
    times, the calls ``_build_comfort_bounds`` makes, so the lifted floor
    never passes the target the same solve pulls towards. A step on a
    holiday date takes no lift, as a house that is away takes none.
    """
    if held is None or held.lift_c <= 0.0:
        return base
    times, hours = _step_clock(start_time, n_steps, config.dt_hours)
    margins = _padded_nonneg(() if base is None else base, n_steps)
    band = np.array([
        0.0 if t.date() in config.holiday_dates
        else config.get_comfort_temp(h, when=t) - config.get_temp_bounds(h, when=t)[0]
        for h, t in zip(hours, times)
    ]) - margins
    ramp = held.anchor_c + ROOM_LIFT_RAMP_C_PER_H * config.dt_hours * np.arange(n_steps)
    lift = np.clip(np.minimum(np.minimum(band, ramp), held.lift_c), 0.0, None)
    return margins + lift if lift.any() else base


def lifted_margins(
    owner: Any, base: np.ndarray | None, config: OptimizationConfig,
    house_c: float, start_time: datetime, n_steps: int, gated: str | None,
) -> np.ndarray | None:
    """The scheduled solve's floor margins: ``base`` (the confidence margins,
    or None) plus the room lift, and ``base`` itself under any gate.

    Resolves and keeps ``owner``'s lift for this solve from its last
    readings. ``gated`` is :func:`gate`'s word; a solve starting on a holiday
    date is gated too. The house's shortfall is against step 0's comfort
    target of ``config``, and the ramp's anchor is the house's margin over
    step 0's floor with ``base`` on it.
    """
    times, hours = _step_clock(start_time, 1, config.dt_hours)
    if gated is None and times[0].date() in config.holiday_dates:
        gated = "holiday"
    floor_c = config.get_temp_bounds(hours[0], when=times[0])[0] + float(_padded_nonneg(() if base is None else base, 1)[0])
    held = _held(
        readings_of(owner), gated,
        config.get_comfort_temp(hours[0], when=times[0]) - house_c,
        house_c - floor_c, _LIFTS.get(owner),
    )
    _LIFTS[owner] = held
    return _lifted(held, base, config, start_time, n_steps)


def held_margins(
    owner: Any, base: np.ndarray | None, config: OptimizationConfig,
    start_time: datetime, n_steps: int,
) -> np.ndarray | None:
    """A what-if's floor margins: the lift and anchor ``owner``'s last
    scheduled solve was given, never a recomputed one, clipped to the band of
    the what-if's own ``config``. A lift resolved afresh would put the rooms'
    drift since the baseline into the difference the what-if reports."""
    return _lifted(_LIFTS.get(owner), base, config, start_time, n_steps)
