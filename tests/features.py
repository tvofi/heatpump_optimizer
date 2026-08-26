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
prices, mask, _sig = extend_price_series(known, 96, steps, model)
R.check("published prices are preserved exactly", list(prices[:40]) == known)
R.check("the mask marks which steps are real", mask[:40].all() and not mask[40:].any())
R.check("the tail is not flat", len(set(np.round(prices[40:], 4))) > 1)

flat_prices, flat_mask, _ = extend_price_series(known, 96, steps, None)
R.check(
    "without a model the old flat repeat is used, not an invention",
    np.allclose(flat_prices[40:], 1.0),
)
full_prices, full_mask, _ = extend_price_series([1.0] * 96, 96, steps, model)
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
_lvl_prices, _lvl_mask, _lvl_sig = extend_price_series(
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
_wa_outdoor, _, _, _, _ = _wa._weather_series(4, _pa_mid, 0)
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
        # A modest gap: v4.0.5's tracking gate discards samples whose
        # commanded-vs-measured mismatch is too large to be efficiency at
        # all, and this fixture is about the frost-band *split*, not the
        # magnitude — it has to stay on the efficiency side of that gate.
        self._measured_power = 2.6
        self._current_action = {"power": 3.0}
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(
            room_temperature=21.0, outdoor_temperature=outdoor
        )
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._last_measured_cop = None
        self._immersion_active = False

    def _learning_frozen(self, *entities):
        return None

    def _observe_cop_health(self, observed_cop):
        # T4a's health watch is exercised on the real coordinator; this
        # stub only gates the frost-band split.
        return None

    def _fold_capacity_envelope(self, observed_cop):
        # T4b's envelope is likewise exercised on the real coordinator.
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
        # v4.0.0 T3 (#18): the learner also teaches the day-type arrays.
        self._dhw_profile_weekday = [1.0] * 24
        self._dhw_profile_weekend = [1.0] * 24
        self._dhw_daytype_samples = [0, 0]
        self._dhw_daytype_last_day = ["", ""]
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


from heatpump_optimizer.drift import Cusum as _Cusum


class _LearnPersist:
    _async_save_thermal_learning = Coord._async_save_thermal_learning
    _async_load_thermal_learning = Coord._async_load_thermal_learning
    # The save path serialises through the same producer the snapshots
    # use (T4a); a stub with its own dict would test a second format.
    _thermal_learning_payload = Coord._thermal_learning_payload
    _load_t4b_learners = Coord._load_t4b_learners
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
        self._vent_cusum = _Cusum(threshold=1.2, drift=0.08, side=-1)
        self._cop_health_cusum = _Cusum(threshold=0.8, drift=0.01, side=1)
        self._cop_baseline = {}
        self._immersion_events = []
        self._snow_accum_cm = 0.0
        self._snow_accum_last = None
        self._last_heavy_snow = None
        self._capacity_envelope = {}
        self._solar_aperture = {
            "n": 0.0, "mx": 0.0, "my": 0.0, "cov": 0.0, "var": 0.0,
            "scale": 1.0,
        }
        self._internal_gains_profile = None
        from heatpump_optimizer.curve_learning import CurveLearner as _CL
        self._curve_learner = _CL()
        from heatpump_optimizer.freq_control import FrequencyMap as _FM
        self._freq_map = _FM()
        self._freq_fallback = False

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
    "dhw_inlet_current",        # resolved per solve: live sensor or season
    "dhw_window_ready_energy",  # learned per-window quantiles, set per solve
    "dhw_legionella_price_ceiling",  # from the price prior, set per solve
    "dhw_ready_margin_c",       # #11 feedback, set per solve from events
    "solar_aperture_scale",     # #36 learned, set per solve when gated on
    "internal_gains_profile",   # #53 learned per-hour, set per solve
    "cop_scale",                # learned from measured power
    "cop_reference_temp",       # a property of the COP curve, not the house
    "internal_gains",           # not exposed in the config flow
    "dhw_windows",              # parsed separately from a string spec
    "two_zone_enabled",         # inferred from presence, overridable by mode
    "dhw_enabled",              # inferred from which keys are present
    "cop_flow_carnot",          # follows the mixing valve mode
    "cop_flow_reference_temp",  # a property of the COP curve, not the house
    "emitter_design_delta_t",   # a sizing convention, not a per-house setting
}

# Fields that *are* configurable but cannot be probed by substituting a
# sentinel, because the mapping validates them. They get an explicit check
# below instead of being quietly exempted.
validated_enums = {"mixing_valve_mode", "topology_layout_override"}

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

# Two-zone can be forced both ways (v4.0.0). Presence of a zone key can only
# ever turn the model on — the initial flow writes the keys into entry.data,
# where the options flow cannot erase them — so disabling needs the explicit
# mode. Its default must be the presence rule byte-for-byte, or every
# untouched install changes behaviour.
_zone_present = {hp_const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
R.check(
    "presence still enables two-zone when the mode key is absent",
    ThermalParameters.from_config(_zone_present).two_zone_enabled,
)
R.check(
    "mode 'off' disables two-zone even with zone values stored",
    not ThermalParameters.from_config(
        {**_zone_present, hp_const.CONF_TWO_ZONE_MODE: "off"}
    ).two_zone_enabled,
    "presence alone can never turn the model off — that is the whole point",
)
R.check(
    "mode 'on' enables two-zone with no zone key present at all",
    ThermalParameters.from_config(
        {hp_const.CONF_TWO_ZONE_MODE: "on"}
    ).two_zone_enabled,
)
R.check(
    "mode 'auto' is exactly the presence rule, both ways",
    not ThermalParameters.from_config(
        {hp_const.CONF_TWO_ZONE_MODE: "auto"}
    ).two_zone_enabled
    and ThermalParameters.from_config(
        {**_zone_present, hp_const.CONF_TWO_ZONE_MODE: "auto"}
    ).two_zone_enabled,
)
R.check(
    "an unknown mode falls back to the presence rule rather than disabling",
    ThermalParameters.from_config(
        {**_zone_present, hp_const.CONF_TWO_ZONE_MODE: "nonsense"}
    ).two_zone_enabled,
    "a typo in stored options must not silently switch a running model off",
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
# _full_cfg is itself a two-tank configuration (two zones, manual valve,
# a wood-tank probe), so as of v3.15.0 its summary claims the wood tank as
# a real store. The v3.14.1 abstraction caption must survive exactly where
# the abstraction still runs: wood present without a probe.
R.check(
    "a modelled wood tank is claimed as its own store",
    "modelled as its own store" in _text
    and "modelled as heat into the heat-pump tank" not in _text
    and "Heat pump tank: 750 L" in _text,
    "issue #40: with the two-tank model active the summary stops "
    "apologizing for an abstraction it no longer uses",
)
_folded = _topo.render_text_summary(
    _topo.describe_setup({**_full_cfg, "wood_tank_top_entity": None})
)
R.check(
    "the wood abstraction is admitted in prose where it still runs",
    "modelled as heat into the heat-pump tank" in _folded
    and "Buffer tank: 750 L" in _folded,
    "issue #40: a flue switch without a probe still folds wood heat into "
    "the heat-pump tank, and the summary must keep saying so",
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
    "lower_floor_loss_ratio"
    in inspect.getsource(_Coord._thermal_learning_payload)
    and "_thermal_learning_payload"
    in inspect.getsource(_Coord._async_save_thermal_learning),
    "the payload producer is shared with the weekly snapshots (T4a); the "
    "save path must serialise through it, not through a second dict",
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


R.section("Two-tank topology (issue #40)")

# The wood tank is now its own store rather than heat folded into the heat
# pump's tank. The abstraction it replaces was not merely coarse: a burn
# raised the *modelled* HP tank, which is the flow temperature the COP curve
# is evaluated at and the level the safe-ceiling cap is measured against, so
# free heat arrived as a COP penalty and as refused cap headroom the
# optimizer then planned around.

from heatpump_optimizer import mixing_valve as _w2t_mv  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    wood_share as _w2t_share,
)
from heatpump_optimizer.const import (  # noqa: E402
    TOPOLOGY_NO_VALVE as _W2T_NO_VALVE,
    TOPOLOGY_SINGLE_TANK_VALVE as _W2T_ONE_TANK,
    TOPOLOGY_TWO_TANK_4WAY as _W2T_TWO_TANK,
    WATER_SPECIFIC_HEAT as _W2T_CP,
    WOOD_TANK_MIN_MARGIN as _W2T_MARGIN,
)

# --- Gating: a probe, not a flag ------------------------------------------
#
# Resolved from a config dict rather than from hand-built parameters, because
# the question is what a real entry activates. The two-tank model must not
# come on for a flue switch: it has to be initializable from a measurement.

_w2t_cfg_base = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 4.5,
    "buffer_tank_volume": 750.0,
}


def _w2t_from_config(**extra):
    cfg = dict(_w2t_cfg_base)
    cfg.update(extra)
    return ThermalParameters.from_config(cfg)


_w2t_p_no_valve = _w2t_from_config(wood_tank_top_entity="sensor.wood_top")
_w2t_p_full = _w2t_from_config(
    mixing_valve_mode="manual", wood_tank_top_entity="sensor.wood_top"
)
_w2t_p_no_probe = _w2t_from_config(mixing_valve_mode="manual")
_w2t_p_flue = _w2t_from_config(
    mixing_valve_mode="manual",
    external_heat_detection_enabled=True,
    external_heat_entity="binary_sensor.flue",
)
_w2t_p_one_zone = ThermalParameters.from_config({
    "indoor_temp_entity": "sensor.indoor",
    "mixing_valve_mode": "manual",
    "wood_tank_top_entity": "sensor.wood_top",
})

R.check(
    "without a valve the layout is the valveless one",
    _w2t_p_no_valve.topology_layout == _W2T_NO_VALVE
    and not _w2t_p_no_valve.two_tank_modelled,
    f"got {_w2t_p_no_valve.topology_layout}; a wood probe cannot conjure a "
    "4-way valve that is not plumbed in",
)
R.check(
    "a valve, two zones and a wood probe resolve to the 4-way layout",
    _w2t_p_full.topology_layout == _W2T_TWO_TANK
    and _w2t_p_full.two_tank_modelled,
    f"got {_w2t_p_full.topology_layout}",
)
R.check(
    "a valve without a wood probe stays single-tank",
    _w2t_p_no_probe.topology_layout == _W2T_ONE_TANK
    and not _w2t_p_no_probe.two_tank_modelled,
    f"got {_w2t_p_no_probe.topology_layout}",
)
R.check(
    "a flue switch alone does not activate the two-tank model",
    _w2t_p_flue.topology_layout == _W2T_ONE_TANK
    and not _w2t_p_flue.two_tank_modelled,
    "detection says heat is arriving; it does not say how hot the tank is, "
    "and the second state variable has to start from a measurement",
)
R.check(
    "and neither does a wood probe without a second zone",
    _w2t_p_one_zone.topology_layout == _W2T_ONE_TANK
    and not _w2t_p_one_zone.two_tank_modelled,
    "the draw law lives in the two-zone step; there is no other branch to "
    "gate it into",
)
_w2t_p_vol = _w2t_from_config(
    mixing_valve_mode="manual",
    wood_tank_top_entity="sensor.wood_top",
    wood_tank_volume=800.0,
)
R.check(
    "one number sizes the one physical tank",
    abs(_w2t_p_vol.wood_tank_thermal_mass - 800.0 * _W2T_CP) < 1e-12,
    "the detector and the model share CONF_WOOD_TANK_VOLUME, so a tank "
    "cannot be 500 L to one of them and 800 L to the other",
)


# --- Simulation arms ------------------------------------------------------

_w2t_params_two = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=500.0,
    mixing_valve_mode=_w2t_mv.MODE_MANUAL, mixing_valve_target=21.0,
    cop_flow_carnot=True, wood_tank_configured=True, wood_tank_volume=500.0,
)
_w2t_params_off = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=500.0,
    mixing_valve_mode=_w2t_mv.MODE_MANUAL, mixing_valve_target=21.0,
    cop_flow_carnot=True,
)


def _w2t_state(wood, buf=45.0):
    return ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=buf, outdoor_temperature=-5.0,
        wood_tank_temperature=wood,
    )


def _w2t_run(params, wood, burn, *, n=48, power=0.5, dt=0.25):
    model = ThermalModel(params)
    out = model.simulate_trajectory(
        _w2t_state(wood), np.full(n, power), np.full(n, -5.0), dt_hours=dt,
        external_heat_kw=np.full(n, burn),
    )
    return model, out


# --- Reduction: no reading, no second tank --------------------------------
#
# The gate is the *state*, not only the parameters: a configured probe that
# has gone stale must fall back to the old abstraction exactly, wood heat and
# all, rather than to a differently-wrong third behaviour.

_w2t_m_none, _w2t_out_none = _w2t_run(_w2t_params_two, None, 5.0)
_w2t_m_ref, _w2t_out_ref = _w2t_run(_w2t_params_off, None, 5.0)
R.check(
    "a gated-on model with no wood reading reduces byte-for-byte",
    all(
        np.array_equal(a, b)
        for a, b in zip(_w2t_out_none, _w2t_out_ref)
    )
    and np.array_equal(
        _w2t_m_none.last_buffer_trajectory, _w2t_m_ref.last_buffer_trajectory
    ),
    "a 5 kW burn must fold into the heat-pump tank identically in both, or "
    "a stale probe silently changes the plan",
)
R.check(
    "and reports no wood trajectory at all",
    _w2t_m_none.last_wood_trajectory is None,
    "None rather than a flat line of ambient, so a silent reset is visible",
)


# --- The draw law: wood-while-usable, not hotter-tank-first ---------------

R.check(
    "the wood tank is drawn while it can meet the curve, hotter tank or not",
    _w2t_share(45.0, 55.0, 40.0, 21.0) == 1.0
    and _w2t_share(60.0, 40.0, 45.0, 21.0) == 1.0,
    "the owner's ESBE setting is wood priority; hotter-tank-first would "
    "burn the wood into a full tank and then dump it",
)

# In the blend region the modelled outlet is the curve itself, so the blend
# fraction the model uses must be the one the displacement estimator measures
# at the valve outlet: (t_out - T_hp) / (T_wood - T_hp). One law, two users.
_w2t_blend_ok = True
for _w2t_bw, _w2t_bh, _w2t_bf in (
    (30.0, 55.0, 40.0), (25.0, 60.0, 45.0), (35.0, 50.0, 42.0)
):
    _w2t_measured = (_w2t_bf - _w2t_bh) / (_w2t_bw - _w2t_bh)
    _w2t_derate = (_w2t_bw - 21.0) / (_w2t_bf - 21.0)
    _w2t_blend_ok = _w2t_blend_ok and abs(
        _w2t_share(_w2t_bw, _w2t_bh, _w2t_bf, 21.0)
        - _w2t_measured * _w2t_derate
    ) < 1e-12
R.check(
    "the blend fraction is the one the outlet estimator measures",
    _w2t_blend_ok,
    "external_heat.py infers the wood share from the mixed outlet; if the "
    "model blended by a different rule the two would disagree about the "
    "same burn",
)

R.check(
    "below the curve both tanks fall back to a smooth hotter-source switch",
    _w2t_share(30.0, 35.0, 40.0, 21.0) == 0.0
    and _w2t_share(30.0 + _W2T_MARGIN, 30.0, 40.0, 21.0) == 1.0
    and 0.0 < _w2t_share(31.0, 30.0, 40.0, 21.0) < 1.0,
    "switching hard at equality would chatter the share between steps over "
    "sensor noise, which the estimator already calls unidentifiable there",
)

# Continuity in the delivered quantity, w * Q, across every region boundary:
# a step change there is a step change in emitter heat, which no valve does.
def _w2t_max_jump(values):
    return max(abs(b - a) for a, b in zip(values, values[1:]))


_w2t_step = 0.02
_w2t_flow_sweep = [
    _w2t_share(30.0, 55.0, 25.0 + i * _w2t_step, 21.0)
    * (25.0 + i * _w2t_step - 21.0)
    for i in range(int(35.0 / _w2t_step) + 1)
]
_w2t_wood_sweep = [
    _w2t_share(20.0 + i * _w2t_step, 55.0, 40.0, 21.0) * (40.0 - 21.0)
    for i in range(int(30.0 / _w2t_step) + 1)
]
R.check(
    "sweeping the curve across both boundaries moves the draw smoothly",
    _w2t_max_jump(_w2t_flow_sweep) < 3.0 * _w2t_step,
    f"largest step in w*Q was {_w2t_max_jump(_w2t_flow_sweep):.4f} K for a "
    f"{_w2t_step} K increment",
)
R.check(
    "and so does sweeping the wood tank up through the curve",
    _w2t_max_jump(_w2t_wood_sweep) < 3.0 * _w2t_step,
    f"largest step in w*Q was {_w2t_max_jump(_w2t_wood_sweep):.4f} K for a "
    f"{_w2t_step} K increment",
)


# --- The regression this release exists for -------------------------------
#
# Equal power schedules, hot wood tank, burn versus no burn. The burn must be
# invisible to everything the heat pump is judged by.

_w2t_m_burn, _ = _w2t_run(_w2t_params_two, 60.0, 10.0)
_w2t_m_calm, _ = _w2t_run(_w2t_params_two, 60.0, 0.0)
_w2t_m_old, _ = _w2t_run(_w2t_params_off, None, 10.0)

R.check(
    "a burn charges the wood tank, pointwise",
    np.all(
        _w2t_m_burn.last_wood_trajectory
        >= _w2t_m_calm.last_wood_trajectory - 1e-12
    )
    and _w2t_m_burn.last_wood_trajectory[-1]
    > _w2t_m_calm.last_wood_trajectory[-1] + 1.0,
    f"ends at {_w2t_m_burn.last_wood_trajectory[-1]:.1f} C against "
    f"{_w2t_m_calm.last_wood_trajectory[-1]:.1f} C unburnt",
)
R.check(
    "and takes no cap headroom from the heat pump's tank",
    _w2t_m_burn.last_buffer_refused.max() == 0.0
    and _w2t_m_burn.last_buffer_trajectory.max()
    < _w2t_params_two.buffer_max_temp - 1.0,
    f"HP tank peaked at {_w2t_m_burn.last_buffer_trajectory.max():.1f} C "
    f"against a {_w2t_params_two.buffer_max_temp:.0f} C cap with nothing "
    "refused",
)
R.check(
    "the burn moves load off the heat pump's tank rather than into it",
    _w2t_m_burn.last_buffer_trajectory[-1]
    >= _w2t_m_calm.last_buffer_trajectory[-1] - 1e-9,
    f"HP tank ends {_w2t_m_burn.last_buffer_trajectory[-1]:.1f} C with the "
    f"burn and {_w2t_m_calm.last_buffer_trajectory[-1]:.1f} C without: the "
    "wood side carries the emitters, so the HP tank is drawn less",
)
R.check(
    "which is exactly what the single-tank abstraction could not do",
    _w2t_m_old.last_buffer_trajectory.max()
    > _w2t_m_burn.last_buffer_trajectory.max() + 5.0
    and _w2t_m_old.last_buffer_refused.max() > 0.0,
    f"the same burn put the old model's tank at "
    f"{_w2t_m_old.last_buffer_trajectory.max():.1f} C and had it refuse "
    f"{_w2t_m_old.last_buffer_refused.max():.1f} kW of the pump's own heat",
)
_w2t_cop_model = ThermalModel(_w2t_params_two)
_w2t_cop_two = _w2t_cop_model.compute_cop(
    -5.0, flow_temp=float(_w2t_m_burn.last_buffer_trajectory[-1])
)
_w2t_cop_old = _w2t_cop_model.compute_cop(
    -5.0, flow_temp=float(_w2t_m_old.last_buffer_trajectory[-1])
)
R.check(
    "so wood heat no longer shows up as a heat pump COP penalty",
    _w2t_cop_old < _w2t_cop_two - 0.1,
    f"the abstraction rated the same pump at {_w2t_cop_old:.2f} against "
    f"{_w2t_cop_two:.2f}, purely because the burn was modelled as raising "
    "the flow temperature the pump charges at",
)


# --- Conservation ---------------------------------------------------------
#
# One step in the blend region, where both tanks supply the emitters. The
# balance is recomputed from the same helpers the model uses, and the emitter
# side is cross-checked against the slab's own dynamics so that a starved
# draw cannot pass as a conserved one.

_w2t_p_c = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=500.0,
    mixing_valve_mode=_w2t_mv.MODE_MANUAL, mixing_valve_target=23.0,
    cop_flow_carnot=True, wood_tank_configured=True, wood_tank_volume=500.0,
)
_w2t_m_c = ThermalModel(_w2t_p_c)
_w2t_s0 = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=24.0,
    buffer_tank_temperature=45.0, outdoor_temperature=-15.0,
    wood_tank_temperature=25.0,
)
_w2t_dt, _w2t_pw, _w2t_ext = 0.25, 2.0, 1.0
_w2t_s1 = _w2t_m_c.simulate_step(
    _w2t_s0, _w2t_pw, -15.0, dt_hours=_w2t_dt, external_heat_kw=_w2t_ext
)
_w2t_ua_tot = (
    _w2t_p_c.max_electrical_power
    * max(_w2t_p_c.cop_nominal, 1.0)
    / max(_w2t_p_c.emitter_design_delta_t, 1.0)
)
_w2t_ua_rad = _w2t_p_c.radiator_power_fraction * _w2t_ua_tot
_w2t_ua_floor = (1.0 - _w2t_p_c.radiator_power_fraction) * _w2t_ua_tot
_w2t_fs = _w2t_mv.flow_setpoint(
    target_temp=23.0, outdoor_temp=-15.0,
    heat_loss_coefficient=(
        _w2t_m_c.effective_heat_loss_coefficient(
            _w2t_p_c.upper_floor_heat_loss
        )
        + _w2t_m_c.effective_heat_loss_coefficient(
            _w2t_p_c.lower_floor_heat_loss_learned
        )
    ),
    emitter_ua=_w2t_ua_tot,
)
_w2t_tmix = min(
    max(_w2t_s0.wood_tank_temperature, _w2t_s0.buffer_tank_temperature),
    _w2t_fs,
)
_w2t_q_rad = _w2t_mv.emitter_delivery(
    mix_temp=_w2t_tmix,
    zone_temp=_w2t_s0.upper_floor_temperature,
    ua=_w2t_ua_rad,
)
_w2t_q_floor = _w2t_mv.emitter_delivery(
    mix_temp=_w2t_tmix, zone_temp=_w2t_s0.slab_temperature, ua=_w2t_ua_floor
)
_w2t_q_floor_seen = (
    _w2t_p_c.slab_thermal_mass
    * (_w2t_s1.slab_temperature - _w2t_s0.slab_temperature)
    / _w2t_dt
    + _w2t_p_c.slab_heat_transfer
    * (_w2t_s0.slab_temperature - _w2t_s0.lower_floor_temperature)
)
_w2t_store = (
    _w2t_p_c.wood_tank_thermal_mass
    * (_w2t_s1.wood_tank_temperature - _w2t_s0.wood_tank_temperature)
    + _w2t_p_c.buffer_tank_thermal_mass
    * (_w2t_s1.buffer_tank_temperature - _w2t_s0.buffer_tank_temperature)
) / _w2t_dt
_w2t_residual = (
    _w2t_store
    + _w2t_p_c.wood_tank_heat_loss_coefficient
    * (_w2t_s0.wood_tank_temperature - 20.0)
    + _w2t_p_c.buffer_tank_heat_loss_coefficient
    * (_w2t_s0.buffer_tank_temperature - 20.0)
    + _w2t_q_rad
    + _w2t_q_floor
    - _w2t_m_c.compute_cop(-15.0, flow_temp=_w2t_s0.buffer_tank_temperature)
    * _w2t_pw
    - _w2t_ext
)
R.check(
    "the emitters got what the valve outlet says they got",
    abs(_w2t_q_floor - _w2t_q_floor_seen) < 1e-9 and _w2t_q_floor > 0.1,
    f"recomputed {_w2t_q_floor:.4f} kW into the slab against "
    f"{_w2t_q_floor_seen:.4f} kW the slab's own dynamics show; a starved "
    "draw would show up here as a gap",
)
R.check(
    "and one two-tank step balances to the last bit",
    abs(_w2t_residual) < 1e-9
    and _w2t_s1.wood_tank_temperature < _w2t_s0.wood_tank_temperature,
    f"stored + lost + delivered - (COP*P + burn) = {_w2t_residual:.3e} kW, "
    "with the wood tank supplying its share of the blend",
)


# --- Step length ----------------------------------------------------------

_w2t_m_q, _ = _w2t_run(_w2t_params_two, 60.0, 3.0, n=24, dt=0.25)
_w2t_m_f, _ = _w2t_run(_w2t_params_two, 60.0, 3.0, n=72, dt=1.0 / 12.0)
R.check(
    "six hours of two-tank operation does not depend on the step length",
    abs(
        _w2t_m_q.last_wood_trajectory[-1] - _w2t_m_f.last_wood_trajectory[-1]
    ) < 0.5
    and abs(
        _w2t_m_q.last_buffer_trajectory[-1]
        - _w2t_m_f.last_buffer_trajectory[-1]
    ) < 0.5,
    f"wood ends {_w2t_m_q.last_wood_trajectory[-1]:.2f} C at 15 min vs "
    f"{_w2t_m_f.last_wood_trajectory[-1]:.2f} C at 5 min",
)


# --- A tiny wood tank -----------------------------------------------------
#
# The per-tank availability bound is the 10 L buffer fix generalized: each
# tank is judged against its own contents. Unbounded, a 10 L store against a
# 40 K flow-to-room difference overshoots its Euler step and goes negative.

_w2t_m_tiny, _w2t_out_tiny = _w2t_run(
    ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=500.0,
        mixing_valve_mode=_w2t_mv.MODE_MANUAL, mixing_valve_target=21.0,
        cop_flow_carnot=True, wood_tank_configured=True, wood_tank_volume=10.0,
    ),
    60.0, 0.0, n=48, power=0.0,
)
_w2t_wood_tiny = _w2t_m_tiny.last_wood_trajectory
# The floor each step is judged against is the coldest zone it feeds, or the
# 20 C room the tank stands in once the zones fall below that: standby loss
# to a warmer room is not a draw, and the availability bound does not (and
# must not) stop it.
_w2t_floors = np.minimum(
    np.minimum(_w2t_out_tiny[2][:-1], _w2t_out_tiny[1][:-1]), 20.0
)
R.check(
    "a 10 L wood tank cannot discharge below what it is feeding",
    np.all(_w2t_wood_tiny[1:] >= _w2t_floors - 1e-9),
    f"12 h of coasting left the wood tank at {_w2t_wood_tiny.min():.2f} C; "
    f"the shallowest margin over its floor was "
    f"{float(np.min(_w2t_wood_tiny[1:] - _w2t_floors)):.3f} K",
)
R.check(
    "and it empties into the house rather than through zero",
    _w2t_wood_tiny.min() > 15.0 and _w2t_wood_tiny[1] < 30.0,
    f"the first 15-minute step took it from 60 C to "
    f"{_w2t_wood_tiny[1]:.1f} C -- everything it had above the zones -- and "
    "no further; unbounded, the same bug took a 10 L buffer to -8.04 C",
)


# --- Null control ---------------------------------------------------------
#
# A wood tank colder than everything it could feed is not a feature: with no
# burn it must be indistinguishable from having no wood tank at all. Without
# this the arms above could be measuring the second branch rather than the
# second tank.

_w2t_m_cold, _w2t_out_cold = _w2t_run(_w2t_params_two, 15.0, 0.0)
_w2t_m_flat, _w2t_out_flat = _w2t_run(_w2t_params_off, None, 0.0)
R.check(
    "a cold wood tank and no burn is byte-identical to no wood tank",
    all(
        np.array_equal(a, b)
        for a, b in zip(_w2t_out_cold, _w2t_out_flat)
    )
    and np.array_equal(
        _w2t_m_cold.last_buffer_trajectory, _w2t_m_flat.last_buffer_trajectory
    ),
    "the share is zero, the supply is the HP tank either way, and the two "
    "branches must agree exactly there -- not to within a tolerance",
)
R.check(
    "and the cold tank only drifts towards the room it stands in",
    _w2t_m_cold.last_wood_trajectory[-1] > 15.0
    and _w2t_m_cold.last_wood_trajectory[-1] < 20.0,
    f"ended at {_w2t_m_cold.last_wood_trajectory[-1]:.2f} C from 15 C, on "
    "standby loss alone",
)


R.section("DHW refill coil in the wood tank (v3.15.1)")

from heatpump_optimizer.thermal_model import dhw_coil_draw_reduction as _coil

# The reduction and the coil heat are one identity: what the electric side
# no longer buys is exactly what left the wood tank.
for _draw, _tw, _sp in ((2.0, 70.0, 55.0), (1.3, 25.0, 55.0), (0.7, 95.0, 50.0)):
    _red, _q = _coil(_draw, _tw, _sp)
    R.check(
        f"coil identity holds at T_w={_tw:.0f}",
        _red + _q == _draw and 0.0 <= _red <= _draw,
        f"reduced {_red} + coil {_q} != draw {_draw}",
    )
_red_cold, _q_cold = _coil(2.0, 10.0, 55.0)
R.check(
    "mains-temperature wood gives no preheat",
    _red_cold == 2.0 and _q_cold == 0.0,
    "a 10 C tank cannot warm 10 C water",
)
_red_hot, _q_hot = _coil(2.0, 70.0, 55.0)
R.check(
    "a 70 C tank at a 55 C setpoint covers two thirds of the draw",
    abs(_q_hot - 2.0 * (30.0 / 45.0)) < 1e-12,
    f"t_in = 10 + 0.5*60 = 40, so coil covers (40-10)/(55-10): got {_q_hot}",
)

_coil_cfg = dict(
    upper_floor_thermal_mass=2.0,
    mixing_valve_mode="manual",
    wood_tank_top_entity="sensor.wood_top",
    dhw_tank_volume=200.0,
    dhw_wood_coil_enabled=True,
)
_p_coil = ThermalParameters.from_config(_coil_cfg)
R.check(
    "the coil activates only on the full stack",
    _p_coil.dhw_coil_active
    and not ThermalParameters.from_config(
        {**_coil_cfg, "dhw_wood_coil_enabled": False}
    ).dhw_coil_active
    and not ThermalParameters.from_config(
        {k: v for k, v in _coil_cfg.items() if k != "wood_tank_top_entity"}
    ).dhw_coil_active,
    "option + hot water + two-tank model, each necessary",
)

def _coil_run(params, wood):
    m = ThermalModel(params)
    s = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=45.0, dhw_temperature=50.0,
        outdoor_temperature=-5.0, wood_tank_temperature=wood,
    )
    n = 24
    out = m.simulate_trajectory_with_dhw(
        s, np.full(n, 0.5), np.zeros(n), np.full(n, -5.0),
        start_hour=6.0, dt_hours=0.25,
    )
    return m, out

_p_nocoil = ThermalParameters.from_config(
    {**_coil_cfg, "dhw_wood_coil_enabled": False}
)
_m_on, _out_on = _coil_run(_p_coil, 70.0)
_m_off, _out_off = _coil_run(_p_nocoil, 70.0)
R.check(
    "the coil keeps the hot water warmer on the same schedule",
    float(_out_on[4][-1]) > float(_out_off[4][-1]),
    f"dhw ended {_out_on[4][-1]:.2f} with coil vs {_out_off[4][-1]:.2f} "
    "without: preheated refill water draws less from the tank",
)
R.check(
    "and the preheat genuinely comes out of the wood tank",
    float(_m_on.last_wood_trajectory[-1])
    < float(_m_off.last_wood_trajectory[-1]),
    f"wood ended {_m_on.last_wood_trajectory[-1]:.2f} with the coil vs "
    f"{_m_off.last_wood_trajectory[-1]:.2f} without",
)
_m_flag, _out_flag = _coil_run(_p_coil, None)
_m_ref2, _out_ref2 = _coil_run(_p_nocoil, None)
R.check(
    "an unsensed wood tank disables the coil byte-identically",
    all(np.array_equal(a, b) for a, b in zip(_out_flag, _out_ref2)),
    "no probe means no preheat claim, exactly the two-tank rule",
)


R.section("Topology catalog and the layout editor's contract (v3.16.0)")

from heatpump_optimizer.topology import (
    LAYOUTS as _LAYOUTS,
    layout_edges as _layout_edges,
    match_layout as _match_layout,
)

# Every layout's composed edge set must match only itself, under every flag
# combination the catalog can meet -- two layouts with one signature would
# let the editor store a key the drawing did not show.
_sig_ok = True
for _tz, _wd in ((True, True), (True, False), (False, True), (False, False)):
    _sets = {}
    for _key in _LAYOUTS:
        _sets[_key] = frozenset(
            _layout_edges(_key, two_zone=_tz, wood=_wd)
        )
    _vals = list(_sets.values())
    if len(set(_vals)) != len(_vals):
        # Collisions are acceptable only between layouts that cannot both
        # exist under these flags (e.g. one-zone collapses the slab
        # variants onto single_tank_valve's shape).
        for _a in _sets:
            for _b in _sets:
                if _a < _b and _sets[_a] == _sets[_b]:
                    _sig_ok = _sig_ok and not (_tz or _a == _b)
