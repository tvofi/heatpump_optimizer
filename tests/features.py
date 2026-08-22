"""Unit tests for the v2.8.0 feature modules.

    PYTHONPATH=tests/hastub python tests/features.py

Each module is driven directly rather than through a full optimization run.
The end-to-end scripts already cover "does the plan come out sensible"; what
they cannot cover is a detector that never fires, a watchdog that lets a
flatline through, or a tariff term that charges a month's fee once per hour.
Those failures produce a *plausible* plan, which is exactly why they need
tests that look at the mechanism rather than at the outcome.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeState, Results, UTC, minutes_ago

import numpy as np

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import battery as battery_view
from heatpump_optimizer import presets, pv
from heatpump_optimizer.accuracy import (
    AccuracySample,
    AccuracyTracker,
    delivered_ratio,
)
from heatpump_optimizer.comfort_learning import (
    COMFORT_WEIGHT_MAX,
    COMFORT_WEIGHT_MIN,
    ComfortLearner,
    OverrideEvent,
)
from heatpump_optimizer.const import COP_SCALE_MAX, COP_SCALE_MIN
from heatpump_optimizer.defrost import DefrostDerate
from heatpump_optimizer.external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
)
from heatpump_optimizer.inputs import InputReader, normalize_power_kw, stale_summary
from heatpump_optimizer.price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
)
from heatpump_optimizer.sysid import (
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import CapacityTariff, PeakTracker, peak_penalty
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

R = Results("Feature modules")


# ===========================================================================
# Item 12: input staleness watchdog
# ===========================================================================
R.section("Input staleness watchdog (item 12)")

NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
CONFIG = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_temp_entity": "sensor.tank",
    "heat_pump_power_entity": "sensor.pump_power",
}


def reader(states, **kwargs):
    return InputReader(
        FakeHass(states), CONFIG, now=lambda: NOW, **kwargs
    )


fresh = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(5, NOW))}
)
reading = fresh.read("indoor_temp_entity")
R.check("a fresh sensor reads normally", reading.ok and reading.value == 21.4)

# The whole point of the feature: a value that is perfectly valid but old.
stale = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(600, NOW))}
)
reading = stale.read("indoor_temp_entity")
R.check("an over-age value is rejected", not reading.ok and reading.stale)
R.check(
    "the rejected value is still available for a graceful fallback",
    reading.value == 21.4,
    "callers that want last-known-good must be able to get it",
)
R.check(
    "the age is reported so a user can see why",
    reading.age_minutes is not None and reading.age_minutes > 599,
)

# Limits differ per input: a forecast may reasonably be hours old.
old_outdoor = reader(
    {"sensor.outdoor": FakeState("-3.0", last_updated=minutes_ago(120, NOW))}
)
R.check(
    "an outdoor reading may be older than an indoor one",
    old_outdoor.read("outdoor_temp_entity").ok,
)

# Fail closed, not open.
disabled = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(600, NOW))},
    enabled=False,
)
R.check(
    "the watchdog can be switched off entirely",
    disabled.read("indoor_temp_entity").ok,
)
scaled = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(120, NOW))},
    scale=4.0,
)
R.check("the age limit can be relaxed", scaled.read("indoor_temp_entity").ok)

unavailable = reader({"sensor.indoor": FakeState("unavailable")})
r = unavailable.read("indoor_temp_entity")
R.check(
    "unavailable is distinguished from stale",
    not r.ok and r.problem == "unavailable" and not r.stale,
)
missing = reader({})
R.check(
    "a missing entity is reported as such",
    missing.read("indoor_temp_entity").problem == "missing_entity",
)
R.check(
    "an unconfigured input is not a problem",
    reader({}).read("floor_return_temp_entity").problem == "not_configured",
)
nonnumeric = reader({"sensor.indoor": FakeState("warm")})
R.check(
    "a non-numeric state does not raise",
    nonnumeric.read("indoor_temp_entity").problem == "not_numeric",
)

# A state with no timestamp at all: age is unknown, which is not the same as
# fresh, but rejecting it would break every stubbed integration.
class Timeless:
    state = "20.0"


timeless = reader({"sensor.indoor": Timeless()})
R.check(
    "an untimestamped state is used rather than discarded",
    timeless.read("indoor_temp_entity").ok,
)

health_reader = reader(
    {
        "sensor.indoor": FakeState("21.4", last_updated=minutes_ago(600, NOW)),
        "sensor.outdoor": FakeState("-3.0", last_updated=minutes_ago(5, NOW)),
        "sensor.tank": FakeState("unavailable"),
    }
)
for key in ("indoor_temp_entity", "outdoor_temp_entity", "dhw_temp_entity"):
    health_reader.read(key)
health = health_reader.health
R.check("stale inputs are listed", health.stale_keys == ["indoor_temp_entity"])
R.check("missing inputs are listed", health.missing_keys == ["dhw_temp_entity"])
R.check("a healthy snapshot says so", not health.healthy)
R.check(
    "the summary is human-readable",
    stale_summary(health) == "1 stale, 1 missing",
    stale_summary(health),
)
R.check(
    "the evidence names the entity",
    any(d["entity_id"] == "sensor.indoor" for d in health.details()),
)

# Units: guessing kW would read 3000 W as 3000 kW.
R.check("watts are converted to kW", normalize_power_kw(3000.0, "W") == 3.0)
R.check("kilowatts pass through", normalize_power_kw(3.0, "kW") == 3.0)
R.check(
    "an unrecognised unit is refused rather than guessed",
    normalize_power_kw(3000.0, "furlongs") is None,
)
R.check("a missing unit is refused", normalize_power_kw(3000.0, None) is None)

power_reader = reader(
    {"sensor.pump_power": FakeState("2400", unit="W", last_updated=NOW)}
)
R.check(
    "a power entity is normalised on read",
    abs(power_reader.read_power_kw("heat_pump_power_entity").value - 2.4) < 1e-9,
)
bad_unit = reader(
    {"sensor.pump_power": FakeState("2400", unit="bananas", last_updated=NOW)}
)
bad = bad_unit.read_power_kw("heat_pump_power_entity")
R.check(
    "a wrongly-united power entity yields nothing",
    bad.value is None and bad.problem == "unknown_unit",
)


# ===========================================================================
# Item 5: external heat source detection
# ===========================================================================
R.section("External heat source detection (item 5)")

CFG = ExternalHeatConfig(enabled=True, confirm_samples=2, release_samples=2)


def run(detector, samples):
    """Feed a detector a list of (minutes, dhw_temp, power) samples."""
    base = datetime(2026, 1, 10, 18, 0, tzinfo=UTC)
    state = None
    for minutes, temp, power in samples:
        state = detector.update(
            ExternalHeatObservation(
                now=base + timedelta(minutes=minutes),
                dhw_temp=temp,
                commanded_power_kw=power,
                measured_power_kw=power,
                dhw_max_rise_c_per_h=8.0,
            )
        )
    return state


det = ExternalHeatDetector(CFG)
state = run(det, [(0, 45.0, 0.0), (15, 46.0, 0.0)])
R.check(
    "a single suspicious interval does not trip it",
    not state.active,
    "false positives are the expensive direction",
)
state = run(det, [(30, 47.0, 0.0)])
R.check("two consecutive intervals do", state.active)
R.check("the evidence explains why", bool(state.evidence))
R.check("confidence is full while active", state.confidence == 1.0)

# Release, then the decay tail.
state = run(det, [(45, 47.0, 0.0), (60, 46.9, 0.0)])
R.check("it releases once the rise stops", not state.active)
R.check(
    "but keeps suppressing while it fades",
    det.suppressing and state.fading,
    "a fire dies down gradually; re-planning a full charge instantly is wrong",
)
state = det.update(
    ExternalHeatObservation(
        now=datetime(2026, 1, 10, 21, 0, tzinfo=UTC),
        dhw_temp=46.0,
        commanded_power_kw=0.0,
        measured_power_kw=0.0,
    )
)
R.check("the decay eventually clears", not det.suppressing)

# Ordinary heat pump operation must not look like a fire.
quiet = ExternalHeatDetector(CFG)
state = run(quiet, [(0, 45.0, 3.0), (15, 46.5, 3.0), (30, 48.0, 3.0)])
R.check(
    "the heat pump heating its own tank is not external heat",
    not state.active,
)

# ...unless it heats faster than it possibly could.
impossible = ExternalHeatDetector(CFG)
state = run(impossible, [(0, 45.0, 3.0), (15, 51.0, 3.0), (30, 57.0, 3.0)])
R.check(
    "a rise beyond the pump's capacity is caught even while it runs",
    state.active,
)

# Noise below the threshold.
noisy = ExternalHeatDetector(CFG)
state = run(noisy, [(0, 45.0, 0.0), (15, 45.2, 0.0), (30, 45.4, 0.0)])
R.check("sensor drift below the threshold is ignored", not state.active)

# An explicit user entity is authoritative and skips the hysteresis.
override = ExternalHeatDetector(CFG)
state = override.update(
    ExternalHeatObservation(now=NOW, dhw_temp=45.0, override=True)
)
R.check(
    "a user-provided entity takes effect immediately",
    state.active and state.source == "entity",
)
state = override.update(
    ExternalHeatObservation(now=NOW + timedelta(minutes=15), override=False)
)
R.check("and clears immediately", not state.active)

off = ExternalHeatDetector(ExternalHeatConfig(enabled=False))
state = run(off, [(0, 45.0, 0.0), (15, 50.0, 0.0), (30, 55.0, 0.0)])
R.check(
    "disabled means disabled, whatever the tanks do",
    not state.active and not off.suppressing,
)


# ===========================================================================
# Item 7: modelling the unknown price horizon
# ===========================================================================
R.section("Unknown price horizon (item 7)")

model = PriceShapeModel()
CHEAP_NIGHT = [0.5] * 6 + [2.0] * 12 + [0.8] * 6
for day in range(10):
    model.observe_day(datetime(2026, 1, 5) + timedelta(days=day), CHEAP_NIGHT)

R.check("a complete day is learned", model.days[0] + model.days[1] == 10)
R.check(
    "a partial day is rejected",
    not model.observe_day(datetime(2026, 1, 20), [1.0] * 12),
    "a day missing its cheap night hours would bias every hour upward",
)
R.check(
    "the learned shape has a trough at night",
    model.predict(datetime(2026, 1, 20, 3), 1.0)
    < model.predict(datetime(2026, 1, 20, 12), 1.0),
    "a flat tail has no trough, which is the whole bug",
)

fresh_model = PriceShapeModel()
fresh_model.observe_day(datetime(2026, 1, 5), CHEAP_NIGHT)
R.check(
    "one day's evidence is heavily damped",
    abs(fresh_model.predict(datetime(2026, 1, 6, 3), 1.0) - 1.0) < 0.35,
    "commitment must be damped while the tail is mostly a guess",
)

steps = [datetime(2026, 1, 20, 0) + timedelta(minutes=15 * i) for i in range(96)]
known = [1.0] * 40
prices, mask = extend_price_series(known, 96, steps, model)
R.check("published prices are preserved exactly", list(prices[:40]) == known)
R.check("the mask marks which steps are real", mask[:40].all() and not mask[40:].any())
R.check("the tail is not flat", len(set(np.round(prices[40:], 4))) > 1)

flat_prices, flat_mask = extend_price_series(known, 96, steps, None)
R.check(
    "without a model the old flat repeat is used, not an invention",
    np.allclose(flat_prices[40:], 1.0),
)
full_prices, full_mask = extend_price_series([1.0] * 96, 96, steps, model)
R.check(
    "a fully published horizon never consults the prior",
    full_mask.all() and np.allclose(full_prices, 1.0),
)
R.check(
    "no prices at all falls back rather than crashing",
    len(extend_price_series([], 96, steps, model)[0]) == 96,
)

entries = [
    {"total": 1.0 + h * 0.1, "starts_at": f"2026-01-05T{h:02d}:00:00"}
    for h in range(24)
] + [{"total": 3.0, "starts_at": "2026-01-06T00:00:00"}]
days = hourly_from_entries(entries)
R.check("complete days are extracted", "2026-01-05" in days)
R.check("incomplete days are dropped", "2026-01-06" not in days)
R.check(
    "malformed entries do not crash the extractor",
    hourly_from_entries([{"total": None}, {"starts_at": "nonsense"}]) == {},
)


# ===========================================================================
# Item 8: capacity (peak power) tariff
# ===========================================================================
R.section("Capacity tariff (item 8)")

tariff = CapacityTariff(enabled=True, price_per_kw=60.0, peaks_averaged=3)
R.check(
    "the marginal price is the tariff divided by the peaks averaged",
    tariff.marginal_price_per_kw == 20.0,
    "charging the full tariff would over-price it threefold",
)
R.check(
    "a disabled tariff costs nothing",
    CapacityTariff(price_per_kw=60.0).marginal_price_per_kw == 0.0,
)

tracker = PeakTracker()
base = datetime(2026, 3, 1, 0, 0)
for hour, load in enumerate([2.0, 5.0, 9.0, 4.0, 7.0, 3.0]):
    tracker.observe(base + timedelta(hours=hour), load, tariff)
tracker._close_window(tariff)
R.check(
    "the billed peak averages the highest hours",
    abs(tracker.billed_peak_kw(tariff) - (9.0 + 7.0 + 5.0) / 3) < 1e-6,
    str(tracker.peaks),
)
R.check(
    "the free-headroom threshold is the lowest billed peak",
    abs(tracker.threshold_kw(tariff) - 5.0) < 1e-6,
    "below it, another hour changes nothing and costs nothing",
)

new_month = PeakTracker()
new_month.observe(datetime(2026, 4, 1, 0, 0), 3.0, tariff)
new_month._close_window(tariff)
R.check(
    "early in the month every kW is chargeable",
    new_month.threshold_kw(tariff) == 0.0,
    "there is no free headroom until the billed set is full",
)
tracker.observe(datetime(2026, 4, 1, 0, 0), 1.0, tariff)
R.check("a new month resets the peaks", tracker.month == "2026-04")

R.check(
    "staying under the threshold costs nothing",
    peak_penalty(np.full(8, 2.0), np.full(8, 1.0), 5.0, tariff, 0.25) == 0.0,
)
R.check(
    "exceeding it is priced at the marginal rate",
    abs(peak_penalty(np.full(8, 5.0), np.full(8, 2.0), 5.0, tariff, 0.25) - 40.0)
    < 1e-6,
    "2 kW over at 20/kW",
)
# A short burst inside an hourly-metered tariff barely moves the hourly mean.
burst = np.zeros(8)
burst[0] = 8.0
R.check(
    "a 15-minute burst is averaged over the metering window",
    peak_penalty(burst, np.zeros(8), 1.0, tariff, 0.25)
    < peak_penalty(np.full(8, 8.0), np.zeros(8), 1.0, tariff, 0.25),
    "penalising the instantaneous step would give away real savings",
)
R.check(
    "only the largest excess counts, not one per hour",
    abs(
        peak_penalty(np.full(8, 7.0), np.zeros(8), 5.0, tariff, 1.0)
        - 2.0 * tariff.marginal_price_per_kw
    )
    < 1e-6,
)


# ===========================================================================
# Item 9: PV self-consumption
# ===========================================================================
R.section("PV self-consumption (item 9)")

pv_cfg = pv.PVConfig(enabled=True, peak_kw=8.0, system_efficiency=0.8, export_price=0.3)
production = pv.forecast_production_kw(np.array([0.0, 500.0, 1000.0, 1400.0]), pv_cfg)
R.check("darkness produces nothing", production[0] == 0.0)
R.check("half irradiance produces half output", abs(production[1] - 3.2) < 1e-6)
R.check(
    "production is capped at the nameplate",
    production[3] == 8.0,
    "cloud-edge enhancement can push GHI over 1000 W/m2",
)
R.check(
    "a disabled array produces nothing",
    pv.forecast_production_kw(np.full(4, 1000.0), pv.PVConfig()).sum() == 0.0,
)

surplus = pv.surplus_kw(np.array([0.0, 3.0, 6.0]), np.array([1.0, 1.0, 1.0]))
R.check("surplus is net of the rest of the house", list(surplus) == [0.0, 2.0, 5.0])

effective = pv.effective_prices(
    np.array([1.5, 1.5, 1.5]), np.array([0.0, 2.0, 5.0]), 0.3
)
R.check(
    "surplus steps are priced at the export compensation",
    list(effective) == [1.5, 0.3, 0.3],
    "an extra kWh in surplus costs the export you gave up, not the import price",
)
inverted = pv.effective_prices(np.array([0.2]), np.array([5.0]), 0.9)
R.check(
    "an export price above the import price is clamped",
    inverted[0] == 0.2,
    "otherwise the objective would pay the house to consume",
)


# ===========================================================================
# Item 13: away / holiday mode
# ===========================================================================
R.section("Away and holiday mode (item 13)")

R.check(
    "a person being not_home means away",
    away_mode.interpret_presence("not_home", "person.alice") is True,
)
R.check(
    "a person being home does not",
    away_mode.interpret_presence("home", "person.alice") is False,
)
R.check(
    "a named zone still counts as away",
    away_mode.interpret_presence("work", "device_tracker.phone") is True,
)
R.check(
    "a holiday toggle being on means away",
    away_mode.interpret_presence("on", "input_boolean.holiday") is True,
    "the polarity is the opposite of a person entity, which is the whole point",
)
R.check(
    "an unknown state means unknown, not away",
    away_mode.interpret_presence("unavailable", "person.alice") is None,
)

AWAY_CFG = away_mode.AwayConfig(
    enabled=True,
    presence_entity="input_boolean.holiday",
    return_entity="input_datetime.back",
    away_temperature=16.0,
)


def resolve_away(now, return_at, current=16.0):
    return away_mode.resolve(
        AWAY_CFG,
        now=now,
        presence_raw="on",
        presence_attributes=None,
        return_raw=return_at,
        current_temp=current,
        comfort_temp=21.0,
        heat_capacity_kwh_per_c=10.0,
        available_thermal_kw=12.0,
        heat_loss_kw_per_c=0.15,
        outdoor_temp=0.0,
    )


now = datetime(2026, 2, 10, 12, 0)
far = resolve_away(now, (now + timedelta(days=3)).isoformat())
R.check("away is detected", far.active)
R.check("the deep setback applies while away", far.target_temperature == 16.0)
R.check("recovery is not started three days out", not far.recovery_active)
R.check("the recovery estimate is published", far.recovery_hours is not None)

near = resolve_away(now, (now + timedelta(hours=2)).isoformat())
R.check("recovery starts before the stated return", near.recovery_active)
R.check(
    "the comfort target is restored during recovery",
    near.target_temperature == 21.0,
    "so the plan buys the heat in the cheapest hours of the ramp",
)

no_return = resolve_away(now, None)
R.check(
    "without a return time the setback still applies",
    no_return.active and not no_return.recovery_active,
)
home = away_mode.resolve(
    AWAY_CFG,
    now=now,
    presence_raw="off",
    presence_attributes=None,
    return_raw=None,
    current_temp=21.0,
    comfort_temp=21.0,
    heat_capacity_kwh_per_c=10.0,
    available_thermal_kw=12.0,
    heat_loss_kw_per_c=0.15,
    outdoor_temp=0.0,
)
R.check("an occupied house is never set back", not home.active)
disabled_away = away_mode.resolve(
    away_mode.AwayConfig(enabled=False),
    now=now,
    presence_raw="on",
    presence_attributes=None,
    return_raw=None,
    current_temp=16.0,
    comfort_temp=21.0,
    heat_capacity_kwh_per_c=10.0,
    available_thermal_kw=12.0,
    heat_loss_kw_per_c=0.15,
    outdoor_temp=0.0,
)
R.check("disabled means the feature cannot cost anything", not disabled_away.active)

R.check(
    "a warm house needs no recovery time",
    away_mode.estimate_recovery_hours(21.0, 21.0, 10.0, 12.0, 0.15, 0.0) == 0.0,
)
R.check(
    "a pump that cannot reach the target starts as early as allowed",
    away_mode.estimate_recovery_hours(10.0, 21.0, 10.0, 0.5, 0.5, -20.0)
    == away_mode.MAX_RECOVERY_HOURS,
    "refusing to plan recovery would be worse than starting early",
)

cal = away_mode.resolve(
    away_mode.AwayConfig(enabled=True, presence_entity="calendar.holidays"),
    now=now,
    presence_raw="on",
    presence_attributes={"end_time": (now + timedelta(hours=1)).isoformat()},
    return_raw=None,
    current_temp=16.0,
    comfort_temp=21.0,
    heat_capacity_kwh_per_c=10.0,
    available_thermal_kw=12.0,
    heat_loss_kw_per_c=0.15,
    outdoor_temp=0.0,
)
R.check(
    "a calendar event supplies its own return time",
    cal.return_time is not None and cal.recovery_active,
)


# ===========================================================================
# Item 11: closed-loop accuracy
# ===========================================================================
R.section("Closed-loop accuracy (item 11)")

acc = AccuracyTracker()
for i in range(20):
    acc.record(
        AccuracySample(
            when=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=30 * i),
            predicted_power_kw=2.0,
            actual_power_kw=2.4,
            predicted_temp=21.0,
            actual_temp=20.5,
            predicted_cost=2.0,
            actual_cost=2.4,
            outdoor_temp=2.0,
            humidity=85.0,
        )
    )
R.check("the mean absolute error is reported", acc.temperature_mae() == 0.5)
R.check(
    "the bias keeps its sign",
    acc.temperature_bias() == 0.5,
    "an absolute error cannot tell noise from a consistently optimistic model",
)
R.check("the power ratio is reported", acc.power_ratio() == 1.2)
R.check(
    "the cost error is signed and in percent",
    abs(acc.cost_accuracy() + 16.67) < 0.1,
)
R.check("trust falls as the error grows", acc.trust() < 1.0)

perfect = AccuracyTracker()
perfect.record(
    AccuracySample(
        when=NOW, predicted_temp=21.0, actual_temp=21.0, predicted_power_kw=2.0,
        actual_power_kw=2.0,
    )
)
R.check("a perfect model is fully trusted", perfect.trust() == 1.0)
R.check("an empty tracker reports nothing rather than zero", AccuracyTracker().temperature_mae() is None)

partial = AccuracyTracker()
partial.record(AccuracySample(when=NOW, predicted_temp=21.0, actual_temp=20.8))
R.check(
    "temperature accuracy works without a power meter",
    partial.temperature_mae() is not None and partial.power_ratio() is None,
)

R.check(
    "the delivered ratio inverts the power ratio",
    abs(
        delivered_ratio(
            AccuracySample(when=NOW, predicted_power_kw=2.0, actual_power_kw=2.5)
        )
        - 0.8
    )
    < 1e-9,
    "drawing more for the same outcome means less heat per kWh",
)
R.check(
    "an idle interval carries no information",
    delivered_ratio(
        AccuracySample(when=NOW, predicted_power_kw=0.0, actual_power_kw=0.0)
    )
    is None,
)

restored = AccuracyTracker.from_dict(acc.as_dict())
R.check("history survives a restart", len(restored.samples) > 0)
R.check("corrupt stored history is ignored", len(AccuracyTracker.from_dict({"samples": ["x"]}).samples) == 0)


# ===========================================================================
# Item 14: defrost / cold-humid derate
# ===========================================================================
R.section("Defrost derate (item 14)")

derate = DefrostDerate()
R.check(
    "with no evidence the derate changes nothing",
    derate.factor(2.0, 85.0) == 1.0,
    "a hand-coded datasheet curve would be wrong for most units",
)
derate.observe(2.0, 85.0, 0.75)
R.check(
    "one observation barely moves it",
    derate.factor(2.0, 85.0) > 0.99,
    "a derate the size of the effect should need more than one sample",
)
for _ in range(60):
    derate.observe(2.0, 85.0, 0.75)
R.check("sustained evidence does move it", derate.factor(2.0, 85.0) < 0.95)
R.check(
    "the derate is local to the frosting band",
    derate.factor(15.0, 85.0) == 1.0,
    "a mild afternoon must not inherit a frosting-band derate",
)
R.check(
    "dry cold air is a separate bucket",
    derate.factor(2.0, 30.0) == 1.0,
    "frost needs moisture",
)
for _ in range(100):
    derate.observe(2.0, 85.0, 0.1)
R.check("an implausible derate is clamped", derate.factor(2.0, 85.0) > 0.5)
R.check(
    "a nonsense ratio is discarded outright",
    (lambda d: (d.observe(2.0, 85.0, -1.0), d.observe(2.0, 85.0, 50.0), d.total_samples)[-1])(
        DefrostDerate()
    )
    == 0,
)
R.check("the buckets are reportable", len(derate.summary()) >= 1)
R.check(
    "the derate survives a restart",
    abs(
        DefrostDerate.from_dict(derate.as_dict()).factor(2.0, 85.0)
        - derate.factor(2.0, 85.0)
    )
    < 1e-9,
)
R.check(
    "a corrupt stored derate falls back to neutral",
    DefrostDerate.from_dict({"factors": "nonsense"}).factor(2.0, 85.0) == 1.0,
)

# The derate has to actually reach the COP the optimizer prices plans through.
params = ThermalParameters()
model = ThermalModel(params)
plain = model.compute_cop(2.0)
params.defrost_derate = derate
R.check(
    "the learned derate lowers the COP the optimizer uses",
    model.compute_cop(2.0, 85.0) < plain,
)
params.defrost_derate = None
params.cop_scale = 0.8
R.check(
    "the measured COP correction also applies",
    abs(model.compute_cop(2.0) - plain * 0.8) < 1e-9,
)
params.cop_scale = 1.0


# ===========================================================================
# Item 17: building presets
# ===========================================================================
R.section("Building presets (item 17)")

light = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_TIMBER_CRAWLSPACE,
        era=presets.ERA_POST_2005,
        heated_area_m2=140,
    )
)
heavy = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_MASONRY,
        era=presets.ERA_PRE_1960,
        heated_area_m2=140,
    )
)
R.check(
    "a masonry house has more thermal mass than a timber one",
    heavy["house_thermal_mass"] > light["house_thermal_mass"],
)
R.check(
    "an older house loses more heat",
    heavy["house_heat_loss_coefficient"] > light["house_heat_loss_coefficient"],
)
R.check(
    "loss scales with heated area",
    presets.derive(presets.BuildingPreset(heated_area_m2=280))[
        "house_heat_loss_coefficient"
    ]
    > presets.derive(presets.BuildingPreset(heated_area_m2=140))[
        "house_heat_loss_coefficient"
    ],
)

floor_house = presets.BuildingPreset(lower_emitter=presets.EMITTER_FLOOR)
rad_house = presets.BuildingPreset(lower_emitter=presets.EMITTER_RADIATORS)
R.check(
    "floor heating adds an actively charged store",
    presets.derive(floor_house)["slab_thermal_mass"]
    > presets.derive(rad_house)["slab_thermal_mass"],
)
R.check(
    "radiators respond faster than floor heating",
    presets.response_hours(rad_house) < presets.response_hours(floor_house),
    "this bounds how far ahead load can usefully be shifted",
)

basement = presets.derive(
    presets.BuildingPreset(foundation=presets.FOUNDATION_BASEMENT)
)
plain_found = presets.derive(
    presets.BuildingPreset(foundation=presets.FOUNDATION_NONE)
)
R.check(
    "a heated basement adds both mass and loss",
    basement["house_thermal_mass"] > plain_found["house_thermal_mass"]
    and basement["house_heat_loss_coefficient"]
    > plain_found["house_heat_loss_coefficient"],
)

two_zone = presets.derive(
    presets.BuildingPreset(
        two_zone=True,
        upper_emitter=presets.EMITTER_RADIATORS,
        lower_emitter=presets.EMITTER_FLOOR,
        upper_area_ratio=0.5,
    )
)
R.check(
    "a slab-heated lower floor carries the heavy mass",
    two_zone["lower_floor_thermal_mass"] > two_zone["upper_floor_thermal_mass"],
)
R.check(
    "the radiator power fraction follows the emitters",
    abs(two_zone["radiator_power_fraction"] - 0.5) < 1e-6,
)

R.check(
    "nonsense options are clamped rather than propagated",
    presets.BuildingPreset(structure="unicorn", era="tomorrow", heated_area_m2=1e9)
    .validate()
    .structure
    == presets.STRUCTURE_TIMBER_SLAB,
)
R.check(
    "the derived values are presented as a starting point",
    "learn" in presets.describe(presets.BuildingPreset())["note"].lower(),
    "users must not read a preset as a claim about their building",
)

# The derived values must be usable by the model they are derived for.
derived_params = ThermalParameters.from_config(
    {**presets.derive(presets.BuildingPreset()), "heat_pump_max_power": 5.0}
)
R.check(
    "derived values are accepted by the thermal model",
    derived_params.room_thermal_mass > 0 and derived_params.heat_loss_coefficient > 0,
)


# ===========================================================================
# Item 18: active system identification
# ===========================================================================
R.section("Active system identification (item 18)")

sysid = SystemIdentification(SysIdConfig(enabled=True))
R.check("arming works when enabled", sysid.arm(NOW) and sysid.phase == PHASE_ARMED)
R.check("arming twice is a no-op", not sysid.arm(NOW))

disabled_sysid = SystemIdentification(SysIdConfig(enabled=False))
R.check("a disabled experiment cannot be armed", not disabled_sysid.arm(NOW))

night = datetime(2026, 2, 1, 1, 0, tzinfo=UTC)
cheap = np.linspace(0.5, 2.0, 96)
ok, why = sysid.conditions_met(night, 2.0, 0.55, cheap, 5)
R.check("mild, cheap, night conditions are accepted", ok, why)
R.check(
    "a cold night is refused",
    not sysid.conditions_met(night, -20.0, 0.55, cheap, 5)[0],
)
R.check(
    "an expensive hour is refused",
    not sysid.conditions_met(night, 2.0, 1.9, cheap, 5)[0],
)
R.check(
    "the middle of the afternoon is refused",
    not sysid.conditions_met(
        datetime(2026, 2, 1, 15, 0, tzinfo=UTC), 2.0, 0.55, cheap, 5
    )[0],
)
R.check(
    "a converged house is not experimented on",
    not sysid.conditions_met(night, 2.0, 0.55, cheap, 5000)[0],
)

# A synthetic house, driven through a whole experiment.
run_sysid = SystemIdentification(
    SysIdConfig(
        enabled=True,
        settle_hours=0.5,
        step_hours=2.0,
        relax_hours=2.0,
        max_excursion_c=5.0,
    )
)
run_sysid.arm(night)
capacity, ua, outdoor, cop = 8.0, 0.2, 0.0, 3.0
room = 20.0
t = night
override_seen = False
for i in range(40):
    # The override is electrical power, which is what the rest of the
    # integration speaks; the fit works in thermal terms, so the COP is passed
    # in rather than assumed. Getting this wrong scales both identified
    # parameters by the COP while leaving their ratio correct, which is exactly
    # the kind of error that looks plausible.
    power = run_sysid.step(
        now=t,
        room_temp=room,
        outdoor_temp=outdoor,
        price=0.55,
        price_horizon=cheap,
        learner_samples=5,
        max_power_kw=5.0,
        cop=cop,
    )
    if power:
        override_seen = True
    # Integrate the true first-order dynamics the experiment is trying to find.
    thermal = (power or 0.0) * cop
    room += (thermal - ua * (room - outdoor)) / capacity * 0.25
    t += timedelta(minutes=15)

R.check("the experiment injects a step", override_seen)
R.check("it completes", run_sysid.phase == PHASE_DONE)
result = run_sysid.result
R.check("it identifies something", result.completed, result.reason)
if result.completed:
    R.check(
        "the identified heat loss is close to the truth",
        abs(result.heat_loss_kw_per_c - ua) < ua * 0.35,
        f"got {result.heat_loss_kw_per_c:.4f}, truth {ua}",
    )
    R.check(
        "the identified capacity is close to the truth",
        abs(result.thermal_mass_kwh_per_c - capacity) < capacity * 0.35,
        f"got {result.thermal_mass_kwh_per_c:.2f}, truth {capacity}",
    )
    R.check("confidence is reported", 0.0 <= result.confidence <= 1.0)

# Comfort is a hard constraint on the experiment, not a cost term.
strict = SystemIdentification(
    SysIdConfig(enabled=True, settle_hours=0.0, max_excursion_c=0.2)
)
strict.arm(night)
strict.step(
    now=night, room_temp=20.0, outdoor_temp=2.0, price=0.5,
    price_horizon=cheap, learner_samples=5, max_power_kw=5.0,
)
strict.step(
    now=night + timedelta(minutes=15), room_temp=23.0, outdoor_temp=2.0,
    price=0.5, price_horizon=cheap, learner_samples=5, max_power_kw=5.0,
)
R.check(
    "an excursion beyond the comfort limit aborts the experiment",
    not strict.active,
)
R.check("the abort is recorded with a reason", "excursion" in strict.result.reason)

no_data = SystemIdentification(SysIdConfig(enabled=True))
R.check(
    "a fit with no samples fails cleanly",
    not no_data.identify().completed,
)

repeat = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=30))
repeat.last_run = NOW - timedelta(days=2)
R.check("a recent run blocks another", not repeat.arm(NOW))


# ===========================================================================
# Item 19: revealed-preference comfort tuning
# ===========================================================================
R.section("Revealed-preference comfort tuning (item 19)")

learner = ComfortLearner(configured_weight=5.0, learned_weight=5.0)
when = datetime(2026, 1, 1, 18, 0, tzinfo=UTC)
for i in range(6):
    learner.record_override(
        OverrideEvent(
            when=when + timedelta(days=i),
            delta_c=1.5,
            indoor_temp=19.0,
            planned_setpoint=19.0,
            relative_price=1.8,
        )
    )
R.check(
    "repeated upward overrides raise the comfort weight",
    learner.learned_weight > 5.0,
    f"{learner.learned_weight:.2f}",
)

single = ComfortLearner(configured_weight=5.0, learned_weight=5.0)
single.record_override(
    OverrideEvent(when=when, delta_c=1.0, indoor_temp=19.0, planned_setpoint=19.0)
)
R.check(
    "one override does not move it",
    single.learned_weight == 5.0,
    "a party or an open window is not a preference",
)

tiny = ComfortLearner(configured_weight=5.0, learned_weight=5.0)
for i in range(20):
    tiny.record_override(
        OverrideEvent(
            when=when + timedelta(days=i),
            delta_c=0.1,
            indoor_temp=21.0,
            planned_setpoint=21.0,
        )
    )
R.check("a rounding-sized override is ignored entirely", tiny.overrides == 0)

quiet_learner = ComfortLearner(configured_weight=8.0, learned_weight=8.0)
for i in range(40):
    quiet_learner.record_quiet_period(
        when + timedelta(days=i), temperature_span=0.1, comfort_band=2.0, days=1.0
    )
R.check(
    "a long flat, uncomplained-about profile lowers it",
    quiet_learner.learned_weight < 8.0,
    "without this the learner could only ever ratchet upward",
)
swingy = ComfortLearner(configured_weight=8.0, learned_weight=8.0)
for i in range(40):
    swingy.record_quiet_period(
        when + timedelta(days=i), temperature_span=1.9, comfort_band=2.0, days=1.0
    )
R.check(
    "a house already using its whole band is not evidence",
    swingy.learned_weight == 8.0,
)

extreme = ComfortLearner(configured_weight=5.0, learned_weight=5.0)
for i in range(200):
    extreme.record_override(
        OverrideEvent(
            when=when + timedelta(hours=i),
            delta_c=3.0,
            indoor_temp=18.0,
            planned_setpoint=18.0,
            relative_price=2.5,
        )
    )
R.check(
    "the learned value stays inside sane bounds",
    COMFORT_WEIGHT_MIN <= extreme.learned_weight <= COMFORT_WEIGHT_MAX,
)

learner.reset()
R.check("reset returns to the configured value", learner.learned_weight == 5.0)
R.check("reset forgets the evidence", learner.evidence == 0.0 and learner.overrides == 0)

reconfigured = ComfortLearner.from_dict(extreme.as_dict(), 12.0)
R.check(
    "changing the configured weight discards what was learned against the old one",
    reconfigured.learned_weight == 12.0,
)
same = ComfortLearner.from_dict(extreme.as_dict(), 5.0)
R.check(
    "an unchanged configured weight keeps the learning",
    abs(same.learned_weight - extreme.learned_weight) < 1e-9,
)
R.check(
    "corrupt stored learning falls back to the configured value",
    ComfortLearner.from_dict({"learned_weight": "banana", "configured_weight": 5.0}, 5.0)
    .learned_weight
    == 5.0,
)


# ===========================================================================
# Item 20: the house as a virtual battery
# ===========================================================================
R.section("The house as a virtual battery (item 20)")

bat_params = ThermalParameters()
bat_params.dhw_enabled = True
state = ThermalState(
    room_temperature=21.0,
    slab_temperature=23.0,
    outdoor_temperature=0.0,
    dhw_temperature=52.0,
    buffer_tank_temperature=40.0,
)
bat = battery_view.build(
    bat_params,
    state,
    comfort_min=19.0,
    comfort_max=23.0,
    dhw_min=45.0,
    dhw_max=65.0,
    cop=3.2,
)
view = bat.as_dict()
R.check("stored energy is positive for a warm house", view["stored_energy_kwh"] > 0)
R.check("state of charge is a percentage", 0 <= view["state_of_charge_percent"] <= 100)
R.check(
    "the charge rate is thermal, not electrical",
    view["charge_rate_kw"] > view["charge_power_electrical_kw"],
    "charging happens at COP > 1",
)
R.check("autonomy is reported", view["hours_of_autonomy"] is not None)
R.check(
    "round-trip efficiency is thermal and at most 100%",
    0 <= view["round_trip_efficiency_6h"] <= 100,
    "an electrical figure would exceed 100% and mean nothing",
)
R.check("every store is listed", len(view["components"]) >= 3)

cold = battery_view.build(
    bat_params,
    ThermalState(
        room_temperature=19.0, slab_temperature=19.0, outdoor_temperature=0.0,
        dhw_temperature=45.0, buffer_tank_temperature=19.0,
    ),
    comfort_min=19.0,
    comfort_max=23.0,
    dhw_min=45.0,
    dhw_max=65.0,
    cop=3.2,
)
R.check(
    "a house at its comfort floor is an empty battery",
    cold.stored_kwh < 1e-6,
    "energy below the minimum acceptable temperature is not available",
)
below = battery_view.StorageComponent(
    name="x", capacity_kwh_per_c=5.0, temperature=15.0,
    min_temperature=19.0, max_temperature=23.0,
)
R.check("a store below its floor never reports negative energy", below.stored_kwh == 0.0)



# ===========================================================================
# Regressions found in review
# ===========================================================================
R.section("Regressions")

# --- The COP learner must not erase its own learning ----------------------
#
# ``cop_scale`` multiplies the *nameplate* curve, and the modelled COP already
# has the current scale folded in. Using the observed correction as the new
# absolute scale makes 1.0 the only fixed point, so a sample that perfectly
# confirms the model still drags the parameter back to "trust the nameplate".
def cop_update(scale, commanded, measured, alpha=0.03, max_step=0.05):
    """The coordinator's update rule, extracted so it can be driven directly."""
    target = scale * commanded / measured
    updated = (1.0 - alpha) * scale + alpha * target
    updated = float(
        np.clip(updated, scale - scale * max_step, scale + scale * max_step)
    )
    return float(np.clip(updated, COP_SCALE_MIN, COP_SCALE_MAX))


