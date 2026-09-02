"""Switch entity for Heat Pump Cost Optimizer.

Provides an on/off switch to enable/disable the optimizer.
When off, the heat pump is left in its default state.
When on, the optimizer actively controls the heat pump.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import MODE_AUTO, MODE_OFF
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator

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
    async_add_entities([OptimizerEnableSwitch(coordinator, entry)])


class OptimizerEnableSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable the optimizer."""

    _attr_has_entity_name = True
    _attr_translation_key = "optimizer_active"
    _attr_icon = "mdi:robot"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_optimizer_switch"
        # Pin today's English object id for new installs (the integration
        # suggested-object-id mechanism); see the sensor base class.
        self.entity_id = "switch.heat_pump_optimizer_optimizer_active"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if the optimizer is active."""
        if self.coordinator.data:
            return self.coordinator.data.get("mode", MODE_OFF) != MODE_OFF
        return False

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
        current = (self.coordinator.data or {}).get("mode", MODE_OFF)
        if current == MODE_OFF:
            await self.coordinator.async_set_mode(MODE_AUTO)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the optimizer."""
        await self.coordinator.async_set_mode(MODE_OFF)
