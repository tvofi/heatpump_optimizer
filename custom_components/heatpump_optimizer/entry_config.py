"""The config entry's settings, parsed once per entry (#1745).

Home Assistant hands an entry its setup answers in ``data`` and its options in
``options``. Readers used to ``.get`` keys off the merged dict site by site,
each with a default and a coercion of its own, so two readers of one key could
disagree on a stored value one of them refused. ``EntryConfig`` parses every
key it declares once, with the one default and the one coercion declared beside
it, when the coordinator is built; an options save that changes anything
reloads the entry, so a coordinator never sees its configuration change.

A field's name is its stored key, so the declaration is the only place a key
is spelled at runtime. The object is still the read-only merged mapping, for
the parsers that take one whole (the thermal parameters, the grid-fee
schedule, the topology).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any

from . import mixing_valve
from .freq_control import FREQ_MODE_CONTROL, FREQ_MODE_OBSERVE
from .const import (
    DEFAULT_CAPACITY_CURVE_ENABLED,
    DEFAULT_COMFORT_LEARNING_ENABLED,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_COMFORT_WEIGHT,
    DEFAULT_COMPRESSOR_FREQ_MAX_HZ,
    DEFAULT_COMPRESSOR_FREQ_MIN_HZ,
    DEFAULT_COMPRESSOR_RATED_STARTS,
    DEFAULT_COMPRESSOR_REPLACEMENT_COST,
    DEFAULT_CONFIDENCE_MARGINS_ENABLED,
    DEFAULT_CONTRACT_FIXED_PRICE,
    DEFAULT_COP_SCALE,
    DEFAULT_CURVE_LEARNING_ENABLED,
    DEFAULT_CYCLING_COST,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_DHW_DISINFECTION_MODE,
    DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
    DEFAULT_DHW_QUANTILE_TARGETS_ENABLED,
    DEFAULT_DHW_TANK_VOLUME,
    DEFAULT_ECL110_DISPLACE_MAX,
    DEFAULT_ECL110_DISPLACE_MIN,
    DEFAULT_ECL110_QOS,
    DEFAULT_ECL110_RETAIN,
    DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
    DEFAULT_EXTERNAL_HEAT_ENABLED,
    DEFAULT_EXTERNAL_HEAT_MIN_RISE,
    DEFAULT_FREQ_CONTROL_MODE,
    DEFAULT_FUSE_GUARD_ENABLED,
    DEFAULT_IMMERSION_FEEDBACK_ENABLED,
    DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
    DEFAULT_MAIN_FUSE_A,
    DEFAULT_MAIN_FUSE_PHASES,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND,
    DEFAULT_MOLD_FLOOR_BREACH_MARGIN,
    DEFAULT_MOLD_GUARD_ENABLED,
    DEFAULT_OPEN_WINDOW_RELAX_ENABLED,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_OUTAGE_RECOVERY_ENABLED,
    DEFAULT_PEAK_GUARD_ENABLED,
    DEFAULT_PEAK_GUARD_MARGIN_KW,
    DEFAULT_PEAK_TARIFF_COUNT,
    DEFAULT_PEAK_TARIFF_DISTINCT_DAYS,
    DEFAULT_PEAK_TARIFF_ENABLED,
    DEFAULT_PEAK_TARIFF_HOURS,
    DEFAULT_PEAK_TARIFF_MONTHS,
    DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR,
    DEFAULT_PEAK_TARIFF_PRICE,
    DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY,
    DEFAULT_PEAK_TARIFF_WINDOW,
    DEFAULT_PRECIP_TYPE_ENABLED,
    DEFAULT_PRICE_PRIOR_ENABLED,
    DEFAULT_PRICE_RISK_LAMBDA,
    DEFAULT_PRICE_SOURCE,
    DEFAULT_PRICE_TILES_ENABLED,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_PV_EFFICIENCY,
    DEFAULT_PV_ENABLED,
    DEFAULT_PV_EXPORT_PRICE,
    DEFAULT_PV_PEAK_KW,
    DEFAULT_PUMP_DUTY_MODE,
    DEFAULT_SHOWER_FLOW_LPM,
    DEFAULT_SILENT_MODE_FRACTION,
    DEFAULT_SILENT_MODE_WINDOWS,
    DEFAULT_SNOW_ROOF_FACTOR_ENABLED,
    DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
    DEFAULT_SOLAR_FORECAST_SOURCE,
    DEFAULT_SPACE_SETPOINT_UNIT,
    DEFAULT_STALENESS_ENABLED,
    DEFAULT_STALENESS_SCALE,
    DEFAULT_SYSID_ENABLED,
    DEFAULT_TARGET_TEMP,
    DEFAULT_THERMAL_BRIDGE_FRSI,
    DEFAULT_VVC_LEAD_MINUTES,
    DEFAULT_WEAR_AUTOTUNE_ENABLED,
    DEFAULT_WOOD_TANK_VOLUME,
    PUMP_DUTY_MODES,
    SPACE_SETPOINT_UNITS,
)

Parse = Callable[[Any, Any], Any]


def _number(value: Any, default: float) -> float:
    """A finite float; anything else, a stored string or a NaN, is the default."""
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return result if math.isfinite(result) else default


def _refused_number(value: Any, default: float) -> float | None:
    """A finite float, or None for a stored value that is not one."""
    result = _number(value, math.nan)
    return None if math.isnan(result) else result


def _nonzero_number(value: Any, default: float) -> float:
    return _number(value, default) or default


def _optional_number(value: Any, default: None) -> float | None:
    return None if value == "" else _number(value, default)  # type: ignore[arg-type]


def _whole(value: Any, default: int | None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _flag(value: Any, default: bool) -> bool:
    return bool(value)


def _text(value: Any, default: str) -> str:
    return str(value)


def _entity(value: Any, default: None) -> str | None:
    """An entity id, or None where the slot is empty."""
    return str(value) if value else None


def _or_default(value: Any, default: Any) -> Any:
    return value or default


def _as_stored(value: Any, default: Any) -> Any:
    return value


def _one_of(allowed: frozenset[str]) -> Parse:
    return lambda value, default: value if value in allowed else default


def _key(default: Any, parse: Parse) -> Any:
    return field(default=default, metadata={"parse": parse})


def _entity_slot() -> Any:
    return _key(None, _entity)


@dataclass(frozen=True, eq=False)
class EntryConfig(Mapping[str, Any]):
    """One entry's merged data and options, each declared key parsed once."""

    raw: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}), repr=False)

    # Entity slots.
    away_presence_entity: str | None = _entity_slot()
    away_return_entity: str | None = _entity_slot()
    compressor_freq_entity: str | None = _entity_slot()
    compressor_freq_sensor: str | None = _entity_slot()
    dhw_disinfection_switch_entity: str | None = _entity_slot()
    dhw_inlet_entity: str | None = _entity_slot()
    dhw_setpoint_entity: str | None = _entity_slot()
    dhw_temp_entity: str | None = _entity_slot()
    grid_fee_entity: str | None = _entity_slot()
    heat_pump_defrost_entity: str | None = _entity_slot()
    heat_pump_mode_entity: str | None = _entity_slot()
    heat_pump_power_entity: str | None = _entity_slot()
    heat_pump_supply_temp_entity: str | None = _entity_slot()
    heat_pump_switch_entity: str | None = _entity_slot()
    holiday_calendar_entity: str | None = _entity_slot()
    house_power_entity: str | None = _entity_slot()
    indoor_humidity_entity: str | None = _entity_slot()
    indoor_temp_entity: str | None = _entity_slot()
    lower_floor_temp_entity: str | None = _entity_slot()
    mixing_valve_write_entity: str | None = _entity_slot()
    price_entity: str | None = _entity_slot()
    pv_export_price_entity: str | None = _entity_slot()
    pv_production_entity: str | None = _entity_slot()
    space_circulation_pump_entity: str | None = _entity_slot()
    space_setpoint_entity: str | None = _entity_slot()
    vvc_pump_entity: str | None = _entity_slot()
    weather_entity: str | None = _entity_slot()

    # Switches.
    capacity_curve_enabled: bool = _key(DEFAULT_CAPACITY_CURVE_ENABLED, _flag)
    comfort_learning_enabled: bool = _key(DEFAULT_COMFORT_LEARNING_ENABLED, _flag)
    confidence_margins_enabled: bool = _key(DEFAULT_CONFIDENCE_MARGINS_ENABLED, _flag)
    curve_learning_enabled: bool = _key(DEFAULT_CURVE_LEARNING_ENABLED, _flag)
    dhw_free_disinfection_enabled: bool = _key(DEFAULT_DHW_FREE_DISINFECTION_ENABLED, _flag)
    dhw_quantile_targets_enabled: bool = _key(DEFAULT_DHW_QUANTILE_TARGETS_ENABLED, _flag)
    ecl110_mqtt_retain: bool = _key(DEFAULT_ECL110_RETAIN, _flag)
    external_heat_detection_enabled: bool = _key(DEFAULT_EXTERNAL_HEAT_ENABLED, _flag)
    fuse_guard_enabled: bool = _key(DEFAULT_FUSE_GUARD_ENABLED, _flag)
    immersion_feedback_enabled: bool = _key(DEFAULT_IMMERSION_FEEDBACK_ENABLED, _flag)
    internal_gains_learning_enabled: bool = _key(DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED, _flag)
    mold_guard_enabled: bool = _key(DEFAULT_MOLD_GUARD_ENABLED, _flag)
    open_window_relax_enabled: bool = _key(DEFAULT_OPEN_WINDOW_RELAX_ENABLED, _flag)
    outage_recovery_enabled: bool = _key(DEFAULT_OUTAGE_RECOVERY_ENABLED, _flag)
    peak_guard_enabled: bool = _key(DEFAULT_PEAK_GUARD_ENABLED, _flag)
    peak_tariff_distinct_days: bool = _key(DEFAULT_PEAK_TARIFF_DISTINCT_DAYS, _flag)
    peak_tariff_enabled: bool = _key(DEFAULT_PEAK_TARIFF_ENABLED, _flag)
    peak_tariff_weekdays_only: bool = _key(DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY, _flag)
    precip_type_enabled: bool = _key(DEFAULT_PRECIP_TYPE_ENABLED, _flag)
    price_prior_enabled: bool = _key(DEFAULT_PRICE_PRIOR_ENABLED, _flag)
    price_tiles_enabled: bool = _key(DEFAULT_PRICE_TILES_ENABLED, _flag)
    pv_enabled: bool = _key(DEFAULT_PV_ENABLED, _flag)
    snow_roof_factor_enabled: bool = _key(DEFAULT_SNOW_ROOF_FACTOR_ENABLED, _flag)
    solar_aperture_learning_enabled: bool = _key(DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED, _flag)
    staleness_watchdog_enabled: bool = _key(DEFAULT_STALENESS_ENABLED, _flag)
    system_identification_enabled: bool = _key(DEFAULT_SYSID_ENABLED, _flag)
    wear_autotune_enabled: bool = _key(DEFAULT_WEAR_AUTOTUNE_ENABLED, _flag)

    # Numbers.
    comfort_temp_day: float = _key(DEFAULT_COMFORT_TEMP_DAY, _number)
    comfort_temp_night: float = _key(DEFAULT_COMFORT_TEMP_NIGHT, _number)
    comfort_weight: float = _key(DEFAULT_COMFORT_WEIGHT, _number)
    compressor_cycling_cost: float = _key(DEFAULT_CYCLING_COST, _number)
    compressor_freq_max_hz: float = _key(DEFAULT_COMPRESSOR_FREQ_MAX_HZ, _number)
    compressor_freq_min_hz: float = _key(DEFAULT_COMPRESSOR_FREQ_MIN_HZ, _number)
    compressor_rated_starts: float = _key(DEFAULT_COMPRESSOR_RATED_STARTS, _number)
    compressor_replacement_cost: float = _key(DEFAULT_COMPRESSOR_REPLACEMENT_COST, _number)
    contract_fixed_price: float = _key(DEFAULT_CONTRACT_FIXED_PRICE, _number)
    cop_scale: float = _key(DEFAULT_COP_SCALE, _number)
    # A volume of 0 is an unset field, not an empty tank.
    dhw_tank_volume: float = _key(DEFAULT_DHW_TANK_VOLUME, _nonzero_number)
    ecl110_displace_max: float = _key(DEFAULT_ECL110_DISPLACE_MAX, _number)
    ecl110_displace_min: float = _key(DEFAULT_ECL110_DISPLACE_MIN, _number)
    external_heat_decay_minutes: float = _key(DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES, _number)
    external_heat_min_rise: float = _key(DEFAULT_EXTERNAL_HEAT_MIN_RISE, _number)
    main_fuse_amperes: float = _key(DEFAULT_MAIN_FUSE_A, _number)
    main_fuse_phases: float = _key(DEFAULT_MAIN_FUSE_PHASES, _number)
    max_temperature: float = _key(DEFAULT_MAX_TEMP, _number)
    min_temperature: float = _key(DEFAULT_MIN_TEMP, _number)
    mold_floor_breach_margin: float = _key(DEFAULT_MOLD_FLOOR_BREACH_MARGIN, _number)
    optimization_interval: float = _key(DEFAULT_OPTIMIZATION_INTERVAL, _number)
    peak_guard_margin_kw: float = _key(DEFAULT_PEAK_GUARD_MARGIN_KW, _number)
    peak_tariff_offpeak_factor: float = _key(DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR, _number)
    peak_tariff_peaks_averaged: float = _key(DEFAULT_PEAK_TARIFF_COUNT, _number)
    peak_tariff_price_per_kw: float = _key(DEFAULT_PEAK_TARIFF_PRICE, _number)
    peak_tariff_window_minutes: float = _key(DEFAULT_PEAK_TARIFF_WINDOW, _number)
    price_risk_lambda: float = _key(DEFAULT_PRICE_RISK_LAMBDA, _number)
    price_weight: float = _key(DEFAULT_PRICE_WEIGHT, _number)
    pv_export_price: float = _key(DEFAULT_PV_EXPORT_PRICE, _number)
    pv_peak_kw: float = _key(DEFAULT_PV_PEAK_KW, _number)
    pv_system_efficiency: float = _key(DEFAULT_PV_EFFICIENCY, _number)
    shower_flow_lpm: float = _key(DEFAULT_SHOWER_FLOW_LPM, _number)
    staleness_max_age_scale: float = _key(DEFAULT_STALENESS_SCALE, _number)
    target_temperature: float = _key(DEFAULT_TARGET_TEMP, _number)
    thermal_bridge_frsi: float = _key(DEFAULT_THERMAL_BRIDGE_FRSI, _number)
    vvc_lead_minutes: float = _key(DEFAULT_VVC_LEAD_MINUTES, _number)
    wood_tank_volume: float = _key(DEFAULT_WOOD_TANK_VOLUME, _number)

    # A fraction this version cannot read caps nothing: None, not the default.
    silent_mode_power_fraction: float | None = _key(DEFAULT_SILENT_MODE_FRACTION, _refused_number)

    # Optional numbers: None keeps the weekday or ordinary-day value.
    comfort_temp_day_weekend: float | None = _key(None, _optional_number)
    comfort_temp_night_weekend: float | None = _key(None, _optional_number)
    holiday_comfort_temp_day: float | None = _key(None, _optional_number)
    holiday_comfort_temp_night: float | None = _key(None, _optional_number)

    # Whole numbers.
    day_end_hour: int = _key(DEFAULT_DAY_END_HOUR, _whole)
    day_start_hour: int = _key(DEFAULT_DAY_START_HOUR, _whole)
    day_end_hour_weekend: int | None = _key(None, _whole)
    day_start_hour_weekend: int | None = _key(None, _whole)
    ecl110_mqtt_qos: int = _key(DEFAULT_ECL110_QOS, _whole)
    holiday_day_end_hour: int | None = _key(None, _whole)
    holiday_day_start_hour: int | None = _key(None, _whole)

    # Choices and text. An ECL110 topic is exactly what the options flow
    # stored, "" when absent: the shipped default topics standing in for an
    # absent key had an install with no ECL110 publishing to them (R5-D12-01).
    ecl110_command_topic: str = _key("", _text)
    ecl110_displace_set_topic: str = _key("", _text)
    ecl110_state_topic: str = _key("", _text)
    dhw_disinfection_mode: str = _key(
        DEFAULT_DHW_DISINFECTION_MODE, _one_of(frozenset((FREQ_MODE_OBSERVE, FREQ_MODE_CONTROL))))
    freq_control_mode: str = _key(DEFAULT_FREQ_CONTROL_MODE, _text)
    mixing_valve_write_target_kind: str = _key(
        DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND, _one_of(mixing_valve.WRITE_TARGET_KINDS))
    peak_tariff_hours: str = _key(DEFAULT_PEAK_TARIFF_HOURS, _text)
    peak_tariff_months: str = _key(DEFAULT_PEAK_TARIFF_MONTHS, _text)
    price_source: str = _key(DEFAULT_PRICE_SOURCE, _text)
    pump_duty_mode: str = _key(DEFAULT_PUMP_DUTY_MODE, _one_of(frozenset(PUMP_DUTY_MODES)))
    silent_mode_windows: Any = _key(DEFAULT_SILENT_MODE_WINDOWS, _or_default)
    solar_forecast_source: str = _key(DEFAULT_SOLAR_FORECAST_SOURCE, _text)
    solar_location: Any = _key(None, _as_stored)
    space_setpoint_unit: str = _key(DEFAULT_SPACE_SETPOINT_UNIT, _one_of(frozenset(SPACE_SETPOINT_UNITS)))

    @classmethod
    def from_mapping(cls, merged: Mapping[str, Any]) -> EntryConfig:
        """Parse ``merged``: an absent key is its default, a present one its parse.

        An ``EntryConfig`` is returned as it is: it was parsed once already.
        """
        if isinstance(merged, EntryConfig):
            return merged
        parsed = {
            f.name: f.metadata["parse"](merged[f.name], f.default)
            for f in fields(cls)
            if f.metadata and f.name in merged
        }
        return cls(raw=MappingProxyType(dict(merged)), **parsed)

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.raw)

    def __len__(self) -> int:
        return len(self.raw)
