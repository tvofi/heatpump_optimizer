"""Sensor entities for Heat Pump Cost Optimizer."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DHW_MIN_TEMP_SETPOINT_MARGIN, DOMAIN, MANUAL_PLAN_WINDOW_HOURS
from .coordinator import HeatPumpOptimizerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heat Pump Optimizer sensors from a config entry."""
    coordinator: HeatPumpOptimizerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        OptimizationModeSensor(coordinator, entry),
        OptimizationStatusSensor(coordinator, entry),
        PredictedSavingsSensor(coordinator, entry),
        SavingsPercentageSensor(coordinator, entry),
        PredictedCostSensor(coordinator, entry),
        BaselineCostSensor(coordinator, entry),
        CurrentPriceSensor(coordinator, entry),
        CurrentSetpointSensor(coordinator, entry),
        CurrentPowerSensor(coordinator, entry),
        CurrentCOPSensor(coordinator, entry),
        IndoorTempSensor(coordinator, entry),
        OutdoorTempSensor(coordinator, entry),
        SolarIrradianceSensor(coordinator, entry),
        SlabTempSensor(coordinator, entry),
        NextOptimizationSensor(coordinator, entry),
        LastOptimizationSensor(coordinator, entry),
        HeatPumpActionSensor(coordinator, entry),
        ScheduleSensor(coordinator, entry),
        # Two-zone sensors
        UpperFloorTempSensor(coordinator, entry),
        LowerFloorTempSensor(coordinator, entry),
        FloorReturnTempSensor(coordinator, entry),
        SolarRadiationSensor(coordinator, entry),
        SolarHeatGainSensor(coordinator, entry),
        BufferTankTempSensor(coordinator, entry),
        # DHW sensors
        DHWTemperatureSensor(coordinator, entry),
        DHWScheduleSensor(coordinator, entry),
        DHWHeatingCostSensor(coordinator, entry),
        # Predictive insight sensors
        PredictiveInsightSensor(coordinator, entry),
        ECL110DisplaceSensor(coordinator, entry),
        ECL110EffectiveDisplaceSensor(coordinator, entry),
        # Plan sensors backing the dashboard card
        SpaceHeatingPlanSensor(coordinator, entry),
        DHWHeatingPlanSensor(coordinator, entry),
        # Measured draw and observed efficiency (items 6, 14)
        MeasuredPowerSensor(coordinator, entry),
        ObservedCOPSensor(coordinator, entry),
        # Long-term energy and cost statistics (item 15)
        SpaceEnergySensor(coordinator, entry),
        DHWEnergySensor(coordinator, entry),
        TotalEnergySensor(coordinator, entry),
        SpaceCostSensor(coordinator, entry),
        DHWCostSensor(coordinator, entry),
        TotalCostSensor(coordinator, entry),
        # Closed-loop accuracy (item 11)
        PredictionAccuracySensor(coordinator, entry),
        # Capacity tariff (item 8)
        MonthlyPeakSensor(coordinator, entry),
        # PV self-consumption (item 9)
        PVSurplusSensor(coordinator, entry),
        # The house as a virtual battery (item 20)
        ThermalBatterySensor(coordinator, entry),
        ThermalBatteryEnergySensor(coordinator, entry),
        # Learned comfort weight (item 19)
        ComfortWeightSensor(coordinator, entry),
        ContractComparisonSensor(coordinator, entry),
        # Dumb-valve setting recommendation (item 29)
        ValveTargetRecommendationSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class HeatPumpOptimizerSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Heat Pump Optimizer sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HeatPumpOptimizerCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._entry = entry
        self._key = key

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.coordinator.device_info


# ---------------------------------------------------------------------------
# Original sensors (maintained for backward compatibility)
# ---------------------------------------------------------------------------


class OptimizationModeSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the current optimization mode."""

    _attr_icon = "mdi:cog-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "mode", "Optimization Mode")

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            return self.coordinator.data.get("mode", "unknown")
        return "unknown"


class OptimizationStatusSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the optimization solver status."""

    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "optimization_status", "Optimization Status")

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            return self.coordinator.data.get("optimization_status", "not_run")
        return "not_run"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            return {
                "solve_time_ms": self.coordinator.data.get("solve_time_ms", 0),
                "prices_available": self.coordinator.data.get("prices_available", 0),
                "weather_forecast_available": self.coordinator.data.get(
                    "weather_forecast_available", 0
                ),
                "two_zone_enabled": self.coordinator.data.get("two_zone_enabled", False),
            }
        return {}


class PredictedSavingsSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:piggy-bank-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "predicted_savings", "Predicted Savings")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("predicted_savings")
            return round(val, 2) if val is not None else None
        return None


class SavingsPercentageSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:percent"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "savings_percentage", "Savings Percentage")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("savings_percentage")
            return round(val, 1) if val is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "baseline_cost": data.get("baseline_cost"),
            "predicted_cost": data.get("predicted_cost"),
            # Heat the plan leaves unstored at the end of the horizon has to be
            # bought back later, so it is charged against the savings even
            # though it is not part of predicted_cost.
            "deferred_energy_cost": data.get("deferred_energy_cost"),
        }


class PredictedCostSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:currency-usd"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "predicted_cost", "Predicted Cost")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("predicted_cost")
            return round(val, 2) if val is not None else None
        return None


class BaselineCostSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:currency-usd-off"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "baseline_cost", "Baseline Cost")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("baseline_cost")
            return round(val, 2) if val is not None else None
        return None


class CurrentPriceSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:flash"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK/kWh"
    # No device_class: this is a unit price, not a monetary total. Home
    # Assistant only accepts state_class "total" for device_class "monetary",
    # so declaring it here made HA reject the sensor's statistics.

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "current_price", "Current Electricity Price")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("current_price")
            return round(val, 4) if val is not None else None
        return None


class CurrentSetpointSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:thermometer"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "current_setpoint", "Optimal Setpoint")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            return action.get("setpoint")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            attrs = {}
            if "upper_setpoint" in action:
                attrs["upper_floor_setpoint"] = action["upper_setpoint"]
            if "lower_setpoint" in action:
                attrs["lower_floor_setpoint"] = action["lower_setpoint"]
            return attrs
        return {}


class CurrentPowerSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:lightning-bolt"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "current_power", "Recommended Power")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            val = action.get("power")
            return round(val, 2) if val is not None else None
        return None


class CurrentCOPSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:gauge"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "current_cop", "Estimated COP")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            outdoor_temp = self.coordinator.data.get("outdoor_temperature", 5.0)
            cop = self.coordinator._thermal_model.compute_cop(outdoor_temp)
            return round(cop, 2)
        return None


class IndoorTempSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:home-thermometer"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "indoor_temp", "Indoor Temperature (Optimizer)")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("indoor_temperature")
            return round(val, 1) if val is not None else None
        return None


class OutdoorTempSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:thermometer"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "outdoor_temp", "Outdoor Temperature (Optimizer)")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("outdoor_temperature")
            return round(val, 1) if val is not None else None
        return None


class SolarIrradianceSensor(HeatPumpOptimizerSensorBase):
    """Global horizontal irradiance the optimizer is currently planning with.

    Publishing this makes an otherwise invisible input checkable: if the
    forecast source is misconfigured the value sits at zero in daylight, which
    is immediately obvious here and very hard to spot in the schedule.
    """

    _attr_icon = "mdi:weather-sunny"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W/m²"
    _attr_device_class = SensorDeviceClass.IRRADIANCE
    # The forecast series is far too large to write to the recorder on every
    # update, and its history is of no interest once superseded.
    _unrecorded_attributes = frozenset({"forecast"})

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "solar_irradiance", "Solar Irradiance")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("solar_radiation")
            return round(val, 1) if val is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        attrs: dict[str, Any] = {
            # A stable marker the dashboard card discovers this sensor by.
            # Entity ids are derived from the device name, so they are not a
            # contract — hardcoding one is what caused the v2.6.1 bug where the
            # card never found its plan sensors.
            "plan_kind": "solar",
            "source": data.get("solar_source"),
            "solar_heat_gain_kw": round(data.get("solar_heat_gain", 0.0) or 0.0, 3),
            "forecast": data.get("solar_forecast", []),
        }
        diagnostics = data.get("solar_diagnostics")
        if diagnostics:
            attrs.update(diagnostics)
        return attrs


class SlabTempSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:floor-plan"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "slab_temp", "Slab Temperature (Estimated)")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("slab_temperature")
            return round(val, 1) if val is not None else None
        return None


class NextOptimizationSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:clock-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "next_optimization", "Next Optimization")

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.data:
            return self.coordinator.data.get("next_optimization")
        return None


class LastOptimizationSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:clock-check-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "last_optimization", "Last Optimization")

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.data:
            return self.coordinator.data.get("last_optimization")
        return None


class HeatPumpActionSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:heat-pump"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "heat_pump_action", "Heat Pump Action")

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            return action.get("mode", "unknown")
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            action = self.coordinator.data.get("current_action", {})
            attrs = {
                "power_kw": action.get("power"),
                "setpoint": action.get("setpoint"),
                "price": action.get("price"),
                "power_normalized": action.get("power_normalized"),
                "heat_pump_on": action.get("heat_pump_on"),
                "ecl110_displace": action.get("displace_value"),
            }
            if "upper_setpoint" in action:
                attrs["upper_floor_setpoint"] = action["upper_setpoint"]
            if "lower_setpoint" in action:
                attrs["lower_floor_setpoint"] = action["lower_setpoint"]
            if "solar_gain_kw" in action:
                attrs["solar_gain_kw"] = action["solar_gain_kw"]
            return attrs
        return {}


class ScheduleSensor(HeatPumpOptimizerSensorBase):
    _attr_icon = "mdi:calendar-clock"
    # The schedule is re-published every update and superseded history is of
    # no interest; recording it would write kilobytes per cycle, the same
    # reason the plan sensors keep their forecasts out of the recorder.
    _unrecorded_attributes = frozenset({"schedule"})

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "schedule", "Optimization Schedule")

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            schedule = self.coordinator.data.get("schedule", [])
            return f"{len(schedule)} steps" if schedule else "no schedule"
        return "no schedule"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            return {
                "schedule": self.coordinator.data.get("schedule", []),
            }
        return {}


# ---------------------------------------------------------------------------
# New two-zone and solar sensors
# ---------------------------------------------------------------------------


class UpperFloorTempSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing upper floor (radiator zone) temperature."""

    _attr_icon = "mdi:home-floor-1"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "upper_floor_temp", "Upper Floor Temperature"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("upper_floor_temperature")
            return round(val, 1) if val is not None else None
        return None


class LowerFloorTempSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing lower floor (slab/floor heating zone) temperature."""

    _attr_icon = "mdi:home-floor-0"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "lower_floor_temp", "Lower Floor Temperature"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("lower_floor_temperature")
            return round(val, 1) if val is not None else None
        return None


class FloorReturnTempSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the floor heating return temperature (from real sensor)."""

    _attr_icon = "mdi:pipe-valve"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "floor_return_temp", "Floor Heating Return Temperature"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("floor_return_temperature")
            return round(val, 1) if val is not None else None
        return None


class SolarRadiationSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the current solar radiation used by optimizer."""

    _attr_icon = "mdi:white-balance-sunny"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W/m²"
    _attr_device_class = SensorDeviceClass.IRRADIANCE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "solar_radiation", "Solar Radiation (Optimizer)"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("solar_radiation")
            return round(val, 0) if val is not None else None
        return None


class SolarHeatGainSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the current solar heat gain contribution in kW."""

    _attr_icon = "mdi:solar-power"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "solar_heat_gain", "Solar Heat Gain"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("solar_heat_gain")
            return round(val, 3) if val is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            return {
                "solar_radiation_wm2": self.coordinator.data.get("solar_radiation", 0),
                "window_area_m2": self.coordinator._thermal_params.window_area,
                "shgc": self.coordinator._thermal_params.solar_heat_gain_coefficient,
                "orientation_factor": self.coordinator._thermal_params.solar_orientation_factor,
            }
        return {}


class BufferTankTempSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the modeled buffer tank temperature."""

    _attr_icon = "mdi:water-boiler"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "buffer_tank_temp", "Buffer Tank Temperature (Model)"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("buffer_tank_temperature")
            return round(val, 1) if val is not None else None
        return None


# ---------------------------------------------------------------------------
# DHW (Domestic Hot Water) sensors
# ---------------------------------------------------------------------------


class DHWTemperatureSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing current DHW tank temperature."""

    _attr_icon = "mdi:water-thermometer"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "dhw_temperature", "DHW Temperature"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("dhw_temperature")
            return round(val, 1) if val is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            data = self.coordinator.data
            info = data.get("predictive_info", {})
            return {
                "dhw_setpoint": data.get("dhw_setpoint"),
                "dhw_min_temperature": data.get("dhw_min_temperature"),
                "dhw_heating_active": data.get("dhw_heating_active", False),
                "dhw_enabled": data.get("dhw_enabled", False),
                "dhw_windows": data.get("dhw_windows"),
                "dhw_in_demand_window": data.get("dhw_in_demand_window"),
                "dhw_next_window_in_hours": data.get("dhw_next_window_in_hours"),
                "dhw_required_temperature": info.get(
                    "dhw_required_temperature_now", data.get("dhw_min_temperature")
                ),
                "dhw_idle_min_temperature": data.get("dhw_idle_min_temperature"),
                "dhw_legionella_due_in_hours": data.get(
                    "dhw_legionella_due_in_hours"
                ),
                "dhw_cooling_rate": data.get("dhw_cooling_rate"),
                "dhw_cooling_rate_learned": data.get("dhw_cooling_rate_learned"),
                "dhw_cooling_samples": data.get("dhw_cooling_samples"),
                "dhw_hold_hours": data.get("dhw_hold_hours"),
            }
        return {}


class DHWScheduleSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the planned DHW heating schedule for the next 24 hours."""

    _attr_icon = "mdi:water-boiler-auto"
    # Superseded plans are of no interest; see ScheduleSensor.
    _unrecorded_attributes = frozenset({"dhw_schedule"})

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "dhw_schedule", "DHW Heating Schedule"
        )

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            schedule = self.coordinator.data.get("dhw_schedule", [])
            if schedule:
                active_steps = sum(1 for s in schedule if s.get("dhw_power", 0) > 0.1)
                return f"{active_steps} heating periods"
            return "no schedule"
        return "no schedule"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            data = self.coordinator.data
            info = data.get("predictive_info", {})
            return {
                "dhw_schedule": data.get("dhw_schedule", []),
                "dhw_windows": data.get("dhw_windows"),
                "dhw_schedule_enabled": data.get("dhw_schedule_enabled"),
                "dhw_in_demand_window": data.get("dhw_in_demand_window"),
                "dhw_next_window_in_hours": data.get("dhw_next_window_in_hours"),
                "dhw_planned_heating_hours": info.get("dhw_planned_heating_hours", []),
                "dhw_preheat_hours": info.get("dhw_preheat_hours"),
                "dhw_legionella_due": info.get("dhw_legionella_due"),
                "dhw_legionella_step_hour": info.get("dhw_legionella_step_hour"),
                "dhw_legionella_due_in_hours": data.get(
                    "dhw_legionella_due_in_hours"
                ),
            }
        return {}


class DHWHeatingCostSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing the estimated DHW heating cost."""

    _attr_icon = "mdi:cash-minus"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK"

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "dhw_heating_cost", "DHW Heating Cost"
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("dhw_heating_cost")
            return round(val, 2) if val is not None else None
        return None


# ---------------------------------------------------------------------------
# Predictive insight sensors
# ---------------------------------------------------------------------------


class PredictiveInsightSensor(HeatPumpOptimizerSensorBase):
    """Sensor showing predictive optimization insights.

    Exposes the anticipatory control signals from the forecast analysis:
    - Solar reduction factor (how much heating is reduced due to upcoming sun)
    - Wind anticipation factor (how much extra heating due to upcoming wind)
    - Pre-heat urgency (overall urgency to pre-heat)
    """

    _attr_icon = "mdi:crystal-ball"

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "predictive_insight", "Predictive Optimization Insight"
        )

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data:
            info = self.coordinator.data.get("predictive_info", {})
            if not info:
                return "no forecast"

            urgency = info.get("pre_heat_urgency", 0)
            solar_red = info.get("solar_reduction_factor", 1.0)

            if solar_red < 0.8:
                return "solar_anticipation"
            elif urgency > 0.5:
                return "pre_heating"
            else:
                return "normal"
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            info = self.coordinator.data.get("predictive_info", {})
            return {
                "solar_reduction_factor": info.get("solar_reduction_factor"),
                "wind_anticipation_factor": info.get("wind_anticipation_factor"),
                "rain_anticipation_factor": info.get("rain_anticipation_factor"),
                "pre_heat_urgency": info.get("pre_heat_urgency"),
                "future_solar_energy_kwh": info.get("future_solar_energy_kwh"),
                "future_solar_6_12h_kwh": info.get("future_solar_6_12h_kwh"),
                "avg_future_wind_ms": info.get("avg_future_wind_ms"),
                "avg_future_precip_mmh": info.get("avg_future_precip_mmh"),
                "dhw_preheat_lead_hours": info.get("dhw_preheat_lead_hours"),
                "dhw_peak_usage_hours": info.get("dhw_peak_usage_hours"),
                "dhw_min_temperature": info.get("dhw_min_temperature"),
                "dhw_target_temperature": info.get("dhw_target_temperature"),
                "dhw_windows": info.get("dhw_windows"),
                "dhw_in_demand_window": info.get("dhw_in_demand_window"),
                "dhw_next_window_in_hours": info.get("dhw_next_window_in_hours"),
                "dhw_required_temperature_now": info.get(
                    "dhw_required_temperature_now"
                ),
                "dhw_idle_min_temperature": info.get("dhw_idle_min_temperature"),
                "dhw_legionella_due": info.get("dhw_legionella_due"),
                "dhw_planned_heating_hours": info.get("dhw_planned_heating_hours"),
                "dhw_usage_profile": self.coordinator.data.get("dhw_usage_profile", []),
            }
        return {}


class ECL110DisplaceSensor(HeatPumpOptimizerSensorBase):
    """Current ECL110 displace command value."""

    _attr_icon = "mdi:tune-vertical"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "ecl110_displace", "ECL110 Displace")

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("ecl110_displace")
            return round(val, 1) if val is not None else None
        return None


class ECL110EffectiveDisplaceSensor(HeatPumpOptimizerSensorBase):
    """Modeled effective displace after ECL110 PI/PID dynamics."""

    _attr_icon = "mdi:chart-bell-curve"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "ecl110_effective_displace",
            "ECL110 Effective Displace",
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data:
            val = self.coordinator.data.get("ecl110_effective_displace")
            return round(val, 1) if val is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data:
            return {
                "command_topic": self.coordinator.data.get("ecl110_command_topic"),
                "state_topic": self.coordinator.data.get("ecl110_state_topic"),
            }
        return {}

def _dhw_min_ceiling(setpoint: Any) -> float | None:
    """Highest usable minimum that still leaves a deadband below the setpoint.

    Returns ``None`` when the setpoint is not known yet, so the card can tell
    "no answer" from a real limit and fall back rather than clamp to zero.
    """
    try:
        return round(float(setpoint) - DHW_MIN_TEMP_SETPOINT_MARGIN, 1)
    except (TypeError, ValueError):
        return None


class _PlanSensorBase(HeatPumpOptimizerSensorBase):
    """Shared behaviour for the two full-horizon plan sensors.

    These carry the whole optimization horizon (96 points at the default 15
    minute resolution) so the dashboard card can chart it. That is far too much
    data to write to the recorder database every update, so the bulky series
    are declared unrecorded; the state and the small summary attributes are
    still recorded and remain usable in history and automations.
    """

    _unrecorded_attributes = frozenset({"forecast", "slots", "setup_topology"})
    _plan_key: str = ""
    # Stable machine-readable marker. Entity ids depend on the device name and
    # can be renamed by the user, so the dashboard card discovers these sensors
    # by this attribute rather than by guessing at an entity id.
    _plan_kind: str = ""

    @property
    def _plan(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        plan = self.coordinator.data.get(self._plan_key)
        return plan if isinstance(plan, dict) else {}

    @property
    def native_value(self) -> str | None:
        plan = self._plan
        if not plan:
            return "no plan"
        slots = plan.get("slots", [])
        if not slots:
            return "no heating planned"
        if plan.get("active_now"):
            return "heating now"
        return f"{len(slots)} slots planned"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        plan = self._plan
        # plan_kind is emitted even with no plan yet so the card can still find
        # the entity and report *why* it is empty rather than "not found".
        if not plan:
            return {
                "plan_kind": self._plan_kind,
                "manual_override": (self.coordinator.data or {}).get("manual_plan"),
                # Published here too: it is a fixed property of the integration,
                # not something derived from a plan, and the card needs it to
                # bound editing before the first plan has arrived.
                "manual_plan_window_hours": MANUAL_PLAN_WINDOW_HOURS,
                # Configuration-derived, so it exists before the first plan
                # does; the card's setup page should not need a solve to draw.
                "setup_topology": self.coordinator.describe_setup(),
            }
        slots = plan.get("slots", [])
        next_slot = None
        if not plan.get("active_now") and slots:
            next_slot = slots[0].get("start")
        elif plan.get("active_now") and len(slots) > 1:
            next_slot = slots[1].get("start")
        data = self.coordinator.data or {}
        return {
            "plan_kind": self._plan_kind,
            "forecast": plan.get("forecast", []),
            "slots": slots,
            "slot_count": len(slots),
            "total_energy_kwh": plan.get("total_energy_kwh", 0.0),
            "total_cost": plan.get("total_cost", 0.0),
            "active_now": plan.get("active_now", False),
            "next_slot_start": next_slot,
            # The schedule this plan was made against, so the card's what-if
            # editor can pre-fill from what is really in force rather than
            # from a default that would propose an unasked-for change.
            "day_start_hour": data.get("day_start_hour"),
            "day_end_hour": data.get("day_end_hour"),
            "comfort_temp_day": data.get("comfort_temp_day"),
            "comfort_temp_night": data.get("comfort_temp_night"),
            "dhw_windows": data.get("dhw_windows"),
            "dhw_min_temperature": data.get("dhw_min_temperature"),
            "dhw_setpoint": data.get("dhw_setpoint"),
            # The ceiling the hot water minimum has to stay under, computed
            # here rather than in the card so the margin lives in exactly one
            # place and the card's slider re-clamps on its own whenever the
            # setpoint is reconfigured -- a slider whose maximum was fixed at
            # render time against a stale setpoint is the same class of bug
            # `_draftRuns` had in v3.2.0.
            "dhw_min_temperature_max": _dhw_min_ceiling(data.get("dhw_setpoint")),
            # The active manual override (or None). The card reads this to show
            # which slots are pinned and which pins safety had to release.
            "manual_override": data.get("manual_plan"),
            # How far ahead a hand-arranged plan may be pinned, published rather
            # than duplicated in the card so the chart's edit ceiling and the
            # service's expiry default cannot drift apart. If they did, the card
            # would show slots as pinned beyond the point `channel_pins` frees
            # them -- which is the failure this number exists to prevent.
            "manual_plan_window_hours": MANUAL_PLAN_WINDOW_HOURS,
            # The configured topology for the card's setup page (item 33),
            # emitted by the coordinator so the config flow's overview and
            # the card can never disagree about what the system looks like.
            "setup_topology": self.coordinator.describe_setup(),
        }


class SpaceHeatingPlanSensor(_PlanSensorBase):
    """Planned space heating slots for the full optimization horizon."""

    _attr_icon = "mdi:radiator"
    _plan_key = "space_plan"
    _plan_kind = "space"

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "space_heating_plan", "Space Heating Plan"
        )


class DHWHeatingPlanSensor(_PlanSensorBase):
    """Planned DHW heating slots for the full optimization horizon."""

    _attr_icon = "mdi:water-boiler"
    _plan_key = "dhw_plan"
    _plan_kind = "dhw"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "dhw_heating_plan", "DHW Heating Plan")


# ---------------------------------------------------------------------------
# Measured electrical draw and observed COP (item 6)
# ---------------------------------------------------------------------------


class MeasuredPowerSensor(HeatPumpOptimizerSensorBase):
    """The heat pump's actual electrical draw.

    Deliberately named to contrast with "Recommended Power", which is what the
    optimizer is *commanding*. Two sensors on one device that differ only in
    whether they are a plan or a measurement will be confused constantly unless
    the names say which is which.
    """

    _attr_icon = "mdi:flash"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "measured_power", "Measured Power")

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return bool(data.get("measured_power_available"))

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get("measured_power")
        return round(value, 3) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "recommended_power": (data.get("current_action") or {}).get("power"),
            "house_power": data.get("measured_house_power"),
            "energy_meter": data.get("measured_energy"),
        }


class ObservedCOPSensor(HeatPumpOptimizerSensorBase):
    """COP derived from measured electrical input, not from the nameplate curve.

    Every plan is priced through COP, so an error here is an error in every
    cost the integration reports. With a measured power entity it stops being
    an assumption and becomes an observable.
    """

    _attr_icon = "mdi:gauge-full"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "observed_cop", "Observed COP")

    def _modelled_cop(self, data: dict[str, Any]) -> float | None:
        model = getattr(self.coordinator, "_thermal_model", None)
        if model is None:
            return None
        return round(model.compute_cop(data.get("outdoor_temperature", 5.0)), 2)

    @property
    def available(self) -> bool:
        return bool((self.coordinator.data or {}).get("measured_power_available"))

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return data.get("measured_cop")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "cop_scale": data.get("cop_scale"),
            "cop_samples": data.get("cop_samples"),
            # The same curve the Estimated COP sensor publishes, so observed
            # and modelled can be compared side by side. The previous source,
            # current_action["cop"], is a key nothing ever writes.
            "modelled_cop": self._modelled_cop(data),
            "defrost_derate": data.get("defrost_derate"),
            "defrost_samples": data.get("defrost_samples"),
            "defrost_buckets": data.get("defrost_buckets", []),
        }


# ---------------------------------------------------------------------------
# Energy dashboard statistics (item 15)
# ---------------------------------------------------------------------------


class _AccumulatingSensor(HeatPumpOptimizerSensorBase):
    """Base for the TOTAL_INCREASING accumulators.

    Every monetary sensor in the integration was ``MEASUREMENT``, so none of it
    reached Home Assistant's Energy dashboard and there was no long-term cost
    history. The result was that the integration's central claim — that it
    saves money — was invisible in the one place users look for exactly that.
    """

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _data_key: str = ""

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        value = data.get(self._data_key)
        return round(value, 3) if isinstance(value, (int, float)) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            # Stated rather than implied: one meter cannot separate two
            # circuits, so the split is apportioned by what the plan asked each
            # circuit to draw.
            "split_method": (
                "apportioned from the planned space/DHW power split; the "
                "total is measured when a power entity is configured"
            ),
            "measured": bool(
                (self.coordinator.data or {}).get("measured_power_available")
            ),
        }


class SpaceEnergySensor(_AccumulatingSensor):
    _attr_icon = "mdi:radiator"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _data_key = "space_energy_kwh"

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "space_energy", "Space Heating Energy"
        )


class DHWEnergySensor(_AccumulatingSensor):
    _attr_icon = "mdi:water-boiler"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _data_key = "dhw_energy_kwh"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "dhw_energy", "Hot Water Energy")


class TotalEnergySensor(_AccumulatingSensor):
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _data_key = "total_energy_kwh"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_energy", "Total Energy")


class _AccumulatingCostSensor(_AccumulatingSensor):
    """Monetary accumulator.

    Home Assistant only accepts state class ``TOTAL`` for ``MONETARY`` (the
    same rule the price sensor documents), and statistics require a currency
    unit; ``TOTAL_INCREASING`` with no unit made HA reject these sensors'
    long-term statistics — the exact feature the accumulators exist for.
    """

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "SEK"


class SpaceCostSensor(_AccumulatingCostSensor):
    _attr_icon = "mdi:cash"
    _data_key = "space_cost"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "space_cost", "Space Heating Cost")


class DHWCostSensor(_AccumulatingCostSensor):
    _attr_icon = "mdi:cash"
    _data_key = "dhw_cost"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "dhw_cost_total", "Hot Water Cost")


class TotalCostSensor(_AccumulatingCostSensor):
    _attr_icon = "mdi:cash-multiple"
    _data_key = "total_cost"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_cost", "Total Heating Cost")


# ---------------------------------------------------------------------------
# Closed-loop accuracy (item 11)
# ---------------------------------------------------------------------------


class PredictionAccuracySensor(HeatPumpOptimizerSensorBase):
    """Mean absolute error of the predicted indoor temperature.

    Publishing the *bias* alongside it matters more than the magnitude: an
    absolute error cannot distinguish random noise from a model that is
    consistently half a degree optimistic, and it is the second that indicates
    drift.
    """

    _attr_icon = "mdi:target"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "prediction_accuracy", "Prediction Accuracy"
        )

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("accuracy", {}).get(
            "temperature_mae"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return dict((self.coordinator.data or {}).get("accuracy", {}) or {})


# ---------------------------------------------------------------------------
# Capacity tariff (item 8)
# ---------------------------------------------------------------------------


class MonthlyPeakSensor(HeatPumpOptimizerSensorBase):
    """The peak level this month's capacity tariff is currently based on."""

    _attr_icon = "mdi:chart-bell-curve"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "monthly_peak", "Monthly Peak Power")

    @property
    def available(self) -> bool:
        return bool((self.coordinator.data or {}).get("peak_tariff_enabled"))

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("billed_peak_kw")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "month": data.get("peak_month"),
            # Below this a new hour is free: the bill is already set by the
            # peaks already recorded, so keeping power low buys nothing.
            "free_headroom_threshold_kw": data.get("peak_threshold_kw"),
            "projected_peak_kw": data.get("projected_peak_kw"),
            "projected_peak_cost": data.get("projected_peak_cost"),
        }


