"""Heat Pump Cost Optimizer integration for Home Assistant.

This integration optimizes heat pump operation to minimize electricity costs
using Model Predictive Control (MPC). It integrates with Tibber for electricity
prices and Home Assistant weather entities for temperature forecasts.

The optimization accounts for:
- Thermal mass of slab floor heating (slow response)
- Weather-dependent heat loss
- COP variation with outdoor temperature
- Pre-heating before expensive periods
- Temperature setback during expensive periods
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv
from homeassistant.loader import async_get_integration

from .const import (
    DOMAIN,
    CONFIG_ENTRY_VERSION,
    PLATFORMS,
    SERVICE_RUN_OPTIMIZATION,
    SERVICE_SET_MODE,
    SERVICE_SET_THERMAL_PARAMS,
    SERVICE_SIMULATE_PLAN,
    CONF_TIBBER_TOKEN,
    CONF_WEATHER_ENTITY,
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECONOMY,
    MODE_OFF,
    MODE_BOOST,
)
from .coordinator import HeatPumpOptimizerCoordinator
from .frontend import async_register_frontend

_LOGGER = logging.getLogger(__name__)

PLATFORM_LIST = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SWITCH,
]

SERVICE_SCHEMA_RUN_OPTIMIZATION = vol.Schema({})

# What-if simulator (item 21). Every field is optional: the card sends only the
# one the user is dragging, and anything absent keeps its configured value.
SERVICE_SCHEMA_SIMULATE_PLAN = vol.Schema(
    {
        vol.Optional("target_temp"): vol.Coerce(float),
        vol.Optional("min_temp"): vol.Coerce(float),
        vol.Optional("max_temp"): vol.Coerce(float),
        vol.Optional("comfort_temp_day"): vol.Coerce(float),
        vol.Optional("comfort_temp_night"): vol.Coerce(float),
        vol.Optional("comfort_weight"): vol.Coerce(float),
        vol.Optional("dhw_setpoint"): vol.Coerce(float),
        vol.Optional("dhw_min_temperature"): vol.Coerce(float),
        vol.Optional("dhw_windows"): cv.string,
    }
)

SERVICE_SCHEMA_SET_MODE = vol.Schema(
    {
        vol.Required("mode"): vol.In(
            [MODE_AUTO, MODE_COMFORT, MODE_ECONOMY, MODE_OFF, MODE_BOOST]
        ),
    }
)

SERVICE_SCHEMA_SET_THERMAL_PARAMS = vol.Schema(
    {
        vol.Optional("house_thermal_mass"): vol.Coerce(float),
        vol.Optional("house_heat_loss_coefficient"): vol.Coerce(float),
        vol.Optional("slab_thermal_mass"): vol.Coerce(float),
        vol.Optional("slab_heat_transfer"): vol.Coerce(float),
        vol.Optional("heat_pump_cop_nominal"): vol.Coerce(float),
        vol.Optional("upper_floor_thermal_mass"): vol.Coerce(float),
        vol.Optional("lower_floor_thermal_mass"): vol.Coerce(float),
        vol.Optional("inter_zone_heat_transfer"): vol.Coerce(float),
        vol.Optional("radiator_power_fraction"): vol.Coerce(float),
        vol.Optional("window_area"): vol.Coerce(float),
        vol.Optional("solar_heat_gain_coefficient"): vol.Coerce(float),
        # DHW parameters
        vol.Optional("dhw_tank_volume"): vol.Coerce(float),
        vol.Optional("dhw_setpoint"): vol.Coerce(float),
        vol.Optional("dhw_min_temperature"): vol.Coerce(float),
        vol.Optional("dhw_daily_consumption"): vol.Coerce(float),
        vol.Optional("dhw_cooling_rate"): vol.Coerce(float),
        vol.Optional("buffer_cooling_rate"): vol.Coerce(float),
        vol.Optional("dhw_schedule_enabled"): cv.boolean,
        vol.Optional("dhw_windows"): cv.string,
        vol.Optional("dhw_idle_min_temperature"): vol.Coerce(float),
        vol.Optional("dhw_legionella_enabled"): cv.boolean,
        vol.Optional("dhw_legionella_temperature"): vol.Coerce(float),
        vol.Optional("dhw_legionella_interval_days"): vol.Coerce(float),
        # Weather sensitivity parameters
        vol.Optional("wind_sensitivity_factor"): vol.Coerce(float),
        vol.Optional("rain_heat_loss_multiplier"): vol.Coerce(float),
        # ECL110 dynamics parameter
        vol.Optional("ecl110_pid_time_constant_hours"): vol.Coerce(float),
    }
)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate a config entry created by an older version of the integration.

    Every option the integration reads is looked up with a default, so older
    entries only need their version stamped forward. Without this handler Home
    Assistant refuses to load entries created before the current
    ``ConfigFlow.VERSION`` and the integration appears broken after an upgrade.
    """
    if entry.version > CONFIG_ENTRY_VERSION:
        # Downgrade: the entry was written by a newer release than this one.
        _LOGGER.error(
            "Config entry version %s is newer than the supported version %s; "
            "downgrade is not supported",
            entry.version,
            CONFIG_ENTRY_VERSION,
        )
        return False

    if entry.version < CONFIG_ENTRY_VERSION:
        _LOGGER.info(
            "Migrating Heat Pump Optimizer config entry from version %s to %s",
            entry.version,
            CONFIG_ENTRY_VERSION,
        )
        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Heat Pump Optimizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = HeatPumpOptimizerCoordinator(hass, entry)
    try:
        integration = await async_get_integration(hass, DOMAIN)
        coordinator.integration_version = str(integration.version)
    except Exception:  # noqa: BLE001 - version is cosmetic, never block setup
        _LOGGER.debug("Could not resolve integration version", exc_info=True)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Serve and register the Lovelace dashboard card (idempotent; runs once).
    await async_register_frontend(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_LIST)

    # Register services
    async def handle_run_optimization(call: ServiceCall) -> None:
        """Handle the run_optimization service call."""
        _LOGGER.info("Manual optimization triggered via service call")
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_run_optimization()

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle the set_mode service call."""
        mode = call.data["mode"]
        _LOGGER.info("Setting optimizer mode to: %s", mode)
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_set_mode(mode)

    async def handle_set_thermal_params(call: ServiceCall) -> None:
        """Handle the set_thermal_parameters service call."""
        params = dict(call.data)
        _LOGGER.info("Updating thermal parameters: %s", params)
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                await coord.async_update_thermal_params(params)

    async def handle_simulate_plan(call: ServiceCall) -> dict[str, Any]:
        """Price a hypothetical comfort choice without disturbing operation.

        Backs the dashboard card's what-if simulator. Returns a response rather
        than firing an event so the card can await the answer directly, and the
        coordinator rate-limits the underlying solve so that dragging a slider
        cannot trigger one solve per pixel.
        """
        overrides = {k: v for k, v in call.data.items() if v is not None}
        results: dict[str, Any] = {}
        for entry_id, coord in hass.data[DOMAIN].items():
            if isinstance(coord, HeatPumpOptimizerCoordinator):
                results[entry_id] = await coord.async_simulate(overrides)
        return {"results": results}

    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_OPTIMIZATION,
        handle_run_optimization,
        schema=SERVICE_SCHEMA_RUN_OPTIMIZATION,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MODE,
        handle_set_mode,
        schema=SERVICE_SCHEMA_SET_MODE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_THERMAL_PARAMS,
        handle_set_thermal_params,
        schema=SERVICE_SCHEMA_SET_THERMAL_PARAMS,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SIMULATE_PLAN,
        handle_simulate_plan,
        schema=SERVICE_SCHEMA_SIMULATE_PLAN,
        supports_response=SupportsResponse.ONLY,
    )

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORM_LIST)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    # Remove services if no more entries
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_RUN_OPTIMIZATION)
        hass.services.async_remove(DOMAIN, SERVICE_SET_MODE)
        hass.services.async_remove(DOMAIN, SERVICE_SET_THERMAL_PARAMS)
        hass.services.async_remove(DOMAIN, SERVICE_SIMULATE_PLAN)

    return unload_ok
