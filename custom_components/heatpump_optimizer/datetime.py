"""Date/time entity for the away-override return instant."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .away import _parse_return_time
from .coordinator import HeatPumpOptimizerConfigEntry
from .entity import HeatPumpOptimizerEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HeatPumpOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([AwayReturnDateTime(coordinator, entry)])


class AwayReturnDateTime(HeatPumpOptimizerEntity, DateTimeEntity):
    """Published return instant for the Plan-page away override."""

    _attr_translation_key = "away_return"

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_away_return"
        self.entity_id = "datetime.heat_pump_optimizer_away_return"

    @property
    def native_value(self) -> datetime | None:
        raw = (self.coordinator.data or {}).get("away_override_return_time")
        return _parse_return_time(raw)

    async def async_set_value(self, value: datetime) -> None:
        await self.coordinator.async_set_away(return_time=value)