# ---------------------------------------------------------------------------
# PV self-consumption (item 9)
# ---------------------------------------------------------------------------


class PVSurplusSensor(HeatPumpOptimizerSensorBase):
    """Forecast solar surplus available to the heat pump."""

    _attr_icon = "mdi:solar-power-variant"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "pv_surplus", "Solar Surplus Forecast")

    @property
    def available(self) -> bool:
        return bool((self.coordinator.data or {}).get("pv_enabled"))

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("pv", {}).get(
            "forecast_surplus_kwh"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        attrs = dict(data.get("pv", {}) or {})
        attrs["self_consumed_kwh"] = data.get("pv_self_consumed_kwh")
        return attrs


# ---------------------------------------------------------------------------
# The house as a virtual battery (item 20)
# ---------------------------------------------------------------------------


class ThermalBatterySensor(HeatPumpOptimizerSensorBase):
    """State of charge of the building fabric and tanks, as a battery.

    Reported against the comfort band rather than against absolute zero:
    energy stored above the minimum acceptable temperature is what is actually
    available, and counting the rest would overstate the asset.
    """

    _attr_icon = "mdi:home-battery"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "thermal_battery", "Thermal Battery Charge"
        )

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("battery", {}).get(
            "state_of_charge_percent"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return dict((self.coordinator.data or {}).get("battery", {}) or {})


class ThermalBatteryEnergySensor(HeatPumpOptimizerSensorBase):
    """Stored thermal energy available above the comfort floor."""

    _attr_icon = "mdi:battery-charging"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "thermal_battery_energy", "Thermal Battery Energy"
        )

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("battery", {}).get(
            "stored_energy_kwh"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        battery = (self.coordinator.data or {}).get("battery", {}) or {}
        return {
            "usable_capacity_kwh": battery.get("usable_capacity_kwh"),
            "charge_rate_kw": battery.get("charge_rate_kw"),
            "discharge_rate_kw": battery.get("discharge_rate_kw"),
            "hours_of_autonomy": battery.get("hours_of_autonomy"),
            "round_trip_efficiency_6h": battery.get("round_trip_efficiency_6h"),
        }


# ---------------------------------------------------------------------------
# Learned comfort weight (item 19)
# ---------------------------------------------------------------------------


class ValveTargetRecommendationSensor(HeatPumpOptimizerSensorBase):
    """What to set a dumb mixing valve to, and why.

    Item 29 asks the integration to *recommend* a setting for a valve it
    cannot command. The number alone would invite blind trust, so the
    attributes carry the reasoning and what it costs — a target at the
    comfort ceiling gives up the valve's own overshoot protection. Unknown
    unless a mixing valve mode is configured.
    """

    _attr_icon = "mdi:valve"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry,
            "valve_target_recommendation", "Valve Target Recommendation",
        )

    @property
    def native_value(self) -> float | None:
        rec = (self.coordinator.data or {}).get("valve_target_recommendation")
        return rec.get("target") if isinstance(rec, dict) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        rec = data.get("valve_target_recommendation")
        if not isinstance(rec, dict):
            return {}
        return {
            "reason": rec.get("reason"),
            "configured_target": rec.get("configured_target"),
            "mixing_valve_mode": data.get("mixing_valve_mode"),
            "price_ratio": rec.get("price_ratio"),
        }


