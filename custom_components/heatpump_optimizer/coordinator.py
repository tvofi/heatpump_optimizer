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
from bisect import bisect_right
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
from homeassistant.helpers.event import async_track_state_change_event
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
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    CONF_MIXING_VALVE_WRITE_ENTITY,
    MIXING_VALVE_WRITE_EPSILON,
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
    buffer_cooling_rate_bounds,
    default_buffer_cooling_rate,
    CONF_BUFFER_COOLING_RATE,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    DEFAULT_HOUSE_HEAT_LOSS_SCALE,
    DHW_COOLING_RATE_MIN,
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    DEFAULT_LOWER_FLOOR_LOSS_RATIO,
    LOWER_FLOOR_LOSS_RATIO_MAX,
    LOWER_FLOOR_LOSS_RATIO_MIN,
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
    ECONOMY_ABSOLUTE_FLOOR,
    ECONOMY_MIN_TEMP_WIDENING,
    MODE_ECONOMY,
    OPERATION_MODES,
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
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_WOOD_TANK_VOLUME,
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
    CONF_GRID_FEE_MODE,
    DEFAULT_GRID_FEE_MODE,
    CONF_GRID_FEE_RULES,
    DEFAULT_GRID_FEE_RULES,
    CONF_GRID_FEE_ENTITY,
    CONF_GRID_FEE_FIXED,
    DEFAULT_GRID_FEE_FIXED,
    CONF_PEAK_TARIFF_MONTHS,
    DEFAULT_PEAK_TARIFF_MONTHS,
    CONF_PEAK_TARIFF_HOURS,
    DEFAULT_PEAK_TARIFF_HOURS,
    CONF_PEAK_TARIFF_WEEKDAYS_ONLY,
    DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY,
    CONF_PEAK_TARIFF_OFFPEAK_FACTOR,
    DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR,
    CONF_PRICE_RISK_LAMBDA,
    DEFAULT_PRICE_RISK_LAMBDA,
    CONF_CONTRACT_FIXED_PRICE,
    DEFAULT_CONTRACT_FIXED_PRICE,
    CONF_MAIN_FUSE_A,
    DEFAULT_MAIN_FUSE_A,
    CONF_MAIN_FUSE_PHASES,
    DEFAULT_MAIN_FUSE_PHASES,
    CONF_FUSE_GUARD_ENABLED,
    DEFAULT_FUSE_GUARD_ENABLED,
    CONF_PEAK_GUARD_ENABLED,
    DEFAULT_PEAK_GUARD_ENABLED,
    CONF_PEAK_GUARD_MARGIN_KW,
    DEFAULT_PEAK_GUARD_MARGIN_KW,
    CONF_OUTAGE_RECOVERY_ENABLED,
    DEFAULT_OUTAGE_RECOVERY_ENABLED,
    FUSE_LADDER_A,
    PEAK_GUARD_DISPLACE_NUDGE_C,
    OUTAGE_GAP_MINUTES,
    OUTAGE_RECOVERY_HOURS,
    OUTAGE_DHW_DELAY_MINUTES,
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
    MANUAL_PLAN_STORE_VERSION,
    SIMULATE_MIN_INTERVAL_SECONDS,
    CONF_DHW_INLET_ENTITY,
    CONF_DHW_QUANTILE_TARGETS_ENABLED,
    DEFAULT_DHW_QUANTILE_TARGETS_ENABLED,
    CONF_DHW_FREE_DISINFECTION_ENABLED,
    DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
    CONF_SHOWER_FLOW_LPM,
    DEFAULT_SHOWER_FLOW_LPM,
    CONF_VVC_PUMP_ENTITY,
    CONF_VVC_LEAD_MINUTES,
    DEFAULT_VVC_LEAD_MINUTES,
    CONF_SPACE_PUMP_ENTITY,
    DHW_LEGIONELLA_HOLD_MINUTES,
    DHW_DAYTYPE_BLEND_K,
    SPACE_PUMP_FLOOR_MARGIN_C,
)
from .inputs import InputHealth, InputReader, normalize_power_kw, stale_summary
from .external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
    wood_mean_temperature,
)
from . import away as away_mode
from . import battery as battery_view
from . import mixing_valve
from . import topology
from . import pv as pv_model
from .accuracy import AccuracySample, AccuracyTracker, delivered_ratio
from .comfort_learning import ComfortLearner, OverrideEvent
from .defrost import DefrostDerate, in_frost_band
from .manual_plan import (
    CHANNEL_DHW,
    CHANNEL_SPACE,
    ManualOverride,
    ManualPlanError,
)
from .price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
    quarters_from_entries,
)
from .sysid import SysIdConfig, SystemIdentification
from .tariff import CapacityTariff, PeakTracker
from .grid_fee import (
    GridFeeError,
    GridFeeSchedule,
    parse_month_range as grid_fee_parse_month_range,
)
from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
from .ledger import MonthlyLedger, month_key
from .power_guard import GuardState, project_window_mean
from . import pump_schedule
from .open_meteo import OpenMeteoSolar
from .thermal_model import (
    DHW_AMBIENT_TEMP,
    WATER_SPECIFIC_HEAT,
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from .dhw_schedule import (
    DHWWindowError,
    format_windows,
    hour_in_windows,
    hours_until_next_window,
    overlap_fraction,
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

    #: Raw import prices. The optimizer charges consumption piecewise against
    #: ``pv_surplus`` — up to it at the export compensation, beyond it at
    #: these — so no repricing happens here.
    prices: np.ndarray
    outdoor_temps: np.ndarray
    wind_speeds: np.ndarray
    precipitation: np.ndarray
    solar_radiation: np.ndarray
    #: True where the price came from published market data rather than the
    #: learned diurnal prior.
    price_known: np.ndarray
    pv_surplus: np.ndarray
    #: The prior's learned one-sigma dispersion per step (#34), zero on
    #: known steps. Appended, never inserted: the positional consumers
    #: slice by index and an insertion would silently re-map them all.
    price_sigma: np.ndarray = np.array([], dtype=float)

    @classmethod
    def empty(cls) -> "ForecastArrays":
        """No usable horizon, so the caller should skip the run."""
        blank = np.array([], dtype=float)
        return cls(blank, blank, blank, blank, blank, blank, blank, blank)


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
# Symmetric bound on how far one sample's Newton target may sit from the
# *current* estimate before it is clipped. Centred on the current value,
# zero-mean noise has zero-mean effect after clipping; rejecting or clamping
# against fixed global bounds does not have that property, because the
# midpoint of a fixed range is not the current estimate.
_LEARNER_TRUST_REGION = 0.5

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
            self._async_load_dhw_draws,
            self._async_load_dhw_legionella,
            self._async_load_thermal_learning,
            self._async_load_price_model,
            self._async_load_accuracy,
            self._async_load_energy_totals,
            self._async_load_ledger,
            self._async_setup_peak_guard,
            self._async_load_manual_plan,
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

        # --- Hot water, v4.0.0 T3 -----------------------------------------
        # #18: day-type profiles learned BESIDE the pooled one, blended
        # toward pooled by their own evidence. A store that has only ever
        # seen the pooled profile loads with zero day-type samples, which
        # blends to exactly the pooled answer.
        self._dhw_profile_weekday: list[float] = self._dhw_hourly_profile.copy()
        self._dhw_profile_weekend: list[float] = self._dhw_hourly_profile.copy()
        #: Distinct DAYS with draw evidence per day type — the blend's
        #: trust must measure days lived, not sensor ticks survived.
        self._dhw_daytype_samples: list[int] = [0, 0]  # [weekday, weekend]
        self._dhw_daytype_last_day: list[str] = ["", ""]
        # #32/#20: per-window draw-occurrence statistics, own store.
        self._draw_stats = DrawStats()
        self._dhw_draws_store: Store = Store(
            hass,
            DHW_PROFILE_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_dhw_draws",
        )
        self._dhw_draws_dirty: bool = False
        # #24: minutes the tank has HELD the disinfection temperature.
        self._legionella_hold_minutes: float = 0.0
        self._legionella_hold_last: datetime | None = None
        # #6: last commanded pump states, so actuation is transitions-only.
        self._pump_commanded: dict[str, bool] = {}

        # Self-learned buffer tank standby cooling, in °C/h at the same
        # reference ΔT as the DHW rate. Only learned when a buffer tank
        # temperature sensor is configured.
        # 0.0 on the parameters means "no rate known yet"; the prior then comes
        # from the tank's own size rather than from a 35 L tank's number.
        self._buffer_cooling_rate: float = float(
            self._thermal_params.buffer_cooling_rate
            or default_buffer_cooling_rate(
                self._thermal_params.buffer_tank_volume
            )
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
        self._lower_floor_loss_ratio: float = DEFAULT_LOWER_FLOOR_LOSS_RATIO
        self._lower_floor_loss_samples: int = 0

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

        self._price_qdays_seen: set[str] = set()

        # --- Grid transfer fees and the monthly ledger (v4.0.0 T1) ---------
        self._grid_fee_cache: tuple | None = None
        self._ledger = MonthlyLedger()
        self._ledger_store: Store = Store(
            hass,
            1,
            f"{DOMAIN}_{entry.entry_id}_ledger",
        )

        # --- Capacity tariff (item 8) --------------------------------------
        self._peak_tracker = PeakTracker()

        # --- Live peak guard, fuse and outage recovery (v4.0.0 T2) ---------
        self._peak_guard = GuardState()
        self._unsub_peak_guard = None
        self._guard_last_fold: datetime | None = None
        self._fuse_advisor: dict[str, Any] = {}
        self._fuse_advisor_at: datetime | None = None
        self._outage_recovery_until: datetime | None = None
        self._outage_dhw_until: datetime | None = None

        # --- PV self-consumption (item 9) ----------------------------------
        self._pv_surplus: np.ndarray | None = None
        self._pv_summary: dict[str, Any] = {}
        self._pv_production: float | None = None

    def _init_features(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Away mode, accuracy tracking, learning experiments and totals."""
        self._external_heat = ExternalHeatDetector(self._external_heat_config())
        self._external_heat_active: bool = False
        # Last valve target actually written in smart_write mode, so identical
        # answers on consecutive cycles do not re-command the device.
        self._valve_commanded_target: float | None = None
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

        # --- Manual plan override -----------------------------------------
        # The active hand-arranged plan, if any. Persisted through its own Store
        # (never config options: an override changes far too often, and writing
        # options reloads the whole entry) so a plan survives a restart within
        # the day it was set for.
        self._manual_override: ManualOverride | None = None
        self._manual_plan_store: Store = Store(
            hass,
            MANUAL_PLAN_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_manual_plan",
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

        # #18: day-type profiles are additive keys. A pooled-only store —
        # every store written before T3 — leaves both arrays at the pooled
        # profile with zero samples, and the blend below then answers
        # exactly the pooled pattern.
        for attr, key, count_idx in (
            ("_dhw_profile_weekday", "profile_weekday", 0),
            ("_dhw_profile_weekend", "profile_weekend", 1),
        ):
            arr = stored.get(key)
            if isinstance(arr, list) and len(arr) == 24:
                setattr(self, attr, self._normalize_dhw_profile(arr))
            else:
                setattr(self, attr, self._dhw_hourly_profile.copy())
            try:
                self._dhw_daytype_samples[count_idx] = max(
                    0, int(stored.get(f"{key}_samples", 0))
                )
            except (TypeError, ValueError):
                self._dhw_daytype_samples[count_idx] = 0

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
                    # #18: additive — old loaders ignore these keys.
                    "profile_weekday": self._dhw_profile_weekday,
                    "profile_weekend": self._dhw_profile_weekend,
                    "profile_weekday_samples": self._dhw_daytype_samples[0],
                    "profile_weekend_samples": self._dhw_daytype_samples[1],
                    "updated_at": dt_util.now().isoformat(),
                }
            )
        except Exception as err:
            _LOGGER.debug("Could not persist DHW profile: %s", err)

    async def _async_load_dhw_draws(self) -> None:
        """Load the per-window draw statistics (#32)."""
        try:
            stored = await self._dhw_draws_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load DHW draw statistics: %s", err)
            return
        if stored:
            self._draw_stats = DrawStats.from_dict(stored)

    async def _async_save_dhw_draws(self) -> None:
        try:
            await self._dhw_draws_store.async_save(self._draw_stats.as_dict())
            self._dhw_draws_dirty = False
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist DHW draw statistics: %s", err)

    def _dhw_pattern_for(self, weekend: bool) -> list[float]:
        """The #18 blended pattern for one day type, volume-preserving.

        ``w = n/(n+K)`` leans on the pooled profile until the day type has
        real evidence of its own; the result is re-normalised so each day
        type still budgets the same daily volume — the profile decides
        *when*, never *how much*.
        """
        idx = 1 if weekend else 0
        daytype = (
            self._dhw_profile_weekend if weekend else self._dhw_profile_weekday
        )
        n = float(self._dhw_daytype_samples[idx])
        w = n / (n + DHW_DAYTYPE_BLEND_K) if n > 0 else 0.0
        if w <= 0.0:
            return self._dhw_hourly_profile.copy()
        blended = [
            (1.0 - w) * pooled + w * day
            for pooled, day in zip(self._dhw_hourly_profile, daytype)
        ]
        return self._normalize_dhw_profile(blended)

    def _prepare_dhw_inputs(self, now: datetime) -> None:
        """Refresh everything the hot-water plan reads, before each solve.

        One chokepoint on purpose: the inlet, the day-type pattern, the
        quantile targets and the elastic-legionella ceiling all reach the
        solver through parameters set here, so a stale value can survive at
        most one cycle and there is exactly one place to look.
        """
        params = self._thermal_params

        # #18: today's blended pattern. With no day-type evidence this IS
        # the pooled profile, byte for byte.
        params.dhw_hourly_draw_pattern = self._dhw_pattern_for(
            now.weekday() >= 5
        )

        # The inlet: live sensor wins, then the seasonal model, whose
        # default amplitude of zero keeps it at the configured mean.
        inlet: float | None = None
        entity = self._config.get(CONF_DHW_INLET_ENTITY)
        if entity:
            state = self.hass.states.get(entity)
            try:
                value = float(state.state) if state is not None else None
            except (TypeError, ValueError):
                value = None
            if value is not None and -5.0 <= value <= 35.0:
                inlet = value
        if inlet is None:
            inlet = params.seasonal_inlet_temp(now.timetuple().tm_yday)
        params.dhw_inlet_current = inlet

        # #20: the learned heavy-day targets, only when opted in — and
        # only with CONFIGURED time frames. With none, the optimizer plans
        # against windows derived from the learned profile, whose labels
        # can never match statistics keyed by the configured spec; rather
        # than let the feature silently do nothing, it is explicitly
        # scoped to configured frames (the option text says so too).
        params.dhw_window_ready_energy = None
        if params.dhw_enabled and params.dhw_windows_active and bool(
            self._config.get(
                CONF_DHW_QUANTILE_TARGETS_ENABLED,
                DEFAULT_DHW_QUANTILE_TARGETS_ENABLED,
            )
        ):
            table: dict[str, tuple[float, int]] = {}
            for label in labels_for(params.dhw_demand_windows):
                count = self._draw_stats.count(label)
                p90 = self._draw_stats.quantile(label, 0.9)
                if count > 0 and p90 is not None:
                    table[label] = (p90, count)
            params.dhw_window_ready_energy = table or None

        # #47: what a typical remaining day is expected to bottom out at.
        params.dhw_legionella_price_ceiling = None
        if (
            params.dhw_elastic_legionella_enabled
            and params.dhw_legionella_enabled
            and self._dhw_last_legionella is not None
            and self._prices
        ):
            deadline = self._dhw_last_legionella + timedelta(
                days=float(params.dhw_legionella_interval_days)
            )
            day_types: list[int] = []
            day = (now + timedelta(days=1)).date()
            while day <= deadline.date():
                day_types.append(1 if day.weekday() >= 5 else 0)
                day = day + timedelta(days=1)
            level = float(
                np.mean([p.get("total", 0.0) for p in self._prices])
            )
            ceiling = self._price_model.expected_daily_min(
                sorted(set(day_types)), level
            )
            params.dhw_legionella_price_ceiling = ceiling

    def _dhw_mixed_water(self) -> dict[str, Any]:
        """#28: what the tank actually holds, in shower terms.

        ``V·(T_tank − T_inlet)/(40 − T_inlet)`` litres of 40 °C water — the
        translation between the abstract tank temperature and the only
        quantity anyone showers in.
        """
        params = self._thermal_params
        tank = self._current_state.dhw_temperature
        if not params.dhw_enabled or tank is None:
            return {}
        inlet = params.dhw_inlet_reference
        if 40.0 - inlet < 1.0:
            return {}
        litres = (
            params.dhw_tank_volume * max(0.0, float(tank) - inlet) / (40.0 - inlet)
        )
        flow = _as_float(
            self._config.get(CONF_SHOWER_FLOW_LPM), DEFAULT_SHOWER_FLOW_LPM
        )
        out = {"litres_40c": round(litres, 1), "tank_temperature": round(float(tank), 1)}
        if flow > 0:
            out["shower_minutes"] = round(litres / flow, 1)
        return out

    def _dhw_setpoint_sweep(self) -> dict[str, Any]:
        """#9: replay candidate setpoints against everything learned.

        Read-only. For each candidate: a day of standby loss at that
        temperature through the LEARNED cooling rate, the fixed daily draw
        energy from the learned consumption and the current inlet, both
        priced at the learned COP for that tank temperature and the recent
        mean price. The recommendation is the cheapest candidate that
        still covers the heaviest learned window demand.
        """
        params = self._thermal_params
        if not params.dhw_enabled or not self._prices:
            return {}
        c_dhw = max(params.dhw_tank_thermal_mass, 0.05)
        inlet = params.dhw_inlet_reference
        outdoor = float(self._current_state.outdoor_temperature)
        mean_price = float(
            np.mean([p.get("total", 0.0) for p in self._prices])
        )
        # The heaviest ready energy any window needs, learned where
        # evidence exists, profile-mean otherwise. Without the fallback a
        # fresh install has a 0 kWh "heaviest window", every candidate
        # trivially covers it, and the advisor recommends the sweep bottom
        # regardless of how the household actually lives.
        heaviest = 0.0
        pattern = params.effective_dhw_draw_pattern()
        windows = params.dhw_demand_windows
        for window, label in zip(windows, labels_for(windows)):
            p90 = self._draw_stats.quantile(label, 0.9)
            if p90 is None:
                p90 = sum(
                    params.dhw_draw_power
                    * pattern[hour]
                    * overlap_fraction(float(hour), float(hour) + 1.0, [window])
                    for hour in range(24)
                )
            heaviest = max(heaviest, p90)
        draw_day_kwh = (
            params.dhw_daily_consumption
            * WATER_SPECIFIC_HEAT
            * max(params.dhw_setpoint - inlet, 0.0)
        )
        candidates = []
        best: dict[str, Any] | None = None
        for setpoint in range(48, 61, 2):
            t = float(setpoint)
            standby_kwh = (
                params.dhw_tank_heat_loss_coefficient
                * max(0.5 * (t + params.dhw_min_temp) - DHW_AMBIENT_TEMP, 0.0)
                * 24.0
            )
            cop = max(
                float(self._thermal_model.compute_cop_dhw(outdoor, t)), 0.5
            )
            cost_day = (standby_kwh + draw_day_kwh) / cop * mean_price
            # Can a tank at this setpoint cover the heaviest window from
            # its usable band at all?
            usable_kwh = c_dhw * max(t - params.dhw_min_temp, 0.0)
            meets = usable_kwh >= heaviest
            entry = {
                "setpoint": setpoint,
                "cost_per_day": round(cost_day, 2),
                "meets_heaviest_window": meets,
            }
            candidates.append(entry)
            if meets and (best is None or cost_day < best["cost_per_day"]):
                best = entry
        # A tank too small to hold its heaviest window in the usable band
        # at ANY setpoint gets the advice a plumber would give — run it as
        # hot as allowed — flagged honestly rather than answered with
        # nothing. In-window reheat covers the remainder in practice; the
        # storage band is simply the margin.
        covers = best is not None
        if best is None and candidates:
            best = candidates[-1]
        return {
            "current_setpoint": params.dhw_setpoint,
            "recommended_setpoint": (best or {}).get("setpoint"),
            "covers_heaviest_window": covers,
            "heaviest_window_kwh": round(heaviest, 2),
            "candidates": candidates,
        }

    async def _async_drive_pumps(self) -> None:
        """#6: follow the plan with the circulation pumps, transitions only.

        Only entities the user explicitly configured are ever touched, and
        each is commanded exactly once per state change.
        """
        vvc_entity = self._config.get(CONF_VVC_PUMP_ENTITY)
        space_entity = self._config.get(CONF_SPACE_PUMP_ENTITY)
        if not vvc_entity and not space_entity:
            return
        now = dt_util.now()
        params = self._thermal_params

        if vvc_entity:
            # With hot water disabled (or no schedule) there is no frame to
            # exploit and the loop is simply left on — never abandoned in
            # whatever state the last schedule-driven command left it.
            windows = (
                list(params.dhw_windows)
                if params.dhw_enabled and params.dhw_windows_active
                else []
            )
            on, reason = pump_schedule.vvc_should_run(
                now.hour + now.minute / 60.0,
                windows,
                _as_float(
                    self._config.get(CONF_VVC_LEAD_MINUTES),
                    DEFAULT_VVC_LEAD_MINUTES,
                ),
            )
            await self._async_set_pump(vvc_entity, on, reason)

        if space_entity:
            result = self._optimization_result
            idx = 0
            schedule = None
            if result is not None and result.power_schedule:
                schedule = result.power_schedule
                dt_hours = max(self._opt_config.dt_hours, 1e-6)
                if result.timestamps:
                    idx = int(
                        max(
                            0.0,
                            (now - result.timestamps[0]).total_seconds()
                            / 3600.0
                            / dt_hours,
                        )
                    )
            heat_now, heat_next = pump_schedule.plan_commands_heat(
                schedule, idx
            )
            action = self._current_action or {}
            curve_driven = bool(action.get("heat_pump_on")) or (
                abs(_as_float(action.get("displace_value"), 0.0)) > 0.01
            )
            state = self._current_state
            zones = [state.room_temperature]
            if params.two_zone_enabled:
                zones += [
                    state.upper_floor_temperature,
                    state.lower_floor_temperature,
                ]
            on, reason = pump_schedule.space_pump_should_run(
                plan_heat_now=heat_now,
                plan_heat_next=heat_next,
                curve_driven=curve_driven,
                zone_temps=[z for z in zones if z is not None],
                floor_temp=float(self._opt_config.min_temp),
                outdoor_temp=state.outdoor_temperature,
            )
            await self._async_set_pump(space_entity, on, reason)

    async def _async_set_pump(
        self, entity_id: str, on: bool, reason: str
    ) -> None:
        previous = self._pump_commanded.get(entity_id)
        if previous is not None and previous == on:
            return
        service = "turn_on" if on else "turn_off"
        try:
            await self.hass.services.async_call(
                "homeassistant", service, {"entity_id": entity_id}
            )
            _LOGGER.info("Pump %s → %s: %s", entity_id, service, reason)
        except Exception as err:  # noqa: BLE001 - a pump must never kill the cycle
            _LOGGER.warning("Could not command pump %s: %s", entity_id, err)
            return
        # Recorded only AFTER the call succeeded: a command that failed
        # (entity briefly unavailable) must be retried next tick, not
        # remembered as done.
        self._pump_commanded[entity_id] = on

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

        ratio = stored.get("lower_floor_loss_ratio")
        if ratio is not None:
            try:
                self._apply_lower_floor_loss_ratio(float(ratio))
                self._lower_floor_loss_samples = int(
                    stored.get("lower_floor_loss_samples", 0)
                )
                _LOGGER.info(
                    "Loaded learned lower floor loss ratio %.3f (%d samples)",
                    self._lower_floor_loss_ratio,
                    self._lower_floor_loss_samples,
                )
            except (TypeError, ValueError) as err:
                _LOGGER.debug("Could not load lower floor loss ratio: %s", err)

        cop_scale = stored.get("cop_scale")
        if cop_scale is not None:
            try:
                self._apply_cop_scale(float(cop_scale))
                self._cop_samples = int(stored.get("cop_samples", 0))
                _LOGGER.info(
                    "Loaded learned COP scale %.3f (%d samples)",
                    self._cop_scale,
                    self._cop_samples,
                )
            except (TypeError, ValueError) as err:
                _LOGGER.debug("Could not load COP scale: %s", err)

    async def _async_save_thermal_learning(self) -> None:
        """Persist the learned buffer and building parameters."""
        try:
            await self._thermal_learning_store.async_save(
                {
                    "buffer_cooling_rate": self._buffer_cooling_rate,
                    "buffer_cooling_samples": self._buffer_cooling_samples,
                    "house_heat_loss_scale": self._house_heat_loss_scale,
                    "house_heat_loss_samples": self._house_heat_loss_samples,
                    "lower_floor_loss_ratio": self._lower_floor_loss_ratio,
                    "lower_floor_loss_samples": self._lower_floor_loss_samples,
                    # Every plan is priced through the COP curve, so a learned
                    # correction that evaporated on restart silently re-based
                    # all costs on the nameplate figure.
                    "cop_scale": self._cop_scale,
                    "cop_samples": self._cop_samples,
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

        space_plan = {
            "forecast": space_forecast,
            "slots": space_slots,
            "total_energy_kwh": round(sum(raw_space) * dt_hours, 2),
            "total_cost": round(
                sum(p * pr for p, pr in zip(raw_space, raw_prices)) * dt_hours, 2
            ),
            "active_now": bool(raw_space and raw_space[0] > 0.05),
        }
        # Only when a hold schedule was adopted (smart_write), so every
        # existing capture of the plan view stays byte-for-byte identical.
        if result.valve_target_schedule:
            space_plan["valve_target_schedule"] = [
                round(v, 1) for v in result.valve_target_schedule
            ]
        return {
            "space_plan": space_plan,
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
        interval_hours = (
            self._config.get(
                CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
            )
            / 60.0
        )
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
            # Samples arrive once per update cycle, so the window has to
            # outlast the interval or every pair is rejected and the detector
            # is blind at exactly the 60-minute setting it appears to support.
            max_sample_hours=max(1.0, 1.5 * interval_hours),
            wood_tank_volume_l=_as_float(
                self._config.get(CONF_WOOD_TANK_VOLUME),
                DEFAULT_WOOD_TANK_VOLUME,
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

    def _space_demand_kw(self) -> float:
        """Current space-heating standing loss, kW thermal."""
        params = self._thermal_params
        state = self._current_state
        if params.two_zone_enabled:
            u = params.upper_floor_heat_loss + params.lower_floor_heat_loss
        else:
            u = params.heat_loss_coefficient
        return max(
            0.0,
            u * (state.room_temperature - state.outdoor_temperature),
        )

    def _update_external_heat_detection(self) -> None:
        """Fold this interval's observation into the external-heat detector."""
        self._external_heat.config = self._external_heat_config()
        # The wood-furnace sensors go through the stale-aware reader: a
        # stalled hot probe would look like an indefinite free fire, which is
        # the expensive failure direction, so staleness maps to absence.
        reader = InputReader(
            self.hass,
            self._config,
            enabled=bool(
                self._config.get(
                    CONF_STALENESS_ENABLED, DEFAULT_STALENESS_ENABLED
                )
            ),
            scale=_as_float(
                self._config.get(CONF_STALENESS_SCALE),
                DEFAULT_STALENESS_SCALE,
            ),
        )
        outlet = reader.read(CONF_VALVE_OUTLET_TEMP_ENTITY)
        wood_top = reader.read(CONF_WOOD_TANK_TOP_ENTITY)
        wood_bottom = reader.read(CONF_WOOD_TANK_BOTTOM_ENTITY)
        observation = ExternalHeatObservation(
            now=dt_util.now(),
            dhw_temp=self._current_state.dhw_temperature,
            buffer_temp=self._current_state.buffer_tank_temperature,
            commanded_power_kw=self._commanded_power(),
            measured_power_kw=self._measured_power,
            dhw_max_rise_c_per_h=self._max_pump_rise("dhw"),
            buffer_max_rise_c_per_h=self._max_pump_rise("buffer"),
            override=self._external_heat_override(),
            outlet_temp=outlet.value if outlet.ok else None,
            wood_top=wood_top.value if wood_top.ok else None,
            wood_bottom=wood_bottom.value if wood_bottom.ok else None,
            hp_tank_temp=self._current_state.buffer_tank_temperature,
            space_demand_kw=self._space_demand_kw(),
        )
        state = self._external_heat.update(observation)
        self._external_heat_active = self._external_heat.suppressing
        if state.active:
            _LOGGER.debug(
                "External heat source active (%s): %s",
                state.source,
                "; ".join(state.evidence),
            )

    def _external_heat_forecast(self, n_steps: int) -> np.ndarray | None:
        """Free-heat forecast for the solve, or None when there is nothing.

        The detector's own bounds do the safety work (a hard two-hour
        horizon, a fade, and the measured wood-tank energy); this only turns
        its answer into the array the optimizer takes.
        """
        if not self._external_heat.suppressing:
            return None
        forecast = self._external_heat.forecast_free_heat(
            n_steps,
            self._opt_config.time_step_minutes / 60.0,
            # With the wood tank modelled its stored energy is initial state
            # in the solve; budgeting the forecast against it as well would
            # count the same heat twice (issue #40).
            tank_modelled=self._thermal_params.two_tank_modelled,
        )
        arr = np.asarray(forecast, dtype=float)
        return arr if bool(np.any(arr > 0.0)) else None

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

        # In the frosting band the shortfall belongs to the defrost derate,
        # which learns from the same signal; letting both learners fold in the
        # same interval corrects one shortfall twice. See defrost.in_frost_band.
        if in_frost_band(self._current_state.outdoor_temperature):
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
            # The learned split belongs in the total the diagnostic reports, or
            # it would show a number the model does not actually use.
            base = params.upper_floor_heat_loss + params.lower_floor_heat_loss_learned
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

    def _buffer_cooling_bounds(self) -> tuple[float, float]:
        """Plausible cooling-rate range for *this* tank, C/h.

        Volume-dependent, because UA follows surface area while the rate is
        UA/C: a big accumulator loses proportionally far less than a small
        buffer. The flat bounds this replaced floored a 750 L tank around
        17 W/K when a real one is nearer 2, so the learner could never reach
        the truth however long it ran.
        """
        return buffer_cooling_rate_bounds(
            self._thermal_params.buffer_tank_volume
        )

    def _apply_buffer_cooling_rate(self, rate: float) -> None:
        """Clamp a buffer cooling rate to a plausible range and push it out."""
        low, high = self._buffer_cooling_bounds()
        self._buffer_cooling_rate = float(np.clip(rate, low, high))
        self._thermal_params.buffer_cooling_rate = self._buffer_cooling_rate

    def _apply_house_heat_loss_scale(self, scale: float) -> None:
        """Clamp the house heat loss correction and push it to the model."""
        self._house_heat_loss_scale = float(
            np.clip(scale, HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX)
        )
        self._thermal_params.house_heat_loss_scale = self._house_heat_loss_scale

    def _apply_lower_floor_loss_ratio(self, ratio: float) -> None:
        """Clamp the learned zone split and push it to the model."""
        self._lower_floor_loss_ratio = float(
            np.clip(ratio, LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX)
        )
        self._thermal_params.lower_floor_loss_ratio = self._lower_floor_loss_ratio

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

        # With a mixing valve the tank is a store the house draws on while the
        # pump is off — that is the feature — so a pump-off interval is not
        # quiet decay, and reading the draw as standby loss would creep the
        # learned rate toward its ceiling and quietly price storage off the
        # table. There is no interval this learner can trust in a throttling
        # mode; the volume-derived prior (or an explicitly configured rate)
        # stands instead.
        if mixing_valve.is_throttling(self._thermal_params.mixing_valve_mode):
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
        low, high = self._buffer_cooling_bounds()
        if observed < low or observed > high:
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
        # The action that governed the elapsed interval is the one in
        # ``_current_action`` *right now*: the learners run before this cycle's
        # optimization replaces it, so it still holds what the pump was told at
        # the previous cycle — exactly the interval being replayed. The old
        # snapshot taken a cycle earlier was one action further back, and under
        # bang-bang price scheduling that off-by-one injected a spurious
        # residual an order of magnitude above the learning signal.
        previous_power = float(self._current_action.get("power", 0.0))

        # Snapshot for the next interval before any early return, so a rejected
        # sample does not poison the following one with a stale baseline.
        self._last_house_sample = replace(self._current_state)
        self._last_house_sample_time = now

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
        # Same zone as the residual, or the Newton step is taken about a
        # temperature difference the residual does not describe.
        driving_temp = (
            previous_state.upper_floor_temperature
            if self._thermal_params.two_zone_enabled
            else previous_state.room_temperature
        )
        delta_t = driving_temp - outdoor
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

        # Compare like with like. `observed` is the indoor sensor, which in
        # two-zone mode is the *upper* floor -- while `room_temperature` on the
        # prediction is the area-weighted average of both zones. Differencing
        # those two conflates the zone split with the heat-loss error: measured
        # against the real model, a 1.5 K difference between the floors injects
        # a systematic +0.53 K into the residual, over half the rejection
        # threshold. It does not average out, so it accumulated into the learned
        # scale, and at a 3 K split it exceeded the threshold and the sample was
        # thrown away instead.
        params = self._thermal_params
        predicted_room = (
            predicted_state.upper_floor_temperature
            if params.two_zone_enabled
            else predicted_state.room_temperature
        )
        residual = observed - predicted_room
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
        #
        # Two-zone fits from the upper zone alone, matching the residual above.
        # The scale still multiplies both zones -- it owns the overall *level* --
        # while `lower_floor_loss_ratio` owns the split and is fitted separately
        # from the lower zone. Splitting the jobs this way is what keeps the two
        # identifiable: the ratio does not touch the upper zone, so this fit is
        # unaffected by it.
        if params.two_zone_enabled:
            base_u = params.upper_floor_heat_loss
            capacity = params.upper_floor_thermal_mass
        else:
            base_u = params.heat_loss_coefficient
            capacity = params.room_thermal_mass
        if base_u <= 1e-6 or capacity <= 1e-6:
            return

        current_u = base_u * self._house_heat_loss_scale
        # Warmer than predicted means the model is over-estimating the loss.
        delta_u = -residual * capacity / (delta_t * dt_h)
        target_scale = (current_u + delta_u) / base_u
        if not np.isfinite(target_scale):
            return
        # Bound the target symmetrically about the current value rather than
        # discarding or globally clamping it. Discarding was one-sided: a
        # warm-side residual of just +0.13 °C (inside sensor noise) drove the
        # target non-positive and threw the sample away, while cold-side
        # residuals were kept to the full 1.0 °C guard — pure zero-mean noise
        # ratcheted the scale upward, measured at 1.0 → 1.2 in 60 days at
        # σ=0.1 °C. A clamp to fixed global bounds merely slows the same drift,
        # because their midpoint is not the current value; a symmetric trust
        # region makes noise-dominated samples exactly zero-mean, and the EWMA
        # and step limit below still decide how fast genuine signal moves it.
        target_scale = float(
            np.clip(
                target_scale,
                self._house_heat_loss_scale - _LEARNER_TRUST_REGION,
                self._house_heat_loss_scale + _LEARNER_TRUST_REGION,
            )
        )

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

    async def _async_learn_lower_floor_loss(self) -> None:
        """Redistribute the heat loss between the two zones (item 31).

        Only reachable with a real lower-floor sensor. Without one the lower zone
        is inferred from the floor return water, and the inference is derived
        from the same sensor as the slab -- so the regressor has no independent
        variance and fitting against it would be fitting against the model's own
        prior. Item 30 is what makes this measurable at all.

        The split, not the level. ``house_heat_loss_scale`` multiplies both zones
        and is fitted from the upper one; this ratio multiplies only the lower.
        Two parameters against two independent measurements, so neither can
        absorb the other's error and drift.

        Same Newton step as the house learner, taken about the lower zone:
        predicted lower-zone change is linear in its own U with slope
        ``-(T_lower - T_out)·Δt / C_lower``.
        """
        now = dt_util.now()
        params = self._thermal_params
        previous_state = self._last_house_sample
        previous_time = self._last_house_sample_time
        # See the house learner: the current action is the one that governed
        # the elapsed interval.
        previous_power = float(self._current_action.get("power", 0.0))
        observed = self._current_state.lower_floor_temperature

        if not params.two_zone_enabled:
            return
        # A configured sensor is the whole precondition. `_update_current_state`
        # falls back to the return-temp estimate when it is missing or stale, and
        # that estimate carries no information about this coefficient.
        if not self._config.get(CONF_LOWER_FLOOR_TEMP_ENTITY):
            return

        frozen = self._learning_frozen(
            CONF_INDOOR_TEMP_ENTITY,
            CONF_OUTDOOR_TEMP_ENTITY,
            CONF_LOWER_FLOOR_TEMP_ENTITY,
        )
        if frozen:
            self._learner_freeze_reason = frozen
            return

        if previous_state is None or previous_time is None or observed is None:
            return

        dt_h = (now - previous_time).total_seconds() / 3600.0
        if dt_h < HOUSE_LOSS_MIN_SAMPLE_HOURS or dt_h > HOUSE_LOSS_MAX_SAMPLE_HOURS:
            return

        outdoor = previous_state.outdoor_temperature
        delta_t = previous_state.lower_floor_temperature - outdoor
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
            _LOGGER.debug("Lower floor loss learning simulation failed: %s", err)
            return

        residual = observed - predicted_state.lower_floor_temperature
        if not np.isfinite(residual):
            return
        if abs(residual) > HOUSE_LOSS_MAX_RESIDUAL:
            _LOGGER.debug(
                "Ignoring lower floor loss sample: residual %.2f°C is too large "
                "to be a heat loss error",
                residual,
            )
            return

        base_u = params.lower_floor_heat_loss * self._house_heat_loss_scale
        capacity = params.lower_floor_thermal_mass
        if base_u <= 1e-6 or capacity <= 1e-6:
            return

        current_u = base_u * self._lower_floor_loss_ratio
        delta_u = -residual * capacity / (delta_t * dt_h)
        target_ratio = (current_u + delta_u) / base_u
        if not np.isfinite(target_ratio):
            return
        # Clamp the target rather than discarding it when it comes out
        # implausible, because discarding is not symmetric here and would bias
        # the fit one way.
        #
        # The lower zone's standalone time constant is `C / u` = 8.0 / 0.07,
        # over a hundred hours, so its temperature barely moves and the Newton
        # step is correspondingly enormous: a residual of only +0.12 K implies a
        # ΔU larger than the whole coefficient, i.e. a *negative* target. Those
        # are exactly the intervals where the house lost less heat than
        # predicted. Rejecting them while accepting the cold-side ones -- whose
        # targets stay positive -- would let the ratio ratchet upward on noise
        # alone. And the clamp must be centred on the *current* estimate, not
        # on the fixed [MIN, MAX] range: with the estimate sitting off-centre
        # in that range, symmetric noise clips asymmetrically and drifts the
        # ratio toward the range's midpoint. The trust region keeps both sides
        # equally, and the EWMA and step limit below are what actually decide
        # how fast the estimate moves. `_apply_lower_floor_loss_ratio` still
        # holds the final value inside the global bounds.
        target_ratio = float(
            np.clip(
                target_ratio,
                self._lower_floor_loss_ratio - _LEARNER_TRUST_REGION,
                self._lower_floor_loss_ratio + _LEARNER_TRUST_REGION,
            )
        )

        new_ratio = (
            1.0 - HOUSE_LOSS_ALPHA
        ) * self._lower_floor_loss_ratio + HOUSE_LOSS_ALPHA * target_ratio
        max_step = self._lower_floor_loss_ratio * HOUSE_LOSS_MAX_STEP
        new_ratio = float(
            np.clip(
                new_ratio,
                self._lower_floor_loss_ratio - max_step,
                self._lower_floor_loss_ratio + max_step,
            )
        )
        self._apply_lower_floor_loss_ratio(new_ratio)
        self._lower_floor_loss_samples += 1

        _LOGGER.debug(
            "Learned lower floor loss split: residual %.3f°C over %.2fh at "
            "ΔT=%.1f°C suggests ratio %.3f, model now %.3f (%d samples)",
            residual,
            dt_h,
            delta_t,
            target_ratio,
            self._lower_floor_loss_ratio,
            self._lower_floor_loss_samples,
        )
        if self._lower_floor_loss_samples % 10 == 0:
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
        a planned cycle, a manual boost, a wood coil or an immersion heater.

        With free disinfection (#24) switched on, the credit is
        hold-verified: the tank must spend ``DHW_LEGIONELLA_HOLD_MINUTES``
        at temperature, integrated across observations, before the
        completion timestamp is written — exactly the timestamp a planned
        cycle writes. A momentary blip at 60 °C kills nothing and credits
        nothing. With the flag off the historical instant-credit rule is
        untouched.
        """
        target = float(self._thermal_params.dhw_legionella_temp)
        now = dt_util.now()

        if bool(
            self._config.get(
                CONF_DHW_FREE_DISINFECTION_ENABLED,
                DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
            )
        ):
            if dhw_temp >= target - 0.5:
                previous_obs = self._legionella_hold_last
                # Accumulate only hot-to-hot gaps: an interval that STARTED
                # cold proves nothing about the water in between. Capped so
                # a long observation gap cannot claim more than was
                # plausibly held.
                if previous_obs is not None:
                    gap_min = (now - previous_obs).total_seconds() / 60.0
                    self._legionella_hold_minutes += min(gap_min, 90.0)
                self._legionella_hold_last = now
                if self._legionella_hold_minutes < DHW_LEGIONELLA_HOLD_MINUTES:
                    return
            else:
                # Not at temperature: the accumulation chain breaks, and a
                # clear fall below the band starts the hold over.
                self._legionella_hold_last = None
                if dhw_temp < target - 1.5:
                    self._legionella_hold_minutes = 0.0
                return
        elif dhw_temp < target - 1.0:
            return

        previous = self._dhw_last_legionella
        if previous is not None and (now - previous).total_seconds() < 3600:
            return
        self._legionella_hold_minutes = 0.0
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
            previous_temp,
            temp_drop,
            dt_h,
            now.hour,
            heated_during_interval,
            weekend=now.weekday() >= 5,
        )
        await self._async_fold_draw_stats(now, previous_temp, temp_drop, dt_h)

    async def _async_fold_draw_stats(
        self, now: datetime, previous_temp: float, temp_drop: float, dt_h: float
    ) -> None:
        """Fold one interval's beyond-standby draw energy into #32's stats.

        External heat is the one contamination the freeze guard upstream
        does not cover: a wood burn drives the tank temperature and every
        drop-based attribution with it, so those intervals are skipped
        outright. Heated intervals ARE folded — heating makes the drop
        smaller, so the attributed energy is a lower bound of the true
        draw, which can only make the learned heavy-day target
        conservative relative to reality, never inflated.
        """
        if getattr(self._current_state, "external_heat_active", False):
            return
        params = self._thermal_params
        if not params.dhw_enabled:
            return
        standby_rate = (
            self._dhw_cooling_rate
            * max(0.0, previous_temp - DHW_AMBIENT_TEMP)
            / DHW_COOLING_REFERENCE_DELTA
        )
        intensity = max(0.0, temp_drop / dt_h - standby_rate)  # °C/h beyond standby
        energy_kwh = (
            intensity * dt_h * max(params.dhw_tank_thermal_mass, 0.05)
        )
        windows = params.dhw_demand_windows
        label = draw_window_label(
            now.hour + now.minute / 60.0, windows
        )
        self._draw_stats.prune(labels_for(windows))
        before = {k: len(v) for k, v in self._draw_stats.reservoirs.items()}
        self._draw_stats.fold(now, label, energy_kwh)
        after = {k: len(v) for k, v in self._draw_stats.reservoirs.items()}
        # Persist when an occurrence closes, and also whenever real energy
        # was folded into the OPEN occurrence — as_dict carries it, and
        # saving only at close time meant a restart mid-shower silently
        # dropped everything since the last close, dragging the p90 down.
        # Zero-energy ticks (most of the day) still cause no churn.
        if before != after or energy_kwh > 1e-4:
            await self._async_save_dhw_draws()

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
        self,
        previous_temp: float,
        temp_drop: float,
        dt_h: float,
        hour: int,
        heated: bool,
        weekend: bool = False,
    ) -> None:
        """Learn hourly DHW usage profile from observed temperature drops."""
        # Learn only while DHW is not actively heated, and only from the part
        # of the drop that standby loss cannot explain. The tank cools all the
        # time — roughly 0.4 °C/h for a 55 °C tank at the default rate — and
        # attributing that to usage taught a phantom draw into every idle
        # hour, washing the real morning/evening pattern towards flat.
        if temp_drop < 0.15 or heated:
            return

        standby_rate = (
            self._dhw_cooling_rate
            * max(0.0, previous_temp - DHW_AMBIENT_TEMP)
            / DHW_COOLING_REFERENCE_DELTA
        )
        draw_intensity = temp_drop / dt_h - standby_rate
        if draw_intensity <= 0.05:
            return

        profile = self._dhw_hourly_profile.copy()
        profile[hour] = (
            (1.0 - DHW_PROFILE_EWMA_ALPHA) * profile[hour]
            + DHW_PROFILE_EWMA_ALPHA * draw_intensity
        )
        self._dhw_hourly_profile = self._normalize_dhw_profile(profile)
        self._thermal_params.dhw_hourly_draw_pattern = self._dhw_hourly_profile.copy()

        # #18: the same observation also teaches this day type's own
        # profile. Both are normalised independently, so each day type
        # preserves the daily volume on its own — the invariant the ready
        # targets stand on.
        idx = 1 if weekend else 0
        daytype = (
            self._dhw_profile_weekend if weekend else self._dhw_profile_weekday
        ).copy()
        daytype[hour] = (
            (1.0 - DHW_PROFILE_EWMA_ALPHA) * daytype[hour]
            + DHW_PROFILE_EWMA_ALPHA * draw_intensity
        )
        normalized = self._normalize_dhw_profile(daytype)
        if weekend:
            self._dhw_profile_weekend = normalized
        else:
            self._dhw_profile_weekday = normalized
        # Trust counts distinct days, not ticks: at a five-minute sample
        # cadence a tick counter would reach half-trust inside one
        # Saturday morning.
        day = dt_util.now().date().isoformat()
        if self._dhw_daytype_last_day[idx] != day:
            self._dhw_daytype_last_day[idx] = day
            self._dhw_daytype_samples[idx] += 1

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

            # T3 #6: follow the plan with the circulation pumps. Every tick,
            # transitions only, and never allowed to break the cycle.
            try:
                await self._async_drive_pumps()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Pump scheduling skipped: %s", err)

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
        # Announce the flip: the Optimize Now button disables itself off this
        # flag, and without a listener update the change is invisible until
        # the next scheduled refresh — after the solve is already over.
        self.async_update_listeners()
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
            # Post-outage recovery (#22): every neighbour restarts at once,
            # so the fresh-month "no reference yet" free pass is exactly
            # wrong now. Force the peak term active by pricing from zero
            # when the threshold would otherwise be infinite.
            if self._outage_recovery_active(dt_util.now()) and not np.isfinite(
                self._opt_config.peak_threshold_kw
            ):
                self._opt_config.peak_threshold_kw = 0.0
            self._opt_config.peak_window_minutes = tariff.window_minutes
            self._opt_config.peak_count = tariff.peaks_averaged
            self._opt_config.peak_months = tariff.months
            self._opt_config.peak_hours = tariff.peak_hours
            self._opt_config.peak_weekdays_only = tariff.weekdays_only
            self._opt_config.peak_offpeak_factor = tariff.offpeak_factor
            self._opt_config.price_risk_lambda = _as_float(
                self._config.get(CONF_PRICE_RISK_LAMBDA),
                DEFAULT_PRICE_RISK_LAMBDA,
            )
            self._opt_config.baseline_load_kw = self._baseline_house_load(
                len(prices)
            )
            self._opt_config.cycling_cost = _as_float(
                self._config.get(CONF_CYCLING_COST), DEFAULT_CYCLING_COST
            )
            # The optimizer prices surplus consumption at this, so it has to
            # travel with the same freshness as the tariff settings above —
            # an entity-supplied compensation can change between runs.
            self._opt_config.pv_export_price = self._pv_export_price()
            self._apply_comfort_weight()

            # Away mode is applied around the solve and unwound afterwards, so
            # a setback can never leak past the end of the holiday.
            self._resolve_away()
            away_original = self._apply_away_setback()

            # Economy mode, which until now was a rename of auto and nothing
            # else: identical power schedule, identical hot water, identical
            # predicted cost, with only the published mode string differing.
            # `services.yaml` has promised "wider temperature swings allowed"
            # since the mode was added, so that is what it does.
            #
            # Deliberately *after* the away snapshot, so the `finally` block
            # below unwinds it. `min_temp` is otherwise written only at
            # `_init_model()`, so a widening applied anywhere earlier would
            # persist into every later solve and outlive the mode itself.
            if self._mode == MODE_ECONOMY:
                self._opt_config.min_temp = max(
                    ECONOMY_ABSOLUTE_FLOOR,
                    self._opt_config.min_temp - ECONOMY_MIN_TEMP_WIDENING,
                )

            self._current_state.external_heat_active = self._external_heat_active
            # T2: the live guard's suppression and the post-outage DHW queue
            # both ride the same discretionary-DHW gate in the solve (#7/#22).
            self._current_state.peak_guard_active = (
                self._peak_guard.suppressing
                or self._outage_dhw_hold(dt_util.now())
            )

            # T3: everything the hot-water plan reads is refreshed here, in
            # one place, immediately before the solve.
            self._prepare_dhw_inputs(dt_util.now())

            # Manual plan: build the per-step pin arrays aligned to the exact
            # horizon this solve will use. An expired override is dropped here so
            # it can never influence planning, and the solve timestamp is taken
            # once and reused so the pins line up with the steps the optimizer
            # builds from the same instant.
            solve_now = dt_util.now()
            space_pins, dhw_pins = self._manual_pins(solve_now, len(prices))

            # The opt-in fuse guard (#3): a hard per-step ceiling on heat
            # pump power at what the fuse leaves after the rest of the house.
            caps_extra = None
            if self._config.get(
                CONF_FUSE_GUARD_ENABLED, DEFAULT_FUSE_GUARD_ENABLED
            ):
                fuse_kw = self._fuse_kw()
                if fuse_kw is not None:
                    caps_extra = np.clip(
                        fuse_kw - self._baseline_house_load(len(prices)),
                        0.0,
                        None,
                    )

            # Run optimization in executor to avoid blocking
            result = await self.hass.async_add_executor_job(
                self._optimizer.optimize,
                self._current_state,
                horizon.prices,
                horizon.outdoor_temps,
                horizon.wind_speeds,
                horizon.precipitation,
                horizon.solar_radiation,
                solve_now,
                horizon.price_known,
                horizon.pv_surplus,
                space_pins,
                dhw_pins,
                self._external_heat_forecast(len(horizon.prices)),
                horizon.price_sigma,
                caps_extra,
            )

            self._record_manual_release(result)

            self._optimization_result = result
            self._last_optimization = dt_util.now()

            self._current_action = self._optimizer.get_current_action(
                result, dt_util.now()
            )

            # A step-response experiment overrides the plan for its duration.
            self._run_system_identification(prices)
            self._adopt_system_identification()

            # The monthly fuse right-sizing what-if (#3); rate-limited to
            # weekly inside, and never allowed to break the cycle.
            try:
                await self._maybe_run_fuse_advisor()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Fuse advisor skipped: %s", err)

            self._record_quiet_comfort_period()

            # smart_write: command the valve's controller to the target the
            # plan was just built against. After the solve rather than before,
            # so a failed write can never delay or break planning.
            await self._command_valve_target()

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
            self.async_update_listeners()

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
        if self._unsub_peak_guard:
            self._unsub_peak_guard()
            self._unsub_peak_guard = None

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
        floor_return = reader.read(CONF_FLOOR_RETURN_TEMP_ENTITY)
        if floor_return.ok:
            self._floor_return_temp = floor_return.value
            self._current_state.floor_return_temperature = self._floor_return_temp
            # Update slab temperature estimate from return temp
            self._thermal_model.update_slab_from_return_temp(
                self._current_state, self._floor_return_temp
            )

        # The lower zone's room temperature, best source first.
        #
        # A real thermometer beats both estimates and is the only one that
        # carries information. The return-temp estimate below is a *water*
        # temperature standing in for an air temperature -- typically 3-9 K too
        # warm -- and because the slab is derived from the same sensor as
        # `return + 1.0`, the slab-to-room difference it produces is pinned at a
        # constant 0.5 K whatever the sensor reads. So the main heat path into
        # the lower zone is both wrong and unresponsive, and the error is judged
        # against the same comfort bounds as the upper floor.
        lower_floor = reader.read(CONF_LOWER_FLOOR_TEMP_ENTITY)
        if lower_floor.ok:
            self._current_state.lower_floor_temperature = lower_floor.value
        elif floor_return.ok:
            self._current_state.lower_floor_temperature = (
                self._floor_return_temp + 0.5
            )

        # A smart valve's target, when the integration can see it. Knowing
        # where the valve regulates to is what tells the model whether it is
        # throttling -- and therefore whether surplus heat can reach the tank
        # at all -- so charging cannot be planned without it.
        valve_target = reader.read(CONF_MIXING_VALVE_TARGET_ENTITY)
        if valve_target.ok:
            self._thermal_params.mixing_valve_target = float(valve_target.value)

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

        # Wood tank temperature (issue #40): seeds the two-tank model each
        # cycle through the same stale-aware reader — the model never
        # extrapolates yesterday's fire, it re-reads the physical tank.
        # Staleness maps to absence, and absence means the step falls back
        # to the single-tank abstraction (free heat routed into the HP
        # tank) rather than planning against a stalled hot probe or
        # dropping the heat. Logged once per transition.
        if self._thermal_params.two_tank_modelled:
            wood_top = reader.read(CONF_WOOD_TANK_TOP_ENTITY)
            wood_bottom = reader.read(CONF_WOOD_TANK_BOTTOM_ENTITY)
            wood_mean = wood_mean_temperature(
                wood_top.value if wood_top.ok else None,
                wood_bottom.value if wood_bottom.ok else None,
            )
            had = self._current_state.wood_tank_temperature is not None
            if wood_mean is None and had:
                _LOGGER.warning(
                    "Wood tank probe stale or missing; falling back to the "
                    "single-tank abstraction until it recovers"
                )
            elif wood_mean is not None and not had:
                _LOGGER.info(
                    "Two-tank model active: wood tank at %.1f °C", wood_mean
                )
            self._current_state.wood_tank_temperature = wood_mean
        elif self._current_state.wood_tank_temperature is not None:
            # Reconfigured away mid-session: drop the state so nothing
            # simulates a tank the parameters no longer model.
            self._current_state.wood_tank_temperature = None

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
        # Order matters, and not obviously. `_async_learn_house_heat_loss`
        # overwrites `_last_house_sample` with the *current* state near its top,
        # so anything reading that baseline has to run first or it silently
        # compares the current state against itself and learns nothing.
        await self._async_learn_lower_floor_loss()
        await self._async_learn_house_heat_loss()

        # Observed COP, which is only possible with a measured power entity.
        # Persisted on the same every-10-samples cadence as the house learner;
        # both share the thermal learning store.
        cop_samples_before = self._cop_samples
        self._learn_measured_cop()
        if self._cop_samples != cop_samples_before and self._cop_samples % 10 == 0:
            await self._async_save_thermal_learning()

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

        # Last resort: seed the slab, and the lower zone if nothing better has
        # been read, from the room temperature.
        #
        # This used to be guarded on the floor-return *entity* being unset while
        # the branch above is guarded on the *reading* being good. A sensor that
        # was configured but stale or unavailable satisfied neither, so both
        # values silently held whatever they were last set to, with nothing
        # marking them as unfreshened. Guarding both on the reading closes that
        # gap. The seed still happens once per process, because nothing else
        # advances these fields between cycles -- but it now happens for a
        # broken sensor as well as for an absent one.
        if not floor_return.ok:
            if not hasattr(self, "_slab_temp_initialized"):
                self._current_state.slab_temperature = (
                    self._current_state.room_temperature + 1.0
                )
                self._slab_temp_initialized = True
            if not lower_floor.ok:
                self._current_state.lower_floor_temperature = (
                    self._current_state.room_temperature
                )

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
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
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

        step_starts = [
            midnight + timedelta(minutes=FORECAST_STEP_MINUTES * (step_offset + i))
            for i in range(n_steps)
        ]

        # Align by each entry's own timestamp, not by its position. Position
        # assumed the first entry is *today's* midnight, which breaks two real
        # ways: a stale list (fetch failing since yesterday) shifts the whole
        # horizon a day, and quarter-hour entries — Tibber's 15-minute pricing
        # — would each be stretched to a full hour. An entry covers from its
        # start to the next entry's start; the last covers its predecessor's
        # span. The known series stops at the first step no entry covers, and
        # the learned prior fills the rest below.
        known = self._known_prices_for(step_starts)

        # Past the published horizon, model the shape rather than repeating the
        # last price. A flat tail has no trough, so the optimizer cannot see a
        # cheap period ahead worth waiting for. The mask records which steps
        # rest on the learned prior so that stays visible downstream.
        prices, price_known, price_sigma = extend_price_series(
            known, n_steps, step_starts, self._price_prior()
        )
        self._price_known_steps = int(np.sum(price_known))

        # The fee chokepoint (#1): DSO transfer fees join the planning prices
        # here, strictly AFTER the prior has both learned from and filled the
        # spot series — a fee folded in earlier would contaminate the learned
        # shape and mis-scale the level calibration (`observe_day` reads the
        # raw Tibber entries and is fee-free by construction). Tibber's
        # `total` includes tax and VAT but not the DSO transfer fee, so this
        # is additive, never double-counted.
        schedule = self._grid_fee_schedule()
        if schedule.active:
            prices = prices + self._fee_series(step_starts)
        return prices, price_known, price_sigma

    @staticmethod
    def _comparable_ts(raw: Any, reference: datetime) -> datetime | None:
        """Parse an entry timestamp so it can be ordered against the step grid.

        A naive timestamp against an aware grid is taken as UTC, matching
        ``_get_current_price``; an aware one against a naive grid keeps its
        own wall clock.
        """
        try:
            ts = datetime.fromisoformat(str(raw))
        except (TypeError, ValueError):
            return None
        if ts.tzinfo is None and reference.tzinfo is not None:
            return ts.replace(tzinfo=timezone.utc)
        if ts.tzinfo is not None and reference.tzinfo is None:
            return dt_util.as_local(ts).replace(tzinfo=None)
        return ts

    def _known_prices_for(self, step_starts: list[datetime]) -> list[float]:
        """Published prices covering a leading run of the step grid."""
        if not step_starts:
            return []
        entries: list[tuple[datetime, float]] = []
        for entry in self._prices:
            ts = self._comparable_ts(entry.get("starts_at"), step_starts[0])
            if ts is not None:
                entries.append((ts, _as_float(entry.get("total"), 0.0)))
        if not entries:
            # Data with no timestamps at all: keep the old positional
            # assumption of hourly entries starting at the first step.
            known: list[float] = []
            for entry in self._prices:
                known.extend([_as_float(entry.get("total"), 0.0)] * 4)
            return known[: len(step_starts)]

        entries.sort(key=lambda item: item[0])
        starts = [ts for ts, _ in entries]
        known = []
        for step_start in step_starts:
            idx = bisect_right(starts, step_start) - 1
            if idx < 0:
                break
            if idx + 1 < len(starts):
                end = starts[idx + 1]
            elif idx > 0:
                end = starts[idx] + (starts[idx] - starts[idx - 1])
            else:
                end = starts[idx] + timedelta(hours=1)
            if step_start >= end:
                break
            known.append(entries[idx][1])
        return known

    def _weather_series(
        self, n_steps: int, midnight: datetime, step_offset: int
    ) -> tuple[list[float], list[float], list[float], list[float]]:
        """Per-step outdoor temperature, wind, precipitation and irradiance.

        These are *forecast trajectories*, not current conditions: using the
        whole horizon is what makes the control anticipatory rather than
        reactive. Entries are matched to steps by their own timestamps where
        they carry one — assuming the first entry is the current hour breaks
        as soon as the forecast is stale or starts at the *next* hour, and
        the whole horizon then reads a few hours out of phase.
        """
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
        step_starts = [
            midnight + timedelta(minutes=FORECAST_STEP_MINUTES * (step_offset + i))
            for i in range(n_steps)
        ]

        parsed: list[tuple[datetime | None, tuple[float, float, float, float]]] = []
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

            ts = (
                self._comparable_ts(entry.get("datetime"), step_starts[0])
                if step_starts
                else None
            )
            parsed.append((ts, (temp, gust, rain, irradiance)))

        timed = sorted(
            (item for item in parsed if item[0] is not None),
            key=lambda item: item[0],
        )
        outdoor: list[float] = []
        wind: list[float] = []
        precipitation: list[float] = []
        solar: list[float] = []

        if timed:
            starts = [ts for ts, _ in timed]
            for step_start in step_starts:
                # Each entry holds until the next one begins; before the first
                # entry the first is the best information there is, and past
                # the last the caller pads flat anyway.
                idx = max(0, bisect_right(starts, step_start) - 1)
                temp, gust, rain, irradiance = timed[idx][1]
                outdoor.append(temp)
                wind.append(gust)
                precipitation.append(rain)
                solar.append(irradiance)
        else:
            # No timestamps at all: the old positional assumption, hourly
            # entries starting now.
            for _, (temp, gust, rain, irradiance) in parsed:
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

    def _pv_surplus_series(self, solar: np.ndarray, n_steps: int) -> np.ndarray:
        """Forecast PV surplus per step, for the optimizer to price against.

        The prices themselves stay the raw import prices: the optimizer
        charges consumption piecewise against this surplus (up to it at the
        export compensation, beyond it at the import price), which is what an
        extra kWh actually costs. Substituting the export price into the
        series here — the old approach — repriced a whole step on any surplus
        at all, however trivial.
        """
        surplus, _ = self._pv_forecast(solar, n_steps)
        self._pv_surplus = surplus
        return surplus

    def _forecast_arrays(self) -> ForecastArrays:
        """Everything the optimizer needs to know about the horizon.

        Assembled in one place because the pieces depend on each other: the PV
        surplus is derived from the irradiance series the weather assembly
        produced. Computing them elsewhere is how they would drift apart.
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
        prices, price_known, price_sigma = priced

        outdoor, wind, precipitation, solar = self._weather_series(
            n_steps, midnight, step_offset
        )
        solar = self._apply_open_meteo(solar, n_steps, midnight, step_offset)

        # A forecast shorter than the horizon is held flat at its last value.
        for series in (outdoor, wind, precipitation, solar):
            while len(series) < n_steps:
                series.append(series[-1] if series else 0.0)

        solar_array = np.array(solar[:n_steps], dtype=float)
        surplus = self._pv_surplus_series(solar_array, n_steps)

        return ForecastArrays(
            prices=prices,
            outdoor_temps=np.array(outdoor[:n_steps], dtype=float),
            wind_speeds=np.array(wind[:n_steps], dtype=float),
            precipitation=np.array(precipitation[:n_steps], dtype=float),
            solar_radiation=solar_array,
            price_known=price_known,
            pv_surplus=surplus,
            price_sigma=price_sigma,
        )

    def _get_current_price(self) -> float:
        """The current price of a consumed kWh: spot plus the DSO fee.

        The second of the fee chokepoint's three sites (#1): everything that
        prices the present — the settlement's pending dict, the published
        current price, the comfort learner's relative price — goes through
        here, so the fee can never diverge between them.
        """
        return self._current_spot_price() + self._current_grid_fee(dt_util.now())

    def _current_spot_price(self) -> float:
        """The current spot price alone, exactly as Tibber bills it."""
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

    # ------------------------------------------------------------------
    # The grid-fee layer (v4.0.0 T1, #1)
    # ------------------------------------------------------------------

    def _grid_fee_schedule(self) -> GridFeeSchedule:
        """The parsed fee schedule, re-parsed only when its config changes."""
        key = (
            self._config.get(CONF_GRID_FEE_MODE, DEFAULT_GRID_FEE_MODE),
            self._config.get(CONF_GRID_FEE_RULES, DEFAULT_GRID_FEE_RULES),
            self._config.get(CONF_GRID_FEE_FIXED, DEFAULT_GRID_FEE_FIXED),
        )
        cache = self._grid_fee_cache
        if cache is None or cache[0] != key:
            self._grid_fee_cache = (
                key,
                GridFeeSchedule.from_config(self._config),
            )
        return self._grid_fee_cache[1]

    def _grid_fee_entity_value(self) -> float | None:
        """The live SEK/kWh fee entity's value, when one is configured."""
        entity_id = self._config.get(CONF_GRID_FEE_ENTITY)
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        return value if np.isfinite(value) else None

    def _fee_series(self, step_starts: list[datetime]) -> np.ndarray:
        return self._grid_fee_schedule().fee_vector(
            step_starts, self._grid_fee_entity_value()
        )

    def _current_grid_fee(self, when: datetime) -> float:
        return self._grid_fee_schedule().current_fee(
            when, self._grid_fee_entity_value()
        )

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

    async def _command_valve_target(self) -> None:
        """Write the valve target to its controller, in ``smart_write`` mode.

        The commanded number is the one the plan was built against: the
        configured static target, or the comfort ceiling -- which is also
        what the dumb-valve recommendation tells a user to set by hand. It is
        deliberately *not* the read-back entity: commanding what a sensor
        reports would freeze whatever the valve happened to hold when the
        mode was enabled, and a changed comfort band would never reach it.

        Skipped when the answer has not meaningfully changed
        (``MIXING_VALVE_WRITE_EPSILON``): the write runs after every
        optimization cycle, and re-sending an identical setpoint every 15
        minutes wears flash on some controllers and floods others' logs.
        Failures are logged and swallowed -- a valve that refuses a write must
        never break planning, and the model keeps working from the target it
        intended, exactly as ``manual`` mode does.
        """
        params = self._thermal_params
        if params.mixing_valve_mode != mixing_valve.MODE_SMART_WRITE:
            return
        entity_id = self._config.get(CONF_MIXING_VALVE_WRITE_ENTITY)
        if not entity_id:
            _LOGGER.debug(
                "smart_write selected but no valve write entity configured"
            )
            return
        target = params.mixing_valve_target or params.comfort_ceiling
        # When the plan carries a hold schedule, actuate the current step's
        # entry instead of the fixed recommendation: low between charging and
        # the peak so the tank keeps its heat, back up through the peak. Read
        # from the current action, which already resolved which step is now.
        planned = (self._current_action or {}).get("valve_target")
        if planned is not None:
            target = float(planned)
        if (
            self._valve_commanded_target is not None
            and abs(target - self._valve_commanded_target)
            < MIXING_VALVE_WRITE_EPSILON
        ):
            return
        domain = entity_id.split(".", 1)[0]
        try:
            if domain == "climate":
                await self.hass.services.async_call(
                    "climate",
                    "set_temperature",
                    {"entity_id": entity_id, "temperature": round(target, 1)},
                    blocking=True,
                )
            elif domain in ("number", "input_number"):
                await self.hass.services.async_call(
                    domain,
                    "set_value",
                    {"entity_id": entity_id, "value": round(target, 1)},
                    blocking=True,
                )
            else:
                _LOGGER.warning(
                    "Valve write entity %s is a %s; smart_write can command "
                    "number, input_number and climate entities",
                    entity_id,
                    domain,
                )
                return
        except Exception as err:  # noqa: BLE001 - never break planning
            _LOGGER.error("Error commanding valve target: %s", err)
            return
        _LOGGER.info(
            "Commanded mixing valve target %.1f °C via %s", target, entity_id
        )
        self._valve_commanded_target = target

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
        # Conditional keys, not null keys: installs without the two-tank
        # topology publish exactly the attributes they published before
        # (issue #40's conditional-key pattern).
        two_tank: dict[str, Any] = {}
        if self._thermal_params.two_tank_modelled:
            two_tank = {
                "two_tank_modelled": True,
                "wood_tank_temperature": state.wood_tank_temperature,
            }
        return {
            **two_tank,
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
            # T3: the inlet actually in force, the tank in shower terms
            # (#28), the setpoint sweep (#9) and the learned heavy-day
            # statistics (#32/#20).
            "dhw_inlet_temperature": round(params.dhw_inlet_reference, 1),
            "dhw_mixed": self._dhw_mixed_water(),
            "dhw_advisor": self._dhw_setpoint_sweep(),
            "dhw_draw_stats": {
                label: {
                    "events": self._draw_stats.count(label),
                    "p90_kwh": round(p90, 2)
                    if (p90 := self._draw_stats.quantile(label, 0.9))
                    is not None
                    else None,
                }
                for label in labels_for(params.dhw_demand_windows)
            }
            if params.dhw_enabled
            else {},
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
            "lower_floor_loss_ratio": round(self._lower_floor_loss_ratio, 3),
            "lower_floor_loss_samples": self._lower_floor_loss_samples,
            "lower_floor_loss_learned": self._lower_floor_loss_samples > 0,
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
            # T1: what the same metered month would have cost under each
            # contract type on the market, and the DSO fee actually paid.
            "contract_comparison": self._contract_comparison(),
            "current_grid_fee": round(
                self._current_grid_fee(dt_util.now()), 4
            ),
            # T2: the headroom broadcast (#5), the fuse advisor's latest
            # answer (#3), the live guard's state (#7) and the recovery
            # window (#22).
            "power_headroom": self._power_headroom(),
            "fuse_advisor": dict(self._fuse_advisor),
            "peak_guard_suppressing": self._peak_guard.suppressing,
            "peak_guard_evidence": list(self._peak_guard.evidence),
            "outage_recovery_active": self._outage_recovery_active(
                dt_util.now()
            ),
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

    def describe_setup(self) -> dict[str, Any]:
        """The configured topology, for every picture of the system.

        Item 32/33's single source: the config-flow overview and the card's
        setup page both consume this, so the two can never disagree about
        what the system looks like. Pure over configuration — not part of
        the data dict, because it only changes when the config does.
        """
        return topology.describe_setup(self._config)

    def _mixing_valve_view(self) -> dict[str, Any]:
        """The valve mode in force, and what a dumb valve should be set to.

        ``recommend_target`` has existed since v3.7.0 and nothing called it —
        the integration could recommend a setting and told nobody. The price
        ratio feeding it is cheapest over dearest of the currently published
        prices, so the reason can say when storing is not worth much today.
        """
        params = self._thermal_params
        mode = params.mixing_valve_mode
        if not mixing_valve.is_throttling(mode):
            # No keys at all without a valve, so every existing capture of the
            # coordinator's data stays byte-for-byte identical.
            return {}
        totals = [
            _as_float(entry.get("total"), 0.0) for entry in self._prices
        ]
        positives = [t for t in totals if t > 0.0]
        ratio = (
            min(positives) / max(positives) if len(positives) >= 2 else None
        )
        rec = mixing_valve.recommend_target(
            comfort_min=self._opt_config.min_temp,
            comfort_max=self._opt_config.max_temp,
            price_ratio=ratio,
        )
        return {
            "mixing_valve_mode": mode,
            "valve_target_recommendation": {
                "target": rec.target,
                "reason": rec.reason,
                "configured_target": params.mixing_valve_target or None,
                "price_ratio": round(ratio, 3) if ratio is not None else None,
            },
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
            self._mixing_valve_view,
        ):
            data.update(view())
        data.update(self._away_state.as_dict())
        data.update({k: round(v, 4) for k, v in self._energy_totals.items()})
        data["battery"] = self._battery_view()

        # Only surface the manual-plan key while an override is actually active,
        # so a plan-free solve (the golden fixtures included) is byte-for-byte
        # unchanged from before this feature existed.
        manual_state = self._manual_plan_state()
        if manual_state is not None:
            data["manual_plan"] = manual_state

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
        qdays = stored.get("quarter_days_seen")
        if isinstance(qdays, list):
            self._price_qdays_seen = {str(d) for d in qdays}

    async def _async_save_price_model(self) -> None:
        try:
            await self._price_model_store.async_save(
                {
                    "model": self._price_model.as_dict(),
                    # Only recent days matter for de-duplication, and an
                    # unbounded set would grow forever.
                    "days_seen": sorted(self._price_days_seen)[-90:],
                    "quarter_days_seen": sorted(self._price_qdays_seen)[-90:],
                }
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist price model: %s", err)

    async def _async_load_ledger(self) -> None:
        """Restore the monthly ledger (T1)."""
        try:
            stored = await self._ledger_store.async_load()
        except Exception as err:  # noqa: BLE001 - never block setup on storage
            _LOGGER.debug("Could not load ledger: %s", err)
            return
        if not stored:
            return
        self._ledger = MonthlyLedger.from_dict(stored.get("ledger"))

    def _schedule_ledger_save(self) -> None:
        """Persist the ledger without blocking the settlement path."""
        self.hass.async_create_task(self._async_save_ledger())

    async def _async_save_ledger(self) -> None:
        try:
            await self._ledger_store.async_save(
                {"ledger": self._ledger.as_dict()}
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist ledger: %s", err)

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
        stored_mode = stored.get("mode")
        if isinstance(stored_mode, str) and stored_mode in OPERATION_MODES:
            self._mode = stored_mode
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
                    # Persisted because `_init_runtime_state` resets it to
                    # `auto` on every reload, and writing any option reloads the
                    # entry -- so dragging the thermostat card's temperature, or
                    # simply restarting Home Assistant, silently dropped the
                    # user out of the mode they had selected.
                    "mode": self._mode,
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
        # A long silence before this restart reads as a power cut (#22).
        self._detect_outage(stored.get("last_tick"))

    async def _async_save_energy_totals(self) -> None:
        try:
            await self._energy_store.async_save(
                {
                    **self._energy_totals,
                    # The outage detector's heartbeat (#22): the last instant
                    # this coordinator was alive. Numeric-key loaders skip it.
                    "last_tick": dt_util.now().isoformat(),
                }
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist energy totals: %s", err)

    # ==================================================================
    # Manual plan override
    # ==================================================================

    async def _async_load_manual_plan(self) -> None:
        """Restore a persisted override, discarding it if already expired.

        A plan set at 18:00 must still hold after a restart at 19:00 on the same
        day; one whose expiry has already passed is dropped on restore so it can
        never resurrect stale pins into a fresh horizon.
        """
        try:
            stored = await self._manual_plan_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load manual plan: %s", err)
            return
        if not stored:
            return
        try:
            override = ManualOverride.from_dict(stored)
        except (ManualPlanError, AttributeError, TypeError) as err:
            # from_dict expects a mapping, so a corrupted or hand-edited
            # .storage file holding a list or a bare string raises something
            # other than ManualPlanError. A bad file must cost the user their
            # override, not their whole integration setup.
            _LOGGER.warning("Discarding unreadable stored manual plan: %s", err)
            await self._manual_plan_store.async_save({})
            return
        if override.is_expired(dt_util.now()):
            await self._manual_plan_store.async_save({})
            return
        self._manual_override = override

    async def _async_save_manual_plan(self) -> None:
        try:
            payload = (
                self._manual_override.to_dict()
                if self._manual_override is not None
                else {}
            )
            await self._manual_plan_store.async_save(payload)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist manual plan: %s", err)

    def _horizon_step_starts(self, solve_now: datetime, n_steps: int) -> list[datetime]:
        """The instant each solved step begins, matching the optimizer's own."""
        dt_hours = self._opt_config.dt_hours
        return [solve_now + timedelta(hours=i * dt_hours) for i in range(n_steps)]

    def _manual_pins(
        self, solve_now: datetime, n_steps: int
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Per-step pin arrays for the active override, or ``(None, None)``.

        Returns ``None`` for a channel left automatic (or when no override is in
        force / it has expired), so a solve with no manual plan is byte-for-byte
        identical to one from before this feature existed.
        """
        override = self._manual_override
        if override is None:
            return None, None
        if override.is_expired(solve_now):
            # Drop it eagerly; the next save persists the cleared state.
            self._manual_override = None
            self.hass.async_create_task(self._async_save_manual_plan())
            return None, None
        step_starts = self._horizon_step_starts(solve_now, n_steps)
        space = override.channel_pins(CHANNEL_SPACE, step_starts)
        dhw = override.channel_pins(CHANNEL_DHW, step_starts)
        return (
            np.array(space, dtype=float) if space is not None else None,
            np.array(dhw, dtype=float) if dhw is not None else None,
        )

    def _record_manual_release(self, result: "OptimizationResult") -> None:
        """Fold the solve's safety releases back onto the override for display."""
        override = self._manual_override
        if override is None:
            return
        override.released_space = [
            {"step": i, "reason": "safety"} for i in result.manual_released_space
        ]
        override.released_dhw = [
            {"step": i, "reason": "safety"} for i in result.manual_released_dhw
        ]

    def _manual_plan_state(self) -> dict[str, Any] | None:
        """The override state the plan sensors expose, or ``None`` when inactive."""
        override = self._manual_override
        if override is None or override.is_expired(dt_util.now()):
            return None
        return {
            "active": True,
            "expires_at": override.expires_at.isoformat(),
            "space_slots": override.normalized_slots(CHANNEL_SPACE),
            "dhw_slots": override.normalized_slots(CHANNEL_DHW),
            "released_space": list(override.released_space),
            "released_dhw": list(override.released_dhw),
        }

    async def async_apply_manual_plan(
        self, override: ManualOverride
    ) -> dict[str, Any]:
        """Store a validated override, persist it, and re-solve immediately.

        The override arrives already validated (the service layer builds it via
        ``manual_plan.build_override`` so a rejected call never reaches here),
        so this only has to adopt it, persist it and trigger a refresh. Returns
        the stored summary for the service response.
        """
        self._manual_override = override
        await self._async_save_manual_plan()
        await self.async_request_refresh()
        # The solver's own horizon length. `len(self._prices)` counts *hourly*
        # price entries, so using it would measure a 15-minute-step horizon in
        # hours and under-report the pins -- reporting zero for an evening plan
        # that had in fact applied perfectly well.
        step_starts = self._horizon_step_starts(
            dt_util.now(), self._opt_config.n_steps
        )
        return {
            "expires_at": override.expires_at.isoformat(),
            "space_slots": override.normalized_slots(CHANNEL_SPACE),
            "dhw_slots": override.normalized_slots(CHANNEL_DHW),
            "pinned_space_steps": override.pinned_step_count(
                CHANNEL_SPACE, step_starts
            ),
            "pinned_dhw_steps": override.pinned_step_count(CHANNEL_DHW, step_starts),
        }

    async def async_clear_manual_plan(self) -> None:
        """Remove any override and re-solve so the plan reverts to automatic."""
        self._manual_override = None
        await self._async_save_manual_plan()
        await self.async_request_refresh()


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
        # The quarter refinement (#19) learns beside the hourly shape, from
        # days that arrived at full 15-minute resolution only.
        for day, quarters in quarters_from_entries(self._prices).items():
            if day in self._price_qdays_seen:
                continue
            try:
                when = datetime.fromisoformat(f"{day}T12:00:00")
            except ValueError:
                continue
            if self._price_model.observe_day_quarters(when, quarters):
                self._price_qdays_seen.add(day)
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
            months=self._tariff_months(),
            peak_hours=self._tariff_hours(),
            weekdays_only=bool(
                self._config.get(
                    CONF_PEAK_TARIFF_WEEKDAYS_ONLY,
                    DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY,
                )
            ),
            offpeak_factor=_as_float(
                self._config.get(CONF_PEAK_TARIFF_OFFPEAK_FACTOR),
                DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR,
            ),
        )

    def _tariff_months(self) -> frozenset[int]:
        """The #13 month mask, empty (= every month) when unset or broken."""
        spec = str(
            self._config.get(CONF_PEAK_TARIFF_MONTHS, DEFAULT_PEAK_TARIFF_MONTHS)
        ).strip()
        if not spec:
            return frozenset()
        months: set[int] = set()
        try:
            for chunk in spec.replace(";", ",").split(","):
                chunk = chunk.strip()
                if chunk:
                    months |= grid_fee_parse_month_range(chunk)
        except GridFeeError as err:
            _LOGGER.warning(
                "Invalid peak tariff months %r (%s); applying the tariff "
                "in every month",
                spec,
                err,
            )
            return frozenset()
        return frozenset(months)

    def _tariff_hours(self) -> tuple:
        """The #13 peak-hour windows, empty (= every hour) when unset."""
        spec = str(
            self._config.get(CONF_PEAK_TARIFF_HOURS, DEFAULT_PEAK_TARIFF_HOURS)
        ).strip()
        if not spec:
            return ()
        try:
            return tuple(parse_windows(spec))
        except DHWWindowError as err:
            _LOGGER.warning(
                "Invalid peak tariff hours %r (%s); treating every hour "
                "as peak",
                spec,
                err,
            )
            return ()

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

    # ==================================================================
    # Live peak guard (#7), fuse (#3/#5) and outage recovery (#22) — T2
    # ==================================================================

    async def _async_setup_peak_guard(self) -> None:
        """Register the meter listener — only when the guard is switched on.

        The flag gates *registration*, not just behaviour: an opt-out
        install carries no listener at all, so the event path cannot even
        run. The subscription follows the whole-house meter when one exists
        (the billed quantity), else the heat pump's own meter.
        """
        if not self._config.get(
            CONF_PEAK_GUARD_ENABLED, DEFAULT_PEAK_GUARD_ENABLED
        ):
            return
        entity = self._config.get(CONF_HOUSE_POWER_ENTITY) or self._config.get(
            CONF_POWER_ENTITY
        )
        if not entity:
            _LOGGER.warning(
                "Peak guard enabled but no power meter configured; "
                "the guard stays dormant"
            )
            return
        self._unsub_peak_guard = async_track_state_change_event(
            self.hass, [entity], self._on_power_event
        )
        _LOGGER.info("Peak guard listening on %s", entity)

    @callback
    def _on_power_event(self, event) -> None:
        """One meter reading: fold, project, and flip the flag on crossings.

        Never solves, never blocks: the only work here is arithmetic on the
        open metering window and, on a *transition*, scheduling the
        already-async actuation. A chatty meter is throttled to one
        processed event per ``MIN_EVENT_SPACING_S``.

        ``@callback`` is load-bearing, not a style choice: without it the
        event helper dispatches this to an executor thread, where
        ``async_create_task`` raises and the tracker accumulators race the
        update loop.
        """
        new_state = getattr(event, "data", {}).get("new_state")
        if new_state is None:
            return
        now = dt_util.now()
        if self._peak_guard.throttled(now):
            return
        tariff = self._capacity_tariff()
        fuse = self._fuse_kw()
        if not tariff.enabled and fuse is None:
            return
        try:
            raw = float(getattr(new_state, "state", None))
        except (TypeError, ValueError):
            return
        attrs = getattr(new_state, "attributes", {}) or {}
        kw = normalize_power_kw(raw, attrs.get("unit_of_measurement"))
        if kw is None or not np.isfinite(kw):
            return

        # Time-weighted fold (#7): the listener knows real sample spacing,
        # which the 30-minute tick never did. Clamped so a reconnecting
        # meter cannot claim an hour-long sample.
        dt_h: float | None = None
        if self._guard_last_fold is not None:
            spacing = (now - self._guard_last_fold).total_seconds() / 3600.0
            if 0.0 < spacing <= 0.25:
                dt_h = spacing
        self._guard_last_fold = now
        if tariff.enabled:
            self._peak_tracker.observe(now, kw, tariff, dt_hours=dt_h)

        key, mean, elapsed, factor = self._peak_tracker.window_snapshot(
            now, tariff
        )
        projection = project_window_mean(
            mean, elapsed, kw, tariff.window_minutes
        )
        margin = _as_float(
            self._config.get(CONF_PEAK_GUARD_MARGIN_KW),
            DEFAULT_PEAK_GUARD_MARGIN_KW,
        )
        # Two independent lines can be crossed, each in its own currency.
        # The tariff bills this window's kW scaled by the #13 masks, so the
        # comparison is billed-equivalent on BOTH sides — a half-rate night
        # window projects half as much, a free one cannot cross at all.
        # The fuse is raw physics: projected window mean is the wrong
        # quantity for a breaker, but staying under it on average is still
        # the conservative guard behaviour, and the instantaneous
        # protection is the breaker's own job. The guard folds in whichever
        # line is worse off right now.
        candidates: list[tuple[float, float]] = []
        if tariff.enabled and factor > 0.0:
            candidates.append(
                (projection * factor, self._peak_tracker.threshold_kw(tariff))
            )
        if fuse is not None:
            candidates.append((projection, fuse))
        proj_eff, threshold = max(
            candidates,
            key=lambda pair: pair[0] - pair[1],
            default=(projection, float("inf")),
        )
        changed = self._peak_guard.update(
            now,
            key,
            proj_eff,
            threshold,
            margin,
            floor_hold=self._guard_floor_hold(),
        )
        if changed:
            self._current_state.peak_guard_active = self._peak_guard.suppressing
            self.hass.async_create_task(self._async_peak_guard_transition())

    def _guard_floor_hold(self) -> bool:
        """Whether a hard floor outranks suppression right now.

        A cold tank or a breached comfort floor means the house needs the
        heat more than the bill needs protecting — the guard must refuse to
        engage and release immediately.
        """
        params = self._thermal_params
        state = self._current_state
        if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp:
            return True
        floor = float(self._opt_config.min_temp)
        temps = [state.room_temperature]
        if params.two_zone_enabled:
            temps += [
                state.upper_floor_temperature,
                state.lower_floor_temperature,
            ]
        return any(t is not None and float(t) < floor for t in temps)

    async def _async_peak_guard_transition(self) -> None:
        """Actuate one suppression transition — and only transitions.

        Engaging nudges the ECL displace down for the rest of the window;
        releasing re-publishes the plan's own action. The DHW hold itself
        rides ``ThermalState.peak_guard_active`` through the same
        discretionary-suppression gate external heat uses, at the next
        solve — no solve happens here.
        """
        if not self._current_action:
            self.async_update_listeners()
            return
        if self._peak_guard.suppressing:
            await self.async_publish_ecl110_command(
                displace_value=float(
                    self._current_action.get("displace_value", 0.0)
                )
                - PEAK_GUARD_DISPLACE_NUDGE_C,
                heat_pump_on=bool(
                    self._current_action.get("heat_pump_on", False)
                ),
                reason="peak_guard",
            )
        else:
            await self.async_publish_current_action(reason="peak_guard_release")
        self.async_update_listeners()

    def _fuse_kw(self) -> float | None:
        """The main fuse's continuous capacity, or None when unconfigured."""
        amps = _as_float(
            self._config.get(CONF_MAIN_FUSE_A), DEFAULT_MAIN_FUSE_A
        )
        if amps <= 0:
            return None
        phases = int(
            _as_float(
                self._config.get(CONF_MAIN_FUSE_PHASES),
                DEFAULT_MAIN_FUSE_PHASES,
            )
        )
        return amps * max(1, phases) * 230.0 / 1000.0

    def _power_headroom(self) -> dict[str, Any]:
        """How many kW the house can draw right now without new cost (#5).

        ``min(fuse, capacity threshold) − current house draw``, clamped at
        zero, with the per-step horizon headroom in attributes so a charger
        automation can follow the plan, not just the instant.
        """
        fuse = self._fuse_kw()
        tariff = self._capacity_tariff()
        threshold = (
            self._peak_tracker.threshold_kw(tariff)
            if tariff.enabled
            else float("inf")
        )
        limits = [
            v
            for v in (fuse, threshold)
            if v is not None and np.isfinite(v)
        ]
        if not limits:
            return {"available": False}
        limit = float(min(limits))

        if self._measured_house_power is not None:
            house_now = float(self._measured_house_power)
            source = "house meter"
        elif self._measured_power is not None:
            house_now = float(self._measured_power)
            source = "heat pump meter only (baseline load invisible)"
        else:
            house_now = float(self._current_action.get("power", 0.0)) + float(
                self._current_action.get("dhw_power", 0.0)
            )
            source = "planned power only (no meter)"

        out: dict[str, Any] = {
            "available": True,
            "limit_kw": round(limit, 3),
            "headroom_kw": round(max(0.0, limit - house_now), 3),
            "baseline_source": source,
        }
        result = self._optimization_result
        if result is not None and result.power_schedule:
            planned = np.asarray(result.power_schedule, dtype=float)
            if result.dhw_power_schedule:
                dhw = np.asarray(result.dhw_power_schedule, dtype=float)
                planned = planned + dhw[: planned.size]
            baseline = self._baseline_house_load(planned.size)
            steps = np.clip(limit - planned - baseline, 0.0, None)
            out["horizon_headroom_kw"] = [
                round(float(v), 2) for v in steps[:48]
            ]
        return out

    async def _maybe_run_fuse_advisor(self) -> None:
        """The monthly what-if: would this house run under the next fuse (#3).

        At most weekly, through the existing simulate harness and executor.
        The answer is published on the Monthly Peak sensor; nothing here
        actuates.
        """
        fuse = self._fuse_kw()
        if fuse is None:
            return
        amps = _as_float(
            self._config.get(CONF_MAIN_FUSE_A), DEFAULT_MAIN_FUSE_A
        )
        smaller = max(
            (a for a in FUSE_LADDER_A if a < amps), default=None
        )
        if smaller is None:
            return
        now = dt_util.now()
        if (
            self._fuse_advisor_at is not None
            and (now - self._fuse_advisor_at).total_seconds() < 7 * 24 * 3600.0
            and self._fuse_advisor.get("month") == month_key(now)
        ):
            return

        phases = int(
            _as_float(
                self._config.get(CONF_MAIN_FUSE_PHASES),
                DEFAULT_MAIN_FUSE_PHASES,
            )
        )
        candidate_kw = smaller * max(1, phases) * 230.0 / 1000.0
        baseline_now = float(self._baseline_house_load(1)[0])
        cap_kw = max(0.0, candidate_kw - baseline_now)
        # The advisor borrows the card's simulate harness but must not
        # spend its rate-limit slot or leave a fuse-capped payload in the
        # cache the card's next drag would read back.
        cache_snapshot = (self._last_simulation, self._simulation_cache)
        try:
            simulated = await self.async_simulate({"power_cap_kw": cap_kw})
        finally:
            self._last_simulation, self._simulation_cache = cache_snapshot
        echoed = (simulated.get("overrides") or {}).get("power_cap_kw")
        if (
            "error" in simulated
            or simulated.get("rate_limited")
            or echoed != cap_kw
        ):
            # Retry tomorrow rather than in a week: a rate-limited or failed
            # what-if is not an answer, and a month of "error" would be. A
            # rate-limited call returns the card's *cached* payload — a
            # different what-if entirely — which is why the overrides echo
            # is checked rather than trusted. Last month's real verdict, if
            # any, stays published; an error dict is not an upgrade.
            self._fuse_advisor_at = now - timedelta(days=6)
            if "candidate_kw" not in self._fuse_advisor:
                self._fuse_advisor = {
                    "month": month_key(now),
                    "candidate_fuse_a": int(smaller),
                    "error": simulated.get("error", "rate_limited"),
                }
            return
        self._fuse_advisor_at = now
        breach = float(simulated.get("power_cap_breach_c") or 0.0)
        # The breach the solver reports is absolute: "the capped plan dips
        # this far below the floor". On a cold-snap morning the *uncapped*
        # plan dips too, and blaming the candidate fuse for weather would
        # tell the user their house needs amperes it does not. What the cap
        # itself costs is bounded by how much colder the capped plan gets
        # than the baseline it was differenced against.
        base_cold = simulated.get("baseline_min_room_temperature")
        sim_cold = simulated.get("min_room_temperature")
        if breach > 0.0 and base_cold is not None and sim_cold is not None:
            breach = max(0.0, min(breach, float(base_cold) - float(sim_cold)))
        peak = float(simulated.get("projected_peak_kw") or 0.0)
        self._fuse_advisor = {
            "month": month_key(now),
            "current_fuse_a": int(amps),
            "candidate_fuse_a": int(smaller),
            "candidate_kw": round(candidate_kw, 2),
            "feasible": breach <= 0.05,
            "comfort_shortfall_c": round(breach, 2),
            "worst_margin_kw": round(candidate_kw - peak, 2),
            "cost_delta_sek_month": simulated.get("monthly_cost_delta"),
        }

    def _outage_recovery_active(self, now: datetime) -> bool:
        return (
            self._outage_recovery_until is not None
            and now < self._outage_recovery_until
        )

    def _outage_dhw_hold(self, now: datetime) -> bool:
        """Whether recovery is still queueing hot water behind space (#22).

        Never while the tank is genuinely low: post-outage the water may
        already be cold, and a delay that leaves a family without hot water
        to protect a tariff is the wrong trade.
        """
        if self._outage_dhw_until is None or now >= self._outage_dhw_until:
            return False
        params = self._thermal_params
        if params.dhw_enabled and (
            self._current_state.dhw_temperature < params.dhw_min_temp
        ):
            return False
        return True

    def _detect_outage(self, last_tick_iso: str | None) -> None:
        """Open the staggered-recovery window after a real gap (#22)."""
        if not self._config.get(
            CONF_OUTAGE_RECOVERY_ENABLED, DEFAULT_OUTAGE_RECOVERY_ENABLED
        ):
            return
        if not last_tick_iso:
            return
        try:
            last = datetime.fromisoformat(str(last_tick_iso))
        except (TypeError, ValueError):
            return
        now = dt_util.now()
        if last.tzinfo is None and now.tzinfo is not None:
            last = last.replace(tzinfo=now.tzinfo)
        gap_minutes = (now - last).total_seconds() / 60.0
        if gap_minutes <= OUTAGE_GAP_MINUTES:
            return
        self._outage_recovery_until = now + timedelta(
            hours=OUTAGE_RECOVERY_HOURS
        )
        self._outage_dhw_until = now + timedelta(
            minutes=OUTAGE_DHW_DELAY_MINUTES
        )
        _LOGGER.warning(
            "Update gap of %.0f minutes reads as an outage; staggered "
            "recovery active for %.1f h (hot water queued %.0f min behind "
            "space heating)",
            gap_minutes,
            OUTAGE_RECOVERY_HOURS,
            OUTAGE_DHW_DELAY_MINUTES,
        )

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

    def _pv_measured_production(self, config: pv_model.PVConfig) -> float | None:
        """Live production in kW from the configured entity, if readable."""
        entity_id = config.production_entity
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or str(state.state).lower() in ("unknown", "unavailable", ""):
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        unit = state.attributes.get("unit_of_measurement")
        converted = normalize_power_kw(value, unit)
        if converted is None or not np.isfinite(converted):
            return None
        return max(0.0, converted)

    def _pv_forecast(
        self, solar_rad: np.ndarray, n_steps: int
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Forecast PV surplus over the horizon."""
        config = self._pv_config()
        if not config.enabled or config.peak_kw <= 0:
            self._pv_summary = {}
            self._pv_production = None
            return np.zeros(n_steps, dtype=float), {}
        production = pv_model.forecast_production_kw(solar_rad[:n_steps], config)
        # A meter on the inverter beats the irradiance model for the step being
        # acted on right now; the rest of the horizon stays modelled.
        self._pv_production = self._pv_measured_production(config)
        if self._pv_production is not None and len(production):
            production = production.copy()
            production[0] = min(self._pv_production, config.peak_kw)
        baseline = self._baseline_house_load(n_steps)
        if not np.any(baseline > 0):
            baseline = np.full(n_steps, config.default_baseline_kw, dtype=float)
        surplus = pv_model.surplus_kw(production, baseline)
        summary = pv_model.summarize(production, surplus, self._opt_config.dt_hours)
        summary["export_price"] = round(config.export_price, 4)
        if self._pv_production is not None:
            summary["measured_production_kw"] = round(self._pv_production, 3)
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

        now = dt_util.now()
        self._away_state = away_mode.resolve(
            config,
            now=now,
            presence_raw=presence_raw,
            presence_attributes=presence_attrs,
            return_raw=return_raw,
            comfort_temp=self._opt_config.get_comfort_temp(
                now.hour + now.minute / 60.0
            ),
            # The estimator ramps the real model at full power, so it sees the
            # slab bottleneck the old lumped formula ignored.
            model=self._thermal_model,
            thermal_state=self._current_state,
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
            "target_temp": self._opt_config.target_temp,
            "min_temp": self._opt_config.min_temp,
            "comfort_temp_day": self._opt_config.comfort_temp_day,
            "comfort_temp_night": self._opt_config.comfort_temp_night,
            "dhw_min_temp": self._thermal_params.dhw_min_temp,
            "dhw_idle_min_temp": self._thermal_params.dhw_idle_min_temp,
        }
        if not state.active or state.recovery_active:
            return original

        target = state.target_temperature or DEFAULT_AWAY_TEMPERATURE
        # target_temp joins the setback: the terminal cost, the settlement
        # caps and the baseline thermostat all anchor on it, so leaving it at
        # full comfort kept the objective buying heat into the slab for a
        # house nobody is in — measured at roughly 40% more energy per away
        # day — and inflated the reported savings against a 21 °C baseline.
        # min() so an away target configured above the normal one can never
        # raise anything.
        self._opt_config.target_temp = min(original["target_temp"], target)
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
        self._opt_config.target_temp = original["target_temp"]
        self._opt_config.min_temp = original["min_temp"]
        self._opt_config.comfort_temp_day = original["comfort_temp_day"]
        self._opt_config.comfort_temp_night = original["comfort_temp_night"]
        self._thermal_params.dhw_min_temp = original["dhw_min_temp"]
        self._thermal_params.dhw_idle_min_temp = original["dhw_idle_min_temp"]

    # ==================================================================
    # Closed-loop accuracy and the defrost derate (items 11, 14)
    # ==================================================================

    def _current_humidity(self) -> float | None:
        """Outdoor relative humidity, from the forecast entry covering now.

        Entry 0 used to be read positionally — the last of the positional
        reads the v3.8.0 audit aligned, deferred then because the defrost
        bucket tolerates a stale-by-hours humidity. It reuses the same
        timestamp comparison as the horizon alignment: the entry nearest the
        current time wins, and a forecast with no timestamps at all falls
        back to the old first-entry behaviour rather than reading nothing.
        """
        if not self._weather_forecast:
            return None
        now = dt_util.now()
        best: tuple[float, Any] | None = None
        for entry in self._weather_forecast:
            raw = entry.get("humidity")
            if raw is None:
                continue
            ts = self._comparable_ts(entry.get("datetime"), now)
            distance = (
                abs((ts - now).total_seconds())
                if ts is not None
                else float("inf")
            )
            if best is None or distance < best[0]:
                best = (distance, raw)
        if best is None:
            return None
        try:
            value = float(best[1])
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
                # the learners are not frozen for some other reason. Outside
                # the frosting band the same shortfall is the COP scale
                # learner's to explain, and exactly one of the two may see any
                # given interval. See defrost.in_frost_band.
                if not self._learning_frozen(CONF_POWER_ENTITY):
                    ratio = delivered_ratio(sample)
                    if (
                        ratio is not None
                        and sample.outdoor_temp is not None
                        and in_frost_band(sample.outdoor_temp)
                    ):
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
            # The third fee-chokepoint site (#1): the settlement books spot
            # and fee as separate lines, so the ledger can itemise the bill
            # while "price" above stays what the kWh actually cost.
            "spot_price": self._current_spot_price(),
            "grid_fee": self._current_grid_fee(now),
            "predicted_temp": self._predicted_next_room_temp(),
            "outdoor": self._current_state.outdoor_temperature,
            "humidity": self._current_humidity(),
        }

    def _predicted_next_room_temp(self) -> float | None:
        """What the plan says the room will be at the next interval.

        Only meaningful while the plan is what is actually running. In
        comfort, boost and off modes `_optimization_result` still holds the
        *last* auto-mode plan, whose trajectory assumed powers the fixed-rule
        action is not applying — pairing that stale prediction against reality
        would charge the model with errors it never made.
        """
        if self._mode not in (MODE_AUTO, MODE_ECONOMY):
            return None
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

        when = pending.get("when") or dt_util.now()
        spot = _as_float(pending.get("spot_price"), 0.0)

        # The månadsspot shadow column (#23) settles on the month's *average*
        # spot price, so the average must sample every interval — including
        # the ones where nothing was consumed. Before the energy gate below.
        self._ledger.observe_meta_mean(when, "spot_price", spot)

        actual = sample.actual_power_kw
        if actual is None:
            actual = planned_total
        energy = max(0.0, actual * elapsed_hours)
        if energy <= 0:
            self._schedule_ledger_save()
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

        # The monthly ledger (T1): spot and DSO fee booked as separate lines,
        # so every later SEK claim can reconcile against the month's
        # receipts, and the fee never contaminates the spot column the
        # contract comparison settles on.
        fee = _as_float(pending.get("grid_fee"), 0.0)
        self._ledger.add(when, "spot", kwh=energy, sek=energy * spot)
        if fee:
            self._ledger.add(when, "grid_fee", kwh=energy, sek=energy * fee)
        self._schedule_ledger_save()

    def _contract_comparison(self) -> dict[str, Any]:
        """This month's metered consumption settled under each contract (#23).

        Hourly spot is what Tibber actually bills; monthly-average spot
        (månadsspot) is the same kWh at the month's mean spot price; fixed is
        the configured contract price. The "load profile value" is the
        öre/kWh the optimizer's shifting earns below the flat-consumer
        average — a household on månadsspot gains nothing from hourly
        shifting, and this is the proof, either way.
        """
        month = month_key(dt_util.now())
        spot_line = self._ledger.line(month, "spot")
        kwh = spot_line["kwh"]
        spot_cost = spot_line["sek"]
        out: dict[str, Any] = {
            "month": month,
            "kwh": round(kwh, 3),
            "hourly_spot_sek": round(spot_cost, 2),
        }
        fee_line = self._ledger.line(month, "grid_fee")
        if fee_line["sek"]:
            out["grid_fee_sek"] = round(fee_line["sek"], 2)

        costs: dict[str, float] = {"hourly_spot": spot_cost}
        mean_spot = self._ledger.meta_mean(month, "spot_price")
        if kwh > 0 and mean_spot is not None:
            monthly_avg_cost = kwh * mean_spot
            costs["monthly_avg_spot"] = monthly_avg_cost
            out["monthly_avg_spot_sek"] = round(monthly_avg_cost, 2)
            out["load_profile_value_per_kwh"] = round(
                mean_spot - spot_cost / kwh, 4
            )
        fixed_price = _as_float(
            self._config.get(CONF_CONTRACT_FIXED_PRICE),
            DEFAULT_CONTRACT_FIXED_PRICE,
        )
        if kwh > 0 and fixed_price > 0:
            fixed_cost = kwh * fixed_price
            costs["fixed"] = fixed_cost
            out["fixed_sek"] = round(fixed_cost, 2)
        if kwh > 0 and len(costs) > 1:
            out["cheapest"] = min(costs, key=costs.get)
        return out

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
        # Spot on BOTH sides of the ratio: the denominator is a mean over raw
        # Tibber entries, so a fee-inclusive numerator (T1's #1) would inflate
        # every override's price-weight by the fee regardless of hour.
        relative = self._current_spot_price() / mean_price if mean_price else 1.0
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

        # Flatness only says the weight might be too high when swinging would
        # actually have paid: with near-flat prices there is nothing to trade
        # comfort against, and with no planned heating there is nothing being
        # held flat at any cost. Counting those periods ratcheted the weight
        # down to its floor over mild spells — every quiet day was read as
        # evidence, even the ones where flatness was free.
        prices = np.asarray(result.prices, dtype=float) if result.prices else None
        if prices is None or prices.size == 0:
            return
        mean_price = float(np.mean(prices))
        if mean_price <= 1e-6:
            return
        if float(np.max(prices) - np.min(prices)) / mean_price < 0.15:
            return
        heating_kwh = float(
            np.sum(np.asarray(result.power_schedule, dtype=float))
            * self._opt_config.dt_hours
        )
        if heating_kwh < 1.0:
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
        # Persist immediately: the whole point of an experiment is a result
        # good enough to outlive a restart, and the passive learner's periodic
        # save may be many samples away.
        self.hass.async_create_task(self._async_save_thermal_learning())
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
        if "max_temp" in overrides:
            # The valve's default target is the comfort ceiling, so a
            # simulated ceiling change has to reach the model too.
            scratch_params.comfort_ceiling = float(overrides["max_temp"])
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

        # T2: a per-step electrical ceiling for shadow solves — the fuse
        # advisor (#3) and, later, the what-if tiles (#39).
        cap_extra = None
        if "power_cap_kw" in overrides:
            cap_extra = np.full(
                len(horizon.prices), float(overrides["power_cap_kw"])
            )

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
                    # The scratch config inherits price_risk_lambda, so the
                    # what-if must price guessed steps the same way the plan
                    # it is compared against did (#34).
                    price_sigma=horizon.price_sigma,
                    power_caps_extra=cap_extra,
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
            # T2: present only when the what-if capped power — the worst
            # comfort-floor shortfall that cap forced, 0.0 when feasible.
            **(
                {
                    "power_cap_breach_c": simulated.predictive_info.get(
                        "power_cap_breach_c", 0.0
                    )
                }
                if "power_cap_kw" in overrides and simulated.predictive_info
                else {}
            ),
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
