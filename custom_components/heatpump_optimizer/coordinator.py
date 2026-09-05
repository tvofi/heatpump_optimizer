"""Data coordinator for Heat Pump Cost Optimizer.

The coordinator manages:
1. Fetching electricity prices from Tibber API
2. Fetching weather forecasts from Home Assistant weather entities
3. Fetching solar radiation, floor return temperature, and DHW temperature
4. Running the MPC optimization (with predictive weather anticipation + DHW)
5. Applying optimization results to heat pump control
"""
from __future__ import annotations

import atexit
import asyncio
import copy
import hashlib
import json
import logging
import math
import os
import pickle
import subprocess
import sys
import threading
from bisect import bisect_right
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NamedTuple

import aiohttp
import numpy as np

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType
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
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    CONF_MIXING_VALVE_WRITE_ENTITY,
    CONF_MIXING_VALVE_WRITE_TARGET_KIND, DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND,
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
    MODE_LAST_GOOD_MAX_AGE_MINUTES,
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
    COP_TRACKING_ERROR_GATE,
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
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_SETPOINT,
    CONF_SHOWER_FLOW_LPM,
    DEFAULT_SHOWER_FLOW_LPM,
    CONF_VVC_PUMP_ENTITY,
    CONF_VVC_LEAD_MINUTES,
    DEFAULT_VVC_LEAD_MINUTES,
    CONF_SPACE_PUMP_ENTITY,
    DHW_LEGIONELLA_BOOST_MAX_HOURS,
    DHW_LEGIONELLA_HOLD_MINUTES,
    DHW_DAYTYPE_BLEND_K,
    SPACE_PUMP_FLOOR_MARGIN_C,
    CONF_OPEN_WINDOW_RELAX_ENABLED,
    DEFAULT_OPEN_WINDOW_RELAX_ENABLED,
    CONF_IMMERSION_FEEDBACK_ENABLED,
    DEFAULT_IMMERSION_FEEDBACK_ENABLED,
    VENT_CUSUM_THRESHOLD_C,
    VENT_CUSUM_DRIFT_C,
    VENT_CUSUM_CLIP_C,
    VENT_CUSUM_STARVE_HOURS,
    OPEN_WINDOW_RELAX_C,
    IMMERSION_FACTOR,
    COP_BASELINE_MIN_SAMPLES,
    COP_BASELINE_ALPHA,
    COP_HEALTH_THRESHOLD,
    COP_HEALTH_DRIFT,
    CONF_PRECIP_TYPE_ENABLED,
    DEFAULT_PRECIP_TYPE_ENABLED,
    CONF_SNOW_ROOF_FACTOR_ENABLED,
    DEFAULT_SNOW_ROOF_FACTOR_ENABLED,
    SNOW_CM_PER_MM_WATER,
    SNOW_HEAVY_CM,
    SNOW_ROOF_DAMPING,
    SNOW_ROOF_DAYS,
    CONF_CAPACITY_CURVE_ENABLED,
    DEFAULT_CAPACITY_CURVE_ENABLED,
    CAPACITY_MIN_SAMPLES,
    CAPACITY_FLOOR_FRACTION,
    CAPACITY_FORGET,
    CONF_SOLAR_APERTURE_LEARNING_ENABLED,
    DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
    SOLAR_APERTURE_MIN,
    SOLAR_APERTURE_MAX,
    SOLAR_APERTURE_MIN_IRRADIANCE,
    SOLAR_APERTURE_ALPHA,
    SOLAR_APERTURE_MIN_SAMPLES,
    CONF_INTERNAL_GAINS_LEARNING_ENABLED,
    DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
    INTERNAL_GAINS_ALPHA,
    INTERNAL_GAINS_RIDGE,
    INTERNAL_GAINS_MAX_FACTOR,
    CONF_CURVE_LEARNING_ENABLED,
    DEFAULT_CURVE_LEARNING_ENABLED,
    CONF_CONFIDENCE_MARGINS_ENABLED,
    DEFAULT_CONFIDENCE_MARGINS_ENABLED,
    CONFIDENCE_MARGIN_CAP_C,
    CONF_MOLD_GUARD_ENABLED,
    DEFAULT_MOLD_GUARD_ENABLED,
    CONF_INDOOR_HUMIDITY_ENTITY,
    CONF_THERMAL_BRIDGE_FRSI,
    DEFAULT_THERMAL_BRIDGE_FRSI,
    MOLD_SURFACE_RH_LIMIT,
    CONF_COMPRESSOR_REPLACEMENT_COST,
    DEFAULT_COMPRESSOR_REPLACEMENT_COST,
    CONF_COMPRESSOR_RATED_STARTS,
    DEFAULT_COMPRESSOR_RATED_STARTS,
    CONF_WEAR_AUTOTUNE_ENABLED,
    DEFAULT_WEAR_AUTOTUNE_ENABLED,
    CONF_PRICE_TILES_ENABLED,
    DEFAULT_PRICE_TILES_ENABLED,
    SCORE_ALPHA,
    CONF_COMPRESSOR_FREQ_ENTITY,
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_FREQ_CONTROL_MODE,
    DEFAULT_FREQ_CONTROL_MODE,
)
from .inputs import (
    UNBOUNDED,
    InputHealth,
    InputReader,
    age_of,
    normalize_power_kw,
    parse_bool,
    stale_summary,
)
from .external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
    wood_mean_temperature,
)
from . import away as away_mode
from . import battery as battery_view
from . import comfort_band
from . import mixing_valve
from . import topology
from . import pv as pv_model
from .accuracy import (
    LEAD_BUCKETS,
    AccuracySample,
    AccuracyTracker,
    delivered_ratio,
)
from .comfort_learning import ComfortLearner, OverrideEvent
from .defrost import DefrostDerate, DefrostWindow, in_frost_band
from . import pump_signals
from .pump_signals import PumpSignals
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
    IMPLAUSIBLE_FEE_SEK_PER_KWH,
    min_component as grid_fee_min_component,
    max_abs_component as grid_fee_max_abs_component,
    parse_month_range as grid_fee_parse_month_range,
)
from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
from .curve_learning import CurveLearner
from .currency import resolve_currency
from .drift import Cusum
from .ledger import KEEP_MONTHS, MonthlyLedger, month_key
from .wear import StartCounter, wear_price_per_start
from . import narrative
from . import diagnosis
from .freq_control import (
    FREQ_MODE_CONTROL,
    FREQ_MODE_OBSERVE,
    FREQ_WRITE_EPSILON_HZ,
    FREQ_WRITE_MIN_INTERVAL_S,
    FrequencyMap,
    FrequencyWatchdog,
)
from .power_guard import GuardState, project_window_mean
from .snapshots import BIAS_TRIP_DAYS, SnapshotRing
from . import pump_schedule
from homeassistant.helpers import issue_registry as ir
from .open_meteo import OpenMeteoSolar
from .thermal_model import (
    DHW_AMBIENT_TEMP,
    WATER_SPECIFIC_HEAT,
    ThermalModel,
    ThermalParameters,
    ThermalState,
    mold_safe_room_floor,
)
from .dhw_schedule import (
    DHWWindowError,
    format_weekly_windows,
    format_windows,
    hour_in_windows,
    hours_until_next_window,
    overlap_fraction,
    parse_weekly_windows,
    parse_windows,
)
from .optimizer import (
    REASON_LEGIONELLA,
    HeatPumpOptimizer,
    OptimizationConfig,
    OptimizationResult,
    optimize_in_process,
    slab_settlement_cap,
)

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


def _utc_step_starts(
    midnight: datetime,
    n_steps: int,
    step_offset: int = 0,
    step_minutes: int = FORECAST_STEP_MINUTES,
) -> list[datetime]:
    """Step labels walked in UTC, then converted back to ``midnight``'s zone.

    Adding a wall-clock step invents the spring DST gap and stretches the
    autumn overlap into a 75-minute step. Walking the same count in UTC
    keeps every label a real instant. Naive ``midnight`` keeps the old
    wall-clock walk so unzoned fixtures stay byte-identical.
    """
    step = timedelta(minutes=step_minutes)
    tz = midnight.tzinfo
    if tz is None:
        return [midnight + step * (step_offset + i) for i in range(n_steps)]
    base = midnight.astimezone(timezone.utc)
    return [(base + step * (step_offset + i)).astimezone(tz) for i in range(n_steps)]


