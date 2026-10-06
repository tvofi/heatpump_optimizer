"""The typed contract of the coordinator's published payload.

Every key ``HeatPumpOptimizerCoordinator._build_data_dict`` can publish, with
the value type its producer gives it. ``total=False`` throughout: a key is
conditional (the two-tank block, ``manual_plan``, the wood-fuel extras) or an
empty dict while its subsystem is off, so presence is never part of the type.
A read of a key no producer sets is therefore a type error, not a fallback.

``Payload`` inherits one slice per assembler view, and each view returns its
slice, so mypy checks a producer's literal against the keys it may publish and
no cast is needed to hand the assembled dict out.

A slice joins ``data`` through ``data = {**data, **view()}`` and not
``data.update(view())``: under the pinned ruler's flags ``update`` takes the
whole payload's keys and refuses a slice, and a display with a ``**`` item must
cover every key, which ``**data`` does.

A fixed-shape report has its own TypedDict. A value that stays a
``dict[str, object]`` is an open-ended report, kept open on purpose, and each
is named here with its reason (R9-EG-B3b). ``object``, not ``Any``, so a read
must narrow it:

* ``predictive_info``: the optimizer's own diagnostics, a dict that gains a
  key per feature and goes through ``_plain_types`` (declared ``-> Any``).
* ``monthly_report``: a frozen month receipt, persisted and restored, so one
  written by an older release carries that release's keys.
* ``ComfortLearning.recent_overrides``: the learner's history, which the comfort
  store restores keeping any entry that passes an ``isinstance(dict)`` check
  alone, so its keys are whatever the store held.

Every other report is fixed-shape and typed, including the ones the first draft
kept open (``solar_diagnostics``, ``ecl110_last_payload``, ``sensor_advisor``,
``Narrative.items``, ``FreqControl.map``, ``last_diagnosis``, ``fuse_advisor``
and ``ManualPlan.released_space`` / ``released_dhw``): each has a closed shape
-- ``fuse_advisor`` is admitted from the store only through ``store.admitted``'s
declared keys, ``released_*`` are never saved -- and a producer whose literal
mypy now checks. Values read through a coordinator's hubs are checked too:
``_ctx_of`` types them, where ``getattr(self, "_ctx", self)`` was ``Any``.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .open_meteo import SolarDiagnostics  # standalone-loaded by a test: not imported at run time


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
    boost_space: bool
    boost_dhw: bool


class DisinfectionSwitch(TypedDict, total=False):
    entity_id: str
    mode: str
    state: bool | None
    turned_on_by_optimizer: bool
    write_failed: bool


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
    price_per_kw: float
    window_minutes: int
    peaks_averaged: int


class SavingsMonth(TypedDict, total=False):
    month: str
    baseline_sek: float
    actual_sek: float
    savings_sek: float
    savings_pct: float | None
    estimated: bool


class NarrativeItem(TypedDict):
    reason: str
    kwh: float
    sek: float
    hours: float


class Narrative(TypedDict, total=False):
    items: list[NarrativeItem]
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
    wear_price_per_start: float


class PriceTile(TypedDict, total=False):
    overrides: dict[str, float]
    monthly_cost_delta: float | None
    min_room_temperature: float | None
    computed_at: str


class FreqMapBucket(TypedDict):
    mid_hz: float
    kw_per_hz: float
    samples: int


class FreqControl(TypedDict, total=False):
    mode: str
    fallback_active: bool
    reported_hz: float | None
    recommended_hz: float | None
    evidence_exhausted: bool
    commanded_hz: float | None
    range_hz: list[float] | None
    map: dict[str, FreqMapBucket]
    source: str


class Insight(TypedDict, total=False):
    narrative: Narrative
    scores: Scores
    compressor_starts: CompressorStarts
    monthly_report: dict[str, object] | None
    price_tiles: dict[str, PriceTile]
    last_diagnosis: DiagnosisReport | None


class ReleasedStep(TypedDict):
    step: int
    reason: str


class DiagnosisReport(TypedDict, total=False):
    predicted: float
    actual: float
    residual: float
    contributions: dict[str, float]
    unexplained: float
    interval_end: str


class FuseAdvisor(TypedDict, total=False):
    """Two code paths fill it: the rate-limited stub (``error``) and the answer."""

    month: str
    current_fuse_a: int
    candidate_fuse_a: int
    candidate_kw: float
    feasible: bool
    comfort_shortfall_c: float
    worst_margin_kw: float
    cost_delta_sek_month: float | None
    error: str


class ManualPlan(TypedDict, total=False):
    active: bool
    expires_at: str
    space_slots: list[dict[str, str]] | None
    dhw_slots: list[dict[str, str]] | None
    released_space: list[ReleasedStep]
    released_dhw: list[ReleasedStep]


class MixingValveRecommendation(TypedDict, total=False):
    target: float
    reason: str
    configured_target: float | None
    price_ratio: float | None


class HeatPumpSignals(TypedDict, total=False):
    """``PumpSignals.as_dict``: the pump's slots, already resolved."""

    mode: str
    mode_key: str | None
    mode_state: str | None
    mode_source: str
    space_heat_available: bool
    dhw_available: bool
    cooling: bool
    concurrent_duties: bool
    space_blocked: bool
    dhw_blocked: bool
    defrosting: bool | None
    online: bool | None
    fault: bool | None
    freeze_reason: str | None
    backup_heater: bool | None
    dhw_booster: bool | None
    capacity_limited: bool | None
    dhw_booster_started: bool
    resistive_heat: bool
    compressor_draw_distorted: bool