R.check(
    "every two-zone layout signature matches only itself",
    _sig_ok
    and all(
        _match_layout(
            _layout_edges(_key, two_zone=True, wood=(
                _key == "two_tank_4way"
            )), two_zone=True, wood=(_key == "two_tank_4way"),
        )[0] == _key
        for _key in _LAYOUTS
        if _LAYOUTS[_key].selectable
    ),
    "the editor stores whichever key the edge set snaps to; a collision "
    "stores the wrong physics",
)
_ss_key, _ss_why = _match_layout(
    _layout_edges("slab_shunt", two_zone=True, wood=False),
    two_zone=True, wood=False,
)
R.check(
    "a drawn slab shunt is recognized and refused, with the reason",
    _ss_key is None and "not modelled" in _ss_why,
    f"got {_ss_key!r}: {_ss_why}",
)
# The pre-v3.14.1 drawing (valve to the radiators, slab fed direct from
# the tank) is not a mistake the catalog rejects -- it is a real layout it
# recognizes. This is the design working: some houses have it. The wood
# chain is tank-to-tank since v4.0.0: the separate wood-valve box modelled
# nothing and was removed (#40 feedback, item 3).
_old_drawing = [
    ["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
    ["mixing_valve", "upper_zone"], ["buffer_tank", "lower_zone"],
    ["wood_tank", "buffer_tank"],
]
R.check(
    "the old drawing is recognized as the layout it always depicted",
    _match_layout(_old_drawing, two_zone=True, wood=True)[0]
    == "valve_upper_direct_slab",
    "valve on the radiators, slab fed direct: a supported layout, not an "
    "error",
)
# A drawing carrying the removed wood-valve hop no longer matches anything,
# but the rejection must still explain itself rather than crash or claim an
# empty diff.
_wv_key, _wv_why = _match_layout(
    _old_drawing[:-1]
    + [["wood_tank", "wood_valve"], ["wood_valve", "buffer_tank"]],
    two_zone=True, wood=True,
)
R.check(
    "the removed wood-valve chain degrades to a named nearest layout",
    _wv_key is None and "Closest supported layout" in _wv_why,
    f"got {_wv_key!r}: {_wv_why}",
)
_wrong = [["heat_pump", "buffer_tank"], ["buffer_tank", "mixing_valve"],
          ["mixing_valve", "upper_zone"], ["mixing_valve", "lower_zone"],
          ["buffer_tank", "lower_zone"]]
_wk, _wwhy = _match_layout(_wrong, two_zone=True, wood=False)
R.check(
    "a genuinely unsupported set names the nearest layout and the diff",
    _wk is None and "Closest supported layout" in _wwhy
    and ("Missing" in _wwhy or "Not in it" in _wwhy),
    f"got {_wk!r}: {_wwhy}",
)

# 750 L, not the tiny default: the per-step availability bound must not be
# what limits delivery here, or both slab variants drain the same energy
# and the drain-rate contrast below measures the bound instead of the pipe.
_vud_cfg = {
    "upper_floor_thermal_mass": 2.0,
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    "topology_layout": "valve_upper_direct_slab",
}
_p_vud = ThermalParameters.from_config(_vud_cfg)
R.check(
    "a stored layout wins while it is honest",
    _p_vud.topology_layout == "valve_upper_direct_slab"
    and _p_vud.slab_fed_direct
    and not _p_vud.two_tank_modelled,
    "valve + two zones + no probe can store the direct-slab layout",
)
R.check(
    "and falls back to the derived default when it stops being honest",
    ThermalParameters.from_config(
        {**_vud_cfg, "wood_tank_top_entity": "sensor.w"}
    ).topology_layout == "two_tank_4way"
    and ThermalParameters.from_config(
        {**_vud_cfg, "topology_layout": "no_such_layout"}
    ).topology_layout == "single_tank_valve",
    "a probe invalidates direct-slab; an unknown key is dropped entirely",
)
R.check(
    "storing single_tank_valve is the two-tank model's off switch",
    not ThermalParameters.from_config(
        {
            **_vud_cfg,
            "wood_tank_top_entity": "sensor.w",
            "topology_layout": "single_tank_valve",
        }
    ).two_tank_modelled,
    "a user may deliberately opt out of the two-tank physics",
)

# The direct-slab physics: the slab drinks raw tank water, so with the tank
# above the curve it receives more heat than the valved slab would -- and
# with the override absent the step is byte-identical to v3.15.1.
def _vud_run(cfg):
    m = ThermalModel(ThermalParameters.from_config(cfg))
    s = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=60.0, outdoor_temperature=-5.0,
    )
    out = m.simulate_trajectory(
        s, np.full(8, 1.0), np.full(8, -5.0), dt_hours=0.25
    )
    return m, out

_m_vud, _out_vud = _vud_run(_vud_cfg)
_m_valved, _out_valved = _vud_run(
    {k: v for k, v in _vud_cfg.items() if k != "topology_layout"}
)
R.check(
    "a direct-fed slab takes more heat from a hot tank than a valved one",
    float(_out_vud[1][-1]) > float(_out_valved[1][-1]),
    f"slab reached {_out_vud[1][-1]:.2f} direct vs {_out_valved[1][-1]:.2f} "
    "behind the valve, from a 60 C tank",
)
R.check(
    "and the tank pays for it",
    float(_m_vud.last_buffer_trajectory[-1])
    < float(_m_valved.last_buffer_trajectory[-1]),
    "raw tank water to the slab must drain the tank faster",
)
_m_a, _out_a2 = _vud_run(
    {k: v for k, v in _vud_cfg.items() if k != "topology_layout"}
)
R.check(
    "no stored layout means byte-identical v3.15.1 behaviour",
    all(np.array_equal(a, b) for a, b in zip(_out_valved, _out_a2))
    and np.array_equal(
        _m_valved.last_buffer_trajectory, _m_a.last_buffer_trajectory
    ),
    "the editor's absence is exactly the previous release",
)

_ds = _topo.describe_setup(_vud_cfg)
R.check(
    "describe_setup ships the active edges and the catalog",
    _ds["layout"] == "valve_upper_direct_slab"
    and sorted(map(tuple, _ds["edges"]))
    == sorted(_layout_edges(
        "valve_upper_direct_slab", two_zone=True, wood=False))
    and {c["key"] for c in _ds["catalog"]} == set(_LAYOUTS)
    and all(
        set(c) >= {"key", "label", "selectable", "valid", "edges",
                   "requirement"}
        for c in _ds["catalog"]
    )
    and not next(
        c for c in _ds["catalog"] if c["key"] == "slab_shunt"
    )["valid"],
    "the card draws topo.edges and the editor matches against topo.catalog "
    "-- both derived here, never in the frontend",
)

# Every catalog entry ships its requirement text (#40 feedback, item 5): the
# card renders "<label> — needs <requirement>" when a drawing matches a
# layout the configuration cannot store, and the missing field is what made
# that message read "needs undefined" at the exact moment it was supposed to
# say what to configure.
R.check(
    "every catalog entry carries a non-empty requirement",
    all(
        isinstance(c.get("requirement"), str) and c["requirement"]
        for c in _ds["catalog"]
    ),
    str([(c["key"], c.get("requirement")) for c in _ds["catalog"]]),
)

# The arrangement from the user's #40 report: a 4-way valve, two tanks and
# hot water, with the refill coil OFF. It must be storable, its drawn edge
# set must snap to two_tank_4way, and the diagram must show the heat pump
# feeding the hot water tank (#40 item 2) — coil or no coil.
_u_cfg = dict(_full_cfg)  # two-zone + manual valve + wood probe + dhw
_u = _topo.describe_setup(_u_cfg)
_u_entry = next(c for c in _u["catalog"] if c["key"] == "two_tank_4way")
R.check(
    "4-way + two tanks + hot water, coil off, is valid and matches",
    _u_entry["valid"]
    and _u["layout"] == "two_tank_4way"
    and _match_layout(
        _u["edges"], two_zone=True, wood=True, dhw_coil=False, dhw=True
    )[0] == "two_tank_4way",
    "the user's report said this could not be saved; the message was the "
    "bug, the arrangement itself is supported",
)
R.check(
    "the heat pump visibly feeds the hot water tank, coil or no coil",
    ["heat_pump", "dhw_tank"] in _u["edges"]
    and ["heat_pump", "dhw_tank"]
    in _topo.describe_setup(
        {**_u_cfg, "dhw_wood_coil_enabled": True}
    )["edges"],
    "the DHW tank floated unconnected in every drawing (#40 item 2)",
)
R.check(
    "and no hot-water pipe is drawn for a house without hot water",
    ["heat_pump", "dhw_tank"]
    not in _topo.describe_setup(
        {k: v for k, v in _u_cfg.items() if k != "dhw_tank_volume"}
    )["edges"],
)
# Without the probe the same drawing is recognized but not storable, and the
# requirement text names exactly what is missing — the actionable message
# the user should have seen.
_np_cfg = {k: v for k, v in _u_cfg.items() if k != "wood_tank_top_entity"}
_np = _topo.describe_setup(_np_cfg)
_np_entry = next(c for c in _np["catalog"] if c["key"] == "two_tank_4way")
R.check(
    "without the probe the entry is invalid and the requirement says why",
    not _np_entry["valid"] and "wood-tank top probe" in _np_entry["requirement"],
    f"got valid={_np_entry['valid']} requirement={_np_entry.get('requirement')!r}",
)

# The wood-valve box is gone (#40 item 3): no slot and no edge references
# the place. The outlet probe's slot sits on the 4-way valve in the two-tank
# layout and on the wood tank in the single-tank abstraction.
_wv_places_two_tank = {
    s["place"] for s in _u["slots"] if s["key"] == "valve_outlet_temp_entity"
}
_single_wood = _topo.describe_setup(
    {k: v for k, v in _u_cfg.items() if k != "wood_tank_top_entity"}
    | {"external_heat_detection_enabled": True}
)
_wv_places_single = {
    s["place"]
    for s in _single_wood["slots"]
    if s["key"] == "valve_outlet_temp_entity"
}
R.check(
    "the wood valve is a slot on a real device, not a box of its own",
    _wv_places_two_tank == {"mixing_valve"}
    and _wv_places_single == {"wood_tank"}
    and all("wood_valve" not in e for e in _u["edges"])
    and all(
        "wood_valve" not in e for c in _u["catalog"] for e in c["edges"]
    ),
    f"two-tank {_wv_places_two_tank}, single {_wv_places_single}",
)
R.check(
    "positions pass through untouched and default empty",
    _ds["positions"] == {}
    and _topo.describe_setup(
        {**_vud_cfg, "topology_positions": {"buffer_tank": [10, 20]}}
    )["positions"] == {"buffer_tank": [10, 20]},
    "cosmetic only, but they must survive the round trip",
)


R.section("T1 — the bill beyond spot (#1 #13 #19 #34 #23)")

from heatpump_optimizer import grid_fee as _gf
from heatpump_optimizer.ledger import MonthlyLedger as _Ledger
from heatpump_optimizer.price_model import (
    PriceShapeModel as _PSM,
    hourly_from_entries as _hourly,
    quarters_from_entries as _quarters,
)
from heatpump_optimizer.tariff import (
    CapacityTariff as _CT,
    PeakTracker as _PT,
    peak_cost as _peak_cost,
    window_factors as _wfactors,
    metering_windows as _mwindows,
)

# --- #1: the fee rule grammar ------------------------------------------------
_rules = _gf.parse_rules("Nov-Mar Mon-Fri 06:00-22:00 = 0.25, Jul = 0.10")
_sched = _gf.GridFeeSchedule(mode=_gf.MODE_RULES, fixed=0.05, rules=_rules)
_winter_day = datetime(2026, 1, 14, 10, 0)   # a Wednesday in January
_winter_night = datetime(2026, 1, 14, 23, 0)
_winter_sat = datetime(2026, 1, 17, 10, 0)   # Saturday
_july_noon = datetime(2026, 7, 14, 12, 0)
R.check(
    "a höglast rule bills winter weekday daytime and nothing else",
    abs(_sched.current_fee(_winter_day) - 0.30) < 1e-9
    and abs(_sched.current_fee(_winter_night) - 0.05) < 1e-9
    and abs(_sched.current_fee(_winter_sat) - 0.05) < 1e-9
    and abs(_sched.current_fee(_july_noon) - 0.15) < 1e-9,
    f"day {_sched.current_fee(_winter_day)}, night {_sched.current_fee(_winter_night)}, "
    f"sat {_sched.current_fee(_winter_sat)}, july {_sched.current_fee(_july_noon)}",
)
R.check(
    "overlapping rules add, matching base fee plus surcharge tariffs",
    abs(
        _gf.GridFeeSchedule(
            mode=_gf.MODE_RULES,
            rules=_gf.parse_rules("= 0.10, Mon-Fri = 0.20"),
        ).current_fee(_winter_day)
        - 0.30
    )
    < 1e-9,
)
R.check(
    "Swedish month and weekday spellings parse",
    _gf.is_valid_spec("Maj Mån-Fre 06:00-22:00 = 0.2")
    and _gf.is_valid_spec("Okt-Dec Lör-Sön = 0.1"),
)
R.check(
    "a wrapping month range covers the wrap and not the middle",
    2 in _gf.parse_month_range("Nov-Mar") and 6 not in _gf.parse_month_range("Nov-Mar"),
)
R.check(
    "broken specs are rejected by validation, not stored",
    not _gf.is_valid_spec("Nov-Mar = banana")
    and not _gf.is_valid_spec("Frunday = 0.2")
    and not _gf.is_valid_spec("06:00-22:00"),
)
R.check(
    "mode none is a sentinel: zero vector and inactive, whatever else is set",
    not _gf.GridFeeSchedule(mode=_gf.MODE_NONE, fixed=9.9, rules=_rules).active
    and float(
        np.sum(
            _gf.GridFeeSchedule(mode=_gf.MODE_NONE, fixed=9.9, rules=_rules)
            .fee_vector([_winter_day, _winter_night])
        )
    )
    == 0.0,
    "an untouched install must price exactly as before",
)
_ent = _gf.GridFeeSchedule(mode=_gf.MODE_ENTITY, fixed=0.1)
R.check(
    "entity mode holds the live value flat across the horizon",
    np.allclose(_ent.fee_vector([_winter_day, _july_noon], 0.4), 0.5)
    and abs(_ent.current_fee(_winter_day, None) - 0.1) < 1e-9,
)

# --- #13: masks on the capacity tariff ---------------------------------------
_flat_ct = _CT(enabled=True, price_per_kw=30.0)
_masked_ct = _CT(
    enabled=True, price_per_kw=30.0,
    months=frozenset({11, 12, 1, 2, 3}),
    peak_hours=(( 7.0, 19.0),),
    weekdays_only=True,
    offpeak_factor=0.5,
)
R.check(
    "with no masks every hour counts in full, exactly the old model",
    _flat_ct.sample_factor(_winter_night) == 1.0
    and _flat_ct.sample_factor(_july_noon) == 1.0,
)
R.check(
    "masked months contribute nothing, off-peak hours count at the factor",
    _masked_ct.sample_factor(_july_noon) == 0.0
    and _masked_ct.sample_factor(_winter_night) == 0.5
    and _masked_ct.sample_factor(_winter_sat) == 0.5
    and _masked_ct.sample_factor(_winter_day) == 1.0,
)
_pt_masked = _PT()
for _h in range(3):
    _pt_masked.observe(_july_noon.replace(hour=10 + _h), 8.0, _masked_ct)
_pt_masked.observe(_july_noon.replace(hour=13), 8.0, _masked_ct)  # closes last
R.check(
    "a July window under a Nov-Mar tariff is not recorded at all",
    _pt_masked.peaks == [] and _pt_masked.threshold_kw(_masked_ct) == float("inf"),
    "recording a zero would poison the early-month threshold",
)
_pt_night = _PT()
_pt_night.observe(_winter_night, 8.0, _masked_ct)
_pt_night.observe(_winter_night.replace(hour=23, minute=30), 8.0, _masked_ct)
_pt_night.observe(datetime(2026, 1, 15, 0, 0), 8.0, _masked_ct)  # closes 23:00
R.check(
    "a half-rate night window is recorded at half its kW",
    len(_pt_night.peaks) == 1 and abs(_pt_night.peaks[0] - 4.0) < 1e-9,
    f"peaks {_pt_night.peaks}",
)
_pt_flat = _PT()
_pt_flat.observe(_winter_night, 8.0, _flat_ct)
_pt_flat.observe(datetime(2026, 1, 15, 0, 0), 8.0, _flat_ct)
R.check(
    "unmasked observation is bit-identical to the old tracker",
    _pt_flat.peaks == [8.0],
)
_power = np.zeros(96)
_power[92:96] = 6.0  # a 23:00 burst on a day starting at midnight
_day_start = datetime(2026, 1, 14, 0, 0)
_nf = _wfactors(_masked_ct, _day_start, _mwindows(_power, 60, 0.25).size, 0.25)
_cost_masked = _peak_cost(_power, np.zeros(96), 1.0, 10.0, 60, 0.25, 3,
                          window_factors=_nf)
_cost_flat = _peak_cost(_power, np.zeros(96), 1.0, 10.0, 60, 0.25, 3)
R.check(
    "the plan's peak term prices a night burst at the off-peak rate",
    0.0 < _cost_masked < _cost_flat
    and _wfactors(_flat_ct, _day_start, 24, 0.25) is None,
    f"masked {_cost_masked}, flat {_cost_flat}",
)
_ct_free_night = _CT(enabled=True, price_per_kw=30.0, peak_hours=((7.0, 19.0),),
                     offpeak_factor=0.0)
R.check(
    "free off-peak hours make a night burst cost nothing in capacity",
    _peak_cost(_power, np.zeros(96), 1.0, 10.0, 60, 0.25, 3,
               window_factors=_wfactors(
                   _ct_free_night, _day_start,
                   _mwindows(_power, 60, 0.25).size, 0.25)) == 0.0,
)
_pt_round = _PT.from_dict(_pt_night.as_dict())
R.check(
    "the tracker's window factor survives the round trip, and old payloads "
    "default to 1.0",
    _pt_round._window_factor == _pt_night._window_factor
    and _PT.from_dict({"month": "2026-01", "peaks": [5.0]})._window_factor == 1.0,
)

# --- #19: the quarter refinement ----------------------------------------------
_q_entries = [
    {
        "starts_at": f"2026-01-12T{h:02d}:{m:02d}:00",
        "total": 1.0 + h * 0.01 + (0.2 if m == 45 else 0.0),
    }
    for h in range(24)
    for m in (0, 15, 30, 45)
]
_h_days = _hourly(_q_entries)
R.check(
    "quarter entries train the hourly shape on the hour's mean, not on :45",
    "2026-01-12" in _h_days
    and abs(_h_days["2026-01-12"][0] - 1.05) < 1e-9,
    "assigning quarters to one slot per hour trained on whichever came last",
)
_q_days = _quarters(_q_entries)
R.check(
    "a full 15-minute day qualifies for quarter learning, an hourly one not",
    "2026-01-12" in _q_days and len(_q_days["2026-01-12"]) == 96
    and not _quarters(
        [{"starts_at": f"2026-01-12T{h:02d}:00:00", "total": 1.0} for h in range(24)]
    ),
)
_psm = _PSM()
_monday = datetime(2026, 1, 12, 12, 0)
R.check(
    "with no quarter evidence the 96-bin model collapses onto the 24-bin one",
    _psm.quarter_factor(_monday.replace(minute=45)) == 1.0
    and _psm.predict(_monday, 1.0) == _PSM().predict(_monday, 1.0),
)
for _ in range(6):
    _psm.observe_day(_monday, [1.0] * 24)
    _psm.observe_day_quarters(_monday, _q_days["2026-01-12"])
_qpred = [
    _psm.predict(_monday.replace(hour=6, minute=m), 1.0) for m in (0, 15, 30, 45)
]
R.check(
    "learned quarter structure moves the :45 quarter above its siblings",
    _qpred[3] > _qpred[0] and _qpred[3] > _qpred[1],
    f"quarter predictions {_qpred}",
)
R.check(
    "and the hour's mean is preserved: the refinement splits, never shifts",
    abs(float(np.mean(_qpred)) - _psm.predict(_monday.replace(hour=6), 1.0)
        / _psm.quarter_factor(_monday.replace(hour=6, minute=0))) < 0.05,
)
# The renormalization is only load-bearing when clipping breaks the natural
# mean — so feed it a spiked quarter far beyond the clip ceiling and require
# the hour's four factors to still average 1.0. Without the post-EWMA
# renormalization this hour would learn a level shift, not a split.
_spiked = [1.0] * 96
_spiked[24:28] = [0.2, 0.2, 0.2, 20.0]  # hour 6: one quarter at 34x its mean
_psm_clip = _PSM()
for _ in range(3):
    _psm_clip.observe_day_quarters(_monday, _spiked)
_h6 = _psm_clip.quarter_factors[0][24:28]
R.check(
    "a clipped quarter still leaves its hour's factors at mean 1.0",
    abs(float(np.mean(_h6)) - 1.0) < 1e-6 and max(_h6) < 4.5,
    f"hour-6 factors {_h6}",
)
_old_payload = {"shapes": [[1.1] * 24, [0.9] * 24], "days": [7, 7]}
_loaded = _PSM.from_dict(_old_payload)
R.check(
    "a pre-v4 store loads into exactly the behaviour it had",
    _loaded.quarter_days == [0, 0]
    and _loaded.quarter_factor(_monday) == 1.0
    and _loaded.sigma(_monday, 1.0) == 0.0
    and _loaded.shapes[0][0] == 1.1,
    "the silent-fallback loader must never discard learned state",
)

# --- #34: risk-adjusted pricing on the guessed tail ---------------------------
_steps_34 = [datetime(2026, 1, 12, 0, 0) + timedelta(minutes=15 * i) for i in range(96)]
_p34, _m34, _s34 = extend_price_series([1.0] * 48, 96, _steps_34, _psm)
R.check(
    "sigma is zero on every published step",
    float(np.sum(_s34[:48])) == 0.0,
)
_vol = _PSM()
for _i in range(10):
    # Alternate the SHAPE day to day — cheap nights one day, cheap days the
    # next — so the learned mean converges near flat while the per-hour
    # dispersion stays large: exactly the prior a trough-chaser overrates.
    # (A flat day at a different level carries no shape risk at all: the
    # level calibration owns that, and normalisation removes it here.)
    _shape = (
        [0.5] * 12 + [1.5] * 12 if _i % 2 else [1.5] * 12 + [0.5] * 12
    )
    _vol.observe_day(_monday, _shape)
_pv_, _mv_, _sv_ = extend_price_series([1.0] * 48, 96, _steps_34, _vol)
R.check(
    "a prior that has been wrong carries real sigma on guessed steps",
    float(np.min(_sv_[48:])) > 0.05,
    f"min sigma {float(np.min(_sv_[48:]))}",
)

# --- #23 + ledger arithmetic ---------------------------------------------------
_led = _Ledger()
_jan = datetime(2026, 1, 10, 8, 0)
for _kwh, _spot in ((2.0, 0.50), (1.0, 2.00), (1.0, 0.50)):
    _led.add(_jan, "spot", kwh=_kwh, sek=_kwh * _spot)
for _sample in (0.50, 2.00, 0.50, 1.00):
    _led.observe_meta_mean(_jan, "spot_price", _sample)
_line = _led.line("2026-01", "spot")
R.check(
    "the ledger's month adds up to the hand-computed bill",
    abs(_line["kwh"] - 4.0) < 1e-9 and abs(_line["sek"] - 3.5) < 1e-9
    and abs(_led.meta_mean("2026-01", "spot_price") - 1.0) < 1e-9,
    f"line {_line}",
)
# Hand-check of the contract columns' arithmetic: 4 kWh at hourly spot cost
# 3.50; the same 4 kWh at the month's 1.00 mean costs 4.00 — the shifting
# earned 0.125 SEK/kWh below the flat-consumer average.
R.check(
    "the load-profile value is the öre/kWh below the flat average",
    abs((_led.meta_mean("2026-01", "spot_price")
         - _line["sek"] / _line["kwh"]) - 0.125) < 1e-9,
)
for _m in range(30):
    _led.add(datetime(2020, 1, 1, 0, 0) + timedelta(days=31 * _m), "spot",
             kwh=1.0, sek=1.0)
R.check(
    "the ledger prunes itself to two years of months",
    len(_led.months) <= 24,
    f"{len(_led.months)} months kept",
)
R.check(
    "a garbage ledger payload loads as empty rather than raising",
    _Ledger.from_dict({"months": "nonsense"}).months == {}
    and _Ledger.from_dict(None).months == {},
)

# --- #34 at the solver: λ=0 is byte-identity, λ>0 pulls load off the guess ----
from golden import make as _mk_golden, START as _G_START

_rk = _mk_golden(hours=24)
_rk_n = len(_rk["prices"])
_rk_known = np.zeros(_rk_n, dtype=bool)
_rk_known[: int(_rk_n * 0.4)] = True
_rk_sigma = np.where(_rk_known, 0.0, 1.0)

def _rk_solve(lam, sigma):
    _rk["optimizer"].config.price_risk_lambda = lam
    return _rk["optimizer"].optimize(
        _rk["state"], _rk["prices"], _rk["outdoor"], _rk["wind"],
        _rk["rain"], _rk["solar"], _G_START,
        price_known=_rk_known, price_sigma=sigma,
    )

_rk_none = _rk_solve(0.0, None)
_rk_zero = _rk_solve(0.0, _rk_sigma)
R.check(
    "λ=0 with a sigma vector present is byte-identical to no sigma at all",
    np.array_equal(
        np.asarray(_rk_none.power_schedule), np.asarray(_rk_zero.power_schedule)
    )
    and np.array_equal(
        np.asarray(_rk_none.dhw_power_schedule),
        np.asarray(_rk_zero.dhw_power_schedule),
    ),
    "the default must not move a single step",
)
_rk_on = _rk_solve(1.0, _rk_sigma)
_unknown = ~_rk_known
_e0 = float(np.sum(np.asarray(_rk_zero.power_schedule)[_unknown])) + float(
    np.sum(np.asarray(_rk_zero.dhw_power_schedule)[_unknown])
)
_e1 = float(np.sum(np.asarray(_rk_on.power_schedule)[_unknown])) + float(
    np.sum(np.asarray(_rk_on.dhw_power_schedule)[_unknown])
)
R.check(
    "a risk premium moves energy off the guessed tail, never onto it",
    _e1 <= _e0 + 1e-6
    and not np.array_equal(
        np.asarray(_rk_on.power_schedule), np.asarray(_rk_zero.power_schedule)
    ),
    f"unknown-step energy {_e0:.2f} -> {_e1:.2f} kW-steps",
)

# --- #1 null control and directional shift at the solver -----------------------
# A fee with no time structure cannot create time-shifting: a uniform price
# rise may legitimately buy a little less energy overall (it trades against
# the comfort weight — measured at ~3.5% on the flat-price day, which is why
# this is deliberately NOT a byte-identity check), but the SHARE of energy
# placed in any window must stay put. A ToU fee on the same day must move it.
def _fee_share(prices_add):
    _sc = _mk_golden(price_profile="flat")
    _res = _sc["optimizer"].optimize(
        _sc["state"], _sc["prices"] + prices_add, _sc["outdoor"], _sc["wind"],
        _sc["rain"], _sc["solar"], _G_START,
    )
    _tot = np.asarray(_res.power_schedule) + np.asarray(_res.dhw_power_schedule)
    _day = _tot[24:88]  # 06:00-22:00 on the 15-minute grid
    _sum = float(_tot.sum())
    return float(_day.sum()) / _sum if _sum > 0 else 0.0

_share_none = _fee_share(0.0)
_share_flat = _fee_share(0.25)
_tou_add = np.zeros(96)
_tou_add[24:88] = 0.25  # the höglast window priced up
_share_tou = _fee_share(_tou_add)
R.check(
    "a flat fee does not shift energy in time — the null control",
    # 0.03, not 0.02, since v4.0.5: the terminal refill price scales with
    # the price level, so a uniform fee legitimately has the plan end the
    # horizon holding slightly more heat — a small share wobble with no
    # time structure, an order below the 0.05 the ToU check below demands.
    abs(_share_flat - _share_none) < 0.03,
    f"06-22 share {_share_none:.3f} -> {_share_flat:.3f} under a uniform fee",
)
R.check(
    "a höglast fee moves energy out of the hours it prices up",
    _share_tou < _share_none - 0.05,
    f"06-22 share {_share_none:.3f} -> {_share_tou:.3f} under a 06-22 fee",
)

# ===========================================================================
# T2 — peak & power (#7 #5 #3 #22)
# ===========================================================================
R.section("T2 — peak & power (#7 #5 #3 #22)")

from types import SimpleNamespace as _NS

from homeassistant.util import dt as dt_util

from heatpump_optimizer.const import (
    OUTAGE_DHW_DELAY_MINUTES,
    OUTAGE_RECOVERY_HOURS,
    PEAK_GUARD_DISPLACE_NUDGE_C,
)
from heatpump_optimizer.power_guard import (
    GuardState,
    MIN_EVENT_SPACING_S,
    project_window_mean,
)

# --- #7 the projection, against hand arithmetic --------------------------------
# (2 kW × 30 min + 6 kW × 30 min) / 60 min — the DSO's own bill formula.
R.check(
    "mid-window projection is the bill formula, by hand",
    abs(project_window_mean(2.0, 30.0, 6.0, 60.0) - 4.0) < 1e-9,
    f"got {project_window_mean(2.0, 30.0, 6.0, 60.0)}",
)
R.check(
    "an empty window projects the current draw itself",
    abs(project_window_mean(None, 45.0, 5.0, 60.0) - 5.0) < 1e-9,
    "elapsed must be ignored when there is no accumulated mean",
)
R.check(
    "at the window's end the projection is the realised mean",
    abs(project_window_mean(3.0, 60.0, 99.0, 60.0) - 3.0) < 1e-9,
)
R.check(
    "elapsed time is clamped into the window",
    abs(project_window_mean(3.0, 90.0, 99.0, 60.0) - 3.0) < 1e-9,
    "a stale clock must not extrapolate outside the window",
)

# --- #7 the guard's hysteresis, as mutation pairs -------------------------------
_T0 = datetime(2026, 1, 15, 7, 3, tzinfo=UTC)


def _guard_events(projections, *, floors=None, keys=None, threshold=6.0):
    g = GuardState()
    changes = []
    for i, p in enumerate(projections):
        changes.append(
            g.update(
                _T0 + timedelta(seconds=20 * i),
                (keys or ["w1"] * len(projections))[i],
                p,
                threshold,
                0.5,
                floor_hold=(floors or [False] * len(projections))[i],
            )
        )
    return g, changes

_g, _ch = _guard_events([7.0, 7.0])
R.check(
    "two crossing projections engage suppression",
    _g.suppressing and _ch == [False, True],
    f"changes {_ch}",
)
_g, _ch = _guard_events([7.0, 4.0, 7.0])
R.check(
    "a single crossing does nothing — one noisy sample is not a peak",
    not _g.suppressing and not any(_ch),
)
_g, _ch = _guard_events([5.4, 5.4])
R.check(
    "sub-margin projections never engage",
    not _g.suppressing,
    "5.4 < 6.0 − 0.5, so no crossing",
)
_g, _ch = _guard_events([5.6, 5.6])
R.check(
    "the margin engages early — the guard acts before the money is spent",
    _g.suppressing,
    "5.6 > 6.0 − 0.5 must count as crossing",
)
_g, _ch = _guard_events([7.0, 7.0, 7.0, 4.0, 4.0])
R.check(
    "two clear projections release",
    not _g.suppressing and _ch[-1] and not _ch[-2],
    f"changes {_ch}",
)
_g, _ch = _guard_events([7.0, 7.0, 7.0, 4.0, 7.0, 7.0])
R.check(
    "a single clear sample does not release",
    _g.suppressing and not any(_ch[3:]),
    "release needs the same two-sample evidence as engagement",
)
_g, _ch = _guard_events([7.0, 7.0], floors=[False, True])
R.check(
    "a floor hold refuses engagement outright",
    not _g.suppressing,
    "protecting the bill never outranks protecting the house",
)
_g, _ch = _guard_events([7.0, 7.0, 7.0], floors=[False, False, True])
R.check(
    "a floor hold releases an active suppression immediately",
    not _g.suppressing and _ch[-1],
    f"changes {_ch}",
)
_g, _ch = _guard_events([7.0, 7.0, 7.0], keys=["w1", "w1", "w2"])
R.check(
    "the window closing releases unconditionally",
    not _g.suppressing and _ch[-1],
    "a suppression must never leak into the next billed window",
)
_g = GuardState()
_g.update(_T0, "w1", 7.0, 6.0, 0.5, floor_hold=False)
R.check(
    "the event throttle holds for the spacing window and then opens",
    _g.throttled(_T0 + timedelta(seconds=MIN_EVENT_SPACING_S - 1))
    and not _g.throttled(_T0 + timedelta(seconds=MIN_EVENT_SPACING_S + 1)),
)

# --- #7 the time-weighted window fold -------------------------------------------
_tariff_t2 = CapacityTariff(
    enabled=True, price_per_kw=20.0, peaks_averaged=1, window_minutes=60
)
_w0 = datetime(2026, 1, 15, 7, 0, tzinfo=UTC)

_tr_u, _tr_w = PeakTracker(), PeakTracker()
for i in range(4):
    when = _w0 + timedelta(minutes=15 * i)
    _tr_u.observe(when, 2.0 + i, _tariff_t2)
    _tr_w.observe(when, 2.0 + i, _tariff_t2, dt_hours=0.25)
_tr_u.observe(_w0 + timedelta(minutes=60), 0.0, _tariff_t2)
_tr_w.observe(_w0 + timedelta(minutes=60), 0.0, _tariff_t2, dt_hours=0.25)
R.check(
    "uniform spacing: weighted and unweighted folds close the same peak",
    abs(_tr_u.peaks[0] - _tr_w.peaks[0]) < 1e-9,
    f"{_tr_u.peaks[0]} vs {_tr_w.peaks[0]}",
)

# 2 kW standing for 45 minutes, then a 3-minute 10 kW burst: the unweighted
# mean says 4.0, the bill says (2·0.75 + 10·0.05)/0.8 = 2.5. The whole point
# of the weighted fold is that a chatty meter burst cannot buy 1.5 kW of
# phantom peak.
_tr_b = PeakTracker()
for i in range(3):
    _tr_b.observe(
        _w0 + timedelta(minutes=15 * i), 2.0, _tariff_t2, dt_hours=0.25
    )
_tr_b.observe(_w0 + timedelta(minutes=48), 10.0, _tariff_t2, dt_hours=0.05)
_key, _mean, _elapsed, _factor = _tr_b.window_snapshot(
    _w0 + timedelta(minutes=48), _tariff_t2
)
R.check(
    "the running window mean is time-weighted, by hand",
    _mean is not None and abs(_mean - 2.5) < 1e-9,
    f"got {_mean}, unweighted would be 4.0",
)
R.check(
    "the snapshot reports the true elapsed minutes",
    abs(_elapsed - 48.0) < 1e-9,
    f"got {_elapsed}",
)
_k2, _m2, _, _ = _tr_b.window_snapshot(
    _w0 + timedelta(minutes=75), _tariff_t2
)
R.check(
    "a snapshot of a window that has no samples reports no mean",
    _k2 != _key and _m2 is None,
    "the projection must then assume the current draw throughout",
)
_tr_b.observe(_w0 + timedelta(minutes=61), 0.0, _tariff_t2, dt_hours=0.05)
R.check(
    "the closed window's peak is the weighted average",
    abs(_tr_b.peaks[0] - 2.5) < 1e-9,
    f"got {_tr_b.peaks[0]}",
)

# --- #3 the external cap holds through DHW blocks --------------------------------
# The one composition the per-channel caps cannot express: space + hot water
# together must stay under the fuse. The 60%-of-nameplate cap forces DHW
# blocks and space heating to share.
def _cap_solve(cap_kw):
    sc = _mk_golden(dhw=True)
    n = len(sc["prices"])
    caps = None if cap_kw is None else np.full(n, cap_kw)
    res = sc["optimizer"].optimize(
        sc["state"], sc["prices"], sc["outdoor"], sc["wind"], sc["rain"],
        sc["solar"], _G_START, power_caps_extra=caps,
    )
    total = np.asarray(res.power_schedule) + np.asarray(res.dhw_power_schedule)
    return res, total

_res_cap, _total_cap = _cap_solve(3.6)
R.check(
    "space + hot water never exceed the external cap, any step",
    float(np.max(_total_cap)) <= 3.6 + 1e-6,
    f"worst step {float(np.max(_total_cap)):.4f} kW against 3.6",
)
R.check(
    "a DHW block genuinely runs under the cap (the check is not vacuous)",
    float(np.max(np.asarray(_res_cap.dhw_power_schedule))) > 0.5,
)
R.check(
    "a feasible cap reports no comfort breach",
    _res_cap.predictive_info.get("power_cap_breach_c") == 0.0,
    f"got {_res_cap.predictive_info.get('power_cap_breach_c')}",
)
_res_tiny, _total_tiny = _cap_solve(0.05)
R.check(
    "an infeasible cap says so in degrees, not silently",
    float(_res_tiny.predictive_info.get("power_cap_breach_c", 0.0)) > 0.5,
    f"got {_res_tiny.predictive_info.get('power_cap_breach_c')}",
)
_res_free, _ = _cap_solve(None)
R.check(
    "without a cap the breach report does not exist at all",
    "power_cap_breach_c" not in _res_free.predictive_info,
    "the field appearing everywhere would break inert-by-default",
)