def _comparable_ts(raw: Any, reference: datetime) -> datetime | None:
    """Parse an entry timestamp so it can be ordered against the step grid.

    A naive timestamp against an aware grid is taken as UTC, matching
    ``_get_current_price``; an aware one against a naive grid keeps its own
    wall clock.

    Module level, not a coordinator method: it reads nothing off ``self``
    and never did, and the class it sat in is the one the decomposition
    programme is trying to empty.
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


def forecast_outdoor_now(forecast: list[dict], now: datetime) -> float | None:
    """The outdoor temperature the solve horizon starts on, °C.

    The plan is solved on the forecast, not on the outdoor thermometer, and
    without a thermometer `ThermalState.outdoor_temperature` is never
    overwritten at all -- `_update_current_state` writes it only under
    ``if outdoor.ok``. So the published "outdoor" 5.0 °C was a dataclass
    default standing beside a plan made at −5 °C, and the modelled COP that
    reads it followed (#282). This is the number the plan is actually
    acting on.

    Matched to ``now`` by the entry's own timestamp, on ``_weather_series``'
    rule -- each entry holds until the next one begins, and before the first
    entry the first is the best information there is. Assuming entry 0 is
    the current hour is what that method's docstring warns about: a stale
    forecast, or one starting at the next hour, then reads hours out of
    phase.

    ``None`` with no forecast -- the one branch where the constructor
    default really is what the horizon gets, and `_weather_series` falls
    back to the same state.
    """
    if not forecast:
        return None
    timed = sorted(
        (
            (ts, entry)
            for entry in forecast
            if (ts := _comparable_ts(entry.get("datetime"), now)) is not None
        ),
        key=lambda item: item[0],
    )
    if timed:
        index = max(0, bisect_right([ts for ts, _ in timed], now) - 1)
        entry = timed[index][1]
    else:
        # No timestamps anywhere: the same positional assumption
        # `_weather_series` falls back to, which starts the series at now.
        entry = forecast[0]
    temperature = entry.get("temperature")
    return None if temperature is None else _as_float(temperature, 5.0)


# A failed solve keeps the last good plan published — deliberately, a solver
# hiccup must not blank the entities — but a plan that keeps failing to
# refresh eventually describes yesterday's prices and weather, not today's.
# Stale = older than three missed solve cycles, floored at 90 minutes so a
# short 5-minute update interval does not declare a plan stale over one
# transient failure. A stale plan stops being actuated (the pump falls back
# to its own curve, exactly as when no plan exists) and, after three
# consecutive failures, raises a repair issue.
PLAN_STALE_INTERVALS = 3
PLAN_STALE_FLOOR_MINUTES = 90.0
SOLVE_FAILURE_ISSUE_COUNT = 3

#: Which configured entity backs each published temperature -- the table
#: `_thermal_view` builds its ``reading_ok`` map from. ``ThermalState`` has
#: constructor defaults (55.0 tank, 40.0 buffer, 22.0 slab, 21.0 either
#: floor, 5.0 outdoor) and a field is overwritten only when its entity read
#: OK, so without this map nothing downstream can tell a measurement from a
#: default that has never moved (#282).
READING_SOURCES: dict[str, str] = {
    # The indoor thermometer is the upper zone, by the two-zone convention
    # `_update_current_state` states and applies.
    "upper_floor_temperature": CONF_INDOOR_TEMP_ENTITY,
    # Only a real lower-floor thermometer; the room-temperature fallback is
    # a modelling stand-in, not a second measurement.
    "lower_floor_temperature": CONF_LOWER_FLOOR_TEMP_ENTITY,
    "floor_return_temperature": CONF_FLOOR_RETURN_TEMP_ENTITY,
    # The slab is never sensed. It is integrated from the floor return, so
    # it is a live estimate exactly while that sensor reads and a one-off
    # `room + 1.0` seed otherwise.
    "slab_temperature": CONF_FLOOR_RETURN_TEMP_ENTITY,
    "buffer_tank_temperature": CONF_BUFFER_TANK_TEMP_ENTITY,
    # Published by `_dhw_view`; the freshness of every temperature this
    # integration publishes belongs in one map.
    "dhw_temperature": CONF_DHW_TEMP_ENTITY,
    # The one this map was missing. Without an outdoor thermometer the 5.0
    # default is what the Outdoor sensor, the climate attribute and the
    # modelled COP all read, every cycle, forever -- and nothing said so.
    "outdoor_temperature": CONF_OUTDOOR_TEMP_ENTITY,
}

# Age limits for the optional sensors read outside InputReader. Humidity
# drives the mold floor — a frozen sensor would hold a raised floor
# forever, so it gets the reader's indoor-scale limit. The DHW inlet probe
# is genuinely slow-moving (ground temperature), so a day; past that the
# seasonal model is the honest fallback.
HUMIDITY_MAX_AGE_MINUTES = 120.0
DHW_INLET_MAX_AGE_MINUTES = 24.0 * 60.0


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
    #: Forecast relative humidity per step, % with NaN where unknown (#21).
    #: Appended, never inserted — same rule as above.
    humidity: np.ndarray = np.array([], dtype=float)
    #: Forecast snowfall rate per step, cm/h (#30). Zero when no data.
    snowfall: np.ndarray = np.array([], dtype=float)

    @classmethod
    def empty(cls) -> "ForecastArrays":
        """No usable horizon, so the caller should skip the run."""
        blank = np.array([], dtype=float)
        return cls(
            blank, blank, blank, blank, blank, blank, blank, blank, blank,
            blank,
        )


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


def house_loss_confidence(samples: int) -> float:
    """The fraction of an EWMA walk from 1.0 the learner has traversed.

    The learner moves ``scale`` toward its target by ``HOUSE_LOSS_ALPHA``
    per sample, so after ``n`` samples the distance still to travel is
    ``(1 - alpha) ** n`` and the traversed fraction is one minus that.
    This is the phi of the re-anchor law: how much of the stored scale
    is measurement rather than starting prior. It is derived from the
    learner's own constant and nothing else, and it lives at module
    level so tests import it rather than re-implement it (issue #91).
    """
    return 1.0 - (1.0 - HOUSE_LOSS_ALPHA) ** max(0, int(samples))


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


_PROCESS_LOCK = threading.Lock()
_PROCESS_WORKER: subprocess.Popen | None = None
_PROCESS_ATEXIT = False


def _worker_env() -> dict[str, str]:
    """Make ``heatpump_optimizer`` importable in the child, tests or HA."""
    env = os.environ.copy()
    here = Path(__file__).resolve().parent
    extra = [str(here.parent)]
    tests_dir = here.parent.parent / "tests"
    if tests_dir.is_dir():
        extra.append(str(tests_dir))
        extra.append(str(tests_dir / "hastub"))
    old = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(extra + ([old] if old else []))
    return env


def _ensure_worker() -> subprocess.Popen:
    """Persistent child interpreter. Not multiprocessing: spawn reimports __main__."""
    global _PROCESS_WORKER, _PROCESS_ATEXIT
    worker = _PROCESS_WORKER
    if worker is not None and worker.poll() is None:
        return worker
    script = Path(__file__).resolve().with_name("process_worker.py")
    _PROCESS_WORKER = subprocess.Popen(
        [sys.executable, "-u", str(script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
        env=_worker_env(),
    )
    if not _PROCESS_ATEXIT:
        atexit.register(_shutdown_process_pool)
        _PROCESS_ATEXIT = True
    return _PROCESS_WORKER


def _shutdown_process_pool() -> None:
    global _PROCESS_WORKER
    with _PROCESS_LOCK:
        worker, _PROCESS_WORKER = _PROCESS_WORKER, None
    if worker is None:
        return
    try:
        if worker.stdin:
            worker.stdin.close()
    except Exception:  # noqa: BLE001 - shutdown must not raise
        pass
    if worker.poll() is None:
        worker.terminate()
        try:
            worker.wait(timeout=2)
        except Exception:  # noqa: BLE001
            worker.kill()


def _run_in_process(fn, args):
    """Run ``fn(*args)`` in the process worker. ``fn`` must be picklable."""
    global _PROCESS_WORKER
    with _PROCESS_LOCK:
        worker = _ensure_worker()
        stdin, stdout = worker.stdin, worker.stdout
        if stdin is None or stdout is None:
            raise RuntimeError("process worker pipes missing")
        pickle.dump((fn, args), stdin, protocol=pickle.HIGHEST_PROTOCOL)
        stdin.flush()
        try:
            status, payload = pickle.load(stdout)
        except (EOFError, BrokenPipeError) as err:
            rc = worker.poll()
            _PROCESS_WORKER = None
            raise RuntimeError(f"process worker exited rc={rc}") from err
    if status == "err":
        raise payload
    return payload


async def _await_process(hass, fn, *args):
    """Park on HA's executor; the CPU work is in another interpreter."""
    return await hass.async_add_executor_job(_run_in_process, fn, args)


async def _await_optimize(hass, optimizer, state, *positional, **keywords):
    """Submit ``optimizer.optimize`` through the process pool (#199 #290)."""
    return await _await_process(
        hass, optimize_in_process, optimizer, state, positional, keywords
    )


def _diagnose_payload(coord) -> tuple:
    """Picklable diagnose args; the coordinator itself is not picklable."""
    record = coord._last_interval_record
    if record is None:
        return None, None
    return record, copy.deepcopy(coord._thermal_params)


def _store_diagnosis(coord, report) -> None:
    if report is not None:
        coord._last_diagnosis = report


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
        # Resolved once: the sensors stamp it into their units at
        # construction, and units must not change while an entity lives.
        self.currency = resolve_currency(hass)

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
        self._init_insurance(hass, entry)
        self._init_ecl110()

        # #236: ConfigEntryNotReady runs the entry's unload callbacks and
        # nothing else -- no async_unload_entry, so no async_shutdown -- and
        # the registrations above are already on ``hass``: 1 leak per retry.
        on_unload = getattr(entry, "async_on_unload", None)
        if on_unload is not None:
            on_unload(self._release_registrations)

        # Deferred: MQTT may not be up yet, and the stores are on disk.
        # Tracked (D1-02 hygiene): the panel's refuted leak does not
        # reproduce through the config-entry state machine, but an
        # untracked task still runs against whatever hass becomes after
        # unload, and tracking costs one set entry.
        self._spawn(self._async_setup_ecl110_state_subscription())
        for load in (
            self._async_load_dhw_profile,
            self._async_load_dhw_draws,
            self._async_load_dhw_legionella,
            self._async_load_thermal_learning,
            self._async_load_price_model,
            self._async_load_accuracy,
            self._async_load_energy_totals,
            self._async_load_ledger,
            self._async_load_snapshots,
            self._async_setup_peak_guard,
            self._async_setup_defrost_watch,
            self._async_load_manual_plan,
        ):
            self._spawn(load())

    @callback
    def _release_registrations(self) -> None:
        """Drop every hass-level registration this coordinator holds (#236).

        Idempotent: both the entry's ``async_on_unload`` list and
        ``async_shutdown`` may run it. The latch matters as much as the
        unsubscribes -- a deferred registration task can still be queued when
        setup fails and would otherwise register after this ran -- and it is
        also what every actuation point reads to decline (#237).
        """
        self._entry_released = True
        for name in ("_unsub_ecl110_state", "_unsub_peak_guard", "_unsub_defrost"):
            unsub = getattr(self, name, None)
            setattr(self, name, None)
            if unsub is not None:
                unsub()

    def _spawn(self, coro) -> Any:
        """Fire-and-forget a coroutine, but keep the task until it lands.

        Home Assistant tracks tasks itself; this set exists so
        ``async_shutdown`` can let in-flight store writes finish rather
        than orphan them against a torn-down entry. The bare test stub
        closes the coroutine and returns None -- nothing to track then.
        """
        task = self.hass.async_create_task(coro)
        if task is None:
            return None
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def _init_insurance(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """The learners' insurance and the drift detectors (v4.0.0 T4a).

        Detection ships default-on because a freeze only stops learning —
        it never moves a plan. Everything that could move one (the comfort
        relaxation, the DHW margin nudge) is gated behind its own flag.
        """
        # #26: an open window shows as sustained colder-than-predicted
        # residuals in the heat-loss learner's replay.
        self._vent_cusum = Cusum(
            threshold=VENT_CUSUM_THRESHOLD_C,
            drift=VENT_CUSUM_DRIFT_C,
            side=-1,
        )
        # #11: the immersion element announces itself as measured power
        # beyond what the compressor can draw. 2/2 hysteresis, like every
        # event detector in this integration.
        self._immersion_active: bool = False
        self._immersion_over_count: int = 0
        self._immersion_clear_count: int = 0
        self._immersion_evidence: list[str] = []
        self._immersion_events: list[str] = []
        # #12: a weeks-scale COP baseline per 3 °C bucket, fed only outside
        # the frost band, and a slow CUSUM on the relative shortfall.
        #
        # v5.3.0: keyed by (bucket, which curve the sample was judged
        # against), not by bucket alone. ``_cop_reference_curve`` made
        # ``observed_cop`` curve-dependent — a hot-water interval is measured
        # against the DHW curve, which the model itself prices 8-20 % below
        # the space curve at the same outdoor temperature. Feeding both into
        # one baseline compares two different quantities: the shortfall of a
        # perfectly healthy pump then reads as the gap between the curves,
        # the one-sided CUSUM accumulates it, and the owner is told his
        # compressor has degraded. In the committed ``shoulder`` fixture 38
        # of 96 steps are space-only and 30 are DHW-only, so this is the
        # ordinary plan shape rather than an edge case.
        self._cop_baseline: dict[tuple[int, bool], list[float]] = {}
        self._cop_health_cusum = Cusum(
            threshold=COP_HEALTH_THRESHOLD, drift=COP_HEALTH_DRIFT, side=1
        )
        # #42: the weekly ring of learner snapshots.
        self._snapshot_ring = SnapshotRing()
        self._snapshot_store: Store = Store(
            hass, 1, f"{DOMAIN}_{entry.entry_id}_snapshots"
        )
        self._rollback_done_for_alarm: bool = False
        # The heartbeat must not act before the persisted ring loads, or
        # the first cycle snapshots half-loaded learners into an empty
        # ring and saves that over eight weeks of insurance.
        self._snapshots_loaded: bool = False
        # T4b #30: the roof-snow memory — a decaying accumulator of
        # snowfall and the instant it last crossed "heavy". Weather
        # memory, not learning; persisted so a restart mid-snow does not
        # brighten the roof.
        self._snow_accum_cm: float = 0.0
        self._snow_accum_last: datetime | None = None
        self._last_heavy_snow: datetime | None = None
        # T4b learners (#17 #36 #53 #2), each fully behind its own flag —
        # learning AND application, so a config change never suddenly
        # applies weeks of evidence gathered while nobody was looking.
        #: #17: per-3 °C-bucket upper envelope of delivered thermal kW.
        self._capacity_envelope: dict[int, list[float]] = {}
        #: #36: EWMA regression moments of (modelled Q_solar, implied
        #: residual power) and the scale they currently support.
        self._solar_aperture: dict[str, float] = {
            "n": 0.0, "mx": 0.0, "my": 0.0, "cov": 0.0, "var": 0.0,
            "scale": 1.0,
        }
        #: #53: learned per-hour internal gains, kW; None until first fold.
        self._internal_gains_profile: list[float] | None = None
        #: #2: the standing heat-curve displace bias.
        self._curve_learner = CurveLearner()
        #: #2's evidence: worst (zone − floor) margin seen so far today.
        self._curve_day: str = ""
        self._curve_day_worst: float | None = None
        # Worst-of-day input health, accumulated across heartbeats and
        # consumed when a day is counted (#42): a morning of garbage
        # inputs must not green-light an evening rollback.
        self._day_inputs_healthy: bool = True

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
        # Consecutive failed solves. A failed solve keeps the last good plan
        # published; this counter is what turns "keeps" into "keeps, and
        # says so" — the staleness flag, the actuation fallback and the
        # repair issue all key off it and off the last success time.
        self._solve_failures: int = 0
        self._next_optimization: datetime | None = None
        self._prices: list[dict] = []
        self._weather_forecast: list[dict] = []
        # Weather staleness (M2): a failed or empty fetch marks the forecast
        # stale from that moment; the payload publishes the age so a plan
        # built on stale weather can say so. None means fresh.
        self._weather_stale_since: datetime | None = None
        self._weather_outage_cycles: int = 0
        self._current_state = ThermalState()
        self._current_action: dict[str, Any] = {}
        self._unsub_timer: Any = None
        # Fire-and-forget tasks (store saves, listener registrations), held
        # so shutdown can let them finish instead of orphaning them against
        # a torn-down entry; and the Tibber outage latch (D10-09).
        self._background_tasks: set[Any] = set()
        # The lifecycle seam (#236, #237): one latch for "this entry is gone",
        # and the refresh handle shutdown cancels -- HA cancels an entry's
        # BACKGROUND tasks, and the scheduled refresh may not be one.
        self._entry_released: bool = False
        self._refresh_task: Any = None
        self._tibber_outage_cycles: int = 0
        # One reauth flow per auth outage (D10-08): re-armed on recovery.
        self._tibber_reauth_started: bool = False

        # Solar irradiance and the floor return temperature sensor.
        self._solar_radiation: float = 0.0
        self._floor_return_temp: float | None = None
        self._solar_radiation_forecast: list[float] = []
        self._open_meteo: OpenMeteoSolar | None = None

        # A run takes seconds, so a user tapping the button repeatedly must not
        # be able to stack solves on top of each other.
        self._optimization_running: bool = False

        # Set by ``async_setup_entry`` — and by nothing else — just before the
        # first refresh: that refresh runs inside setup, where a full cold
        # solve stalls the whole instance. Consumed on the next update cycle,
        # so every subsequent refresh (and every direct test call) solves
        # exactly as it always has.
        self._skip_solve_once: bool = False
        # The previous plan, handed over by ``async_unload_entry`` across an
        # in-process reload so the flag-lightened first refresh can republish
        # it instantly, without even a network fetch. Never persisted.
        self._reload_handover: dict[str, Any] | None = None

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
        # v5.1.10: the cycle the PLAN commanded, followed independently of
        # whether the tank was ever seen at temperature. Without this the
        # only way the timer could ever reset was an observation at
        # ``legionella_temp - 1``, so a pump that cannot get there — or a
        # tank with no probe at all — left the countdown running for ever.
        self._legionella_boost_active: bool = False
        self._legionella_boost_peak: float | None = None
        self._legionella_boost_started: datetime | None = None
        #: When a commanded cycle last FINISHED SHORT of the disinfection
        #: temperature, and how far it got. This is not success and is never
        #: reported as such; it exists so the retry happens once per
        #: interval instead of on the first step of every single plan.
        self._dhw_legionella_attempt: datetime | None = None
        self._dhw_legionella_attempt_peak: float | None = None
        #: The (disinfection temp, charge limit, interval) the ceiling notice
        #: was last raised for, so it is only rewritten when the pair changes.
        self._legionella_ceiling_notice: tuple[float, float, float] | None = None
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
        #: Walking measured/commanded ratio; the COP fold judges outliers
        #: against it so a persistent efficiency shift can still teach.
        self._cop_ratio_ewma: float | None = None
        self._last_measured_cop: float | None = None
        # Which curve ``_last_measured_cop`` was judged against, and the tank
        # temperature that curve was evaluated at. Recorded rather than the
        # modelled *value* on purpose: the accuracy residual is taken at the
        # settling sample's own outdoor temperature, not at the one the COP
        # was learned from, and swapping in a stored value would silently
        # change that for every install. Storing the curve *choice* leaves the
        # default path expression for expression identical.
        self._last_cop_curve_dhw: bool = False
        self._last_cop_dhw_temp: float | None = None
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
        # The fee magnitude the standing "grid_fee_magnitude" repair issue
        # was raised for; None = no issue. Re-raising every cycle would
        # refresh the issue's timestamp and bury when the bad value first
        # appeared — the same reason solve_failures raises exactly-at.
        self._grid_fee_issue_value: float | None = None
        # The sign notice's counterpart (audit D4-05, #169), same contract.
        self._grid_fee_sign_issue_value: float | None = None
        # Whether the standing "lower_floor_modelled" repair issue is up.
        # Raised once, not per cycle, for the same reason the fee issue is:
        # re-raising refreshes the timestamp and buries when it started.
        self._lower_floor_issue_raised = False
        # The contradiction the standing "comfort_band_contradiction" issue
        # was raised for; None = no issue.
        self._band_issue_problem: str | None = None
        self._ledger = MonthlyLedger()
        self._ledger_store: Store = Store(
            hass,
            1,
            f"{DOMAIN}_{entry.entry_id}_ledger",
        )

        # --- Insight (v4.0.0 T6) -------------------------------------------
        # #55: the realised compressor-start counter, sharing the ledger's
        # store so counts and the wear SEK they book can never load from
        # different generations of state.
        self._start_counter = StartCounter()
        # #40: receipts frozen at month rollover. Frozen rather than
        # recomputed on read, so a receipt never changes after the month it
        # describes has closed.
        self._month_reports: dict[str, dict] = {}
        # #65: the operation score's day book (today's settled kWh, SEK and
        # spot samples) plus the smoothed score, persisted with the ledger.
        self._score_day: dict[str, Any] = {}
        self._operation_score: float | None = None
        # #39: the price tiles, refreshed one per scheduled solve.
        self._price_tiles: dict[str, dict] = {}
        self._price_tile_cursor = 0
        # #52: the last settled interval's (planned, realised, actual)
        # triple, and the latest attribution run over one. In memory only:
        # a diagnosis is about the interval that just happened.
        self._last_interval_record: dict[str, Any] | None = None
        self._last_diagnosis: dict[str, Any] | None = None

        # --- Inverter frequency (v4.0.0 T7 #61) ----------------------------
        # Observe learns; control actuates only on explicit opt-in, and the
        # watchdog's stand-down latch survives restarts via the thermal
        # learning store.
        self._freq_map = FrequencyMap()
        self._freq_watchdog = FrequencyWatchdog()
        self._freq_fallback = False
        # Stamped at init rather than None: the rate limit is in-memory,
        # and a crash-looping HA restarting every minute must not get a
        # fresh write per boot. Costs one 5-minute delay after any start.
        self._freq_last_write: datetime | None = dt_util.now()

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
        # v5.2.0: the same machinery, keyed to the hot-water tank instead of
        # the room. A SECOND INSTANCE rather than a per-channel key threaded
        # through AccuracyTracker: the lead-time record is already
        # self-contained (file a promise, score it when it matures, ask
        # sigma), so a separate tracker reuses the bucketing, the admission
        # window, the EWMA rate and the persistence format exactly as
        # written, and adds no branch to any of them. Only its lead record
        # is fed — the one-step `samples` deque stays empty, because the
        # tank has no realised power or cost column of its own to settle,
        # and `trust()`/`temperature_mae()` are the room model's judgement,
        # not the tank's.
        self._dhw_accuracy = AccuracyTracker()
        self._pending_prediction: dict[str, Any] | None = None
        self._accuracy_store: Store = Store(
            hass,
            ACCURACY_STORE_VERSION,
            f"{DOMAIN}_{entry.entry_id}_accuracy",
        )
        # Serialized form of the last payload each store accepted, keyed by
        # store name. An every-cycle save that rewrites unchanged content is
        # pure disk wear; a digest recorded only after a successful save means
        # a failed write is retried on the next cycle rather than skipped.
        self._store_digests: dict[str, str] = {}

        # --- Defrost derate (item 14) --------------------------------------
        self._defrost = DefrostDerate()
        self._thermal_params.defrost_derate = self._defrost

        # Defrost on-time for the interval being measured (v5.3.0). Fed by
        # the per-cycle read AND by a state listener, because the two see
        # different things — see ``DefrostWindow``.
        self._defrost_window = DefrostWindow()
        self._unsub_defrost: Any = None

        # --- Heat pump signals (v5.3.0) ------------------------------------
        # All four slots are optional and default absent, and absent resolves
        # to full capability with no freeze — so an install that configures
        # none of them behaves exactly as v5.1.5 did.
        self._pump_signals: PumpSignals = PumpSignals()
        # The last operating mode that was actually recognised, kept so a mode
        # entity that drops out falls back to what the pump last said rather
        # than to "it can do everything". None until one is seen.
        self._pump_mode_last_good = None
        # When that mode was actually read. The fallback is bounded by it:
        # see MODE_LAST_GOOD_MAX_AGE_MINUTES for why an unbounded one made
        # the mode entity's freshness horizon do nothing at all.
        self._pump_mode_last_good_at: datetime | None = None
        #: Whether the "your mode entity has gone quiet" notice is raised.
        self._pump_mode_expired_notice: bool = False
        # Signature of the "disinfection is blocked by the pump's mode"
        # notice currently raised, or None when none is. Coarsened to whole
        # overdue days so a worsening situation updates the text without
        # re-raising the issue every cycle.
        self._legionella_mode_block_notice: int | None = None
        #: Whether the "flue probe has gone quiet" warning has been logged
        #: for the current outage. Cleared when the probe reports again.
        self._external_probe_stale_warned: bool = False

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
        #: The date the lifetime accumulators started, restored from the
        #: energy store; set on first publish when the store has none.
        self._energy_totals_since: str | None = None
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
                ),
                # The fit's intercept ridge pulls toward the CONFIGURED
                # gains and mass — the only priors the experiment may use
                # without assuming the answer it is trying to measure.
                gains_prior_kw=float(self._thermal_params.internal_gains),
                thermal_mass_prior=float(
                    self._thermal_params.room_thermal_mass
                ),
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
            unsub = await mqtt.async_subscribe(
                self.hass,
                self._ecl110_state_topic,
                self._async_handle_ecl110_state_message,
                qos=self._ecl110_qos,
            )
            # #236: the entry can go away across the await, and the state
            # topic defaults on -- the leak neither guard being on can avoid.
            if self._entry_released:
                if unsub is not None:
                    unsub()
                return
            self._unsub_ecl110_state = unsub
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

        This integration is a service (a cloud API plus the user's own
        entities), not a physical device, so the registry entry says so:
        ``entry_type=DeviceEntryType.SERVICE`` is what the Gold "devices"
        rule asks for and what makes HA present the entry as a service
        (#305). It lives in ``helpers.device_registry`` at the 2024.6 floor;
        ``DeviceInfo`` has no ``config_entry`` field there.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="Heat Pump Optimizer",
            manufacturer="Custom",
            model="MPC Optimizer",
            sw_version=self.integration_version,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def effective_config(self) -> dict[str, Any]:
        """The merged data and options this coordinator was built from.

        ``async_update_options`` compares a save against it: the options
        flow rewrites the options dict on every page it leaves, so only a
        save that changes the effective config earns a reload.
        """
        return self._config

    @property
    def target_temperature(self) -> float:
        """The comfort target the user configured."""
        return self._opt_config.target_temp

    async def async_set_target_temperature(self, temperature: float) -> None:
        """Change the comfort target and persist it across restarts.

        Writing it back to the entry options is what makes the change survive
        a reload; updating only the in-memory optimizer config meant the value
        silently reverted the next time the entry was reloaded.

        Checked against the comfort band first (v5.1.7). This is a write to the
        same config entry the options flow guards, and it used to arrive with
        nothing checking it at all — the thermostat's own slider ran to
        ``max_temp + 1``, so its top notch stored a target above the ceiling by
        construction. A band the plan can never satisfy is not rejected
        downstream, because the bounds are priced rather than fenced; it just
        plans in permanent violation.
        """
        found = comfort_band.violations(
            {CONF_TARGET_TEMP: float(temperature)}, self._config
        )
        if found:
            raise ServiceValidationError(
                comfort_band.describe(found),
                translation_domain=DOMAIN,
                translation_key="set_temperature_comfort_band_violation",
                translation_placeholders={
                    "violations": comfort_band.describe(found)
                },
            )
        self._opt_config.target_temp = temperature
        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, CONF_TARGET_TEMP: temperature},
        )

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
        default = self._thermal_params.dhw_hourly_draw_pattern.copy()
        if len(profile) != 24:
            return default
        try:
            cleaned = [float(np.clip(v, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY)) for v in profile]
            avg = float(np.mean(cleaned))
        except (TypeError, ValueError):
            return default
        if avg <= 0:
            return default
        return [float(np.clip(v / avg, DHW_PROFILE_MIN_INTENSITY, DHW_PROFILE_MAX_INTENSITY)) for v in cleaned]

    async def _async_load_dhw_profile(self) -> None:
        """Load the persisted DHW usage profile and tank cooling rate."""
        try:
            stored = dict(await self._dhw_profile_store.async_load() or {})
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
            except (TypeError, ValueError, OverflowError):
                self._dhw_daytype_samples[count_idx] = 0

        rate = stored.get("cooling_rate")
        if rate is None:
            return
        try:
            self._apply_dhw_cooling_rate(float(rate))
            self._dhw_cooling_samples = int(stored.get("cooling_samples", 0))
        except (TypeError, ValueError, OverflowError) as err:
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

    def _dhw_profile_payload(self) -> dict[str, Any]:
        """The DHW profile store's exact save shape.

        One producer for both the store and the weekly snapshot (#42),
        same contract as ``_thermal_learning_payload``: a second
        hand-built copy is how formats drift.
        """
        return {
            "hourly_profile": self._dhw_hourly_profile,
            "cooling_rate": self._dhw_cooling_rate,
            "cooling_samples": self._dhw_cooling_samples,
            # #18: additive — old loaders ignore these keys.
            "profile_weekday": self._dhw_profile_weekday,
            "profile_weekend": self._dhw_profile_weekend,
            "profile_weekday_samples": self._dhw_daytype_samples[0],
            "profile_weekend_samples": self._dhw_daytype_samples[1],
        }

    async def _async_save_dhw_profile(self) -> None:
        """Persist learned DHW profile to Home Assistant storage."""
        try:
            await self._dhw_profile_store.async_save(
                {
                    **self._dhw_profile_payload(),
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
        if isinstance(stored, dict):
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
            # An inlet probe is slow-moving, so a generous day-scale limit —
            # but a probe frozen since last winter would otherwise pin the
            # inlet at winter cold forever. Stale degrades to the seasonal
            # model below, which is the configured no-sensor behaviour.
            age = age_of(state, dt_util.utcnow()) if state is not None else None
            if age is not None and age <= timedelta(
                minutes=DHW_INLET_MAX_AGE_MINUTES
            ):
                try:
                    value = float(state.state)
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

        # T4a #11 (gated): a recurring immersion rescue asks the plan to
        # arrive a little earlier. 0.0 with the flag off — byte-inert.
        params.dhw_ready_margin_c = self._immersion_dhw_margin(now)

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
            # A near-zero or negative mean (negative spot spells are real
            # in a Nordic spring) makes the scaled ceiling ~0 or negative,
            # which the elastic gate can never see the price dip under —
            # silently deferring the anti-legionella boost to its hard
            # deadline through exactly the cheap spells it should use.
            # None is the configured "no elasticity, run on schedule"
            # answer, which is the fail-safe one for hygiene. Same guard
            # style as ``_record_quiet_comfort_period``.
            if level > 1e-6:
                params.dhw_legionella_price_ceiling = (
                    self._price_model.expected_daily_min(
                        sorted(set(day_types)), level
                    )
                )

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
        outdoor = float(self._current_state.outdoor_temperature)
        mean_price = float(
            np.mean([p.get("total", 0.0) for p in self._prices])
        )
        # The sweep ranks candidates by cost, and ranking needs a positive
        # price level: a negative mean flips every ``cost_day`` negative and
        # min-cost then crowns the candidate using the MOST energy. The
        # sweep is a relative comparison, so on a worthless-energy day a
        # floored positive level keeps the ranking meaningful — better than
        # the advisor entity vanishing, which would look like a bug.
        if mean_price <= 1e-6:
            mean_price = max(abs(mean_price), 0.1)
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
        # The model's own daily draw, not a re-derivation: the inline
        # `volume · cp · ΔT` this replaces omitted the greywater-recovery
        # factor the simulation applies, so the advisor priced a heavier
        # draw than the model ever runs and every candidate's absolute cost
        # sat high. `dhw_draw_power` carries the recovery and the shared
        # inlet reference. The draw is still referenced to the *configured*
        # setpoint, deliberately: the tank delivers at the tap mix whatever
        # the candidate stores at, so the term is candidate-independent and
        # cannot disturb the ranking.
        draw_day_kwh = params.dhw_draw_power * 24.0
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
            stored = dict(await self._thermal_learning_store.async_load() or {})
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
            except (TypeError, ValueError, OverflowError) as err:
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
            except (TypeError, ValueError, OverflowError) as err:
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
            except (TypeError, ValueError, OverflowError) as err:
                _LOGGER.debug("Could not load lower floor loss ratio: %s", err)

        # v5.7.0 (issue #86): the store now records the UA the scale was
        # fitted against, and an options edit that changed it is corrected
        # here -- on load, before anything solves -- rather than restored
        # verbatim against the new nameplate. The gated write adopts an
        # anchor for a pre-fix store and persists a re-anchor; unconditional
        # saves are useless here because `updated_at` defeats the store's
        # content-hash skip.
        _had_anchor = "house_heat_loss_anchor" in stored
        _reanchored = self._reanchor_house_heat_loss_scale(
            stored.get("house_heat_loss_anchor")
        )
        if _reanchored or not _had_anchor:
            await self._async_save_thermal_learning()

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
            except (TypeError, ValueError, OverflowError) as err:
                _LOGGER.debug("Could not load COP scale: %s", err)

        # v4.0.0 T4a — the detectors' memory. Absent from every pre-T4
        # payload, and each loader tolerates garbage on its own.
        self._vent_cusum.load(stored.get("vent_cusum"))
        self._cop_health_cusum.load(stored.get("cop_health_cusum"))
        raw_baseline = stored.get("cop_baseline")
        if isinstance(raw_baseline, dict):
            for key, entry in raw_baseline.items():
                try:
                    # "4" is a pre-v5.3.0 space-curve bucket and is kept as
                    # one; "4:dhw" is the hot-water curve's own baseline.
                    text = str(key)
                    is_dhw = text.endswith(":dhw")
                    bucket = int(text[:-4] if is_dhw else text)
                    self._cop_baseline[(bucket, is_dhw)] = [
                        float(entry[0]),
                        int(entry[1]),
                    ]
                except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                    continue
        raw_events = stored.get("immersion_events")
        if isinstance(raw_events, list):
            self._immersion_events = [str(e) for e in raw_events[-20:]]
        try:
            self._snow_accum_cm = max(0.0, float(stored.get("snow_accum_cm", 0.0)))
        except (TypeError, ValueError, OverflowError):
            self._snow_accum_cm = 0.0
        raw_snow = stored.get("last_heavy_snow")
        if isinstance(raw_snow, str):
            try:
                self._last_heavy_snow = datetime.fromisoformat(raw_snow)
            except ValueError:
                self._last_heavy_snow = None
        # The accumulator's clock persists too: without it, a restart
        # after a multi-day outage skipped the downtime's decay entirely
        # and stale accumulation could re-trip the roof-snow damping.
        raw_snow_last = stored.get("snow_accum_last")
        if isinstance(raw_snow_last, str):
            try:
                self._snow_accum_last = datetime.fromisoformat(raw_snow_last)
            except ValueError:
                self._snow_accum_last = None
        # T7 #61: the watchdog's stand-down latch. Parsed HERE and not in
        # the shared learner parser on purpose — a learner rollback must
        # not quietly re-arm a controller that stood down over a hardware
        # fault; only the user re-arms it (by re-saving the mode). Strict
        # `is True`, not truthiness: corrupt store garbage silently
        # latching a stand-down that never happened would disable control
        # with no repair issue and no visible cause.
        self._freq_fallback = stored.get("freq_fallback") is True
        if self._freq_fallback and (
            str(
                self._config.get(
                    CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE
                )
            )
            == FREQ_MODE_CONTROL
        ):
            _LOGGER.warning(
                "Frequency control is standing down from an earlier "
                "watchdog trip; switch the frequency mode to observe and "
                "back to control to re-arm it"
            )
        self._load_t4b_learners(stored)

    def _load_t4b_learners(self, stored: dict) -> None:
        """Parse the T4b learners' additive keys (#17 #36 #53 #2).

        One parser for both the store loader and the snapshot restore, so
        the two paths cannot drift apart.
        """
        raw_env = stored.get("capacity_envelope")
        if isinstance(raw_env, dict):
            for key, entry in raw_env.items():
                try:
                    self._capacity_envelope[int(key)] = [
                        float(entry[0]),
                        int(entry[1]),
                    ]
                except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                    continue
        raw_ap = stored.get("solar_aperture")
        if isinstance(raw_ap, dict):
            for key in ("n", "mx", "my", "cov", "var", "scale"):
                try:
                    self._solar_aperture[key] = float(raw_ap.get(key, self._solar_aperture[key]))
                except (TypeError, ValueError, OverflowError):
                    continue
            self._solar_aperture["scale"] = float(
                np.clip(
                    self._solar_aperture["scale"],
                    SOLAR_APERTURE_MIN,
                    SOLAR_APERTURE_MAX,
                )
            )
        raw_gains = stored.get("internal_gains_profile")
        if isinstance(raw_gains, list) and len(raw_gains) == 24:
            try:
                self._internal_gains_profile = [float(g) for g in raw_gains]
            except (TypeError, ValueError, OverflowError):
                self._internal_gains_profile = None
        raw_curve = stored.get("curve_learner")
        if isinstance(raw_curve, dict):
            self._curve_learner = CurveLearner.from_dict(raw_curve)
        # T7 #61: the kW-per-Hz map is a learner like the envelope above —
        # snapshots carry it and rollbacks restore it through this same
        # parser (from_dict is its own corruption barrier).
        raw_freq = stored.get("freq_map")
        if isinstance(raw_freq, dict):
            self._freq_map = FrequencyMap.from_dict(raw_freq)

    def _thermal_learning_payload(self) -> dict[str, Any]:
        """The thermal-learning store's exact save shape.

        One producer for both the store and the weekly snapshot (#42):
        serialising learned state by any second path is how formats drift.
        """
        return {
            "buffer_cooling_rate": self._buffer_cooling_rate,
            "buffer_cooling_samples": self._buffer_cooling_samples,
            # The configured UA the scale was fitted against, so an options
            # edit that changes it can be corrected on load instead of
            # multiplying a correction fitted against the old nameplate by
            # the new one (issue #86). The KNOWN DEFECT note that was here
            # is resolved by _reanchor_house_heat_loss_scale; the shape of
            # the fix and the four attempts that did not ship are recorded
            # in docs/backlog.md's "Open" entry and its decisions.
            "house_heat_loss_anchor": round(self._house_heat_loss_anchor(), 6),
            "house_heat_loss_scale": self._house_heat_loss_scale,
            "house_heat_loss_samples": self._house_heat_loss_samples,
            "lower_floor_loss_ratio": self._lower_floor_loss_ratio,
            "lower_floor_loss_samples": self._lower_floor_loss_samples,
            # Every plan is priced through the COP curve, so a learned
            # correction that evaporated on restart silently re-based
            # all costs on the nameplate figure.
            "cop_scale": self._cop_scale,
            "cop_samples": self._cop_samples,
            # v4.0.0 T4a — the detectors' memory, all additive keys.
            "vent_cusum": self._vent_cusum.as_dict(),
            # A space-curve bucket keeps its pre-v5.3.0 key ("4"), so an
            # older store loads unchanged and a downgrade still reads it; a
            # DHW-curve bucket rides alongside under "4:dhw". Additive, and
            # nothing is discarded on upgrade.
            "cop_baseline": {
                (f"{k[0]}:dhw" if k[1] else str(k[0])): [
                    round(v[0], 4),
                    int(v[1]),
                ]
                for k, v in self._cop_baseline.items()
            },
            "cop_health_cusum": self._cop_health_cusum.as_dict(),
            "immersion_events": list(self._immersion_events),
            # T4b #30: roof-snow memory, so a restart mid-snow does not
            # brighten the roof. Weather memory riding the nearest store.
            "snow_accum_cm": round(self._snow_accum_cm, 3),
            "snow_accum_last": (
                self._snow_accum_last.isoformat()
                if self._snow_accum_last is not None
                else None
            ),
            "last_heavy_snow": (
                self._last_heavy_snow.isoformat()
                if self._last_heavy_snow is not None
                else None
            ),
            # T4b learners (#17 #36 #53 #2) — all additive keys, so this
            # payload (and every weekly snapshot of it) stays loadable by
            # any earlier version.
            "capacity_envelope": {
                str(k): [round(float(v[0]), 3), int(v[1])]
                for k, v in self._capacity_envelope.items()
            },
            "solar_aperture": {
                k: round(float(v), 6) for k, v in self._solar_aperture.items()
            },
            "internal_gains_profile": (
                [round(float(g), 4) for g in self._internal_gains_profile]
                if self._internal_gains_profile is not None
                else None
            ),
            "curve_learner": self._curve_learner.as_dict(),
            # T7 #61 — the kW-per-Hz map (a learner) and the watchdog's
            # stand-down latch (a safety fact, exempt from rollback).
            "freq_map": self._freq_map.as_dict(),
            "freq_fallback": bool(self._freq_fallback),
            "updated_at": dt_util.now().isoformat(),
        }

    async def _async_save_thermal_learning(self) -> None:
        """Persist the learned buffer and building parameters."""
        try:
            await self._thermal_learning_store.async_save(
                self._thermal_learning_payload()
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
        other_powers: list[float] | None = None,
    ) -> list[dict[str, Any]]:
        """Collapse a per-step power schedule into contiguous heating slots.

        The step schedule is what the optimizer produces, but what a person
        wants to see is "the pump runs from 02:00 to 04:30 and that costs 4.20".
        Consecutive steps above ``threshold`` kW are merged into one slot and
        summarised with their energy, average price and cost.

        Each slot also carries the reason code that dominates it, so an
        unexpected slot is no longer indistinguishable from a bug.

        ``other_powers`` is the OTHER channel's schedule (hot water when
        these are space steps, and vice versa). Where both are active in
        the same step the pump is time-sharing the quarter hour — a
        deliberate relaxation, not double-booking — and the slot says so
        via ``shared_kwh``: the other channel's energy inside this slot's
        shared steps. Zero-overlap slots carry no key, so captures without
        overlap are unchanged.
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
            if other_powers is not None:
                shared = sum(
                    other_powers[i]
                    for i in span
                    if i < len(other_powers)
                    and other_powers[i] > threshold
                    and powers[i] > threshold
                ) * dt_hours
                if shared > 1e-9:
                    slot["shared_kwh"] = round(shared, 3)
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

    def _dhw_confidence_band(
        self, dhw_temp: list[float | None], dt_hours: float
    ) -> tuple[list[float | None], list[float | None]]:
        """``dhw_temp`` ∓ the tank record's expected error, per step.

        ``None`` at every step until the record has actually scored a pair.
        ``sigma`` answers 0.0 with no evidence, and publishing
        ``dhw_temp ± 0`` would lay two dashed lines exactly on the curve —
        a fresh install claiming perfect foresight, which is the opposite
        of what the band is for. Nothing beats a lie here, so the card gets
        nulls and draws nothing at all.

        Step ``i`` holds trajectory index ``i + 1``, so its promise is
        ``(i + 1) * dt_hours`` ahead — the same lead convention
        ``_confidence_margins`` uses for the comfort floor, and the same one
        the promises were filed under.
        """
        n = len(dhw_temp)
        if not self._dhw_accuracy.has_lead_history():
            return [None] * n, [None] * n
        lo: list[float | None] = []
        hi: list[float | None] = []
        for i, value in enumerate(dhw_temp):
            if value is None:
                # A step past the end of the trajectory has no centre to
                # put a band around; nulls here break the dashed line
                # exactly where the solid one already ends.
                lo.append(None)
                hi.append(None)
                continue
            sigma = self._dhw_accuracy.sigma((i + 1) * dt_hours)
            # Two decimals, as `series()` rounds `dhw_temp` itself: the
            # band and the curve it brackets must not disagree in the
            # last digit.
            lo.append(round(float(value) - sigma, 2))
            hi.append(round(float(value) + sigma, 2))
        return lo, hi

    def _build_plan_views(self, result) -> dict[str, Any]:
        """Full-resolution space heating and DHW plans for the plan sensors.

        Same horizon as ``schedule`` / ``dhw_schedule`` (those keys used to
        stop at 24 steps / 6 h). Charting the plan needs slots and a
        full-horizon forecast, which those keys do not group.
        The legacy sensors still publish the raw step list, not the slots.
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
        # v5.2.0: how far the tank curve has historically been out, at each
        # step's own distance ahead. Deliberately NOT the same kind of thing
        # as the room's `upper`/`lower`, which are two real predicted floor
        # temperatures — this is an expected-error envelope, and the card
        # labels the two differently for exactly that reason.
        dhw_temp_lo, dhw_temp_hi = self._dhw_confidence_band(
            dhw_temp, dt_hours
        )

        raw_prices = [p if p is not None else 0.0 for p in prices]
        raw_space = [p if p is not None else 0.0 for p in space_power]
        raw_dhw = [p if p is not None else 0.0 for p in dhw_power]

        space_slots = self._plan_slots(
            timestamps,
            raw_space,
            raw_prices,
            dt_hours,
            reasons=result.space_reasons,
            other_powers=raw_dhw,
        )
        dhw_slots = self._plan_slots(
            timestamps,
            raw_dhw,
            raw_prices,
            dt_hours,
            reasons=result.dhw_reasons,
            other_powers=raw_space,
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
                "dhw_temp_lo": dhw_temp_lo[i],
                "dhw_temp_hi": dhw_temp_hi[i],
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

    def _commanded_split(self) -> tuple[float, float]:
        """The plan's (space, hot water) allocation as the pump can serve it.

        The split the plan wrote, with any channel the *observed* operating
        mode cannot deliver zeroed. A pump switched to ``heat`` will not make
        hot water however much the plan allocated to it, and the meter will
        never show that kilowatt; leaving it in the commanded figure books the
        difference as the pump failing to track its plan.

        The window this matters in is real but bounded: the mode gate stops
        the *next* solve from allocating a channel the pump cannot serve, so
        what is corrected here is every interval between the mode changing on
        the pump and the plan catching up. That is exactly the interval whose
        measurement is least like the others and most likely to be believed.

        Gated on ``mode_observed``, not on the capability flags: with no mode
        entity the capability is the full-capability fallback and both
        channels pass through untouched, so an install without one is
        bit-identical to v5.1.5.
        """
        action = self._current_action
        space = float(action.get("power", 0.0))
        dhw = float(action.get("dhw_power", 0.0))
        signals = self._pump_signals
        if signals.mode_observed:
            if not signals.mode.space_heat:
                space = 0.0
            if not signals.mode.dhw:
                dhw = 0.0
        return space, dhw

    def _commanded_power(self) -> float:
        """Total electrical draw the plan is asking of the heat pump, kW.

        ``current_action["power"]`` is the *space heating* allocation and
        ``dhw_power`` is the hot water one; a meter sees only their sum.
        Comparing the space figure alone against a measured total makes a
        planned hot-water charge look like the pump drawing power it was never
        asked for — which reads as an external heat source, as a collapsed
        COP, and as a defrost derate, all at once.

        The sum is right whether or not the compressor serves the two duties
        concurrently — and on this hardware ``HEATDHW`` and ``COOLDHW`` do run
        both at once, which the comment here used to deny (see
        ``pump_mode.ModeCapability.concurrent``). What the sum is *not* right
        about is a channel the pump is not serving at all, which is what
        ``_commanded_split`` removes.
        """
        space, dhw = self._commanded_split()
        return space + dhw

    def _interval_space_power(self) -> float | None:
        """Electrical power that actually heated the house last interval, kW.

        The interval learners replay the elapsed period through the model, and
        what the model needs is what the pump really drew — a delivery
        shortfall replayed as if the commanded power had flowed gets blamed on
        the heat loss coefficient (v4.0.5). With a power entity the measured
        total wins, minus the plan's hot-water allocation, because the meter
        sees one sum; while the immersion element is latched the reading is a
        different appliance's and the interval carries no usable space figure.
        ``None`` means "skip this sample": the entity is configured but stale
        (`read_power_kw`'s ok=False contract) or contaminated. Without any
        power entity there is no measurement to prefer and the commanded
        figure remains the only available estimate, as before.

        v5.3.0 fixes a silent under-report here. The subtraction removes *the
        plan's* hot-water allocation from the measured total, on the premise
        that the plan describes what the pump is doing. When the pump is
        actually in ``heat`` that premise is false: no hot water was made, the
        meter reading is all space heating, and subtracting a phantom DHW
        share hands the house heat-loss learner a space figure that is too low
        by exactly the allocation — every interval, in the same direction, for
        as long as the mismatch lasts. A biased-low input to a learner that
        persists what it concludes is the failure class this whole guard
        exists for. ``_commanded_split`` now zeroes the channel the observed
        mode cannot serve, so the subtraction removes only hot water that
        could actually have been made.
        """
        commanded_space, dhw_share = self._commanded_split()
        if not self._config.get(CONF_POWER_ENTITY):
            return commanded_space
        if self._measured_power is None or self._immersion_active:
            return None
        if self._pump_signals.mode_observed and not self._pump_signals.space_heat:
            # v5.3.0: the pump is in a mode that heats no rooms, so whatever
            # the meter is reading went somewhere else — hot water, or the
            # cooling circuit. There is no space figure to extract, and
            # returning zero would be a *confident* claim that the house got
            # nothing, which the house heat-loss learner would then replay as
            # thermal behaviour. Skip the sample instead.
            return None
        # The subtraction only splits the meter correctly while the pump is
        # plausibly running the plan: a deferred DHW start, or a
        # controller-initiated boost the plan never commanded, lands the
        # whole gap on the space figure — and the floor at zero then
        # fabricates a confident 0 kW sample. Same gate, same reasoning as
        # the COP fold: a large total gap is tracking, not measurement, so
        # the interval carries no usable split (v4.0.5 review).
        commanded_total = commanded_space + dhw_share
        if (
            abs(float(self._measured_power) - commanded_total)
            / max(commanded_total, 0.5)
            > COP_TRACKING_ERROR_GATE
        ):
            return None
        return max(0.0, float(self._measured_power) - dhw_share)

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

    def _external_heat_override(self, reader: InputReader) -> bool | None:
        """State of a user-provided stove/flue entity, if one is configured.

        v5.3.0: read through the same guarded reader as the wood-side probes
        beside it, rather than straight out of ``hass.states``. The override
        is the strongest single input in the integration: while it says "yes"
        the detector suppresses and the optimizer stops planning heat it
        believes the fire is supplying, and while it says "no" it overrules
        the inference outright.

        **The freshness horizon applies to numbers only, and that asymmetry is
        the whole point.** The argument for ageing this input out is an
        argument about a *measurement*: a flue probe with a flat battery
        stuck at 400 °C looks like an indefinite free fire, which is the
        expensive failure direction, and it is the same failure the
        neighbouring wood probes have been gated against since v3.x. A probe
        re-reports every poll, so its age is real evidence about whether
        anything is still watching the flue.

        None of that holds for a flag. This slot is offered as
        ``binary_sensor``/``switch``/``input_boolean``/``sensor``, and the two
        the documentation recommends first are helpers that are written
        *only when they change*: an ``input_boolean``, or a template
        ``binary_sensor`` fed by one, has ``last_reported`` equal to the
        moment the user last flipped it and never moves again. Ageing that
        out does not catch a broken sensor; it discards a deliberate setting
        an hour after it was made, in both directions at once — the "yes"
        that suppresses and the "no" that overrules the detector alike — for
        a household that may well leave the switch on for a fortnight of
        wood-burning. So a flag is read with no horizon, exactly as it was
        before v5.3.0.

        The boolean vocabulary is shared (``inputs.parse_bool``); the numeric
        rule is NOT, and numbers are therefore tested FIRST. A flue
        temperature above 30 °C means a fire is burning, which is a heuristic
        about this one sensor. The shared rule reads any non-zero number as
        "yes" — right for a fault code, and quite wrong for a probe reading
        20 °C in a cold room — so it must never see a number here.
        """
        # A numeric read applies the horizon from INPUT_MAX_AGE_MINUTES and
        # rejects a word as ``not_numeric``, so this one call both classifies
        # the entity and gates the probe case.
        probe = reader.read(CONF_EXTERNAL_HEAT_ENTITY)
        if probe.ok and probe.value is not None:
            self._external_probe_stale_warned = False
            return probe.value > 30.0
        if probe.stale:
            # Warned once per outage, not once per cycle: a probe that has
            # gone quiet stays quiet, and a line every five minutes for days
            # is how a log stops being read. Re-armed when it reports again.
            if not self._external_probe_stale_warned:
                self._external_probe_stale_warned = True
                _LOGGER.warning(
                    "External heat override %s has not reported for %.0f min "
                    "(limit %.0f); ignoring it until it does. A flue probe "
                    "that stops reporting would otherwise hold heating back "
                    "forever",
                    probe.entity_id,
                    probe.age_minutes if probe.age_minutes is not None else -1.0,
                    probe.max_age_minutes
                    if probe.max_age_minutes is not None
                    else -1.0,
                )
            return None
        self._external_probe_stale_warned = False
        if probe.problem != "not_numeric":
            # not_configured, missing_entity or unavailable: nothing to read.
            return None
        reading = reader.read_state(
            CONF_EXTERNAL_HEAT_ENTITY, max_age_minutes=UNBOUNDED
        )
        if not reading.ok or reading.text is None:
            return None
        return parse_bool(reading.text)

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
            override=self._external_heat_override(reader),
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

    #: How lopsided the commanded split has to be before one curve owns the
    #: interval. Below it the other channel is a rounding error; between the
    #: two the interval belongs to neither and is dropped.
    _COP_CURVE_SHARE = 0.15

    def _cop_reference_curve(self) -> tuple[float | None, bool, float | None]:
        """The modelled COP this interval should be judged against, or None.

        Returns ``(cop, dhw_curve, dhw_tank_temp)``. The choice is *returned*
        rather than stored on the instance: several of
        ``_learn_measured_cop``'s guards sit between this call and the point
        where ``_last_measured_cop`` is written, so a method that recorded
        the choice as a side effect re-pointed the residual's reference on
        every cycle that then declined to produce a COP at all — including
        the blended-interval branch below, which in ``HEATDHW`` with an even
        split is *every* cycle on the hardware this release targets. The
        stored COP would then be subtracted from a curve it was never
        referenced to. ``_learn_measured_cop`` writes all three together.

        v5.3.0. ``_learn_measured_cop`` used to compare every interval against
        ``compute_cop`` — the SPACE curve — including intervals the pump spent
        making hot water. Hot water runs 55-65 °C flow against 35-45 °C for
        space heating, and the model prices that at roughly 16 % lower COP at a
        55 °C setpoint. So a perfectly healthy pump doing exactly what the plan
        asked looked ~16 % less efficient than modelled, every hot-water
        interval, in the same direction.

        Three things consume the result and all three were wrong for those
        intervals: the reported ``measured_cop``, the capacity envelope, and —
        the one that bites — ``_observe_cop_health``, the weeks-scale
        degradation watch whose whole job is to notice a *persistent* shortfall
        against its own baseline. A DHW-heavy household fed it a persistent
        shortfall by construction.

        The choice is made from the commanded split as the pump can actually
        serve it (``_commanded_split``), and only when the mode was observed:
        without a mode entity the split may be a plan-side fiction, and every
        install without one must stay bit-identical to v5.1.5.

        Returns ``None`` when the interval is a genuine blend — the ``HEATDHW``
        and ``COOLDHW`` modes really do run both duties at once, so this is not
        hypothetical on the hardware this release targets — because one ratio
        cannot be attributed to two curves.
        """
        outdoor = self._current_state.outdoor_temperature
        space_curve = self._thermal_model.compute_cop(outdoor)
        space_ref = (space_curve, False, None)
        if not self._pump_signals.mode_observed:
            return space_ref
        space, dhw = self._commanded_split()
        total = space + dhw
        if total <= 1e-6:
            return space_ref
        dhw_share = dhw / total
        if dhw_share <= self._COP_CURVE_SHARE:
            return space_ref
        if dhw_share >= 1.0 - self._COP_CURVE_SHARE:
            tank = float(self._current_state.dhw_temperature)
            return self._thermal_model.compute_cop_dhw(outdoor, tank), True, tank
        return None, False, None

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
        #
        # v5.3.0 narrows this from the whole band to the intervals that
        # actually contain a defrost. The disjointness argument only ever
        # justified excluding intervals the derate learns from — but without a
        # flag there was no way to tell which those were, so the exclusion had
        # to cover 0-5 °C entirely. In a Swedish shoulder season that is a
        # large share of all heating hours, and ``cop_scale`` multiplies every
        # cost the integration reports: the one learner whose error is in
        # every number was blind in the conditions it spends most of its life
        # in. With a real flag the attribution stays disjoint at much finer
        # grain — a defrosting interval is still the derate's alone.
        #
        # ``observed`` is what keeps this honest. No flag, an unreadable flag,
        # or a flag past its horizon all fall back to the whole-band
        # exclusion, so nothing changes for an install without one.
        if in_frost_band(self._current_state.outdoor_temperature):
            window = self._defrost_window.peek(dt_util.now())
            if not window.observed or window.any_defrost:
                return

        # #11: a resistive kW in the reading is not the compressor being
        # inefficient, it is a different appliance on the same meter.
        if self._immersion_active:
            return

        # v4.0.5: delivered heat is not measured, so this ratio can only be
        # read as efficiency when the pump is plausibly running the plan. A
        # large commanded-vs-measured gap is usually the pump NOT tracking
        # (compressor limits, cycling, ramp lag) — folding it booked pure
        # tracking error into ``cop_scale``. But a gate fixed on the
        # commanded ratio deadlocks: a pump whose true efficiency sits more
        # than the gate away from the current scale shows that same gap on
        # EVERY sample, so nothing ever folds, the scale never moves, and
        # the degradation watchdog downstream goes blind at exactly the
        # severity it exists for (v4.0.5 review). So outliers are judged
        # against a walking ratio EWMA instead: a one-off blip deviates
        # from it and is dropped, while a persistent shift WALKS the EWMA
        # (it updates from every sample) and unlocks folding within a
        # handful of intervals.
        ratio = float(self._measured_power) / max(commanded, 1e-6)
        # Seeded at 1.0 — the model's own expectation, since ``commanded``
        # already carries the current scale — and gated against the value
        # BEFORE this sample updates it, so a first-sample blip cannot
        # vouch for itself. The EWMA walks on every sample, accepted or
        # not: that is what lets a genuine persistent shift unlock.
        ewma = self._cop_ratio_ewma if self._cop_ratio_ewma is not None else 1.0
        self._cop_ratio_ewma = 0.9 * ewma + 0.1 * ratio
        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:
            _LOGGER.debug(
                "Skipping COP sample: commanded %.2f kW vs measured %.2f kW "
                "deviates from the running ratio %.2f — a tracking blip, "
                "not an efficiency reading",
                commanded,
                self._measured_power,
                ewma,
            )
            return

        modelled_cop, cop_curve_dhw, cop_dhw_temp = self._cop_reference_curve()
        if modelled_cop is None:
            # A genuinely blended interval: the pump ran both duties at once
            # and neither dominates, so the one ratio this method produces
            # cannot be attributed to either curve. Skipping is the honest
            # answer; guessing would put a DHW-shaped error into the space
            # multiplier every plan's cost runs through.
            return
        if modelled_cop <= 0.1:
            return

        # The thermal output the plan intended is commanded power times the
        # modelled COP; delivering that with a different electrical input means
        # the real COP differs by the ratio of the two inputs.
        observed_cop = modelled_cop * commanded / self._measured_power
        if not np.isfinite(observed_cop) or observed_cop <= 0.1:
            return
        # The COP and the curve it was judged against are written together,
        # and only here. Every guard above returns without touching either,
        # so the pair the accuracy residual reads can never be mismatched.
        self._last_measured_cop = round(float(observed_cop), 2)
        self._last_cop_curve_dhw = cop_curve_dhw
        self._last_cop_dhw_temp = cop_dhw_temp

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
        # #12: the same vetted sample feeds the weeks-scale health watch —
        # this path is already guarded against frost, immersion, freezes
        # and low duty, so the baseline inherits every filter for free.
        self._observe_cop_health(float(observed_cop), cop_curve_dhw)
        # #17 (gated): and the capacity envelope, for the same reason.
        self._fold_capacity_envelope(float(observed_cop))

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

    def _house_heat_loss_anchor(self) -> float:
        """The total base UA the learned scale currently multiplies.

        In two-zone mode the scale owns the *level* of both zones -- the
        ratio owns the split -- so the quantity it multiplies is the zone
        total with the learned ratio applied, not the upper zone the fit
        reads. Round 1 of the re-anchor got exactly this wrong and went
        sign-negative on every single-zone edit in a two-zone house.
        """
        p = self._thermal_params
        if p.two_zone_enabled:
            return (
                p.upper_floor_heat_loss
                + p.lower_floor_heat_loss * self._lower_floor_loss_ratio
            )
        return p.heat_loss_coefficient

    def _reanchor_house_heat_loss_scale(self, anchor: float | None) -> bool:
        """Re-express the learned scale against the UA now configured.

        An options edit reloads the entry with a new nameplate while the
        store still holds a scale fitted against the old one; restoring
        it verbatim left the model up to 1.94x wrong (issue #86, four
        prior attempts recorded in docs/backlog.md). The law, from the
        recorded decisions:

        ``U_eff' = (1 - phi) * nameplate_new + phi * measured_UA``

        written in absolute UA on the zone-total basis, where
        ``measured_UA = scale * anchor`` and phi is
        ``house_loss_confidence(samples)``. Path-independent and sign-
        preserving at convergence, and the nameplate at zero samples --
        an install that has learned nothing keeps its configuration
        edits, which is where round 1 did its damage.

        Two guards, both from the recorded decisions:

        * **Threshold gate.** Below a ``HOUSE_LOSS_MAX_STEP`` nameplate
          change the stored scale is kept verbatim: below convergence
          the law is a measured regression against today's behaviour on
          exactly that path (the 30-hop walk: +2.5% for today against
          the ungated law's 18.2%), and the learner absorbs a small
          edit in one step anyway.
        * **Clamp means reset.** If the re-anchored scale falls outside
          ``[0.3, 3.0]`` the measurement cannot be expressed against
          the new nameplate: reset explicitly and log it. Clipping onto
          a bound instead lets the next edit read that bound as the
          learner's own signal.

        Returns whether the stored state changed, so callers can gate
        the one persistence write (``updated_at`` moves every save, so
        the content-hash skip cannot gate this store).
        """
        if anchor is None:
            # A pre-fix store carries no anchor: nothing to re-express,
            # and the caller adopts one on its next save.
            return False
        try:
            anchor = float(anchor)
        except (TypeError, ValueError, OverflowError):
            return False
        current = self._house_heat_loss_anchor()
        if anchor <= 1e-9 or current <= 1e-9 or not np.isfinite(anchor):
            return False
        if abs(current / anchor - 1.0) <= HOUSE_LOSS_MAX_STEP:
            return False
        phi = house_loss_confidence(self._house_heat_loss_samples)
        measured_ua = self._house_heat_loss_scale * anchor
        effective = (1.0 - phi) * current + phi * measured_ua
        new_scale = effective / current
        if (
            new_scale < HOUSE_HEAT_LOSS_SCALE_MIN
            or new_scale > HOUSE_HEAT_LOSS_SCALE_MAX
        ):
            _LOGGER.warning(
                "Learned house heat loss scale %.3f (fitted against "
                "%.4f kW/°C, %d samples) cannot be expressed against the "
                "newly configured %.4f kW/°C: resetting to the "
                "configuration",
                self._house_heat_loss_scale,
                anchor,
                self._house_heat_loss_samples,
                current,
            )
            self._apply_house_heat_loss_scale(DEFAULT_HOUSE_HEAT_LOSS_SCALE)
            self._house_heat_loss_samples = 0
            return True
        _LOGGER.info(
            "Re-anchored learned house heat loss scale %.3f -> %.3f "
            "against the configured UA %.4f -> %.4f kW/°C (%d samples, "
            "confidence %.2f)",
            self._house_heat_loss_scale,
            new_scale,
            anchor,
            current,
            self._house_heat_loss_samples,
            phi,
        )
        self._apply_house_heat_loss_scale(new_scale)
        return True

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
        # Measured where a meter exists (v4.0.5): replaying the *commanded*
        # power attributed every delivery shortfall to the heat loss
        # coefficient. ``None`` = no trustworthy figure this interval.
        previous_power = self._interval_space_power()

        # Snapshot for the next interval before any early return, so a rejected
        # sample does not poison the following one with a stale baseline.
        self._last_house_sample = replace(self._current_state)
        self._last_house_sample_time = now

        frozen = self._learning_frozen(
            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY
        )
        # "ventilation" is the one freeze reason this method must look
        # past: the ventilation detector below is what CLEARS it, and it
        # needs the residual to see the window close. Every other reason
        # (stale sensors, external heat) makes the residual itself
        # untrustworthy, detector included.
        vent_only = frozen == "ventilation"
        if frozen and not vent_only:
            self._learner_freeze_reason = frozen
            return

        if previous_state is None or previous_time is None or observed is None:
            return
        # A configured meter that is stale or contaminated this interval:
        # nothing trustworthy to replay, so no sample — a skipped interval
        # loses convergence; a wrong power replayed corrupts a persisted
        # parameter.
        if previous_power is None:
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
                # #53: the replay must predict with the learned per-hour
                # profile, or its residuals never re-centre and the gains
                # learner becomes an open-loop integrator converging to
                # α/ridge times the true correction. None-profile (flag
                # off, nothing learned) makes this byte-inert.
                hour_of_day=previous_time.hour + previous_time.minute / 60.0,
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

        # #26: an open window shows as SUSTAINED colder-than-predicted
        # residuals — often exactly the large ones the guard below throws
        # away, which is why the detector is fed first, clipped so one
        # sensor glitch cannot trip it alone. On a trip every learner
        # freezes with reason "ventilation" until the residuals recover.
        vent_changed = self._vent_cusum.update(
            now, float(np.clip(residual, -VENT_CUSUM_CLIP_C, VENT_CUSUM_CLIP_C))
        )
        if vent_changed:
            _LOGGER.info(
                "Open-window detector %s (stat %.2f)",
                "tripped" if self._vent_cusum.tripped else "released",
                self._vent_cusum.stat,
            )
            await self._async_save_thermal_learning()
        if vent_only:
            # The detector has been fed; the learner itself stays frozen
            # until the window closes.
            self._learner_freeze_reason = frozen
            return

        if abs(residual) > HOUSE_LOSS_MAX_RESIDUAL:
            _LOGGER.debug(
                "Ignoring house heat loss sample: residual %.2f°C is too large "
                "to be a heat loss error",
                residual,
            )
            return

        # T4b (#36 #53, both gated): the same accepted residual, split by
        # attribution so the two learners cannot fight over one sample —
        # sunny intervals inform the solar aperture, dark ones the
        # internal-gains profile, and the heat-loss fold below keeps
        # everything as before (UA error correlates with ΔT, not with the
        # sun, so sharing samples with it is sound).
        self._fold_solar_aperture(previous_state, residual, dt_h)
        self._fold_internal_gains(previous_time, previous_state, residual, dt_h)

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
        # the elapsed interval, and the measured figure wins over the
        # commanded one wherever a meter exists (v4.0.5).
        previous_power = self._interval_space_power()
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
        # Same skip as the house learner: a stale or contaminated meter
        # leaves nothing trustworthy to replay.
        if previous_power is None:
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
                # Same physics as the solve when #53 is on; inert when off.
                hour_of_day=previous_time.hour + previous_time.minute / 60.0,
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
            # A cycle that ran but fell short is remembered separately, so a
            # restart cannot turn a failed attempt back into an overdue timer
            # that pins a boost on every plan.
            attempt_raw = (stored or {}).get("last_attempt")
            attempt = (
                dt_util.parse_datetime(attempt_raw)
                if isinstance(attempt_raw, str)
                else None
            )
            if attempt is not None:
                self._dhw_legionella_attempt = attempt
                peak = (stored or {}).get("last_attempt_peak")
                if isinstance(peak, (int, float)):
                    self._dhw_legionella_attempt_peak = float(peak)
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
        payload: dict[str, Any] = {
            "last_cycle": self._dhw_last_legionella.isoformat()
        }
        if self._dhw_legionella_attempt is not None:
            payload["last_attempt"] = self._dhw_legionella_attempt.isoformat()
            if self._dhw_legionella_attempt_peak is not None:
                payload["last_attempt_peak"] = round(
                    float(self._dhw_legionella_attempt_peak), 2
                )
        try:
            await self._dhw_legionella_store.async_save(payload)
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
        # A real cycle clears any record of one that fell short, and takes the
        # "cannot reach temperature" notice down with it.
        self._dhw_legionella_attempt = None
        self._dhw_legionella_attempt_peak = None
        self._clear_legionella_unreachable_issue()
        self._clear_legionella_unverified_issue()
        _LOGGER.info(
            "DHW anti-legionella cycle observed at %.1f°C, timer reset", dhw_temp
        )
        await self._async_save_dhw_legionella()

    async def _async_track_dhw_legionella_cycle(
        self, dhw_temp: float | None
    ) -> None:
        """Follow the disinfection boost the PLAN commanded, to its end.

        The observer above resets the timer only on seeing the tank at
        ``legionella_temp - 1``. That is the only reset path there is, and it
        has two holes:

        * a pump that cannot physically get the tank to 60 °C never triggers
          it, so ``hours_since`` runs past the interval and never comes back;
        * with no tank probe configured it cannot run at all, while the
          countdown keeps advancing on the clock.

        Either way the cycle is permanently overdue — and an overdue cycle
        used to pin a 60 °C requirement on the first step of every plan, for
        ever, while never actually disinfecting anything. Both the scheduling
        half and the user-facing half of that are fixed here: the boost the
        plan commanded is followed to its end, and what happened is recorded
        honestly.

        "Its end" has to be bounded, because a cycle the tank cannot finish
        is re-commanded on every solve and its boost window never closes on
        its own. After ``DHW_LEGIONELLA_BOOST_MAX_HOURS`` the window is
        closed here and judged on what it managed — otherwise a pump heating
        towards a temperature it will never reach would do so indefinitely,
        and nothing would ever be recorded or reported.

        Success is never inferred from the peak this saw. The observer above
        owns that decision, and its rule differs with the free-disinfection
        flag; asking "did the observer credit a cycle while this boost ran?"
        is the same question on both sides of it. Reading the peak instead
        left a cycle topping out in the half-degree between the two rules
        neither credited nor recorded, with the countdown pinned at its
        overdue value for ever.
        """
        params = self._thermal_params
        if not params.dhw_legionella_enabled:
            self._legionella_boost_active = False
            self._legionella_boost_peak = None
            self._legionella_boost_started = None
            return

        now = dt_util.now()
        commanded = (
            str(self._current_action.get("dhw_reason") or "") == REASON_LEGIONELLA
        )
        if commanded:
            if not self._legionella_boost_active:
                self._legionella_boost_active = True
                self._legionella_boost_started = now
            if dhw_temp is not None:
                self._legionella_boost_peak = max(
                    self._legionella_boost_peak
                    if self._legionella_boost_peak is not None
                    else float(dhw_temp),
                    float(dhw_temp),
                )
            started = self._legionella_boost_started
            expired = (
                started is not None
                and (now - started).total_seconds()
                >= DHW_LEGIONELLA_BOOST_MAX_HOURS * 3600.0
            )
            if not expired:
                return
            # Still commanded after half a day. A cycle the tank cannot
            # finish is re-commanded on every solve, so waiting for the boost
            # to end is waiting for something that never happens: the window
            # is closed here instead and judged on what it managed, which is
            # what lets the retry be spaced and the user be told.
            _LOGGER.warning(
                "DHW anti-legionella boost has been commanded for %.0f h "
                "without completing; recording what it achieved",
                DHW_LEGIONELLA_BOOST_MAX_HOURS,
            )
        elif not self._legionella_boost_active:
            return

        # The boost window closed — either the plan moved on, or it outlasted
        # the bound above. Decide what it achieved.
        started = self._legionella_boost_started
        self._legionella_boost_active = False
        self._legionella_boost_started = None
        peak = self._legionella_boost_peak
        self._legionella_boost_peak = None
        target = float(params.dhw_legionella_temp)

        # Did the observer credit a completed cycle while this boost ran? That
        # is the only evidence of success there is, and it is the same test on
        # both sides of the free-disinfection flag. Reading the peak instead
        # (`peak >= target - 1.0`) disagreed with the observer's own rule
        # (`target - 0.5`, held for DHW_LEGIONELLA_HOLD_MINUTES): a cycle
        # peaking in [59.0, 59.5) was neither credited nor recorded, no notice
        # was raised, and `hours_since` stayed pinned at its overdue value
        # while the cycle was re-commanded on every single solve.
        credited = (
            self._dhw_last_legionella is not None
            and started is not None
            and self._dhw_last_legionella >= started
        )
        if credited:
            return

        has_probe = bool(self._config.get(CONF_DHW_TEMP_ENTITY))
        if not has_probe:
            # No way to verify, ever. What is recorded is an ATTEMPT, not a
            # completion: nothing observed the tank, and this integration
            # publishes a plan — the actuation may be an external automation
            # that never ran. An attempt already drives `hours_since` from
            # 192 h to 0 exactly as a completion would, because
            # `_dhw_hours_since_legionella` counts attempts too, so claiming
            # success bought no scheduling benefit at all and cost the ability
            # to say the cycle is unverified. It is said instead.
            self._legionella_hold_minutes = 0.0
            self._dhw_legionella_attempt = now
            self._dhw_legionella_attempt_peak = None
            _LOGGER.warning(
                "DHW anti-legionella cycle commanded but cannot be verified: "
                "no tank temperature sensor is configured, so nothing confirms "
                "the tank reached %.0f °C",
                target,
            )
            self._raise_legionella_unverified_issue(target)
            await self._async_save_dhw_legionella()
            return

        if peak is None:
            # A probe exists but said nothing for the whole boost. Nothing was
            # observed, so nothing is claimed — but the retry is still spaced
            # by the interval rather than repeated on every solve.
            self._dhw_legionella_attempt = now
            self._dhw_legionella_attempt_peak = None
            _LOGGER.warning(
                "DHW anti-legionella cycle ran with no usable tank reading; "
                "it cannot be confirmed and will be retried next interval"
            )
            await self._async_save_dhw_legionella()
            return

        self._dhw_legionella_attempt = now
        self._dhw_legionella_attempt_peak = float(peak)
        if peak >= target - 1.0:
            # It got to temperature but the completion was never credited —
            # under the free-disinfection flag that means the hold was not
            # observed for long enough. The retry is spaced by the interval,
            # and no "cannot reach temperature" notice is raised, because the
            # tank plainly can.
            _LOGGER.warning(
                "DHW anti-legionella cycle reached %.1f °C but the completion "
                "could not be confirmed; it will be retried next interval",
                peak,
            )
        else:
            # Commanded, run, and the tank topped out below the disinfection
            # temperature. This is the achievable maximum for this pump and
            # this tank, so repeating the same boost cannot do better.
            _LOGGER.warning(
                "DHW anti-legionella cycle reached only %.1f °C against a "
                "%.0f °C target; the tank is not being disinfected",
                peak,
                target,
            )
            self._raise_legionella_unreachable_issue(float(peak), target)
        await self._async_save_dhw_legionella()

    def _check_dhw_legionella_ceiling(self) -> None:
        """Say so when disinfection takes the tank above the charge limit.

        A warning, not a block. Since v5.1.10 the charge limit really is the
        highest temperature the plan charges to, and the disinfection
        temperature applies only during a cycle — so a 52/60 pair is a valid
        configuration with a consequence: once an interval the tank goes 8 °C
        above the limit. Judged from the parameters actually in force, which
        is what makes it cover the ``set_thermal_parameters`` service as well
        as the two config-flow pages; the flow's own validator warns at save
        time, but a service call never touches a form.
        """
        params = self._thermal_params
        legionella = float(params.dhw_legionella_temp)
        setpoint = float(params.dhw_setpoint)
        # The stock pair says nothing. `dhw_enabled=True` alone gives 55/60,
        # both straight from DEFAULT_*, so raising a WARNING-severity,
        # non-fixable Repairs card on it put a permanent card on every fresh
        # install — one whose own text reads "That is allowed and nothing is
        # wrong", which is not what a Repairs card is for. Nothing about the
        # stock pair is a surprise the user needs telling; a pair they edited
        # to differ still is. The config flow logs the same fact at save time
        # for anyone who does set it up that way.
        stock = (
            legionella == float(DEFAULT_DHW_LEGIONELLA_TEMP)
            and setpoint == float(DEFAULT_DHW_SETPOINT)
        )
        active = (
            bool(params.dhw_enabled and params.dhw_legionella_enabled)
            and legionella > setpoint
            and not stock
        )
        signature = (
            (
                round(legionella, 1),
                round(setpoint, 1),
                round(float(params.dhw_legionella_interval_days), 1),
            )
            if active
            else None
        )
        if signature == self._legionella_ceiling_notice:
            return
        self._legionella_ceiling_notice = signature
        if signature is None:
            try:
                ir.async_delete_issue(
                    self.hass, DOMAIN, "dhw_legionella_above_setpoint"
                )
            except Exception as err:  # noqa: BLE001 - clearing is best-effort
                _LOGGER.debug("Could not clear legionella ceiling notice: %s", err)
            return
        legionella, setpoint, interval = signature
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_above_setpoint",
            is_fixable=False,
            # Not persistent: it is derived from configuration, so it is
            # re-raised on the next cycle for as long as the pair stands.
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_above_setpoint",
            translation_placeholders={
                "legionella_temp": f"{legionella:.0f}",
                "setpoint": f"{setpoint:.0f}",
                "interval_days": f"{interval:.0f}",
            },
        )

    def _raise_legionella_unreachable_issue(
        self, peak: float, target: float
    ) -> None:
        """Tell the user the disinfection cycle is not reaching temperature.

        Silent failure is the worst outcome available here: the user believes
        the tank is being disinfected weekly and it is not. Persistent, because
        the fact survives a restart in the store.
        """
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_unreachable",
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_unreachable",
            translation_placeholders={
                "reached": f"{peak:.1f}",
                "target": f"{target:.0f}",
            },
        )

    def _clear_legionella_unreachable_issue(self) -> None:
        """Take the notice down once a cycle actually reaches temperature."""
        try:
            ir.async_delete_issue(self.hass, DOMAIN, "dhw_legionella_unreachable")
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear legionella issue: %s", err)

    def _raise_legionella_unverified_issue(self, target: float) -> None:
        """Say that the cycle was commanded but nothing confirmed it ran.

        This integration publishes a plan; whether the pump obeyed it is
        something only a tank temperature can answer. Without one, a
        commanded cycle is a request, not a disinfection — and telling the
        user their water is being disinfected weekly when nothing checked is
        the one failure mode worth a notice all by itself. Persistent,
        because the fact survives a restart.
        """
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_unverified",
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_unverified",
            translation_placeholders={"target": f"{target:.0f}"},
        )

    def _clear_legionella_unverified_issue(self) -> None:
        """Take it down once a cycle is actually observed at temperature."""
        try:
            ir.async_delete_issue(self.hass, DOMAIN, "dhw_legionella_unverified")
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear legionella notice: %s", err)

    def _dhw_hours_since_legionella(self) -> float | None:
        """Hours since the last anti-legionella cycle, or None if unknown.

        A cycle that RAN but fell short counts here too. It is not success —
        nothing pretends it was — but it does bound the retry rate. Without
        it, a pump that cannot reach the disinfection temperature leaves the
        timer permanently overdue, and an overdue timer used to pin a 60 °C
        requirement on the first step of every plan for ever: the boost was
        re-commanded every quarter of an hour and never once completed.
        """
        last = self._dhw_last_legionella
        attempt = self._dhw_legionella_attempt
        if attempt is not None and (last is None or attempt > last):
            last = attempt
        if last is None:
            return None
        delta = (dt_util.now() - last).total_seconds() / 3600.0
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

    def _check_pump_mode_expired(self) -> None:
        """Say so when the mode entity has gone quiet long enough to stop acting.

        The expiry itself is the safety fix -- an unbounded ``last_good`` left
        a dead mode entity suppressing a channel for the life of the install.
        But expiring silently trades one invisible state for another: the
        integration would go back to planning heat while the pump may well
        still be in the mode it was last seen in. This is the half the user
        can act on, by fixing or clearing the entity.
        """
        expired = (
            self._pump_signals.mode_source == pump_signals.MODE_SOURCE_EXPIRED
        )
        if expired == self._pump_mode_expired_notice:
            return
        self._pump_mode_expired_notice = expired
        if not expired:
            try:
                ir.async_delete_issue(self.hass, DOMAIN, "pump_mode_unreadable")
            except Exception as err:  # noqa: BLE001 - clearing is best-effort
                _LOGGER.debug("Could not clear the mode notice: %s", err)
            return
        _LOGGER.warning(
            "The heat pump's operating mode entity has been unreadable for "
            "over %.0f min; the mode it last reported (%s) has stopped "
            "acting and the plan is back to assuming full capability",
            MODE_LAST_GOOD_MAX_AGE_MINUTES,
            self._pump_mode_last_good.label
            if self._pump_mode_last_good is not None
            else "unknown",
        )
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "pump_mode_unreadable",
            is_fixable=False,
            # Derived from the live reading, so it is re-raised for as long
            # as the entity stays unreadable and clears the moment it returns.
            severity=ir.IssueSeverity.WARNING,
            translation_key="pump_mode_unreadable",
            translation_placeholders={
                "hours": f"{MODE_LAST_GOOD_MAX_AGE_MINUTES / 60.0:.0f}",
                "mode": (
                    self._pump_mode_last_good.label
                    if self._pump_mode_last_good is not None
                    else "unknown"
                ),
            },
        )

    def _check_legionella_mode_block(self, dhw_blocked: bool) -> None:
        """Say so when a mode block is holding disinfection past its deadline.

        A hot-water channel the pump's mode has blocked is hard-zeroed for
        the whole horizon, so the anti-legionella cycle simply never gets
        placed: ``dhw_legionella_due_in_hours`` goes negative in an attribute
        and nothing else happens. A pump left in a heating-only mode for a
        fortnight therefore stops disinfecting the tank silently, which is
        the same failure ``dhw_legionella_unreachable`` exists to prevent,
        arriving by a different route — the cycle is not falling short of
        temperature, it is not being scheduled at all.

        Only ever a notice: the mode block is never released, here or
        anywhere else. Putting hot water back into the plan would promise
        water the hardware refuses to heat.
        """
        params = self._thermal_params
        due = self._dhw_legionella_due_in_hours()
        overdue_days: int | None = None
        if (
            dhw_blocked
            and bool(params.dhw_enabled)
            and bool(params.dhw_legionella_enabled)
            and due is not None
            and due < 0.0
        ):
            overdue_days = max(1, int(-due // 24.0) + 1)
        if overdue_days == self._legionella_mode_block_notice:
            return
        self._legionella_mode_block_notice = overdue_days
        if overdue_days is None:
            try:
                ir.async_delete_issue(
                    self.hass, DOMAIN, "dhw_legionella_mode_blocked"
                )
            except Exception as err:  # noqa: BLE001 - clearing is best-effort
                _LOGGER.debug(
                    "Could not clear legionella mode-block notice: %s", err
                )
            return
        _LOGGER.warning(
            "The anti-legionella cycle has been due for %d day(s) but the "
            "heat pump's mode makes no hot water, so it cannot be planned",
            overdue_days,
        )
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "dhw_legionella_mode_blocked",
            is_fixable=False,
            # Not persistent: it is derived from the live mode reading, so it
            # is re-raised on the next cycle for as long as the mode stands.
            severity=ir.IssueSeverity.WARNING,
            translation_key="dhw_legionella_mode_blocked",
            translation_placeholders={
                "overdue_days": f"{overdue_days:d}",
                "interval_days": f"{float(params.dhw_legionella_interval_days):.0f}",
            },
        )

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
        # #237: the handle ``async_shutdown`` cancels.
        self._refresh_task = asyncio.current_task()
        if self._skip_solve_once:
            # Consume the flag FIRST: no exception below may leave it
            # latched, or every later cycle would skip its solve too.
            self._skip_solve_once = False
            return await self._async_first_refresh_light()
        try:
            # Update current state from sensors
            await self._update_current_state()

            # Raises UpdateFailed on any failure -- see _fetch_tibber_prices.
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

            # #237: everything below writes to the world, and a plan cut
            # before a reload must not land on the instance that replaced us.
            if self._entry_released:
                _LOGGER.debug("Shutdown requested mid-cycle; not actuating")
                return self._build_data_dict()

            # Apply current action to heat pump
            await self._apply_action()

            # T7 #61 (control stage only): translate the commanded kW into
            # the frequency that delivers it. After _apply_action so a
            # failed write can never block the primary actuation, and
            # never allowed to break the cycle.
            try:
                await self._command_frequency()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Frequency command skipped: %s", err)

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

            # T4a #42: the learners' insurance — weekly snapshot, daily
            # bias check, and the rollback when drift proves itself on
            # healthy inputs. Never allowed to break the cycle.
            try:
                await self._async_watch_learning_drift()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Snapshot heartbeat skipped: %s", err)

            self._next_optimization = dt_util.now() + timedelta(
                minutes=self._config.get(
                    CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                )
            )

            return self._build_data_dict()

        except UpdateFailed:
            # #216 (D10-09): the raiser — the Tibber outage latch — already
            # logged this failure once, at the severity its state machine
            # chose (ERROR on the transition, DEBUG after). Re-logging it
            # here, with a traceback, on every poll defeated the latch: a
            # day-long outage printed the same ERROR on every cycle.
            raise
        except Exception as err:
            _LOGGER.error(
                "Error updating Heat Pump Optimizer: %s", err, exc_info=True
            )
            raise UpdateFailed(f"Error updating data: {err}") from err

    async def _async_first_refresh_light(self) -> dict[str, Any]:
        """The setup-time refresh: publish something valid without solving.

        Runs at most once per setup, when ``async_setup_entry`` set
        ``_skip_solve_once``. Two cases:

        * After an in-process reload the unload handler passed the previous
          plan through ``_reload_handover``; it is returned as-is, with no
          fetches at all — an options save must not wait on Tibber. The
          background refresh scheduled at the end of setup replaces it with
          a freshly solved plan within the first cycle.
        * On a genuinely fresh start there is nothing to hand over, so the
          cheap reads run — live sensor state, prices, weather — and the
          payload is built without a plan. Only the solve and its dependents
          (actuation, accuracy pairing, drift heartbeat) are skipped: none
          of them makes sense before a plan exists.
        """
        handover = self._reload_handover
        self._reload_handover = None
        if handover is not None:
            _LOGGER.debug(
                "First refresh republishes the pre-reload plan; the real "
                "solve follows in the background"
            )
            return handover

        try:
            await self._update_current_state()
            await self._fetch_tibber_prices()
            await self._fetch_weather_forecast()
            await self._fetch_solar_forecast()
            await self._async_learn_price_shape()
            _LOGGER.debug(
                "First refresh completed without a solve; the real solve "
                "follows in the background"
            )
            return self._build_data_dict()
        except UpdateFailed:
            # #216, same as _async_update_data's wrapper: this path also
            # runs _fetch_tibber_prices, whose latch has already logged the
            # failure once. An install whose first poll fails logs exactly
            # one ERROR, not two.
            raise
        except Exception as err:
            _LOGGER.error(
                "Error updating Heat Pump Optimizer: %s", err, exc_info=True
            )
            raise UpdateFailed(f"Error updating data: {err}") from err

    def _solve_snapshot(self) -> tuple[ThermalState, HeatPumpOptimizer]:
        """Frozen copies for the process worker: the solve must never share
        mutable state with the event loop (learners, the live peak guard and
        the climate entity all write mid-solve).

        The returned optimizer wraps its own ThermalModel over its own
        parameter copy, so the solve's per-step scratch (the buffer
        trajectory, the refused-heat carry) never lands on the live model the
        event loop's ``simulate_step`` callers are walking. Construction per
        solve is cheap — ``HeatPumpOptimizer.__init__`` only stores references
        and per-solve scratch. ``defrost_derate`` holds the learner object
        itself; deepcopying it is safe (the solve only reads it) and also
        freezes the derate table mid-solve, which is the point.
        """
        state = copy.deepcopy(self._current_state)
        params = copy.deepcopy(self._thermal_params)
        config = copy.deepcopy(self._opt_config)
        return state, HeatPumpOptimizer(ThermalModel(params), config)

    async def async_run_optimization(self) -> str | None:
        """Run the MPC optimization.

        Returns ``None`` when a solve ran to completion — or one was already
        in flight, which is the same outcome for whoever asked — and a short
        reason code (``"no_prices"``, ``"solve_failed"``) when it could not.
        The scheduled cycle ignores the answer, but the service handler
        cannot: its own body is fenced by the ``except Exception`` below, so
        an exception raised in here never reaches the caller. The status is
        the one channel through which the handler can learn the run did not
        happen and raise ``HomeAssistantError`` instead of reporting success
        (#294, action-exceptions).
        """
        _LOGGER.info("Running heat pump optimization (predictive MPC)")

        if self._optimization_running:
            _LOGGER.debug("An optimization is already in flight; skipping")
            return None

        self._optimization_running = True
        # Announce the flip: the Optimize Now button disables itself off this
        # flag, and without a listener update the change is invisible until
        # the next scheduled refresh — after the solve is already over.
        self.async_update_listeners()
        away_original: dict[str, float] | None = None
        try:
            # One clock reading for the whole solve. The snapped anchor and
            # the forecast grid must derive from the same instant: two
            # separate ``dt_util.now()`` calls straddling a quarter boundary
            # would shift every array one step against the plan's own
            # timestamps — silently, and only a few times a day.
            now = dt_util.now()
            solve_now = self._solve_anchor(now)
            horizon = self._forecast_arrays(now)
            prices = horizon.prices

            if len(prices) < 4:
                _LOGGER.warning(
                    "Not enough price data for optimization (got %d steps)",
                    len(prices),
                )
                return "no_prices"

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
            self._opt_config.cycling_cost = self._effective_cycling_cost()
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

            # #26 (gated): while a window is detected open, holding the
            # comfort floor heats the street. Applied inside the same
            # snapshot-and-unwind envelope as the away setback, so the
            # relaxation can never outlive the window.
            if self._vent_cusum.tripped and bool(
                self._config.get(
                    CONF_OPEN_WINDOW_RELAX_ENABLED,
                    DEFAULT_OPEN_WINDOW_RELAX_ENABLED,
                )
            ):
                self._opt_config.min_temp = max(
                    ECONOMY_ABSOLUTE_FLOOR,
                    self._opt_config.min_temp - OPEN_WINDOW_RELAX_C,
                )

            # T4b (#36 #53, gated): the learned solar aperture and internal
            # gains apply per solve, so a flag change takes effect on the
            # next run and never leaves a stale value behind when turned
            # off — 1.0 / None are the byte-inert defaults.
            aperture_on = bool(
                self._config.get(
                    CONF_SOLAR_APERTURE_LEARNING_ENABLED,
                    DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
                )
            )
            self._thermal_params.solar_aperture_scale = (
                float(self._solar_aperture["scale"])
                if aperture_on
                and self._solar_aperture["n"] >= SOLAR_APERTURE_MIN_SAMPLES
                else 1.0
            )
            gains_on = bool(
                self._config.get(
                    CONF_INTERNAL_GAINS_LEARNING_ENABLED,
                    DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
                )
            )
            self._thermal_params.internal_gains_profile = (
                list(self._internal_gains_profile)
                if gains_on and self._internal_gains_profile is not None
                else None
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
            # horizon this solve will use. ``solve_now`` is the quarter
            # anchor taken above, so the pins land on the same grid as the
            # price array and the timestamps the optimizer will publish.
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
            # #17 (gated): the learned capacity envelope composes through
            # the SAME channel as the fuse guard — elementwise minimum,
            # never a second cap mechanism.
            env_caps = self._capacity_caps(horizon.outdoor_temps)
            if env_caps is not None:
                caps_extra = (
                    env_caps
                    if caps_extra is None
                    else np.minimum(caps_extra, env_caps)
                )

            # T5 (#16 #54): the comfort floor's two gated adjustments;
            # None for both is the byte-inert default path. Evaluated here,
            # not inside the lambda — they read hass state, which belongs
            # on the event loop, not in the executor.
            margins = self._confidence_margins(len(horizon.prices))
            mold_floors = self._mold_floor_series(horizon.outdoor_temps)
            external_heat = self._external_heat_forecast(len(horizon.prices))
            # The mode gate, read on the event loop with everything else the
            # lambda closes over. A suppressed channel's comfort floor is
            # deliberately left UNMET rather than quietly relaxed: the plan
            # then shows the shortfall and labels the slots ``pump_mode``, so
            # the user can see that the mode selection is costing them
            # comfort. Silently widening the band would hide the one fact
            # worth surfacing.
            mode_blocked_space = self._pump_signals.space_blocked
            mode_blocked_dhw = self._pump_signals.dhw_blocked
            if mode_blocked_space or mode_blocked_dhw:
                _LOGGER.info(
                    "Heat pump reports mode %s: planning without %s for this "
                    "horizon",
                    self._pump_signals.mode.label,
                    " and ".join(
                        name
                        for name, blocked in (
                            ("space heating", mode_blocked_space),
                            ("hot water", mode_blocked_dhw),
                        )
                        if blocked
                    ),
                )
            self._check_legionella_mode_block(mode_blocked_dhw)
            # Taken here, after every pre-solve mutation above, so the copies
            # carry all of them into the process worker.
            solve_state, solve_optimizer = self._solve_snapshot()
            # Process pool: a thread still shares this interpreter's GIL.
            result = await _await_optimize(
                self.hass,
                solve_optimizer,
                solve_state,
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
                external_heat,
                horizon.price_sigma,
                caps_extra,
                # #21: the forecast humidity series, when it carries
                # data. None keeps the solve's inner loop free of dead
                # lookups.
                (
                    horizon.humidity
                    if horizon.humidity.size
                    and bool(np.any(np.isfinite(horizon.humidity)))
                    else None
                ),
                min_temp_margins=margins,
                min_temp_floors=mold_floors,
                # v5.3.0: never promise heat the pump's current mode
                # cannot deliver — symmetrically. A cooling or hot-water
                # mode suppresses space slots; a heating-only mode
                # suppresses hot-water slots. Both default False and the
                # capability defaults to "can do everything", so an
                # install with no mode entity plans exactly as before.
                space_blocked=mode_blocked_space,
                dhw_blocked=mode_blocked_dhw,
            )

            # #237: the executor await above is seconds wide, and an options
            # save inside it unloads the entry.
            if self._entry_released:
                _LOGGER.debug("Solve finished after shutdown; discarding it")
                return "shutdown"

            self._record_manual_release(result)

            self._optimization_result = result
            self._last_optimization = dt_util.now()
            if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT:
                ir.async_delete_issue(self.hass, DOMAIN, "solve_failures")
            self._solve_failures = 0
            # T5 #16: file this plan's promises at each lead bucket, to be
            # scored when their moment arrives. Anchored to the instant
            # the trajectory was built from, not to "after the solve".
            self._file_lead_predictions(result, solve_now)

            self._current_action = solve_optimizer.get_current_action(
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

            # T6 #39 (gated): one price tile per scheduled solve, and only
            # here — the tiles must never run on demand.
            try:
                await self._maybe_refresh_price_tile()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Price tile skipped: %s", err)

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
            return None

        except Exception as err:
            _LOGGER.error("Optimization failed: %s", err, exc_info=True)
            self._solve_failures += 1
            if self._solve_failures == SOLVE_FAILURE_ISSUE_COUNT:
                # Exactly-at, not at-or-above: the issue is idempotent to
                # re-create, but re-raising it every cycle would refresh
                # its timestamp and bury when the failures started.
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "solve_failures",
                    is_fixable=False,
                    # Persistent: the stale plan survives a restart (it is
                    # simply re-solved — or not), so the notice must too.
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="solve_failures",
                    translation_placeholders={
                        "count": str(self._solve_failures),
                        "last_success": (
                            self._last_optimization.isoformat(
                                sep=" ", timespec="minutes"
                            )
                            if self._last_optimization
                            else "—"
                        ),
                    },
                )
            return "solve_failed"
        finally:
            if away_original is not None:
                self._restore_away_setback(away_original)
            self._optimization_running = False
            self.async_update_listeners()

    async def async_set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        self._mode = mode
        if mode not in (MODE_AUTO, MODE_ECONOMY):
            # The plan stops being what runs, so its unmatured promises
            # (T5 #16) are void: scoring them against a room now driven by
            # fixed-rule comfort/boost/off would charge the model with
            # errors it never made. The tank's promises are void for the
            # same reason: comfort/boost/off charge it on their own rules.
            self._accuracy.lead_pending.clear()
            self._dhw_accuracy.lead_pending.clear()
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
            # the old one, so start over from "trust the configuration". The
            # save below records the anchor for the coefficient just applied,
            # so the restart pairs this reset with whatever the options carry
            # (issue #86: the old defect was the reset outliving an in-memory-
            # only coefficient change, leaving the next start 0.80x wrong).
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
                # Both structures from one parse (#3): the every-day view
                # and the weekly one can then never disagree about what
                # was configured, the same guarantee from_config gives.
                self._thermal_params.dhw_weekly_windows = parse_weekly_windows(
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

        # Attribute writes bypass __post_init__, so the thermal-mass divisor
        # floor is re-enforced here — the one chokepoint for service writes.
        self._thermal_params.clamp()

        # The model and optimizer hold the parameters by reference at
        # construction, so both are rebuilt rather than mutated in place.
        self._thermal_model = ThermalModel(self._thermal_params)
        self._optimizer = HeatPumpOptimizer(self._thermal_model, self._opt_config)

        _LOGGER.info("Thermal parameters updated, re-running optimization")
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator.

        The latch is set before anything is awaited, so every point that
        would command the pump or write a store declines from here on (#237).
        The in-flight refresh is then cancelled, which the base class does
        NOT do: it cancels the SCHEDULED timer and the debouncer, and a
        refresh already running is a task somebody else owns.

        The base class's shutdown still runs (D10-06): an override that skips
        it leaks the debouncer and the timer on every unload/reload. Then our
        own listeners go, via the same ``_release_registrations`` the entry's
        unload callbacks use so a failed setup cleans up too (#236), then any
        still-pending fire-and-forget tasks are awaited (a capped wait, so a
        wedged save cannot hang the unload).
        """
        refresh, self._refresh_task = self._refresh_task, None
        self._entry_released = True
        if refresh is not None and refresh is not asyncio.current_task():
            refresh.cancel()
        await super().async_shutdown()
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        self._release_registrations()
        pending = [t for t in self._background_tasks if not t.done()]
        if pending:
            _LOGGER.debug(
                "Shutdown awaiting %d background task(s)", len(pending)
            )
            done, still_pending = await asyncio.wait(pending, timeout=5.0)
            if still_pending:
                _LOGGER.warning(
                    "%d background task(s) did not finish within 5 s of "
                    "shutdown; they run on regardless",
                    len(still_pending),
                )
        self._background_tasks.clear()

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
        # A real thermometer beats every estimate and is the only source that
        # carries information about the lower zone at all. There used to be a
        # second-best branch here: the floor-return reading plus 0.5 K. That was
        # a *water* temperature standing in for an air temperature -- typically
        # 3-9 K too warm -- and because the slab is derived from the same sensor
        # as `return + 1.0`, the slab-to-room difference it produced was pinned
        # at a constant 0.5 K whatever the sensor read. So the main heat path
        # into the lower zone was both wrong and unresponsive, the error was
        # judged against the same comfort bounds as the upper floor, and the
        # number was published and plotted as a house temperature: an underfloor
        # return of 27.5 C in a cold snap drew a "house" trace at 28.0 C while
        # the upper zone sat at 22.1 C, which reads as the optimizer cooking the
        # house to a temperature nothing ever planned.
        #
        # The floor return keeps the job it is a genuine proxy for -- driving
        # the slab estimate through `update_slab_from_return_temp` above. With
        # no lower-floor thermometer the honest stand-in is the room
        # temperature, which is what the last-resort seed further down has
        # always used; a repair issue says so rather than letting a wrong
        # number pass for a measurement.
        lower_floor = reader.read(CONF_LOWER_FLOOR_TEMP_ENTITY)
        if lower_floor.ok:
            self._current_state.lower_floor_temperature = lower_floor.value
        elif floor_return.ok:
            self._current_state.lower_floor_temperature = (
                self._current_state.room_temperature
            )
        self._audit_lower_floor_sensor()
        self._audit_comfort_band()

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
        # #11: draw beyond what the compressor can pull means the immersion
        # element is running — a different appliance wearing the pump's meter.
        self._detect_immersion()
        # #2 (gated): the curve learner's daily comfort evidence.
        self._track_curve_comfort(dt_util.now())
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

        # The four heat-pump signals (v5.3.0). Read through the same reader
        # as everything else, so all four appear in this cycle's health with
        # their entity id and problem — a mode entity nobody can read is
        # *visible* in the diagnostics, it just does not act. Read before the
        # health snapshot is published because every learner below consults
        # ``_learning_frozen``, which now consults these.
        _mode_now = dt_util.now()
        _last_good_age = (
            (_mode_now - self._pump_mode_last_good_at).total_seconds() / 60.0
            if self._pump_mode_last_good_at is not None
            else None
        )
        self._pump_signals = pump_signals.read(
            reader,
            last_good=self._pump_mode_last_good,
            last_good_age_minutes=_last_good_age,
        )
        if self._pump_signals.mode_source == pump_signals.MODE_SOURCE_LIVE:
            self._pump_mode_last_good = self._pump_signals.mode
            self._pump_mode_last_good_at = _mode_now
        self._check_pump_mode_expired()
        # The flag's level, once per cycle. Complements the listener, which
        # only ever sees transitions.
        self._defrost_window.observe(
            dt_util.now(), self._pump_signals.defrosting
        )

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

        # Deliberately NOT gated on `dhw.ok`: the observer above is the only
        # reset path there was, and it cannot run without a tank reading —
        # while the countdown below advances on the clock regardless. That
        # asymmetry is the latch. This follows the boost the plan actually
        # commanded, so a cycle can complete even when the probe is absent
        # or the pump cannot reach the disinfection temperature.
        await self._async_track_dhw_legionella_cycle(
            dhw.value if dhw.ok else None
        )
        self._check_dhw_legionella_ceiling()

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
        # v5.3.0: the plant-wide freezes, from the heat pump's own signals.
        #
        # These have a shape the loop below cannot express, which is why they
        # are not folded into it. That loop asks "is the reading the caller
        # named unusable" — it freezes on the *absence* of a measurement. The
        # three conditions here freeze on the *presence* of one: the online
        # flag says False, the fault flag says True, the mode says cooling.
        # Every one of them is a perfectly healthy, perfectly fresh reading
        # that happens to be bad news, and every one of them makes the whole
        # interval misleading rather than one sensor unreadable — so they are
        # not scoped to the caller's keys either. See ``pump_signals.py`` for
        # why the absence of these signals never freezes anything.
        #
        # Ahead of the key loop because they are the root cause when both
        # fire: a pump that has dropped off the network explains its own
        # sensors going quiet, and reporting the symptom would send a user
        # looking at the wrong thing.
        if self._pump_signals.freeze_reason is not None:
            return self._pump_signals.freeze_reason
        # An unusable input outranks ventilation deliberately: the heat-loss
        # learner treats "ventilation" as a pass-through to keep feeding
        # the detector, and a flatline fed through that pass would
        # drive the very detector that froze everything. With the input
        # check first, the latch simply holds until real data returns.
        #
        # v5.1.3: this used to freeze only on ``stale``. Every other
        # unusable-input problem — ``unavailable``, ``missing_entity``,
        # ``not_numeric``, ``unknown_unit`` — left the learners running.
        # That mattered because ``_update_current_state`` deliberately PINS
        # the last good value when a read fails (there is no ``else`` on
        # those branches, by design: the planner is better off steering from
        # the last known room temperature than from nothing). Pinning is
        # right for the *input*; it is fatal for a *learner*, which then
        # reads a frozen number as thermal behaviour and persists the
        # result. A flat battery or a dropped Zigbee sensor walked the house
        # heat-loss scale from 1.0 to ~0.37 inside 48 h, saved every 10
        # samples, and the corruption outlived the sensor outage by weeks.
        # So: freeze on ANY unusable reading. The pinning in
        # ``_update_current_state`` is untouched and intentional — this
        # bounds only what the learners may do with a pinned value.
        #
        # ``reading.entity_id`` is the load-bearing half of the predicate: a
        # slot the user never configured reads as ``not_configured`` with no
        # entity, and must NOT freeze learning — otherwise every install
        # without an optional sensor would never learn anything.
        health = self._input_health
        if health is not None:
            for key in keys:
                reading = health.readings.get(key)
                if reading is not None and reading.entity_id and not reading.ok:
                    return f"{reading.problem}:{key}"
        # #26: training on an open window teaches a phantom heat loss the
        # house does not have — measured in °C-scale residuals, far above
        # any learning signal.
        if self._vent_cusum.tripped:
            return "ventilation"
        return None

    async def _fetch_tibber_prices(self) -> None:
        """Fetch electricity prices from Tibber API.

        A failed fetch raises :class:`UpdateFailed` (D10-07): the update
        cycle then reports failure through the coordinator base, which
        flips ``last_update_success`` and takes the entities unavailable --
        the honest signal that no fresh data arrived, instead of a silent
        eternity of stale prices behind a green integration. The outage is
        logged once (D10-09), not on every cycle; recovery logs the
        outage's length.
        """
        token = self._config.get(CONF_TIBBER_TOKEN)
        if not token:
            self._tibber_fetch_failed("No Tibber token configured")
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
            # Home Assistant's shared session — a fresh ClientSession per
            # update leaked a connection pool every cycle. Shared, so it is
            # never closed here. Resolved inside the try: environments
            # without an HTTP session (the test stub) degrade exactly as a
            # failed fetch does.
            session = async_get_clientsession(self.hass)
            async with session.post(
                TIBBER_API_URL,
                data=query_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status in (401, 403):
                    # The token itself was refused: a retry cannot fix it.
                    # Start the reauthentication flow (D10-08) so Repairs
                    # offers to fix the credential instead of the
                    # integration sitting unavailable until the entry is
                    # deleted and recreated.
                    self._tibber_start_reauth()
                    self._tibber_fetch_failed(
                        f"Tibber refused the token (HTTP {resp.status}); "
                        "reauthentication started"
                    )
                    return
                if resp.status != 200:
                    self._tibber_fetch_failed(f"Tibber API error: {resp.status}")
                    return
                data = await resp.json()

            if "errors" in data:
                self._tibber_fetch_failed(f"Tibber API errors: {data['errors']}")
                return

            homes = data.get("data", {}).get("viewer", {}).get("homes", [])
            if not homes:
                self._tibber_fetch_failed("No homes found in Tibber data")
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
            self._tibber_fetch_recovered()
            _LOGGER.debug("Fetched %d price entries from Tibber", len(prices))

        except UpdateFailed:
            # #216 (D10-09): _tibber_fetch_failed already latched, logged
            # and raised. Re-catching it here entered the latch a SECOND
            # time per poll (the count doubled; recovery reported twice the
            # outage's length). Let it propagate.
            raise
        except aiohttp.ClientError as err:
            self._tibber_fetch_failed(f"Error fetching Tibber prices: {err}")
        except Exception as err:
            self._tibber_fetch_failed(
                f"Unexpected error fetching prices: {err}", exc_info=True
            )

    def _tibber_fetch_failed(self, reason: str, *, exc_info: bool = False) -> None:
        """Record one failed price fetch: log once, raise as a failed update.

        D10-09: an outage lasting a day used to print the same ERROR on
        every cycle. The first failure logs ERROR; the rest log DEBUG until
        a fetch succeeds again, which logs the outage's length at INFO.
        """
        if not self._tibber_outage_cycles:
            _LOGGER.error("%s", reason, exc_info=exc_info)
        else:
            _LOGGER.debug("Tibber still failing (%s)", reason)
        self._tibber_outage_cycles += 1
        raise UpdateFailed(reason)

    def _tibber_fetch_recovered(self) -> None:
        """Clear the outage latch after a successful fetch."""
        if self._tibber_outage_cycles:
            _LOGGER.info(
                "Tibber prices recovered after %d failed cycle(s)",
                self._tibber_outage_cycles,
            )
        self._tibber_outage_cycles = 0
        # A later revocation of the (new) token deserves its own flow.
        self._tibber_reauth_started = False

    def _tibber_start_reauth(self) -> None:
        """Offer the reauthentication flow once per refused token (D10-08).

        Home Assistant raises the Repairs item and walks the user through
        replacing the credential; without it, a rotated or revoked token
        meant deleting and recreating the whole entry. Idempotent-guarded
        because a refused token fails every cycle until fixed: the flow
        is only started once per auth outage.
        """
        if self._tibber_reauth_started:
            return
        entry = getattr(self, "config_entry", None)
        if entry is None or not hasattr(entry, "async_start_reauth"):
            return
        self._tibber_reauth_started = True
        entry.async_start_reauth(self.hass)
        _LOGGER.warning(
            "Tibber refused the configured token; reauthentication is "
            "required (Home Assistant will offer it under Repairs)"
        )

    async def _fetch_weather_forecast(self) -> None:
        """Fetch full 24-hour weather forecast from Home Assistant weather entity.

        Extracts per-hour forecasts for:
        - Temperature (°C)
        - Wind speed (m/s)
        - Precipitation (mm/h)
        - Solar radiation / irradiance (W/m²)

        These FORECAST values (not current conditions) are what enable
        true predictive/anticipative control in the MPC optimizer.

        A failed or empty fetch is never silently papered over (M2): a
        48 h flat forecast fabricated from the current temperature read
        as real data and cost +41.9 % realized on the verification
        panel's cold-front scenario, and an empty result used to keep a
        stale forecast forever with no signal at all. Failures now mark
        the forecast stale (``_weather_stale_since``, published as
        ``weather_forecast_stale_hours``) and the outage logs once, not
        per cycle. The fabricated constant trajectory is only built when
        nothing better exists -- a first fetch failure with no prior
        forecast -- and it is stale from birth.
        """
        weather_entity = self._config.get(CONF_WEATHER_ENTITY)
        if not weather_entity:
            self._weather_fetch_failed("No weather entity configured")
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
                if forecast_data:
                    self._weather_forecast = forecast_data

                    # Extract solar radiation forecast if present in weather data
                    self._solar_radiation_forecast = []
                    for fc in forecast_data:
                        # Some weather integrations provide solar irradiance
                        sr = fc.get("solar_irradiance") or fc.get(
                            "native_solar_irradiance", 0.0
                        )
                        self._solar_radiation_forecast.append(float(sr or 0.0))

                    self._weather_fetch_recovered()
                    _LOGGER.debug(
                        "Fetched %d weather forecast entries (full 24h+ "
                        "trajectory: temp, wind, rain, solar)",
                        len(forecast_data),
                    )
                else:
                    # D8-02's half: an empty result used to keep the
                    # previous forecast forever with no signal. The
                    # previous forecast is still the best data -- but it
                    # is stale data now, and the plan built on it says so.
                    self._weather_fetch_failed(
                        f"Empty forecast returned for {weather_entity}"
                    )
            else:
                self._weather_fetch_failed(
                    f"No forecast data returned for {weather_entity}"
                )

        except Exception as err:
            self._weather_fetch_failed(f"Error fetching weather forecast: {err}")
            state = self.hass.states.get(weather_entity)
            if state and not self._weather_forecast:
                # Nothing better exists: fabricate the constant trajectory,
                # already marked stale by the failure above -- a plan built
                # on it discloses what it is standing on.
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

    def _weather_fetch_failed(self, reason: str) -> None:
        """Latch one failed weather fetch: log once, mark the data stale."""
        if not self._weather_outage_cycles:
            _LOGGER.warning(
                "%s. Plans continue on the last forecast, marked stale.", reason
            )
        else:
            _LOGGER.debug("Weather forecast still failing (%s)", reason)
        self._weather_outage_cycles += 1
        if self._weather_stale_since is None:
            self._weather_stale_since = dt_util.now()

    def _weather_fetch_recovered(self) -> None:
        """Clear the outage and the staleness after a successful fetch."""
        if self._weather_outage_cycles:
            _LOGGER.info(
                "Weather forecast recovered after %d failed cycle(s)",
                self._weather_outage_cycles,
            )
        self._weather_outage_cycles = 0
        self._weather_stale_since = None

    def weather_stale_hours(self) -> float | None:
        """How long the forecast has been stale, in hours; None when fresh.

        Published in the data dict so the card, sensors and diagnostics
        can disclose it -- the whole point of M2 is that a plan built on
        stale weather must be able to say so.
        """
        if self._weather_stale_since is None:
            return None
        return round(
            (dt_util.now() - self._weather_stale_since).total_seconds() / 3600.0,
            1,
        )


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

        step_starts = _utc_step_starts(midnight, n_steps, step_offset)

        # Align by each entry's own timestamp, not by its position. Position
        # assumed the first entry is *today's* midnight, which breaks two real
        # ways: a stale list (fetch failing since yesterday) shifts the whole
        # horizon a day, and quarter-hour entries — Tibber's 15-minute pricing
        # — would each be stretched to a full hour. An entry covers from its
        # start to the next entry's start; the last covers its predecessor's
        # span. The known series stops at the first step no entry covers, and
        # the learned prior fills the rest below.
        known = self._known_prices_for(step_starts)
        if not known:  # #239: empty known == empty list
            _LOGGER.warning("No published prices cover the planning horizon; skipping")
            return None

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

    def _known_prices_for(self, step_starts: list[datetime]) -> list[float]:
        """Published prices covering a leading run of the step grid."""
        if not step_starts:
            return []
        entries: list[tuple[datetime, float]] = []
        for entry in self._prices:
            ts = _comparable_ts(entry.get("starts_at"), step_starts[0])
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
    ) -> tuple[
        list[float], list[float], list[float], list[float], list[float]
    ]:
        """Per-step outdoor temperature, wind, precipitation, irradiance
        and relative humidity (NaN where the entry offers none, #21).

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
                [float("nan")] * n_steps,
            )

        # Convert using the unit the weather entity actually reports in.
        # Guessing from the magnitude misreads a moderate 20 km/h breeze as a
        # 20 m/s storm and doubles the predicted heat loss.
        wind_scale = self._wind_speed_scale()
        step_starts = _utc_step_starts(midnight, n_steps, step_offset)

        parsed: list[
            tuple[datetime | None, tuple[float, float, float, float, float]]
        ] = []
        for idx, entry in enumerate(self._weather_forecast):
            temp = _as_float(entry.get("temperature"), 5.0)
            gust = max(0.0, _as_float(entry.get("wind_speed"), 0.0) * wind_scale)
            rain = max(0.0, _as_float(entry.get("precipitation"), 0.0))
            # NaN, not a guess: the model reads NaN as "use the ambient
            # value", while any invented number would select a real
            # defrost bucket (#21).
            rh = _as_float(entry.get("humidity"), float("nan"))

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
                _comparable_ts(entry.get("datetime"), step_starts[0])
                if step_starts
                else None
            )
            parsed.append((ts, (temp, gust, rain, irradiance, rh)))

        timed = sorted(
            (item for item in parsed if item[0] is not None),
            key=lambda item: item[0],
        )
        outdoor: list[float] = []
        wind: list[float] = []
        precipitation: list[float] = []
        solar: list[float] = []
        humidity: list[float] = []

        if timed:
            starts = [ts for ts, _ in timed]
            for step_start in step_starts:
                # Each entry holds until the next one begins; before the first
                # entry the first is the best information there is, and past
                # the last the caller pads flat anyway.
                idx = max(0, bisect_right(starts, step_start) - 1)
                temp, gust, rain, irradiance, rh = timed[idx][1]
                outdoor.append(temp)
                wind.append(gust)
                precipitation.append(rain)
                solar.append(irradiance)
                humidity.append(rh)
        else:
            # No timestamps at all: the old positional assumption, hourly
            # entries starting now.
            for _, (temp, gust, rain, irradiance, rh) in parsed:
                for _ in range(4):
                    outdoor.append(temp)
                    wind.append(gust)
                    precipitation.append(rain)
                    solar.append(irradiance)
                    humidity.append(rh)

        return outdoor, wind, precipitation, solar, humidity

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
        for i, step_start in enumerate(
            _utc_step_starts(midnight, n_steps, step_offset)
        ):
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

    def _solve_anchor(self, now: datetime) -> datetime:
        """``now`` floored onto the grid the forecast arrays are built on.

        ``_forecast_arrays`` anchors every price and weather step at
        ``midnight + FORECAST_STEP_MINUTES·k``, so a solve labelled with the
        raw instant (12:07) published timestamps seven minutes off the
        quarter its own arrays described — and pins, capacity-window
        offsets, filed lead promises and every card timestamp inherited
        that skew. The granularity is the forecast grid's, deliberately not
        ``time_step_minutes``: if the two ever diverge the arrays disagree
        first, and the anchor must follow the arrays. Wall-clock lookups
        INTO the plan (``get_current_action``, ``_async_drive_pumps``) stay
        on the raw clock — they ask what applies now, not where step 0 is.
        """
        step = int(FORECAST_STEP_MINUTES)
        return now.replace(
            minute=(now.minute // step) * step, second=0, microsecond=0
        )

    def _forecast_arrays(self, now: datetime | None = None) -> ForecastArrays:
        """Everything the optimizer needs to know about the horizon.

        Assembled in one place because the pieces depend on each other: the PV
        surplus is derived from the irradiance series the weather assembly
        produced. Computing them elsewhere is how they would drift apart.

        ``now`` is accepted from the caller so the solve anchor and this
        grid come from one clock reading; left ``None`` for consumers with
        no anchor of their own (the plain forecast property).
        """
        n_steps = self._opt_config.n_steps
        if now is None:
            now = dt_util.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        step_offset = int(
            (now - midnight).total_seconds() / 60 / FORECAST_STEP_MINUTES
        )

        priced = self._price_series(n_steps, midnight, step_offset)
        if priced is None:
            return ForecastArrays.empty()
        prices, price_known, price_sigma = priced

        outdoor, wind, precipitation, solar, humidity = self._weather_series(
            n_steps, midnight, step_offset
        )
        solar = self._apply_open_meteo(solar, n_steps, midnight, step_offset)

        # A forecast shorter than the horizon is held flat at its last value.
        for series in (outdoor, wind, precipitation, solar, humidity):
            while len(series) < n_steps:
                series.append(series[-1] if series else 0.0)

        # Open-Meteo's hourly humidity and snowfall overlay the weather
        # entity by wall-clock time, exactly like the irradiance above.
        # Humidity keeps the entity's value where Open-Meteo has none;
        # snowfall has no entity fallback — no data reads as no snow.
        snowfall = [0.0] * n_steps
        if self._open_meteo is not None and self._open_meteo.available:
            step = timedelta(minutes=FORECAST_STEP_MINUTES)
            for i, step_start in enumerate(
                _utc_step_starts(midnight, n_steps, step_offset)
            ):
                rh = self._open_meteo.humidity_for(step_start, step)
                if rh is not None:
                    humidity[i] = float(np.clip(rh, 0.0, 100.0))
                snow = self._open_meteo.snowfall_for(step_start, step)
                if snow is not None:
                    snowfall[i] = max(0.0, float(snow))

        precip_array = np.array(precipitation[:n_steps], dtype=float)
        snow_array = np.array(snowfall[:n_steps], dtype=float)
        # #30 (gated): weight the rain heat-loss effect by the liquid
        # fraction — snow does not wet the building envelope. The array the
        # optimizer sees is what carries the physics, so with the flag off
        # it is byte-for-byte the raw precipitation.
        if bool(
            self._config.get(CONF_PRECIP_TYPE_ENABLED, DEFAULT_PRECIP_TYPE_ENABLED)
        ) and np.any(snow_array > 0.0):
            precip_array = precip_array * self._liquid_fraction(
                precip_array, snow_array
            )

        solar_list = solar[:n_steps]
        # #30 (gated): a roof under fresh snow admits far less sun. Crude by
        # design — a factor and a holding period, not a melt model.
        if self._update_snow_memory(now, snow_array):
            solar_list = [s * SNOW_ROOF_DAMPING for s in solar_list]

        solar_array = np.array(solar_list, dtype=float)
        surplus = self._pv_surplus_series(solar_array, n_steps)

        return ForecastArrays(
            prices=prices,
            outdoor_temps=np.array(outdoor[:n_steps], dtype=float),
            wind_speeds=np.array(wind[:n_steps], dtype=float),
            precipitation=precip_array,
            solar_radiation=solar_array,
            price_known=price_known,
            pv_surplus=surplus,
            price_sigma=price_sigma,
            humidity=np.array(humidity[:n_steps], dtype=float),
            snowfall=snow_array,
        )

    @staticmethod
    def _liquid_fraction(
        precip_array: np.ndarray, snow_array: np.ndarray
    ) -> np.ndarray:
        """#30's split: what share of each step's precipitation is rain.

        Open-Meteo's ``precipitation`` already includes the snowfall's
        water equivalent (cm × 1/0.7 mm), so subtracting it leaves the
        liquid share; the clip absorbs cross-source disagreement (entity
        rain vs Open-Meteo snow) and a dry step is defined as fully
        liquid so it multiplies to zero either way.
        """
        snow_water = np.asarray(snow_array, dtype=float) / SNOW_CM_PER_MM_WATER
        precip = np.asarray(precip_array, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(
                precip > 1e-9,
                np.clip((precip - snow_water) / precip, 0.0, 1.0),
                1.0,
            )

    def _update_snow_memory(self, now: datetime, snow_array: np.ndarray) -> bool:
        """#30's roof-snow bookkeeping; True while solar should be damped.

        A 24-hour decaying accumulator of the current snowfall rate trips
        the "roof snowed over" assumption at SNOW_HEAVY_CM, which then
        holds for SNOW_ROOF_DAYS. Entirely inert — no state is touched —
        while the flag is off.
        """
        if not bool(
            self._config.get(
                CONF_SNOW_ROOF_FACTOR_ENABLED, DEFAULT_SNOW_ROOF_FACTOR_ENABLED
            )
        ):
            return False
        rate_now = float(snow_array[0]) if snow_array.size else 0.0
        last = self._snow_accum_last
        if last is not None:
            dt_true = max(0.0, (now - last).total_seconds() / 3600.0)
            # Decay over the FULL gap — clamping it would keep two-day-old
            # snow "fresh" forever — but credit new fall only for a bounded
            # window, so a long outage cannot book a blizzard from one rate
            # sample.
            self._snow_accum_cm *= math.exp(-dt_true / 24.0)
            self._snow_accum_cm += rate_now * min(dt_true, 6.0)
        self._snow_accum_last = now
        if self._snow_accum_cm >= SNOW_HEAVY_CM:
            self._last_heavy_snow = now
        if self._last_heavy_snow is None:
            return False
        return (now - self._last_heavy_snow).total_seconds() < (
            SNOW_ROOF_DAYS * 86400.0
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
        schedule = self._grid_fee_schedule()
        entity_value = self._grid_fee_entity_value()
        self._audit_grid_fee(schedule, entity_value)
        return schedule.fee_vector(step_starts, entity_value)

    def _audit_grid_fee(
        self, schedule: GridFeeSchedule, entity_value: float | None
    ) -> None:
        """Warn-only magnitude check on the fee layer, per planning cycle.

        A fee rate above ``IMPLAUSIBLE_FEE_SEK_PER_KWH`` is öre typed into a
        SEK field (25 for 0.25 — the 100× slip), whether it arrived through
        the rules text, the fixed component, a hand-edited store, or a
        sensor publishing öre. The plan keeps running on exactly what was
        configured — mutating or suppressing the value here would make the
        planning prices silently diverge from what the user typed and from
        the settlement paths reading the same schedule — so the only output
        is a repair issue, raised once per offending value and cleared as
        soon as the configured fees are plausible again.

        The sign gets the same treatment (audit D4-05, #169). The config
        flow refuses a negative rule since that audit, but a store written
        before it did, a hand-edited one, or a fee sensor publishing a
        negative value still reaches the plan -- as a subsidy on exactly the
        hours the grid company charges for. Both notices name the instance
        currency (audit D4-04, #168) rather than assuming one.
        """
        worst, source = grid_fee_max_abs_component(schedule, entity_value)
        if worst > IMPLAUSIBLE_FEE_SEK_PER_KWH:
            if self._grid_fee_issue_value != worst:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "grid_fee_magnitude",
                    is_fixable=False,
                    # Persistent: the configuration survives a restart
                    # unchanged, so the notice must too.
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="grid_fee_magnitude",
                    translation_placeholders={
                        "rate": f"{worst:.2f}",
                        "source": source,
                        "currency": self.currency,
                    },
                )
                self._grid_fee_issue_value = worst
        else:
            # Unconditional for the reason spelled out in
            # `_audit_lower_floor_sensor`: correcting the fee writes options,
            # which reloads the entry, which resets this flag to None -- so
            # gating the delete on it left a corrected installation showing a
            # persistent warning about a value it no longer has.
            ir.async_delete_issue(self.hass, DOMAIN, "grid_fee_magnitude")
            self._grid_fee_issue_value = None

        lowest, sign_source = grid_fee_min_component(schedule, entity_value)
        if lowest < 0.0:
            if self._grid_fee_sign_issue_value != lowest:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "grid_fee_sign",
                    is_fixable=False,
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="grid_fee_sign",
                    translation_placeholders={
                        "rate": f"{lowest:.2f}",
                        "source": sign_source,
                        "currency": self.currency,
                    },
                )
                self._grid_fee_sign_issue_value = lowest
        else:
            ir.async_delete_issue(self.hass, DOMAIN, "grid_fee_sign")
            self._grid_fee_sign_issue_value = None

    def _audit_lower_floor_sensor(self) -> None:
        """Tell the user when the lower zone's temperature is not measured.

        Two-zone planning judges the lower zone against the same comfort
        bounds as the upper one, so its temperature is an input the plan acts
        on. Without ``lower_floor_temp_entity`` there is nothing to read and
        the room sensor stands in for the whole downstairs — good enough to
        plan from, but not a measurement, and the published trace says
        "lower floor" either way. Say so once, rather than letting an
        estimate pass for a reading.

        Silent unless two-zone is actually running: a single-zone house has no
        lower zone to measure, and the field is not even shown to it.
        """
        wanted = bool(
            self._thermal_params.two_zone_enabled
            and not self._config.get(CONF_LOWER_FLOOR_TEMP_ENTITY)
        )
        if wanted:
            if not self._lower_floor_issue_raised:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "lower_floor_modelled",
                    is_fixable=False,
                    # Persistent: the missing sensor survives a restart, so
                    # the notice must too.
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="lower_floor_modelled",
                )
                self._lower_floor_issue_raised = True
        else:
            # UNCONDITIONAL, and that is the whole point. Assigning the sensor
            # writes options, which reloads the entry, which builds a NEW
            # coordinator whose flag starts at False -- so a delete gated on
            # the flag can never run, and an `is_persistent` issue that says
            # "this notice clears when you do" would stay up forever. The
            # in-memory flag can only ever suppress a repeated CREATE; it must
            # never guard the clear. (`freq_watchdog` deletes unconditionally
            # for exactly this reason; `_audit_grid_fee` did not, and had the
            # same defect until v5.1.7.) Deleting an issue that is not there
            # is a no-op.
            ir.async_delete_issue(self.hass, DOMAIN, "lower_floor_modelled")
            self._lower_floor_issue_raised = False

    def _audit_comfort_band(self) -> None:
        """Say so when the STORED comfort band contradicts itself.

        Every write path now runs the band's rules, so a contradiction can no
        longer be created (v5.1.7). One can still be inherited: until this
        release the thermostat's slider ran to ``max_temp + 1`` and persisted
        whatever it was given, so a single tap on its top notch stored a target
        one degree above the ceiling, and nothing said a word.

        Reported rather than migrated. These are the user's own numbers and
        only they know which one is wrong -- silently rewriting a comfort
        target to make an inequality hold is exactly the kind of help nobody
        asked for. The plan keeps running meanwhile: the bounds are priced
        rather than fenced, so a contradictory band is a plan in permanent
        violation, not a crash.
        """
        found = comfort_band.violations({}, self._config)
        if found:
            problem = comfort_band.describe(found)
            if self._band_issue_problem != problem:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "comfort_band_contradiction",
                    is_fixable=False,
                    # Persistent: stored configuration survives a restart.
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="comfort_band_contradiction",
                    translation_placeholders={"problem": problem},
                )
                self._band_issue_problem = problem
        else:
            # Unconditional, like the two audits above: correcting the band
            # reloads the entry and resets this flag, so a guarded delete
            # could never fire.
            ir.async_delete_issue(
                self.hass, DOMAIN, "comfort_band_contradiction"
            )
            self._band_issue_problem = None

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
        # #2 (gated): the standing learned curve bias joins after every
        # guard has had its say and before the configured displace clamp —
        # exactly where a user correcting an over-hot installer curve by
        # hand would apply it. Never positive: the bias may only cool.
        if bool(
            self._config.get(
                CONF_CURVE_LEARNING_ENABLED, DEFAULT_CURVE_LEARNING_ENABLED
            )
        ):
            displace_value = displace_value + self._curve_learner.bias
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

        Commands the plan's target (static target or comfort ceiling), never
        the read-back entity, so a changed comfort band still reaches it.
        Skipped when unchanged by less than ``MIXING_VALVE_WRITE_EPSILON``
        (avoids flash wear on every cycle); write failures are logged and
        swallowed so a balky valve never breaks planning.
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
        kind = self._config.get(CONF_MIXING_VALVE_WRITE_TARGET_KIND)
        if kind not in mixing_valve.WRITE_TARGET_KINDS:  # #398: caught, not trusted
            kind = DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND
        if kind == mixing_valve.WRITE_TARGET_FLOW:
            if not params.two_zone_enabled:
                _LOGGER.error("mixing_valve_write_target_kind=flow needs two-zone")
                return
            outdoor = self._current_state.outdoor_temperature
            target = self._thermal_model.flow_target_for_indoor(target, outdoor)
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

    def _plan_age_minutes(self) -> float | None:
        """Minutes since the last successful solve; None before the first."""
        if self._last_optimization is None:
            return None
        return max(
            0.0,
            (dt_util.now() - self._last_optimization).total_seconds() / 60.0,
        )

    def _plan_is_stale(self) -> bool:
        """True when the plan is older than three solve cycles (min 90 min)."""
        age = self._plan_age_minutes()
        if age is None:
            return False
        interval = float(
            self._config.get(
                CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
            )
        )
        return age > max(PLAN_STALE_INTERVALS * interval, PLAN_STALE_FLOOR_MINUTES)

    async def _apply_action(self) -> None:
        """Apply current action as (heat_pump_on, displace_value)."""
        if not self._current_action:
            return
        if self._mode in (MODE_AUTO, MODE_ECONOMY) and self._plan_is_stale():
            # The action was cut from a plan whose horizon has slid out from
            # under it — its "cheap hour" may be the current peak. Stop
            # actuating, exactly as when no plan exists: the pump's own
            # weather-compensated curve holds comfort until a solve succeeds.
            # Fixed-rule modes (comfort/boost/off) carry no horizon and are
            # unaffected.
            _LOGGER.warning(
                "Plan is %.0f minutes old after %d failed solves; holding "
                "comfort on the pump's own curve instead of actuating it",
                self._plan_age_minutes() or 0.0,
                self._solve_failures,
            )
            return

        heat_pump_on = bool(self._current_action.get("heat_pump_on", False))

        # 1) Toggle heat pump supply (ON/OFF)
        #
        # Skip OFF only when cooling or both channels are blocked. A
        # single-channel heat block (DHW-only, heating-only) still
        # commands OFF on an empty plan — otherwise a summer DHW pulse
        # leaves the supply latched while the tank is supposed to drift.
        both_blocked = (
            self._pump_signals.space_blocked and self._pump_signals.dhw_blocked
        )
        skip_off = (not heat_pump_on) and (
            both_blocked or self._pump_signals.mode.cooling
        )
        switch_entity = self._config.get(CONF_HEAT_PUMP_SWITCH_ENTITY)
        if switch_entity and not skip_off:
            try:
                await self.hass.services.async_call(
                    "switch",
                    "turn_on" if heat_pump_on else "turn_off",
                    {"entity_id": switch_entity},
                    blocking=True,
                )
            except Exception as err:
                _LOGGER.error("Error toggling heat pump switch: %s", err)
        elif switch_entity:
            _LOGGER.debug(
                "Not switching %s off: mode %s is cooling or blocks both "
                "channels, so an empty plan is this integration's doing "
                "rather than a decision to stop the pump",
                switch_entity,
                self._pump_signals.mode.label,
            )

        # 2) Publish ECL110 displace command
        await self.async_publish_current_action(reason="scheduled_update")
    # ------------------------------------------------------------------
    # Published state
    # ------------------------------------------------------------------
    #
    # ``_build_data_dict`` composes these. Each returns one domain, so a new
    # field is added next to its siblings rather than appended to a
    # two-hundred-line literal where nothing has a natural home.

    def _reading_ok(self, key: str) -> bool:
        """Whether ``key``'s configured entity produced a usable value.

        ``False`` for an unconfigured entity as well as for a stale, missing
        or non-numeric one, because all three publish the same thing: the
        thermal model's constructor default or its last seed, never a
        measurement. The entities gate on this so a default cannot be read as
        a reading.
        """
        health = self._input_health
        if health is None:
            return False
        reading = health.readings.get(key)
        return bool(reading is not None and reading.entity_id and reading.ok)

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
            # Which of the temperatures above stand on a reading that
            # actually came in this cycle; see READING_SOURCES.
            "reading_ok": {
                field: self._reading_ok(entity)
                for field, entity in READING_SOURCES.items()
            },
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
            # Reports learned=True and an effective figure that the defect
            # noted at _thermal_learning_payload can leave ~2x wrong after an
            # options edit. The confidence shown here is in the sample count,
            # not in the number. See docs/backlog.md, "Open".
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
            # v5.3.0: how much of the derate rests on counted defrost time
            # rather than on the power-ratio inference, and — because a duty
            # counted from three-minute cloud polls misses short defrosts and
            # is therefore biased LOW — whether this install can measure it at
            # full resolution at all.
            "defrost_measured_samples": self._defrost.measured_samples,
            "defrost_flag_configured": bool(
                self._config.get(CONF_HEAT_PUMP_DEFROST_ENTITY)
            ),
            "defrost_store_migrated": self._defrost.migrated,
            "defrost_buckets": self._defrost.summary(),
            "comfort_weight": self._opt_config.comfort_weight,
            "comfort_learning": self._comfort_learner.summary(),
            "system_identification": self._sysid.as_dict(),
            "accuracy": self._accuracy.summary(),
            # v5.3.0: the four heat-pump signals, resolved. Published
            # unconditionally — an install with none of them configured shows
            # "Unknown"/absent, which is itself the answer to "why is nothing
            # being suppressed".
            "heat_pump_signals": self._pump_signals.as_dict(),
            # T4a: the detectors and the insurance, all additive.
            "ventilation_active": self._vent_cusum.tripped,
            "ventilation_evidence": list(self._vent_cusum.evidence),
            "immersion_active": self._immersion_active,
            "immersion_evidence": list(self._immersion_evidence),
            "cop_health": {
                "watched_buckets": sum(
                    1
                    for entry in self._cop_baseline.values()
                    if int(entry[1]) >= COP_BASELINE_MIN_SAMPLES
                ),
                "alarm": self._cop_health_cusum.tripped,
                "evidence": list(self._cop_health_cusum.evidence),
            },
            # T4b learners, all additive. Published even while gated off
            # (they read as empty/inert) so a user weighing the flags can
            # see what the learners would say.
            "capacity_envelope": {
                "buckets": {
                    str(k * 3): [round(float(v[0]), 2), int(v[1])]
                    for k, v in self._capacity_envelope.items()
                },
            },
            "solar_aperture": {
                "scale": round(float(self._solar_aperture["scale"]), 3),
                "samples": int(self._solar_aperture["n"]),
            },
            "internal_gains_profile": (
                [round(float(g), 3) for g in self._internal_gains_profile]
                if self._internal_gains_profile is not None
                else None
            ),
            "heat_curve": self._curve_learner.summary(),
            "snapshots": {
                "count": len(self._snapshot_ring.snapshots),
                "alarm": self._snapshot_ring.alarmed,
                "last_taken": (
                    self._snapshot_ring.snapshots[-1].get("taken_at")
                    if self._snapshot_ring.snapshots
                    else None
                ),
            },
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
        forecast = self._weather_forecast
        return {
            "current_price": self._get_current_price(),
            "prices_available": len(self._prices),
            "weather_forecast_available": len(forecast),
            # The outdoor temperature the horizon starts on, beside the
            # count of the forecast it comes from: what the plan is priced
            # against, where `outdoor_temperature` without a thermometer is
            # the constructor default (#282).
            "outdoor_forecast_temperature": forecast_outdoor_now(
                forecast, dt_util.now()
            ),
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

    def configured_dhw_windows(self) -> str:
        """The hot-water windows as CONFIGURED, in the grammar the config flow
        and `apply_schedule` accept: the weekly form when the configuration
        names days ("weekdays 06:00-08:30, weekend 08:00-09:30"), the flat
        form otherwise, and "" when none are configured.

        Distinct from the plan sensor's `dhw_windows`, which is what the last
        solve planned against -- learned windows when nothing is configured,
        and one day's set of a weekly spec. The card's schedule editor edits
        the configuration, so it needs the configuration, not the plan's
        reading of it; before this the editor could neither show a weekly
        schedule nor save one without flattening it.
        """
        params = self._thermal_params
        weekly = params.dhw_weekly_windows
        if weekly is not None:
            return format_weekly_windows(weekly)
        return format_windows(params.dhw_windows)

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
            # Staleness is judged where the data is read, not only where the
            # solve fails: a dashboard acting on `current_action` needs the
            # same "this plan is old" signal the actuator uses.
            "plan_age_minutes": (
                round(age, 1)
                if (age := self._plan_age_minutes()) is not None
                else None
            ),
            "plan_stale": self._plan_is_stale(),
            # M2: the same honesty for the weather the plan was built on.
            # None when the forecast is fresh; hours since the last
            # successful fetch when every fetch since has failed or come
            # back empty.
            "weather_forecast_stale_hours": self.weather_stale_hours(),
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
        # The date the lifetime accumulators started: a number that answers
        # to no stated period reads as "very high", and this is the since.
        if self._energy_totals_since is None:
            self._energy_totals_since = dt_util.now().date().isoformat()
        data["energy_totals_counting_since"] = self._energy_totals_since
        # Which of the battery's stores stand on a thermometer. Labelled
        # here rather than inside the view because this is where the
        # reading map is already assembled (#282).
        data["battery"] = battery_view.label_measured(
            self._battery_view(), data.get("reading_ok") or {}
        )
        # T6: narrative, scores, starts, receipts, tiles and the last
        # diagnosis — one additive block, present even while everything in
        # it is gated off (it reads as empty/inert).
        data["insight"] = self._insight_view()
        # T7 #61: the frequency stage, map and recommendation — additive,
        # "unconfigured" and empty without the entity.
        data["freq_control"] = self._freq_view()
        # v4.1.0: the unit every monetary figure above is denominated in,
        # published so the card never has to guess it from a sensor's unit
        # string.
        data["currency"] = self.currency

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
                    result.timestamps,
                    result.dhw_power_schedule,
                    result.dhw_temp_trajectory[1:] if result.dhw_temp_trajectory else [0.0] * len(result.timestamps),
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
                            result.timestamps,
                            result.power_schedule,
                            result.optimal_setpoints,
                            result.prices,
                            result.room_temp_trajectory[1:],
                            (
                                result.upper_temp_trajectory[1:]
                                if result.upper_temp_trajectory
                                else result.room_temp_trajectory[1:]
                            ),
                            (
                                result.lower_temp_trajectory[1:]
                                if result.lower_temp_trajectory
                                else result.room_temp_trajectory[1:]
                            ),
                            (
                                result.solar_gain_trajectory
                                if result.solar_gain_trajectory
                                else [0.0] * len(result.timestamps)
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
        if not isinstance(stored, dict):
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
        if not isinstance(stored, dict):
            return
        self._ledger = MonthlyLedger.from_dict(stored.get("ledger"))
        # T6, all additive on the same payload: absent keys on a pre-T6
        # store load as inert defaults.
        self._start_counter = StartCounter.from_dict(stored.get("starts"))
        reports = stored.get("month_reports")
        if isinstance(reports, dict):
            self._month_reports = {
                str(key): value
                for key, value in reports.items()
                if isinstance(value, dict)
            }
        day = stored.get("score_day")
        if isinstance(day, dict):
            # Same corruption barrier as the other riders: a book with a
            # non-numeric field would raise inside every subsequent
            # settlement and take the WHOLE update loop down for the rest
            # of the day. A day book is one day of evidence — dropping a
            # corrupt one costs one operation sample, never the loop.
            try:
                cleaned = {
                    "day": str(day.get("day") or ""),
                    "kwh": float(day.get("kwh", 0.0)),
                    "sek": float(day.get("sek", 0.0)),
                    "spot_sum": float(day.get("spot_sum", 0.0)),
                    "spot_h": float(day.get("spot_h", 0.0)),
                }
                if cleaned["day"] and all(
                    np.isfinite(v)
                    for k, v in cleaned.items()
                    if k != "day"
                ):
                    self._score_day = cleaned
            except (TypeError, ValueError, OverflowError):
                pass
        score = stored.get("operation_score")
        if isinstance(score, (int, float)) and np.isfinite(score):
            self._operation_score = float(np.clip(score, 0.0, 100.0))

    def _schedule_ledger_save(self) -> None:
        """Persist the ledger without blocking the settlement path."""
        self._spawn(self._async_save_ledger())

    async def _async_save_ledger(self) -> None:
        try:
            await self._ledger_store.async_save(
                {
                    "ledger": self._ledger.as_dict(),
                    # T6 riders — one store, one generation of money state.
                    "starts": self._start_counter.as_dict(),
                    "month_reports": self._month_reports,
                    "score_day": self._score_day,
                    "operation_score": self._operation_score,
                }
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist ledger: %s", err)

    async def _async_load_accuracy(self) -> None:
        try:
            stored = await self._accuracy_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load accuracy history: %s", err)
            return
        if not isinstance(stored, dict):
            return
        self._accuracy = AccuracyTracker.from_dict(stored.get("accuracy"))
        # v5.2.0, additive key. A store written by an older build has no
        # "dhw_accuracy"; `from_dict(None)` answers an empty tracker and the
        # band simply stays absent until the record fills. In the other
        # direction an older build ignores a key it never reads, so a
        # downgrade loads this store without error too.
        self._dhw_accuracy = AccuracyTracker.from_dict(
            stored.get("dhw_accuracy")
        )
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

    async def _async_save_if_changed(
        self, name: str, store: Store, payload: dict[str, Any]
    ) -> None:
        """Write ``payload`` unless the store already holds exactly it.

        Both callers run every update cycle, and most cycles change nothing —
        an unconditional rewrite is pure disk wear on the Pi-class hardware
        Home Assistant usually lives on. The digest is remembered only after
        the store accepted the payload, so a failed save is retried on the
        next cycle rather than skipped as already-written.
        """
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        if self._store_digests.get(name) == digest:
            return
        await store.async_save(payload)
        self._store_digests[name] = digest

    async def _async_save_accuracy(self) -> None:
        try:
            await self._async_save_if_changed(
                "accuracy",
                self._accuracy_store,
                {
                    "accuracy": self._accuracy.as_dict(),
                    # v5.2.0: the tank's lead record, alongside the room's
                    # rather than inside it.
                    "dhw_accuracy": self._dhw_accuracy.as_dict(),
                    "defrost": self._defrost.as_dict(),
                    "peaks": self._peak_tracker.as_dict(),
                    "comfort": self._comfort_learner.as_dict(),
                    # Persisted because `_init_runtime_state` resets it to
                    # `auto` on every reload, and writing any option reloads the
                    # entry -- so dragging the thermostat card's temperature, or
                    # simply restarting Home Assistant, silently dropped the
                    # user out of the mode they had selected.
                    "mode": self._mode,
                },
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist accuracy history: %s", err)

    async def _async_load_energy_totals(self) -> None:
        try:
            stored = await self._energy_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load energy totals: %s", err)
            return
        if not isinstance(stored, dict):
            return
        for key in list(self._energy_totals):
            value = stored.get(key)
            if isinstance(value, (int, float)) and np.isfinite(np.float64(value)):
                # Accumulators must never go backwards, or Home Assistant reads
                # the drop as a meter reset and creates a spurious spike.
                self._energy_totals[key] = max(
                    self._energy_totals[key], float(value)
                )
        since = stored.get("since")
        if isinstance(since, str) and since:
            self._energy_totals_since = since
        # A long silence before this restart reads as a power cut (#22).
        self._detect_outage(stored.get("last_tick"))

    async def _async_save_energy_totals(self) -> None:
        try:
            await self._async_save_if_changed(
                "energy_totals",
                self._energy_store,
                {
                    **self._energy_totals,
                    # The accumulators' stated period ("since"): written once
                    # and then never -- a lifetime counter's start date does
                    # not move, and the content-hash skip is what keeps this
                    # store from writing every cycle for an unchanging field.
                    "since": self._energy_totals_since,
                    # The outage detector's heartbeat (#22): the last instant
                    # this coordinator was alive. Numeric-key loaders skip it.
                    # It advances every cycle, so this store writes every
                    # cycle — the skip cannot be allowed to starve the
                    # heartbeat, or a plain restart reads as a power cut.
                    "last_tick": dt_util.now().isoformat(),
                },
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist energy totals: %s", err)

    def month_channel_totals(self, line: str) -> tuple[float, float] | None:
        """This month's (kWh, cost) for one accumulator channel.

        Booked per settlement alongside the lifetime fold, from the same
        numbers, so the two can never disagree. None while the month is
        still empty — an absent figure, never a zero that would read as
        "measured nothing".
        """
        entry = self._ledger.line(month_key(dt_util.now()), line)
        if not entry:
            return None
        return float(entry.get("kwh", 0.0)), float(entry.get("sek", 0.0))

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
        return _utc_step_starts(
            solve_now,
            n_steps,
            step_minutes=int(round(self._opt_config.dt_hours * 60)),
        )

    def _manual_pins(
        self, solve_now: datetime, n_steps: int
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Per-step pin arrays for the active override, or ``(None, None)``.

        Returns ``None`` for a channel left automatic (or when no override is in
        force / it has expired), so a solve with no manual plan is byte-for-byte
        identical to one from before this feature existed.

        Expiry is judged at the snapped ``solve_now``, deliberately: an
        override expiring 12:05 still pins step 0 of a 12:07 solve, because
        that step IS [12:00, 12:15) and the override covered its start.
        ``channel_pins`` already frees every step starting at or past the
        expiry, so this is the grid's own semantics, not a grace period.
        """
        override = self._manual_override
        if override is None:
            return None, None
        if override.is_expired(solve_now):
            # Drop it eagerly; the next save persists the cleared state.
            self._manual_override = None
            self._spawn(self._async_save_manual_plan())
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
        """The override state the plan sensors expose, or ``None`` when inactive.

        Expiry is judged at the snapped solve anchor, the same clock the
        pins were built against: judged at raw ``now`` instead, an override
        expiring mid-step read "inactive" here while the live plan still
        forced the step the anchor pinned — the sensor contradicting the
        actuation for up to a quarter hour.
        """
        override = self._manual_override
        if override is None or override.is_expired(
            self._solve_anchor(dt_util.now())
        ):
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
        # that had in fact applied perfectly well. Counted on the snapped
        # anchor, the same lattice the refresh just triggered will solve on;
        # a raw-instant lattice counts slot edges differently and the
        # reported figure would disagree with the plan by one step.
        step_starts = self._horizon_step_starts(
            self._solve_anchor(dt_util.now()), self._opt_config.n_steps
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

    async def _async_setup_defrost_watch(self) -> None:
        """Follow the defrost flag's transitions, when one is configured.

        Registration is conditional on the slot being filled, so an install
        without a defrost sensor carries no listener at all — the same
        discipline as the peak guard above.

        The listener is not an optimisation. Home Assistant fires no
        state-change event when a value is rewritten unchanged, so the
        per-cycle read is what supplies the flag's *level*; and a defrost runs
        for minutes inside an interval of thirty, so the per-cycle read alone
        would sample the flag at one instant and settle a real defrost as a
        confident duty of zero. Each source sees what the other cannot.
        """
        entity = self._config.get(CONF_HEAT_PUMP_DEFROST_ENTITY)
        # #236: released means the entry is gone; registering now would leak.
        if not entity or self._entry_released:
            return
        self._unsub_defrost = async_track_state_change_event(
            self.hass, [entity], self._on_defrost_event
        )
        _LOGGER.info("Defrost duty measured from %s", entity)

    @callback
    def _on_defrost_event(self, event) -> None:
        """One defrost flag transition: accrue on-time. Arithmetic only.

        ``@callback`` for the same reason as ``_on_power_event``: without it
        the helper dispatches to an executor thread and the window's
        accumulators race the update loop.

        Deliberately NOT freshness-guarded. A transition is a report by
        definition — it arrived, so it is current — and applying the reader's
        horizon to an event that has just fired would be nonsense. The
        horizon's job is to expire the per-cycle *level*, which is the reading
        that can go quietly out of date.
        """
        new_state = getattr(event, "data", {}).get("new_state")
        raw = getattr(new_state, "state", None) if new_state is not None else None
        flag = None
        if raw is not None and str(raw).lower() not in ("unknown", "unavailable"):
            flag = parse_bool(raw)
        self._defrost_window.observe(dt_util.now(), flag)

    async def _async_setup_peak_guard(self) -> None:
        """Register the meter listener — only when the guard is switched on.

        The flag gates *registration*, not just behaviour: an opt-out
        install carries no listener at all, so the event path cannot even
        run. The subscription follows the whole-house meter when one exists
        (the billed quantity), else the heat pump's own meter.
        """
        # #236's latch as well -- see ``_release_registrations``.
        if self._entry_released or not self._config.get(
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
            self._spawn(self._async_peak_guard_transition())

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
        if limits:
            limit = float(min(limits))
            limit_source = "main fuse" if limit == fuse else "capacity threshold"
        elif tariff.enabled and tariff.sample_factor(dt_util.now()) > 0.0:
            # A capacity tariff with no reference peak yet. `threshold_kw`
            # answers +inf there, which means "do not let the peak term
            # distort the plan" -- it does not mean the house may draw
            # freely, and this sensor asks a different question: how many kW
            # can be drawn right now *without new cost*. With no peak
            # recorded the month's bill is set from the first window, so no
            # kW is free and the true answer is 0.0.
            #
            # It used to be no answer at all. An install with a capacity
            # tariff and no `main_fuse_amperes` -- the default, since the
            # fuse defaults to 0 -- had both candidate limits filtered out
            # here and lost the entity entirely for the first metering window
            # of every month. A charger automation following it saw its input
            # disappear monthly, at the exact hour the month's peak was being
            # set. Installs with a fuse are unaffected: their limit is finite
            # and this branch is not reached.
            limit = 0.0
            limit_source = "capacity tariff with no peak reference yet"
        else:
            # Neither a fuse nor a capacity term that bills this window.
            # Nothing bounds the house that this integration knows about,
            # and saying nothing is the honest answer.
            return {"available": False}

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
            "limit_source": limit_source,
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
        # v5.3.0: a month in which the pump's mode stopped it heating is not
        # evidence about how many amperes the house needs. Passing the block
        # into the shadow solve above makes the comparison honest, but an
        # honest comparison of two crippled plans still answers the wrong
        # question -- "would a smaller fuse do" is about the house's real
        # demand, and while a channel is blocked the plan is not showing it.
        # The last real verdict, if there is one, stays published untouched.
        if self._pump_signals.space_blocked or self._pump_signals.dhw_blocked:
            _LOGGER.debug(
                "Skipping the fuse advisor: the heat pump's mode (%s) is "
                "suppressing a channel, so this horizon is not evidence "
                "about the house's demand",
                self._pump_signals.mode.label,
            )
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

    # ==================================================================
    # Model & learning insurance (v4.0.0 T4a)
    # ==================================================================

    def _detect_immersion(self) -> None:
        """#11: notice the immersion element wearing the pump's meter.

        Measured draw beyond ``nameplate × IMMERSION_FACTOR`` while the
        plan commands heat cannot be the compressor. Two agreeing samples
        latch, two clear ones release — one meter spike does nothing.
        While latched the COP learner skips (a resistive kW in the ratio
        reads as catastrophic efficiency) and the settlement books the
        excess as its own ledger line.
        """
        measured = self._measured_power
        nameplate = float(self._thermal_params.max_electrical_power)
        over = (
            measured is not None
            and nameplate > 0.1
            and measured > nameplate * IMMERSION_FACTOR
            and self._commanded_power() > 0.1
        )
        now = dt_util.now()
        if over:
            self._immersion_over_count += 1
            self._immersion_clear_count = 0
            if not self._immersion_active and self._immersion_over_count >= 2:
                self._immersion_active = True
                self._immersion_evidence.append(
                    f"{now.isoformat(timespec='seconds')}: measured "
                    f"{measured:.1f} kW over {nameplate:.1f} kW nameplate; "
                    "immersion element running"
                )
                del self._immersion_evidence[:-6]
                self._immersion_events.append(now.isoformat())
                del self._immersion_events[:-20]
                _LOGGER.info(
                    "Immersion element detected (%.1f kW measured, %.1f kW "
                    "nameplate)",
                    measured,
                    nameplate,
                )
        else:
            self._immersion_clear_count += 1
            self._immersion_over_count = 0
            if self._immersion_active and self._immersion_clear_count >= 2:
                self._immersion_active = False
                self._immersion_evidence.append(
                    f"{now.isoformat(timespec='seconds')}: draw back under "
                    "nameplate; released"
                )
                del self._immersion_evidence[:-6]

    # -- T5 comfort floors (#16 #54), both gated ---------------------------

    def _confidence_margins(self, n_steps: int) -> np.ndarray | None:
        """#16: raise the floor by the model's own expected error per lead.

        ``sigma(lead) × (1 − trust)``, hard-capped: a model with a good
        recent record (trust → 1) margins nothing however noisy the long
        buckets look, and no history means sigma 0 means None — the
        byte-inert fresh-install case. The cap plus the damping is also
        what keeps the loop (margin → different plan → different errors)
        from oscillating: the margin can only shrink as accuracy improves.
        """
        if not bool(
            self._config.get(
                CONF_CONFIDENCE_MARGINS_ENABLED,
                DEFAULT_CONFIDENCE_MARGINS_ENABLED,
            )
        ):
            return None
        damp = 1.0 - self._accuracy.trust()
        if damp <= 1e-9:
            return None
        dt_h = max(self._opt_config.time_step_minutes, 1.0) / 60.0
        margins = np.array(
            [
                min(
                    self._accuracy.sigma((i + 1) * dt_h) * damp,
                    CONFIDENCE_MARGIN_CAP_C,
                )
                for i in range(n_steps)
            ],
            dtype=float,
        )
        return margins if bool(np.any(margins > 1e-9)) else None

    def _indoor_humidity_value(self) -> float | None:
        """The measured indoor relative humidity, %, or None."""
        entity_id = self._config.get(CONF_INDOOR_HUMIDITY_ENTITY)
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        # A frozen sensor holds a raised mold floor forever; with no live
        # reading the floor vanishes instead — the fail-safe direction the
        # inputs module prescribes for every optional sensor.
        age = age_of(state, dt_util.utcnow())
        if age is None or age > timedelta(minutes=HUMIDITY_MAX_AGE_MINUTES):
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        if not np.isfinite(value) or not 0.0 < value <= 100.0:
            return None
        return value

    def _mold_floor_series(
        self, outdoor: np.ndarray, target_cap: float | None = None
    ) -> np.ndarray | None:
        """#54: the per-step room floor keeping every surface under mold RH.

        Double-gated — the flag AND a humidity entity with a live reading.
        The measured vapour pressure is held constant across the horizon
        (cooling the room does not remove moisture), and the floor is
        capped at the comfort target: heating past target to fight mold is
        dehumidification's job, not the heat pump's.

        The cap is the CONFIGURED target, never the live one: the away
        setback lowers ``self._opt_config.target_temp``, and capping at
        that would disarm the guard exactly when mold risk peaks — a cold,
        damp, unheated house. For the same reason this floor deliberately
        outranks the open-window relax: a tripped window detector lowers
        the comfort floor, not the physics of condensation. What-if solves
        pass ``target_cap`` so a simulated target override gets a
        consistently capped floor.
        """
        if not bool(
            self._config.get(CONF_MOLD_GUARD_ENABLED, DEFAULT_MOLD_GUARD_ENABLED)
        ):
            return None
        rh = self._indoor_humidity_value()
        room = self._current_state.room_temperature
        if rh is None or room is None or not np.isfinite(room):
            return None
        frsi = _as_float(
            self._config.get(CONF_THERMAL_BRIDGE_FRSI),
            DEFAULT_THERMAL_BRIDGE_FRSI,
        )
        floors = np.array(
            [
                mold_safe_room_floor(
                    float(room), rh, float(t), frsi, MOLD_SURFACE_RH_LIMIT
                )
                for t in outdoor
            ],
            dtype=float,
        )
        cap = (
            float(target_cap)
            if target_cap is not None
            else _as_float(
                self._config.get(CONF_TARGET_TEMP), DEFAULT_TARGET_TEMP
            )
        )
        return np.minimum(floors, cap)

    def _track_curve_comfort(self, now: datetime) -> None:
        """#2's evidence: the day's worst (zone − comfort floor) margin.

        Measured zone temperatures against the floor the optimizer was
        enforcing at that hour. A touch of the floor while the bias is
        applied resets it on the spot — safety reacts immediately, only
        the downward creep waits for the day to close.
        """
        if not bool(
            self._config.get(
                CONF_CURVE_LEARNING_ENABLED, DEFAULT_CURVE_LEARNING_ENABLED
            )
        ):
            return
        # An away setback sits deliberately below the normal floor this
        # tracker reads (the lowered floor lives only inside the solve's
        # snapshot/unwind envelope), so every vacation would read as a
        # comfort miss and wipe the learned bias. Same for a tripped
        # window detector or stale sensor: the dip is real but it is not
        # the curve's doing. No evidence is collected on such days.
        if self._away_state.active or self._away_state.recovery_active:
            return
        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) is not None:
            return
        hour = now.hour + now.minute / 60.0
        try:
            # The BASE floor, deliberately: #16's confidence margin lifts
            # the floor inside the solve as a cushion against model error,
            # but eating into that cushion is not a comfort miss — only
            # dipping under the floor the user actually configured is.
            floor_c = float(self._opt_config.get_temp_bounds(hour)[0])
        except Exception:  # noqa: BLE001 - evidence, never operations
            return
        temps = [
            t
            for t in (
                self._current_state.room_temperature,
                self._current_state.upper_floor_temperature,
                self._current_state.lower_floor_temperature,
            )
            if t is not None and np.isfinite(t)
        ]
        if not temps:
            return
        margin = min(temps) - floor_c

        day = now.date().isoformat()
        if self._curve_day and day != self._curve_day:
            # Yesterday closed: fold its verdict, then start today's book.
            self._curve_learner.record_day(now, self._curve_day_worst)
            self._curve_day_worst = None
        self._curve_day = day
        self._curve_day_worst = (
            margin
            if self._curve_day_worst is None
            else min(self._curve_day_worst, margin)
        )
        if margin <= 0.0 and self._curve_learner.bias < 0.0:
            self._curve_learner.record_miss(now, margin)

    def _immersion_dhw_margin(self, now: datetime) -> float:
        """#11's gated feedback: extra readiness when rescues recur.

        Three or more immersion events inside fourteen days say the tank
        keeps arriving late enough that the element has to save it; the
        margin asks the plan to arrive a little earlier instead of paying
        resistive prices for the difference.
        """
        if not bool(
            self._config.get(
                CONF_IMMERSION_FEEDBACK_ENABLED,
                DEFAULT_IMMERSION_FEEDBACK_ENABLED,
            )
        ):
            return 0.0
        cutoff = now - timedelta(days=14)
        recent = 0
        for raw in self._immersion_events:
            try:
                when = datetime.fromisoformat(raw)
            except (TypeError, ValueError):
                continue
            if when.tzinfo is None and now.tzinfo is not None:
                when = when.replace(tzinfo=now.tzinfo)
            if when >= cutoff:
                recent += 1
        return 2.0 if recent >= 3 else 0.0

    # -- T4b learners (#17 #36 #53), each fully behind its flag ------------

    def _fold_capacity_envelope(self, observed_cop: float) -> None:
        """#17: remember the most heat the unit has delivered per bucket.

        Fed only from ``_learn_measured_cop``'s vetted tail, so frost,
        immersion, freezes and low duty are already filtered. The envelope
        is an upper bound with slow forgetting — a one-off spike decays
        instead of pinning the bucket forever.

        Only near-nameplate commands are evidence: a partial-load interval
        says nothing about what the machine COULD deliver, and folding it
        would make the envelope self-censoring — the caps limit the plan,
        the plan limits the samples, and every bucket would ratchet down
        to the floor within weeks of ordinary partial-load running.
        """
        if not bool(
            self._config.get(
                CONF_CAPACITY_CURVE_ENABLED, DEFAULT_CAPACITY_CURVE_ENABLED
            )
        ):
            return
        if self._measured_power is None:
            return
        p_max = float(self._thermal_params.max_electrical_power)
        if p_max <= 0.1 or self._commanded_power() < 0.95 * p_max:
            return
        thermal_kw = float(observed_cop) * float(self._measured_power)
        if not np.isfinite(thermal_kw) or thermal_kw <= 0.0:
            return
        bucket = int(
            np.floor(float(self._current_state.outdoor_temperature) / 3.0)
        )
        entry = self._capacity_envelope.get(bucket)
        if entry is None:
            self._capacity_envelope[bucket] = [thermal_kw, 1]
            return
        entry[0] = max(thermal_kw, float(entry[0]) * CAPACITY_FORGET)
        entry[1] = int(entry[1]) + 1

    def _capacity_caps(self, outdoor_temps: np.ndarray) -> np.ndarray | None:
        """#17's per-step electrical ceiling from the learned envelope.

        Composes through T2's ``power_caps_extra`` channel — never a new
        one. Floored at ``CAPACITY_FLOOR_FRACTION`` of nameplate: a starved
        house at −15 °C is this program's worst failure mode, so the cap
        may trim optimism but can never take the pump away. Buckets still
        under ``CAPACITY_MIN_SAMPLES`` cap nothing. Returns None when no
        bucket caps anything.
        """
        if not bool(
            self._config.get(
                CONF_CAPACITY_CURVE_ENABLED, DEFAULT_CAPACITY_CURVE_ENABLED
            )
        ):
            return None
        p_max = float(self._thermal_params.max_electrical_power)
        if p_max <= 0.1:
            return None
        floor = CAPACITY_FLOOR_FRACTION * p_max
        caps = np.full(len(outdoor_temps), p_max, dtype=float)
        any_cap = False
        for i, outdoor in enumerate(outdoor_temps):
            entry = self._capacity_envelope.get(int(np.floor(outdoor / 3.0)))
            if entry is None or int(entry[1]) < CAPACITY_MIN_SAMPLES:
                continue
            cop_i = max(self._thermal_model.compute_cop(float(outdoor)), 1e-6)
            cap_i = float(np.clip(float(entry[0]) / cop_i, floor, p_max))
            if cap_i < p_max - 1e-9:
                caps[i] = cap_i
                any_cap = True
        return caps if any_cap else None

    def _fold_solar_aperture(
        self, previous_state: ThermalState, residual: float, dt_h: float
    ) -> None:
        """#36: regress the sunny-step residual against modelled Q_solar.

        The slope of implied surplus power on modelled solar gain is
        exactly (true aperture / modelled − 1); with the learned scale
        already applied in the simulation, the residuals re-centre and
        the regression converges to a fixed point.
        """
        if not bool(
            self._config.get(
                CONF_SOLAR_APERTURE_LEARNING_ENABLED,
                DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
            )
        ):
            return
        irradiance = float(previous_state.solar_radiation or 0.0)
        if irradiance < SOLAR_APERTURE_MIN_IRRADIANCE:
            return
        capacity = (
            self._thermal_params.upper_floor_thermal_mass
            if self._thermal_params.two_zone_enabled
            else self._thermal_params.room_thermal_mass
        )
        if capacity <= 1e-6 or dt_h <= 1e-6:
            return
        x = self._thermal_model.compute_solar_gain(irradiance)
        y = residual * capacity / dt_h  # implied surplus power, kW
        if x <= 1e-6 or not np.isfinite(y):
            return
        a = SOLAR_APERTURE_ALPHA
        m = self._solar_aperture
        m["n"] += 1.0
        dx = x - m["mx"]
        m["mx"] += a * dx
        dy = y - m["my"]
        m["my"] += a * dy
        # EWMA covariance/variance about the running means.
        m["cov"] += a * (dx * (y - m["my"]) - m["cov"])
        m["var"] += a * (dx * (x - m["mx"]) - m["var"])
        if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:
            m["scale"] = float(
                np.clip(
                    m["scale"] + m["cov"] / m["var"],
                    SOLAR_APERTURE_MIN,
                    SOLAR_APERTURE_MAX,
                )
            )
            # The step has been taken into the standing scale; the moments
            # restart so the next correction is measured against it.
            m["cov"] = 0.0

    def _fold_internal_gains(
        self,
        previous_time: datetime | None,
        previous_state: ThermalState,
        residual: float,
        dt_h: float,
    ) -> None:
        """#53: pull the interval's hour toward the residual it produced.

        Only dark intervals feed it — under real sun the same surplus is
        the aperture learner's business (#36) — and the ridge term keeps
        every hour tethered to the configured constant: the profile is a
        perturbation of the prior, never a replacement for it.
        """
        if not bool(
            self._config.get(
                CONF_INTERNAL_GAINS_LEARNING_ENABLED,
                DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
            )
        ):
            return
        if float(previous_state.solar_radiation or 0.0) > 50.0:
            return
        if previous_time is None or dt_h <= 1e-6:
            return
        capacity = (
            self._thermal_params.upper_floor_thermal_mass
            if self._thermal_params.two_zone_enabled
            else self._thermal_params.room_thermal_mass
        )
        if capacity <= 1e-6:
            return
        g0 = float(self._thermal_params.internal_gains)
        if self._internal_gains_profile is None:
            self._internal_gains_profile = [g0] * 24
        hour = int(previous_time.hour) % 24
        y = residual * capacity / dt_h
        if not np.isfinite(y):
            return
        g = self._internal_gains_profile[hour]
        g += INTERNAL_GAINS_ALPHA * y - INTERNAL_GAINS_RIDGE * (g - g0)
        self._internal_gains_profile[hour] = float(
            np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))
        )

    def _observe_cop_health(
        self, observed_cop: float, dhw_curve: bool = False
    ) -> None:
        """#12: the weeks-scale compressor-health watch.

        Baseline per (3 °C outdoor bucket, reference curve), fed only from
        the frost-band- and immersion-guarded samples `_learn_measured_cop`
        already vetted. The shortfall is judged BEFORE the observation joins
        the baseline, or a slow decline would drag its own reference down and
        never trip.

        ``dhw_curve`` says which curve produced ``observed_cop``, and a
        sample is only ever compared against a baseline built from the same
        curve. Without it the watch compares a hot-water COP against a
        space-heating reference and reads the 8-20 % the model itself puts
        between them as a failing compressor — a fabricated fault report
        about expensive hardware, raised within hours on an ordinary plan.
        It defaults to False, which is what every install without a mode
        entity produces and is the pre-v5.3.0 behaviour exactly.
        """
        outdoor = float(self._current_state.outdoor_temperature)
        bucket = (int(np.floor(outdoor / 3.0)), bool(dhw_curve))
        entry = self._cop_baseline.get(bucket)
        if entry is None:
            self._cop_baseline[bucket] = [float(observed_cop), 1]
            return
        baseline, count = float(entry[0]), int(entry[1])
        if count >= COP_BASELINE_MIN_SAMPLES and baseline > 0.5:
            shortfall = (baseline - float(observed_cop)) / baseline
            changed = self._cop_health_cusum.update(dt_util.now(), shortfall)
            if changed:
                if self._cop_health_cusum.tripped:
                    self._raise_cop_issue(baseline)
                else:
                    ir.async_delete_issue(self.hass, DOMAIN, "cop_degradation")
        # While the watch is tripped the baseline stops absorbing samples:
        # otherwise the EWMA re-anchors to the degraded level within weeks
        # and a permanent fault "recovers" on its own, clearing the issue
        # the user was told clears only when efficiency does.
        if self._cop_health_cusum.tripped:
            return
        if count < COP_BASELINE_MIN_SAMPLES:
            # A plain mean while young: seeding the EWMA with a single
            # first sample lets one outlier interval distort the baseline
            # for its first fifty folds — and the watch starts judging
            # after twenty.
            entry[0] = (baseline * count + float(observed_cop)) / (count + 1)
        else:
            entry[0] = (
                (1.0 - COP_BASELINE_ALPHA) * baseline
                + COP_BASELINE_ALPHA * float(observed_cop)
            )
        entry[1] = count + 1

    def _raise_cop_issue(self, baseline: float) -> None:
        """One repair issue with the money the shortfall costs per month."""
        now = dt_util.now()
        monthly_kwh = 0.0
        try:
            summary = self._ledger.month_summary(month_key(now))
            monthly_kwh = float((summary.get("spot") or {}).get("kwh", 0.0))
            # The ledger holds month-to-date; a trip on the 2nd would
            # otherwise price a month off two days of receipts. Scale to
            # a full month — a rough estimate, honestly labelled "~".
            monthly_kwh = monthly_kwh / max(1, now.day) * 30.0
        except Exception:  # noqa: BLE001 - the estimate is best-effort
            monthly_kwh = 0.0
        mean_price = (
            float(np.mean([p.get("total", 0.0) for p in self._prices]))
            if self._prices
            else 1.0
        )
        current = self._last_measured_cop or baseline
        shortfall = max(0.0, (baseline - float(current)) / baseline)
        # In the instance currency: the prices are, so the product is
        # (audit D4-04, #168 -- the placeholder used to be named after SEK).
        cost_month = monthly_kwh * mean_price * shortfall
        _LOGGER.warning(
            "Compressor efficiency has drifted %.0f%% below its own "
            "baseline (~%.0f %s/month at current usage)",
            shortfall * 100.0,
            cost_month,
            self.currency,
        )
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "cop_degradation",
            is_fixable=False,
            # Persistent: the tripped watch survives a restart in the
            # store, so the notice must too.
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="cop_degradation",
            translation_placeholders={
                "shortfall_percent": f"{shortfall * 100.0:.0f}",
                "cost_month": f"{cost_month:.0f}",
                "currency": self.currency,
            },
        )

    # -- #42: the weekly snapshots and the drift alarm ---------------------

    def _learner_snapshot_payloads(self) -> dict[str, dict]:
        """Every learner's persisted shape, by the stores' own producers."""
        return {
            "thermal_learning": self._thermal_learning_payload(),
            "dhw_profile": self._dhw_profile_payload(),
            "dhw_draws": self._draw_stats.as_dict(),
            "price_model": self._price_model.as_dict(),
            "accuracy": self._accuracy.as_dict(),
            "comfort": self._comfort_learner.as_dict(),
            "defrost": self._defrost.as_dict(),
            # peak_tracker deliberately absent: realised monthly peaks are
            # billed facts, not learned state — see _apply_learner_payloads.
        }

    def _apply_learner_payloads(self, learners: dict) -> None:
        """Restore learners from a snapshot, via the loaders' own parsing."""
        thermal = learners.get("thermal_learning")
        if isinstance(thermal, dict):
            for setter, key in (
                (self._apply_buffer_cooling_rate, "buffer_cooling_rate"),
                (self._apply_house_heat_loss_scale, "house_heat_loss_scale"),
                (self._apply_lower_floor_loss_ratio, "lower_floor_loss_ratio"),
                (self._apply_cop_scale, "cop_scale"),
            ):
                value = thermal.get(key)
                if value is not None:
                    try:
                        setter(float(value))
                    except (TypeError, ValueError):
                        continue
            # T4b learners roll back through the same parser the store
            # loader uses, cleared first so a restore is a restore, not a
            # merge with the drifted state it replaces — ALL of them: a
            # pre-T4b snapshot without these keys must restore to inert,
            # not keep whatever drifted in since.
            self._capacity_envelope = {}
            self._internal_gains_profile = None
            self._solar_aperture = {
                "n": 0.0, "mx": 0.0, "my": 0.0, "cov": 0.0, "var": 0.0,
                "scale": 1.0,
            }
            self._curve_learner = CurveLearner()
            # T7: the frequency map rolls back with its fellow learners; a
            # pre-T7 snapshot restores it to inert. The fallback latch does
            # NOT ride this path — see _async_load_thermal_learning.
            self._freq_map = FrequencyMap()
            self._load_t4b_learners(thermal)
            # v5.7.0 (issue #86): a snapshot from before an options edit
            # carries a scale fitted against the pre-edit anchor; restoring
            # it verbatim here would re-install the pre-edit correction
            # against the new configuration. The same law the loader uses,
            # without the save -- snapshots are restores, and the next
            # regular save records the fresh anchor.
            self._reanchor_house_heat_loss_scale(
                thermal.get("house_heat_loss_anchor")
            )
        profile = learners.get("dhw_profile")
        if isinstance(profile, dict):
            hourly = profile.get("hourly_profile")
            if isinstance(hourly, list) and len(hourly) == 24:
                self._dhw_hourly_profile = self._normalize_dhw_profile(hourly)
                self._thermal_params.dhw_hourly_draw_pattern = (
                    self._dhw_hourly_profile.copy()
                )
            # The day-type profiles restore alongside the pooled one, or a
            # rollback would blend a rolled-back pool with un-rolled-back
            # day shapes — half of one week, half of another.
            for attr, key, count_idx in (
                ("_dhw_profile_weekday", "profile_weekday", 0),
                ("_dhw_profile_weekend", "profile_weekend", 1),
            ):
                arr = profile.get(key)
                if isinstance(arr, list) and len(arr) == 24:
                    setattr(self, attr, self._normalize_dhw_profile(arr))
                    try:
                        self._dhw_daytype_samples[count_idx] = max(
                            0, int(profile.get(f"{key}_samples", 0))
                        )
                    except (TypeError, ValueError):
                        self._dhw_daytype_samples[count_idx] = 0
            rate = profile.get("cooling_rate")
            if rate is not None:
                try:
                    self._apply_dhw_cooling_rate(float(rate))
                except (TypeError, ValueError):
                    pass
        draws = learners.get("dhw_draws")
        if isinstance(draws, dict):
            self._draw_stats = DrawStats.from_dict(draws)
        prices = learners.get("price_model")
        if isinstance(prices, dict):
            self._price_model = PriceShapeModel.from_dict(prices)
        # The accuracy tracker is deliberately NOT restored: it is the
        # evidence the drift alarm judges, not a learner. Restoring it
        # made the rollback erase its own justification — the next
        # counted day saw in-band bias, released the alarm, deleted the
        # notice, and under genuine drift the cycle repeated until a
        # drifted snapshot laundered itself into the restore pool.
        comfort = learners.get("comfort")
        if isinstance(comfort, dict):
            self._comfort_learner = ComfortLearner.from_dict(
                comfort, self._comfort_learner.configured_weight
            )
            self._apply_comfort_weight()
        defrost = learners.get("defrost")
        if isinstance(defrost, dict):
            self._defrost = DefrostDerate.from_dict(defrost)
            # Rebind, exactly as the load path does: the thermal model
            # consumes the derate through this reference, and without it
            # the restored object trains while an orphan keeps serving.
            self._thermal_params.defrost_derate = self._defrost
        # The peak tracker is deliberately NOT restored: the month's
        # realised peaks are billed facts — the DSO already metered them —
        # not learned state. Restoring a week-old peak list lowered
        # threshold_kw below what this month will actually be billed at,
        # mis-arming the live peak guard against a ceiling that no longer
        # exists. Old snapshots still carrying the key are simply ignored.

    def _inputs_healthy(self) -> bool:
        return (
            self._learning_frozen(
                CONF_INDOOR_TEMP_ENTITY,
                CONF_OUTDOOR_TEMP_ENTITY,
                CONF_POWER_ENTITY,
            )
            is None
        )

    async def _async_watch_learning_drift(self) -> None:
        """The #42 heartbeat: weekly snapshot, daily bias check, rollback."""
        # Never act before the persisted ring has loaded: the first
        # heartbeat would otherwise snapshot half-loaded learners into an
        # empty ring and overwrite eight weeks of insurance with it.
        if not self._snapshots_loaded:
            return
        now = dt_util.now()

        # #26's escape hatch: the vent detector is fed only by heat-loss
        # residuals, which stop entirely in mild weather. A latch nothing
        # can feed must time out, or the "ventilation" freeze (and the
        # gated relax) would outlive the window by weeks.
        if self._vent_cusum.release_if_starved(now, VENT_CUSUM_STARVE_HOURS):
            _LOGGER.info(
                "Open-window detector released: no residuals for %.0f h",
                VENT_CUSUM_STARVE_HOURS,
            )
            await self._async_save_thermal_learning()

        # Health is accumulated worst-of-day across heartbeats, not
        # sampled at whichever tick happens to count the day: a morning
        # of garbage inputs must not green-light an evening rollback.
        healthy_now = self._inputs_healthy()
        self._day_inputs_healthy = self._day_inputs_healthy and healthy_now
        healthy = self._day_inputs_healthy

        if self._snapshot_ring.due(now):
            self._snapshot_ring.take(
                now,
                self._learner_snapshot_payloads(),
                self._accuracy.summary(),
                healthy,
            )
            await self._async_save_snapshots()

        day_before = self._snapshot_ring._last_day
        changed = self._snapshot_ring.observe_bias(
            now, self._accuracy.temperature_bias(), healthy
        )
        day_counted = self._snapshot_ring._last_day != day_before
        if day_counted:
            # The counted day consumed the accumulator; the next day's
            # verdict starts from this tick's health.
            self._day_inputs_healthy = healthy_now
        if not changed:
            if day_counted:
                # Persist the streak daily — a restart on drift day 3
                # must not rewind the count to the last weekly save.
                await self._async_save_snapshots()
            return
        if not self._snapshot_ring.alarmed:
            ir.async_delete_issue(self.hass, DOMAIN, "accuracy_drift")
            self._rollback_done_for_alarm = False
            await self._async_save_snapshots()
            return

        rolled_back = False
        if (
            self._snapshot_ring.auto_rollback_justified
            and not self._rollback_done_for_alarm
        ):
            snap = self._snapshot_ring.best_restore()
            if snap is not None:
                self._apply_learner_payloads(snap.get("learners") or {})
                self._rollback_done_for_alarm = True
                rolled_back = True
                _LOGGER.warning(
                    "Prediction bias out of band for %d days on healthy "
                    "inputs; learned state rolled back to the snapshot "
                    "from %s",
                    BIAS_TRIP_DAYS,
                    snap.get("taken_at"),
                )
                await self._async_save_thermal_learning()
                await self._async_save_dhw_profile()
                await self._async_save_dhw_draws()
                await self._async_save_price_model()
                await self._async_save_accuracy()
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "accuracy_drift",
            is_fixable=False,
            # Persistent: the alarm state survives a restart in the
            # store, so its notice must too — a repair issue that
            # silently vanishes on reboot while the fault stays is worse
            # than none.
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=(
                "accuracy_drift_rolled_back" if rolled_back else "accuracy_drift"
            ),
        )
        await self._async_save_snapshots()

    async def async_restore_learned_snapshot(self) -> bool:
        """The one-click rollback service. True when a snapshot applied."""
        snap = self._snapshot_ring.best_restore()
        if snap is None:
            _LOGGER.warning(
                "No snapshot qualifies for restore (healthy inputs and "
                "in-band accuracy at capture time are required)"
            )
            return False
        self._apply_learner_payloads(snap.get("learners") or {})
        _LOGGER.info(
            "Learned state restored from the snapshot taken %s",
            snap.get("taken_at"),
        )
        await self._async_save_thermal_learning()
        await self._async_save_dhw_profile()
        await self._async_save_dhw_draws()
        await self._async_save_price_model()
        await self._async_save_accuracy()
        self.async_update_listeners()
        return True

    async def _async_load_snapshots(self) -> None:
        try:
            stored = await self._snapshot_store.async_load()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not load learner snapshots: %s", err)
            return
        finally:
            # Set even on failure: a lost store means an empty ring, and
            # the insurance must keep running rather than disarm forever.
            self._snapshots_loaded = True
        if isinstance(stored, dict):
            self._snapshot_ring = SnapshotRing.from_dict(stored)

    async def _async_save_snapshots(self) -> None:
        try:
            await self._snapshot_store.async_save(self._snapshot_ring.as_dict())
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not persist learner snapshots: %s", err)

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
            ts = _comparable_ts(entry.get("datetime"), now)
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

    def _settle_defrost(self, sample: AccuracySample, window: Any) -> None:
        """Teach the derate from the interval that has just been settled.

        With a legible flag the derate learns from **measured duty**, in every
        temperature bucket rather than only in the frosting band: defrosts
        happen below 0 °C too, and a bucket that measures a duty of zero is
        learning something real — that it does not need a derate.

        Without one it falls back to the pre-v5.3.0 inference from
        ``delivered_ratio``, restricted to the frosting band as before, so
        that an install with no defrost sensor behaves exactly as it did.

        The two never both fold the same interval. That is not tidiness: they
        estimate the same quantity from different evidence, and averaging a
        measurement with an inference of it produces a number that is neither
        — the more so here, where the inference is known to be biased
        optimistic and structurally blind to the very event it is standing in
        for (see ``defrost.py``).
        """
        outdoor = sample.outdoor_temp
        if outdoor is None:
            return
        if window.observed:
            # A window far from the expected interval length is a restart, a
            # long stall or a reload, not a measurement: the denominator would
            # be meaningless and a duty computed from it would be too.
            interval_s = (
                _as_float(
                    self._config.get(CONF_OPTIMIZATION_INTERVAL),
                    DEFAULT_OPTIMIZATION_INTERVAL,
                )
                * 60.0
            )
            if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s:
                self._defrost.observe_duty(
                    outdoor, sample.humidity, window.duty, window.events
                )
            return
        ratio = delivered_ratio(sample)
        if ratio is not None and in_frost_band(outdoor):
            self._defrost.observe(outdoor, sample.humidity, ratio)

    def _record_accuracy(self) -> None:
        """Close the loop on the prediction made at the previous interval."""
        pending = self._pending_prediction
        now = dt_util.now()

        # The defrost measurement window is closed on EVERY cycle, before
        # anything can return early. It is a measurement of wall-clock time,
        # not a learner: leaving it open through a freeze, or through a cycle
        # with no prediction to settle, would let it accumulate across hours
        # and then report that span's duty as if it were one interval's.
        # Whether the derate is allowed to *learn* from it is decided below.
        defrost_window = self._defrost_window.close(now)

        # T6 #55: every cycle is one power sample for the start counter,
        # whether or not a prediction pair settles this time.
        self._observe_compressor_start(now)
        # T7 #61: and one frequency sample for the kW-per-Hz map (plus the
        # control watchdog, when that stage is armed).
        self._observe_frequency(now)

        # T5 #16: settle every matured lead-time promise against the same
        # measured temperature the one-step sample below uses. The window
        # is the sampling cadence itself — score only on the default
        # half-hour and every bucket whose lead is not a multiple of a
        # coarser configured interval starves forever. A stale or frozen
        # indoor sensor scores nothing: a frozen reading is not a
        # measurement, and an EWMA poisoned by one persists for weeks.
        interval_h = (
            _as_float(
                self._config.get(CONF_OPTIMIZATION_INTERVAL),
                DEFAULT_OPTIMIZATION_INTERVAL,
            )
            / 60.0
        )
        actual_now = self._current_state.room_temperature
        indoor_frozen = self._learning_frozen(CONF_INDOOR_TEMP_ENTITY)
        if actual_now is not None and indoor_frozen is None:
            self._accuracy.score_lead_predictions(
                now, float(actual_now), window_hours=interval_h
            )

        # v5.2.0: and the same settlement for the hot-water tank, against
        # the measured probe. `_dhw_probe_temperature` carries the whole
        # gate — configured, read, usable this interval — so a house with
        # no tank probe scores nothing and its band never appears.
        dhw_now = self._dhw_probe_temperature()
        if dhw_now is not None:
            self._dhw_accuracy.score_lead_predictions(
                now, dhw_now, window_hours=interval_h
            )

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
                # T4a: observed-minus-modelled COP rides on the sample, so
                # the snapshots' accuracy tags and #12's history both see
                # efficiency, not just temperature error.
                if (
                    self._last_measured_cop is not None
                    and sample.outdoor_temp is not None
                ):
                    try:
                        # v5.3.0: subtract the curve the observation was
                        # actually referenced to. Recomputing the space curve
                        # for a hot-water interval would put back exactly the
                        # mismatch ``_cop_reference_curve`` removes — the
                        # residual would show ~16 % and nothing would be wrong
                        # with the pump. Without a mode entity the flag is
                        # never set and this is the v5.1.5 expression.
                        if (
                            self._last_cop_curve_dhw
                            and self._last_cop_dhw_temp is not None
                        ):
                            modelled = self._thermal_model.compute_cop_dhw(
                                sample.outdoor_temp, self._last_cop_dhw_temp
                            )
                        else:
                            modelled = self._thermal_model.compute_cop(
                                sample.outdoor_temp
                            )
                        sample.cop_residual = round(
                            float(self._last_measured_cop) - float(modelled),
                            3,
                        )
                    except Exception:  # noqa: BLE001 - tag is best-effort
                        sample.cop_residual = None
                # D7-03/D7-05: skip the accuracy sample when ``indoor_frozen``
                # above is set — open window, external heat, pump fault, or
                # an unusable indoor sensor. Energy below is still
                # accumulated: it really was drawn.
                if indoor_frozen is None:
                    self._accuracy.record(sample)
                self._accumulate_energy(sample, elapsed, pending)

                # T6 #52: the settled triple the diagnosis button re-runs.
                # Realised values measured NOW close the interval whose
                # assumptions were captured when it began.
                diag = pending.get("diag")
                if diag is not None and sample.actual_temp is not None:
                    # The meter reads the whole pump; the model's power
                    # input is the space channel. Apportion the measured
                    # draw by the plan's own split — the same convention
                    # the energy settlement uses — so the power swap
                    # compares space against space.
                    planned_space = float(pending.get("space_power") or 0.0)
                    planned_dhw = float(pending.get("dhw_power") or 0.0)
                    planned_total = planned_space + planned_dhw
                    share = (
                        planned_space / planned_total
                        if planned_total > 1e-6
                        else 1.0
                    )
                    self._last_interval_record = {
                        "when": now.isoformat(timespec="seconds"),
                        "state": diag["state"],
                        "planned": diag["planned"],
                        "dt_hours": elapsed,
                        "realised": {
                            "electrical_power": (
                                sample.actual_power_kw * share
                                if sample.actual_power_kw is not None
                                else None
                            ),
                            "outdoor_temp": (
                                self._current_state.outdoor_temperature
                            ),
                            "solar_radiation": (
                                self._current_state.solar_radiation
                            ),
                        },
                        "actual": float(sample.actual_temp),
                    }

                # The defrost derate, from whichever estimator this install
                # can support. Either way it is only meaningful while the
                # learners are not frozen for some other reason.
                if not self._learning_frozen(CONF_POWER_ENTITY):
                    self._settle_defrost(sample, defrost_window)

        self._pending_prediction = {
            "when": now,
            # The meter sees the whole heat pump, so the prediction it is
            # compared against has to be the whole plan. Recording space
            # heating alone made every hot-water charge look like the unit
            # under-delivering, which fed straight into the defrost derate.
            "power": self._commanded_power(),
            "space_power": float(self._current_action.get("power", 0.0)),
            "dhw_power": float(self._current_action.get("dhw_power", 0.0)),
            # T6: why the plan wanted this interval's draw, captured at
            # prediction time — the plan that commanded the draw, not
            # whatever plan exists when the interval settles.
            "space_reason": self._current_action.get("space_reason"),
            "dhw_reason": self._current_action.get("dhw_reason"),
            "price": self._get_current_price(),
            # The third fee-chokepoint site (#1): the settlement books spot
            # and fee as separate lines, so the ledger can itemise the bill
            # while "price" above stays what the kWh actually cost.
            "spot_price": self._current_spot_price(),
            "grid_fee": self._current_grid_fee(now),
            "predicted_temp": self._predicted_next_room_temp(),
            "outdoor": self._current_state.outdoor_temperature,
            "humidity": self._current_humidity(),
            # T6 #52: the assumptions this interval starts under, for the
            # diagnosis re-run when it settles.
            "diag": self._capture_diagnosis_inputs(),
        }

    def _dhw_probe_temperature(self) -> float | None:
        """The tank's MEASURED temperature, or ``None`` when there is none.

        ``_current_state.dhw_temperature`` cannot answer this. It carries a
        55 °C modelling default, and ``_update_current_state`` deliberately
        PINS the last good value when a read fails, so on a house with no
        tank probe it reads as a perfectly steady 55 °C — which would train
        the hot-water record on a constant and draw a confidence band around
        a measurement that does not exist.

        Three gates, in order.

        1. The entity must be configured at all. Said plainly: today this is
           belt and braces, because ``_dhw_temperature`` is only ever
           assigned from an ``ok`` reading and gate 2 already answers an
           unconfigured house. It is here for the OTHER tank temperature in
           this class — ``_current_state.dhw_temperature``, the 55 °C
           modelling default, which the coordinator does fall back to
           elsewhere. One such fallback reaching this probe would train the
           record on a constant and report a flawless model. Note that
           ``_learning_frozen`` cannot stand in for it: an unconfigured slot
           must never freeze learning, so it answers None here.
        2. A value must have been read at least once.
        3. This interval must not be one the learners would refuse. That is
           the v5.1.3 discipline — freeze on ANY unusable configured input,
           not only a stale one — reached through the same predicate
           ``_async_learn_dhw_dynamics`` uses, so the accuracy record and the
           tank's own learners admit exactly the same intervals.
        """
        if not self._config.get(CONF_DHW_TEMP_ENTITY):
            return None
        raw = self._dhw_temperature
        if raw is None:
            return None
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        if not np.isfinite(value):
            return None
        if self._learning_frozen(CONF_DHW_TEMP_ENTITY) is not None:
            return None
        return value

    def _file_dhw_lead_predictions(
        self, result, solve_time: datetime, dt_h: float
    ) -> None:
        """v5.2.0: the plan's tank-temperature promises, per lead bucket.

        Gated on a usable probe at FILING time as well as at scoring time.
        A promise filed while the tank is unmeasured could only ever be
        settled against the model's own default, which would teach the
        record that the model is flawless and draw a hairline band on a
        house that has no evidence at all.
        """
        if self._dhw_probe_temperature() is None:
            return
        trajectory = result.dhw_temp_trajectory
        if not trajectory:
            return
        for lead in LEAD_BUCKETS:
            idx = int(round(lead / dt_h))
            if 0 < idx < len(trajectory):
                self._dhw_accuracy.note_lead_prediction(
                    solve_time + timedelta(hours=lead),
                    lead,
                    float(trajectory[idx]),
                )

    def _file_lead_predictions(self, result, solve_time: datetime) -> None:
        """T5 #16: file the plan's room-temperature promises per lead bucket.

        Same mode gate and same trajectory convention as the one-step
        accuracy sample: only a plan that is actually running makes
        promises worth scoring, and in two-zone mode the indoor sensor the
        score will use reads the upper floor.
        """
        if self._mode not in (MODE_AUTO, MODE_ECONOMY):
            return
        if self._sysid.active:
            # A step-response experiment overrides the plan for its
            # duration, so the plan's promises are fiction while it runs —
            # and any already on file were made by a plan the experiment
            # is about to override.
            self._accuracy.lead_pending.clear()
            self._dhw_accuracy.lead_pending.clear()
            return
        dt_h = max(self._opt_config.time_step_minutes, 1.0) / 60.0
        # Filed first, so a plan with no room trajectory to promise about
        # (the early return below) does not also silence the tank's record.
        self._file_dhw_lead_predictions(result, solve_time, dt_h)
        trajectory = (
            result.upper_temp_trajectory
            if self._thermal_params.two_zone_enabled
            and result.upper_temp_trajectory
            else result.room_temp_trajectory
        )
        if not trajectory:
            return
        for lead in LEAD_BUCKETS:
            idx = int(round(lead / dt_h))
            if 0 < idx < len(trajectory):
                self._accuracy.note_lead_prediction(
                    solve_time + timedelta(hours=lead),
                    lead,
                    float(trajectory[idx]),
                )

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

        # T6 #40: a settlement landing in a new month means the old month
        # just closed — freeze its receipt before anything else books.
        self._roll_month(when)

        # The månadsspot shadow column (#23) settles on the month's *average*
        # spot price, so the average must sample every interval — including
        # the ones where nothing was consumed. Before the energy gate below.
        self._ledger.observe_meta_mean(when, "spot_price", spot)

        actual = sample.actual_power_kw
        if actual is None:
            actual = planned_total
        energy = max(0.0, actual * elapsed_hours)
        # T6 #65: the operation score's day book samples every interval
        # too — the flat-consumer baseline it replays against is the
        # time-mean spot price, idle hours included, but only hours whose
        # price was actually known.
        self._fold_score_sample(
            when,
            energy,
            energy * spot,
            spot,
            elapsed_hours,
            pending.get("spot_price") is not None,
        )
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
        # Per-channel monthly lines, so the accumulators can state a period
        # smaller than "lifetime" without a second store. Same numbers the
        # accumulators just folded, booked where the month's other receipts
        # live; the wear and immersion lines below book the same way.
        self._ledger.add(
            when, "dhw", kwh=dhw_energy, sek=dhw_energy * price
        )
        self._ledger.add(
            when, "space", kwh=space_energy, sek=space_energy * price
        )

        # The monthly ledger (T1): spot and DSO fee booked as separate lines,
        # so every later SEK claim can reconcile against the month's
        # receipts, and the fee never contaminates the spot column the
        # contract comparison settles on.
        fee = _as_float(pending.get("grid_fee"), 0.0)
        # T4a #11: while the immersion element runs, the draw beyond what
        # the plan commanded is resistive heat. Its kWh are CARVED OUT of
        # the spot line, not booked on top of it — the lines must sum to
        # the metered energy, or every cross-line total overstates. The
        # fee line keeps the full energy: resistive kWh pay the grid fee
        # like any other.
        immersion_excess = 0.0
        if (
            self._immersion_active
            and sample.actual_power_kw is not None
            and sample.actual_power_kw > planned_total
        ):
            immersion_excess = min(
                energy,
                max(
                    0.0,
                    (sample.actual_power_kw - planned_total) * elapsed_hours,
                ),
            )
        metered = energy - immersion_excess
        self._ledger.add(when, "spot", kwh=metered, sek=metered * spot)
        # T6: the same metered kWh again, partitioned by WHY the plan drew
        # them — the space share under the space slot's reason, the DHW
        # share under the DHW slot's. A partition, not a bonus column: the
        # reason lines must sum to the spot line, or every receipt built
        # from them overstates. An interval without a tag (manual modes, a
        # restart before the first solve) books as "untagged" rather than
        # vanishing from the total.
        space_reason = pending.get("space_reason") or "untagged"
        dhw_reason = pending.get("dhw_reason") or "untagged"
        metered_dhw = metered * dhw_share
        metered_space = metered - metered_dhw
        if metered_space > 1e-9:
            self._ledger.add(
                when,
                f"reason:{space_reason}",
                kwh=metered_space,
                sek=metered_space * spot,
            )
        if metered_dhw > 1e-9:
            self._ledger.add(
                when,
                f"reason:{dhw_reason}",
                kwh=metered_dhw,
                sek=metered_dhw * spot,
            )
        if fee:
            self._ledger.add(when, "grid_fee", kwh=energy, sek=energy * fee)
        if immersion_excess > 1e-6:
            self._ledger.add(
                when,
                "immersion",
                kwh=immersion_excess,
                sek=immersion_excess * spot,
            )
        self._schedule_ledger_save()

    def _contract_comparison(self, month: str | None = None) -> dict[str, Any]:
        """This month's metered consumption settled under each contract (#23).

        ``month`` defaults to the current month; the month-freeze receipt
        (T6 #40) passes the month that just closed so the shadow settlement
        in the receipt is the closed month's, not the new month's empty one.

        Hourly spot is what Tibber actually bills; monthly-average spot
        (månadsspot) is the same kWh at the month's mean spot price; fixed is
        the configured contract price. The "load profile value" is the
        öre/kWh the optimizer's shifting earns below the flat-consumer
        average — a household on månadsspot gains nothing from hourly
        shifting, and this is the proof, either way.
        """
        month = month or month_key(dt_util.now())
        spot_line = self._ledger.line(month, "spot")
        # The immersion line is spot-priced energy carved out of "spot"
        # for visibility (#11); the settlement is over ALL metered kWh,
        # so it folds back in here.
        imm_line = self._ledger.line(month, "immersion")
        kwh = spot_line["kwh"] + imm_line["kwh"]
        spot_cost = spot_line["sek"] + imm_line["sek"]
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
    # Insight (v4.0.0 T6): wear, receipts, scores, narrative, tiles
    # ==================================================================

    def _wear_price(self) -> float:
        """SEK one compressor start costs (#55). 0 until the user prices it."""
        return wear_price_per_start(
            _as_float(
                self._config.get(CONF_COMPRESSOR_REPLACEMENT_COST),
                DEFAULT_COMPRESSOR_REPLACEMENT_COST,
            ),
            int(
                _as_float(
                    self._config.get(CONF_COMPRESSOR_RATED_STARTS),
                    DEFAULT_COMPRESSOR_RATED_STARTS,
                )
            ),
        )

    def _effective_cycling_cost(self) -> float:
        """#55 (gated): the cycling penalty, floored by realised wear.

        max(), never replace — a user who priced chatter ABOVE the
        datasheet wear keeps their number; the autotune only stops the
        penalty understating a cost the user has made explicit through
        the replacement fields. With the flag off this is exactly the
        configured value.
        """
        cost = _as_float(
            self._config.get(CONF_CYCLING_COST), DEFAULT_CYCLING_COST
        )
        if bool(
            self._config.get(
                CONF_WEAR_AUTOTUNE_ENABLED, DEFAULT_WEAR_AUTOTUNE_ENABLED
            )
        ):
            cost = max(cost, self._wear_price())
        return cost

    def _observe_compressor_start(self, now: datetime) -> None:
        """#55: fold one measured-power sample into the start counter.

        The threshold is the optimizer's own on/off convention (half the
        pump's minimum electrical power), so the counter and the plan agree
        about what "running" means. Immersion intervals are the #11
        classifier's, never the compressor's.
        """
        started = self._start_counter.observe(
            now,
            self._measured_power,
            max(0.1, 0.5 * self._thermal_params.min_electrical_power),
            self._immersion_active,
        )
        if started:
            wear = self._wear_price()
            if wear > 0:
                # kwh 0 by design: the wear line is money, not energy, and
                # a receipt that adds wear kWh to metered kWh double-counts.
                self._ledger.add(now, "wear", kwh=0.0, sek=wear)
            self._schedule_ledger_save()

    def _roll_month(self, when: datetime) -> None:
        """#40: freeze receipts for months that have closed.

        Derived from the ledger itself rather than a "last month seen"
        marker: any ledger month strictly before the current one that has
        no frozen receipt yet gets one now. Self-healing across restarts
        and downtime spanning a month end — and bounded, because the
        ledger prunes itself and each month freezes exactly once.
        """
        current = month_key(when)
        closed = sorted(
            key
            for key in self._ledger.months
            if key < current and key not in self._month_reports
        )
        for month in closed:
            # Defense in depth: MonthlyLedger.from_dict already quarantines
            # malformed months at load time, but a still-live month can in
            # principle be freezable-yet-broken (a bug in this file, not the
            # ledger's shape). Never let one bad month wedge every future
            # cycle forever (#D1-01) -- skip it and mark it closed with an
            # empty receipt so the cycle completes and it is not retried.
            try:
                self._month_reports[month] = self._freeze_month_report(month)
            except Exception:  # noqa: BLE001 -- must never wedge the coordinator
                _LOGGER.warning(
                    "Skipping malformed ledger month %s while freezing "
                    "monthly receipts; recording an empty receipt instead",
                    month,
                    exc_info=True,
                )
                self._month_reports[month] = {"month": month, "lines": {}}
        if closed:
            # Receipts follow the ledger's retention; a receipt for a month
            # the ledger no longer holds cannot be reconciled anyway.
            extra = sorted(self._month_reports)[
                : max(0, len(self._month_reports) - KEEP_MONTHS)
            ]
            for old in extra:
                del self._month_reports[old]
            self._schedule_ledger_save()

    def _freeze_month_report(self, month: str) -> dict[str, Any]:
        """One month's itemised receipt, frozen at rollover (#40).

        Everything in it comes from the ledger's own lines — the receipt is
        a PRESENTATION of the accounting, never a second accounting. The
        reason lines partition the spot line by construction, and the
        receipt states how well that held rather than assuming it.
        """
        lines = self._ledger.month_summary(month)
        reasons = {
            name.split(":", 1)[1]: entry
            for name, entry in lines.items()
            if name.startswith("reason:")
        }
        # Reconcile on the RAW ledger values, not the rounded publication
        # ones: with a full reason set the accumulated 2-decimal rounding
        # alone can exceed the tolerance and cry wolf on a perfectly
        # partitioned month.
        raw_lines = self._ledger.months.get(month, {}).get("lines", {})
        reason_kwh = sum(
            self._ledger.line(month, name)["kwh"]
            for name in raw_lines
            if name.startswith("reason:")
        )
        reason_sek = sum(
            self._ledger.line(month, name)["sek"]
            for name in raw_lines
            if name.startswith("reason:")
        )
        raw_spot = self._ledger.line(month, "spot")
        spot = lines.get("spot", {"kwh": 0.0, "sek": 0.0})
        report: dict[str, Any] = {
            "month": month,
            "lines": {
                name: entry
                for name, entry in lines.items()
                if not name.startswith("reason:")
            },
            "reasons": reasons,
            "total_kwh": round(
                spot["kwh"] + lines.get("immersion", {}).get("kwh", 0.0), 3
            ),
            "total_sek": round(
                sum(entry["sek"] for entry in lines.values() if entry)
                - reason_sek,
                2,
            ),
            "compressor_starts": self._start_counter.month_count(month),
            "contract_comparison": self._contract_comparison(month),
            # The partition check, published instead of asserted: a receipt
            # that hides its own bookkeeping error is worse than one that
            # admits it. None, not False, for a month with no reason lines
            # at all — a pre-T6 month never had a partition to break, and
            # publishing "failed" for it would make an upgrade look like
            # the very bug the flag exists to expose.
            "reasons_reconcile": (
                bool(
                    abs(reason_kwh - raw_spot["kwh"]) <= 0.05
                    and abs(reason_sek - raw_spot["sek"]) <= 0.05
                )
                if reasons
                else None
            ),
        }
        mean_spot = self._ledger.meta_mean(month, "spot_price")
        if mean_spot is not None:
            report["mean_spot_price"] = round(mean_spot, 4)
        return report

    def _fold_score_sample(
        self,
        when: datetime,
        kwh: float,
        sek: float,
        spot: float,
        elapsed_hours: float,
        spot_known: bool,
    ) -> None:
        """#65's operation evidence: today's kWh, SEK and spot samples.

        The day closes on the first sample of the next day — the daily
        replay against realised prices happens exactly once per day, on
        numbers the ledger already settled. The SEK fold is SIGNED: a
        negative-price hour where the consumer was paid must lower the
        day's mean paid price, not be zeroed away. The flat-consumer
        baseline is time-weighted and samples only intervals whose spot
        price was actually known — a missing price settling at the 0.0
        default would otherwise drag the baseline toward free electricity
        and flatter every real day.
        """
        day = when.date().isoformat()
        book = self._score_day
        if book.get("day") and book["day"] != day:
            self._close_score_day()
            book = self._score_day
        if not book.get("day"):
            book.update(
                {"day": day, "kwh": 0.0, "sek": 0.0, "spot_sum": 0.0, "spot_h": 0.0}
            )
        book["kwh"] = _as_float(book.get("kwh"), 0.0) + max(0.0, kwh)
        book["sek"] = _as_float(book.get("sek"), 0.0) + (
            sek if np.isfinite(sek) else 0.0
        )
        if spot_known and np.isfinite(spot) and elapsed_hours > 0:
            book["spot_sum"] = (
                _as_float(book.get("spot_sum"), 0.0) + spot * elapsed_hours
            )
            book["spot_h"] = _as_float(book.get("spot_h"), 0.0) + elapsed_hours

    def _close_score_day(self) -> None:
        """Replay yesterday against its own realised prices, fold the score.

        The replay: the same kWh bought flat at the day's time-mean spot
        price is what a non-shifting consumer pays. Buying 20 % below that
        scores 100; buying at or above it scores 0. Days with too little
        energy or price signal teach nothing and are skipped, not scored.
        """
        book = self._score_day
        self._score_day = {}
        kwh = _as_float(book.get("kwh"), 0.0)
        hours = _as_float(book.get("spot_h"), 0.0)
        if kwh < 1.0 or hours < 1.0:
            return
        mean_spot = _as_float(book.get("spot_sum"), 0.0) / hours
        if mean_spot <= 0.01:
            # Free or negative-price days make the ratio meaningless; a
            # score of "you saved nothing off zero" is not evidence.
            return
        paid_mean = _as_float(book.get("sek"), 0.0) / kwh
        saved_fraction = 1.0 - paid_mean / mean_spot
        sample = float(np.clip(saved_fraction / 0.2, 0.0, 1.0)) * 100.0
        if self._operation_score is None:
            self._operation_score = sample
        else:
            self._operation_score = (
                (1.0 - SCORE_ALPHA) * self._operation_score + SCORE_ALPHA * sample
            )
        self._schedule_ledger_save()

    def _scores_view(self) -> dict[str, Any]:
        """#65: envelope, machine and operation on one 0–100 scale.

        Each score answers a different question — how good is the house,
        how healthy is the machine, how well is it being driven — so a low
        overall points at its own cause. None means "no evidence yet",
        never "zero": a fresh install has no grades, not failing ones.
        """
        envelope = None
        loss = (
            self._thermal_params.heat_loss_coefficient
            * max(self._thermal_params.house_heat_loss_scale, 0.1)
        )
        if loss > 1e-6 and self._thermal_params.room_thermal_mass > 0:
            # The house's time constant in hours: how long the stored heat
            # lasts against the losses. ~20 h is a leaky house, ~100 h a
            # well-insulated one; the learned loss scale keeps the grade
            # honest about the house as measured, not as configured.
            tau_h = self._thermal_params.room_thermal_mass / loss
            envelope = float(np.clip((tau_h - 20.0) / 80.0, 0.0, 1.0)) * 100.0

        machine = None
        watched = sum(
            1
            for entry in self._cop_baseline.values()
            if int(entry[1]) >= COP_BASELINE_MIN_SAMPLES
        )
        if watched:
            # 100 while the COP watch (#12) accumulates no shortfall; the
            # grade falls as the Cusum climbs toward its alarm.
            machine = (
                1.0
                - float(
                    np.clip(
                        self._cop_health_cusum.stat / COP_HEALTH_THRESHOLD,
                        0.0,
                        1.0,
                    )
                )
            ) * 100.0

        operation = self._operation_score
        available = [s for s in (envelope, machine, operation) if s is not None]
        return {
            "envelope": round(envelope, 1) if envelope is not None else None,
            "machine": round(machine, 1) if machine is not None else None,
            "operation": round(operation, 1) if operation is not None else None,
            "overall": (
                round(float(np.mean(available)), 1) if available else None
            ),
        }

    def _narrative_view(self) -> dict[str, Any]:
        """#29: the current plan grouped by reason, with rendered lines."""
        result = self._optimization_result
        if result is None or not result.timestamps:
            return {"items": [], "lines": [], "language": "en"}
        dt_hours = max(self._opt_config.time_step_minutes, 1.0) / 60.0
        prices = list(result.prices or [])
        items = narrative.build(
            {
                "powers": list(result.power_schedule or []),
                "prices": prices,
                "reasons": list(result.space_reasons or []),
            },
            {
                "powers": list(result.dhw_power_schedule or []),
                "prices": prices,
                "reasons": list(result.dhw_reasons or []),
            },
            dt_hours,
        )
        language = str(
            getattr(getattr(self.hass, "config", None), "language", "en") or "en"
        )
        # The narrative speaks the languages it has parity for; anything
        # else falls back to English rather than to silence.
        short = language.split("-")[0].lower()
        chosen = short if short in narrative.TEMPLATES else "en"
        return {
            "items": items,
            "lines": narrative.render(items, chosen),
            "language": chosen,
        }

    def _capture_diagnosis_inputs(self) -> dict[str, Any] | None:
        """#52: what the plan assumed for the interval now starting.

        Captured at prediction time next to the accuracy pending sample,
        because a diagnosis re-run against inputs remembered any later
        would attribute the residual against assumptions the plan never
        made.
        """
        try:
            state = replace(self._current_state)
        except Exception:  # noqa: BLE001 - diagnosis is best-effort evidence
            return None
        now = dt_util.now()
        try:
            planned_wind, _ = self._current_weather()
        except Exception:  # noqa: BLE001 - wind is optional evidence
            planned_wind = 0.0
        return {
            "state": state,
            "planned": {
                # The SPACE channel only: simulate_step's electrical_power
                # heats the house, not the tank. Handing it the commanded
                # total would charge every DHW charge to room heating.
                "electrical_power": float(
                    self._current_action.get("power") or 0.0
                ),
                "outdoor_temp": self._current_state.outdoor_temperature,
                "wind_speed": planned_wind,
                "solar_radiation": self._current_state.solar_radiation,
                "external_heat_kw": 0.0,
                "humidity": self._current_humidity(),
                "hour_of_day": now.hour + now.minute / 60.0,
            },
        }

    def diagnose_last_interval(self) -> dict[str, Any] | None:
        """#52: attribute the last settled interval's residual, input by input.

        Runs on the LAST SETTLED interval, not live state: attribution
        needs a completed (planned, realised, actual) triple, and the
        freshest one is the interval the accuracy sample just closed.
        """
        report = diagnosis.diagnose_record(
            self._last_interval_record, self._thermal_params
        )
        if report is not None:
            self._last_diagnosis = report
        return report

    async def async_diagnose_interval(self) -> None:
        """Service/button entry for #52; publishes on the insight view."""
        report = await _await_process(
            self.hass,
            diagnosis.diagnose_record,
            *_diagnose_payload(self),
        )
        _store_diagnosis(self, report)
        if report is None:
            _LOGGER.info(
                "No settled interval to diagnose yet — one full "
                "optimization interval must pass first"
            )
        await self.async_request_refresh()

    def _price_tile_specs(self) -> list[tuple[str, dict[str, Any]]]:
        """#39's fixed perturbation set. Fixed on purpose: tiles answer the
        same three questions every day, so their day-to-day drift means the
        situation changed, not the question.

        The target tiles perturb the LIVE target — the one the baseline
        plan the what-if is compared against actually used. During an away
        setback the configured target would make "one degree lower" a
        raise against the setback plan, and the published trade would
        carry the wrong sign.
        """
        target = float(self._opt_config.target_temp)
        return [
            ("target_minus_1", {"target_temp": round(target - 1.0, 1)}),
            ("target_plus_1", {"target_temp": round(target + 1.0, 1)}),
            (
                "power_cap_75",
                {
                    "power_cap_kw": round(
                        0.75 * self._thermal_params.max_electrical_power, 2
                    )
                },
            ),
        ]

    async def _maybe_refresh_price_tile(self) -> None:
        """#39 (gated): refresh ONE tile after a scheduled solve.

        One per solve, rotating, so the whole set costs at most one extra
        solve per interval — and through ``async_simulate``'s own solve
        path and executor, never a second one. The tile borrows the card's
        harness the way the fuse advisor does: rate-limit slot and cache
        snapshot-restored, so a card drag right after a solve neither gets
        rate-limited by the tile nor reads the tile's payload back as its
        own answer. When the limiter says no (the user dragged first), the
        tile waits for the next interval; the card's budget wins in both
        directions.
        """
        if not bool(
            self._config.get(CONF_PRICE_TILES_ENABLED, DEFAULT_PRICE_TILES_ENABLED)
        ):
            # Gate off means gone: stale what-if money left published
            # would outlive the user's decision to stop paying for it.
            if self._price_tiles:
                self._price_tiles.clear()
            return
        specs = self._price_tile_specs()
        name, overrides = specs[self._price_tile_cursor % len(specs)]
        cache_snapshot = (self._last_simulation, self._simulation_cache)
        try:
            answer = await self.async_simulate(dict(overrides))
        except Exception as err:  # noqa: BLE001 - tiles are decoration
            _LOGGER.debug("Price tile %s failed: %s", name, err)
            # A consistently failing spec must not block the other tiles:
            # move on and retry it on the rotation's next pass.
            self._price_tile_cursor += 1
            return
        finally:
            self._last_simulation, self._simulation_cache = cache_snapshot
        if answer.get("rate_limited"):
            return
        self._price_tile_cursor += 1
        if answer.get("error"):
            return
        self._price_tiles[name] = {
            "overrides": overrides,
            "monthly_cost_delta": answer.get("monthly_cost_delta"),
            "min_room_temperature": answer.get("min_room_temperature"),
            "computed_at": dt_util.now().isoformat(timespec="seconds"),
        }

    def _insight_view(self) -> dict[str, Any]:
        """Everything T6 publishes, in one additive block."""
        return {
            "narrative": self._narrative_view(),
            "scores": self._scores_view(),
            "compressor_starts": {
                "lifetime": self._start_counter.lifetime,
                "month": self._start_counter.month_count(
                    month_key(dt_util.now())
                ),
                "wear_price_per_start": round(self._wear_price(), 4),
            },
            "monthly_report": (
                self._month_reports[max(self._month_reports)]
                if self._month_reports
                else None
            ),
            "price_tiles": dict(self._price_tiles),
            "last_diagnosis": self._last_diagnosis,
        }

    # ==================================================================
    # Inverter frequency (v4.0.0 T7 #61)
    # ==================================================================

    def _freq_entity_reading(self) -> tuple[float | None, float, float]:
        """(reported Hz, range min, range max) for #61.

        The range comes from the number entity's OWN min/max attributes —
        the hardware integration knows its register limits; guessing them
        here would let a clamp "protect" the pump into an invalid write.
        The REPORTED frequency prefers the separate actual-frequency
        sensor when one is configured: a number entity is often a setpoint
        register that echoes the last written value, and feedback read
        from an echo can never diverge — the watchdog would be decorative
        and the map would learn against a frozen setpoint.
        """
        entity_id = self._config.get(CONF_COMPRESSOR_FREQ_ENTITY)
        if not entity_id:
            return (None, 0.0, 0.0)
        state = self.hass.states.get(entity_id)
        if state is None:
            return (None, 0.0, 0.0)
        attrs = getattr(state, "attributes", {}) or {}
        hz_min = _as_float(attrs.get("min"), 20.0)
        hz_max = _as_float(attrs.get("max"), 120.0)
        source = state
        sensor_id = self._config.get(CONF_COMPRESSOR_FREQ_SENSOR)
        if sensor_id:
            sensor_state = self.hass.states.get(sensor_id)
            if sensor_state is None:
                # A configured but unavailable feedback sensor must not
                # silently fall back to the echoing setpoint: that would
                # quietly re-decorate the watchdog exactly when the real
                # feedback disappeared.
                return (None, hz_min, hz_max)
            source = sensor_state
        try:
            reported = float(source.state)
        except (TypeError, ValueError):
            reported = None
        if reported is not None and not np.isfinite(reported):
            reported = None
        return (reported, hz_min, hz_max)

    def _freq_mode(self) -> str:
        """The stage actually in force, not the one merely configured.

        Control requires ALL of: the entity, the explicit opt-in, and a
        watchdog that has not stood the controller down. Everything else
        is observe — and without an entity there is nothing to observe.
        """
        if not self._config.get(CONF_COMPRESSOR_FREQ_ENTITY):
            return "unconfigured"
        configured = str(
            self._config.get(CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE)
        )
        if configured == FREQ_MODE_CONTROL and not self._freq_fallback:
            return FREQ_MODE_CONTROL
        return FREQ_MODE_OBSERVE

    def _observe_frequency(self, now: datetime) -> None:
        """One cycle of #61: watchdog first, then the kW-per-Hz fold.

        The learning fold skips immersion intervals (#11 owns resistive
        draw — folding it would teach the map that some frequency draws
        the element's kilowatts), but the watchdog never skips: divergence
        evidence is about the write path, not about what the meter reads.
        """
        configured = str(
            self._config.get(CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE)
        )
        if (
            configured != FREQ_MODE_CONTROL
            or not self._config.get(CONF_COMPRESSOR_FREQ_ENTITY)
        ) and self._freq_fallback:
            # The user switched back to observe — or removed the entity
            # entirely, which unconfigures the feature just as explicitly.
            # Either is the acknowledgement that re-arms the latch and
            # retires its repair issue; a restart alone never clears it,
            # and without this clause a cleared entity would orphan both
            # forever behind a mode selector nothing renders any more.
            self._freq_fallback = False
            self._freq_watchdog.reset()
            ir.async_delete_issue(self.hass, DOMAIN, "freq_watchdog")
            self._spawn(self._async_save_thermal_learning())
        reported, hz_min, hz_max = self._freq_entity_reading()
        if reported is None:
            return
        if configured == FREQ_MODE_CONTROL and not self._freq_fallback:
            # Divergence is only meaningful while the plan is actually
            # asking for the compressor AND the reading is in its running
            # range: an idle pump reading 0 Hz overnight, or one pausing
            # for a defrost, is an operating point at rest, not a write
            # path that stopped listening — three cycles of routine MPC
            # idle must not stand control down.
            watch_active = (
                self._commanded_power() > 0.05 and reported >= hz_min
            )
            if self._freq_watchdog.note_report(reported, active=watch_active):
                # Three consecutive divergent ticks: the hardware is not
                # actually listening (wrong register, protective mode, a
                # write path that silently drops). Stand down and say so;
                # the latch survives restarts.
                self._freq_fallback = True
                self._spawn(self._async_save_thermal_learning())
                entity_id = str(
                    self._config.get(CONF_COMPRESSOR_FREQ_ENTITY) or ""
                )
                _LOGGER.warning(
                    "Compressor frequency control stood down: %s reports "
                    "%.1f Hz against a commanded %.1f Hz for %d ticks",
                    entity_id,
                    reported,
                    self._freq_watchdog.commanded or 0.0,
                    self._freq_watchdog.strikes,
                )
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    "freq_watchdog",
                    is_fixable=False,
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="freq_watchdog",
                    translation_placeholders={"entity": entity_id},
                )
        if self._measured_power is None or self._immersion_active:
            return
        self._freq_map.observe(
            reported, float(self._measured_power), hz_min, hz_max
        )

    async def _command_frequency(self) -> None:
        """The control stage's single write path — every rail in one place.

        Rate-limited to one write per five minutes, clamped to the
        entity's own range, deduplicated against the last command, and a
        map with no evidence writes NOTHING: None is never a frequency.
        """
        entity_id = self._config.get(CONF_COMPRESSOR_FREQ_ENTITY)
        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL:
            return
        _reported, hz_min, hz_max = self._freq_entity_reading()
        target = self._freq_map.recommend(
            self._commanded_power() or 0.0, hz_min, hz_max
        )
        if target is None:
            return
        target = float(np.clip(target, hz_min, hz_max))
        now = dt_util.now()
        if (
            self._freq_last_write is not None
            and (now - self._freq_last_write).total_seconds()
            < FREQ_WRITE_MIN_INTERVAL_S
        ):
            return
        if (
            self._freq_watchdog.commanded is not None
            and abs(target - self._freq_watchdog.commanded)
            < FREQ_WRITE_EPSILON_HZ
        ):
            return
        try:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": entity_id, "value": round(target, 1)},
                blocking=True,
            )
        except Exception as err:  # noqa: BLE001 - never break the cycle
            _LOGGER.error("Error commanding compressor frequency: %s", err)
            return
        self._freq_last_write = now
        self._freq_watchdog.note_command(target)
        _LOGGER.info(
            "Commanded compressor frequency %.1f Hz via %s", target, entity_id
        )

    def _freq_view(self) -> dict[str, Any]:
        """#61's publication: the map, the stage, and what control WOULD do.

        The recommendation publishes in observe mode too — that is the
        observe stage's entire product: evidence for the user's go/no-go
        before any wire is touched.
        """
        reported, hz_min, hz_max = self._freq_entity_reading()
        mode = self._freq_mode()
        recommended = None
        exhausted = False
        if mode != "unconfigured":
            target = self._commanded_power() or 0.0
            recommended = self._freq_map.recommend(target, hz_min, hz_max)
            # "Running flat out on faith" must be visible: the flat-out
            # answer above the map's evidence is deliberate, but the user
            # deserves to see when it is extrapolation, not knowledge.
            exhausted = self._freq_map.evidence_exhausted(
                target, hz_min, hz_max
            )
        return {
            "mode": mode,
            "fallback_active": bool(self._freq_fallback),
            "reported_hz": reported,
            "recommended_hz": recommended,
            "evidence_exhausted": exhausted,
            "commanded_hz": self._freq_watchdog.commanded,
            "range_hz": (
                [round(hz_min, 1), round(hz_max, 1)]
                if mode != "unconfigured"
                else None
            ),
            "map": (
                self._freq_map.summary(hz_min, hz_max)
                if mode != "unconfigured"
                else {}
            ),
        }

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
        mean_price = float(np.mean([_as_float(p, 0.0) for p in prices]))
        # Spot on BOTH sides of the ratio: the denominator is a mean over raw
        # Tibber entries, so a fee-inclusive numerator (T1's #1) would inflate
        # every override's price-weight by the fee regardless of hour.
        # A near-zero or negative mean has no "relative price" to learn
        # from — a negative denominator flips the sign, filing an
        # expensive-hour override as a cheap-hour complaint, and a tiny one
        # lets a single override swamp the learner. Recorded neutral
        # instead, same guard style as ``_record_quiet_comfort_period``.
        relative = (
            self._current_spot_price() / mean_price
            if mean_price > 1e-6
            else 1.0
        )
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
        """Advance sysid and override the plan when the experiment commands heat.

        Subject to the mode gate and pump freeze like every other power path.
        Writes ``_current_action["power"]`` after the solve — the one route
        that bypasses mode bounds — so a response measured while cooling,
        faulted or offline seeds wrong parameters via ``_adopt_system_identification``.
        """
        if not self._sysid.active:
            return
        if self._pump_signals.space_blocked:
            self._sysid.abort(
                f"heat pump mode {self._pump_signals.mode.label} cannot heat "
                "the house"
            )
            return
        if self._pump_signals.freeze_reason is not None:
            self._sysid.abort(self._pump_signals.freeze_reason)
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
            plan_power_kw=float(self._current_action.get("power", 0.0)),
            house_ua=(
                self._thermal_params.heat_loss_coefficient
                * self._thermal_params.house_heat_loss_scale
            ),
            house_capacity=self._thermal_params.room_thermal_mass,
            house_gains=self._thermal_params.internal_gains,
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
            # T6: the experiment's draw is not the plan's — settling it
            # under the overridden plan's reason would book experiment
            # energy as "cheapest hours" or whatever the plan happened to
            # claim for this step.
            "space_reason": None,
            "dhw_reason": None,
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
        self._spawn(self._async_save_thermal_learning())
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
            # The slab's ceiling is the optimizer's settlement cap, not a
            # comfort offset: heat above the temperature that sustains the
            # target is heat the plan can never spend, so counting it as
            # capacity overstates the store. Read at the outdoor temperature
            # in force now — the view is a snapshot of the house as it stands,
            # like every other figure in it.
            slab_max=slab_settlement_cap(
                params,
                self._opt_config.target_temp,
                self._current_state.outdoor_temperature,
            ),
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

        # Same shared-instant discipline as the live solve: the shadow
        # solve's anchor and its arrays must not straddle a quarter
        # boundary, or its predicted_cost stops being comparable to the
        # plan it is differenced against below.
        horizon = self._forecast_arrays(now)
        if len(horizon.prices) < 4:
            return {"error": "no_prices", "rate_limited": False}

        # #240: ``replace`` copies scalars and shares the rest by reference,
        # so the what-if carried the LIVE learner, draw pattern and windows
        # into the executor, where ``observe`` could write them mid-solve.
        scratch_config = copy.deepcopy(self._opt_config)
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

        scratch_params = copy.deepcopy(self._thermal_params)
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
                scratch_params.dhw_weekly_windows = None
            else:
                try:
                    scratch_params.dhw_windows = parse_windows(spec)
                    scratch_params.dhw_weekly_windows = parse_weekly_windows(spec)
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
            simulated = await _await_optimize(
                self.hass,
                scratch,
                # Shallow deliberately: ``ThermalState`` is scalars only.
                replace(self._current_state),
                horizon.prices,
                horizon.outdoor_temps,
                horizon.wind_speeds,
                horizon.precipitation,
                horizon.solar_radiation,
                self._solve_anchor(now),
                horizon.price_known,
                horizon.pv_surplus,
                # The scratch config inherits price_risk_lambda, so the
                # what-if must price guessed steps the same way the plan
                # it is compared against did (#34).
                price_sigma=horizon.price_sigma,
                power_caps_extra=cap_extra,
                # #21: the what-if is compared against a plan that saw
                # the humidity series, so it must see the same one.
                humidity=(
                    horizon.humidity
                    if horizon.humidity.size
                    and bool(np.any(np.isfinite(horizon.humidity)))
                    else None
                ),
                # T5: same floors as the live plan, same reasoning —
                # except the mold cap follows the SIMULATED target, so
                # a what-if dragging the target down sees the floor
                # that choice would actually get.
                min_temp_margins=self._confidence_margins(
                    len(horizon.prices)
                ),
                min_temp_floors=self._mold_floor_series(
                    horizon.outdoor_temps,
                    target_cap=float(scratch_config.target_temp),
                ),
                # v5.3.0: and the mode block, for the same reason as
                # every inherited input above — the what-if is
                # DIFFERENCED against the live plan, so anything that
                # shaped the live plan and not the shadow one turns the
                # difference into a comparison of two different
                # questions. This one is the worst of them: the live
                # plan under a block heats nothing, so an unblocked
                # shadow solve looks warmer than its own baseline,
                # ``base_cold - sim_cold`` goes negative, and the fuse
                # advisor's clamp turns a real comfort breach into
                # "feasible" — a published recommendation to fit a
                # smaller main fuse.
                space_blocked=self._pump_signals.space_blocked,
                dhw_blocked=self._pump_signals.dhw_blocked,
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


# The typed config entry (runtime-data, Bronze): ``entry.runtime_data`` is the
# entry's coordinator from ``async_setup_entry`` until Home Assistant unloads
# the entry. Platforms and service handlers annotate with this and read the
# coordinator from the entry, never from ``hass.data``.
HeatPumpOptimizerConfigEntry = ConfigEntry[HeatPumpOptimizerCoordinator]
