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
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    peak_cost,
    peak_penalty,
    realised_peak,
)
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


R.section("Wood furnace displacement (item 28)")

# The valve outlet identifies the mixing fraction directly:
# f = (T_outlet - T_hp) / (T_wood - T_hp). It turns the boolean fire into
# "the furnace covers 70% of space heating right now", which is what lets
# electric heat stand down by that much instead of all-or-nothing.


def _fire_obs(minutes, **kw):
    return ExternalHeatObservation(
        now=datetime(2026, 1, 10, 18, 0, tzinfo=UTC) + timedelta(minutes=minutes),
        dhw_temp=kw.pop("dhw_temp", None),
        commanded_power_kw=0.0,
        measured_power_kw=0.0,
        **kw,
    )


_wd = ExternalHeatDetector(ExternalHeatConfig(
    enabled=True, confirm_samples=2, release_samples=2,
    wood_tank_volume_l=500.0,
))
# Light the fire via the buffer rising with the pump off.
_wd.update(_fire_obs(0, buffer_temp=40.0))
_wd.update(_fire_obs(15, buffer_temp=41.0))
_wd_state = _wd.update(_fire_obs(
    30, buffer_temp=42.0,
    outlet_temp=61.0, wood_top=70.0, wood_bottom=55.0,
    hp_tank_temp=40.0, space_demand_kw=6.0,
))
R.check(
    "the outlet temperature identifies the mixing fraction",
    abs(_wd_state.displacement - 0.7) < 1e-6,
    f"(61-40)/(70-40) should be 0.70, got {_wd_state.displacement:.2f}",
)
R.check(
    "and scales to an absolute free-heat figure",
    abs(_wd_state.free_heat_kw - 4.2) < 1e-6,
    f"0.70 of 6 kW demand, got {_wd_state.free_heat_kw:.2f} kW",
)
R.check(
    "the wood tank's remaining energy is measured, not assumed",
    _wd_state.wood_energy_kwh is not None and _wd_state.wood_energy_kwh > 10.0,
    f"got {_wd_state.wood_energy_kwh} kWh from a 500 L tank at 62.5 C mean",
)
R.check(
    "displacement is a separate field from confidence",
    _wd_state.confidence == 1.0 and _wd_state.displacement < 1.0,
    "confidence means how recently; displacement means how much",
)

# Never predict an unlit fire: same sensors, no active state, no displacement.
_cold_det = ExternalHeatDetector(ExternalHeatConfig(enabled=True))
_cold_state = _cold_det.update(_fire_obs(
    0, outlet_temp=61.0, wood_top=70.0, wood_bottom=55.0,
    hp_tank_temp=40.0, space_demand_kw=6.0,
))
R.check(
    "no active fire means no displacement, whatever the sensors read",
    _cold_state.displacement == 0.0 and _cold_state.free_heat_kw == 0.0,
    "lighting a fire is human behaviour and is never predicted",
)

# Unidentifiable mix: the wood side barely above the pump side.
_flat_state = _wd.update(_fire_obs(
    45, buffer_temp=43.0,
    outlet_temp=40.5, wood_top=41.0, wood_bottom=40.0,
    hp_tank_temp=40.0, space_demand_kw=6.0,
))
R.check(
    "too small a margin reads as zero, not as a noisy fraction",
    _flat_state.displacement == 0.0,
    "a 1 K difference is sensor noise, not a measurement of the mix",
)

# A stalled sensor maps to absence, and absence means zero. This is the
# backlog's named verification: a stalled hot probe must stop being
# believed rather than look like an indefinite free fire.
_stale_state = _wd.update(_fire_obs(
    60, buffer_temp=44.0,
    outlet_temp=None, wood_top=70.0, hp_tank_temp=40.0, space_demand_kw=6.0,
))
R.check(
    "a missing or stale outlet reading zeroes the displacement",
    _stale_state.displacement == 0.0 and _stale_state.free_heat_kw == 0.0,
    "staleness maps to absence upstream, and absence must fail closed",
)

# The forecast the optimizer receives is bounded three independent ways.
_fc_det = ExternalHeatDetector(ExternalHeatConfig(
    enabled=True, decay_minutes=360.0, wood_tank_volume_l=500.0,
))
_fc_det.state.active = True
_fc_det.state.free_heat_kw = 6.0
_fc_det.state.wood_energy_kwh = 100.0
_fc = _fc_det.forecast_free_heat(96, 0.25)
R.check(
    "the forecast never promises past its hard two-hour cap",
    _fc[7] > 0.0 and all(v == 0.0 for v in _fc[8:]),
    "whatever the detector's own decay says -- a wrong promise here is a "
    "cold house in winter",
)
R.check(
    "and fades over that horizon rather than carrying full weight",
    _fc[0] == 6.0 and _fc[7] < _fc[0] * 0.2,
    f"first step {_fc[0]:.1f} kW, last promised step {_fc[7]:.2f} kW",
)
_fc_det.state.wood_energy_kwh = 0.5
_fc_low = _fc_det.forecast_free_heat(96, 0.25)
R.check(
    "the promise never exceeds what the wood tank measurably holds",
    sum(v * 0.25 for v in _fc_low) <= 0.5 + 1e-9,
    f"promised {sum(v * 0.25 for v in _fc_low):.2f} kWh against 0.5 in the tank",
)
_fc_det.state.active = False
_fc_det.state.fading = False
_fc_det.state.free_heat_kw = 0.0
R.check(
    "no fire, no forecast",
    all(v == 0.0 for v in _fc_det.forecast_free_heat(96, 0.25)),
)

# The tank pair can shorten the decay tail, never extend it: a fire whose
# tank measurably holds nothing is spent, whatever the timer says. This
# replaces the fixed decay's job with a measurement, in the only direction
# measurement is allowed to argue -- towards less trust.
def _burn_then_release(det, spent_pair):
    """Confirm a fire, release it, and hand the detector one post-release
    observation -- with or without a wood pair that reads spent."""
    det.update(_fire_obs(0, buffer_temp=40.0))
    det.update(_fire_obs(15, buffer_temp=41.0))
    det.update(_fire_obs(30, buffer_temp=42.0))          # active
    det.update(_fire_obs(45, buffer_temp=42.0))          # release 1
    kw = (
        dict(wood_top=41.0, wood_bottom=40.0, hp_tank_temp=40.5)
        if spent_pair
        else {}
    )
    det.update(_fire_obs(60, buffer_temp=41.8, **kw))    # release 2: fading
    det.update(_fire_obs(75, buffer_temp=41.6, **kw))


