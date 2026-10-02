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
from .const import DOMAIN
from .drift import stored_instant
from .entity import has_hot_water

_LOGGER = logging.getLogger(__name__)
BOOST_STORE_VERSION = 1
BOOST_HOURS = 2
_MAX_LEAD = timedelta(hours=BOOST_HOURS)
CHANNEL_DHW = "dhw"
CHANNEL_SPACE = "space"
CHANNELS = (CHANNEL_DHW, CHANNEL_SPACE)


class _BoostOpt(Protocol):
    max_temp: float


class _BoostCoord(Protocol):
    hass: Any
    entry: Any
    _current_action: dict[str, Any]
    _thermal_model: Any
    _ecl110_displace_max: float
    _opt_config: _BoostOpt
    _ctx: Any

    async def async_request_refresh(self) -> None: ...


@dataclass
class BoostState:
    """Per-channel expiry. A missing key is off."""

    until: dict[str, datetime] = field(default_factory=dict)

    def active(self, channel: str, now: datetime) -> bool:
        end = self.until.get(channel)
        return end is not None and utc_elapsed_seconds(end, now) > 0

    def expire(self, now: datetime) -> None:
        for channel, end in list(self.until.items()):
            if utc_elapsed_seconds(end, now) <= 0:
                self.until.pop(channel, None)
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
            self.until.pop(channel, None)

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
_PLAN_BASES: WeakKeyDictionary[Any, dict[str, Any]] = WeakKeyDictionary()


def adopt_plan(coord: _BoostCoord, action: dict[str, Any]) -> None:
    """Adopt ``action`` as the plan base the cycle overlays onto (#1752).

    Every whole-dict writer of ``_current_action`` -- the solve, the fixed
    modes, the sysid override -- routes through here. The live action is
    the base unchanged until ``apply`` lays the overlay on a copy of it,
    so a cancelled or expired boost disappears on the next cycle whatever
    that cycle's solve outcome is.
    """
    _PLAN_BASES[coord] = action
    coord._current_action = action


def held_for(coord: Any) -> BoostState:
    """In-memory boost state for this coordinator, created on first use."""
    held = _STATES.get(coord)
    if held is None:
        held = BoostState()
        _STATES[coord] = held
    return held


def overlay(
    action: dict[str, Any],
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


def apply(coord: _BoostCoord) -> None:
    """Expire, then lay the overlay on a COPY of the plan base (#1752).

    The published and actuated action is rebuilt every cycle from the base
    the solve or mode block last adopted, never carried forward from the
    previous cycle's overlaid dict, so a boost that is no longer live is
    gone from the action whatever kept the plan.
    """
    now = dt_util.now()
    held = held_for(coord)
    held.expire(now)
    if not has_hot_water(coord):
        # No tank to heat: a DHW boost set or restored anyway is dropped here,
        # the one place it could reach the action (#1527).
        held.until.pop(CHANNEL_DHW, None)
    action = dict(_PLAN_BASES.get(coord) or {})
    ctx: Any = getattr(coord, "_ctx", coord)
    overlay(
        action,
        held,
        max_power=float(coord._thermal_model.params.max_electrical_power),
        max_temp=float(ctx._opt_config.max_temp),
        ecl_max=float(coord._ecl110_displace_max),
    )
    coord._current_action = action


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


async def restore_session(coord: Any) -> None:
    """Away override and boost channels, one spawn from the coordinator."""
    await away_mode.restore_override(coord)
    await restore(coord)


async def set_channel(
    coord: Any, channel: str, active: bool, *, refresh: bool = True
) -> None:
    held_for(coord).set(channel, active, dt_util.now())
    await persist(coord)
    if refresh:
        await coord.async_request_refresh()
