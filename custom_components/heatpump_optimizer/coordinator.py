"""Data coordinator for Heat Pump Cost Optimizer.

The coordinator manages:
1. Fetching electricity prices from Tibber API
2. Fetching weather forecasts from Home Assistant weather entities
3. Fetching solar radiation, floor return temperature, and DHW temperature
4. Running the MPC optimization (with predictive weather anticipation + DHW)
5. Applying optimization results to heat pump control
"""
from __future__ import annotations

import json
import logging
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, NamedTuple

import aiohttp
import numpy as np

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_TIBBER_TOKEN,
    CONF_WEATHER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
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
    CONF_TARGET_TEMP,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_COMFORT_TEMP_DAY,
    CONF_COMFORT_TEMP_NIGHT,
    CONF_DAY_START_HOUR,
    CONF_DAY_END_HOUR,
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
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_COMFORT_WEIGHT,
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
    MODE_AUTO,
    MODE_COMFORT,
    MODE_ECONOMY,
    MODE_OFF,
    MODE_BOOST,
    CONF_SOLAR_FORECAST_SOURCE,
    CONF_SOLAR_LOCATION,
    DEFAULT_SOLAR_FORECAST_SOURCE,
    SOLAR_SOURCE_OPEN_METEO,
    CONF_POWER_ENTITY,
    CONF_ENERGY_ENTITY,
    CONF_HOUSE_POWER_ENTITY,
    CONF_COP_SCALE,
    COP_SCALE_MAX,
    COP_SCALE_MIN,
    DEFAULT_COP_SCALE,
    CONF_STALENESS_ENABLED,
    CONF_STALENESS_SCALE,
    DEFAULT_STALENESS_ENABLED,
    DEFAULT_STALENESS_SCALE,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_EXTERNAL_HEAT_MIN_RISE,
    CONF_EXTERNAL_HEAT_DECAY_MINUTES,
    DEFAULT_EXTERNAL_HEAT_ENABLED,
    DEFAULT_EXTERNAL_HEAT_MIN_RISE,
    DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
    CONF_PRICE_PRIOR_ENABLED,
    DEFAULT_PRICE_PRIOR_ENABLED,
    PRICE_MODEL_STORE_VERSION,
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
    ACCURACY_STORE_VERSION,
    ENERGY_STORE_VERSION,
    SIMULATE_MIN_INTERVAL_SECONDS,
)
from .inputs import InputHealth, InputReader, stale_summary
from .external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
)
from . import away as away_mode
from . import battery as battery_view
from . import pv as pv_model
from .accuracy import AccuracySample, AccuracyTracker, delivered_ratio
from .comfort_learning import ComfortLearner, OverrideEvent
from .defrost import DefrostDerate
from .price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
)
from .sysid import SysIdConfig, SystemIdentification
from .tariff import CapacityTariff, PeakTracker
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

#: Resolution the optimizer plans at, and therefore the resolution every
#: forecast series is resampled to.
FORECAST_STEP_MINUTES = 15


class ForecastArrays(NamedTuple):
    """The horizon, as the optimizer sees it.

    A NamedTuple rather than a dataclass so the seven series stay indexable
    for the callers that slice them, while everything else can use the names
    instead of remembering that position five is the price provenance mask.
    """

    #: *Marginal* prices: the export compensation replaces the import price
    #: wherever PV surplus exists, because that is what consuming costs there.
    prices: np.ndarray
    outdoor_temps: np.ndarray
    wind_speeds: np.ndarray
    precipitation: np.ndarray
    solar_radiation: np.ndarray
    #: True where the price came from published market data rather than the
    #: learned diurnal prior.
    price_known: np.ndarray
    pv_surplus: np.ndarray

    @classmethod
    def empty(cls) -> "ForecastArrays":
        """No usable horizon, so the caller should skip the run."""
        blank = np.array([], dtype=float)
        return cls(blank, blank, blank, blank, blank, blank, blank)


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