_spent = ExternalHeatDetector(ExternalHeatConfig(
    enabled=True, confirm_samples=2, release_samples=2,
    decay_minutes=90.0, wood_tank_volume_l=500.0,
))
_burn_then_release(_spent, spent_pair=True)
R.check(
    "a measurably spent wood tank ends the decay early",
    not _spent.suppressing,
    "the 90-minute timer would still be fading; the empty tank overrules it",
)
_timed = ExternalHeatDetector(ExternalHeatConfig(
    enabled=True, confirm_samples=2, release_samples=2, decay_minutes=90.0,
))
_burn_then_release(_timed, spent_pair=False)
R.check(
    "while without the tank pair the timer stands",
    _timed.suppressing,
    "the measured cut-off must be the difference, not a detector change",
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

# --- The shape's level must be calibrated to the known window --------------
#
# The learned shape has mean 1.0 over a whole day, but the known window
# rarely covers one. Scaling by the raw mean of a window that sits on the
# expensive half of the day overprices the entire guessed tail by the same
# ratio.
_lvl_model = PriceShapeModel()
_lvl_model.shapes[0] = [1.5] * 12 + [0.5] * 12  # expensive night, cheap day
_lvl_model.days = [10, 10]
_lvl_steps = [datetime(2026, 1, 7, h, 0) for h in range(24)]  # a Wednesday
_lvl_prices, _lvl_mask = extend_price_series(
    [3.0] * 4, 24, _lvl_steps, _lvl_model
)
R.check(
    "the guessed tail is scaled by the true daily level",
    abs(_lvl_prices[12] - 1.0) < 1e-6,
    f"known 3.0 sits on shape 1.5 → level 2.0; hour 12 at shape 0.5 must be "
    f"1.0, not {3.0 * 0.5}, got {_lvl_prices[12]}",
)
R.check(
    "and reproduces the known window at its own hours",
    abs(2.0 * 1.5 - 3.0) < 1e-9 and bool(_lvl_mask[3]) and not bool(_lvl_mask[4]),
)

# --- Prices align by their own timestamps, not by list position ------------
#
# Position assumed the first entry is *today's* midnight. A stale list — the
# fetch failing since yesterday — then shifts the whole horizon a day, and
# quarter-hour entries (Tibber's 15-minute pricing) are each stretched to a
# full hour.
_pa = type(
    "_PriceAlign",
    (),
    {
        "_known_prices_for": Coord._known_prices_for,
        "_comparable_ts": staticmethod(Coord._comparable_ts),
    },
)()
_pa_mid = datetime(2026, 1, 6, 0, 0)
_pa_steps = [_pa_mid + timedelta(minutes=15 * i) for i in range(8)]

_pa._prices = [
    {
        "total": 1.0 + h,
        "starts_at": (_pa_mid - timedelta(hours=24) + timedelta(hours=h)).isoformat(),
    }
    for h in range(24)
]
R.check(
    "a stale price list is not read as today's prices",
    _pa._known_prices_for(_pa_steps) == [],
    "yesterday's midnight in position 0 must not become today's midnight",
)
_pa._prices = [
    {"total": float(h), "starts_at": (_pa_mid + timedelta(hours=h)).isoformat()}
    for h in range(2)
]
R.check(
    "hourly entries cover their own four quarters",
    _pa._known_prices_for(_pa_steps) == [0.0] * 4 + [1.0] * 4,
)
_pa._prices = [
    {
        "total": float(i),
        "starts_at": (_pa_mid + timedelta(minutes=15 * i)).isoformat(),
    }
    for i in range(4)
]
R.check(
    "quarter-hour entries are not stretched to hours",
    _pa._known_prices_for(_pa_steps) == [0.0, 1.0, 2.0, 3.0],
    "15-minute Tibber pricing maps one entry to one step",
)

# --- Weather aligns by entry timestamps too --------------------------------
_wa = type(
    "_WeatherAlign",
    (),
    {
        "_weather_series": Coord._weather_series,
        "_comparable_ts": staticmethod(Coord._comparable_ts),
        "_wind_speed_scale": lambda self: 1.0,
    },
)()
_wa._solar_radiation_forecast = []
_wa._solar_radiation = 0.0
# Forecast fetched two hours ago: entry 0 describes 22:00 *yesterday*.
_wa._weather_forecast = [
    {
        "datetime": (_pa_mid - timedelta(hours=2) + timedelta(hours=h)).isoformat(),
        "temperature": -10.0 + h,
        "wind_speed": 0.0,
        "precipitation": 0.0,
    }
    for h in range(6)
]
_wa_outdoor, _, _, _ = _wa._weather_series(4, _pa_mid, 0)
R.check(
    "a stale weather forecast still lines up with the clock",
    _wa_outdoor[0] == -8.0,
    f"midnight must read the entry *for* midnight (-8), not the first entry "
    f"(-10); got {_wa_outdoor[0]}",
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
    "early in the month the threshold is what has actually been seen",
    new_month.threshold_kw(tariff) == 3.0,
    "not zero: charging for every kW makes the term dwarf the energy bill",
)
tracker.observe(datetime(2026, 4, 1, 0, 0), 1.0, tariff)
R.check("a new month resets the peaks", tracker.month == "2026-04")

R.check(
    "staying under the threshold costs nothing",
    peak_penalty(np.full(8, 2.0), np.full(8, 1.0), 5.0, tariff, 0.25) == 0.0,
)

# The bill is full_price x mean(top-k peaks), which rearranges exactly to
# marginal_price x sum(top-k excesses). Charging only the single largest, as
# this originally did, under-states a plan with several high hours -- the very
# plan a capacity tariff exists to discourage.
hourly = np.array([8.0, 7.9, 7.8, 5.5, 5.1] + [3.0] * 19)
charged = peak_cost(hourly, np.zeros(24), 6.0, 20.0, 60, 1.0, 3)
top3 = np.sort(np.maximum(0.0, hourly - 6.0))[-3:]
R.check(
    "the peak charge equals the bill it models",
    abs(charged - 60.0 * float(np.mean(top3))) < 1e-6,
    f"charged {charged:.2f}, bill {60.0 * float(np.mean(top3)):.2f}",
)
R.check(
    "several high hours cost more than one",
    peak_cost(np.array([8.0] * 3 + [3.0] * 21), np.zeros(24), 6.0, 20.0, 60, 1.0, 3)
    > peak_cost(np.array([8.0] + [3.0] * 23), np.zeros(24), 6.0, 20.0, 60, 1.0, 3),
)

# The solver reaches this through numerical gradients, so a term that is flat
# almost everywhere is invisible to it. Measured: with a plain ``max`` the
# tariff had gradient at 1 step in 96 and enabling it *raised* the peak.
flat = np.full(96, 3.0)
base_cost = peak_cost(flat, np.full(96, 1.5), 3.0, 20.0, 60, 0.25, 3)
gradients = []
for index in (5, 50, 90, 95):
    probe = flat.copy()
    probe[index] += 1e-4
    gradients.append(
        (peak_cost(probe, np.full(96, 1.5), 3.0, 20.0, 60, 0.25, 3) - base_cost) / 1e-4
    )
R.check(
    "the peak charge has a gradient the solver can follow",
    sum(1 for g in gradients if abs(g) > 1e-6) >= 3,
    f"only {sum(1 for g in gradients if abs(g) > 1e-6)} of 4 probes moved it",
)

# With no history there is no reference, and treating every kW as a brand-new
# peak makes the term dwarf the whole energy bill.
fresh = PeakTracker()
R.check(
    "a month with no recorded peaks disables the charge",
    not np.isfinite(fresh.threshold_kw(tariff))
    and peak_cost(
        np.full(96, 6.0), np.zeros(96),
        fresh.threshold_kw(tariff), 20.0, 60, 0.25, 3,
    )
    == 0.0,
    "otherwise a normal day is charged ~9x its own energy cost",
)
partial = PeakTracker()
partial.peaks = [5.5]
partial.month = "2026-03"
R.check(
    "a partial month measures against what has actually been seen",
    partial.threshold_kw(tariff) == 5.5,
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
# Not one charge per hour -- that would price a whole month's tariff into
# every busy hour of one day -- but not only the single largest either, since
# the bill averages the month's top few.
R.check(
    "the charge covers exactly the peaks the bill averages",
    abs(
        peak_penalty(np.full(8, 7.0), np.zeros(8), 5.0, tariff, 1.0)
        - tariff.peaks_averaged * 2.0 * tariff.marginal_price_per_kw
    )
    < 1e-6,
    "three hours 2 kW over, averaged, at the full 60/kW = 120",
)

# --- The metering windows sit on the DSO's clock, not the plan's -----------
#
# A solve at 12:30 used to fold hourly windows [12:30, 13:30), so a one-hour
# burst that the meter bills inside a single window was split across two and
# its priced excess halved. `offset_steps` says how many steps remain to the
# real boundary.
_dso_burst = np.array([0.0, 0.0, 8.0, 8.0, 8.0, 8.0, 0.0, 0.0])
R.check(
    "a burst inside one billed window is priced as one window",
    realised_peak(_dso_burst, np.zeros(8), 60, 0.25, offset_steps=2) == 8.0
    and realised_peak(_dso_burst, np.zeros(8), 60, 0.25) == 4.0,
    "on the shifted fold the same burst averages into two half-windows of 4",
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

# The cost of a draw is piecewise: surplus-covered energy at the export
# price, the rest at the import price. The whole-step substitution this
# replaced made 0.05 kW of sun reprice a full compressor draw.
_pw_prices = np.array([1.5, 1.5, 1.5])
_pw_surplus = np.array([0.0, 2.0, 5.0])
R.check(
    "a draw inside the surplus costs the export compensation",
    abs(pv.piecewise_cost(_pw_prices, _pw_surplus, 0.3, np.array([0.0, 2.0, 4.0]), 1.0)
        - (2.0 * 0.3 + 4.0 * 0.3)) < 1e-9,
)
R.check(
    "a draw beyond the surplus pays the import price for the excess",
    abs(pv.piecewise_cost(_pw_prices, _pw_surplus, 0.3, np.array([3.0, 6.0, 5.0]), 1.0)
        - (3.0 * 1.5 + (2.0 * 0.3 + 4.0 * 1.5) + 5.0 * 0.3)) < 1e-9,
    "epsilon surplus must not reprice a full compressor draw",
)
R.check(
    "an export price above the import price is clamped",
    abs(pv.piecewise_cost(np.array([0.2]), np.array([5.0]), 0.9, np.array([2.0]), 1.0)
        - 2.0 * 0.2) < 1e-9,
    "otherwise the objective would pay the house to consume",
)
_blend = pv.blended_block_prices(_pw_prices, _pw_surplus, 0.3, 4.0)
R.check(
    "a hot-water block's price blends by the covered fraction",
    abs(_blend[0] - 1.5) < 1e-9
    and abs(_blend[1] - (1.5 - 1.2 * 0.5)) < 1e-9
    and abs(_blend[2] - 0.3) < 1e-9,
    f"{[round(v, 3) for v in _blend]}",
)

# The optimizer's objective must charge that same piecewise cost. This is the
# regression the old formulation failed: 0.05 kW of surplus made a full 6 kW
# draw look like it cost the export price.
from heatpump_optimizer.optimizer import HeatPumpOptimizer as _PvOpt
from heatpump_optimizer.optimizer import OptimizationConfig as _PvOptCfg
from heatpump_optimizer.thermal_model import ThermalModel as _PvModel
from heatpump_optimizer.thermal_model import ThermalParameters as _PvParams

_pv_opt = _PvOpt(_PvModel(_PvParams()), _PvOptCfg(pv_export_price=0.3))
_pv_opt._pv_surplus = np.array([0.05, 4.0, 0.0])
_pv_cost = _pv_opt._energy_cost_fn(np.array([1.5, 1.5, 1.5]), 1.0)
_pv_draw = np.array([6.0, 4.0, 6.0])
_pv_expected = (0.05 * 0.3 + 5.95 * 1.5) + 4.0 * 0.3 + 6.0 * 1.5
R.check(
    "the objective reprices the covered sliver, not the whole step",
    abs(_pv_cost(_pv_draw) - _pv_expected) < 1e-9,
    f"cost {_pv_cost(_pv_draw):.4f}, exact {_pv_expected:.4f}",
)
_pv_opt._pv_surplus = None
R.check(
    "without surplus the cost is the plain import bill",
    abs(_pv_opt._energy_cost_fn(_pw_prices, 1.0)(_pv_draw) - 16.0 * 1.5) < 1e-9,
)
_pv_opt._pv_surplus = np.array([0.0, 4.0, 0.0])
_ranked = _pv_opt._dhw_planning_prices(np.array([1.5, 1.5, 1.5]), 4.0)
R.check(
    "hot-water planning ranks a fully covered step at the export price",
    abs(_ranked[1] - 0.3) < 1e-9 and abs(_ranked[0] - 1.5) < 1e-9,
)
_ranked_shared = _pv_opt._dhw_planning_prices(
    np.array([1.5, 1.5, 1.5]), 4.0, space_demand=np.array([0.0, 2.0, 0.0])
)
R.check(
    "on the replan, space heating takes its surplus share first",
    abs(_ranked_shared[1] - (1.5 - 1.2 * 0.5)) < 1e-9,
    f"{_ranked_shared[1]:.3f} should blend only the remaining 2 kW",
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
R.check(
    "a presence-class binary sensor being on means home",
    away_mode.interpret_presence(
        "on", "binary_sensor.someone", {"device_class": "presence"}
    )
    is False,
    "presence semantics are the inverse of a toggle; reading on as away "
    "deep-setbacks an occupied house",
)
R.check(
    "a presence-class binary sensor being off means away",
    away_mode.interpret_presence(
        "off", "binary_sensor.someone", {"device_class": "occupancy"}
    )
    is True,
)
R.check(
    "a class-less binary sensor keeps toggle semantics",
    away_mode.interpret_presence("on", "binary_sensor.holiday", {}) is True,
)
R.check(
    "a template sensor speaking the person vocabulary reads correctly",
    away_mode.interpret_presence("away", "sensor.presence_text") is True,
    "these used to invert: 'away' fell into the toggle-off list",
)

AWAY_CFG = away_mode.AwayConfig(
    enabled=True,
    presence_entity="input_boolean.holiday",
    return_entity="input_datetime.back",
    away_temperature=16.0,
)

# A real model, so the recovery estimate sees the slab bottleneck the old
# lumped formula ignored.
_away_model = ThermalModel(ThermalParameters())


def _away_house(current=16.0):
    return ThermalState(room_temperature=current, slab_temperature=current + 1.0)


def resolve_away(now, return_at, current=16.0):
    return away_mode.resolve(
        AWAY_CFG,
        now=now,
        presence_raw="on",
        presence_attributes=None,
        return_raw=return_at,
        comfort_temp=21.0,
        model=_away_model,
        thermal_state=_away_house(current),
        outdoor_temp=0.0,
    )


now = datetime(2026, 2, 10, 12, 0)
far = resolve_away(now, (now + timedelta(days=3)).isoformat())
R.check("away is detected", far.active)
R.check("the deep setback applies while away", far.target_temperature == 16.0)
R.check("recovery is not started three days out", not far.recovery_active)
R.check("the recovery estimate is published", far.recovery_hours is not None)

near = resolve_away(now, (now + timedelta(hours=6)).isoformat())
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
    comfort_temp=21.0,
    model=_away_model,
    thermal_state=_away_house(21.0),
    outdoor_temp=0.0,
)
R.check("an occupied house is never set back", not home.active)
disabled_away = away_mode.resolve(
    away_mode.AwayConfig(enabled=False),
    now=now,
    presence_raw="on",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    model=_away_model,
    thermal_state=_away_house(),
    outdoor_temp=0.0,
)
R.check("disabled means the feature cannot cost anything", not disabled_away.active)

R.check(
    "a warm house needs no recovery time",
    away_mode.estimate_recovery_hours(_away_model, _away_house(21.0), 21.0, 0.0)
    == 0.0,
)
_weak_model = ThermalModel(ThermalParameters(max_electrical_power=0.2))
R.check(
    "a pump that cannot reach the target starts as early as allowed",
    away_mode.estimate_recovery_hours(_weak_model, _away_house(10.0), 21.0, -20.0)
    == away_mode.MAX_RECOVERY_HOURS,
    "refusing to plan recovery would be worse than starting early",
)
# The estimate has to see the slab bottleneck: all the pump's heat enters the
# slab and reaches the room only through slab_heat_transfer, so a cold house
# needs several hours even at full power. The lumped formula this replaced
# said 4.4 h here; the real ramp needs roughly twice that.
_cold_ramp = away_mode.estimate_recovery_hours(
    _away_model, _away_house(16.0), 21.0, 0.0
)
R.check(
    "a cold house's recovery estimate respects the slab bottleneck",
    _cold_ramp >= 6.0,
    f"got {_cold_ramp:.2f} h; the lumped estimate this replaced said 4.4 h "
    "and left the house ~3 °C cold at the stated return",
)

cal = away_mode.resolve(
    away_mode.AwayConfig(enabled=True, presence_entity="calendar.holidays"),
    now=now,
    presence_raw="on",
    presence_attributes={"end_time": (now + timedelta(hours=1)).isoformat()},
    return_raw=None,
    comfort_temp=21.0,
    model=_away_model,
    thermal_state=_away_house(),
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
# The heavy mass must live in exactly one store. The heated slab *is* the
# building's heavy floor, and the model already couples it to the lower zone;
# counting it in the lower zone as well doubled the downstairs store and let
# plans coast on heat the building does not have.
R.check(
    "the heavy mass lives in the heated slab, and only there",
    two_zone["slab_thermal_mass"] > two_zone["lower_floor_thermal_mass"]
    and abs(
        two_zone["lower_floor_thermal_mass"]
        - two_zone["upper_floor_thermal_mass"]
    ) < 0.5,
    f"slab {two_zone['slab_thermal_mass']}, lower "
    f"{two_zone['lower_floor_thermal_mass']}, upper "
    f"{two_zone['upper_floor_thermal_mass']}",
)
R.check(
    "the radiator power fraction follows the emitters",
    abs(two_zone["radiator_power_fraction"] - 0.5) < 1e-6,
)

# A radiator house pushes every watt through the same "slab" slot of the
# model, so that store has to be the radiator loop: small, and coupled well
# enough to deliver the design heat load at a sane flow temperature. Giving
# it the building's slow mass behind the minimum 0.05 kW/°C transfer modelled
# a house where 3 kW needs the emitter 60 °C above the room.
_rad_house = presets.derive(
    presets.BuildingPreset(lower_emitter=presets.EMITTER_RADIATORS)
)
_floor_house = presets.derive(
    presets.BuildingPreset(lower_emitter=presets.EMITTER_FLOOR)
)
R.check(
    "a radiator loop is a small store, not the building's slab",
    _rad_house["slab_thermal_mass"] < 1.0
    < _floor_house["slab_thermal_mass"],
    f"radiators {_rad_house['slab_thermal_mass']} kWh/°C vs floor "
    f"{_floor_house['slab_thermal_mass']} kWh/°C",
)
R.check(
    "radiators can deliver the design heat load at a sane flow temperature",
    _rad_house["slab_heat_transfer"]
    >= _rad_house["house_heat_loss_coefficient"],
    "at transfer >= loss, holding the house at ΔT 30 K outside needs the "
    "emitter no more than 30 K above the room",
)
R.check(
    "with radiators the heavy floor coasts as part of the room store",
    _rad_house["house_thermal_mass"] > _floor_house["house_thermal_mass"] * 2,
    f"{_rad_house['house_thermal_mass']} vs {_floor_house['house_thermal_mass']} "
    "kWh/°C: the slow mass is passively coupled, not deleted",
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

# --- One shortfall, one learner -------------------------------------------
#
# The COP scale and the defrost derate watch the same commanded-versus-
# measured signal, so attribution is split by the frosting band: inside it
# only the derate learns, outside it only the COP scale does. Without the
# split, one frost cycle was corrected twice — as a permanently collapsed
# COP *and* as a derate — and plans in the band overcompensated.
from heatpump_optimizer.defrost import in_frost_band

R.check(
    "the frosting band covers the frosting temperatures",
    in_frost_band(0.0) and in_frost_band(2.0) and in_frost_band(4.9),
)
R.check(
    "dry deep cold is not frost, and mild air is not frost",
    not in_frost_band(-2.0) and not in_frost_band(5.0) and not in_frost_band(8.0),
)


class _CopGate:
    _learn_measured_cop = Coord._learn_measured_cop
    _commanded_power = Coord._commanded_power
    _apply_cop_scale = Coord._apply_cop_scale

    def __init__(self, outdoor: float) -> None:
        self._measured_power = 2.0
        self._current_action = {"power": 3.0}
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(
            room_temperature=21.0, outdoor_temperature=outdoor
        )
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._last_measured_cop = None

    def _learning_frozen(self, *entities):
        return None


_in_band = _CopGate(outdoor=2.0)
_in_band._learn_measured_cop()
R.check(
    "the COP scale does not learn inside the frosting band",
    _in_band._cop_samples == 0 and _in_band._cop_scale == 1.0,
    "that shortfall is the defrost derate's to explain",
)
_out_band = _CopGate(outdoor=8.0)
_out_band._learn_measured_cop()
R.check(
    "outside the band the same sample still teaches the COP scale",
    _out_band._cop_samples == 1 and _out_band._cop_scale > 1.0,
)

# --- Standby loss is not hot water usage ----------------------------------
#
# The tank cools all the time — about 0.42 °C/h for a 55 °C tank at the
# default rate — and a drop of that size passed the raw 0.15 °C gate every
# idle hour, teaching a phantom draw into all 24 slots and washing the real
# morning/evening pattern towards flat. Only the drop *beyond* expected
# standby decay is usage.
import asyncio as _aio


class _DhwUsage:
    _async_learn_dhw_usage = Coord._async_learn_dhw_usage
    _normalize_dhw_profile = Coord._normalize_dhw_profile

    def __init__(self) -> None:
        self._dhw_cooling_rate = 0.3
        self._dhw_hourly_profile = [1.0] * 24
        self._thermal_params = ThermalParameters()

    async def _async_save_dhw_profile(self) -> None:
        pass


_standby_only = _DhwUsage()
_aio.run(
    _standby_only._async_learn_dhw_usage(
        55.0, 0.42, 1.0, 3, False  # exactly the expected standby drop at 55 °C
    )
)
R.check(
    "a pure standby drop teaches no draw",
    _standby_only._dhw_hourly_profile == [1.0] * 24,
    "0.42 °C/h at 55 °C is the tank cooling, not a shower at 3 am",
)
_real_draw = _DhwUsage()
_aio.run(_real_draw._async_learn_dhw_usage(55.0, 2.0, 1.0, 7, False))
R.check(
    "a genuine draw still reinforces its hour",
    _real_draw._dhw_hourly_profile[7] > 1.0
    and _real_draw._dhw_hourly_profile[7] > _real_draw._dhw_hourly_profile[3],
)

# --- A stale plan is not a prediction -------------------------------------
#
# In comfort, boost and off modes the optimizer does not run, but
# `_optimization_result` still holds the *last* auto-mode plan. Its
# trajectory assumed powers the fixed-rule action is not applying, so pairing
# it against the measured room temperature charges the model with errors it
# never made.
from heatpump_optimizer.const import MODE_AUTO as _MODE_AUTO
from heatpump_optimizer.const import MODE_BOOST as _MODE_BOOST


class _PredGate:
    _predicted_next_room_temp = Coord._predicted_next_room_temp

    def __init__(self, mode: str) -> None:
        self._mode = mode
        self._config = {}
        self._thermal_params = ThermalParameters()

        class _Res:
            room_temp_trajectory = [21.0, 21.4, 21.8]
            upper_temp_trajectory = []

        class _OptCfg:
            time_step_minutes = 30.0

        self._optimization_result = _Res()
        self._opt_config = _OptCfg()


R.check(
    "a stale plan trajectory is not offered as a prediction in boost mode",
    _PredGate(_MODE_BOOST)._predicted_next_room_temp() is None,
)
R.check(
    "in auto mode the plan is what runs, so it is the prediction",
    _PredGate(_MODE_AUTO)._predicted_next_room_temp() == 21.4,
)

# --- The learned COP survives a restart -----------------------------------
#
# Every plan is priced through the COP curve; a learned correction that
# evaporated on restart silently re-based all costs on the nameplate figure.
class _FakeLearnStore:
    def __init__(self) -> None:
        self.saved = None

    async def async_save(self, data) -> None:
        self.saved = data

    async def async_load(self):
        return self.saved


class _LearnPersist:
    _async_save_thermal_learning = Coord._async_save_thermal_learning
    _async_load_thermal_learning = Coord._async_load_thermal_learning
    _apply_cop_scale = Coord._apply_cop_scale

    def __init__(self, store) -> None:
        self._thermal_learning_store = store
        self._thermal_params = ThermalParameters()
        self._buffer_cooling_rate = 6.0
        self._buffer_cooling_samples = 3
        self._house_heat_loss_scale = 1.1
        self._house_heat_loss_samples = 12
        self._lower_floor_loss_ratio = 1.05
        self._lower_floor_loss_samples = 4
        self._cop_scale = 0.85
        self._cop_samples = 20

    def _apply_buffer_cooling_rate(self, rate: float) -> None:
        self._buffer_cooling_rate = float(rate)

    def _apply_house_heat_loss_scale(self, scale: float) -> None:
        self._house_heat_loss_scale = float(scale)

    def _apply_lower_floor_loss_ratio(self, ratio: float) -> None:
        self._lower_floor_loss_ratio = float(ratio)


_learn_store = _FakeLearnStore()
_aio.run(_LearnPersist(_learn_store)._async_save_thermal_learning())
_restarted = _LearnPersist(_learn_store)
_restarted._cop_scale = 1.0
_restarted._cop_samples = 0
_aio.run(_restarted._async_load_thermal_learning())
R.check(
    "the learned COP scale is saved and restored",
    abs(_restarted._cop_scale - 0.85) < 1e-9 and _restarted._cop_samples == 20,
    f"restored scale {_restarted._cop_scale}, {_restarted._cop_samples} samples",
)

# --- The savings baseline follows the comfort schedule ---------------------
#
# The reference thermostat used to hold the flat day target around the clock,
# so a configured night setback was booked as optimizer savings — value any
# programmable thermostat delivers without an optimizer.
_bl_state = ThermalState(
    room_temperature=21.0, slab_temperature=26.0, outdoor_temperature=-5.0
)
_bl_opt = _PvOpt(_PvModel(_PvParams()), _PvOptCfg(target_temp=21.0))
_bl_n = 16
_bl_out = np.full(_bl_n, -5.0)
_bl_zero = np.zeros(_bl_n)
_bl_flat, _ = _bl_opt._compute_baseline_power(
    _bl_state, _bl_out, _bl_zero, _bl_zero, _bl_zero, 0.25
)
_bl_setback, _ = _bl_opt._compute_baseline_power(
    _bl_state,
    _bl_out,
    _bl_zero,
    _bl_zero,
    _bl_zero,
    0.25,
    np.array([21.0] * 8 + [17.0] * 8),
)
R.check(
    "a night setback lowers the reference, not the reported savings",
    float(np.sum(_bl_setback[8:])) < float(np.sum(_bl_flat[8:])) - 0.5,
    f"setback half {np.sum(_bl_setback[8:]):.2f} kW-steps vs flat "
    f"{np.sum(_bl_flat[8:]):.2f}",
)
R.check(
    "while the schedule agrees, so do the baselines",
    np.allclose(_bl_setback[:8], _bl_flat[:8]),
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
# Private fields are not part of the configuration surface by construction --
# they are caches and internal bookkeeping, not parameters. Excluded by the
# leading underscore rather than by name, so the next one needs no new
# exemption, and so a *public* field can never be hidden this way.
declared = {
    f.name
    for f in dataclasses.fields(ThermalParameters)
    if not f.name.startswith("_")
}
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
    "cop_flow_carnot",          # follows the mixing valve mode
    "cop_flow_reference_temp",  # a property of the COP curve, not the house
    "emitter_design_delta_t",   # a sizing convention, not a per-house setting
}

# Fields that *are* configurable but cannot be probed by substituting a
# sentinel, because the mapping validates them. They get an explicit check
# below instead of being quietly exempted.
validated_enums = {"mixing_valve_mode"}

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


probe = {name: reachable(name) for name in declared - runtime_only - validated_enums}

unreachable = sorted(n for n, k in probe.items() if k is None)
R.check(
    "every configurable parameter is reachable from a config key",
    not unreachable,
    ", ".join(unreachable),
)

# The enum the probe cannot express. It is validated on the way in, so an
# unknown string must fall back rather than reaching the model -- otherwise the
# user sees no valve behaviour and nothing explains why.
_valve_set = ThermalParameters.from_config(
    {hp_const.CONF_MIXING_VALVE_MODE: "manual"}
)
_valve_bad = ThermalParameters.from_config(
    {hp_const.CONF_MIXING_VALVE_MODE: "nonsense"}
)
R.check(
    "the mixing valve mode is reachable from its config key",
    _valve_set.mixing_valve_mode == "manual",
    f"got {_valve_set.mixing_valve_mode!r}",
)
R.check(
    "and an unknown mode falls back rather than silently doing nothing",
    _valve_bad.mixing_valve_mode == "none",
    f"got {_valve_bad.mixing_valve_mode!r}",
)
R.check(
    "the COP flow penalty follows the mode rather than being separate",
    _valve_set.cop_flow_carnot and not _valve_bad.cop_flow_carnot,
    "it only means anything when a valve can actually charge the tank",
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
R.section("Lower floor temperature sensor (item 30)")

# Nothing in the suite drove `_update_current_state` before this. The optimizer
# scenarios seed `ThermalState` directly and the coordinator golden captures call
# only `_build_data_dict`, so the whole sensor-to-state path was untested -- and
# an empty golden diff for this change is therefore expected, not evidence that
# the sensor is wired up. These checks are that evidence.

import asyncio as _asyncio

from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _Coord,
)


def _zone_coord(states, **extra):
    """A two-zone coordinator reading the given entity states."""
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        # Inferred from the presence of zone settings, not from a flag.
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
        **extra,
    }
    coord = _Coord(_FakeHass(states), _FakeEntry(data=cfg))
    return coord


def _lower_after_update(states, **extra):
    coord = _zone_coord(states, **extra)
    _asyncio.run(coord._update_current_state())
    return coord._current_state


_BASE = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
}

# 1. The bug this item exists to fix. A floor return of 28 °C means a *water*
#    temperature, and the room it serves is nowhere near that warm.
st = _lower_after_update(
    {**_BASE, "sensor.ret": FakeState("28.0", unit="°C")},
    floor_return_temp_entity="sensor.ret",
)
R.check(
    "without a lower-floor sensor the zone is still inferred from return water",
    abs(st.lower_floor_temperature - 28.5) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 2. A real sensor must win. This is the whole feature.
st = _lower_after_update(
    {
        **_BASE,
        "sensor.ret": FakeState("28.0", unit="°C"),
        "sensor.lower": FakeState("20.4", unit="°C"),
    },
    floor_return_temp_entity="sensor.ret",
    lower_floor_temp_entity="sensor.lower",
)
R.check(
    "a real lower-floor sensor takes precedence over the return-temp estimate",
    abs(st.lower_floor_temperature - 20.4) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 3. And it must break the constant that made the main heat path useless.
#
#    `update_slab_from_return_temp` merges 0.7 sensor / 0.3 prior, so the slab
#    only reaches its `return + 1.0` fixed point after several cycles. Converge
#    it first: a single-cycle assertion here passes for the wrong reason -- the
#    merge has not settled yet -- and would go on passing with the fix reverted.
def _converged_delta(states, **extra):
    coord = _zone_coord(states, **extra)
    for _ in range(20):
        _asyncio.run(coord._update_current_state())
    cs = coord._current_state
    return cs.slab_temperature - cs.lower_floor_temperature


_ret_only = {**_BASE, "sensor.ret": FakeState("28.0", unit="°C")}
_delta_inferred = _converged_delta(_ret_only, floor_return_temp_entity="sensor.ret")
_delta_measured = _converged_delta(
    {**_ret_only, "sensor.lower": FakeState("20.4", unit="°C")},
    floor_return_temp_entity="sensor.ret",
    lower_floor_temp_entity="sensor.lower",
)
R.check(
    "the inferred path really does pin slab-to-room at 0.5 K",
    abs(_delta_inferred - 0.5) < 0.01,
    f"delta {_delta_inferred:.3f}",
)
R.check(
    "and a real sensor unpins it, so the main heat path can vary at all",
    _delta_measured > 5.0,
    f"delta {_delta_measured:.3f} (was {_delta_inferred:.3f})",
)

# 4. With no floor return at all, the room temperature is the better estimate --
#    and a real sensor still beats it.
st = _lower_after_update({**_BASE, "sensor.lower": FakeState("19.2", unit="°C")},
                         lower_floor_temp_entity="sensor.lower")
R.check(
    "the sensor is used even when there is no floor return sensor",
    abs(st.lower_floor_temperature - 19.2) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

st = _lower_after_update(dict(_BASE))
R.check(
    "with neither sensor the lower zone falls back to room temperature",
    abs(st.lower_floor_temperature - 21.0) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 5. The guard asymmetry. The two branches used to be gated on different things
#    -- one on the reading being good, the other on the entity being unset -- so
#    a configured-but-dead sensor satisfied neither and both values silently
#    held. A stale reading must still land somewhere defensible.
st = _lower_after_update(
    {
        **_BASE,
        "sensor.ret": FakeState("28.0", unit="°C", last_updated=minutes_ago(600)),
    },
    floor_return_temp_entity="sensor.ret",
)
R.check(
    "a configured but stale floor return still leaves a defensible lower zone",
    abs(st.lower_floor_temperature - 21.0) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 6. An unavailable lower-floor sensor must fall back rather than poison state.
st = _lower_after_update(
    {
        **_BASE,
        "sensor.ret": FakeState("28.0", unit="°C"),
        "sensor.lower": FakeState("unavailable"),
    },
    floor_return_temp_entity="sensor.ret",
    lower_floor_temp_entity="sensor.lower",
)
R.check(
    "an unavailable lower-floor sensor falls back to the return-temp estimate",
    abs(st.lower_floor_temperature - 28.5) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 7. The watchdog has to cover it. A key absent from INPUT_MAX_AGE_MINUTES gets
#    no age limit at all, which disables staleness detection silently.
R.check(
    "the new sensor has a staleness limit like the other room sensors",
    hp_const.INPUT_MAX_AGE_MINUTES.get("lower_floor_temp_entity")
    == hp_const.INPUT_MAX_AGE_MINUTES.get("indoor_temp_entity"),
)


R.section("The optimizer can see the buffer tank (item 29)")

# Two defects meant a charged tank was worth exactly nothing to the optimizer,
# so charging could only ever look like cost. Neither was the seeding problem
# the backlog predicted -- a storage-aware seed and even a full-power seed
# descend to the same plan as the existing ones.

from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _Opt,
    OptimizationConfig as _OptCfg,
)


def _optimizer_for(mode):
    p = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=mode, buffer_max_temp=70.0,
    )
    cfg = _OptCfg(horizon_hours=24, time_step_minutes=15,
                  target_temp=21.0, min_temp=19.0, max_temp=23.0)
    return ThermalModel(p), cfg, _Opt(ThermalModel(p), cfg)


_outdoor = np.full(96, -5.0)
_m_valve, _cfg, _opt_valve = _optimizer_for("manual")
_m_none, _, _opt_none = _optimizer_for("none")

# 1. The tank borrowed the *slab's* settlement ceiling, which sits near the
#    temperature that sustains the comfort target -- around 28 C. Every degree
#    of tank above that counted for nothing, so charging 45 -> 70 C was credited
#    with 0.0 kWh of the 21.8 kWh actually stored.
_caps_valve = _opt_valve._settlement_caps(_outdoor)
_caps_none = _opt_none._settlement_caps(_outdoor)
R.check(
    "the tank has its own settlement ceiling, not the slab's",
    _caps_valve["buffer"] > _caps_valve["slab"] + 20.0,
    f"buffer {_caps_valve['buffer']:.1f} C vs slab {_caps_valve['slab']:.1f} C",
)
R.check(
    "which is the tank's own maximum",
    _caps_valve["buffer"] == 70.0,
    f"got {_caps_valve['buffer']}",
)
R.check(
    "and without a valve nothing changes, since the tank cannot be charged",
    _caps_none["buffer"] == _caps_none["slab"],
    "this path must stay byte-for-byte identical",
)

# 2. Stored energy has to respond to the tank at all.
_st = lambda t: ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=t, outdoor_temperature=-5.0,
)
_cold = _opt_valve._stored_thermal_energy(_st(45.0), caps=_caps_valve)
_hot = _opt_valve._stored_thermal_energy(_st(70.0), caps=_caps_valve)
R.check(
    "a charged tank counts as stored energy",
    _hot - _cold > 15.0,
    f"45 -> 70 C is worth {_hot - _cold:.1f} kWh",
)

# 3. And the *objective* has to see it, which is the half that was missing:
#    `_terminal_cost` listed upper, lower and slab, and `simulate_trajectory`
#    computed the buffer trajectory and then discarded it.
_prices = np.full(96, 1.0)
_term = _opt_valve._terminal_cost(_prices, _outdoor)
_flat = lambda v: np.full(97, v)
_cost_cold = _term(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(45.0))
_cost_hot = _term(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(70.0))
R.check(
    "the objective prices a tank left cold",
    _cost_cold > _cost_hot,
    f"cold {_cost_cold:.2f} vs charged {_cost_hot:.2f}",
)
R.check(
    "and omitting the tank entirely is treated as the worst case, not ignored",
    _term(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5)) >= _cost_cold,
    "a missing trajectory must not silently score as a full tank",
)

# 4. Inert without a valve.
_term_none = _opt_none._terminal_cost(_prices, _outdoor)
R.check(
    "without a valve the terminal cost ignores the tank",
    _term_none(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(45.0))
    == _term_none(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(70.0)),
    "the tank cannot be charged there, so it must not enter the objective",
)

# 4b. And inert below the store threshold, valve or not. The default 35 L
# tank holds ~0.8 kWh over a 20 K swing -- less than one optimizer step --
# and crediting it would have the solver planning around noise (item 27).
_p_tiny = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=35.0,
    mixing_valve_mode="manual", buffer_max_temp=70.0,
)
_opt_tiny = _Opt(ThermalModel(_p_tiny), _cfg)
R.check(
    "a 35 L tank behind a valve is not a store",
    not _p_tiny.buffer_is_store,
    "the default volume must land below the threshold decisively",
)
_caps_tiny = _opt_tiny._settlement_caps(_outdoor)
R.check(
    "so its settlement cap stays the slab's",
    _caps_tiny["buffer"] == _caps_tiny["slab"],
    f"got {_caps_tiny['buffer']:.1f} C",
)
_term_tiny = _opt_tiny._terminal_cost(_prices, _outdoor)
R.check(
    "and the terminal cost ignores it",
    _term_tiny(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(45.0))
    == _term_tiny(_flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(70.0)),
    "too small to matter must mean too small to plan around",
)
R.check(
    "while a real accumulator on the same valve is one",
    _opt_valve.model.params.buffer_is_store,
    "750 L must clear the threshold",
)

# 5. The trajectory the objective needs must actually be recorded.
_m_valve.simulate_trajectory(
    _st(45.0), np.full(96, 3.0), _outdoor, dt_hours=0.25
)
R.check(
    "the buffer trajectory is available after a simulation",
    _m_valve.last_buffer_trajectory is not None
    and len(_m_valve.last_buffer_trajectory) == 97,
    "the objective reads it from here rather than from a return value",
)


R.section("Mixing valve and the buffer tank as a store (items 27/29)")

from heatpump_optimizer import mixing_valve as _mv  # noqa: E402


def _tank_run(mode, power, *, target=23.0, hours=6.0, volume=750.0, start=45.0,
              dt=0.25):
    p = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=volume,
        mixing_valve_mode=mode, mixing_valve_target=target,
        cop_flow_carnot=True,
    )
    m = ThermalModel(p)
    st = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=start, outdoor_temperature=-5.0,
    )
    for _ in range(int(hours / dt)):
        st = m.simulate_step(st, power, -5.0, dt_hours=dt)
    return st


# The defect item 27 names: with no valve the draw is defined as a fixed share
# of the supply, so the two cancel and the pump cannot touch the tank at all.
_none = [_tank_run(_mv.MODE_NONE, pw).buffer_tank_temperature for pw in (0.0, 3.0, 9.0)]
R.check(
    "without a valve the tank ignores the heat pump entirely",
    max(_none) - min(_none) < 1e-6,
    f"0/3/9 kW all give {_none[0]:.3f} C -- the supply term cancels",
)

# And what the valve changes. Delivery becomes what the house asks for, so
# surplus has somewhere to go.
_charged = _tank_run(_mv.MODE_MANUAL, 9.0)
_coasted = _tank_run(_mv.MODE_MANUAL, 0.0)
R.check(
    "with a valve, running the pump hard charges the tank",
    _charged.buffer_tank_temperature > 60.0,
    f"got {_charged.buffer_tank_temperature:.1f} C from 45 C",
)
R.check(
    "and with the pump off the tank discharges into the house",
    _coasted.buffer_tank_temperature < 30.0,
    f"got {_coasted.buffer_tank_temperature:.1f} C",
)

# The point of the valve is that charging does *not* cost comfort: it throttles
# delivery, so the surplus goes to the tank rather than overheating the house.
_runaway = _tank_run(_mv.MODE_NONE, 9.0)
R.check(
    "charging hard does not overheat the house",
    _charged.upper_floor_temperature < 24.5,
    f"held at {_charged.upper_floor_temperature:.1f} C while charging",
)
R.check(
    "which is exactly what an unvalved system fails to do",
    _runaway.upper_floor_temperature > _charged.upper_floor_temperature + 3.0,
    f"unvalved reaches {_runaway.upper_floor_temperature:.1f} C on the same power",
)

# The tank's safe ceiling is a physical limit, not a preference.
R.check(
    "the tank cannot be charged past its ceiling",
    _charged.buffer_tank_temperature <= 70.0 + 1e-6,
    f"got {_charged.buffer_tank_temperature:.2f} C against a 70 C cap",
)

# The shipped default target of 0 means "the top of the comfort band", as the
# option describes everywhere. The previous fallback was house_temp + 1.0 — a
# target that recedes above wherever the house currently is — so the default
# valve never throttled: the house overheated and the tank could not charge.
_default_target = _tank_run(_mv.MODE_MANUAL, 9.0, target=0.0)
R.check(
    "an unconfigured valve target throttles at the comfort ceiling",
    _default_target.upper_floor_temperature < 24.5,
    f"house reached {_default_target.upper_floor_temperature:.1f} C on the "
    "default target; the receding fallback drove it past 29 C",
)
R.check(
    "and the tank still charges on the default target",
    _default_target.buffer_tank_temperature > 60.0,
    f"got {_default_target.buffer_tank_temperature:.1f} C from 45 C",
)

# A tank read above its cap must cool at its physical rate. The unconditional
# min() clamp teleported it down to the cap within one step, deleting the
# excess stored energy from the model entirely.
_over = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=75.0, outdoor_temperature=-5.0,
)
_over_m = ThermalModel(
    ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=21.0,
        buffer_max_temp=60.0, cop_flow_carnot=True,
    )
)
_after_over = _over_m.simulate_step(_over, 0.0, -5.0, dt_hours=0.25)
R.check(
    "a tank read above its cap cools physically, not by teleport",
    _after_over.buffer_tank_temperature > 65.0,
    f"75 C against a 60 C cap left {_after_over.buffer_tank_temperature:.2f} C "
    "after one 15-minute step; the old clamp forced exactly 60.0",
)