# --- #7 the suppression flag rides the external-heat gate -----------------------
# ``peak_guard_active`` must take exactly the discretionary-DHW path external
# heat proved: same flag semantics, same coasting guard. Byte-equivalence to
# ``external_heat_active`` (with no burn forecast) IS that statement.
def _flag_solve(**state_overrides):
    sc = _mk_golden(dhw=True, state_overrides=state_overrides)
    return sc["optimizer"].optimize(
        sc["state"], sc["prices"], sc["outdoor"], sc["wind"], sc["rain"],
        sc["solar"], _G_START,
    )

_r_guard = _flag_solve(dhw_temperature=58.0, peak_guard_active=True)
_r_ext = _flag_solve(dhw_temperature=58.0, external_heat_active=True)
_r_neither = _flag_solve(dhw_temperature=58.0)
R.check(
    "peak_guard_active suppresses discretionary DHW exactly as external heat",
    np.array_equal(
        np.asarray(_r_guard.dhw_power_schedule),
        np.asarray(_r_ext.dhw_power_schedule),
    ),
)
R.check(
    "and the gate actually bites on this day (the pair is not vacuous)",
    not np.array_equal(
        np.asarray(_r_guard.dhw_power_schedule),
        np.asarray(_r_neither.dhw_power_schedule),
    ),
    "with no flag the planner must have been topping up somewhere early",
)

# --- the coordinator wiring: registration, events, fuse, outage -----------------
_METER = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
    "sensor.house_power": FakeState("6500", unit="W"),
    "sensor.hp_power": FakeState("2000", unit="W"),
}


def _t2_coord(states=None, **extra):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **extra,
    }
    return _Coord(_FakeHass(dict(_METER, **(states or {}))), _FakeEntry(data=cfg))


def _listeners(coord):
    _asyncio.run(coord._async_setup_peak_guard())
    return getattr(coord.hass, "state_listeners", [])

_c = _t2_coord(
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
    heat_pump_power_entity="sensor.hp_power",
)
_regs = _listeners(_c)
R.check(
    "the guard listens on the whole-house meter when there is one",
    len(_regs) == 1 and _regs[0][0] == ["sensor.house_power"],
    f"got {[e for e, _ in _regs]}",
)
_regs = _listeners(
    _t2_coord(peak_guard_enabled=True, heat_pump_power_entity="sensor.hp_power")
)
R.check(
    "without a house meter it falls back to the heat pump's own",
    len(_regs) == 1 and _regs[0][0] == ["sensor.hp_power"],
)
R.check(
    "switched off, no listener is registered at all",
    not _listeners(
        _t2_coord(house_power_entity="sensor.house_power")
    ),
    "the flag gates registration, not just behaviour",
)
R.check(
    "enabled but meterless, the guard stays dormant instead of crashing",
    not _listeners(_t2_coord(peak_guard_enabled=True)),
)

# One meter event through the real handler: a 16 A single-phase fuse is
# 3.68 kW, a steady 6.5 kW house is projected over it, and two spaced events
# engage. FakeHass.async_create_task closes coroutines, so the actuation is
# then driven directly and recorded through instance-attribute stubs.
_c = _t2_coord(
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
    main_fuse_amperes=16.0,
    main_fuse_phases=1,
)
_ev = _NS(data={"new_state": FakeState("6500", unit="W")})
_c._on_power_event(_ev)
_first = _c._peak_guard.suppressing
# Rewind the throttle rather than sleeping through it.
_c._peak_guard._last_event -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
_c._guard_last_fold -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
_c._on_power_event(_ev)
R.check(
    "two real meter events over the fuse engage the guard",
    not _first and _c._peak_guard.suppressing,
    f"after one: {_first}, after two: {_c._peak_guard.suppressing}",
)
R.check(
    "the state flag the solver reads follows the guard",
    _c._current_state.peak_guard_active is True,
)
R.check(
    "the evidence trail says what happened and when",
    any("suppressing" in e for e in _c._peak_guard.evidence),
    f"evidence: {_c._peak_guard.evidence}",
)

_published = []
async def _rec_ecl(**kw):
    _published.append(kw)
async def _rec_plan(reason="optimizer"):
    _published.append({"reason": reason})
_c.async_publish_ecl110_command = _rec_ecl
_c.async_publish_current_action = _rec_plan
_c._current_action = {"displace_value": 5.0, "heat_pump_on": True}
_asyncio.run(_c._async_peak_guard_transition())
R.check(
    "engaging nudges the ECL displace down by the configured step",
    _published
    and _published[-1].get("reason") == "peak_guard"
    and abs(
        _published[-1].get("displace_value")
        - (5.0 - PEAK_GUARD_DISPLACE_NUDGE_C)
    )
    < 1e-9,
    f"published {_published[-1] if _published else None}",
)
_c._peak_guard.suppressing = False
_asyncio.run(_c._async_peak_guard_transition())
R.check(
    "releasing re-publishes the plan's own action",
    _published[-1] == {"reason": "peak_guard_release"},
    f"published {_published[-1]}",
)

_c2 = _t2_coord(
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
)
_c2._on_power_event(_ev)
R.check(
    "with neither tariff nor fuse configured the event path is a no-op",
    not _c2._peak_guard.suppressing and _c2._peak_guard._last_event is None,
    "no threshold exists, so nothing must be folded or engaged",
)

# --- #5 fuse arithmetic and the headroom answer ----------------------------------
_c3 = _t2_coord(main_fuse_amperes=20.0, main_fuse_phases=3)
R.check(
    "20 A × 3 phases × 230 V is 13.8 kW",
    abs(_c3._fuse_kw() - 13.8) < 1e-9,
    f"got {_c3._fuse_kw()}",
)
R.check(
    "no fuse configured means no fuse, not a zero-kW one",
    _t2_coord()._fuse_kw() is None,
)
_c3._measured_house_power = 6.5
_hr = _c3._power_headroom()
R.check(
    "headroom is the fuse minus the live house draw",
    _hr["available"]
    and abs(_hr["limit_kw"] - 13.8) < 1e-9
    and abs(_hr["headroom_kw"] - (13.8 - 6.5)) < 1e-9,
    f"got {_hr}",
)
R.check(
    "the answer names its baseline source honestly",
    _hr.get("baseline_source") == "house meter",
    f"got {_hr.get('baseline_source')}",
)
_c3._measured_house_power = None
_c3._measured_power = 2.0
R.check(
    "a heat-pump-only meter admits the baseline load is invisible",
    _c3._power_headroom().get("baseline_source")
    == "heat pump meter only (baseline load invisible)",
)
_c3._measured_power = None
R.check(
    "and with no meter at all the answer says it is plan-derived",
    _c3._power_headroom().get("baseline_source")
    == "planned power only (no meter)",
)
R.check(
    "with no limit configured the sensor says unavailable, not zero",
    _t2_coord()._power_headroom() == {"available": False},
)

# --- #22 outage detection and staggered recovery ---------------------------------
_now_t2 = dt_util.now()


def _outage_coord(gap_minutes, **extra):
    c = _t2_coord(outage_recovery_enabled=True, **extra)
    c._detect_outage((_now_t2 - timedelta(minutes=gap_minutes)).isoformat())
    return c

_c4 = _outage_coord(180.0)
R.check(
    "a three-hour silence reads as an outage and opens recovery",
    _c4._outage_recovery_active(_now_t2)
    and not _c4._outage_recovery_active(
        _now_t2 + timedelta(hours=OUTAGE_RECOVERY_HOURS, minutes=1)
    ),
)
R.check(
    "hot water is queued behind space heating, then released by the clock",
    _c4._outage_dhw_hold(_now_t2)
    and not _c4._outage_dhw_hold(
        _now_t2 + timedelta(minutes=OUTAGE_DHW_DELAY_MINUTES + 1)
    ),
)
_c4._thermal_params.dhw_enabled = True
_c4._current_state.dhw_temperature = _c4._thermal_params.dhw_min_temp - 5.0
R.check(
    "a genuinely cold tank overrides the hot-water delay",
    not _c4._outage_dhw_hold(_now_t2),
    "post-outage the water may already be cold; the family wins",
)
_c5 = _outage_coord(20.0)
R.check(
    "an ordinary restart gap does nothing",
    not _c5._outage_recovery_active(_now_t2)
    and not _c5._outage_dhw_hold(_now_t2),
    "20 minutes is a reboot, not an outage",
)
_c6 = _t2_coord()
_c6._detect_outage((_now_t2 - timedelta(minutes=180)).isoformat())
R.check(
    "switched off, even a real gap changes nothing",
    not _c6._outage_recovery_active(_now_t2),
)
_c7 = _t2_coord(outage_recovery_enabled=True)
_c7._detect_outage("not a timestamp")
_c7._detect_outage(None)
R.check(
    "garbage in the stored tick is ignored, never fatal",
    not _c7._outage_recovery_active(_now_t2),
)

# --- #22 the heartbeat's full round trip through the store ----------------------
# `_detect_outage` in isolation proves the arithmetic; what actually broke
# things elsewhere in T2 was wiring. This drives save → persisted payload →
# a fresh coordinator's load → detection, through the real Store stub.
_ca = _t2_coord(outage_recovery_enabled=True)
_asyncio.run(_ca._async_save_energy_totals())
_cb = _t2_coord(outage_recovery_enabled=True)
_asyncio.run(_cb._async_load_energy_totals())
R.check(
    "a fresh restart right after a save is not an outage",
    not _cb._outage_recovery_active(dt_util.now()),
)
_payload = _asyncio.run(_ca._energy_store.async_load())
_payload["last_tick"] = (dt_util.now() - timedelta(hours=3)).isoformat()
_asyncio.run(_ca._energy_store.async_save(_payload))
_cc = _t2_coord(outage_recovery_enabled=True)
_asyncio.run(_cc._async_load_energy_totals())
R.check(
    "a three-hour-old persisted heartbeat opens recovery on load",
    _cc._outage_recovery_active(dt_util.now()),
    "the save->load->detect chain, not just the detector",
)

# --- #7 the guard bills the projection through the #13 masks --------------------
# A tariff that half-rates nights must be defended in billed-equivalent kW on
# BOTH sides of the comparison — otherwise the guard suppresses hot water in
# exactly the cheap hours the planner shifts load into.
_mask_tariff = dict(
    peak_tariff_enabled=True,
    peak_tariff_price=20.0,
    peak_tariff_window_minutes=60,
    peak_tariff_hours="07:00-19:00",
    peak_tariff_offpeak_factor=0.5,
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
    peak_guard_margin_kw=0.5,
)


def _guard_after_two_events(fixed_now, kw_state="8000"):
    import homeassistant.util.dt as _dt_mod

    c = _t2_coord(
        states={"sensor.house_power": FakeState(kw_state, unit="W")},
        **_mask_tariff,
    )
    c._peak_tracker.month = fixed_now.strftime("%Y-%m")
    c._peak_tracker.peaks = [5.0, 5.0, 5.0]
    ev = _NS(data={"new_state": FakeState(kw_state, unit="W")})
    real_now = _dt_mod.now
    try:
        _dt_mod.now = lambda: fixed_now
        c._on_power_event(ev)
        c._peak_guard._last_event -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
        c._guard_last_fold -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
        c._on_power_event(ev)
    finally:
        _dt_mod.now = real_now
    return c._peak_guard.suppressing

_daytime = datetime(2026, 1, 15, 10, 12, tzinfo=UTC)  # a Thursday, in-hours
_night = datetime(2026, 1, 15, 21, 12, tzinfo=UTC)  # same day, off-peak
R.check(
    "in billed hours an 8 kW projection over a 5 kW threshold engages",
    _guard_after_two_events(_daytime),
)
R.check(
    "the same draw at half-rate night bills 4 kW and does not engage",
    not _guard_after_two_events(_night),
    "8 x 0.5 = 4.0 < 5.0 - 0.5: defending this hour would cost, not save",
)

# --- #3 the advisor actually runs, end to end ------------------------------------
# tests/entities.py fabricates the advisor's payload; nothing before this
# executed `_maybe_run_fuse_advisor` itself, which is how a call to a method
# that did not exist survived to review. The simulate harness is stubbed at
# its REAL name — a renamed call site fails here with AttributeError.
_adv_calls = []


def _advisor_coord(payload_extra=None, **cfg):
    c = _t2_coord(main_fuse_amperes=20.0, main_fuse_phases=3, **cfg)

    async def _fake_simulate(overrides):
        _adv_calls.append(overrides)
        return {
            "overrides": overrides,
            "rate_limited": False,
            "power_cap_breach_c": 0.0,
            "projected_peak_kw": 4.0,
            "monthly_cost_delta": -35.0,
            "baseline_min_room_temperature": 20.6,
            "min_room_temperature": 20.6,
            **(payload_extra or {}),
        }

    c.async_simulate = _fake_simulate
    return c

_adv_calls.clear()
_cad = _advisor_coord()
_cad._simulation_cache = {"marker": "card"}
_cad._last_simulation = None
_asyncio.run(_cad._maybe_run_fuse_advisor())
_adv = _cad._fuse_advisor
R.check(
    "the advisor publishes a verdict for the next-smaller fuse",
    _adv.get("candidate_fuse_a") == 16
    and _adv.get("current_fuse_a") == 20
    and _adv.get("feasible") is True
    and _adv.get("cost_delta_sek_month") == -35.0,
    f"got {_adv}",
)
R.check(
    "the advisor asked for the candidate's headroom, not the full fuse",
    len(_adv_calls) == 1
    and abs(_adv_calls[0]["power_cap_kw"] - 16 * 3 * 0.23) < 1e-6,
    f"calls {_adv_calls}",
)
R.check(
    "the card's simulate cache survives an advisor run untouched",
    _cad._simulation_cache == {"marker": "card"}
    and _cad._last_simulation is None,
)
_asyncio.run(_cad._maybe_run_fuse_advisor())
R.check(
    "a second run inside the week is skipped",
    len(_adv_calls) == 1,
)

# A breach the uncapped plan shares is the weather's, not the fuse's.
_adv_calls.clear()
_cad2 = _advisor_coord(
    payload_extra={
        "power_cap_breach_c": 1.5,
        "baseline_min_room_temperature": 19.5,
        "min_room_temperature": 19.5,
    }
)
_asyncio.run(_cad2._maybe_run_fuse_advisor())
R.check(
    "a shortfall the baseline plan shares is not blamed on the fuse",
    _cad2._fuse_advisor.get("feasible") is True
    and _cad2._fuse_advisor.get("comfort_shortfall_c") == 0.0,
    f"got {_cad2._fuse_advisor}",
)
_adv_calls.clear()
_cad3 = _advisor_coord(
    payload_extra={
        "power_cap_breach_c": 1.5,
        "baseline_min_room_temperature": 21.0,
        "min_room_temperature": 19.5,
    }
)
_asyncio.run(_cad3._maybe_run_fuse_advisor())
R.check(
    "a shortfall the cap itself forces still fails the candidate",
    _cad3._fuse_advisor.get("feasible") is False
    and _cad3._fuse_advisor.get("comfort_shortfall_c") == 1.5,
    f"got {_cad3._fuse_advisor}",
)

# A rate-limited answer is the card's cached payload, not this what-if:
# it must be discarded, retried tomorrow, and never displace a real verdict.
_adv_calls.clear()
_cad4 = _advisor_coord(payload_extra={"rate_limited": True})
_cad4._fuse_advisor = {"candidate_kw": 11.04, "feasible": True}
_asyncio.run(_cad4._maybe_run_fuse_advisor())
R.check(
    "a rate-limited what-if keeps last month's real verdict",
    _cad4._fuse_advisor == {"candidate_kw": 11.04, "feasible": True}
    and _cad4._fuse_advisor_at is not None,
    f"got {_cad4._fuse_advisor}",
)

# ===========================================================================
# T3 — hot water (#32 #18 #20 #24 #47 #9 #28 #6)
# ===========================================================================
R.section("T3 — hot water (#32 #18 #20 #24 #47 #9 #28 #6)")

from heatpump_optimizer.const import (
    DHW_LEGIONELLA_HOLD_MINUTES,
    DHW_QUANTILE_MIN_EVENTS,
)
from heatpump_optimizer.dhw_draws import (
    DrawStats,
    labels_for,
    window_label as _wlabel,
)
from heatpump_optimizer import pump_schedule as _ps
from heatpump_optimizer.thermal_model import WATER_SPECIFIC_HEAT

# --- the inlet model, against the numbers it replaced ---------------------------
_tp = ThermalParameters()
_old_draw = (
    _tp.dhw_daily_consumption / 24.0 * WATER_SPECIFIC_HEAT
    * (_tp.dhw_setpoint - 10.0)
)
R.check(
    "the default inlet reproduces the hard-coded 10.0 draw power bit for bit",
    _tp.dhw_draw_power == _old_draw,
    f"{_tp.dhw_draw_power} vs {_old_draw}",
)
R.check(
    "amplitude zero keeps the inlet constant across the year",
    all(_tp.seasonal_inlet_temp(d) == 10.0 for d in (1, 60, 182, 242, 365)),
)
_tp_swing = ThermalParameters(dhw_inlet_seasonal_amplitude=3.0)
R.check(
    "the seasonal swing bottoms in late February and peaks in late summer",
    abs(_tp_swing.seasonal_inlet_temp(60) - 7.0) < 0.01
    and abs(_tp_swing.seasonal_inlet_temp(242) - 13.0) < 0.05,
    f"feb {_tp_swing.seasonal_inlet_temp(60):.2f}, aug {_tp_swing.seasonal_inlet_temp(242):.2f}",
)
_tp.dhw_inlet_current = 4.5
R.check(
    "a resolved live inlet wins over the configured mean",
    _tp.dhw_inlet_reference == 4.5,
)
_tp_grey = ThermalParameters(greywater_recovery=0.3)
R.check(
    "greywater recovery scales the draw chain down by its effectiveness",
    abs(_tp_grey.dhw_draw_power - 0.7 * _old_draw) < 1e-12,
)

# --- the presence rule ignores None (the phantom-enable fix) --------------------
R.check(
    "a cleared DHW sensor written back as None does not enable hot water",
    ThermalParameters.from_config({"dhw_temp_entity": None}).dhw_enabled
    is False,
)
R.check(
    "a real DHW key still enables it, and empty windows still count",
    ThermalParameters.from_config({"dhw_temp_entity": "sensor.t"}).dhw_enabled
    and ThermalParameters.from_config({"dhw_windows": ""}).dhw_enabled,
)
R.check(
    "no T3 hot-water key joins the presence trio",
    not ThermalParameters.from_config(
        {
            "dhw_inlet_temp": 8.0,
            "dhw_quantile_targets_enabled": True,
            "vvc_pump_entity": "switch.vvc",
        }
    ).dhw_enabled,
)

# --- #32 the draw-occurrence statistics ------------------------------------------
_WINDOWS = [(6.0, 8.5), (17.0, 22.0)]
R.check(
    "hours resolve to their window label, outside hours to nothing",
    _wlabel(7.0, _WINDOWS) == "06:00-08:30"
    and _wlabel(21.9, _WINDOWS) == "17:00-22:00"
    and _wlabel(12.0, _WINDOWS) == "",
)
R.check(
    "a midnight-wrapping window resolves on both sides of midnight",
    _wlabel(23.0, [(22.0, 2.0)]) == "22:00-02:00"
    and _wlabel(1.0, [(22.0, 2.0)]) == "22:00-02:00"
    and _wlabel(12.0, [(22.0, 2.0)]) == "",
)

_ds = DrawStats()
_D1 = datetime(2026, 1, 15, 6, 0, tzinfo=UTC)
for minutes, kwh in ((0, 0.8), (30, 1.0), (60, 0.4)):
    _ds.fold(_D1 + timedelta(minutes=minutes), "06:00-08:30", kwh)
_ds.fold(_D1 + timedelta(hours=4), "", 0.0)  # window closed
R.check(
    "ticks inside one window merge into a single occurrence",
    _ds.count("06:00-08:30") == 1
    and abs(_ds.reservoirs["06:00-08:30"][0] - 2.2) < 1e-9,
    f"got {_ds.reservoirs}",
)
_ds.fold(_D1 + timedelta(days=1), "06:00-08:30", 0.0)
_ds.fold(_D1 + timedelta(days=1, hours=4), "", 0.0)
R.check(
    "a quiet morning records its zero — calm days are evidence too",
    _ds.count("06:00-08:30") == 2 and _ds.reservoirs["06:00-08:30"][1] == 0.0,
)
R.check(
    "energy outside every window belongs to no statistic",
    "" not in _ds.reservoirs,
)
_mean = 1.0
R.check(
    "below the evidence floor the ready energy leans on the mean",
    abs(
        _ds.ready_energy("17:00-22:00", _mean) - _mean
    ) < 1e-9,  # zero events -> pure mean
)
_ds2 = DrawStats()
for day in range(DHW_QUANTILE_MIN_EVENTS):
    _ds2.fold(_D1 + timedelta(days=day), "06:00-08:30", 3.0)
    _ds2.fold(_D1 + timedelta(days=day, hours=4), "", 0.0)
R.check(
    "at full evidence the ready energy is the quantile itself",
    abs(_ds2.ready_energy("06:00-08:30", 1.0) - 3.0) < 1e-9,
    f"got {_ds2.ready_energy('06:00-08:30', 1.0)}",
)
_ds3 = DrawStats.from_dict(_ds2.as_dict())
R.check(
    "the statistics survive a store round trip",
    _ds3.reservoirs == _ds2.reservoirs and _ds3.count("06:00-08:30") == 8,
)
_ds3.prune(["17:00-22:00"])
R.check(
    "redrawn windows forget their old statistics",
    _ds3.count("06:00-08:30") == 0,
    "stats about hours that are no longer windows would be silently wrong",
)
_ds4 = DrawStats()
for day in range(50):
    _ds4.fold(_D1 + timedelta(days=day), "06:00-08:30", float(day))
    _ds4.fold(_D1 + timedelta(days=day, hours=4), "", 0.0)
R.check(
    "reservoirs keep the newest forty occurrences and drop the rest",
    _ds4.count("06:00-08:30") == 40
    and _ds4.reservoirs["06:00-08:30"][0] == 10.0,
)

# --- #20 the quantile targets reach the plan (mutation pair) --------------------
# Flat prices and a big tank on purpose: on the winter day the planner
# charges the tank overnight for arbitrage anyway, and on the default
# 300 L tank a single DHW block moves it 3.4 °C — both of which would
# swamp exactly the ready-target change these pairs exist to see.
def _q_solve(table):
    sc = _mk_golden(
        dhw=True,
        price_profile="flat",
        config_overrides={"dhw_tank_volume": 1500.0},
        state_overrides={"dhw_temperature": 46.0},
        param_overrides=(
            {"dhw_window_ready_energy": table} if table is not None else {}
        ),
    )
    return sc["optimizer"].optimize(
        sc["state"], sc["prices"], sc["outdoor"], sc["wind"], sc["rain"],
        sc["solar"], _G_START,
    )

_q_base = _q_solve(None)
_q_heavy = _q_solve({"06:00-08:30": (15.0, DHW_QUANTILE_MIN_EVENTS)})
R.check(
    "a learned heavy morning raises what the tank holds before the window",
    not np.array_equal(
        np.asarray(_q_base.dhw_power_schedule),
        np.asarray(_q_heavy.dhw_power_schedule),
    )
    and max(_q_heavy.dhw_temp_trajectory[:25])
    > max(_q_base.dhw_temp_trajectory[:25]) + 0.5,
    f"pre-window peak {max(_q_base.dhw_temp_trajectory[:25]):.1f} -> "
    f"{max(_q_heavy.dhw_temp_trajectory[:25]):.1f}",
)
_q_one = _q_solve({"06:00-08:30": (15.0, 1)})
R.check(
    "one early outlier moves the target a step, not the whole way",
    max(_q_one.dhw_temp_trajectory[:25])
    < max(_q_heavy.dhw_temp_trajectory[:25]) - 0.3,
    "the ramp must damp single-event evidence",
)
R.check(
    "an empty table is byte-identical to no table at all",
    np.array_equal(
        np.asarray(_q_base.dhw_power_schedule),
        np.asarray(_q_solve({}).dhw_power_schedule),
    ),
)

# --- #24 hold-verified free disinfection -----------------------------------------
def _legionella_run(flag, observations):
    """Feed (minutes, temp) observations through the tracker; return credit."""
    import homeassistant.util.dt as _dt_mod

    c = _t2_coord(dhw_free_disinfection_enabled=flag)
    c._thermal_params.dhw_legionella_temp = 60.0
    base = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    c._dhw_last_legionella = base - timedelta(days=3)
    before = c._dhw_last_legionella
    real_now = _dt_mod.now
    try:
        for minutes, temp in observations:
            _dt_mod.now = lambda m=minutes: base + timedelta(minutes=m)
            _asyncio.run(c._async_track_dhw_legionella(temp))
    finally:
        _dt_mod.now = real_now
    return c._dhw_last_legionella != before

R.check(
    "58 °C for an hour credits nothing — warm is not disinfected",
    not _legionella_run(
        True, [(m, 58.0) for m in range(0, 61, 10)]
    ),
)
R.check(
    "61 °C held past the hold time writes the completion timestamp",
    _legionella_run(True, [(m, 61.0) for m in range(0, 31, 10)]),
    f"hold is {DHW_LEGIONELLA_HOLD_MINUTES} min of observed time at temperature",
)
R.check(
    "a blip at temperature between cold readings starts the hold over",
    not _legionella_run(
        True,
        [(0, 61.0), (10, 61.0), (20, 55.0), (30, 61.0), (40, 61.0)],
    ),
)
R.check(
    "with the flag off the historical instant credit is untouched",
    _legionella_run(False, [(0, 61.0)]),
)

# --- #47 the elastic legionella gate ----------------------------------------------
from heatpump_optimizer.price_model import PriceShapeModel as _PSM

_psm_fresh = _PSM()
R.check(
    "a fresh prior has NO opinion on the daily minimum",
    _psm_fresh.expected_daily_min([0], 1.0) is None,
    "a damped young shape's minimum is the daily mean, and every day's "
    "cheapest hour beats its mean — 'level x ~1' would fire the gate "
    "at the minimum interval every time instead of deferring",
)
_psm_half = _PSM()
_psm_half.days[0] = 3  # partially trained: still no opinion
R.check(
    "a partially trained prior still defers",
    _psm_half.expected_daily_min([0], 1.0) is None,
)
_psm_mixed = _PSM()
_psm_mixed.days[0] = 10  # weekday trained, weekend not
R.check(
    "one untrained day type in the span withholds the whole answer",
    _psm_mixed.expected_daily_min([0, 1], 1.0) is None,
)
_psm_tr = _PSM()
_shape_day = [1.5] * 7 + [0.5] * 5 + [1.0] * 12
_base_day = datetime(2026, 1, 12, tzinfo=UTC)  # a Monday
for d in range(30):
    _psm_tr.observe_day(_base_day + timedelta(days=d), list(_shape_day))
_exp = _psm_tr.expected_daily_min([0], 1.0)
R.check(
    "a trained prior expects the minimum at the cheap hours' factor",
    _exp is not None and _exp < 0.75,
    f"got {_exp}",
)

def _el_solve(**param_overrides):
    sc = _mk_golden(
        dhw=True,
        price_profile="flat",  # winter arbitrage would mask the cycle
        config_overrides={"dhw_tank_volume": 1500.0},
        state_overrides={"dhw_hours_since_legionella": 130.0},
        param_overrides=param_overrides,
    )
    return sc["optimizer"].optimize(
        sc["state"], sc["prices"], sc["outdoor"], sc["wind"], sc["rain"],
        sc["solar"], _G_START,
    )

_el_off = _el_solve()
_el_inert = _el_solve(dhw_elastic_legionella_enabled=True)
R.check(
    "elastic with no ceiling (a young prior) is byte-identical to off",
    np.array_equal(
        np.asarray(_el_off.dhw_power_schedule),
        np.asarray(_el_inert.dhw_power_schedule),
    ),
)
_el_go = _el_solve(
    dhw_elastic_legionella_enabled=True, dhw_legionella_price_ceiling=99.0
)
R.check(
    "a generous ceiling runs the cycle early on a known cheap hour",
    max(_el_go.dhw_temp_trajectory) > max(_el_off.dhw_temp_trajectory) + 2.0,
    f"peak {max(_el_off.dhw_temp_trajectory):.1f} -> {max(_el_go.dhw_temp_trajectory):.1f}",
)
_el_wait = _el_solve(
    dhw_elastic_legionella_enabled=True, dhw_legionella_price_ceiling=1e-6
)
R.check(
    "a ceiling no known price beats keeps waiting for a better day",
    np.array_equal(
        np.asarray(_el_wait.dhw_power_schedule),
        np.asarray(_el_off.dhw_power_schedule),
    ),
)
_el_early = _el_solve(
    dhw_elastic_legionella_enabled=True,
    dhw_legionella_price_ceiling=99.0,
    dhw_legionella_min_interval_days=6.0,
)
R.check(
    "inside the minimum interval even a free day does not re-run the cycle",
    np.array_equal(
        np.asarray(_el_early.dhw_power_schedule),
        np.asarray(_el_off.dhw_power_schedule),
    ),
    "130 h since the last cycle is under a 6-day minimum interval",
)

# --- #18 day-type profiles ---------------------------------------------------------
_c18 = _t2_coord()
R.check(
    "with no day-type evidence the blend IS the pooled profile",
    _c18._dhw_pattern_for(True) == _c18._dhw_hourly_profile,
)
_c18._dhw_profile_weekend = [2.0 if h in (9, 10) else 0.5 for h in range(24)]
_c18._dhw_daytype_samples[1] = 28  # two weekends of evidence -> w = 2/3
_blend = _c18._dhw_pattern_for(True)
R.check(
    "weekend evidence moves the weekend pattern toward late mornings",
    _blend != _c18._dhw_hourly_profile and _blend[9] > _c18._dhw_hourly_profile[9],
)
R.check(
    "and the blend still budgets the same daily volume",
    abs(sum(_blend) - 24.0) < 0.3,
    f"sum {sum(_blend):.2f} — the profile decides when, never how much",
)
R.check(
    "weekday evidence does not leak into the weekend answer",
    _c18._dhw_pattern_for(False) == _c18._dhw_hourly_profile,
)

# --- #28 mixed litres, by hand -----------------------------------------------------
_c28 = _t2_coord(dhw_tank_volume=300.0)
_c28._thermal_params.dhw_enabled = True
_c28._thermal_params.dhw_tank_volume = 300.0
_c28._current_state.dhw_temperature = 55.0
_mix = _c28._dhw_mixed_water()
R.check(
    "300 L at 55 °C over a 10 °C inlet is 450 L of 40 °C shower water",
    abs(_mix.get("litres_40c", 0) - 450.0) < 0.5,
    f"got {_mix}",
)
R.check(
    "and 56 minutes of shower at the default 8 L/min",
    abs(_mix.get("shower_minutes", 0) - 56.3) < 0.2,
    f"got {_mix}",
)

# --- #9 the setpoint sweep ----------------------------------------------------------
# A 1500 L tank, where "which setpoint covers the heavy days" is a real
# question; the default 200 L tank cannot hold its evening window in the
# usable band at any setpoint (see the small-tank check below).
_c9 = _t2_coord(dhw_tank_volume=1500.0)
_c9._thermal_params.dhw_enabled = True
_c9._prices = [{"total": 1.0}] * 24
_sweep = _c9._dhw_setpoint_sweep()
_rec1 = _sweep.get("recommended_setpoint")
R.check(
    "with no draw evidence the sweep falls back to the profile mean",
    len(_sweep.get("candidates", [])) == 7
    and _sweep.get("heaviest_window_kwh", 0.0) > 0.5
    and _rec1 is not None,
    f"got {_sweep.get('heaviest_window_kwh')} kWh heaviest, rec {_rec1} — "
    "a 0 kWh heaviest window would recommend the sweep bottom for everyone",
)
R.check(
    "the recommendation actually covers the heaviest window",
    _rec1 is not None
    and _sweep.get("covers_heaviest_window") is True
    and max(_c9._thermal_params.dhw_tank_thermal_mass, 0.05)
    * (_rec1 - _c9._thermal_params.dhw_min_temp)
    >= _sweep["heaviest_window_kwh"] - 1e-6,
)
R.check(
    "hotter tanks cost more per day — the trade the sweep exists to show",
    _sweep["candidates"][-1]["cost_per_day"]
    > _sweep["candidates"][0]["cost_per_day"],
)
_c9._draw_stats.reservoirs["06:00-08:30"] = [8.0] * 10
_sweep2 = _c9._dhw_setpoint_sweep()
R.check(
    "a heavy learned window pushes the recommendation up",
    (_sweep2.get("recommended_setpoint") or 0) > _rec1,
    f"got {_sweep2.get('recommended_setpoint')} vs {_rec1} after 8 kWh "
    f"heavy days on a {_c9._thermal_params.dhw_tank_volume:.0f} L tank",
)
_c9s = _t2_coord()  # the default 200 L tank
_c9s._thermal_params.dhw_enabled = True
_c9s._prices = [{"total": 1.0}] * 24
_sweep_small = _c9s._dhw_setpoint_sweep()
R.check(
    "a tank too small for its heavy days says 'as hot as allowed', honestly",
    _sweep_small.get("recommended_setpoint") == 60
    and _sweep_small.get("covers_heaviest_window") is False,
    f"got {_sweep_small.get('recommended_setpoint')}, covers "
    f"{_sweep_small.get('covers_heaviest_window')} — None-forever helps no one",
)

# --- #6 the pump schedule ------------------------------------------------------------
R.check(
    "the VVC pump runs inside a demand window and rests outside",
    _ps.vvc_should_run(7.0, _WINDOWS, 20)[0]
    and not _ps.vvc_should_run(12.0, _WINDOWS, 20)[0],
)
R.check(
    "the lead time pre-heats the loop just before a window opens",
    _ps.vvc_should_run(16.8, _WINDOWS, 20)[0]
    and not _ps.vvc_should_run(16.3, _WINDOWS, 20)[0],
)
R.check(
    "a window shorter than the lead has no hole in its final approach",
    all(
        _ps.vvc_should_run(h, [(17.0, 17.5)], 60)[0]
        for h in (16.0, 16.4, 16.7, 16.9, 17.2)
    )
    and not _ps.vvc_should_run(15.9, [(17.0, 17.5)], 60)[0],
    "probing the single instant now+lead went dark 16:30-17:00 — the "
    "exact minutes the pre-heat exists for",
)
R.check(
    "with no windows the loop is simply left on",
    _ps.vvc_should_run(3.0, [], 20)[0],
)

_SAFE = dict(
    plan_heat_now=False,
    plan_heat_next=False,
    curve_driven=False,
    zone_temps=[21.0],
    floor_temp=19.0,
    outdoor_temp=5.0,
)
R.check(
    "a provably idle warm slot is the only one that switches the space pump off",
    not _ps.space_pump_should_run(**_SAFE)[0],
)
for name, mutation in (
    ("heat planned now", {"plan_heat_now": True}),
    ("heat planned next step", {"plan_heat_next": True}),
    ("heat curve driven", {"curve_driven": True}),
    ("a zone near its floor", {"zone_temps": [19.2]}),
    ("freezing outside", {"outdoor_temp": -1.0}),
    ("outdoor unknown", {"outdoor_temp": None}),
):
    R.check(
        f"rail: {name} forces the space pump on",
        _ps.space_pump_should_run(**{**_SAFE, **mutation})[0],
    )