scale = 1.4
for _ in range(60):
    # A perfectly confirming sample: the pump draws exactly what was asked.
    scale = cop_update(scale, 3.0, 3.0)
R.check(
    "a confirming sample leaves the learned COP scale alone",
    abs(scale - 1.4) < 1e-6,
    f"drifted to {scale:.4f}",
)

# Driven in closed loop, which is how it actually runs: the optimizer sizes the
# command from the *modelled* COP, so a wrong model produces a mismatch that
# shrinks as the model is corrected. The learned scale must converge on the
# real efficiency, not chase the residual to zero.
NAMEPLATE_COP = 3.0
TRUE_COP = 3.75          # the unit is 25% better than its nameplate curve
HEAT_DEMAND_KW = 7.5     # thermal output the house needs

scale = 1.0
for _ in range(400):
    modelled_cop = NAMEPLATE_COP * scale
    commanded = HEAT_DEMAND_KW / modelled_cop
    measured = HEAT_DEMAND_KW / TRUE_COP
    scale = cop_update(scale, commanded, measured)

R.check(
    "closed-loop learning converges on the real efficiency",
    abs(NAMEPLATE_COP * scale - TRUE_COP) < 0.05,
    f"learned COP {NAMEPLATE_COP * scale:.3f}, truth {TRUE_COP}",
)
R.check(
    "and then stays there",
    abs(cop_update(scale, HEAT_DEMAND_KW / (NAMEPLATE_COP * scale),
                   HEAT_DEMAND_KW / TRUE_COP) - scale) < 1e-3,
    "a correct model must be a fixed point of the update",
)