# Storing hot has to cost something, or the optimizer will store on every cheap
# hour whether or not it pays. Carnot-derived, because a linear %/K collapses to
# the floor at the temperatures storage actually reaches.
_m = ThermalModel(ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True))
_cold, _hot = _m.compute_cop(-5.0, flow_temp=35.0), _m.compute_cop(-5.0, flow_temp=70.0)
R.check(
    "charging the tank hot costs COP",
    _hot < _cold * 0.75,
    f"{_cold:.2f} at 35 C vs {_hot:.2f} at 70 C",
)
R.check(
    "but stays physically plausible rather than collapsing to a floor",
    _hot > 1.2,
    f"a real unit manages 1.5-2.0 at 70 C flow; got {_hot:.2f}",
)
_off = ThermalModel(ThermalParameters(two_zone_enabled=True))
R.check(
    "and the penalty is inert unless it is switched on",
    _off.compute_cop(-5.0, flow_temp=70.0) == _off.compute_cop(-5.0),
    "a flow temperature must not change COP when the term is disabled",
)

# A dumb valve needs a number to set. The recommendation is the top of the
# comfort band: the building stores at room temperature for no COP penalty, so
# it should fill first and the tank should take only the surplus.
_rec = _mv.recommend_target(comfort_min=19.0, comfort_max=23.0)
R.check(
    "a dumb valve is recommended the top of the comfort band",
    _rec.target == 23.0 and "surplus" in _rec.reason,
    f"got {_rec.target} -- {_rec.reason[:60]}",
)
R.check(
    "and the recommendation says what it costs, not just what to set",
    "comfort limits" in _rec.reason or "no longer limiting" in _rec.reason,
    "a high target gives up the valve's own overshoot protection",
)


