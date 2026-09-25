"""Switch entities for Heat Pump Cost Optimizer.

Four switches, all plain toggles over coordinator state. Each reads the live
state rather than the published payload and writes its own state as soon as
the action lands: the payload changes only when the refresh the action asks
for has run its solve, 30 to 70 s on a Pi, and Home Assistant's toggle falls
back to the old state after about two seconds without a state change -- so a
switch turned off flipped back on in front of the user (v6.6.12).

* "Optimizer Active" — the master on/off switch for the optimizer. When off,
  the heat pump is left in its default state; when on, the optimizer actively
  controls the heat pump.
* "Away" — the plan page's away override.
* "DHW Boost" and "Boost Space Heating" — two-hour maximum boosts of the hot
  water and the space heating, released when their window ends.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import boost
from .const import MODE_AUTO, MODE_OFF
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .entity import DHWEntityMixin
from .entity import HeatPumpOptimizerEntity

_LOGGER = logging.getLogger(__name__)

# Turning the optimizer on or off lands on the coordinator, which commands
# one heat pump; two toggles racing is two commands to one machine, so
# actions on this platform run one at a time (parallel-updates, Silver).
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HeatPumpOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer switch from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            OptimizerEnableSwitch(coordinator, entry),
            AwaySwitch(coordinator, entry),
            BoostDhwSwitch(coordinator, entry),
            BoostSpaceSwitch(coordinator, entry),
        ]
    )


class OptimizerEnableSwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """Switch to enable/disable the optimizer."""

    _attr_translation_key = "optimizer_active"
    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_optimizer_switch"
        # Pin today's English object id for new installs (the integration
        # suggested-object-id mechanism); see the sensor base class.
        self.entity_id = "switch.heat_pump_optimizer_optimizer_active"

    @property
    def is_on(self) -> bool:
        """Return true if the optimizer is active."""
        return bool(self.coordinator.mode != MODE_OFF)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data:
            return {
                "mode": self.coordinator.data.get("mode"),
                "optimization_status": self.coordinator.data.get("optimization_status"),
            }
        return {}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the optimizer.

        Only from *off*. Turning on a switch that is already on used to force
        `auto`, which silently threw away a live economy or comfort selection --
        easy to trigger from a dashboard toggle or a scene.
        """
        if self.coordinator.mode == MODE_OFF:
            await self.coordinator.async_set_mode(MODE_AUTO)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the optimizer."""
        await self.coordinator.async_set_mode(MODE_OFF)
        self.async_write_ha_state()


class AwaySwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """Plan-page away override on/off. ``is_on`` is the override, not resolve()."""

    _attr_translation_key = "away"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_away"
        self.entity_id = "switch.heat_pump_optimizer_away"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator._away_state.override_active)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_away(active=True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_away(active=False)
        self.async_write_ha_state()


class BoostDhwSwitch(DHWEntityMixin, SwitchEntity):
    """Two-hour maximum hot-water heat; gated like every hot-water entity (#1527)."""

    _attr_translation_key = "dhw_boost"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        # The unique id keeps the pre-#1334 key: an existing install's registry
        # entry (and its history) is identified by this string, so the rename
        # moves the suggested object id for NEW installs only, exactly as #1227
        # and #1333 moved the sensors'.
        self._attr_unique_id = f"{entry.entry_id}_boost_dhw"
        self.entity_id = "switch.heat_pump_optimizer_dhw_boost"

    @property
    def is_on(self) -> bool:
        return boost.held_for(self.coordinator).active("dhw", dt_util.now())

    async def async_turn_on(self, **kwargs: Any) -> None:
        await boost.set_channel(self.coordinator, "dhw", True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await boost.set_channel(self.coordinator, "dhw", False)
        self.async_write_ha_state()


class BoostSpaceSwitch(HeatPumpOptimizerEntity, SwitchEntity):
    """Two-hour maximum space heat."""

    _attr_translation_key = "boost_space"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_boost_space"
        self.entity_id = "switch.heat_pump_optimizer_boost_space"

    @property
    def is_on(self) -> bool:
        return boost.held_for(self.coordinator).active("space", dt_util.now())

    async def async_turn_on(self, **kwargs: Any) -> None:
        await boost.set_channel(self.coordinator, "space", True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await boost.set_channel(self.coordinator, "space", False)
        self.async_write_ha_state()