# The bound exists because a mis-scaled power entity, or a plan the user is
# overriding, breaks the closed loop the convergence above relies on.
runaway = 1.0
for _ in range(500):
    runaway = cop_update(runaway, 1.0, 4.0)
R.check(
    "a persistently broken feedback loop is bounded, not unbounded",
    runaway >= COP_SCALE_MIN - 1e-9,
    f"{runaway:.4f}",
)

# --- Space-only power must not be compared against a whole-pump meter -----
#
# ``current_action["power"]`` is the space heating allocation; ``dhw_power`` is
# separate. A meter sees only the sum, so comparing the space figure alone
# makes a planned hot-water charge look like the pump drawing power nobody
# asked for.
class _Coord:
    _commanded_power = Coord._commanded_power


c = _Coord()
c._current_action = {"power": 1.2, "dhw_power": 4.8}
R.check(
    "the commanded total includes hot water",
    c._commanded_power() == 6.0,
    "otherwise a DHW charge reads as an external heat source, a collapsed COP "
    "and a defrost derate, all at once",
)
c._current_action = {"power": 2.0}
R.check("a plan with no hot water still works", c._commanded_power() == 2.0)
c._current_action = {}
R.check("an empty action is zero, not an error", c._commanded_power() == 0.0)

# The concrete symptom: a normal DHW charge with space heating idle must not
# be mistaken for a wood fire.
charge = ExternalHeatDetector(ExternalHeatConfig(enabled=True))
charge_state = None
charge_start = datetime(2026, 1, 12, 2, 0, tzinfo=UTC)
for i in range(4):
    # 10 °C/h rise, well inside what the pump itself can deliver.
    charge_state = charge.update(
        ExternalHeatObservation(
            now=charge_start + timedelta(minutes=30 * i),
            dhw_temp=45.0 + i * 5.0,
            commanded_power_kw=4.8,   # the DHW allocation, correctly included
            dhw_max_rise_c_per_h=12.0,
        )
    )