class ComfortWeightSensor(HeatPumpOptimizerSensorBase):
    """The comfort weight actually in force, learned or configured.

    An invisible self-adjusting objective would be alarming, so the learned
    value, the configured value and the evidence behind the difference are all
    published, and a button resets it.
    """

    _attr_icon = "mdi:scale-balance"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "comfort_weight", "Comfort Weight")

    @property
    def native_value(self) -> float | None:
        value = (self.coordinator.data or {}).get("comfort_weight")
        return round(value, 2) if isinstance(value, (int, float)) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return dict((self.coordinator.data or {}).get("comfort_learning", {}) or {})


class ContractComparisonSensor(HeatPumpOptimizerSensorBase):
    """This month's consumption settled under each contract type (#23).

    The state is the load-profile value: how many SEK/kWh below the month's
    flat-consumer average the optimizer's shifting lands. A household on
    monthly-average spot gains nothing from hourly shifting, and this sensor
    is the proof, either way — which is why the per-contract totals ride
    along as attributes.
    """

    _attr_icon = "mdi:file-compare"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "SEK/kWh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator, entry, "contract_comparison", "Contract Comparison"
        )

    @property
    def native_value(self) -> float | None:
        data = (self.coordinator.data or {}).get("contract_comparison") or {}
        value = data.get("load_profile_value_per_kwh")
        return value if isinstance(value, (int, float)) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return dict(
            (self.coordinator.data or {}).get("contract_comparison", {}) or {}
        )