class ElectricHeatSignals(TypedDict, total=False):
    """``PumpElectricHeat.as_dict``: the part of the above it spreads in."""

    backup_heater: bool | None
    dhw_booster: bool | None
    capacity_limited: bool | None
    dhw_booster_started: bool
    resistive_heat: bool
    compressor_draw_distorted: bool


class BatteryComponent(TypedDict, total=False):
    name: str
    temperature: float
    stored_kwh: float
    usable_capacity_kwh: float
    soc_percent: float
    standing_loss_kw: float
    measured: bool


class Battery(TypedDict, total=False):
    stored_energy_kwh: float
    usable_capacity_kwh: float
    state_of_charge_percent: float
    charge_rate_kw: float
    charge_power_electrical_kw: float
    discharge_rate_kw: float
    hours_of_autonomy: float | None
    round_trip_efficiency_6h: float
    components: list[BatteryComponent]
    measured_components: list[str]
    modelled_components: list[str]


class NightAdvice(TypedDict, total=False):
    action: str
    text: str
    when: str | None
    reason: str


class WoodSlot(TypedDict, total=False):
    start: str
    end: str
    source: str


class WoodFuel(TypedDict, total=False):
    ready: bool
    cheaper: bool
    show_whatif: bool
    sek_per_kwh: float | None
    type: str | None
    packing: str | None
    efficiency: float | None
    price_sek_m3: float | None
    cheaper_hour_count: int
    slots: list[WoodSlot]
    night_advice: NightAdvice


class Accuracy(TypedDict, total=False):
    samples: int
    temperature_mae: float | None
    temperature_bias: float | None
    power_ratio: float | None
    cost_error_percent: float | None
    realised_cost: float
    predicted_cost: float
    trust: float
    lead_sigma: dict[str, float]


class PricePrior(TypedDict, total=False):
    weekday_days: int
    weekend_days: int
    weekday_shape: list[float]
    weekend_shape: list[float]
    weekday_quarter_days: int
    weekend_quarter_days: int
    weekday_sigma: list[float]
    weekend_sigma: list[float]


class Ecl110Command(TypedDict):
    type: str
    heat_pump_on: bool
    displace: int


class Ecl110Context(TypedDict):
    price: float | None
    mode: str | None
    pre_heat_urgency: float | None


class Ecl110Payload(TypedDict, total=False):
    """The legacy command body ``_ecl110_legacy_payload`` publishes."""

    source: str
    reason: str
    timestamp: str
    command: Ecl110Command
    context: Ecl110Context


class SensorAdvisorRow(TypedDict, total=False):
    key: str
    label: str
    priced: bool
    reason: str
    parameters: list[str]
    spread_c: float


class SensorAdvisor(TypedDict):
    basis: str
    candidates: list[SensorAdvisorRow]


class ExternalHeat(TypedDict, total=False):
    active: bool
    confidence: float
    fading: bool
    source: str
    evidence: list[str]
    since: str | None
    dhw_rise_c_per_h: float | None
    buffer_rise_c_per_h: float | None
    displacement: float
    free_heat_kw: float
    wood_energy_kwh: float


class SysIdResultView(TypedDict, total=False):
    completed: bool
    time_constant_hours: float | None
    heat_loss_kw_per_c: float | None
    thermal_mass_kwh_per_c: float | None
    internal_gains_kw: float | None
    confidence: float
    slab_mode_tau_hours: float | None
    reason: str


