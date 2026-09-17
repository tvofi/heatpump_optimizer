"""The pump's own disinfection switch: observe first, write only when told to.

Many heat pumps run their own anti-legionella program behind a switch, and a
tank heated by the pump's program reaches temperatures the compressor alone
does not. This is the actuation half of #1067's disinfection lever, in the
frequency stage's order (``freq_control.py``):

* **Observe** (the default): the switch is read and published beside the
  cycle's other hot water attributes, and nothing is written. That is the
  evidence a user reads before letting the integration touch the pump.
* **Control** (explicit opt-in, and only with a switch configured): the
  anti-legionella guard turns it on when the plan's disinfection boost
  starts and off when that boost closes.

A switch left ON heats the tank electrically for as long as it stays on, so
the OFF half is built on a persisted record and the entities' real states,
never on memory:

* **Ownership.** ``owned`` lists the switches this integration turned ON and
  has not yet SEEN off. The intent is saved BEFORE the ON is written and
  withdrawn if the write fails, so a crash between the two cannot leave a
  switch on with no record. A switch that already reads on is never claimed.
* **Release, per owned switch.** OFF is re-sent every cycle it still reads
  on; the record ends when a read shows it off. An owned switch that cannot
  be read is waited for while it is the configured switch and merely
  unavailable. When it has no state at all (renamed or deleted), or is no
  longer the configured switch, it is waited for only
  ``DHW_DISINFECTION_LOST_MINUTES`` -- startup ordering is the reason for any
  wait -- and then dropped into ``lost``, which the guard turns into a repair
  saying the switch may still be on. A stale record never blocks the
  configured switch: ON to it proceeds while older records resolve.
* **Unload.** ``release_blind`` writes OFF without waiting for a cycle's
  reading and drops each record whose OFF landed, so a program the user
  starts while the integration is unloaded is not switched off at the next
  setup.
* **Landed means read back.** A write counts only when the target has a
  usable state before the call and reads back the commanded state after it.
  Home Assistant returns from a call to an entity id with no state without
  raising and without doing anything, and runs a non-blocking call's handler
  in the background; neither "returned" nor "did not raise" says the switch
  moved (#1106 review rounds 2 and 3).

The one case ownership cannot separate: a user who turns the switch on by
hand during a boost this integration started has it turned off when that
boost ends. The service call is injected, so the module is free of Home
Assistant imports.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime, timedelta
from typing import Any

from .const import (
    CONF_DHW_DISINFECTION_MODE,
    CONF_DHW_DISINFECTION_SWITCH_ENTITY,
    DEFAULT_DHW_DISINFECTION_MODE,
    DHW_DISINFECTION_LOST_MINUTES,
)
from .freq_control import FREQ_MODE_CONTROL
from .inputs import UNBOUNDED, parse_bool

_LOGGER = logging.getLogger(__name__)

#: ``hass.services.async_call``: (domain, service, data, blocking=...).
ServiceCall = Callable[..., Awaitable[Any]]
#: An entity's current state text, or None when it has no state at all.
ReadState = Callable[[str], "str | None"]

#: How long one write may take before it counts as failed. Writes are
#: BLOCKING, because Home Assistant runs a non-blocking call's handler in the
#: background and only logs its error: a write to an offline device would
#: otherwise read as landed. A bound keeps a device that never answers from
#: stalling the update cycle that awaits it.
WRITE_TIMEOUT_S: float = 10.0


async def _no_persist() -> None:
    """The default persistence hook: nothing to save to."""


class DisinfectionSwitch:
    """Reads, and in control mode writes, the pump's disinfection switch."""

    def __init__(
        self, config: Mapping[str, Any], service: ServiceCall, read_state: ReadState
    ) -> None:
        #: The live effective configuration, read on every call.
        self._config = config
        self._service = service
        #: Reads an entity's state immediately before and after each write.
        self._read_state = read_state
        #: Saves the owner's record; the guard installs its store's save.
        self.persist: Callable[[], Awaitable[None]] = _no_persist
        #: True once this boost's ON is satisfied (written, or found already
        #: on), so it is not re-sent every cycle.
        self.memo: bool | None = None
        #: True while the most recent write attempt raised, and to which switch.
        self.failed: bool = False
        self.failed_entity: str | None = None
        #: The configured switch as read this cycle, or None when unread.
        self.observed: bool | None = None
        #: The switches this integration turned ON and has not yet read OFF.
        self.owned: list[str] = []
        #: Records dropped as unreadable, for the owner to report and drain.
        self.lost: list[str] = []
        self._readings: dict[str, tuple[bool | None, str | None]] = {}
        self._unreadable_since: dict[str, datetime] = {}
        self._blocked_logged: bool = False

    @property
    def entity_id(self) -> str | None:
        """The configured switch, or None."""
        return self._config.get(CONF_DHW_DISINFECTION_SWITCH_ENTITY) or None

    @property
    def mode(self) -> str:
        """Observe or control; anything unrecognised reads as observe."""
        mode = self._config.get(CONF_DHW_DISINFECTION_MODE, DEFAULT_DHW_DISINFECTION_MODE)
        return FREQ_MODE_CONTROL if mode == FREQ_MODE_CONTROL else DEFAULT_DHW_DISINFECTION_MODE

    @property
    def controlling(self) -> bool:
        """Control mode with a switch configured."""
        return self.entity_id is not None and self.mode == FREQ_MODE_CONTROL

    async def turn_on(self, *, dhw_blocked: bool) -> bool:
        """Turn the configured switch on; True when it is known to be on.

        False is every refusal and every failed write. ``failed`` tells the
        two apart, so the caller can raise its repair only for a failure.
        """
        entity_id = self.entity_id
        if entity_id is None or self.mode != FREQ_MODE_CONTROL:
            return False
        if dhw_blocked:
            if not self._blocked_logged:
                self._blocked_logged = True
                _LOGGER.warning(
                    "Not turning on the disinfection switch %s: the heat "
                    "pump's mode makes no hot water",
                    entity_id,
                )
            return False
        self._blocked_logged = False
        if self.memo is True:
            return True
        if self.observed is True:
            # Already on: nothing to write, and a program this integration
            # did not start is not claimed, so it is never switched off here.
            self.memo = True
            return True
        claimed = entity_id not in self.owned
        if claimed:
            # The intent is on disk before the write, so a crash between the
            # write and a later save cannot leave the switch on unrecorded.
            self.owned.append(entity_id)
            await self.persist()
        if not await self._write(entity_id, "turn_on"):
            if claimed:
                self.owned.remove(entity_id)
                await self.persist()
            return False
        self.memo = True
        return True

    async def release(self, now: datetime, *, keep: str | None = None) -> None:
        """Resolve every owned switch except ``keep`` against its reading.

        A record this drops is persisted by the caller, which saves on any
        change to the record (``LegionellaGuard._drive_switch``).
        """
        for owned in list(self.owned):
            if owned == keep:
                continue
            flag, problem = self._readings.get(owned, (None, "unread"))
            if flag is not None:
                self._unreadable_since.pop(owned, None)
                if flag:
                    await self._write(owned, "turn_off")
                    continue
                self.owned.remove(owned)
                continue
            if owned == self.entity_id and problem != "missing_entity":
                # The configured switch, unavailable: wait for it.
                continue
            since = self._unreadable_since.setdefault(owned, now)
            if now - since < timedelta(minutes=DHW_DISINFECTION_LOST_MINUTES):
                continue
            self._unreadable_since.pop(owned, None)
            self.owned.remove(owned)
            self.lost.append(owned)
            _LOGGER.warning(
                "Disinfection switch %s has been unreadable for %.0f min; the "
                "optimizer can no longer turn it off, and it may still be on",
                owned,
                DHW_DISINFECTION_LOST_MINUTES,
            )

    async def release_blind(self) -> None:
        """On unload: OFF to every owned switch unread; drop what landed."""
        landed = [owned for owned in list(self.owned) if await self._write(owned, "turn_off")]
        if landed:
            self.owned = [owned for owned in self.owned if owned not in landed]
            await self.persist()

    def _flag_now(self, entity_id: str) -> bool | None:
        """The entity's state as a flag right now; None when it has none."""
        text = self._read_state(entity_id)
        return None if text is None else parse_bool(text, strict=True)

    async def _write(self, entity_id: str, service: str) -> bool:
        want = service == "turn_on"
        if self._flag_now(entity_id) is None:
            # Nothing to act on: a call to an id with no usable state returns
            # without raising and changes nothing. Not a failed write -- the
            # record waits, and an id that never comes back is the grace's.
            return False
        try:
            async with asyncio.timeout(WRITE_TIMEOUT_S):
                await self._service(
                    "homeassistant", service, {"entity_id": entity_id}, blocking=True
                )
        except Exception as err:  # noqa: BLE001 - a switch must never kill the cycle
            self.failed = True
            self.failed_entity = entity_id
            _LOGGER.warning(
                "Could not %s the disinfection switch %s: %s", service, entity_id, err
            )
            return False
        if self._flag_now(entity_id) is not want:
            self.failed = True
            self.failed_entity = entity_id
            _LOGGER.warning(
                "The disinfection switch %s did not read back %s after %s",
                entity_id,
                "on" if want else "off",
                service,
            )
            return False
        self.failed = False
        _LOGGER.info("Disinfection switch %s → %s", entity_id, service)
        return True

    def observe(self, reader: Any) -> None:
        """Read the configured switch and every owned one through the reader."""
        self._readings = {}
        for target in dict.fromkeys([*self.owned, self.entity_id]):
            if target is None:
                continue
            reading = reader.read_bool(
                CONF_DHW_DISINFECTION_SWITCH_ENTITY,
                max_age_minutes=UNBOUNDED,
                entity_id=target,
            )
            self._readings[target] = (
                reading.flag if reading.ok else None,
                reading.problem,
            )
        self.observed = self._readings.get(self.entity_id or "", (None, None))[0]

    def view(self) -> dict[str, Any]:
        """The published attributes: nothing at all when no switch is involved."""
        target = self.entity_id or next(iter(self.owned), None)
        if target is None:
            return {}
        return {
            "dhw_disinfection_switch": {
                "entity_id": target,
                "mode": self.mode,
                "state": self._readings.get(target, (None, None))[0],
                "turned_on_by_optimizer": target in self.owned,
                "write_failed": self.failed,
            }
        }
