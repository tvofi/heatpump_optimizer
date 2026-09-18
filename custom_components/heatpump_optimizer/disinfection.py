"""The pump's own disinfection switch, observed.

Many heat pumps run their own anti-legionella program behind a switch. This
module reads that switch through the cycle's input reader and publishes what
it says beside the hot water attributes, so a user can see whether the pump's
program is on while the plan's disinfection cycle runs. It writes nothing and
changes no plan: turning the switch on and off is W1067-G5b's, behind an
explicit opt-in.

Kept free of Home Assistant imports so it can be unit-tested directly.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .const import CONF_DHW_DISINFECTION_SWITCH_ENTITY
from .inputs import UNBOUNDED


class DisinfectionSwitch:
    """Reads the pump's disinfection switch; never writes it."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        #: The live effective configuration, read on every call.
        self._config = config
        #: The switch as read this cycle, or None when unread or unreadable.
        self.observed: bool | None = None

    @property
    def entity_id(self) -> str | None:
        """The configured switch, or None."""
        return self._config.get(CONF_DHW_DISINFECTION_SWITCH_ENTITY) or None

    def observe(self, reader: Any) -> None:
        """Read the configured switch through the cycle's input reader.

        UNBOUNDED on the external-heat flag's rationale: a switch is written
        only when it changes, so its age is not evidence of staleness.
        """
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
                "state": self.observed,
            }
        }