R.section("The discharge law: the valve regulates flow temperature (item 29)")

# Why these exist: the old model discharged the tank with the valve wide open
# at the raw tank temperature, capped by a controller demand whose gap term
# divided by the step length. A 40-45 C tank dumped 22-26 kW, anything stored
# was gone within a step or two of the pump stopping, and every plan relaxed
# to the same empty tank -- so the terminal credit had no gradient and the
# optimizer correctly concluded storage buys nothing.

# The curve: the flow setpoint that holds the house at the target.
_fs = _mv.flow_setpoint(
    target_temp=23.0, outdoor_temp=-5.0,
    heat_loss_coefficient=0.19, emitter_ua=1.4,
)
R.check(
    "the flow setpoint is the target plus the standing loss over the emitter UA",
    abs(_fs - (23.0 + 0.19 * 28.0 / 1.4)) < 1e-9,
    f"got {_fs:.2f} C",
)
R.check(
    "and collapses to the target when there is nothing to hold against",
    _mv.flow_setpoint(
        target_temp=23.0, outdoor_temp=25.0,
        heat_loss_coefficient=0.19, emitter_ua=1.4,
    ) == 23.0,
    "a compensation curve never runs below its own target",
)
R.check(
    "delivery cannot be negative",
    _mv.emitter_delivery(mix_temp=20.0, zone_temp=25.0, ua=1.4) == 0.0,
    "a valve can shut, but it cannot cool a house",
)

