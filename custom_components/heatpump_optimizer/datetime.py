"""Date/time entity for the away-override return instant."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .away import _parse_return_time
from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .entity import HeatPumpOptimizerEntity, publish_then_refresh

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
        entry: HeatPumpOptimizerConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_away_return"
        self.entity_id = "datetime.heat_pump_optimizer_away_return"

    @property
    def native_value(self) -> datetime | None:
        # The live override, not the payload's copy, which changes only after
        # the refresh the set call asks for has run its solve (v6.6.12).
        return _parse_return_time(self.coordinator._away_state.override_return_iso)

    async def async_set_value(self, value: datetime) -> None:
        await self.coordinator.async_set_away(return_time=value, refresh=False)
        publish_then_refresh(self)