R.check(
    "no plan at all reads as heat-wanted, never as off",
    _ps.plan_commands_heat(None, 0) == (True, True),
)
R.check(
    "the plan lookup reads this step and the next",
    _ps.plan_commands_heat([0.0, 2.0, 0.0], 0) == (False, True)
    and _ps.plan_commands_heat([0.0, 2.0, 0.0], 2) == (False, False),
)

# The coordinator glue: transitions only, and only configured entities.
_c6 = _t2_coord(
    vvc_pump_entity="switch.vvc",
    dhw_tank_volume=300.0,  # presence -> dhw_enabled
)
_c6._thermal_params.dhw_enabled = True
_c6._thermal_params.dhw_schedule_enabled = True
from heatpump_optimizer.dhw_schedule import parse_windows as _parse_w

_c6._thermal_params.dhw_windows = _parse_w("06:00-08:30")
_asyncio.run(_c6._async_drive_pumps())
_first_calls = len(_c6.hass.services.calls)
_asyncio.run(_c6._async_drive_pumps())
R.check(
    "the pump is commanded on the first tick and not again without a change",
    _first_calls == 1 and len(_c6.hass.services.calls) == 1,
    f"calls {_c6.hass.services.calls}",
)
_dom, _svc, _payload = _c6.hass.services.calls[0]
R.check(
    "the command names the configured entity and a real on/off service",
    _payload == {"entity_id": "switch.vvc"}
    and _svc in ("turn_on", "turn_off"),
)
_c7v = _t2_coord()
_asyncio.run(_c7v._async_drive_pumps())
R.check(
    "no configured pump entities means no service call, ever",
    len(_c7v.hass.services.calls) == 0,
)
_c6b = _t2_coord(vvc_pump_entity="switch.vvc")
_c6b._thermal_params.dhw_enabled = False
_c6b._pump_commanded["switch.vvc"] = False  # last schedule-driven command
_asyncio.run(_c6b._async_drive_pumps())
R.check(
    "hot water disabled leaves the loop pump ON, never stuck off",
    _c6b._pump_commanded.get("switch.vvc") is True
    and len(_c6b.hass.services.calls) == 1
    and _c6b.hass.services.calls[0][1] == "turn_on",
    "a configured pump abandoned in its last commanded state is a "
    "cold-loop trap",
)


async def _failing_call(domain, service, data=None, **kwargs):
    raise RuntimeError("entity unavailable")

_c6c = _t2_coord(vvc_pump_entity="switch.vvc")
_c6c._thermal_params.dhw_enabled = False
_c6c.hass.services.async_call = _failing_call
_asyncio.run(_c6c._async_drive_pumps())
R.check(
    "a failed pump command is retried next tick, not remembered as done",
    "switch.vvc" not in _c6c._pump_commanded,
    f"cache {_c6c._pump_commanded} — recording before the call succeeded "
    "meant one unavailable moment froze the pump state forever",
)

# --- #47 through the coordinator path (the review's major finding) --------------
# The ceiling must be None with a young prior even when the user opted
# in: the mechanism-level None is only real protection if the coordinator
# actually passes it through.
_c47 = _t2_coord(dhw_tank_volume=300.0)
_c47._thermal_params.dhw_enabled = True
_c47._thermal_params.dhw_elastic_legionella_enabled = True
_c47._thermal_params.dhw_legionella_enabled = True
_c47._dhw_last_legionella = dt_util.now() - timedelta(days=5)
_c47._prices = [{"total": 1.0}] * 24
_c47._prepare_dhw_inputs(dt_util.now())
R.check(
    "elastic opted in with a fresh prior sets NO ceiling",
    _c47._thermal_params.dhw_legionella_price_ceiling is None,
    "the young-prior 'ceiling = mean' fired the cycle at the minimum "
    "interval every time — the opposite of deferring",
)
_c47._price_model.days = [30, 30]
_c47._prepare_dhw_inputs(dt_util.now())
_ceiling = _c47._thermal_params.dhw_legionella_price_ceiling
R.check(
    "a fully trained prior sets a real ceiling at or below the level",
    _ceiling is not None and _ceiling <= 1.0 + 1e-9,
    f"got {_ceiling}",
)

# ===========================================================================
# T3b — shared-step honesty (user report on v3.16.0)
# ===========================================================================
R.section("T3b — shared-step honesty")

# space runs steps 0-1, hot water steps 1-2: they share step 1 only. Each
# slot's shared_kwh is the OTHER channel's energy inside the shared steps —
# by hand: dhw contributes 3 kW x 0.25 h = 0.75 to the space slot, space
# contributes 2 kW x 0.25 h = 0.5 to the dhw slot.
_ts = [datetime(2026, 1, 15, 6, 0, tzinfo=UTC) + timedelta(minutes=15 * i) for i in range(4)]
_space_p = [2.0, 2.0, 0.0, 0.0]
_dhw_p = [0.0, 3.0, 3.0, 0.0]
_prices_p = [1.0] * 4
_sp_slots = Coord._plan_slots(_ts, _space_p, _prices_p, 0.25, other_powers=_dhw_p)
_dw_slots = Coord._plan_slots(_ts, _dhw_p, _prices_p, 0.25, other_powers=_space_p)
R.check(
    "a slot names the other channel's energy in its shared steps, by hand",
    len(_sp_slots) == 1
    and _sp_slots[0].get("shared_kwh") == 0.75
    and len(_dw_slots) == 1
    and _dw_slots[0].get("shared_kwh") == 0.5,
    f"space {_sp_slots}, dhw {_dw_slots}",
)
_solo = Coord._plan_slots(
    _ts, [2.0, 2.0, 0.0, 0.0], _prices_p, 0.25,
    other_powers=[0.0, 0.0, 3.0, 3.0],
)
R.check(
    "no overlap, no key — captures without sharing are unchanged",
    len(_solo) == 1 and "shared_kwh" not in _solo[0],
)
_legacy = Coord._plan_slots(_ts, _space_p, _prices_p, 0.25)
R.check(
    "callers that pass no other channel get the pre-T3b slot, byte for byte",
    _legacy == [{k: v for k, v in _sp_slots[0].items() if k != "shared_kwh"}],
)

# The invariant the whole fixture library already witnesses, asserted once
# explicitly: overlap steps exist AND respect the capacity sum. If a future
# change ever made them exceed it, "time-share" would become a lie.
import json as _json

_wf = _json.load(open("tests/golden/winter_single_dhw.json"))
_pairs = list(zip(_wf["power_schedule"], _wf["dhw_power_schedule"]))
_over = [(s, w) for s, w in _pairs if s > 0.05 and w > 0.05]
R.check(
    "the recorded winter day shares steps and every one respects capacity",
    len(_over) > 0 and all(s + w <= 6.0 + 1e-6 for s, w in _over),
    f"{len(_over)} shared steps, worst sum "
    f"{max((s + w for s, w in _over), default=0):.2f} of 6.0",
)


# ===========================================================================
# T4a — model & learning, part one (#42 #26 #11 #12)
# ===========================================================================
R.section("T4a — insurance and detectors (#42 #26 #11 #12)")

import random as _random
from dataclasses import replace as _dc_replace

from heatpump_optimizer.const import (
    COP_BASELINE_MIN_SAMPLES,
    IMMERSION_FACTOR,
    OPEN_WINDOW_RELAX_C,
    VENT_CUSUM_CLIP_C,
    VENT_CUSUM_THRESHOLD_C,
)
from heatpump_optimizer.drift import Cusum
from heatpump_optimizer.snapshots import (
    BIAS_TRIP_DAYS,
    RING_SIZE,
    SnapshotRing,
)

_T4 = datetime(2026, 1, 15, 7, 0, tzinfo=UTC)

# --- the CUSUM primitive, against hand arithmetic --------------------------------
_cu = Cusum(threshold=1.2, drift=0.08, side=-1)
_random.seed(7)
for i in range(500):
    _cu.update(_T4 + timedelta(minutes=30 * i), _random.gauss(0.0, 0.06))
R.check(
    "centred noise accumulates nothing",
    not _cu.tripped and _cu.stat < 0.5,
    f"stat {_cu.stat:.3f} after 500 noisy samples",
)
_cu2 = Cusum(threshold=1.2, drift=0.08, side=-1)
_trip_at = None
for i in range(10):
    if _cu2.update(_T4 + timedelta(minutes=30 * i), -0.4) and _cu2.tripped:
        _trip_at = i + 1
        break
R.check(
    "a -0.4 °C step trips at exactly the hand-computed fourth sample",
    _trip_at == 4,
    "4 x (0.4 - 0.08) = 1.28 is the first total over 1.2",
)
_rel = None
for i in range(30):
    if (
        _cu2.update(_T4 + timedelta(hours=10, minutes=30 * i), 0.0)
        and not _cu2.tripped
    ):
        _rel = i + 1
        break
R.check(
    "recovery releases through hysteresis, not at the trip line",
    _rel is not None and _cu2.stat <= 0.3 + 1e-9,
    "a detector that releases at the trip line chatters on it",
)
_cu3 = Cusum(threshold=1.2, drift=0.08, side=-1)
for i in range(100):
    _cu3.update(_T4 + timedelta(minutes=i), 0.5)
R.check(
    "the wrong-side residual never accumulates",
    not _cu3.tripped and _cu3.stat == 0.0,
    "warm-side error is the heat-loss learner's business, not a window",
)
_cu4 = Cusum(threshold=1.2, drift=0.08, side=-1)
_cu4.load(_cu2.as_dict())
R.check(
    "the detector's state survives a store round trip",
    abs(_cu4.stat - _cu2.stat) < 1e-3
    and _cu4.tripped == _cu2.tripped
    and _cu4.evidence == _cu2.evidence,
)
_cu5 = Cusum(threshold=1.2, drift=0.08, side=-1)
_cu5.load({"stat": "garbage", "tripped": "yes", "evidence": None})
R.check(
    "a corrupt payload loads as a QUIET detector, not a latched one",
    _cu5.stat == 0.0 and _cu5.tripped is False,
    'a truthy string like "yes" must not freeze every learner on load',
)
_cu6 = Cusum(threshold=1.2, drift=0.08, side=-1)
for i in range(100):
    _cu6.update(_T4 + timedelta(minutes=30 * i), -0.4)
R.check(
    "the statistic is capped, so release lag cannot grow with trip length",
    _cu6.stat <= 1.2 * 1.5 + 1e-9,
    "an 8-hour window must not freeze learning for two extra days after "
    "it closes",
)
_cu7 = Cusum(threshold=1.2, drift=0.08, side=-1)
for i in range(6):
    _cu7.update(_T4 + timedelta(minutes=30 * i), -0.4)
R.check(
    "a tripped detector nothing feeds for hours force-releases as stale",
    not _cu7.release_if_starved(_T4 + timedelta(hours=5), 6.0)
    and _cu7.release_if_starved(_T4 + timedelta(hours=10), 6.0)
    and not _cu7.tripped
    and _cu7.stat == 0.0,
    "the feed dries up in mild weather; a latch nothing can feed must "
    "time out",
)
_cu8 = Cusum(threshold=1.2, drift=0.08, side=-1)
_cu8.load({"stat": 2.0, "tripped": True})  # a pre-cap payload, no last_fed
R.check(
    "an unknown feed history starts the clock instead of releasing blind",
    not _cu8.release_if_starved(_T4, 6.0)
    and _cu8.last_fed == _T4
    and _cu8.release_if_starved(_T4 + timedelta(hours=7), 6.0),
)

# --- #26 through the heat-loss learner ---------------------------------------------
# The real _async_learn_house_heat_loss, with only the model's one-step
# prediction stubbed (at its real name, like the advisor tests) so the
# residual is exact. Each helper call replays `n` intervals of a chosen
# residual through the learner.


def _vent_coord(**cfg):
    c = _t2_coord(**cfg)
    c._current_state.room_temperature = 20.0
    c._current_state.outdoor_temperature = 0.0
    c._current_action = {"power": 2.0}
    c._current_weather = lambda: (0.0, 0.0)
    return c


def _feed_residual(c, residual, n, start):
    """Replay exactly ``n`` half-hour intervals of one residual.

    Successive runs must start >2 h after the previous one ended: the
    learner's max-interval guard then skips call 0, which only re-seeds
    the baseline, so calls 1..n each feed one residual.
    """
    import homeassistant.util.dt as _dt_mod

    observed = c._current_state.room_temperature

    def _sim(prev, power, outdoor, **kw):
        return _dc_replace(prev, room_temperature=observed - residual)

    c._thermal_model.simulate_step = _sim
    real_now = _dt_mod.now
    try:
        for i in range(n + 1):
            _dt_mod.now = lambda i=i: start + timedelta(minutes=30 * i)
            _asyncio.run(c._async_learn_house_heat_loss())
    finally:
        _dt_mod.now = real_now


_cv = _vent_coord()
_feed_residual(_cv, -0.4, 3, _T4)
R.check(
    "three cold intervals are not yet a window",
    not _cv._vent_cusum.tripped,
    f"stat {_cv._vent_cusum.stat:.2f}",
)
_feed_residual(_cv, -0.4, 1, _T4 + timedelta(hours=4))
R.check(
    "the fourth trips the detector through the real learner",
    _cv._vent_cusum.tripped and _cv._vent_cusum.evidence,
)
R.check(
    "a tripped detector freezes every learner with reason ventilation",
    _cv._learning_frozen() == "ventilation",
)
_scale_frozen = _cv._house_heat_loss_scale
_feed_residual(_cv, -0.4, 4, _T4 + timedelta(hours=8))
R.check(
    "while frozen, cold residuals feed the detector but never the model",
    _cv._house_heat_loss_scale == _scale_frozen
    and _cv._learner_freeze_reason == "ventilation",
    "an afternoon of airing out must not teach a phantom heat loss",
)
# The four frozen feeds above kept accumulating up to the 1.8 cap, so
# the decay back to the 0.3 release line takes 19 clean half-hours.
_feed_residual(_cv, 0.0, 32, _T4 + timedelta(hours=12))
R.check(
    "closing the window releases the freeze through the same path",
    not _cv._vent_cusum.tripped and _cv._learning_frozen() is None,
    "the detector must be fed while frozen, or nothing can ever release it",
)

_cw = _vent_coord()
_feed_residual(_cw, 0.4, 10, _T4)
R.check(
    "ten warm intervals never look like a window",
    not _cw._vent_cusum.tripped and _cw._vent_cusum.stat == 0.0,
)

# The clip is half the threshold by construction, so no single glitched
# reading — however wild — can trip the detector alone.
R.check(
    "the per-sample clip is half the trip threshold",
    abs(VENT_CUSUM_CLIP_C - VENT_CUSUM_THRESHOLD_C / 2.0) < 1e-12,
)
_cg = _vent_coord()
_feed_residual(_cg, -10.0, 1, _T4)
R.check(
    "one glitched -10 °C reading cannot trip the detector alone",
    not _cg._vent_cusum.tripped,
    f"stat {_cg._vent_cusum.stat:.2f}: clipped to {VENT_CUSUM_CLIP_C}",
)
_feed_residual(_cg, -10.0, 2, _T4 + timedelta(hours=4))
R.check(
    "but a third consecutive one is a window, not a glitch",
    _cg._vent_cusum.tripped,
)

# While a stale sensor is what feeds the residual, the detector must not
# be driven by the flatline: staleness outranks ventilation, so the latch
# simply holds until real data returns.
_cs11 = _vent_coord()
_cs11._vent_cusum.tripped = True
_cs11._input_health = _NS(
    readings={"indoor_temp_entity": _NS(stale=True)}
)
R.check(
    "a stale sensor outranks the ventilation freeze for the feed path",
    _cs11._learning_frozen("indoor_temp_entity") == "stale:indoor_temp_entity"
    and _cs11._learning_frozen() == "ventilation",
    "a dead battery's flatline must not drive the very detector that "
    "froze everything",
)

# The gated relax rides the same snapshot-and-unwind envelope as the away
# setback and economy mode; the envelope carrying min_temp is what makes
# all three unwindable. Default-off byte-inertness is the goldens' job.
_ce = _vent_coord()
R.check(
    "the away snapshot carries min_temp, which is what unwinds the relax",
    "min_temp" in _ce._apply_away_setback(),
)
R.check(
    "the relax is one degree and can never pierce the absolute floor",
    OPEN_WINDOW_RELAX_C == 1.0
    and ECONOMY_ABSOLUTE_FLOOR >= 12.0,
)
# Wiring, pinned at the source level like the learner-ordering checks:
# the relax must be gated on its flag AND applied after the away
# snapshot, inside the same method, so the finally-restore unwinds it.
_run_src = inspect.getsource(_Coord.async_run_optimization)
R.check(
    "the relax sits behind its flag, after the away snapshot",
    0
    < _run_src.find("_apply_away_setback")
    < _run_src.find("CONF_OPEN_WINDOW_RELAX_ENABLED")
    < _run_src.find("OPEN_WINDOW_RELAX_C")
    and "_vent_cusum.tripped" in _run_src,
    "dropping the config gate or moving the relax outside the envelope "
    "must fail here, not in a February install",
)

# --- #11 the immersion detector -----------------------------------------------------
def _imm_coord(**cfg):
    c = _t2_coord(**cfg)
    c._current_action = {"power": 2.0}
    return c


_ci = _imm_coord()
_ci._measured_power = 6.0  # 1.20 x the 5.0 kW nameplate
_ci._detect_immersion()
R.check("one over-nameplate sample is a spike, not a latch", not _ci._immersion_active)
_ci._detect_immersion()
R.check(
    "two agreeing samples latch, with evidence and an event on record",
    _ci._immersion_active
    and _ci._immersion_evidence
    and len(_ci._immersion_events) == 1,
)
_ci._measured_power = 3.0
_ci._detect_immersion()
R.check("one clean sample does not release either", _ci._immersion_active)
_ci._detect_immersion()
R.check(
    "two clean samples release, and the event history stays",
    not _ci._immersion_active and len(_ci._immersion_events) == 1,
)

_cj = _imm_coord()
_cj._measured_power = 5.0 * IMMERSION_FACTOR * 0.98  # just under the line
_cj._detect_immersion()
_cj._detect_immersion()
R.check(
    "a draw just under nameplate x factor never latches",
    not _cj._immersion_active,
    "compressor spread must not read as a resistive element",
)
_ck0 = _imm_coord()
_ck0._measured_power = None
_ck0._detect_immersion()
_ck0._detect_immersion()
R.check("no meter, no detection", not _ck0._immersion_active)
_cl = _imm_coord()
_cl._measured_power = 6.0
_cl._detect_immersion()
_cl._measured_power = 3.0
_cl._detect_immersion()
_cl._measured_power = 6.0
_cl._detect_immersion()
R.check(
    "alternating samples never latch: the count demands consecutive evidence",
    not _cl._immersion_active,
)

# While latched, the COP learner must skip: a resistive kW in the ratio
# reads as catastrophic compressor efficiency.
_ck = _t2_coord()
_ck._current_state.outdoor_temperature = 10.0  # outside the frost band
_ck._current_action = {"power": 4.0}
_ck._measured_power = 4.0
_ck._immersion_active = True
_ck._learn_measured_cop()
R.check("an immersion interval never joins the COP learner", _ck._cop_samples == 0)
_ck._immersion_active = False
_ck._learn_measured_cop()
R.check(
    "the identical interval folds once the element is off — the guard is the "
    "only difference",
    _ck._cop_samples == 1,
)

# The gated feedback: recurring rescues raise the DHW planning margin.
_now_imm = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
_cm = _t2_coord(immersion_feedback_enabled=True)
_cm._immersion_events = [
    (_now_imm - timedelta(days=d)).isoformat() for d in (1, 3, 5)
]
R.check(
    "three rescues in a fortnight ask the plan for two extra degrees",
    _cm._immersion_dhw_margin(_now_imm) == 2.0,
)
_cm._immersion_events = _cm._immersion_events[:2]
R.check("two rescues do not", _cm._immersion_dhw_margin(_now_imm) == 0.0)
_cm._immersion_events = [
    (_now_imm - timedelta(days=d)).isoformat() for d in (20, 21, 22)
]
R.check(
    "old rescues age out of the window",
    _cm._immersion_dhw_margin(_now_imm) == 0.0,
)
_cn = _t2_coord()
_cn._immersion_events = [
    (_now_imm - timedelta(days=d)).isoformat() for d in (1, 3, 5)
]
R.check(
    "with the flag off the margin is always zero — the detector is",
    _cn._immersion_dhw_margin(_now_imm) == 0.0,
    "evidence-only until the user opts into moving the plan",
)

# And the margin genuinely moves a solve when set (mutation pair against
# the same flat-price scenario the quantile targets used).
def _m_solve(margin):
    sc = _mk_golden(
        dhw=True,
        price_profile="flat",
        config_overrides={"dhw_tank_volume": 1500.0},
        state_overrides={"dhw_temperature": 46.0},
        param_overrides={"dhw_ready_margin_c": margin},
    )
    return sc["optimizer"].optimize(
        sc["state"], sc["prices"], sc["outdoor"], sc["wind"], sc["rain"],
        sc["solar"], _G_START,
    )


R.check(
    "the margin's inert value IS the default, and an explicit zero solves "
    "byte-identically to it",
    ThermalParameters().dhw_ready_margin_c == 0.0
    and np.array_equal(
        np.asarray(_m_solve(0.0).dhw_power_schedule),
        np.asarray(_q_base.dhw_power_schedule),
    ),
    "the pre-T4a baseline itself is golden.py's pin, not this check's",
)
_m2 = _m_solve(2.0)
R.check(
    "two degrees of margin heat the tank higher before the window",
    max(_m2.dhw_temp_trajectory[:25])
    > max(_q_base.dhw_temp_trajectory[:25]) + 0.5,
    f"pre-window peak {max(_q_base.dhw_temp_trajectory[:25]):.1f} -> "
    f"{max(_m2.dhw_temp_trajectory[:25]):.1f}",
)

# The ledger carve-out: the immersion line comes OUT of spot, so the
# month's lines sum to the metered energy instead of overstating it.
_cl2 = _t2_coord()
_cl2._immersion_active = True
_lsample = AccuracySample(when=NOW, actual_power_kw=6.9)
_lpending = {
    "price": 2.5,
    "spot_price": 2.0,
    "grid_fee": 0.5,
    "space_power": 1.0,
    "dhw_power": 1.0,
    "when": NOW,
}
_cl2._accumulate_energy(_lsample, 0.5, _lpending)
_lmonth = NOW.strftime("%Y-%m")
_lspot = _cl2._ledger.line(_lmonth, "spot")
_limm = _cl2._ledger.line(_lmonth, "immersion")
_lfee = _cl2._ledger.line(_lmonth, "grid_fee")
R.check(
    "the immersion kWh are carved out of spot, and the lines sum to the "
    "metered energy",
    abs(_limm["kwh"] - 2.45) < 1e-9
    and abs(_lspot["kwh"] + _limm["kwh"] - 3.45) < 1e-9
    and abs(_lfee["kwh"] - 3.45) < 1e-9,
    f"spot {_lspot['kwh']:.2f} + immersion {_limm['kwh']:.2f} must equal "
    "the 3.45 kWh metered; the fee line keeps the full energy",
)
import homeassistant.util.dt as _dt_mod_led

_real_now_led = _dt_mod_led.now
try:
    _dt_mod_led.now = lambda: NOW  # the settlement reads "this month"
    _settled_kwh = _cl2._contract_comparison()["kwh"]
finally:
    _dt_mod_led.now = _real_now_led
R.check(
    "the contract settlement folds the carved-out kWh back in",
    abs(_settled_kwh - 3.45) < 1e-3,
    "the comparison settles ALL metered energy, however it is lined",
)
_cl3 = _t2_coord()
_cl3._accumulate_energy(_lsample, 0.5, dict(_lpending))
R.check(
    "with the element off the spot line carries everything and no "
    "immersion line appears",
    abs(_cl3._ledger.line(_lmonth, "spot")["kwh"] - 3.45) < 1e-9
    and _cl3._ledger.line(_lmonth, "immersion")["kwh"] == 0.0,
)

# --- #12 the compressor-health watch --------------------------------------------------
_ch = _t2_coord()
_ch._current_state.outdoor_temperature = 9.5  # bucket 3, outside frost
for _ in range(COP_BASELINE_MIN_SAMPLES + 5):
    _ch._observe_cop_health(3.0)
R.check(
    "the baseline forms in its outdoor bucket and trips nothing on itself",
    _ch._cop_baseline.get(3, [0, 0])[1] >= COP_BASELINE_MIN_SAMPLES
    and not _ch._cop_health_cusum.tripped,
)
_ch._last_measured_cop = 2.4
_trip_n = None
for i in range(12):
    _ch._observe_cop_health(2.4)
    if _ch._cop_health_cusum.tripped:
        _trip_n = i + 1
        break
_cop_issues = [
    i for i in getattr(_ch.hass, "issues", []) if i[1] == "cop_degradation"
]
R.check(
    "a 20% shortfall trips within a handful of samples and raises the issue",
    _trip_n is not None and _trip_n <= 8 and len(_cop_issues) == 1,
    f"tripped after {_trip_n} samples",
)
R.check(
    "the issue prices the shortfall for the user and survives a restart",
    _cop_issues[0][2].get("translation_key") == "cop_degradation"
    and set(_cop_issues[0][2].get("translation_placeholders", {}))
    == {"shortfall_percent", "sek_month"}
    and _cop_issues[0][2].get("is_persistent") is True,
    "a non-persistent issue vanishes on reboot while the fault stays",
)
_baseline_at_trip = _ch._cop_baseline[3][0]
for _ in range(5):
    _ch._observe_cop_health(2.4)
R.check(
    "staying degraded keeps exactly one issue, not a pile",
    len([
        i for i in getattr(_ch.hass, "issues", []) if i[1] == "cop_degradation"
    ]) == 1,
)
R.check(
    "the baseline stops absorbing samples while tripped",
    _ch._cop_baseline[3][0] == _baseline_at_trip,
    "otherwise the EWMA re-anchors to the fault and a permanent "
    "degradation clears its own issue within weeks",
)
for _ in range(40):
    _ch._observe_cop_health(3.2)
    if not _ch._cop_health_cusum.tripped:
        break
R.check(
    "recovery releases the watch and deletes the issue",
    not _ch._cop_health_cusum.tripped
    and not [
        i for i in getattr(_ch.hass, "issues", []) if i[1] == "cop_degradation"
    ],
    "a repair issue that outlives its problem trains users to ignore repairs",
)

_ch2 = _t2_coord()
_ch2._current_state.outdoor_temperature = 9.5
for _ in range(COP_BASELINE_MIN_SAMPLES + 5):
    _ch2._observe_cop_health(3.0)
for i in range(40):
    _ch2._observe_cop_health(2.97 if i % 2 else 3.03)
R.check(
    "spread inside the drift allowance never trips the watch",
    not _ch2._cop_health_cusum.tripped and _ch2._cop_health_cusum.stat < 0.1,
    "session-to-session COP noise is not degradation",
)

_ch3 = _t2_coord()
_ch3._current_state.outdoor_temperature = 9.5
_ch3._observe_cop_health(9.0)  # one wild first interval
for _ in range(24):
    _ch3._observe_cop_health(3.0)
R.check(
    "one outlier first sample cannot anchor the young baseline",
    _ch3._cop_baseline[3][0] < 3.5,
    f"got {_ch3._cop_baseline[3][0]:.2f}: a plain mean while young; an "
    "EWMA seeded at 9.0 would still read ~6.7 when the watch starts "
    "judging at twenty samples",
)

# Frost-band disjointness: the health watch is fed only through
# _learn_measured_cop, which hands the frost band to the defrost learner.
_cf = _t2_coord()
_cf._current_state.outdoor_temperature = 2.0
_cf._current_action = {"power": 4.0}
_cf._measured_power = 4.0
_cf._learn_measured_cop()
R.check(
    "a frost-band interval reaches neither the COP learner nor the baseline",
    _cf._cop_samples == 0 and not _cf._cop_baseline,
    "the defrost derate owns that band; feeding both corrects one loss twice",
)

# --- #42 snapshots: the ring and the alarm -------------------------------------------
_ring = SnapshotRing()
_taken = 0
for d in range(120):
    _rnow = _T4 + timedelta(days=d)
    if _ring.due(_rnow):
        _ring.take(
            _rnow,
            {"thermal": {"scale": 1.0 + d / 100.0}},
            {"temperature_bias": 0.1},
            healthy=True,
        )
        _taken += 1
R.check(
    "snapshots are weekly and the ring keeps eight",
    _taken == 18 and len(_ring.snapshots) == RING_SIZE,
    f"{_taken} takes, {len(_ring.snapshots)} kept",
)
_r2 = SnapshotRing()
_r2.take(_T4, {"thermal": {"scale": 1.0}}, {"temperature_bias": 0.1}, True)
_flags = [
    _r2.observe_bias(_T4 + timedelta(days=d), 0.9, healthy=True)
    for d in range(1, 7)
]
R.check(
    "five consecutive out-of-band days raise the alarm exactly once",
    _r2.alarmed and _flags.count(True) == 1 and _flags[BIAS_TRIP_DAYS - 1],
    f"flags {_flags}",
)
R.check(
    "healthy inputs throughout justify the automatic rollback",
    _r2.auto_rollback_justified,
)
_r3 = SnapshotRing()
for d in range(1, 7):
    _r3.observe_bias(_T4 + timedelta(days=d), 0.9, healthy=(d != 3))
R.check(
    "one unhealthy day keeps the alarm but blocks auto-rollback",
    _r3.alarmed and not _r3.auto_rollback_justified,
    "if the sensors were the problem, the learners are innocent",
)
_r4 = SnapshotRing()
for _ in range(10):
    _r4.observe_bias(_T4, 0.9, True)
R.check("the alarm counts days, not ticks", not _r4.alarmed)
_r5 = SnapshotRing()
_r5.take(_T4, {"a": 1}, {"temperature_bias": 0.1}, healthy=True)
_r5.take(_T4 + timedelta(days=7), {"a": 2}, {"temperature_bias": 0.9}, True)
_r5.take(_T4 + timedelta(days=14), {"a": 3}, {"temperature_bias": 0.1}, False)
R.check(
    "restore picks the newest healthy, in-band snapshot",
    (_r5.best_restore() or {}).get("learners") == {"a": 1},
    "restoring to a drifting snapshot rewinds the clock on the problem",
)
_r6 = SnapshotRing.from_dict(_r2.as_dict())
R.check(
    "the ring round-trips its alarm latch and history",
    _r6.alarmed
    and len(_r6.snapshots) == 1
    and SnapshotRing.from_dict({"snapshots": "garbage"}).snapshots == [],
)
_r7 = SnapshotRing()
_live = {"thermal": {"scale": 1.0}}
_r7.take(_T4, _live, {"temperature_bias": 0.1}, True)
_live["thermal"]["scale"] = 999.0
R.check(
    "a snapshot is a copy, never a window into live learner state",
    _r7.snapshots[0]["learners"]["thermal"]["scale"] == 1.0,
    "an aliased snapshot mutates for eight weeks and restores the very "
    "drift it was taken to undo",
)
_r8 = SnapshotRing()
_r8.alarmed = True
_r8.take(_T4, {"a": 1}, {"temperature_bias": 0.1}, healthy=True)
R.check(
    "a snapshot taken during an active alarm never enters the restore pool",
    _r8.best_restore() is None,
    "it can only hold state the alarm already distrusts",
)
# Slow drift: the learners walk away days before the bias tag leaves the
# band, so during an alarm only snapshots older than the streak qualify.
_r9 = SnapshotRing()
_r9.take(_T4 - timedelta(days=10), {"good": True}, {"temperature_bias": 0.1}, True)
_r9.observe_bias(_T4 + timedelta(days=1), 0.9, True)  # streak starts day 1
_r9.take(_T4 + timedelta(days=3), {"good": False}, {"temperature_bias": 0.3}, True)
for d in range(2, 6):
    _r9.observe_bias(_T4 + timedelta(days=d), 0.9, True)
R.check(
    "during an alarm, restore skips snapshots taken inside the drift streak",
    _r9.alarmed
    and (_r9.best_restore() or {}).get("learners") == {"good": True},
    "the day-3 snapshot's in-band tag is not proof of innocence",
)
R.check(
    "the streak marker rides the store round trip",
    SnapshotRing.from_dict(_r9.as_dict())._streak_started
    == _r9._streak_started
    and _r9._streak_started != "",
)

# --- #42 through the coordinator: drift, rollback, restore -----------------------------
def _drift_run(unhealthy_day=None):
    """Take a clean snapshot, corrupt a learned value, drive 5 drift days."""
    import homeassistant.util.dt as _dt_mod

    c = _t2_coord()
    c._snapshots_loaded = True  # the store gate; loading is its own check
    c._apply_house_heat_loss_scale(1.0)
    c._accuracy.temperature_bias = lambda: 0.05
    base = datetime(2026, 3, 1, 3, 0, tzinfo=UTC)
    real_now = _dt_mod.now
    try:
        _dt_mod.now = lambda: base
        _asyncio.run(c._async_watch_learning_drift())  # day 0: weekly take
        c._apply_house_heat_loss_scale(1.4)
        c._accuracy.temperature_bias = lambda: 0.9
        for d in range(1, 6):
            if d == unhealthy_day:
                c._inputs_healthy = lambda: False
            _dt_mod.now = lambda d=d: base + timedelta(days=d)
            _asyncio.run(c._async_watch_learning_drift())
            if d == unhealthy_day:
                del c._inputs_healthy
    finally:
        _dt_mod.now = real_now
    return c


_cd = _drift_run()
_drift_issues = [
    i for i in getattr(_cd.hass, "issues", []) if i[1] == "accuracy_drift"
]
R.check(
    "five out-of-band days on healthy inputs roll the learners back",
    _cd._house_heat_loss_scale == 1.0 and _cd._snapshot_ring.alarmed,
    f"scale {_cd._house_heat_loss_scale}",
)
R.check(
    "and the issue says so, in the rolled-back voice",
    len(_drift_issues) == 1
    and _drift_issues[0][2].get("translation_key") == "accuracy_drift_rolled_back",
)
R.check(
    "the rollback leaves the accuracy tracker alone — it is evidence",
    _cd._accuracy.temperature_bias() == 0.9,
    "restoring the tracker made the rollback erase its own justification "
    "and repeat until a drifted snapshot laundered itself in",
)
_cd._apply_house_heat_loss_scale(1.4)
import homeassistant.util.dt as _dt_mod_t4

_real_now_t4 = _dt_mod_t4.now
try:
    _dt_mod_t4.now = lambda: datetime(2026, 3, 7, 3, 0, tzinfo=UTC)
    _asyncio.run(_cd._async_watch_learning_drift())
finally:
    _dt_mod_t4.now = _real_now_t4
