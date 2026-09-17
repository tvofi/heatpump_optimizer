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
the OFF half is built on two facts rather than on memory:

* **Ownership, persisted.** ``owned`` names the switch this integration
  turned ON and has not yet SEEN off. The guard stores it with the cycle's
  own timestamps, so a restart, a reload, an options save that switches to
  observe or names another switch, all still know which switch to turn off.
  A switch that was already on when a boost started is never claimed, so a
  program the user or the pump started is never switched off by this code.
* **The entity's real state.** OFF is re-sent on every cycle while the owned
  switch still READS on, and ownership ends only when a read shows it off. A
  write that raised, one the entity silently dropped, and one sent while the
  entity was unavailable are all retried the same way. An unreadable switch
  is waited for, not written blind.

ON is refused rather than guessed: outside control mode, without a switch, or
while the pump's mode blocks hot water (OFF is always allowed). The service
call is injected, so the module is free of Home Assistant imports.
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from .const import (
    CONF_DHW_DISINFECTION_MODE,
    CONF_DHW_DISINFECTION_SWITCH_ENTITY,
    DEFAULT_DHW_DISINFECTION_MODE,
)
from .freq_control import FREQ_MODE_CONTROL
from .inputs import UNBOUNDED

_LOGGER = logging.getLogger(__name__)

#: ``hass.services.async_call``'s shape: (domain, service, data).
ServiceCall = Callable[[str, str, dict[str, Any]], Awaitable[Any]]


class DisinfectionSwitch:
    """Reads, and in control mode writes, the pump's disinfection switch."""

    def __init__(self, config: Mapping[str, Any], service: ServiceCall) -> None:
        #: The live effective configuration, read on every call.
        self._config = config
        self._service = service
        #: True once this boost's ON is satisfied (written, or found already
        #: on), so it is not re-sent every cycle; cleared by ``release``.
        self.memo: bool | None = None
        #: True while the most recent write attempt raised.
        self.failed: bool = False
        #: The switch as read this cycle (the owned one if any), or None when
        #: unread or unreadable.
        self.observed: bool | None = None
        #: The switch this integration turned ON and has not yet read OFF.
        self.owned: str | None = None
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
        if not await self._write(entity_id, "turn_on"):
            return False
        # Recorded only AFTER the call succeeded, so a failed write is retried.
        self.memo = True
        self.owned = entity_id
        return True

    async def release(self, *, blind: bool = False) -> bool:
        """Turn off the switch this integration turned on, in any mode.

        Ownership ends only when a read shows the switch off; until then OFF
        is re-sent each cycle it still reads on. An unreadable switch is
        waited for. ``blind`` writes OFF without a read, for an unload that
        will not see another cycle, and keeps ownership for the next setup.
        """
        self.memo = None
        owned = self.owned
        if owned is None:
            return False
        if not blind:
            if self.observed is False:
                self.owned = None
                return True
            if self.observed is None:
                return False
        return await self._write(owned, "turn_off")

    async def _write(self, entity_id: str, service: str) -> bool:
        try:
            await self._service("homeassistant", service, {"entity_id": entity_id})
        except Exception as err:  # noqa: BLE001 - a switch must never kill the cycle
            self.failed = True
            _LOGGER.warning(
                "Could not %s the disinfection switch %s: %s", service, entity_id, err
            )
            return False
        self.failed = False
        _LOGGER.info("Disinfection switch %s → %s", entity_id, service)
        return True

    def observe(self, reader: Any) -> None:
        """Read the owned switch, else the configured one, through the reader."""
        target = self.owned or self.entity_id
        if target is None:
            self.observed = None
            return
        reading = reader.read_bool(
            CONF_DHW_DISINFECTION_SWITCH_ENTITY,
            max_age_minutes=UNBOUNDED,
            entity_id=target,
        )
        self.observed = reading.flag if reading.ok else None

    def view(self) -> dict[str, Any]:
        """The published attributes: nothing at all when no switch is involved."""
        target = self.owned or self.entity_id
        if target is None:
            return {}
        return {
            "dhw_disinfection_switch": {
                "entity_id": target,
                "mode": self.mode,
                "state": self.observed,
                "turned_on_by_optimizer": self.owned is not None,
                "write_failed": self.failed,
            }
        }