# Survival: stored heat leaves at house-demand rate, not in one dump. Under
# the old law this tank was at the curve within two steps.
_surv = _tank_run(_mv.MODE_MANUAL, 0.0, start=60.0, hours=2.0)
R.check(
    "a charged tank survives hours, not steps",
    _surv.buffer_tank_temperature > 45.0,
    f"60 C held {_surv.buffer_tank_temperature:.1f} C after 2 h; the old law "
    "left it at the curve inside two steps",
)
R.check(
    "and while it lasts the tank alone carries the house",
    _surv.upper_floor_temperature > 21.0,
    f"house at {_surv.upper_floor_temperature:.2f} C on stored heat only",
)

# dt-invariance: the old gap term divided by dt_hours, so halving the step
# doubled the demand and the trajectory changed with time_step_minutes.
_dt_a = _tank_run(_mv.MODE_MANUAL, 0.0, start=60.0)
_dt_b = _tank_run(_mv.MODE_MANUAL, 0.0, start=60.0, dt=0.125)
R.check(
    "the trajectory does not depend on the step length",
    abs(_dt_a.buffer_tank_temperature - _dt_b.buffer_tank_temperature) < 0.3,
    f"6 h end state {_dt_a.buffer_tank_temperature:.2f} C at 15 min vs "
    f"{_dt_b.buffer_tank_temperature:.2f} C at 7.5 min",
)

# Design-point equivalence: when the tank cannot meet the curve the valve
# saturates wide open and delivery follows the raw tank temperature, exactly
# as the pre-valve calibration assumed.
_p_dp = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=23.0,
    cop_flow_carnot=True,
)
_m_dp = ThermalModel(_p_dp)
_st_dp = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=26.0, outdoor_temperature=-20.0,
)
_after_dp = _m_dp.simulate_step(_st_dp, 0.0, -20.0, dt_hours=0.25)
_ua_tot = _p_dp.max_electrical_power * max(_p_dp.cop_nominal, 1.0) / max(
    _p_dp.emitter_design_delta_t, 1.0
)
_ua_rad = _p_dp.radiator_power_fraction * _ua_tot
_ua_floor = (1.0 - _p_dp.radiator_power_fraction) * _ua_tot
_q_open = _ua_rad * (26.0 - 21.0) + _ua_floor * (26.0 - 25.0)
_q_loss_buf = _p_dp.buffer_tank_heat_loss_coefficient * (26.0 - 20.0)
_dT_expect = -(_q_open + _q_loss_buf) / _p_dp.buffer_tank_thermal_mass * 0.25
R.check(
    "below the curve the valve saturates wide open",
    abs(_after_dp.buffer_tank_temperature - (26.0 + _dT_expect)) < 1e-6,
    "delivery at a depleted tank follows the raw tank temperature, "
    "preserving the design-point calibration",
)

# Conservation: with the pump off, what the tank loses in a step is exactly
# what the emitters received plus the standing loss.
_st_c = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=50.0, outdoor_temperature=-5.0,
)
_after_c = _m_dp.simulate_step(_st_c, 0.0, -5.0, dt_hours=0.25)
_u_up = _m_dp.effective_heat_loss_coefficient(
    _p_dp.upper_floor_heat_loss, 0.0, 0.0
)
_u_lo = _m_dp.effective_heat_loss_coefficient(
    _p_dp.lower_floor_heat_loss_learned, 0.0, 0.0
)
_fs_c = _mv.flow_setpoint(
    target_temp=23.0, outdoor_temp=-5.0,
    heat_loss_coefficient=_u_up + _u_lo, emitter_ua=_ua_tot,
)
_tmix_c = min(50.0, _fs_c)
_q_del = _mv.emitter_delivery(
    mix_temp=_tmix_c, zone_temp=21.0, ua=_ua_rad
) + _mv.emitter_delivery(mix_temp=_tmix_c, zone_temp=25.0, ua=_ua_floor)
_q_stand = _p_dp.buffer_tank_heat_loss_coefficient * (50.0 - 20.0)
_lost = (50.0 - _after_c.buffer_tank_temperature) * _p_dp.buffer_tank_thermal_mass
R.check(
    "energy is conserved: the tank's loss is the delivery plus standing loss",
    abs(_lost - (_q_del + _q_stand) * 0.25) < 1e-6,
    f"tank lost {_lost:.4f} kWh vs {( _q_del + _q_stand) * 0.25:.4f} delivered+lost",
)

# The behaviour the whole feature exists for: with a valve and a price spread,
# the optimizer concentrates purchases into the cheap night and coasts the
# peaks on stored heat; with flat prices that concentration must vanish -- the
# null control every sizing claim here needs. Both are full solves against a
# tank that starts too cold to coast for free, because a tank that already
# holds enough heat gives charging nothing to displace and the optimizer is
# right to decline (measured: exactly that, at a 40 C start).
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _StoreOpt,
    OptimizationConfig as _StoreCfg,
)


def _storage_plan(price_profile):
    p = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_MANUAL, buffer_max_temp=70.0,
        cop_flow_carnot=True,
        upper_floor_thermal_mass=3.0, lower_floor_thermal_mass=4.5,
        upper_floor_heat_loss=0.10, lower_floor_heat_loss=0.09,
        radiator_power_fraction=0.4,
    )
    m = ThermalModel(p)
    opt = _StoreOpt(m, _StoreCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0,
    ))
    n = 96
    hours = np.arange(n) * 0.25
    if price_profile == "spread":
        prices = np.full(n, 1.80)
        prices[hours < 5] = 0.90
        prices[(hours >= 7) & (hours < 10)] = 4.80
        prices[(hours >= 16) & (hours < 20)] = 7.40
    else:
        prices = np.full(n, 1.20)
    outdoor = np.full(n, -10.0)
    zeros = np.zeros(n)
    st = ThermalState(
        room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=21.0,
        buffer_tank_temperature=25.0, outdoor_temperature=-10.0,
    )
    r = opt.optimize(st, prices, outdoor, zeros, zeros, zeros,
                     datetime(2026, 1, 15))
    pw = np.asarray(r.power_schedule)
    m.simulate_trajectory(st, pw, outdoor, zeros, zeros, zeros, 0.25)
    night = float(pw[hours < 5].sum() * 0.25)
    peaks = float(
        pw[((hours >= 7) & (hours < 10)) | ((hours >= 16) & (hours < 20))].sum()
        * 0.25
    )
    return night, peaks, m.last_buffer_trajectory


_night_s, _peak_s, _buf_s = _storage_plan("spread")
_night_f, _peak_f, _buf_f = _storage_plan("flat")
R.check(
    "with a price spread the optimizer charges through the cheap night",
    _night_s > 22.0,
    f"bought {_night_s:.1f} kWh of a possible 30 in the 00-05 trough",
)
R.check(
    "and deliberately lifts the tank to do it",
    float(_buf_s.max()) > 25.0 + 8.0,
    f"tank peaked at {float(_buf_s.max()):.1f} C from a 25 C start",
)
R.check(
    "and coasts both price peaks on stored heat",
    _peak_s < 2.0,
    f"bought {_peak_s:.1f} kWh across seven peak hours",
)
R.check(
    "the null control: flat prices produce no night concentration",
    _night_f < _night_s - 5.0 and _peak_f > 10.0,
    f"flat: night {_night_f:.1f} kWh, peak-hours {_peak_f:.1f} kWh -- "
    "storage must not appear where it cannot pay",
)


R.section("The valve hold schedule (item 29)")

# A fixed-curve valve starts feeding the house the moment the tank is warmer
# than the curve, so storage mostly shifts the hours right after charging --
# measured in v3.10.0 at roughly a fifth of the analytical value. A valve the
# optimizer can command does not have to wait passively: lower the curve
# between charging and the peak and the tank holds its heat for when it is
# worth most. The schedule is a *candidate*: derived from the solved plan,
# re-solved in full, and adopted only if it beats the fixed target on the
# same objective.