R.check(
    "a planned hot-water charge is not mistaken for a wood fire",
    not charge_state.active,
    "; ".join(charge_state.evidence),
)

# --- The defrost derate's humidity bucket must actually be consulted ------
#
# The derate learns per (temperature, humidity) bucket. If lookup always lands
# in the dry bucket, everything observed in humid frosting conditions — the
# conditions it exists for — is recorded and then never applied.
humid = DefrostDerate()
for _ in range(60):
    humid.observe(2.0, 90.0, 0.75)

humid_params = ThermalParameters()
humid_model = ThermalModel(humid_params)
nominal = humid_model.compute_cop(2.0)
humid_params.defrost_derate = humid

humid_params.ambient_humidity = 30.0
R.check(
    "a dry cold day does not inherit the humid derate",
    abs(humid_model.compute_cop(2.0) - nominal) < 1e-9,
)
humid_params.ambient_humidity = 90.0
R.check(
    "the ambient humidity selects the bucket that was learned",
    humid_model.compute_cop(2.0) < nominal * 0.98,
    f"{humid_model.compute_cop(2.0):.3f} vs {nominal:.3f}",
)
humid_params.ambient_humidity = None
R.check(
    "an explicit humidity still wins over the ambient default",
    humid_model.compute_cop(2.0, 90.0) < nominal * 0.98,
)

