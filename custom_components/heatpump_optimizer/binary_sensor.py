"""Binary sensors for Heat Pump Cost Optimizer.

Six states are worth surfacing as their own entities rather than as
attributes buried on another sensor, because each one is something a user may
reasonably want to automate on or be alerted about:

* "Input Problem" — whether any input the optimizer depends on has gone stale,
* "External Heat Source" — whether something other than the heat pump
  (typically a wood furnace) is currently heating the tanks,
* "Away Mode" — whether the house is unoccupied and the deep setback applies,
* "Open Window Detected" — whether the house is losing heat like a window is
  open,
* "Mold Floor Breach" — whether the measured room sits below the mold-safe
  floor the optimizer promises, typically because space heating is blocked,
* "Wood Cheaper Than Heat Pump" — whether burning wood costs less per kWh
  than running the heat pump.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
from .entity import HeatPumpOptimizerEntity
from .const import (
    CONF_MOLD_FLOOR_BREACH_MARGIN,
    DEFAULT_MOLD_FLOOR_BREACH_MARGIN,
)

_LOGGER = logging.getLogger(__name__)

# Coordinator-fed and read-only: the coordinator serialises the one inbound
# refresh, and no entity here calls out, so there is nothing to throttle
# (parallel-updates, Silver).
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HeatPumpOptimizerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer binary sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            InputHealthBinarySensor(coordinator, entry),
            ExternalHeatBinarySensor(coordinator, entry),
            AwayModeBinarySensor(coordinator, entry),
            VentilationBinarySensor(coordinator, entry),
            MoldFloorBreachBinarySensor(coordinator, entry),
            WoodCheaperBinarySensor(coordinator, entry),
        ]
    )


class _OptimizerBinarySensorBase(HeatPumpOptimizerEntity, BinarySensorEntity):
    """Shared plumbing so the entities land on the existing device."""

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: HeatPumpOptimizerConfigEntry,
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

    def _data(self) -> dict[str, Any]:
        return self.coordinator.data or {}


class InputHealthBinarySensor(_OptimizerBinarySensorBase):
    """On when an input the optimizer depends on is stale or missing.

    Reported as a problem rather than as a status so that a failure is visible
    instead of silent. A dead sensor otherwise degrades the plan and poisons
    the learners with nothing at all to show for it. The attributes name the
    culprits: ``problem_inputs`` carries the failing entities and
    ``problem_messages`` one readable line per failure, because a flag a user
    cannot act on asks them to audit every configured sensor by hand.
    """

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
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
            "problem_inputs": data.get("problem_inputs", []),
            "problem_messages": data.get("problem_messages", []),
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
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
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


class MoldFloorBreachBinarySensor(_OptimizerBinarySensorBase):
    """On while the measured room sits below the mold-safe floor (#1495).

    The mold guard computes the lowest room temperature that keeps the worst
    thermal-bridge surface under the mold RH limit (~18 °C in cold/damp
    weather), capped at the configured comfort target, and the solve holds the
    plan's predicted room at that floor. In
    DHW-only / space-blocked mode the pump cannot deliver space heat, so the
    room free-cools below the floor while the dashboard card charts the plan's
    promise instead of the room. This fires when the measured room is that far
    below the floor, and carries the floor, the shortfall and whether space
    heating is blocked so a breach and its cause are one glance apart.
    """

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "mold_floor_breach", "mold_floor_breach")
        self._config = {**entry.data, **entry.options}

    def _margin_c(self) -> float:
        """The breach margin, °C: a noisily jittering reading must not fire."""
        raw = self._config.get(
            CONF_MOLD_FLOOR_BREACH_MARGIN, DEFAULT_MOLD_FLOOR_BREACH_MARGIN
        )
        try:
            return float(raw)
        except (TypeError, ValueError):
            return float(DEFAULT_MOLD_FLOOR_BREACH_MARGIN)

    def _floor(self) -> tuple[float | None, float | None]:
        """``(floor_c, shortfall_c)`` against the measured room, or ``(None, None)``.

        The floor is the one the solve enforces: the coordinator's own
        ``_mold_floor_series`` evaluated at the measured outdoor temperature,
        so the guard toggle, the humidity entity's age check and the cap at
        the configured comfort target are the solve's, not a second copy.
        """
        data = self._data()
        ok = data.get("reading_ok") or {}
        # Only live readings are measurements: without an indoor or outdoor
        # thermometer the payload carries ThermalState's constructor seeds
        # (21.0 / 5.0 °C), which must not be compared as if measured.
        if not (ok.get("upper_floor_temperature") and ok.get("outdoor_temperature")):
            return None, None
        floors = self.coordinator._mold_floor_series(
            np.array([float(data["outdoor_temperature"])])
        )
        if floors is None:
            return None, None
        two_zone = bool(data.get("two_zone_enabled"))
        room = float(data["upper_floor_temperature" if two_zone else "indoor_temperature"])
        floor = float(floors[0])
        return round(floor, 2), round(floor - room, 2)

    @property
    def is_on(self) -> bool:
        _floor, shortfall = self._floor()
        return bool(shortfall is not None and shortfall >= self._margin_c())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        floor, shortfall = self._floor()
        data = self._data()
        return {
            "floor_c": floor,
            "shortfall_c": shortfall,
            "space_blocked": bool(
                (data.get("heat_pump_signals") or {}).get("space_blocked")
            ),
        }


class ExternalHeatBinarySensor(_OptimizerBinarySensorBase):
    """On while something other than the heat pump is heating the tanks.

    The evidence is published in the attributes deliberately: a heuristic that
    silently changes the plan is impossible to trust or to debug, and a user
    who can see *why* it triggered can tell a real fire from a false positive.
    """

    _attr_device_class = BinarySensorDeviceClass.HEAT
    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
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

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
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


class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):
    # The wood furnace is an options-page opt-in most installs never turn
    # on; the comparison is unavailable without it, so disabled rather than
    # shipped dead (#1335), with the advisor twin on the same gate.
    # Existing registry entries keep their state.
    _attr_entity_registry_enabled_default = False

    def __init__(
        self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "wood_cheaper", "wood_cheaper")

    @property
    def available(self) -> bool:
        fuel = self._data().get("wood_fuel") or {}
        return bool(super().available and fuel.get("ready"))

    @property
    def is_on(self) -> bool:
        fuel = self._data().get("wood_fuel") or {}
        return bool(fuel.get("ready") and fuel.get("cheaper"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        fuel = self._data().get("wood_fuel") or {}
        return {
            "sek_per_kwh": fuel.get("sek_per_kwh"),
            "cheaper_hour_count": fuel.get("cheaper_hour_count"),
        }