def _hold_plan(price_profile, mode=_mv.MODE_SMART_WRITE, volume=750.0):
    p = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=volume,
        mixing_valve_mode=mode, buffer_max_temp=70.0, cop_flow_carnot=True,
        upper_floor_thermal_mass=3.0, lower_floor_thermal_mass=4.5,
        upper_floor_heat_loss=0.10, lower_floor_heat_loss=0.09,
        radiator_power_fraction=0.4,
    )
    m = ThermalModel(p)
    opt = _StoreOpt(m, _StoreCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0,
    ))
    n = 96
    hours = np.arange(n) * 0.25
    if price_profile == "spread":
        prices = np.full(n, 1.80)
        prices[hours < 5] = 0.90
        prices[(hours >= 7) & (hours < 10)] = 4.80
        prices[(hours >= 16) & (hours < 20)] = 7.40
    else:
        prices = np.full(n, 1.20)
    outdoor = np.full(n, -10.0)
    zeros = np.zeros(n)
    st = ThermalState(
        room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=21.0,
        buffer_tank_temperature=25.0, outdoor_temperature=-10.0,
    )
    return opt.optimize(st, prices, outdoor, zeros, zeros, zeros,
                        datetime(2026, 1, 15)), hours


_hold_r, _hold_hours = _hold_plan("spread")
R.check(
    "a price spread earns a hold schedule",
    bool(_hold_r.valve_target_schedule),
    "with cheap hours to charge in and a peak to save for, a commanded "
    "valve has something to do that a fixed one cannot",
)
_sched = np.asarray(_hold_r.valve_target_schedule or [23.0] * 96)
R.check(
    "and the schedule is fully resolved -- real temperatures, no sentinels",
    len(_sched) == 96 and bool(np.all((_sched >= 15.0) & (_sched <= 30.0))),
    f"range {_sched.min():.1f}-{_sched.max():.1f} C",
)
R.check(
    "it holds the valve down between charging and the peak",
    bool(np.any(_sched < 20.0)) and bool(np.any(_sched >= 22.0)),
    f"{int((_sched < 20.0).sum())} held steps of 96; a schedule that never "
    "lowers the curve is the fixed target under another name",
)
_floor_by_step = np.array([
    _StoreCfg(horizon_hours=24, time_step_minutes=15, target_temp=21.0,
              min_temp=17.0, max_temp=23.0).get_temp_bounds((i * 0.25) % 24)[0]
    for i in range(96)
])
R.check(
    "and it never asks for a house below the comfort floor",
    bool(np.all(_sched >= _floor_by_step - 1e-9)),
    f"lowest target {_sched.min():.1f} C against a per-step floor bottoming "
    f"at {_floor_by_step.min():.1f} C -- the hold uses the floor the solve "
    "already plans against (which the night setback lowers), so it can "
    "never ask for a house the objective would refuse",
)

# The null control, and the two gates.
_flat_r, _ = _hold_plan("flat")
R.check(
    "the null control: flat prices earn no schedule at all",
    not _flat_r.valve_target_schedule,
    "with nothing to arbitrage there is nothing to hold for, and the "
    "candidate is not even proposed",
)
_read_r, _ = _hold_plan("spread", mode=_mv.MODE_SMART_READ)
R.check(
    "a valve the integration cannot command gets no schedule",
    not _read_r.valve_target_schedule,
    "smart_read and manual can only be told what to do by a human; "
    "planning a schedule nobody will actuate would make the plan a fiction",
)
_small_r, _ = _hold_plan("spread", volume=35.0)
R.check(
    "and neither does a tank too small to be a store",
    not _small_r.valve_target_schedule,
    "below BUFFER_STORE_MIN_VOLUME there is no charge worth holding",
)

# The adoption rule itself: a candidate that does not beat the fixed target
# on the same objective must be discarded, schedule and all.
_ho = _StoreOpt(
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_SMART_WRITE, buffer_max_temp=70.0,
        cop_flow_carnot=True,
    )),
    _StoreCfg(horizon_hours=24, time_step_minutes=15,
              target_temp=21.0, min_temp=17.0, max_temp=23.0),
)
_flat_prices = np.full(96, 1.20)
_spread_prices = np.full(96, 1.80)
_spread_prices[np.arange(96) * 0.25 < 5] = 0.90
_spread_prices[(np.arange(96) * 0.25 >= 16) & (np.arange(96) * 0.25 < 20)] = 7.40
_pw_charge = np.zeros(96)
_pw_charge[:20] = 6.0
_floors = np.full(96, 17.0)
R.check(
    "no candidate is derived where prices are flat",
    _ho._derive_hold_schedule(_pw_charge, _flat_prices, _floors) is None,
    "the derivation refuses before the solver is ever asked",
)
R.check(
    "nor where the plan never charges",
    _ho._derive_hold_schedule(np.zeros(96), _spread_prices, _floors) is None,
    "there is no stored heat to hold",
)
_derived = _ho._derive_hold_schedule(_pw_charge, _spread_prices, _floors)
R.check(
    "a charging plan against a spread does derive one",
    _derived is not None and bool(np.any(np.asarray(_derived) < 20.0)),
    f"got {None if _derived is None else 'a schedule'}",
)
R.check(
    "the peak itself is never held down",
    _derived is not None
    and bool(np.all(np.asarray(_derived)[
        (np.arange(96) * 0.25 >= 16) & (np.arange(96) * 0.25 < 20)
    ] >= 22.0)),
    "holding through the peak would store heat for a moment that has "
    "already arrived -- the tank must be delivering then, not saving",
)

# And the model has to actually obey a per-step target, or the schedule is
# a number the plan believes and the physics ignores.
_ht_p = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode=_mv.MODE_SMART_WRITE, buffer_max_temp=70.0,
    cop_flow_carnot=True,
)
_ht_m = ThermalModel(_ht_p)
_ht_st = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=60.0, outdoor_temperature=-5.0,
)
_ht_zero = np.zeros(24)
_ht_open = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero, 0.25,
    valve_targets=np.full(24, 23.0),
)
_ht_open_end = float(_ht_m.last_buffer_trajectory[-1])
_ht_held = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero, 0.25,
    valve_targets=np.full(24, 17.0),
)
_ht_held_end = float(_ht_m.last_buffer_trajectory[-1])
R.check(
    "a held valve really does keep heat in the tank",
    _ht_held_end > _ht_open_end + 2.0,
    f"6 h coasting: open curve leaves {_ht_open_end:.1f} C, held leaves "
    f"{_ht_held_end:.1f} C -- if these matched, the schedule would be a "
    "number the plan believes and the physics ignores",
)
R.check(
    "and no schedule is byte-for-byte the configured target",
    float(_ht_m.simulate_trajectory(
        _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero,
        0.25, valve_targets=None,
    )[0][-1]) == float(_ht_m.simulate_trajectory(
        _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero,
        0.25, valve_targets=np.full(24, _ht_p.comfort_ceiling),
    )[0][-1]),
    "passing the value the model would have used itself must change nothing",
)

# The tank's ceiling is a hard constraint in the solve, not a soft penalty.
# The model's clamp deletes heat charged into a full tank, so in the
# objective overcharging is merely wasteful -- and at a low enough price the
# solver is indifferent to waste while the real tank boils. The tighten loop
# must cut the ceiling at exactly the refusing steps.


def _cap_fixture():
    p = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_MANUAL, buffer_max_temp=60.0,
        cop_flow_carnot=True,
        upper_floor_thermal_mass=3.0, lower_floor_thermal_mass=4.5,
        upper_floor_heat_loss=0.10, lower_floor_heat_loss=0.09,
        radiator_power_fraction=0.4,
    )
    m = ThermalModel(p)
    opt = _StoreOpt(m, _StoreCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0,
    ))
    n = 96
    st = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, slab_temperature=23.0,
        buffer_tank_temperature=55.0, outdoor_temperature=-2.0,
    )
    zeros = np.zeros(n)
    return p, m, opt, st, np.full(n, 0.001), np.full(n, -2.0), zeros


_cp, _cm, _copt, _cst, _cprices, _cout, _czeros = _cap_fixture()

# The mechanism, directly: a full-power schedule against a near-full tank
# must refuse heat, and the tighten helper must cut those steps' ceilings.
_full = np.full(96, _cp.max_electrical_power)
_cm.simulate_trajectory(_cst, _full, _cout, _czeros, _czeros, _czeros, 0.25)
R.check(
    "charging a full tank at full power is refused by the physics",
    _cm.last_buffer_refused is not None and _cm.last_buffer_refused.max() > 0.5,
    f"peak refusal {_cm.last_buffer_refused.max():.2f} kW",
)


class _FakeResult:
    power_schedule = _full


_caps = np.full(96, _cp.max_electrical_power)
_tightened = _copt._tighten_buffer_caps(
    _FakeResult(), _caps, _cst, _cout, _czeros, _czeros, _czeros, 0.25
)
R.check(
    "the tighten loop cuts the ceiling at the refusing steps",
    _tightened and _caps.min() < _cp.max_electrical_power - 0.5,
    f"lowest ceiling now {_caps.min():.2f} kW of {_cp.max_electrical_power}",
)

# End to end: even at effectively free electricity, the returned plan must
# not charge past the cap. Free power is the adversarial case -- deleted
# heat costs nothing, so only the hard constraint stands between the solver
# and a boiled tank.
_cres = _copt.optimize(
    _cst, _cprices, _cout, _czeros, _czeros, _czeros, datetime(2026, 1, 15)
)
_cm.simulate_trajectory(
    _cst, np.asarray(_cres.power_schedule), _cout,
    _czeros, _czeros, _czeros, 0.25,
)
R.check(
    "even free electricity cannot plan past the tank's ceiling",
    float(_cm.last_buffer_refused.max()) < 1e-6,
    f"refused {float(_cm.last_buffer_refused.max()):.4f} kW somewhere in the "
    "final plan; the cap loop should have re-solved it away",
)
R.check(
    "and the trajectory itself respects the cap",
    float(_cm.last_buffer_trajectory.max()) <= 60.0 + 1e-6,
    f"tank peaked at {float(_cm.last_buffer_trajectory.max()):.2f} C",
)

# The recommendation is surfaced, not just computable. recommend_target()
# existed since v3.7.0 with zero callers -- the integration could recommend a
# setting and told nobody. The coordinator now publishes it for the
# diagnostic sensor.
_vc = _zone_coord(_BASE, mixing_valve_mode="manual", max_temperature=23.0)
_vview = _vc._mixing_valve_view()
_vrec = _vview.get("valve_target_recommendation")
R.check(
    "the valve recommendation reaches the coordinator's data",
    isinstance(_vrec, dict) and _vrec.get("target") == 23.0,
    f"got {_vrec!r}",
)
R.check(
    "with the reasoning attached, not just a number",
    isinstance(_vrec, dict) and bool(_vrec.get("reason")),
    "a bare setpoint invites blind trust",
)
R.check(
    "and stays out of the data entirely without a valve to set",
    _zone_coord(_BASE)._mixing_valve_view() == {},
    "no valve, no keys -- existing captures of the coordinator's data must "
    "stay byte-for-byte identical",
)


R.section("smart_write: the optimizer commands the valve (item 29)")

# The mode was withheld until its actuation path existed -- a mode that cannot
# do what its name says is worse than one that is absent. It now writes the
# recommended target to the valve's own controller through a configured
# number/input_number/climate entity.
R.check(
    "smart_write is selectable now that it can act",
    _mv.MODE_SMART_WRITE in _mv.SELECTABLE_MODES,
    "the actuation path exists, so the mode may be offered",
)


def _write_coord(**extra):
    return _zone_coord(_BASE, max_temperature=23.5, **extra)


_wc = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="number.valve"
)
_asyncio.run(_wc._command_valve_target())
_calls = _wc.hass.services.calls
R.check(
    "a number entity is commanded through set_value",
    _calls == [("number", "set_value",
                {"entity_id": "number.valve", "value": 23.5})],
    f"got {_calls!r}",
)
R.check(
    "and the commanded number is the comfort ceiling, the same value the "
    "dumb-valve recommendation gives",
    _calls and _calls[0][2]["value"] == 23.5,
    "commanding what a read-back sensor reports would freeze whatever the "
    "valve held when the mode was enabled",
)