# --- The foundation mass adjustment must be applied once ------------------
basement_two_zone = presets.derive(
    presets.BuildingPreset(
        two_zone=True,
        foundation=presets.FOUNDATION_BASEMENT,
        lower_emitter=presets.EMITTER_FLOOR,
        upper_emitter=presets.EMITTER_RADIATORS,
    )
)
plain_two_zone = presets.derive(
    presets.BuildingPreset(
        two_zone=True,
        foundation=presets.FOUNDATION_NONE,
        lower_emitter=presets.EMITTER_FLOOR,
        upper_emitter=presets.EMITTER_RADIATORS,
    )
)
ratio = (
    basement_two_zone["lower_floor_thermal_mass"]
    / plain_two_zone["lower_floor_thermal_mass"]
)
R.check(
    "a heated basement scales the slow store once, not twice",
    ratio < 1.30,
    f"lower floor mass scaled by {ratio:.3f}; the adjustment is 1.25",
)


# ===========================================================================
# Configuration mapping
# ===========================================================================
R.section("Configuration mapping")

import dataclasses

from heatpump_optimizer import const as hp_const

# The table-driven ``from_config`` is only correct if it actually covers the
# parameters. A field the table forgets keeps its dataclass default forever,
# silently ignoring whatever the user configured — which is invisible until
# someone wonders why a setting does nothing.
declared = {f.name for f in dataclasses.fields(ThermalParameters)}
# Fields that are deliberately not user-configurable.
runtime_only = {
    "dhw_hourly_draw_pattern",  # learned from observed draws
    "defrost_derate",           # learned per temperature/humidity bucket
    "ambient_humidity",         # current conditions, set per update
    "cop_scale",                # learned from measured power
    "cop_reference_temp",       # a property of the COP curve, not the house
    "internal_gains",           # not exposed in the config flow
    "dhw_windows",              # parsed separately from a string spec
    "two_zone_enabled",         # inferred from which keys are present
    "dhw_enabled",              # inferred from which keys are present
}