# COP learning. Slower than the house-loss learner because a single interval's
# ratio of commanded to measured power is noisy: compressor start transients,
# defrost cycles and any auxiliary heater all land in the measurement.
COP_LEARNING_ALPHA = 0.03
COP_LEARNING_MAX_STEP = 0.05

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
        """Initialize the coordinator.

        The list below is the whole story: what state this object owns, in the
        order it comes into existence. Previously this was two hundred and
        fifty lines of uninterrupted assignment in which nothing had a natural
        home, so a new attribute went wherever the last one happened to end.
        """
        self.entry = entry
        self._config = {**entry.data, **entry.options}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=self._config.get(
                    CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                )
            ),
        )

        self._init_model()
        self._init_runtime_state()
        self._init_dhw_learning(hass, entry)
        self._init_measurements()
        self._init_grid(hass, entry)
        self._init_features(hass, entry)
        self._init_ecl110()

        # Deferred: MQTT may not be up yet, and the stores are on disk.
        hass.async_create_task(self._async_setup_ecl110_state_subscription())
        for load in (
            self._async_load_dhw_profile,
            self._async_load_dhw_legionella,
            self._async_load_thermal_learning,
            self._async_load_price_model,
            self._async_load_accuracy,
            self._async_load_energy_totals,
        ):
            hass.async_create_task(load())

    # -- construction, one concern at a time ---------------------------------

    def _init_model(self) -> None:
        """The thermal model, the optimizer, and the configuration between."""
        self._thermal_params = ThermalParameters.from_config(self._config)
        self._thermal_model = ThermalModel(self._thermal_params)

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
        self._optimizer = HeatPumpOptimizer(self._thermal_model, self._opt_config)

    def _init_runtime_state(self) -> None:
        """What the current update cycle is working with."""
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

        # Solar irradiance and the floor return temperature sensor.
        self._solar_radiation: float = 0.0
        self._floor_return_temp: float | None = None
        self._solar_radiation_forecast: list[float] = []
        self._open_meteo: OpenMeteoSolar | None = None

        # A run takes seconds, so a user tapping the button repeatedly must not
        # be able to stack solves on top of each other.
        self._optimization_running: bool = False

    def _init_dhw_learning(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Hot water: usage profile, cooling rate and the legionella timer."""
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

    def _init_measurements(self) -> None:
        """Optional measured inputs and the COP correction they feed."""
        # --- Measured electrical draw (optional) -------------------------
        # Absent on most installs, so every consumer must degrade cleanly.
        self._measured_power: float | None = None
        self._measured_house_power: float | None = None
        self._measured_energy: float | None = None
        # Learned correction to the modelled COP, from measured input against
        # modelled thermal output. Only moves when a power entity exists.
        self._cop_scale: float = float(
            self._config.get(CONF_COP_SCALE, DEFAULT_COP_SCALE)
        )
        self._cop_samples: int = 0
        self._last_measured_cop: float | None = None
        self._apply_cop_scale(self._cop_scale)

        # --- Input health -------------------------------------------------
        self._input_health: InputHealth | None = None
        self._learner_freeze_reason: str | None = None

    def _init_grid(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Price modelling, the capacity tariff and PV surplus."""
        # --- Unknown price horizon (item 7) --------------------------------
        self._price_model = PriceShapeModel()
        self._price_days_seen: set[str] = set()
        self._price_known_steps: int = 0
        self._price_model_store: Store = Store(
            hass,
            PRICE_MODEL_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_price_model",
        )

        # --- Capacity tariff (item 8) --------------------------------------
        self._peak_tracker = PeakTracker()

        # --- PV self-consumption (item 9) ----------------------------------
        self._pv_surplus: np.ndarray | None = None
        self._pv_summary: dict[str, Any] = {}
        self._pv_production: float | None = None

    def _init_features(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Away mode, accuracy tracking, learning experiments and totals."""
        self._external_heat = ExternalHeatDetector(self._external_heat_config())
        self._external_heat_active: bool = False
        # --- Away mode (item 13) -------------------------------------------
        self._away_state = away_mode.AwayState()

        # --- Closed-loop accuracy (item 11) --------------------------------
        self._accuracy = AccuracyTracker()
        self._pending_prediction: dict[str, Any] | None = None
        self._accuracy_store: Store = Store(
            hass,
            ACCURACY_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_accuracy",
        )

        # --- Defrost derate (item 14) --------------------------------------
        self._defrost = DefrostDerate()
        self._thermal_params.defrost_derate = self._defrost

        # --- Energy dashboard statistics (item 15) -------------------------
        # Monotonic accumulators, so Home Assistant's Energy dashboard can pick
        # them up as TOTAL_INCREASING.
        self._energy_totals: dict[str, float] = {
            "space_energy_kwh": 0.0,
            "dhw_energy_kwh": 0.0,
            "total_energy_kwh": 0.0,
            "space_cost": 0.0,
            "dhw_cost": 0.0,
            "total_cost": 0.0,
        }
        self._last_energy_sample: datetime | None = None
        self._energy_store: Store = Store(
            hass,
            ENERGY_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_energy",
        )

        # --- Active system identification (item 18) ------------------------
        self._sysid = SystemIdentification(
            SysIdConfig(
                enabled=bool(
                    self._config.get(CONF_SYSID_ENABLED, DEFAULT_SYSID_ENABLED)
                )
            )
        )

        # --- Revealed-preference comfort tuning (item 19) ------------------
        configured_weight = _as_float(
            self._config.get(CONF_COMFORT_WEIGHT), DEFAULT_COMFORT_WEIGHT
        )
        self._comfort_learner = ComfortLearner(
            configured_weight=configured_weight,
            learned_weight=configured_weight,
        )
        self._last_manual_setpoint: float | None = None

        # --- What-if simulator (item 21) -----------------------------------
        self._last_simulation: datetime | None = None
        self._simulation_cache: dict[str, Any] = {}

    def _init_ecl110(self) -> None:
        """MQTT heat-curve control state."""
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
        reasons: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Collapse a per-step power schedule into contiguous heating slots.

        The step schedule is what the optimizer produces, but what a person
        wants to see is "the pump runs from 02:00 to 04:30 and that costs 4.20".
        Consecutive steps above ``threshold`` kW are merged into one slot and
        summarised with their energy, average price and cost.

        Each slot also carries the reason code that dominates it, so an
        unexpected slot is no longer indistinguishable from a bug.
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
            slot = {
                "start": timestamps[start_idx].isoformat(),
                "end": end_ts.isoformat(),
                "duration_hours": round(duration, 2),
                "avg_power_kw": round(energy / duration, 2) if duration else 0.0,
                "energy_kwh": round(energy, 3),
                "avg_price": (round(cost / energy, 4) if energy > 1e-9 else 0.0),
                "cost": round(cost, 2),
            }
            if reasons:
                codes = [
                    reasons[i]
                    for i in span
                    if i < len(reasons) and reasons[i] != "idle"
                ]
                if codes:
                    # The most frequent code within the slot, which reads
                    # better than a list when a slot spans two motivations.
                    slot["reason"] = max(set(codes), key=codes.count)
                    slot["reasons"] = sorted(set(codes))
            slots.append(slot)

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

        space_slots = self._plan_slots(
            timestamps,
            raw_space,
            raw_prices,
            dt_hours,
            reasons=result.space_reasons,
        )
        dhw_slots = self._plan_slots(
            timestamps,
            raw_dhw,
            raw_prices,
            dt_hours,
            reasons=result.dhw_reasons,
        )

        def reason_at(codes: list[str], index: int) -> str | None:
            return codes[index] if codes and index < len(codes) else None

        known = result.price_known or []

        def price_known_at(index: int) -> bool:
            return bool(known[index]) if index < len(known) else True

        surplus = result.pv_surplus or []

        def surplus_at(index: int) -> float | None:
            return surplus[index] if index < len(surplus) else None

        space_forecast = [
            {
                "t": timestamps[i].isoformat(),
                "price": prices[i],
                # Marks where the plan rests on the learned diurnal prior
                # rather than on published market data.
                "price_known": price_known_at(i),
                "outdoor": outdoor[i],
                "space_power": space_power[i],
                "room": room[i],
                "upper": upper[i],
                "lower": lower[i],
                "reason": reason_at(result.space_reasons, i),
                "pv_surplus": surplus_at(i),
            }
            for i in range(n)
        ]
        dhw_forecast = [
            {
                "t": timestamps[i].isoformat(),
                "price": prices[i],
                "price_known": price_known_at(i),
                "outdoor": outdoor[i],
                "dhw_power": dhw_power[i],
                "dhw_temp": dhw_temp[i],
                "reason": reason_at(result.dhw_reasons, i),
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

    # ------------------------------------------------------------------
    # Measured power, COP learning and external heat detection
    # ------------------------------------------------------------------

    def _commanded_power(self) -> float:
        """Total electrical draw the plan is asking of the heat pump, kW.

        ``current_action["power"]`` is the *space heating* allocation and
        ``dhw_power`` is the hot water one; the compressor serves them one at a
        time but a meter sees only their sum. Comparing the space figure alone
        against a measured total makes a planned hot-water charge look like the
        pump drawing power it was never asked for — which reads as an external
        heat source, as a collapsed COP, and as a defrost derate, all at once.
        """
        action = self._current_action
        return float(action.get("power", 0.0)) + float(action.get("dhw_power", 0.0))

    def _external_heat_config(self) -> ExternalHeatConfig:
        """Build the detector configuration from the config entry."""
        return ExternalHeatConfig(
            enabled=bool(
                self._config.get(
                    CONF_EXTERNAL_HEAT_ENABLED, DEFAULT_EXTERNAL_HEAT_ENABLED
                )
            ),
            min_rise_c_per_h=_as_float(
                self._config.get(CONF_EXTERNAL_HEAT_MIN_RISE),
                DEFAULT_EXTERNAL_HEAT_MIN_RISE,
            ),
            decay_minutes=_as_float(
                self._config.get(CONF_EXTERNAL_HEAT_DECAY_MINUTES),
                DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
            ),
        )

    def _apply_cop_scale(self, scale: float) -> None:
        """Clamp the learned COP correction and push it to the model."""
        self._cop_scale = float(np.clip(scale, COP_SCALE_MIN, COP_SCALE_MAX))
        self._thermal_params.cop_scale = self._cop_scale

    def _max_pump_rise(self, tank: str) -> float | None:
        """Fastest the heat pump alone could warm a tank, °C/h.

        Used to recognise an external source even while the compressor runs:
        no heat pump can outrun its own thermal output into a known volume.
        """
        params = self._thermal_params
        cop = self._thermal_model.compute_cop(
            self._current_state.outdoor_temperature
        )
        thermal_kw = params.max_electrical_power * max(cop, 1.0)
        if tank == "dhw":
            capacity = params.dhw_tank_thermal_mass
        else:
            capacity = params.buffer_tank_thermal_mass
        if capacity <= 1e-6:
            return None
        return thermal_kw / capacity

    def _external_heat_override(self) -> bool | None:
        """State of a user-provided stove/flue entity, if one is configured."""
        entity_id = self._config.get(CONF_EXTERNAL_HEAT_ENTITY)
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        raw = str(getattr(state, "state", "")).lower()
        if raw in ("unknown", "unavailable", ""):
            return None
        if raw in ("on", "true", "home", "open", "heat", "detected"):
            return True
        if raw in ("off", "false", "not_home", "closed", "clear"):
            return False
        # A numeric entity (a flue temperature, say) counts as active when it
        # reads above freezing-ish; anything else is not interpretable.
        try:
            return float(raw) > 30.0
        except ValueError:
            return None

    def _update_external_heat_detection(self) -> None:
        """Fold this interval's observation into the external-heat detector."""
        self._external_heat.config = self._external_heat_config()
        observation = ExternalHeatObservation(
            now=dt_util.now(),
            dhw_temp=self._current_state.dhw_temperature,
            buffer_temp=self._current_state.buffer_tank_temperature,
            commanded_power_kw=self._commanded_power(),
            measured_power_kw=self._measured_power,
            dhw_max_rise_c_per_h=self._max_pump_rise("dhw"),
            buffer_max_rise_c_per_h=self._max_pump_rise("buffer"),
            override=self._external_heat_override(),
        )
        state = self._external_heat.update(observation)
        self._external_heat_active = self._external_heat.suppressing
        if state.active:
            _LOGGER.debug(
                "External heat source active (%s): %s",
                state.source,
                "; ".join(state.evidence),
            )

    def _learn_measured_cop(self) -> None:
        """Compare measured electrical input with modelled thermal output.

        Without a power entity the COP is a curve fitted to a nameplate figure,
        and since every plan is priced through it, an error there is an error
        in every cost the integration reports. With one, COP becomes an
        observable and can join the other learners.

        Only intervals where the pump is genuinely running carry information;
        at low duty the measured average is dominated by standby draw.
        """
        if self._measured_power is None:
            return
        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY):
            return

        commanded = self._commanded_power()
        params = self._thermal_params
        # Below a third of nameplate the reading is mostly auxiliaries and the
        # ratio says little about compressor efficiency.
        floor = max(0.3 * params.max_electrical_power, 0.2)
        if commanded < floor or self._measured_power < floor:
            return

        modelled_cop = self._thermal_model.compute_cop(
            self._current_state.outdoor_temperature
        )
        if modelled_cop <= 0.1:
            return

        # The thermal output the plan intended is commanded power times the
        # modelled COP; delivering that with a different electrical input means
        # the real COP differs by the ratio of the two inputs.
        observed_cop = modelled_cop * commanded / self._measured_power
        if not np.isfinite(observed_cop) or observed_cop <= 0.1:
            return
        self._last_measured_cop = round(float(observed_cop), 2)

        # ``cop_scale`` multiplies the *nameplate* curve, and ``modelled_cop``
        # already has the current scale folded in. So the new absolute scale is
        # the current one times the observed correction, not the correction on
        # its own — using the ratio alone makes 1.0 the only fixed point, and a
        # sample that perfectly confirms the model would still drag the learned
        # value back towards "trust the nameplate".
        target_scale = self._cop_scale * commanded / self._measured_power
        alpha = COP_LEARNING_ALPHA
        new_scale = (1.0 - alpha) * self._cop_scale + alpha * target_scale
        max_step = self._cop_scale * COP_LEARNING_MAX_STEP
        new_scale = float(
            np.clip(
                new_scale,
                self._cop_scale - max_step,
                self._cop_scale + max_step,
            )
        )
        self._apply_cop_scale(new_scale)
        self._cop_samples += 1
        _LOGGER.debug(
            "Learned COP: commanded %.2f kW drew %.2f kW, implying COP %.2f "
            "against a modelled %.2f; scale now %.3f (%d samples)",
            commanded,
            self._measured_power,
            observed_cop,
            modelled_cop,
            self._cop_scale,
            self._cop_samples,
        )

    def _input_health_view(self) -> dict[str, Any]:
        """Diagnostics for the input watchdog, published as entity attributes."""
        health = self._input_health
        if health is None:
            return {
                "input_health": "unknown",
                "stale_inputs": [],
                "input_problems": [],
                "input_ages_minutes": {},
                "learners_frozen": False,
                "learner_freeze_reason": None,
            }
        reason = self._learner_freeze_reason
        return {
            "input_health": stale_summary(health),
            "stale_inputs": health.stale_keys,
            "input_problems": health.details(),
            "input_ages_minutes": health.ages(),
            "learners_frozen": reason is not None,
            "learner_freeze_reason": reason,
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

        # An interval that is only *partly* externally heated does not look
        # like an outlier — it looks like a tank that cooled unusually slowly,
        # and BUFFER_COOLING_ALPHA_UP absorbs it rather than rejecting it. So
        # this learner in particular has to be told, not left to infer.
        frozen = self._learning_frozen(CONF_BUFFER_TANK_TEMP_ENTITY)
        if frozen:
            self._learner_freeze_reason = frozen
            return

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

        frozen = self._learning_frozen(
            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY
        )
        if frozen:
            self._learner_freeze_reason = frozen
            return

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

        frozen = self._learning_frozen(CONF_DHW_TEMP_ENTITY)
        if frozen:
            self._learner_freeze_reason = frozen
            return

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

            # Fold any newly complete price day into the learned diurnal shape,
            # which is what fills the horizon past the published data.
            await self._async_learn_price_shape()

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

            # Close the loop: pair the previous interval's prediction with what
            # actually happened, accumulate energy, and train the derate.
            self._record_accuracy()
            self._track_realised_peak()
            await self._async_save_accuracy()
            await self._async_save_energy_totals()

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

        if self._optimization_running:
            _LOGGER.debug("An optimization is already in flight; skipping")
            return

        self._optimization_running = True
        away_original: dict[str, float] | None = None
        try:
            horizon = self._forecast_arrays()
            prices = horizon.prices

            if len(prices) < 4:
                _LOGGER.warning(
                    "Not enough price data for optimization (got %d steps)",
                    len(prices),
                )
                return

            _LOGGER.debug(
                "Forecast data: %d steps (%d from published prices), wind "
                "range=%.1f-%.1f m/s, precip range=%.1f-%.1f mm/h, solar "
                "range=%.0f-%.0f W/m²",
                len(prices),
                int(np.sum(horizon.price_known)),
                float(np.min(horizon.wind_speeds)),
                float(np.max(horizon.wind_speeds)),
                float(np.min(horizon.precipitation)),
                float(np.max(horizon.precipitation)),
                float(np.min(horizon.solar_radiation)),
                float(np.max(horizon.solar_radiation)),
            )

            # Push the grid-cost settings into the optimizer configuration
            # immediately before the solve, so an options change takes effect
            # on the next run rather than on the next restart.
            tariff = self._capacity_tariff()
            self._opt_config.peak_price_per_kw = tariff.marginal_price_per_kw
            self._opt_config.peak_threshold_kw = self._peak_tracker.threshold_kw(
                tariff
            )
            self._opt_config.peak_window_minutes = tariff.window_minutes
            self._opt_config.peak_count = tariff.peaks_averaged
            self._opt_config.baseline_load_kw = self._baseline_house_load(
                len(prices)
            )
            self._opt_config.cycling_cost = _as_float(
                self._config.get(CONF_CYCLING_COST), DEFAULT_CYCLING_COST
            )
            self._apply_comfort_weight()

            # Away mode is applied around the solve and unwound afterwards, so
            # a setback can never leak past the end of the holiday.
            self._resolve_away()
            away_original = self._apply_away_setback()

            self._current_state.external_heat_active = self._external_heat_active

            # Run optimization in executor to avoid blocking
            result = await self.hass.async_add_executor_job(
                self._optimizer.optimize,
                self._current_state,
                horizon.prices,
                horizon.outdoor_temps,
                horizon.wind_speeds,
                horizon.precipitation,
                horizon.solar_radiation,
                dt_util.now(),
                horizon.price_known,
                horizon.pv_surplus,
            )

            self._optimization_result = result
            self._last_optimization = dt_util.now()

            self._current_action = self._optimizer.get_current_action(
                result, dt_util.now()
            )

            # A step-response experiment overrides the plan for its duration.
            self._run_system_identification(prices)
            self._adopt_system_identification()

            self._record_quiet_comfort_period()

            _LOGGER.info(
                "Optimization complete: savings=%.1f%%, cost=%.2f, status=%s, "
                "dhw_enabled=%s, starts=%d, peak=%.1f kW",
                result.savings_percentage,
                result.predicted_cost,
                result.status,
                self._thermal_params.dhw_enabled,
                result.compressor_starts,
                result.projected_peak_kw,
            )

        except Exception as err:
            _LOGGER.error("Optimization failed: %s", err, exc_info=True)
        finally:
            if away_original is not None:
                self._restore_away_setback(away_original)
            self._optimization_running = False

    async def async_set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        self._mode = mode
        _LOGGER.info("Operation mode set to: %s", mode)
        await self.async_request_refresh()

    # Service parameter name -> thermal parameter attribute. Plain assignments
    # only; anything with a side effect is handled explicitly below.
    _THERMAL_PARAM_FIELDS = {
        "house_thermal_mass": "room_thermal_mass",
        "slab_thermal_mass": "slab_thermal_mass",
        "slab_heat_transfer": "slab_heat_transfer",
        "heat_pump_cop_nominal": "cop_nominal",
        "upper_floor_thermal_mass": "upper_floor_thermal_mass",
        "lower_floor_thermal_mass": "lower_floor_thermal_mass",
        "inter_zone_heat_transfer": "inter_zone_transfer",
        "radiator_power_fraction": "radiator_power_fraction",
        "window_area": "window_area",
        "solar_heat_gain_coefficient": "solar_heat_gain_coefficient",
        "dhw_tank_volume": "dhw_tank_volume",
        "dhw_setpoint": "dhw_setpoint",
        "dhw_min_temperature": "dhw_min_temp",
        "dhw_daily_consumption": "dhw_daily_consumption",
        "ecl110_pid_time_constant_hours": "ecl110_pid_time_constant_hours",
        "wind_sensitivity_factor": "wind_sensitivity",
        "rain_heat_loss_multiplier": "rain_heat_loss_multiplier",
    }

    async def async_update_thermal_params(self, params: dict[str, Any]) -> None:
        """Apply a runtime parameter change from the service call.

        Most parameters are a plain assignment and live in the table above.
        The rest are here because they have a consequence beyond themselves —
        a learned correction to invalidate, a mirrored attribute to keep in
        step, or a value that has to be parsed and may fail.
        """
        for name, attribute in self._THERMAL_PARAM_FIELDS.items():
            if name in params:
                setattr(self._thermal_params, attribute, params[name])

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

        if CONF_DHW_COOLING_RATE in params:
            # An explicit value replaces the learned one and resets the sample
            # count, so the learner treats it as the new starting point.
            self._apply_dhw_cooling_rate(float(params[CONF_DHW_COOLING_RATE]))
            self._dhw_cooling_samples = 0
            await self._async_save_dhw_profile()

        # The displace limits are mirrored on the coordinator because the MQTT
        # publisher clamps against them without going through the model.
        for name, attribute in (
            ("ecl110_displace_min", "_ecl110_displace_min"),
            ("ecl110_displace_max", "_ecl110_displace_max"),
        ):
            if name in params:
                setattr(self._thermal_params, name, params[name])
                setattr(self, attribute, params[name])

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

        # The model and optimizer hold the parameters by reference at
        # construction, so both are rebuilt rather than mutated in place.
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
        """Update current thermal state from HA entities.

        Every read goes through :class:`InputReader`, which rejects values that
        are too old as well as ones that are unavailable. That distinction
        matters: a sensor that has silently stopped updating still returns a
        plausible number, and feeding that to the learners corrupts parameters
        that are then persisted.
        """
        reader = InputReader(
            self.hass,
            self._config,
            enabled=bool(
                self._config.get(CONF_STALENESS_ENABLED, DEFAULT_STALENESS_ENABLED)
            ),
            scale=_as_float(
                self._config.get(CONF_STALENESS_SCALE, DEFAULT_STALENESS_SCALE),
                DEFAULT_STALENESS_SCALE,
            ),
        )

        # Indoor temperature
        indoor = reader.read(CONF_INDOOR_TEMP_ENTITY)
        if indoor.ok:
            self._current_state.room_temperature = indoor.value
            # For two-zone: indoor sensor is typically upper floor
            self._current_state.upper_floor_temperature = indoor.value

        # Outdoor temperature
        outdoor = reader.read(CONF_OUTDOOR_TEMP_ENTITY)
        if outdoor.ok:
            self._current_state.outdoor_temperature = outdoor.value

        # Floor heating return temperature sensor
        floor_return_entity = self._config.get(CONF_FLOOR_RETURN_TEMP_ENTITY)
        floor_return = reader.read(CONF_FLOOR_RETURN_TEMP_ENTITY)
        if floor_return.ok:
            self._floor_return_temp = floor_return.value
            self._current_state.floor_return_temperature = self._floor_return_temp
            # Update slab temperature estimate from return temp
            self._thermal_model.update_slab_from_return_temp(
                self._current_state, self._floor_return_temp
            )
            # Lower floor temp ~ return temp (rough estimate)
            self._current_state.lower_floor_temperature = (
                self._floor_return_temp + 0.5
            )

        # Measured electrical draw. Optional, and everything downstream has to
        # degrade cleanly without it, because most installs will not have one.
        power_reading = reader.read_power_kw(CONF_POWER_ENTITY)
        self._measured_power = power_reading.value if power_reading.ok else None
        house_power = reader.read_power_kw(CONF_HOUSE_POWER_ENTITY)
        self._measured_house_power = house_power.value if house_power.ok else None
        energy_reading = reader.read(CONF_ENERGY_ENTITY)
        self._measured_energy = energy_reading.value if energy_reading.ok else None

        # Solar radiation: a local pyranometer measures this house, so it wins
        # over any remote estimate. Open-Meteo fills in when no sensor is
        # configured or the sensor is not reporting.
        solar = reader.read(CONF_SOLAR_RADIATION_ENTITY)
        solar_from_sensor = False
        if solar.ok:
            self._solar_radiation = solar.value
            self._current_state.solar_radiation = self._solar_radiation
            solar_from_sensor = True

        if not solar_from_sensor and self._open_meteo is not None:
            observed = self._open_meteo.current_irradiance(dt_util.utcnow())
            if observed is not None:
                self._solar_radiation = observed
                self._current_state.solar_radiation = observed

        # DHW temperature sensor
        dhw = reader.read(CONF_DHW_TEMP_ENTITY)
        if dhw.ok:
            self._dhw_temperature = dhw.value
            self._current_state.dhw_temperature = self._dhw_temperature

        # Buffer tank temperature sensor (optional; enables cooling learning)
        buffer_reading = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)
        if buffer_reading.ok:
            self._current_state.buffer_tank_temperature = buffer_reading.value

        # The health snapshot has to be complete before any learner runs, since
        # each one consults it to decide whether to freeze.
        self._input_health = reader.health
        self._learner_freeze_reason = None

        # The defrost derate's humidity bucket is resolved from this, so it has
        # to be current before anything calls compute_cop.
        self._thermal_params.ambient_humidity = self._current_humidity()

        # Detect an external heat source before the learners run: while one is
        # active every thermal observation is contaminated, and the learners
        # need to know that rather than quietly absorbing it.
        self._update_external_heat_detection()

        if dhw.ok:
            await self._async_learn_dhw_dynamics(dhw.value)
            await self._async_track_dhw_legionella(dhw.value)

        self._current_state.dhw_hours_since_legionella = (
            self._dhw_hours_since_legionella()
        )

        if buffer_reading.ok:
            await self._async_learn_buffer_cooling(buffer_reading.value)

        # Refine the building fabric model from how the last interval actually
        # went. Runs last so it sees the fully populated state.
        await self._async_learn_house_heat_loss()

        # Observed COP, which is only possible with a measured power entity.
        self._learn_measured_cop()

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

    def _learning_frozen(self, *keys: str) -> str | None:
        """Why learning should be skipped this interval, or ``None``.

        Fail closed. A learner that pauses for an hour loses an hour of
        convergence; a learner that trains on a flatline or on heat it did not
        supply corrupts a parameter that is persisted to disk.
        """
        if self._external_heat_active:
            return "external_heat_source"
        health = self._input_health
        if health is None:
            return None
        for key in keys:
            reading = health.readings.get(key)
            if reading is not None and reading.stale:
                return f"stale:{key}"
        return None

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
        """The five weather/price series, for callers predating the rest."""
        return self._forecast_arrays()[:5]

    def _price_series(
        self, n_steps: int, midnight: datetime, step_offset: int
    ) -> tuple[np.ndarray, np.ndarray] | None:
        """Per-step prices, and a mask of which came from published data.

        Returns ``None`` when there are no prices at all. Inventing a flat
        curve there used to let the optimizer run and report a savings figure
        that no price data supported, so the caller skips the run instead.
        """
        if not self._prices:
            _LOGGER.warning(
                "No electricity price data available; skipping optimization "
                "until prices can be fetched"
            )
            return None

        # Tibber publishes hourly; the optimizer works in quarters.
        quarters: list[float] = []
        for entry in self._prices:
            total = _as_float(entry.get("total"), 0.0)
            quarters.extend([total] * 4)

        if step_offset < len(quarters):
            known = quarters[step_offset : step_offset + n_steps]
        else:
            known = quarters[:n_steps]

        # Past the published horizon, model the shape rather than repeating the
        # last price. A flat tail has no trough, so the optimizer cannot see a
        # cheap period ahead worth waiting for. The mask records which steps
        # rest on the learned prior so that stays visible downstream.
        step_starts = [
            midnight + timedelta(minutes=FORECAST_STEP_MINUTES * (step_offset + i))
            for i in range(n_steps)
        ]
        prices, price_known = extend_price_series(
            known, n_steps, step_starts, self._price_prior()
        )
        self._price_known_steps = int(np.sum(price_known))
        return prices, price_known

    def _weather_series(
        self, n_steps: int
    ) -> tuple[list[float], list[float], list[float], list[float]]:
        """Per-step outdoor temperature, wind, precipitation and irradiance.

        These are *forecast trajectories*, not current conditions: using the
        whole horizon is what makes the control anticipatory rather than
        reactive.
        """
        outdoor: list[float] = []
        wind: list[float] = []
        precipitation: list[float] = []
        solar: list[float] = []

        if not self._weather_forecast:
            _LOGGER.warning(
                "No weather forecast available — using current conditions. "
                "Predictive optimization will be limited."
            )
            return (
                [self._current_state.outdoor_temperature] * n_steps,
                [0.0] * n_steps,
                [0.0] * n_steps,
                [self._solar_radiation] * n_steps,
            )

        # Convert using the unit the weather entity actually reports in.
        # Guessing from the magnitude misreads a moderate 20 km/h breeze as a
        # 20 m/s storm and doubles the predicted heat loss.
        wind_scale = self._wind_speed_scale()
        for idx, entry in enumerate(self._weather_forecast):
            temp = _as_float(entry.get("temperature"), 5.0)
            gust = max(0.0, _as_float(entry.get("wind_speed"), 0.0) * wind_scale)
            rain = max(0.0, _as_float(entry.get("precipitation"), 0.0))

            irradiance = 0.0
            if idx < len(self._solar_radiation_forecast):
                irradiance = _as_float(self._solar_radiation_forecast[idx], 0.0)
            if irradiance == 0.0:
                irradiance = _as_float(
                    entry.get("solar_irradiance")
                    or entry.get("native_solar_irradiance"),
                    0.0,
                )
            irradiance = max(0.0, irradiance)

            # Hourly forecast held flat across the four quarters it covers.
            for _ in range(4):
                outdoor.append(temp)
                wind.append(gust)
                precipitation.append(rain)
                solar.append(irradiance)

        return outdoor, wind, precipitation, solar

    def _apply_open_meteo(
        self,
        solar: list[float],
        n_steps: int,
        midnight: datetime,
        step_offset: int,
    ) -> list[float]:
        """Overlay Open-Meteo irradiance, aligned by wall-clock time.

        The weather-entity path above aligns by *position*, which assumes its
        first forecast entry is the current hour — not guaranteed. An
        irradiance series carries its own timestamps, so match on those.
        """
        if self._open_meteo is None or not self._open_meteo.available:
            return solar

        step = timedelta(minutes=FORECAST_STEP_MINUTES)
        aligned: list[float] = []
        missing = 0
        for i in range(n_steps):
            step_start = midnight + timedelta(
                minutes=FORECAST_STEP_MINUTES * (step_offset + i)
            )
            value = self._open_meteo.irradiance_for(step_start, step)
            if value is None:
                # Past the end of the published horizon: keep whatever the
                # weather entity offered rather than asserting darkness.
                missing += 1
                value = solar[i] if i < len(solar) else 0.0
            aligned.append(max(0.0, value))

        if missing:
            _LOGGER.debug(
                "Open-Meteo irradiance covered %d/%d steps; the rest fell back "
                "to the weather entity",
                n_steps - missing,
                n_steps,
            )
        return aligned

    def _apply_pv_pricing(
        self, prices: np.ndarray, solar: np.ndarray, n_steps: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Replace the import price with the marginal cost of consuming.

        While the array is in surplus, an extra kWh does not cost the import
        price — it costs the export compensation foregone. Substituting it here
        means every downstream consumer (the hot-water LP, the space objective,
        the savings settle-up) is right without any structural change.
        """
        surplus, _ = self._pv_forecast(solar, n_steps)
        if np.any(surplus > 1e-6):
            prices = pv_model.effective_prices(
                prices, surplus, self._pv_export_price()
            )
        self._pv_surplus = surplus
        return prices, surplus

    def _forecast_arrays(self) -> ForecastArrays:
        """Everything the optimizer needs to know about the horizon.

        Assembled in one place because the pieces depend on each other: the PV
        surplus is derived from the irradiance series, and the marginal price
        from the surplus. Computing any of them elsewhere is how the three
        would drift apart.
        """
        n_steps = self._opt_config.n_steps
        now = dt_util.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        step_offset = int(
            (now - midnight).total_seconds() / 60 / FORECAST_STEP_MINUTES
        )

        priced = self._price_series(n_steps, midnight, step_offset)
        if priced is None:
            return ForecastArrays.empty()
        prices, price_known = priced

        outdoor, wind, precipitation, solar = self._weather_series(n_steps)
        solar = self._apply_open_meteo(solar, n_steps, midnight, step_offset)

        # A forecast shorter than the horizon is held flat at its last value.
        for series in (outdoor, wind, precipitation, solar):
            while len(series) < n_steps:
                series.append(series[-1] if series else 0.0)

        solar_array = np.array(solar[:n_steps], dtype=float)
        prices, surplus = self._apply_pv_pricing(prices, solar_array, n_steps)

        return ForecastArrays(
            prices=prices,
            outdoor_temps=np.array(outdoor[:n_steps], dtype=float),
            wind_speeds=np.array(wind[:n_steps], dtype=float),
            precipitation=np.array(precipitation[:n_steps], dtype=float),
            solar_radiation=solar_array,
            price_known=price_known,
            pv_surplus=surplus,
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
    # ------------------------------------------------------------------
    # Published state
    # ------------------------------------------------------------------
    #
    # ``_build_data_dict`` composes these. Each returns one domain, so a new
    # field is added next to its siblings rather than appended to a
    # two-hundred-line literal where nothing has a natural home.

    def _thermal_view(self) -> dict[str, Any]:
        """Measured and modelled temperatures, and the solar input."""
        state = self._current_state
        return {
            "indoor_temperature": state.room_temperature,
            "outdoor_temperature": state.outdoor_temperature,
            "slab_temperature": state.slab_temperature,
            "upper_floor_temperature": state.upper_floor_temperature,
            "lower_floor_temperature": state.lower_floor_temperature,
            "buffer_tank_temperature": state.buffer_tank_temperature,
            "floor_return_temperature": self._floor_return_temp,
            "solar_radiation": self._solar_radiation,
            "solar_heat_gain": self._thermal_model.compute_solar_gain(
                self._solar_radiation
            ),
            "solar_source": self._solar_forecast_source(),
            "solar_forecast": self._solar_forecast_view(),
            "solar_diagnostics": (
                self._open_meteo.diagnostics() if self._open_meteo else None
            ),
            "two_zone_enabled": self._thermal_params.two_zone_enabled,
            # The comfort schedule the plan was actually made against. The
            # card's what-if editor pre-fills from this: an editor that
            # started from defaults would silently propose a change the user
            # never made.
            "comfort_temp_day": self._opt_config.comfort_temp_day,
            "comfort_temp_night": self._opt_config.comfort_temp_night,
            "day_start_hour": self._opt_config.day_start_hour,
            "day_end_hour": self._opt_config.day_end_hour,
            "min_temperature": self._opt_config.min_temp,
            "max_temperature": self._opt_config.max_temp,
        }

    def _dhw_view(self) -> dict[str, Any]:
        """Hot water configuration and current demand state."""
        params = self._thermal_params
        result = self._optimization_result
        # The optimizer may derive demand windows from the learned usage
        # profile when the user configured none, so prefer what it actually
        # planned against over what the configuration says.
        planned_windows = (
            (result.predictive_info or {}).get("dhw_windows") if result else None
        )
        return {
            "dhw_enabled": params.dhw_enabled,
            "dhw_temperature": (
                self._dhw_temperature or self._current_state.dhw_temperature
            ),
            "dhw_setpoint": params.dhw_setpoint,
            "dhw_min_temperature": params.dhw_min_temp,
            "dhw_usage_profile": self._dhw_hourly_profile,
            "dhw_hold_hours": round(self._thermal_model.dhw_hold_hours(), 1),
            "dhw_windows": planned_windows
            or format_windows(params.dhw_demand_windows),
            "dhw_schedule_enabled": params.dhw_schedule_enabled,
            "dhw_in_demand_window": self._dhw_in_demand_window(),
            "dhw_next_window_in_hours": self._dhw_next_window_in_hours(),
            "dhw_idle_min_temperature": params.dhw_idle_min_temp,
            "dhw_legionella_enabled": params.dhw_legionella_enabled,
            "dhw_legionella_due_in_hours": self._dhw_legionella_due_in_hours(),
        }

    def _learning_view(self) -> dict[str, Any]:
        """What the self-learning estimators currently believe.

        ``*_learned`` flags say whether a value is still the configured prior
        or has moved, which is the difference between "the default is wrong"
        and "the house really is like this".
        """
        return {
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
            "cop_scale": round(self._cop_scale, 3),
            "cop_samples": self._cop_samples,
            "measured_cop": self._last_measured_cop,
            "defrost_derate": self._defrost.factor(
                self._current_state.outdoor_temperature, self._current_humidity()
            ),
            "defrost_samples": self._defrost.total_samples,
            "defrost_buckets": self._defrost.summary(),
            "comfort_weight": self._opt_config.comfort_weight,
            "comfort_learning": self._comfort_learner.summary(),
            "system_identification": self._sysid.as_dict(),
            "accuracy": self._accuracy.summary(),
        }

    def _measurement_view(self) -> dict[str, Any]:
        """Optional measured inputs. All ``None`` on an install without them."""
        return {
            "measured_power": self._measured_power,
            "measured_house_power": self._measured_house_power,
            "measured_energy": self._measured_energy,
            "measured_power_available": self._measured_power is not None,
        }

    def _grid_view(self) -> dict[str, Any]:
        """Prices, the capacity tariff and PV, i.e. what a kWh actually costs."""
        tariff = self._capacity_tariff()
        return {
            "current_price": self._get_current_price(),
            "prices_available": len(self._prices),
            "weather_forecast_available": len(self._weather_forecast),
            "price_known_steps": self._price_known_steps,
            "price_prior": self._price_model.summary(),
            "peak_tariff_enabled": tariff.enabled,
            "billed_peak_kw": round(self._peak_tracker.billed_peak_kw(tariff), 2),
            "peak_threshold_kw": round(self._peak_tracker.threshold_kw(tariff), 2),
            "peak_month": self._peak_tracker.month,
            "pv_enabled": bool(
                self._config.get(CONF_PV_ENABLED, DEFAULT_PV_ENABLED)
            ),
            "pv": self._pv_summary,
        }

    def _ecl110_view(self) -> dict[str, Any]:
        """Heat-curve control state for the ECL110 integration."""
        return {
            "ecl110_command_topic": self._ecl110_command_topic,
            "ecl110_state_topic": self._ecl110_state_topic,
            "ecl110_displace": self._current_action.get(
                "displace_value", self._ecl110_current_displace
            ),
            "ecl110_effective_displace": (
                self._current_state.ecl110_effective_displace
            ),
            "ecl110_last_payload": self._ecl110_last_payload,
        }

    def _external_heat_view(self) -> dict[str, Any]:
        """Whether something other than the heat pump is charging the tanks."""
        return {
            "external_heat_active": self._external_heat.state.active,
            "external_heat_suppressing": self._external_heat.suppressing,
            "external_heat": self._external_heat.state.as_dict(),
        }

    def _build_data_dict(self) -> dict[str, Any]:
        """Everything the entities read, assembled from the domain views."""
        result = self._optimization_result

        data: dict[str, Any] = {
            "mode": self._mode,
            "current_action": self._current_action,
            "last_optimization": self._last_optimization,
            "next_optimization": self._next_optimization,
        }
        for view in (
            self._thermal_view,
            self._dhw_view,
            self._learning_view,
            self._measurement_view,
            self._grid_view,
            self._ecl110_view,
            self._external_heat_view,
            self._input_health_view,
        ):
            data.update(view())
        data.update(self._away_state.as_dict())
        data.update({k: round(v, 4) for k, v in self._energy_totals.items()})
        data["battery"] = self._battery_view()

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
                    # Grid-cost and provenance figures (items 7, 8, 10, 9)
                    "projected_peak_kw": result.projected_peak_kw,
                    "projected_peak_cost": result.peak_cost,
                    "compressor_starts": result.compressor_starts,
                    "pv_self_consumed_kwh": result.pv_self_consumed_kwh,
                    "plan_price_known": result.price_known,
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
                    "projected_peak_kw": 0.0,
                    "projected_peak_cost": 0.0,
                    "compressor_starts": 0,
                    "pv_self_consumed_kwh": 0.0,
                    "plan_price_known": [],
                }
            )

        return data

    # ==================================================================
    # Persistence for the new learners
    # ==================================================================

    async def _async_load_price_model(self) -> None:
        """Restore the learned diurnal price shape."""
        try:
            stored = await self._price_model_store.async_load()
        except Exception as err:  # noqa: BLE001 - never block setup on storage
            _LOGGER.debug("Could not load price model: %s", err)
            return
        if not stored:
            return
        self._price_model = PriceShapeModel.from_dict(stored.get("model"))
        days = stored.get("days_seen")
        if isinstance(days, list):
            self._price_days_seen = {str(d) for d in days}

    async def _async_save_price_model(self) -> None:
        try:
            await self._price_model_store.async_save(
                {
                    "model": self._price_model.as_dict(),
                    # Only recent days matter for de-duplication, and an
                    # unbounded set would grow forever.
                    "days_seen": sorted(self._price_days_seen)[-90:],
                }
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist price model: %s", err)

    async def _async_load_accuracy(self) -> None:
        try:
            stored = await self._accuracy_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load accuracy history: %s", err)
            return
        if not stored:
            return
        self._accuracy = AccuracyTracker.from_dict(stored.get("accuracy"))
        self._defrost = DefrostDerate.from_dict(stored.get("defrost"))
        self._thermal_params.defrost_derate = self._defrost
        self._peak_tracker = PeakTracker.from_dict(stored.get("peaks"))
        self._comfort_learner = ComfortLearner.from_dict(
            stored.get("comfort"),
            _as_float(self._config.get(CONF_COMFORT_WEIGHT), DEFAULT_COMFORT_WEIGHT),
        )
        self._apply_comfort_weight()

    async def _async_save_accuracy(self) -> None:
        try:
            await self._accuracy_store.async_save(
                {
                    "accuracy": self._accuracy.as_dict(),
                    "defrost": self._defrost.as_dict(),
                    "peaks": self._peak_tracker.as_dict(),
                    "comfort": self._comfort_learner.as_dict(),
                }
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist accuracy history: %s", err)

    async def _async_load_energy_totals(self) -> None:
        try:
            stored = await self._energy_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load energy totals: %s", err)
            return
        if not stored:
            return
        for key in list(self._energy_totals):
            value = stored.get(key)
            if isinstance(value, (int, float)) and np.isfinite(value):
                # Accumulators must never go backwards, or Home Assistant reads
                # the drop as a meter reset and creates a spurious spike.
                self._energy_totals[key] = max(
                    self._energy_totals[key], float(value)
                )

    async def _async_save_energy_totals(self) -> None:
        try:
            await self._energy_store.async_save(dict(self._energy_totals))
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist energy totals: %s", err)

    # ==================================================================
    # Price horizon modelling (item 7)
    # ==================================================================

    async def _async_learn_price_shape(self) -> None:
        """Fold any newly complete price days into the learned shape."""
        if not self._config.get(
            CONF_PRICE_PRIOR_ENABLED, DEFAULT_PRICE_PRIOR_ENABLED
        ):
            return
        days = hourly_from_entries(self._prices)
        learned = False
        for day, hours in days.items():
            if day in self._price_days_seen:
                continue
            try:
                when = datetime.fromisoformat(f"{day}T12:00:00")
            except ValueError:
                continue
            if self._price_model.observe_day(when, hours):
                self._price_days_seen.add(day)
                learned = True
        if learned:
            await self._async_save_price_model()

    def _price_prior(self) -> PriceShapeModel | None:
        if not self._config.get(
            CONF_PRICE_PRIOR_ENABLED, DEFAULT_PRICE_PRIOR_ENABLED
        ):
            return None
        return self._price_model

    # ==================================================================
    # Capacity tariff (item 8)
    # ==================================================================

    def _capacity_tariff(self) -> CapacityTariff:
        return CapacityTariff(
            enabled=bool(
                self._config.get(
                    CONF_PEAK_TARIFF_ENABLED, DEFAULT_PEAK_TARIFF_ENABLED
                )
            ),
            price_per_kw=_as_float(
                self._config.get(CONF_PEAK_TARIFF_PRICE),
                DEFAULT_PEAK_TARIFF_PRICE,
            ),
            peaks_averaged=int(
                _as_float(
                    self._config.get(CONF_PEAK_TARIFF_COUNT),
                    DEFAULT_PEAK_TARIFF_COUNT,
                )
            ),
            window_minutes=int(
                _as_float(
                    self._config.get(CONF_PEAK_TARIFF_WINDOW),
                    DEFAULT_PEAK_TARIFF_WINDOW,
                )
            ),
        )

    def _track_realised_peak(self) -> None:
        """Fold the current whole-house draw into this month's peaks.

        Without a house power entity, the heat pump's own draw is all that can
        be seen. That under-states the real peak, so the threshold it produces
        is conservative in the wrong direction — which is why the config flow
        asks for a house meter and says why.
        """
        tariff = self._capacity_tariff()
        if not tariff.enabled:
            return
        house = self._measured_house_power
        if house is None:
            house = self._measured_power
        if house is None:
            house = float(self._current_action.get("power", 0.0))
        self._peak_tracker.observe(dt_util.now(), float(house), tariff)

    def _baseline_house_load(self, n_steps: int) -> np.ndarray:
        """Whole-house load excluding the heat pump, per step, in kW."""
        heat_pump = self._measured_power
        house = self._measured_house_power
        if house is None:
            return np.zeros(n_steps, dtype=float)
        baseline = max(0.0, house - (heat_pump or 0.0))
        return np.full(n_steps, baseline, dtype=float)

    # ==================================================================
    # PV self-consumption (item 9)
    # ==================================================================

    def _pv_config(self) -> pv_model.PVConfig:
        return pv_model.PVConfig(
            enabled=bool(self._config.get(CONF_PV_ENABLED, DEFAULT_PV_ENABLED)),
            peak_kw=_as_float(
                self._config.get(CONF_PV_PEAK_KW), DEFAULT_PV_PEAK_KW
            ),
            system_efficiency=_as_float(
                self._config.get(CONF_PV_EFFICIENCY), DEFAULT_PV_EFFICIENCY
            ),
            export_price=self._pv_export_price(),
            export_price_entity=self._config.get(CONF_PV_EXPORT_PRICE_ENTITY),
            production_entity=self._config.get(CONF_PV_PRODUCTION_ENTITY),
        )

    def _pv_export_price(self) -> float:
        """Export compensation, preferring a live entity over the static value."""
        entity_id = self._config.get(CONF_PV_EXPORT_PRICE_ENTITY)
        if entity_id:
            state = self.hass.states.get(entity_id)
            if state is not None and str(state.state).lower() not in (
                "unknown",
                "unavailable",
                "",
            ):
                try:
                    return float(state.state)
                except (TypeError, ValueError):
                    pass
        return _as_float(
            self._config.get(CONF_PV_EXPORT_PRICE), DEFAULT_PV_EXPORT_PRICE
        )

    def _pv_forecast(
        self, solar_rad: np.ndarray, n_steps: int
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Forecast PV surplus over the horizon."""
        config = self._pv_config()
        if not config.enabled or config.peak_kw <= 0:
            self._pv_summary = {}
            return np.zeros(n_steps, dtype=float), {}
        production = pv_model.forecast_production_kw(solar_rad[:n_steps], config)
        baseline = self._baseline_house_load(n_steps)
        if not np.any(baseline > 0):
            baseline = np.full(n_steps, config.default_baseline_kw, dtype=float)
        surplus = pv_model.surplus_kw(production, baseline)
        summary = pv_model.summarize(production, surplus, self._opt_config.dt_hours)
        summary["export_price"] = round(config.export_price, 4)
        self._pv_summary = summary
        return surplus, summary

    # ==================================================================
    # Away / holiday mode (item 13)
    # ==================================================================

    def _away_config(self) -> away_mode.AwayConfig:
        return away_mode.AwayConfig(
            enabled=bool(
                self._config.get(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED)
            ),
            presence_entity=self._config.get(CONF_AWAY_PRESENCE_ENTITY),
            return_entity=self._config.get(CONF_AWAY_RETURN_ENTITY),
            away_temperature=_as_float(
                self._config.get(CONF_AWAY_TEMPERATURE), DEFAULT_AWAY_TEMPERATURE
            ),
            away_dhw_min_temperature=_as_float(
                self._config.get(CONF_AWAY_DHW_MIN_TEMP),
                DEFAULT_AWAY_DHW_MIN_TEMP,
            ),
        )

    def _entity_state(self, entity_id: str | None) -> tuple[str | None, dict]:
        if not entity_id:
            return None, {}
        state = self.hass.states.get(entity_id)
        if state is None:
            return None, {}
        attributes = getattr(state, "attributes", None) or {}
        try:
            attributes = dict(attributes)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            attributes = {}
        return getattr(state, "state", None), attributes

    def _resolve_away(self) -> away_mode.AwayState:
        """Work out whether the house is empty, and when it must be warm again."""
        config = self._away_config()
        if not config.enabled:
            self._away_state = away_mode.AwayState()
            return self._away_state

        presence_raw, presence_attrs = self._entity_state(config.presence_entity)
        return_raw, _ = self._entity_state(config.return_entity)

        params = self._thermal_params
        if params.two_zone_enabled:
            capacity = (
                params.upper_floor_thermal_mass + params.lower_floor_thermal_mass
            )
        else:
            capacity = params.room_thermal_mass

        cop = self._thermal_model.compute_cop(
            self._current_state.outdoor_temperature
        )
        now = dt_util.now()
        self._away_state = away_mode.resolve(
            config,
            now=now,
            presence_raw=presence_raw,
            presence_attributes=presence_attrs,
            return_raw=return_raw,
            current_temp=self._current_state.room_temperature,
            comfort_temp=self._opt_config.get_comfort_temp(
                now.hour + now.minute / 60.0
            ),
            heat_capacity_kwh_per_c=capacity,
            available_thermal_kw=params.max_electrical_power * max(cop, 1.0),
            heat_loss_kw_per_c=self._effective_house_heat_loss(),
            outdoor_temp=self._current_state.outdoor_temperature,
        )
        return self._away_state

    def _apply_away_setback(self) -> dict[str, float]:
        """Temporarily lower the comfort targets while away.

        Returns the original values so they can be restored, because the
        optimizer config is shared state and a setback that leaked past the
        end of the holiday would be a comfort failure nobody would connect
        back to this feature.
        """
        state = self._away_state
        original = {
            "min_temp": self._opt_config.min_temp,
            "comfort_temp_day": self._opt_config.comfort_temp_day,
            "comfort_temp_night": self._opt_config.comfort_temp_night,
            "dhw_min_temp": self._thermal_params.dhw_min_temp,
            "dhw_idle_min_temp": self._thermal_params.dhw_idle_min_temp,
        }
        if not state.active or state.recovery_active:
            return original

        target = state.target_temperature or DEFAULT_AWAY_TEMPERATURE
        self._opt_config.min_temp = min(original["min_temp"], target)
        self._opt_config.comfort_temp_day = target
        self._opt_config.comfort_temp_night = target
        dhw_floor = state.dhw_min_temperature or DEFAULT_AWAY_DHW_MIN_TEMP
        self._thermal_params.dhw_min_temp = min(original["dhw_min_temp"], dhw_floor)
        self._thermal_params.dhw_idle_min_temp = min(
            original["dhw_idle_min_temp"], dhw_floor
        )
        return original

    def _restore_away_setback(self, original: dict[str, float]) -> None:
        self._opt_config.min_temp = original["min_temp"]
        self._opt_config.comfort_temp_day = original["comfort_temp_day"]
        self._opt_config.comfort_temp_night = original["comfort_temp_night"]
        self._thermal_params.dhw_min_temp = original["dhw_min_temp"]
        self._thermal_params.dhw_idle_min_temp = original["dhw_idle_min_temp"]

    # ==================================================================
    # Closed-loop accuracy and the defrost derate (items 11, 14)
    # ==================================================================

    def _current_humidity(self) -> float | None:
        """Outdoor relative humidity, if the weather entity reports it."""
        if not self._weather_forecast:
            return None
        raw = self._weather_forecast[0].get("humidity")
        if raw is None:
            return None
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        return value if 0.0 <= value <= 100.0 else None

    def _record_accuracy(self) -> None:
        """Close the loop on the prediction made at the previous interval."""
        pending = self._pending_prediction
        now = dt_util.now()

        if pending is not None:
            elapsed = (now - pending["when"]).total_seconds() / 3600.0
            # Only pair up predictions with the interval they were actually
            # about; a restart or a long gap makes the pairing meaningless.
            if 0.05 <= elapsed <= 2.0:
                sample = AccuracySample(
                    when=now,
                    predicted_power_kw=pending.get("power"),
                    actual_power_kw=self._measured_power,
                    predicted_temp=pending.get("predicted_temp"),
                    actual_temp=self._current_state.room_temperature,
                    predicted_cost=(
                        (pending.get("power") or 0.0)
                        * elapsed
                        * (pending.get("price") or 0.0)
                    ),
                    actual_cost=(
                        self._measured_power * elapsed * (pending.get("price") or 0.0)
                        if self._measured_power is not None
                        else None
                    ),
                    outdoor_temp=pending.get("outdoor"),
                    humidity=pending.get("humidity"),
                )
                self._accuracy.record(sample)
                self._accumulate_energy(sample, elapsed, pending)

                # The delivered-versus-predicted ratio is exactly what the
                # defrost derate learns from, and it is only meaningful while
                # the learners are not frozen for some other reason.
                if not self._learning_frozen(CONF_POWER_ENTITY):
                    ratio = delivered_ratio(sample)
                    if ratio is not None and sample.outdoor_temp is not None:
                        self._defrost.observe(
                            sample.outdoor_temp, sample.humidity, ratio
                        )

        self._pending_prediction = {
            "when": now,
            # The meter sees the whole heat pump, so the prediction it is
            # compared against has to be the whole plan. Recording space
            # heating alone made every hot-water charge look like the unit
            # under-delivering, which fed straight into the defrost derate.
            "power": self._commanded_power(),
            "space_power": float(self._current_action.get("power", 0.0)),
            "dhw_power": float(self._current_action.get("dhw_power", 0.0)),
            "price": self._get_current_price(),
            "predicted_temp": self._predicted_next_room_temp(),
            "outdoor": self._current_state.outdoor_temperature,
            "humidity": self._current_humidity(),
        }

    def _predicted_next_room_temp(self) -> float | None:
        """What the plan says the room will be at the next interval."""
        result = self._optimization_result
        if result is None or not result.room_temp_trajectory:
            return None
        steps = max(
            1,
            int(
                round(
                    self._config.get(
                        CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                    )
                    / max(self._opt_config.time_step_minutes, 1.0)
                )
            ),
        )
        trajectory = (
            result.upper_temp_trajectory
            if self._thermal_params.two_zone_enabled
            and result.upper_temp_trajectory
            else result.room_temp_trajectory
        )
        idx = min(steps, len(trajectory) - 1)
        return float(trajectory[idx])

    # ==================================================================
    # Energy dashboard statistics (item 15)
    # ==================================================================

    def _accumulate_energy(
        self, sample: AccuracySample, elapsed_hours: float, pending: dict[str, Any]
    ) -> None:
        """Accumulate realised energy and cost, split DHW versus space.

        Uses the *measured* draw when one exists so the totals reflect reality
        rather than the commanded plan; that distinction is the whole reason
        the Energy dashboard is worth feeding.

        The DHW/space split cannot be measured — one meter, two circuits — so
        it is apportioned by what the plan asked each circuit to draw. That is
        stated in the sensor attributes rather than presented as measured.
        """
        price = pending.get("price") or 0.0
        planned_space = float(pending.get("space_power") or 0.0)
        planned_dhw = float(pending.get("dhw_power") or 0.0)
        planned_total = planned_space + planned_dhw

        actual = sample.actual_power_kw
        if actual is None:
            actual = planned_total
        energy = max(0.0, actual * elapsed_hours)
        if energy <= 0:
            return

        if planned_total > 1e-6:
            dhw_share = planned_dhw / planned_total
        else:
            dhw_share = 0.0
        dhw_energy = energy * dhw_share
        space_energy = energy - dhw_energy

        self._energy_totals["space_energy_kwh"] += space_energy
        self._energy_totals["dhw_energy_kwh"] += dhw_energy
        self._energy_totals["total_energy_kwh"] += energy
        self._energy_totals["space_cost"] += space_energy * price
        self._energy_totals["dhw_cost"] += dhw_energy * price
        self._energy_totals["total_cost"] += energy * price

    # ==================================================================
    # Revealed-preference comfort tuning (item 19)
    # ==================================================================

    def _apply_comfort_weight(self) -> None:
        """Push the learned comfort weight into the optimizer configuration."""
        if not self._config.get(
            CONF_COMFORT_LEARNING_ENABLED, DEFAULT_COMFORT_LEARNING_ENABLED
        ):
            self._opt_config.comfort_weight = self._comfort_learner.configured_weight
            return
        self._opt_config.comfort_weight = self._comfort_learner.effective_weight

    def record_setpoint_override(self, requested: float) -> None:
        """Note that the user overrode the plan's setpoint.

        Called from the climate entity. Every override is the user saying the
        plan went too far in one direction, which is the only evidence anyone
        ever produces about what ``comfort_weight`` should be.
        """
        if not self._config.get(
            CONF_COMFORT_LEARNING_ENABLED, DEFAULT_COMFORT_LEARNING_ENABLED
        ):
            return
        planned = float(self._current_action.get("setpoint", requested))
        delta = float(requested) - planned
        prices = [p.get("total", 0.0) for p in self._prices] or [1.0]
        mean_price = float(np.mean([_as_float(p, 0.0) for p in prices])) or 1.0
        relative = self._get_current_price() / mean_price if mean_price else 1.0
        self._comfort_learner.record_override(
            OverrideEvent(
                when=dt_util.now(),
                delta_c=delta,
                indoor_temp=self._current_state.room_temperature,
                planned_setpoint=planned,
                relative_price=relative,
            )
        )
        self._apply_comfort_weight()
        self._last_manual_setpoint = float(requested)

    def _record_quiet_comfort_period(self) -> None:
        """Feed the learner the "nobody complained" half of the signal."""
        if not self._config.get(
            CONF_COMFORT_LEARNING_ENABLED, DEFAULT_COMFORT_LEARNING_ENABLED
        ):
            return
        result = self._optimization_result
        if result is None or not result.room_temp_trajectory:
            return
        trajectory = np.asarray(result.room_temp_trajectory, dtype=float)
        span = float(np.max(trajectory) - np.min(trajectory))
        band = max(
            0.5, self._opt_config.comfort_temp_day - self._opt_config.min_temp
        )
        interval_days = (
            self._config.get(
                CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
            )
            / 1440.0
        )
        self._comfort_learner.record_quiet_period(
            dt_util.now(), span, band, days=interval_days
        )
        self._apply_comfort_weight()

    async def async_reset_comfort_weight(self) -> None:
        """Return the comfort weight to the configured value."""
        self._comfort_learner.reset()
        self._apply_comfort_weight()
        await self._async_save_accuracy()
        await self.async_request_refresh()

    # ==================================================================
    # Active system identification (item 18)
    # ==================================================================

    @property
    def system_identification_active(self) -> bool:
        return self._sysid.active

    async def async_arm_system_identification(self) -> None:
        """Arm a step-response experiment for the next suitable moment."""
        self._sysid.config.enabled = bool(
            self._config.get(CONF_SYSID_ENABLED, DEFAULT_SYSID_ENABLED)
        )
        if self._sysid.arm(dt_util.now()):
            _LOGGER.info(
                "System identification armed; it will start at the next mild, "
                "cheap night hour"
            )
        await self.async_request_refresh()

    def _run_system_identification(self, prices: np.ndarray) -> None:
        """Advance the experiment and override the plan if it wants the pump."""
        if not self._sysid.active:
            return
        override = self._sysid.step(
            now=dt_util.now(),
            room_temp=self._current_state.room_temperature,
            outdoor_temp=self._current_state.outdoor_temperature,
            price=self._get_current_price(),
            price_horizon=prices,
            learner_samples=self._house_heat_loss_samples,
            max_power_kw=self._thermal_params.max_electrical_power,
            cop=self._thermal_model.compute_cop(
                self._current_state.outdoor_temperature
            ),
        )
        if override is None:
            return
        self._current_action = {
            **self._current_action,
            "power": float(override),
            "power_normalized": float(
                override / max(self._thermal_params.max_electrical_power, 0.1)
            ),
            "heat_pump_on": override > 0.05,
            "mode": "system_identification",
        }

    def _adopt_system_identification(self) -> None:
        """Seed the passive learners from a completed experiment."""
        result = self._sysid.result
        if not result.completed or result.confidence < 0.3:
            return
        params = self._thermal_params
        if params.two_zone_enabled:
            base_u = params.upper_floor_heat_loss + params.lower_floor_heat_loss
        else:
            base_u = params.heat_loss_coefficient
        if base_u <= 1e-6 or result.heat_loss_kw_per_c is None:
            return
        scale = result.heat_loss_kw_per_c / base_u
        # A high-confidence experiment is a much better prior than weeks of
        # ambiguous passive samples, but it is still one experiment: blend
        # rather than overwrite, weighted by the fit quality.
        blended = (
            1.0 - result.confidence
        ) * self._house_heat_loss_scale + result.confidence * scale
        self._apply_house_heat_loss_scale(blended)
        self._house_heat_loss_samples = max(
            self._house_heat_loss_samples, int(20 * result.confidence)
        )
        self._sysid.result = replace(result, completed=False, reason="adopted")
        _LOGGER.info(
            "Adopted system identification result: heat loss scale now %.3f",
            self._house_heat_loss_scale,
        )

    # ==================================================================
    # Virtual battery view (item 20)
    # ==================================================================

    def _battery_view(self) -> dict[str, Any]:
        """Publish the thermal stores as a battery."""
        params = self._thermal_params
        cop = self._thermal_model.compute_cop(
            self._current_state.outdoor_temperature
        )
        view = battery_view.build(
            params,
            self._current_state,
            comfort_min=self._opt_config.min_temp,
            comfort_max=self._opt_config.max_temp,
            dhw_min=params.dhw_min_temp,
            dhw_max=params.dhw_max_temp,
            cop=cop,
        )
        return view.as_dict()

    # ==================================================================
    # Forcing a run, and the what-if simulator (items 3, 21)
    # ==================================================================

    @property
    def optimization_running(self) -> bool:
        return self._optimization_running

    async def async_force_optimization(self) -> None:
        """Run the optimization now, ignoring the schedule."""
        if self._optimization_running:
            _LOGGER.debug("Optimization already running; ignoring the request")
            return
        await self.async_request_refresh()

    async def async_simulate(
        self, overrides: dict[str, Any]
    ) -> dict[str, Any]:
        """Price a hypothetical comfort choice against the current forecast.

        Backs the card's what-if simulator. Two things matter here:

        * it runs off a **copy** of the configuration, so an exploratory drag
          can never disturb actual operation;
        * it is **rate-limited**, because a full solve is seconds of CPU and
          dragging a slider would otherwise trigger one per pixel.
        """
        now = dt_util.now()
        if (
            self._last_simulation is not None
            and (now - self._last_simulation).total_seconds()
            < SIMULATE_MIN_INTERVAL_SECONDS
        ):
            return {
                **self._simulation_cache,
                "rate_limited": True,
            }

        result = self._optimization_result
        if result is None:
            return {"error": "no_plan", "rate_limited": False}

        horizon = self._forecast_arrays()
        if len(horizon.prices) < 4:
            return {"error": "no_prices", "rate_limited": False}

        scratch_config = replace(self._opt_config)
        for key in (
            "target_temp",
            "min_temp",
            "max_temp",
            "comfort_temp_day",
            "comfort_temp_night",
            "comfort_weight",
        ):
            if key in overrides:
                setattr(scratch_config, key, float(overrides[key]))
        # The heating schedule: which hours count as "day" and therefore get
        # the day comfort temperature. Integers, because they index hours.
        for key in ("day_start_hour", "day_end_hour"):
            if key in overrides:
                setattr(scratch_config, key, int(overrides[key]))

        scratch_params = replace(self._thermal_params)
        if "dhw_setpoint" in overrides:
            scratch_params.dhw_setpoint = float(overrides["dhw_setpoint"])
        if "dhw_min_temperature" in overrides:
            scratch_params.dhw_min_temp = float(overrides["dhw_min_temperature"])
        if "dhw_windows" in overrides:
            spec = str(overrides["dhw_windows"]).strip()
            if not spec:
                # An explicitly empty schedule means "no demand windows", which
                # is a legitimate thing to simulate: it is what the plan looks
                # like with hot water availability unconstrained.
                scratch_params.dhw_windows = []
            else:
                try:
                    scratch_params.dhw_windows = parse_windows(spec)
                except DHWWindowError as err:
                    return {
                        "error": f"invalid_windows: {err}",
                        "rate_limited": False,
                    }

        scratch = HeatPumpOptimizer(ThermalModel(scratch_params), scratch_config)
        try:
            simulated = await self.hass.async_add_executor_job(
                lambda: scratch.optimize(
                    replace(self._current_state),
                    horizon.prices,
                    horizon.outdoor_temps,
                    horizon.wind_speeds,
                    horizon.precipitation,
                    horizon.solar_radiation,
                    now,
                    horizon.price_known,
                    horizon.pv_surplus,
                )
            )
        except Exception as err:  # noqa: BLE001 - a what-if must never break ops
            _LOGGER.warning("What-if simulation failed: %s", err)
            return {"error": str(err), "rate_limited": False}

        horizon_hours = max(self._opt_config.horizon_hours, 1.0)
        days_per_month = 30.4
        scale = days_per_month * 24.0 / horizon_hours
        delta = simulated.predicted_cost - result.predicted_cost

        def coldest(plan) -> float | None:
            """Lowest temperature the plan actually reaches, in either zone."""
            series = [
                s
                for s in (
                    plan.upper_temp_trajectory,
                    plan.lower_temp_trajectory,
                    plan.room_temp_trajectory,
                )
                if s
            ]
            return round(min(min(s) for s in series), 2) if series else None

        def dhw_low(plan) -> float | None:
            if not plan.dhw_temp_trajectory:
                return None
            return round(float(min(plan.dhw_temp_trajectory)), 2)

        payload = {
            "baseline_cost": round(result.predicted_cost, 2),
            "simulated_cost": round(simulated.predicted_cost, 2),
            "cost_delta": round(delta, 2),
            "monthly_cost_delta": round(delta * scale, 2),
            "savings_percentage": round(simulated.savings_percentage, 1),
            "min_room_temperature": coldest(simulated),
            # The comfort consequence, alongside the money. A cheaper plan that
            # is colder or leaves the tank short is not the same trade, and a
            # simulator that reported only the saving would be inviting the
            # user to make exactly that mistake.
            "baseline_min_room_temperature": coldest(result),
            "min_dhw_temperature": dhw_low(simulated),
            "baseline_min_dhw_temperature": dhw_low(result),
            "dhw_slots": len(
                self._plan_slots(
                    simulated.timestamps,
                    list(simulated.dhw_power_schedule or []),
                    list(simulated.prices),
                    self._opt_config.dt_hours,
                )
            ),
            "space_slots": len(
                self._plan_slots(
                    simulated.timestamps,
                    list(simulated.power_schedule),
                    list(simulated.prices),
                    self._opt_config.dt_hours,
                )
            ),
            "compressor_starts": simulated.compressor_starts,
            "projected_peak_kw": simulated.projected_peak_kw,
            "overrides": overrides,
            "rate_limited": False,
        }
        self._last_simulation = now
        self._simulation_cache = payload
        return payload
