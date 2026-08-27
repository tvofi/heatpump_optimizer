"""Binary sensors for Heat Pump Cost Optimizer.

Three states are worth surfacing as their own entities rather than as
attributes buried on another sensor, because each one is something a user may
reasonably want to automate on or be alerted about:

* whether any input the optimizer depends on has gone stale,
* whether an external heat source (typically a wood furnace) is currently
  heating the tanks,
* whether the house is in away mode.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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
    """Set up Heat Pump Optimizer binary sensors from a config entry."""
    coordinator: HeatPumpOptimizerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            InputHealthBinarySensor(coordinator, entry),
            ExternalHeatBinarySensor(coordinator, entry),
            AwayModeBinarySensor(coordinator, entry),
            VentilationBinarySensor(coordinator, entry),
        ]
    )


class _OptimizerBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Shared plumbing so the entities land on the existing device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: ConfigEntry,
        key: str,
        translation_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = translation_key
        # Pin today's English object id for new installs (the integration
        # suggested-object-id mechanism); see the sensor base class.
        self.entity_id = f"binary_sensor.heat_pump_optimizer_{translation_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.coordinator.device_info

    def _data(self) -> dict[str, Any]:
        return self.coordinator.data or {}


class InputHealthBinarySensor(_OptimizerBinarySensorBase):
    """On when an input the optimizer depends on is stale or missing.

    Reported as a problem rather than as a status so that a failure is visible
    instead of silent. A dead sensor otherwise degrades the plan and poisons
    the learners with nothing at all to show for it.
    """

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:alert-decagram-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "input_health", "input_problem")

    @property
    def is_on(self) -> bool:
        data = self._data()
        return bool(data.get("stale_inputs") or data.get("input_problems"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._data()
        return {
            "summary": data.get("input_health"),
            "stale_inputs": data.get("stale_inputs", []),
            "problems": data.get("input_problems", []),
            "input_ages_minutes": data.get("input_ages_minutes", {}),
            "learners_frozen": data.get("learners_frozen", False),
            "learner_freeze_reason": data.get("learner_freeze_reason"),
        }


class VentilationBinarySensor(_OptimizerBinarySensorBase):
    """On while the house is losing heat like a window is open (#26).

    The detector accumulates colder-than-predicted residuals from the
    heat-loss learner's own replay; while it is tripped every learner
    freezes (reason "ventilation") so an afternoon of airing out cannot
    teach the model a heat loss the house does not have. Evidence rides
    in the attributes, same contract as the external-heat detector: a
    heuristic nobody can audit is a heuristic nobody can trust.
    """

    _attr_device_class = BinarySensorDeviceClass.WINDOW
    _attr_icon = "mdi:window-open-variant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry) -> None:
        super().__init__(
            coordinator, entry, "ventilation", "open_window_detected"
        )

    @property
    def is_on(self) -> bool:
        return bool(self._data().get("ventilation_active"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "evidence": self._data().get("ventilation_evidence", []),
        }


class ExternalHeatBinarySensor(_OptimizerBinarySensorBase):
    """On while something other than the heat pump is heating the tanks.

    The evidence is published in the attributes deliberately: a heuristic that
    silently changes the plan is impossible to trust or to debug, and a user
    who can see *why* it triggered can tell a real fire from a false positive.
    """

    _attr_device_class = BinarySensorDeviceClass.HEAT
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "external_heat", "external_heat_source")

    @property
    def is_on(self) -> bool:
        return bool(self._data().get("external_heat_active"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        info = self._data().get("external_heat", {}) or {}
        return {
            "confidence": info.get("confidence"),
            "fading": info.get("fading"),
            "source": info.get("source"),
            "evidence": info.get("evidence", []),
            "since": info.get("since"),
            "dhw_rise_c_per_h": info.get("dhw_rise_c_per_h"),
            "buffer_rise_c_per_h": info.get("buffer_rise_c_per_h"),
            "suppressing_electric_dhw": bool(
                self._data().get("external_heat_suppressing")
            ),
        }


class AwayModeBinarySensor(_OptimizerBinarySensorBase):
    """On while the house is unoccupied and the deep setback applies.

    Deliberately no device class: PRESENCE means on = somebody is home, which
    is the inverse of this sensor, so the UI showed "Home" while away.
    """

    _attr_icon = "mdi:home-export-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "away_mode", "away_mode")

    @property
    def is_on(self) -> bool:
        return bool(self._data().get("away_active"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._data()
        return {
            "return_time": data.get("away_return_time"),
            "hours_until_return": data.get("away_hours_until_return"),
            "away_target_temperature": data.get("away_target_temperature"),
            "away_dhw_min_temperature": data.get("away_dhw_min_temperature"),
            "recovery_active": data.get("away_recovery_active"),
            "source": data.get("away_source"),
        }
