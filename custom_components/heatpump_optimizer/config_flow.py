"""Config flow for Heat Pump Cost Optimizer integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.translation import async_get_translations

from .const import (
    DOMAIN,
    CONFIG_ENTRY_VERSION,
    CONF_TIBBER_TOKEN,
    CONF_WEATHER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_SOLAR_FORECAST_SOURCE,
    CONF_SOLAR_LOCATION,
    DEFAULT_SOLAR_FORECAST_SOURCE,
    SOLAR_SOURCES,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_BUFFER_MAX_TEMP,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_MODE,
    CONF_MIXING_VALVE_TARGET,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    DEFAULT_BUFFER_MAX_TEMP,
    DEFAULT_MIXING_VALVE_TARGET,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_ECL110_COMMAND_TOPIC,
    CONF_ECL110_DISPLACE_SET_TOPIC,
    CONF_ECL110_STATE_TOPIC,
    CONF_ECL110_QOS,
    CONF_ECL110_RETAIN,
    CONF_ECL110_DISPLACE_MIN,
    CONF_ECL110_DISPLACE_MAX,
    CONF_ECL110_PID_TIME_CONSTANT,
    CONF_TARGET_TEMP,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_COMFORT_TEMP_DAY,
    CONF_COMFORT_TEMP_NIGHT,
    CONF_DAY_START_HOUR,
    CONF_DAY_END_HOUR,
    CONF_HOUSE_THERMAL_MASS,
    CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
    CONF_SLAB_THERMAL_MASS,
    CONF_SLAB_HEAT_TRANSFER,
    CONF_HEAT_PUMP_COP_NOMINAL,
    CONF_HEAT_PUMP_MAX_POWER,
    CONF_HEAT_PUMP_MIN_POWER,
    CONF_UPPER_FLOOR_THERMAL_MASS,
    CONF_LOWER_FLOOR_THERMAL_MASS,
    CONF_UPPER_FLOOR_HEAT_LOSS,
    CONF_LOWER_FLOOR_HEAT_LOSS,
    CONF_INTER_ZONE_TRANSFER,
    CONF_RADIATOR_POWER_FRACTION,
    CONF_UPPER_FLOOR_AREA_RATIO,
    CONF_BUFFER_TANK_VOLUME,
    CONF_WINDOW_AREA,
    CONF_SOLAR_ORIENTATION_FACTOR,
    CONF_SOLAR_HEAT_GAIN_COEFF,
    CONF_DHW_TANK_VOLUME,
    CONF_DHW_SETPOINT,
    CONF_DHW_MIN_TEMP,
    CONF_DHW_DAILY_CONSUMPTION,
    CONF_DHW_COOLING_RATE,
    CONF_DHW_SCHEDULE_ENABLED,
    CONF_DHW_WINDOWS,
    CONF_DHW_IDLE_MIN_TEMP,
    CONF_DHW_LEGIONELLA_ENABLED,
    CONF_DHW_LEGIONELLA_TEMP,
    CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
    CONF_WIND_SENSITIVITY,
    CONF_RAIN_HEAT_LOSS_MULTIPLIER,
    CONF_OPTIMIZATION_INTERVAL,
    CONF_PRICE_WEIGHT,
    CONF_COMFORT_WEIGHT,
    DEFAULT_TARGET_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_HOUSE_THERMAL_MASS,
    DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
    DEFAULT_SLAB_THERMAL_MASS,
    DEFAULT_SLAB_HEAT_TRANSFER,
    DEFAULT_HEAT_PUMP_COP_NOMINAL,
    DEFAULT_HEAT_PUMP_MAX_POWER,
    DEFAULT_HEAT_PUMP_MIN_POWER,
    DEFAULT_UPPER_FLOOR_THERMAL_MASS,
    DEFAULT_LOWER_FLOOR_THERMAL_MASS,
    DEFAULT_UPPER_FLOOR_HEAT_LOSS,
    DEFAULT_LOWER_FLOOR_HEAT_LOSS,
    DEFAULT_INTER_ZONE_TRANSFER,
    DEFAULT_RADIATOR_POWER_FRACTION,
    DEFAULT_UPPER_FLOOR_AREA_RATIO,
    DEFAULT_BUFFER_TANK_VOLUME,
    DEFAULT_WINDOW_AREA,
    DEFAULT_SOLAR_ORIENTATION_FACTOR,
    DEFAULT_SOLAR_HEAT_GAIN_COEFF,
    DEFAULT_DHW_TANK_VOLUME,
    DEFAULT_DHW_SETPOINT,
    DEFAULT_DHW_MIN_TEMP,
    DHW_MIN_TEMP_SETPOINT_MARGIN,
    DEFAULT_DHW_DAILY_CONSUMPTION,
    DEFAULT_DHW_COOLING_RATE,
    DEFAULT_DHW_SCHEDULE_ENABLED,
    DEFAULT_DHW_WINDOWS,
    DEFAULT_DHW_IDLE_MIN_TEMP,
    DEFAULT_DHW_LEGIONELLA_ENABLED,
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
    DEFAULT_ECL110_COMMAND_TOPIC,
    DEFAULT_ECL110_DISPLACE_SET_TOPIC,
    DEFAULT_ECL110_STATE_TOPIC,
    DEFAULT_ECL110_QOS,
    DEFAULT_ECL110_RETAIN,
    DEFAULT_ECL110_DISPLACE_MIN,
    DEFAULT_ECL110_DISPLACE_MAX,
    DEFAULT_ECL110_PID_TIME_CONSTANT,
    DEFAULT_WIND_SENSITIVITY,
    DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_COMFORT_WEIGHT,
    # Added in v2.8.0
    CONF_POWER_ENTITY,
    CONF_ENERGY_ENTITY,
    CONF_HOUSE_POWER_ENTITY,
    CONF_STALENESS_ENABLED,
    CONF_STALENESS_SCALE,
    DEFAULT_STALENESS_ENABLED,
    DEFAULT_STALENESS_SCALE,
    STALENESS_SCALE_MIN,
    STALENESS_SCALE_MAX,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_EXTERNAL_HEAT_MIN_RISE,
    CONF_EXTERNAL_HEAT_DECAY_MINUTES,
    DEFAULT_EXTERNAL_HEAT_ENABLED,
    DEFAULT_EXTERNAL_HEAT_MIN_RISE,
    DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_WOOD_TANK_VOLUME,
    CONF_PRICE_PRIOR_ENABLED,
    DEFAULT_PRICE_PRIOR_ENABLED,
    CONF_PEAK_TARIFF_ENABLED,
    CONF_PEAK_TARIFF_PRICE,
    CONF_PEAK_TARIFF_COUNT,
    CONF_PEAK_TARIFF_WINDOW,
    DEFAULT_PEAK_TARIFF_ENABLED,
    DEFAULT_PEAK_TARIFF_PRICE,
    DEFAULT_PEAK_TARIFF_COUNT,
    DEFAULT_PEAK_TARIFF_WINDOW,
    CONF_CYCLING_COST,
    DEFAULT_CYCLING_COST,
    CONF_PV_ENABLED,
    CONF_PV_PEAK_KW,
    CONF_PV_EFFICIENCY,
    CONF_PV_EXPORT_PRICE,
    CONF_PV_EXPORT_PRICE_ENTITY,
    CONF_PV_PRODUCTION_ENTITY,
    DEFAULT_PV_ENABLED,
    DEFAULT_PV_PEAK_KW,
    DEFAULT_PV_EFFICIENCY,
    DEFAULT_PV_EXPORT_PRICE,
    CONF_AWAY_ENABLED,
    CONF_AWAY_PRESENCE_ENTITY,
    CONF_AWAY_RETURN_ENTITY,
    CONF_AWAY_TEMPERATURE,
    CONF_AWAY_DHW_MIN_TEMP,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_AWAY_TEMPERATURE,
    DEFAULT_AWAY_DHW_MIN_TEMP,
    CONF_SYSID_ENABLED,
    DEFAULT_SYSID_ENABLED,
    CONF_COMFORT_LEARNING_ENABLED,
    DEFAULT_COMFORT_LEARNING_ENABLED,
    CONF_BUILDING_PRESET_ENABLED,
    CONF_BUILDING_STRUCTURE,
    CONF_BUILDING_ERA,
    CONF_BUILDING_FOUNDATION,
    CONF_HEATED_AREA,
    CONF_UPPER_EMITTER,
    CONF_LOWER_EMITTER,
    DEFAULT_BUILDING_PRESET_ENABLED,
    DEFAULT_HEATED_AREA,
)
from . import mixing_valve, presets
from .dhw_schedule import is_valid_spec

_LOGGER = logging.getLogger(__name__)

TIBBER_API_URL = "https://api.tibber.com/v1-beta/gql"


async def validate_tibber_token(token: str) -> bool:
    """Validate the Tibber API token."""
    query = '{ "query": "{ viewer { name } }" }'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TIBBER_API_URL, data=query, headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return "errors" not in data
                return False
    except Exception:
        return False


def _number(
    minimum: float,
    maximum: float,
    step: float,
    unit: str | None = None,
    *,
    slider: bool = False,
) -> selector.NumberSelector:
    """A numeric field.

    The nested ``NumberSelector(NumberSelectorConfig(...))`` construction
    appeared eighty-two times in this file; collapsing it makes each field one
    readable line, so a form reads as a list of settings rather than as a wall
    of constructor calls.
    """
    config: dict[str, Any] = {
        "min": minimum,
        "max": maximum,
        "step": step,
        "mode": (
            selector.NumberSelectorMode.SLIDER
            if slider
            else selector.NumberSelectorMode.BOX
        ),
    }
    if unit is not None:
        config["unit_of_measurement"] = unit
    return selector.NumberSelector(selector.NumberSelectorConfig(**config))


def _temperature(
    minimum: float, maximum: float, step: float = 0.5, *, slider: bool = True
) -> selector.NumberSelector:
    """A temperature in degrees Celsius."""
    return _number(minimum, maximum, step, "°C", slider=slider)


def _dhw_min_too_close(candidate: dict[str, Any], current: dict[str, Any]) -> bool:
    """Whether the effective DHW minimum leaves no deadband below the setpoint.

    The apply_schedule service and the card already enforce this margin; a form
    that lets the same pair through would store the one configuration the
    solver cannot express — the tank limits are soft penalties, so an
    impossible minimum is not rejected downstream, the plan just sits in
    permanent slight violation.
    """
    setpoint = candidate.get(
        CONF_DHW_SETPOINT, current.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT)
    )
    minimum = candidate.get(
        CONF_DHW_MIN_TEMP, current.get(CONF_DHW_MIN_TEMP, DEFAULT_DHW_MIN_TEMP)
    )
    return float(minimum) > float(setpoint) - DHW_MIN_TEMP_SETPOINT_MARGIN


def _entity_of(
    domain: str | list[str], device_class: str | None = None
) -> selector.EntitySelector:
    """An entity picker, optionally narrowed to a device class.

    The filter is expressed under ``filter`` rather than as top-level
    ``domain``/``device_class`` keys. Those top-level keys are the legacy form:
    Home Assistant still accepts them, but the frontend reads only ``filter``
    when it decides which entities match and which helper types the picker may
    offer to create. With the legacy form the "create helper" shortcut cannot
    resolve a single helper domain, and submits the creation without a name —
    which surfaces to the user as "required key not provided @ data['name']".
    """
    entity_filter: dict[str, Any] = {
        "domain": [domain] if isinstance(domain, str) else list(domain)
    }
    if device_class is not None:
        entity_filter["device_class"] = [device_class]
    return selector.EntitySelector(
        selector.EntitySelectorConfig(filter=[entity_filter])
    )


def _select(options: list[str], translation_key: str) -> selector.SelectSelector:
    """A dropdown of fixed options with a translation key for its labels."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=options,
            translation_key=translation_key,
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _solar_source_selector() -> selector.SelectSelector:
    """Where irradiance comes from.

    Kept as an explicit choice rather than "use Open-Meteo when no sensor
    exists": silently calling an external API on a user's behalf is not a
    decision an integration should make for them.
    """
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=list(SOLAR_SOURCES),
            translation_key="solar_forecast_source",
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _solar_location_selector() -> selector.LocationSelector:
    """Map picker for the irradiance coordinate."""
    return selector.LocationSelector(selector.LocationSelectorConfig(radius=False))


