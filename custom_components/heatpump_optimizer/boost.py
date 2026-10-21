"""Timed boost and block overlays for hot water and space heating.

Each channel is a two-hour maximum-heat overlay on the live action, or a
two-hour block that zeroes that duty. Space boost matches the global boost
mode (nameplate electrical power, the comfort ceiling, full ECL displace).
DHW boost matches the planner's own hot-water ceiling (80 % of nameplate).
The channels are independent: one does not rewrite the other, and neither
stomps comfort or economy the way selecting the global boost mode does. A
block and a boost on one channel exclude each other. A safety floor releases
a block; there is no separate frost-protection feature.

State lives in a Store next to the away override, and in a weak map keyed
by coordinator so the coordinator class does not grow another attribute.
The coordinator adopts each cycle's plan action here, the overlay is
applied to a copy of it, and the switches call in.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol
from weakref import WeakKeyDictionary

from .store import QuarantiningStore, load_mapping
from homeassistant.util import dt as dt_util

from . import away as away_mode
from .accuracy import utc_elapsed_seconds, utc_shift
from .const import (
    DOMAIN,
    ECONOMY_ABSOLUTE_FLOOR,
    MODE_BOOST,
    SPACE_PUMP_FLOOR_MARGIN_C,
)
from .dhw_schedule import DHWWindowError, hour_in_windows, parse_windows
from .drift import stored_instant
from .entity import has_hot_water
from .payload import CurrentAction

_LOGGER = logging.getLogger(__name__)
BOOST_STORE_VERSION = 1
BOOST_HOURS = 2
#: A block is the opposite of a boost: the same two hours, the duty zeroed.
BLOCK_HOURS = 2
_MAX_LEAD = timedelta(hours=max(BOOST_HOURS, BLOCK_HOURS))
_BLOCK_LEAD = timedelta(hours=BLOCK_HOURS)
#: Why a safety floor released a block, published on the switch.
RELEASE_LEGIONELLA = "anti-legionella cycle is due"
RELEASE_DISINFECTION = "disinfection is running"
RELEASE_TANK = "the tank is at its minimum inside a demand window"
RELEASE_ROOM = "the room is at the safety floor"
RELEASE_COLD = "the house is below its plan while it is cold outside"
RELEASE_SYSID = "a measurement experiment is running"
RELEASE_STALE = "the plan is stale"
#: Installed by the pump arbiter. boost does not import that module.
_cold_lease: Any = None
#: #1935: how long after a space overlay ends the interval learners stay
#: frozen. The replay integrates from a plant state propagated open-loop
#: from the PLAN's trajectory, so the slab heat the overlay added -- real in
#: the house, absent from the model's -- keeps every replay residual
#: warm-side until the slab coupling re-equilibrates. The slab's own time
#: constant at the default parameters is C/H = 5.0/0.8 = 6.25 h, and the
#: gate arm measured the pre-study's 2 h guess insufficient on its own
#: (-34 % on the scale across two boost days, with the window freeze
#: already holding); two time constants clear ~86 % of the divergence.
SPACE_SETTLE_TAIL = timedelta(hours=12)
#: The freeze reason ``_learning_frozen`` reports while the space overlay
#: (channel or global mode) is live or settling (#1935).
FREEZE_REASON = "boost_space"
CHANNEL_DHW = "dhw"
CHANNEL_SPACE = "space"
CHANNELS = (CHANNEL_DHW, CHANNEL_SPACE)


@dataclass(frozen=True)
class BoostOverlay:
    """The three numbers the overlay prices its channels with (#1739).

    Built by the coordinator at each cycle from its own members; ``apply``
    receives it instead of reading the coordinator's privates.
    """

    max_power: float
    max_temp: float
    ecl_max: float


class _BoostCoord(Protocol):
    hass: Any
    entry: Any

    def adopt_action(self, action: CurrentAction) -> None: ...

    async def async_request_refresh(self) -> None: ...


@dataclass
class BoostState:
    """Per-channel expiry. A missing key is off."""

    until: dict[str, datetime] = field(default_factory=dict)
    #: Per-duty block expiry. Same channel names as ``until``; a block and a
    #: boost on one channel are never both set.
    blocked: dict[str, datetime] = field(default_factory=dict)
    #: #1935: when the space overlay's settling tail ends -- set when the
    #: overlay ends (expiry or cancel) and when the global boost mode is
    #: left. In-memory only: a restart mid-tail also loses
    #: ``_last_house_sample``, so the first replay after it is skipped
    #: anyway and no tail is owed.
    space_settle_until: datetime | None = None

    def active(self, channel: str, now: datetime) -> bool:
        end = self.until.get(channel)
        return end is not None and utc_elapsed_seconds(end, now) > 0

    def block_active(self, channel: str, now: datetime) -> bool:
        end = self.blocked.get(channel)
        return end is not None and utc_elapsed_seconds(end, now) > 0

    def _expire_one(
        self,
        slots: dict[str, datetime],
        channel: str,
        end: datetime,
        now: datetime,
        lead: timedelta,
        *,
        settle: bool,
    ) -> None:
        if utc_elapsed_seconds(end, now) <= 0:
            slots.pop(channel, None)
            if settle and channel == CHANNEL_SPACE:
                # Anchored to the window's own end, not to when this
                # expiry was observed: re-equilibration starts when the
                # heat stopped (#1935).
                self.space_settle_until = utc_shift(end, SPACE_SETTLE_TAIL)
        elif utc_elapsed_seconds(end, now) > lead.total_seconds():
            # The clock stepped back since the window was set: the two-hour
            # maximum is a duration, not an instant (D1-s3-05), so it is
            # held to two hours from now rather than for the step as well.
            slots[channel] = utc_shift(now, lead)

    def expire(self, now: datetime) -> None:
        for channel, end in list(self.until.items()):
            if utc_elapsed_seconds(end, now) <= 0:
                self.until.pop(channel, None)
                if channel == CHANNEL_SPACE:
                    # Anchored to the window's own end, not to when this
                    # expiry was observed: re-equilibration starts when the
                    # heat stopped (#1935).
                    self.space_settle_until = utc_shift(end, SPACE_SETTLE_TAIL)
            elif utc_elapsed_seconds(end, now) > _MAX_LEAD.total_seconds():
                # The clock stepped back since the boost was set: the two-hour
                # maximum is a duration, not an instant (D1-s3-05), so it is
                # held to two hours from now rather than for the step as well.
                self.until[channel] = utc_shift(now, _MAX_LEAD)
        for channel, end in list(self.blocked.items()):
            self._expire_one(
                self.blocked, channel, end, now, _BLOCK_LEAD, settle=False
            )

    def _note_space_boost_ended(self, now: datetime) -> None:
        # A cancel leaves the same diverged plant state an expiry does
        # (#1935), so it owes the same settling tail.
        self.space_settle_until = utc_shift(now, SPACE_SETTLE_TAIL)

    def _set_blocked(self, channel: str, active: bool, now: datetime) -> None:
        if active:
            # The later press wins. Cancelling a live space boost owes the
            # settling tail a cancel from the switch owes.
            if channel == CHANNEL_SPACE and self.active(channel, now):
                self._note_space_boost_ended(now)
            self.until.pop(channel, None)
            self.blocked[channel] = utc_shift(now, _BLOCK_LEAD)
        else:
            self.blocked.pop(channel, None)

    def set(
        self, channel: str, active: bool, now: datetime, *, block: bool = False
    ) -> None:
        if channel not in CHANNELS:
            raise ValueError(channel)
        if block:
            self._set_blocked(channel, active, now)
            return
        if active:
            # A boost press clears a block on the same channel.
            self.blocked.pop(channel, None)
            self.until[channel] = utc_shift(now, _MAX_LEAD)
        else:
            was_live = self.active(channel, now)
            self.until.pop(channel, None)
            if channel == CHANNEL_SPACE and was_live:
                self._note_space_boost_ended(now)

    def as_dict(self) -> dict[str, Any]:
        self.expire(dt_util.now())
        dhw = self.until.get(CHANNEL_DHW)
        space = self.until.get(CHANNEL_SPACE)
        return {
            "boost_dhw_active": dhw is not None,
            "boost_dhw_until": dhw.isoformat() if dhw is not None else None,
            "boost_space_active": space is not None,
            "boost_space_until": space.isoformat() if space is not None else None,
        }


_STATES: WeakKeyDictionary[Any, BoostState] = WeakKeyDictionary()

# The last plan action, kept pristine for re-overlay (#1752). The overlay
# used to mutate ``_current_action`` in place, so a cycle that kept the plan
# (``no_prices``, ``solve_failed``, busy) also kept the boost: after a
# cancel the pump ran at nameplate power and maximum displace until the
# plan-stale gate. The same weak-map discipline as ``_STATES``.
_PLAN_BASES: WeakKeyDictionary[Any, CurrentAction] = WeakKeyDictionary()


def adopt_plan(coord: _BoostCoord, action: CurrentAction) -> None:
    """Adopt ``action`` as the plan base the cycle overlays onto (#1752).

    Every whole-dict writer of the running action -- the solve, the fixed
    modes, the sysid override -- routes through here. The live action is
    the base unchanged until ``apply`` lays the overlay on a copy of it,
    so a cancelled or expired boost disappears on the next cycle whatever
    that cycle's solve outcome is. The slot itself is written by the
    coordinator's ``adopt_action`` (#1739): the state transition has one
    owner.
    """
    _PLAN_BASES[coord] = action
    coord.adopt_action(action)


def held_for(coord: Any) -> BoostState:
    """In-memory boost state for this coordinator, created on first use."""
    held = _STATES.get(coord)
    if held is None:
        held = BoostState()
        _STATES[coord] = held
    return held


def space_boost_active(coord: Any, now: datetime | None = None) -> bool:
    """#1935: is boost space heating governing the action right now?

    Either surface — the channel overlay live, or the global boost mode
    selected. The live window only, not the settling tail: prediction
    suppression and the accuracy tag ask exactly "is the plan being
    overridden this interval". The learners' question
    (``space_learning_frozen``) additionally covers the plant-state
    divergence the overlay leaves behind.
    """
    if getattr(coord, "mode", None) == MODE_BOOST:
        return True
    return held_for(coord).active(CHANNEL_SPACE, now or dt_util.now())


def space_learning_frozen(coord: Any, now: datetime | None = None) -> bool:
    """#1935: boost space heating live, plus its settling tail.

    ``True`` from the moment either surface goes live until the plant state
    it diverged has re-equilibrated. The interval learners replay from a
    plant state propagated open-loop from the PLAN's trajectory, so heat the
    overlay added -- real in the house's slab, absent from the model's --
    leaves every replay residual warm-side until the slab coupling catches
    up: two boost days walked a converged, persisted
    ``house_heat_loss_scale`` from 1.04 to the 0.5 trust-region floor
    (R9-DIAG-1, #1935). Freezing through the tail is fail-closed -- a
    skipped interval loses convergence, a folded one corrupts a parameter
    that is persisted to disk.

    The channel check is PRESENCE in ``until``, not activity: the learners
    run before ``apply`` expires a window, so at the cycle that ends it the
    elapsed time reads zero and an activity test would fold the very
    interval the overlay governed for its whole span -- measured as a leak
    of one boosted sample per window on top of the tail below.
    """
    now = now or dt_util.now()
    held = held_for(coord)
    if space_boost_active(coord, now) or CHANNEL_SPACE in held.until:
        return True
    tail = held.space_settle_until
    return tail is not None and utc_elapsed_seconds(tail, now) > 0


def interval_boosted(pending: Mapping[str, Any], coord: Any) -> bool:
    """#1935: did a boost overlay govern the interval ``pending`` describes?

    The flag captured when the interval began, or an overlay live at
    settlement -- a boost switched on mid-interval contaminates the pair
    even though the prediction was made clean. An overlay that begins
    exactly AT settlement governs only the next interval, not the one
    closing, so it does not tag this one.
    """
    if pending.get("boost_space"):
        return True
    now = dt_util.now()
    end = held_for(coord).until.get(CHANNEL_SPACE)
    if end is None or utc_elapsed_seconds(end, now) <= 0:
        return False
    return utc_elapsed_seconds(utc_shift(end, -_MAX_LEAD), now) < 0


def note_mode_boost_ended(coord: Any, now: datetime | None = None) -> None:
    """#1935: the global boost mode was left; its settling tail begins.

    The mode surface diverges the replayed plant state exactly as the
    channel overlay does -- same actuation, same mechanism -- so it owes
    the same tail.
    """
    held_for(coord).space_settle_until = utc_shift(
        now or dt_util.now(), SPACE_SETTLE_TAIL
    )


def overlay(
    action: CurrentAction,
    held: BoostState,
    *,
    max_power: float,
    max_temp: float,
    ecl_max: float,
) -> None:
    """Mutate ``action`` for every channel that is still live."""
    if CHANNEL_SPACE in held.until:
        action["power"] = max_power
        action["setpoint"] = max_temp
        action["mode"] = "boost"
        action["power_normalized"] = 1.0
        action["heat_pump_on"] = True
        action["displace_value"] = ecl_max
        action["boost_space"] = True
    if CHANNEL_DHW in held.until:
        action["dhw_power"] = max(0.1, max_power * 0.8)
        action["dhw_heating_active"] = True
        action["heat_pump_on"] = True
        action["boost_dhw"] = True
        # The pump now runs for the tank, so a mode saying it does not would
        # publish a false Heat Pump Action (#1499).
        if action.get("mode") in (None, "off", "idle"):
            action["mode"] = "hot_water"
    _zero_blocked(action, held)


def _zero_blocked(action: CurrentAction, held: BoostState) -> None:
    """Zero a blocked duty on the action copy. Never the power switch.

    A single-channel block leaves ``heat_pump_on`` as the plan wrote it.
    ``_apply_action`` commands the supply switch from that flag, and it
    skips OFF only when the pump's own mode blocks both channels or is
    cooling. Zeroing the flag here would switch the supply off for one
    duty. The arbiter drops that duty and serves the idle row instead.
    """
    if CHANNEL_SPACE in held.blocked:
        action["power"] = 0.0
        if "power_normalized" in action:
            action["power_normalized"] = 0.0
    if CHANNEL_DHW in held.blocked:
        action["dhw_power"] = 0.0
        action["dhw_heating_active"] = False


def apply(coord: _BoostCoord, specs: BoostOverlay) -> None:
    """Expire, then lay the overlay on a COPY of the plan base (#1752).

    The published and actuated action is rebuilt every cycle from the base
    the solve or mode block last adopted, never carried forward from the
    previous cycle's overlaid dict, so a boost that is no longer live is
    gone from the action whatever kept the plan. ``specs`` are the
    coordinator's overlay numbers, passed in (#1739) rather than read off
    its privates.
    """
    now = dt_util.now()
    held = held_for(coord)
    held.expire(now)
    if not has_hot_water(coord):
        # No tank to heat: a DHW boost or block set or restored anyway is
        # dropped here, the one place it could reach the action (#1527).
        held.until.pop(CHANNEL_DHW, None)
        held.blocked.pop(CHANNEL_DHW, None)
    snap = _floor_snap(coord)
    released = snap is not None and release_blocked(coord, snap, now)
    base = _PLAN_BASES.get(coord)
    action: CurrentAction = {**base} if base else {}
    overlay(
        action,
        held,
        max_power=specs.max_power,
        max_temp=specs.max_temp,
        ecl_max=specs.ecl_max,
    )
    coord.adopt_action(action)
    if released:
        _schedule_persist(coord)


def _store(coord: _BoostCoord) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(
        coord.hass,
        BOOST_STORE_VERSION,
        f"{DOMAIN}_{coord.entry.entry_id}_boost",
        lead=_MAX_LEAD,
        naive_zone=dt_util.DEFAULT_TIME_ZONE,  # _parse_until's zone
    )


def _parse_until(raw: Any) -> datetime | None:
    return stored_instant(raw, dt_util.DEFAULT_TIME_ZONE)


async def persist(coord: _BoostCoord) -> None:
    try:
        held = held_for(coord)
        payload = {
            channel: {"until": end.isoformat()}
            for channel, end in held.until.items()
        }
        # Absent when no block is set, so a boost-only store is unchanged.
        payload.update({
            f"block_{channel}": {"until": end.isoformat()}
            for channel, end in held.blocked.items()
        })
        await _store(coord).async_save(payload)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not persist boost state: %s", err)


async def restore(coord: Any) -> None:
    raw = await load_mapping(_store(coord), "boost state")
    if raw is None:
        return
    now = dt_util.now()
    held = held_for(coord)
    for channel in CHANNELS:
        payload = raw.get(channel)
        if isinstance(payload, Mapping):
            parsed = _parse_until(payload.get("until"))
        else:
            parsed = None
        # Both sides through as_utc (#1299's rule): the loader keeps a naive
        # stamp naive when no zone is configured (F3.1's recorded decision),
        # and comparing it straight against an aware now is the TypeError the
        # store boundary exists to make unreachable. The comparison stays the
        # line the mutation pins name.
        if parsed is not None and dt_util.as_utc(parsed) > dt_util.as_utc(now):
            held.until[channel] = parsed
        block = raw.get(f"block_{channel}")
        if isinstance(block, Mapping):
            parsed_block = _parse_until(block.get("until"))
            if (
                parsed_block is not None
                and dt_util.as_utc(parsed_block) > dt_util.as_utc(now)
            ):
                held.blocked[channel] = parsed_block


async def restore_session(
    coord: Any,
    state: away_mode.AwayState,
    config: Mapping[str, Any],
    read_entity: away_mode.EntityReader,
) -> None:
    """Away override and boost channels, one spawn from the coordinator.

    The away half's inputs pass through to ``away_mode.restore_override``
    (#1739); the boost half keeps only the coordinator's public surface.
    """
    await away_mode.restore_override(coord, state, config, read_entity)
    await restore(coord)


async def set_channel(
    coord: Any, channel: str, active: bool, *, refresh: bool = True
) -> None:
    held_for(coord).set(channel, active, dt_util.now())
    await persist(coord)
    if refresh:
        await coord.async_request_refresh()


async def set_block(
    coord: Any, channel: str, active: bool, *, refresh: bool = True
) -> None:
    """Turn a block on or off. A live safety floor refuses the on-press."""
    now = dt_util.now()
    if active and block_release_reason(coord, channel, now) is not None:
        held_for(coord).blocked.pop(channel, None)
    else:
        held_for(coord).set(channel, active, now, block=True)
    await persist(coord)
    if refresh:
        await coord.async_request_refresh()


def bind_cold_lease(fn: Any) -> None:
    """The arbiter registers the cold-rail test. No import the other way."""
    global _cold_lease
    _cold_lease = fn


def _floor_snap(coord: Any) -> Any:
    fn = getattr(coord, "arbiter_inputs", None)
    if not callable(fn):
        return None
    return fn()


def _schedule_persist(coord: Any) -> None:
    coord.hass.async_create_task(persist(coord))


def _due_inside_horizon(coord: Any) -> bool:
    """Whether the anti-legionella hard deadline falls inside this horizon.

    ``dhw_legionella_due_in_hours`` is ``legionella.due_in_hours``: hours
    left before the cycle is required. The planner places that cycle when
    the same remainder, in steps, is still inside the horizon
    (``deadline_step < n_steps``). Equal to the horizon is the next
    horizon, so the comparison is strict.
    """
    data = getattr(coord, "data", None)
    if not isinstance(data, Mapping):
        return False
    due = data.get("dhw_legionella_due_in_hours")
    if due is None:
        return False
    horizon = data.get("horizon_hours", 24.0)
    try:
        return float(due) < float(horizon)
    except (TypeError, ValueError):
        return False


def _window_open(snap: Any, now: datetime) -> bool:
    info = getattr(snap.plan, "predictive_info", None) or {}
    planned = info.get("dhw_windows") if snap.plan is not None else None
    windows = None
    if planned:
        try:
            windows = parse_windows(planned)
        except DHWWindowError:
            windows = None
    if not windows:
        windows = list(getattr(snap.params, "dhw_demand_windows", None) or [])
    if not windows:
        return False
    hour = now.hour + now.minute / 60.0
    return hour_in_windows(hour, windows)


def _dhw_floor(coord: Any, snap: Any, now: datetime) -> str | None:
    if snap.disinfecting:
        return RELEASE_DISINFECTION
    if _due_inside_horizon(coord):
        return RELEASE_LEGIONELLA
    temp = getattr(snap.state, "dhw_temperature", None)
    floor = getattr(snap.params, "dhw_min_temp", None)
    if (
        temp is not None
        and floor is not None
        and float(temp) <= float(floor)
        and _window_open(snap, now)
    ):
        return RELEASE_TANK
    return None


def _space_floor(snap: Any, now: datetime) -> str | None:
    room = getattr(snap.state, "room_temperature", None)
    if (
        room is not None
        and float(room) <= ECONOMY_ABSOLUTE_FLOOR + SPACE_PUMP_FLOOR_MARGIN_C
    ):
        return RELEASE_ROOM
    if _cold_lease is not None and _cold_lease(snap, now):
        return RELEASE_COLD
    return None


def block_release_reason(
    coord: Any, channel: str, now: datetime | None = None, snap: Any = None
) -> str | None:
    """Why this block cannot hold, or None when the press may stand."""
    now = now or dt_util.now()
    if snap is None:
        snap = _floor_snap(coord)
    if snap is None:
        return None
    if channel == CHANNEL_DHW:
        why = _dhw_floor(coord, snap, now)
        if why is not None:
            return why
    elif channel == CHANNEL_SPACE:
        why = _space_floor(snap, now)
        if why is not None:
            return why
    action = snap.action or {}
    if action.get("mode") == "system_identification":
        return RELEASE_SYSID
    if snap.plan_stale:
        return RELEASE_STALE
    return None


def release_blocked(coord: Any, snap: Any, now: datetime) -> bool:
    """Drop every live block a safety floor forbids. True if one dropped."""
    held = held_for(coord)
    released = False
    for channel in list(held.blocked):
        if not held.block_active(channel, now):
            continue
        if block_release_reason(coord, channel, now, snap) is None:
            continue
        held.blocked.pop(channel, None)
        released = True
    return released
