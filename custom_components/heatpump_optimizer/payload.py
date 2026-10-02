"""The typed contract of the coordinator's published payload.

Every key ``HeatPumpOptimizerCoordinator._build_data_dict`` can publish, with
the value type its producer gives it. ``total=False`` throughout: a key is
conditional (the two-tank block, ``manual_plan``, the wood-fuel extras) or an
empty dict while its subsystem is off, so presence is never part of the type.
A read of a key no producer sets is therefore a type error, not a fallback.

A value that is a dict of unrelated shapes is ``dict[str, object]``, never
``Any``. Two kinds are: open-ended reports no producer fixes the shape of, and
fixed-shape reports not yet given their own TypedDict (R9-EG-B3b).
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict


class CurrentAction(TypedDict, total=False):
    mode: str
    power: float
    power_normalized: float
    setpoint: float
    upper_setpoint: float
    lower_setpoint: float
    displace_value: float
    heat_pump_on: bool
    price: float
    valve_target: float
    solar_gain_kw: float
    baseline_kw: float
    dhw_power: float
    dhw_heating_active: bool
    dhw_temperature: float
    dhw_target_temperature: float | None
    solar_reduction_factor: float
    wind_anticipation_factor: float
    pre_heat_urgency: float
    space_reason: str | None
    dhw_reason: str | None


class InputProblem(TypedDict, total=False):
    input: str
    entity_id: str
    problem: str | None
    age_minutes: float | None
    max_age_minutes: float | None


class SolarForecastStep(TypedDict, total=False):
    t: str
    ghi: float


class DhwMixed(TypedDict, total=False):
    litres_40c: float
    tank_temperature: float
    shower_minutes: float


class DrawStat(TypedDict, total=False):
    events: int
    p90_kwh: float | None


class CopHealth(TypedDict, total=False):
    watched_buckets: int
    alarm: bool
    evidence: list[str]


class CapacityEnvelope(TypedDict, total=False):
    buckets: dict[str, list[float]]


class SolarAperture(TypedDict, total=False):
    scale: float
    samples: int


class SnapshotRing(TypedDict, total=False):
    count: int
    alarm: bool
    last_taken: str | None


class PeakTariff(TypedDict, total=False):
    month: str
    peak_days: list[str]
    peaks: list[float]
    peaks_averaged: int
    price_per_kw: float
    window_factor: float
    window_key: str
    window_minutes: int
    window_samples: int
    window_sum: float
    window_weight: float
    window_wsum: float


class SavingsMonth(TypedDict, total=False):
    month: str
    baseline_sek: float
    actual_sek: float
    savings_sek: float
    savings_pct: float | None
    estimated: bool


class Narrative(TypedDict, total=False):
    items: list[dict[str, object]]
    language: str
    lines: list[str]


class Scores(TypedDict, total=False):
    overall: float | None
    machine: float | None
    operation: float | None
    envelope: float | None


class CompressorStarts(TypedDict, total=False):
    lifetime: int
    month: int


class PriceTile(TypedDict, total=False):
    overrides: dict[str, float]
    monthly_cost_delta: float | None
    min_room_temperature: float | None
    computed_at: str


class FreqControl(TypedDict, total=False):
    mode: str
    fallback_active: bool
    reported_hz: float | None
    recommended_hz: float | None
    evidence_exhausted: bool
    commanded_hz: float | None
    range_hz: list[float] | None
    map: dict[str, object]
    source: str


class Insight(TypedDict, total=False):
    narrative: Narrative
    scores: Scores
    compressor_starts: CompressorStarts
    monthly_report: dict[str, object] | None
    price_tiles: dict[str, PriceTile]
    last_diagnosis: dict[str, object] | None
    wear_price_per_start: float


class ManualPlan(TypedDict, total=False):
    active: bool
    expires_at: str
    space_slots: list[dict[str, str]] | None
    dhw_slots: list[dict[str, str]] | None
    released_space: list[dict[str, object]]
    released_dhw: list[dict[str, object]]


class MixingValveRecommendation(TypedDict, total=False):
    target: float
    reason: str
    configured_target: float | None
    price_ratio: float | None


class Payload(TypedDict, total=False):
    """The coordinator's ``data``: one key per published attribute."""

    # Assembler
    mode: str
    current_action: CurrentAction
    last_optimization: datetime | None
    next_optimization: datetime | None
    plan_age_minutes: float | None
    plan_stale: bool
    weather_forecast_stale_hours: float | None
    heat_pump_power_series: list[float]
    house_power_series: list[float]
    energy_totals_counting_since: str
    battery: dict[str, object]
    insight: Insight
    freq_control: FreqControl
    currency: str
    wood_fuel: dict[str, object]
    manual_plan: ManualPlan
    # Plan settings view
    comfort_temp_day: float
    comfort_temp_night: float
    day_start_hour: int
    day_end_hour: int
    horizon_hours: float
    min_temperature: float
    max_temperature: float
    # Thermal view
    indoor_temperature: float
    outdoor_temperature: float
    slab_temperature: float
    upper_floor_temperature: float
    lower_floor_temperature: float
    buffer_tank_temperature: float
    floor_return_temperature: float | None
    reading_ok: dict[str, bool]
    solar_radiation: float
    solar_heat_gain: float
    solar_source: str
    solar_forecast: list[SolarForecastStep]
    solar_diagnostics: dict[str, object] | None
    two_zone_enabled: bool
    two_tank_modelled: bool
    wood_tank_temperature: float | None
    # Domestic hot water view
    dhw_enabled: bool
    dhw_temperature: float
    dhw_setpoint: float
    dhw_min_temperature: float
    dhw_usage_profile: list[float]
    dhw_hold_hours: float
    dhw_windows: str
    dhw_schedule_enabled: bool
    dhw_in_demand_window: bool
    dhw_next_window_in_hours: float | None
    dhw_idle_min_temperature: float
    dhw_legionella_enabled: bool
    dhw_legionella_due_in_hours: float | None
    dhw_inlet_temperature: float
    dhw_mixed: DhwMixed
    dhw_advisor: dict[str, object]
    dhw_draw_stats: dict[str, DrawStat]
    # Learning view
    dhw_cooling_rate: float
    dhw_cooling_samples: int
    dhw_cooling_rate_learned: bool
    buffer_cooling_rate: float
    buffer_cooling_samples: int
    buffer_cooling_rate_learned: bool
    house_heat_loss_scale: float
    house_heat_loss_samples: int
    house_heat_loss_learned: bool
    house_heat_loss_effective: float
    lower_floor_loss_ratio: float
    lower_floor_loss_samples: int
    lower_floor_loss_learned: bool
    cop_scale: float
    cop_samples: int
    measured_cop: float | None
    defrost_derate: float
    defrost_samples: int
    defrost_measured_samples: int
    defrost_flag_configured: bool
    defrost_store_migrated: bool
    defrost_buckets: list[dict[str, object]]
    comfort_weight: float
    comfort_learning: dict[str, object]
    system_identification: dict[str, object]
    accuracy: dict[str, object]
    heat_pump_signals: dict[str, object]
    ventilation_active: bool
    ventilation_evidence: list[str]
    immersion_active: bool
    immersion_evidence: list[str]
    cop_health: CopHealth
    capacity_envelope: CapacityEnvelope
    solar_aperture: SolarAperture
    internal_gains_profile: list[float] | None
    heat_curve: dict[str, object]
    snapshots: SnapshotRing
    # Measurement view
    measured_power: float | None
    measured_house_power: float | None
    measured_energy: float | None
    measured_power_available: bool
    # Grid view
    current_price: float
    prices_available: int
    weather_forecast_available: int
    outdoor_forecast_temperature: float | None
    price_known_steps: int
    price_prior: dict[str, object]
    contract_comparison: dict[str, object]
    current_grid_fee: float
    power_headroom: dict[str, object]
    fuse_advisor: dict[str, object]
    peak_guard_suppressing: bool
    peak_guard_evidence: list[str]
    outage_recovery_active: bool
    peak_tariff_enabled: bool
    peak_tariff: PeakTariff
    billed_peak_kw: float
    peak_threshold_kw: float
    peak_month: str
    pv_enabled: bool
    pv: dict[str, object]
    savings_months: list[SavingsMonth]
    # ECL110 view
    ecl110_command_topic: str
    ecl110_state_topic: str
    ecl110_displace: float
    ecl110_effective_displace: float
    ecl110_last_payload: dict[str, object]
    # External heat view
    external_heat_active: bool
    external_heat_suppressing: bool
    external_heat: dict[str, object]
    # Input health view
    input_health: str
    stale_inputs: list[str]
    input_problems: list[InputProblem]
    problem_inputs: list[str]
    problem_messages: list[str]
    input_ages_minutes: dict[str, float]
    learners_frozen: bool
    learner_freeze_reason: str | None
    # Mixing valve view
    mixing_valve_mode: str
    valve_target_recommendation: MixingValveRecommendation
    # Away state
    away_active: bool
    away_dhw_min_temperature: float | None
    away_hours_until_return: float | None
    away_override_active: bool
    away_override_return_time: str | None
    away_recovery_active: bool
    away_recovery_hours: float | None
    away_return_time: str | None
    away_source: str
    away_target_temperature: float | None
    # Lifetime accumulators (``_energy_totals``)
    space_energy_kwh: float
    dhw_energy_kwh: float
    total_energy_kwh: float
    space_cost: float
    dhw_cost: float
    total_cost: float
    sensor_advisor: dict[str, object]
    # Solved plan (absent or inert before the first solve)
    predicted_cost: float | None
    baseline_cost: float | None
    predicted_savings: float | None
    savings_percentage: float | None
    deferred_energy_cost: float | None
    optimization_status: str
    solve_time_ms: float
    dhw_heating_cost: float
    dhw_heating_active: bool
    dhw_schedule: list[dict[str, object]]
    predictive_info: dict[str, object]
    projected_peak_kw: float
    projected_peak_cost: float
    compressor_starts: int
    pv_self_consumed_kwh: float
    plan_price_known: list[bool]
    schedule: list[dict[str, object]]
    space_plan: dict[str, object]
    dhw_plan: dict[str, object]
    valve_target_schedule: list[float]