# An unchanged answer is not re-sent: the write runs after every optimization
# cycle, and re-commanding an identical setpoint every 15 minutes wears flash
# on some controllers.
_asyncio.run(_wc._command_valve_target())
R.check(
    "an unchanged target is not rewritten",
    len(_wc.hass.services.calls) == 1,
    f"{len(_wc.hass.services.calls)} calls after two cycles with one answer",
)
_wc._thermal_params.comfort_ceiling = 22.0
_asyncio.run(_wc._command_valve_target())
R.check(
    "while a changed comfort band reaches the valve",
    len(_wc.hass.services.calls) == 2
    and _wc.hass.services.calls[1][2]["value"] == 22.0,
    f"got {_wc.hass.services.calls[1:]}",
)

_cc = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="climate.valve"
)
_asyncio.run(_cc._command_valve_target())
R.check(
    "a climate entity is commanded through set_temperature",
    _cc.hass.services.calls == [("climate", "set_temperature",
                                 {"entity_id": "climate.valve",
                                  "temperature": 23.5})],
    f"got {_cc.hass.services.calls!r}",
)

_tc = _write_coord(
    mixing_valve_mode="smart_write",
    mixing_valve_write_entity="number.valve",
    mixing_valve_target=22.0,
)
_asyncio.run(_tc._command_valve_target())
R.check(
    "a configured static target wins over the ceiling",
    _tc.hass.services.calls[0][2]["value"] == 22.0,
    f"got {_tc.hass.services.calls!r}",
)

_nc = _write_coord(mixing_valve_mode="smart_write")
_asyncio.run(_nc._command_valve_target())
_mc = _write_coord(
    mixing_valve_mode="manual", mixing_valve_write_entity="number.valve"
)
_asyncio.run(_mc._command_valve_target())
_uc = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="switch.valve"
)
_asyncio.run(_uc._command_valve_target())
R.check(
    "no entity, another mode, or an uncommandable domain all write nothing",
    _nc.hass.services.calls == [] and _mc.hass.services.calls == []
    and _uc.hass.services.calls == [],
    f"got {_nc.hass.services.calls} / {_mc.hass.services.calls} / "
    f"{_uc.hass.services.calls}",
)

# With a hold schedule in force the actuator follows *it*, not the fixed
# recommendation -- otherwise the plan holds the tank on paper while the real
# valve stays wide open and empties it, which is worse than never planning
# the hold at all.
_sc = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="number.valve"
)
_sc._current_action = {"valve_target": 17.0}
_asyncio.run(_sc._command_valve_target())
R.check(
    "a hold schedule is what actually reaches the valve",
    _sc.hass.services.calls
    and _sc.hass.services.calls[0][2]["value"] == 17.0,
    f"got {_sc.hass.services.calls!r}; the plan holds this step at 17.0, "
    "and writing the fixed 23.5 would empty the tank the plan is saving",
)

# The step the actuator writes is chosen by `get_current_action`, once, so
# there is no second search to disagree with the first.
_ao = _StoreOpt(
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, mixing_valve_mode=_mv.MODE_SMART_WRITE)),
    _StoreCfg(horizon_hours=24, time_step_minutes=15,
              target_temp=21.0, min_temp=17.0, max_temp=23.0),
)
_a_now = datetime(2026, 1, 15, 12, 0)
_a_res = _hold_r
_a_res_action = _ao.get_current_action(_hold_r, _hold_r.timestamps[8])
R.check(
    "the current action carries the valve target for the step it is about",
    _a_res_action.get("valve_target") == round(
        float(_hold_r.valve_target_schedule[8]), 1
    ),
    f"action says {_a_res_action.get('valve_target')}, schedule step 8 is "
    f"{_hold_r.valve_target_schedule[8]:.1f}",
)


R.section("Per-step external heat reaches the model and the plan (item 28)")

# The harness prerequisite the item names: `external_heat_active` was a scalar
# bool on the initial state and the model had no free-heat input at all, so a
# fire could not be represented, sized, or planned around.

_x_p = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=200.0,
    upper_floor_thermal_mass=3.0, lower_floor_thermal_mass=4.5,
    upper_floor_heat_loss=0.10, lower_floor_heat_loss=0.09,
    radiator_power_fraction=0.4,
)
_x_m = ThermalModel(_x_p)
_x_st = ThermalState(
    room_temperature=20.0, upper_floor_temperature=20.0,
    lower_floor_temperature=20.0, slab_temperature=21.0,
    buffer_tank_temperature=30.0, outdoor_temperature=-5.0,
)


def _x_coast(ext_kw):
    st = _x_st
    for _ in range(8):
        st = _x_m.simulate_step(
            st, 0.0, -5.0, dt_hours=0.25, external_heat_kw=ext_kw
        )
    return st


_x_none = _x_coast(0.0)
_x_burn = _x_coast(8.0)
R.check(
    "free heat warms the house with the compressor off",
    _x_burn.upper_floor_temperature > _x_none.upper_floor_temperature + 1.0,
    f"{_x_none.upper_floor_temperature:.2f} C without vs "
    f"{_x_burn.upper_floor_temperature:.2f} C with an 8 kW burn",
)
R.check(
    "and it is heat, not electricity: a zero burn is the old model exactly",
    _x_coast(0.0) == _x_none,
    "the default path must stay byte-for-byte identical",
)

# The plan defers electric heat the furnace is already providing: a burn
# forecast over the first six hours must reduce what the optimizer buys
# there, and an all-zero forecast must change nothing at all.
_x_opt = _StoreOpt(_x_m, _StoreCfg(
    horizon_hours=24, time_step_minutes=15,
    target_temp=21.0, min_temp=17.0, max_temp=23.0,
))
_x_prices = np.full(96, 1.2)
_x_out = np.full(96, -5.0)
_x_zero = np.zeros(96)
_x_blind = _x_opt.optimize(
    _x_st, _x_prices, _x_out, _x_zero, _x_zero, _x_zero, datetime(2026, 1, 15)
)
_x_fc = np.zeros(96)
_x_fc[:24] = 6.0
_x_aware = _x_opt.optimize(
    _x_st, _x_prices, _x_out, _x_zero, _x_zero, _x_zero, datetime(2026, 1, 15),
    external_heat_kw=_x_fc,
)
_x_pb = np.asarray(_x_blind.power_schedule)
_x_pa = np.asarray(_x_aware.power_schedule)
R.check(
    "a burn forecast reduces electric heating during the burn",
    float(_x_pa[:24].sum()) < float(_x_pb[:24].sum()) - 2.0,
    f"first 6 h: blind {_x_pb[:24].sum() * 0.25:.1f} kWh vs "
    f"aware {_x_pa[:24].sum() * 0.25:.1f} kWh",
)
_x_zeroed = _x_opt.optimize(
    _x_st, _x_prices, _x_out, _x_zero, _x_zero, _x_zero, datetime(2026, 1, 15),
    external_heat_kw=np.zeros(96),
)
R.check(
    "an all-zero forecast is byte-identical to no forecast",
    np.array_equal(np.asarray(_x_zeroed.power_schedule), _x_pb),
    "zeros must take the exact default path",
)


R.section("Setup topology: one description for every picture (items 32/33)")

from heatpump_optimizer import topology as _topo  # noqa: E402

_full_cfg = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 4.5,
    "dhw_tank_volume": 200.0,
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    "external_heat_detection_enabled": True,
    "wood_tank_top_entity": "sensor.wood_top",
}
_full = _topo.describe_setup(_full_cfg)
R.check(
    "the topology derives from the model's own inference",
    _full["two_zone"] and _full["dhw"] and _full["buffer"]["is_store"],
    "two-zone from zone settings, DHW from tank settings, store from the "
    "valve and volume -- never from separate flags that could disagree",
)
_places = {s["place"] for s in _full["slots"]}
R.check(
    "a full topology shows every place",
    {"lower_zone", "dhw_tank", "wood_tank", "mixing_valve"} <= _places,
    f"got {sorted(_places)}",
)
_empty_slots = [s for s in _full["slots"] if s["entity"] is None]
_filled = {s["key"]: s["entity"] for s in _full["slots"] if s["entity"]}
R.check(
    "empty slots are shown empty, not omitted",
    len(_empty_slots) >= 5 and "sensor.wood_top" in _filled.values(),
    "a diagram that silently omits an unconfigured sensor looks complete, "
    "which is worse than no diagram",
)

_min = _topo.describe_setup({"indoor_temp_entity": "sensor.i"})
_min_places = {s["place"] for s in _min["slots"]}
R.check(
    "a minimal setup does not grow places it does not have",
    not ({"lower_zone", "dhw_tank", "wood_tank", "wood_valve"} & _min_places),
    f"got {sorted(_min_places)}",
)

_text = _topo.render_text_summary(_full)
R.check(
    "every assignable slot carries the domains it accepts",
    all(s.get("domains") for s in _full["slots"])
    and {s["key"] for s in _full["slots"]} <= set(_topo.ASSIGNABLE_KEYS),
    "the picker filters and the service validates from one list, so a "
    "diagram cannot offer what the service would refuse",
)
R.check(
    "a temperature slot does not accept a switch",
    "switch" not in _topo.ASSIGNABLE_KEYS[hp_const.CONF_INDOOR_TEMP_ENTITY]
    and "switch" in _topo.ASSIGNABLE_KEYS[
        hp_const.CONF_HEAT_PUMP_SWITCH_ENTITY
    ],
    "assigning a switch to a temperature slot is the mistake a clickable "
    "diagram makes easy, and it plans against nonsense rather than erroring",
)

R.check(
    "the flow overview is a fenced monospaced block",
    _text.startswith("```\n") and _text.endswith("\n```"),
    "the one drawing surface every install already renders",
)
R.check(
    "with configured sensors named and empty slots called out",
    "sensor.wood_top" in _text and "not configured" in _text,
)
R.check(
    "and the storage claim matches the model",
    "used as a store" in _text,
    "a 750 L tank behind a manual valve is a store as of v3.10.0",
)


# A tank cannot deliver heat it does not have. Capping the emitters at the
# weather curve (v3.10.0) made discharge physical for any tank a step cannot
# empty, which is every realistic size -- but a 10 L separator against a 40 K
# flow-to-room difference still overshoots its own Euler step. Measured before
# this bound, a 10 L tank coasting from 60 C reached -8.04 C.
for _vol, _floor in ((10.0, 15.0), (35.0, 15.0), (750.0, 20.0)):
    _tiny = ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=_vol,
        mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=21.0,
        cop_flow_carnot=True,
    ))
    _ts = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=60.0, outdoor_temperature=-5.0,
    )
    _seen = [_ts.buffer_tank_temperature]
    for _ in range(48):
        _ts = _tiny.simulate_step(_ts, 0.0, -5.0, dt_hours=0.25)
        _seen.append(_ts.buffer_tank_temperature)
    R.check(
        f"a {_vol:.0f} L tank cannot discharge below what it is feeding",
        min(_seen) > _floor,
        f"12 h of coasting left the buffer at {min(_seen):.2f} C; unbounded, a "
        "10 L tank went to -8.04 C",
    )

# The settlement is symmetric. It used to charge a deficit and pay nothing for a
# surplus, which made the reported savings understate themselves exactly when
# the plan chose to end the window warm -- by 62 % on flat prices with no valve
# at all, where it is the building's own mass and not the tank. What keeps a
# credit honest is the caps: a store above its useful ceiling is worth nothing
# in either direction.
_warm_end = _st(45.0)
_cool_end = _st(45.0)
for _attr in ("room_temperature", "upper_floor_temperature",
              "lower_floor_temperature", "slab_temperature"):
    setattr(_warm_end, _attr, getattr(_cool_end, _attr) + 2.0)
_charge = _opt_valve._deferred_energy_cost(
    _warm_end, _cool_end, np.full(96, 1.0), _outdoor, caps=_caps_valve
)
_credit = _opt_valve._deferred_energy_cost(
    _cool_end, _warm_end, np.full(96, 1.0), _outdoor, caps=_caps_valve
)
R.check(
    "ending colder than the reference is charged for",
    _charge > 0.1,
    f"a 2 K colder end state settles at {_charge:.3f} SEK",
)
R.check(
    "and ending warmer is credited by exactly the same amount",
    abs(_credit + _charge) < 1e-9,
    f"charged {_charge:.3f} but credited {_credit:.3f}; one-sided settlement "
    "returned 0.0 here and understated the savings it reported",
)