class SysIdView(TypedDict, total=False):
    phase: str
    active: bool
    samples: int
    last_run: str | None
    result: SysIdResultView


class DefrostBucket(TypedDict, total=False):
    outdoor_range: list[float]
    humidity_range: list[float]
    source: str
    derate: float
    learned: float
    samples: int
    duty: float
    events: int
    duty_samples: int


class ComfortLearning(TypedDict, total=False):
    configured: float
    learned: float
    evidence: float
    overrides: int
    recent_overrides: list[dict[str, object]]


class HeatCurve(TypedDict, total=False):
    bias_k: float
    comfortable_days: int
    resets: int


class ContractComparison(TypedDict, total=False):
    month: str
    kwh: float
    hourly_spot_sek: float
    grid_fee_sek: float
    monthly_avg_spot_sek: float
    load_profile_value_per_kwh: float
    fixed_sek: float
    cheapest: str


class PowerHeadroom(TypedDict, total=False):
    available: bool
    limit_kw: float
    headroom_kw: float
    baseline_source: str
    limit_source: str
    horizon_headroom_kw: list[float]


class Pv(TypedDict, total=False):
    forecast_production_kwh: float
    forecast_surplus_kwh: float
    surplus_hours: float
    peak_production_kw: float
    export_price: float
    measured_production_kw: float


class DhwCandidate(TypedDict):
    setpoint: int
    cost_per_day: float
    meets_heaviest_window: bool


class DhwAdvisor(TypedDict, total=False):
    current_setpoint: float
    recommended_setpoint: int | None
    covers_heaviest_window: bool
    heaviest_window_kwh: float
    candidates: list[DhwCandidate]


class ScheduleStep(TypedDict, total=False):
    time: str
    power: float
    setpoint: float
    price: float
    room_temp: float
    upper_temp: float
    lower_temp: float
    solar_gain: float
    displace: float
    heat_pump_on: bool


class DhwScheduleStep(TypedDict, total=False):
    time: str
    dhw_power: float
    dhw_temp: float


class PlanSlot(TypedDict, total=False):
    start: str
    end: str
    duration_hours: float
    avg_power_kw: float
    energy_kwh: float
    avg_price: float
    cost: float
    shared_kwh: float
    reason: str
    reasons: list[str]


class SpaceForecastStep(TypedDict, total=False):
    t: str
    price: float | None
    price_known: bool
    outdoor: float | None
    space_power: float | None
    room: float | None
    upper: float | None
    lower: float | None
    reason: str | None
    pv_surplus: float | None


class DhwForecastStep(TypedDict, total=False):
    t: str
    price: float | None
    price_known: bool
    outdoor: float | None
    dhw_power: float | None
    dhw_temp: float | None
    dhw_temp_lo: float | None
    dhw_temp_hi: float | None
    reason: str | None


class SpacePlan(TypedDict, total=False):
    forecast: list[SpaceForecastStep]
    slots: list[PlanSlot]
    total_energy_kwh: float
    total_cost: float
    active_now: bool
    valve_target_schedule: list[float]


class DhwPlan(TypedDict, total=False):
    forecast: list[DhwForecastStep]
    slots: list[PlanSlot]
    total_energy_kwh: float
    total_cost: float
    active_now: bool


class PlanViews(TypedDict, total=False):
    """``_build_plan_views``: the two plans, or two empty dicts."""

    space_plan: SpacePlan
    dhw_plan: DhwPlan


class AssemblerSlice(TypedDict, total=False):
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
    battery: Battery
    insight: Insight
    freq_control: FreqControl
    currency: str
    wood_fuel: WoodFuel
    manual_plan: ManualPlan


class PlanSettingsView(TypedDict, total=False):
    comfort_temp_day: float
    comfort_temp_night: float
    day_start_hour: int
    day_end_hour: int
    horizon_hours: float
    min_temperature: float
    configured_min_temperature: float
    max_temperature: float


class ThermalView(PlanSettingsView, total=False):
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
    solar_diagnostics: SolarDiagnostics | None
    two_zone_enabled: bool
    two_tank_modelled: bool
    wood_tank_temperature: float | None


class DisinfectionView(TypedDict, total=False):
    """``DisinfectView.view``: nothing at all when no switch is involved."""

    dhw_disinfection_switch: DisinfectionSwitch


