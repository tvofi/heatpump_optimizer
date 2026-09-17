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

The command object refuses rather than guesses. It writes nothing outside
control mode or without a switch; it refuses to turn the program ON while the
pump's mode blocks hot water, because a disinfection the hardware cannot run
must not be requested (OFF is always allowed); and it remembers a state only
after the call that set it succeeded, so a write that raised is retried on
the next cycle instead of being remembered as done. That is the rule
``_async_set_pump`` follows for the circulation pumps.

Kept free of Home Assistant imports: the service call is injected.
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
        #: The live effective configuration, read on every call so an options
        #: save takes effect without rebuilding the object.
        self._config = config
        self._service = service
        #: The state the last SUCCESSFUL write set; None until one has.
        self.memo: bool | None = None
        #: True while the most recent write attempt raised.
        self.failed: bool = False
        #: The switch as last read, or None when unread or unreadable.
        self.observed: bool | None = None
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

    async def command(self, on: bool, *, dhw_blocked: bool) -> bool:
        """Set the switch; True when it is known to be in the asked state.

        False is every refusal and every failed write. ``failed`` tells the
        two apart, so the caller can raise its repair only for a failure.
        """
        entity_id = self.entity_id
        if entity_id is None or self.mode != FREQ_MODE_CONTROL:
            return False
        if on and dhw_blocked:
            if not self._blocked_logged:
                self._blocked_logged = True
                _LOGGER.warning(
                    "Not turning on the disinfection switch %s: the heat "
                    "pump's mode makes no hot water",
                    entity_id,
                )
            return False
        self._blocked_logged = False
        if self.memo is on:
            return True
        service = "turn_on" if on else "turn_off"
        try:
            await self._service("homeassistant", service, {"entity_id": entity_id})
        except Exception as err:  # noqa: BLE001 - a switch must never kill the cycle
            self.failed = True
            _LOGGER.warning(
                "Could not %s the disinfection switch %s: %s", service, entity_id, err
            )
            return False
        # Recorded only AFTER the call succeeded, so a failed write is retried.
        self.memo = on
        self.failed = False
        _LOGGER.info("Disinfection switch %s → %s", entity_id, service)
        return True

    def observe(self, reader: Any) -> None:
        """Read the switch through the cycle's input reader, if one is set."""
        if self.entity_id is None:
            self.observed = None
            return
        reading = reader.read_bool(
            CONF_DHW_DISINFECTION_SWITCH_ENTITY, max_age_minutes=UNBOUNDED
        )
        self.observed = reading.flag if reading.ok else None

    def view(self) -> dict[str, Any]:
        """The published attributes: nothing at all when no switch is set."""
        entity_id = self.entity_id
        if entity_id is None:
            return {}
        return {
            "dhw_disinfection_switch": {
                "entity_id": entity_id,
                "mode": self.mode,
                "state": self.observed,
                "commanded": self.memo,
                "write_failed": self.failed,
            }
        }