def reachable(name: str) -> str | None:
    """Find a config key that actually changes ``name``, or None.

    Booleans are probed by flipping them away from their default rather than
    by a sentinel value: the mapping coerces with ``bool()``, so any sentinel
    would come back as True and look like a match for every boolean field.
    """
    default_value = getattr(ThermalParameters.from_config({}), name)
    if isinstance(default_value, bool):
        sentinel = not default_value
    else:
        sentinel = 0.5 if default_value != 0.5 else 0.25
    for candidate in dir(hp_const):
        if not candidate.startswith("CONF_"):
            continue
        try:
            built = ThermalParameters.from_config(
                {getattr(hp_const, candidate): sentinel}
            )
        except Exception:
            continue
        if getattr(built, name, None) == sentinel:
            return candidate
    return None


probe = {name: reachable(name) for name in declared - runtime_only}

unreachable = sorted(n for n, k in probe.items() if k is None)
R.check(
    "every configurable parameter is reachable from a config key",
    not unreachable,
    ", ".join(unreachable),
)

# Round-tripping: a value set in the config must arrive in the parameters.
sample = {
    hp_const.CONF_HOUSE_THERMAL_MASS: 12.5,
    hp_const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.22,
    hp_const.CONF_HEAT_PUMP_MAX_POWER: 9.0,
    hp_const.CONF_DHW_SETPOINT: 58.0,
    hp_const.CONF_DHW_TANK_VOLUME: 300.0,
    hp_const.CONF_WIND_SENSITIVITY: 0.25,
    hp_const.CONF_ECL110_DISPLACE_MAX: 12.0,
}
built = ThermalParameters.from_config(sample)
R.check("configured thermal mass arrives", built.room_thermal_mass == 12.5)
R.check("configured heat loss arrives", built.heat_loss_coefficient == 0.22)
R.check("configured max power arrives", built.max_electrical_power == 9.0)
R.check("configured DHW setpoint arrives", built.dhw_setpoint == 58.0)
R.check("configured wind sensitivity arrives", built.wind_sensitivity == 0.25)
R.check("configured displace limit arrives", built.ecl110_displace_max == 12.0)