R.check(
    "one alarm rolls back once — staying alarmed must not re-restore daily",
    _cd._house_heat_loss_scale == 1.4,
    "a daily rollback would fight every attempt to relearn",
)
R.check(
    "the alarm stays latched while the bias stays out of band",
    _cd._snapshot_ring.alarmed
    and [
        i for i in getattr(_cd.hass, "issues", []) if i[1] == "accuracy_drift"
    ][0][2].get("is_persistent") is True,
    "no self-release, and the notice survives a Home Assistant restart",
)

_cd2 = _drift_run(unhealthy_day=3)
_drift_issues2 = [
    i for i in getattr(_cd2.hass, "issues", []) if i[1] == "accuracy_drift"
]
R.check(
    "one unhealthy drift day raises the alarm but leaves the learners alone",
    _cd2._house_heat_loss_scale == 1.4
    and len(_drift_issues2) == 1
    and _drift_issues2[0][2].get("translation_key") == "accuracy_drift",
)

_cr = _t2_coord()
R.check(
    "restore with an empty ring refuses instead of pretending",
    _asyncio.run(_cr.async_restore_learned_snapshot()) is False,
)
_cr._apply_house_heat_loss_scale(1.0)
# Profiles are mean-1 weight vectors; this shape survives normalization.
_cr._dhw_profile_weekend = [1.5] * 12 + [0.5] * 12
_cr._dhw_daytype_samples[1] = 9
_cr._snapshot_ring.take(
    NOW, _cr._learner_snapshot_payloads(), {"temperature_bias": 0.1}, True
)
_cr._apply_house_heat_loss_scale(1.5)
_cr._dhw_daytype_samples[1] = 0
_cr._dhw_profile_weekend = [0.5] * 12 + [1.5] * 12
R.check(
    "the service applies the newest qualifying snapshot",
    _asyncio.run(_cr.async_restore_learned_snapshot()) is True
    and _cr._house_heat_loss_scale == 1.0,
)
R.check(
    "the day-type profiles restore with the pool, samples included",
    _cr._dhw_daytype_samples[1] == 9
    and abs(_cr._dhw_profile_weekend[0] - 1.5) < 1e-9,
    "half a rollback would blend one week's pool with another's shapes",
)
R.check(
    "the restored defrost derate is rebound where the model reads it",
    _cr._thermal_params.defrost_derate is _cr._defrost,
    "without the rebind the restored object trains while an orphan serves",
)
R.check(
    "the snapshot serialises the DHW profile through the store's own producer",
    "profile_weekday" in inspect.getsource(_Coord._dhw_profile_payload)
    and "_dhw_profile_payload"
    in inspect.getsource(_Coord._async_save_dhw_profile)
    and "_dhw_profile_payload"
    in inspect.getsource(_Coord._learner_snapshot_payloads),
    "a second hand-built copy is how formats drift",
)

# The heartbeat gates on the persisted ring having loaded (the first
# cycle must not snapshot half-loaded learners over eight weeks of
# insurance), and a counted day persists the streak even when nothing
# else changed.
_cg2 = _t2_coord()
_asyncio.run(_cg2._async_watch_learning_drift())
R.check(
    "no snapshot is taken before the persisted ring has loaded",
    not _cg2._snapshot_ring.snapshots,
)
_asyncio.run(_cg2._async_load_snapshots())
R.check(
    "the loader arms the heartbeat even when the store is empty",
    _cg2._snapshots_loaded,
)
_cg3 = _t2_coord()
_cg3._snapshots_loaded = True
_cg3._snapshot_ring.take(NOW, {}, {"temperature_bias": 0.1}, True)
_cg3._accuracy.temperature_bias = lambda: 0.9
_ring_saves = []


async def _fake_ring_save():
    _ring_saves.append(1)


_cg3._async_save_snapshots = _fake_ring_save
import homeassistant.util.dt as _dt_mod_t4b

_real_now_t4b = _dt_mod_t4b.now
try:
    _dt_mod_t4b.now = lambda: NOW + timedelta(days=1)
    _asyncio.run(_cg3._async_watch_learning_drift())  # day counted
    _asyncio.run(_cg3._async_watch_learning_drift())  # same day, no count
finally:
    _dt_mod_t4b.now = _real_now_t4b
R.check(
    "each counted drift day persists the streak, once",
    len(_ring_saves) == 1 and _cg3._snapshot_ring._bias_days == 1,
    "a restart on drift day 3 must not rewind the count to the last "
    "weekly save",
)

# --- persistence: the detectors' memory rides the thermal store ----------------------
_cp = _t2_coord()
_cp._vent_cusum.stat = 0.66
_cp._vent_cusum.tripped = True
_cp._cop_baseline[3] = [3.0, 25]
_cp._immersion_events = ["2026-01-01T00:00:00+00:00"]
_t4_payload = _cp._thermal_learning_payload()
_cq = _t2_coord()


async def _fake_thermal_load(_p=_t4_payload):
    return _p


_cq._thermal_learning_store.async_load = _fake_thermal_load
_asyncio.run(_cq._async_load_thermal_learning())
R.check(
    "a tripped window detector survives a restart tripped",
    _cq._vent_cusum.tripped and abs(_cq._vent_cusum.stat - 0.66) < 1e-3,
    "a restart mid-window must not unfreeze the learners",
)
R.check(
    "the COP baseline and the immersion history ride along",
    _cq._cop_baseline.get(3) == [3.0, 25]
    and _cq._immersion_events == ["2026-01-01T00:00:00+00:00"],
)
_cq2 = _t2_coord()


async def _fake_old_load():
    return {"house_heat_loss_scale": 1.2}


_cq2._thermal_learning_store.async_load = _fake_old_load
_asyncio.run(_cq2._async_load_thermal_learning())
R.check(
    "a pre-T4 payload loads clean and every detector starts quiet",
    _cq2._house_heat_loss_scale == 1.2
    and not _cq2._vent_cusum.tripped
    and not _cq2._cop_baseline
    and _cq2._immersion_events == [],
)

# --- the accuracy sample's new field --------------------------------------------------
_smp = AccuracySample(
    when=NOW, predicted_temp=21.0, actual_temp=20.8, cop_residual=0.3
)
R.check(
    "cop_residual survives the sample's store round trip",
    AccuracySample.from_dict(_smp.as_dict()).cop_residual == 0.3,
)
R.check(
    "an old sample without the key still loads, as None",
    AccuracySample.from_dict({"t": NOW.isoformat()}).cop_residual is None,
)

# ===========================================================================
# T4b — model & learning, part two (#21 #30 #17 #36 #53 #2)
# ===========================================================================
R.section("T4b — weather inputs and learners (#21 #30 #17 #36 #53 #2)")

from heatpump_optimizer.const import (
    CAPACITY_FLOOR_FRACTION,
    CAPACITY_MIN_SAMPLES,
    INTERNAL_GAINS_MAX_FACTOR,
    SNOW_HEAVY_CM,
    SNOW_ROOF_DAYS,
    SOLAR_APERTURE_MAX,
    SOLAR_APERTURE_MIN_SAMPLES,
)
from heatpump_optimizer.curve_learning import (
    BIAS_MIN,
    COMFORT_MARGIN_C,
    DAYS_PER_STEP,
    STEP_K,
    CurveLearner,
)
from heatpump_optimizer.defrost import DefrostDerate

# --- #21 the humidity threading ------------------------------------------------
# A derate with full-trust factors: 0.6 in the humid frost bucket, un-
# touched (1.0) in the dry one, so the lookup's bucket choice is visible
# in the COP itself.
_dr = DefrostDerate()
_dr.factors[2][1] = 0.6
_dr.counts[2][1] = 20
# The deep-cold bucket too, so the winter-day solve below — which never
# leaves -16..-8 °C — has a humid penalty to react to.
_dr.factors[0][1] = 0.6
_dr.counts[0][1] = 20
_tm21 = ThermalModel(ThermalParameters(defrost_derate=_dr, ambient_humidity=40.0))
R.check(
    "the forecast humidity selects the derate bucket per step",
    abs(_tm21.compute_cop(1.0, humidity=90.0) / _tm21.compute_cop(1.0, humidity=40.0) - 0.6)
    < 1e-9,
)
R.check(
    "NaN humidity falls back exactly like an absent argument",
    _tm21.compute_cop(1.0, humidity=float("nan")) == _tm21.compute_cop(1.0)
    and _tm21.compute_cop(1.0) == _tm21.compute_cop(1.0, humidity=40.0),
    "the ambient value, never the 0-100 bucket a coerced NaN would pick",
)
_st21 = ThermalState(room_temperature=20.0, outdoor_temperature=1.0)
R.check(
    "the step simulation carries the humidity into the physics",
    _tm21.simulate_step(_st21, 3.0, 1.0, humidity=90.0).slab_temperature
    < _tm21.simulate_step(_st21, 3.0, 1.0, humidity=40.0).slab_temperature,
    "0.6 x the COP is 0.6 x the delivered heat",
)

# With NO defrost evidence the humidity series is inert by construction:
# the same solve, with and without a full humidity array, byte for byte.
_h21 = _mk_golden(dhw=True)
_hum_arr = np.full(len(_h21["prices"]), 85.0)
_r_dry = _h21["optimizer"].optimize(
    _h21["state"], _h21["prices"], _h21["outdoor"], _h21["wind"], _h21["rain"],
    _h21["solar"], _G_START,
)
_h21b = _mk_golden(dhw=True)
_r_hum = _h21b["optimizer"].optimize(
    _h21b["state"], _h21b["prices"], _h21b["outdoor"], _h21b["wind"],
    _h21b["rain"], _h21b["solar"], _G_START, humidity=_hum_arr,
)
R.check(
    "with zero defrost samples the humidity series changes nothing",
    np.array_equal(
        np.asarray(_r_dry.power_schedule), np.asarray(_r_hum.power_schedule)
    )
    and np.array_equal(
        np.asarray(_r_dry.dhw_power_schedule),
        np.asarray(_r_hum.dhw_power_schedule),
    ),
    "the derate is 1.0 everywhere, so #21 ships ungated",
)
_h21c = _mk_golden(
    dhw=True,
    param_overrides={"defrost_derate": _dr, "ambient_humidity": 40.0},
)
_r_derate = _h21c["optimizer"].optimize(
    _h21c["state"], _h21c["prices"], _h21c["outdoor"], _h21c["wind"],
    _h21c["rain"], _h21c["solar"], _G_START, humidity=_hum_arr,
)
_h21d = _mk_golden(
    dhw=True,
    param_overrides={"defrost_derate": _dr, "ambient_humidity": 40.0},
)
_r_ambient = _h21d["optimizer"].optimize(
    _h21d["state"], _h21d["prices"], _h21d["outdoor"], _h21d["wind"],
    _h21d["rain"], _h21d["solar"], _G_START,
)
R.check(
    "with real defrost evidence a humid forecast reshapes the plan",
    not np.array_equal(
        np.asarray(_r_derate.power_schedule),
        np.asarray(_r_ambient.power_schedule),
    ),
    "the winter day crosses the frost band, where the humid bucket bites",
)

# --- #30 the roof-snow memory ----------------------------------------------------
import homeassistant.util.dt as _dt_snow

_c30 = _t2_coord()
_heavy = np.full(4, 1.0)  # 1 cm/h at the current step
_real_now_snow = _dt_snow.now
_snow_t0 = datetime(2026, 1, 20, 6, 0, tzinfo=UTC)
try:
    _dt_snow.now = lambda: _snow_t0
    R.check(
        "with the flag off the snow memory never engages and never mutates",
        not _c30._update_snow_memory(_snow_t0, _heavy)
        and _c30._snow_accum_last is None,
    )
    _c31 = _t2_coord(snow_roof_factor_enabled=True)
    _c31._update_snow_memory(_snow_t0, _heavy)  # seeds the clock
    _damped = _c31._update_snow_memory(
        _snow_t0 + timedelta(hours=3), _heavy
    )
    R.check(
        "three hours of heavy snowfall cross the trip line and damp the sun",
        _damped and _c31._snow_accum_cm >= SNOW_HEAVY_CM,
        f"accumulated {_c31._snow_accum_cm:.1f} cm",
    )
    R.check(
        "the roof is assumed clear again after the holding period",
        not _c31._update_snow_memory(
            _snow_t0 + timedelta(days=SNOW_ROOF_DAYS, hours=4), np.zeros(4)
        ),
    )
finally:
    _dt_snow.now = _real_now_snow

# --- #17 the capacity envelope ------------------------------------------------------
_c17 = _t2_coord(capacity_curve_enabled=True)
_c17._current_state.outdoor_temperature = -10.0  # bucket -4
_c17._current_action = {"power": 5.0}  # commanded at nameplate
_c17._measured_power = 4.0
for _ in range(CAPACITY_MIN_SAMPLES + 2):
    _c17._fold_capacity_envelope(2.0)  # 8 kW thermal delivered
_bucket = int(np.floor(-10.0 / 3.0))
R.check(
    "the envelope remembers the most heat the bucket has delivered",
    abs(_c17._capacity_envelope[_bucket][0] - 8.0) < 1e-6
    and _c17._capacity_envelope[_bucket][1] == CAPACITY_MIN_SAMPLES + 2,
)
_caps17 = _c17._capacity_caps(np.array([-10.0, -10.0, 15.0]))
_cop_cold = _c17._thermal_model.compute_cop(-10.0)
_exp_cap = float(np.clip(8.0 / _cop_cold, CAPACITY_FLOOR_FRACTION * 5.0, 5.0))
R.check(
    "a sampled bucket caps to its envelope at that step's own COP",
    _caps17 is not None
    and abs(_caps17[0] - _exp_cap) < 1e-6
    and _caps17[2] == 5.0,
    "the unsampled 15 °C bucket must stay at nameplate",
)
_c17._capacity_envelope[_bucket][0] = 0.5  # absurdly weak evidence
R.check(
    "the cap can never starve the house below the nameplate floor",
    _c17._capacity_caps(np.array([-10.0]))[0]
    >= CAPACITY_FLOOR_FRACTION * 5.0 - 1e-9,
    "a starved house at -15 °C is this program's worst failure mode",
)
_c17._capacity_envelope[_bucket][1] = CAPACITY_MIN_SAMPLES - 1
R.check(
    "an under-sampled bucket caps nothing at all",
    _c17._capacity_caps(np.array([-10.0])) is None,
)
_c18 = _t2_coord()
_c18._measured_power = 4.0
_c18._current_action = {"power": 5.0}
_c18._current_state.outdoor_temperature = -10.0
_c18._fold_capacity_envelope(3.0)
R.check(
    "with the flag off the envelope neither learns nor caps",
    not _c18._capacity_envelope and _c18._capacity_caps(np.array([-10.0])) is None,
)
_c19 = _t2_coord(capacity_curve_enabled=True)
_c19._current_state.outdoor_temperature = -10.0
_c19._measured_power = 2.0
_c19._current_action = {"power": 2.0}  # 40% duty: censored, not evidence
_c19._fold_capacity_envelope(3.0)
R.check(
    "partial-load intervals are censored, never envelope evidence",
    not _c19._capacity_envelope,
    "the caps limit the plan and the plan limits the samples; folding "
    "partial load would ratchet every active bucket down to the floor",
)
R.check(
    "the envelope composes through caps_extra, never a second channel",
    "np.minimum(caps_extra, env_caps)"
    in inspect.getsource(_Coord.async_run_optimization),
)

# --- #36 the solar aperture -------------------------------------------------------
_c36 = _t2_coord(solar_aperture_learning_enabled=True)
_st36 = replace(_c36._current_state)
_cap36 = _c36._thermal_params.room_thermal_mass
_random.seed(11)
# Closed loop, exactly as the coordinator runs it: the residual is what
# remains AFTER the current scale is applied in the simulation, and the
# irradiance varies — a constant sun carries no slope information at all.
for _ in range(SOLAR_APERTURE_MIN_SAMPLES * 6):
    _irr = _random.uniform(200.0, 800.0)
    _st36.solar_radiation = _irr
    _x = _c36._thermal_model.compute_solar_gain(_irr)
    _scale_now = _c36._solar_aperture["scale"]
    _res = ((1.5 - _scale_now) * _x + _random.gauss(0.0, 0.05)) * 0.5 / _cap36
    _c36._fold_solar_aperture(_st36, _res, 0.5)
R.check(
    "the aperture regression converges on the true scale",
    abs(_c36._solar_aperture["scale"] - 1.5) < 0.15,
    f"learned {_c36._solar_aperture['scale']:.2f}, truth 1.5",
)
_c36x = _t2_coord(solar_aperture_learning_enabled=True)
_st36x = replace(_c36x._current_state)
for _ in range(SOLAR_APERTURE_MIN_SAMPLES * 4):
    _irr = _random.uniform(200.0, 800.0)
    _st36x.solar_radiation = _irr
    _x = _c36x._thermal_model.compute_solar_gain(_irr)
    _c36x._fold_solar_aperture(_st36x, 10.0 * _x * 0.5 / _cap36, 0.5)
R.check(
    "an absurd slope pins at the clamp instead of running away",
    _c36x._solar_aperture["scale"] == SOLAR_APERTURE_MAX,
)
_c37 = _t2_coord(solar_aperture_learning_enabled=True)
_st37 = replace(_c37._current_state)
_st37.solar_radiation = 50.0  # below the information threshold
for _ in range(100):
    _c37._fold_solar_aperture(_st37, 0.4, 0.5)
R.check(
    "dim steps carry no aperture information and never move the scale",
    _c37._solar_aperture["n"] == 0.0 and _c37._solar_aperture["scale"] == 1.0,
)
_c38 = _t2_coord()
_st38 = replace(_c38._current_state)
_st38.solar_radiation = 400.0
_c38._fold_solar_aperture(_st38, 0.4, 0.5)
R.check(
    "with the flag off the aperture learner is inert",
    _c38._solar_aperture["n"] == 0.0,
)
R.check(
    "the aperture scale multiplies the solar gain, and 1.0 is byte-inert",
    abs(
        ThermalModel(
            ThermalParameters(solar_aperture_scale=1.5)
        ).compute_solar_gain(400.0)
        - 1.5 * ThermalModel(ThermalParameters()).compute_solar_gain(400.0)
    )
    < 1e-12,
)

# --- #53 the internal-gains profile ---------------------------------------------
_tm53 = ThermalModel(
    ThermalParameters(internal_gains_profile=[0.3] * 18 + [0.9] * 6)
)
R.check(
    "the per-hour profile answers its hour, and None answers the constant",
    _tm53.internal_gains_at(19.5) == 0.9
    and _tm53.internal_gains_at(3.0) == 0.3
    and ThermalModel(ThermalParameters()).internal_gains_at(19.5)
    == ThermalParameters().internal_gains,
)
_st53 = ThermalState(room_temperature=20.0, outdoor_temperature=0.0)
R.check(
    "the evening bump reaches the simulated physics",
    _tm53.simulate_step(_st53, 0.0, 0.0, hour_of_day=19.5).room_temperature
    > _tm53.simulate_step(_st53, 0.0, 0.0, hour_of_day=3.0).room_temperature,
)
_c53 = _t2_coord(internal_gains_learning_enabled=True)
_st53d = replace(_c53._current_state)
_st53d.solar_radiation = 0.0
_g0 = _c53._thermal_params.internal_gains
_when53 = datetime(2026, 1, 15, 19, 10, tzinfo=UTC)
for _ in range(60):
    # Consistently warmer than predicted at 19:00, in the dark.
    _c53._fold_internal_gains(_when53, _st53d, 0.1, 0.5)
R.check(
    "a warm evening hour learns extra gains, tethered under the cap",
    _c53._internal_gains_profile is not None
    and _c53._internal_gains_profile[19] > _g0 + 0.1
    and _c53._internal_gains_profile[19]
    <= INTERNAL_GAINS_MAX_FACTOR * _g0 + 1e-9
    and _c53._internal_gains_profile[3] == _g0,
    f"hour 19 learned {_c53._internal_gains_profile[19]:.2f} vs prior {_g0}",
)
_before53 = _c53._internal_gains_profile[19]
for _ in range(200):
    _c53._fold_internal_gains(_when53, _st53d, 0.0, 0.5)
R.check(
    "with the evidence gone the ridge pulls the hour back toward the prior",
    _c53._internal_gains_profile[19] < _before53
    and _c53._internal_gains_profile[19] < _g0 + 0.05,
)
_st53s = replace(_c53._current_state)
_st53s.solar_radiation = 300.0
_h3_before = _c53._internal_gains_profile[3]
_c53._fold_internal_gains(
    datetime(2026, 1, 15, 3, 10, tzinfo=UTC), _st53s, 0.5, 0.5
)
R.check(
    "sunny intervals are the aperture learner's business, never this one's",
    _c53._internal_gains_profile[3] == _h3_before,
)
_c54 = _t2_coord()
_c54._fold_internal_gains(_when53, _st53d, 0.1, 0.5)
R.check(
    "with the flag off no profile ever forms",
    _c54._internal_gains_profile is None,
)

# --- #2 the heat-curve bias -------------------------------------------------------
_cl_t4 = CurveLearner()
_d2 = datetime(2026, 1, 10, 23, 0, tzinfo=UTC)
for d in range(DAYS_PER_STEP):
    _cl_t4.record_day(_d2 + timedelta(days=d), 1.0)
R.check(
    "three comfortable days step the bias down by one notch",
    abs(_cl_t4.bias + STEP_K) < 1e-9,
    f"bias {_cl_t4.bias}",
)
for d in range(DAYS_PER_STEP):
    _cl_t4.record_day(_d2 + timedelta(days=DAYS_PER_STEP + d), 1.0)
R.check(
    "the weekly rate cap slows further steps below the notch size",
    -0.5 < _cl_t4.bias < -STEP_K,
    f"bias {_cl_t4.bias:.3f}: 3 days at 0.5 K/week allows ~0.21 K, not 0.4",
)
_cl_t4.record_day(_d2 + timedelta(days=20), -0.2)
R.check(
    "one comfort miss surrenders the whole bias on the spot",
    _cl_t4.bias == 0.0 and _cl_t4.resets == 1,
    "a learner that undershoots comfort and negotiates about it has "
    "chosen the wrong failure mode",
)
_cl2_t4 = CurveLearner()
for d in range(10):
    _cl2_t4.record_day(_d2 + timedelta(days=d), COMFORT_MARGIN_C / 2.0)
R.check(
    "days that held with nothing to spare are no evidence either way",
    _cl2_t4.bias == 0.0 and _cl2_t4.comfortable_days == 0,
)
_cl3_t4 = CurveLearner()
for _ in range(10):
    _cl3_t4.record_day(_d2, 1.0)
R.check("the curve learner counts days, not ticks", _cl3_t4.comfortable_days == 1)
_cl4_t4 = CurveLearner.from_dict(_cl_t4.as_dict())
R.check(
    "the bias and its evidence survive the store round trip",
    _cl4_t4.bias == _cl_t4.bias and _cl4_t4.resets == 1
    and CurveLearner.from_dict({"bias": -99}).bias == BIAS_MIN,
)

