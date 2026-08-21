"""Data coordinator for Heat Pump Cost Optimizer.

The coordinator manages:
1. Fetching electricity prices from Tibber API
2. Fetching weather forecasts from Home Assistant weather entities
3. Fetching solar radiation, floor return temperature, and DHW temperature
4. Running the MPC optimization (with predictive weather anticipation + DHW)
5. Applying optimization results to heat pump control
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
import numpy as np

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_TIBBER_TOKEN,
    CONF_WEATHER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_HEAT_PUMP_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_DHW_SCHEDULE_ENABLED,
    CONF_DHW_WINDOWS,
    CONF_DHW_IDLE_MIN_TEMP,
    CONF_DHW_COOLING_RATE,
    CONF_DHW_LEGIONELLA_ENABLED,
    CONF_DHW_LEGIONELLA_TEMP,
    CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
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
    CONF_OPTIMIZATION_INTERVAL,
    CONF_PRICE_WEIGHT,
    CONF_COMFORT_WEIGHT,
    CONF_DHW_SETPOINT,
    CONF_DHW_MIN_TEMP,
    CONF_WIND_SENSITIVITY,
    CONF_RAIN_HEAT_LOSS_MULTIPLIER,
    DEFAULT_TARGET_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_COMFORT_WEIGHT,
    DEFAULT_DHW_SETPOINT,
    DEFAULT_DHW_MIN_TEMP,
    DEFAULT_DHW_COOLING_RATE,
    BUFFER_COOLING_RATE_MAX,
    BUFFER_COOLING_RATE_MIN,
    CONF_BUFFER_COOLING_RATE,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    DEFAULT_HOUSE_HEAT_LOSS_SCALE,
    DHW_COOLING_RATE_MIN,
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    DHW_COOLING_RATE_MAX,
    DHW_COOLING_REFERENCE_DELTA,
    DEFAULT_ECL110_COMMAND_TOPIC,
    DEFAULT_ECL110_DISPLACE_SET_TOPIC,
    DEFAULT_ECL110_STATE_TOPIC,
    DEFAULT_ECL110_QOS,
    DEFAULT_ECL110_RETAIN,
    DEFAULT_ECL110_DISPLACE_MIN,
    DEFAULT_ECL110_DISPLACE_MAX,
    DEFAULT_ECL110_PID_TIME_CONSTANT,
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECONOMY,
    MODE_OFF,
    MODE_BOOST,
    UPDATE_INTERVAL_OPTIMIZATION,
    CONF_SOLAR_FORECAST_SOURCE,
    CONF_SOLAR_LOCATION,
    DEFAULT_SOLAR_FORECAST_SOURCE,
    SOLAR_SOURCE_OPEN_METEO,
)
from .open_meteo import OpenMeteoSolar
from .thermal_model import (
    DHW_AMBIENT_TEMP,
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from .dhw_schedule import (
    DHWWindowError,
    format_windows,
    hour_in_windows,
    hours_until_next_window,
    parse_windows,
)
from .optimizer import HeatPumpOptimizer, OptimizationConfig, OptimizationResult

_LOGGER = logging.getLogger(__name__)

TIBBER_API_URL = "https://api.tibber.com/v1-beta/gql"

# Forecast wind speed arrives in whatever unit the user's Home Assistant is
# configured for, so it has to be converted explicitly rather than guessed.
_WIND_UNIT_TO_MS = {
    UnitOfSpeed.METERS_PER_SECOND: 1.0,
    UnitOfSpeed.KILOMETERS_PER_HOUR: 1.0 / 3.6,
    UnitOfSpeed.MILES_PER_HOUR: 1.0 / 2.236936,
    UnitOfSpeed.FEET_PER_SECOND: 0.3048,
    UnitOfSpeed.KNOTS: 1.0 / 1.943844,
}


def _plain_types(value: Any) -> Any:
    """Recursively convert numpy scalars/arrays into plain Python types.

    Entity attributes have to survive Home Assistant's JSON serialization, and
    orjson rejects numpy types such as ``float32``, ``int64`` and ``ndarray``.
    """
    if isinstance(value, dict):
        return {k: _plain_types(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_types(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_plain_types(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _as_float(value: Any, default: float) -> float:
    """Coerce a forecast/sensor value to a finite float.

    Weather integrations are free to report a key as ``None`` (Home Assistant's
    own ``Forecast`` type allows it) or as a non-numeric string. Letting either
    through produces a ``TypeError`` on the next comparison, or a silent NaN
    that poisons the whole optimization horizon, so anything that is not a
    finite number falls back to ``default``.
    """
    if value is None:
        return default
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if not np.isfinite(result):
        return default
    return result

DHW_PROFILE_STORE_VERSION = 1
DHW_PROFILE_EWMA_ALPHA = 0.12
DHW_PROFILE_MIN_INTENSITY = 0.2
DHW_PROFILE_MAX_INTENSITY = 3.5

# Learning rates for the tank cooling model. Every observation is an upper
# bound on the true standby loss — an unnoticed draw can only make the tank
# look leakier than it is, never tighter. So the estimate follows the lower
# envelope of what is observed: it drops quickly towards a quieter reading and
# only creeps upward, which keeps a single shower from convincing the model
# that the tank is badly insulated.
DHW_COOLING_ALPHA_DOWN = 0.25
DHW_COOLING_ALPHA_UP = 0.02
# Sample intervals outside this range are useless: too short and sensor
# quantisation dominates, too long and the tank was almost certainly used.
DHW_COOLING_MIN_SAMPLE_HOURS = 0.25
DHW_COOLING_MAX_SAMPLE_HOURS = 6.0
# The tank has to be meaningfully warmer than its surroundings for the decay
# to carry any information about the loss coefficient.
DHW_COOLING_MIN_DELTA = 5.0

# The buffer tank is learned with the same lower-envelope estimator as the DHW
# tank, but it is a much smaller vessel that is charged frequently, so quiet
# intervals are shorter and rarer. The window is therefore tighter and the
# minimum useful ΔT lower.
BUFFER_COOLING_ALPHA_DOWN = 0.25
BUFFER_COOLING_ALPHA_UP = 0.02
BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15
BUFFER_COOLING_MAX_SAMPLE_HOURS = 3.0
BUFFER_COOLING_MIN_DELTA = 4.0
BUFFER_AMBIENT_TEMP = 20.0

# House heat loss learning.
#
# The estimator is a one-step model correction: simulate the interval that just
# elapsed with the power that was actually applied, compare the predicted
# indoor temperature to the measured one, and attribute the residual to the
# heat loss coefficient. The sensitivity of the predicted change to UA is
#
#     d(ΔT_room)/dUA = -(T_room - T_out) * Δt / C_room
#
# so a Newton step gives the correction directly. Unlike the tank, the bias
# here is two-sided (unmodelled solar and occupancy gains push it down, an open
# window or a draughty day pushes it up), so a symmetric EWMA is correct and
# the lower-envelope trick from the DHW learner deliberately does *not* apply.
HOUSE_LOSS_ALPHA = 0.02
# Below this indoor/outdoor difference the residual says almost nothing about
# UA and dividing by it amplifies sensor noise without limit.
HOUSE_LOSS_MIN_DELTA = 6.0
HOUSE_LOSS_MIN_SAMPLE_HOURS = 0.15
HOUSE_LOSS_MAX_SAMPLE_HOURS = 1.5
# A single interval may never move the estimate more than this fraction; real
# building fabric does not change, so anything larger is a disturbance.
HOUSE_LOSS_MAX_STEP = 0.05
# Residuals beyond this are a door left open, a wood stove, or a sensor glitch
# rather than a heat loss error.
HOUSE_LOSS_MAX_RESIDUAL = 1.0  # °C

THERMAL_LEARNING_STORE_VERSION = 1

# Tibber GraphQL query for price data
TIBBER_PRICE_QUERY = """
{
  viewer {
    homes {
      currentSubscription {
        priceInfo {
          current {
            total
            startsAt
            level
          }
          today {
            total
            startsAt
            level
          }
          tomorrow {
            total
            startsAt
            level
          }
        }
      }
    }
  }
}
"""


class HeatPumpOptimizerCoordinator(DataUpdateCoordinator):
    """Coordinator for Heat Pump Cost Optimizer."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._config = {**entry.data, **entry.options}

        # Get optimization interval
        interval_min = self._config.get(
            CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval_min),
        )

        # Initialize thermal model
        self._thermal_params = ThermalParameters.from_config(self._config)
        self._thermal_model = ThermalModel(self._thermal_params)

        # Initialize optimizer config
        self._opt_config = OptimizationConfig(
            target_temp=self._config.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
            min_temp=self._config.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP),
            max_temp=self._config.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP),
            comfort_temp_day=self._config.get(
                CONF_COMFORT_TEMP_DAY, DEFAULT_COMFORT_TEMP_DAY
            ),
            comfort_temp_night=self._config.get(
                CONF_COMFORT_TEMP_NIGHT, DEFAULT_COMFORT_TEMP_NIGHT
            ),
            day_start_hour=int(
                self._config.get(CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR)
            ),
            day_end_hour=int(
                self._config.get(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR)
            ),
            price_weight=self._config.get(CONF_PRICE_WEIGHT, DEFAULT_PRICE_WEIGHT),
            comfort_weight=self._config.get(
                CONF_COMFORT_WEIGHT, DEFAULT_COMFORT_WEIGHT
            ),
        )

        # Initialize optimizer
        self._optimizer = HeatPumpOptimizer(self._thermal_model, self._opt_config)

        # State
        self._mode: str = MODE_AUTO
        # Populated during setup from the manifest so the device registry
        # reports the real integration version.
        self.integration_version: str | None = None
        self._optimization_result: OptimizationResult | None = None
        self._last_optimization: datetime | None = None
        self._next_optimization: datetime | None = None
        self._prices: list[dict] = []
        self._weather_forecast: list[dict] = []
        self._current_state = ThermalState()
        self._current_action: dict[str, Any] = {}
        self._unsub_timer: Any = None

        # Solar / return temp state
        self._solar_radiation: float = 0.0
        self._floor_return_temp: float | None = None
        self._solar_radiation_forecast: list[float] = []
        self._open_meteo: OpenMeteoSolar | None = None

        # DHW state
        self._dhw_temperature: float | None = None
        self._last_dhw_temp_sample: float | None = None
        self._last_dhw_sample_time: datetime | None = None
        self._dhw_hourly_profile: list[float] = (
            self._thermal_params.dhw_hourly_draw_pattern.copy()
        )
        # Self-learned standby cooling of the tank, in °C/h at the reference
        # condition (45 °C tank, 20 °C ambient). Seeded from the configured
        # default until enough quiet decay has been observed.
        self._dhw_cooling_rate: float = float(
            self._thermal_params.dhw_cooling_rate
        )
        self._dhw_cooling_samples: int = 0
        self._dhw_heating_since_sample: bool = False
        self._dhw_profile_store: Store = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_dhw_profile",
        )
        self._dhw_last_legionella: datetime | None = None
        self._dhw_legionella_store: Store = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_dhw_legionella",
        )

        # Self-learned buffer tank standby cooling, in °C/h at the same
        # reference ΔT as the DHW rate. Only learned when a buffer tank
        # temperature sensor is configured.
        self._buffer_cooling_rate: float = float(
            self._thermal_params.buffer_cooling_rate
        )
        self._buffer_cooling_samples: int = 0
        self._last_buffer_temp_sample: float | None = None
        self._last_buffer_sample_time: datetime | None = None
        self._buffer_heating_since_sample: bool = False

        # Self-learned correction to the configured house heat loss
        # coefficients. 1.0 means the configuration is taken at face value.
        self._house_heat_loss_scale: float = float(
            self._thermal_params.house_heat_loss_scale
        )
        self._house_heat_loss_samples: int = 0
        self._last_house_sample: ThermalState | None = None
        self._last_house_sample_time: datetime | None = None
        self._last_house_sample_power: float = 0.0

        self._thermal_learning_store: Store = Store(
            hass,
            THERMAL_LEARNING_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_thermal_learning",
        )

        # ECL110 MQTT state
        self._ecl110_command_topic: str = self._config.get(
            CONF_ECL110_COMMAND_TOPIC, DEFAULT_ECL110_COMMAND_TOPIC
        )
        self._ecl110_displace_set_topic: str = self._config.get(
            CONF_ECL110_DISPLACE_SET_TOPIC, DEFAULT_ECL110_DISPLACE_SET_TOPIC
        )
        self._ecl110_state_topic: str = self._config.get(
            CONF_ECL110_STATE_TOPIC, DEFAULT_ECL110_STATE_TOPIC
        )
        self._ecl110_qos: int = int(self._config.get(CONF_ECL110_QOS, DEFAULT_ECL110_QOS))
        self._ecl110_retain: bool = bool(self._config.get(CONF_ECL110_RETAIN, DEFAULT_ECL110_RETAIN))
        self._ecl110_displace_min: float = float(
            self._config.get(CONF_ECL110_DISPLACE_MIN, DEFAULT_ECL110_DISPLACE_MIN)
        )
        self._ecl110_displace_max: float = float(
            self._config.get(CONF_ECL110_DISPLACE_MAX, DEFAULT_ECL110_DISPLACE_MAX)
        )
        self._ecl110_current_displace: float = 0.0
        self._ecl110_last_payload: dict[str, Any] = {}
        self._unsub_ecl110_state: Any = None

        # Subscribe to ECL110 state topic if MQTT is available
        hass.async_create_task(self._async_setup_ecl110_state_subscription())

        # Load learned DHW usage profile (persisted across restarts)
        hass.async_create_task(self._async_load_dhw_profile())
        hass.async_create_task(self._async_load_dhw_legionella())
        hass.async_create_task(self._async_load_thermal_learning())

    @property
    def mode(self) -> str:
        """Return current operation mode."""
        return self._mode

    @property
    def optimization_result(self) -> OptimizationResult | None:
        """Return the latest optimization result."""
        return self._optimization_result

    @property
    def last_optimization(self) -> datetime | None:
        return self._last_optimization

    @property
    def next_optimization(self) -> datetime | None:
        return self._next_optimization

    @property
    def current_action(self) -> dict[str, Any]:
        return self._current_action
    async def _async_setup_ecl110_state_subscription(self) -> None:
        """Subscribe to ECL110 MQTT state updates if MQTT integration is available."""
        if not self._ecl110_state_topic:
            return
        try:
            self._unsub_ecl110_state = await mqtt.async_subscribe(
                self.hass,
                self._ecl110_state_topic,
                self._async_handle_ecl110_state_message,
                qos=self._ecl110_qos,
            )
            _LOGGER.debug("Subscribed to ECL110 state topic: %s", self._ecl110_state_topic)
        except Exception as err:
            _LOGGER.debug("ECL110 MQTT state subscription not available: %s", err)

    @callback
    def _async_handle_ecl110_state_message(self, msg: Any) -> None:
        """Handle ECL110 MQTT state payload updates."""
        payload = msg.payload
        try:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8", errors="ignore")
            data = json.loads(payload) if isinstance(payload, str) else payload

            displace: float | None = None
            if isinstance(data, dict):
                # Legacy state payload shape
                displace_raw = data.get("displace")
                if displace_raw is None and isinstance(data.get("command"), dict):
                    displace_raw = data["command"].get("displace")
                if displace_raw is not None:
                    displace = float(displace_raw)

                effective = data.get("effective_displace")
                if effective is not None:
                    self._current_state.ecl110_effective_displace = float(effective)
            elif isinstance(data, (int, float)):
                # New direct topic payload shape: scalar JSON value
                displace = float(data)

            if displace is not None:
                self._ecl110_current_displace = displace
                self._current_state.ecl110_displace_command = displace
        except Exception:
            # Ignore malformed payloads
            return

    @property
    def device_info(self) -> DeviceInfo:
        """Device registry entry shared by every platform of this entry.

        All three platforms previously declared their own model and version,
        which disagreed with each other and with the manifest; whichever
        entity registered last silently won.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="Heat Pump Optimizer",
            manufacturer="Custom",
            model="MPC Optimizer",
            sw_version=self.integration_version,
        )

    @property
    def target_temperature(self) -> float:
        """The comfort target the user configured."""
        return self._opt_config.target_temp

    async def async_set_target_temperature(self, temperature: float) -> None:
        """Change the comfort target and persist it across restarts.

        Writing it back to the entry options is what makes the change survive
        a reload; updating only the in-memory optimizer config meant the value
        silently reverted the next time the entry was reloaded.
        """
        self._opt_config.target_temp = temperature
        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, CONF_TARGET_TEMP: temperature},
        )

    @property
    def current_state(self) -> ThermalState:
        return self._current_state

    @property
    def prices(self) -> list[dict]:
        return self._prices

    @property
    def solar_radiation(self) -> float:
        """Current solar radiation reading."""
        return self._solar_radiation

    @property
    def floor_return_temp(self) -> float | None:
        """Current floor heating return temperature."""
        return self._floor_return_temp

    @property
    def dhw_temperature(self) -> float | None:
        """Current DHW temperature."""
        return self._dhw_temperature

    def _normalize_dhw_profile(self, profile: list[float]) -> list[float]:
        """Normalize and clamp DHW hourly profile (average ~= 1.0)."""
        if len(profile) != 24:
            profile = self._thermal_params.dhw_hourly_draw_pattern.copy()

        cleaned = [
            float(np.clip(v, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY))
            for v in profile
        ]
        avg = float(np.mean(cleaned)) if cleaned else 1.0
        if avg <= 0:
            return self._thermal_params.dhw_hourly_draw_pattern.copy()

        normalized = [float(np.clip(v / avg, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY)) for v in cleaned]
        return normalized

    async def _async_load_dhw_profile(self) -> None:
        """Load the persisted DHW usage profile and tank cooling rate."""
        try:
            stored = await self._dhw_profile_store.async_load() or {}
        except Exception as err:
            _LOGGER.debug("Could not load learned DHW profile: %s", err)
            return

        profile = stored.get("hourly_profile")
        if isinstance(profile, list) and len(profile) == 24:
            self._dhw_hourly_profile = self._normalize_dhw_profile(profile)
            self._thermal_params.dhw_hourly_draw_pattern = (
                self._dhw_hourly_profile.copy()
            )
            _LOGGER.info("Loaded learned DHW usage profile from storage")

        rate = stored.get("cooling_rate")
        if rate is None:
            return
        try:
            self._apply_dhw_cooling_rate(float(rate))
            self._dhw_cooling_samples = int(stored.get("cooling_samples", 0))
        except (TypeError, ValueError) as err:
            _LOGGER.debug("Could not load learned DHW cooling rate: %s", err)
            return
        _LOGGER.info(
            "Loaded learned DHW tank cooling rate %.2f °C/h (%d samples)",
            self._dhw_cooling_rate,
            self._dhw_cooling_samples,
        )

    def _apply_dhw_cooling_rate(self, rate: float) -> None:
        """Clamp a cooling rate to a plausible range and push it to the model."""
        self._dhw_cooling_rate = float(
            np.clip(rate, DHW_COOLING_RATE_MIN, DHW_COOLING_RATE_MAX)
        )
        self._thermal_params.dhw_cooling_rate = self._dhw_cooling_rate

    async def _async_save_dhw_profile(self) -> None:
        """Persist learned DHW profile to Home Assistant storage."""
        try:
            await self._dhw_profile_store.async_save(
                {
                    "hourly_profile": self._dhw_hourly_profile,
                    "cooling_rate": self._dhw_cooling_rate,
                    "cooling_samples": self._dhw_cooling_samples,
                    "updated_at": dt_util.now().isoformat(),
                }
            )
        except Exception as err:
            _LOGGER.debug("Could not persist DHW profile: %s", err)

    # ------------------------------------------------------------------
    # Buffer tank and building fabric learning
    # ------------------------------------------------------------------

    async def _async_load_thermal_learning(self) -> None:
        """Load the learned buffer cooling rate and house heat loss scale."""
        try:
            stored = await self._thermal_learning_store.async_load() or {}
        except Exception as err:
            _LOGGER.debug("Could not load learned thermal parameters: %s", err)
            return

        rate = stored.get("buffer_cooling_rate")
        if rate is not None:
            try:
                self._apply_buffer_cooling_rate(float(rate))
                self._buffer_cooling_samples = int(
                    stored.get("buffer_cooling_samples", 0)
                )
                _LOGGER.info(
                    "Loaded learned buffer tank cooling rate %.2f °C/h (%d samples)",
                    self._buffer_cooling_rate,
                    self._buffer_cooling_samples,
                )
            except (TypeError, ValueError) as err:
                _LOGGER.debug("Could not load buffer cooling rate: %s", err)

        scale = stored.get("house_heat_loss_scale")
        if scale is not None:
            try:
                self._apply_house_heat_loss_scale(float(scale))
                self._house_heat_loss_samples = int(
                    stored.get("house_heat_loss_samples", 0)
                )
                _LOGGER.info(
                    "Loaded learned house heat loss scale %.3f (%d samples)",
                    self._house_heat_loss_scale,
                    self._house_heat_loss_samples,
                )
            except (TypeError, ValueError) as err:
                _LOGGER.debug("Could not load house heat loss scale: %s", err)

    async def _async_save_thermal_learning(self) -> None:
        """Persist the learned buffer and building parameters."""
        try:
            await self._thermal_learning_store.async_save(
                {
                    "buffer_cooling_rate": self._buffer_cooling_rate,
                    "buffer_cooling_samples": self._buffer_cooling_samples,
                    "house_heat_loss_scale": self._house_heat_loss_scale,
                    "house_heat_loss_samples": self._house_heat_loss_samples,
                    "updated_at": dt_util.now().isoformat(),
                }
            )
        except Exception as err:
            _LOGGER.debug("Could not persist learned thermal parameters: %s", err)

    @staticmethod
    def _plan_slots(
        timestamps: list[datetime],
        powers: list[float],
        prices: list[float],
        dt_hours: float,
        threshold: float = 0.05,
    ) -> list[dict[str, Any]]:
        """Collapse a per-step power schedule into contiguous heating slots.

        The step schedule is what the optimizer produces, but what a person
        wants to see is "the pump runs from 02:00 to 04:30 and that costs 4.20".
        Consecutive steps above ``threshold`` kW are merged into one slot and
        summarised with their energy, average price and cost.
        """
        slots: list[dict[str, Any]] = []
        start_idx: int | None = None

        def close(end_idx: int) -> None:
            assert start_idx is not None
            span = list(range(start_idx, end_idx))
            energy = sum(powers[i] for i in span) * dt_hours
            cost = sum(powers[i] * prices[i] for i in span) * dt_hours
            end_ts = (
                timestamps[end_idx]
                if end_idx < len(timestamps)
                else timestamps[-1] + timedelta(hours=dt_hours)
            )
            duration = len(span) * dt_hours
            slots.append(
                {
                    "start": timestamps[start_idx].isoformat(),
                    "end": end_ts.isoformat(),
                    "duration_hours": round(duration, 2),
                    "avg_power_kw": round(energy / duration, 2) if duration else 0.0,
                    "energy_kwh": round(energy, 3),
                    "avg_price": (round(cost / energy, 4) if energy > 1e-9 else 0.0),
                    "cost": round(cost, 2),
                }
            )

        for i, power in enumerate(powers):
            if power > threshold:
                if start_idx is None:
                    start_idx = i
            elif start_idx is not None:
                close(i)
                start_idx = None
        if start_idx is not None:
            close(len(powers))
        return slots

    def _build_plan_views(self, result) -> dict[str, Any]:
        """Full-resolution space heating and DHW plans for the plan sensors.

        Deliberately separate from the ``schedule`` / ``dhw_schedule`` keys,
        which are truncated to 24 steps (only six hours at the default 15
        minute resolution) for the legacy sensors. Charting the plan needs the
        whole horizon.
        """
        dt_hours = self._opt_config.dt_hours
        timestamps = result.timestamps
        n = len(timestamps)
        if not n:
            return {"space_plan": {}, "dhw_plan": {}}

        def series(values, offset: int = 0, fill: float | None = None):
            out: list[float | None] = []
            for i in range(n):
                idx = i + offset
                if values and idx < len(values):
                    out.append(round(float(values[idx]), 2))
                else:
                    out.append(fill)
            return out

        prices = series(result.prices)
        outdoor = series(result.outdoor_temps)
        space_power = series(result.power_schedule)
        # Trajectories carry the initial state at index 0, so the value that
        # belongs to step i is at i + 1.
        room = series(result.room_temp_trajectory, offset=1)
        two_zone = bool(
            result.upper_temp_trajectory and result.lower_temp_trajectory
        )
        upper = series(result.upper_temp_trajectory, offset=1) if two_zone else [None] * n
        lower = series(result.lower_temp_trajectory, offset=1) if two_zone else [None] * n
        dhw_power = series(result.dhw_power_schedule)
        dhw_temp = series(result.dhw_temp_trajectory, offset=1)

        raw_prices = [p if p is not None else 0.0 for p in prices]
        raw_space = [p if p is not None else 0.0 for p in space_power]
        raw_dhw = [p if p is not None else 0.0 for p in dhw_power]

        space_slots = self._plan_slots(timestamps, raw_space, raw_prices, dt_hours)
        dhw_slots = self._plan_slots(timestamps, raw_dhw, raw_prices, dt_hours)

        space_forecast = [
            {
                "t": timestamps[i].isoformat(),
                "price": prices[i],
                "outdoor": outdoor[i],
                "space_power": space_power[i],
                "room": room[i],
                "upper": upper[i],
                "lower": lower[i],
            }
            for i in range(n)
        ]
        dhw_forecast = [
            {
                "t": timestamps[i].isoformat(),
                "price": prices[i],
                "outdoor": outdoor[i],
                "dhw_power": dhw_power[i],
                "dhw_temp": dhw_temp[i],
            }
            for i in range(n)
        ]

        return {
            "space_plan": {
                "forecast": space_forecast,
                "slots": space_slots,
                "total_energy_kwh": round(sum(raw_space) * dt_hours, 2),
                "total_cost": round(
                    sum(p * pr for p, pr in zip(raw_space, raw_prices)) * dt_hours, 2
                ),
                "active_now": bool(raw_space and raw_space[0] > 0.05),
            },
            "dhw_plan": {
                "forecast": dhw_forecast,
                "slots": dhw_slots,
                "total_energy_kwh": round(sum(raw_dhw) * dt_hours, 2),
                "total_cost": round(
                    sum(p * pr for p, pr in zip(raw_dhw, raw_prices)) * dt_hours, 2
                ),
                "active_now": bool(raw_dhw and raw_dhw[0] > 0.05),
            },
        }

    def _effective_house_heat_loss(self) -> float:
        """Configured heat loss coefficient after the learned correction, kW/°C."""
        params = self._thermal_params
        if params.two_zone_enabled:
            base = params.upper_floor_heat_loss + params.lower_floor_heat_loss
        else:
            base = params.heat_loss_coefficient
        return round(base * self._house_heat_loss_scale, 4)

    def _current_weather(self) -> tuple[float, float]:
        """Current wind speed (m/s) and precipitation (mm/h) for simulation."""
        if self._weather_forecast:
            first = self._weather_forecast[0]
            return (
                max(0.0, _as_float(first.get("wind_speed"), 0.0)),
                max(0.0, _as_float(first.get("precipitation"), 0.0)),
            )
        return 0.0, 0.0

    def _apply_buffer_cooling_rate(self, rate: float) -> None:
        """Clamp a buffer cooling rate to a plausible range and push it out."""
        self._buffer_cooling_rate = float(
            np.clip(rate, BUFFER_COOLING_RATE_MIN, BUFFER_COOLING_RATE_MAX)
        )
        self._thermal_params.buffer_cooling_rate = self._buffer_cooling_rate

    def _apply_house_heat_loss_scale(self, scale: float) -> None:
        """Clamp the house heat loss correction and push it to the model."""
        self._house_heat_loss_scale = float(
            np.clip(scale, HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX)
        )
        self._thermal_params.house_heat_loss_scale = self._house_heat_loss_scale

    async def _async_learn_buffer_cooling(self, buffer_temp: float) -> None:
        """Refine the buffer tank standby loss from quiet decay.

        Identical in form to the DHW cooling learner: an idle interval pins the
        time constant through ``UA/C = -ln(ΔT_end / ΔT_start) / Δt``, and the
        result is folded in as a lower envelope because every contaminating
        effect (a space heating call drawing from the tank) can only make the
        tank look leakier than it is.
        """
        now = dt_util.now()
        heating = float(self._current_action.get("power", 0.0)) > 0.05

        previous_temp = self._last_buffer_temp_sample
        previous_time = self._last_buffer_sample_time
        heated = self._buffer_heating_since_sample or heating

        self._last_buffer_temp_sample = buffer_temp
        self._last_buffer_sample_time = now
        self._buffer_heating_since_sample = heating

        if previous_temp is None or previous_time is None or heated:
            return

        dt_h = (now - previous_time).total_seconds() / 3600.0
        if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:
            return
        if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:
            return
        if buffer_temp > previous_temp:
            return

        start_delta = previous_temp - BUFFER_AMBIENT_TEMP
        end_delta = buffer_temp - BUFFER_AMBIENT_TEMP
        if start_delta < BUFFER_COOLING_MIN_DELTA:
            return
        if end_delta < BUFFER_COOLING_MIN_DELTA:
            return

        observed = float(
            -np.log(end_delta / start_delta) / dt_h * DHW_COOLING_REFERENCE_DELTA
        )
        if not np.isfinite(observed):
            return
        if observed < BUFFER_COOLING_RATE_MIN or observed > BUFFER_COOLING_RATE_MAX:
            return

        alpha = (
            BUFFER_COOLING_ALPHA_DOWN
            if observed < self._buffer_cooling_rate
            else BUFFER_COOLING_ALPHA_UP
        )
        self._apply_buffer_cooling_rate(
            (1.0 - alpha) * self._buffer_cooling_rate + alpha * observed
        )
        self._buffer_cooling_samples += 1

        _LOGGER.debug(
            "Learned buffer cooling: %.2f°C→%.2f°C over %.2fh gives %.2f °C/h, "
            "model now %.2f °C/h (%d samples)",
            previous_temp,
            buffer_temp,
            dt_h,
            observed,
            self._buffer_cooling_rate,
            self._buffer_cooling_samples,
        )
        await self._async_save_thermal_learning()

    async def _async_learn_house_heat_loss(self) -> None:
        """Correct the house heat loss coefficient from prediction error.

        Rather than trying to isolate a coasting period — a heated house rarely
        has one — this replays the interval that just elapsed through the very
        model the optimizer uses, with the electrical power that was actually
        applied, and compares the predicted indoor temperature to the measured
        one. Everything the model already knows about (slab transfer, solar
        gain, internal gains, wind and rain) is therefore accounted for, and
        what is left over is attributed to the heat loss coefficient.

        The Newton step follows from the single-zone dynamics: predicted room
        change is linear in UA with slope ``-(T_room - T_out)·Δt / C_room``, so
        a residual of ``e`` degrees implies ``ΔUA = -e·C_room / (ΔT·Δt)``.
        Expressed as a correction to the configured coefficient this becomes a
        multiplicative scale, which is also the right shape for the two-zone
        model where only one indoor sensor is available and the two floors
        cannot be identified separately.
        """
        now = dt_util.now()
        observed = self._current_state.room_temperature
        previous_state = self._last_house_sample
        previous_time = self._last_house_sample_time
        previous_power = self._last_house_sample_power

        # Snapshot for the next interval before any early return, so a rejected
        # sample does not poison the following one with a stale baseline.
        self._last_house_sample = replace(self._current_state)
        self._last_house_sample_time = now
        self._last_house_sample_power = float(self._current_action.get("power", 0.0))

        if previous_state is None or previous_time is None or observed is None:
            return

        dt_h = (now - previous_time).total_seconds() / 3600.0
        if dt_h < HOUSE_LOSS_MIN_SAMPLE_HOURS:
            return
        if dt_h > HOUSE_LOSS_MAX_SAMPLE_HOURS:
            return

        outdoor = previous_state.outdoor_temperature
        delta_t = previous_state.room_temperature - outdoor
        if delta_t < HOUSE_LOSS_MIN_DELTA:
            return

        try:
            wind_speed, precipitation = self._current_weather()
            predicted_state = self._thermal_model.simulate_step(
                previous_state,
                previous_power,
                outdoor,
                wind_speed=wind_speed,
                precipitation=precipitation,
                solar_radiation=previous_state.solar_radiation,
                dt_hours=dt_h,
            )
        except Exception as err:
            _LOGGER.debug("House heat loss learning simulation failed: %s", err)
            return

        residual = observed - predicted_state.room_temperature
        if not np.isfinite(residual):
            return
        if abs(residual) > HOUSE_LOSS_MAX_RESIDUAL:
            _LOGGER.debug(
                "Ignoring house heat loss sample: residual %.2f°C is too large "
                "to be a heat loss error",
                residual,
            )
            return

        # Current effective coefficient, i.e. what actually produced the
        # prediction, so the Newton step is taken about the right point.
        params = self._thermal_params
        if params.two_zone_enabled:
            base_u = params.upper_floor_heat_loss + params.lower_floor_heat_loss
            capacity = (
                params.upper_floor_thermal_mass + params.lower_floor_thermal_mass
            )
        else:
            base_u = params.heat_loss_coefficient
            capacity = params.room_thermal_mass
        if base_u <= 1e-6 or capacity <= 1e-6:
            return

        current_u = base_u * self._house_heat_loss_scale
        # Warmer than predicted means the model is over-estimating the loss.
        delta_u = -residual * capacity / (delta_t * dt_h)
        target_scale = (current_u + delta_u) / base_u
        if not np.isfinite(target_scale) or target_scale <= 0.0:
            return

        new_scale = (
            1.0 - HOUSE_LOSS_ALPHA
        ) * self._house_heat_loss_scale + HOUSE_LOSS_ALPHA * target_scale
        # Rate-limit so a single odd interval cannot jump the model.
        max_step = self._house_heat_loss_scale * HOUSE_LOSS_MAX_STEP
        new_scale = float(
            np.clip(
                new_scale,
                self._house_heat_loss_scale - max_step,
                self._house_heat_loss_scale + max_step,
            )
        )
        self._apply_house_heat_loss_scale(new_scale)
        self._house_heat_loss_samples += 1

        _LOGGER.debug(
            "Learned house heat loss: residual %.3f°C over %.2fh at ΔT=%.1f°C "
            "suggests scale %.3f, model now %.3f (%d samples)",
            residual,
            dt_h,
            delta_t,
            target_scale,
            self._house_heat_loss_scale,
            self._house_heat_loss_samples,
        )
        if self._house_heat_loss_samples % 10 == 0:
            await self._async_save_thermal_learning()

    async def _async_load_dhw_legionella(self) -> None:
        """Load the timestamp of the last completed anti-legionella cycle.

        A fresh install has no record. It is initialised to "now" rather than
        "never" so a brand-new setup does not immediately blast the tank to the
        legionella temperature.
        """
        try:
            stored = await self._dhw_legionella_store.async_load()
            raw = (stored or {}).get("last_cycle")
            parsed = dt_util.parse_datetime(raw) if isinstance(raw, str) else None
            if parsed is not None:
                self._dhw_last_legionella = parsed
                return
        except Exception as err:
            _LOGGER.debug("Could not load DHW legionella timestamp: %s", err)

        self._dhw_last_legionella = dt_util.now()
        await self._async_save_dhw_legionella()

    async def _async_save_dhw_legionella(self) -> None:
        """Persist the timestamp of the last completed anti-legionella cycle."""
        if self._dhw_last_legionella is None:
            return
        try:
            await self._dhw_legionella_store.async_save(
                {"last_cycle": self._dhw_last_legionella.isoformat()}
            )
        except Exception as err:
            _LOGGER.debug("Could not persist DHW legionella timestamp: %s", err)

    async def _async_track_dhw_legionella(self, dhw_temp: float) -> None:
        """Reset the anti-legionella timer whenever the tank actually gets hot.

        Any reason for the tank reaching the disinfection temperature counts —
        a planned cycle, a manual boost, or an immersion heater.
        """
        target = float(self._thermal_params.dhw_legionella_temp)
        if dhw_temp < target - 1.0:
            return
        now = dt_util.now()
        previous = self._dhw_last_legionella
        if previous is not None and (now - previous).total_seconds() < 3600:
            return
        self._dhw_last_legionella = now
        _LOGGER.info(
            "DHW anti-legionella cycle observed at %.1f°C, timer reset", dhw_temp
        )
        await self._async_save_dhw_legionella()

    def _dhw_hours_since_legionella(self) -> float | None:
        """Hours since the last anti-legionella cycle, or None if unknown."""
        if self._dhw_last_legionella is None:
            return None
        delta = (dt_util.now() - self._dhw_last_legionella).total_seconds() / 3600.0
        return max(0.0, delta)

    def _dhw_legionella_due_in_hours(self) -> float | None:
        """Hours left before the next anti-legionella cycle is required."""
        params = self._thermal_params
        if not params.dhw_legionella_enabled:
            return None
        since = self._dhw_hours_since_legionella()
        if since is None:
            return None
        return round(params.dhw_legionella_interval_days * 24.0 - since, 1)

    def _dhw_current_hour(self) -> float:
        now = dt_util.now()
        return now.hour + now.minute / 60.0

    def _dhw_effective_windows(self) -> list:
        """Demand windows the optimizer is actually planning against."""
        result = self._optimization_result
        planned = (result.predictive_info or {}).get("dhw_windows") if result else None
        if planned:
            try:
                return parse_windows(planned)
            except DHWWindowError:
                pass
        return self._thermal_params.dhw_demand_windows

    def _dhw_in_demand_window(self) -> bool:
        """Whether hot water is required right now."""
        return hour_in_windows(
            self._dhw_current_hour(), self._dhw_effective_windows()
        )

    def _dhw_next_window_in_hours(self) -> float | None:
        """Hours until the next DHW demand window opens (0 if inside one)."""
        hours = hours_until_next_window(
            self._dhw_current_hour(), self._dhw_effective_windows()
        )
        return round(hours, 2) if hours is not None else None

    async def _async_learn_dhw_dynamics(self, dhw_temp: float) -> None:
        """Learn the tank's usage profile and its standby cooling rate.

        Both models are fed by the same observation — how far the tank
        temperature moved since the previous sample — so they are derived
        together from a single consistent measurement.
        """
        now = dt_util.now()
        heating = bool(self._current_action.get("dhw_heating_active", False))

        previous_temp = self._last_dhw_temp_sample
        previous_time = self._last_dhw_sample_time
        heated_during_interval = self._dhw_heating_since_sample or heating

        self._last_dhw_temp_sample = dhw_temp
        self._last_dhw_sample_time = now
        self._dhw_heating_since_sample = heating

        if previous_temp is None or previous_time is None:
            return

        dt_h = (now - previous_time).total_seconds() / 3600.0
        if dt_h <= 0.02 or dt_h > DHW_COOLING_MAX_SAMPLE_HOURS:
            return

        temp_drop = previous_temp - dhw_temp

        if not heated_during_interval:
            await self._async_learn_dhw_cooling(previous_temp, dhw_temp, dt_h)
        await self._async_learn_dhw_usage(
            temp_drop, dt_h, now.hour, heated_during_interval
        )

    async def _async_learn_dhw_cooling(
        self, previous_temp: float, dhw_temp: float, dt_h: float
    ) -> None:
        """Refine the tank cooling model from an interval with no heating.

        Standby decay follows ``C·dT/dt = -UA·(T - T_ambient)``, so a pair of
        temperatures bracketing an idle interval pins down the time constant:

            UA/C = -ln((T_end - T_amb) / (T_start - T_amb)) / Δt

        Scaled to the reference condition that gives a cooling rate in °C/h
        directly comparable to the configured default.

        Any hot water drawn during the interval inflates the estimate, which is
        why the result is folded in as a lower envelope rather than a plain
        average — see the alpha constants.
        """
        if dt_h < DHW_COOLING_MIN_SAMPLE_HOURS:
            return
        # A rise means the tank was heated or refilled from a hotter source;
        # either way it says nothing about standby loss.
        if dhw_temp > previous_temp:
            return

        start_delta = previous_temp - DHW_AMBIENT_TEMP
        end_delta = dhw_temp - DHW_AMBIENT_TEMP
        if start_delta < DHW_COOLING_MIN_DELTA or end_delta < DHW_COOLING_MIN_DELTA:
            return

        time_constant = -np.log(end_delta / start_delta) / dt_h  # 1/h
        observed = float(time_constant * DHW_COOLING_REFERENCE_DELTA)
        if not np.isfinite(observed):
            return
        if observed < DHW_COOLING_RATE_MIN or observed > DHW_COOLING_RATE_MAX:
            return

        alpha = (
            DHW_COOLING_ALPHA_DOWN
            if observed < self._dhw_cooling_rate
            else DHW_COOLING_ALPHA_UP
        )
        self._apply_dhw_cooling_rate(
            (1.0 - alpha) * self._dhw_cooling_rate + alpha * observed
        )
        self._dhw_cooling_samples += 1

        _LOGGER.debug(
            "Learned DHW cooling: %.2f°C→%.2f°C over %.2fh gives %.2f °C/h, "
            "model now %.2f °C/h (%d samples)",
            previous_temp,
            dhw_temp,
            dt_h,
            observed,
            self._dhw_cooling_rate,
            self._dhw_cooling_samples,
        )
        await self._async_save_dhw_profile()

    async def _async_learn_dhw_usage(
        self, temp_drop: float, dt_h: float, hour: int, heated: bool
    ) -> None:
        """Learn hourly DHW usage profile from observed temperature drops."""
        # Learn only on meaningful drops while DHW is not actively heated.
        if temp_drop < 0.15 or heated:
            return

        draw_intensity = temp_drop / dt_h

        profile = self._dhw_hourly_profile.copy()
        profile[hour] = (
            (1.0 - DHW_PROFILE_EWMA_ALPHA) * profile[hour]
            + DHW_PROFILE_EWMA_ALPHA * draw_intensity
        )
        self._dhw_hourly_profile = self._normalize_dhw_profile(profile)
        self._thermal_params.dhw_hourly_draw_pattern = self._dhw_hourly_profile.copy()

        _LOGGER.debug(
            "Learned DHW usage hour=%d drop=%.2f°C dt=%.2fh intensity=%.2f",
            hour,
            temp_drop,
            dt_h,
            draw_intensity,
        )
        await self._async_save_dhw_profile()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data and run optimization."""
        try:
            # Update current state from sensors
            await self._update_current_state()

            # Fetch prices from Tibber
            await self._fetch_tibber_prices()

            # Fetch weather forecast (full 24h for solar, wind, rain, temp)
            await self._fetch_weather_forecast()

            # Refresh Open-Meteo irradiance, if that is the selected source.
            # Deliberately after the weather fetch: it overrides whatever
            # irradiance the weather entity did or did not supply.
            await self._fetch_solar_forecast()

            # Run optimization if in auto mode
            if self._mode in (MODE_AUTO, MODE_ECONOMY):
                await self.async_run_optimization()
            elif self._mode == MODE_COMFORT:
                self._current_action = {
                    "power": self._thermal_model.params.max_electrical_power * 0.7,
                    "setpoint": self._opt_config.target_temp,
                    "mode": "comfort",
                    "price": self._get_current_price(),
                    "power_normalized": 0.7,
                    "heat_pump_on": True,
                    "displace_value": min(4.0, self._ecl110_displace_max),
                }
            elif self._mode == MODE_BOOST:
                self._current_action = {
                    "power": self._thermal_model.params.max_electrical_power,
                    "setpoint": self._opt_config.max_temp,
                    "mode": "boost",
                    "price": self._get_current_price(),
                    "power_normalized": 1.0,
                    "heat_pump_on": True,
                    "displace_value": self._ecl110_displace_max,
                }
            elif self._mode == MODE_OFF:
                self._current_action = {
                    "power": 0.0,
                    "setpoint": self._opt_config.min_temp,
                    "mode": "off",
                    "price": self._get_current_price(),
                    "power_normalized": 0.0,
                    "heat_pump_on": False,
                    "displace_value": self._ecl110_displace_min,
                }

            # Apply current action to heat pump
            await self._apply_action()

            self._next_optimization = dt_util.now() + timedelta(
                minutes=self._config.get(
                    CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                )
            )

            return self._build_data_dict()

        except Exception as err:
            _LOGGER.error(
                "Error updating Heat Pump Optimizer: %s", err, exc_info=True
            )
            raise UpdateFailed(f"Error updating data: {err}") from err

    async def async_run_optimization(self) -> None:
        """Run the MPC optimization."""
        _LOGGER.info("Running heat pump optimization (predictive MPC)")

        try:
            prices, outdoor_temps, wind_speeds, precipitation, solar_rad = (
                self._prepare_forecast_data()
            )

            if len(prices) < 4:
                _LOGGER.warning(
                    "Not enough price data for optimization (got %d steps)",
                    len(prices),
                )
                return

            _LOGGER.debug(
                "Forecast data: %d steps, wind range=%.1f-%.1f m/s, "
                "precip range=%.1f-%.1f mm/h, solar range=%.0f-%.0f W/m²",
                len(prices),
                float(np.min(wind_speeds)), float(np.max(wind_speeds)),
                float(np.min(precipitation)), float(np.max(precipitation)),
                float(np.min(solar_rad)), float(np.max(solar_rad)),
            )

            # Run optimization in executor to avoid blocking
            result = await self.hass.async_add_executor_job(
                self._optimizer.optimize,
                self._current_state,
                prices,
                outdoor_temps,
                wind_speeds,
                precipitation,
                solar_rad,
                dt_util.now(),
            )

            self._optimization_result = result
            self._last_optimization = dt_util.now()

            self._current_action = self._optimizer.get_current_action(
                result, dt_util.now()
            )

            _LOGGER.info(
                "Optimization complete: savings=%.1f%%, cost=%.2f, status=%s, "
                "dhw_enabled=%s",
                result.savings_percentage,
                result.predicted_cost,
                result.status,
                self._thermal_params.dhw_enabled,
            )

        except Exception as err:
            _LOGGER.error("Optimization failed: %s", err, exc_info=True)

    async def async_set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        self._mode = mode
        _LOGGER.info("Operation mode set to: %s", mode)
        await self.async_request_refresh()

    async def async_update_thermal_params(self, params: dict[str, Any]) -> None:
        """Update thermal model parameters."""
        if "house_thermal_mass" in params:
            self._thermal_params.room_thermal_mass = params["house_thermal_mass"]
        if "house_heat_loss_coefficient" in params:
            self._thermal_params.heat_loss_coefficient = params[
                "house_heat_loss_coefficient"
            ]
            # A new nameplate value invalidates the correction learned against
            # the old one, so start over from "trust the configuration".
            self._apply_house_heat_loss_scale(DEFAULT_HOUSE_HEAT_LOSS_SCALE)
            self._house_heat_loss_samples = 0
            await self._async_save_thermal_learning()
        if CONF_BUFFER_COOLING_RATE in params:
            self._apply_buffer_cooling_rate(float(params[CONF_BUFFER_COOLING_RATE]))
            self._buffer_cooling_samples = 0
            await self._async_save_thermal_learning()
        if "ecl110_displace_min" in params:
            self._thermal_params.ecl110_displace_min = params["ecl110_displace_min"]
            self._ecl110_displace_min = params["ecl110_displace_min"]
        if "ecl110_displace_max" in params:
            self._thermal_params.ecl110_displace_max = params["ecl110_displace_max"]
            self._ecl110_displace_max = params["ecl110_displace_max"]
        if "slab_thermal_mass" in params:
            self._thermal_params.slab_thermal_mass = params["slab_thermal_mass"]
        if "slab_heat_transfer" in params:
            self._thermal_params.slab_heat_transfer = params["slab_heat_transfer"]
        if "heat_pump_cop_nominal" in params:
            self._thermal_params.cop_nominal = params["heat_pump_cop_nominal"]
        # Two-zone params
        if "upper_floor_thermal_mass" in params:
            self._thermal_params.upper_floor_thermal_mass = params[
                "upper_floor_thermal_mass"
            ]
        if "lower_floor_thermal_mass" in params:
            self._thermal_params.lower_floor_thermal_mass = params[
                "lower_floor_thermal_mass"
            ]
        if "inter_zone_heat_transfer" in params:
            self._thermal_params.inter_zone_transfer = params[
                "inter_zone_heat_transfer"
            ]
        if "radiator_power_fraction" in params:
            self._thermal_params.radiator_power_fraction = params[
                "radiator_power_fraction"
            ]
        if "window_area" in params:
            self._thermal_params.window_area = params["window_area"]
        if "solar_heat_gain_coefficient" in params:
            self._thermal_params.solar_heat_gain_coefficient = params[
                "solar_heat_gain_coefficient"
            ]
        # DHW params
        if "dhw_tank_volume" in params:
            self._thermal_params.dhw_tank_volume = params["dhw_tank_volume"]
        if "dhw_setpoint" in params:
            self._thermal_params.dhw_setpoint = params["dhw_setpoint"]
        if "ecl110_pid_time_constant_hours" in params:
            self._thermal_params.ecl110_pid_time_constant_hours = params[
                "ecl110_pid_time_constant_hours"
            ]
        if "dhw_min_temperature" in params:
            self._thermal_params.dhw_min_temp = params["dhw_min_temperature"]
        if "dhw_daily_consumption" in params:
            self._thermal_params.dhw_daily_consumption = params["dhw_daily_consumption"]
        if CONF_DHW_COOLING_RATE in params:
            # An explicit value replaces the learned one and resets the sample
            # count, so the learner treats it as the new starting point.
            self._apply_dhw_cooling_rate(float(params[CONF_DHW_COOLING_RATE]))
            self._dhw_cooling_samples = 0
            await self._async_save_dhw_profile()
        if CONF_DHW_SCHEDULE_ENABLED in params:
            self._thermal_params.dhw_schedule_enabled = bool(
                params[CONF_DHW_SCHEDULE_ENABLED]
            )
        if CONF_DHW_WINDOWS in params:
            try:
                self._thermal_params.dhw_windows = parse_windows(
                    params[CONF_DHW_WINDOWS]
                )
            except DHWWindowError as err:
                _LOGGER.warning("Ignoring invalid DHW demand windows: %s", err)
        if CONF_DHW_IDLE_MIN_TEMP in params:
            self._thermal_params.dhw_idle_min_temp = float(
                params[CONF_DHW_IDLE_MIN_TEMP]
            )
        if CONF_DHW_LEGIONELLA_ENABLED in params:
            self._thermal_params.dhw_legionella_enabled = bool(
                params[CONF_DHW_LEGIONELLA_ENABLED]
            )
        if CONF_DHW_LEGIONELLA_TEMP in params:
            self._thermal_params.dhw_legionella_temp = float(
                params[CONF_DHW_LEGIONELLA_TEMP]
            )
        if CONF_DHW_LEGIONELLA_INTERVAL_DAYS in params:
            self._thermal_params.dhw_legionella_interval_days = float(
                params[CONF_DHW_LEGIONELLA_INTERVAL_DAYS]
            )
        # Weather sensitivity params
        if "wind_sensitivity_factor" in params:
            self._thermal_params.wind_sensitivity = params["wind_sensitivity_factor"]
        if "rain_heat_loss_multiplier" in params:
            self._thermal_params.rain_heat_loss_multiplier = params[
                "rain_heat_loss_multiplier"
            ]

        self._thermal_model = ThermalModel(self._thermal_params)
        self._optimizer = HeatPumpOptimizer(self._thermal_model, self._opt_config)

        _LOGGER.info("Thermal parameters updated, re-running optimization")
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        if self._unsub_ecl110_state:
            self._unsub_ecl110_state()
            self._unsub_ecl110_state = None

    async def _update_current_state(self) -> None:
        """Update current thermal state from HA entities."""
        # Indoor temperature
        indoor_entity = self._config.get(CONF_INDOOR_TEMP_ENTITY)
        if indoor_entity:
            state = self.hass.states.get(indoor_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    self._current_state.room_temperature = float(state.state)
                    # For two-zone: indoor sensor is typically upper floor
                    self._current_state.upper_floor_temperature = float(state.state)
                except (ValueError, TypeError):
                    pass

        # Outdoor temperature
        outdoor_entity = self._config.get(CONF_OUTDOOR_TEMP_ENTITY)
        if outdoor_entity:
            state = self.hass.states.get(outdoor_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    self._current_state.outdoor_temperature = float(state.state)
                except (ValueError, TypeError):
                    pass

        # Floor heating return temperature sensor
        floor_return_entity = self._config.get(CONF_FLOOR_RETURN_TEMP_ENTITY)
        if floor_return_entity:
            state = self.hass.states.get(floor_return_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    self._floor_return_temp = float(state.state)
                    self._current_state.floor_return_temperature = (
                        self._floor_return_temp
                    )
                    # Update slab temperature estimate from return temp
                    self._thermal_model.update_slab_from_return_temp(
                        self._current_state, self._floor_return_temp
                    )
                    # Lower floor temp ~ return temp (rough estimate)
                    self._current_state.lower_floor_temperature = (
                        self._floor_return_temp + 0.5
                    )
                except (ValueError, TypeError):
                    pass

        # Solar radiation: a local pyranometer measures this house, so it wins
        # over any remote estimate. Open-Meteo fills in when no sensor is
        # configured or the sensor is not reporting.
        solar_entity = self._config.get(CONF_SOLAR_RADIATION_ENTITY)
        solar_from_sensor = False
        if solar_entity:
            state = self.hass.states.get(solar_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    self._solar_radiation = float(state.state)
                    self._current_state.solar_radiation = self._solar_radiation
                    solar_from_sensor = True
                except (ValueError, TypeError):
                    pass

        if not solar_from_sensor and self._open_meteo is not None:
            observed = self._open_meteo.current_irradiance(dt_util.utcnow())
            if observed is not None:
                self._solar_radiation = observed
                self._current_state.solar_radiation = observed

        # DHW temperature sensor
        dhw_entity = self._config.get(CONF_DHW_TEMP_ENTITY)
        if dhw_entity:
            state = self.hass.states.get(dhw_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    self._dhw_temperature = float(state.state)
                    self._current_state.dhw_temperature = self._dhw_temperature
                    await self._async_learn_dhw_dynamics(self._dhw_temperature)
                    await self._async_track_dhw_legionella(self._dhw_temperature)
                except (ValueError, TypeError):
                    pass

        self._current_state.dhw_hours_since_legionella = (
            self._dhw_hours_since_legionella()
        )

        # Buffer tank temperature sensor (optional; enables cooling learning)
        buffer_entity = self._config.get(CONF_BUFFER_TANK_TEMP_ENTITY)
        if buffer_entity:
            state = self.hass.states.get(buffer_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    buffer_temp = float(state.state)
                    self._current_state.buffer_tank_temperature = buffer_temp
                    await self._async_learn_buffer_cooling(buffer_temp)
                except (ValueError, TypeError):
                    pass

        # Refine the building fabric model from how the last interval actually
        # went. Runs last so it sees the fully populated state.
        await self._async_learn_house_heat_loss()

        # Update ECL110 effective displace state (PID/PI lag approximation)
        if "displace_value" in self._current_action:
            displace_cmd = float(self._current_action.get("displace_value", 0.0))
            dt_h = self._opt_config.dt_hours
            self._thermal_model.update_ecl110_displace_state(
                self._current_state,
                displace_cmd,
                dt_h,
            )
            self._ecl110_current_displace = self._current_state.ecl110_displace_command

        # If no floor return sensor, estimate slab from room temp
        if not floor_return_entity:
            if not hasattr(self, "_slab_temp_initialized"):
                self._current_state.slab_temperature = (
                    self._current_state.room_temperature + 1.0
                )
                self._current_state.lower_floor_temperature = (
                    self._current_state.room_temperature
                )
                self._slab_temp_initialized = True

    async def _fetch_tibber_prices(self) -> None:
        """Fetch electricity prices from Tibber API."""
        token = self._config.get(CONF_TIBBER_TOKEN)
        if not token:
            _LOGGER.error("No Tibber token configured")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        query_data = (
            '{"query": "'
            + TIBBER_PRICE_QUERY.replace("\n", " ").replace('"', '\\"')
            + '"}'
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    TIBBER_API_URL,
                    data=query_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Tibber API error: %s", resp.status)
                        return
                    data = await resp.json()

            if "errors" in data:
                _LOGGER.error("Tibber API errors: %s", data["errors"])
                return

            homes = data.get("data", {}).get("viewer", {}).get("homes", [])
            if not homes:
                _LOGGER.error("No homes found in Tibber data")
                return

            price_info = (
                homes[0].get("currentSubscription", {}).get("priceInfo", {})
            )

            prices = []
            for period in ["today", "tomorrow"]:
                period_prices = price_info.get(period, [])
                if period_prices:
                    for p in period_prices:
                        prices.append(
                            {
                                "total": p.get("total", 0),
                                "starts_at": p.get("startsAt", ""),
                                "level": p.get("level", "NORMAL"),
                            }
                        )

            self._prices = prices
            _LOGGER.debug("Fetched %d price entries from Tibber", len(prices))

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching Tibber prices: %s", err)
        except Exception as err:
            _LOGGER.error(
                "Unexpected error fetching prices: %s", err, exc_info=True
            )

    async def _fetch_weather_forecast(self) -> None:
        """Fetch full 24-hour weather forecast from Home Assistant weather entity.

        Extracts per-hour forecasts for:
        - Temperature (°C)
        - Wind speed (m/s)
        - Precipitation (mm/h)
        - Solar radiation / irradiance (W/m²)

        These FORECAST values (not current conditions) are what enable
        true predictive/anticipatory control in the MPC optimizer.
        """
        weather_entity = self._config.get(CONF_WEATHER_ENTITY)
        if not weather_entity:
            _LOGGER.warning("No weather entity configured")
            return

        try:
            result = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {"entity_id": weather_entity, "type": "hourly"},
                blocking=True,
                return_response=True,
            )

            if result and weather_entity in result:
                forecast_data = result[weather_entity].get("forecast", [])
                self._weather_forecast = forecast_data

                # Extract solar radiation forecast if present in weather data
                self._solar_radiation_forecast = []
                for fc in forecast_data:
                    # Some weather integrations provide solar irradiance
                    sr = fc.get("solar_irradiance") or fc.get(
                        "native_solar_irradiance", 0.0
                    )
                    self._solar_radiation_forecast.append(float(sr or 0.0))

                _LOGGER.debug(
                    "Fetched %d weather forecast entries (full 24h+ trajectory: "
                    "temp, wind, rain, solar)",
                    len(forecast_data),
                )
            else:
                _LOGGER.warning(
                    "No forecast data returned for %s", weather_entity
                )

        except Exception as err:
            _LOGGER.warning(
                "Error fetching weather forecast: %s. Using fallback.", err
            )
            state = self.hass.states.get(weather_entity)
            if state:
                try:
                    temp = _as_float(state.attributes.get("temperature"), 5.0)
                    wind = _as_float(
                        state.attributes.get("wind_speed"), 0.0
                    ) * self._wind_speed_scale()
                    self._weather_forecast = [
                        {
                            "datetime": (
                                dt_util.now() + timedelta(hours=i)
                            ).isoformat(),
                            "temperature": temp,
                            "wind_speed": wind,
                            "precipitation": 0.0,
                        }
                        for i in range(48)
                    ]
                    self._solar_radiation_forecast = [0.0] * 48
                except (ValueError, TypeError):
                    pass

    def _solar_forecast_source(self) -> str:
        """Configured irradiance source."""
        return self._config.get(
            CONF_SOLAR_FORECAST_SOURCE, DEFAULT_SOLAR_FORECAST_SOURCE
        )

    def _solar_location(self) -> tuple[float, float] | None:
        """Coordinate to request irradiance for.

        Falls back to the Home Assistant home location so the option works
        without picking a point on the map; a heat pump is nearly always at
        the same place as the installation it belongs to.
        """
        location = self._config.get(CONF_SOLAR_LOCATION)
        if isinstance(location, dict):
            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat is not None and lon is not None:
                try:
                    return float(lat), float(lon)
                except (TypeError, ValueError):
                    _LOGGER.warning(
                        "Ignoring malformed solar location %s", location
                    )

        lat = getattr(self.hass.config, "latitude", None)
        lon = getattr(self.hass.config, "longitude", None)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)

    async def _fetch_solar_forecast(self) -> None:
        """Refresh Open-Meteo irradiance when that source is selected."""
        if self._solar_forecast_source() != SOLAR_SOURCE_OPEN_METEO:
            self._open_meteo = None
            return

        location = self._solar_location()
        if location is None:
            _LOGGER.warning(
                "Open-Meteo solar is selected but no coordinate is available; "
                "set one in the integration options or configure the Home "
                "Assistant home location"
            )
            self._open_meteo = None
            return

        latitude, longitude = location
        # Rebuild on a coordinate change so an edited location takes effect
        # instead of serving cached irradiance for the previous place.
        if self._open_meteo is None or not self._open_meteo.matches(
            latitude, longitude
        ):
            self._open_meteo = OpenMeteoSolar(self.hass, latitude, longitude)

        await self._open_meteo.async_refresh(dt_util.utcnow())

    def _solar_forecast_view(self, hours: int = 48) -> list[dict[str, Any]]:
        """Upcoming irradiance as timestamped points, for sensor attributes."""
        if self._open_meteo is None or not self._open_meteo.forecast:
            return []

        series = self._open_meteo.forecast
        now = dt_util.utcnow()
        horizon = now + timedelta(hours=hours)
        points: list[dict[str, Any]] = []
        for t, value in zip(series.times, series.values):
            if t < now or t > horizon:
                continue
            points.append(
                {
                    # Timestamps mark the end of each averaging interval, so
                    # report the interval start, which is what a chart wants.
                    "t": (t - series.resolution).isoformat(),
                    "ghi": round(value, 1),
                }
            )
        return points

    def _wind_speed_scale(self) -> float:
        """Factor converting the weather entity's wind unit into m/s.

        Home Assistant converts forecast wind speed into whichever unit the
        user has configured, and reports that unit on the weather entity as
        ``wind_speed_unit``. An unrecognised unit falls back to 1.0 (m/s),
        which is the Home Assistant metric default.
        """
        entity_id = self._config.get(CONF_WEATHER_ENTITY)
        if not entity_id:
            return 1.0
        state = self.hass.states.get(entity_id)
        if state is None:
            return 1.0
        unit = state.attributes.get("wind_speed_unit")
        scale = _WIND_UNIT_TO_MS.get(unit)
        if scale is None:
            if unit:
                _LOGGER.debug(
                    "Unknown wind speed unit %r on %s; assuming m/s",
                    unit,
                    entity_id,
                )
            return 1.0
        return scale

    def _prepare_forecast_data(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare full 24-hour forecast arrays for the optimizer.

        CRITICAL: This provides the FORECAST TRAJECTORIES (not just current values)
        that enable true predictive optimization. Each array contains per-step
        forecasted values for the entire optimization horizon.

        Returns: (prices, outdoor_temps, wind_speeds, precipitation, solar_radiation)
        """
        dt_minutes = 15
        n_steps = self._opt_config.n_steps
        now = dt_util.now()

        # --- Prices ---
        prices_15min = []
        if self._prices:
            for price_entry in self._prices:
                total = _as_float(price_entry.get("total"), 0.0)
                for _ in range(4):
                    prices_15min.append(total)
        else:
            # Without real prices there is nothing to arbitrage against.
            # Inventing a flat curve here used to let the optimizer run and
            # report a savings figure that no price data supported, so the
            # caller is left to skip the run instead.
            _LOGGER.warning(
                "No electricity price data available; skipping optimization "
                "until prices can be fetched"
            )
            empty = np.array([], dtype=float)
            return (empty, empty, empty, empty, empty)

        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        minutes_since_midnight = (now - midnight).total_seconds() / 60
        step_offset = int(minutes_since_midnight / dt_minutes)

        if step_offset < len(prices_15min):
            prices = prices_15min[step_offset : step_offset + n_steps]
        else:
            prices = prices_15min[:n_steps]

        while len(prices) < n_steps:
            prices.append(prices[-1] if prices else 0.5)

        # --- Weather forecast (FULL 24h trajectories) ---
        outdoor_temps = []
        wind_speeds = []
        precipitation_rates = []
        solar_rad = []

        if self._weather_forecast:
            wind_scale = self._wind_speed_scale()
            for idx, fc in enumerate(self._weather_forecast):
                temp = _as_float(fc.get("temperature"), 5.0)
                # Convert using the unit the weather entity actually reports in.
                # Guessing from the magnitude misreads a moderate 20 km/h breeze
                # as a 20 m/s storm and inflates predicted heat loss twofold.
                wind = max(0.0, _as_float(fc.get("wind_speed"), 0.0) * wind_scale)
                precip = max(0.0, _as_float(fc.get("precipitation"), 0.0))

                # Solar radiation: from forecast or from separate list
                sr = 0.0
                if idx < len(self._solar_radiation_forecast):
                    sr = _as_float(self._solar_radiation_forecast[idx], 0.0)
                if sr == 0.0:
                    sr = _as_float(
                        fc.get("solar_irradiance")
                        or fc.get("native_solar_irradiance"),
                        0.0,
                    )
                sr = max(0.0, sr)

                # Interpolate hourly forecast to 15-min steps
                for _ in range(4):
                    outdoor_temps.append(temp)
                    wind_speeds.append(wind)
                    precipitation_rates.append(precip)
                    solar_rad.append(sr)
        else:
            # Fallback: use current conditions (NOT ideal for predictive MPC)
            base_temp = self._current_state.outdoor_temperature
            current_sr = self._solar_radiation
            _LOGGER.warning(
                "No weather forecast available — using current conditions. "
                "Predictive optimization will be limited."
            )
            for _ in range(n_steps):
                outdoor_temps.append(base_temp)
                wind_speeds.append(0.0)
                precipitation_rates.append(0.0)
                solar_rad.append(current_sr)

        # Open-Meteo irradiance, aligned by wall-clock time rather than by
        # position in the weather forecast list. The positional path above
        # assumes the weather entity's first forecast entry is the current
        # hour, which is not guaranteed; an irradiance series carries its own
        # timestamps, so match on those instead.
        if self._open_meteo is not None and self._open_meteo.available:
            step = timedelta(minutes=dt_minutes)
            aligned: list[float] = []
            missing = 0
            for i in range(n_steps):
                step_start = midnight + timedelta(
                    minutes=dt_minutes * (step_offset + i)
                )
                value = self._open_meteo.irradiance_for(step_start, step)
                if value is None:
                    # Past the end of the published horizon: keep whatever the
                    # weather entity offered rather than asserting darkness.
                    missing += 1
                    value = solar_rad[i] if i < len(solar_rad) else 0.0
                aligned.append(max(0.0, value))
            solar_rad = aligned
            if missing:
                _LOGGER.debug(
                    "Open-Meteo irradiance covered %d/%d steps; the rest fell "
                    "back to the weather entity",
                    n_steps - missing,
                    n_steps,
                )

        # Pad to ensure we have enough data points
        for arr in [outdoor_temps, wind_speeds, precipitation_rates, solar_rad]:
            while len(arr) < n_steps:
                arr.append(arr[-1] if arr else 0.0)

        return (
            np.array(prices[:n_steps], dtype=float),
            np.array(outdoor_temps[:n_steps], dtype=float),
            np.array(wind_speeds[:n_steps], dtype=float),
            np.array(precipitation_rates[:n_steps], dtype=float),
            np.array(solar_rad[:n_steps], dtype=float),
        )

    def _get_current_price(self) -> float:
        """Get the current electricity price."""
        if not self._prices:
            return 0.0

        now = dt_util.now()
        for price_entry in self._prices:
            starts_at = price_entry.get("starts_at", "")
            if starts_at:
                try:
                    ts = datetime.fromisoformat(starts_at)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts <= now < ts + timedelta(hours=1):
                        return price_entry.get("total", 0)
                except (ValueError, TypeError):
                    continue

        return self._prices[0].get("total", 0) if self._prices else 0.0

    async def async_publish_ecl110_command(
        self,
        displace_value: float,
        heat_pump_on: bool,
        reason: str = "optimizer",
    ) -> None:
        """Publish ECL110 displace command via direct `/set` topic and optional legacy JSON topic."""
        displace = float(
            np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max)
        )
        displace_int = int(round(displace))

        legacy_payload = {
            "source": DOMAIN,
            "reason": reason,
            "timestamp": dt_util.now().isoformat(),
            "command": {
                "type": "ecl110_control",
                "heat_pump_on": bool(heat_pump_on),
                "displace": displace_int,
            },
            "context": {
                "price": self._current_action.get("price"),
                "mode": self._current_action.get("mode"),
                "pre_heat_urgency": self._current_action.get("pre_heat_urgency"),
            },
        }

        self._ecl110_last_payload = legacy_payload
        self._ecl110_current_displace = float(displace_int)

        if not self._ecl110_displace_set_topic and not self._ecl110_command_topic:
            return

        # Preferred path: write plain numeric payload directly to /set topic.
        if self._ecl110_displace_set_topic:
            try:
                await self.hass.services.async_call(
                    "mqtt",
                    "publish",
                    {
                        "topic": self._ecl110_displace_set_topic,
                        "payload": str(displace_int),
                        "qos": int(self._ecl110_qos),
                        "retain": bool(self._ecl110_retain),
                    },
                    blocking=True,
                )
            except Exception as err:
                _LOGGER.error("Error publishing ECL110 direct displace MQTT command: %s", err)

        # Backward compatibility path: optional legacy JSON command topic.
        if self._ecl110_command_topic:
            try:
                await self.hass.services.async_call(
                    "mqtt",
                    "publish",
                    {
                        "topic": self._ecl110_command_topic,
                        "payload": json.dumps(legacy_payload),
                        "qos": int(self._ecl110_qos),
                        "retain": bool(self._ecl110_retain),
                    },
                    blocking=True,
                )
            except Exception as err:
                _LOGGER.error("Error publishing ECL110 legacy MQTT command: %s", err)

    async def async_publish_current_action(self, reason: str = "optimizer") -> None:
        """Publish MQTT command for the currently selected optimizer action."""
        if not self._current_action:
            return
        await self.async_publish_ecl110_command(
            displace_value=float(self._current_action.get("displace_value", 0.0)),
            heat_pump_on=bool(self._current_action.get("heat_pump_on", False)),
            reason=reason,
        )

    async def _apply_action(self) -> None:
        """Apply current action as (heat_pump_on, displace_value)."""
        if not self._current_action:
            return

        heat_pump_on = bool(self._current_action.get("heat_pump_on", False))

        # 1) Toggle heat pump supply (ON/OFF)
        switch_entity = self._config.get(CONF_HEAT_PUMP_SWITCH_ENTITY)
        if switch_entity:
            try:
                await self.hass.services.async_call(
                    "switch",
                    "turn_on" if heat_pump_on else "turn_off",
                    {"entity_id": switch_entity},
                    blocking=True,
                )
            except Exception as err:
                _LOGGER.error("Error toggling heat pump switch: %s", err)

        # 2) Publish ECL110 displace command
        await self.async_publish_current_action(reason="scheduled_update")
    def _build_data_dict(self) -> dict[str, Any]:
        """Build the data dictionary for the coordinator."""
        result = self._optimization_result

        # Compute current solar gain
        current_solar_gain = self._thermal_model.compute_solar_gain(
            self._solar_radiation
        )

        # The optimizer may derive demand windows from the learned usage profile
        # when the user has not configured any, so prefer what it actually
        # planned against.
        planned_windows = (
            (result.predictive_info or {}).get("dhw_windows") if result else None
        )
        data = {
            "mode": self._mode,
            "current_action": self._current_action,
            "current_price": self._get_current_price(),
            "indoor_temperature": self._current_state.room_temperature,
            "outdoor_temperature": self._current_state.outdoor_temperature,
            "slab_temperature": self._current_state.slab_temperature,
            "upper_floor_temperature": self._current_state.upper_floor_temperature,
            "lower_floor_temperature": self._current_state.lower_floor_temperature,
            "buffer_tank_temperature": self._current_state.buffer_tank_temperature,
            "floor_return_temperature": self._floor_return_temp,
            "solar_radiation": self._solar_radiation,
            "solar_heat_gain": current_solar_gain,
            "solar_source": self._solar_forecast_source(),
            "solar_forecast": self._solar_forecast_view(),
            "solar_diagnostics": (
                self._open_meteo.diagnostics() if self._open_meteo else None
            ),
            "two_zone_enabled": self._thermal_params.two_zone_enabled,
            "dhw_enabled": self._thermal_params.dhw_enabled,
            "dhw_temperature": self._dhw_temperature or self._current_state.dhw_temperature,
            "dhw_setpoint": self._thermal_params.dhw_setpoint,
            "dhw_min_temperature": self._thermal_params.dhw_min_temp,
            "dhw_usage_profile": self._dhw_hourly_profile,
            "dhw_cooling_rate": round(self._dhw_cooling_rate, 3),
            "dhw_cooling_samples": self._dhw_cooling_samples,
            "dhw_cooling_rate_learned": self._dhw_cooling_samples > 0,
            "buffer_cooling_rate": self._buffer_cooling_rate,
            "buffer_cooling_samples": self._buffer_cooling_samples,
            "buffer_cooling_rate_learned": self._buffer_cooling_samples > 0,
            "house_heat_loss_scale": self._house_heat_loss_scale,
            "house_heat_loss_samples": self._house_heat_loss_samples,
            "house_heat_loss_learned": self._house_heat_loss_samples > 0,
            "house_heat_loss_effective": self._effective_house_heat_loss(),
            "dhw_hold_hours": round(self._thermal_model.dhw_hold_hours(), 1),
            "dhw_windows": planned_windows
            or format_windows(self._thermal_params.dhw_demand_windows),
            "dhw_schedule_enabled": self._thermal_params.dhw_schedule_enabled,
            "dhw_in_demand_window": self._dhw_in_demand_window(),
            "dhw_next_window_in_hours": self._dhw_next_window_in_hours(),
            "dhw_idle_min_temperature": self._thermal_params.dhw_idle_min_temp,
            "dhw_legionella_enabled": self._thermal_params.dhw_legionella_enabled,
            "dhw_legionella_due_in_hours": self._dhw_legionella_due_in_hours(),
            "last_optimization": self._last_optimization,
            "next_optimization": self._next_optimization,
            "prices_available": len(self._prices),
            "weather_forecast_available": len(self._weather_forecast),
            "ecl110_command_topic": self._ecl110_command_topic,
            "ecl110_state_topic": self._ecl110_state_topic,
            "ecl110_displace": self._current_action.get("displace_value", self._ecl110_current_displace),
            "ecl110_effective_displace": self._current_state.ecl110_effective_displace,
            "ecl110_last_payload": self._ecl110_last_payload,
        }

        if result:
            # DHW schedule data
            dhw_schedule = []
            if result.dhw_power_schedule:
                for i, (ts, dp, dt_val) in enumerate(zip(
                    result.timestamps[:24],
                    result.dhw_power_schedule[:24],
                    result.dhw_temp_trajectory[1:25] if result.dhw_temp_trajectory else [0.0] * 24,
                )):
                    dhw_schedule.append({
                        "time": ts.isoformat(),
                        "dhw_power": round(dp, 2),
                        "dhw_temp": round(dt_val, 1),
                    })

            data.update(
                {
                    "predicted_cost": result.predicted_cost,
                    "baseline_cost": result.baseline_cost,
                    "predicted_savings": result.predicted_savings,
                    "savings_percentage": result.savings_percentage,
                    "deferred_energy_cost": result.deferred_energy_cost,
                    "optimization_status": result.status,
                    "solve_time_ms": result.solve_time_ms,
                    "dhw_heating_cost": result.dhw_heating_cost,
                    "dhw_heating_active": self._current_action.get("dhw_heating_active", False),
                    "dhw_schedule": dhw_schedule,
                    # Predictive info. Numpy scalars are converted to plain
                    # Python types because these values end up in entity
                    # attributes, which Home Assistant must serialize.
                    "predictive_info": _plain_types(result.predictive_info),
                    **self._build_plan_views(result),
                    "schedule": [
                        {
                            "time": ts.isoformat(),
                            "power": p,
                            "setpoint": s,
                            "price": pr,
                            "room_temp": rt,
                            "upper_temp": ut,
                            "lower_temp": lt,
                            "solar_gain": sg,
                            "displace": (
                                result.displace_schedule[idx]
                                if result.displace_schedule and idx < len(result.displace_schedule)
                                else 0.0
                            ),
                            "heat_pump_on": (
                                result.heat_pump_on_schedule[idx]
                                if result.heat_pump_on_schedule and idx < len(result.heat_pump_on_schedule)
                                else p > 0.1
                            ),
                        }
                        for idx, (ts, p, s, pr, rt, ut, lt, sg) in enumerate(zip(
                            result.timestamps[:24],
                            result.power_schedule[:24],
                            result.optimal_setpoints[:24],
                            result.prices[:24],
                            result.room_temp_trajectory[1:25],
                            (
                                result.upper_temp_trajectory[1:25]
                                if result.upper_temp_trajectory
                                else result.room_temp_trajectory[1:25]
                            ),
                            (
                                result.lower_temp_trajectory[1:25]
                                if result.lower_temp_trajectory
                                else result.room_temp_trajectory[1:25]
                            ),
                            (
                                result.solar_gain_trajectory[:24]
                                if result.solar_gain_trajectory
                                else [0.0] * 24
                            ),
                        ))
                    ],
                }
            )
        else:
            data.update(
                {
                    "predicted_cost": None,
                    "baseline_cost": None,
                    "predicted_savings": None,
                    "savings_percentage": None,
                    "deferred_energy_cost": None,
                    "optimization_status": "not_run",
                    "solve_time_ms": 0,
                    "dhw_heating_cost": 0.0,
                    "dhw_heating_active": False,
                    "dhw_schedule": [],
                    "predictive_info": {},
                    "schedule": [],
                    "space_plan": {},
                    "dhw_plan": {},
                }
            )

        return data