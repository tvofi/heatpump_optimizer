"""Timed boost overlays for hot water and space heating.

Each channel is a two-hour maximum-heat overlay on the live action. Space
boost matches the global boost mode (nameplate electrical power, the
comfort ceiling, full ECL displace). DHW boost matches the planner's own
hot-water ceiling (80 % of nameplate). The channels are independent: one
does not rewrite the other, and neither stomps comfort or economy the way
selecting the global boost mode does.

State lives in a Store next to the away override, and in a weak map keyed
by coordinator so the coordinator class does not grow another attribute.
The coordinator only restores, overlays, and lets the switches call in.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol
from weakref import WeakKeyDictionary

from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from . import away as away_mode
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
BOOST_STORE_VERSION = 1
BOOST_HOURS = 2
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
        return end is not None and end > now

    def expire(self, now: datetime) -> None:
        for channel, end in list(self.until.items()):
            if end <= now:
                self.until.pop(channel, None)

    def set(self, channel: str, active: bool, now: datetime) -> None:
        if channel not in CHANNELS:
            raise ValueError(channel)
        if active:
            self.until[channel] = now + timedelta(hours=BOOST_HOURS)
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


def state(coord: Any) -> BoostState:
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


def apply(coord: _BoostCoord) -> None:
    """Expire, then overlay the live action the cycle is about to write."""
    now = dt_util.now()
    held = state(coord)
    held.expire(now)
    action = coord._current_action
    if not action:
        coord._current_action = {}
        action = coord._current_action
    ctx: Any = getattr(coord, "_ctx", coord)
    overlay(
        action,
        held,
        max_power=float(coord._thermal_model.params.max_electrical_power),
        max_temp=float(ctx._opt_config.max_temp),
        ecl_max=float(coord._ecl110_displace_max),
    )


def _store(coord: _BoostCoord) -> Store[dict[str, Any]]:
    return Store(
        coord.hass,
        BOOST_STORE_VERSION,
        f"{DOMAIN}_{coord.entry.entry_id}_boost",
    )


def _parse_until(raw: Any) -> datetime | None:
    if isinstance(raw, datetime):
        return raw
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).strip())
    except ValueError:
        return None


async def persist(coord: _BoostCoord) -> None:
    try:
        await _store(coord).async_save(
            {
                channel: {"until": end.isoformat()}
                for channel, end in state(coord).until.items()
            }
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not persist boost state: %s", err)


async def restore(coord: Any) -> None:
    try:
        raw = await _store(coord).async_load()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not load boost state: %s", err)
        raw = None
    if not isinstance(raw, dict):
        return
    now = dt_util.now()
    held = state(coord)
    for channel in CHANNELS:
        payload = raw.get(channel)
        if not isinstance(payload, Mapping):
            continue
        parsed = _parse_until(payload.get("until"))
        if parsed is not None and parsed > now:
            held.until[channel] = parsed


async def restore_session(coord: Any) -> None:
    """Away override and boost channels, one spawn from the coordinator."""
    await away_mode.restore_override(coord)
    await restore(coord)


async def set_channel(coord: Any, channel: str, active: bool) -> None:
    state(coord).set(channel, active, dt_util.now())
    recorder = getattr(coord, "boost_calls", None)
    if recorder is not None:
        recorder.append({"channel": channel, "active": active})
        return
    await persist(coord)
    await coord.async_request_refresh()