# The wiring: the bias joins the displace before the configured clamp,
# only when the flag is on, and never moves the plan itself.
_c2 = _t2_coord(curve_learning_enabled=True)
_c2._curve_learner.bias = -2.0
_asyncio.run(_c2.async_publish_ecl110_command(5.0, True))
R.check(
    "the published displace carries the learned bias",
    _c2._ecl110_current_displace == 3.0,
)
_c2b = _t2_coord()
_c2b._curve_learner.bias = -2.0
_asyncio.run(_c2b.async_publish_ecl110_command(5.0, True))
R.check(
    "with the flag off the installer's curve is published untouched",
    _c2b._ecl110_current_displace == 5.0,
)
_c2c = _t2_coord(curve_learning_enabled=True)
_c2c._current_state.room_temperature = 21.5
_c2c._track_curve_comfort(datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
_c2c._current_state.room_temperature = 20.2
_c2c._track_curve_comfort(datetime(2026, 1, 15, 18, 0, tzinfo=UTC))
_floor_now = float(_c2c._opt_config.get_temp_bounds(18.0)[0])
R.check(
    "the day's evidence is the WORST margin, not the last one",
    _c2c._curve_day_worst is not None
    and abs(_c2c._curve_day_worst - (20.2 - _floor_now)) < 1e-9,
)
_c2c._curve_learner.bias = -1.0
_c2c._current_state.room_temperature = _floor_now - 0.1
_c2c._track_curve_comfort(datetime(2026, 1, 15, 19, 0, tzinfo=UTC))
R.check(
    "touching the floor with the bias applied resets it immediately",
    _c2c._curve_learner.bias == 0.0,
    "safety reacts now; only the downward creep waits for the day to close",
)
_c2d = _t2_coord()
_c2d._track_curve_comfort(datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
R.check(
    "with the flag off no comfort evidence is even collected",
    _c2d._curve_day == "" and _c2d._curve_day_worst is None,
)

# --- persistence: the T4b learners ride the thermal store -------------------------
_cp4 = _t2_coord()
_cp4._capacity_envelope[-4] = [12.0, 9]
_cp4._solar_aperture.update({"n": 50.0, "scale": 1.4})
_cp4._internal_gains_profile = [0.3] * 24
_cp4._internal_gains_profile[19] = 0.8
_cp4._curve_learner.bias = -1.2
_t4b_payload = _cp4._thermal_learning_payload()
_cq4 = _t2_coord()


async def _fake_t4b_load(_p=_t4b_payload):
    return _p


_cq4._thermal_learning_store.async_load = _fake_t4b_load
_asyncio.run(_cq4._async_load_thermal_learning())
R.check(
    "every T4b learner survives a restart",
    _cq4._capacity_envelope.get(-4) == [12.0, 9]
    and abs(_cq4._solar_aperture["scale"] - 1.4) < 1e-9
    and _cq4._internal_gains_profile[19] == 0.8
    and abs(_cq4._curve_learner.bias + 1.2) < 1e-9,
)
_cq5 = _t2_coord()


async def _fake_t4a_load():
    return {"house_heat_loss_scale": 1.1}


_cq5._thermal_learning_store.async_load = _fake_t4a_load
_asyncio.run(_cq5._async_load_thermal_learning())
R.check(
    "a pre-T4b payload loads clean and every learner starts inert",
    not _cq5._capacity_envelope
    and _cq5._solar_aperture["scale"] == 1.0
    and _cq5._internal_gains_profile is None
    and _cq5._curve_learner.bias == 0.0,
)
_cr4 = _t2_coord()
_cr4._capacity_envelope[-4] = [12.0, 9]
_cr4._snapshot_ring.take(
    NOW, _cr4._learner_snapshot_payloads(), {"temperature_bias": 0.1}, True
)
_cr4._capacity_envelope[-4] = [3.0, 40]
_cr4._capacity_envelope[0] = [5.0, 7]
_asyncio.run(_cr4.async_restore_learned_snapshot())
R.check(
    "a rollback restores the envelope and clears what drifted in since",
    _cr4._capacity_envelope.get(-4) == [12.0, 9]
    and 0 not in _cr4._capacity_envelope,
    "a restore is a restore, not a merge with the state it replaces",
)

# --- the T4b review round's regressions ------------------------------------------
# #53's loop closure: the learner replays must predict WITH the learned
# profile (and #36's scale must reach the params the replay shares), or
# the gains learner is an open-loop integrator converging to alpha/ridge
# times the true correction.
_hl_src = inspect.getsource(_Coord._async_learn_house_heat_loss)
R.check(
    "the heat-loss replay predicts with the per-hour profile",
    "hour_of_day=previous_time.hour" in _hl_src,
    "an open-loop residual never re-centres: fixed point g0 + 2.5*surplus",
)
_run_src2 = inspect.getsource(_Coord.async_run_optimization)
R.check(
    "the apply path writes both learned scales onto the shared params",
    "solar_aperture_scale" in _run_src2
    and "internal_gains_profile" in _run_src2,
    "the replay closes its loop through these params — a scale that "
    "never lands there is learned but never applied OR re-centred",
)

# #2's evidence collection stands down when the floor it reads is not the
# floor being enforced: away setbacks and frozen learners both fake a miss.
_c2e = _t2_coord(curve_learning_enabled=True)
_c2e._curve_learner.bias = -1.0
_c2e._away_state.active = True
_c2e._current_state.room_temperature = 15.0  # deep in the away setback
_c2e._track_curve_comfort(datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
R.check(
    "an away setback is not a comfort miss — the bias survives vacations",
    _c2e._curve_learner.bias == -1.0 and _c2e._curve_day_worst is None,
    "the tracker reads the normal floor; away lowers it only inside the "
    "solve envelope",
)
_c2f = _t2_coord(curve_learning_enabled=True)
_c2f._curve_learner.bias = -1.0
_c2f._vent_cusum.tripped = True
_c2f._current_state.room_temperature = 15.0
_c2f._track_curve_comfort(datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
R.check(
    "an open window's dip is the window's doing, not the curve's",
    _c2f._curve_learner.bias == -1.0 and _c2f._curve_day_worst is None,
)

# #30's arithmetic, now a named helper with its own numbers.
_lf = _Coord._liquid_fraction
R.check(
    "the liquid fraction: all snow is 0, all rain is 1, dry is 1",
    float(_lf(np.array([1.0]), np.array([0.7]))[0]) == 0.0
    and float(_lf(np.array([2.0]), np.array([0.0]))[0]) == 1.0
    and float(_lf(np.array([0.0]), np.array([1.0]))[0]) == 1.0,
    "0.7 cm of snow IS 1 mm of the water-equivalent precipitation",
)
R.check(
    "a half-snow step splits at one half",
    abs(float(_lf(np.array([2.0]), np.array([0.7]))[0]) - 0.5) < 1e-9,
)
R.check(
    "cross-source disagreement clips instead of going negative",
    float(_lf(np.array([0.5]), np.array([7.0]))[0]) == 0.0,
)

# The snow clock persists: a restart after a multi-day outage must decay
# the accumulator over the downtime instead of re-tripping on stale snow.
_cp5 = _t2_coord()
_cp5._snow_accum_cm = 3.0
_cp5._snow_accum_last = NOW
_snow_payload = _cp5._thermal_learning_payload()
_cq6 = _t2_coord()


async def _fake_snow_load(_p=_snow_payload):
    return _p


_cq6._thermal_learning_store.async_load = _fake_snow_load
_asyncio.run(_cq6._async_load_thermal_learning())
R.check(
    "the snow accumulator's clock survives a restart with its value",
    _cq6._snow_accum_last == NOW and abs(_cq6._snow_accum_cm - 3.0) < 1e-9,
)

# A pre-T4b snapshot restores EVERY T4b learner to inert — aperture and
# curve bias included, not just the two container types.
_cr5 = _t2_coord()
_old_snapshot = {"thermal_learning": {"house_heat_loss_scale": 1.0}}
_cr5._solar_aperture.update({"n": 99.0, "scale": 1.8})
_cr5._curve_learner.bias = -2.0
_cr5._apply_learner_payloads(_old_snapshot)
R.check(
    "restoring a pre-T4b snapshot resets the aperture and the curve bias",
    _cr5._solar_aperture["scale"] == 1.0
    and _cr5._solar_aperture["n"] == 0.0
    and _cr5._curve_learner.bias == 0.0,
    "keeping the drifted values would be the merge the comment forbids",
)

# ===========================================================================
# T5 — comfort floors (#16 #54)
# ===========================================================================
R.section("T5 — comfort floors (#16 #54)")

from heatpump_optimizer.accuracy import LEAD_BUCKETS
from heatpump_optimizer.const import CONFIDENCE_MARGIN_CAP_C
from heatpump_optimizer.thermal_model import (
    dew_point_for_pressure,
    mold_safe_room_floor,
    saturation_vapor_pressure,
)

# --- the lead-time error tracker -------------------------------------------------
_T5 = datetime(2026, 1, 20, 6, 0, tzinfo=UTC)
_tr5 = AccuracyTracker()
R.check("no history means sigma zero at every lead", _tr5.sigma(12.0) == 0.0)
for k in LEAD_BUCKETS:
    _tr5.note_lead_prediction(_T5 + timedelta(hours=k), k, 21.0)
for k in LEAD_BUCKETS:
    _tr5.score_lead_predictions(_T5 + timedelta(hours=k, minutes=10), 20.6)
R.check(
    "a matured promise scores into its own lead bucket",
    abs(_tr5.sigma(3.0) - 0.4) < 1e-9 and abs(_tr5.sigma(24.0) - 0.4) < 1e-9,
)
R.check(
    "between buckets the nearest one with evidence answers",
    abs(_tr5.sigma(4.0) - _tr5.sigma(3.0)) < 1e-12
    and abs(_tr5.sigma(40.0) - _tr5.sigma(24.0)) < 1e-12,
)
_tr5b = AccuracyTracker.from_dict(_tr5.as_dict())
R.check(
    "sigmas, counts and unmatured promises all ride the store round trip",
    abs(_tr5b.sigma(6.0) - 0.4) < 1e-9
    and _tr5b.lead_counts == _tr5.lead_counts,
)
_tr5c = AccuracyTracker()
_tr5c.note_lead_prediction(_T5, 1.0, 21.0)
_tr5c.score_lead_predictions(_T5 + timedelta(hours=2), 19.0)
R.check(
    "a promise that missed its measurement window is discarded unscored",
    _tr5c.sigma(1.0) == 0.0 and not _tr5c.lead_pending,
    "pairing a 1-hour promise with a 2-hour-late reading would file the "
    "error under the wrong lead",
)

# --- filing promises through the coordinator ---------------------------------------
_c16 = _t2_coord()
_c16._mode = "auto"
_fake_plan = _NS(
    room_temp_trajectory=[21.0 + 0.01 * i for i in range(97)],
    upper_temp_trajectory=[],
)
_c16._file_lead_predictions(_fake_plan, _T5)
R.check(
    "each solve files one promise per lead bucket within the horizon",
    len(_c16._accuracy.lead_pending) == len(LEAD_BUCKETS)
    and _c16._accuracy.lead_pending[0][1] == 1.0
    # Anchored to the instant the trajectory was built from, not to
    # "whenever the solve finished": a slow solve must not skew every
    # bucket by its own duration.
    and _c16._accuracy.lead_pending[0][0] == _T5 + timedelta(hours=1),
    f"filed {len(_c16._accuracy.lead_pending)}",
)
_c16b = _t2_coord()
_c16b._mode = "comfort"
_c16b._file_lead_predictions(_fake_plan, _T5)
R.check(
    "a plan that is not running makes no promises worth scoring",
    not _c16b._accuracy.lead_pending,
    "same mode gate as the one-step accuracy sample",
)

# --- #16 the margins ------------------------------------------------------------------
def _seed_sigma(coord, err):
    for k in LEAD_BUCKETS:
        coord._accuracy.note_lead_prediction(_T5 + timedelta(hours=k), k, 21.0)
    for k in LEAD_BUCKETS:
        coord._accuracy.score_lead_predictions(
            _T5 + timedelta(hours=k, minutes=5), 21.0 - err
        )


_cm5 = _t2_coord(confidence_margins_enabled=True)
_seed_sigma(_cm5, 0.5)
_cm5._accuracy.temperature_mae = lambda: 2.0  # trust 0 -> full damping
_m5 = _cm5._confidence_margins(96)
R.check(
    "the margin is the expected error at each step's own lead",
    _m5 is not None and abs(_m5[3] - 0.5) < 1e-9 and abs(_m5[95] - 0.5) < 1e-9,
)
_cm5._accuracy.temperature_mae = lambda: 0.25  # trust 1 -> no margin at all
R.check(
    "a trusted model margins nothing however noisy the history",
    _cm5._confidence_margins(96) is None,
)
_cm6 = _t2_coord(confidence_margins_enabled=True)
_seed_sigma(_cm6, 5.0)
_cm6._accuracy.temperature_mae = lambda: 2.0
R.check(
    "the cap holds whatever the history claims",
    float(np.max(_cm6._confidence_margins(96))) <= CONFIDENCE_MARGIN_CAP_C + 1e-12,
    "an unbounded margin is the oscillation the plan forbids",
)
# The fixed point, replayed for real: margins A, then a whole new round of
# promises scored with the SAME error magnitude the history already claims,
# then margins B. The EWMA sits still only at its fixed point, so equality
# here is the anti-oscillation argument (margin -> plan -> errors converges),
# not a tautology about calling the same function twice. Uncapped on purpose
# — at the cap the claim would be vacuously true again.
_cm8 = _t2_coord(confidence_margins_enabled=True)
_seed_sigma(_cm8, 0.5)
_cm8._accuracy.temperature_mae = lambda: 2.0
_m8_a = _cm8._confidence_margins(96)
_seed_sigma(_cm8, 0.5)
_m8_b = _cm8._confidence_margins(96)
R.check(
    "a model erring exactly as history claims is a fixed point of the margin",
    _m8_a is not None and np.allclose(_m8_a, _m8_b, atol=1e-12),
    "margin -> plan -> errors loops only if the margin itself moves",
)
_seed_sigma(_cm8, 0.0)
_m8_c = _cm8._confidence_margins(96)
R.check(
    "a round of perfect predictions shrinks the margin strictly",
    _m8_c is None or bool(np.all(_m8_c < _m8_b - 1e-9)),
    "the loop's only drift direction is toward less margin",
)
_cm7 = _t2_coord()
_seed_sigma(_cm7, 0.5)
_cm7._accuracy.temperature_mae = lambda: 2.0
R.check(
    "with the flag off no margin exists, whatever the history",
    _cm7._confidence_margins(96) is None,
)
R.check(
    "a fresh install margins nothing — zero history, zero sigma",
    _t2_coord(confidence_margins_enabled=True)._confidence_margins(96) is None,
)

# --- the optimizer's floor channel ---------------------------------------------------
_g5 = _mk_golden(dhw=False)
_r5_base = _g5["optimizer"].optimize(
    _g5["state"], _g5["prices"], _g5["outdoor"], _g5["wind"], _g5["rain"],
    _g5["solar"], _G_START,
)
_g5b = _mk_golden(dhw=False)
_r5_zero = _g5b["optimizer"].optimize(
    _g5b["state"], _g5b["prices"], _g5b["outdoor"], _g5b["wind"], _g5b["rain"],
    _g5b["solar"], _G_START,
    min_temp_margins=np.zeros(len(_g5b["prices"])),
    min_temp_floors=np.full(len(_g5b["prices"]), -100.0),
)
R.check(
    "zero margins and a bottomless floor are byte-identical to none at all",
    np.array_equal(
        np.asarray(_r5_base.power_schedule), np.asarray(_r5_zero.power_schedule)
    ),
)
_g5c = _mk_golden(dhw=False)
_r5_m = _g5c["optimizer"].optimize(
    _g5c["state"], _g5c["prices"], _g5c["outdoor"], _g5c["wind"], _g5c["rain"],
    _g5c["solar"], _G_START,
    min_temp_margins=np.full(len(_g5c["prices"]), 0.8),
)
R.check(
    "a real margin lifts the coldest hour of the plan",
    min(_r5_m.room_temp_trajectory) > min(_r5_base.room_temp_trajectory) + 0.3,
    f"coldest {min(_r5_base.room_temp_trajectory):.2f} -> "
    f"{min(_r5_m.room_temp_trajectory):.2f}",
)
_g5d = _mk_golden(dhw=False)
_r5_f = _g5d["optimizer"].optimize(
    _g5d["state"], _g5d["prices"], _g5d["outdoor"], _g5d["wind"], _g5d["rain"],
    _g5d["solar"], _G_START,
    min_temp_floors=np.full(len(_g5d["prices"]), 19.5),
)
R.check(
    "a mold floor holds the coldest hour above it",
    min(_r5_f.room_temp_trajectory) > 19.0,
    f"coldest {min(_r5_f.room_temp_trajectory):.2f} against a 19.5 floor",
)
_g5e = _mk_golden(dhw=False)
_r5_wild = _g5e["optimizer"].optimize(
    _g5e["state"], _g5e["prices"], _g5e["outdoor"], _g5e["wind"], _g5e["rain"],
    _g5e["solar"], _G_START,
    min_temp_margins=np.full(len(_g5e["prices"]), 10.0),
)
R.check(
    "an absurd margin cannot squeeze the band shut",
    max(_r5_wild.room_temp_trajectory) < 30.0
    and "failed" not in str(_r5_wild.status),
    "the floor clamps below the ceiling instead of making the solve "
    "infeasible",
)

# --- #54 the mold guard ---------------------------------------------------------------
_p12 = saturation_vapor_pressure(12.0)
R.check(
    "the Magnus pair inverts itself",
    abs(dew_point_for_pressure(_p12) - 12.0) < 0.01,
)
R.check(
    "colder outside means a higher room floor — the guard's whole physics",
    mold_safe_room_floor(21.0, 60.0, -15.0, 0.75)
    > mold_safe_room_floor(21.0, 60.0, 5.0, 0.75),
)


def _mold_coord(rh_state=None, **cfg):
    states = (
        {"sensor.rh": FakeState(rh_state, unit="%")} if rh_state is not None else {}
    )
    c = _t2_coord(states=states, **cfg)
    c._current_state.room_temperature = 21.0
    return c


_out5 = np.array([-15.0, -15.0, 5.0])
_cold = _mold_coord(
    "60", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
)
_floors_wet = _cold._mold_floor_series(_out5)
R.check(
    "60% indoor humidity at -15 °C raises the floor to the target cap",
    _floors_wet is not None
    and abs(_floors_wet[0] - _cold._opt_config.target_temp) < 1e-9
    and _floors_wet[2] < _floors_wet[0],
    "the honest physics wants more than the target; the cap is the guard "
    "against heating past comfort to fight a ventilation problem",
)
_dry = _mold_coord(
    "20", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
)
_floors_dry = _dry._mold_floor_series(_out5)
R.check(
    "20% indoor humidity raises nothing — dry air cannot mold",
    _floors_dry is not None and float(np.max(_floors_dry)) < 10.0,
)
R.check(
    "the double gate: flag without a sensor, or sensor without the flag, is off",
    _mold_coord("60", mold_guard_enabled=True)._mold_floor_series(_out5) is None
    and _mold_coord(
        "60", indoor_humidity_entity="sensor.rh"
    )._mold_floor_series(_out5)
    is None,
)
R.check(
    "an unusable humidity reading disarms the guard instead of guessing",
    _mold_coord(
        "unavailable", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
    )._mold_floor_series(_out5)
    is None
    and _mold_coord(
        "0", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
    )._mold_floor_series(_out5)
    is None,
)

# --- the T5 review round's regressions ------------------------------------------------

# The scoring window follows the caller's cadence: an hourly scorer must not
# discard every promise that matured between its ticks — with the default
# half-hour window the 12 h and 24 h buckets would starve on any install
# whose optimization interval is coarser than the tolerance.
_tr1 = AccuracyTracker()
_tr1.note_lead_prediction(_T5, 3.0, 21.0)
_tr1.score_lead_predictions(_T5 + timedelta(minutes=45), 20.0)
_tr1b = AccuracyTracker()
_tr1b.note_lead_prediction(_T5, 3.0, 21.0)
_tr1b.score_lead_predictions(_T5 + timedelta(minutes=45), 20.0, window_hours=1.0)
R.check(
    "a coarse solve cadence widens the window instead of starving buckets",
    _tr1.sigma(3.0) == 0.0
    and not _tr1.lead_pending
    and abs(_tr1b.sigma(3.0) - 1.0) < 1e-9,
)

# Equidistant buckets: sigma(2.0) sits exactly between the 1 h and 3 h
# buckets, and the answer must be the longer (more conservative) one.
_tr11 = AccuracyTracker()
_tr11.lead_sigma = {1.0: 0.2, 3.0: 0.6}
_tr11.lead_counts = {1.0: 1, 3.0: 1}
R.check(
    "an exact tie between buckets answers with the longer one",
    abs(_tr11.sigma(2.0) - 0.6) < 1e-12,
)

# The corruption barrier: a hand-edited or half-written store must not brick
# the loop. A tz-naive pending timestamp would raise on the first aware
# subtraction inside every subsequent score call; a NaN sigma would reach
# the comfort bounds as a NaN margin.
_tr8 = AccuracyTracker.from_dict(
    {
        "lead_sigma": {"1.0": float("nan"), "3.0": 0.4, "6.0": "junk"},
        "lead_counts": {"1.0": 3, "3.0": 3, "6.0": 3},
        "lead_pending": [
            ["2026-01-20T06:00:00", 1.0, 21.0],
            ["2026-01-20T06:00:00+00:00", 3.0, float("nan")],
            ["2026-01-20T06:00:00+00:00", 6.0, 21.0],
        ],
    }
)
_loaded_pending = len(_tr8.lead_pending)  # naive + NaN entries never loaded
_tr8.score_lead_predictions(_T5 + timedelta(minutes=10), 20.5)
R.check(
    "a corrupt store loads what survives and never bricks the score loop",
    _tr8.sigma(1.0) == 0.4  # NaN sigma dropped; 3 h bucket answers for 1 h
    and _loaded_pending == 1
    and abs(_tr8.lead_sigma[6.0] - 0.5) < 1e-9,  # the good promise scored
)

# Leaving the plan's modes voids its unmatured promises: in comfort, boost
# and off the room is driven by fixed rules, and scoring the old plan's
# promises against it would charge the model with errors it never made.
_c2m = _t2_coord()
_c2m._mode = "auto"
_c2m._file_lead_predictions(_fake_plan, _T5)
_asyncio.run(_c2m.async_set_mode("economy"))
_kept_between_plan_modes = len(_c2m._accuracy.lead_pending) == len(LEAD_BUCKETS)
_asyncio.run(_c2m.async_set_mode("comfort"))
R.check(
    "leaving auto/economy voids the plan's unmatured promises",
    _kept_between_plan_modes and not _c2m._accuracy.lead_pending,
    "auto -> economy keeps them; auto -> comfort clears them",
)

# A step-response experiment overrides the plan for its duration, so no
# promises are filed while it runs — and the ones the overridden plan
# already filed are void too.
_c2s = _t2_coord()
_c2s._mode = "auto"
_c2s._file_lead_predictions(_fake_plan, _T5)
_c2s._sysid.phase = PHASE_ARMED
_c2s._file_lead_predictions(_fake_plan, _T5)
R.check(
    "an active experiment files nothing and voids what the plan had filed",
    not _c2s._accuracy.lead_pending,
)

# A frozen indoor sensor scores nothing: a stuck reading is not a
# measurement, and an EWMA poisoned by one persists for weeks.
from homeassistant.util import dt as _dt5

_c9 = _t2_coord()
_c9._mode = "auto"
_c9._current_state.room_temperature = 20.0
_t9 = datetime(2026, 1, 21, 6, 0, tzinfo=UTC)
_c9._accuracy.note_lead_prediction(_t9 - timedelta(minutes=10), 1.0, 21.0)
_dt5.freeze(_t9)
try:
    _c9._learning_frozen = lambda key: "stale"
    _c9._record_accuracy()
    _frozen_kept = (
        len(_c9._accuracy.lead_pending) == 1 and _c9._accuracy.sigma(1.0) == 0.0
    )
    _c9._learning_frozen = lambda key: None
    _c9._record_accuracy()
    _live_scored = (
        not _c9._accuracy.lead_pending
        and abs(_c9._accuracy.sigma(1.0) - 1.0) < 1e-9
    )
finally:
    _dt5.freeze(None)
R.check(
    "a frozen indoor sensor scores nothing; a live one settles the promise",
    _frozen_kept and _live_scored,
    "the promise waits through the freeze instead of being mis-scored",
)

# The floor channel is keyword-only: both arguments are per-step temperature
# series the same shape as half the solver's inputs, so a positional
# transposition would be silent and plausible-looking.
_g5f = _mk_golden(dhw=False)
try:
    _g5f["optimizer"].optimize(
        _g5f["state"], _g5f["prices"], _g5f["outdoor"], _g5f["wind"],
        _g5f["rain"], _g5f["solar"], _G_START,
        None, None, None, None, None, None, None, None,
        np.zeros(len(_g5f["prices"])),
    )
    _f5_raised = False
except TypeError:
    _f5_raised = True
R.check(
    "the comfort-floor arguments cannot be passed positionally",
    _f5_raised,
    "a transposed margins/floors pair must be a loud TypeError, not a plan",
)

# The mold cap is the CONFIGURED target, never the live one: the away
# setback lowers _opt_config.target_temp, and capping there would disarm
# the guard exactly when mold risk peaks — a cold, damp, unheated house.
_c6away = _mold_coord(
    "60", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
)
_c6away._opt_config.target_temp = 15.0
_floors_away = _c6away._mold_floor_series(_out5)
R.check(
    "an away setback cannot lower the mold cap",
    _floors_away is not None
    and abs(float(_floors_away[0]) - float(_floors_wet[0])) < 1e-9
    and float(_floors_away[0]) > 15.0 + 1.0,
    "the guard holds the configured comfort target through the setback",
)

# What-if solves pass their scratch target as the cap, so a simulated
# target override sees the floor that choice would actually get.
_c7cap = _mold_coord(
    "60", mold_guard_enabled=True, indoor_humidity_entity="sensor.rh"
)
_floors_cap = _c7cap._mold_floor_series(_out5, target_cap=18.0)
R.check(
    "a simulated target override caps its own what-if floor",
    _floors_cap is not None
    and abs(float(np.max(_floors_cap)) - 18.0) < 1e-9,
)

# ===========================================================================
# T6 — insight (#29 #52 #55 #65 #39 #40)
# ===========================================================================
R.section("T6 — insight (#29 #52 #55 #65 #39 #40)")

import re as _re6

from heatpump_optimizer import diagnosis as diagnosis_mod
from heatpump_optimizer import narrative as narrative_mod
from heatpump_optimizer.const import COP_HEALTH_THRESHOLD
from heatpump_optimizer.wear import StartCounter, wear_price_per_start

_T6 = datetime(2026, 3, 28, 12, 0, tzinfo=UTC)

# --- #55 the start counter -------------------------------------------------------
_sc = StartCounter()
_thr = 0.5
R.check(
    "one noisy sample above the threshold books nothing",
    not _sc.observe(_T6, 2.0, _thr, False) and _sc.lifetime == 0,
    "two-sample hysteresis: a single meter glitch is not a start",
)
R.check(
    "the second consecutive sample confirms the start",
    _sc.observe(_T6, 2.0, _thr, False) and _sc.lifetime == 1 and _sc.running,
)
R.check(
    "a falling edge needs two samples too, and books no start",
    not _sc.observe(_T6, 0.0, _thr, False)
    and not _sc.observe(_T6, 0.0, _thr, False)
    and _sc.lifetime == 1
    and not _sc.running,
)
_sc.observe(_T6, 2.0, _thr, False)  # half an edge...
R.check(
    "the immersion element freezes the machine and resets the streak",
    not _sc.observe(_T6, 2.0, _thr, True)  # ...the element cuts in
    and not _sc.observe(_T6, 2.0, _thr, False)  # half an edge again
    and _sc.lifetime == 1,
    "#11's classifier owns resistive draw; half-edges must not combine "
    "across an immersion event",
)
_sc.observe(_T6, 2.0, _thr, False)
R.check(
    "after the element drops out a full clean edge counts again",
    _sc.lifetime == 2 and _sc.month_count("2026-03") == 2,
)
_sc2 = StartCounter.from_dict(_sc.as_dict())
R.check(
    "the counter rides its store round trip, running state included",
    _sc2.lifetime == 2
    and _sc2.month_count("2026-03") == 2
    and _sc2.running == _sc.running,
)
R.check(
    "a pre-T6 store (or garbage) loads as an inert counter",
    StartCounter.from_dict(None).lifetime == 0
    and StartCounter.from_dict({"lifetime": "junk"}).lifetime == 0,
)
R.check(
    "the wear price: unpriced is 0, priced is cost over rated starts",
    wear_price_per_start(0.0, 100000) == 0.0
    and abs(wear_price_per_start(40000.0, 100000) - 0.4) < 1e-12,
)

# The coordinator's threshold convention and the wear booking on a start.
_cw = _t2_coord(
    compressor_replacement_cost=50000.0, compressor_rated_starts=100000
)
_cw._measured_power = 3.0
_cw._observe_compressor_start(_T6)
_cw._observe_compressor_start(_T6)
R.check(
    "a confirmed start books its wear price on the ledger's wear line",
    _cw._start_counter.lifetime == 1
    and abs(_cw._ledger.line("2026-03", "wear")["sek"] - 0.5) < 1e-9
    and _cw._ledger.line("2026-03", "wear")["kwh"] == 0.0,
    "money, not energy: wear kWh on a receipt would double-count the meter",
)
R.check(
    "the default install books starts but no money",
    _t2_coord()._wear_price() == 0.0,
)
R.check(
    "the autotune floors the cycling cost only when asked",
    _t2_coord()._effective_cycling_cost() == 0.0
    and abs(
        _t2_coord(
            wear_autotune_enabled=True, compressor_replacement_cost=50000.0
        )._effective_cycling_cost()
        - 0.5
    )
    < 1e-12
    and abs(
        _t2_coord(
            wear_autotune_enabled=True,
            compressor_replacement_cost=50000.0,
            compressor_cycling_cost=2.0,
        )._effective_cycling_cost()
        - 2.0
    )
    < 1e-12,
    "max, never replace: a user who priced chatter above the datasheet "
    "wear keeps their number",
)

# --- reason-tagged settlement ----------------------------------------------------
_r6 = _g5["optimizer"].optimize(
    _g5["state"], _g5["prices"], _g5["outdoor"], _g5["wind"], _g5["rain"],
    _g5["solar"], _G_START,
)
_act6 = _g5["optimizer"].get_current_action(_r6, _r6.timestamps[2])
R.check(
    "the current action carries this step's reason codes",
    _act6.get("space_reason") == _r6.space_reasons[2],
    "the settlement tags money with WHY at the same index the action ran",
)

_ct = _t2_coord()
_ct_pending = {
    "price": 2.5,
    "spot_price": 2.0,
    "grid_fee": 0.5,
    "space_power": 1.5,
    "dhw_power": 0.5,
    "when": _T6,
    "space_reason": "cheap_price",
    "dhw_reason": "dhw_preheat",
}
_ct._accumulate_energy(AccuracySample(when=_T6, actual_power_kw=2.0), 1.0, _ct_pending)
_ct_spot = _ct._ledger.line("2026-03", "spot")
_ct_space = _ct._ledger.line("2026-03", "reason:cheap_price")
_ct_dhw = _ct._ledger.line("2026-03", "reason:dhw_preheat")
R.check(
    "the reason lines partition the spot line, split by the plan's shares",
    abs(_ct_space["kwh"] - 1.5) < 1e-9
    and abs(_ct_dhw["kwh"] - 0.5) < 1e-9
    and abs(_ct_space["kwh"] + _ct_dhw["kwh"] - _ct_spot["kwh"]) < 1e-9
    and abs(_ct_space["sek"] + _ct_dhw["sek"] - _ct_spot["sek"]) < 1e-9,
    "a partition, not a bonus column — receipts built from these must not "
    "overstate",
)
_ci = _t2_coord()
_ci._immersion_active = True
_ci._accumulate_energy(
    AccuracySample(when=_T6, actual_power_kw=6.9), 0.5, dict(_ct_pending)
)
_ci_reasons = (
    _ci._ledger.line("2026-03", "reason:cheap_price")["kwh"]
    + _ci._ledger.line("2026-03", "reason:dhw_preheat")["kwh"]
)
R.check(
    "the immersion carve-out comes out of the reason lines too",
    abs(_ci_reasons - _ci._ledger.line("2026-03", "spot")["kwh"]) < 1e-9,
    "reason lines partition METERED kWh; the element's excess is #11's line",
)
_cu6 = _t2_coord()
_cu6._accumulate_energy(
    AccuracySample(when=_T6, actual_power_kw=2.0),
    1.0,
    {k: v for k, v in _ct_pending.items() if not k.endswith("_reason")},
)
R.check(
    "an interval without a tag books as untagged, not as nothing",
    abs(
        _cu6._ledger.line("2026-03", "reason:untagged")["kwh"]
        - _cu6._ledger.line("2026-03", "spot")["kwh"]
    )
    < 1e-9,
    "manual modes and restarts must still land in the month's total",
)

# The sys-ID override wipes the plan's reasons off the running action.
_cs6 = _t2_coord()
_cs6._current_action = {"power": 1.0, "space_reason": "cheap_price", "dhw_reason": None}
_cs6._sysid.phase = PHASE_ARMED
_cs6._sysid.step = lambda **kw: 2.0
_cs6._run_system_identification(np.array([1.0]))
R.check(
    "an experiment's draw settles untagged, never under the dead plan's reason",
    _cs6._current_action["space_reason"] is None
    and _cs6._current_action["mode"] == "system_identification",
)

# --- #40 the month freeze --------------------------------------------------------
_cm = _t2_coord()
_cm._accumulate_energy(
    AccuracySample(when=_T6, actual_power_kw=2.0), 1.0, dict(_ct_pending)
)
R.check(
    "no receipt exists while the month is still open",
    not _cm._month_reports,
)
_apr = datetime(2026, 4, 1, 0, 30, tzinfo=UTC)
_cm._accumulate_energy(
    AccuracySample(when=_apr, actual_power_kw=1.0),
    1.0,
    dict(_ct_pending, when=_apr),
)
R.check(
    "the first settlement of a new month freezes the old month's receipt",
    "2026-03" in _cm._month_reports
    and _cm._month_reports["2026-03"]["month"] == "2026-03",
)
_receipt = _cm._month_reports["2026-03"]
R.check(
    "the receipt's reason lines reconcile against its spot line",
    _receipt["reasons_reconcile"] is True
    and abs(
        sum(entry["kwh"] for entry in _receipt["reasons"].values())
        - _receipt["lines"]["spot"]["kwh"]
    )
    < 0.05,
)
R.check(
    "the receipt settles the CLOSED month's contracts, not the new month's",
    _receipt["contract_comparison"]["month"] == "2026-03"
    and abs(_receipt["contract_comparison"]["kwh"] - 2.0) < 1e-6,
)
_frozen_total = _receipt["total_kwh"]
# A LATE booking into the already-closed month: a wrongly re-frozen
# receipt would pick it up and change; a truly frozen one cannot.
_cm._ledger.add(_T6, "wear", kwh=0.0, sek=5.0)
_cm._accumulate_energy(
    AccuracySample(when=_apr, actual_power_kw=5.0),
    1.0,
    dict(_ct_pending, when=_apr),
)
R.check(
    "a frozen receipt never changes after its month closed",
    _cm._month_reports["2026-03"]["total_kwh"] == _frozen_total
    and "wear" not in _cm._month_reports["2026-03"]["lines"],
    "even a late line booked into the closed month cannot rewrite history",
)

# --- #65 the scores --------------------------------------------------------------
_ce = _t2_coord()
_ce._thermal_params.room_thermal_mass = 10.0
_ce._thermal_params.heat_loss_coefficient = 0.1
_ce._thermal_params.house_heat_loss_scale = 1.0
R.check(
    "a 100-hour house grades 100 on the envelope",
    _ce._scores_view()["envelope"] == 100.0,
)
_ce._thermal_params.heat_loss_coefficient = 0.5
R.check(
    "a 20-hour house grades 0 — the learned loss scale keeps it honest",
    _ce._scores_view()["envelope"] == 0.0,
)
_ce._thermal_params.heat_loss_coefficient = 0.25
_ce._thermal_params.house_heat_loss_scale = 0.5
R.check(
    "the envelope grade follows the house as measured, not as configured",
    abs(_ce._scores_view()["envelope"] - 75.0) < 0.1,
    "tau = 10 / (0.25 x 0.5) = 80 h -> (80-20)/80 of the way to 100",
)
_cmach = _t2_coord()
R.check(
    "no COP evidence means no machine grade, not a failing one",
    _cmach._scores_view()["machine"] is None,
)
_cmach._cop_baseline[3] = [3.0, COP_BASELINE_MIN_SAMPLES + 1]
R.check(
    "a healthy watched machine grades 100",
    _cmach._scores_view()["machine"] == 100.0,
)
_cmach._cop_health_cusum.stat = COP_HEALTH_THRESHOLD
R.check(
    "a machine at the alarm threshold grades 0",
    _cmach._scores_view()["machine"] == 0.0,
)
_cop6 = _t2_coord()
for _spot6 in (1.0, 1.0, 3.0, 3.0):
    _cop6._fold_score_sample(_T6, 1.0, 1.6 * 1.0, _spot6, 0.25, True)
_cop6._fold_score_sample(_apr, 0.0, 0.0, 2.0, 0.25, True)  # next day closes
R.check(
    "buying 20% under the day's mean spot replays to a perfect operation day",
    _cop6._operation_score is not None
    and abs(_cop6._operation_score - 100.0) < 1e-6,
    "4 kWh at 1.60 mean against a 2.00 flat-consumer mean is the full "
    "0.2 saved fraction",
)
_ctiny = _t2_coord()
_ctiny._fold_score_sample(_T6, 0.1, 0.2, 2.0, 1.0, True)
_ctiny._fold_score_sample(_apr, 0.0, 0.0, 2.0, 1.0, True)
R.check(
    "a day with too little energy teaches nothing and is skipped",
    _ctiny._operation_score is None,
)
_fresh6 = _t2_coord()._scores_view()
R.check(
    "a fresh install grades only what it has: the configured envelope",
    _fresh6["machine"] is None
    and _fresh6["operation"] is None
    and _fresh6["overall"] == _fresh6["envelope"],
    "machine and operation need measurements; the envelope is the house "
    "as configured until the learners move its loss scale",
)

# --- #29 the narrative -----------------------------------------------------------
for _lang6 in narrative_mod.LANGUAGES:
    R.check(
        f"every template language carries every reason key ({_lang6})",
        set(narrative_mod.TEMPLATES[_lang6]) == set(narrative_mod.TEMPLATES["en"]),
    )
_par_ok = all(
    set(_re6.findall(r"{(\w+)}", narrative_mod.TEMPLATES["en"][key]))
    == set(_re6.findall(r"{(\w+)}", narrative_mod.TEMPLATES["sv"][key]))
    for key in narrative_mod.TEMPLATES["en"]
)
R.check(
    "en and sv templates use identical placeholders per key",
    _par_ok,
    "a placeholder present in one language and absent in the other is a "
    "sentence that cannot be said",
)
_n_items = narrative_mod.build(
    {
        "powers": [2.0, 2.0, 0.0, 1.0],
        "prices": [1.0, 2.0, 3.0, 4.0],
        "reasons": ["cheap_price", "cheap_price", "idle", "comfort_floor"],
    },
    {
        "powers": [0.0, 0.0, 1.0, 0.0],
        "prices": [1.0, 2.0, 3.0, 4.0],
        "reasons": ["idle", "idle", "dhw_preheat", "idle"],
    },
    0.25,
)
R.check(
    "the narrative groups both channels and orders by spend",
    [i["reason"] for i in _n_items][:2] == ["cheap_price", "comfort_floor"]
    and any(i["reason"] == "dhw_preheat" for i in _n_items),
)
R.check(
    "the groups are arithmetic over the same steps the plan publishes",
    abs(next(i for i in _n_items if i["reason"] == "cheap_price")["kwh"] - 1.0)
    < 1e-9
    and abs(
        next(i for i in _n_items if i["reason"] == "cheap_price")["sek"] - 1.5
    )
    < 1e-9,
)
R.check(
    "an unknown reason degrades to a missing sentence, not a crash",
    narrative_mod.render(
        [{"reason": "from_the_future", "kwh": 1.0, "sek": 1.0, "hours": 1.0}],
        "sv",
    )
    == [],
)
_cn = _t2_coord()
_cn._optimization_result = _r6
_n_view = _cn._narrative_view()
R.check(
    "the coordinator's narrative view renders lines for the current plan",
    _n_view["items"] and _n_view["lines"] and _n_view["language"] == "en",
)

# --- #52 the diagnosis -----------------------------------------------------------
_dmodel = ThermalModel(ThermalParameters())
_dstate = ThermalState(
    room_temperature=20.0, slab_temperature=25.0, outdoor_temperature=0.0
)
_dplanned = {
    "electrical_power": 2.0,
    "outdoor_temp": 0.0,
    "wind_speed": 2.0,
    "solar_radiation": 0.0,
    "external_heat_kw": 0.0,
    "dt_hours": 1.0,
    "humidity": None,
    "hour_of_day": None,
}
_dbase = diagnosis_mod._room_after(_dmodel, _dstate, _dplanned)
_dreport = diagnosis_mod.attribute(
    _dmodel,
    _dstate,
    _dplanned,
    {"outdoor_temp": -10.0, "electrical_power": None},
    _dbase - 0.3,
)
R.check(
    "a colder realised outdoor explains a colder room",
    _dreport is not None
    and _dreport["contributions"].get("outdoor_temp", 0.0) < 0.0,
)
R.check(
    "an unmeasured input attributes nothing",
    "electrical_power" not in _dreport["contributions"],
)
R.check(
    "predicted + contributions + unexplained always accounts for actual",
    abs(
        _dreport["predicted"]
        + sum(_dreport["contributions"].values())
        + _dreport["unexplained"]
        - _dreport["actual"]
    )
    < 0.02,
    "the attribution is a partition of the residual by construction",
)
_cd = _t2_coord()
R.check(
    "no settled interval means no diagnosis, not a crash",
    _cd.diagnose_last_interval() is None,
)
_cd._last_interval_record = {
    "when": _T6.isoformat(),
    "state": _dstate,
    "planned": dict(_dplanned),
    "dt_hours": 1.0,
    "realised": {"outdoor_temp": -10.0},
    "actual": _dbase - 0.3,
}
_cd_report = _cd.diagnose_last_interval()
R.check(
    "the coordinator's diagnosis runs the settled triple and publishes it",
    _cd_report is not None
    and _cd._last_diagnosis is _cd_report
    and _cd_report["interval_end"] == _T6.isoformat(),
)

# --- #39 the price tiles ---------------------------------------------------------
_ctile = _t2_coord()


async def _fake_sim(overrides):
    return {
        "monthly_cost_delta": -42.0,
        "min_room_temperature": 19.1,
        "rate_limited": False,
    }


_ctile.async_simulate = _fake_sim
_asyncio.run(_ctile._maybe_refresh_price_tile())
R.check(
    "with the flag off no tile ever computes, whatever solves happen",
    not _ctile._price_tiles,
)
_ctile2 = _t2_coord(price_tiles_enabled=True)
_ctile2.async_simulate = _fake_sim
_asyncio.run(_ctile2._maybe_refresh_price_tile())
R.check(
    "one solve refreshes exactly one tile, in rotation",
    list(_ctile2._price_tiles) == ["target_minus_1"]
    and _ctile2._price_tiles["target_minus_1"]["monthly_cost_delta"] == -42.0
    and _ctile2._price_tile_cursor == 1,
)


async def _fake_sim_limited(overrides):
    return {"rate_limited": True}


_ctile2.async_simulate = _fake_sim_limited
_asyncio.run(_ctile2._maybe_refresh_price_tile())
R.check(
    "the card's rate budget wins: a limited answer leaves the rotation alone",
    _ctile2._price_tile_cursor == 1 and len(_ctile2._price_tiles) == 1,
    "tiles wait for the next interval instead of stealing the user's solve",
)
R.check(
    "the tile set is fixed at three perturbations",
    len(_ctile2._price_tile_specs()) == 3,
)

# --- the insight view and its persistence ----------------------------------------
_cv = _t2_coord()
_cv._optimization_result = _r6
_iview = _cv._insight_view()
R.check(
    "the insight view publishes every T6 surface, inert on a fresh install",
    set(_iview)
    == {
        "narrative",
        "scores",
        "compressor_starts",
        "monthly_report",
        "price_tiles",
        "last_diagnosis",
    }
    and _iview["monthly_report"] is None
    and _iview["compressor_starts"]["lifetime"] == 0,
)

_cp6 = _t2_coord()
_cp6._start_counter.lifetime = 7
_cp6._month_reports["2026-02"] = {"month": "2026-02", "total_kwh": 1.0}
_cp6._operation_score = 88.0
_led_payload = {
    "ledger": _cp6._ledger.as_dict(),
    "starts": _cp6._start_counter.as_dict(),
    "month_reports": _cp6._month_reports,
    "score_day": _cp6._score_day,
    "operation_score": _cp6._operation_score,
}
_cq7 = _t2_coord()


async def _fake_led_load(_p=_led_payload):
    return _p


_cq7._ledger_store.async_load = _fake_led_load
_asyncio.run(_cq7._async_load_ledger())
R.check(
    "starts, receipts and the operation score ride the ledger store",
    _cq7._start_counter.lifetime == 7
    and "2026-02" in _cq7._month_reports
    and _cq7._operation_score == 88.0,
)


async def _fake_led_old(_p={"ledger": {"months": {}}}):
    return _p


_cq8 = _t2_coord()
_cq8._ledger_store.async_load = _fake_led_old
_asyncio.run(_cq8._async_load_ledger())
R.check(
    "a pre-T6 ledger store loads with every insight rider inert",
    _cq8._start_counter.lifetime == 0
    and not _cq8._month_reports
    and _cq8._operation_score is None,
)

# --- the T6 review round's regressions ------------------------------------------------

# A corrupt persisted day book must cost one operation sample, never the
# update loop: bare float() on a stored "junk" would raise inside every
# settlement for the rest of the day.
_cq9 = _t2_coord()


async def _fake_led_bad(
    _p={
        "ledger": {"months": {}},
        "score_day": {"day": "2026-03-01", "kwh": "junk"},
    }
):
    return _p


_cq9._ledger_store.async_load = _fake_led_bad
_asyncio.run(_cq9._async_load_ledger())
_cq9._accumulate_energy(
    AccuracySample(when=_T6, actual_power_kw=1.0), 1.0, dict(_ct_pending)
)
R.check(
    "a corrupt day book is dropped at load and settlement carries on",
    _cq9._score_day.get("day") == "2026-03-28",
    "the T4a lesson again: a poisoned rider must not brick the loop",
)

# The diagnosis compares space against space: planned power is the space
# channel, and the measured whole-meter draw is apportioned by the plan's
# own split before the swap.
_csp = _t2_coord()
_csp._current_action = {"power": 1.5, "dhw_power": 2.0}
R.check(
    "the diagnosis plans with the space channel, not the commanded total",
    _csp._capture_diagnosis_inputs()["planned"]["electrical_power"] == 1.5,
    "simulate_step's power heats the house; handing it the total would "
    "charge every tank charge to room heating",
)
_c10 = _t2_coord()
_c10._mode = "auto"
_c10._current_action = {"power": 1.0, "dhw_power": 1.0}
_c10._measured_power = 3.0
_c10._current_state.room_temperature = 20.0
_t10 = datetime(2026, 3, 29, 6, 0, tzinfo=UTC)
_dt5.freeze(_t10)
try:
    _c10._record_accuracy()
    _dt5.freeze(_t10 + timedelta(minutes=15))
    _c10._record_accuracy()
finally:
    _dt5.freeze(None)
R.check(
    "the realised power in the settled triple is the space share of the meter",
    _c10._last_interval_record is not None
    and abs(
        _c10._last_interval_record["realised"]["electrical_power"] - 1.5
    )
    < 1e-9
    and _c10._last_interval_record["planned"]["electrical_power"] == 1.0,
    "3 kW metered at a 1.0/1.0 plan split diagnoses as 1.5 kW of space",
)

# The diagnosis runs on a scratch model, never the live one the scheduled
# solve may be walking in another executor thread.
from heatpump_optimizer import coordinator as _coord_mod

_cd10 = _t2_coord()
_cd10._last_interval_record = {
    "when": _T6.isoformat(),
    "state": _dstate,
    "planned": dict(_dplanned),
    "dt_hours": 1.0,
    "realised": {},
    "actual": 20.0,
}
_seen10: dict = {}
_real_attribute = _coord_mod.diagnosis.attribute


def _spy_attribute(model, state, planned, realised, actual):
    _seen10["model"] = model
    return _real_attribute(model, state, planned, realised, actual)


_coord_mod.diagnosis.attribute = _spy_attribute
try:
    _cd10.diagnose_last_interval()
finally:
    _coord_mod.diagnosis.attribute = _real_attribute
R.check(
    "the diagnosis never touches the live thermal model",
    _seen10.get("model") is not None
    and _seen10["model"] is not _cd10._thermal_model,
    "simulate_step writes per-call scratch on the model instance",
)

# The tile borrows the card's harness without spending its budget: the
# rate-limit stamp and the cache are snapshot-restored, so a drag right
# after a solve neither rate-limits nor reads the tile's payload back.
_ctile3 = _t2_coord(price_tiles_enabled=True)
_marker3 = {"marker": True}
_stamp3 = datetime(2026, 3, 1, tzinfo=UTC)
_ctile3._simulation_cache = _marker3
_ctile3._last_simulation = _stamp3


async def _fake_sim_poison(overrides, _c=_ctile3):
    _c._last_simulation = datetime(2026, 3, 2, tzinfo=UTC)
    _c._simulation_cache = {"poison": True}
    return {
        "monthly_cost_delta": -1.0,
        "min_room_temperature": 19.0,
        "rate_limited": False,
    }


_ctile3.async_simulate = _fake_sim_poison
_asyncio.run(_ctile3._maybe_refresh_price_tile())
R.check(
    "a tile run leaves the card's rate budget and cache exactly as found",
    _ctile3._simulation_cache is _marker3
    and _ctile3._last_simulation == _stamp3
    and _ctile3._price_tiles,
    "the fuse advisor's own rule: borrow the harness, never the slot",
)

# The target tiles perturb the LIVE target: during an away setback the
# configured target would flip the sign of the published trade.
_ctile6 = _t2_coord(price_tiles_enabled=True)
_ctile6._opt_config.target_temp = 17.0
R.check(
    "the target tiles follow the live target through an away setback",
    _ctile6._price_tile_specs()[0][1]["target_temp"] == 16.0
    and _ctile6._price_tile_specs()[1][1]["target_temp"] == 18.0,
    "'one degree lower' must be lower than the plan being compared against",
)

# A consistently failing spec must not block the other tiles forever.
_ctile4 = _t2_coord(price_tiles_enabled=True)


async def _fake_sim_err(overrides):
    return {"error": "boom", "rate_limited": False}


_ctile4.async_simulate = _fake_sim_err
_asyncio.run(_ctile4._maybe_refresh_price_tile())
R.check(
    "an erroring tile spec advances the rotation instead of stalling it",
    _ctile4._price_tile_cursor == 1 and not _ctile4._price_tiles,
)

# Turning the flag off retires the published tiles too.
_ctile5 = _t2_coord()
_ctile5._price_tiles["stale"] = {"monthly_cost_delta": 1.0}
_asyncio.run(_ctile5._maybe_refresh_price_tile())
R.check(
    "gate off means gone: no stale what-if money outlives the flag",
    not _ctile5._price_tiles,
)

# A pre-T6 month has no partition to break: its receipt says None, never
# False — an upgrade must not look like the bug the flag exists to catch.
_cpre = _t2_coord()
_cpre._ledger.add(_T6, "spot", kwh=100.0, sek=150.0)
_cpre._roll_month(_apr)
R.check(
    "a month with no reason lines reconciles to None, not to failure",
    _cpre._month_reports["2026-03"]["reasons_reconcile"] is None,
)

# The reconcile compares RAW ledger values: rounding thirty tiny lines to
# two decimals each would otherwise cry wolf on a perfect partition.
_crr = _t2_coord()
for _i in range(30):
    _crr._ledger.add(_T6, f"reason:r{_i}", kwh=0.001, sek=0.005017)
_crr._ledger.add(_T6, "spot", kwh=0.03, sek=0.005017 * 30)
R.check(
    "a perfectly partitioned month reconciles whatever the rounding does",
    _crr._freeze_month_report("2026-03")["reasons_reconcile"] is True,
)

# The debounce streak dies with the meter: two noise spikes separated by
# an outage are not two CONSECUTIVE samples.
_sc8 = StartCounter()
_sc8.observe(_T6, 2.0, 0.5, False)
_sc8.observe(_T6, None, 0.5, False)
R.check(
    "a meter outage resets the hysteresis streak",
    not _sc8.observe(_T6, 2.0, 0.5, False) and _sc8.lifetime == 0,
)

# The day book keeps its signs and its baseline honest: a negative-price
# hour lowers the paid mean, and an hour with no known price stays out of
# the flat-consumer baseline entirely.
_cneg = _t2_coord()
for _ in range(3):
    _cneg._fold_score_sample(_T6, 0.5, 1.5, 3.0, 0.25, True)
_cneg._fold_score_sample(_T6, 1.0, -1.0, -1.0, 0.25, True)
_cneg._fold_score_sample(_T6, 0.0, 0.0, 0.0, 0.25, False)
_cneg._fold_score_sample(_apr, 0.0, 0.0, 2.0, 0.25, True)
R.check(
    "signed SEK and a known-price-only baseline score the day correctly",
    _cneg._operation_score is not None
    and abs(_cneg._operation_score - 100.0) < 1e-6,
    "paid 1.40 against a 2.00 known-hours mean: zeroing the negative hour "
    "or folding the unknown one would both under-score the day",
)

# ===========================================================================
# T7 — inverter frequency (#61)
# ===========================================================================
R.section("T7 — inverter frequency (#61)")

from heatpump_optimizer.freq_control import (
    FREQ_MIN_SAMPLES,
    FREQ_MODE_CONTROL,
    FREQ_MODE_OBSERVE,
    FREQ_WATCHDOG_TICKS,
    FrequencyMap,
    FrequencyWatchdog,
)

# --- the kW-per-Hz map -----------------------------------------------------------
_fm = FrequencyMap()
_fm.observe(0.0, 2.0, 20.0, 120.0)   # stopped compressor
_fm.observe(45.0, 0.01, 20.0, 120.0)  # no meaningful draw
_fm.observe(200.0, 2.0, 20.0, 120.0)  # outside the entity's range
R.check(
    "a stopped compressor, a dead meter and a wild reading all teach nothing",
    not _fm.buckets,
)
for _ in range(FREQ_MIN_SAMPLES + 1):
    _fm.observe(45.0, 2.0, 20.0, 120.0)
for _ in range(FREQ_MIN_SAMPLES + 1):
    _fm.observe(95.0, 6.0, 20.0, 120.0)
R.check(
    "readings fold into their own frequency decile",
    len(_fm.buckets) == 2
    and abs(_fm.buckets[2][0] - 2.0 / 45.0) < 1e-9,
)
_before = float(_fm.buckets[2][0])
_fm.observe(45.0, 4.0, 20.0, 120.0)  # one outlier after seeding
R.check(
    "a seeded bucket moves by its EWMA step, not to the outlier",
    _fm.buckets[2][0] < _before * 1.15,
    "mean-until-N then slow EWMA — the COP baseline's own lesson",
)
R.check(
    "the recommendation is the LOWEST evidenced frequency that delivers",
    _fm.recommend(1.5, 20.0, 120.0) == 45.0
    and _fm.recommend(5.0, 20.0, 120.0) == 95.0,
    "an inverter runs most efficiently slow",
)
R.check(
    "above every bucket's reach the answer is TRUE flat out, and says so",
    _fm.recommend(50.0, 20.0, 120.0) == 120.0
    and _fm.evidence_exhausted(50.0, 20.0, 120.0)
    and not _fm.evidence_exhausted(1.5, 20.0, 120.0),
    "answering from evidence alone would be the #17 ratchet: no higher "
    "decile could ever earn its samples and capacity would freeze",
)
R.check(
    "no evidence, or nothing to deliver, is None — never a write",
    FrequencyMap().recommend(2.0, 20.0, 120.0) is None
    and _fm.recommend(0.0, 20.0, 120.0) is None,
)
_fm2 = FrequencyMap.from_dict(_fm.as_dict())
R.check(
    "the map rides its store round trip",
    _fm2.recommend(1.5, 20.0, 120.0) == 45.0,
)
R.check(
    "a corrupt map loads what survives",
    FrequencyMap.from_dict(
        {"2": ["junk", 9], "5": [0.05, 9], "x": [0.1, "y"], "7": [-1.0, 9]}
    ).buckets
    == {5: [0.05, 9]},
)

# --- the watchdog ----------------------------------------------------------------
_wd = FrequencyWatchdog()
_wd.note_command(60.0)
R.check(
    "transient divergence during a ramp is not a fault",
    not _wd.note_report(80.0)
    and not _wd.note_report(80.0)
    and not _wd.note_report(61.0)  # converged: streak clears
    and _wd.strikes == 0,
)
_tripped_on = [_wd.note_report(80.0) for _ in range(FREQ_WATCHDOG_TICKS)]
R.check(
    "three CONSECUTIVE divergent ticks trip the watchdog, exactly then",
    _tripped_on == [False, False, True] and _wd.tripped,
)
_wd2 = FrequencyWatchdog()
_wd2.note_command(60.0)
_wd2.note_report(None)
R.check(
    "a missing report is a stale input, never divergence evidence",
    _wd2.strikes == 0,
)

# --- the coordinator's observe stage ---------------------------------------------
def _freq_coord(hz="45", mode=None, **extra):
    states = {
        "number.freq": FakeState(hz, attributes={"min": 20.0, "max": 120.0})
    }
    cfg = {"compressor_freq_entity": "number.freq"}
    if mode is not None:
        cfg["freq_control_mode"] = mode
    cfg.update(extra)
    c = _t2_coord(states=states, **cfg)
    c._measured_power = 2.0
    # The plan is asking for 2 kW total — what control translates to Hz.
    c._current_action = {"power": 1.5, "dhw_power": 0.5}
    return c


_cf = _freq_coord()
_cf._observe_frequency(_T6)
R.check(
    "an observed cycle folds (frequency, kW) into the map",
    _cf._freq_map.buckets and _cf._freq_map.buckets[2][1] == 1,
)
_cfi = _freq_coord()
_cfi._immersion_active = True
_cfi._observe_frequency(_T6)
R.check(
    "immersion intervals never teach the map",
    not _cfi._freq_map.buckets,
    "#11 owns resistive draw; folding it would teach the map that some "
    "frequency draws the element's kilowatts",
)
R.check(
    "without the entity the stage is unconfigured and the view says so",
    _t2_coord()._freq_view()["mode"] == "unconfigured"
    and _t2_coord()._freq_view()["map"] == {},
)
R.check(
    "observe is the stage in force unless control is explicitly chosen",
    _freq_coord()._freq_mode() == FREQ_MODE_OBSERVE
    and _freq_coord(mode="control")._freq_mode() == FREQ_MODE_CONTROL,
)

# --- the control stage's rails ---------------------------------------------------
def _armed_coord(**extra):
    c = _freq_coord(mode="control", **extra)
    for _ in range(FREQ_MIN_SAMPLES + 1):
        c._freq_map.observe(45.0, 2.0, 20.0, 120.0)
    # The boot stamp (below) blocks the first five minutes after any
    # start; these tests exercise the steady state.
    c._freq_last_write = None
    return c


_cc = _armed_coord()
_asyncio.run(_cc._command_frequency())
R.check(
    "control writes the recommendation via number.set_value",
    _cc.hass.services.calls
    and _cc.hass.services.calls[-1][:2] == ("number", "set_value")
    and _cc.hass.services.calls[-1][2]["value"] == 45.0,
)
_n_calls = len(_cc.hass.services.calls)
_asyncio.run(_cc._command_frequency())
R.check(
    "a second write inside five minutes is rate-limited away",
    len(_cc.hass.services.calls) == _n_calls,
)
_cc._freq_last_write = None
_asyncio.run(_cc._command_frequency())
R.check(
    "re-commanding the same value is deduplicated, not re-sent",
    len(_cc.hass.services.calls) == _n_calls,
    "an unchanged setpoint on the wire every cycle is noise",
)
_co = _freq_coord()  # observe mode
for _ in range(FREQ_MIN_SAMPLES + 1):
    _co._freq_map.observe(45.0, 2.0, 20.0, 120.0)
_asyncio.run(_co._command_frequency())
R.check(
    "observe mode never writes, however good the map",
    not _co.hass.services.calls,
    "the observe stage's entire contract: no actuation of any kind",
)
_cn = _freq_coord(mode="control")  # control but NO evidence
_asyncio.run(_cn._command_frequency())
R.check(
    "a map with no evidence writes nothing — None is never a frequency",
    not _cn.hass.services.calls,
)

# --- the watchdog stand-down, end to end -----------------------------------------
_ct7 = _armed_coord()
_asyncio.run(_ct7._command_frequency())  # commands 45.0
_ct7.hass.states.set(
    "number.freq", FakeState("90", attributes={"min": 20.0, "max": 120.0})
)
# One extra tick: the first report after a command is a grace tick.
for _ in range(FREQ_WATCHDOG_TICKS + 1):
    _ct7._observe_frequency(_T6)
R.check(
    "persistent divergence stands control down to observe and latches",
    _ct7._freq_fallback and _ct7._freq_mode() == FREQ_MODE_OBSERVE,
)
_n7 = len(_ct7.hass.services.calls)
_ct7._freq_last_write = None
_asyncio.run(_ct7._command_frequency())
R.check(
    "a stood-down controller makes no further writes",
    len(_ct7.hass.services.calls) == _n7,
)
# The re-arm gesture: the user switches back to observe and saves.
_ct7._config["freq_control_mode"] = "observe"
_ct7._observe_frequency(_T6)
R.check(
    "switching the mode to observe is the acknowledgement that re-arms",
    not _ct7._freq_fallback and not _ct7._freq_watchdog.tripped,
    "a restart alone must never clear the latch — the user does",
)

# --- persistence and rollback ----------------------------------------------------
_cp7 = _freq_coord()
for _ in range(FREQ_MIN_SAMPLES + 1):
    _cp7._freq_map.observe(45.0, 2.0, 20.0, 120.0)
_cp7._freq_fallback = True
_payload7 = _cp7._thermal_learning_payload()
_cq10 = _t2_coord()


async def _fake_freq_load(_p=_payload7):
    return _p


_cq10._thermal_learning_store.async_load = _fake_freq_load
_asyncio.run(_cq10._async_load_thermal_learning())
R.check(
    "the map and the stand-down latch both survive a restart",
    _cq10._freq_map.recommend(1.5, 20.0, 120.0) == 45.0
    and _cq10._freq_fallback,
)
_cr7 = _t2_coord()
_cr7._freq_map.observe(45.0, 2.0, 20.0, 120.0)
_cr7._freq_fallback = True
_cr7._apply_learner_payloads(
    {"thermal_learning": {"house_heat_loss_scale": 1.0}}
)
R.check(
    "a pre-T7 snapshot rolls the map back to inert but keeps the latch",
    not _cr7._freq_map.buckets and _cr7._freq_fallback,
    "a learner rollback must not quietly re-arm a controller that stood "
    "down over a hardware fault",
)

# --- the T7 review round's regressions ------------------------------------------------

# An idle plan reading 0 Hz overnight is an operating point at rest, not a
# write path that stopped listening: three cycles of routine MPC idle must
# never stand control down.
_ci7 = _armed_coord()
_asyncio.run(_ci7._command_frequency())  # commands 45.0
_ci7._current_action = {"power": 0.0, "dhw_power": 0.0}
_ci7.hass.states.set(
    "number.freq", FakeState("0", attributes={"min": 20.0, "max": 120.0})
)
for _ in range(FREQ_WATCHDOG_TICKS + 2):
    _ci7._observe_frequency(_T6)
R.check(
    "overnight idle never trips the watchdog",
    not _ci7._freq_fallback and _ci7._freq_watchdog.strikes == 0,
    "compressor-off is not write-path divergence",
)

# The first report after a command is a grace tick: the pump is entitled
# to still be ramping (or the register to a stale poll).
_wdg = FrequencyWatchdog()
_wdg.note_command(60.0)
R.check(
    "a setpoint change eats no strike on its own command tick",
    not _wdg.note_report(90.0)
    and _wdg.strikes == 0
    and not _wdg.note_report(90.0)
    and _wdg.strikes == 1,
    "bang-bang plans alternating deciles must not accumulate false strikes",
)

# Echo hardware: the number entity mirrors the setpoint, so the watchdog
# reads the SEPARATE actual-frequency sensor when one is configured.
def _echo_coord(sensor_state="90"):
    states = {
        "number.freq": FakeState(
            "45", attributes={"min": 20.0, "max": 120.0}
        )
    }
    if sensor_state is not None:
        states["sensor.hz_actual"] = FakeState(sensor_state)
    c = _t2_coord(
        states=states,
        compressor_freq_entity="number.freq",
        compressor_freq_sensor="sensor.hz_actual",
        freq_control_mode="control",
    )
    c._measured_power = 2.0
    c._current_action = {"power": 1.5, "dhw_power": 0.5}
    c._freq_last_write = None
    for _ in range(FREQ_MIN_SAMPLES + 1):
        c._freq_map.observe(45.0, 2.0, 20.0, 120.0)
    return c


_ce7 = _echo_coord()
_asyncio.run(_ce7._command_frequency())  # number echoes 45; sensor says 90
for _ in range(FREQ_WATCHDOG_TICKS + 1):
    _ce7._observe_frequency(_T6)
R.check(
    "with a real feedback sensor the watchdog sees through the echo",
    _ce7._freq_fallback,
    "read from the echoing setpoint alone this divergence is invisible",
)
_cm7 = _echo_coord(sensor_state=None)  # sensor configured but unavailable
R.check(
    "a configured but missing feedback sensor reads as no reading at all",
    _cm7._freq_entity_reading()[0] is None,
    "falling back to the echo would re-decorate the watchdog exactly when "
    "the real feedback disappeared",
)

# Removing the entity is as explicit an acknowledgement as switching the
# mode: neither may orphan the latch and its repair issue forever.
_co7 = _armed_coord()
_co7._freq_fallback = True
_co7._config["compressor_freq_entity"] = None
_co7._observe_frequency(_T6)
R.check(
    "clearing the entity re-arms the latch instead of orphaning it",
    not _co7._freq_fallback,
)

# The latch loads strictly: corrupt truthy garbage must not silently
# disable control with no repair issue and no visible cause.
_cs7 = _t2_coord()


async def _fake_junk_latch(_p={"freq_fallback": "junk"}):
    return _p


_cs7._thermal_learning_store.async_load = _fake_junk_latch
_asyncio.run(_cs7._async_load_thermal_learning())
R.check(
    "only a stored True is a stand-down; garbage is not",
    not _cs7._freq_fallback,
)

# The rate limit survives boot: a crash-looping HA must not get a fresh
# write per restart. (The steady-state tests clear the stamp explicitly.)
_cb7 = _freq_coord(mode="control")
for _ in range(FREQ_MIN_SAMPLES + 1):
    _cb7._freq_map.observe(45.0, 2.0, 20.0, 120.0)
_asyncio.run(_cb7._command_frequency())
R.check(
    "the first five minutes after any start write nothing",
    not _cb7.hass.services.calls,
)

# Flat-out-on-faith is visible: the view flags evidence exhaustion.
_cx7 = _armed_coord()
_cx7._current_action = {"power": 7.0, "dhw_power": 2.0}
_x_view = _cx7._freq_view()
R.check(
    "the view says when the recommendation is extrapolation, not evidence",
    _x_view["evidence_exhausted"] and _x_view["recommended_hz"] == 120.0,
)

R.section("v4.0.2 — entry lifecycle, the solve boundary, store writes")

from pathlib import Path as _Path

import heatpump_optimizer as _integ
from heatpump_optimizer.const import DOMAIN as _DOMAIN
from homeassistant.helpers import storage as _ha_storage

_LC_DATA = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
}

# The full entry lifecycle through the real setup and unload handlers. The
# FakeServices registry is honest — registration stores, removal deletes — so
# a service that setup registers and unload forgets stays visible. Two did:
# restore_snapshot and diagnose_interval outlived the last entry because the
# hand-written removal tuple had drifted from the registration list again.
_lc_hass = FakeHass()
_lc_entry = FakeEntry(data=_LC_DATA)
_asyncio.run(_integ.async_setup_entry(_lc_hass, _lc_entry))
_lc_registered = dict(_lc_hass.services.async_services().get(_DOMAIN, {}))
R.check(
    "setup registers the integration's services",
    len(_lc_registered) == 11,
    f"{len(_lc_registered)} registered: {sorted(_lc_registered)}",
)
_asyncio.run(_integ.async_unload_entry(_lc_hass, _lc_entry))
_lc_left = dict(_lc_hass.services.async_services().get(_DOMAIN, {}))
R.check(
    "every registered service is gone after the last entry unloads",
    not _lc_left,
    f"leaked: {sorted(_lc_left)}",
)

# The solve runs in an executor thread while learners, the live peak guard
# and the climate entity keep writing on the event loop. The snapshot is the
# boundary: nothing it returns may alias the coordinator's live objects.
_ss_coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_LC_DATA))
_ss_state, _ss_opt = _ss_coord._solve_snapshot()
R.check(
    "the snapshot state is a copy, not the live state",
    _ss_state is not _ss_coord._current_state,
)
R.check(
    "the snapshot optimizer carries its own parameter copy",
    _ss_opt.model.params is not _ss_coord._thermal_params,
)
R.check(
    "and its own model, so per-solve scratch stays off the live one",
    _ss_opt.model is not _ss_coord._thermal_model,
)
_ss_before = float(_ss_opt.model.params.heat_loss_coefficient)
_ss_coord._thermal_params.heat_loss_coefficient = _ss_before + 5.0
R.check(
    "a mid-solve write on the live parameters cannot reach the snapshot",
    _ss_opt.model.params.heat_loss_coefficient == _ss_before,
    f"{_ss_opt.model.params.heat_loss_coefficient} vs {_ss_before}",
)

# The accuracy store used to be rewritten every update cycle whether or not
# anything in it had changed. The stub's per-key save counter is the honest
# witness: same payload, one write.
_wr_coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_LC_DATA))
_wr_key = f"{_DOMAIN}_test_entry_accuracy"
_wr_base = _ha_storage.SAVE_COUNTS.get(_wr_key, 0)
_asyncio.run(_wr_coord._async_save_accuracy())
_asyncio.run(_wr_coord._async_save_accuracy())
R.check(
    "an unchanged accuracy payload is written exactly once",
    _ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _wr_base == 1,
    f"{_ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _wr_base} writes",
)
_wr_coord._mode = MODE_ECONOMY  # the payload persists the mode
_asyncio.run(_wr_coord._async_save_accuracy())
R.check(
    "a changed payload is written again",
    _ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _wr_base == 2,
    f"{_ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _wr_base} writes",
)

