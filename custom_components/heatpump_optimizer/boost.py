"""Timed boost overlays for hot water and space heating.

Each channel is a two-hour maximum-heat overlay on the live action. Space
boost matches the global boost mode (nameplate electrical power, the
comfort ceiling, full ECL displace). DHW boost matches the planner's own
hot-water ceiling (80 % of nameplate). The channels are independent: one
does not rewrite the other, and neither stomps comfort or economy the way
selecting the global boost mode does.

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
from .const import DOMAIN, MODE_BOOST
from .drift import stored_instant
from .entity import has_hot_water
from .payload import CurrentAction

_LOGGER = logging.getLogger(__name__)
BOOST_STORE_VERSION = 1
BOOST_HOURS = 2
_MAX_LEAD = timedelta(hours=BOOST_HOURS)
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
    #: #1935: when the space overlay's settling tail ends -- set when the
    #: overlay ends (expiry or cancel) and when the global boost mode is
    #: left. In-memory only: a restart mid-tail also loses
    #: ``_last_house_sample``, so the first replay after it is skipped
    #: anyway and no tail is owed.
    space_settle_until: datetime | None = None

    def active(self, channel: str, now: datetime) -> bool:
        end = self.until.get(channel)
        return end is not None and utc_elapsed_seconds(end, now) > 0

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

    def set(self, channel: str, active: bool, now: datetime) -> None:
        if channel not in CHANNELS:
            raise ValueError(channel)
        if active:
            self.until[channel] = utc_shift(now, _MAX_LEAD)
        else:
            was_live = self.active(channel, now)
            self.until.pop(channel, None)
            if channel == CHANNEL_SPACE and was_live:
                # A cancel leaves the same diverged plant state an expiry
                # does (#1935), so it owes the same settling tail.
                self.space_settle_until = utc_shift(now, SPACE_SETTLE_TAIL)

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
        # No tank to heat: a DHW boost set or restored anyway is dropped here,
        # the one place it could reach the action (#1527).
        held.until.pop(CHANNEL_DHW, None)
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
        await _store(coord).async_save(
            {
                channel: {"until": end.isoformat()}
                for channel, end in held_for(coord).until.items()
            }
        )
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
        if not isinstance(payload, Mapping):
            continue
        parsed = _parse_until(payload.get("until"))
        # Both sides through as_utc (#1299's rule): the loader keeps a naive
        # stamp naive when no zone is configured (F3.1's recorded decision),
        # and comparing it straight against an aware now is the TypeError the
        # store boundary exists to make unreachable.
        if parsed is not None and dt_util.as_utc(parsed) > dt_util.as_utc(now):
            held.until[channel] = parsed


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
