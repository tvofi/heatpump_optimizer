"""Button entities for Heat Pump Cost Optimizer.

Forcing an optimization run and starting a system-identification experiment are
both momentary actions with no lasting state, which is exactly what a
``ButtonEntity`` is for. A switch would have to bounce itself back off, and
until it did, the UI would imply a state that does not exist.

Both runs take real time — an optimization fetches prices and weather and then
solves — so both report ``available`` as False while busy, giving the user
feedback that the press landed rather than inviting a second one.
"""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeatPumpOptimizerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer buttons from a config entry."""
    coordinator: HeatPumpOptimizerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ForceOptimizationButton(coordinator, entry),
            SystemIdentificationButton(coordinator, entry),
            ResetComfortWeightButton(coordinator, entry),
            DiagnoseIntervalButton(coordinator, entry),
        ]
    )


class _OptimizerButtonBase(CoordinatorEntity, ButtonEntity):
    """Shared plumbing so the buttons land on the existing device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.coordinator.device_info


class ForceOptimizationButton(_OptimizerButtonBase):
    """Run the optimization now, without waiting for the next interval."""

    _attr_icon = "mdi:play-circle-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "force_optimization", "Optimize Now")

    @property
    def available(self) -> bool:
        """Unavailable while a run is in flight, so repeated taps do nothing."""
        return not self.coordinator.optimization_running

    async def async_press(self) -> None:
        """Force an optimization run."""
        _LOGGER.info("Optimization run requested from the dashboard")
        await self.coordinator.async_force_optimization()


class SystemIdentificationButton(_OptimizerButtonBase):
    """Arm the commissioning step test (item 18).

    Pressing does not start an experiment immediately: it arms one, and the
    coordinator runs it at the next moment the gating conditions hold (mild
    weather, cheap electricity, night). Running it on demand regardless of
    conditions would be both expensive and uncomfortable.
    """

    _attr_icon = "mdi:flask-outline"
    _attr_entity_category = None

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry, "system_identification", "Run System Identification"
        )

    @property
    def available(self) -> bool:
        return not self.coordinator.system_identification_active

    async def async_press(self) -> None:
        await self.coordinator.async_arm_system_identification()


class ResetComfortWeightButton(_OptimizerButtonBase):
    """Undo the revealed-preference comfort tuning (item 19).

    A self-adjusting objective the user cannot reset would be alarming, so the
    learned value is always both visible and revertible.
    """

    _attr_icon = "mdi:restore"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry, "reset_comfort_weight", "Reset Learned Comfort Weight"
        )

    async def async_press(self) -> None:
        await self.coordinator.async_reset_comfort_weight()


class DiagnoseIntervalButton(_OptimizerButtonBase):
    """Attribute the last interval's temperature residual (T6 #52).

    One press, one attribution: the coordinator re-runs the interval that
    just settled, swapping realised inputs into the plan's assumptions one
    at a time, and publishes what each swap explains on the Prediction
    Accuracy sensor. A button rather than an automatic per-interval run,
    because the answer is for a person mid-investigation — computed
    unasked it would be noise, and noise about the model's errors is the
    fastest way to teach people to ignore them.
    """

    _attr_icon = "mdi:stethoscope"
    _attr_entity_category = None

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry, "diagnose_interval", "Diagnose Last Interval"
        )

    async def async_press(self) -> None:
        await self.coordinator.async_diagnose_interval()