# The digest is recorded only after the store accepted the payload; a failed
# save that also recorded it would silently never be retried.
_fl_coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_LC_DATA))
_fl_orig = _fl_coord._accuracy_store.async_save


async def _fl_boom(data):
    raise OSError("disk full")


_fl_coord._accuracy_store.async_save = _fl_boom
_asyncio.run(_fl_coord._async_save_accuracy())
_fl_coord._accuracy_store.async_save = _fl_orig
_fl_base = _ha_storage.SAVE_COUNTS.get(_wr_key, 0)
_asyncio.run(_fl_coord._async_save_accuracy())
R.check(
    "a failed save is retried on the next cycle, not skipped as written",
    _ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _fl_base == 1,
    f"{_ha_storage.SAVE_COUNTS.get(_wr_key, 0) - _fl_base} writes",
)

# One aiohttp session, Home Assistant's, everywhere: a private ClientSession
# per fetch or per token validation leaked its connection pool.
_net_coord_src = _Path(
    "custom_components/heatpump_optimizer/coordinator.py"
).read_text()
_net_flow_src = _Path(
    "custom_components/heatpump_optimizer/config_flow.py"
).read_text()
R.check(
    "the price fetch rides the shared aiohttp session",
    "aiohttp.ClientSession(" not in _net_coord_src
    and "async_get_clientsession" in _net_coord_src,
)
R.check(
    "token validation rides the shared aiohttp session",
    "aiohttp.ClientSession(" not in _net_flow_src
    and "async_get_clientsession" in _net_flow_src,
)

R.section("v4.0.3 — stale-plan guards, billed peaks, boundary clamps")

from heatpump_optimizer.config_flow import validate_tibber_token as _g_tibber
from heatpump_optimizer.coordinator import (
    PLAN_STALE_FLOOR_MINUTES as _G_STALE_FLOOR,
    SOLVE_FAILURE_ISSUE_COUNT as _G_FAIL_COUNT,
)
from heatpump_optimizer.optimizer import (
    OptimizationResult as _GRes,
)
from heatpump_optimizer.thermal_model import (
    THERMAL_MASS_FLOOR as _G_MASS_FLOOR,
)

# --- the pre-horizon clock guard -------------------------------------------------
# The step-selection loop's else-branch answers "past the horizon" with the
# LAST step; a clock BEFORE the horizon fell into the same branch — and the
# last step is where terminal-value charging lives.
_g_opt = _PvOpt(_PvModel(_PvParams()), _PvOptCfg())
_g_t0 = datetime(2026, 3, 1, 12, 0, tzinfo=UTC)
_g_res = _GRes(
    power_schedule=[1.4, 2.8, 4.2],
    room_temp_trajectory=[21.0] * 4,
    slab_temp_trajectory=[22.0] * 4,
    timestamps=[_g_t0 + timedelta(minutes=15 * i) for i in range(3)],
    prices=[0.5, 1.0, 1.5],
    predicted_cost=1.0,
    baseline_cost=1.0,
    predicted_savings=0.0,
    savings_percentage=0.0,
    optimal_setpoints=[21.0, 21.5, 22.0],
    status="ok",
)
_g_act = _g_opt.get_current_action(_g_res, _g_t0 - timedelta(minutes=5))
R.check(
    "a skew within one step length clamps to the FIRST step, not the last",
    _g_act["power"] == 1.4 and _g_act["setpoint"] == 21.0,
    f"got power {_g_act['power']}, setpoint {_g_act['setpoint']}",
)
_g_far = _g_opt.get_current_action(_g_res, _g_t0 - timedelta(hours=2))
R.check(
    "beyond one step the plan says nothing about now: idle",
    _g_far["mode"] == "idle" and _g_far["heat_pump_on"] is False,
    f"got {_g_far['mode']}",
)
R.check(
    "the pre-horizon idle IS the empty-plan fallback, one shared dict",
    _g_far == _g_opt._idle_action(),
    "two hand-maintained fallbacks would drift",
)
_g_last = _g_opt.get_current_action(_g_res, _g_t0 + timedelta(hours=5))
R.check(
    "past the horizon the last step still answers, unchanged",
    _g_last["power"] == 4.2,
)

# --- solve failures: the counter, the issue, the stale predicate -----------------
_g_coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_LC_DATA))
R.check(
    "before any solve the plan has no age and is not stale",
    _g_coord._plan_age_minutes() is None
    and _g_coord._plan_is_stale() is False,
)


def _g_boom(*_args):
    raise RuntimeError("solver exploded")


_g_coord._forecast_arrays = _g_boom
for _ in range(_G_FAIL_COUNT):
    _asyncio.run(_g_coord.async_run_optimization())
_g_issues = [
    i for i in getattr(_g_coord.hass, "issues", []) if i[1] == "solve_failures"
]
R.check(
    "three consecutive failed solves raise exactly one repair issue",
    _g_coord._solve_failures == _G_FAIL_COUNT and len(_g_issues) == 1,
    f"failures {_g_coord._solve_failures}, issues {len(_g_issues)}",
)
R.check(
    "the issue carries its translation key and placeholders",
    _g_issues[0][2].get("translation_key") == "solve_failures"
    and set(_g_issues[0][2].get("translation_placeholders", {}))
    == {"count", "last_success"}
    and _g_issues[0][2].get("is_persistent") is True,
)

from homeassistant.util import dt as _g_dt

_g_coord._last_optimization = _g_dt.now() - timedelta(minutes=60)
R.check(
    "an hour-old plan is not yet stale (90-minute floor)",
    not _g_coord._plan_is_stale()
    and abs(_g_coord._plan_age_minutes() - 60.0) < 1.0,
)
_g_coord._last_optimization = _g_dt.now() - timedelta(
    minutes=_G_STALE_FLOOR + 10
)
R.check(
    "past three missed cycles the plan is stale",
    _g_coord._plan_is_stale(),
)
_g_slow = HeatPumpOptimizerCoordinator(
    FakeHass(), FakeEntry(data={**_LC_DATA, "optimization_interval": 60})
)
_g_slow._last_optimization = _g_dt.now() - timedelta(minutes=100)
R.check(
    "the threshold scales with the configured update interval",
    not _g_slow._plan_is_stale(),
    "3 x 60 min = 180 min; 100 minutes is one missed cycle, not staleness",
)

# The fallback path: a stale plan's action is NOT actuated — the same
# non-actuation as having no plan, handing comfort to the pump's own curve.
_g_pub: list[str] = []


async def _g_rec(reason="optimizer"):
    _g_pub.append(reason)


_g_coord.async_publish_current_action = _g_rec
_g_coord._current_action = {"heat_pump_on": True, "displace_value": 2.0}
_asyncio.run(_g_coord._apply_action())
R.check(
    "a stale plan's schedule step is not applied",
    not _g_pub,
    f"published {_g_pub}",
)
_g_coord._last_optimization = _g_dt.now()
_asyncio.run(_g_coord._apply_action())
R.check(
    "a fresh plan actuates exactly as before",
    _g_pub == ["scheduled_update"],
    f"published {_g_pub}",
)
_g_coord._last_optimization = _g_dt.now() - timedelta(days=1)
_g_coord._mode = "boost"
_asyncio.run(_g_coord._apply_action())
R.check(
    "fixed-rule modes carry no horizon and ignore staleness",
    _g_pub == ["scheduled_update", "scheduled_update"],
    f"published {_g_pub}",
)

# --- a rollback must not un-remember billed peaks --------------------------------
_g_pk = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=_LC_DATA))
_g_pk._peak_tracker.month = "2026-08"
_g_pk._peak_tracker.peaks = [5.0]
_g_snap = _g_pk._learner_snapshot_payloads()
R.check(
    "new snapshots no longer carry the peak tracker at all",
    "peak_tracker" not in _g_snap,
)
_g_pk._peak_tracker.peaks = [7.0, 5.0]  # the DSO has metered a higher peak
_g_pk._apply_learner_payloads(_g_snap)
R.check(
    "a learner rollback leaves the month's realised peaks alone",
    _g_pk._peak_tracker.peaks == [7.0, 5.0],
    f"peaks after rollback: {_g_pk._peak_tracker.peaks}",
)
_g_pk._apply_learner_payloads(
    {"peak_tracker": {"month": "2026-01", "peaks": [2.0]}}
)
R.check(
    "an old snapshot still carrying the key is simply ignored",
    _g_pk._peak_tracker.peaks == [7.0, 5.0]
    and _g_pk._peak_tracker.month == "2026-08",
)

# --- the thermal-mass boundary clamp and the Euler stability guard ---------------
_g_cfgp = ThermalParameters.from_config(
    {"house_thermal_mass": 0.0, "upper_floor_thermal_mass": -3.0}
)
R.check(
    "from_config clamps zero and negative masses to the physical floor",
    _g_cfgp.room_thermal_mass == _G_MASS_FLOOR
    and _g_cfgp.upper_floor_thermal_mass == _G_MASS_FLOOR,
)
_g_dirp = ThermalParameters(slab_thermal_mass=0.0)
R.check(
    "direct construction runs through the same clamp",
    _g_dirp.slab_thermal_mass == _G_MASS_FLOOR,
)
_g_dirp.lower_floor_thermal_mass = 0.0
_g_dirp.clamp()
R.check(
    "the service-write chokepoint re-clamps after attribute assignment",
    _g_dirp.lower_floor_thermal_mass == _G_MASS_FLOOR,
)

_g_sane = ThermalModel(ThermalParameters(two_zone_enabled=True))
R.check(
    "no sane configuration ever subdivides a step",
    _g_sane._stability_substeps(0.0, 0.0, 0.25) == 1
    and ThermalModel(ThermalParameters())._stability_substeps(0.0, 0.0, 0.25)
    == 1,
    "the committed fixtures depend on n == 1 being the universal case",
)

# A floored upper-floor mass against a strong inter-zone coupling is exactly
# the u·dt/C > 1.5 regime where plain Euler oscillates divergently.
_g_stiff = ThermalModel(
    ThermalParameters(
        two_zone_enabled=True,
        upper_floor_thermal_mass=0.001,  # clamps to the floor
        inter_zone_transfer=3.0,
    )
)
R.check(
    "the stiff case genuinely exercises the subdivision",
    _g_stiff._stability_substeps(0.0, 0.0, 0.25) > 1,
)
_g_room, _g_slab, _g_up, _g_low = _g_stiff.simulate_trajectory(
    ThermalState(),
    np.full(96, 2.0),
    np.full(96, -5.0),
)
R.check(
    "a 24 h trajectory on the stiff house stays finite and bounded",
    bool(np.all(np.isfinite(_g_up)))
    and float(np.max(np.abs(_g_up))) < 100.0,
    f"max |T_upper| {float(np.max(np.abs(_g_up))):.1f}",
)

# --- stale-sensor guards and the naive-timestamp restore -------------------------
_g_cus = Cusum(threshold=1.0, drift=0.1)
_g_cus.load(
    {"stat": 2.0, "tripped": True, "last_fed": "2026-01-01T00:00:00"}
)
R.check(
    "a legacy naive last_fed loads as aware UTC",
    _g_cus.last_fed is not None and _g_cus.last_fed.tzinfo is not None,
)
R.check(
    "and release_if_starved subtracts it without raising",
    _g_cus.release_if_starved(datetime(2026, 1, 2, tzinfo=UTC), 12.0)
    is True,
)

_g_hum_cfg = {**_LC_DATA, "indoor_humidity_entity": "sensor.rh",
              "mold_guard_enabled": True}