R.section("Buffer tank standby loss scales with the tank (items 27/29)")

# UA follows the tank's *surface area*, which grows as volume^(2/3), while the
# cooling rate is UA/C and so falls as volume^(-1/3). Holding the rate flat
# across every size made UA scale linearly with volume, which modelled a large
# accumulator as losing an order of magnitude more than it does -- enough on its
# own to make storing heat never pay.

_ua = lambda v, **kw: ThermalParameters(
    buffer_tank_volume=float(v), **kw
).buffer_tank_heat_loss_coefficient

_ua35, _ua750 = _ua(35), _ua(750)
R.check(
    "a bigger tank loses more in absolute terms",
    _ua750 > _ua35,
    f"{_ua35*1000:.2f} vs {_ua750*1000:.2f} W/K",
)
R.check(
    "but far less than in proportion to its volume",
    _ua750 < _ua35 * (750 / 35) * 0.5,
    f"{_ua750*1000:.2f} W/K vs {_ua35*1000*750/35:.1f} if it scaled with volume",
)
# Surface area grows as volume^(2/3), so UA should too, within a little slack.
_expected = _ua35 * (750 / 35) ** (2.0 / 3.0)
R.check(
    "UA grows with surface area, not with volume",
    abs(_ua750 - _expected) < 0.02 * _expected,
    f"{_ua750*1000:.2f} W/K, area-scaled prediction {_expected*1000:.2f}",
)

# The prior has to be physically possible. The old flat 6 C/h came out at
# 9.7 W/K on a 35 L tank -- worse than a bare uncovered cylinder.
_area35 = hp_const.buffer_tank_surface_area(35)
R.check(
    "the prior is no worse than an uninsulated tank",
    _ua35 * 1000 <= hp_const.BUFFER_INSULATION_U_WORST * _area35,
    f"{_ua35*1000:.2f} W/K vs bare-cylinder {hp_const.BUFFER_INSULATION_U_WORST*_area35:.2f}",
)

# The clamp is the half that mattered most: it decides what the learner is
# *allowed* to conclude. A real 750 L accumulator is around 2 W/K, and the flat
# 0.5 C/h floor put a hard stop several times above that.
_lo, _hi = hp_const.buffer_cooling_rate_bounds(750)
_real = _ua(750, buffer_cooling_rate=0.06)
R.check(
    "the learner may reach a real accumulator's standby loss",
    _lo <= 0.06 <= _hi and 1.0 < _real * 1000 < 4.0,
    f"bounds {_lo:.3f}-{_hi:.2f} C/h, 0.06 C/h -> {_real*1000:.2f} W/K",
)
R.check(
    "which the old flat floor would have forbidden",
    0.06 < hp_const.BUFFER_COOLING_RATE_MIN,
    "if this ever passes trivially the floor has been changed too",
)

# A rate someone configured explicitly must still win over the derived prior.
R.check(
    "an explicitly configured rate is honoured",
    _ua(750, buffer_cooling_rate=0.5) > _ua(750),
    "the derived prior should only apply when nothing is set",
)
R.check(
    "and from_config leaves it unset rather than injecting a 35 L number",
    ThermalParameters.from_config({"buffer_tank_volume": 750.0}).buffer_cooling_rate
    == 0.0,
    "0.0 is the sentinel meaning 'derive a prior from the volume'",
)


R.section("Two-zone loss split learning (item 31)")

# `house_heat_loss_scale` multiplies BOTH zone losses, so it can move the total
# but never the split. The ratio owns the split and is fitted from the lower
# zone; the scale owns the level and is fitted from the upper. Two parameters,
# two independent measurements.

import inspect
from dataclasses import replace
from datetime import timedelta as _timedelta

import homeassistant.util.dt as _lz_dt


def _two_zone_learner(*, lower_entity=None, ratio=1.0):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        # Two-zone is inferred from the presence of zone settings rather than a
        # flag, so a bare `two_zone_enabled` would silently do nothing.
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
    }
    if lower_entity:
        cfg["lower_floor_temp_entity"] = lower_entity
    c = _Coord(_FakeHass({}), _FakeEntry(data=cfg))
    c._apply_lower_floor_loss_ratio(ratio)
    return c


def _drive_lower(coord, *, observed_lower, hours=0.5, power=2.0):
    """One learning interval, with the plant landing on `observed_lower`."""
    base = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.0, slab_temperature=27.0,
        outdoor_temperature=-5.0,
    )
    now = _lz_dt.now()
    coord._last_house_sample = base
    coord._last_house_sample_time = now - _timedelta(hours=hours)
    coord._current_state = replace(base, lower_floor_temperature=observed_lower)
    coord._current_action = {"power": power}
    _asyncio.run(coord._async_learn_lower_floor_loss())
    return coord._lower_floor_loss_ratio, coord._lower_floor_loss_samples


# Backward compatibility: untouched, the ratio is 1.0 and the model is exactly
# what it was before this existed.
R.check(
    "the split defaults to the configured one",
    ThermalParameters(two_zone_enabled=True).lower_floor_loss_ratio == 1.0,
)
_p = ThermalParameters(two_zone_enabled=True)
R.check(
    "and the learned lower loss is then just the configured value",
    _p.lower_floor_heat_loss_learned == _p.lower_floor_heat_loss,
)

# Without a real sensor the lower zone is inferred from the floor return water,
# and the inference is derived from the same sensor as the slab -- so it carries
# no independent information. Fitting against it would fit the model's own prior.
_no_sensor = _two_zone_learner()
_r, _n = _drive_lower(_no_sensor, observed_lower=21.5)
R.check(
    "without a lower-floor sensor nothing is learned",
    _r == 1.0 and _n == 0,
    f"ratio {_r}, {_n} samples",
)

# With one, a house losing more heat than the model expects must push the ratio
# up, and one losing less must push it down.
_cold = _two_zone_learner(lower_entity="sensor.lower")
_r_cold, _n_cold = _drive_lower(_cold, observed_lower=19.6)
_warm = _two_zone_learner(lower_entity="sensor.lower")
_r_warm, _n_warm = _drive_lower(_warm, observed_lower=20.4)
R.check(
    "a lower zone colder than predicted raises its share of the loss",
    _r_cold > 1.0 and _n_cold == 1,
    f"ratio {_r_cold:.4f} after {_n_cold} samples",
)
R.check(
    "and a warmer one lowers it",
    _r_warm < 1.0 and _n_warm == 1,
    f"ratio {_r_warm:.4f} after {_n_warm} samples",
)

# The fit must not run away on one odd interval, exactly as the house scale
# rate-limits itself.
R.check(
    "a single interval cannot move the split more than the step limit",
    abs(_r_cold - 1.0) <= 0.05 + 1e-9 and abs(_r_warm - 1.0) <= 0.05 + 1e-9,
    f"{_r_cold:.4f} / {_r_warm:.4f}",
)

# Symmetry, which is the subtle one. The lower zone's time constant is over a
# hundred hours (C/u = 8.0/0.07), so its temperature barely moves and the Newton
# step is huge: a fraction of a degree implies a ΔU larger than the whole
# coefficient. On the warm side that makes the target *negative*. Discarding
# those while keeping the cold-side ones lets the ratio ratchet upward on noise,
# so the target is clamped rather than thrown away and both sides count.
_pred_lower = 20.2812  # what the model predicts for this interval
_sym_cold = _two_zone_learner(lower_entity="sensor.lower")
_sym_warm = _two_zone_learner(lower_entity="sensor.lower")
_rc, _nc = _drive_lower(_sym_cold, observed_lower=_pred_lower - 0.4)
_rw, _nw = _drive_lower(_sym_warm, observed_lower=_pred_lower + 0.4)
R.check(
    "equal residuals either side of the prediction are both learned from",
    _nc == 1 and _nw == 1,
    f"cold {_nc} samples, warm {_nw} samples",
)
R.check(
    "and they move the split in opposite directions",
    _rc > 1.0 > _rw,
    f"cold {_rc:.4f}, warm {_rw:.4f}",
)
# Both saturating targets must be clipped the same distance from the current
# estimate. A clamp to the fixed global bounds is off-centre — from a ratio of
# 1.0 the ceiling is +2.0 away but the floor only -0.7 — so equal noise on the
# two sides moved the ratio by unequal amounts and it still drifted upward.
R.check(
    "and by exactly the same amount, or noise still ratchets the split",
    abs((_rc - 1.0) + (_rw - 1.0)) < 1e-9,
    f"cold moved {_rc - 1.0:+.4f}, warm moved {_rw - 1.0:+.4f}",
)

# A residual too large to be a loss error is something else -- a window opened,
# a sensor glitch -- and must be rejected rather than absorbed.
_wild = _two_zone_learner(lower_entity="sensor.lower")
_r_wild, _n_wild = _drive_lower(_wild, observed_lower=14.0)
R.check(
    "an implausible residual is rejected, not absorbed",
    _n_wild == 0 and _r_wild == 1.0,
    f"ratio {_r_wild}, {_n_wild} samples",
)

# Physical bounds, like every other learner here.
_clamp = _two_zone_learner(lower_entity="sensor.lower", ratio=99.0)
R.check(
    "the split is clamped to a physical range",
    _clamp._lower_floor_loss_ratio == hp_const.LOWER_FLOOR_LOSS_RATIO_MAX,
    f"got {_clamp._lower_floor_loss_ratio}",
)

# External heat means the house is being warmed by something the model cannot
# see, so every learner has to stop -- this one included.
_ext = _two_zone_learner(lower_entity="sensor.lower")
_ext._external_heat_active = True
_r_ext, _n_ext = _drive_lower(_ext, observed_lower=19.6)
R.check(
    "external heat freezes the split learner too",
    _n_ext == 0 and _ext._learner_freeze_reason == "external_heat_source",
    f"{_n_ext} samples, reason {_ext._learner_freeze_reason}",
)

# The learned value has to survive a restart, or it re-converges from scratch
# every time Home Assistant is restarted.
R.check(
    "the split is persisted alongside the other learned parameters",
    "lower_floor_loss_ratio" in inspect.getsource(_Coord._async_save_thermal_learning),
)

# The two learners share one baseline snapshot, and the house one overwrites it
# near its top. If the order were reversed the split learner would compare the
# current state against itself and silently never learn.
_src = inspect.getsource(_Coord)
R.check(
    "the split learner runs before the one that consumes the baseline",
    _src.index("await self._async_learn_lower_floor_loss()")
    < _src.index("await self._async_learn_house_heat_loss()"),
    "reversing these makes the split learner a no-op",
)


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

R.section("Economy mode (audit item 4)")

# Economy was a rename of auto and nothing else: identical power schedule,
# identical hot water, identical predicted cost, with only the published mode
# string differing -- while services.yaml has promised "wider temperature swings
# allowed" since the mode was added.
from heatpump_optimizer.const import (  # noqa: E402
    ECONOMY_ABSOLUTE_FLOOR,
    ECONOMY_MIN_TEMP_WIDENING,
    MODE_ECONOMY,
    OPERATION_MODES,
)

R.check(
    "economy is a real mode, not a label",
    ECONOMY_MIN_TEMP_WIDENING > 0.0,
    f"the plan may go {ECONOMY_MIN_TEMP_WIDENING} K below the comfort floor",
)
R.check(
    "and it is not a licence to freeze the house",
    ECONOMY_ABSOLUTE_FLOOR >= 12.0,
    f"the widening stops at {ECONOMY_ABSOLUTE_FLOOR} C whatever the floor is",
)

# The widening is applied after the away snapshot so the solve's `finally`
# restore unwinds it. `min_temp` is otherwise written only at `_init_model()`,
# so a widening that escaped the restore would outlive the mode and quietly
# lower the floor of every later plan -- including after the user left economy.
_away_snapshot = param_coord._apply_away_setback()
R.check(
    "the away snapshot carries min_temp, which is what unwinds the widening",
    "min_temp" in _away_snapshot,
    "economy writes _opt_config.min_temp and relies on this restore; drop the "
    "key and the widening leaks into every subsequent solve",
)
R.check(
    "every mode the service accepts can be persisted and restored",
    MODE_ECONOMY in OPERATION_MODES
    and len(set(OPERATION_MODES)) == len(OPERATION_MODES),
    f"{OPERATION_MODES}; the set was written out inline in the service schema "
    "and nowhere else, so a new mode had to be added in two places",
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