def _default_location(hass: HomeAssistant, current: dict[str, Any]) -> dict[str, float]:
    """Pre-fill the map with the configured point, else the HA home location."""
    existing = current.get(CONF_SOLAR_LOCATION)
    if isinstance(existing, dict) and "latitude" in existing:
        return existing
    return {
        "latitude": hass.config.latitude,
        "longitude": hass.config.longitude,
    }


class HeatPumpOptimizerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Heat Pump Optimizer."""

    VERSION = CONFIG_ENTRY_VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step — API credentials and entity selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if not await validate_tibber_token(user_input[CONF_TIBBER_TOKEN]):
                errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
            else:
                self._data.update(user_input)
                return await self.async_step_temperature()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Heat Pump Optimizer"): str,
                    vol.Required(CONF_TIBBER_TOKEN): str,
                    vol.Required(CONF_WEATHER_ENTITY): _entity_of("weather"),
                    vol.Optional(CONF_INDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_OUTDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_HEAT_PUMP_SWITCH_ENTITY): _entity_of("switch"),
                    vol.Optional(CONF_SOLAR_RADIATION_ENTITY): _entity_of("sensor"),
                    vol.Optional(
                        CONF_SOLAR_FORECAST_SOURCE,
                        default=DEFAULT_SOLAR_FORECAST_SOURCE,
                    ): _solar_source_selector(),
                    vol.Optional(
                        CONF_SOLAR_LOCATION,
                        default=_default_location(self.hass, {}),
                    ): _solar_location_selector(),
                    vol.Optional(CONF_FLOOR_RETURN_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_LOWER_FLOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_DHW_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(
                        CONF_BUFFER_TANK_TEMP_ENTITY
                    ): _entity_of("sensor", "temperature"),
                    vol.Optional(
                        CONF_ECL110_DISPLACE_SET_TOPIC,
                        default=DEFAULT_ECL110_DISPLACE_SET_TOPIC,
                    ): str,
                    vol.Optional(
                        CONF_ECL110_COMMAND_TOPIC,
                        default=DEFAULT_ECL110_COMMAND_TOPIC,
                    ): str,
                    vol.Optional(
                        CONF_ECL110_STATE_TOPIC,
                        default=DEFAULT_ECL110_STATE_TOPIC,
                    ): str,
                    vol.Optional(
                        CONF_ECL110_QOS,
                        default=DEFAULT_ECL110_QOS,
                    ): _number(0, 2, 1, slider=True),
                    vol.Optional(
                        CONF_ECL110_RETAIN,
                        default=DEFAULT_ECL110_RETAIN,
                    ): bool,
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MIN,
                        default=DEFAULT_ECL110_DISPLACE_MIN,
                    ): _number(-30, 0, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MAX,
                        default=DEFAULT_ECL110_DISPLACE_MAX,
                    ): _number(0, 30, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_PID_TIME_CONSTANT,
                        default=DEFAULT_ECL110_PID_TIME_CONSTANT,
                    ): _number(0.25, 6.0, 0.25, "h"),
                }
            ),
            errors=errors,
            description_placeholders={
                "tibber_info": "Get your token from https://developer.tibber.com",
            },
        )

    async def async_step_temperature(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle temperature configuration step."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_thermal()

        return self.async_show_form(
            step_id="temperature",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP
                    ): _number(15, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP
                    ): _number(14, 25, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP
                    ): _number(18, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_DAY, default=DEFAULT_COMFORT_TEMP_DAY
                    ): _number(16, 26, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_NIGHT, default=DEFAULT_COMFORT_TEMP_NIGHT
                    ): _number(15, 24, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_DAY_START_HOUR, default=DEFAULT_DAY_START_HOUR
                    ): _number(0, 12, 1, slider=True),
                    vol.Required(
                        CONF_DAY_END_HOUR, default=DEFAULT_DAY_END_HOUR
                    ): _number(18, 23, 1, slider=True),
                }
            ),
        )

    async def async_step_thermal(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle thermal model configuration step."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_zones()

        return self.async_show_form(
            step_id="thermal",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOUSE_THERMAL_MASS, default=DEFAULT_HOUSE_THERMAL_MASS
                    ): _number(2, 50, 0.5, "kWh/°C"),
                    vol.Required(
                        CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
                        default=DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
                    ): _number(0.05, 1.0, 0.01, "kW/°C"),
                    vol.Required(
                        CONF_SLAB_THERMAL_MASS, default=DEFAULT_SLAB_THERMAL_MASS
                    ): _number(1, 30, 0.5, "kWh/°C"),
                    vol.Required(
                        CONF_SLAB_HEAT_TRANSFER, default=DEFAULT_SLAB_HEAT_TRANSFER
                    ): _number(0.1, 5.0, 0.1, "kW/°C"),
                    vol.Required(
                        CONF_HEAT_PUMP_COP_NOMINAL,
                        default=DEFAULT_HEAT_PUMP_COP_NOMINAL,
                    ): _number(1.5, 6.0, 0.1),
                    vol.Required(
                        CONF_HEAT_PUMP_MAX_POWER, default=DEFAULT_HEAT_PUMP_MAX_POWER
                    ): _number(1, 20, 0.5, "kW"),
                    vol.Required(
                        CONF_HEAT_PUMP_MIN_POWER, default=DEFAULT_HEAT_PUMP_MIN_POWER
                    ): _number(0, 10, 0.5, "kW"),
                    vol.Required(
                        CONF_OPTIMIZATION_INTERVAL,
                        default=DEFAULT_OPTIMIZATION_INTERVAL,
                    ): _number(10, 120, 5, "min", slider=True),
                    vol.Required(
                        CONF_PRICE_WEIGHT, default=DEFAULT_PRICE_WEIGHT
                    ): _number(0.1, 10, 0.1),
                    vol.Required(
                        CONF_COMFORT_WEIGHT, default=DEFAULT_COMFORT_WEIGHT
                    ): _number(0.1, 20, 0.1),
                }
            ),
        )

    async def async_step_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle two-zone and solar configuration (optional step)."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_dhw()

        return self.async_show_form(
            step_id="zones",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPPER_FLOOR_THERMAL_MASS,
                        default=DEFAULT_UPPER_FLOOR_THERMAL_MASS,
                    ): _number(1, 20, 0.5, "kWh/°C"),
                    vol.Optional(
                        CONF_LOWER_FLOOR_THERMAL_MASS,
                        default=DEFAULT_LOWER_FLOOR_THERMAL_MASS,
                    ): _number(1, 30, 0.5, "kWh/°C"),
                    vol.Optional(
                        CONF_UPPER_FLOOR_HEAT_LOSS,
                        default=DEFAULT_UPPER_FLOOR_HEAT_LOSS,
                    ): _number(0.01, 0.5, 0.01, "kW/°C"),
                    vol.Optional(
                        CONF_LOWER_FLOOR_HEAT_LOSS,
                        default=DEFAULT_LOWER_FLOOR_HEAT_LOSS,
                    ): _number(0.01, 0.5, 0.01, "kW/°C"),
                    vol.Optional(
                        CONF_INTER_ZONE_TRANSFER,
                        default=DEFAULT_INTER_ZONE_TRANSFER,
                    ): _number(0.0, 3.0, 0.1, "kW/°C"),
                    vol.Optional(
                        CONF_RADIATOR_POWER_FRACTION,
                        default=DEFAULT_RADIATOR_POWER_FRACTION,
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_UPPER_FLOOR_AREA_RATIO,
                        default=DEFAULT_UPPER_FLOOR_AREA_RATIO,
                    ): _number(0.1, 0.9, 0.05, slider=True),
                    vol.Optional(
                        CONF_BUFFER_TANK_VOLUME,
                        default=DEFAULT_BUFFER_TANK_VOLUME,
                    ): _number(10, 1500, 5, "L"),
                    vol.Optional(
                        CONF_WINDOW_AREA, default=DEFAULT_WINDOW_AREA
                    ): _number(0, 50, 0.5, "m²"),
                    vol.Optional(
                        CONF_SOLAR_ORIENTATION_FACTOR,
                        default=DEFAULT_SOLAR_ORIENTATION_FACTOR,
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_SOLAR_HEAT_GAIN_COEFF,
                        default=DEFAULT_SOLAR_HEAT_GAIN_COEFF,
                    ): _number(0.1, 1.0, 0.05, slider=True),
                }
            ),
        )

    async def async_step_dhw(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle DHW (Domestic Hot Water) configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not is_valid_spec(user_input.get(CONF_DHW_WINDOWS, "")):
                errors[CONF_DHW_WINDOWS] = "invalid_dhw_windows"
            elif _dhw_min_too_close(user_input, self._data):
                errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
            else:
                self._data.update(user_input)
                return await self.async_step_weather_sensitivity()

        return self.async_show_form(
            step_id="dhw",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DHW_TANK_VOLUME,
                        default=DEFAULT_DHW_TANK_VOLUME,
                    ): _number(50, 1500, 10, "L"),
                    vol.Optional(
                        CONF_DHW_SETPOINT,
                        default=DEFAULT_DHW_SETPOINT,
                    ): _number(40, 65, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_MIN_TEMP,
                        default=DEFAULT_DHW_MIN_TEMP,
                    ): _number(35, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_DAILY_CONSUMPTION,
                        default=DEFAULT_DHW_DAILY_CONSUMPTION,
                    ): _number(50, 1500, 10, "L/day"),
                    vol.Optional(
                        CONF_DHW_COOLING_RATE,
                        default=DEFAULT_DHW_COOLING_RATE,
                    ): _number(0.05, 3.0, 0.05, "°C/h"),
                    vol.Optional(
                        CONF_DHW_SCHEDULE_ENABLED,
                        default=DEFAULT_DHW_SCHEDULE_ENABLED,
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_WINDOWS,
                        default=DEFAULT_DHW_WINDOWS,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_DHW_IDLE_MIN_TEMP,
                        default=DEFAULT_DHW_IDLE_MIN_TEMP,
                    ): _number(10, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_ENABLED,
                        default=DEFAULT_DHW_LEGIONELLA_ENABLED,
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_TEMP,
                        default=DEFAULT_DHW_LEGIONELLA_TEMP,
                    ): _number(55, 70, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                        default=DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
                    ): _number(1, 30, 1, "days", slider=True),
                }
            ),
        )

    async def async_step_weather_sensitivity(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle weather sensitivity configuration step."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data.get(CONF_NAME, "Heat Pump Optimizer"),
                data=self._data,
            )

        return self.async_show_form(
            step_id="weather_sensitivity",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_WIND_SENSITIVITY,
                        default=DEFAULT_WIND_SENSITIVITY,
                    ): _number(0.0, 0.5, 0.01),
                    vol.Optional(
                        CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                        default=DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
                    ): _number(1.0, 1.5, 0.01),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HeatPumpOptimizerOptionsFlow:
        """Get the options flow for this handler."""
        return HeatPumpOptimizerOptionsFlow(config_entry)


class HeatPumpOptimizerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Heat Pump Optimizer.

    The options are split into a menu of focused pages rather than one very
    long form, so that changing a single setting does not mean scrolling past
    forty unrelated fields.
    """

    # Entity fields on the "Sensors and entities" page. A cleared selector is
    # simply absent from ``user_input``, and because options are merged on top
    # of the original setup data, an absent key would silently restore the old
    # entity. These are written back explicitly as ``None`` so clearing them
    # sticks — but only for the fields this page actually renders: nulling the
    # whole roster wiped the PV, away and external-heat entities configured on
    # their own pages every time this one was saved.
    _ENTITIES_PAGE_KEYS = (
        CONF_INDOOR_TEMP_ENTITY,
        CONF_OUTDOOR_TEMP_ENTITY,
        CONF_HEAT_PUMP_SWITCH_ENTITY,
        CONF_SOLAR_RADIATION_ENTITY,
        CONF_FLOOR_RETURN_TEMP_ENTITY,
        CONF_LOWER_FLOOR_TEMP_ENTITY,
        CONF_DHW_TEMP_ENTITY,
        CONF_BUFFER_TANK_TEMP_ENTITY,
        CONF_POWER_ENTITY,
        CONF_ENERGY_ENTITY,
        CONF_HOUSE_POWER_ENTITY,
    )

    # Every clearable entity across all pages; the solar, away, learning and
    # mixing-valve pages clear their own members in their own handlers.
    _OPTIONAL_ENTITY_KEYS = _ENTITIES_PAGE_KEYS + (
        CONF_EXTERNAL_HEAT_ENTITY,
        CONF_VALVE_OUTLET_TEMP_ENTITY,
        CONF_WOOD_TANK_TOP_ENTITY,
        CONF_WOOD_TANK_BOTTOM_ENTITY,
        CONF_MIXING_VALVE_TARGET_ENTITY,
        CONF_PV_PRODUCTION_ENTITY,
        CONF_PV_EXPORT_PRICE_ENTITY,
        CONF_AWAY_PRESENCE_ENTITY,
        CONF_AWAY_RETURN_ENTITY,
    )

    # Fallback labels for the menu, used when the frontend has no translation
    # to show. They double as the definition of which pages the menu offers.
    _MENU_LABELS = {
        "entities": "Sensors and entities",
        "comfort": "Comfort and temperatures",
        "hot_water": "Hot water",
        "building": "House and heating system",
        "building_preset": "Building type and emitters",
        "tuning": "Savings vs comfort",
        "grid": "Grid costs and cycling",
        "solar_pv": "Solar panels",
        "away": "Away and holiday mode",
        "learning": "Self-learning and diagnostics",
        "heat_curve": "Heat curve control (ECL110)",
        "mixing_valve": "Mixing valve and heat storage",
    }

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Assigning to ``self.config_entry`` goes through a property setter that
        # Home Assistant deprecated in 2024.11 and removed in 2025.12, which makes
        # the options flow raise and the frontend report a 500 error. Keep our own
        # reference instead so the flow works on every supported version.
        self._entry = config_entry

    @property
    def _current(self) -> dict[str, Any]:
        """Effective configuration: setup data with saved options applied."""
        return {**self._entry.data, **self._entry.options}

    def _save(self, user_input: dict[str, Any]) -> FlowResult:
        """Persist one page without discarding settings from the other pages."""
        return self.async_create_entry(
            title="", data={**self._entry.options, **user_input}
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=await self._menu_options(),
        )

    async def _menu_options(self) -> dict[str, str]:
        """Menu entries as explicit ``step id -> label`` pairs.

        Passing plain step ids instead would leave the frontend to translate
        them, and it renders an empty row when that lookup comes back empty,
        which shows up as a menu of unreadable blank lines. Supplying the label
        ourselves means the menu is always legible; the translation is still
        used whenever it resolves.
        """
        labels = dict(self._MENU_LABELS)
        try:
            translations = await async_get_translations(
                self.hass, self.hass.config.language, "options", {DOMAIN}
            )
        except Exception:  # noqa: BLE001 - a menu must never fail to render
            _LOGGER.debug("Could not load option menu translations", exc_info=True)
            return labels

        prefix = f"component.{DOMAIN}.options.step.init.menu_options."
        for step_id in labels:
            translated = translations.get(f"{prefix}{step_id}")
            if translated:
                labels[step_id] = translated
        return labels

    async def async_step_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Change which Home Assistant entities the optimizer reads."""
        errors: dict[str, str] = {}
        current = self._current

        if user_input is not None:
            token = user_input.get(CONF_TIBBER_TOKEN)
            if token and token != current.get(CONF_TIBBER_TOKEN):
                if not await validate_tibber_token(token):
                    errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
            if not errors:
                cleaned = dict(user_input)
                for key in self._ENTITIES_PAGE_KEYS:
                    if not cleaned.get(key):
                        cleaned[key] = None
                return self._save(cleaned)
            current = {**current, **user_input}

        def _entity(key: str) -> Any:
            """Optional key that keeps the currently configured entity as default."""
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="entities",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TIBBER_TOKEN,
                        default=current.get(CONF_TIBBER_TOKEN, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                    vol.Required(
                        CONF_WEATHER_ENTITY,
                        default=current.get(CONF_WEATHER_ENTITY, ""),
                    ): _entity_of("weather"),
                    _entity(CONF_INDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_OUTDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_SOLAR_RADIATION_ENTITY): _entity_of("sensor"),
                    vol.Optional(
                        CONF_SOLAR_FORECAST_SOURCE,
                        default=current.get(
                            CONF_SOLAR_FORECAST_SOURCE,
                            DEFAULT_SOLAR_FORECAST_SOURCE,
                        ),
                    ): _solar_source_selector(),
                    vol.Optional(
                        CONF_SOLAR_LOCATION,
                        default=_default_location(self.hass, current),
                    ): _solar_location_selector(),
                    _entity(CONF_DHW_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_BUFFER_TANK_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_FLOOR_RETURN_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_LOWER_FLOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_HEAT_PUMP_SWITCH_ENTITY): _entity_of("switch"),
                    # Measured electrical draw. Optional, and everything that
                    # uses it degrades cleanly without it — but with it, COP
                    # becomes observable, predicted cost gets a realised
                    # counterpart, and the external-heat detector gets its
                    # cleanest signal.
                    _entity(CONF_POWER_ENTITY): _entity_of("sensor", "power"),
                    _entity(CONF_ENERGY_ENTITY): _entity_of("sensor", "energy"),
                    # Whole-house load. The capacity tariff is metered at the
                    # connection point, not at the heat pump, so without this
                    # the peak model only sees part of the picture.
                    _entity(CONF_HOUSE_POWER_ENTITY): _entity_of("sensor", "power"),
                }
            ),
        )

    async def async_step_comfort(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """How warm the house should be, and when."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="comfort",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TARGET_TEMP,
                        default=current.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
                    ): _number(15, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MIN_TEMP,
                        default=current.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP),
                    ): _number(14, 25, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MAX_TEMP,
                        default=current.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP),
                    ): _number(18, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_DAY,
                        default=current.get(
                            CONF_COMFORT_TEMP_DAY, DEFAULT_COMFORT_TEMP_DAY
                        ),
                    ): _number(16, 26, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_NIGHT,
                        default=current.get(
                            CONF_COMFORT_TEMP_NIGHT, DEFAULT_COMFORT_TEMP_NIGHT
                        ),
                    ): _number(15, 24, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_DAY_START_HOUR,
                        default=current.get(
                            CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR
                        ),
                    ): _number(0, 12, 1, slider=True),
                    vol.Required(
                        CONF_DAY_END_HOUR,
                        default=current.get(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR),
                    ): _number(18, 23, 1, slider=True),
                }
            ),
        )

    async def async_step_hot_water(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """When hot water is needed and how hot it has to be."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not is_valid_spec(user_input.get(CONF_DHW_WINDOWS, "")):
                errors[CONF_DHW_WINDOWS] = "invalid_dhw_windows"
            elif _dhw_min_too_close(user_input, self._current):
                errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
            else:
                return self._save(user_input)

        current = self._current
        if user_input is not None:
            current = {**current, **user_input}

        return self.async_show_form(
            step_id="hot_water",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DHW_SCHEDULE_ENABLED,
                        default=current.get(
                            CONF_DHW_SCHEDULE_ENABLED, DEFAULT_DHW_SCHEDULE_ENABLED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_WINDOWS,
                        default=current.get(CONF_DHW_WINDOWS, DEFAULT_DHW_WINDOWS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_DHW_MIN_TEMP,
                        default=current.get(CONF_DHW_MIN_TEMP, DEFAULT_DHW_MIN_TEMP),
                    ): _number(35, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_IDLE_MIN_TEMP,
                        default=current.get(
                            CONF_DHW_IDLE_MIN_TEMP, DEFAULT_DHW_IDLE_MIN_TEMP
                        ),
                    ): _number(10, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_SETPOINT,
                        default=current.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT),
                    ): _number(40, 65, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_TANK_VOLUME,
                        default=current.get(
                            CONF_DHW_TANK_VOLUME, DEFAULT_DHW_TANK_VOLUME
                        ),
                    ): _number(50, 1500, 10, "L"),
                    vol.Optional(
                        CONF_DHW_DAILY_CONSUMPTION,
                        default=current.get(
                            CONF_DHW_DAILY_CONSUMPTION, DEFAULT_DHW_DAILY_CONSUMPTION
                        ),
                    ): _number(50, 1500, 10, "L/day"),
                    vol.Optional(
                        CONF_DHW_COOLING_RATE,
                        default=current.get(
                            CONF_DHW_COOLING_RATE, DEFAULT_DHW_COOLING_RATE
                        ),
                    ): _number(0.05, 3.0, 0.05, "°C/h"),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_ENABLED,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_ENABLED,
                            DEFAULT_DHW_LEGIONELLA_ENABLED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_TEMP,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_TEMP, DEFAULT_DHW_LEGIONELLA_TEMP
                        ),
                    ): _number(55, 70, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                            DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
                        ),
                    ): _number(1, 30, 1, "days", slider=True),
                }
            ),
        )

    async def async_step_building(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Physical properties of the house and heating system."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="building",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BUFFER_TANK_VOLUME,
                        default=current.get(
                            CONF_BUFFER_TANK_VOLUME, DEFAULT_BUFFER_TANK_VOLUME
                        ),
                    ): _number(10, 1500, 5, "L"),
                    vol.Optional(
                        CONF_RADIATOR_POWER_FRACTION,
                        default=current.get(
                            CONF_RADIATOR_POWER_FRACTION,
                            DEFAULT_RADIATOR_POWER_FRACTION,
                        ),
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_WINDOW_AREA,
                        default=current.get(CONF_WINDOW_AREA, DEFAULT_WINDOW_AREA),
                    ): _number(0, 50, 0.5, "m²"),
                    vol.Optional(
                        CONF_SOLAR_HEAT_GAIN_COEFF,
                        default=current.get(
                            CONF_SOLAR_HEAT_GAIN_COEFF,
                            DEFAULT_SOLAR_HEAT_GAIN_COEFF,
                        ),
                    ): _number(0.1, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_WIND_SENSITIVITY,
                        default=current.get(
                            CONF_WIND_SENSITIVITY, DEFAULT_WIND_SENSITIVITY
                        ),
                    ): _number(0.0, 0.5, 0.01),
                    vol.Optional(
                        CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                        default=current.get(
                            CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                            DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
                        ),
                    ): _number(1.0, 1.5, 0.01),
                }
            ),
        )

    async def async_step_tuning(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Balance between saving money and holding the setpoint."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="tuning",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PRICE_WEIGHT,
                        default=current.get(CONF_PRICE_WEIGHT, DEFAULT_PRICE_WEIGHT),
                    ): _number(0.1, 10, 0.1),
                    vol.Required(
                        CONF_COMFORT_WEIGHT,
                        default=current.get(
                            CONF_COMFORT_WEIGHT, DEFAULT_COMFORT_WEIGHT
                        ),
                    ): _number(0.1, 20, 0.1),
                    vol.Required(
                        CONF_OPTIMIZATION_INTERVAL,
                        default=current.get(
                            CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                        ),
                    ): _number(10, 120, 5, "min", slider=True),
                }
            ),
        )

    async def async_step_mixing_valve(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Mixing valve, and whether the buffer tank can be used as a store."""
        if user_input is not None:
            cleaned = dict(user_input)
            # This page's own clearable entity, mirroring the solar/away/
            # learning pages: an absent selector must be written back as None
            # or clearing it silently restores the old entity.
            if not cleaned.get(CONF_MIXING_VALVE_TARGET_ENTITY):
                cleaned[CONF_MIXING_VALVE_TARGET_ENTITY] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            """Optional key that keeps the currently configured entity as default."""
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="mixing_valve",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MIXING_VALVE_MODE,
                        default=current.get(
                            CONF_MIXING_VALVE_MODE, mixing_valve.MODE_NONE
                        ),
                    ): _select(
                        list(mixing_valve.SELECTABLE_MODES), "mixing_valve_mode"
                    ),
                    # 0 means "use the top of the comfort band", which is also
                    # what a dumb valve is recommended to be set to.
                    vol.Optional(
                        CONF_MIXING_VALVE_TARGET,
                        default=current.get(
                            CONF_MIXING_VALVE_TARGET, DEFAULT_MIXING_VALVE_TARGET
                        ),
                    ): _number(0, 30, 0.5, "°C"),
                    _entity(CONF_MIXING_VALVE_TARGET_ENTITY): _entity_of(
                        "sensor", "temperature"
                    ),
                    vol.Optional(
                        CONF_BUFFER_MAX_TEMP,
                        default=current.get(
                            CONF_BUFFER_MAX_TEMP, DEFAULT_BUFFER_MAX_TEMP
                        ),
                    ): _number(40, 90, 1, "°C", slider=True),
                }
            ),
        )

    async def async_step_heat_curve(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Danfoss ECL110 heat-curve offset control over MQTT."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="heat_curve",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ECL110_DISPLACE_SET_TOPIC,
                        default=current.get(
                            CONF_ECL110_DISPLACE_SET_TOPIC,
                            DEFAULT_ECL110_DISPLACE_SET_TOPIC,
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_COMMAND_TOPIC,
                        default=current.get(
                            CONF_ECL110_COMMAND_TOPIC, DEFAULT_ECL110_COMMAND_TOPIC
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_STATE_TOPIC,
                        default=current.get(
                            CONF_ECL110_STATE_TOPIC, DEFAULT_ECL110_STATE_TOPIC
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_QOS,
                        default=current.get(CONF_ECL110_QOS, DEFAULT_ECL110_QOS),
                    ): _number(0, 2, 1, slider=True),
                    vol.Optional(
                        CONF_ECL110_RETAIN,
                        default=current.get(CONF_ECL110_RETAIN, DEFAULT_ECL110_RETAIN),
                    ): bool,
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MIN,
                        default=current.get(
                            CONF_ECL110_DISPLACE_MIN, DEFAULT_ECL110_DISPLACE_MIN
                        ),
                    ): _number(-30, 0, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MAX,
                        default=current.get(
                            CONF_ECL110_DISPLACE_MAX, DEFAULT_ECL110_DISPLACE_MAX
                        ),
                    ): _number(0, 30, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_PID_TIME_CONSTANT,
                        default=current.get(
                            CONF_ECL110_PID_TIME_CONSTANT,
                            DEFAULT_ECL110_PID_TIME_CONSTANT,
                        ),
                    ): _number(0.25, 6.0, 0.25, "h"),
                }
            ),
        )

    # ------------------------------------------------------------------
    # Option pages added in v2.8.0
    # ------------------------------------------------------------------

    async def async_step_building_preset(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Describe the building in terms a homeowner can actually answer.

        The numeric thermal page asks for kWh/°C, which nobody knows. This page
        asks what the house is made of, roughly when it was built and what the
        heat comes out of, then derives the physics. Enabling it overwrites the
        numeric values on the *House and heating system* page, which stays
        available for anyone with a real energy declaration.
        """
        current = self._current
        if user_input is not None:
            saved = dict(user_input)
            if saved.get(CONF_BUILDING_PRESET_ENABLED):
                preset = presets.BuildingPreset(
                    structure=saved.get(CONF_BUILDING_STRUCTURE, ""),
                    era=saved.get(CONF_BUILDING_ERA, ""),
                    foundation=saved.get(CONF_BUILDING_FOUNDATION, ""),
                    heated_area_m2=float(
                        saved.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA)
                    ),
                    upper_emitter=saved.get(CONF_UPPER_EMITTER, ""),
                    lower_emitter=saved.get(CONF_LOWER_EMITTER, ""),
                    upper_area_ratio=float(
                        current.get(
                            CONF_UPPER_FLOOR_AREA_RATIO,
                            DEFAULT_UPPER_FLOOR_AREA_RATIO,
                        )
                    ),
                    two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),
                )
                derived = presets.derive(preset)
                # The derived response time is informational; it is not a
                # thermal parameter and would be rejected by the model.
                derived.pop("heating_response_hours", None)
                saved.update(derived)
            return self._save(saved)

        return self.async_show_form(
            step_id="building_preset",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BUILDING_PRESET_ENABLED,
                        default=current.get(
                            CONF_BUILDING_PRESET_ENABLED,
                            DEFAULT_BUILDING_PRESET_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_BUILDING_STRUCTURE,
                        default=current.get(
                            CONF_BUILDING_STRUCTURE, presets.STRUCTURE_TIMBER_SLAB
                        ),
                    ): _select(list(presets.STRUCTURES), "building_structure"),
                    vol.Optional(
                        CONF_BUILDING_ERA,
                        default=current.get(CONF_BUILDING_ERA, presets.ERA_1980_2005),
                    ): _select(list(presets.ERAS), "building_era"),
                    vol.Optional(
                        CONF_BUILDING_FOUNDATION,
                        default=current.get(
                            CONF_BUILDING_FOUNDATION, presets.FOUNDATION_NONE
                        ),
                    ): _select(list(presets.FOUNDATIONS), "building_foundation"),
                    vol.Optional(
                        CONF_HEATED_AREA,
                        default=current.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA),
                    ): _number(20, 1000, 5, "m²"),
                    vol.Optional(
                        CONF_UPPER_EMITTER,
                        default=current.get(
                            CONF_UPPER_EMITTER, presets.EMITTER_RADIATORS
                        ),
                    ): _select(list(presets.EMITTERS), "emitter"),
                    vol.Optional(
                        CONF_LOWER_EMITTER,
                        default=current.get(CONF_LOWER_EMITTER, presets.EMITTER_FLOOR),
                    ): _select(list(presets.EMITTERS), "emitter"),
                }
            ),
        )

    async def async_step_grid(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Capacity tariff, compressor cycling and the price prior."""
        if user_input is not None:
            cleaned = dict(user_input)
            # The dropdown speaks strings; everything downstream treats the
            # window as a number of minutes. Convert once, here, so the stored
            # value has the type the rest of the integration expects.
            window = cleaned.get(CONF_PEAK_TARIFF_WINDOW)
            if window is not None:
                try:
                    cleaned[CONF_PEAK_TARIFF_WINDOW] = int(window)
                except (TypeError, ValueError):
                    cleaned[CONF_PEAK_TARIFF_WINDOW] = DEFAULT_PEAK_TARIFF_WINDOW
            return self._save(cleaned)

        current = self._current
        return self.async_show_form(
            step_id="grid",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PEAK_TARIFF_ENABLED,
                        default=current.get(
                            CONF_PEAK_TARIFF_ENABLED, DEFAULT_PEAK_TARIFF_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PEAK_TARIFF_PRICE,
                        default=current.get(
                            CONF_PEAK_TARIFF_PRICE, DEFAULT_PEAK_TARIFF_PRICE
                        ),
                    ): _number(0, 500, 1),
                    vol.Optional(
                        CONF_PEAK_TARIFF_COUNT,
                        default=current.get(
                            CONF_PEAK_TARIFF_COUNT, DEFAULT_PEAK_TARIFF_COUNT
                        ),
                    ): _number(1, 10, 1, slider=True),
                    vol.Optional(
                        CONF_PEAK_TARIFF_WINDOW,
                        # The selector's options are strings, so the default
                        # must be one too. An int default is returned verbatim
                        # when the field is left untouched, and SelectSelector
                        # rejects it with "expected str" — which made the
                        # already-selected option the one that could not be
                        # submitted.
                        default=str(
                            current.get(
                                CONF_PEAK_TARIFF_WINDOW, DEFAULT_PEAK_TARIFF_WINDOW
                            )
                        ),
                    ): _select(["15", "60"], "peak_window"),
                    vol.Optional(
                        CONF_CYCLING_COST,
                        default=current.get(CONF_CYCLING_COST, DEFAULT_CYCLING_COST),
                    ): _number(0, 10, 0.05),
                    vol.Optional(
                        CONF_PRICE_PRIOR_ENABLED,
                        default=current.get(
                            CONF_PRICE_PRIOR_ENABLED, DEFAULT_PRICE_PRIOR_ENABLED
                        ),
                    ): bool,
                }
            ),
        )

    async def async_step_solar_pv(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Photovoltaic array and export economics."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (CONF_PV_PRODUCTION_ENTITY, CONF_PV_EXPORT_PRICE_ENTITY):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="solar_pv",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PV_ENABLED,
                        default=current.get(CONF_PV_ENABLED, DEFAULT_PV_ENABLED),
                    ): bool,
                    vol.Optional(
                        CONF_PV_PEAK_KW,
                        default=current.get(CONF_PV_PEAK_KW, DEFAULT_PV_PEAK_KW),
                    ): _number(0, 100, 0.1, "kWp"),
                    vol.Optional(
                        CONF_PV_EFFICIENCY,
                        default=current.get(
                            CONF_PV_EFFICIENCY, DEFAULT_PV_EFFICIENCY
                        ),
                    ): _number(0.3, 1.0, 0.01, slider=True),
                    vol.Optional(
                        CONF_PV_EXPORT_PRICE,
                        default=current.get(
                            CONF_PV_EXPORT_PRICE, DEFAULT_PV_EXPORT_PRICE
                        ),
                    ): _number(0, 10, 0.01),
                    _entity(CONF_PV_EXPORT_PRICE_ENTITY): _entity_of("sensor"),
                    _entity(CONF_PV_PRODUCTION_ENTITY): _entity_of("sensor", "power"),
                }
            ),
        )

    async def async_step_away(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Deep setback while the house is empty, with timed recovery."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (CONF_AWAY_PRESENCE_ENTITY, CONF_AWAY_RETURN_ENTITY):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="away",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_AWAY_ENABLED,
                        default=current.get(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED),
                    ): bool,
                    _entity(CONF_AWAY_PRESENCE_ENTITY): _entity_of([ "input_boolean", "person", "device_tracker", "calendar", "binary_sensor", ]),
                    _entity(CONF_AWAY_RETURN_ENTITY): _entity_of(["input_datetime", "sensor"]),
                    vol.Optional(
                        CONF_AWAY_TEMPERATURE,
                        default=current.get(
                            CONF_AWAY_TEMPERATURE, DEFAULT_AWAY_TEMPERATURE
                        ),
                    ): _number(5, 21, 0.5, "°C", slider=True),
                    vol.Optional(
                        CONF_AWAY_DHW_MIN_TEMP,
                        default=current.get(
                            CONF_AWAY_DHW_MIN_TEMP, DEFAULT_AWAY_DHW_MIN_TEMP
                        ),
                    ): _number(10, 55, 1, "°C", slider=True),
                }
            ),
        )

    async def async_step_learning(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Watchdogs and the opt-in learning features."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (
                CONF_EXTERNAL_HEAT_ENTITY,
                CONF_VALVE_OUTLET_TEMP_ENTITY,
                CONF_WOOD_TANK_TOP_ENTITY,
                CONF_WOOD_TANK_BOTTOM_ENTITY,
            ):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="learning",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_STALENESS_ENABLED,
                        default=current.get(
                            CONF_STALENESS_ENABLED, DEFAULT_STALENESS_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_STALENESS_SCALE,
                        default=current.get(
                            CONF_STALENESS_SCALE, DEFAULT_STALENESS_SCALE
                        ),
                    ): _number(STALENESS_SCALE_MIN, STALENESS_SCALE_MAX, 0.5, slider=True),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_ENABLED,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_ENABLED,
                            DEFAULT_EXTERNAL_HEAT_ENABLED,
                        ),
                    ): bool,
                    _entity(CONF_EXTERNAL_HEAT_ENTITY): _entity_of(["binary_sensor", "switch", "input_boolean", "sensor"]),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_MIN_RISE,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_MIN_RISE,
                            DEFAULT_EXTERNAL_HEAT_MIN_RISE,
                        ),
                    ): _number(0.5, 10, 0.1, "°C/h"),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_DECAY_MINUTES,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_DECAY_MINUTES,
                            DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
                        ),
                    ): _number(15, 360, 15, "min", slider=True),
                    # Wood-furnace topology (item 28): the valve outlet is
                    # the sensor that turns the boolean fire into a
                    # continuous displacement; the tank pair bounds how long
                    # the fire can back it.
                    _entity(CONF_VALVE_OUTLET_TEMP_ENTITY): _entity_of(
                        ["sensor"]
                    ),
                    _entity(CONF_WOOD_TANK_TOP_ENTITY): _entity_of(["sensor"]),
                    _entity(CONF_WOOD_TANK_BOTTOM_ENTITY): _entity_of(
                        ["sensor"]
                    ),
                    vol.Optional(
                        CONF_WOOD_TANK_VOLUME,
                        default=current.get(
                            CONF_WOOD_TANK_VOLUME, DEFAULT_WOOD_TANK_VOLUME
                        ),
                    ): _number(50, 3000, 50, "L", slider=True),
                    vol.Optional(
                        CONF_COMFORT_LEARNING_ENABLED,
                        default=current.get(
                            CONF_COMFORT_LEARNING_ENABLED,
                            DEFAULT_COMFORT_LEARNING_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SYSID_ENABLED,
                        default=current.get(
                            CONF_SYSID_ENABLED, DEFAULT_SYSID_ENABLED
                        ),
                    ): bool,
                }
            ),
        )