class DhwView(DisinfectionView, total=False):
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
    dhw_advisor: DhwAdvisor
    dhw_draw_stats: dict[str, DrawStat]


class LearningView(TypedDict, total=False):
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
    defrost_buckets: list[DefrostBucket]
    comfort_weight: float
    comfort_learning: ComfortLearning
    system_identification: SysIdView
    accuracy: Accuracy
    heat_pump_signals: HeatPumpSignals
    ventilation_active: bool
    ventilation_evidence: list[str]
    immersion_active: bool
    immersion_evidence: list[str]
    cop_health: CopHealth
    capacity_envelope: CapacityEnvelope
    solar_aperture: SolarAperture
    internal_gains_profile: list[float] | None
    heat_curve: HeatCurve
    snapshots: SnapshotRing


class MeasurementView(TypedDict, total=False):
    measured_power: float | None
    measured_house_power: float | None
    measured_energy: float | None
    measured_power_available: bool


class GridView(TypedDict, total=False):
    current_price: float
    prices_available: int
    weather_forecast_available: int
    outdoor_forecast_temperature: float | None
    price_known_steps: int
    price_prior: PricePrior
    contract_comparison: ContractComparison
    current_grid_fee: float
    power_headroom: PowerHeadroom
    fuse_advisor: FuseAdvisor
    peak_guard_suppressing: bool
    peak_guard_evidence: list[str]
    outage_recovery_active: bool
    peak_tariff_enabled: bool
    peak_tariff: PeakTariff
    billed_peak_kw: float
    peak_threshold_kw: float
    peak_month: str
    pv_enabled: bool
    pv: Pv
    savings_months: list[SavingsMonth]


class Ecl110View(TypedDict, total=False):
    ecl110_command_topic: str
    ecl110_state_topic: str
    ecl110_displace: float
    ecl110_effective_displace: float
    ecl110_last_payload: Ecl110Payload


class ExternalHeatView(TypedDict, total=False):
    external_heat_active: bool
    external_heat_suppressing: bool
    external_heat: ExternalHeat


class InputHealthView(TypedDict, total=False):
    input_health: str
    stale_inputs: list[str]
    input_problems: list[InputProblem]
    problem_inputs: list[str]
    problem_messages: list[str]
    input_ages_minutes: dict[str, float]
    learners_frozen: bool
    learner_freeze_reason: str | None


class MixingValveView(TypedDict, total=False):
    mixing_valve_mode: str
    valve_target_recommendation: MixingValveRecommendation


class AwayView(TypedDict, total=False):
    away_active: bool
    away_override_active: bool
    away_override_return_time: str | None
    away_recovery_active: bool
    away_recovery_hours: float | None
    away_return_time: str | None
    away_source: str
    away_target_temperature: float | None
    away_dhw_min_temperature: float | None
    away_hours_until_return: float | None


class EnergyTotals(TypedDict, total=False):
    space_energy_kwh: float
    dhw_energy_kwh: float
    total_energy_kwh: float
    space_cost: float
    dhw_cost: float
    total_cost: float


class SolvedSlice(TypedDict, total=False):
    """What a solve leaves: ``_apply_result_payload`` / ``_apply_unsolved_payload``."""

    predicted_cost: float | None
    baseline_cost: float | None
    predicted_savings: float | None
    savings_percentage: float | None
    deferred_energy_cost: float | None
    optimization_status: str
    solve_time_ms: float
    dhw_heating_cost: float
    dhw_heating_active: bool
    dhw_schedule: list[DhwScheduleStep]
    predictive_info: dict[str, object]
    projected_peak_kw: float
    projected_peak_cost: float
    compressor_starts: int
    pv_self_consumed_kwh: float
    plan_price_known: list[bool]
    schedule: list[ScheduleStep]
    space_plan: SpacePlan
    dhw_plan: DhwPlan


class Payload(
    AssemblerSlice,
    ThermalView,
    DhwView,
    LearningView,
    MeasurementView,
    GridView,
    Ecl110View,
    ExternalHeatView,
    InputHealthView,
    MixingValveView,
    AwayView,
    EnergyTotals,
    SolvedSlice,
    total=False,
):
    """The coordinator's ``data``: one key per published attribute.

    The keys are the slices'. ``sensor_advisor`` is the one this class adds:
    ``_with_sensor_advisor`` attaches it after the assembler has run.
    """

    sensor_advisor: SensorAdvisor