_g_hfresh = HeatPumpOptimizerCoordinator(
    FakeHass({"sensor.rh": FakeState("70", last_updated=minutes_ago(10))}),
    FakeEntry(data=_g_hum_cfg),
)
R.check(
    "a fresh humidity reading feeds the mold floor",
    _g_hfresh._indoor_humidity_value() == 70.0
    and _g_hfresh._mold_floor_series(np.array([-5.0, -10.0])) is not None,
)
_g_hstale = HeatPumpOptimizerCoordinator(
    FakeHass({"sensor.rh": FakeState("70", last_updated=minutes_ago(300))}),
    FakeEntry(data=_g_hum_cfg),
)
R.check(
    "a frozen humidity sensor reads as no reading — the mold floor vanishes",
    _g_hstale._indoor_humidity_value() is None
    and _g_hstale._mold_floor_series(np.array([-5.0, -10.0])) is None,
    "failing safe is a floor that disappears, not one held raised forever",
)

_g_now43 = datetime(2026, 8, 26, 12, 0, tzinfo=UTC)
_g_ifresh = HeatPumpOptimizerCoordinator(
    FakeHass({"sensor.inlet": FakeState("12.0", last_updated=minutes_ago(30))}),
    FakeEntry(data={**_LC_DATA, "dhw_inlet_entity": "sensor.inlet"}),
)
_g_ifresh._prepare_dhw_inputs(_g_now43)
R.check(
    "a live inlet probe still wins",
    _g_ifresh._thermal_params.dhw_inlet_current == 12.0,
)
_g_istale = HeatPumpOptimizerCoordinator(
    FakeHass(
        {"sensor.inlet": FakeState("12.0", last_updated=minutes_ago(60 * 48))}
    ),
    FakeEntry(data={**_LC_DATA, "dhw_inlet_entity": "sensor.inlet"}),
)
_g_istale._prepare_dhw_inputs(_g_now43)
R.check(
    "a probe frozen for two days degrades to the seasonal model",
    _g_istale._thermal_params.dhw_inlet_current
    == _g_istale._thermal_params.seasonal_inlet_temp(
        _g_now43.timetuple().tm_yday
    ),
)

# --- the Tibber verdict split ----------------------------------------------------
# The stub has no HTTP session at all, which is precisely a network failure:
# it must read as "cannot connect", never as "your token is wrong".
R.check(
    "an unreachable Tibber is a connectivity verdict, not an auth one",
    _asyncio.run(_g_tibber(FakeHass(), "any-token")) == "cannot_connect",
)


# ===========================================================================
# v4.0.4 — the quarter grid, DST days, window arithmetic, price-level guards
# ===========================================================================
R.section("v4.0.4 — DST-day exclusion from price learning")

import os as _os
import subprocess as _subprocess
from zoneinfo import ZoneInfo as _ZoneInfo

from heatpump_optimizer.grid_fee import (
    GridFeeSchedule as _FeeSchedule,
    IMPLAUSIBLE_FEE_SEK_PER_KWH as _FEE_BOUND,
    max_abs_component as _fee_worst,
    parse_rules as _fee_parse,
)
from heatpump_optimizer.optimizer import (
    PRICE_MEAN_GUESS_EPS as _GUESS_EPS,
    _price_guess_weights as _guess_weights,
)
from heatpump_optimizer.price_model import (
    quarters_from_entries as _quarters_from_entries,
)

_STHLM = _ZoneInfo("Europe/Stockholm")


def _local_day_entries(first_utc: datetime, hours: int, base: float) -> list[dict]:
    """Hourly Tibber-style entries for one local day, built from UTC instants
    so the transition days carry exactly the offsets Tibber delivers."""
    return [
        {
            "starts_at": (first_utc + timedelta(hours=i))
            .astimezone(_STHLM)
            .isoformat(),
            "total": base + 0.01 * i,
        }
        for i in range(hours)
    ]


# Europe/Stockholm 2026: spring gap 29 Mar (23 local hours), autumn fold
# 25 Oct (25 local hours). Local midnight is 22:00 UTC (CEST) before the
# fold and 23:00 UTC (CET) after it.
_fold_day = _local_day_entries(
    datetime(2026, 10, 24, 22, 0, tzinfo=UTC), 25, 0.5
)
_gap_day = _local_day_entries(
    datetime(2026, 3, 28, 23, 0, tzinfo=UTC), 23, 0.5
)
_plain_day = _local_day_entries(
    datetime(2026, 10, 23, 22, 0, tzinfo=UTC), 24, 0.5
)
R.check(
    "the synthetic fold day really carries 25 hourly entries",
    len(_fold_day) == 25
    and len({e["starts_at"][-6:] for e in _fold_day}) == 2,
)
_hourly = hourly_from_entries(_plain_day + _fold_day + _gap_day)
R.check(
    "a plain 24-hour day trains the hourly shape",
    "2026-10-24" in _hourly and len(_hourly["2026-10-24"]) == 24,
    f"days: {sorted(_hourly)}",
)
R.check(
    "the 25-hour autumn fold day is excluded — its collapse used to pass "
    "the 24-hour gate with a fabricated hour 2",
    "2026-10-25" not in _hourly,
    f"days: {sorted(_hourly)}",
)
R.check(
    "the 23-hour spring gap day is excluded by the same predicate",
    "2026-03-29" not in _hourly,
)


def _quarter_day_entries(first_utc: datetime, hours: int) -> list[dict]:
    return [
        {
            "starts_at": (first_utc + timedelta(minutes=15 * q))
            .astimezone(_STHLM)
            .isoformat(),
            "total": 0.4 + 0.001 * q,
        }
        for q in range(hours * 4)
    ]


_q_days = _quarters_from_entries(
    _quarter_day_entries(datetime(2026, 10, 23, 22, 0, tzinfo=UTC), 24)
    + _quarter_day_entries(datetime(2026, 10, 24, 22, 0, tzinfo=UTC), 25)
)
R.check(
    "quarter learning sees the same exclusion: plain day in, fold day out",
    "2026-10-24" in _q_days
    and len(_q_days["2026-10-24"]) == 96
    and "2026-10-25" not in _q_days,
    f"days: {sorted(_q_days)}",
)

_naive_day = [
    {
        "starts_at": f"2026-10-25T{h:02d}:00:00",
        "total": 0.5 + 0.01 * h,
    }
    for h in range(24)
]
R.check(
    "naive timestamps carry one offset (None) and keep learning",
    "2026-10-25" in hourly_from_entries(_naive_day),
)

# ---------------------------------------------------------------------------
R.section("v4.0.4 — negative-mean initial guess")

_pos_prices = np.array([0.42, 1.31, 0.05, 2.5, 0.9, 0.63, 1.1, 0.77])
_old_form = np.clip(
    1.5 - _pos_prices / (np.mean(_pos_prices) + 1e-6), 0.2, 1.0
)
R.check(
    "a positive-mean horizon gets the historical formula bit for bit",
    np.array_equal(_guess_weights(_pos_prices), _old_form),
)

_neg_prices = np.array([-0.9, -0.1, -1.4, -0.3, -0.05, -2.0])
_neg_w = _guess_weights(_neg_prices)
R.check(
    "all-negative prices: the cheapest (most negative) step starts highest",
    int(np.argmax(_neg_w)) == int(np.argmin(_neg_prices))
    and int(np.argmin(_neg_w)) == int(np.argmax(_neg_prices)),
    f"weights {_neg_w}",
)
R.check(
    "and the guess is monotone in price rank, inside the same 0.2-1.0 band",
    bool(
        np.all(np.diff(_neg_w[np.argsort(_neg_prices)]) < 0)
    )
    and float(np.min(_neg_w)) >= 0.2 - 1e-12
    and float(np.max(_neg_w)) <= 1.0 + 1e-12,
)
# The historical formula on the same input, for the record: it INVERTED —
# the cheapest step clipped to the floor.
_neg_old = np.clip(1.5 - _neg_prices / (np.mean(_neg_prices) + 1e-6), 0.2, 1.0)
R.check(
    "the un-guarded formula really did invert on this input",
    _neg_old[int(np.argmin(_neg_prices))] == 0.2,
)
_zero_prices = np.array([-1.0, 1.0, -0.5, 0.5])
_zero_w = _guess_weights(_zero_prices)
R.check(
    "a near-zero mean takes the rank path instead of saturating the clip",
    int(np.argmax(_zero_w)) == 0 and float(np.min(_zero_w)) >= 0.2 - 1e-12,
    f"weights {_zero_w}",
)

# ---------------------------------------------------------------------------
R.section("v4.0.4 — grid-fee magnitude repair issue")

_fm_sched = _FeeSchedule(mode="rules", fixed=0.1, rules=_fee_parse("Nov-Mar = 25"))
R.check(
    "max_abs_component finds the öre-as-SEK rule and names its source",
    _fee_worst(_fm_sched) == (25.0, "rules"),
)
R.check(
    "an inactive layer has nothing to warn about",
    _fee_worst(_FeeSchedule(mode="none", fixed=99.0)) == (0.0, "fixed"),
)
R.check(
    "entity mode inspects the live value, rules mode ignores it",
    _fee_worst(_FeeSchedule(mode="entity"), 25.0) == (25.0, "entity")
    and _fee_worst(_fm_sched, 999.0)[1] == "rules",
)

_gf_steps = [
    datetime(2026, 1, 7, 12, 0, tzinfo=UTC) + timedelta(minutes=15 * i)
    for i in range(8)
]
_gf_bad = HeatPumpOptimizerCoordinator(
    FakeHass(),
    FakeEntry(
        data={**_LC_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= 25"}
    ),
)
_gf_vec = _gf_bad._fee_series(_gf_steps)
_gf_issues = [
    i for i in getattr(_gf_bad.hass, "issues", []) if i[1] == "grid_fee_magnitude"
]
R.check(
    "a 25 SEK/kWh rule — öre in a SEK field — raises the repair issue",
    len(_gf_issues) == 1
    and _gf_issues[0][2].get("translation_key") == "grid_fee_magnitude"
    and set(_gf_issues[0][2].get("translation_placeholders", {}))
    == {"rate", "source"},
)
R.check(
    "warn-only: the plan still prices with exactly what was typed",
    bool(np.all(_gf_vec == 25.0)),
    f"vector {_gf_vec[:2]}",
)
_gf_bad._fee_series(_gf_steps)
R.check(
    "the issue is raised once per offending value, not every cycle",
    len(
        [
            i
            for i in getattr(_gf_bad.hass, "issues", [])
            if i[1] == "grid_fee_magnitude"
        ]
    )
    == 1,
)
_gf_bad._config["grid_fee_rules"] = "= 0.25"
_gf_bad._fee_series(_gf_steps)
R.check(
    "a corrected configuration clears the issue on the next cycle",
    not [
        i
        for i in getattr(_gf_bad.hass, "issues", [])
        if i[1] == "grid_fee_magnitude"
    ],
)
_gf_ok = HeatPumpOptimizerCoordinator(
    FakeHass(),
    FakeEntry(
        data={**_LC_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= 0.25"}
    ),
)
_gf_ok._fee_series(_gf_steps)
R.check(
    "0.25 SEK/kWh — the value that was meant — raises nothing",
    not [
        i
        for i in getattr(_gf_ok.hass, "issues", [])
        if i[1] == "grid_fee_magnitude"
    ],
)
_gf_ent = HeatPumpOptimizerCoordinator(
    FakeHass({"sensor.fee": FakeState("25.0")}),
    FakeEntry(
        data={
            **_LC_DATA,
            "grid_fee_mode": "entity",
            "grid_fee_entity": "sensor.fee",
        }
    ),
)
_gf_ent._fee_series(_gf_steps)
_gf_ent_issues = [
    i for i in getattr(_gf_ent.hass, "issues", []) if i[1] == "grid_fee_magnitude"
]
R.check(
    "a fee sensor publishing öre trips the same issue, attributed to it",
    len(_gf_ent_issues) == 1
    and _gf_ent_issues[0][2]["translation_placeholders"]["source"] == "entity",
)

# ---------------------------------------------------------------------------
R.section("v4.0.4 — the quarter snap and DST windows, under a real timezone")

# The stub's DEFAULT_TIME_ZONE is fixed at import, so the timezone-dependent
# checks run in a subprocess with HASTUB_TZ set; see tests/dst_checks.py.
_dst = _subprocess.run(
    [sys.executable, "tests/dst_checks.py"],
    env={**_os.environ, "HASTUB_TZ": "Europe/Stockholm"},
    capture_output=True,
    text=True,
)
print(_dst.stdout, end="")
R.check(
    "the HASTUB_TZ subprocess suite passed",
    _dst.returncode == 0,
    (_dst.stdout + _dst.stderr)[-400:],
)

# ===========================================================================
# v4.0.5 — physics: one price of heat, honest tanks, honest learners
# ===========================================================================
R.section("v4.0.5 — one marginal COP per store, shared with the dynamics")

from dataclasses import replace as _dc_replace

from heatpump_optimizer.thermal_model import (
    dhw_coil_draw_reduction as _coil_split,
)

_p5 = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", buffer_max_temp=70.0,
)
# `from_config` arms the Carnot flow derate with any throttling valve; the
# direct constructor leaves it off, so arm it the way a real install has it.
_p5.cop_flow_carnot = True
_m5 = ThermalModel(_p5)
R.check(
    "marginal_cop('buffer') is the simulate step's own conversion",
    _m5.marginal_cop(-5.0, "buffer", store_temp=70.0)
    == _m5.compute_cop(-5.0, flow_temp=70.0),
    "thermal_model.py:1548 charges the tank at exactly this COP",
)
R.check(
    "marginal_cop('dhw') is compute_cop_dhw",
    _m5.marginal_cop(-5.0, "dhw", store_temp=55.0)
    == _m5.compute_cop_dhw(-5.0, 55.0),
)
R.check(
    "building-mass stores heat at the plain curve",
    _m5.marginal_cop(-5.0, "room") == _m5.compute_cop(-5.0)
    and _m5.marginal_cop(-5.0, "slab") == _m5.compute_cop(-5.0),
)
_p5_off = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", buffer_max_temp=70.0,
)
_m5_off = ThermalModel(_p5_off)
R.check(
    "without the Carnot derate the buffer collapses to the plain curve",
    _m5_off.marginal_cop(-5.0, "buffer", store_temp=70.0)
    == _m5_off.compute_cop(-5.0),
    "the cop_flow_carnot gate is what keeps unthrottled paths byte-identical",
)

# --- Terminal price of a stored kWh == the simulation's cost of storing it.
_cfg5 = _OptCfg(horizon_hours=24, time_step_minutes=15,
                target_temp=21.0, min_temp=19.0, max_temp=23.0)
_opt5 = _Opt(_m5, _cfg5)
_out5 = np.full(96, -5.0)
_prices5 = np.full(96, 1.0)
_caps5 = _opt5._settlement_caps(_out5)
_term5 = _opt5._terminal_cost(_prices5, _out5)
_f5 = lambda v: np.full(97, v)
_mass_buf = _p5.buffer_tank_thermal_mass
_t_lo = _term5(_f5(21.0), _f5(25.0), _f5(21.0), _f5(20.5),
               _f5(_caps5["buffer"] - 1.0))
_t_hi = _term5(_f5(21.0), _f5(25.0), _f5(21.0), _f5(20.5),
               _f5(_caps5["buffer"]))
_grad_buf = (_t_lo - _t_hi) / _mass_buf  # SEK per marginal stored kWh
_sim_cost = 1.0 / _m5.compute_cop(-5.0, flow_temp=_caps5["buffer"])
R.check(
    "the terminal credit repays a stored buffer kWh at the flow-derated COP "
    "the simulation charged to store it",
    abs(_grad_buf - _sim_cost) < 1e-9,
    f"terminal {_grad_buf:.4f} vs simulate {_sim_cost:.4f} SEK/kWh",
)
_grad_plain = 1.0 / _m5.compute_cop(-5.0)
R.check(
    "which is genuinely dearer than the plain curve the old code paid",
    _grad_buf > _grad_plain * 1.3,
    f"derated {_grad_buf:.4f} vs plain {_grad_plain:.4f} — the artificial "
    "COP gap the solver had to overcome before storing anything",
)
# Room deficits still convert at the plain curve. Only the upper floor's
# end moves here (the lower sits below the cap either way), so the marginal
# kWh is the upper mass's alone.
_t_room = _term5(_f5(20.0), _f5(25.0), _f5(20.0), _f5(20.5),
                 _f5(_caps5["buffer"]))
_grad_room = (_t_room - _term5(
    _f5(21.0), _f5(25.0), _f5(21.0), _f5(20.5), _f5(_caps5["buffer"])
)) / _p5.upper_floor_thermal_mass
R.check(
    "building-mass deficits keep the plain conversion",
    abs(_grad_room - _grad_plain) < 1e-9,
    f"room {_grad_room:.4f} vs plain {_grad_plain:.4f}",
)
# With the derate off, the whole term must reproduce the historical
# arithmetic bit for bit — that is the branch that keeps every unthrottled
# fixture untouched.
_opt5_off = _Opt(_m5_off, _cfg5)
_caps5_off = _opt5_off._settlement_caps(_out5)
_term5_off = _opt5_off._terminal_cost(_prices5, _out5)
_ends = {"room": 21.0, "slab": 25.0, "upper": 21.0, "lower": 20.5,
         "buffer": 45.0}
_expected_off = (
    float(np.percentile(_prices5, 25))
    * _cfg5.price_weight
    * (
        _p5_off.upper_floor_thermal_mass * max(0.0, _caps5_off["room"] - 21.0)
        + _p5_off.lower_floor_thermal_mass * max(0.0, _caps5_off["room"] - 20.5)
        + _p5_off.slab_thermal_mass * max(0.0, _caps5_off["slab"] - 25.0)
        + _p5_off.buffer_tank_thermal_mass
        * max(0.0, _caps5_off["buffer"] - 45.0)
    )
    / max(_m5_off.compute_cop(-5.0), 1e-6)
)
R.check(
    "derate off: the terminal term is the historical single-sum, exactly",
    _term5_off(_f5(21.0), _f5(25.0), _f5(21.0), _f5(20.5), _f5(45.0))
    == _expected_off,
    "unthrottled solves must keep their descent paths bit for bit",
)

# --- The reported settlement prices each tank share at its own COP too.
_base_end = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=50.0, outdoor_temperature=-5.0,
    dhw_temperature=47.0,
)
_caps_dhw = dict(_caps5, dhw=50.0)
_opt_end_a = _dc_replace(_base_end, dhw_temperature=47.0)
_opt_end_b = _dc_replace(_base_end, dhw_temperature=45.0)
_d_a = _opt5._deferred_energy_cost(
    _base_end, _opt_end_a, _prices5, _out5, include_dhw=True, caps=_caps_dhw
)
_d_b = _opt5._deferred_energy_cost(
    _base_end, _opt_end_b, _prices5, _out5, include_dhw=True, caps=_caps_dhw
)
_gap_dhw = _p5.dhw_tank_thermal_mass * 2.0
_exp_dhw = _gap_dhw / _m5.compute_cop_dhw(-5.0, 50.0) * 1.0
R.check(
    "a DHW deficit settles at compute_cop_dhw of its settlement temperature",
    abs((_d_b - _d_a) - _exp_dhw) < 1e-9,
    f"settled {(_d_b - _d_a):.4f} vs expected {_exp_dhw:.4f} SEK",
)
_opt_end_c = _dc_replace(_base_end, buffer_tank_temperature=48.0)
_d_c = _opt5._deferred_energy_cost(
    _base_end, _opt_end_c, _prices5, _out5, include_dhw=True, caps=_caps_dhw
)
_exp_buf = (
    _mass_buf * 2.0 / _m5.compute_cop(-5.0, flow_temp=_caps5["buffer"])
)
R.check(
    "and a buffer deficit at the flow-derated COP of its settlement ceiling",
    abs((_d_c - _d_a) - _exp_buf) < 1e-9,
    f"settled {(_d_c - _d_a):.4f} vs expected {_exp_buf:.4f} SEK",
)

# ---------------------------------------------------------------------------
R.section("v4.0.5 — settlement caps: the lower zone's slab, a reachable tank")

# The slab feeds only the lower zone (`q_slab_to_lower`); the upper floor is
# radiator-fed. Its ceiling is therefore sized from the lower zone alone,
# through the learned loss, with the lower zone's share of the gains.
_exp_slab = 21.0 + max(
    0.0,
    _p5.lower_floor_heat_loss_learned * (21.0 - (-5.0))
    - _p5.internal_gains * (1.0 - _p5.upper_floor_area_ratio),
) / max(_p5.slab_heat_transfer, 1e-6)
R.check(
    "two-zone slab cap is sized from the lower zone alone",
    _caps5["slab"] == _exp_slab,
    f"cap {_caps5['slab']:.3f} vs lower-zone formula {_exp_slab:.3f}",
)
_p5_ratio = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", lower_floor_loss_ratio=0.8,
)
_caps_ratio = _Opt(ThermalModel(_p5_ratio), _cfg5)._settlement_caps(_out5)
R.check(
    "and it moves with the learned split, like the dynamics it settles",
    _caps_ratio["slab"] < _caps5["slab"],
    f"ratio 0.8 gives {_caps_ratio['slab']:.3f}",
)
_p5_single = ThermalParameters()
_caps_single = _Opt(ThermalModel(_p5_single), _cfg5)._settlement_caps(_out5)
_exp_single = 21.0 + max(
    0.0,
    _p5_single.heat_loss_coefficient * (21.0 - (-5.0))
    - _p5_single.internal_gains,
) / max(_p5_single.slab_heat_transfer, 1e-6)
R.check(
    "single-zone keeps the historical formula exactly",
    _caps_single["slab"] == _exp_single,
)

# The buffer's cap is the ceiling the pump can still charge past, not the
# nameplate rating. A strong pump reaches the rating; a weak one against a
# cold day cannot, and settling the unreachable distance charged every plan
# for failing to hold a temperature no plan could reach.
R.check(
    "a strong pump's cap is the rating — mild installs are untouched",
    _caps5["buffer"] == 70.0,
    f"got {_caps5['buffer']:.1f}",
)
_p5_weak = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", buffer_max_temp=70.0,
    max_electrical_power=1.2,
)
_p5_weak.cop_flow_carnot = True
_opt_weak = _Opt(ThermalModel(_p5_weak), _cfg5)
_cap_cold = _opt_weak._settlement_caps(np.full(96, -15.0))["buffer"]
_cap_mild = _opt_weak._settlement_caps(np.full(96, 8.0))["buffer"]
R.check(
    "a weak pump against a cold day cannot reach the rating, and the cap "
    "says so",
    _cap_cold < 69.9,
    f"reachable ceiling {_cap_cold:.1f} °C",
)
R.check(
    "the reachable ceiling rises with milder weather, up to the rating",
    _cap_cold < _cap_mild <= 70.0,
    f"cold {_cap_cold:.1f} vs mild {_cap_mild:.1f}",
)

# ---------------------------------------------------------------------------
R.section("v4.0.5 — DHW conservation: a cold tank cannot pour hot water")

_ec_p = ThermalParameters(dhw_enabled=True, dhw_tank_volume=300.0)
_ec_m = ThermalModel(_ec_p)
_ec_C = _ec_p.dhw_tank_thermal_mass
_ec_ua = _ec_p.dhw_tank_heat_loss_coefficient
_ec_nominal = 5.0  # kW, a heavy constant draw against a 300 L tank
_ec_T = [25.0]
_ec_resid = 0.0
_ec_floor = 0.0
_ec_delivered = 0.0
for _i in range(96):
    _q_in = 8.0 if 40 <= _i < 64 else 0.0
    _T = _ec_T[-1]
    _q_loss = _ec_ua * (_T - 20.0)
    _Tn = _ec_m.simulate_dhw_step(
        _T, _q_in, 0.0, dt_hours=0.25, draw_power=_ec_nominal
    )
    # The step's own ledger: input minus booked draw, standby loss and any
    # refused charge, plus any floor-fabricated heat, must equal the stored
    # change exactly. The old floor clamp created energy with no ledger —
    # this balance is the check that cannot pass on it.
    _bal = _ec_C * (_Tn - _T) - (
        _q_in - _ec_m._step_dhw_draw_kw - _q_loss
        - _ec_m._step_dhw_refused + _ec_m._step_dhw_floor_injected
    ) * 0.25
    _ec_resid = max(_ec_resid, abs(_bal))
    _ec_floor = max(_ec_floor, _ec_m._step_dhw_floor_injected)
    _ec_delivered += _ec_m._step_dhw_draw_kw * 0.25
    _ec_draw_max = max(
        _ec_draw_max if _i else 0.0, _ec_m._step_dhw_draw_kw
    )
    _ec_T.append(_Tn)
R.check(
    "the booked draw never exceeds the nominal demand",
    _ec_draw_max <= _ec_nominal + 1e-12,
    f"peak booked draw {_ec_draw_max:.3f} kW",
)
R.check(
    "every step balances: in == out + losses + storage delta",
    _ec_resid < 1e-9,
    f"worst residual {_ec_resid:.2e} kWh",
)
R.check(
    "the inlet floor fabricated nothing — the scaled draw makes it inert",
    _ec_floor == 0.0,
    f"worst injection {_ec_floor:.4f} kW",
)
R.check(
    "a cold tank delivers less than the nominal demand, not the same",
    _ec_delivered < _ec_nominal * 96 * 0.25 - 1.0,
    f"delivered {_ec_delivered:.1f} of {_ec_nominal * 96 * 0.25:.1f} kWh asked",
)
R.check(
    "and the tank never pins to the inlet pouring imaginary heat",
    min(_ec_T) > _ec_p.dhw_inlet_reference + 0.5,
    f"minimum {min(_ec_T):.1f} °C against inlet {_ec_p.dhw_inlet_reference}",
)
# At or above the setpoint the mixed-at-tap convention makes the constant
# nominal exactly right: mixing shrinks the drawn volume, enthalpy stays put.
_ec_m.simulate_dhw_step(
    _ec_p.dhw_setpoint, 0.0, 0.0, dt_hours=0.25, draw_power=_ec_nominal
)
R.check(
    "a tank at the setpoint is debited exactly the nominal draw",
    _ec_m._step_dhw_draw_kw == _ec_nominal,
    "the fix is the cold-tank side only; hot tanks were already physical",
)

# The rating is now enforced in the model with refused-heat accounting, the
# buffer clamp's pattern, instead of trusting every caller to pre-clamp.
_hot = _ec_m.simulate_dhw_step(54.0, 500.0, 0.0, dt_hours=0.25, draw_power=0.0)
R.check(
    "charging cannot pass the tank rating, and the excess is booked",
    _hot == _ec_p.dhw_max_temp and _ec_m._step_dhw_refused > 0.0,
    f"landed {_hot:.1f} °C, refused {_ec_m._step_dhw_refused:.1f} kW",
)
_over = _ec_m.simulate_dhw_step(72.0, 0.0, 0.0, dt_hours=0.25, draw_power=0.0)
R.check(
    "a tank read above the rating cools at its physical rate, not by fiat",
    _over > 70.0 and _ec_m._step_dhw_refused == 0.0,
    f"72 °C cooled to {_over:.2f} °C — only the charging direction is clamped",
)

# One inlet reference everywhere: the coil split loses its hardcoded 10 °C.
_red_d, _coil_d = _coil_split(2.0, 40.0, 55.0)
R.check(
    "coil split at the default inlet is the historical arithmetic",
    abs(_red_d - 2.0 * (55.0 - 25.0) / 45.0) < 1e-12
    and abs(_red_d + _coil_d - 2.0) < 1e-12,
)
_red_c, _coil_c = _coil_split(2.0, 40.0, 55.0, inlet_temp=4.0)
R.check(
    "a real winter inlet changes the split and keeps the identity exact",
    abs(_red_c + _coil_c - 2.0) < 1e-12 and _coil_c > _coil_d,
    f"coil covers {_coil_c:.3f} kW at 4 °C vs {_coil_d:.3f} at 10 °C — a "
    "colder inlet gives the wood tank more of the rise to pre-heat",
)

# ---------------------------------------------------------------------------
R.section("v4.0.5 — sysid: the intercept the relax phase was smuggling")

from heatpump_optimizer.sysid import (
    PHASE_RELAX as _PH_RELAX,
    PHASE_STEP as _PH_STEP,
    SysIdSample as _SidSample,
)

_SID_C, _SID_UA, _SID_G = 6.0, 0.12, 0.5


def _sid_samples(gains):
    """A synthetic step response with a known constant free heat."""
    out = []
    temp, tout = 20.7, 0.0
    when = datetime(2026, 2, 10, 0, 0, tzinfo=UTC)
    for phase, power, steps in ((_PH_STEP, 3.0, 12), (_PH_RELAX, 0.0, 19)):
        for _ in range(steps):
            out.append(_SidSample(when, temp, tout, power, phase))
            temp += (1.0 / 6.0) * (
                power + gains - _SID_UA * (temp - tout)
            ) / _SID_C
            when += timedelta(minutes=10)
    return out


_sid = SystemIdentification()
_sid.samples = _sid_samples(_SID_G)
_sid_res = _sid.identify()
R.check(
    "known UA, C and gains are recovered together",
    _sid_res.completed
    and abs(_sid_res.heat_loss_kw_per_c - _SID_UA) < 0.01
    and abs(_sid_res.thermal_mass_kwh_per_c - _SID_C) < 0.3
    and abs(_sid_res.internal_gains_kw - _SID_G) < 0.05,
    f"UA {_sid_res.heat_loss_kw_per_c} C {_sid_res.thermal_mass_kwh_per_c} "
    f"G {_sid_res.internal_gains_kw} ({_sid_res.reason})",
)
# The defect this section exists for: without the intercept, the same data
# pushes the gains into UA and C. Fit the old two-column form on the same
# samples and show the bias the fix removes.
_sid_rows, _sid_targets = [], []
for _prev, _cur in zip(_sid.samples, _sid.samples[1:]):
    _dt_h = (_cur.when - _prev.when).total_seconds() / 3600.0
    _sid_rows.append(
        [-(_prev.room_temp - _prev.outdoor_temp), _prev.power_kw]
    )
    _sid_targets.append((_cur.room_temp - _prev.room_temp) / _dt_h)
_sid_old, *_ = np.linalg.lstsq(
    np.asarray(_sid_rows), np.asarray(_sid_targets), rcond=None
)
_sid_old_ua = float(_sid_old[0]) / float(_sid_old[1])
R.check(
    "the old no-intercept fit really was biased on this data",
    abs(_sid_old_ua - _SID_UA) > 0.02,
    f"no-intercept UA {_sid_old_ua:.4f} vs truth {_SID_UA}",
)
_sid_wild = SystemIdentification()
_sid_wild.samples = _sid_samples(5.0)
R.check(
    "an implausible fitted gain rejects the experiment instead of adopting it",
    not _sid_wild.identify().completed,
    _sid_wild.identify().reason,
)

# ---------------------------------------------------------------------------
R.section("v4.0.5 — learners: tracking error is not efficiency")

_L5_CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
}
_L5_STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-10.0", unit="°C"),
    "sensor.pump_power": FakeState("2700", unit="W"),
}


def _cop_learn(commanded, measured):
    coord = _Coord(_FakeHass(dict(_L5_STATES)), _FakeEntry(data=dict(_L5_CFG)))
    coord._current_action = {"power": commanded, "dhw_power": 0.0}
    coord._measured_power = measured
    coord._current_state.outdoor_temperature = -10.0  # outside the frost band
    before = coord._cop_scale
    coord._learn_measured_cop()
    return coord._cop_scale - before, coord._cop_samples


_moved, _n = _cop_learn(3.0, 1.5)
R.check(
    "a pure tracking error — pump at half the commanded power — moves "
    "cop_scale not at all",
    _moved == 0.0 and _n == 0,
    f"scale moved {_moved:+.5f} on {_n} samples",
)
_moved, _n = _cop_learn(3.0, 2.7)
R.check(
    "while a modest, efficiency-shaped gap still teaches",
    _moved > 1e-4 and _n == 1,
    f"scale moved {_moved:+.5f}",
)

# The interval learners' power source: measured where a meter exists,
# commanded only where none does, and no sample at all on a stale meter.
_ip_none = _Coord(
    _FakeHass(dict(_L5_STATES)),
    _FakeEntry(data={k: v for k, v in _L5_CFG.items()
                     if k != "heat_pump_power_entity"}),
)
_ip_none._current_action = {"power": 3.0, "dhw_power": 0.5}
R.check(
    "without a power entity the commanded space figure is all there is",
    _ip_none._interval_space_power() == 3.0,
)
_ip = _Coord(_FakeHass(dict(_L5_STATES)), _FakeEntry(data=dict(_L5_CFG)))
_ip._current_action = {"power": 3.0, "dhw_power": 0.5}
_ip._measured_power = 2.0
R.check(
    "with one, the meter wins, net of the hot-water allocation the meter "
    "cannot tell apart",
    _ip._interval_space_power() == 1.5,
)
_ip._measured_power = None
R.check(
    "a configured-but-stale meter yields no sample rather than a commanded "
    "guess",
    _ip._interval_space_power() is None,
    "a skipped interval loses convergence; a wrong power corrupts a "
    "persisted parameter",
)
_ip._measured_power = 2.0
_ip._immersion_active = True
R.check(
    "an immersion-latched meter is a different appliance's reading — skip",
    _ip._interval_space_power() is None,
)

# ---------------------------------------------------------------------------
R.section("v4.0.5 — the battery view shares the optimizer's caps")

_bat_p = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", buffer_max_temp=65.0,
    lower_floor_loss_ratio=0.8, house_heat_loss_scale=1.1,
)
_bat_state = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=20.5, slab_temperature=25.0,
    buffer_tank_temperature=40.0, outdoor_temperature=-5.0,
)
_bat5 = battery_view.build(
    _bat_p, _bat_state, comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=65.0, cop=3.2,
)
_bat_by_name = {c.name: c for c in _bat5.components}
R.check(
    "the buffer component's ceiling is the tank's configured rating — the "
    "same constant the simulation clamps at and the settlement caps read",
    _bat_by_name["buffer_tank"].max_temperature == _bat_p.buffer_max_temp,
    f"got {_bat_by_name['buffer_tank'].max_temperature}",
)
R.check(
    "a 40 °C tank no longer reads nearly full",
    _bat_by_name["buffer_tank"].soc < 0.5,
    f"soc {_bat_by_name['buffer_tank'].soc:.3f} — the comfort+20 offset "
    "published ~0.88 for the same tank",
)
R.check(
    "the zone losses are the learned ones the dynamics actually run",
    _bat_by_name["lower_floor"].loss_kw_per_c
    == _bat_p.lower_floor_heat_loss_learned * _bat_p.house_heat_loss_scale
    and _bat_by_name["upper_floor"].loss_kw_per_c
    == _bat_p.upper_floor_heat_loss * _bat_p.house_heat_loss_scale,
)
_bat_default = battery_view.build(
    ThermalParameters(two_zone_enabled=True), _bat_state,
    comfort_min=19.0, comfort_max=23.0, dhw_min=45.0, dhw_max=65.0, cop=3.2,
)
_bat_def_by_name = {c.name: c for c in _bat_default.components}
R.check(
    "at default learned values the loss figures are the raw configured ones",
    _bat_def_by_name["lower_floor"].loss_kw_per_c
    == ThermalParameters().lower_floor_heat_loss,
    "both corrections default to 1.0, so this half of the change is inert",
)

sys.exit(R.close("FEATURE CHECKS"))