R.check(
    "an empty config yields the documented defaults",
    ThermalParameters.from_config({}).room_thermal_mass
    == hp_const.DEFAULT_HOUSE_THERMAL_MASS,
)
R.check(
    "two-zone is inferred from the presence of its keys",
    ThermalParameters.from_config(
        {hp_const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
    ).two_zone_enabled
    and not ThermalParameters.from_config({}).two_zone_enabled,
    "an entry written before two-zone existed must keep working",
)
R.check(
    "hot water is inferred from the presence of its keys",
    ThermalParameters.from_config(
        {hp_const.CONF_DHW_TANK_VOLUME: 200.0}
    ).dhw_enabled
    and not ThermalParameters.from_config({}).dhw_enabled,
)
R.check(
    "a boolean stored as a string is still a boolean",
    ThermalParameters.from_config(
        {hp_const.CONF_DHW_LEGIONELLA_ENABLED: "yes"}
    ).dhw_legionella_enabled
    is True,
)
R.check(
    "an unparseable window spec falls back rather than raising",
    ThermalParameters.from_config(
        {hp_const.CONF_DHW_WINDOWS: "not a time range"}
    ).dhw_windows
    == [],
)


# ===========================================================================
# Runtime parameter updates
# ===========================================================================
R.section("Runtime parameter updates")

import asyncio

from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

param_coord = HeatPumpOptimizerCoordinator(
    FakeHass(),
    FakeEntry(
        data={
            "tibber_token": "x",
            "weather_entity": "weather.home",
            "dhw_tank_volume": 200.0,
            "upper_floor_thermal_mass": 3.0,
        }
    ),
)

# The table covers plain assignments; every one has to actually land.
asyncio.run(
    param_coord.async_update_thermal_params(
        {
            "house_thermal_mass": 14.0,
            "slab_thermal_mass": 9.0,
            "heat_pump_cop_nominal": 4.2,
            "dhw_setpoint": 60.0,
            "dhw_min_temperature": 48.0,
            "window_area": 22.0,
            "wind_sensitivity_factor": 0.3,
            "radiator_power_fraction": 0.55,
        }
    )
)
params = param_coord._thermal_params
R.check("a mapped parameter is applied", params.room_thermal_mass == 14.0)
R.check("a renamed parameter is applied", params.dhw_min_temp == 48.0)
R.check("COP nominal is applied", params.cop_nominal == 4.2)
R.check("a two-zone parameter is applied", params.radiator_power_fraction == 0.55)
R.check(
    "the model is rebuilt against the new parameters",
    param_coord._thermal_model.params is params
    and param_coord._optimizer.model is param_coord._thermal_model,
    "the model holds the parameters by reference at construction",
)

# The special cases exist because each has a consequence beyond itself.
param_coord._house_heat_loss_samples = 50
param_coord._apply_house_heat_loss_scale(1.8)
asyncio.run(
    param_coord.async_update_thermal_params({"house_heat_loss_coefficient": 0.3})
)
R.check(
    "a new nameplate heat loss resets what was learned against the old one",
    param_coord._house_heat_loss_scale == 1.0
    and param_coord._house_heat_loss_samples == 0,
)

asyncio.run(
    param_coord.async_update_thermal_params({"ecl110_displace_max": 14.0})
)
R.check(
    "the displace limit is mirrored where the publisher clamps against it",
    param_coord._ecl110_displace_max == 14.0
    and params.ecl110_displace_max == 14.0,
)

asyncio.run(
    param_coord.async_update_thermal_params({"dhw_windows": "07:00-09:00"})
)
R.check(
    "a valid window spec is parsed",
    param_coord._thermal_params.dhw_windows == [(7.0, 9.0)],
    str(param_coord._thermal_params.dhw_windows),
)
before = list(param_coord._thermal_params.dhw_windows)
asyncio.run(param_coord.async_update_thermal_params({"dhw_windows": "garbage"}))
R.check(
    "an invalid window spec is ignored rather than clearing the schedule",
    param_coord._thermal_params.dhw_windows == before,
)

param_coord._dhw_cooling_samples = 30
asyncio.run(param_coord.async_update_thermal_params({"dhw_cooling_rate": 0.5}))
R.check(
    "an explicit cooling rate restarts the learner from it",
    abs(param_coord._dhw_cooling_rate - 0.5) < 1e-9
    and param_coord._dhw_cooling_samples == 0,
)

R.check(
    "an unknown parameter is ignored, not fatal",
    asyncio.run(
        param_coord.async_update_thermal_params({"not_a_parameter": 1})
    )
    is None,
)

sys.exit(R.close("FEATURE CHECKS"))
