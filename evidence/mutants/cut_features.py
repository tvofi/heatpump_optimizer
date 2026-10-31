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

from harness import FakeHass, FakeState, Results, UTC, minutes_ago, with_config
from profiles import solve_inputs  # noqa: E402

import numpy as np

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer import battery as battery_view
from heatpump_optimizer import presets, price_tiles, pv
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
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.defrost import (
    DEFROST_LOSS_MULTIPLIER,
    DERATE_CONFIDENCE_SAMPLES,
    DERATE_MAX,
    HUMIDITY_CENTERS,
    DefrostDerate,
    DefrostWindow,
    derate_from_duty,
)
from heatpump_optimizer.external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
)
from heatpump_optimizer import inputs as inputs_mod
from heatpump_optimizer import flow_lift, pump_mode, pump_signals
from heatpump_optimizer.pump_signals import PumpSignals
from heatpump_optimizer.inputs import (
    InputReader,
    InputReading,
    normalize_power_kw,
    parse_bool,
    stale_summary,
)
from heatpump_optimizer.price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
)
from heatpump_optimizer.sysid import (
    HousePlant,
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakBilling,
    PeakTracker,
    _smooth_topk_sum,
    peak_cost,
    peak_cost_smooth,
    realised_peak,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.plan_slots import plan_slots
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext
from heatpump_optimizer.optimizer import _Horizon


def _owned_params(params):
    """A test owner of ``params``, as the coordinator's ``_publish_params`` owns
    its own: the learner reads through ``params`` and publishes a new snapshot."""
    from dataclasses import replace as _replace
    box = [params]

    def publish(**fields):
        box[0] = _replace(box[0], **fields)

    return {"params": lambda: box[0], "publish": publish}


R = Results("Feature modules")


def _keystone_expire_away():
    """`_expire_away_override`'s (active, return-time) pair, which
    `_resolve_away` unpacks, on a bare coordinator: one live override and one
    lapsed. Its own returns, not the pair as an end-to-end cycle sees it."""
    coord = object.__new__(Coord)
    coord._away_state = away_mode.AwayState(override_active=True)
    saved = []

    def spawn(coro):
        saved.append(coro.__qualname__)
        coro.close()

    coord._spawn = spawn
    now = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
    ret = now + timedelta(hours=6)
    coord._away_state.override_return_iso = ret.isoformat()
    live = coord._expire_away_override(now)
    lapsed = coord._expire_away_override(now + timedelta(hours=7))
    return live, lapsed, ret, saved


# A keystone: a broken return here makes every later away cycle raise inside
# `_resolve_away`, and the whole script outruns the mutation pin run's budget
# (PR #2632's two timed-out pin runs). Failing, it ends the run at once.
_ks_live, _ks_lapsed, _ks_ret, _ks_saved = _keystone_expire_away()
if not R.check(
    "keystone: _expire_away_override returns the live override's (True, "
    "return time) and a lapsed one's (False, None), saving only the lapse",
    _ks_live == (True, _ks_ret) and _ks_lapsed == (False, None)
    and _ks_saved == ["persist_override"],
    str((_ks_live, _ks_lapsed, _ks_saved)),
):
    sys.exit(R.close("FEATURE CHECKS"))


def _WS(outdoor, wind=None, rain=None, solar=None, humidity=None, ext=None):
    """The physics module's weather record from this file's fixture arrays
    (#1776): the series the trajectory entry points now take as one frozen
    object instead of five positional lists."""
    return WeatherSeries(
        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain,
        solar_radiation=solar, humidity=humidity, external_heat_kw=ext)


def _dhw_horizon(*, prices, outdoor, n, dt, step_hours=None, state=None,
                 step_weekdays=None, holiday_flags=None, humidity=None,
                 dhw_pins=None):
    """A minimal solve horizon for the DHW planner's direct calls (#1776)."""
    return _Horizon(
        initial_state=state or ThermalState(
            room_temperature=21.0, slab_temperature=22.0,
            outdoor_temperature=-5.0, dhw_temperature=48.0,
            dhw_hours_since_legionella=20.0,
            buffer_tank_temperature=40.0),
        prices=prices, outdoor_temps=outdoor,
        wind_speeds=np.zeros(n), precipitation=np.zeros(n),
        solar_radiation=np.zeros(n), start_time=None, n_steps=n, dt=dt,
        comfort_targets=np.full(n, 21.0), temp_min_bounds=np.full(n, 17.0),
        temp_max_bounds=np.full(n, 23.0),
        step_hours=np.arange(n) * dt if step_hours is None else step_hours,
        solar_gains=np.zeros(n), heat_loss_factors=np.ones(n), forecast={},
        t_start=0.0, step_weekdays=step_weekdays, holiday_flags=holiday_flags,
        humidity=humidity, dhw_pins=dhw_pins,
    )


def _dhw_ctx(*, prices, outdoor, n, dt, c_dhw, p_dhw_max,
             min_run_power=0.1, max_lead_steps=24, humidity=None,
             import_prices=None):
    """The DHW planners' shared record for direct calls (#1776). The floor
    repair ranks at ``import_prices``, defaulting to the same series."""
    return _DhwPlanContext(
        prices=prices, import_prices=prices if import_prices is None
        else import_prices,
        outdoor_temps=outdoor, humidity=humidity,
        n_steps=n, dt=dt, c_dhw=c_dhw, p_dhw_max=p_dhw_max,
        min_run_power=min_run_power, max_lead_steps=max_lead_steps)


def _solve_record_now(coord):
    """The record a solve started now would plan with (#1736): what the
    solve's tail -- the fuse advisor, the price tiles -- is handed."""
    from homeassistant.util import dt as _rec_dt
    from heatpump_optimizer.plan_step import plan_step_start

    now = _rec_dt.now()
    return coord._solve_record(plan_step_start(now), coord._forecast_arrays(now))


def _dhw_planner(opt):
    """The DhwPlanner ``opt.optimize`` would build from its current inputs.

    The DHW planner core moved off HeatPumpOptimizer (#1743); a check that
    drives one of its stages directly drives it on this planner.
    """
    return DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)


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

# Clock skew: a hub whose clock runs behind the sensor stamps a state in
# the future. Clamping that to age 0.0 is the #775 fail-open — a backward
# host-clock step then reports every input as brand new. Not knowable is
# stale, not fresh. Untimestamped stubs stay usable (the check below).
future = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(-30, NOW))}
)
_future_reading = future.read("indoor_temp_entity")
R.check(
    "a future-stamped state is stale, not age 0",
    (not _future_reading.ok)
    and _future_reading.stale
    and _future_reading.age_minutes is None,
    f"ok={_future_reading.ok} age={_future_reading.age_minutes} "
    f"problem={_future_reading.problem}",
)
_back = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(-240, NOW))}
)
_back_reading = _back.read("indoor_temp_entity")
R.check(
    "a 4 h backward host-clock step flags the reading stale",
    _back_reading.stale and not _back_reading.ok,
    f"problem={_back_reading.problem} age={_back_reading.age_minutes}",
)

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

# R5-D1-06 (#1297): `float()` parses more than numbers. "nan", "inf",
# "-inf", "1e999" and "Infinity" all float() without raising, so a sensor
# publishing one reached the thermal state as a non-finite float -- a "nan"
# indoor temperature published a FAILED plan at inflated cost with NaN
# savings while the cycle reported success. `read` refuses them with the
# same not_numeric problem a word gets, after unit conversion (a NaN in °F
# converts to a NaN in °C; the guard has to sit on the converted value).
_NONFINITE_STATES = ("nan", "inf", "-inf", "1e999", "NaN", "Infinity")
_nonfinite = {
    s: reader({"sensor.indoor": FakeState(s)}).read("indoor_temp_entity")
    for s in _NONFINITE_STATES
}
R.check(
    "a non-finite state string is refused exactly like a word",
    all(
        r.problem == "not_numeric" and r.value is None
        for r in _nonfinite.values()
    ),
    "; ".join(
        f"{s!r} -> {r.problem}, value {r.value!r}"
        for s, r in _nonfinite.items()
    ),
)
_nonfinite_f = reader(
    {
        "sensor.indoor": FakeState(
            "nan", unit="°F", attributes={"unit_of_measurement": "°F"}
        )
    }
).read("indoor_temp_entity")
R.check(
    "a non-finite value is refused after unit conversion too",
    _nonfinite_f.problem == "not_numeric" and _nonfinite_f.value is None,
    f"{_nonfinite_f.problem}, value {_nonfinite_f.value!r}",
)
_nonfinite_ok_f = reader(
    {
        "sensor.indoor": FakeState(
            "70.0", unit="°F", attributes={"unit_of_measurement": "°F"}
        )
    }
).read("indoor_temp_entity")
R.check(
    "the °F path itself keeps working (null control for the guard above)",
    _nonfinite_ok_f.ok and abs(_nonfinite_ok_f.value - 21.1111) < 0.001,
    f"problem {_nonfinite_ok_f.problem}, value {_nonfinite_ok_f.value!r}",
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
R.check(
    "the summary is human-readable",
    stale_summary(health) == "1 stale, 1 missing",
    stale_summary(health),
)
R.check(
    "the evidence names the entity",
    any(d["entity_id"] == "sensor.indoor" for d in health.details()),
)

# The owner's ask (2026-09-14): the input_problem flag must say WHICH
# input flipped it. The health snapshot derives the two published shapes
# from the same readings the flag itself reads: the failing entity ids,
# and one short line per failure.
R.check(
    "the failing entity ids are listed",
    health.problem_entity_ids == ["sensor.indoor", "sensor.tank"],
)
R.check(
    "each failure reads as one line naming entity and class",
    health.problem_messages()
    == [
        "sensor.tank: unavailable",
        "sensor.indoor: stale (last report 600 min)",
    ],
    str(health.problem_messages()),
)

# Units: guessing kW would read 3000 W as 3000 kW.
R.check("watts are converted to kW", normalize_power_kw(3000.0, "W") == 3.0)
R.check("kilowatts pass through", normalize_power_kw(3.0, "kW") == 3.0)
R.check(
    "an unrecognised unit is refused rather than guessed",
    normalize_power_kw(3000.0, "furlongs") is None,
)
R.check("a missing unit is refused", normalize_power_kw(3000.0, None) is None)

# D7-s2-61: the one live-state power parse and its three sign policies. Each
# row is a policy's own answer; the non-finite, word and unit rows are every
# policy's "no reading".
from heatpump_optimizer.inputs import state_power_kw as _spk  # noqa: E402
_spk_rows = {
    ("-400", "W"): (-0.4, 0.0, None),
    ("0", "kW"): (0.0, 0.0, None),
    ("2500", "W"): (2.5, 2.5, 2.5),
    ("inf", "kW"): (None, None, None),
    ("1e400", "kW"): (None, None, None),
    ("1e306", "MW"): (None, None, None),  # finite in, overflows on conversion
    ("unknown", "kW"): (None, None, None),
    ("3", "furlong"): (None, None, None),
}
_spk_got = {
    k: tuple(_spk(FakeState(k[0], unit=k[1]), sign=p) for p in ("signed", "clamp", "positive"))
    for k in _spk_rows
}
R.check(
    "a power state parses to finite kW under the caller's sign policy, or to no reading",
    _spk_got == _spk_rows and _spk(None) is None,
    f"got {_spk_got}",
)

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
R.check(
    "an unknown unit reads as words, not a token",
    bad_unit.health.problem_messages() == ["sensor.pump_power: unknown unit"],
    str(bad_unit.health.problem_messages()),
)

# The word-valued classes reach the same list: an unrecognised mode word
# (read_state with a valid set) and a free-text flag sensor that is not a
# flag (read_bool, strict outside the flag domains).
_wording_reader = InputReader(
    FakeHass(
        {
            "sensor.mode": FakeState("banana"),
            "sensor.flag": FakeState("maybe"),
        }
    ),
    {
        **CONFIG,
        "heat_pump_mode_entity": "sensor.mode",
        "heat_pump_defrost_entity": "sensor.flag",
    },
    now=lambda: NOW,
)
_wording_reader.read_state(
    "heat_pump_mode_entity", valid=("heating", "idle", "dhw", "off")
)
_wording_reader.read_bool("heat_pump_defrost_entity")
R.check(
    "every word-valued failure class renders in words a user can read",
    _wording_reader.health.problem_messages()
    == [
        "sensor.flag: not a yes/no flag",
        "sensor.mode: unrecognized state",
    ],
    str(_wording_reader.health.problem_messages()),
)
R.check(
    "an unconfigured slot contributes no source and no line",
    _wording_reader.health.problem_entity_ids == ["sensor.flag", "sensor.mode"],
    str(_wording_reader.health.problem_entity_ids),
)

# Temperature and energy units (#961): Home Assistant converts a
# device_class:temperature sensor to the instance unit system in the state
# machine, so a US-customary install hands the integration the same physical
# plant in °F -- and a device-class-less sensor can publish degF spellings.
# `read` consults the entity's declared unit rather than adopting the raw
# number as degC/kWh, the same principle `read_power_kw` applies to W. The
# values are the finder's plant: indoor 21.4 °C reports as 70.5 °F, the DHW
# tank 52.0 °C as 125.6 °F, the meter 1234.5 kWh as 1234500 Wh.
us_reader = InputReader(
    FakeHass(
        {
            "sensor.us_indoor": FakeState("70.5", unit="°F", last_updated=NOW),
            "sensor.us_tank": FakeState("125.6", unit="°F", last_updated=NOW),
            "sensor.us_meter": FakeState("1234500", unit="Wh", last_updated=NOW),
            "sensor.us_inlet": FakeState("294.55", unit="K", last_updated=NOW),
            "sensor.se_indoor": FakeState("21.4", unit="°C", last_updated=NOW),
            "sensor.odd_tank": FakeState("21.4", unit="Réaumur", last_updated=NOW),
        }
    ),
    {
        "indoor_temp_entity": "sensor.us_indoor",
        "dhw_temp_entity": "sensor.us_tank",
        "heat_pump_energy_entity": "sensor.us_meter",
        "floor_return_temp_entity": "sensor.us_inlet",
        "outdoor_temp_entity": "sensor.se_indoor",
        "buffer_tank_temp_entity": "sensor.odd_tank",
    },
    now=lambda: NOW,
)
us_indoor = us_reader.read("indoor_temp_entity")
R.check(
    "a °F temperature is converted to °C on read",
    us_indoor.ok and abs(us_indoor.value - (70.5 - 32.0) * 5.0 / 9.0) < 1e-9,
    f"got {us_indoor.value!r} for a plant at 21.4 °C reporting 70.5 °F",
)
us_dhw = us_reader.read("dhw_temp_entity")
R.check(
    "the DHW tank's °F reading converts exactly",
    us_dhw.ok and abs(us_dhw.value - 52.0) < 1e-9,
    f"got {us_dhw.value!r} for a tank at 52.0 °C reporting 125.6 °F",
)
us_meter = us_reader.read("heat_pump_energy_entity")
R.check(
    "a Wh energy meter is converted to kWh on read",
    us_meter.ok and abs(us_meter.value - 1234.5) < 1e-9,
    f"got {us_meter.value!r} for a meter at 1234.5 kWh reporting 1234500 Wh",
)
us_kelvin = us_reader.read("floor_return_temp_entity")
R.check(
    "a kelvin reading is converted to °C on read",
    us_kelvin.ok and abs(us_kelvin.value - 21.4) < 1e-9,
    f"got {us_kelvin.value!r} for 294.55 K",
)
R.check(
    "a °C state still reads bit-for-bit",
    us_reader.read("outdoor_temp_entity").value == 21.4,
)
odd_unit = us_reader.read("buffer_tank_temp_entity")
R.check(
    "an unrecognised unit keeps today's raw read instead of a guess",
    odd_unit.ok and odd_unit.value == 21.4 and odd_unit.problem is None,
    f"got {odd_unit.value!r} ({odd_unit.problem})",
)


# ===========================================================================
# Round 9, F4.1: class-named blocks, sorted by class
# ===========================================================================
from dataclasses import replace as _r9f41_replace  # noqa: E402
import ast as _r9f41_ast  # noqa: E402
import re as _r9f41_re  # noqa: E402

from heatpump_optimizer import const as _r9f41_const  # noqa: E402
from heatpump_optimizer import sysid as _r9f41_sysid  # noqa: E402

# --- R9 N-clamp-range (#1673): the flow-lift bias reaches the real supply ----
R.section("R9 N-clamp-range: the flow-lift bias reaches the plant's supply (D2-s2-02)")

# The model's own curve asks 22-28 C of a default house, so a plant at 50 C
# sits 20-odd K above it; the priced supply must be able to get there.
_r9f41_p = ThermalParameters(flow_curve_cop=True)
_r9f41_curve = flow_lift.curve_supply_temp(
    ThermalModel(_r9f41_p), -5.0, _r9f41_p.flow_curve_indoor_target
)
_r9f41_bias = flow_lift.FlowCurveBias()
for _ in range(20):
    _r9f41_bias.observe(50.0, _r9f41_curve)
_r9f41_priced = ThermalModel(
    _r9f41_replace(_r9f41_p, flow_curve_bias=_r9f41_bias.bias_k)
).curve_flow_temp(-5.0)
R.check(
    "D2-s2-02: a 50 C plant against the model's curve is priced at 50 C, "
    "not pinned 15 K over the curve",
    _r9f41_curve is not None
    and _r9f41_priced is not None
    and abs(_r9f41_priced - 50.0) < 1e-9,
    f"curve {_r9f41_curve}, bias {_r9f41_bias.bias_k}, priced {_r9f41_priced}",
)
_r9f41_under = flow_lift.FlowCurveBias()
for _ in range(20):
    _r9f41_under.observe(_r9f41_curve - 40.0, _r9f41_curve)
R.check(
    "D2-s2-02: the bias still stops FLOW_BIAS_CLAMP_K under the curve",
    _r9f41_under.bias_k == -flow_lift.FLOW_BIAS_CLAMP_K,
    f"bias {_r9f41_under.bias_k}",
)
_r9f41_hot = flow_lift.FlowCurveBias()
_r9f41_hot.observe(flow_lift.FLOW_SUPPLY_MAX_C + 47.0, 25.0)
R.check(
    "D2-s2-02: a supply no direct plant runs at (degF adopted raw) is refused "
    "as a sample, not absorbed",
    _r9f41_hot.samples == 0 and _r9f41_hot.bias_k == 0.0,
    f"samples {_r9f41_hot.samples}, bias {_r9f41_hot.bias_k}",
)
_r9f41_ceiling = flow_lift.FlowCurveBias()
for _ in range(20):
    _r9f41_ceiling.observe(flow_lift.FLOW_SUPPLY_MAX_C, 25.0)
R.check(
    "D2-s2-02: a plant at the supply ceiling is learned all the way up",
    abs(_r9f41_ceiling.bias_k - (flow_lift.FLOW_SUPPLY_MAX_C - 25.0)) < 1e-9,
    f"bias {_r9f41_ceiling.bias_k}",
)
_r9f41_loaded = flow_lift.FlowCurveBias.from_dict({"bias_k": 25.0, "samples": 9})
_r9f41_wild = flow_lift.FlowCurveBias.from_dict({"bias_k": 500.0, "samples": 9})
R.check(
    "D2-s2-02: a stored bias this version learns loads as stored; a wild one "
    "is re-clamped to the supply ceiling",
    _r9f41_loaded.bias_k == 25.0
    and _r9f41_wild.bias_k == flow_lift.FLOW_SUPPLY_MAX_C,
    f"loaded {_r9f41_loaded.bias_k}, wild {_r9f41_wild.bias_k}",
)
# A restored or mild-day bias meets a colder day's curve: the priced supply is
# held to the ceiling however the sum lands (D2-s2-02 fix review).
_r9f41_cold = ThermalModel(
    _r9f41_replace(_r9f41_p, flow_curve_bias=_r9f41_wild.bias_k)
).curve_flow_temp(-20.0)
R.check(
    "D2-s2-02: a restored bias at the ceiling prices no supply past "
    "FLOW_SUPPLY_MAX_C on the coldest curve",
    _r9f41_cold == flow_lift.FLOW_SUPPLY_MAX_C,
    f"priced {_r9f41_cold}",
)
# The fix review's three survivors (#1704), each pinned by its own mutant.
_r9f41_at80 = flow_lift.FlowCurveBias()
_r9f41_at80.observe(80.0, 25.0)
R.check(
    "D2-s2-02: the supply ceiling is 75 C, so an 80 C measured supply is "
    "refused as a sample",
    flow_lift.FLOW_SUPPLY_MAX_C == 75.0 and _r9f41_at80.samples == 0,
    f"ceiling {flow_lift.FLOW_SUPPLY_MAX_C}, samples {_r9f41_at80.samples}",
)
_r9f41_steep = flow_lift.FlowCurveBias.from_dict({"bias_k": 10.0, "samples": 9})
_r9f41_steep.observe(75.0, 80.0)
_r9f41_steeper = flow_lift.FlowCurveBias()
_r9f41_steeper.observe(70.0, 100.0)
R.check(
    "D2-s2-02: on a curve above the ceiling the hot-side bound is zero, not "
    "negative: a positive bias lands at 0 and the cold clamp still holds",
    _r9f41_steep.bias_k == 0.0
    and _r9f41_steeper.bias_k == -flow_lift.FLOW_BIAS_CLAMP_K,
    f"80 C curve {_r9f41_steep.bias_k}, 100 C curve {_r9f41_steeper.bias_k}",
)
R.check(
    "D2-s2-02: a non-finite outdoor temperature prices no curve flow at all",
    ThermalModel(_r9f41_p).curve_flow_temp(float("nan")) is None,
    f"priced {ThermalModel(_r9f41_p).curve_flow_temp(float('nan'))}",
)

# --- R9 N-future-instant (#1660): a stored instant ahead of the clock --------
R.section("R9 N-future-instant: a persisted instant ahead of the clock (FI-sw1, FI-sw2, FI-sw3, FI-sw4, FI-rca1)")
import asyncio as _fi_aio  # noqa: E402
import json as _fi_json  # noqa: E402
from harness import FakeEntry as _fi_entry  # noqa: E402
from heatpump_optimizer import const as _fi_const  # noqa: E402
from heatpump_optimizer.ledger import month_key as _fi_month  # noqa: E402
from homeassistant.helpers import storage as _fi_storage  # noqa: E402
from homeassistant.util import dt as _fi_dt  # noqa: E402

# Each instance through its real store and loader, the clock frozen aware, and
# a stamp written 400 days ahead (the RCA's repro_loaders.py shape; a parse
# alone is not the seam, a use-time clamp inside one is a no-op there). The
# restart is at T0 and the gate reads at the stated time. Every row owes a null
# control: an honest stamp whose window must still hold.
_FI_T0 = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
_FI_D30 = _FI_T0 + timedelta(days=30)
_FI_AHEAD = _FI_T0 + timedelta(days=400)


def _fi_restart(at, store_of, payload, loader):
    """A coordinator restarted at ``at`` over ``payload``, read by its real loader."""
    _fi_storage._DISK.clear()
    _fi_dt.freeze(at)
    c = Coord(FakeHass(), _fi_entry(data={
        _fi_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        _fi_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        _fi_const.CONF_DHW_TANK_VOLUME: 180.0,
        _fi_const.CONF_OUTAGE_RECOVERY_ENABLED: True,
        _fi_const.CONF_SNOW_ROOF_FACTOR_ENABLED: True,
        _fi_const.CONF_IMMERSION_FEEDBACK_ENABLED: True,
        _fi_const.CONF_MAIN_FUSE_A: 25,
    }))
    _fi_storage._DISK[store_of(c)._key] = _fi_json.dumps(payload)
    _fi_aio.run(loader(c))
    return c


def _fi_fuse_held(stamp, gate):
    """FI-sw1: the 7-day recompute cooldown still holds at ``gate``."""
    c = _fi_restart(
        _FI_T0, lambda k: k._ledger_store,
        {"fuse_advisor": {"month": _fi_month(_FI_T0), "candidate_kw": 1.0},
         "fuse_advisor_at": stamp.isoformat()},
        lambda k: k._async_load_ledger())
    for when in (_FI_T0, gate):
        _fi_dt.freeze(when)
        before = c._fuse_advisor_at
        try:
            _fi_aio.run(c._maybe_run_fuse_advisor(_solve_record_now(c)))
        except Exception:  # noqa: BLE001 -- only whether the cooldown held is read
            pass
    return c._fuse_advisor_at == before


def _fi_snow_damped(stamp, at):
    """FI-sw2: the heavy-snow damping window is open at ``at``."""
    c = _fi_restart(
        _FI_T0, lambda k: k._thermal_learning_store,
        {"last_heavy_snow": stamp.isoformat()},
        lambda k: k._async_load_thermal_learning())
    _fi_dt.freeze(at)
    c._snow_accum_last, c._snow_accum_cm = None, 0.0
    return c._update_snow_memory(at, np.zeros(4))


def _fi_immersion_margin(stamp, at):
    """FI-sw4: the immersion margin three recent events buy at ``at``."""
    c = _fi_restart(
        _FI_T0, lambda k: k._thermal_learning_store,
        {"immersion_events": [stamp.isoformat()] * 3},
        lambda k: k._async_load_thermal_learning())
    _fi_dt.freeze(at)
    return c._immersion_dhw_margin(at)


def _fi_legionella_due(stamp, at):
    """FI-rca1: hours until the anti-legionella cycle is due at ``at``."""
    c = _fi_restart(
        _FI_T0, lambda k: k._legionella.store,
        {"last_cycle": stamp.isoformat()},
        lambda k: k._legionella.async_load())
    c._thermal_params.dhw_legionella_enabled = True
    _fi_dt.freeze(at)
    return c._legionella.due_in_hours()


def _fi_outage(stamp):
    """FI-sw3: a restart six hours after T0 opens the staggered recovery."""
    c = _fi_restart(
        _FI_T0 + timedelta(hours=6), lambda k: k._energy_store,
        {"last_tick": stamp.isoformat()},
        lambda k: k._async_load_energy_totals())
    return c._outage_recovery_until is not None


def _fi_outage_direct(stamp):
    """FI-sw3, a caller that bypasses the store's bound: the stamp as written."""
    c = _fi_restart(
        _FI_T0 + timedelta(hours=6), lambda k: k._energy_store, {},
        lambda k: k._async_load_energy_totals())
    c._detect_outage(stamp.isoformat())
    return c._outage_recovery_until is not None


try:
    _fi_got = {
        "fuse ahead": _fi_fuse_held(_FI_T0 + timedelta(days=5), _FI_T0 + timedelta(days=10)),
        "fuse honest": _fi_fuse_held(_FI_T0 - timedelta(days=1), _FI_T0 + timedelta(days=3)),
        "snow ahead": _fi_snow_damped(_FI_AHEAD, _FI_D30),
        "snow honest": _fi_snow_damped(_FI_T0 - timedelta(days=1), _FI_T0),
        "immersion ahead": _fi_immersion_margin(_FI_AHEAD, _FI_D30),
        "immersion honest": _fi_immersion_margin(_FI_T0 - timedelta(hours=1), _FI_T0),
        "legionella ahead": _fi_legionella_due(_FI_AHEAD, _FI_D30),
        "legionella honest": _fi_legionella_due(_FI_T0 - timedelta(days=1), _FI_T0),
        "outage cut": _fi_outage(_FI_T0),
        "outage ahead": _fi_outage(_FI_AHEAD),
        "outage ahead by a minute": _fi_outage(_FI_T0 + timedelta(hours=6, minutes=1)),
        "outage plain restart": _fi_outage(_FI_T0 + timedelta(hours=6) - timedelta(minutes=10)),
        "outage at now": _fi_outage(_FI_T0 + timedelta(hours=6)),
        "outage zoned stamp": _fi_outage(
            (_FI_T0 + timedelta(hours=5, minutes=50)).astimezone(
                timezone(timedelta(hours=5)))),
        "outage unbounded ahead": _fi_outage_direct(_FI_AHEAD),
        "outage unbounded honest": _fi_outage_direct(_FI_T0 + timedelta(hours=5, minutes=50)),
    }
finally:
    _fi_dt.freeze(None)
    _fi_storage._DISK.clear()

R.check(
    "FI-sw1: a fuse-advisor stamp ahead of the clock, inside its month, does not "
    "hold the 7-day cooldown past it; an honest recent stamp still does",
    _fi_got["fuse ahead"] is False and _fi_got["fuse honest"] is True,
    f"held at day 10 with a stamp 5 days ahead {_fi_got['fuse ahead']}; "
    f"held at day 3 with an honest stamp {_fi_got['fuse honest']}",
)
R.check(
    "FI-sw2: a heavy-snow stamp ahead of the clock does not keep the damping on "
    "30 days later; an honest day-old stamp still does",
    _fi_got["snow ahead"] is False and _fi_got["snow honest"] is True,
    f"ahead {_fi_got['snow ahead']}, honest {_fi_got['snow honest']}",
)
R.check(
    "FI-sw4: three immersion events stamped ahead of the clock buy no margin; "
    "three honest recent ones still do",
    _fi_got["immersion ahead"] == 0.0 and _fi_got["immersion honest"] > 0.0,
    f"ahead {_fi_got['immersion ahead']}, honest {_fi_got['immersion honest']}",
)
R.check(
    "FI-rca1: a legionella cycle stamped ahead of the clock does not postpone "
    "the next one for the skew; an honest day-old cycle is not yet due",
    _fi_got["legionella ahead"] < 0.0 and _fi_got["legionella honest"] > 0.0,
    f"due in {_fi_got['legionella ahead']} h with a stamp 400 days ahead, "
    f"{_fi_got['legionella honest']} h with an honest one",
)
R.check(
    "FI-sw3: a stored last_tick ahead of the clock reads as an outage "
    "(tvofi's rule, card C13); a real cut still does, and a plain restart, or "
    "a tick at the restart instant, still does not",
    _fi_got["outage ahead"] is True
    and _fi_got["outage ahead by a minute"] is True
    and _fi_got["outage cut"] is True
    and _fi_got["outage plain restart"] is False
    and _fi_got["outage at now"] is False
    and _fi_got["outage zoned stamp"] is False
    and _fi_got["outage unbounded ahead"] is True
    and _fi_got["outage unbounded honest"] is False,
    f"{ {k: v for k, v in _fi_got.items() if k.startswith('outage')} }",
)

# --- R9 N-plausibility (#1659): a live input meets its physical window ------
R.section("R9 N-plausibility: live inputs meet their physical window (D1-s2-02, D1-s1-03)")
import asyncio as _np_aio  # noqa: E402
from types import SimpleNamespace as _np_ns  # noqa: E402
from harness import FakeEntry as _np_entry  # noqa: E402
from heatpump_optimizer.coordinator import _plausible_forecast_rows  # noqa: E402

# D1-s2-02, the weather family: the boundary is the validation at the storage
# point, driven here directly. The first row is the null control -- a healthy
# row comes back byte-identical, so the boundary is not a rewrite.
_np_rows = _plausible_forecast_rows([
    {"datetime": "2026-01-15T12:00:00+01:00", "temperature": -5.0,
     "wind_speed": 3.0, "precipitation": 0.5, "humidity": 80.0},
    {"datetime": "2026-01-15T13:00:00+01:00", "temperature": 1e308,
     "wind_speed": -2.0, "precipitation": 5.0},
    "x", None, 5,
])
R.check(
    "a forecast row's out-of-window field is dropped to its consumer's "
    "fallback and a non-dict row is not stored at all (D1-s2-02)",
    _np_rows[0] == {"datetime": "2026-01-15T12:00:00+01:00", "temperature": -5.0,
                    "wind_speed": 3.0, "precipitation": 0.5, "humidity": 80.0}
    and _np_rows[1] == {"datetime": "2026-01-15T13:00:00+01:00", "temperature": None,
                        "wind_speed": None, "precipitation": 5.0}
    and len(_np_rows) == 2,
    f"{_np_rows!r}",
)
R.check(
    "a forecast that is not a list of rows stores nothing (D1-s2-02)",
    _plausible_forecast_rows("x") == [] and _plausible_forecast_rows(None) == [],
    f"{_plausible_forecast_rows('x')!r} {_plausible_forecast_rows(None)!r}",
)

# The wiring, through the real fetch: one poisoned field, one non-dict row
# and one healthy row on the wire; what the coordinator STORES is validated.
# A pin on the helper alone would stay green if the storage call came off.
_np_wire = Coord(
    FakeHass(), _np_entry(data={"tibber_token": "x", "weather_entity": "weather.home"})
)

async def _np_forecast_payload(call):
    return {"weather.home": {"forecast": [
        {"datetime": "2026-01-15T12:00:00+01:00", "temperature": 1e308,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0},
        "x",
        {"datetime": "2026-01-15T13:00:00+01:00", "temperature": -5.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0},
    ]}}

_np_wire.hass.services.async_register(
    "weather", "get_forecasts", _np_forecast_payload
)
_np_aio.run(_np_wire._fetch_weather_forecast())
R.check(
    "the stored forecast is the validated one: an out-of-window field is "
    "None and a non-dict row never reaches storage (D1-s2-02)",
    len(_np_wire._weather_forecast) == 2
    and _np_wire._weather_forecast[0]["temperature"] is None
    and _np_wire._weather_forecast[1]["temperature"] == -5.0,
    f"{_np_wire._weather_forecast!r}",
)

# The sibling seam the fetch pin cannot reach (fix review, round 1): a failed
# FIRST fetch plans on rows fabricated from the weather entity's CURRENT
# attributes, which is the same class of live input and was not windowed.
# Driven on the production symbol; the metric is what the rows hand
# _forecast_arrays, i.e. the series the solve receives (D1-s2-02's count key).
from heatpump_optimizer.coordinator import _fabricated_forecast  # noqa: E402

def _np_fab(**attrs):
    return _fabricated_forecast(
        FakeState("sunny", attributes=dict({"temperature_unit": "°C"}, **attrs))
    )

_np_fab_t = _np_fab(temperature=1e308, wind_speed=3.0)
_np_fab_w = _np_fab(temperature=-5.0, wind_speed=1e6)
_np_fab_ok = _np_fab(temperature=-5.0, wind_speed=3.0)
R.check(
    "a fabricated forecast windows its source attributes too: an absurd "
    "temperature falls to the 5.0 C fallback and an absurd wind to the "
    "consumers' 0.0, while a healthy entity fabricates unchanged (D1-s2-02)",
    len(_np_fab_t) == len(_np_fab_w) == len(_np_fab_ok) == 48
    and {r["temperature"] for r in _np_fab_t} == {5.0}
    and {r["wind_speed"] for r in _np_fab_w} == {None}
    and {r["temperature"] for r in _np_fab_ok} == {-5.0}
    and {r["wind_speed"] for r in _np_fab_ok} == {3.0},
    f"absurd T {_np_fab_t[0]!r}; absurd wind {_np_fab_w[0]!r}; "
    f"healthy {_np_fab_ok[0]!r}",
)

# D1-s2-02, the ECL110 family: a state displace outside the window the
# integration itself commands is not a measurement, and never lands.
_np_ecl = Coord(FakeHass(), _np_entry(data={"tibber_token": "x"}))
_np_ecl._async_handle_ecl110_state_message(_np_ns(payload=b'{"displace": 1e308}'))
_np_refused = (
    _np_ecl._ecl110_current_displace,
    _np_ecl._current_state.ecl110_displace_command,
    _np_ecl._current_state.ecl110_effective_displace,
)
_np_ecl._async_handle_ecl110_state_message(_np_ns(payload=b'{"displace": -2.5}'))
R.check(
    "an ECL110 displace outside the commanded window never lands; an "
    "in-window one still does (D1-s2-02)",
    _np_refused == (0.0, 0.0, 0.0)
    and _np_ecl._ecl110_current_displace == -2.5
    and _np_ecl._current_state.ecl110_displace_command == -2.5,
    f"refused={_np_refused!r} accepted={_np_ecl._ecl110_current_displace!r}",
)

# D1-s1-03: the DHW learner refuses a tank sample outside the DHW window
# before any state it owns moves -- the sample is not booked as a draw and
# does not become the next interval's baseline. The in-window sample beside
# it is the null control: learning proceeds exactly as before.
_np_dhw = DhwProfileLearner(
    FakeHass(), "np", **_owned_params(ThermalParameters()),
    frozen=lambda *a: None, heating_active=lambda: False,
    external_heat_active=lambda: False,
)
_np_refusal = _np_aio.run(_np_dhw.async_learn_dynamics(-127.0))
_np_accepted = _np_aio.run(_np_dhw.async_learn_dynamics(55.0))
R.check(
    "an out-of-window DHW sample is refused before any learner state moves, "
    "and an in-window one is learned as before (D1-s1-03)",
    _np_refusal == "dhw_sample_implausible"
    and _np_accepted is None
    and _np_dhw.last_temp_sample == 55.0
    and not any(_np_dhw.draw_stats.reservoirs.values()),
    f"refusal={_np_refusal!r} accepted={_np_accepted!r} "
    f"last={_np_dhw.last_temp_sample!r} "
    f"reservoirs={_np_dhw.draw_stats.reservoirs!r}",
)

# --- R9 N-staleness (#1684): a quiet store is not a dead probe ---------------
R.section("R9 N-staleness: a report-on-change probe on a still store (D1-s5-51)")

# The slow stores, each read through the one limit. A report-on-change probe
# in a calm room sent nothing for 4 h 15 min in the field (the finding's own
# evidence); the watchdog must still trip once the limit passes.
_r9f41_quiet = (
    "indoor_temp_entity",
    "lower_floor_temp_entity",
    "floor_return_temp_entity",
    "buffer_tank_temp_entity",
    "dhw_temp_entity",
)
for _r9f41_key in _r9f41_quiet:
    _r9f41_limit = inputs_mod.max_age_for(_r9f41_key)
    _r9f41_calm = InputReader(
        FakeHass({"sensor.x": FakeState("21.3", last_updated=minutes_ago(255, NOW))}),
        {_r9f41_key: "sensor.x"},
        now=lambda: NOW,
    ).read(_r9f41_key)
    _r9f41_dead = InputReader(
        FakeHass(
            {
                "sensor.x": FakeState(
                    "21.3",
                    last_updated=minutes_ago(
                        _r9f41_const.QUIET_STORE_MAX_AGE_MINUTES + 1, NOW
                    ),
                )
            }
        ),
        {_r9f41_key: "sensor.x"},
        now=lambda: NOW,
    ).read(_r9f41_key)
    R.check(
        f"D1-s5-51: {_r9f41_key} silent 255 min reads ok; past the quiet-store "
        "limit it is stale",
        _r9f41_limit == _r9f41_const.QUIET_STORE_MAX_AGE_MINUTES
        and _r9f41_calm.ok
        and _r9f41_dead.stale,
        f"limit {_r9f41_limit}, calm {_r9f41_calm.problem}, "
        f"dead {_r9f41_dead.problem}",
    )


# --- R9 P2 (#1644): the cycle's own outcome ----------------------------------
R.section(
    "R9 P2: the cycle's own outcome -- covering quarter, fenced steps, "
    "failed solves, an honest press "
    "(D2-s3-01, D1-s2-51, D1-s2-91, D1-s4-02, D10-s1-02)"
)

# One fact, one owner (the P2 shape) applied to the cycle itself: the
# covering quarter is read the way the plan's own step grid reads it, each
# best-effort step owns its own failure, a solve whose status says "failed"
# is a failed solve, and the optimize-now press answers with the same
# refusal the run_optimization action raises instead of reporting success.
import asyncio as _r9f13_aio  # noqa: E402
from unittest import mock as _r9f13_mock  # noqa: E402

from harness import FakeEntry as _r9f13_entry  # noqa: E402
from homeassistant.exceptions import HomeAssistantError as _r9f13_err  # noqa: E402
from homeassistant.util import dt as _r9f13_dt  # noqa: E402
from heatpump_optimizer import button as _r9f13_button  # noqa: E402
from heatpump_optimizer import const as _r9f13_const  # noqa: E402
from heatpump_optimizer import coordinator as _r9f13_cmod  # noqa: E402
from heatpump_optimizer import optimizer as _r9f13_omod  # noqa: E402
from heatpump_optimizer import pump_arbiter as _r9f13_arb  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process as _r9f13_solve  # noqa: E402

_R9F13_NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
_R9F13_GUARDED = (
    "_command_frequency",
    "_async_drive_pumps",
    "_async_save_accuracy",
    "_async_save_energy_totals",
    "_async_watch_learning_drift",
)


def _r9f13_make(entry_id: str, extra: dict | None = None):
    """One coordinator on injected series, its three fetches no-ops.

    The same rig the round-9 leads harness built: deterministic hourly
    prices and flat weather, so a cycle runs a real solve without the
    network. The caller freezes the clock.
    """
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = _r9f13_entry(
        data={
            _r9f13_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
            _r9f13_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
            **(extra or {}),
        },
        entry_id=entry_id,
    )
    coord = Coord(hass, entry)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (_R9F13_NOW + timedelta(hours=h - 2)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(50)
    ]
    coord._weather_forecast = [
        {
            "datetime": (_R9F13_NOW + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]

    async def _r9f13_noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = _r9f13_noop
    coord._fetch_weather_forecast = _r9f13_noop
    coord._fetch_solar_forecast = _r9f13_noop
    return hass, entry, coord


async def _r9f13_inline(hass, optimizer, inputs):
    """The #511 in-process fallback, forced: a patched optimizer must be
    the one that solves, which the worker process would re-import."""
    return _r9f13_solve(optimizer, inputs)


# D2-s3-01: an entry covers [start, next start) on the step grid already;
# the "current" reader must answer the same entry the plan's own step 0
# reads, not the first entry that started within the last hour.
_r9f13_dt.freeze(_R9F13_NOW)
_, _, _r9f13_quarters = _r9f13_make("f13_quarters")
_r9f13_quarters._prices = [
    {
        "total": 0.1 + 0.01 * i,
        "starts_at": (_R9F13_NOW + timedelta(minutes=15 * i)).isoformat(),
        "level": "NORMAL",
    }
    for i in range(96)
]
_r9f13_wrong = []
for _r9f13_i in range(96):
    _r9f13_start = _R9F13_NOW + timedelta(minutes=15 * _r9f13_i)
    _r9f13_dt.freeze(_r9f13_start + timedelta(minutes=7))
    _r9f13_got = _r9f13_quarters._current_spot_price()
    if (
        _r9f13_got != 0.1 + 0.01 * _r9f13_i
        or _r9f13_got != _r9f13_quarters._known_prices_for([_r9f13_start])[0]
    ):
        _r9f13_wrong.append((_r9f13_i, round(_r9f13_got, 3)))
R.check(
    "D2-s3-01: under quarter-hour entries the current price is the covering "
    "quarter's, agreeing with the plan's own step-0 reader on every quarter",
    not _r9f13_wrong,
    f"{len(_r9f13_wrong)} of 96 quarters disagree, first {_r9f13_wrong[:3]}",
)
_r9f13_quarters._prices = [
    {
        "total": 0.2 + 0.1 * h,
        "starts_at": (_R9F13_NOW + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(24)
]
_r9f13_hourly_wrong = []
for h in range(24):
    _r9f13_dt.freeze(_R9F13_NOW + timedelta(hours=h, minutes=13))
    if _r9f13_quarters._current_spot_price() != 0.2 + 0.1 * h:
        _r9f13_hourly_wrong.append(h)
R.check(
    "D2-s3-01: hourly entries (the null control) still read their own hour",
    not _r9f13_hourly_wrong,
    f"hours wrong: {_r9f13_hourly_wrong}",
)
_r9f13_dt.freeze(_R9F13_NOW)


# D1-s2-51 (the arbiter half) and D1-s2-91: every best-effort step on the
# cycle path owns its own failure. A raise inside any of them used to fail
# the whole update and skip every step after it.
async def _r9f13_fenced_cycle(entry_id, fault):
    """Run one full cycle with ``fault`` patched in; report what ran."""
    hass, entry, coord = _r9f13_make(entry_id)
    ran = []
    for name in _R9F13_GUARDED:
        real = getattr(coord, name)

        async def _spy(*_a, _n=name, _r=real, **_k):
            ran.append(_n)
            return await _r(*_a, **_k)

        setattr(coord, name, _spy)

    async def _boom(*_a, **_k):
        raise RuntimeError("injected best-effort fault")

    def _boom_sync(*_a, **_k):
        raise RuntimeError("injected best-effort fault")

    patches = []
    if fault == "arbiter":
        patches.append(_r9f13_mock.patch.object(_r9f13_arb, "apply", _boom))
    else:
        coord._record_accuracy = _boom_sync
        coord._track_realised_peak = _boom_sync
    out = {}
    try:
        for p in patches:
            p.start()
        try:
            out["data"] = await coord._async_update_data()
            out["ok"] = True
        except Exception:  # noqa: BLE001 - the defect is the raise itself
            out["ok"] = False
    finally:
        for p in patches:
            p.stop()
    out["ran"] = sorted(set(ran))
    return out


_r9f13_arb_out = _r9f13_aio.run(_r9f13_fenced_cycle("f13_arbiter", "arbiter"))
R.check(
    "D1-s2-51: an arbiter raise fails neither the cycle nor the steps after it",
    _r9f13_arb_out["ok"]
    and isinstance(_r9f13_arb_out["data"], dict)
    and _r9f13_arb_out["ran"] == sorted(_R9F13_GUARDED),
    f"ok={_r9f13_arb_out['ok']} ran={_r9f13_arb_out['ran']} "
    f"(want all of {sorted(_R9F13_GUARDED)})",
)
_r9f13_acc_out = _r9f13_aio.run(_r9f13_fenced_cycle("f13_accuracy", "accuracy"))
R.check(
    "D1-s2-91: a raise in the accuracy pipeline fails neither the cycle nor "
    "the saves after it",
    _r9f13_acc_out["ok"]
    and isinstance(_r9f13_acc_out["data"], dict)
    and _r9f13_acc_out["ran"] == sorted(_R9F13_GUARDED),
    f"ok={_r9f13_acc_out['ok']} ran={_r9f13_acc_out['ran']}",
)


# D1-s2-51 (the learner half, via the production learner the harness used):
# a comfort-learner raise inside the solve is the solve's best-effort tail,
# not a failed solve.
def _r9f13_quiet_learner():
    _, _, coord = _r9f13_make(
        "f13_quiet", {_r9f13_const.CONF_COMFORT_LEARNING_ENABLED: True}
    )
    orig = ComfortLearner.record_quiet_period

    def _boom(self, *_a, **_k):
        raise RuntimeError("injected learner fault")

    ComfortLearner.record_quiet_period = _boom
    try:
        reason = _r9f13_aio.run(coord.async_run_optimization())
    finally:
        ComfortLearner.record_quiet_period = orig
    return reason, coord._optimization_result is not None, coord._solve_failures


_r9f13_reason, _r9f13_published, _r9f13_failures = _r9f13_quiet_learner()
R.check(
    "D1-s2-51: a quiet-period learner raise is not a failed solve -- the "
    "plan stays published and the failure counter untouched",
    _r9f13_reason is None and _r9f13_published and _r9f13_failures == 0,
    f"reason={_r9f13_reason!r} published={_r9f13_published} "
    f"failures={_r9f13_failures}",
)


# D1-s4-02: the optimizer's own guard turns a solver blow-up into a plan
# whose status says "failed (...)". Publishing it counted the cycle a
# success and zeroed the failure counter; the coordinator's failure branch
# must treat that status as the failure it reports.
def _r9f13_solve_status(faulted):
    _, _, coord = _r9f13_make(f"f13_status_{int(faulted)}")

    def _boom(*_a, **_k):
        raise RuntimeError("injected L-BFGS-B blow-up")

    with _r9f13_mock.patch.object(_r9f13_cmod, "_await_optimize", _r9f13_inline):
        if faulted:
            with _r9f13_mock.patch.object(_r9f13_omod, "_scoped_minimize", _boom):
                reason = _r9f13_aio.run(coord.async_run_optimization())
        else:
            reason = _r9f13_aio.run(coord.async_run_optimization())
    return reason, coord._optimization_result, coord._solve_failures


_r9f13_ctrl = _r9f13_solve_status(False)
_r9f13_bad = _r9f13_solve_status(True)
R.check(
    "D1-s4-02 (control): the inline transport solves and publishes",
    _r9f13_ctrl[0] is None and _r9f13_ctrl[1] is not None,
    f"reason={_r9f13_ctrl[0]!r} result={_r9f13_ctrl[1]!r}",
)
R.check(
    "D1-s4-02: a returned plan whose status starts 'failed' is a failed "
    "solve -- refused, counted, and never published",
    _r9f13_bad[0] == "solve_failed"
    and _r9f13_bad[1] is None
    and _r9f13_bad[2] == 1,
    f"reason={_r9f13_bad[0]!r} "
    f"status={getattr(_r9f13_bad[1], 'status', None)!r} "
    f"failures={_r9f13_bad[2]}",
)


# D10-s1-02: the press owes the caller the same refusal the action raises.
class _R9F13Hass(FakeHass):
    """Upstream's background task: a real task, left pending for the caller."""

    def async_create_task(self, coro):
        return _r9f13_aio.get_running_loop().create_task(coro)


def _r9f13_press(reason):
    """Press the button with the coordinator refusing `reason`; `None` runs."""
    hass, entry, coord = _r9f13_make(f"f13_press_{reason}")
    requested = []

    async def _solve():
        return reason

    async def _refresh():
        requested.append(True)
        await _r9f13_aio.Event().wait()

    coord.async_run_optimization = _solve
    coord.async_request_refresh = _refresh
    ent = _r9f13_button.ForceOptimizationButton(coord, entry)
    ent.hass = _R9F13Hass()

    async def _scenario():
        try:
            await _r9f13_aio.wait_for(ent.async_press(), timeout=5.0)
            out = "returned"
        except _r9f13_err as err:
            out = getattr(err, "translation_key", None) or "raised:plain"
        except TimeoutError:
            out = "hung"
        # One yield: 3.12's wait_for awaits the inner coroutine inline, so
        # the refresh task the press scheduled has not started yet here;
        # without this the `requested` read races the interpreter version.
        await _r9f13_aio.sleep(0)
        for task in _r9f13_aio.all_tasks() - {_r9f13_aio.current_task()}:
            task.cancel()
        return out, bool(requested)

    return _r9f13_aio.run(_scenario())


_r9f13_press_refused = _r9f13_press("no_prices")
_r9f13_press_ran = _r9f13_press(None)
R.check(
    "D10-s1-02: the press raises the action's own no-prices refusal when the "
    "solve did not run",
    _r9f13_press_refused == ("run_optimization_no_prices", True),
    f"got {_r9f13_press_refused} (want ('run_optimization_no_prices', True))",
)
R.check(
    "D10-s1-02: the press returns normally when the solve ran, still off "
    "the refresh it asked for",
    _r9f13_press_ran == ("returned", True),
    f"got {_r9f13_press_ran} (want ('returned', True))",
)
_r9f13_press_solve_failed = _r9f13_press("solve_failed")
R.check(
    "D10-s1-02: the press raises the action's solve-failed refusal when the "
    "solve died (the reason-is-not-None arm of the same refusal -- the "
    "mutation survivor at button.py's second guard)",
    _r9f13_press_solve_failed == ("run_optimization_solve_failed", True),
    f"got {_r9f13_press_solve_failed} (want ('run_optimization_solve_failed', True))",
)
R.check(
    "D10-s1-02: no button press queues behind another (PARALLEL_UPDATES 0, "
    "the v6.6.12 bug 5 mechanism)",
    _r9f13_button.PARALLEL_UPDATES == 0,
    f"PARALLEL_UPDATES is {_r9f13_button.PARALLEL_UPDATES!r}",
)
_r9f13_dt.freeze(None)


# --- R9 F1.5 (D1-s2-04): a persistent fenced failure surfaces once ---------
# The N-debug-swallow sweep named five cycle-path fences that swallowed a
# persistent failure at DEBUG forever: a frequency command or a pump
# schedule raising every cycle never reached the log at its default level,
# so actuation could be dead for a season with nothing visible. One fence
# mechanism owns them all now, and it logs the FIRST occurrence of each
# (step, cause) at WARNING -- keyed per distinct cause, exactly as the
# worker-fallback note keys its repair notice -- with repeats staying at
# DEBUG, where their volume belongs. Two cycles per site: one WARNING, one
# DEBUG, and the cycle never fails.
import logging as _f15_logging

_F15_FENCES = (
    ("_command_frequency", "Frequency command skipped"),
    ("_async_drive_pumps", "Pump scheduling skipped"),
    ("_maybe_run_fuse_advisor", "Fuse advisor skipped"),
    ("_maybe_refresh_price_tile", "Price tile skipped"),
    ("_async_watch_learning_drift", "Snapshot heartbeat skipped"),
)


class _F15Sink(_f15_logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=_f15_logging.DEBUG)
        self.rows = []

    def emit(self, record):
        self.rows.append((record.levelno, record.getMessage()))


def _f15_fence_site(name):
    """Two refresh cycles with ``name`` raising every time, plus the
    marker-named log rows and whether both cycles completed. The clock is
    frozen on the rig's own NOW: unfrozen, its price rows are months stale
    and the solve-side sites never run."""
    _, _, coord = _r9f13_make(f"f15_fence_{name}")

    async def _boom(*_a, **_k):
        raise TypeError(f"F1.5 fence fault {name}")

    sink = _F15Sink()
    logger = _f15_logging.getLogger("heatpump_optimizer")
    logger.setLevel(_f15_logging.DEBUG)
    logger.addHandler(sink)
    completed = 0
    _r9f13_dt.freeze(_R9F13_NOW)
    try:
        with _r9f13_mock.patch.object(type(coord), name, _boom), \
                _r9f13_mock.patch.object(
                    _r9f13_cmod, "_await_optimize", _r9f13_inline):
            for _ in range(2):
                _r9f13_aio.run(coord.async_refresh())
                completed += int(coord.last_update_success)
    finally:
        _r9f13_dt.freeze(None)
        logger.removeHandler(sink)
    marker = f"F1.5 fence fault {name}"
    return (
        [row for row in sink.rows if marker in row[1]],
        completed,
    )


_f15_fence_rows, _f15_fence_ok = {}, {}
for _f15_name, _f15_msg in _F15_FENCES:
    _f15_fence_rows[_f15_name], _f15_fence_ok[_f15_name] = _f15_fence_site(
        _f15_name
    )
R.check(
    "D1-s2-04: every cycle-path fence surfaces its persistent failure at "
    "WARNING exactly once, repeats at DEBUG, and the cycle survives",
    all(
        len([lv for lv, _ in rows if lv >= _f15_logging.WARNING]) == 1
        and len(rows) == 2
        and _f15_msg in rows[0][1]
        and _f15_fence_ok[name] == 2
        for name, rows, _f15_msg in (
            (n, r, m) for n, m in _F15_FENCES for r in (_f15_fence_rows[n],)
        )
    ),
    f"{[(n, [(lv, msg[:40]) for lv, msg in rows]) for n, rows in _f15_fence_rows.items()]} "
    f"completed={_f15_fence_ok} -- the sweep measured 5 of 5 sites silent "
    "at the merge base (dev/audit/rounds/round9/D1/s2/guards.py)",
)


# --- R9 P2 (#1644): presence answers, not key presence ----------------------
R.section("R9 P2: presence answers, not key presence (D12-s3-01, D14-s2-01)")

# D14-s2-01: three seams beside their canonical predicate decided the
# two-zone and wood-furnace facts from a proxy key. Each check below pins the
# canonical predicate's verdict at a boundary cell the proxy got wrong
# (mode ignored, one key of four watched, a present-but-0.0 value dropped, a
# different inferred-key set) against the cell where proxy and predicate
# agree -- the null controls.
import asyncio as _r9f12_aio  # noqa: E402
from harness import FakeEntry as _r9f12_entry  # noqa: E402
from homeassistant.util import dt as _r9f12_dt  # noqa: E402
import heatpump_optimizer as _r9f12_integ  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    config_flow as _r9f12_flow,
    const as _r9f12_const,
    modbus_prefill as _r9f12_prefill,
    quick_setup as _r9f12_quick,
    topology as _r9f12_topo,
    wood_fuel as _r9f12_wood,
)
from heatpump_optimizer.thermal_model import ThermalParameters as _r9f12_tp  # noqa: E402

_r9f12_zone_keys = {
    _r9f12_const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
    _r9f12_const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0,
    _r9f12_const.CONF_INTER_ZONE_TRANSFER: 0.1,
    _r9f12_const.CONF_RADIATOR_POWER_FRACTION: 0.5,
}
R.check(
    "D14-s2-01: the questionnaire derives single-zone physics for "
    "two_zone_mode=off however many zone keys survive",
    _r9f12_flow._derive_preset({}, {
        **_r9f12_zone_keys,
        _r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_OFF,
    }) == _r9f12_flow._derive_preset({}, {
        _r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_OFF,
    }),
    "the preset re-derives two-zone from upper-floor mass beside the "
    "canonical rule",
)
R.check(
    "D14-s2-01: two_zone_mode=on derives two-zone physics with no zone key stored",
    _r9f12_flow._derive_preset({}, {
        _r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_ON,
        _r9f12_const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
    }) == _r9f12_flow._derive_preset({}, {
        _r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_ON,
    }),
    "an explicit on with no keys fell back to the mass-presence proxy",
)
R.check(
    "D14-s2-01: an upper mass of 0.0 is presence, like any value (auto mode)",
    _r9f12_flow._derive_preset({}, {
        _r9f12_const.CONF_UPPER_FLOOR_THERMAL_MASS: 0.0,
    }) == _r9f12_flow._derive_preset({}, {
        _r9f12_const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
    }),
    "bool(0.0) dropped a key the canonical rule counts as present",
)

# The pre-fill seam: CONF_MIXING_VALVE_WRITE_TARGET_KIND was offered iff
# bool(upper_floor_thermal_mass), so a flow write target the building page's
# own save refuses was suggested (or a legitimate one missed).
_r9f12_snap = {
    "r4109": ("sensor.p_gchv_r4109", "0", 1.0),  # water temperature control
    "unit_capacity": ("sensor.p_unit_capacity", "8.0", 1.0),
}
for _r9f12_label, _r9f12_cell in (
    (
        "mode off with zone keys",
        {**_r9f12_zone_keys,
         _r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_OFF},
    ),
    (
        "mode on, no keys",
        {_r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_ON},
    ),
    ("auto, upper mass 0.0", {_r9f12_const.CONF_UPPER_FLOOR_THERMAL_MASS: 0.0}),
    ("auto, nothing (null control)", {}),
):
    _r9f12_suggested = (
        _r9f12_const.CONF_MIXING_VALVE_WRITE_TARGET_KIND
        in _r9f12_prefill.infer(_r9f12_snap, _r9f12_cell)
    )
    _r9f12_canonical = _r9f12_tp.from_config(dict(_r9f12_cell)).two_zone_enabled
    R.check(
        f"D14-s2-01: the pre-fill offers a flow write target exactly when the "
        f"canonical rule says two-zone ({_r9f12_label})",
        _r9f12_suggested == _r9f12_canonical,
        f"suggested={_r9f12_suggested} canonical={_r9f12_canonical}",
    )

# The picture seam: describe_setup's wood tank came from a different
# inferred-key set than wood_furnace_on (valve outlet added, the wood coil
# dropped), so the diagram drew a tank the model does not run and hid one it
# does.
for _r9f12_label, _r9f12_cell in (
    ("flag on", {_r9f12_const.CONF_WOOD_FURNACE_ENABLED: True}),
    (
        "flag off, probes stored",
        {
            _r9f12_const.CONF_WOOD_FURNACE_ENABLED: False,
            _r9f12_const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.t",
            _r9f12_const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.b",
        },
    ),
    (
        "no flag, valve outlet alone",
        {_r9f12_const.CONF_VALVE_OUTLET_TEMP_ENTITY: "sensor.v"},
    ),
    (
        "no flag, wood coil alone",
        {_r9f12_const.CONF_DHW_WOOD_COIL_ENABLED: True},
    ),
    (
        "no flag, top probe alone",
        {_r9f12_const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.t"},
    ),
    ("no flag, nothing (null control)", {}),
):
    R.check(
        f"D14-s2-01: the setup picture's wood tank is the canonical "
        f"predicate's ({_r9f12_label})",
        _r9f12_topo.describe_setup(dict(_r9f12_cell))["wood"]["present"]
        == _r9f12_wood.wood_furnace_on(_r9f12_cell),
        "picture=%r canonical=%r" % (
            _r9f12_topo.describe_setup(dict(_r9f12_cell))["wood"]["present"],
            _r9f12_wood.wood_furnace_on(_r9f12_cell),
        ),
    )

# D12-s3-01: the full wizard's dhw and zones pages offered only defaulted
# optional fields, so an untouched submit stored tank volume and zone keys,
# and the presence rules read them as "configured". The fix writes the
# explicit flags from a question on the page, the way quick_setup derives
# them; an untouched page now answers "no".
class _r9f12_OK:
    """The Tibber verify call, answered offline."""

    class _Resp:
        status = 200

        async def json(self):
            return {"data": {"viewer": {"name": "Home"}}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    def post(self, *a, **k):
        return self._Resp()


_r9f12_required = {
    "name": "Heat Pump Optimizer",
    _r9f12_const.CONF_TIBBER_TOKEN: "tok",
    _r9f12_const.CONF_WEATHER_ENTITY: "weather.home",
}


def _r9f12_untouched(schema):
    """What an untouched browser posts: the suggested value, else the default."""
    answers = {}
    for key in schema.schema if schema else ():
        name = str(key)
        desc = getattr(key, "description", None) or {}
        if isinstance(desc, dict) and "suggested_value" in desc:
            answers[name] = desc["suggested_value"]
            continue
        try:
            default = key.default()
        except Exception:  # noqa: BLE001
            default = None
        if default is not None and type(default).__name__ != "Undefined":
            answers[name] = default
    return answers


async def _r9f12_walk(choices, form_overrides):
    """Drive the initial flow to create_entry, menus by ``choices`` then the
    first option; every form is submitted untouched, bar ``form_overrides``."""
    flow = _r9f12_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    result = await flow.async_step_user(None)
    mi = 0
    trail = []
    for _ in range(40):
        if result.get("type") == "create_entry":
            return dict(result["data"]), trail
        if result.get("type") == "menu":
            options = list(result["menu_options"])
            step = choices[mi] if mi < len(choices) else options[0]
            if (
                result["step_id"] == "finish_setup"
                and "quick_setup" in trail
                and step == "quick_setup"
            ):
                # quick_setup declines the pre-fill back to finish_setup; a
                # second visit to that menu finishes.
                step = "finish_now"
            mi += 1
            trail.append(step)
            result = await getattr(flow, f"async_step_{step}")(None)
            continue
        step = result["step_id"]
        trail.append(step)
        if step == "user":
            answers = dict(_r9f12_required)
        else:
            answers = _r9f12_untouched(result.get("data_schema"))
        answers.update(form_overrides.get(step) or {})
        result = await getattr(flow, f"async_step_{step}")(answers)
    raise RuntimeError(f"flow did not finish: {trail}")


_r9f12_session = _r9f12_flow.async_get_clientsession
_r9f12_flow.async_get_clientsession = lambda hass, verify_ssl=True: _r9f12_OK()
try:
    _r9f12_expert, _r9f12_trail = _r9f12_aio.run(
        _r9f12_walk(["temperature", "thermal"], {})
    )
    _r9f12_expert_tp = _r9f12_tp.from_config(_r9f12_expert)
    R.check(
        "D12-s3-01: an untouched expert wizard creates a single-zone, "
        "no-hot-water plant",
        _r9f12_expert_tp.two_zone_enabled is False
        and _r9f12_expert_tp.dhw_enabled is False,
        f"two_zone={_r9f12_expert_tp.two_zone_enabled} "
        f"dhw={_r9f12_expert_tp.dhw_enabled} on {' > '.join(_r9f12_trail)}",
    )
    R.check(
        "D12-s3-01: the wizard writes the explicit presence flags "
        "(two_zone_mode off, dhw_enabled off)",
        _r9f12_expert.get(_r9f12_const.CONF_TWO_ZONE_MODE)
        == _r9f12_const.TWO_ZONE_MODE_OFF
        and _r9f12_expert.get(_r9f12_const.CONF_DHW_ENABLED) is False,
        "two_zone_mode=%r dhw_enabled=%r" % (
            _r9f12_expert.get(_r9f12_const.CONF_TWO_ZONE_MODE),
            _r9f12_expert.get(_r9f12_const.CONF_DHW_ENABLED),
        ),
    )
    _r9f12_quick_data, _ = _r9f12_aio.run(
        _r9f12_walk(
            ["quick_setup"],
            {
                "quick_setup": {
                    _r9f12_quick.FIELD_DHW_TANK: True,
                    _r9f12_quick.FIELD_TWO_ZONE: False,
                }
            },
        )
    )
    R.check(
        "D12-s3-01: a quick-setup 'yes, hot water' still plans hot water "
        "(null control)",
        _r9f12_tp.from_config(_r9f12_quick_data).dhw_enabled is True
        and _r9f12_quick_data.get(_r9f12_const.CONF_DHW_ENABLED) is True,
        "dhw_enabled=%r" % _r9f12_quick_data.get(_r9f12_const.CONF_DHW_ENABLED),
    )
    _r9f12_yes, _ = _r9f12_aio.run(
        _r9f12_walk(
            ["temperature", "thermal"],
            {
                "zones": {_r9f12_quick.FIELD_TWO_ZONE: True},
                "dhw": {_r9f12_const.CONF_DHW_ENABLED: True},
            },
        )
    )
    R.check(
        "D12-s3-01: the wizard's own yes answers turn both plants on",
        _r9f12_tp.from_config(_r9f12_yes).two_zone_enabled is True
        and _r9f12_tp.from_config(_r9f12_yes).dhw_enabled is True,
        "two_zone=%s dhw=%s" % (
            _r9f12_tp.from_config(_r9f12_yes).two_zone_enabled,
            _r9f12_tp.from_config(_r9f12_yes).dhw_enabled,
        ),
    )

    def _r9f12_suggested(step, data):
        flow = _r9f12_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        flow._data = dict(data)
        form = _r9f12_aio.run(getattr(flow, f"async_step_{step}")(None))
        return {
            str(marker): (getattr(marker, "description", None) or {}).get(
                "suggested_value"
            )
            for marker in (form.get("data_schema").schema or {})
        }

    _r9f12_dhw_sugg = _r9f12_suggested(
        "dhw", {_r9f12_const.CONF_DHW_ENABLED: True}
    )
    R.check(
        "D12-s3-01: the hot-water page asks presence and suggests a stored "
        "yes back",
        _r9f12_dhw_sugg.get(_r9f12_const.CONF_DHW_ENABLED) is True,
        "suggested=%r" % _r9f12_dhw_sugg.get(_r9f12_const.CONF_DHW_ENABLED),
    )
    _r9f12_zones_sugg = _r9f12_suggested(
        "zones", {_r9f12_const.CONF_TWO_ZONE_MODE: _r9f12_const.TWO_ZONE_MODE_ON}
    )
    R.check(
        "D12-s3-01: the zones page asks the zone question and suggests a "
        "stored on back",
        _r9f12_zones_sugg.get(_r9f12_quick.FIELD_TWO_ZONE) is True,
        "suggested=%r"
        % _r9f12_zones_sugg.get(_r9f12_quick.FIELD_TWO_ZONE),
    )

    # The merged finding's options half (D12-s1-02): an untouched Hot water
    # or Hot water tank page over an entry with no hot water at all stored
    # the presence-inferred pair and planned a tank the entry never had.
    # The presence question now lives on the wizard; here the pair's own
    # default post is dropped over a no-DHW entry, kept when deliberate.
    _r9f12_phantom = _r9f12_flow._omit_unstored_defaults(
        {
            _r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS,
            _r9f12_const.CONF_DHW_TANK_VOLUME: _r9f12_const.DEFAULT_DHW_TANK_VOLUME,
            _r9f12_const.CONF_DHW_SETPOINT: 52.0,
        },
        {},
    )
    R.check(
        "D12-s3-01: an untouched options page stores no DHW presence over a "
        "no-hot-water entry",
        _r9f12_phantom == {_r9f12_const.CONF_DHW_SETPOINT: 52.0},
        f"stored={sorted(_r9f12_phantom)}",
    )
    R.check(
        "D12-s3-01: an edited windows spec is a deliberate answer and stays "
        "(null control)",
        _r9f12_flow._omit_unstored_defaults(
            {_r9f12_const.CONF_DHW_WINDOWS: "06:00-09:00"}, {}
        )
        == {_r9f12_const.CONF_DHW_WINDOWS: "06:00-09:00"},
        "an edited spec over a no-DHW entry must not be dropped",
    )
    R.check(
        "D12-s3-01: a hot-water entry keeps an untouched pair post, as before "
        "(null control)",
        _r9f12_flow._omit_unstored_defaults(
            {_r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS},
            {_r9f12_const.CONF_DHW_WINDOWS: "07:00-08:00"},
        )
        == {_r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS},
        "a stored key is always kept",
    )
    R.check(
        "D12-s3-01: an entry that affirmed hot water keeps an untouched pair "
        "post without the pair stored (the guard's affirmed arm)",
        _r9f12_flow._omit_unstored_defaults(
            {
                _r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS,
                _r9f12_const.CONF_DHW_TANK_VOLUME: _r9f12_const.DEFAULT_DHW_TANK_VOLUME,
            },
            {_r9f12_const.CONF_DHW_ENABLED: True},
        )
        == {
            _r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS,
            _r9f12_const.CONF_DHW_TANK_VOLUME: _r9f12_const.DEFAULT_DHW_TANK_VOLUME,
        },
        "the explicit flag is the affirmation; its pair is not dropped",
    )
    R.check(
        "D12-s3-01: and so does an entry whose hot water is presence-inferred "
        "(volume stored, windows never)",
        _r9f12_flow._omit_unstored_defaults(
            {_r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS},
            {_r9f12_const.CONF_DHW_TANK_VOLUME: 180.0},
        )
        == {_r9f12_const.CONF_DHW_WINDOWS: _r9f12_const.DEFAULT_DHW_WINDOWS},
        "a hot-water entry by presence keeps an untouched post too",
    )
finally:
    _r9f12_flow.async_get_clientsession = _r9f12_session

# --- R9 P6 (#1651): the unprobed plant state advances from the plan ----------
R.section("R9 P6: the unprobed plant state advances from the plan (D12-s1-01)")

# D12-s1-01: with the tank probe omitted (the default install), every solve
# started from the 55 degC ThermalState default, and the slab from a one-time
# room+1 K seed; neither was ever advanced between cycles. The fix seeds both
# from the previous plan's own trajectory at the elapsed step (hourly cycles,
# 15-minute steps: index 4). The mapped arms are the controls: a probe wins
# over open-loop propagation, at both ends of the fix.
_r9f12_seed_start = datetime(2026, 3, 2, 6, 0, tzinfo=UTC)
_r9f12_seed_cfg = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_daily_consumption": 150.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
}


def _r9f12_seed_prices(hass, now):
    now = now.replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        "sensor.prices",
        FakeState(
            "0.5",
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(0.5 + 0.1 * (h % 4), 3),
                    }
                    for h in range(48)
                ]
            },
        ),
    )


def _r9f12_cycles(mapped):
    """Four hourly closed-loop cycles; returns the solver's seeds and plans."""
    cfg = dict(_r9f12_seed_cfg)
    if mapped:
        cfg["dhw_temp_entity"] = "sensor.tank"
        cfg["floor_return_temp_entity"] = "sensor.floor"
    _r9f12_dt.freeze(_r9f12_seed_start)
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
    hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
    if mapped:
        hass.states.set("sensor.tank", FakeState("48.0", unit="°C"))
        hass.states.set("sensor.floor", FakeState("27.0", unit="°C"))
    _r9f12_seed_prices(hass, _r9f12_seed_start)
    entry = _r9f12_entry(data=cfg, entry_id=f"r9f12_seed_{mapped}")
    _r9f12_aio.run(_r9f12_integ.async_setup_entry(hass, entry))
    coord = entry.runtime_data
    seen = []
    real_snap = coord._solve_record

    def _r9f12_snap(*a, **k):
        record = real_snap(*a, **k)
        state = record.inputs.state
        seen.append((state.dhw_temperature, state.slab_temperature))
        return record

    coord._solve_record = _r9f12_snap
    try:
        plans = []
        for hour in range(4):
            _r9f12_dt.freeze(_r9f12_seed_start + timedelta(hours=hour))
            _r9f12_seed_prices(hass, _r9f12_seed_start + timedelta(hours=hour))
            _r9f12_aio.run(coord.async_refresh())
            plans.append(coord._optimization_result)
    finally:
        coord._solve_record = real_snap
        _r9f12_dt.freeze(None)
    return seen, plans


_r9f12_seen, _r9f12_plans = _r9f12_cycles(False)
R.check(
    "D12-s1-01: with no tank probe the solver's DHW seed follows the previous "
    "plan, not the 55 degC default",
    len(_r9f12_seen) == 4
    and len({round(s[0], 2) for s in _r9f12_seen}) > 1
    and all(
        abs(
            _r9f12_seen[i][0]
            - float(list(_r9f12_plans[i - 1].dhw_temp_trajectory)[4])
        )
        <= 1.0
        for i in range(1, len(_r9f12_seen))
    ),
    "dhw seeds=%r prev-plan+1h=%r"
    % (
        [round(s[0], 2) for s in _r9f12_seen],
        [
            round(float(list(_r9f12_plans[i - 1].dhw_temp_trajectory)[4]), 2)
            for i in range(1, len(_r9f12_seen))
        ],
    ),
)
R.check(
    "D12-s1-01: and the slab seed follows the previous plan, not the one-time "
    "room+1 K seed",
    len(_r9f12_seen) == 4
    and len({round(s[1], 2) for s in _r9f12_seen}) > 1
    and all(
        abs(
            _r9f12_seen[i][1]
            - float(list(_r9f12_plans[i - 1].slab_temp_trajectory)[4])
        )
        <= 1.0
        for i in range(1, len(_r9f12_seen))
    ),
    "slab seeds=%r prev-plan+1h=%r"
    % (
        [round(s[1], 2) for s in _r9f12_seen],
        [
            round(float(list(_r9f12_plans[i - 1].slab_temp_trajectory)[4]), 2)
            for i in range(1, len(_r9f12_seen))
        ],
    ),
)
_r9f12_mseen, _r9f12_mplans = _r9f12_cycles(True)
R.check(
    "D12-s1-01: a mapped tank probe still wins the seed (null control)",
    [round(s[0], 2) for s in _r9f12_mseen] == [48.0] * len(_r9f12_mseen),
    "dhw seeds=%r" % [round(s[0], 2) for s in _r9f12_mseen],
)
R.check(
    "D12-s1-01: a mapped floor-return probe still drives the slab seed "
    "(null control)",
    all(abs(s[1] - 28.0) <= 1.5 for s in _r9f12_mseen),
    "slab seeds=%r" % [round(s[1], 2) for s in _r9f12_mseen],
)

# The seed helper's own early-window tolerance, pinned at both ends (the
# mutation lane's GUARD_OFF site on its ternary): a plan that starts within
# one step of now answers its first step; one that starts further ahead says
# nothing, so the never-advanced default is left alone rather than replaced
# by a plan that has not started.
from types import SimpleNamespace as _r9f12_ns  # noqa: E402
from heatpump_optimizer import coordinator as _r9f12_coord  # noqa: E402

def _r9f12_plan_result(first, values):
    return _r9f12_ns(
        dhw_temp_trajectory=list(values),
        timestamps=[
            first + timedelta(minutes=15 * i) for i in range(len(values))
        ],
    )

R.check(
    "D12-s1-01: a plan starting within one step of now seeds its first step",
    _r9f12_coord._open_loop_plan_value(
        _r9f12_plan_result(NOW + timedelta(seconds=600), [41.0, 42.0, 43.0]),
        "dhw_temp_trajectory",
        NOW,
    )
    == 41.0,
)
R.check(
    "D12-s1-01: a plan starting more than a step after now seeds nothing",
    _r9f12_coord._open_loop_plan_value(
        _r9f12_plan_result(NOW + timedelta(minutes=30), [41.0, 42.0]),
        "dhw_temp_trajectory",
        NOW,
    )
    is None,
    "the 55 degC default must not be replaced by a plan that has not started",
)

# --- R10-DEMAND-OVERBOOK (#2499): the slab advances by the heat delivered ----
R.section("R10-DEMAND-OVERBOOK: the unsensed slab advances by metered heat (#2499)")

# The plan's trajectory advances the slab by the heat COMMANDED. A pump
# drawing less leaves the difference in the slab estimate, the house learner
# replays the next interval from it, finds the room colder than predicted and
# books the gap as fabric loss: the learned scale climbs, and the plan books
# more heat each day. With a power meter the slab advances by the metered
# draw instead. The previous plan says 25 degC after 30 min of 4 kW; the
# prior slab is 23 degC.
from heatpump_optimizer import draw_range as _r10do_draw  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState as _r10do_state  # noqa: E402

_r10do_t0 = datetime(2026, 10, 5, 3, 0, tzinfo=UTC)


def _r10do_slab(meter, drawn_kw, sampled=True, gap_h=0.5, *, mode=None, immersion=False):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "optimization_interval": 30.0,
    }
    if meter:
        cfg["heat_pump_power_entity"] = "sensor.hp_power"
    if mode is not None:
        cfg["heat_pump_mode_entity"] = "select.pump_mode"
    coord = Coord(FakeHass(), _r9f12_entry(data=cfg))
    coord._snapshots_loaded = True
    ctx = getattr(coord, "_ctx", coord)
    ctx._thermal_params.dhw_enabled = False
    ctx.publish(coord, _r10do_state(
        room_temperature=21.0, outdoor_temperature=5.0, slab_temperature=23.0))
    now = _r10do_t0 + timedelta(minutes=30)
    coord._last_house_sample_time = now - timedelta(hours=gap_h) if sampled else None
    # The immersion latch, held from earlier cycles: one clear sample keeps it.
    coord._immersion_active = immersion
    coord._optimization_result = _r9f12_ns(
        slab_temp_trajectory=[25.0, 25.5, 26.0],
        timestamps=[now + timedelta(minutes=30 * i) for i in range(3)],
    )
    coord._current_action = {"power": 4.0, "mode": "auto", "heat_pump_on": True}
    _r9f12_dt.freeze(now)
    try:
        for entity, value in (
            ("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0"),
            ("sensor.hp_power", f"{drawn_kw}"),
        ):
            unit = "kW" if entity == "sensor.hp_power" else "°C"
            coord.hass.states.set(entity, FakeState(value, last_updated=now, unit=unit))
        if mode is not None:
            coord.hass.states.set("select.pump_mode", FakeState(
                mode, last_updated=now, attributes={"options": [mode]}))
        _r9f12_aio.run(coord._update_current_state())
    finally:
        _r9f12_dt.freeze(None)
    return getattr(coord, "_ctx", coord)._current_state.slab_temperature


_r10do_off, _r10do_standby = _r10do_slab(True, 0.0), _r10do_slab(True, 0.2)
_r10do_low, _r10do_full = _r10do_slab(True, 1.0), _r10do_slab(True, 4.0)
R.check(
    "#2499: a metered pump that drew nothing leaves the slab cooling, not at "
    "the plan's commanded 25 degC",
    _r10do_off < 23.0,
    "slab=%.3f" % _r10do_off,
)
R.check(
    "#2499: the slab rises with the metered draw, below the commanded "
    "trajectory while the pump draws less than 4 kW",
    _r10do_off < _r10do_low < _r10do_full < 25.0,
    "slab off/1kW/4kW=%.3f/%.3f/%.3f" % (_r10do_off, _r10do_low, _r10do_full),
)
R.check(
    "#2499: a standby draw under the running floor heats nothing",
    _r10do_standby == _r10do_off,
    "slab standby=%.3f off=%.3f" % (_r10do_standby, _r10do_off),
)
R.check(
    "#2499: without a power meter the slab follows the plan (null control)",
    _r10do_slab(False, 0.0) == 25.0,
)
R.check(
    "#2499: with no previous sample time the slab follows the plan",
    _r10do_slab(True, 0.0, sampled=False) == 25.0,
)
# Through the coordinator's own wiring, not ``space_draw_kw`` alone: the
# immersion latch and the observed mode are what set ``shared`` and
# ``space_served``. A resistive kW booked as space heat is this finding's bias.
_r10do_immersion = _r10do_slab(True, 4.0, immersion=True)
R.check(
    "#2499: an immersion element latched on the pump's meter leaves the slab "
    "on the plan's trajectory, not advanced by its resistive kW as space heat",
    _r10do_immersion == 25.0,
    "slab=%.3f" % _r10do_immersion,
)
_r10do_dhw_only = _r10do_slab(True, 4.0, mode="DHW (Hot Water)")
_r10do_heating = _r10do_slab(True, 4.0, mode="Heating")
R.check(
    "#2499: a pump observed in a hot-water-only mode books 0 kW of space heat "
    "(the slab cools as with the pump off); observed heating rooms, its draw",
    _r10do_dhw_only == _r10do_off and _r10do_heating == _r10do_full,
    "slab dhw-only/off=%.3f/%.3f heating/full=%.3f/%.3f"
    % (_r10do_dhw_only, _r10do_off, _r10do_heating, _r10do_full),
)
R.check(
    "#2499: a resistive element sharing the meter gives no space draw; a pump "
    "not serving rooms gives 0 kW",
    _r10do_draw.space_draw_kw(None, 3.0, (3.0, 0.0), shared=True, space_served=True) is None
    and _r10do_draw.space_draw_kw(None, 3.0, (3.0, 0.0), shared=False, space_served=False) == 0.0
    and _r10do_draw.space_draw_kw(None, 3.0, (2.0, 1.0), shared=False, space_served=True) == 2.0,
)

# The replay window's two bounds. A gap of exactly the learners' sample window
# is still replayed and a minute past it is not; a zero or negative gap (the
# same instant, or a clock stepped back) measured no interval, so the plan's
# prediction stands, as for every other unusable interval. That last one is a
# design choice: a zero-length replay would return the prior slab instead.
from heatpump_optimizer.coordinator import HOUSE_LOSS_MAX_SAMPLE_HOURS as _r10do_max_h  # noqa: E402

_r10do_edge = _r10do_slab(True, 0.0, gap_h=_r10do_max_h)
_r10do_past = _r10do_slab(True, 0.0, gap_h=_r10do_max_h + 1 / 60)
R.check(
    "#2499: a gap of exactly the sample window still advances the slab by the "
    "meter; a minute past it follows the plan",
    _r10do_edge < 23.0 and _r10do_past == 25.0,
    "slab edge/past=%.3f/%.3f" % (_r10do_edge, _r10do_past),
)
_r10do_zero = _r10do_slab(True, 0.0, gap_h=0.0)
_r10do_back = _r10do_slab(True, 0.0, gap_h=-0.5)
R.check(
    "#2499: a zero or negative gap replays nothing; the slab follows the plan",
    _r10do_zero == 25.0 and _r10do_back == 25.0,
    "slab zero/back=%.3f/%.3f" % (_r10do_zero, _r10do_back),
)

# The running floor ``space_draw_kw`` reads through: a reading AT the floor is
# standby, and a learned idle draw above the fixed floor raises it.
_r10do_idle = _r10do_draw.DrawRange()
_r10do_idle.idle.extend([0.4] * _r10do_draw.MIN_IDLE)
R.check(
    "#2499: a draw at the running floor is standby, not heat",
    _r10do_draw.running_kw(None, _r10do_draw.RUNNING_FLOOR_KW) == 0.0
    and _r10do_draw.running_kw(None, 0.3) == 0.3,
)
R.check(
    "#2499: a learned idle draw above the fixed floor raises it to "
    "IDLE_MARGIN times the idle draw",
    _r10do_draw.running_kw(_r10do_idle, 0.4) == 0.0
    and _r10do_draw.running_kw(_r10do_idle, 0.6) == 0.6,
    "idle_kw=%s" % _r10do_idle.idle_kw(),
)

# The tank block of ``_update_current_state``: a tank reading reaches the DHW
# learner and its freeze reason the coordinator; with no reading the learner is
# never called.


def _r10do_dhw(tank):
    coord = Coord(FakeHass(), _r9f12_entry(data={
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "optimization_interval": 30.0,
        "dhw_temp_entity": "sensor.tank",
    }))
    coord._snapshots_loaded = True
    seen = []

    async def _learn(temp):
        seen.append(temp)
        return "tank_probe"

    coord._dhw_learner.async_learn_dynamics = _learn
    _r9f12_dt.freeze(_r10do_t0)
    try:
        readings = [("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0")]
        if tank is not None:
            readings.append(("sensor.tank", tank))
        for entity, value in readings:
            coord.hass.states.set(entity, FakeState(value, last_updated=_r10do_t0, unit="°C"))
        _r9f12_aio.run(coord._update_current_state())
    finally:
        _r9f12_dt.freeze(None)
    return seen, coord._learner_freeze_reason, coord._legionella.last_cycle


_r10do_tank, _r10do_notank = _r10do_dhw("48.0"), _r10do_dhw(None)
R.check(
    "#2499: a tank reading reaches the DHW learner, and its freeze reason the "
    "coordinator; no reading reaches neither",
    _r10do_tank[:2] == ([48.0], "tank_probe") and _r10do_notank[:2] == ([], None),
    "tank=%s notank=%s" % (_r10do_tank, _r10do_notank),
)
# The same cycle hands the reading to ``LegionellaGuard.async_observe``: a tank
# at the disinfection temperature resets the timer; a cooler one, or none, not.
_r10do_hot = _r10do_dhw("65.0")
R.check(
    "#2499: a tank at the disinfection temperature resets the legionella timer "
    "through the coordinator's cycle; a cooler reading or none leaves it unset",
    _r10do_hot[2] == _r10do_t0 and _r10do_tank[2] is None and _r10do_notank[2] is None,
    "hot=%s cool=%s none=%s" % (_r10do_hot[2], _r10do_tank[2], _r10do_notank[2]),
)

# --- R9 P2 (#1644): one stamp owner, one window, one sizing bound ------------
R.section("R9 P2: stamp owner, plausibility window, sizing bound (D1-s5-01/-52, D2-s4-02)")

# D1-s5-01: age_of against the reader, on the same State at the same instant.
# A live sensor re-reporting an unchanged value (last_reported recent,
# last_updated old) and a stamp ahead of the clock were the two divergences.
_r9f41_cells = []
for _r9f41_rep, _r9f41_upd in (
    (5, 5), (5, 480), (30, 900), (-5, -5), (-60, 30), (400, 400),
):
    _r9f41_state = FakeState(
        "72.0",
        last_updated=minutes_ago(_r9f41_upd, NOW),
        last_reported=minutes_ago(_r9f41_rep, NOW),
    )
    _r9f41_age = inputs_mod.age_of(_r9f41_state, NOW)
    _r9f41_reader_age = InputReader(FakeHass({}), {}, now=lambda: NOW)._age_minutes(
        _r9f41_state
    )
    _r9f41_cells.append(
        (
            _r9f41_rep,
            _r9f41_upd,
            None if _r9f41_age is None else _r9f41_age.total_seconds() / 60.0,
            _r9f41_reader_age,
        )
    )
R.check(
    "D1-s5-01: age_of reads the reader's stamp precedence and refuses a future "
    "stamp, in every cell",
    all(
        (a is None and b is None)
        or (a is not None and b is not None and abs(a - b) < 1e-9)
        for _, _, a, b in _r9f41_cells
    )
    and _r9f41_cells[1][2] == 5.0
    and _r9f41_cells[3][2] is None,
    f"(reported, updated, age_of, reader): {_r9f41_cells}",
)

# One owner of the stamp chain (the P2 RCA's `state_stamp`): no other function
# in inputs.py names a stamp attribute, so the three copies cannot diverge.
_r9f41_tree = _r9f41_ast.parse(open(inputs_mod.__file__, encoding="utf-8").read())
_r9f41_stamp_sites = sorted(
    {
        _r9f41_fn.name
        for _r9f41_fn in _r9f41_ast.walk(_r9f41_tree)
        if isinstance(_r9f41_fn, (_r9f41_ast.FunctionDef, _r9f41_ast.AsyncFunctionDef))
        for _r9f41_node in _r9f41_ast.walk(_r9f41_fn)
        if (
            isinstance(_r9f41_node, _r9f41_ast.Constant)
            and _r9f41_node.value in ("last_reported", "last_updated", "last_changed")
        )
        or (
            isinstance(_r9f41_node, _r9f41_ast.Attribute)
            and _r9f41_node.attr in ("last_reported", "last_updated", "last_changed")
        )
    }
)
# source_polls reads the re-report FACT (last_reported past last_updated),
# not a freshness stamp, so it is the one other reader (R10 N-staleness).
R.check(
    "D1-s5-01: state_stamp is the only function in inputs.py reading a stamp, "
    "beside source_polls' re-report test",
    _r9f41_stamp_sites == ["source_polls", "state_stamp"],
    f"functions reading a stamp: {_r9f41_stamp_sites}",
)

# D1-s5-52: every temperature key the reader serves refuses the DS18B20 fault
# codes it cannot physically read, and passes an ordinary reading. The keys
# are enumerated from const, by the finding's seam rule's name pattern.
_r9f41_temp_keys = sorted(
    getattr(_r9f41_const, _r9f41_name)
    for _r9f41_name in dir(_r9f41_const)
    if _r9f41_re.fullmatch(r"CONF_\w*TEMP\w*_ENTITY", _r9f41_name)
)
R.check(
    "D1-s5-52: every CONF_*TEMP*_ENTITY key has a plausibility window",
    bool(_r9f41_temp_keys)
    and all(k in _r9f41_const.INPUT_PLAUSIBLE_RANGE_C for k in _r9f41_temp_keys),
    f"without one: "
    f"{[k for k in _r9f41_temp_keys if k not in _r9f41_const.INPUT_PLAUSIBLE_RANGE_C]}",
)
# Over the enumerated keys as well as the table's, so an empty table cannot
# pass the sentinel checks below by walking nothing.
_r9f41_all_keys = sorted(
    set(_r9f41_temp_keys) | set(_r9f41_const.INPUT_PLAUSIBLE_RANGE_C)
)
_r9f41_sentinel = {}
for _r9f41_key in _r9f41_all_keys:
    for _r9f41_raw in ("-127", "85", "21.3"):
        _r9f41_read = InputReader(
            FakeHass({"sensor.x": FakeState(_r9f41_raw, last_updated=minutes_ago(1, NOW))}),
            {_r9f41_key: "sensor.x"},
            now=lambda: NOW,
        ).read(_r9f41_key)
        _r9f41_sentinel[(_r9f41_key, _r9f41_raw)] = (
            _r9f41_read.problem,
            _r9f41_read.value,
        )
_r9f41_room_like = (
    "indoor_temp_entity",
    "lower_floor_temp_entity",
    "outdoor_temp_entity",
    "floor_return_temp_entity",
)
R.check(
    "D1-s5-52: -127 degC is refused as implausible on every temperature key, "
    "with no value left to read",
    all(_r9f41_sentinel[(k, "-127")] == ("implausible", None) for k in _r9f41_all_keys),
    f"{ {k: v for (k, raw), v in _r9f41_sentinel.items() if raw == '-127'} }",
)
R.check(
    "D1-s5-52: 85 degC is refused in a room, outdoors and in a floor circuit",
    all(_r9f41_sentinel[(k, "85")][0] == "implausible" for k in _r9f41_room_like),
    f"{ {k: _r9f41_sentinel[(k, '85')] for k in _r9f41_room_like} }",
)
R.check(
    "D1-s5-52: an ordinary 21.3 degC passes on every key (the null control)",
    all(_r9f41_sentinel[(k, "21.3")] == (None, 21.3) for k in _r9f41_all_keys),
)
_r9f41_health = InputReader(
    FakeHass({"sensor.x": FakeState("-127", last_updated=minutes_ago(1, NOW))}),
    {"indoor_temp_entity": "sensor.x"},
    now=lambda: NOW,
)
_r9f41_health.read("indoor_temp_entity")
R.check(
    "D1-s5-52: an implausible reading is a missing input with words for it",
    _r9f41_health.health.missing_keys == ["indoor_temp_entity"]
    and _r9f41_health.health.problem_messages()
    == ["sensor.x: outside its plausible range"],
    f"{_r9f41_health.health.missing_keys} {_r9f41_health.health.problem_messages()}",
)

# D2-s4-02: the step is sized under the abort bound by the noise headroom, on
# the heavy default house (#779's own cell), and still uses the rest of it.
_r9f41_sid = SystemIdentification(SysIdConfig(enabled=True))
_r9f41_el = _r9f41_sid._size_step_power(6.0, 3.0, 21.0, 2.0, 0.20, 8.0, 0.3)
_r9f41_peak, _r9f41_final = _r9f41_sysid._predict_step_excursion_plant(
    HousePlant(ua=0.20, capacity=8.0, gains=0.3), 21.0, 2.0,
    (_r9f41_el or 0.0) * 3.0, 2.0, 2.0
)
_r9f41_bound = (
    _r9f41_sid.config.max_excursion_c - _r9f41_sysid.SIZING_NOISE_HEADROOM_C
)
R.check(
    "D2-s4-02: the sized step's noiseless peak leaves the noise headroom under "
    "the abort bound, and uses the allowance below it",
    _r9f41_el is not None
    and _r9f41_bound - 0.05 <= _r9f41_peak <= _r9f41_bound
    and _r9f41_final <= _r9f41_bound,
    f"Pel={_r9f41_el} peak={_r9f41_peak:.4f} final={_r9f41_final:.4f} "
    f"bound={_r9f41_bound}",
)
R.check(
    "the degenerate-house bound is closed AT the bound: a house at exactly "
    "1e-9 predicts infinity, not a finite excursion",
    _r9f41_sysid._predict_step_excursion_plant(
        HousePlant(ua=1e-9, capacity=8.0, gains=0.3), 21.0, 0.0, 3.0, 2.0, 2.0
    ) == (float("inf"), float("inf"))
    and _r9f41_sysid._predict_step_excursion_plant(
        HousePlant(ua=0.2, capacity=1e-9, gains=0.3), 21.0, 0.0, 3.0, 2.0, 2.0
    ) == (float("inf"), float("inf")),
    "a CMP_BOUND mutant on the guard's `<=` passes every value the other "
    "checks drive (0.0 and 0.2 both fire `<` too) and survives on them; only "
    "the bound itself separates closed from open",
)


# --- R9 P11 (#1649): the stub clock and the stub Store answer as Home Assistant's
R.section("R9 P11: the stub clock is aware by default and the stub Store honours version (D1-s1-52, #1740)")
import asyncio as _r9f10b_asyncio  # noqa: E402
import os as _r9f10b_os  # noqa: E402

from homeassistant.exceptions import HomeAssistantError as _r9f10b_HAError  # noqa: E402
from homeassistant.helpers import storage as _r9f10b_storage  # noqa: E402
from homeassistant.util import dt as _r9f10b_dt  # noqa: E402

_r9f10b_clock_default = _r9f10b_os.environ.get("HASTUB_TZ") is None
if _r9f10b_clock_default:
    # Upstream's clock is aware in UTC when no zone is configured. A naive clock
    # inverted the verdict of every stored-stamp comparison: a naive stamp passed
    # against it, where Home Assistant raises (D1-s1-52).
    _r9f10b_live = _r9f10b_dt.now()
    R.check(
        "with no zone configured the clock is aware, in UTC",
        _r9f10b_live.tzinfo is not None and _r9f10b_live.utcoffset() == timedelta(0),
        repr(_r9f10b_live),
    )
    R.check(
        "...and the configured zone is UTC, not None, as upstream's is",
        _r9f10b_dt.DEFAULT_TIME_ZONE is timezone.utc,
        repr(_r9f10b_dt.DEFAULT_TIME_ZONE),
    )
    _r9f10b_wall = datetime(2026, 3, 4, 12, 30)
    _r9f10b_dt.freeze(_r9f10b_wall)
    try:
        _r9f10b_frozen = _r9f10b_dt.now()
        _r9f10b_frozen_utc = _r9f10b_dt.utcnow()
    finally:
        _r9f10b_dt.freeze(None)
    R.check(
        "a naive freeze is read as UTC wall time by both clocks",
        _r9f10b_frozen == _r9f10b_wall.replace(tzinfo=timezone.utc)
        and _r9f10b_frozen_utc == _r9f10b_frozen,
        f"{_r9f10b_frozen!r} / {_r9f10b_frozen_utc!r}",
    )

    def _r9f10b_mixed(stamp):
        try:
            return _r9f10b_dt.now() - stamp
        except TypeError:
            return "TypeError"

    R.check(
        "a naive stored stamp read against the clock raises, as it does upstream",
        _r9f10b_mixed(datetime(2026, 1, 1)) == "TypeError",
    )
    R.check(
        "null control: an aware stamp against the same clock subtracts",
        _r9f10b_mixed(datetime(2026, 1, 1, tzinfo=timezone.utc)) != "TypeError",
    )
    R.check(
        "a stored instant typed without an offset loads aware through the stub's zone "
        "(the away picker string, D1-s3-01)",
        away_mode._parse_return_time("2026-03-04 12:30:00")
        == datetime(2026, 3, 4, 12, 30, tzinfo=timezone.utc),
        repr(away_mode._parse_return_time("2026-03-04 12:30:00")),
    )
    R.check(
        "as_local is still the identity under the UTC default (every golden fixture "
        "was recorded that way)",
        _r9f10b_dt.as_local(_r9f10b_wall) is _r9f10b_wall,
    )


async def _r9f10b_store_load(store_class, saved_at, loaded_at):
    await _r9f10b_storage.Store(None, saved_at, "r9f10b_version").async_save({"n": 1})
    try:
        return await store_class(None, loaded_at, "r9f10b_version").async_load()
    except NotImplementedError:
        return "NotImplementedError"
    except _r9f10b_storage.UnsupportedStorageVersionError:
        return "Unsupported"
    finally:
        _r9f10b_storage._reset_store_disk()


async def _r9f10b_store_resave(saved_at, loaded_at):
    """Load twice through a migrating Store; report loads, stored version, saves."""
    _r9f10b_storage.SAVE_COUNTS.clear()
    await _r9f10b_storage.Store(None, saved_at, "r9f10b_resave").async_save({"n": 1})
    loads = [
        await _R9F10bMigrating(None, loaded_at, "r9f10b_resave").async_load()
        for _ in range(2)
    ]
    state = (
        _r9f10b_storage._VERSIONS["r9f10b_resave"],
        _r9f10b_storage.SAVE_COUNTS["r9f10b_resave"],
    )
    _r9f10b_storage._reset_store_disk()
    return loads, state


class _R9F10bMigrating(_r9f10b_storage.Store):
    async def _async_migrate_func(self, old_major, old_minor, old_data):
        return {"migrated_from": old_major, **old_data}


# Home Assistant re-raises NotImplementedError on a major-version mismatch that
# the Store does not migrate (helpers/storage.py, _async_load_data), so a version
# bump without a migration fails here and not on a user's install (#1740).
R.check(
    "control: a store saved and loaded at one version returns its data",
    _r9f10b_asyncio.run(_r9f10b_store_load(_r9f10b_storage.Store, 1, 1)) == {"n": 1},
)
R.check(
    "a store loaded at a newer major version with no migration raises NotImplementedError",
    _r9f10b_asyncio.run(_r9f10b_store_load(_r9f10b_storage.Store, 1, 2))
    == "NotImplementedError",
)
R.check(
    "...and one that defines _async_migrate_func is migrated from the stored version",
    _r9f10b_asyncio.run(_r9f10b_store_load(_R9F10bMigrating, 1, 2))
    == {"migrated_from": 1, "n": 1},
)
# Upstream refuses a downgrade before it looks for a migration, so a Store that
# migrates is still refused a document saved by a newer release.
R.check(
    "a store saved at a newer major version than the code's raises "
    "UnsupportedStorageVersionError, with or without a migration",
    _r9f10b_asyncio.run(_r9f10b_store_load(_r9f10b_storage.Store, 2, 1)) == "Unsupported"
    and _r9f10b_asyncio.run(_r9f10b_store_load(_R9F10bMigrating, 2, 1)) == "Unsupported"
    and issubclass(_r9f10b_storage.UnsupportedStorageVersionError, _r9f10b_HAError),
)
# ...and a migration is saved back, as upstream does, so it runs once.
R.check(
    "a migrated load is saved back: the stored version updates to 2, there are "
    "two saves, and a second load returns the data without migrating again",
    _r9f10b_asyncio.run(_r9f10b_store_resave(1, 2))
    == ([{"migrated_from": 1, "n": 1}, {"n": 1, "migrated_from": 1}], (2, 2)),
)


# ===========================================================================
# Round 9, F4.2: class-named blocks, sorted by class
# ===========================================================================
# The sysid blocks (N-fit-integrator, P5) extend the #1524 runner, whose block
# they read; they sit beside it. This one reads only the input reader.

# --- R9 N-staleness (carry-1655): a set-point is not a probe -----------------
R.section("R9 N-staleness: the mixing-valve target is a set-point (carry-1655)")

# Home Assistant stamps a set-point only when someone changes it, so a valve
# target left alone for 90 min, and for a day, is still the target.
_r9f42_key = "mixing_valve_target_entity"
_r9f42_reads = {
    _r9f42_age: InputReader(
        FakeHass({"number.valve": FakeState("22.5", last_updated=minutes_ago(_r9f42_age, NOW))}),
        {_r9f42_key: "number.valve"},
        now=lambda: NOW,
    ).read(_r9f42_key)
    for _r9f42_age in (90, 24 * 60)
}
_r9f42_dead = InputReader(
    FakeHass({"number.valve": FakeState("unavailable", last_updated=minutes_ago(5, NOW))}),
    {_r9f42_key: "number.valve"},
    now=lambda: NOW,
).read(_r9f42_key)
R.check(
    "carry-1655: a valve target unchanged for 90 min and for a day reads as "
    "the target; an unavailable valve is still refused",
    all(r.ok and r.value == 22.5 for r in _r9f42_reads.values())
    and inputs_mod.max_age_for(_r9f42_key) is None
    and not _r9f42_dead.ok,
    f"{ {a: (r.problem, r.value) for a, r in _r9f42_reads.items()} }, "
    f"limit {inputs_mod.max_age_for(_r9f42_key)}, dead {_r9f42_dead.problem}",
)

# --- R9 P8 (#1657): a money figure names the currency its feed declares -----
R.section("R9 P8: money units follow the price feed; bounds scale (D14-s2-02, D12-s3-81)")

# One fact, one owner: the price feed denominates every money figure, so the
# published unit is the feed's declared code (D6: the instance's only where
# the feed declares none), the options dialog's money fields and fee bounds
# scale with the currency they are labelled in, and a feed that disagrees with
# the instance raises a notice. Every arm drives the production symbol.
import asyncio as _r9p8_aio  # noqa: E402

from harness import FakeEntry as _r9p8_Entry  # noqa: E402
from heatpump_optimizer import config_flow as _r9p8_flow  # noqa: E402
from heatpump_optimizer import coordinator as _r9p8_coord  # noqa: E402
from heatpump_optimizer import currency as _r9p8_cur  # noqa: E402
from heatpump_optimizer import grid_fee as _r9p8_fee  # noqa: E402
from heatpump_optimizer import sensor as _r9p8_sensor  # noqa: E402
from heatpump_optimizer.const import CONF_WOOD_PRICE_SEK_M3 as _r9p8_WOOD  # noqa: E402

_r9p8_cfg = {
    "price_entity": "sensor.price", "price_source": "entity",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
}


def _r9p8_hass(instance, unit=None, attributes=None):
    states = {}
    if unit is not None or attributes is not None:
        states["sensor.price"] = FakeState(
            "0.10", attributes={"unit_of_measurement": unit, **(attributes or {})}
        )
    hass = FakeHass(states)
    hass.config.currency = instance
    return hass


R.check(
    "D14-s2-02: the feed's code is read from its unit, an unambiguous symbol, "
    "or its currency attribute; 'kr' and a minor unit in any case name none",
    [_r9p8_cur.declared_currency(u, a) for u, a in (
        ("EUR/kWh", None), ("€/MWh", None), ("öre/kWh", {"currency": "SEK"}),
        ("öre/kWh", None), ("kr/kWh", None), (None, None), ("ÖRE/kWh", None),
    )] == ["EUR", "EUR", "SEK", None, None, None, None],
)
_r9p8_units = {}
for _r9p8_inst, _r9p8_unit in (("SEK", "EUR/kWh"), ("SEK", "SEK/kWh"), ("EUR", "öre/kWh")):
    _r9p8_c = _r9p8_coord.HeatPumpOptimizerCoordinator(
        _r9p8_hass(_r9p8_inst, _r9p8_unit), _r9p8_Entry(data=_r9p8_cfg)
    )
    _r9p8_units[(_r9p8_inst, _r9p8_unit)] = _r9p8_sensor.CurrentPriceSensor(
        _r9p8_c, _r9p8_Entry(data=_r9p8_cfg)
    ).native_unit_of_measurement
R.check(
    "D14-s2-02: a EUR feed on a SEK instance publishes EUR/kWh; a SEK feed "
    "(null) and a feed declaring no code keep the instance currency",
    _r9p8_units == {
        ("SEK", "EUR/kWh"): "EUR/kWh", ("SEK", "SEK/kWh"): "SEK/kWh",
        ("EUR", "öre/kWh"): "EUR/kWh",
    },
    str(_r9p8_units),
)

# The startup race: the platforms are built before the feed has a state (the
# replay's order, and a feed integration that loads after this one). The
# first cycle adopts the feed's code, and the built sensor follows it.
_r9p8_race = _r9p8_coord.HeatPumpOptimizerCoordinator(
    _r9p8_hass("SEK"), _r9p8_Entry(data=_r9p8_cfg)
)
_r9p8_early = _r9p8_sensor.PredictedSavingsSensor(_r9p8_race, _r9p8_Entry(data=_r9p8_cfg))
_r9p8_price = _r9p8_sensor.CurrentPriceSensor(_r9p8_race, _r9p8_Entry(data=_r9p8_cfg))
_r9p8_before = (_r9p8_early.native_unit_of_measurement, _r9p8_price.native_unit_of_measurement)
_r9p8_race.hass.states.set(
    "sensor.price", FakeState("0.10", attributes={"unit_of_measurement": "EUR/kWh"})
)
_r9p8_aio.run(_r9p8_race._update_current_state())
_r9p8_race.hass.states.set(
    "sensor.price", FakeState("unavailable", attributes={})
)
_r9p8_aio.run(_r9p8_race._update_current_state())
R.check(
    "D14-s2-02: a feed that loads after the platforms is adopted by the next "
    "cycle, the built sensors follow it, and an unavailable feed keeps it",
    _r9p8_before == ("SEK", "SEK/kWh")
    and _r9p8_race.currency == "EUR"
    and _r9p8_early.native_unit_of_measurement == "EUR"
    and _r9p8_price.native_unit_of_measurement == "EUR/kWh",
    f"before {_r9p8_before}, after {_r9p8_race.currency} "
    f"{_r9p8_early.native_unit_of_measurement} {_r9p8_price.native_unit_of_measurement}",
)

_r9p8_issues = {}
for _r9p8_unit in ("EUR/kWh", "SEK/kWh"):
    _r9p8_h = _r9p8_hass("SEK", _r9p8_unit)
    _r9p8_h.issues = []
    _r9p8_coord._audit_price_units(_r9p8_h, _r9p8_cfg)
    _r9p8_issues[_r9p8_unit] = ([
        (i[1], i[2].get("translation_placeholders")) for i in _r9p8_h.issues
        if i[1] == "price_currency"
    ])
R.check(
    "D14-s2-02: a EUR feed on a SEK instance raises the price_currency notice "
    "naming both; a SEK feed (null) raises none",
    _r9p8_issues["EUR/kWh"] == [("price_currency", {
        "entity": "sensor.price", "feed": "EUR", "configured": "SEK"})]
    and _r9p8_issues["SEK/kWh"] == [],
    str(_r9p8_issues),
)

_r9p8_widgets = {}
for _r9p8_inst in ("EUR", "HUF", "SEK"):
    _r9p8_h = _r9p8_hass(_r9p8_inst)
    for _r9p8_row in _r9p8_flow._OPTION_FIELDS:
        if _r9p8_row.key in (_r9p8_WOOD, "grid_fee_fixed"):
            _r9p8_w = _r9p8_row.widget.of(_r9p8_h)
            _r9p8_widgets[(_r9p8_inst, _r9p8_row.key)] = (
                _r9p8_w.config.get("unit_of_measurement"), _r9p8_w.config.get("max")
            )
R.check(
    "D14-s2-02: the firewood price is labelled in the instance currency, "
    "as every other money field is",
    _r9p8_widgets[("EUR", _r9p8_WOOD)][0] == "EUR/m³"
    and _r9p8_widgets[("SEK", _r9p8_WOOD)][0] == "SEK/m³",
    str(_r9p8_widgets),
)
R.check(
    "D12-s3-81: a 0.05 EUR/kWh fee (about 20 HUF) is enterable and passes the "
    "bound in HUF; the SEK field and bound are unchanged (null)",
    _r9p8_widgets[("HUF", "grid_fee_fixed")] == ("HUF/kWh", 250.0)
    and _r9p8_widgets[("SEK", "grid_fee_fixed")] == ("SEK/kWh", 5)
    and _r9p8_fee.spec_problem("= 20", "HUF") is None
    and _r9p8_fee.spec_problem("= 20", "SEK") == _r9p8_fee.ERROR_IMPLAUSIBLE
    and _r9p8_fee.spec_problem("= 20") == _r9p8_fee.ERROR_IMPLAUSIBLE,
    str(_r9p8_widgets),
)
_r9p8_page = {}
for _r9p8_inst in ("HUF", "SEK"):
    _r9p8_opt = _r9p8_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(
        _r9p8_Entry(data={"tibber_token": "t"})
    )
    _r9p8_opt.hass = _r9p8_hass(_r9p8_inst)
    _r9p8_shown = _r9p8_aio.run(_r9p8_opt.async_step_grid_fees(None))
    _r9p8_sent = _r9p8_aio.run(
        _r9p8_opt.async_step_grid_fees({"grid_fee_rules": "= 20"})
    )
    _r9p8_page[_r9p8_inst] = (
        _r9p8_shown["description_placeholders"]["fee_bound"],
        (_r9p8_sent.get("errors") or {}).get("grid_fee_rules"),
    )
R.check(
    "D12-s3-81: the grid-fee page states the bound in its own currency and "
    "saves 20 HUF/kWh; 20 SEK/kWh (null) is still refused as öre",
    _r9p8_page == {
        "HUF": ("500", None), "SEK": ("10", _r9p8_fee.ERROR_IMPLAUSIBLE),
    },
    str(_r9p8_page),
)
_r9p8_fee_issue = {}
for _r9p8_inst in ("HUF", "SEK"):
    _r9p8_c = _r9p8_coord.HeatPumpOptimizerCoordinator(
        _r9p8_hass(_r9p8_inst),
        _r9p8_Entry(data={"grid_fee_mode": "rules", "grid_fee_rules": "= 20"}),
    )
    _r9p8_c._fee_series([NOW + timedelta(minutes=15 * i) for i in range(4)])
    _r9p8_fee_issue[_r9p8_inst] = [
        i[2].get("translation_placeholders", {}).get("currency")
        for i in getattr(_r9p8_c.hass, "issues", []) if i[1] == "grid_fee_magnitude"
    ]
R.check(
    "D12-s3-81: the coordinator's fee notice scales too: 20 HUF/kWh raises "
    "none, 20 SEK/kWh (null) still raises it",
    _r9p8_fee_issue == {"HUF": [], "SEK": ["SEK"]},
    str(_r9p8_fee_issue),
)


# ===========================================================================
# v5.3.0: strings and flags, guarded like numbers
# ===========================================================================
R.section("Non-numeric inputs (v5.3.0)")

# The four signals a heat-pump integration publishes about itself. `read`
# rejects every one of them as `not_numeric`; `read_state` and `read_bool`
# are what make them readable without giving up the freshness discipline.
SIGNALS = {
    "heat_pump_mode_entity": "select.pump_mode",
    "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
    "heat_pump_online_entity": "binary_sensor.pump_online",
    "heat_pump_fault_entity": "binary_sensor.pump_fault",
}


def signals(states, **kwargs):
    return InputReader(FakeHass(states), SIGNALS, now=lambda: NOW, **kwargs)


# -- present ----------------------------------------------------------------
_mode_now = signals(
    {"select.pump_mode": FakeState("Heating + DHW", last_updated=minutes_ago(2, NOW))}
)
_mode = _mode_now.read_state("heat_pump_mode_entity")
R.check(
    "a fresh string entity reads as text",
    _mode.ok and _mode.text == "Heating + DHW",
    f"{_mode.problem}, text {_mode.text!r}",
)
R.check(
    "and carries no number, so numeric callers cannot mistake it for one",
    _mode.value is None,
)
R.check(
    "the same entity through the numeric reader is still not_numeric",
    signals(
        {"select.pump_mode": FakeState("Heating + DHW")}
    ).read("heat_pump_mode_entity").problem
    == "not_numeric",
    "read()'s contract is unchanged",
)

# -- absent, missing, unavailable -------------------------------------------
R.check(
    "an unconfigured signal is not_configured, not a problem",
    InputReader(FakeHass({}), {}, now=lambda: NOW)
    .read_state("heat_pump_mode_entity")
    .problem
    == "not_configured",
)
R.check(
    "a configured entity that does not exist is missing_entity",
    signals({}).read_state("heat_pump_mode_entity").problem == "missing_entity",
)
for _bad in ("unavailable", "unknown"):
    _r = signals({"select.pump_mode": FakeState(_bad)}).read_state(
        "heat_pump_mode_entity"
    )
    R.check(
        f"a {_bad} string entity yields nothing usable",
        not _r.ok and _r.problem == "unavailable",
        str(_r.problem),
    )

# -- stale ------------------------------------------------------------------
# The whole reason this method exists rather than a bespoke hand-read: a mode
# a polling source has not re-reported for ninety minutes is not evidence
# about the pump now (a source seen only on change is #2234's case).
_old_mode = signals(
    {
        "select.pump_mode": FakeState(
            "cool",
            last_updated=minutes_ago(120, NOW),
            last_reported=minutes_ago(90, NOW),
        )
    }
).read_state("heat_pump_mode_entity")
R.check(
    "an over-age string is rejected exactly like an over-age number",
    not _old_mode.ok and _old_mode.stale and _old_mode.problem == "stale",
    str(_old_mode.problem),
)
R.check(
    "and keeps its text for a caller that wants last-known-good",
    _old_mode.text == "cool" and _old_mode.age_minutes > 89,
)
R.check(
    "a defrost flag goes stale sooner than a mode does",
    signals(
        {
            "binary_sensor.pump_defrost": FakeState(
                "on", last_updated=minutes_ago(45, NOW)
            ),
            "select.pump_mode": FakeState("heat", last_updated=minutes_ago(45, NOW)),
        }
    ).read_bool("heat_pump_defrost_entity").stale
    and not signals(
        {"select.pump_mode": FakeState("heat", last_updated=minutes_ago(45, NOW))}
    ).read_state("heat_pump_mode_entity").stale,
    "an event needs a tighter horizon than a slow-moving state",
)

# -- unknown values ---------------------------------------------------------
_odd = signals({"select.pump_mode": FakeState("turbo")}).read_state(
    "heat_pump_mode_entity", valid=pump_mode.is_known
)
R.check(
    "a state outside the vocabulary is reported, not passed on",
    not _odd.ok and _odd.problem == "unknown_value",
    str(_odd.problem),
)
R.check(
    "while a recognised one passes the same gate",
    signals({"select.pump_mode": FakeState("Cooling + DHW")})
    .read_state("heat_pump_mode_entity", valid=pump_mode.is_known)
    .ok,
)
R.check(
    "a plain container of accepted states works too, case-insensitively",
    signals({"select.pump_mode": FakeState("Heat")})
    .read_state("heat_pump_mode_entity", valid=("heat", "cool"))
    .ok,
)
_stale_odd = signals(
    {
        "select.pump_mode": FakeState(
            "turbo",
            last_updated=minutes_ago(120, NOW),
            last_reported=minutes_ago(90, NOW),
        )
    }
).read_state("heat_pump_mode_entity", valid=pump_mode.is_known)
R.check(
    "staleness outranks an unrecognised value",
    _stale_odd.problem == "stale",
    f"an old unknown value is old first, got {_stale_odd.problem}",
)

# -- flags ------------------------------------------------------------------
for _raw, _expected in (
    ("on", True),
    ("off", False),
    ("true", True),
    ("false", False),
    ("detected", True),
    ("clear", False),
    # A raw Tuya fault DP: zero is healthy, anything else is a fault. The
    # source integration's own rule is literally `value != 0`, so a user who
    # points the slot at the code sensor gets the same answer as the derived
    # binary sensor would give.
    ("0", False),
    ("1", True),
    ("3", True),
):
    _rb = signals({"binary_sensor.pump_fault": FakeState(_raw)}).read_bool(
        "heat_pump_fault_entity"
    )
    R.check(
        f"a flag reading {_raw!r} is {_expected}",
        _rb.ok and _rb.flag is _expected,
        f"{_rb.problem}, flag {_rb.flag!r}",
    )
    R.check(
        f"and {_raw!r} keeps the word it came from",
        _rb.text == _raw,
        "the first question asked of a misbehaving flag is what it said",
    )

_notbool = signals({"binary_sensor.pump_fault": FakeState("warm")}).read_bool(
    "heat_pump_fault_entity"
)
R.check(
    "an uninterpretable flag is refused rather than guessed",
    not _notbool.ok and _notbool.problem == "not_boolean" and _notbool.flag is None,
    str(_notbool.problem),
)
_stale_flag = signals(
    {"binary_sensor.pump_online": FakeState("on", last_updated=minutes_ago(90, NOW))}
).read_bool("heat_pump_online_entity")
R.check(
    "a stale flag is unusable but still reachable",
    not _stale_flag.ok and _stale_flag.stale and _stale_flag.flag is True,
    "mirrors read() keeping value on a stale numeric reading",
)

R.check("parse_bool reads a real bool through", parse_bool(True) is True)
R.check("parse_bool refuses a word it does not know", parse_bool("warm") is None)
R.check("parse_bool reads any non-zero number as yes", parse_bool("-2") is True)

# -- health, and what must NOT freeze ---------------------------------------
# Mode configured and healthy, online configured but unusable, defrost never
# configured at all -- the three states every install is a mixture of.
_health_reader = InputReader(
    FakeHass(
        {
            "binary_sensor.pump_online": FakeState("unavailable"),
            "select.pump_mode": FakeState("heat", last_updated=minutes_ago(2, NOW)),
        }
    ),
    {k: v for k, v in SIGNALS.items() if k != "heat_pump_defrost_entity"},
    now=lambda: NOW,
)
_health_reader.read_state("heat_pump_mode_entity")
_health_reader.read_bool("heat_pump_online_entity")
_health_reader.read_bool("heat_pump_defrost_entity")
R.check(
    "a configured-but-unusable signal is visible in the health snapshot",
    _health_reader.health.missing_keys == ["heat_pump_online_entity"],
    str(_health_reader.health.missing_keys),
)
R.check(
    "a never-configured signal is not held against the install",
    "heat_pump_defrost_entity" not in _health_reader.health.missing_keys
    and "heat_pump_defrost_entity" not in _health_reader.health.stale_keys,
    "absent evidence must not read as a fault, or every install without the "
    "optional sensor would look broken",
)


# ===========================================================================
# v5.3.0: the operating-mode vocabulary
# ===========================================================================
R.section("Heat pump operating mode (v5.3.0)")

# The five modes the reference unit (Rotenso Windmi, Tuya model 000004k4z6)
# exposes on DP 2, and what each one lets the pump actually do.
for _raw, _space, _dhw, _cooling, _concurrent in (
    ("cool", False, False, True, False),
    ("heat", True, False, False, False),
    ("DHW", False, True, False, False),
    ("COOLDHW", False, True, True, True),
    ("HEATDHW", True, True, False, True),
):
    _cap = pump_mode.capability(_raw)
    R.check(
        f"{_raw}: space={_space} dhw={_dhw}",
        _cap.space_heat is _space
        and _cap.dhw is _dhw
        and _cap.cooling is _cooling
        and _cap.known,
        f"got space={_cap.space_heat} dhw={_cap.dhw} cooling={_cap.cooling}",
    )
    R.check(
        f"{_raw}: two duties at once = {_concurrent}",
        _cap.concurrent is _concurrent,
        "HEATDHW and COOLDHW run both duties concurrently, which is exactly "
        "the premise _commanded_power's 'one at a time' comment gets wrong "
        "for this hardware",
    )

# The state Home Assistant actually holds is the select's LABEL, not the Tuya
# enum: the reference integration sets _attr_options to the labels and
# returns one from current_option. A vocabulary that knew only the enum would
# recognise nothing on a real install -- and, falling back to full
# capability, would do nothing at all, silently, forever.
for _label, _key in (
    ("Cooling", "cool"),
    ("Heating", "heat"),
    ("DHW (Hot Water)", "DHW"),
    ("Cooling + DHW", "COOLDHW"),
    ("Heating + DHW", "HEATDHW"),
):
    R.check(
        f"the select label {_label!r} resolves to {_key}",
        pump_mode.resolve(_label) == _key,
        str(pump_mode.resolve(_label)),
    )

for _spelling in ("heatdhw", "HEAT_DHW", "  Heating + DHW  ", "heating and dhw"):
    R.check(
        f"{_spelling!r} is tolerated",
        pump_mode.capability(_spelling).key == "HEATDHW",
        "case, spacing and punctuation must not decide whether the house "
        "gets heat",
    )

for _unknown in ("turbo", "auto", "", None, 7):
    _cap = pump_mode.capability(_unknown)
    R.check(
        f"an unrecognised mode {_unknown!r} falls back to full capability",
        _cap.space_heat and _cap.dhw and not _cap.known and _cap is pump_mode.FULL_CAPABILITY,
        "suppressing everything on a word nobody recognised is a cold house "
        "in January; over-promising for one interval is not",
    )
R.check(
    "and the unknown fallback does not claim two duties at once",
    not pump_mode.FULL_CAPABILITY.concurrent,
    "without evidence, keep the pre-v5.3.0 assumption",
)

R.check(
    "suppression is symmetric",
    not pump_mode.capability("DHW").space_heat
    and not pump_mode.capability("heat").dhw
    and not pump_mode.capability("cool").space_heat
    and not pump_mode.capability("cool").dhw,
    "a hot-water-only mode must suppress space heating and a heating-only "
    "mode must suppress hot water; promising either is promising heat the "
    "pump cannot deliver",
)
R.check(
    "every mode carries what a future writer would need",
    all(
        m.key and m.options and m.label
        for m in pump_mode.MODES.values()
    )
    and tuple(pump_mode.MODES) == ("cool", "heat", "DHW", "COOLDHW", "HEATDHW"),
    "the device enum to put on the wire, and the select option string HA's "
    "select.select_option would have to be given",
)


# -- the external-heat override, migrated onto the shared reader ------------
#
# A deliberate behaviour change (v5.3.0): this was the one input in the
# integration read straight out of hass.states, with no age limit at all. It
# is also the strongest input there is -- while it says "yes" the optimizer
# stops planning heat, and while it says "no" it overrules the detector -- so
# a flue PROBE that died mid-fire suppressed heating indefinitely.
#
# The horizon therefore applies to numbers only. A probe re-reports on every
# poll, so its age is evidence; a flag helper is written only when it changes,
# so its age is "how long since the user decided" and ageing it out silently
# throws the decision away. Both halves are pinned below, because getting the
# second one wrong is a regression for installs with no Tuya hardware at all.
_OVERRIDE_CFG = {"external_heat_entity": "binary_sensor.stove"}


class _OverrideHost:
    _external_heat_override = Coord._external_heat_override

    def __init__(self) -> None:
        # The probe's "has gone quiet" warning is logged once per outage
        # rather than once per cycle; the flag lives on the coordinator.
        self._external_probe_stale_warned = False


def override_at(entity_id, state):
    cfg = {"external_heat_entity": entity_id}
    states = {} if state is None else {entity_id: state}
    return _OverrideHost()._external_heat_override(
        InputReader(FakeHass(states), cfg, now=lambda: NOW)
    )


def override_for(state):
    return override_at("binary_sensor.stove", state)


R.check(
    "a lit stove still reads as an override",
    override_for(FakeState("on", last_updated=minutes_ago(5, NOW))) is True,
)
R.check(
    "and a cold one still reads as no override",
    override_for(FakeState("off", last_updated=minutes_ago(5, NOW))) is False,
)
R.check(
    "a flue PROBE that stopped reporting stops suppressing (v5.3.0)",
    override_at("sensor.flue", FakeState("420", last_updated=minutes_ago(240, NOW)))
    is None
    and override_at("sensor.flue", FakeState("420", last_updated=minutes_ago(5, NOW)))
    is True,
    "the behaviour change, and its whole scope: a stalled hot probe used to "
    "hold suppression forever, which in winter is a cold house on the word "
    "of a flat battery",
)

# The regression this pair exists to catch. config_flow offers this slot as
# binary_sensor/switch/input_boolean/sensor and docs/configuration.md names
# the same four; the two named first are helpers HA writes ONLY on a toggle,
# so last_reported/last_updated/last_changed are all the moment the user
# flipped it. Under a 60 min horizon the reading went stale an hour later and
# the override vanished in BOTH directions -- the deliberate "yes" that holds
# heating back AND the deliberate "no" that overrules the detector -- on an
# install that configures none of the pump signals this branch is about.
for _dom in ("input_boolean.wood_fire", "switch.stove", "binary_sensor.flue_stat"):
    for _age in (61.0, 600.0, 2880.0):
        R.check(
            f"a flag helper is not aged out: {_dom.split('.')[0]} 'on' at "
            f"{_age:.0f} min still suppresses",
            override_at(_dom, FakeState("on", last_updated=minutes_ago(_age, NOW)))
            is True,
            "nothing re-writes an input_boolean, so its age measures how long "
            "ago the user decided, not how long since anyone checked",
        )
        R.check(
            f"...and its deliberate 'off' at {_age:.0f} min still overrules "
            f"the detector ({_dom.split('.')[0]})",
            override_at(_dom, FakeState("off", last_updated=minutes_ago(_age, NOW)))
            is False,
            "losing the 'no' is the same bug in the other direction: the "
            "inference silently takes back over",
        )

R.check(
    "the horizon is scoped to numbers, not to the entity domain",
    override_at("sensor.stove_flag", FakeState("on", last_updated=minutes_ago(600, NOW)))
    is True
    and override_at("sensor.flue", FakeState("420", last_updated=minutes_ago(600, NOW)))
    is None,
    "the same sensor domain carries both a word and a measurement; what "
    "decides is whether age is evidence, which is a property of the value",
)
R.check(
    "a flue probe still uses its own threshold, not the shared numeric rule",
    override_for(FakeState("45", last_updated=NOW)) is True
    and override_for(FakeState("20", last_updated=NOW)) is False,
    "parse_bool would call 20 'yes' because it is non-zero, which is right "
    "for a fault code and wrong for a probe in a cold room",
)
R.check(
    "the shared vocabulary widens what a flag entity may say",
    override_for(FakeState("yes", last_updated=NOW)) is True,
    "unrecognised before, and silently ignored",
)
R.check(
    "UNBOUNDED is not the same as 'no key in the table'",
    InputReader(
        FakeHass({"sensor.x": FakeState("on", last_updated=minutes_ago(600, NOW))}),
        {"indoor_temp_entity": "sensor.x"},
    )
    .read_state("indoor_temp_entity", max_age_minutes=inputs_mod.UNBOUNDED)
    .max_age_minutes
    is None,
    "a key that HAS a horizon reads unbounded on request, and records the "
    "absence of a limit honestly rather than as a very large number",
)
R.check(
    "an unavailable or unconfigured override is simply absent",
    override_for(FakeState("unavailable")) is None and override_for(None) is None,
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
_nan_hour = list(CHEAP_NIGHT)
_nan_hour[3] = float("nan")
_nan_model = PriceShapeModel()
R.check(
    "a day with one NaN hour is refused",
    not _nan_model.observe_day(datetime(2026, 1, 5), _nan_hour)
    and _nan_model.days[0] == 0
    and bool(np.all(np.isfinite(_nan_model.shapes[0]))),
    f"days={_nan_model.days} shape0={_nan_model.shapes[0][:4]}",
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

# --- A corrupt persisted bin must not price the guessed tail at 0 (#922) ----
#
# from_dict coerced each bin with float() and checked no finiteness, while
# observe_day -- the writer of the same field -- refuses a non-finite day.
# The strictly-valid-JSON string "nan" survives the Store round-trip, so a
# corrupted bin reached extend_price_series, where max(0.0, nan) == 0.0
# prices that hour's quarters as free electricity, silently.
import asyncio as _aio922  # noqa: E402
import json as _json922  # noqa: E402
import logging as _logging922  # noqa: E402

from harness import FakeEntry as _Entry922  # noqa: E402
from heatpump_optimizer import const as _const922  # noqa: E402

_LEARNED922 = [
    0.70, 0.65, 0.62, 0.60, 0.62, 0.75, 1.00, 1.35,
    1.40, 1.20, 1.05, 1.00, 0.98, 0.95, 0.95, 1.00,
    1.15, 1.35, 1.30, 1.15, 1.00, 0.90, 0.82, 0.75,
]
_CFG922 = {
    _const922.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    _const922.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    _const922.CONF_DHW_TANK_VOLUME: 180.0,
}


def _coord922(entry_id):
    """A coordinator whose price-model store is the test's own disk key."""
    return Coord(
        FakeHass(),
        _Entry922(data=dict(_CFG922), entry_id=entry_id),
    )


class _Collect922(_logging922.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


_pm_logger922 = _logging922.getLogger("heatpump_optimizer.price_model")
_sink922 = _Collect922()
_pm_logger922.addHandler(_sink922)

_corrupt922 = _coord922("entry922corrupt")
_shape922 = list(_LEARNED922)
_shape922[22] = _json922.loads('"nan"')  # strict JSON: the *string* "nan"
_aio922.run(
    _corrupt922._price_model_store.async_save(
        {
            "model": {"shapes": [_shape922, list(_LEARNED922)], "days": [30, 30]},
            "days_seen": [],
            "quarter_days_seen": [],
        }
    )
)
_aio922.run(_corrupt922._async_load_price_model())
_warned922 = [
    r for r in _sink922.records if r.levelno >= _logging922.WARNING
]
R.check(
    "a non-finite persisted shape bin is refused at load, loudly",
    bool(np.all(np.isfinite(_corrupt922._price_model.shapes[0])))
    and bool(np.all(np.isfinite(_corrupt922._price_model.shapes[1])))
    and bool(_warned922),
    f"weekday[22]={_corrupt922._price_model.shapes[0][22]}, "
    f"warnings={len(_warned922)}",
)
_steps922 = [
    datetime(2026, 1, 20, 0) + timedelta(minutes=15 * i) for i in range(96)
]  # a Tuesday: the horizon reads the weekday profile
_prices922, _mask922, _ = extend_price_series(
    [1.0] * 40, 96, _steps922, _corrupt922._price_model
)
R.check(
    "the guessed tail holds no zero-priced step",
    not bool(np.any(np.asarray(_prices922[40:], dtype=float) <= 1e-12)),
    f"{int(np.count_nonzero(np.asarray(_prices922) <= 1e-12))} of 96 "
    f"planning steps priced at 0.0 SEK/kWh",
)

_qf922 = _coord922("entry922quarters")
_qf_bad922 = [1.0] * 96
_qf_bad922[22 * 4 + 3] = _json922.loads('"nan"')
_aio922.run(
    _qf922._price_model_store.async_save(
        {
            "model": {
                "shapes": [list(_LEARNED922), list(_LEARNED922)],
                "days": [30, 30],
                "quarter_factors": [_qf_bad922, [1.0] * 96],
                "quarter_days": [30, 30],
            },
            "days_seen": [],
            "quarter_days_seen": [],
        }
    )
)
_aio922.run(_qf922._async_load_price_model())
R.check(
    "a non-finite persisted quarter factor is refused at load too",
    bool(np.all(np.isfinite(_qf922._price_model.quarter_factors[0])))
    and bool(np.all(np.isfinite(_qf922._price_model.quarter_factors[1]))),
    f"weekday q87={_qf922._price_model.quarter_factors[0][22 * 4 + 3]}",
)

# Null control: an undamaged store still loads into exactly the model it
# holds, with no warning -- the gate must cost a healthy payload nothing.
_finite922 = _coord922("entry922finite")
_aio922.run(
    _finite922._price_model_store.async_save(
        {
            "model": {
                "shapes": [list(_LEARNED922), list(_LEARNED922)],
                "days": [30, 30],
            },
            "days_seen": ["2026-01-19"],
            "quarter_days_seen": [],
        }
    )
)
_before922 = len(_sink922.records)
_aio922.run(_finite922._async_load_price_model())
_direct922 = PriceShapeModel()
_direct922.shapes = [list(_LEARNED922), list(_LEARNED922)]
_direct922.days = [30, 30]
R.check(
    "a finite store round-trips to the identical model, warning-free",
    _finite922._price_model.as_dict() == _direct922.as_dict()
    and _finite922._price_learner.days_seen == {"2026-01-19"}
    and len(_sink922.records) == _before922,
    f"warnings added={len(_sink922.records) - _before922}",
)
_pm_logger922.removeHandler(_sink922)

# --- A non-finite learned scalar must not install on the live model (D1-01) -
#
# _async_load_thermal_learning parses each stored scalar with float() under a
# (TypeError, ValueError, OverflowError) guard. float('nan') raises nothing, so
# the guard admits it and np.clip propagates it onto the live thermal model: a
# NaN cop_scale publishes a wrong cost and a NaN house_heat_loss_scale fails
# every solve and is re-persisted non-finite. inf is clamped by np.clip rather
# than installed, so the guard has to refuse every non-finite value, not NaN
# alone. The count is read off _thermal_params -- the value the seam delivers
# into the model, which is what a solve actually consumes.
import math as _math_d101  # noqa: E402

_THERMAL_SCALARS = (
    "house_heat_loss_scale", "buffer_cooling_rate",
    "lower_floor_loss_ratio", "cop_scale",
)
_THERMAL_CLEAN = {
    "house_heat_loss_scale": 1.0, "buffer_cooling_rate": 0.3,
    "lower_floor_loss_ratio": 0.5, "cop_scale": 1.0,
    "house_heat_loss_anchor": 0.0,
}


def _thermal_load(entry_id, **overrides):
    """Load _THERMAL_CLEAN plus ``overrides`` through the real loader."""
    coord = Coord(FakeHass(), _Entry922(data=dict(_CFG922), entry_id=entry_id))
    _aio922.run(
        coord._thermal_learning_store.async_save({**_THERMAL_CLEAN, **overrides})
    )
    _aio922.run(coord._async_load_thermal_learning())
    return coord


def _installed_nonfinite(coord):
    """Learned scalars that reached _thermal_params non-finite."""
    tp = coord._thermal_params
    return [n for n in _THERMAL_SCALARS if not _math_d101.isfinite(getattr(tp, n))]


# The coordinator's own pre-load model: the value a refused store must leave in
# place. For a learned scalar the mirror the seam keeps is seeded from exactly
# these, so a refusal has to land back on them.
_THERMAL_PRELOAD = {
    n: getattr(
        Coord(
            FakeHass(), _Entry922(data=dict(_CFG922), entry_id="thermal_d101_pre")
        )._thermal_params,
        n,
    )
    for n in _THERMAL_SCALARS
}


for _d101_name, _d101_bad in (
    ("cop_scale", float("nan")),
    ("house_heat_loss_scale", float("nan")),
    ("buffer_cooling_rate", float("nan")),
    ("lower_floor_loss_ratio", float("nan")),
    ("cop_scale", float("inf")),
    ("house_heat_loss_scale", float("-inf")),
):
    _d101 = _thermal_load(
        f"thermal_d101_{_d101_name}_{_d101_bad}", **{_d101_name: _d101_bad}
    )
    # The scalar the bad value would have replaced has to SURVIVE, which is a
    # stricter claim than "nothing non-finite landed": np.clip turns +-inf into
    # the band's own edge, so an inf arm judged only on finiteness passes
    # against a NaN-only guard.
    _d101_kept = getattr(_d101._thermal_params, _d101_name)
    R.check(
        f"a non-finite {_d101_name}={_d101_bad!r} never installs on the live model",
        _installed_nonfinite(_d101) == []
        and _d101_kept == _THERMAL_PRELOAD[_d101_name],
        f"installed={_installed_nonfinite(_d101)} kept={_d101_kept!r} "
        f"preload={_THERMAL_PRELOAD[_d101_name]!r}",
    )

# Null control: the same store with every scalar finite installs each one, so
# the guard costs a healthy payload nothing.
_thermal_ok = _thermal_load(
    "thermal_d101_finite",
    house_heat_loss_scale=1.25, buffer_cooling_rate=0.4,
    lower_floor_loss_ratio=0.6, cop_scale=0.9,
)
R.check(
    "a finite thermal store still installs every learned scalar",
    _installed_nonfinite(_thermal_ok) == []
    and _thermal_ok._thermal_params.house_heat_loss_scale == 1.25
    and _thermal_ok._thermal_params.buffer_cooling_rate == 0.4
    and _thermal_ok._thermal_params.lower_floor_loss_ratio == 0.6
    and _thermal_ok._thermal_params.cop_scale == 0.9,
    f"installed={_installed_nonfinite(_thermal_ok)} "
    f"cop={_thermal_ok._thermal_params.cop_scale}",
)

# The clamp still binds on a finite value: the guard refuses only non-finite
# input, it does not replace the band.
_thermal_clamped = _thermal_load("thermal_d101_clamped", cop_scale=COP_SCALE_MAX * 4.0)
R.check(
    "a finite cop_scale past the cap is clamped, not refused",
    _thermal_clamped._thermal_params.cop_scale == COP_SCALE_MAX,
    f"cop_scale={_thermal_clamped._thermal_params.cop_scale}",
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
# One peak a day: the billed peaks fall on different days (#1512), and this
# block pins the averaging, not the day rule (the #1512 oracle pins that).
for day, load in enumerate([2.0, 5.0, 9.0, 4.0, 7.0, 3.0]):
    tracker.observe(base + timedelta(days=day), load, tariff)
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

# The plan-side charge is `peak_cost` (what the optimizer's capacity term
# calls, optimizer.py `_grid_terms`); the former `tariff.peak_penalty`
# wrapper around it was dead in production (#226) and is gone.
R.check(
    "staying under the threshold costs nothing",
    peak_cost(
        np.full(8, 2.0), np.full(8, 1.0), PeakBilling(5.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25),
    ) == 0.0,
)

# These checks pin the WINDOW-level top-k arithmetic (#232, #925, #1210) --
# the tariff with the distinct-days rule off, and the across-days top-k the
# rule still applies -- so each passes distinct_days=False. The day rule
# itself is pinned by the #1512 bill oracle (R8-D2-s2-01's section).
# The bill is full_price x mean(top-k peaks), which rearranges exactly to
# marginal_price x sum(top-k excesses). Charging only the single largest, as
# this originally did, under-states a plan with several high hours -- the very
# plan a capacity tariff exists to discourage.
hourly = np.array([8.0, 7.9, 7.8, 5.5, 5.1] + [3.0] * 19)
charged = peak_cost(hourly, np.zeros(24), PeakBilling(6.0, 20.0, 60, 1.0, 3, distinct_days=False))
top3 = np.sort(np.maximum(0.0, hourly - 6.0))[-3:]
R.check(
    "the peak charge equals the bill it models",
    abs(charged - 60.0 * float(np.mean(top3))) < 0.05,
    f"charged {charged:.2f}, bill {60.0 * float(np.mean(top3)):.2f}",
)
R.check(
    "several high hours cost more than one",
    peak_cost(np.array([8.0] * 3 + [3.0] * 21), np.zeros(24), PeakBilling(6.0, 20.0, 60, 1.0, 3, distinct_days=False))
    > peak_cost(np.array([8.0] + [3.0] * 23), np.zeros(24), PeakBilling(6.0, 20.0, 60, 1.0, 3, distinct_days=False)),
)

# The solver reaches this through numerical gradients, so a term that is flat
# almost everywhere is invisible to it. Measured: with a plain ``max`` the
# tariff had gradient at 1 step in 96 and enabling it *raised* the peak.
# peak_cost_smooth, the solver's term (#1210), is the surface that owes the
# gradient; the exact public peak_cost keeps one too on interior ties (the
# probe breaks the tie in its own favour) but not at bound-pinned plateaus,
# which is #232's blindness and the surrogate's reason to exist.
flat = np.full(96, 3.0)
base_cost = peak_cost_smooth(flat, np.full(96, 1.5), PeakBilling(3.0, 20.0, 60, 0.25, 3, distinct_days=False))
gradients = []
for index in (5, 50, 90, 95):
    probe = flat.copy()
    probe[index] += 1e-4
    gradients.append(
        (peak_cost_smooth(probe, np.full(96, 1.5), PeakBilling(3.0, 20.0, 60, 0.25, 3, distinct_days=False))
         - base_cost) / 1e-4
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
        PeakBilling(fresh.threshold_kw(tariff), 20.0, 60, 0.25, 3, distinct_days=False)
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
    peak_cost(
        burst, np.zeros(8), PeakBilling(1.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25, distinct_days=False)
    )
    < peak_cost(
        np.full(8, 8.0), np.zeros(8), PeakBilling(1.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25, distinct_days=False)
    ),
    "penalising the instantaneous step would give away real savings",
)
# Not one charge per hour -- that would price a whole month's tariff into
# every busy hour of one day -- but not only the single largest either, since
# the bill averages the month's top few. Separated peaks use the exact sum;
# a full tie uses the smooth path and may read slightly lower (conservative).
_distinct = np.array([7.0, 7.0, 7.0, 4.9, 4.9, 4.9, 4.9, 4.9])
R.check(
    "the charge covers exactly the peaks the bill averages",
    abs(
        peak_cost(
            _distinct, np.zeros(8), PeakBilling(5.0,
            tariff.marginal_price_per_kw, tariff.window_minutes, 1.0,
            tariff.peaks_averaged, distinct_days=False)
        )
        - tariff.peaks_averaged * 2.0 * tariff.marginal_price_per_kw
    )
    < 5e-5,
    "three hours 2 kW over, averaged, at the full 60/kW = 120",
)

# Sequential softmax under-bills a k-wide tie (42 vs 60 on #454). Logistic
# bisection keeps the weights summing to k so the approximate sum stays
# k × tie_level.
_tie_bill = np.array([20.0, 20.0, 20.0, 5.0, 1.0])
R.check(
    "smooth top-k on a k-wide tie recovers the billed sum",
    abs(_smooth_topk_sum(_tie_bill, 3, 0.05) - 60.0) < 0.05,
    f"soft={_smooth_topk_sum(_tie_bill, 3, 0.05)} hard=60",
)

# Round 4 D3-S3 (#932): the clamp inside _smooth_topk_sum --
# k = max(1, min(int(k), x.size)) -- was deletable with the suite green
# (judged an equivalent mutant through reachable inputs: every production
# caller pre-clamps k on the same array before the call). The clamp states
# the billed contract -- the count is coerced onto [1, n] windows -- so it
# is pinned here rather than removed: a count past the window count bills
# the whole array exactly as the in-range count does, a fractional count
# bills its floor, and a count under one bills the single largest window.
# Each equality is call-vs-call on the same array, so it is exact: after
# the clamp both sides run the identical computation.
R.check(
    "a top-k count past the window count bills the full array unchanged",
    _smooth_topk_sum(_tie_bill, 8, 0.05) == _smooth_topk_sum(_tie_bill, 5, 0.05),
    "k=8 over 5 windows must coerce onto k=5 (the clamp's min arm), "
    f"got {_smooth_topk_sum(_tie_bill, 8, 0.05)} vs "
    f"{_smooth_topk_sum(_tie_bill, 5, 0.05)}",
)
R.check(
    "a fractional top-k count bills its floor (#932)",
    _smooth_topk_sum(_tie_bill, 2.5, 0.05) == _smooth_topk_sum(_tie_bill, 2, 0.05),
    "k=2.5 must coerce onto k=2 (the clamp's int arm), "
    f"got {_smooth_topk_sum(_tie_bill, 2.5, 0.05)} vs "
    f"{_smooth_topk_sum(_tie_bill, 2, 0.05)}",
)
R.check(
    "a top-k count under one bills the single largest window (#932)",
    _smooth_topk_sum(_tie_bill, 0.5, 0.05) == _smooth_topk_sum(_tie_bill, 1, 0.05),
    "k=0.5 must coerce onto k=1 (the clamp's max arm), "
    f"got {_smooth_topk_sum(_tie_bill, 0.5, 0.05)} vs "
    f"{_smooth_topk_sum(_tie_bill, 1, 0.05)}",
)
# Null control: the smooth sum is not inert in k -- inside [1, n] the
# billed count moves it -- so the equalities above pin the clamp's
# coercion and not a constant function.
R.check(
    "an in-range top-k count still moves the billed sum (#932 null control)",
    _smooth_topk_sum(_tie_bill, 1, 0.05) < _smooth_topk_sum(_tie_bill, 5, 0.05),
    "k=1 bills one 20 kW window, k=5 bills all five",
)

# Round 4 D2-01 (#925): the same contract at a *high* tie level. The
# bisection's logistic temperature is scale = tau*peak, and the tie root
# sits at peak + scale*ln((n-k)/k), which grows with the peak while the
# bracket's pad was a constant 1 kW -- so above ~5.84 kW of excess (96
# 15-minute windows, k=3) the root left the bracket, the bisection parked
# on the bracket end, and every tied window kept weight sigmoid(-1/scale).
# A flat 24 h plan at 12 kW -- the profile a capacity tariff exists to
# produce -- was charged 3660.34 SEK against a 720.00 bill (5.08x); the
# bracket must be scaled by its own temperature so the root stays inside
# it at any excess a plan can reach.
_d201_flat = np.full(96, 12.0)
R.check(
    "a flat plan is charged its billed top-k, not a multiple of it",
    abs(peak_cost(_d201_flat, np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)) - 720.0)
    < 7.2,
    f"charged {peak_cost(_d201_flat, np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)):.2f}"
    " SEK, bill 720.00 (1% of 3 x 12 kW at 20/kW)",
)
R.check(
    "smooth top-k keeps the k x tie_level contract at a 12 kW plateau",
    abs(_smooth_topk_sum(_d201_flat, 3, 0.05) - 36.0) < 0.36,
    f"soft={_smooth_topk_sum(_d201_flat, 3, 0.05):.2f}, contract 36",
)
# The same defect at hourly metering: reachable on a 24 h horizon, where
# the break point is ~10.3 kW (fewer windows, smaller ln((n-k)/k)).
_d201_hourly = peak_cost(np.full(96, 14.0), np.zeros(96), PeakBilling(0.0, 20.0, 60, 0.25, 3, distinct_days=False))
R.check(
    "hourly metering keeps the flat-plateau charge at the bill",
    abs(_d201_hourly - 840.0) < 8.4,
    f"charged {_d201_hourly:.2f} SEK, bill 840.00 (1% of 3 x 14 kW at 20/kW)",
)
# Null controls. Below the bracket's old break point the approximation was
# already exact and must stay exact -- the defect is the bracket, not the
# top-k sum. And a plan with at most k windows at the peak never enters the
# smooth branch at all, whatever the excess.
_d201_null_flat = peak_cost(
    np.full(96, 5.0), np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)
)
R.check(
    "below the tie-band break point the charge stays exact",
    abs(_d201_null_flat - 300.0) < 0.003,
    f"5 kW x 3 windows at 20/kW = 300, got {_d201_null_flat:.6f}",
)
_d201_spiky = np.full(96, 1.0)
_d201_spiky[:3] = 12.0
R.check(
    "at most k windows at the peak stay on the exact hard sum",
    peak_cost(_d201_spiky, np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)) == 720.0,
    "hard top-k path: 3 x 12 kW at 20/kW = 720 exactly",
)

# A one-window +eps probe always moves a hard top-k (that window becomes
# the unique largest, FD ≈ price_per_kw). Smooth top-k shares weight k/n
# across the tie, so the same probe is ≈ price * k/n (here 20 * 3/24 ≈ 2.5).
# These gradient pins read the SOLVER's term, peak_cost_smooth (#1210): the
# public peak_cost is the exact hard top-k everywhere, whose tied-window
# FD is the hard unique top (~20 here) -- the shared-weight signal is the
# surrogate's whole reason to exist (#232), so the pin reads the surface
# that owes the property.
_tied_base = peak_cost_smooth(
    np.full(24, 7.0), np.zeros(24), PeakBilling(6.0, 20.0, 60, 1.0, 3, distinct_days=False)
)
_tied_fd = [
    (
        peak_cost_smooth(
            np.where(np.arange(24) == i, 7.0001, 7.0),
            np.zeros(24),
            PeakBilling(6.0,
            20.0,
            60,
            1.0,
            3, distinct_days=False)
        )
        - _tied_base
    )
    / 1e-4
    for i in (0, 6, 12, 18)
]
R.check(
    "tied peak windows all carry gradient under smooth top-k",
    sum(1 for g in _tied_fd if abs(g) > 1e-6) >= 3,
    f"only {sum(1 for g in _tied_fd if abs(g) > 1e-6)} of 4 tied probes moved the charge",
)
R.check(
    "tied-window FD is the shared k/n weight, not a hard unique top",
    all(1.0 < g < 8.0 for g in _tied_fd),
    f"fd={_tied_fd} (hard unique-window is ~20, smooth k/n is ~2.5)",
)

# Round 5 D2-01 (#1210): the MIXED plateau -- more than k windows tied at
# the peak while OTHER windows sit above the threshold but below the tie.
# There the logistic weights still sum to k, but the weight that lands on
# the lower windows is charged at their level, not the tie's, so the smooth
# sum is below the billed top-k on every such input (soft - hard < 0
# identically; the round-5 harness measured it to -3.45%). The pure
# plateaus above are exact because every weighted window sits AT the tie;
# the defect needs the second population. peak_cost's docstring states the
# bill arithmetic, and the published projected_peak_cost is this function,
# so it must return that arithmetic exactly on every input.
_d1201_mixed = np.concatenate([
    np.full(24, 8.0),                        # the tied plateau at the peak
    np.linspace(4.0, 7.9, 72),               # above threshold, below the tie
])
_d1201_exact = 20.0 * 3 * 5.0                # price x k x tie-level excess
R.check(
    "a mixed plateau is charged the exact billed top-k, not the leaked "
    "soft sum (#1210: no under-charge)",
    peak_cost(_d1201_mixed, np.zeros(96), PeakBilling(3.0, 20.0, 15, 0.25, 3, distinct_days=False))
    == _d1201_exact,
    f"charged {peak_cost(_d1201_mixed, np.zeros(96), PeakBilling(3.0, 20.0, 15, 0.25, 3, distinct_days=False)):.6f}"
    f" against the bill {_d1201_exact:.6f} (3 x 5 kW excess at 20/kW)",
)
# Null controls: the shapes that were already exact stay exact -- the pure
# plateau (every window at the tie) and the at-most-k-at-peak plan (hard
# branch both before and after).
R.check(
    "the pure plateau stays at the exact billed top-k",
    peak_cost(np.full(96, 12.0), np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False))
    == 720.0,
    f"charged {peak_cost(np.full(96, 12.0), np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)):.6f}",
)
R.check(
    "at most k windows at the peak stay on the exact hard sum",
    peak_cost(_d201_spiky, np.zeros(96), PeakBilling(0.0, 20.0, 15, 0.25, 3, distinct_days=False)) == 720.0,
    "hard top-k path: 3 x 12 kW at 20/kW = 720 exactly",
)
# The solver's surrogate on the same mixed cell: still smooth (that is its
# product, #232), and never above the exact charge -- the identity the
# finding states (weights sum to k, so soft <= hard) -- with the deficit
# bounded by the measured worst case (-3.45% on the round-5 grid).
_smooth_mixed = peak_cost_smooth(
    _d1201_mixed, np.zeros(96), PeakBilling(3.0, 20.0, 15, 0.25, 3, distinct_days=False)
)
R.check(
    "the solver's surrogate stays on the smooth arm and under the exact "
    "charge on the mixed plateau",
    _smooth_mixed < _d1201_exact
    and _smooth_mixed >= 0.95 * _d1201_exact,
    f"smooth={_smooth_mixed:.6f} against the exact {_d1201_exact:.6f} "
    f"(round-5 measured worst deficit 3.45%)",
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

# The piecewise cost of a draw (surplus-covered energy at the export price,
# the rest at the import price) is charged INLINE by the optimizer's
# `_energy_cost_fn` -- the old `pv.piecewise_cost` delegation target was
# dead and is gone (#226). The import margin is signed: an export price
# above the import price makes a self-consumed kWh cost more than an imported
# one, and flooring it at zero broke the piecewise identity there (R9
# D2-s3-02; the R9-F2.1 block pins both seams on it). The objective checks
# below pin the draw-side piecewise cases on the live inline.
_pw_prices = np.array([1.5, 1.5, 1.5])
_pw_surplus = np.array([0.0, 2.0, 5.0])
_pw_margin = pv.import_margin(_pw_prices, 0.3)
R.check(
    "the import margin is import minus export, signed",
    list(_pw_margin) == [1.2, 1.2, 1.2]
    and abs(float(pv.import_margin(np.array([0.2]), 0.9)[0]) + 0.7) < 1e-12,
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
_ranked = _dhw_planner(_pv_opt)._dhw_planning_prices(np.array([1.5, 1.5, 1.5]), 4.0)
R.check(
    "hot-water planning ranks a fully covered step at the export price",
    abs(_ranked[1] - 0.3) < 1e-9 and abs(_ranked[0] - 1.5) < 1e-9,
)
_ranked_shared = _dhw_planner(_pv_opt)._dhw_planning_prices(
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
    presence_entity="input_boolean.holiday",
    away_temperature=16.0,
)

# A real model, so the recovery estimate sees the slab bottleneck the old
# lumped formula ignored.
_away_model = ThermalModel(ThermalParameters())


def _away_house(current=16.0):
    return ThermalState(room_temperature=current, slab_temperature=current + 1.0)


def _away_estimate(house, model=_away_model, outdoor=0.0):
    """The coordinator's off-loop estimate, run inline: the job is the same."""
    async def estimate(target_temp):
        return away_mode.estimate_recovery_hours(model, house, target_temp, outdoor)
    return estimate


def _away_resolve(config, **kw):
    import asyncio as _away_aio
    return _away_aio.run(away_mode.resolve(config, **kw))


def resolve_away(now, return_at, current=16.0):
    return _away_resolve(
        AWAY_CFG,
        now=now,
        presence_raw="on",
        presence_attributes=None,
        return_raw=return_at,
        comfort_temp=21.0,
        estimate_recovery=_away_estimate(_away_house(current)),
    )


now = datetime(2026, 2, 10, 12, 0, tzinfo=UTC)
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
home = _away_resolve(
    AWAY_CFG,
    now=now,
    presence_raw="off",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    estimate_recovery=_away_estimate(_away_house(21.0)),
)
R.check("an occupied house is never set back", not home.active)

_now = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
_past = _now - timedelta(hours=1)
_future = _now + timedelta(hours=8)

R.check(
    "a past return expires the override",
    away_mode.expire_override(True, _past, _now) == (False, None),
)
R.check(
    "a future return leaves the override",
    away_mode.expire_override(True, _future, _now) == (True, _future),
)
R.check(
    "no return time does not expire",
    away_mode.expire_override(True, None, _now) == (True, None),
)

_person_home = _away_resolve(
    away_mode.AwayConfig(presence_entity="person.alice", away_temperature=16.0),
    now=_now,
    presence_raw="home",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    estimate_recovery=_away_estimate(_away_house()),
    override_active=True,
    override_return_time=_future,
)
R.check("the service override wins over a person at home", _person_home.active)
R.check("override source is service", _person_home.source == "service")

_person_only = _away_resolve(
    away_mode.AwayConfig(presence_entity="person.alice", away_temperature=16.0),
    now=_now,
    presence_raw="not_home",
    presence_attributes=None,
    return_raw=None,
    comfort_temp=21.0,
    estimate_recovery=_away_estimate(_away_house()),
    override_active=False,
    override_return_time=None,
)
R.check("person-away still works when the switch is off", _person_only.active)
R.check(
    "person-away source is the person entity",
    _person_only.source == "person.alice",
)

_mig = away_mode.migrate_helper_override(
    "input_boolean.holiday", "on", None, _future.isoformat()
)
R.check("boolean-on migrates to active", _mig["active"] is True)
R.check("boolean-on drops the presence key", _mig["drop_presence"] is True)
R.check("return helper is copied", _mig["return_time"] == _future.isoformat())
_mig_person = away_mode.migrate_helper_override(
    "person.alice", "not_home", None, None
)
R.check("a person id is not dropped", _mig_person["drop_presence"] is False)
R.check("a person id does not force the switch on", _mig_person["active"] is False)

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

cal = _away_resolve(
    away_mode.AwayConfig(presence_entity="calendar.holidays"),
    now=now,
    presence_raw="on",
    presence_attributes={"end_time": (now + timedelta(hours=1)).isoformat()},
    return_raw=None,
    comfort_temp=21.0,
    estimate_recovery=_away_estimate(_away_house()),
)
R.check(
    "a calendar event supplies its own return time",
    cal.return_time is not None and cal.recovery_active,
)

R.section("Two-hour boost overlays")
_boost_now = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
_boost_dhw = boost_mod.BoostState()
_boost_dhw.set("dhw", True, _boost_now)
R.check(
    "a DHW boost is live for two hours and then expires",
    _boost_dhw.active("dhw", _boost_now)
    and _boost_dhw.active("dhw", _boost_now + timedelta(hours=1, minutes=59))
    and not _boost_dhw.active("dhw", _boost_now + timedelta(hours=2))
    and not _boost_dhw.active("space", _boost_now),
)
_boost_dhw.expire(_boost_now + timedelta(hours=2))
R.check("expiry drops the channel", "dhw" not in _boost_dhw.until)
_boost_dhw.set("dhw", True, _boost_now)
_boost_space = boost_mod.BoostState()
_boost_space.set("space", True, _boost_now)
_dhw_action = {
    "power": 1.0,
    "dhw_power": 0.0,
    "dhw_heating_active": False,
    "heat_pump_on": False,
}
boost_mod.overlay(
    _dhw_action, _boost_dhw, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
R.check(
    "DHW boost maxes hot water without rewriting space power",
    _dhw_action["dhw_heating_active"] is True
    and abs(_dhw_action["dhw_power"] - 4.8) < 1e-9
    and _dhw_action["power"] == 1.0
    and _dhw_action["heat_pump_on"] is True,
    str(_dhw_action),
)
_space_action = {
    "power": 1.0,
    "dhw_power": 0.2,
    "dhw_heating_active": False,
    "heat_pump_on": False,
}
boost_mod.overlay(
    _space_action, _boost_space, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
# #1499: a DHW boost turns the pump on, so a plan step that said "off" (or
# no plan, "idle") must not keep publishing that the pump is off.
_dhw_off_action = {"power": 0.0, "mode": "off", "heat_pump_on": False}
boost_mod.overlay(
    _dhw_off_action, _boost_dhw, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
_dhw_eco_action = {"power": 1.0, "mode": "eco", "heat_pump_on": True}
boost_mod.overlay(
    _dhw_eco_action, _boost_dhw, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
R.check(
    "a DHW boost over an off step reads hot_water; over a space step, the space rung",
    _dhw_off_action["mode"] == "hot_water" and _dhw_eco_action["mode"] == "eco",
    f"{_dhw_off_action['mode']} / {_dhw_eco_action['mode']}",
)
R.check(
    "space boost maxes space heat without rewriting DHW power",
    _space_action["power"] == 6.0
    and _space_action["setpoint"] == 24.0
    and _space_action["displace_value"] == 8.0
    and _space_action["dhw_power"] == 0.2
    and _space_action["heat_pump_on"] is True,
    str(_space_action),
)

# Block switches: the opposite overlay. With no block set the action's keys
# are the plan's keys (null control for the value-bearing goldens).
_block_base = {
    "power": 1.2,
    "dhw_power": 0.4,
    "dhw_heating_active": True,
    "heat_pump_on": True,
    "mode": "normal",
    "power_normalized": 0.3,
}
_block_plain = dict(_block_base)
_block_held_off = boost_mod.BoostState()
boost_mod.overlay(
    _block_plain, _block_held_off, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
R.check(
    "with no block set the overlay adds no key and changes no value",
    _block_plain == _block_base,
    str(_block_plain),
)
_block_space_held = boost_mod.BoostState()
_block_space_held.set("space", True, _boost_now, block=True)
_block_space_action = dict(_block_base)
boost_mod.overlay(
    _block_space_action, _block_space_held, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
_block_dhw_held = boost_mod.BoostState()
_block_dhw_held.set("dhw", True, _boost_now, block=True)
_block_dhw_action = dict(_block_base)
boost_mod.overlay(
    _block_dhw_action, _block_dhw_held, max_power=6.0, max_temp=24.0, ecl_max=8.0,
)
R.check(
    "a space block zeroes space power and leaves the supply switch and DHW alone",
    _block_space_action["power"] == 0.0
    and _block_space_action["power_normalized"] == 0.0
    and _block_space_action["heat_pump_on"] is True
    and _block_space_action["dhw_power"] == 0.4
    and set(_block_space_action) == set(_block_base),
    str(_block_space_action),
)
R.check(
    "a DHW block zeroes hot water and leaves space power and the supply switch",
    _block_dhw_action["dhw_power"] == 0.0
    and _block_dhw_action["dhw_heating_active"] is False
    and _block_dhw_action["power"] == 1.2
    and _block_dhw_action["heat_pump_on"] is True
    and set(_block_dhw_action) == set(_block_base),
    str(_block_dhw_action),
)
_block_excl = boost_mod.BoostState()
_block_excl.set("dhw", True, _boost_now)
_block_excl.set("dhw", True, _boost_now, block=True)
_block_back = boost_mod.BoostState()
_block_back.set("space", True, _boost_now, block=True)
_block_back.set("space", True, _boost_now)
_block_swap = boost_mod.BoostState()
_block_swap.set("space", True, _boost_now)
_block_swap.set("space", True, _boost_now, block=True)
R.check(
    "the later press wins: a block clears that channel's boost, and the reverse",
    _block_excl.until == {}
    and "dhw" in _block_excl.blocked
    and _block_excl.space_settle_until is None
    and _block_back.blocked == {}
    and "space" in _block_back.until
    and _block_swap.until == {}
    and "space" in _block_swap.blocked
    and _block_swap.space_settle_until is not None,
    f"{_block_excl.until} {_block_excl.blocked} {_block_back.until} {_block_back.blocked} "
    f"settle {_block_swap.space_settle_until}",
)
_block_life = boost_mod.BoostState()
_block_life.set("space", True, _boost_now, block=True)
R.check(
    "a block lasts BLOCK_HOURS and then expires",
    _block_life.block_active("space", _boost_now)
    and _block_life.block_active(
        "space", _boost_now + timedelta(hours=boost_mod.BLOCK_HOURS) - timedelta(seconds=1)
    )
    and not _block_life.block_active(
        "space", _boost_now + timedelta(hours=boost_mod.BLOCK_HOURS)
    )
    and boost_mod.BLOCK_HOURS == 2,
)
_block_life.expire(_boost_now + timedelta(hours=boost_mod.BLOCK_HOURS))
R.check("block expiry drops the channel", "space" not in _block_life.blocked)


class _BlockFloorCoord:
    def __init__(self, snap, data=None):
        self._snap = snap
        self.data = data or {}
        self.hass = FakeHass()
        self._current_action = {}

    def arbiter_inputs(self):
        return self._snap

    def adopt_action(self, action):
        self._current_action = action


from types import SimpleNamespace


def _block_floor_snap(**kw):
    return _r9f13_arb.ArbiterInputs(
        hass=None,
        config={},
        mode=kw.get("mode", "auto"),
        plan=kw.get("plan"),
        plan_stale=kw.get("stale", False),
        entry_released=False,
        state=kw.get("state") or SimpleNamespace(),
        thermal=None,
        params=kw.get("params") or SimpleNamespace(),
        action=kw.get("action") or {},
        measured_power_kw=None,
        disinfecting=kw.get("disinfecting", False),
    )


_block_noon = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
_block_warm = SimpleNamespace(
    room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=50.0,
)
_block_params = SimpleNamespace(dhw_min_temp=40.0, dhw_demand_windows=[])
_block_none = _block_floor_snap(state=_block_warm, params=_block_params)
R.check(
    "no safety floor is a reason to release a block",
    boost_mod.block_release_reason(
        _BlockFloorCoord(_block_none), "dhw", _block_noon, _block_none
    ) is None
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_none), "space", _block_noon, _block_none
    ) is None,
)
_block_due = _BlockFloorCoord(
    _block_none,
    data={"dhw_legionella_due_in_hours": -2.0, "horizon_hours": 24.0},
)
_block_hold = _block_floor_snap(
    state=_block_warm, params=_block_params, disinfecting=True,
)
_block_soon = _BlockFloorCoord(
    _block_none, data={"dhw_legionella_due_in_hours": 10.0, "horizon_hours": 24.0},
)
_block_far = _BlockFloorCoord(
    _block_none, data={"dhw_legionella_due_in_hours": 100.0, "horizon_hours": 24.0},
)
_block_horizon = _BlockFloorCoord(
    _block_none, data={"dhw_legionella_due_in_hours": 24.0, "horizon_hours": 24.0},
)
R.check(
    "a due, overdue or live disinfection hold releases a DHW block",
    boost_mod.block_release_reason(_block_due, "dhw", _block_noon) == boost_mod.RELEASE_LEGIONELLA
    and boost_mod.block_release_reason(_block_soon, "dhw", _block_noon) == boost_mod.RELEASE_LEGIONELLA
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_hold), "dhw", _block_noon, _block_hold
    ) == boost_mod.RELEASE_DISINFECTION
    and boost_mod.block_release_reason(_block_far, "dhw", _block_noon) is None
    and boost_mod.block_release_reason(_block_horizon, "dhw", _block_noon) is None,
)
from heatpump_optimizer.dhw_schedule import parse_windows as _block_windows
_block_tank_params = SimpleNamespace(
    dhw_min_temp=45.0, dhw_demand_windows=_block_windows("00:00-23:59"),
)
_block_tank_state = SimpleNamespace(
    room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=45.0,
)
_block_tank = _block_floor_snap(state=_block_tank_state, params=_block_tank_params)
_block_tank_warm = _block_floor_snap(
    state=SimpleNamespace(
        room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=46.0,
    ),
    params=_block_tank_params,
)
R.check(
    "the tank at dhw_min_temp inside a demand window releases a DHW block",
    boost_mod.block_release_reason(
        _BlockFloorCoord(_block_tank), "dhw", _block_noon, _block_tank
    ) == boost_mod.RELEASE_TANK
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_tank_warm), "dhw", _block_noon, _block_tank_warm
    ) is None,
)
_block_room = _block_floor_snap(
    state=SimpleNamespace(room_temperature=15.0, outdoor_temperature=5.0),
    params=_block_params,
)
_block_room_ok = _block_floor_snap(
    state=SimpleNamespace(room_temperature=16.0, outdoor_temperature=5.0),
    params=_block_params,
)
from heatpump_optimizer.const import (  # noqa: E402
    ECONOMY_ABSOLUTE_FLOOR as _BLOCK_ROOM_FLOOR,
    SPACE_PUMP_FLOOR_MARGIN_C as _BLOCK_ROOM_MARGIN,
)
_block_room_at = _BLOCK_ROOM_FLOOR + _BLOCK_ROOM_MARGIN
_block_room_edge = _block_floor_snap(
    state=SimpleNamespace(room_temperature=_block_room_at, outdoor_temperature=5.0),
    params=_block_params,
)
_block_room_above = _block_floor_snap(
    state=SimpleNamespace(
        room_temperature=_block_room_at + 0.1, outdoor_temperature=5.0,
    ),
    params=_block_params,
)
_block_cold_plan = SimpleNamespace(
    timestamps=[_block_noon], optimal_setpoints=[21.0], predictive_info={},
)
_block_cold = _block_floor_snap(
    state=SimpleNamespace(room_temperature=18.0, outdoor_temperature=-11.0),
    params=_block_params,
    plan=_block_cold_plan,
)
_block_cold_warm = _block_floor_snap(
    state=SimpleNamespace(room_temperature=21.0, outdoor_temperature=-11.0),
    params=_block_params,
    plan=_block_cold_plan,
)
R.check(
    "the room floor and the cold-rail lease release a space block",
    boost_mod.block_release_reason(
        _BlockFloorCoord(_block_room), "space", _block_noon, _block_room
    ) == boost_mod.RELEASE_ROOM
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_room_ok), "space", _block_noon, _block_room_ok
    ) is None
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_room_edge), "space", _block_noon, _block_room_edge
    ) == boost_mod.RELEASE_ROOM
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_room_above), "space", _block_noon, _block_room_above
    ) is None
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_cold), "space", _block_noon, _block_cold
    ) == boost_mod.RELEASE_COLD
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_cold_warm), "space", _block_noon, _block_cold_warm
    ) is None,
)
_block_sys = _block_floor_snap(
    state=_block_warm, params=_block_params,
    action={"mode": "system_identification"},
)
_block_stale_snap = _block_floor_snap(
    state=_block_warm, params=_block_params, stale=True,
)
R.check(
    "a measurement experiment and a stale plan release either block",
    boost_mod.block_release_reason(
        _BlockFloorCoord(_block_sys), "space", _block_noon, _block_sys
    ) == boost_mod.RELEASE_SYSID
    and boost_mod.block_release_reason(
        _BlockFloorCoord(_block_stale_snap), "dhw", _block_noon, _block_stale_snap
    ) == boost_mod.RELEASE_STALE,
)
_block_apply_base = {"power": 1.0, "dhw_power": 0.5, "heat_pump_on": True, "mode": "normal"}
_block_apply = _BlockFloorCoord(
    _block_none,
    data={"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0, "dhw_enabled": True},
)
boost_mod.adopt_plan(_block_apply, dict(_block_apply_base))
boost_mod.held_for(_block_apply).set("dhw", True, _block_noon, block=True)
boost_mod.apply(_block_apply, boost_mod.BoostOverlay(6.0, 24.0, 8.0))
R.check(
    "a due anti-legionella cycle releases the block before the overlay zeroes it",
    "dhw" not in boost_mod.held_for(_block_apply).blocked
    and _block_apply._current_action["dhw_power"] == 0.5
    and _block_apply._current_action["heat_pump_on"] is True,
    str(_block_apply._current_action),
)
from heatpump_optimizer import switch as _block_switch  # noqa: E402
_block_why_coord = _BlockFloorCoord(
    _block_none,
    data={"dhw_legionella_due_in_hours": 1.0, "horizon_hours": 24.0, "dhw_enabled": True},
)
_block_why = _block_switch.BlockDhwSwitch(
    _block_why_coord, SimpleNamespace(entry_id="block-why"),
)
_r9f13_aio.run(boost_mod.set_block(_block_why_coord, "dhw", True, refresh=False))
R.check(
    "a due cycle refuses the block press and the switch says why",
    not _block_why.is_on
    and "dhw" not in boost_mod.held_for(_block_why_coord).blocked
    and _block_why.extra_state_attributes == {
        "block_release": boost_mod.RELEASE_LEGIONELLA,
    },
    f"on={_block_why.is_on} attrs={_block_why.extra_state_attributes}",
)


class _BlockMemStore:
    saved: list = []
    payload: Any = None

    def __init__(self, *a, **k):
        pass

    async def async_save(self, data):
        _BlockMemStore.saved.append(data)

    async def async_load(self):
        return _BlockMemStore.payload


class _BlockStoreCoord:
    def __init__(self, entry_id):
        self.hass = FakeHass()
        self.entry = SimpleNamespace(entry_id=entry_id)


_block_store_coord = _BlockStoreCoord("block")
_block_real_store = boost_mod.QuarantiningStore
try:
    boost_mod.QuarantiningStore = _BlockMemStore
    _BlockMemStore.saved = []
    boost_mod.held_for(_block_store_coord).until.clear()
    boost_mod.held_for(_block_store_coord).blocked.clear()
    boost_mod.held_for(_block_store_coord).set("dhw", True, _block_noon)
    _r9f13_aio.run(boost_mod.persist(_block_store_coord))
    _block_boost_only = dict(_BlockMemStore.saved[-1])
    boost_mod.held_for(_block_store_coord).set("space", True, _block_noon, block=True)
    _r9f13_aio.run(boost_mod.persist(_block_store_coord))
    _block_with = dict(_BlockMemStore.saved[-1])
    _block_clock = datetime.now(UTC)
    _BlockMemStore.payload = {
        "block_dhw": {"until": (_block_clock + timedelta(hours=1)).isoformat()},
        "block_space": {"until": (_block_clock - timedelta(hours=1)).isoformat()},
        "dhw": {"until": (_block_clock + timedelta(hours=1)).isoformat()},
    }
    _block_loaded = _BlockStoreCoord("block2")
    _r9f13_aio.run(boost_mod.restore(_block_loaded))
    _block_loaded_held = boost_mod.held_for(_block_loaded)
finally:
    boost_mod.QuarantiningStore = _block_real_store
R.check(
    "a boost-only store gains no block key, and restore keeps a live block only",
    "block_dhw" not in _block_boost_only
    and "block_space" not in _block_boost_only
    and set(_block_with) >= {"dhw", "block_space"}
    and set(_block_loaded_held.blocked) == {"dhw"}
    and "space" not in _block_loaded_held.blocked,
    f"boost-only {sorted(_block_boost_only)} with {sorted(_block_with)} "
    f"restored {sorted(_block_loaded_held.blocked)}",
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

# The factor is a function of two continuous inputs -- outdoor temperature and
# relative humidity -- so it must not step at a bucket edge (R6-D2-01 / #1381):
# a fully-earned duty folded into one bucket must not make the COP every plan
# prices through jump by a whole derate across a 1e-9 change in either input.
_cont = DefrostDerate()
for _ in range(200):
    _cont.observe_duty(1.0, 90.0, 0.30)  # fully-earned measured duty, bucket (2, 1)
R.check(
    "the derate factor is continuous across a temperature bucket edge",
    abs(_cont.factor(1e-9, 90.0) - _cont.factor(-1e-9, 90.0)) < 1e-6,
    f"step {abs(_cont.factor(1e-9, 90.0) - _cont.factor(-1e-9, 90.0)):.6f} at 0 C",
)
R.check(
    "the derate factor is continuous across a humidity bucket edge",
    abs(_cont.factor(1.0, 70.0 + 1e-9) - _cont.factor(1.0, 70.0 - 1e-9)) < 1e-6,
    f"step {abs(_cont.factor(1.0, 70.0 + 1e-9) - _cont.factor(1.0, 70.0 - 1e-9)):.6f} "
    f"at 70 % RH",
)
R.check(
    "and continuity is reached by interpolation, not by disabling the derate",
    _cont.factor(1.0, 90.0) < 0.6,
    f"factor {_cont.factor(1.0, 90.0):.4f} — the learned bucket must still derate",
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

# The solver's batched gradient re-walks the same forecast steps for every
# one of the 544 k batched evaluations a solve costs, so `factor` is asked
# the same handful of exact (temperature, humidity) pairs tens of millions
# of times per solve, and the learner's grids change only in observe /
# observe_duty -- between learns the answer for a given pair cannot move,
# so a memo on the learner returns the identical float. This section pins
# the three properties that make that memo honest: repeats do not
# re-decide, every answer stays bit-identical to the uncached one, and a
# learn invalidates what it changed.
_memo_learner = DefrostDerate()
for _ in range(200):
    _memo_learner.observe_duty(1.0, 90.0, 0.30)
_memo_learner.observe(3.0, 80.0, 0.75)
_decide_calls = [0]
_uncached_decide = _memo_learner._decide


def _counting_decide(*args, **kwargs):
    _decide_calls[0] += 1
    return _uncached_decide(*args, **kwargs)


_memo_learner._decide = _counting_decide
_memo_learner.factor(1.0, 87.5)  # the first sight pays the interpolation once
_decide_calls[0] = 0
for _ in range(1000):
    _memo_learner.factor(1.0, 87.5)
_per_repeat = _decide_calls[0] / 1000
_decide_calls[0] = 0
for _pair in ((2.5, 87.5), (1.0, 30.0), (17.0, 99.0)):
    _memo_learner.factor(*_pair)
_first_sights = _decide_calls[0]
_memo_learner._decide = _uncached_decide
R.check(
    "a repeated (temperature, humidity) pair is not re-decided",
    _per_repeat == 0.0,
    f"{_per_repeat:.1f} four-bucket interpolations per repeat -- a solve "
    "pays these tens of millions of times for pairs that cannot have "
    "changed between the calls",
)
R.check(
    "a first sight of a pair still decides it once",
    _first_sights == 12,
    f"{_first_sights} _decide calls for 3 fresh pairs -- exactly the four "
    "surrounding buckets each, no more",
)

# Bit-identity, not closeness: a memo hit must equal what the unchanged
# computation produces for the SAME conditions, read straight off
# `_factor_uncached` -- comparing two memoized learners would let a
# conflated key (a bucket-rounded pair standing in for the exact floats)
# be wrong identically on both sides. Sampled over the whole plane
# including the bucket edges, where an interpolation weight is exactly 0
# or 1 and a conflated key would show, with the repeat interleaved so a
# hit is exercised everywhere.
_plane_mismatch = 0
_plane_points = 0
for _t in (-35.0, -12.5, -2.5, -1e-9, 0.0, 1e-9, 1.0, 2.0, 3.5, 5.0,
           5.0 + 1e-9, 8.0, 24.0, 40.0, 41.0):
    for _h in (-1.0, 0.0, 35.0, 69.999999, 70.0, 70.0 + 1e-9, 85.5,
               100.0, 101.0, None):
        _hn = HUMIDITY_CENTERS[0] if _h is None else _h
        _plane_points += 1
        _a = _memo_learner.factor(_t, _h)
        _oracle = _memo_learner._factor_uncached(_t, _hn)
        _a2 = _memo_learner.factor(_t, _h)  # the second call is a memo hit
        if _a != _oracle or repr(_a) != repr(_oracle) or _a2 != _oracle:
            _plane_mismatch += 1
R.check(
    "the memoized factor is bit-identical to the uncached one everywhere",
    _plane_mismatch == 0,
    f"{_plane_mismatch} of {_plane_points} sampled conditions disagree, "
    "including bucket edges -- a memo may never change a value by one float",
)

# A learn invalidates: the next call must answer from the new grids, not
# from what the pair cached before the observation. Each mutator is
# checked on its own, so retiring the wrong one cannot hide behind the
# other. The stale answer is read BEFORE the learn and must differ after.
_inval = DefrostDerate()
for _ in range(200):
    _inval.observe_duty(1.0, 90.0, 0.30)
_stale_duty = _inval.factor(1.0, 90.0)
_inval.observe_duty(1.0, 90.0, 0.0)
_after_duty = _inval.factor(1.0, 90.0)
_inval.observe(1.0, 90.0, 0.55)
_after_both = _inval.factor(1.0, 90.0)
_recomputed = DefrostDerate.from_dict(_inval.as_dict()).factor(1.0, 90.0)
R.check(
    "an observation invalidates the memoized answer",
    _after_duty != _stale_duty
    and _after_both == _recomputed
    and _after_both < 0.99,
    f"before the learn {_stale_duty!r}, after the duty learn "
    f"{_after_duty!r}, after the ratio learn {_after_both!r} against "
    f"{_recomputed!r} from a fresh learner of the same state -- each "
    "learn must retire what it changed",
)

# The memo is capped, not unbounded: a coordinator lives for months and
# floats accumulate, so past the cap it must clear (costing recompute,
# never a value) and still answer bit-identically afterwards.
_cap = DefrostDerate()
for _ in range(200):
    _cap.observe_duty(1.0, 90.0, 0.30)
_cap.factor(1.0, 90.0)  # cached while the memo is young
for _i in range(20000):
    _cap.factor(-30.0 + _i * 0.01, 85.0)  # far past the cap: a clear fires
_cap_answer = _cap.factor(1.0, 90.0)
_cap_fresh = DefrostDerate.from_dict(_cap.as_dict()).factor(1.0, 90.0)
R.check(
    "the memo survives its own bound without changing a value",
    _cap_answer == _cap_fresh,
    f"after 20000 distinct pairs the answer is {_cap_answer!r} against "
    f"{_cap_fresh!r} from a fresh learner -- a clear may cost recompute, "
    "never a value",
)
R.check(
    "the memo is actually bounded",
    len(_cap._factor_memo) < 20000,
    f"{len(_cap._factor_memo)} entries cached after 20000 distinct pairs "
    "-- a coordinator lives for months; the cap is what keeps the cache "
    "from growing with the weather",
)
# And the bound is EXACT, read off one full turn of the cycle: a fresh
# learner asked 8202 distinct pairs ends with 10 entries -- the cap
# cleared once at 8192 and refilled. The number is hardcoded on purpose:
# a cap moved by one (>= to >) ends at 9, a doubled cap at 8202, and
# deriving the expectation from the module's own constant would inherit
# either mutation. It is the cap's VALUE the plan's memory ceiling rests
# on, so it is pinned by arithmetic, not by import.
_exact = DefrostDerate()
for _i in range(8202):
    _exact.factor(-40.0 + _i * 0.01, 85.0)
R.check(
    "the memo's cap is 8192 exactly, one entry past it clears",
    len(_exact._factor_memo) == 10,
    f"{len(_exact._factor_memo)} entries after 8202 stores -- 10 says the "
    "cycle is exactly (8202 - 1) mod 8192 + 1; a bound moved by one says "
    "9, a doubled cap says 8202",
)

# The uniform-shortcut in the factor's law (all four surrounding buckets
# agree -> return that value) is a BIT-IDENTITY guarantee, not an
# optimisation: the four-weight sum it skips returns 1.0 x weights, and
# the weights sum to 1 only in exact arithmetic -- in floats the sum
# differs from 1.0 at roughly one sampled pair in thirty (measured: 3379
# of 100000), which would perturb every empty-learner plan's COP by
# ~1e-16. A deterministic sweep pins that the data-less derate is inert
# to the last bit across the plane, memo hit or miss.
_shortcut = DefrostDerate()
_shortcut_bad = 0
for _i in range(2000):
    _st = -35.0 + _i * 0.037
    _sh = (_i * 37 % 102) - 0.5
    if _shortcut.factor(_st, _sh) != 1.0:
        _shortcut_bad += 1
    if _shortcut.factor(_st, _sh) != 1.0:  # the repeat is a memo hit
        _shortcut_bad += 1
R.check(
    "an empty learner's derate is exactly 1.0 across the plane",
    _shortcut_bad == 0,
    f"{_shortcut_bad} of 4000 sampled answers (hit and miss alike) left "
    "1.0 -- the uniform shortcut is what keeps a data-less derate inert "
    "to the last bit, not a speed choice",
)


# ===========================================================================
# Weekly DHW windows: different days, different windows (owner request #3)
# ===========================================================================
R.section("Weekly hot-water windows: different days, different times")

from datetime import datetime as _WDT
from profiles import house as _grad_house, prices as _grad_prices, weather as _grad_weather
from heatpump_optimizer.dhw_schedule import (
    parse_windows as _parse_w,
    parse_weekly_windows as _pw,
    format_weekly_windows as _fw,
    windows_for_day as _wfd,
    is_valid_spec as _ivs,
)

def _try_exc(fn):
    """Run fn(); return the exception it raised, or None."""
    try:
        fn()
        return None
    except Exception as err:  # noqa: BLE001
        return err

# The flat spec every install has is unchanged: no weekly structure, the
# every-day view is the only one.
R.check(
    "a flat spec carries no weekly structure",
    _pw("06:00-08:30, 17:00-22:00") is None,
    "the weekly view must be opt-in, or every existing install pays for it",
)
_wk = _pw("weekdays 06:00-08:30, weekend 08:00-09:30")
R.check(
    "the weekday/weekend split lands on the right days",
    _wk is not None
    and all(_wk[d] == [(6.0, 8.5)] for d in range(5))
    and _wk[5] == [(8.0, 9.5)]
    and _wk[6] == [(8.0, 9.5)],
    str(_wk),
)
R.check(
    "and renders back to the string the user typed",
    _fw(_wk) == "weekdays 06:00-08:30, weekend 08:00-09:30",
    _fw(_wk),
)
_wk2 = _pw("Mo 05:30-07:00, Tu-Fr 06:00-08:00, Sa,Su 08:00-09:30")
R.check(
    "single days and day lists name exactly their own days",
    _wk2 is not None
    and _wk2[0] == [(5.5, 7.0)]
    and all(_wk2[d] == [(6.0, 8.0)] for d in (1, 2, 3, 4))
    and _wk2[5] == [(8.0, 9.5)],
    str(_wk2),
)
R.check(
    "the rendered form re-parses to the same structure",
    _pw(_fw(_wk2)) == _wk2,
    _fw(_wk2),
)
R.check(
    "a dayless segment inside a weekly spec applies to every day",
    _pw("weekdays 06:00-07:00, 18:00-19:00")[5] == [(18.0, 19.0)],
    "same reading the flat grammar gives a bare range",
)
R.check(
    "a wrapping weekly window splits at midnight like the flat one",
    _pw("weekend 22:00-06:00")[5] == [(0.0, 6.0), (22.0, 24.0)],
    str(_pw("weekend 22:00-06:00")[5]),
)
R.check(
    "a day with no segment has no windows -- no requirement that day",
    not _pw("Mo 06:00-07:00")[2],
    "an empty day is the point: Tuesday genuinely needs no hot water",
)
for _bad in ("Mo 25:00-26:00", "weekdays", "Mox 06:00-07:00"):
    R.check(
        f"a malformed weekly spec raises, not silently empties ({_bad!r})",
        isinstance(_try_exc(lambda: _pw(_bad)), Exception),
        "",
    )
R.check(
    "the validator accepts the weekly grammar",
    _ivs("weekdays 06:00-08:30, weekend 08:00-09:30")
    and not _ivs("Mo 99:00-07:00"),
    "",
)
_flat_view = _parse_w("weekdays 06:00-08:30, weekend 08:00-09:30")
R.check(
    "the every-day view of a weekly spec is the merged union of its times",
    _flat_view == [(6.0, 9.5)],
    f"{_flat_view}",
)

# The countdown the optimizer publishes as `dhw_next_window_in_hours` and the
# VVC pump reads through pump_schedule. Every golden solve starts at 00:00,
# outside every window, so the inside-a-window answer is never computed there:
# without a direct check, "0.0 while inside" lives only in the docstring.
from heatpump_optimizer.dhw_schedule import hours_until_next_window as _hunw

_hunw_windows = _parse_w("06:00-08:30, 17:00-22:00")
R.check(
    "inside a demand window the next window is now, not the following one",
    _hunw(7.0, _hunw_windows) == 0.0 and _hunw(18.0, _hunw_windows) == 0.0,
    f"07:00 -> {_hunw(7.0, _hunw_windows)}, 18:00 -> {_hunw(18.0, _hunw_windows)} "
    "-- reading the FOLLOWING window while inside one pre-heats for a tank "
    "that is already being drawn",
)
R.check(
    "outside one it counts the hours to the next opening, wrapping past midnight",
    _hunw(5.0, _hunw_windows) == 1.0
    and _hunw(9.0, _hunw_windows) == 8.0
    and _hunw(23.0, _hunw_windows) == 7.0,
    f"05:00 -> {_hunw(5.0, _hunw_windows)}, 09:00 -> {_hunw(9.0, _hunw_windows)}, "
    f"23:00 -> {_hunw(23.0, _hunw_windows)}",
)
R.check(
    "with no windows configured there is no answer, which is not 'now'",
    _hunw(7.0, []) is None,
    f"got {_hunw(7.0, [])}",
)


# --- #329/#321: one grammar, exhaustively ----------------------------------
# The renderer used to emit what its own first loader rejected. Both issues
# are that one fact seen from two sides: `_raw_windows` split the spec on
# every comma before any day selector was recognised, while the weekly
# parser reassembled a selector's comma -- so the two disagreed on exactly
# the comma-list selectors `_format_day_selector` PREFERS. A canonicalised
# weekly schedule (apply_schedule stores `format_weekly_windows` output) came
# back at the next load as a WARNING and no schedule at all; a service call
# carrying one was acknowledged and dropped.
#
# So the deliverable is a property, not a patch per corner, and it is
# enumerated over the WHOLE space -- all 127 non-empty day-sets, times chosen
# to cover one range, several ranges, a range that wraps midnight, one of
# exactly MIN_WINDOW_MINUTES, and the full day. Sampling would have missed
# the multi-range half: the second range of a day-group used to be rendered
# bare, and a bare range in a weekly spec means all seven days, so Wednesday
# inherited Monday's evening window.
R.section("The window grammar round-trips: renderer out, every loader in")

import itertools as _rt_it
from heatpump_optimizer.dhw_schedule import (
    DHWWindowError as _rt_err,
    spec_problem as _rt_problem,
)

_RT_DAYS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
#: Times chosen for what they do to the GRAMMAR, not for realism: a single
#: range, two ranges in one group, a wrapping range (which normalises to two),
#: the shortest window the form accepts, the full day, and three ranges.
_RT_TIMES = (
    "06:00-07:00",
    "06:00-08:30, 17:00-22:00",
    "22:00-06:00",
    "06:00-06:15",
    "00:00-00:00",
    "05:00-06:00, 12:00-13:00, 18:00-19:30",
)


def _rt_day_sets():
    """Every non-empty subset of the week, all 127 of them. No sampling."""
    for size in range(1, 8):
        for combo in _rt_it.combinations(range(7), size):
            yield list(combo)


def _rt_weekly(days, times):
    """The seven-day structure that puts `times` on `days` and nothing else."""
    wins = _parse_w(times)
    return [list(wins) if d in days else [] for d in range(7)]


def _rt_effective(spec):
    """The seven per-day window lists PRODUCTION applies to `spec`.

    Exactly what the optimizer sees: the weekly structure when there is one,
    the flat every-day view when there is not -- `windows_for_day`'s own
    contract, so this is behaviour and not representation.
    """
    return [_wfd(_pw(spec), d, _parse_w(spec)) for d in range(7)]


def _rt_raises(fn, spec):
    """The DHWWindowError `fn(spec)` raises, or None when it accepts."""
    try:
        fn(spec)
        return None
    except _rt_err as err:
        return err


_rt_cells = [
    (days, times, _fw(_rt_weekly(days, times)))
    for days in _rt_day_sets()
    for times in _RT_TIMES
]
R.check(
    "the property covers the whole day-set space, not a sample",
    len(list(_rt_day_sets())) == 127 and len(_rt_cells) == 127 * len(_RT_TIMES),
    f"{len(list(_rt_day_sets()))} day-sets, {len(_rt_cells)} cells",
)

# Two behaviours the shared segmenter and the per-range renderer had to carry
# across unchanged, and that nothing pinned before: the every-day form stays
# the bare string every existing install has stored (apply_schedule writes
# this value straight into options, so a gratuitous "daily " prefix would
# rewrite every one of them), and ";" and a newline separate segments for
# BOTH parsers, exactly as the module docstring promises.
R.check(
    "a schedule identical on all seven days renders as the flat spec it was",
    _fw([[(6.0, 8.5), (17.0, 22.0)] for _ in range(7)])
    == "06:00-08:30, 17:00-22:00"
    and _fw([[(6.0, 7.0)] for _ in range(7)]) == "06:00-07:00",
    f"{_fw([[(6.0, 8.5), (17.0, 22.0)] for _ in range(7)])!r}",
)
def _rt_val(fn, spec):
    """`fn(spec)`, or the error it raised -- so a check FAILs and never crashes."""
    try:
        return fn(spec)
    except _rt_err as err:
        return err


R.check(
    "';' and a newline separate segments for both parsers, as documented",
    _rt_val(_parse_w, "06:00-07:00; 18:00-19:00") == [(6.0, 7.0), (18.0, 19.0)]
    and _rt_val(_parse_w, "Mo 06:00-07:00\nTu 18:00-19:00")
    == [(6.0, 7.0), (18.0, 19.0)]
    and _rt_val(_pw, "Mo 06:00-07:00; Tu 18:00-19:00")
    == [[(6.0, 7.0)], [(18.0, 19.0)], [], [], [], [], []],
    f"{_rt_val(_parse_w, '06:00-07:00; 18:00-19:00')!r} / "
    f"{_rt_val(_pw, 'Mo 06:00-07:00; Tu 18:00-19:00')!r}",
)

_rt_bad = {k: [] for k in ("flat", "weekly", "valid", "problem", "stable", "fix")}
for _rt_d, _rt_t, _rt_c in _rt_cells:
    # Every property is judged on every cell: short-circuiting on the first
    # failure would have flattered the counts by two thirds.
    _rt_ef = _rt_raises(_parse_w, _rt_c)
    _rt_ew = _rt_raises(_pw, _rt_c)
    if _rt_ef is not None:
        _rt_bad["flat"].append((_rt_c, str(_rt_ef)))
    if _rt_ew is not None:
        _rt_bad["weekly"].append((_rt_c, str(_rt_ew)))
    if not _ivs(_rt_c):
        _rt_bad["valid"].append((_rt_c, "is_valid_spec said False"))
    if _rt_problem(_rt_c) is not None:
        _rt_bad["problem"].append((_rt_c, f"spec_problem {_rt_problem(_rt_c)!r}"))
    if _rt_ef is not None or _rt_ew is not None:
        _rt_bad["stable"].append((_rt_c, "unloadable, so unstable"))
        _rt_bad["fix"].append((_rt_c, "unloadable, so no fixpoint"))
        continue
    _rt_e = _rt_effective(_rt_c)
    if _rt_e != _rt_weekly(_rt_d, _rt_t):
        _rt_bad["stable"].append((_rt_c, f"{_rt_e} != {_rt_weekly(_rt_d, _rt_t)}"))
    if _fw(_rt_e) != _rt_c:
        _rt_bad["fix"].append((_rt_c, f"{_fw(_rt_e)!r} != {_rt_c!r}"))


def _rt_check(name, key):
    bad = _rt_bad[key]
    R.check(
        f"{name} ({len(_rt_cells) - len(bad)}/{len(_rt_cells)})",
        not bad,
        f"{len(bad)} failed: "
        + "; ".join(f"{c!r}: {why}" for c, why in bad[:3]),
    )


# (1) Loadable: every loader production runs on a stored spec.
_rt_check("parse_windows accepts every string the renderer emits", "flat")
_rt_check("parse_weekly_windows accepts every string the renderer emits", "weekly")
_rt_check("is_valid_spec accepts every string the renderer emits", "valid")
_rt_check("spec_problem finds no problem in one", "problem")
# (2) Stable: parse -> format -> parse is the same schedule, and a fixpoint.
_rt_check("the rendered spec re-parses to the days it was rendered from", "stable")
_rt_check("and rendering it again changes nothing", "fix")

# (3) The two parsers accept the same strings -- the invariant #321 broke on
# the write side. The corpus is the canonical form plus the two forms a human
# or the dashboard card would type for the same schedule.
_rt_corpus = set()
for _rt_d, _rt_t in ((d, t) for d in _rt_day_sets() for t in _RT_TIMES):
    _rt_r = [r.strip() for r in _rt_t.split(",")]
    _rt_corpus.add(_fw(_rt_weekly(_rt_d, _rt_t)))
    _rt_corpus.add(", ".join(f"{_RT_DAYS[d]} {r}" for d in _rt_d for r in _rt_r))
    _rt_corpus.add(f"{','.join(_RT_DAYS[d] for d in _rt_d)} {_rt_t}")
for _rt_t in _RT_TIMES:
    _rt_corpus.update(
        (_rt_t, f"daily {_rt_t}", f"weekdays {_rt_t}", f"weekend {_rt_t}")
    )
_rt_corpus = sorted(_rt_corpus)
_rt_split = [
    (s, f"parse_windows={'accepts' if a is None else a}, "
        f"parse_weekly_windows={'accepts' if b is None else b}")
    for s, a, b in (
        (s, _rt_raises(_parse_w, s), _rt_raises(_pw, s)) for s in _rt_corpus
    )
    if (a is None) != (b is None)
]
R.check(
    f"the two parsers accept exactly the same strings "
    f"({len(_rt_corpus) - len(_rt_split)}/{len(_rt_corpus)} in the corpus)",
    not _rt_split,
    f"{len(_rt_split)} disagree: "
    + "; ".join(f"{s!r}: {why}" for s, why in _rt_split[:3]),
)

# (4) The single-schedule case: when every day carries the same windows, the
# every-day view IS those windows -- the two parsers agree on the value, not
# only on acceptance. (A spec whose days DIFFER keeps the documented merged
# union, which is a different claim and is checked above.)
_rt_same = [
    (s, f"{_parse_w(s)} != {_rt_effective(s)[0]}")
    for s in _rt_corpus
    if _rt_raises(_parse_w, s) is None
    and _rt_raises(_pw, s) is None
    and all(day == _rt_effective(s)[0] for day in _rt_effective(s))
    and _parse_w(s) != _rt_effective(s)[0]
]
R.check(
    "on a single-schedule spec the every-day view IS the schedule",
    not _rt_same,
    f"{len(_rt_same)} differ: " + "; ".join(f"{s!r}: {w}" for s, w in _rt_same[:3]),
)

# (5) The guard against the failure mode of this fix: one grammar must not
# mean a WIDER grammar. Every one of these was refused before and must stay
# refused, by both parsers and by both of the form's verdicts.
_RT_MALFORMED = (
    "banana", "Mo 25:00-26:00", "Mox 06:00-07:00", "weekdays", "Mo-Fr",
    "Mo,Tu", "Mo,Tu,We", "Mo 06:00-07:00, weekend", "06:00", "Mo 06:00",
    "Mo 06:00-06:00", "99:00-100:00", "Mo 06:00-07:00, banana",
    "Mo,banana 06:00-07:00", "weekend 06:00-07:00, Fr", "Mo,,Tu",
)
_rt_leaked = [
    (s, f"parse_windows={'ACCEPTED' if a is None else 'refused'}, "
        f"parse_weekly_windows={'ACCEPTED' if b is None else 'refused'}, "
        f"is_valid_spec={_ivs(s)}, spec_problem={_rt_problem(s)!r}")
    for s, a, b in (
        (s, _rt_raises(_parse_w, s), _rt_raises(_pw, s)) for s in _RT_MALFORMED
    )
    if a is None or b is None or _ivs(s) or _rt_problem(s) is None
]
R.check(
    f"a malformed spec is still refused by both parsers and the form "
    f"({len(_RT_MALFORMED) - len(_rt_leaked)}/{len(_RT_MALFORMED)})",
    not _rt_leaked,
    f"{len(_rt_leaked)} leaked through: "
    + "; ".join(f"{s!r}: {why}" for s, why in _rt_leaked),
)

# (6) The grammar the UI PROMISES is the grammar the form accepts. The
# options-flow help text names its examples in single quotes; every one of
# them must pass the form's own verdict. This is where the split was visible
# to a user without reading any code: "Mo 05:30-07:00, Tu-Fr 06:00-08:00,
# Sa,Su 08:00-09:30" is the string all three language files tell you to type,
# and spec_problem called it invalid_dhw_windows. Read out of the files so
# a new example cannot be added without being checked.
import json as _rt_json  # noqa: E402
import re as _rt_re  # noqa: E402

_rt_examples = {}
for _rt_f in ("strings.json", "translations/en.json", "translations/sv.json"):
    with open(f"custom_components/heatpump_optimizer/{_rt_f}", encoding="utf-8") as _fh:
        _rt_doc = _rt_json.load(_fh)

    def _rt_walk(node, out):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "dhw_windows" and isinstance(value, str):
                    out.update(
                        q for q in _rt_re.findall(r"'([^']*)'", value)
                        if _rt_re.search(r"\d", q) and "-" in q
                    )
                _rt_walk(value, out)
        elif isinstance(node, list):
            for value in node:
                _rt_walk(value, out)

    _rt_found = set()
    _rt_walk(_rt_doc, _rt_found)
    for _rt_ex in _rt_found:
        _rt_examples.setdefault(_rt_ex, []).append(_rt_f)

_rt_refused = [
    (ex, f"{files}: spec_problem={_rt_problem(ex)!r}, is_valid_spec={_ivs(ex)}")
    for ex, files in sorted(_rt_examples.items())
    if _rt_problem(ex) is not None or not _ivs(ex)
]
R.check(
    f"every window spec the UI text tells the user to type is accepted by the "
    f"form ({len(_rt_examples) - len(_rt_refused)}/{len(_rt_examples)})",
    _rt_examples and not _rt_refused,
    f"{len(_rt_refused)} refused: "
    + "; ".join(f"{ex!r}: {why}" for ex, why in _rt_refused)
    if _rt_refused
    else "no examples found in the language files -- the check asserts nothing",
)

# End to end: the plan honours the day it is solving for. A Monday-start
# horizon heats the weekday window; a Saturday-start horizon the weekend
# one -- the heating hours are the observable, and they must differ.
def _weekly_solve(spec, start):
    _cfg = _grad_house(two_zone=False, dhw=True)
    _cfg["dhw_windows"] = spec
    _p = ThermalParameters.from_config(_cfg)
    _o = _PvOpt(
        ThermalModel(_p),
        _PvOptCfg(
            horizon_hours=24, time_step_minutes=15,
            target_temp=21.0, min_temp=17.0, max_temp=23.0,
        ),
    )
    _pr = _grad_prices("winter_typical", start)
    _ot, _wi, _ra, _so = _grad_weather("winter_cold", start)
    _st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(_ot[0]), dhw_temperature=48.0,
        dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0,
    )
    return _o.optimize(inputs=solve_inputs(
        initial_state=_st,
        prices=_pr,
        outdoor_temps=_ot,
        wind_speeds=_wi,
        precipitation=_ra,
        solar_radiation=_so,
        start_time=start,
    ))

_SPEC = "weekdays 06:00-08:00, weekend 10:00-12:00"
# The requirement mask is the honest observable: when each step's floor
# temperature is the in-window minimum rather than the idle one, hot water
# is REQUIRED there. Heating power alone cannot say this -- the optimizer
# legitimately preheats hours before a window when electricity is cheap, so
# "power inside the window" and "power outside" both happen for any window.
def _weekly_requirement_hours(spec, start):
    _cfg = _grad_house(two_zone=False, dhw=True)
    _cfg["dhw_windows"] = spec
    _p = ThermalParameters.from_config(_cfg)
    _m = ThermalModel(_p)
    _o = _PvOpt(_m, _PvOptCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    _n = 96
    _hours = np.array([
        (_WDT.combine(start.date(), _WDT.min.time())
         + __import__("datetime").timedelta(hours=i * 0.25)).hour
        + ((_WDT.combine(start.date(), _WDT.min.time())
            + __import__("datetime").timedelta(hours=i * 0.25)).minute) / 60.0
        for i in range(_n)
    ])
    _plan, _ = _dhw_planner(_o)._build_dhw_requirements(
        _dhw_horizon(
            prices=np.full(_n, 1.0), outdoor=np.full(_n, -5.0),
            n=_n, dt=0.25, step_hours=_hours,
            state=ThermalState(
                room_temperature=21.0, slab_temperature=22.0,
                outdoor_temperature=-5.0, dhw_temperature=48.0,
                dhw_hours_since_legionella=20.0,
                buffer_tank_temperature=40.0),
            step_weekdays=np.array(
                [(start + __import__("datetime").timedelta(hours=(i - 1) * 0.25)).weekday()
                 for i in range(_n + 1)]),
        ),
        p_max=4.0,
    )
    _idle = min(_p.dhw_idle_min_temp, _p.dhw_min_temp)
    _floors = np.asarray(_plan.floor_temps)
    _in = np.where(_floors > _idle + 1e-9)[0]
    return sorted(set(round(float(_hours[i]), 2) for i in _in))

_mon_req = _weekly_requirement_hours(_SPEC, _WDT(2026, 1, 5))
_sat_req = _weekly_requirement_hours(_SPEC, _WDT(2026, 1, 10))
R.check(
    "a Monday plan requires hot water in the weekday window",
    _mon_req and min(_mon_req) >= 6.0 and max(_mon_req) < 8.0,
    f"requirement hours {_mon_req}",
)
R.check(
    "a Saturday plan requires it in the weekend window instead",
    _sat_req and min(_sat_req) >= 10.0 and max(_sat_req) < 12.0,
    f"requirement hours {_sat_req}",
)
R.check(
    "the two requirement sets do not overlap at all",
    not (set(_mon_req) & set(_sat_req)),
    f"mon {_mon_req} vs sat {_sat_req}",
)
# The flat spec is byte-identical to before: the weekly path is entirely
# gated on dhw_weekly_windows, which is None here. (The drift gate holds
# this across every captured scenario; this is the local statement.)
_flata = _weekly_solve("06:00-08:00", _WDT(2026, 1, 5))
_flatb = _weekly_solve("06:00-08:00", _WDT(2026, 1, 5))
R.check(
    "a flat spec solves identically regardless (deterministic)",
    np.array_equal(
        np.asarray(_flata.dhw_power_schedule),
        np.asarray(_flatb.dhw_power_schedule),
    ),
    "",
)


# --- D4-08 (#171): the form's verdict on a window spec ----------------------
# ``parse_windows`` stays permissive on purpose (a stored spec must keep
# loading); ``spec_problem`` is the form's stricter view, and it is a
# separate function so the two cannot drift into one.
from heatpump_optimizer.const import DEFAULT_DHW_WINDOWS as _win_default
from heatpump_optimizer.dhw_schedule import (
    ERROR_INVALID as _win_invalid,
    ERROR_TOO_SHORT as _win_short,
    MIN_WINDOW_MINUTES as _win_min,
    hour_in_windows as _win_in,
    spec_problem as _win_problem,
    window_minutes as _win_len,
)
from heatpump_optimizer.optimizer import OptimizationConfig as _WinCfg

R.check(
    "the shortest window the form accepts is one planning step",
    _win_min == _WinCfg().time_step_minutes,
    f"{_win_min} vs {_WinCfg().time_step_minutes}",
)
R.check(
    "a window shorter than a step binds no step start at all",
    not any(_win_in(i / 4.0, _parse_w("06:05-06:06")) for i in range(96)),
    "if it bound one, the finding's 'meaningless' would be wrong",
)
R.check(
    "the form's verdict names the one-minute window",
    _win_problem("06:05-06:06") == _win_short
    and _win_problem("06:00-08:30, 17:00-17:01") == _win_short,
    f"{_win_problem('06:05-06:06')!r}",
)
R.check(
    "a window of exactly one step is fine, and so is the default",
    _win_problem("06:00-06:15") is None and _win_problem(_win_default) is None,
)
R.check(
    "a wrapping window is measured through midnight",
    abs(_win_len((23.0 + 55 / 60.0, 5 / 60.0)) - 10.0) < 1e-9
    and _win_problem("23:55-00:05") == _win_short
    and _win_problem("22:00-06:00") is None,
    f"{_win_len((23.0 + 55 / 60.0, 5 / 60.0))} min",
)
R.check(
    "the judgement is per segment, before normalisation can merge one away",
    _win_problem("06:00-08:30, 08:29-08:30") == _win_short,
    "merged with its neighbour, the one-minute segment would vanish",
)
R.check(
    "a weekly spec's segments are judged too, and 00:00-00:00 stays a full day",
    _win_problem("weekdays 06:00-08:30, weekend 08:00-08:01") == _win_short
    and _win_problem("00:00-00:00") is None,
)
R.check(
    "an unreadable spec keeps its original error, and empty is no problem",
    _win_problem("banana") == _win_invalid and _win_problem("") is None,
)
R.check(
    "the permissive parser still loads the window the form refuses",
    _parse_w("06:05-06:06") == [(6.0 + 5 / 60.0, 6.0 + 6 / 60.0)],
    "a stored spec that stopped loading would be the fix worse than its bug",
)


# --- #1260: per-weekday window overrides -----------------------------------
# The weekly GRAMMAR types day selectors into the one spec field; the
# overrides are the no-typing version: seven flat fields, each an ordinary
# window list for the weekday the field names, empty = inherit. One
# resolution order for all of it, documented on `windows_for_day`:
# per-day override > holiday > the default spec's own day structure.
R.section("Per-weekday DHW window overrides (#1260)")
from datetime import date as _pd_date

from heatpump_optimizer import const as _pd_const
from heatpump_optimizer.dhw_schedule import (
    ERROR_DAY_SELECTOR as _pd_selector_err,
    day_overrides_enabled as _pd_enabled,
    day_spec_problem as _pd_problem,
    format_resolved_day_spec as _pd_resolved,
    parse_day_overrides as _pd_parse,
)

_pd_weekly = _pw("weekdays 06:00-08:00, weekend 08:00-10:00")
_pd_fallback = _parse_w("06:00-08:00")
_pd_holiday = _parse_w("10:00-12:00")
# Monday-first, the order CONF_DHW_WINDOWS_DAY declares and
# datetime.weekday() numbers: 0=Mo .. 6=Su.
_pd_ov = [None] * 7
_pd_ov[5] = _parse_w("12:00-14:00")   # Saturday
_pd_ov[0] = _parse_w("05:00-06:00")   # Monday
R.check(
    "a per-day override beats holiday, weekly and default together",
    _wfd(_pd_weekly, 5, _pd_fallback, holiday_windows=_pd_holiday,
         holiday=True, day_overrides=_pd_ov) == _pd_ov[5]
    and _wfd(None, 5, _pd_fallback, day_overrides=_pd_ov) == _pd_ov[5],
    "the issue's precedence: per-day > holiday > default",
)
R.check(
    "a day with no override keeps the holiday-first behaviour it has today",
    _wfd(_pd_weekly, 4, _pd_fallback, holiday_windows=_pd_holiday,
         holiday=True, day_overrides=_pd_ov) == _pd_holiday
    and _wfd(_pd_weekly, 4, _pd_fallback, holiday_windows=_pd_holiday,
             holiday=False, day_overrides=_pd_ov) == _pd_weekly[4],
    "an empty field inherits; it does not suppress the holiday windows",
)
R.check(
    "an all-empty override set resolves exactly like none at all (null control)",
    all(
        _wfd(_pd_weekly, d, _pd_fallback, holiday_windows=_pd_holiday,
             holiday=(d == 4), day_overrides=[None] * 7)
        == _wfd(_pd_weekly, d, _pd_fallback, holiday_windows=_pd_holiday,
                holiday=(d == 4))
        for d in range(7)
    ),
    "every existing install has no overrides, so none may resolve differently",
)
R.check(
    "an hour-only caller (weekday None) still gets the flat fallback",
    _wfd(_pd_weekly, None, _pd_fallback, day_overrides=_pd_ov) == _pd_fallback,
    "windows_for_day's own contract for callers with no date",
)


def _pd_windows_on(day):
    """The windows in force on one date, resolved the way production does."""
    return _wfd(_pd_weekly, day.weekday(), _pd_fallback,
                holiday_windows=_pd_holiday, holiday=False,
                day_overrides=_pd_ov)


_pd_fri, _pd_sat = _pd_date(2026, 1, 16), _pd_date(2026, 1, 17)
_pd_sun, _pd_mon = _pd_date(2026, 1, 18), _pd_date(2026, 1, 19)
R.check(
    "the Fri->Sat boundary switches to the Saturday override",
    _pd_windows_on(_pd_fri) == _pd_weekly[4]
    and _pd_windows_on(_pd_sat) == _pd_ov[5],
    f"friday {_pd_windows_on(_pd_fri)}, saturday {_pd_windows_on(_pd_sat)}",
)
R.check(
    "the Sun->Mon boundary switches to the Monday override",
    _pd_windows_on(_pd_sun) == _pd_weekly[6]
    and _pd_windows_on(_pd_mon) == _pd_ov[0],
    f"sunday {_pd_windows_on(_pd_sun)}, monday {_pd_windows_on(_pd_mon)}",
)

# The config assembly: the flag gates, absent specs inherit, a stored
# False switches the overrides off without erasing them, and an unparseable
# day degrades to inheriting rather than to no schedule at all.
_pd_cfg = {
    _pd_const.CONF_DHW_WINDOWS: "06:00-08:00",
    _pd_const.CONF_DHW_WINDOWS_BY_DAY: True,
    _pd_const.CONF_DHW_WINDOWS_DAY[0]: "05:00-06:00",
    _pd_const.CONF_DHW_WINDOWS_DAY[5]: "12:00-14:00",
}
R.check(
    "the flag plus specs parses to the seven-day shape",
    _pd_parse(_pd_cfg) == _pd_ov,
    f"{_pd_parse(_pd_cfg)}",
)
R.check(
    "a config with no override keys carries none",
    _pd_parse({_pd_const.CONF_DHW_WINDOWS: "06:00-08:00"}) is None
    and not _pd_enabled({}),
    "the feature is opt-in; from_config's None is the null control",
)
R.check(
    "specs without the flag still enable -- the toggle's computed default",
    _pd_enabled({_pd_const.CONF_DHW_WINDOWS_DAY[3]: "07:00-08:00"}),
    "an entry whose specs predate the toggle (or were hand-set) stays on",
)
R.check(
    "a stored False flag switches the overrides off, specs still in place",
    _pd_parse({**_pd_cfg, _pd_const.CONF_DHW_WINDOWS_BY_DAY: False}) is None
    and not _pd_enabled({**_pd_cfg, _pd_const.CONF_DHW_WINDOWS_BY_DAY: False}),
    "turning the toggle off is non-destructive: the fields come back on",
)
R.check(
    "an unparseable day spec degrades to that day inheriting",
    _pd_parse({**_pd_cfg, _pd_const.CONF_DHW_WINDOWS_DAY[5]: "garbage"})
    == [_pd_ov[0], None, None, None, None, None, None],
    "one bad key must not take the other six days' overrides away",
)
R.check(
    "the flag on with every field empty is no overrides at all",
    _pd_parse({_pd_const.CONF_DHW_WINDOWS_BY_DAY: True,
               _pd_const.CONF_DHW_WINDOWS: "06:00-08:00"}) is None,
    "revealing the fields and saving them empty changes nothing",
)

# The form's verdict on one day field: the ordinary spec verdicts, plus a
# refusal for day selectors -- the field already names the day, and a
# selector there would be silently ignored by the every-day parser.
R.check(
    "a plain spec and an empty field pass the per-day verdict",
    _pd_problem("06:00-08:30, 17:00-22:00") is None and _pd_problem("") is None,
    "",
)
R.check(
    "a day selector is refused in a field that already names the day",
    _pd_problem("weekdays 06:00-08:30") == _pd_selector_err
    and _pd_problem("Sa,Su 08:00-09:30") == _pd_selector_err,
    "parse_windows ignores selectors; accepting one here would silently "
    "apply Saturday's times to every day the field names",
)
R.check(
    "the ordinary verdicts still apply per field",
    _pd_problem("garbage") == _win_invalid
    and _pd_problem("06:05-06:10") == _win_short,
    "",
)

# from_config loads the overrides beside the flat spec, and an unchanged
# config still loads None -- the parse-level null control for the whole
# feature.
_pd_house = _grad_house(two_zone=False, dhw=True)
_pd_house.update(_pd_cfg)
R.check(
    "from_config loads the overrides beside the flat spec",
    ThermalParameters.from_config(_pd_house).dhw_day_windows == _pd_ov,
    "",
)
_pd_house_null = _grad_house(two_zone=False, dhw=True)
_pd_house_null[_pd_const.CONF_DHW_WINDOWS] = "06:00-08:00"
R.check(
    "from_config without override keys keeps dhw_day_windows None",
    ThermalParameters.from_config(_pd_house_null).dhw_day_windows is None,
    "",
)

# The display spec the card's plan-tab band reads: overrides folded onto
# the default's own day structure, None (published as absent) when no
# override is in force.
_pd_sat_only = [None] * 7
_pd_sat_only[5] = _parse_w("10:00-12:00")
R.check(
    "no overrides resolve to no display spec at all",
    _pd_resolved(_pd_weekly, _pd_fallback, None) is None
    and _pd_resolved(_pd_weekly, _pd_fallback, [None] * 7) is None,
    "absent, never an echo of the configuration",
)
R.check(
    "a flat default with one override renders the folded week",
    _pd_resolved(None, _pd_fallback, _pd_sat_only)
    == _fw([[(6.0, 8.0)]] * 5 + [[(10.0, 12.0)]] + [[(6.0, 8.0)]]),
    f"{_pd_resolved(None, _pd_fallback, _pd_sat_only)!r}",
)
R.check(
    "an override onto a weekly default replaces only its own day",
    _pd_resolved(_pd_weekly, _pd_fallback, _pd_sat_only)
    == _fw([[(6.0, 8.0)]] * 5 + [[(10.0, 12.0)]] + [[(8.0, 10.0)]]),
    f"{_pd_resolved(_pd_weekly, _pd_fallback, _pd_sat_only)!r}",
)
R.check(
    "an all-empty fallback plus overrides names only the overridden days",
    _pd_resolved(None, [], _pd_sat_only) == "Sa 10:00-12:00",
    f"{_pd_resolved(None, [], _pd_sat_only)!r}",
)

# End to end: the plan honours the override on the day it names, beside a
# FLAT default spec -- which is also the routing proof: with weekly None,
# only the day overrides can make the optimizer compute step weekdays at
# all, so Saturday planning the override's hours means the routing held.
def _pd_requirement_hours(spec, extra, start):
    _cfg = _grad_house(two_zone=False, dhw=True)
    _cfg["dhw_windows"] = spec
    _cfg.update(extra)
    _p = ThermalParameters.from_config(_cfg)
    _o = _PvOpt(_PvModel(_p), _PvOptCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    _n = 96
    _hours = np.array([
        (_WDT.combine(start.date(), _WDT.min.time())
         + __import__("datetime").timedelta(hours=i * 0.25)).hour
        + ((_WDT.combine(start.date(), _WDT.min.time())
            + __import__("datetime").timedelta(hours=i * 0.25)).minute) / 60.0
        for i in range(_n)
    ])
    _plan, _ = _dhw_planner(_o)._build_dhw_requirements(
        _dhw_horizon(
            prices=np.full(_n, 1.0), outdoor=np.full(_n, -5.0),
            n=_n, dt=0.25, step_hours=_hours,
            state=ThermalState(
                room_temperature=21.0, slab_temperature=22.0,
                outdoor_temperature=-5.0, dhw_temperature=48.0,
                dhw_hours_since_legionella=20.0,
                buffer_tank_temperature=40.0),
            step_weekdays=np.array(
                [(start + __import__("datetime").timedelta(hours=(i - 1) * 0.25)).weekday()
                 for i in range(_n + 1)]),
        ),
        p_max=4.0,
    )
    _idle = min(_p.dhw_idle_min_temp, _p.dhw_min_temp)
    _floors = np.asarray(_plan.floor_temps)
    _in = np.where(_floors > _idle + 1e-9)[0]
    return sorted(set(round(float(_hours[i]), 2) for i in _in))

_pd_extra = {
    _pd_const.CONF_DHW_WINDOWS_BY_DAY: True,
    _pd_const.CONF_DHW_WINDOWS_DAY[5]: "10:00-12:00",
}
_pd_mon_req = _pd_requirement_hours("06:00-08:00", _pd_extra, _WDT(2026, 1, 5))
_pd_sat_req = _pd_requirement_hours("06:00-08:00", _pd_extra, _WDT(2026, 1, 10))
R.check(
    "a Monday plan over a flat spec keeps the default window",
    _pd_mon_req and min(_pd_mon_req) >= 6.0 and max(_pd_mon_req) < 8.0,
    f"requirement hours {_pd_mon_req}",
)
R.check(
    "a Saturday plan honours the Saturday override, not the flat default",
    _pd_sat_req and min(_pd_sat_req) >= 10.0 and max(_pd_sat_req) < 12.0,
    f"requirement hours {_pd_sat_req}",
)
# The optimizer's own optimize() path must compute step weekdays when only
# day overrides exist: with a FLAT spec the weekly structure is None, so
# the weekday array's gate is the day overrides alone. Two solves of the
# same Saturday, one with the override and one without, must differ -- if
# the gate had stayed weekly-only, both would plan the flat 06:00-08:00.
def _pd_full_solve(house, start):
    _o = _PvOpt(_PvModel(ThermalParameters.from_config(house)), _PvOptCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    return _o.optimize(inputs=solve_inputs(
        initial_state=ThermalState(
            room_temperature=21.0, slab_temperature=22.0,
            outdoor_temperature=-5.0, dhw_temperature=48.0,
            dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0),
        prices=_grad_prices("winter_typical", start),
        outdoor_temps=np.full(96, -5.0),
        wind_speeds=np.full(96, 3.0),
        precipitation=np.full(96, 0.0),
        solar_radiation=np.full(96, 0.0),
        start_time=start,
    ))


_pd_sat_start = _WDT(2026, 1, 17, 0, 0)
_pd_house_sat = _grad_house(two_zone=False, dhw=True)
_pd_house_sat.update({
    _pd_const.CONF_DHW_WINDOWS: "06:00-08:00",
    _pd_const.CONF_DHW_WINDOWS_BY_DAY: True,
    _pd_const.CONF_DHW_WINDOWS_DAY[5]: "10:00-12:00",
})
_pd_with = _pd_full_solve(_pd_house_sat, _pd_sat_start)
_pd_without = _pd_full_solve(_pd_house_null, _pd_sat_start)
R.check(
    "a full Saturday solve with the override differs from the flat one",
    not np.array_equal(
        np.asarray(_pd_with.dhw_power_schedule),
        np.asarray(_pd_without.dhw_power_schedule),
    ),
    "identical schedules would mean the override never reached the planner",
)
R.check(
    "that solve publishes the resolved display spec for the card's band",
    (_pd_with.predictive_info or {}).get("dhw_windows_resolved")
    == _fw([[(6.0, 8.0)]] * 5 + [[(10.0, 12.0)]] + [[(6.0, 8.0)]]),
    f"{(_pd_with.predictive_info or {}).get('dhw_windows_resolved')!r}",
)
R.check(
    "the no-override solve publishes no resolved key at all",
    "dhw_windows_resolved" not in (_pd_without.predictive_info or {}),
    "absent, not null: the payload stays byte-for-byte what it was",
)
_pd_mon_start = _WDT(2026, 1, 5, 0, 0)
R.check(
    "the same pair on a Monday (no override that day) solves identically",
    np.array_equal(
        np.asarray(_pd_full_solve(_pd_house_sat, _pd_mon_start).dhw_power_schedule),
        np.asarray(_pd_full_solve(_pd_house_null, _pd_mon_start).dhw_power_schedule),
    ),
    "Monday inherits the flat spec, so the two configs must agree there",
)


# ===========================================================================
# The batched simulation: bitwise parity with the scalar path (issue #97)
# ===========================================================================
R.section("The batched trajectory is the scalar trajectory, bit for bit")

# simulate_trajectory_batch exists so the solver's finite-difference
# gradient can evaluate its 97 perturbations as one vectorized pass. Its
# contract is bitwise: every row must equal the scalar path's output to
# the last bit, because the jac built on it must reproduce scipy's own
# estimate exactly or the plans move. np.array_equal is bitwise for
# floats that are not NaN, which trajectories here never are.
from datetime import datetime as _dt_grad

def _grad_parity(two_zone, wood=False, valve=None, extra_cfg=None, label="",
                 weather_p="winter_cold", state_over=None, bounds_over=None,
                 min_substeps=1, param_over=None, n=48):
    cfg = _grad_house(two_zone=two_zone)
    extra = dict(extra_cfg or {})
    if valve:
        extra.setdefault("mixing_valve_mode", valve)
    if wood:
        extra.setdefault("two_tank_modelled", True)
    p = ThermalParameters.from_config({**cfg, **extra})
    for _k, _v in (param_over or {}).items():
        setattr(p, _k, _v)
    m = ThermalModel(p)
    rng = np.random.default_rng(7)
    powers = rng.uniform(0, 3.0, size=(5, n))
    start = _dt_grad(2026, 1, 15)
    ot, wi, ra, so = (a[:n] for a in _grad_weather(weather_p, start))
    hum = np.full(n, 78.0)
    ext = rng.uniform(0, 2.0, size=n)
    st_kwargs = dict(
        room_temperature=20.5, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.2,
        lower_floor_temperature=20.1, buffer_tank_temperature=48.0,
        wood_tank_temperature=52.0 if wood else None,
    )
    st_kwargs.update(state_over or {})
    st = ThermalState(**st_kwargs)
    # D2-01: a cell claiming to cover the Euler sub-step regime has to
    # actually be in it. The regime is what the batch and the scalar path
    # disagreed about for as long as this contract has existed, and the one
    # cell that *said* "stability substeps" ran at n_sub = 1 -- its
    # `room_thermal_mass` override was not a config key at all, and the
    # masses that did land left the two-zone ratio at 0.746 against the 1.5
    # threshold. Assert the count per step, from the production guard, so
    # the label can never again outrun the configuration.
    subs = [m._substeps_and_loss(float(wi[k]), float(ra[k]), 0.25)[0]
            for k in range(n)]
    R.check(
        f"grad-parity cell subdivides as claimed (n_sub >= {min_substeps}): "
        f"{label}",
        min(subs) >= min_substeps,
        f"_substeps_and_loss gave min={min(subs)} max={max(subs)} "
        f"over {n} steps, wanted every step >= {min_substeps}",
    )
    batch = m.simulate_trajectory_batch(
        st, powers, _WS(ot, wi, ra, so, hum, ext), dt_hours=0.25,
        start_hour=7.0)
    mism = []
    for b in range(powers.shape[0]):
        r, s, u, l, buf, _, wood = m.simulate_trajectory(
            st, powers[b], _WS(ot, wi, ra, so, hum, ext), dt_hours=0.25,
            start_hour=7.0)
        refs = (("room", batch["room"][b], r), ("slab", batch["slab"][b], s),
                ("upper", batch["upper"][b], u), ("lower", batch["lower"][b], l),
                ("buffer", batch["buffer"][b], buf))
        if batch["wood"] is not None:
            refs += (("wood", batch["wood"][b], wood),)
        for name, arr, ref in refs:
            if not np.array_equal(arr, ref):
                mism.append(f"{name}[{b}]@{int(np.argmax(arr != ref))}")
    R.check(
        f"batched simulation is bitwise-identical: {label}",
        not mism,
        f"first divergences: {mism[:4]}",
    )

    # The gradient contract (D9-01): with the batched jac now serving
    # NON-UNIFORM bounds (any DHW block or per-step cap pins the space bounds
    # unevenly), _batch_fd_gradient must reproduce scipy's own 2-point
    # approx_derivative bit-for-bit on those bounds, or the DHW solves it now
    # serves would drift. Assert it directly on a scalarised space objective
    # over these trajectories, at DHW-pinned bounds when asked, so the
    # one-sided/zero-step rules are exercised per variable.
    from scipy.optimize._numdiff import approx_derivative

    targets = np.full(n, 21.0)

    def space_obj(x):
        rr, _, _, _, _, _, _ = m.simulate_trajectory(
            st, np.clip(x, 0.0, None), _WS(ot, wi, ra, so, hum, ext),
            dt_hours=0.25, start_hour=7.0)
        room = rr[1:]
        return float(np.sum((room - targets) ** 2) + 0.01 * np.sum(x))

    def space_obj_batch(mat, *a):
        tr = m.simulate_trajectory_batch(
            st, np.clip(mat, 0.0, None), _WS(ot, wi, ra, so, hum, ext),
            dt_hours=0.25, start_hour=7.0)
        out = np.empty(mat.shape[0])
        for bi in range(mat.shape[0]):
            room = tr["room"][bi][1:]
            out[bi] = float(np.sum((room - targets) ** 2)
                            + 0.01 * np.sum(mat[bi]))
        return out

    p_max = 6.0
    if bounds_over == "dhw_pinned":
        # Emulate a DHW block: some steps have shrunken headroom, a few are
        # pinned to zero range (lb == ub), the shape the with-DHW solve makes.
        ub = np.full(n, p_max)
        ub[5:9] = 0.0          # full DHW block -> zero-range space bounds
        ub[20:24] = 1.2        # partial headroom
        bounds = [(0.0, float(ub[i])) for i in range(n)]
    elif bounds_over == "capped":
        rc = np.random.default_rng(3).uniform(0.5, p_max, size=n)
        bounds = [(0.0, float(rc[i])) for i in range(n)]
    else:
        bounds = [(0.0, p_max)] * n
    lb = np.array([b[0] for b in bounds])
    ubv = np.array([b[1] for b in bounds])
    x0 = np.minimum(rng.uniform(0, 3.0, size=n), ubv)
    f0 = space_obj(x0)
    g_batch = _grad_optmod._batch_fd_gradient(
        space_obj_batch, (), x0, f0, 1e-4, bounds)
    g_scipy = approx_derivative(
        space_obj, x0, method="2-point", abs_step=1e-4, f0=f0,
        bounds=(lb, ubv))
    # A fixed variable (lb == ub) is the ONE place the batched jac departs
    # from scipy's estimate on purpose (D9-01): there the one-sided step is
    # zero and scipy's own divided difference is 0/0 = NaN. The batch returns
    # an exact 0.0 -- the derivative of a variable that cannot move -- and
    # keeps every free variable bit-for-bit. Parity is asserted on the free
    # variables; the fixed ones get their own, stricter assertion below.
    fixed = lb >= ubv
    free = ~fixed
    R.check(
        f"batched jac == scipy 2-point FD bit-for-bit on free variables: {label}",
        np.array_equal(g_batch[free], g_scipy[free], equal_nan=True)
        and np.array_equal(np.isnan(g_batch[free]), np.isnan(g_scipy[free])),
        f"gradient differs from scipy's estimate on the {int(free.sum())} "
        f"free variables (maxabs="
        f"{float(np.nanmax(np.abs(g_batch[free] - g_scipy[free]))):.2e})",
    )
    R.check(
        f"batched jac is finite, and exactly 0.0 at the {int(fixed.sum())} "
        f"fixed variables: {label}",
        bool(np.all(np.isfinite(g_batch)))
        and bool(np.all(g_batch[fixed] == 0.0)),
        f"fixed-variable entries came back as {g_batch[fixed][:4]}; scipy's "
        f"own estimate there is {g_scipy[fixed][:4]}, which is exactly why "
        f"the batch must not simply divide 0 by 0",
    )

    # The end of the finding (D9-01): one fixed variable must not cost the
    # WHOLE solve its batched jac. Run the real multi-start against these
    # bounds and let scipy's own counters name the path -- with a supplied
    # jac L-BFGS-B calls fun and jac once each per iterate (nfev == njev);
    # when it has to estimate the gradient itself it spends n+1 function
    # evaluations per gradient. Only worth paying for on the pinned shape.
    if bounds_over == "dhw_pinned":
        R.check(
            f"a zero-range bound does not disqualify the batch: {label}",
            _grad_optmod._bounds_supported_by_batch(bounds),
            f"{int(fixed.sum())} of {n} bounds are (lo == hi); the gate must "
            f"still serve the solve",
        )
        _bfd_calls = [0]
        _real_bfd = _grad_optmod._batch_fd_gradient

        def _counted_bfd(*a, **k):
            _bfd_calls[0] += 1
            return _real_bfd(*a, **k)

        _grad_optmod._batch_fd_gradient = _counted_bfd
        try:
            res = _grad_optmod._multi_start_minimize(
                space_obj, [x0, np.minimum(x0 * 0.4, ubv)], bounds,
                maxiter=25, batch_objective=space_obj_batch,
            )
        finally:
            _grad_optmod._batch_fd_gradient = _real_bfd
        R.check(
            f"the pinned solve runs on the batched jac, not scipy's scalar "
            f"finite differences: {label}",
            _bfd_calls[0] > 0 and int(res.nfev) == int(res.njev),
            f"batched gradients={_bfd_calls[0]}, nfev={int(res.nfev)}, "
            f"njev={int(res.njev)}; the scalar path spends n+1={n + 1} "
            f"function evaluations per gradient",
        )
        R.check(
            f"the pinned solve gets a finite point on its pins, not a dead "
            f"line search: {label}",
            bool(np.all(np.isfinite(res.x)))
            and int(res.status) != 2
            and int(res.nit) > 0
            and bool(np.all(res.x[fixed] == lb[fixed])),
            f"status={int(res.status)} nit={int(res.nit)} "
            f"finite={bool(np.all(np.isfinite(res.x)))} "
            f"off-pin={float(np.max(np.abs(res.x[fixed] - lb[fixed]))):.3e}; "
            f"a NaN in a SUPPLIED jac is status 2 at nit 0 -- L-BFGS-B dies "
            f"in the first line search, which is the whole reason the fixed "
            f"entry has to be an exact 0.0 rather than scipy's 0/0",
        )


import heatpump_optimizer.optimizer as _grad_optmod


def _d903_jac_f0_reuses_fun():
    """#288: jac f0 must not re-run the objective at scipy's last x."""
    raw = []

    def obj(x, *_a):
        raw.append(np.asarray(x, dtype=float).tobytes())
        d = np.asarray(x, dtype=float) - 1.0
        return float(np.dot(d, d))

    def batch_obj(mat, *_a):
        d = np.asarray(mat, dtype=float) - 1.0
        return np.einsum("ij,ij->i", d, d)

    n = 8
    bounds = [(-2.0, 2.0)] * n
    res = _grad_optmod._multi_start_minimize(
        obj, [np.zeros(n), np.full(n, 0.4)], bounds, maxiter=20,
        batch_objective=batch_obj,
    )
    consecutive_dups = sum(
        1 for i in range(1, len(raw)) if raw[i] == raw[i - 1]
    )
    R.check(
        "D9-03 jac f0 reuses scipy's last objective evaluation (#288)",
        consecutive_dups == 0,
        f"{consecutive_dups} consecutive duplicate objective evaluations "
        f"in {len(raw)} raw calls; nfev={int(res.nfev)} njev={int(res.njev)}",
    )
    R.check(
        "D9-03 memo solve still reaches the quadratic minimizer",
        bool(np.allclose(res.x, 1.0, atol=1e-3)),
        f"x={res.x[:4]} fun={float(res.fun)}",
    )


_d903_jac_f0_reuses_fun()


R.section("R9 vi-b: the evaluation memo's own arms (UX-6)")


def _vib_memo_arms():
    """Both arms of ``_memoized_value_and_gradient``'s contract, driven
    directly. No production caller reaches the memo-None arm --
    ``_multi_start_minimize`` always passes a live dict -- which is why the
    mutation lanes measured optimizer.py:568 GUARD_OFF a survivor: nothing
    in the tree asks the wrapper what it does without a memo. And the memo
    arm's return is driven immediately and UNCAUGHT on purpose: a wrapper
    that hands back None (RETURN_DEL at the ``return fun`` line) crashes
    here, early in this script, where the mutation driver sees a verdict.
    The same mutant caught-and-recorded merely disables the batched jac for
    every later solve in this file, which is pathologically slow and reads
    as a driver timeout, not a kill -- the red the lanes could not reach.
    """
    batch_calls: list[bytes] = []

    def batch_obj(mat, *_a):
        batch_calls.append(np.asarray(mat, dtype=float).tobytes())
        d = np.asarray(mat, dtype=float) - 1.0
        return np.einsum("ij,ij->i", d, d)

    n = 6
    x = np.full(n, 0.25)
    bounds = [(-2.0, 2.0)] * n

    memo: dict = {}
    memo_fun = _grad_optmod._memoized_value_and_gradient(
        batch_obj, bounds, 1e-4, memo,
    )
    first = memo_fun(x)   # computes the (value, gradient) pair and stores it
    served = memo_fun(x)  # the repeat is served from the memo: no batch call
    R.check(
        "vi-b with a memo the wrapper returns the memoizing fun and the "
        "repeat costs no batch evaluation",
        len(memo) == 1 and len(batch_calls) == 1
        and first[0] == served[0] and bool(np.array_equal(first[1], served[1]))
        and bool(np.isfinite(served[0])) and served[1].shape == (n,),
        f"memo entries={len(memo)} batch calls={len(batch_calls)} "
        f"first={first[0]!r} served={served[0]!r}",
    )

    plain_fun = _grad_optmod._memoized_value_and_gradient(
        batch_obj, bounds, 1e-4, None,
    )
    err = None
    out = None
    try:
        out = plain_fun(x)
    except Exception as exc:  # the None arm handed back the memo closure
        err = exc             # (memo.get on None), not the plain fused fun
    R.check(
        "vi-b with no memo the wrapper returns the plain fused fun, working",
        err is None and out is not None and len(out) == 2
        and bool(np.isfinite(out[0])) and bool(np.all(np.isfinite(out[1]))),
        f"err={err!r} out="
        f"{None if out is None else (out[0], out[1].shape)}",
    )
    R.check(
        "vi-b the memo's served pair is the plain fun's pair, to the bit",
        out is not None and first[0] == out[0]
        and bool(np.array_equal(first[1], out[1])),
        f"plain={None if out is None else out[0]!r} memo={first[0]!r}",
    )


_vib_memo_arms()


def _d0_restart_from_returned_point():
    """R3-D0-01/02: L-BFGS-B is restarted once from its own returned point."""
    x0s: list = []
    results: list = []
    real = _grad_optmod._scoped_minimize

    def spy(*a, **k):
        x0 = np.asarray(k["x0"] if "x0" in k else a[1], dtype=float).copy()
        x0s.append(x0)
        out = real(*a, **k)
        results.append(out)
        return out

    def obj(x, *_a):
        d = np.asarray(x, dtype=float) - 1.0
        return float(np.dot(d, d))

    _grad_optmod._scoped_minimize = spy
    try:
        _grad_optmod._multi_start_minimize(
            obj, [np.zeros(4)], [(-2.0, 2.0)] * 4, maxiter=20,
        )
    finally:
        _grad_optmod._scoped_minimize = real
    R.check(
        "one production start is followed by one restart from the returned point",
        len(x0s) == 2,
        f"minimize calls={len(x0s)}",
    )
    R.check(
        "the restart's x0 is the first run's returned point",
        len(x0s) == 2 and bool(np.allclose(x0s[1], results[0].x)),
        f"x0s={len(x0s)} first.x={getattr(results[0], 'x', None) if results else None}",
    )


_d0_restart_from_returned_point()


def _d0_restart_keeps_only_a_real_drop():
    """#826: an ftol tick is not a new plan; a 5e-2 relative drop is."""

    class _Res:
        def __init__(self, x: np.ndarray) -> None:
            self.x = np.asarray(x, dtype=float)

    def obj(x: np.ndarray, *_a: object) -> float:
        x = np.asarray(x, dtype=float)
        if np.allclose(x, 0.0):
            return 100.0
        if np.allclose(x, 1.0):
            return 99.9999
        if np.allclose(x, 2.0):
            return 95.0
        raise AssertionError(x)

    real = _grad_optmod._scoped_minimize
    chosen: dict[str, np.ndarray] = {"x": np.array([1.0, 1.0])}

    def spy(*_a: object, **_k: object) -> _Res:
        return _Res(chosen["x"])

    _grad_optmod._scoped_minimize = spy
    try:
        best = _Res(np.zeros(2))
        bounds = [(-10.0, 10.0)] * 2
        tick = _grad_optmod._lbfgsb_restart(
            best, obj, bounds, (), 20, None,
        )
        R.check(
            "an ftol-tick restart is not adopted",
            tick is best,
            f"kept {getattr(tick, 'x', None)}",
        )
        chosen["x"] = np.array([2.0, 2.0])
        drop = _grad_optmod._lbfgsb_restart(
            best, obj, bounds, (), 20, None,
        )
        R.check(
            "a 5e-2 relative drop is adopted",
            drop is not best and bool(np.allclose(drop.x, 2.0)),
            f"kept {getattr(drop, 'x', None)}",
        )
    finally:
        _grad_optmod._scoped_minimize = real


_d0_restart_keeps_only_a_real_drop()


def _d901_gil_yield_inside_run():
    """R6-D9-01: the solve yields the GIL INSIDE a single L-BFGS-B run.

    The eight between-run ``sleep(0.002)`` calls cannot bound the longest GIL
    hold: they sit *between* runs, and the hold is set by the longest run.
    The fix moves the yield into the objective (``_gil_yield``), so every
    L-BFGS-B function evaluation releases the GIL on the solver thread. This
    asserts that structurally -- the yield fires while inside a
    ``_scoped_minimize`` call, on the executor thread -- not by wall clock.
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor

    real_minimize = _grad_optmod._scoped_minimize
    real_yield = _grad_optmod._gil_yield

    def obj(x, *_a):
        d = np.asarray(x, dtype=float) - 1.0
        return float(np.dot(d, d))

    def batch_obj(mat, *_a):
        d = np.asarray(mat, dtype=float) - 1.0
        return np.einsum("ij,ij->i", d, d)

    state = {"depth": 0, "inside": 0, "outside": 0, "threads": set()}

    def tracking_minimize(*a, **k):
        state["depth"] += 1
        try:
            return real_minimize(*a, **k)
        finally:
            state["depth"] -= 1

    def tracking_yield():
        if state["depth"] > 0:
            state["inside"] += 1
        else:
            state["outside"] += 1
        state["threads"].add(threading.get_ident())

    _grad_optmod._scoped_minimize = tracking_minimize
    _grad_optmod._gil_yield = tracking_yield
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(
                _grad_optmod._multi_start_minimize,
                obj, [np.zeros(6)], [(-2.0, 2.0)] * 6,
                maxiter=15, batch_objective=batch_obj,
            ).result()
    finally:
        _grad_optmod._scoped_minimize = real_minimize
        _grad_optmod._gil_yield = real_yield

    main_tid = threading.main_thread().ident
    R.check(
        "D9-01 the solve yields the GIL inside a single L-BFGS-B run",
        state["inside"] > 0,
        f"in-run yields={state['inside']}, out-of-run yields={state['outside']}",
    )
    R.check(
        "D9-01 the in-run yield fires on the worker thread, not the caller",
        main_tid not in state["threads"],
        f"yield threads={sorted(state['threads'])}, main={main_tid}",
    )


_d901_gil_yield_inside_run()


# Space-only, uniform bounds (the historical five, unchanged).
_grad_parity(False, label="single-zone")
_grad_parity(True, label="two-zone")
_grad_parity(True, valve="manual", label="two-zone with valve")
_grad_parity(False, valve="manual", label="single-zone with valve")
_grad_parity(True, wood=True, valve="manual", label="two-tank")
# D2-01: the Euler sub-step regime, in both zonings, asserted rather than
# named. `_substeps_and_loss` subdivides a step whose worst u*dt/C exceeds
# EULER_STABILITY_MAX_RATIO, and the batch has to subdivide it the way the
# scalar path does -- same dt = dt_hours / n_sub, same carried state across
# sub-steps. Every configuration below sits inside the config flow's own
# selector ranges: RANGE_SLAB_THERMAL_MASS = (0.1, 60.0),
# RANGE_SLAB_HEAT_TRANSFER = (0.02, 5.0), RANGE_HOUSE_THERMAL_MASS =
# (0.5, 80.0), so none of it is a corner the product forbids.
_grad_parity(
    # Was labelled "stability substeps" and ran at n_sub = 1:
    # `room_thermal_mass` is not a config key (`from_config` reads
    # CONF_HOUSE_THERMAL_MASS = "house_thermal_mass"), and with only the
    # three mass overrides that landed the two-zone ratio was 0.746 x dt
    # against the 1.5 threshold. The key is corrected to the real one at its
    # selector minimum and the slab loop is opened to its selector maximum,
    # which puts every step of the horizon at n_sub = 2.
    True, valve="manual", label="two-zone stability substeps",
    extra_cfg={
        "house_thermal_mass": 0.5, "slab_thermal_mass": 0.5,
        "slab_heat_transfer": 5.0,
        "upper_floor_thermal_mass": 0.3, "lower_floor_thermal_mass": 0.5,
    },
    min_substeps=2,
)
_grad_parity(
    # The single-zone half of the same contract, which had no coverage at
    # all: the slab-mass field at its own selector minimum, everything else
    # stock. One field off the defaults puts the whole horizon at n_sub = 2.
    False, label="single-zone stability substeps",
    extra_cfg={"slab_thermal_mass": 0.1},
    min_substeps=2,
)
_grad_parity(
    # Deeper into the regime (n_sub = 9), where a sub-step the batch
    # integrates with the full dt_hours diverges without bound rather than
    # merely differing -- the shape that made this silent.
    False, label="single-zone deep substeps",
    extra_cfg={"slab_thermal_mass": 0.1, "slab_heat_transfer": 5.0},
    min_substeps=9,
)
# D9-01/D7-03: broaden to the shapes the batched jac now serves -- more
# weather, more initial states, and the non-uniform (DHW-pinned and capped)
# bounds that the uniform-bounds gate used to route to the scalar path.
_grad_parity(False, label="single-zone shoulder mild-start",
             weather_p="shoulder",
             state_over={"room_temperature": 19.0, "buffer_tank_temperature": 42.0})
_grad_parity(True, label="two-zone summer-cool warm-start",
             weather_p="summer_cool",
             state_over={"room_temperature": 22.5, "slab_temperature": 23.5,
                         "buffer_tank_temperature": 51.0})
_grad_parity(False, label="single-zone winter-mild",
             weather_p="winter_mild",
             state_over={"room_temperature": 18.0})
_grad_parity(True, label="two-zone DHW-pinned bounds",
             weather_p="winter_cold", bounds_over="dhw_pinned",
             state_over={"room_temperature": 20.0})
_grad_parity(False, label="single-zone DHW-pinned bounds shoulder",
             weather_p="shoulder", bounds_over="dhw_pinned",
             state_over={"room_temperature": 19.5})
_grad_parity(True, valve="manual", label="two-zone capped bounds summer-cool",
             weather_p="summer_cool", bounds_over="capped",
             state_over={"room_temperature": 21.5})
# R10-COP-PARTLOAD: the part-load derate is elementwise on the batch's power
# rows; the twins must stay bitwise with it on, in both zonings.
_grad_parity(False, label="single-zone part-load derate",
             param_over={"cop_partload_derate": 0.15})
_grad_parity(True, valve="manual", label="two-zone part-load derate",
             param_over={"cop_partload_derate": 0.15})
# Mutation anchor: the batch twin once applied the Carnot lift below the
# reference flow temperature (a boost the scalar never grants) and once
# let np.where's both-arms division poison states with 0/0 NaN -- each
# divergence appeared here as a step-37 room mismatch within seconds.

# The gate itself (D9-01): which bound shapes the batched jac may serve. A
# zero-range entry (lo == hi) used to disqualify the WHOLE solve, because at
# such a variable the one-sided FD step is zero and the divided difference is
# 0/0 = NaN -- and a NaN in a supplied jac kills L-BFGS-B in its first line
# search (status 2, nit 0) where scipy's own estimator survives on a one-ULP
# accident. The fix removes the NaN instead of the fast path: a fixed
# variable's gradient entry is an exact 0.0, which is its true derivative,
# and the batch keeps serving the free ones. One such bound is reachable
# through four shipped default-config routes (a single-phase 16 A fuse guard,
# fuse minus house load, the monthly fuse-advisor shadow solve, a one-slot
# manual plan), and it cost 9,220 simulate-step equivalents per gradient
# against 293 batched -- 31.5x. Restoring the `lo >= hi` rejection here, or
# dropping the fixed-variable zeroing in `_batch_fd_gradient`, fails the
# checks below and the pinned-solve checks in _grad_parity above.
_gate = _grad_optmod._bounds_supported_by_batch
R.section("Which bounds the batched jac may serve (D9-01)")
R.check(
    "uniform bounds are served",
    _gate([(0.0, 6.0)] * 8),
    "the historical #97 shape must keep its fast path",
)
R.check(
    "per-step caps and DHW-pinned headroom are served",
    _gate([(0.0, 6.0), (0.0, 1.2), (0.0, 6.0), (1.4, 6.0)]),
    "non-uniform-but-nonzero bounds are the shapes D9-01 widened the gate for",
)
R.check(
    "a zero-range bound (full DHW block or manual pin) is served, "
    "not refused",
    _gate([(0.0, 6.0)] * 3 + [(0.0, 0.0)])
    and _gate([(0.0, 0.0)] * 4),
    "one pinned step must not put the other 95 on scipy's scalar finite "
    "differences; a fixed variable is fixed, and its gradient entry is 0.0",
)
R.check(
    "degenerate classes are still refused: empty, inverted, non-finite",
    not _gate([]) and not _gate([(2.0, 1.0)]) and not _gate([(0.0, np.inf)]),
    "L-BFGS-B could not solve these on any path",
)
# The fixed-variable entry is exactly 0.0 and nothing else -- asserted on the
# production symbol directly, against an objective whose true gradient at the
# pinned coordinate is large and non-zero, so a stale/copied entry cannot pass.
_gate_x0 = np.array([1.0, 2.0, 0.0])
_gate_bounds = [(0.0, 6.0), (0.0, 6.0), (0.0, 0.0)]


def _gate_obj_batch(mat, *_a):
    m = np.atleast_2d(np.asarray(mat, dtype=float))
    return np.sum((m - np.array([3.0, 1.0, 5.0])) ** 2, axis=1)


_gate_f0 = float(_gate_obj_batch(_gate_x0[None, :])[0])
_gate_grad = _grad_optmod._batch_fd_gradient(
    _gate_obj_batch, (), _gate_x0, _gate_f0, 1e-4, _gate_bounds,
)
R.check(
    "the batched jac's fixed-variable entry is an exact 0.0, not a NaN",
    bool(np.all(np.isfinite(_gate_grad))) and _gate_grad[2] == 0.0,
    f"gradient came back as {_gate_grad}; the pinned coordinate sits 5.0 "
    f"below its objective's minimum, so an unguarded 0/0 shows up here as "
    f"NaN and nowhere else",
)

from scipy.optimize._numdiff import approx_derivative as _gate_approx

R.check(
    "the free entries of that jac still match scipy's own 2-point estimate",
    np.array_equal(
        _gate_grad[:2],
        _gate_approx(
            lambda x: float(_gate_obj_batch(np.asarray(x)[None, :])[0]),
            _gate_x0, method="2-point", abs_step=1e-4, f0=_gate_f0,
            bounds=(np.array([0.0, 0.0, 0.0]), np.array([6.0, 6.0, 0.0])),
        )[:2],
    ),
    "zeroing the fixed entry must not perturb any free one",
)


# ===========================================================================
# #948 (R4-D9-05): the batched objective prices the cost half per batch,
# not per row
# ===========================================================================
R.section("The batched objective prices the cost half per batch (#948)")

# ``objective_batch`` (both the space-only and the with-DHW twin) vectorized
# the simulation in #97 and then re-computed every cost term in a Python
# loop over the B batch rows: measured 97.02 ``_comfort_terms`` entries per
# gradient evaluation, 33.3 % of the solve's wall, 0.86x the entire batched
# simulation it decorates (round 4, D9-05). The property pinned here is the
# recomputation itself, on the production closures lifted out of a real
# solve: ONE ``objective_batch`` call must price every row without entering
# a per-row cost helper, while the physics stays exactly one batched
# simulation. The bitwise row-parity checks beside it are the null control
# every performance change owes: each row must equal the scalar objective
# on the same schedule to the last bit, or the solver's iterate path, the
# plans and the golden fixtures move, and a behaviour change is wearing a
# speedup's clothes.
class _MsStub948:
    """Stands in for the minimize result: the solve machinery after the
    capture reads only .x/.success/.message, and no iteration is wanted."""

    def __init__(self, x):
        self.x = np.asarray(x, dtype=float)
        self.success = True
        self.message = "captured"


_orig_msm_948 = _grad_optmod._multi_start_minimize


def _fit948(arr, n):
    """Tile a profiles series out to n steps (profiles are 96 long)."""
    a = np.asarray(arr, dtype=float)
    return a[:n] if len(a) >= n else np.tile(a, int(np.ceil(n / len(a))))[:n]


def _capture_objectives_948(two_zone, dhw, valve=None, pv_surplus=None,
                            peak=False, masked=False, minute=0):
    """The production objective/objective_batch pair from one real solve.

    ``_multi_start_minimize`` is the one place both twins meet a caller on
    either solve path, so it is replaced for the duration of ``optimize``:
    the pair it was handed is recorded and the first start is returned
    unchanged. Everything before that call -- the horizon, the DHW planner,
    every closure construction -- is the production solve's own machinery.
    """
    cfg = _grad_house(two_zone=two_zone)
    extra = {"mixing_valve_mode": valve} if valve else {}
    params = ThermalParameters.from_config({**cfg, **extra})
    params.dhw_enabled = bool(dhw)
    oc_kw = {}
    if peak:
        # A live capacity tariff with a reachable threshold, so the peak
        # term is active on real rows (disabled, peak_cost's own guard
        # returns 0 before any window arithmetic runs).
        oc_kw.update(peak_price_per_kw=60.0, peak_threshold_kw=0.5)
    if masked:
        # #13 billing factors: peak_hours + offpeak_factor < 1 makes the
        # mask active, so window_factors is non-None and the factors arm
        # of the peak term is live.
        oc_kw.update(peak_hours=((17.0, 20.0),), peak_offpeak_factor=0.5)
    opt = _PvOpt(
        ThermalModel(params),
        _PvOptCfg(
            # 24 h: the production horizon, 96 steps. A first version of
            # this grid ran at 48 steps and a 96-step-only ulp divergence
            # between batched and scalar reductions on CI's x86_64 passed
            # it unseen -- the checks below must cover the production
            # width, not a cheaper one.
            horizon_hours=24, time_step_minutes=15,
            target_temp=cfg["target_temperature"],
            min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"],
            **oc_kw,
        ),
    )
    n = 96
    start = _dt_grad(2026, 1, 15, 0, minute)
    pr = _fit948(_grad_prices("winter_typical", start), n)
    ot, wi, ra, so = (
        _fit948(a, n) for a in _grad_weather("winter_cold", start)
    )
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0,
    )
    captured = {}

    def _msm_948(objective, candidates, bounds, *a, **kw):
        captured["objective"] = objective
        captured["batch"] = kw.get("batch_objective")
        captured["args"] = kw.get("args", a)
        return _MsStub948(candidates[0])

    _grad_optmod._multi_start_minimize = _msm_948
    try:
        opt.optimize(inputs=solve_inputs(
            initial_state=st,
            prices=pr,
            outdoor_temps=ot,
            wind_speeds=wi,
            precipitation=ra,
            solar_radiation=so,
            start_time=start,
            pv_surplus=None if pv_surplus is None else _fit948(pv_surplus, n),
        ))
    finally:
        _grad_optmod._multi_start_minimize = _orig_msm_948
    return captured


from contextlib import contextmanager as _cm948


@_cm948
def _count_entries_948(*targets):
    """Count calls into each (holder, attribute) for the duration."""
    counts = [0] * len(targets)
    saved = []
    for i, (holder, name) in enumerate(targets):
        orig = getattr(holder, name)

        def _wrap(fn, i=i):
            def inner(*a, **kw):
                counts[i] += 1
                return fn(*a, **kw)

            return inner

        setattr(holder, name, _wrap(orig))
        saved.append((holder, name, orig))
    try:
        yield counts
    finally:
        for holder, name, orig in saved:
            setattr(holder, name, orig)


_rng948 = np.random.default_rng(41)
_n948 = 96
# Six schedules spanning the shapes the cost terms branch on: random
# profiles, a flat high plan (a plateau at the peak -- the smooth top-k arm
# of the capacity term when it is enabled), a zero plan, and a bang-bang
# plan (maximum cycling swing).
_m948 = np.vstack([
    _rng948.uniform(0.0, 4.5, size=_n948),
    np.full(_n948, 5.0),
    np.zeros(_n948),
    np.where(np.arange(_n948) % 7 < 2, 5.5, 0.0),
    _rng948.uniform(0.0, 2.5, size=_n948),
    np.full(_n948, 2.0),
])
_B948 = _m948.shape[0]

# The #948 round-7 detector grid. The six schedules above can pass a
# ulp-level divergence by luck, and once did: the terminal accumulation's
# scalar form is Python's builtin sum(), Neumaier-compensated on CPython
# 3.12+, and the batch twin this branch first shipped accumulated plain
# left-to-right vector adds -- 1-2 ulp apart in the terminal term at
# interior solve iterates. Every check on this box was green because its
# interpreter is 3.11, whose sum() is plain accumulation and cannot see
# the class; CI's fast lane (3.14) diverged in both optimality jac races.
# These 25 rows are chosen to hit the compensated-vs-plain difference
# (rng(9): 2 of them diverged under 3.13 pre-fix, 0 post-fix), so the
# row-parity checks below fire on any 3.12+ interpreter. On 3.11 they
# agree either way -- that interpreter is blind to the class, and the
# honest detector for it is the 3.14 lane, not this box.
_rng948t = np.random.default_rng(9)
_m948t = np.vstack(
    [_rng948t.uniform(0.0, 5.5, size=_n948) for _ in range(24)]
    + [np.full(_n948, 5.5)]
)


def _check_batch_cost_948(label, cap):
    """The #948 pins on one captured objective/objective_batch pair."""
    obj, batch, args = cap["objective"], cap["batch"], cap["args"]
    # Rule: entries counted into each production symbol during exactly ONE
    # objective_batch call on the 6-row matrix above.
    with _count_entries_948(
        (_PvOpt, "_comfort_terms"),
        (_grad_optmod, "cycling_penalty"),
        (_grad_optmod, "peak_cost_smooth"),
        (_PvModel, "simulate_trajectory"),
        (_PvModel, "simulate_trajectory_batch"),
    ) as counts:
        values = batch(_m948, *args)
    comfort, cyc, peak, sim_scalar, sim_batch = counts
    R.check(
        f"one objective_batch call prices all {_B948} rows without the "
        f"per-row comfort helper: {label}",
        comfort == 0,
        f"_comfort_terms was entered {comfort} times (round 4, D9-05: "
        f"97.02 entries per gradient, a third of the solve's wall)",
    )
    R.check(
        f"and without the per-row grid-term helpers: {label}",
        cyc == 0 and peak == 0,
        f"cycling_penalty entered {cyc} times, peak_cost_smooth {peak} times "
        f"(the solver's capacity term is the smooth surrogate since #1210; "
        f"the exact peak_cost is billed/published only and never batched)",
    )
    R.check(
        f"the physics stays ONE batched simulation, scalar-free: {label}",
        sim_batch == 1 and sim_scalar == 0,
        f"simulate_trajectory_batch entered {sim_batch} times, "
        f"simulate_trajectory {sim_scalar} times",
    )
    # Null control: row for row, the batch must be the scalar objective on
    # the same schedule, to the last bit -- the parity that keeps the
    # solver's iterate path (and every golden fixture) where it was.
    scalar_rows = [float(obj(_m948[b], *args)) for b in range(_B948)]
    R.check(
        f"every row equals the scalar objective bit for bit: {label}",
        [float(v) for v in values] == scalar_rows,
        "first divergences: "
        + str([i for i in range(_B948)
               if float(values[i]) != scalar_rows[i]][:3]),
    )
    # The same parity on the round-7 detector grid (see _m948t's comment):
    # rows chosen to separate builtin sum()'s compensated accumulation
    # (CPython 3.12+) from any plain left-to-right one, which is the ulp
    # class that diverged CI's 3.14 jac races while this box's 3.11 stayed
    # green. On 3.11 this grid agrees either way; on 3.12+ a twin that
    # accumulates differently than the scalar expression fails here.
    values_t = np.asarray(batch(_m948t, *args), dtype=float)
    scalar_rows_t = [
        float(obj(_m948t[b], *args)) for b in range(_m948t.shape[0])
    ]
    R.check(
        f"every row equals the scalar objective bit for bit on the "
        f"Neumaier grid: {label}",
        [float(v) for v in values_t] == scalar_rows_t,
        "first divergences: "
        + str([i for i in range(_m948t.shape[0])
               if float(values_t[i]) != scalar_rows_t[i]][:3]),
    )


# Three captures spanning both twins and every cost-term branch: the
# space-only twin with two-zone comfort, grid-only energy and no tariff;
# the with-DHW twin single-zone with PV surplus, a live capacity tariff and
# an off-boundary start (the leading partial metering window); and the
# with-DHW twin two-zone behind a manual valve (the terminal cost's split
# buffer-COP arm) with #13-masked windows.
_check_batch_cost_948(
    "two-zone space-only",
    _capture_objectives_948(two_zone=True, dhw=False),
)
_check_batch_cost_948(
    "single-zone with-DHW, PV, capacity tariff, off-boundary start",
    _capture_objectives_948(
        two_zone=False, dhw=True, pv_surplus=np.clip(
            _grad_weather("summer_warm", _dt_grad(2026, 7, 15))[3] / 400.0,
            0.0, None,
        ), peak=True, minute=45,
    ),
)
_check_batch_cost_948(
    "two-zone with-DHW, valve, masked windows",
    _capture_objectives_948(
        two_zone=True, dhw=True, valve="manual", peak=True, masked=True,
    ),
)

# The batch twins under their own branch grids, one level below the
# objective: every arm peak_cost and cycling_penalty branch on, priced per
# row against the scalar function on the same plan. Rule: row b of the
# batch result must equal the scalar function on row b's plan, exactly,
# for every (offset, window length, factors) arm -- separated peaks, the
# full-plateau row (every window tied at the peak, the smooth top-k), a
# plan never above threshold, and a disabled tariff. Since #1210 the
# twin's scalar is peak_cost_smooth -- the SOLVER's term, whose plateau
# arm the batched objective exists to gradient -- while the public
# peak_cost is the exact hard top-k with no batch twin (nothing batches
# it); the extra checks below pin that the two scalars agree everywhere
# the plateau gate does not fire.
from heatpump_optimizer.tariff import peak_cost_batch as _pcb948
from heatpump_optimizer.optimizer import (
    cycling_penalty as _cyc948,
    cycling_penalty_batch as _cpb948,
)

_rows948 = np.vstack([
    _rng948.uniform(0.0, 9.0, size=96),        # separated peaks
    np.full(96, 7.0),                          # full plateau -> smooth top-k
    np.full(96, 1.0),                          # under threshold everywhere
    np.concatenate([np.full(48, 8.0), _rng948.uniform(0.0, 4.0, size=48)]),
    _rng948.uniform(0.0, 2.5, size=96),        # never above threshold
])
_base948 = np.full(96, 1.5)
_facs948 = np.tile(np.array([1.0, 0.0, 0.5, 1.0]), 24)
_bad948 = []
_mismatch948 = []
for _off948 in (0, 1, 3):
    for _win948, _dt948 in ((60, 0.25), (15, 0.25), (45, 0.25)):
        for _fac948 in (None, _facs948[: 96 // max(1, _win948 // 15)]):
            _want948 = [
                peak_cost_smooth(_rows948[_b948], _base948, PeakBilling(3.0, 20.0,
                                 _win948, _dt948, 3, _off948,
                                 window_factors=_fac948))
                for _b948 in range(_rows948.shape[0])
            ]
            _got948 = _pcb948(
                _rows948, _base948, PeakBilling(3.0, 20.0, _win948, _dt948, 3,
                _off948, window_factors=_fac948),
            )
            for _b948 in range(_rows948.shape[0]):
                if _got948[_b948] != _want948[_b948]:
                    _bad948.append(
                        f"off={_off948} win={_win948} fac={_fac948 is not None} "
                        f"row={_b948}: {_got948[_b948]!r} != {_want948[_b948]!r}"
                    )
                if peak_cost_smooth(
                    _rows948[_b948], _base948, PeakBilling(3.0, 20.0, _win948, _dt948,
                    3, _off948, window_factors=_fac948),
                ) > peak_cost(
                    _rows948[_b948], _base948, PeakBilling(3.0, 20.0, _win948, _dt948,
                    3, _off948, window_factors=_fac948),
                ) * (1.0 + 1e-6):
                    _mismatch948.append(
                        f"off={_off948} win={_win948} row={_b948}"
                    )
R.check(
    "peak_cost_batch is peak_cost_smooth on every row, every branch, bit "
    "for bit",
    not _bad948,
    f"first divergences: {_bad948[:3]}",
)
R.check(
    "the surrogate never charges meaningfully more than the exact top-k "
    "(#1210's identity: weights sum to k to the bisection's 1e-6 count "
    "tolerance, so soft <= hard x (1 + 1e-6) on every input; measured "
    "worst excess 2.6e-7 relative)",
    not _mismatch948,
    f"rows where peak_cost_smooth > peak_cost x 1.000001: {_mismatch948[:3]}",
)
R.check(
    "a disabled tariff prices a whole batch as zeros, like the scalar guard",
    bool(np.all(_pcb948(_rows948, _base948, PeakBilling(3.0, 0.0, 60, 0.25)) == 0.0)),
    "peak_price_per_kw <= 0 must short-circuit before any window arithmetic",
)
_cyc_bad948 = [
    _b948
    for _b948 in range(_rows948.shape[0])
    if _cpb948(_rows948[_b948 : _b948 + 1], 2.0, 6.0)[0]
    != _cyc948(_rows948[_b948], 2.0, 6.0)
]
R.check(
    "cycling_penalty_batch is cycling_penalty on every row, bit for bit",
    not _cyc_bad948,
    f"divergent rows: {_cyc_bad948}",
)


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

# v5.7.0 (issue #93): a slab-bearing structure over a crawl-space
# foundation counted the floor twice -- as the structure table's slow
# store and as the foundation's loss path. With radiators the slow mass
# rides house_thermal_mass, so these comparisons see the structural
# store directly. Deleting the subtraction in presets.derive fails the
# equality below, because 0.055 is no longer 0.010.
_rad_kw = dict(
    era=presets.ERA_PRE_1960, heated_area_m2=140,
    lower_emitter=presets.EMITTER_RADIATORS,
)
_slab_over_crawl = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_TIMBER_SLAB,
        foundation=presets.FOUNDATION_CRAWLSPACE, **_rad_kw,
    )
)
_crawl_structure = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_TIMBER_CRAWLSPACE,
        foundation=presets.FOUNDATION_CRAWLSPACE, **_rad_kw,
    )
)
R.check(
    "timber-on-slab over a crawl space is the crawl-space house, exactly",
    _slab_over_crawl["house_thermal_mass"]
    == _crawl_structure["house_thermal_mass"]
    and _slab_over_crawl["slab_thermal_mass"]
    == _crawl_structure["slab_thermal_mass"],
    f"{_slab_over_crawl['house_thermal_mass']} vs "
    f"{_crawl_structure['house_thermal_mass']} kWh/°C",
)
R.check(
    "the subtraction only fires under a crawl-space foundation",
    presets.derive(
        presets.BuildingPreset(
            structure=presets.STRUCTURE_TIMBER_SLAB,
            foundation=presets.FOUNDATION_NONE, **_rad_kw,
        )
    )["house_thermal_mass"]
    > _slab_over_crawl["house_thermal_mass"],
    "a slab on grade keeps the slab's store",
)
_masonry_crawl = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_MASONRY,
        foundation=presets.FOUNDATION_CRAWLSPACE, **_rad_kw,
    )
)
R.check(
    "masonry over a crawl space keeps its walls -- nothing was removed twice",
    _masonry_crawl["house_thermal_mass"]
    > 1.5 * _crawl_structure["house_thermal_mass"],
    f"{_masonry_crawl['house_thermal_mass']} vs "
    f"{_crawl_structure['house_thermal_mass']} kWh/°C -- the rejected "
    "min(slow, 0.010) cap collapsed these to the same number",
)
_concrete_crawl = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_CONCRETE_SLAB,
        foundation=presets.FOUNDATION_CRAWLSPACE, **_rad_kw,
    )
)
R.check(
    "a concrete slab over a crawl space loses the slab but keeps the concrete",
    _crawl_structure["house_thermal_mass"]
    < _concrete_crawl["house_thermal_mass"]
    < presets.derive(
        presets.BuildingPreset(
            structure=presets.STRUCTURE_CONCRETE_SLAB,
            foundation=presets.FOUNDATION_NONE, **_rad_kw,
        )
    )["house_thermal_mass"],
    f"{_concrete_crawl['house_thermal_mass']} kWh/°C",
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
# #1386: normalisation keys on membership, not on "is it radiators". A valid
# non-radiator emitter is a real answer the user gave, so validate() must keep
# it; a mutant that forces the branch (`if True`) overwrites the floor answer
# with radiators. The bogus arm is the null control -- it is clamped under both
# the real guard and the mutant, so it shows the check exercises normalisation
# rather than passing vacuously.
R.check(
    "a valid non-radiator emitter is kept, only an unknown one is clamped",
    presets.BuildingPreset(upper_emitter=presets.EMITTER_FLOOR)
    .validate()
    .upper_emitter
    == presets.EMITTER_FLOOR
    and presets.BuildingPreset(upper_emitter="bogus")
    .validate()
    .upper_emitter
    == presets.EMITTER_RADIATORS,
    "floor upper emitter must survive validate(); only 'bogus' is clamped",
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

# The plausible-bounds refusal is the last thing between a completed fit and
# a downstream consumer that weights it as evidence. The guards above reject
# bad SIGNALS (gains, drift, noise); this one rejects a fit whose recovered
# (tau, UA) is physically impossible even though the regression solved. Build
# a house so over-insulated that the fit lands near UA 0.005 kW/C -- below the
# 0.01 floor -- and require identify() to refuse it rather than report done.
from heatpump_optimizer.sysid import (
    PHASE_RELAX as _SID_RELAX,
    PHASE_STEP as _SID_STEP,
    SysIdSample as _SID_SAMPLE,
)

_impossible = SystemIdentification(SysIdConfig(enabled=True))
_impossible.samples = []
_imp_room, _imp_when = 20.7, datetime(2026, 2, 1, 0, 0, tzinfo=UTC)
for _imp_phase, _imp_power, _imp_steps in (
    (_SID_STEP, 3.0, 12), (_SID_RELAX, 0.0, 19),
):
    for _ in range(_imp_steps):
        _impossible.samples.append(
            _SID_SAMPLE(_imp_when, _imp_room, 0.0, _imp_power, _imp_phase)
        )
        _imp_room += (1.0 / 6.0) * (
            _imp_power + 0.5 - 0.005 * _imp_room
        ) / 6.0
        _imp_when += timedelta(minutes=10)
_impossible_res = _impossible.identify()
R.check(
    "a fit outside the plausible (tau, UA) box is refused, not reported done",
    not _impossible_res.completed
    and "plausible bounds" in (_impossible_res.reason or ""),
    f"completed={_impossible_res.completed} reason={_impossible_res.reason!r} "
    f"ua={_impossible_res.heat_loss_kw_per_c}",
)

repeat = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=30))
repeat.last_run = NOW - timedelta(days=2)
R.check("a recent run blocks another", not repeat.arm(NOW))

# ``identify()`` (the one-state regression) is HARNESS-ONLY (#1395). Every
# production experiment arms with a declared plant, so ``_finish`` routes it to
# ``identify_slab()``; the one-state regression is reached only by a caller
# that declares no plant. A static scan cannot pin this -- ``_finish`` DOES
# call ``identify`` through ``self``, so the member census reads it live (which
# is what ``tests/structure.py``'s #1395 metric checks) -- so the shape is pinned here,
# by counting entries along each sequence. The no-plant arm is the null
# control: it must reach ``identify()``, or a screen that counted 0 everywhere
# would read as proof of a property it never tested.
from heatpump_optimizer.sysid import slab_mode_identifiability as _sid_idable

_sid_plant = ThermalParameters()
R.check(
    "the default plant passes the arm-time identifiability gate",
    _sid_idable(_sid_plant, SysIdConfig(enabled=True))[0],
    "production arms with a declared plant; the gate must accept it, or the "
    "production sequence the pin below drives is not the production one",
)

_sid_calls = {"identify": 0, "identify_slab": 0}
_sid_identify = SystemIdentification.identify
_sid_identify_slab = SystemIdentification.identify_slab


def _sid_count(method, key):
    def _wrapper(self, *args, **kwargs):
        _sid_calls[key] += 1
        return method(self, *args, **kwargs)

    return _wrapper


SystemIdentification.identify = _sid_count(_sid_identify, "identify")
SystemIdentification.identify_slab = _sid_count(_sid_identify_slab, "identify_slab")


def _sid_drive(with_plant):
    experiment = SystemIdentification(
        SysIdConfig(
            enabled=True,
            settle_hours=0.5,
            step_hours=2.0,
            relax_hours=2.0,
            max_excursion_c=5.0,
        )
    )
    if with_plant:
        experiment.arm(night, plant=_sid_plant)
    else:
        experiment.arm(night)
    house_capacity, house_ua, outdoor, cop = 8.0, 0.2, 0.0, 3.0
    room, when = 20.0, night
    for _ in range(40):
        power = experiment.step(
            now=when, room_temp=room, outdoor_temp=outdoor, price=0.55,
            price_horizon=cheap, learner_samples=5, max_power_kw=5.0, cop=cop,
        )
        room += (
            (power or 0.0) * cop - house_ua * (room - outdoor)
        ) / house_capacity * 0.25
        when += timedelta(minutes=15)
    return experiment


_sid_before = dict(_sid_calls)
_sid_prod = _sid_drive(with_plant=True)
_sid_prod_calls = {k: _sid_calls[k] - _sid_before[k] for k in _sid_calls}
R.check(
    "the production sequence (declared plant) never enters identify()",
    _sid_prod.phase == PHASE_DONE
    and _sid_prod_calls["identify"] == 0
    and _sid_prod_calls["identify_slab"] == 1,
    f"phase={_sid_prod.phase} identify={_sid_prod_calls['identify']} "
    f"identify_slab={_sid_prod_calls['identify_slab']}",
)

_sid_before = dict(_sid_calls)
_sid_harness = _sid_drive(with_plant=False)
_sid_harness_calls = {k: _sid_calls[k] - _sid_before[k] for k in _sid_calls}
R.check(
    "the no-plant harness path still reaches identify()",
    _sid_harness.phase == PHASE_DONE
    and _sid_harness_calls["identify"] >= 1
    and _sid_harness_calls["identify_slab"] == 0,
    f"phase={_sid_harness.phase} identify={_sid_harness_calls['identify']} "
    f"identify_slab={_sid_harness_calls['identify_slab']}",
)

SystemIdentification.identify = _sid_identify
SystemIdentification.identify_slab = _sid_identify_slab


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

# D12-01 (#1404): the buffer/DHW guards keyed on `state.<field> is not None`
# over floats that never become None, so a 35 L buffer the plant's own
# `describe_setup()` reports as `is_store: false` was still published as a
# storage component. The real signal is `buffer_is_store` (valve + volume) and
# `dhw_enabled`, not the never-None temperature.
_plain_p = ThermalParameters()
_plain_s = ThermalState(
    room_temperature=21.0, slab_temperature=23.0, outdoor_temperature=0.0,
)
_plain_v = battery_view.build(
    _plain_p, _plain_s, comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=65.0, cop=3.2,
)
_plain_names = {c.name for c in _plain_v.components}
R.check(
    "a 35 L buffer without a valve is not published as a store",
    "buffer_tank" not in _plain_names,
    "buffer_is_store is False but the component was still listed",
)
R.check(
    "a disabled DHW tank is not published",
    "dhw_tank" not in _plain_names,
    "dhw_enabled is False",
)

# Null controls: the fix drops only what is not a store, not every tank.
_store_p = ThermalParameters(buffer_tank_volume=750.0, mixing_valve_mode="manual")
_store_v = battery_view.build(
    _store_p, _plain_s, comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=65.0, cop=3.2,
)
R.check(
    "a store-sized throttled buffer IS published",
    any(c.name == "buffer_tank" for c in _store_v.components),
    "buffer_is_store is True",
)
_dhw_p = ThermalParameters(dhw_enabled=True)
_dhw_v = battery_view.build(
    _dhw_p, _plain_s, comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=65.0, cop=3.2,
)
R.check(
    "an enabled DHW tank IS published",
    any(c.name == "dhw_tank" for c in _dhw_v.components),
    "dhw_enabled is True",
)



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
    _commanded_split = Coord._commanded_split
    # v5.3.0: the split is masked by the *observed* operating mode. With no
    # mode entity the signals default to full capability and nothing is
    # masked, which is the state every pre-v5.3.0 install is in.
    _pump_signals = PumpSignals()


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


from heatpump_optimizer.accuracy import MeasuredCop as _CopRecord  # noqa: E402


class _CopGate:
    _learn_measured_cop = Coord._learn_measured_cop
    _fold_measured_cop = Coord._fold_measured_cop
    _fold_cop_evidence = Coord._fold_cop_evidence
    _commanded_power = Coord._commanded_power
    _commanded_split = Coord._commanded_split
    _cop_reference_curve = Coord._cop_reference_curve
    _COP_CURVE_SHARE = Coord._COP_CURVE_SHARE
    _apply_cop_scale = Coord._apply_cop_scale

    def __init__(
        self, outdoor: float, signals=None, action=None, defrost=None
    ) -> None:
        # A modest gap: v4.0.5's tracking gate discards samples whose
        # commanded-vs-measured mismatch is too large to be efficiency at
        # all, and this fixture is about the frost-band *split*, not the
        # magnitude — it has to stay on the efficiency side of that gate.
        self._measured_power = 2.6
        self._current_action = dict(action) if action else {"power": 3.0}
        # v5.3.0: with no mode entity the signals are the full-capability
        # default, which masks nothing and selects the space curve — the
        # v5.1.5 behaviour this fixture was written against.
        self._pump_signals = signals if signals is not None else PumpSignals()
        # v5.3.0: an empty window has observed=False, which keeps the
        # whole-band frost exclusion — the v5.1.5 behaviour.
        self._defrost_window = defrost if defrost is not None else DefrostWindow()
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(
            room_temperature=21.0, outdoor_temperature=outdoor
        )
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._cop_ratio_ewma = None
        self._measured_cop = _CopRecord()
        self._immersion_active = False
        # #1067: the supply/return learner the reference curve consults.
        # Inert unless a test gives it a supply reading, so every check
        # written before it existed judges against the bare curve exactly
        # as it did.
        self._flow_bias = flow_lift.FlowCurveBias()
        self.cop_health_calls: list = []

    def _learning_frozen(self, *entities):
        return None

    def _observe_cop_health(self, observed_cop, dhw_curve=False):
        # T4a's health watch is exercised on the real coordinator; this
        # stub only gates the frost-band split. It takes the curve flag
        # because the watch now keeps a baseline per curve — a stub that
        # did not would hide a caller passing the wrong one.
        self.cop_health_calls.append((observed_cop, dhw_curve))
        return None

    def _fold_capacity_envelope(self, observed_cop, heat_kw=None):
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

# D3-02: the trust-region clamp (``max_step``/``np.clip``) around
# ``_learn_measured_cop``'s EWMA update is the only thing that bounds *how
# fast* a single persistently bad sample can move ``cop_scale`` — a sensor
# glitch or a CT-clamp misconfiguration walks the tracking-error EWMA gate
# open over a handful of intervals (rejected samples still update the EWMA)
# and then, once accepted, would be free to jump the scale in one step by
# however far the raw EWMA update wants, absent the clamp. Every existing
# check above feeds a single, tame sample and never observes the clamp
# itself engage. This asserts the clamp's actual contract directly: no
# accepted sample may move ``cop_scale`` by more than ``cop_scale *
# COP_LEARNING_MAX_STEP`` in one call, however far the raw EWMA target sits.
from heatpump_optimizer.coordinator import (  # noqa: E402
    COP_LEARNING_MAX_STEP as _COP_MAX_STEP,
)

_clamp_gate = _CopGate(outdoor=8.0, action={"power": 3.0})
_clamp_gate._thermal_params.max_electrical_power = 3.0
_clamp_gate._measured_power = 0.9
_clamp_prev_scale = _clamp_gate._cop_scale
_clamp_max_observed_step = 0.0
for _ in range(30):
    _clamp_gate._learn_measured_cop()
    _clamp_step = abs(_clamp_gate._cop_scale - _clamp_prev_scale)
    if _clamp_gate._cop_samples > 0:
        _clamp_max_observed_step = max(_clamp_max_observed_step, _clamp_step)
        R.check(
            "an extreme COP sample moves cop_scale by at most the clamp's max_step",
            _clamp_step
            <= _clamp_prev_scale * _COP_MAX_STEP + 1e-9,
            f"step {_clamp_step:.5f} exceeded {_clamp_prev_scale * _COP_MAX_STEP:.5f} "
            f"(prev scale {_clamp_prev_scale:.5f})",
        )
    _clamp_prev_scale = _clamp_gate._cop_scale
R.check(
    "the clamp scenario actually engaged the clamp at least once",
    _clamp_gate._cop_samples >= 8 and _clamp_max_observed_step > 0.0,
    "a fixture that never triggers the clamp cannot prove it bounds anything",
)

# --- Standby loss is not hot water usage ----------------------------------
#
# The tank cools all the time — about 0.42 °C/h for a 55 °C tank at the
# default rate — and a drop of that size passed the raw 0.15 °C gate every
# idle hour, teaching a phantom draw into all 24 slots and washing the real
# morning/evening pattern towards flat. Only the drop *beyond* expected
# standby decay is usage.
import asyncio as _aio


class _DhwUsage(DhwProfileLearner):
    """The learner itself (W5-G9), with persistence stubbed out."""

    def __init__(self) -> None:
        super().__init__(
            FakeHass(),
            "dhw-usage",
            **_owned_params(ThermalParameters()),
            frozen=lambda *_: None,
            heating_active=lambda: False,
            external_heat_active=lambda: False,
        )
        self.cooling_rate = 0.3
        self.hourly_profile = [1.0] * 24
        # v4.0.0 T3 (#18): the learner also teaches the day-type arrays.
        self.profile_weekday = [1.0] * 24
        self.profile_weekend = [1.0] * 24
        self.daytype_samples = [0, 0]
        self.daytype_last_day = ["", ""]

    async def async_save_profile(self) -> None:
        pass


_standby_only = _DhwUsage()
_aio.run(
    _standby_only.async_learn_usage(
        55.0, 0.42, 1.0, 3, False  # exactly the expected standby drop at 55 °C
    )
)
R.check(
    "a pure standby drop teaches no draw",
    _standby_only.hourly_profile == [1.0] * 24,
    "0.42 °C/h at 55 °C is the tank cooling, not a shower at 3 am",
)
_real_draw = _DhwUsage()
_aio.run(_real_draw.async_learn_usage(55.0, 2.0, 1.0, 7, False))
R.check(
    "a genuine draw still reinforces its hour",
    _real_draw.hourly_profile[7] > 1.0
    and _real_draw.hourly_profile[7] > _real_draw.hourly_profile[3],
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
        self._config = EntryConfig()
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)

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

    async def async_wait_for_read(self) -> None:
        """The fake never holds a read in flight (D1-s2-52's wait)."""


from heatpump_optimizer.drift import Cusum as _Cusum


class _LearnPersist:
    _async_save_thermal_learning = Coord._async_save_thermal_learning
    _async_load_thermal_learning = Coord._async_load_thermal_learning
    # The save path serialises through the same producer the snapshots
    # use (T4a); a stub with its own dict would test a second format.
    _thermal_learning_payload = Coord._thermal_learning_payload
    _load_t4b_learners = Coord._load_t4b_learners
    _apply_cop_scale = Coord._apply_cop_scale
    _house_heat_loss_anchor = Coord._house_heat_loss_anchor
    _heat_loss_anchors = Coord._heat_loss_anchors
    _reanchor_house_heat_loss_scale = Coord._reanchor_house_heat_loss_scale
    _void_heat_loss_learners = Coord._void_heat_loss_learners
    _apply_learner_payloads = Coord._apply_learner_payloads

    def __init__(self, store) -> None:
        self._thermal_learning_store = store
        # The entry's settings: the payload records the power basis (#2239).
        self._config = {}
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
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
        # #1067: the payload producer above is the production one, so a
        # learner it serialises has to exist here too.
        self._flow_bias = flow_lift.FlowCurveBias()
        self._freq_fallback = False
        self._measured_cop = _CopRecord()

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

# #238: the loader's try wraps async_load but not stored.get / int(), so a
# list, a string, 7, inf sample counts and a wrapped freq_map raise out of
# the task. thermal_learning is the store the panel showed does not self-heal.
R.section("Store loaders discard corrupt payloads (#238)")

for _junk in ([1, 2, 3], "nonsense", 7):
    _junk_store = _FakeLearnStore()
    _junk_store.saved = _junk
    try:
        _aio.run(_LearnPersist(_junk_store)._async_load_thermal_learning())
        _survived = True
        _detail = ""
    except Exception as _err:  # noqa: BLE001
        _survived = False
        _detail = f"{type(_err).__name__}: {_err}"
    R.check(
        f"thermal_learning {type(_junk).__name__} payload is discarded, not raised",
        _survived,
        _detail,
    )

_inf_store = _FakeLearnStore()
_inf_store.saved = {
    "buffer_cooling_rate": 1.0,
    "buffer_cooling_samples": float("inf"),
}
try:
    _aio.run(_LearnPersist(_inf_store)._async_load_thermal_learning())
    _inf_ok = True
    _inf_detail = ""
except Exception as _err:  # noqa: BLE001
    _inf_ok = False
    _inf_detail = f"{type(_err).__name__}: {_err}"
R.check(
    "thermal_learning inf sample count is discarded, not raised",
    _inf_ok,
    _inf_detail,
)

_wrap_store = _FakeLearnStore()
_wrap_store.saved = {"freq_map": {"0": {"v": [1.0, 1]}}}
try:
    _aio.run(_LearnPersist(_wrap_store)._async_load_thermal_learning())
    _wrap_ok = True
    _wrap_detail = ""
except Exception as _err:  # noqa: BLE001
    _wrap_ok = False
    _wrap_detail = f"{type(_err).__name__}: {_err}"
R.check(
    "thermal_learning wrapped freq_map is discarded, not raised",
    _wrap_ok,
    _wrap_detail,
)

import json as _json773

# #773: the JSON *string* "nan" is RFC 8259 / orjson-clean and reaches
# float(); a bare NaN token does not. The finite sibling control is 0.
_nan773 = _json773.loads(
    '{"solar_aperture":{"n":"nan","mx":0.0,"my":0.0,"cov":0.0,"var":0.0,"scale":1.0}}'
)
_inf773 = _json773.loads(
    '{"solar_aperture":{"n":"Infinity","mx":0.0,"my":0.0,"cov":0.0,"var":0.0,"scale":1.0}}'
)
_fin773 = _json773.loads(
    '{"solar_aperture":{"n":"12","mx":0.0,"my":0.0,"cov":0.0,"var":0.0,"scale":1.0}}'
)
for _label773, _payload773, _want_n773 in (
    ("JSON-string nan", _nan773, 0.0),
    ("JSON-string Infinity", _inf773, 0.0),
    ("JSON-string finite n", _fin773, 12.0),
):
    _store773 = _FakeLearnStore()
    _store773.saved = _payload773
    _holder773 = _LearnPersist(_store773)
    try:
        _aio.run(_holder773._async_load_thermal_learning())
        _ok773 = True
        _detail773 = ""
    except Exception as _err773:  # noqa: BLE001
        _ok773 = False
        _detail773 = f"{type(_err773).__name__}: {_err773}"
    R.check(
        f"thermal_learning {_label773} does not raise",
        _ok773,
        _detail773,
    )
    R.check(
        f"thermal_learning {_label773} leaves aperture n at {_want_n773}",
        _holder773._solar_aperture["n"] == _want_n773,
        repr(_holder773._solar_aperture),
    )

from harness import FakeEntry as _StoreFakeEntry, FakeHass as _StoreFakeHass
from homeassistant.helpers.storage import _reset_store_disk as _reset_stores

def _store_path(obj, dotted):
    """Resolve ``a.b.c`` on ``obj`` -- the DHW stores moved into the learner (W5-G9)."""
    for part in dotted.split("."):
        obj = getattr(obj, part)
    return obj


_STORE_LOADERS = (
    ("_dhw_learner.profile_store", "_dhw_learner.async_load_profile"),
    ("_thermal_learning_store", "_async_load_thermal_learning"),
    ("_price_model_store", "_async_load_price_model"),
    ("_ledger_store", "_async_load_ledger"),
    ("_accuracy_store", "_async_load_accuracy"),
    ("_energy_store", "_async_load_energy_totals"),
)


def _store_coord():
    _reset_stores()
    return Coord(
        _StoreFakeHass({}),
        _StoreFakeEntry(
            data={
                "tibber_token": "x",
                "weather_entity": "weather.home",
                "indoor_temp_entity": "sensor.indoor",
                "outdoor_temp_entity": "sensor.outdoor",
                "dhw_temp_entity": "sensor.dhw",
                "heat_pump_power_entity": "sensor.hp_power",
            }
        ),
    )


# #773: _learning_view's unguarded int() over learner state. The store
# route is the JSON string; in-memory nan is what that load used to leave.
_view773 = _store_coord()
try:
    _view773._solar_aperture["n"] = float(_json773.loads('"nan"'))
    _view773._capacity_envelope[0] = [1.0, float(_json773.loads('"nan"'))]
    _view773._cop_baseline[(0, False)] = [3.0, float(_json773.loads('"nan"'))]
    _pub773 = _view773._learning_view()
    _view773_ok = True
    _view773_detail = ""
except Exception as _err773:  # noqa: BLE001
    _pub773 = {}
    _view773_ok = False
    _view773_detail = f"{type(_err773).__name__}: {_err773}"
R.check(
    "a non-finite aperture n does not wedge _learning_view",
    _view773_ok and _pub773.get("solar_aperture", {}).get("samples") == 0,
    _view773_detail or repr(_pub773.get("solar_aperture")),
)
_load773 = _store_coord()


async def _fake_nan773(_p=_nan773):
    return _p


_load773._thermal_learning_store.async_load = _fake_nan773
try:
    _aio.run(_load773._async_load_thermal_learning())
    _cycle773 = _load773._learning_view()
    _cycle773_ok = True
    _cycle773_detail = ""
except Exception as _err773:  # noqa: BLE001
    _cycle773 = {}
    _cycle773_ok = False
    _cycle773_detail = f"{type(_err773).__name__}: {_err773}"
R.check(
    "JSON-string nan in the thermal store does not wedge the learning view",
    _cycle773_ok and _cycle773.get("solar_aperture", {}).get("samples") == 0,
    _cycle773_detail or repr(_cycle773.get("solar_aperture")),
)


for _store_attr, _loader_name in _STORE_LOADERS:
    for _junk in ([1, 2, 3], "nonsense", 7):
        _coord = _store_coord()
        _aio.run(_store_path(_coord, _store_attr).async_save(_junk))
        try:
            _aio.run(_store_path(_coord, _loader_name)())
            _ok = True
            _detail = ""
        except Exception as _err:  # noqa: BLE001
            _ok = False
            _detail = f"{type(_err).__name__}: {_err}"
        R.check(
            f"{_loader_name} discards a stored {type(_junk).__name__}",
            _ok,
            _detail,
        )

_dhw_junk = _store_coord()
_aio.run(_dhw_junk._dhw_learner.profile_store.async_save({"hourly_profile": ["x"] * 24}))
try:
    _aio.run(_dhw_junk._dhw_learner.async_load_profile())
    _dhw_ok = True
    _dhw_detail = ""
except Exception as _err:  # noqa: BLE001
    _dhw_ok = False
    _dhw_detail = f"{type(_err).__name__}: {_err}"
R.check(
    "dhw_profile 24-string hourly_profile is discarded, not raised",
    _dhw_ok,
    _dhw_detail,
)

# #923 (R4-D1-02): one corrupt scalar inside the accuracy store -- a JSON
# number where the ``samples`` list belongs -- raised straight out of
# ``AccuracyTracker.from_dict`` (``for raw in data.get("samples", []) or []``
# iterates whatever is there) and out of ``_async_load_accuracy``, the one
# loader whose decode no barrier guards. The raise left the stored peaks,
# defrost table and operation mode unloaded, and the next ordinary cycle's
# save overwrote all three on disk with defaults -- silently, with
# ``last_update_success`` still True. ``from_dict`` is that decode's
# corruption barrier, like the sibling loaders': a non-list ``samples`` is
# skipped with a warning, and every other learned field must still load.
import logging as _d102_logging  # noqa: E402


class _D102Capture(_d102_logging.Handler):
    """Records (level, message) from the package logger, one arm's worth."""

    def __init__(self):
        super().__init__(level=_d102_logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append((record.levelno, record.getMessage()))


#: A month of learned state. Every value is money- or physics-bearing:
#: ``peaks`` is what the capacity tariff is billed on, ``defrost`` is the
#: learned output derate, ``mode`` is the user's own setting.
_D102_LEARNED = {
    "defrost": {
        "version": 2,
        "factors": [[0.80, 0.90]] * 6,
        "counts": [[4, 5]] * 6,
        "duty": [[0.10, 0.20]] * 6,
        # Written with its duty since v5.3.0: a duty grid without its counts
        # is a corrupt store, which loads with a warning (D1-s4-03).
        "duty_counts": [[3, 2]] * 6,
    },
    "peaks": {"month": "2026-09", "peaks": [7.4, 6.8, 5.9]},
    "mode": "economy",
}


def _d102_seed(samples):
    """A coordinator whose accuracy store 'disk' holds ``samples`` where the
    list belongs, with the learned fields otherwise well-formed."""
    coord = _store_coord()
    coord.hass.states.set("sensor.indoor", FakeState("21.4"))
    coord.hass.states.set("sensor.outdoor", FakeState("-3.0"))
    _aio.run(
        coord._accuracy_store.async_save(
            {
                "accuracy": {
                    "samples": samples,
                    "lead_sigma": {},
                    "lead_counts": {},
                    "lead_pending": [],
                },
                "dhw_accuracy": {
                    "samples": [],
                    "lead_sigma": {},
                    "lead_counts": {},
                    "lead_pending": [],
                },
                **_D102_LEARNED,
            }
        )
    )
    return coord


def _d102_cycle(coord):
    """One ordinary update cycle: read inputs, publish, persist -- exactly
    what ``_async_update_data`` does every interval."""
    _aio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    _aio.run(coord._async_save_accuracy())
    return _aio.run(coord._accuracy_store.async_load())


def _d102_kept(store):
    """Which of the three learned fields the cycle left intact, by name."""
    kept = []
    if (
        store.get("peaks") or {}
    ).get("peaks") == _D102_LEARNED["peaks"]["peaks"]:
        kept.append("peaks")
    if (
        store.get("defrost") or {}
    ).get("factors") == _D102_LEARNED["defrost"]["factors"]:
        kept.append("defrost_factors")
    if store.get("mode") == _D102_LEARNED["mode"]:
        kept.append("mode")
    return kept


def _d102_run(samples):
    """Load + one cycle under log capture; (raised, store, records)."""
    coord = _d102_seed(samples)
    capture = _D102Capture()
    logger = _d102_logging.getLogger("heatpump_optimizer")
    logger.addHandler(capture)
    raised, store = "", {}
    try:
        try:
            _aio.run(coord._async_load_accuracy())
            store = _d102_cycle(coord)
        except Exception as err:  # noqa: BLE001
            raised = f"{type(err).__name__}: {err}"
    finally:
        logger.removeHandler(capture)
    return raised, store, capture.records


# Null control: a well-formed store round-trips its learned fields through
# load + one cycle untouched, and logs nothing at WARNING or above.
_d102_raised, _d102_store, _d102_records = _d102_run([])
R.check(
    "a healthy accuracy store round-trips its learned fields (control)",
    not _d102_raised
    and _d102_kept(_d102_store) == ["peaks", "defrost_factors", "mode"],
    _d102_raised or f"kept {_d102_kept(_d102_store)}",
)
R.check(
    "a healthy accuracy store loads without a warning (control)",
    not [lvl for lvl, _ in _d102_records if lvl >= _d102_logging.WARNING],
    f"{len(_d102_records)} records",
)

# The corrupt shapes: a JSON scalar where the samples list belongs. The
# load must not raise, the three learned fields must survive the next
# cycle's save, and the skip must be visible in the log.
for _d102_bad in (1.0, True):
    _d102_raised, _d102_store, _d102_records = _d102_run(_d102_bad)
    _d102_shape = type(_d102_bad).__name__
    R.check(
        f"a non-list 'samples' ({_d102_shape}) loads without raising",
        not _d102_raised,
        _d102_raised,
    )
    R.check(
        f"a non-list 'samples' ({_d102_shape}) keeps the learned peaks, "
        "defrost factors and mode on disk",
        _d102_kept(_d102_store) == ["peaks", "defrost_factors", "mode"],
        f"kept {_d102_kept(_d102_store)}",
    )
    R.check(
        f"a non-list 'samples' ({_d102_shape}) is skipped with a warning",
        any(
            lvl >= _d102_logging.WARNING and "samples" in msg
            for lvl, msg in _d102_records
        ),
        f"{len(_d102_records)} records",
    )

from heatpump_optimizer.price_model import PriceShapeModel as _FuzzPSM
from heatpump_optimizer.wear import StartCounter as _FuzzStarts
from heatpump_optimizer.accuracy import AccuracyTracker as _FuzzAcc
from heatpump_optimizer.dhw_draws import DrawStats as _FuzzDraws


def _from_dict_survives(fn):
    try:
        fn()
        return True, ""
    except Exception as err:  # noqa: BLE001
        return False, f"{type(err).__name__}: {err}"


_ok, _detail = _from_dict_survives(
    lambda: _FuzzPSM.from_dict(
        {"shapes": [[1.0] * 24, [1.0] * 24], "days": [float("inf"), 7]}
    )
)
R.check("PriceShapeModel.from_dict swallows inf day counts", _ok, _detail)
_ok, _detail = _from_dict_survives(
    lambda: _FuzzPSM.from_dict(
        {"shapes": [["x"] * 24, [1.0] * 24], "days": [7, 7]}
    )
)
R.check("PriceShapeModel.from_dict swallows non-numeric shapes", _ok, _detail)
_ok, _detail = _from_dict_survives(
    lambda: _FuzzStarts.from_dict({"lifetime": float("inf")})
)
R.check("StartCounter.from_dict swallows inf lifetime", _ok, _detail)

# The streak is what makes "START_HYSTERESIS_SAMPLES consecutive samples"
# true. A sample that AGREES with the state already held is not part of an
# edge, so it must reset the streak: otherwise a steady running signal keeps
# the streak alive across agreeing samples and the next real edge is
# confirmed on fewer samples than the promise. Drive a steady above-threshold
# signal while the counter already believes it is running.
from heatpump_optimizer.const import START_HYSTERESIS_SAMPLES as _FUZZ_HYST

_steady = _FuzzStarts()
_steady.running = True
_steady_confirmed = 0
for _i in range(_FUZZ_HYST + 2):
    if _steady.observe(NOW + timedelta(minutes=_i), 2.0, 1.0, False):
        _steady_confirmed += 1
R.check(
    "a steady running signal restarts the streak and confirms no start",
    _steady_confirmed == 0 and _steady._streak == 0 and _steady.lifetime == 0,
    f"confirmed {_steady_confirmed}, streak {_steady._streak}, "
    f"lifetime {_steady.lifetime}",
)

# The check above cannot fail on the reset: there `above == self.running`
# holds from the very first sample, so `_streak` never leaves 0 and the
# reset line is dead weight in it. The reset shows itself only when the
# streak is ALIVE as the agreeing sample arrives. Walk above -> below ->
# above: sample 1 starts a streak of 1, sample 2 agrees with the held False
# state, and sample 3 is the second "above" -- but NON-consecutive, so it
# must start a fresh streak of 1, not confirm. Measured: intact -> streak
# 1 -> 0 -> 1, no confirmation (lifetime 0); with `self._streak = 0`
# deleted -> streak 1 -> 1, sample 3 confirms a start (running True,
# lifetime 1).
_noncon = _FuzzStarts()
_noncon_first = _noncon.observe(NOW, 2.0, 1.0, False)
_noncon_streak_first = _noncon._streak
_noncon_agree = _noncon.observe(NOW + timedelta(minutes=1), 0.0, 1.0, False)
_noncon_streak_agree = _noncon._streak
_noncon_third = _noncon.observe(NOW + timedelta(minutes=2), 2.0, 1.0, False)
R.check(
    "above->below->above: the agreeing sample resets the streak, no start",
    not _noncon_first
    and _noncon_streak_first == 1
    and not _noncon_agree
    and _noncon_streak_agree == 0
    and not _noncon_third
    and _noncon._streak == 1
    and not _noncon.running
    and _noncon.lifetime == 0,
    f"confirmed ({_noncon_first!r},{_noncon_agree!r},{_noncon_third!r}), "
    f"streak {_noncon_streak_first}->{_noncon_streak_agree}->{_noncon._streak}, "
    f"running {_noncon.running}, lifetime {_noncon.lifetime}",
)
_ok, _detail = _from_dict_survives(
    lambda: _FuzzAcc.from_dict({"lead_counts": {"1.0": float("inf")}})
)
R.check("AccuracyTracker.from_dict swallows inf lead counts", _ok, _detail)
_ok, _detail = _from_dict_survives(
    lambda: _FuzzDraws.from_dict(
        {"reservoirs": {"06:00-08:30": [10**30]}}
    )
)
R.check("DrawStats.from_dict swallows a huge-int reservoir event", _ok, _detail)

# -- R5-D1-05 (#1296): one non-finite value in a persisted store is
# quarantined at its loader -------------------------------------------------
#
# The round-5 store fuzz measured 220 NaN leaf paths published from ONE
# seeded NaN in the DHW profile store, non-finite learned state from three
# more loaders (draw-stats open occurrence, peak-tracker window
# accumulators and peaks, curve-learner bias), and the corrupt value still
# on disk after the cycles -- no log, reset or repair. The loaders now
# treat a non-finite scalar like any other unusable one: replace it with
# the default the loader already uses for absent data. Every check below
# has its null control: the same payload with finite values loads
# unchanged. (np.clip CLAMPS +-inf, so each guard tests the whole non-
# finite family even where only NaN survives the clamp.)
import math as _nf_math

_nf_learner = _DhwUsage()
# A real learner's fresh seed: the shipped pattern through its projection
# (_DhwUsage overwrites its own seed with a flat profile).
_nf_default = DhwProfileLearner(
    FakeHass(), "nf", **_owned_params(ThermalParameters()),
    frozen=lambda *a: None, heating_active=lambda: False,
    external_heat_active=lambda: False,
).hourly_profile
_nf_profile = _nf_learner.normalize_profile(
    [1.0] * 6 + [float("nan")] + [1.0] * 17
)
_nf_profile_inf = _nf_learner.normalize_profile(
    [1.0] * 6 + [float("inf")] + [1.0] * 17
)
R.check(
    "one non-finite entry quarantines the stored hourly profile to the default pattern",
    _nf_profile == _nf_default and _nf_profile_inf == _nf_default,
    f"nan -> {_nf_profile[:3]!r}..., inf -> {_nf_profile_inf[:3]!r}...; "
    f"default {_nf_default[:3]!r}...",
)
_nf_clean = _DhwUsage().normalize_profile([0.5] * 24)
R.check(
    "a healthy stored profile still normalizes (null control)",
    len(_nf_clean) == 24
    and all(_nf_math.isfinite(v) for v in _nf_clean),
    f"{_nf_clean[:3]!r}...",
)

_nf_draws = _FuzzDraws.from_dict(
    {
        "reservoirs": {"06:00-08:30": [8.0, float("inf")]},
        "open_label": "06:00-08:30",
        "open_date": "2026-01-15",
        "open_kwh": float("inf"),
    }
)
_nf_draws_nan = _FuzzDraws.from_dict({"open_kwh": float("nan")})
R.check(
    "a non-finite draw occurrence resets to 0 kWh; finite events and labels survive",
    _nf_draws.reservoirs["06:00-08:30"] == [8.0]
    and _nf_draws._open_label == "06:00-08:30"
    and _nf_draws._open_date == "2026-01-15"
    and _nf_math.isfinite(_nf_draws._open_kwh)
    and _nf_draws._open_kwh >= 0.0
    and _nf_draws_nan._open_kwh == 0.0,
    f"open_kwh {_nf_draws._open_kwh!r} / {_nf_draws_nan._open_kwh!r}, "
    f"reservoirs {_nf_draws.reservoirs!r}",
)

_nf_peak = PeakTracker.from_dict(
    {
        "month": "2026-01",
        "peaks": [5.2, float("inf"), 4.1, float("nan")],
        "window_sum": float("inf"),
        "window_samples": 3,
        "window_wsum": float("inf"),
        "window_weight": float("inf"),
    }
)
R.check(
    "non-finite peaks and window accumulators are dropped at load; finite ones survive",
    _nf_peak.peaks == [5.2, 4.1]
    and _nf_peak.month == "2026-01"
    and _nf_peak._window_samples == 3
    and _nf_math.isfinite(_nf_peak._window_sum)
    and _nf_math.isfinite(_nf_peak._window_wsum)
    and _nf_math.isfinite(_nf_peak._window_weight),
    f"peaks {_nf_peak.peaks!r}, sums "
    f"{_nf_peak._window_sum!r}/{_nf_peak._window_wsum!r}/"
    f"{_nf_peak._window_weight!r}",
)

from heatpump_optimizer.curve_learning import CurveLearner as _NFCurve

_nf_curve = _NFCurve.from_dict(
    {"bias": float("nan"), "comfortable_days": 2}
)
_nf_curve_inf = _NFCurve.from_dict({"bias": float("inf")})
R.check(
    "a non-finite curve-learner bias resets to the neutral 0 K; evidence survives",
    _nf_curve.bias == 0.0
    and _nf_curve.comfortable_days == 2
    and _nf_curve_inf.bias == 0.0,
    f"bias {_nf_curve.bias!r} / {_nf_curve_inf.bias!r}, "
    f"days {_nf_curve.comfortable_days}",
)

_huge_energy = _store_coord()
_aio.run(
    _huge_energy._energy_store.async_save({"space_cost": 10**30})
)
try:
    _aio.run(_huge_energy._async_load_energy_totals())
    _huge_ok = True
    _huge_detail = ""
except Exception as _err:  # noqa: BLE001
    _huge_ok = False
    _huge_detail = f"{type(_err).__name__}: {_err}"
R.check(
    "energy_totals huge-int accumulator is discarded, not raised",
    _huge_ok,
    _huge_detail,
)

# --- The learned heat-loss scale survives an options edit (issue #86) --------
#
# The store now records the UA the scale was fitted against, and the
# loader re-expresses the scale against the configuration in force with
# the law U_eff' = (1 - phi)*nameplate_new + phi*measured_UA, in absolute
# UA on the zone-total basis. Every number below comes from the
# production confidence curve and threshold -- imported, never
# re-implemented here (the rule tests/README.md states, and the failure
# mode that rule was written for).
from heatpump_optimizer.coordinator import (
    HOUSE_LOSS_MAX_STEP as _HL_STEP,
    house_loss_confidence as _hl_phi,
)

R.section("The learned heat-loss scale is re-anchored, not restored verbatim")


class _CountingLearnStore(_FakeLearnStore):
    """The fake store, counting saves so the gated write can be pinned."""

    def __init__(self) -> None:
        super().__init__()
        self.saves = 0

    async def async_save(self, data) -> None:
        self.saves += 1
        await super().async_save(data)


def _anchored_store(coef, scale, samples):
    """A store as the coordinator itself would have written it."""
    holder = _LearnPersist(_CountingLearnStore())
    holder._thermal_params.heat_loss_coefficient = coef
    holder._apply_house_heat_loss_scale(scale)
    holder._house_heat_loss_samples = samples
    _aio.run(holder._async_save_thermal_learning())
    return holder._thermal_learning_store


def _reloaded(coef, store):
    """A fresh coordinator over that store, configured with `coef`."""
    fresh = _LearnPersist(store)
    fresh._thermal_params.heat_loss_coefficient = coef
    _aio.run(fresh._async_load_thermal_learning())
    return fresh


# The questionnaire re-answer from the issue, at convergence: 150 m²,
# 1980-2005 -> pre-1960, configured U 0.12 -> 0.2325 with a learned
# scale of 1.25 in the store.
_OLD, _NEW, _SCALE = 0.12, 0.2325, 1.25
_conv = _reloaded(_NEW, _anchored_store(_OLD, _SCALE, 300))
_phi_conv = _hl_phi(300)
_expected_eff = (1.0 - _phi_conv) * _NEW + _phi_conv * _SCALE * _OLD
R.check(
    "a converged scale is re-anchored onto the new nameplate, not restored",
    abs(_conv._house_heat_loss_scale * _NEW - _expected_eff) < 1e-9,
    f"effective {_conv._house_heat_loss_scale * _NEW:.4f} kW/°C, "
    f"expected {_expected_eff:.4f}",
)
R.check(
    "which is no longer ~1.94x the UA the learner measured",
    abs(_conv._house_heat_loss_scale * _NEW - _SCALE * _OLD) < (1.0 - _phi_conv) * _NEW + 1e-9,
    f"effective {_conv._house_heat_loss_scale * _NEW:.4f} vs measured "
    f"{_SCALE * _OLD:.4f} kW/°C",
)

# Below the re-anchor threshold, today's behaviour stands: the law is a
# measured regression on exactly that path (the 30-hop walk), and the
# learner's EWMA closes a small edit on its own.
_sub = _reloaded(_OLD * 1.03, _anchored_store(_OLD, _SCALE, 300))
R.check(
    "a sub-threshold nameplate edit keeps the stored scale verbatim",
    abs(_sub._house_heat_loss_scale - _SCALE) < 1e-12
    and 0.03 < _HL_STEP,
    f"scale {_sub._house_heat_loss_scale} vs stored {_SCALE}",
)

# Round 1's failure mode stays dead: an install that has learned
# nothing keeps its configuration edits.
_zero = _reloaded(_NEW, _anchored_store(_OLD, 1.0, 0))
R.check(
    "an unlearned install keeps its configuration edit",
    abs(_zero._house_heat_loss_scale - 1.0) < 1e-12,
    f"scale {_zero._house_heat_loss_scale} -- the config edit was "
    "silently cancelled, the round-1 regression",
)

# The clamp is decided before clipping: a measurement that cannot be
# expressed against the new nameplate resets explicitly, never onto a
# bound the next edit would read as the learner's own signal.
_reset = _reloaded(0.4, _anchored_store(0.05, 1.0, 300))
R.check(
    "an inexpressible measurement resets, not clips onto a bound",
    abs(_reset._house_heat_loss_scale - 1.0) < 1e-12
    and _reset._house_heat_loss_samples == 0,
    f"scale {_reset._house_heat_loss_scale}, "
    f"{_reset._house_heat_loss_samples} samples",
)

# The gated write: exactly one save adopts the anchor or persists the
# re-anchor, and a second load over the same configuration is a no-op.
_gated_store = _anchored_store(_OLD, _SCALE, 300)
_saves_before = _gated_store.saves
_gated = _reloaded(_NEW, _gated_store)
R.check(
    "a re-anchor persists exactly once",
    _gated_store.saves - _saves_before == 1,
    f"{_gated_store.saves - _saves_before} save(s)",
)
R.check(
    "and the persisted anchor is the configuration now in force",
    abs(_gated_store.saved["house_heat_loss_anchor"] - _NEW) < 1e-9,
    f"anchor {_gated_store.saved['house_heat_loss_anchor']}",
)
_gated2 = _reloaded(_NEW, _gated_store)
_saves_mid = _gated_store.saves
R.check(
    "a second load over the same configuration re-anchors nothing",
    abs(_gated2._house_heat_loss_scale - _gated._house_heat_loss_scale) < 1e-12
    and _gated_store.saves == _saves_mid,
    f"scale {_gated2._house_heat_loss_scale}, "
    f"{_gated_store.saves - _saves_mid} extra save(s)",
)

# Round 1's theorem, killed by the basis: the law is written on the
# zone TOTAL, so a single-zone edit in a two-zone house moves the scale
# the right way -- the learned LEVEL survives instead of going
# sign-negative on the upper nameplate.
_tz_store = _CountingLearnStore()
_tz = _LearnPersist(_tz_store)
_tz._thermal_params.two_zone_enabled = True
_tz._thermal_params.upper_floor_heat_loss = 0.10
_tz._thermal_params.lower_floor_heat_loss = 0.10
_tz._apply_lower_floor_loss_ratio(1.0)
_tz._apply_house_heat_loss_scale(2.0)
_tz._house_heat_loss_samples = 300
_aio.run(_tz._async_save_thermal_learning())
_tz_new = _LearnPersist(_tz_store)
_tz_new._thermal_params.two_zone_enabled = True
_tz_new._thermal_params.upper_floor_heat_loss = 0.20
_tz_new._thermal_params.lower_floor_heat_loss = 0.10
_tz_new._apply_lower_floor_loss_ratio(1.0)
_aio.run(_tz_new._async_load_thermal_learning())
_phi_tz = _hl_phi(300)
# The total at the ratio the load now holds: it is re-anchored too (#2239).
_tz_base = 0.20 + 0.10 * _tz_new._lower_floor_loss_ratio
_tz_eff = _tz_new._house_heat_loss_scale * _tz_base
R.check(
    "a two-zone edit re-anchors on the zone total, not the upper zone",
    abs(_tz_eff - ((1.0 - _phi_tz) * _tz_base + _phi_tz * 0.40)) < 1e-9
    and _tz_eff > 0.30,
    f"effective total {_tz_eff:.4f} kW/°C (learned level was 0.40)",
)

# The weekly-snapshot restore path honours the same law: a rollback to
# a pre-edit snapshot no longer re-installs the pre-edit correction.
_snap = _LearnPersist(_CountingLearnStore())
_snap._thermal_params.heat_loss_coefficient = _NEW
_snap._apply_house_heat_loss_scale(1.0)
_snap._house_heat_loss_samples = 300
_snap._apply_learner_payloads(
    {
        "thermal_learning": {
            "house_heat_loss_scale": _SCALE,
            "house_heat_loss_anchor": _OLD,
        }
    }
)
R.check(
    "a snapshot restore re-anchors a pre-edit scale, not restores it",
    abs(_snap._house_heat_loss_scale * _NEW - _expected_eff) < 1e-9,
    f"effective {_snap._house_heat_loss_scale * _NEW:.4f} kW/°C after "
    "rollback",
)

# --- The lower-floor ratio is re-anchored with the scale (#2239) -------------
#
# The ratio multiplies the lower nameplate the way the scale multiplies the
# zone total, so an options edit of the lower nameplate, or a snapshot from
# before one, re-expressed the scale alone and handed the lower zone's learned
# heat loss to the upper one. Adding a power meter changes what the learners
# were fitted against (commanded power carries every delivery shortfall), so
# it re-anchors both at zero confidence. Real coordinators over the stock
# two-zone house; every expectation is a property, never the law restated.
from harness import FakeEntry as _ra_entry  # noqa: E402
from profiles import house as _ra_house  # noqa: E402

R.section("The lower-floor ratio is re-anchored with the scale (#2239)")

_RA_S, _RA_R, _RA_NS, _RA_NR = 1.567, 1.922, 310, 147
_RA_CFG = dict(_ra_house(two_zone=True, dhw=False), lower_floor_temp_entity="sensor.lower")
_RA_U, _RA_L = _RA_CFG["upper_floor_heat_loss"], _RA_CFG["lower_floor_heat_loss"]
_RA_RESEED = dict(_RA_CFG, upper_floor_heat_loss=_RA_U * _RA_S,
                  lower_floor_heat_loss=_RA_L * _RA_R * _RA_S)
_RA_METERED = dict(_RA_CFG, heat_pump_power_entity="sensor.hp_power")


def _ra_coord(cfg, store):
    c = Coord(FakeHass({}), _ra_entry(data=cfg))
    c._thermal_learning_store = store
    return c


def _ra_learned(cfg, scale=_RA_S, ratio=_RA_R, samples=(_RA_NS, _RA_NR)):
    """A store the coordinator itself wrote, with the learners at this state."""
    src = _ra_coord(cfg, _CountingLearnStore())
    src._apply_house_heat_loss_scale(scale)
    src._apply_lower_floor_loss_ratio(ratio)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = samples
    _aio.run(src._async_save_thermal_learning())
    return src._thermal_learning_store


def _ra_zones(c):
    """(upper, lower) effective heat loss, kW/°C, as the model applies it."""
    p = c._thermal_params
    s = c._house_heat_loss_scale
    return p.upper_floor_heat_loss * s, p.lower_floor_heat_loss * c._lower_floor_loss_ratio * s


def _ra_reload(cfg, store):
    c = _ra_coord(cfg, store)
    _aio.run(c._async_load_thermal_learning())
    return c


_ra_want = (_RA_U * _RA_S, _RA_L * _RA_R * _RA_S)
_ra_seed = _ra_reload(_RA_RESEED, _ra_learned(_RA_CFG))
_ra_got = _ra_zones(_ra_seed)
R.check(
    "an options reseed of both zones keeps each zone's learned heat loss",
    all(abs(g / w - 1.0) < 1e-4 for g, w in zip(_ra_got, _ra_want)),
    f"upper {_ra_got[0]:.4f} lower {_ra_got[1]:.4f} vs learned "
    f"{_ra_want[0]:.4f} {_ra_want[1]:.4f} kW/°C (scale "
    f"{_ra_seed._house_heat_loss_scale:.3f}, ratio {_ra_seed._lower_floor_loss_ratio:.3f})",
)
_ra_store2 = _ra_seed._thermal_learning_store
_ra_saves = _ra_store2.saves
_ra_again = _ra_reload(_RA_RESEED, _ra_store2)
R.check(
    "and a second load over the reseeded configuration re-anchors nothing",
    _ra_zones(_ra_again) == _ra_got and _ra_store2.saves == _ra_saves,
    f"{_ra_zones(_ra_again)} vs {_ra_got}, {_ra_store2.saves - _ra_saves} extra save(s)",
)

# The ratio multiplies the nameplate SPLIT: an edit scaling both nameplates
# alike (the scale adopted, the split kept) leaves the ratio verbatim. The
# law blends toward the nameplate at partial confidence, so re-anchoring the
# ratio here would pull the lower zone a ratio-confidence share off.
_ra_keep = _ra_reload(
    dict(_RA_CFG, upper_floor_heat_loss=_RA_U * _RA_S, lower_floor_heat_loss=_RA_L * _RA_S),
    _ra_learned(_RA_CFG),
)
_ra_got_keep = _ra_zones(_ra_keep)
R.check(
    "an edit that keeps the nameplate split keeps the ratio and each zone",
    _ra_keep._lower_floor_loss_ratio == _RA_R
    and all(abs(g / w - 1.0) < 1e-4 for g, w in zip(_ra_got_keep, _ra_want)),
    f"ratio {_ra_keep._lower_floor_loss_ratio}, upper {_ra_got_keep[0]:.4f} lower "
    f"{_ra_got_keep[1]:.4f} vs learned {_ra_want[0]:.4f} {_ra_want[1]:.4f} kW/°C",
)

# The weekly-snapshot restore: a pre-reseed snapshot rolled back onto the
# reseeded configuration is the same edit seen from the other side.
_ra_snap = {"thermal_learning": dict(_ra_learned(_RA_CFG).saved)}
_ra_rest = _ra_reload(_RA_RESEED, _CountingLearnStore())
_ra_rest._apply_learner_payloads(_ra_snap)
_ra_got_rest = _ra_zones(_ra_rest)
R.check(
    "a pre-reseed snapshot restored after the reseed keeps each zone",
    all(abs(g / w - 1.0) < 1e-4 for g, w in zip(_ra_got_rest, _ra_want)),
    f"upper {_ra_got_rest[0]:.4f} lower {_ra_got_rest[1]:.4f} vs learned "
    f"{_ra_want[0]:.4f} {_ra_want[1]:.4f} kW/°C",
)

# Zero evidence: an install that has learned nothing keeps its edit, at
# either nameplate -- round 1's failure mode, now on the ratio.
_ra_zero = _ra_reload(
    dict(_RA_CFG, lower_floor_heat_loss=_RA_L * 2.0),
    _ra_learned(_RA_CFG, scale=1.0, ratio=1.0, samples=(0, 0)),
)
R.check(
    "an unlearned install keeps a lower-nameplate edit",
    _ra_zero._house_heat_loss_scale == 1.0 and _ra_zero._lower_floor_loss_ratio == 1.0,
    f"scale {_ra_zero._house_heat_loss_scale}, ratio {_ra_zero._lower_floor_loss_ratio}",
)

# On the clamp: a ratio that cannot be expressed against the new lower
# nameplate resets explicitly, never clips onto a bound.
_ra_far = _ra_reload(
    dict(_RA_CFG, lower_floor_heat_loss=_RA_L * 40.0), _ra_learned(_RA_CFG)
)
R.check(
    "an inexpressible ratio resets, not clips onto a bound",
    _ra_far._lower_floor_loss_ratio == 1.0 and _ra_far._lower_floor_loss_samples == 0,
    f"ratio {_ra_far._lower_floor_loss_ratio}, {_ra_far._lower_floor_loss_samples} samples",
)
# A reset ratio carries no evidence, so the scale beside it lands where the
# same edit lands over a store whose ratio never learned: a scale solved
# jointly with the inexpressible ratio kept that ratio's share of the total.
_ra_none = _ra_reload(
    dict(_RA_CFG, lower_floor_heat_loss=_RA_L * 40.0),
    _ra_learned(_RA_CFG, samples=(_RA_NS, 0)),
)
R.check(
    "the scale beside a reset ratio is the scale with no ratio evidence",
    abs(_ra_far._house_heat_loss_scale / _ra_none._house_heat_loss_scale - 1.0) < 1e-12
    and _ra_none._lower_floor_loss_ratio == 1.0,
    f"scale {_ra_far._house_heat_loss_scale:.6f} after the reset vs "
    f"{_ra_none._house_heat_loss_scale:.6f} unlearned (ratio {_ra_none._lower_floor_loss_ratio})",
)

# The mirror: a scale that cannot be expressed against the new nameplates
# resets, so the ratio beside it lands where the same edit lands over a store
# whose scale never learned and whose ratio holds the same lower-zone
# measurement (ratio s*r). A ratio solved jointly with the inexpressible
# scale kept that scale's share of the lower zone (fix review of #2698).
_RA_SR_EDIT = dict(_RA_CFG, upper_floor_heat_loss=_RA_U * 1.8, lower_floor_heat_loss=_RA_L * 1.4)
_ra_sr = _ra_reload(_RA_SR_EDIT, _ra_learned(_RA_CFG, scale=0.5, ratio=0.8))
_ra_sr_twin = _ra_reload(
    _RA_SR_EDIT, _ra_learned(_RA_CFG, scale=1.0, ratio=0.5 * 0.8, samples=(0, _RA_NR))
)
R.check(
    "the ratio beside a reset scale is the ratio with no scale evidence",
    abs(_ra_sr._house_heat_loss_scale - 1.0) < 1e-12
    and (_ra_sr._house_heat_loss_samples, _ra_sr._lower_floor_loss_samples) == (0, _RA_NR)
    and abs(_ra_sr._lower_floor_loss_ratio / _ra_sr_twin._lower_floor_loss_ratio - 1.0) < 1e-12
    and _ra_sr._lower_floor_loss_ratio != 1.0,
    f"scale {_ra_sr._house_heat_loss_scale:.6f}, ratio {_ra_sr._lower_floor_loss_ratio:.6f} "
    f"after the reset vs {_ra_sr_twin._lower_floor_loss_ratio:.6f} with no scale evidence, "
    f"samples {_ra_sr._house_heat_loss_samples}/{_ra_sr._lower_floor_loss_samples}",
)

# And where the ratio solved again beside the reset scale is inexpressible
# too, both reset and both say so: the edit lands on the configuration.
_ra_sr2 = _ra_reload(
    dict(_RA_CFG, upper_floor_heat_loss=_RA_U * 0.6, lower_floor_heat_loss=_RA_L * 0.5),
    _ra_learned(_RA_CFG, scale=2.0, ratio=2.5),
)
R.check(
    "a reset scale whose ratio is inexpressible beside it resets both",
    abs(_ra_sr2._house_heat_loss_scale - 1.0) < 1e-12
    and (_ra_sr2._lower_floor_loss_ratio, _ra_sr2._house_heat_loss_samples,
         _ra_sr2._lower_floor_loss_samples) == (1.0, 0, 0),
    f"scale {_ra_sr2._house_heat_loss_scale:.6f}, ratio {_ra_sr2._lower_floor_loss_ratio}, "
    f"samples {_ra_sr2._house_heat_loss_samples}/{_ra_sr2._lower_floor_loss_samples}",
)

# G-ID-3: a power meter added under a learned state. The learners replayed
# commanded power until now, so what they hold is void against the metered
# basis: both start again from the configuration, and the store says so once.
_ra_meter_store = _ra_learned(_RA_CFG)
_ra_meter_saves = _ra_meter_store.saves
_ra_meter = _ra_reload(_RA_METERED, _ra_meter_store)
R.check(
    "adding a power meter re-anchors both learners at zero confidence",
    (_ra_meter._house_heat_loss_scale, _ra_meter._lower_floor_loss_ratio,
     _ra_meter._house_heat_loss_samples, _ra_meter._lower_floor_loss_samples)
    == (1.0, 1.0, 0, 0)
    and _ra_meter_store.saves - _ra_meter_saves == 1,
    f"scale {_ra_meter._house_heat_loss_scale}, ratio "
    f"{_ra_meter._lower_floor_loss_ratio}, samples {_ra_meter._house_heat_loss_samples}/"
    f"{_ra_meter._lower_floor_loss_samples}, {_ra_meter_store.saves - _ra_meter_saves} save(s)",
)
_ra_meter2 = _ra_reload(_RA_METERED, _ra_learned(_RA_METERED))
R.check(
    "a metered store reloaded metered keeps both learners verbatim",
    (_ra_meter2._house_heat_loss_scale, _ra_meter2._lower_floor_loss_ratio) == (_RA_S, _RA_R),
    f"scale {_ra_meter2._house_heat_loss_scale}, ratio {_ra_meter2._lower_floor_loss_ratio}",
)
# Removing the meter voids nothing: metered evidence is the better basis.
_ra_unmeter = _ra_reload(_RA_CFG, _ra_learned(_RA_METERED))
R.check(
    "removing the power meter keeps both learners verbatim",
    (_ra_unmeter._house_heat_loss_scale, _ra_unmeter._lower_floor_loss_ratio) == (_RA_S, _RA_R),
    f"scale {_ra_unmeter._house_heat_loss_scale}, ratio {_ra_unmeter._lower_floor_loss_ratio}",
)
# A store written before the basis was recorded proves nothing about it:
# the load adopts the configuration in force, it does not void the learners.
_ra_old = _ra_learned(_RA_CFG)
_ra_old.saved = {k: v for k, v in _ra_old.saved.items() if k != "house_heat_loss_basis"}
_ra_pre = _ra_reload(_RA_METERED, _ra_old)
R.check(
    "a store without a recorded basis keeps both learners on a meter add",
    (_ra_pre._house_heat_loss_scale, _ra_pre._lower_floor_loss_ratio) == (_RA_S, _RA_R)
    and _ra_old.saved.get("house_heat_loss_basis") == "metered",
    f"scale {_ra_pre._house_heat_loss_scale}, ratio {_ra_pre._lower_floor_loss_ratio}, "
    f"basis adopted {_ra_old.saved.get('house_heat_loss_basis')!r}",
)

# The pair's own refusals: a total not positive on either side has nothing
# to re-express against, the guard ``_reanchor_house_heat_loss_scale`` used
# to hold on both anchors (a zero live total divides the law by zero).
from heatpump_optimizer.thermal_model import heat_loss_anchor_pair as _ra_pair  # noqa: E402

_ra_refused = {
    label: _ra_v
    for label, _ra_v in (
        ("no live total", _ra_pair((0.3, 0.1), (0.0, 0.1), 1.0, void=True, step=0.05)),
        ("a stored total at the floor", _ra_pair((1e-9, 0.0), (0.3, 0.0), 1.0, void=True, step=0.05)),
    )
}
R.check(
    "the anchor pair refuses a total not positive on either side, void or not",
    all(v is None for v in _ra_refused.values())
    and _ra_pair((0.3, 0.1), (0.3, 0.1), 1.0, void=True, step=0.05) is not None,
    f"{_ra_refused!r} -- and a void basis over the same live total must still re-express",
)

# Every bound is inclusive, as the store's domains and the clip are: a value
# landing on its bound is expressible, and a change of exactly ``step`` is
# below the gate, on the total and on the split alike. The ``1e-9`` floors
# are exclusive: an anchor on the floor is no lower zone. Each input is exact
# in binary, so the boundary is hit, not approached.
from heatpump_optimizer.thermal_model import reanchor_heat_loss as _ra_law  # noqa: E402

_RA_BOUNDS = {"scale_bounds": (0.3, 3.0), "ratio_bounds": (0.3, 3.0)}
_ra_edges = {
    "scale on its ceiling": _ra_law((3.0, 0.0), (1.0, 0.0), 1.0, 1.0, (1.0, 0.0), **_RA_BOUNDS)
    == (3.0, 1.0, False, False),
    "scale on its floor": _ra_law((0.3, 0.0), (1.0, 0.0), 1.0, 1.0, (1.0, 0.0), **_RA_BOUNDS)
    == (0.3, 1.0, False, False),
    "ratio on its ceiling": _ra_law((1.0, 1.0), (1.0, 0.5), 1.0, 1.5, (1.0, 1.0), **_RA_BOUNDS)
    == (1.0, 3.0, False, False),
    "ratio on its floor": _ra_law((1.0, 1.0), (1.0, 2.0), 1.0, 0.6, (1.0, 1.0), **_RA_BOUNDS)
    == (1.0, 0.3, False, False),
    "total moved exactly step": _ra_pair((1.0, 0.0), (1.25, 0.0), 1.0, void=False, step=0.25) is None,
    "split moved exactly step": _ra_pair((2.0, 1.0), (2.25, 1.25), 1.0, void=False, step=0.25) is None,
    "lower anchor on the floor": _ra_pair((3.0, 1e-9), (3.0, 1.0), 1.0, void=False, step=0.05) is None,
    "upper zone on the floor": _ra_pair((3.0, 1.0), (2e-9, 1e-9), 1.0, void=False, step=0.05)
    == ((3.0, 0.0), (2e-9, 0.0)),
}
R.check(
    "a bound is inclusive and a step is below the gate, on every learner and zone",
    all(_ra_edges.values()),
    f"failed: {[k for k, v in _ra_edges.items() if not v]}",
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
    _WS(_bl_out, _bl_zero, _bl_zero, _bl_zero), _bl_state, 0.25
)
_bl_setback, _ = _bl_opt._compute_baseline_power(
    _WS(_bl_out, _bl_zero, _bl_zero, _bl_zero),
    _bl_state,
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
# A house that needs more than the pump can draw gets the pump's nameplate, the
# cap a real thermostat runs into, never the demand the pump cannot meet.
_bl_capped, _ = _PvOpt(_PvModel(_PvParams(max_electrical_power=1.0)), _PvOptCfg(
    target_temp=21.0))._compute_baseline_power(
    _WS(_bl_out, _bl_zero, _bl_zero, _bl_zero), _bl_state, 0.25)
R.check(
    "a demand past the pump's nameplate holds the reference at max_electrical_power",
    float(np.max(_bl_capped)) == 1.0 and float(np.min(_bl_capped)) == 1.0,
    f"reference {np.min(_bl_capped):.3f}..{np.max(_bl_capped):.3f} kW against a 1.0 kW pump",
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
    "flow_curve_bias",          # #1067 learned by flow_lift, set per solve
    "internal_gains_profile",   # #53 learned per-hour, set per solve
    "cop_scale",                # learned from measured power
    "cop_reference_temp",       # a property of the COP curve, not the house
    "internal_gains",           # not exposed in the config flow
    "dhw_windows",              # parsed separately from a string spec
    "dhw_weekly_windows",       # parsed with it (#3): the same spec's day view
    "dhw_holiday_windows",      # parsed from CONF_HOLIDAY_DHW_WINDOWS (#700)
    "dhw_day_windows",          # parsed from the seven #1260 override keys
    "two_zone_enabled",         # inferred from presence, overridable by mode
    # dhw_enabled is overridable via CONF_DHW_ENABLED; inferred when absent.
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
    A field whose legal range stops at or below 0.5 on the default config
    (the part-load derate's band limit is 4/9 on 1-5 kW) refuses that
    sentinel, so 0.25 is tried after it.
    """
    default_value = getattr(ThermalParameters.from_config({}), name)
    if isinstance(default_value, bool):
        sentinels = [not default_value]
    else:
        sentinels = [v for v in (0.5, 0.25) if v != default_value]
    for candidate in dir(hp_const):
        if not candidate.startswith("CONF_"):
            continue
        for sentinel in sentinels:
            try:
                built = ThermalParameters.from_config(
                    {getattr(hp_const, candidate): sentinel}
                )
            except Exception:
                continue
            if getattr(built, name, None) == sentinel:
                return candidate
    return None


# Volume is gated on the furnace toggle (#463): a lone CONF_WOOD_TANK_VOLUME
# does not infer a tank, so the single-key probe cannot see it.
toggle_gated = {"wood_tank_volume"}
probe = {name: reachable(name) for name in declared - runtime_only - validated_enums}

unreachable = sorted(
    n for n, k in probe.items() if k is None and n not in toggle_gated
)
R.check(
    "every configurable parameter is reachable from a config key",
    not unreachable,
    ", ".join(unreachable),
)
_wf_vol_on = ThermalParameters.from_config(
    {
        hp_const.CONF_WOOD_FURNACE_ENABLED: True,
        hp_const.CONF_WOOD_TANK_VOLUME: 0.5,
    }
)
R.check(
    "wood tank volume is reachable once the furnace toggle is on",
    _wf_vol_on.wood_tank_volume == 0.5,
    f"got {_wf_vol_on.wood_tank_volume!r}",
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

# D3-03: ``update_ecl110_displace_state`` models the ECL110's real PI/PID
# response as a first-order lag (``effective += alpha*(cmd-effective)``),
# not instant tracking. Every other reference to
# ``ecl110_effective_displace``/``ecl110_displace_command`` in this suite
# checks presence or static config round-tripping, never a value trajectory
# — so deleting the lag term entirely (making effective == cmd on tick one)
# passes unnoticed. This asserts the trajectory shape directly: a step
# command from rest must land strictly between the old and new value after
# one tick (proving lag exists) and must still not have fully arrived after
# one tick, but must converge to the command over enough ticks.
_ecl_model = ThermalModel(ThermalParameters())
_ecl_state = ThermalState(room_temperature=21.0, outdoor_temperature=0.0)
R.check(
    "ECL110 effective displace starts at rest",
    _ecl_state.ecl110_effective_displace == 0.0,
)
_ecl_model.update_ecl110_displace_state(_ecl_state, displace_command=4.0, dt_hours=0.25)
R.check(
    "one tick of a step command lags strictly behind it, not tracks instantly",
    0.0 < _ecl_state.ecl110_effective_displace < 4.0,
    f"got {_ecl_state.ecl110_effective_displace!r} after one tick; a deleted "
    "first-order lag would jump straight to 4.0",
)
_ecl_after_one_tick = _ecl_state.ecl110_effective_displace
_ecl_model.update_ecl110_displace_state(_ecl_state, displace_command=4.0, dt_hours=0.25)
R.check(
    "a second tick keeps closing the gap towards the command, not overshooting",
    _ecl_after_one_tick < _ecl_state.ecl110_effective_displace < 4.0,
)
for _ in range(400):
    _ecl_model.update_ecl110_displace_state(_ecl_state, displace_command=4.0, dt_hours=0.25)
R.check(
    "enough ticks let the lag converge on the commanded value",
    abs(_ecl_state.ecl110_effective_displace - 4.0) < 1e-6,
)

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
    "an explicit dhw_enabled False wins over leftover volume",
    ThermalParameters.from_config(
        {
            hp_const.CONF_DHW_TANK_VOLUME: 200.0,
            hp_const.CONF_DHW_ENABLED: False,
        }
    ).dhw_enabled
    is False,
)
R.check(
    "an explicit dhw_enabled True enables hot water with no other keys",
    ThermalParameters.from_config(
        {hp_const.CONF_DHW_ENABLED: True}
    ).dhw_enabled
    is True,
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
R.check(
    "holiday DHW windows parse from CONF_HOLIDAY_DHW_WINDOWS",
    ThermalParameters.from_config(
        {hp_const.CONF_HOLIDAY_DHW_WINDOWS: "10:00-12:00"}
    ).dhw_holiday_windows
    == [(10.0, 12.0)],
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
#
#    v5.1.7: the `return + 0.5` stand-in is gone. It was the number the card
#    plotted as the house temperature — a floor return of 27.5 °C drew a
#    "house" trace at 28.0 while the upper zone sat at 22.1 — and it was
#    judged against the same comfort band as the measured zone. Without a
#    thermometer the honest stand-in is the room temperature, which is what
#    the no-floor-return branch has always used.
st = _lower_after_update(
    {**_BASE, "sensor.ret": FakeState("28.0", unit="°C")},
    floor_return_temp_entity="sensor.ret",
)
R.check(
    "a floor return sensor never stands in for the lower zone's air temperature",
    abs(st.lower_floor_temperature - 21.0) < 1e-6,
    f"got {st.lower_floor_temperature}",
)
R.check(
    "and the floor return still does its real job: the slab estimate",
    abs(st.slab_temperature - (0.7 * 29.0 + 0.3 * 22.0)) < 1e-6,
    f"got {st.slab_temperature}",
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
    "the estimated path no longer pins slab-to-room at 0.5 K",
    abs(_delta_inferred - 0.5) > 1.0,
    f"delta {_delta_inferred:.3f}",
)
R.check(
    "and a real sensor moves it further still, from a measurement",
    _delta_measured > _delta_inferred,
    f"delta {_delta_measured:.3f} (estimated {_delta_inferred:.3f})",
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
    "an unavailable lower-floor sensor falls back to the room temperature",
    abs(st.lower_floor_temperature - 21.0) < 1e-6,
    f"got {st.lower_floor_temperature}",
)

# 7. The watchdog has to cover it. A key absent from INPUT_MAX_AGE_MINUTES gets
#    no age limit at all, which disables staleness detection silently.
R.check(
    "the new sensor has a staleness limit like the other room sensors",
    hp_const.INPUT_MAX_AGE_MINUTES.get("lower_floor_temp_entity")
    == hp_const.INPUT_MAX_AGE_MINUTES.get("indoor_temp_entity"),
)

# 8. The owner's report, reproduced end to end (v5.1.7). Two-zone, a floor
#    return sensor, no lower-floor thermometer -- exactly his configuration.
#    The published lower zone used to read the return water; the card plotted
#    that as a house temperature, and 28 °C on the chart is what "the optimizer
#    is taking the house to 28 degrees" was.
_owner_states = {
    "sensor.indoor": FakeState("22.07", unit="°C"),
    "sensor.outdoor": FakeState("-8.0", unit="°C"),
    "sensor.ret": FakeState("27.5", unit="°C"),
}
_owner = _zone_coord(_owner_states, floor_return_temp_entity="sensor.ret")
_asyncio.run(_owner._update_current_state())
_owner_state = _owner._current_state
R.check(
    "the reported zone temperatures no longer differ by six degrees",
    abs(_owner_state.lower_floor_temperature - 22.07) < 1e-6
    and abs(_owner_state.upper_floor_temperature - 22.07) < 1e-6,
    f"upper {_owner_state.upper_floor_temperature} "
    f"lower {_owner_state.lower_floor_temperature}",
)

# 9. And the user is told the zone is modelled rather than measured, because a
#    plausible number with nothing behind it is what made this hard to see.
_owner_issues = [
    i for i in getattr(_owner.hass, "issues", [])
    if i[1] == "lower_floor_modelled"
]
R.check(
    "an unmeasured lower zone raises the repair issue",
    len(_owner_issues) == 1
    and _owner_issues[0][2].get("translation_key") == "lower_floor_modelled",
    f"{_owner_issues}",
)
_asyncio.run(_owner._update_current_state())
R.check(
    "raised once, not once per cycle",
    len([
        i for i in getattr(_owner.hass, "issues", [])
        if i[1] == "lower_floor_modelled"
    ]) == 1,
)
_measured_coord = _zone_coord(
    {**_owner_states, "sensor.lower": FakeState("20.4", unit="°C")},
    floor_return_temp_entity="sensor.ret",
    lower_floor_temp_entity="sensor.lower",
)
_asyncio.run(_measured_coord._update_current_state())
R.check(
    "a configured thermometer raises nothing",
    not [
        i for i in getattr(_measured_coord.hass, "issues", [])
        if i[1] == "lower_floor_modelled"
    ],
)
_single = _Coord(
    _FakeHass(dict(_BASE)),
    _FakeEntry(data={
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }),
)
_asyncio.run(_single._update_current_state())
R.check(
    "a single-zone house is never told about a zone it does not have",
    not [
        i for i in getattr(_single.hass, "issues", [])
        if i[1] == "lower_floor_modelled"
    ],
)
# 10. Clearing it, through the transition the integration ACTUALLY performs.
#
#     Assigning the sensor writes the entry's options, which triggers
#     `async_update_options` -> `async_reload` -> a NEW coordinator object.
#     The first version of this check mutated `coord._config` in place on the
#     same coordinator and passed while the real path was broken: the delete
#     was gated on an in-memory flag that a fresh coordinator resets to False,
#     so the branch was dead and an `is_persistent` issue promising "this
#     notice clears when you do" stayed up forever. The shape to copy is a
#     second coordinator sharing the same hass -- same issue registry, fresh
#     object -- because that is what a reload is.
_reload_states = {**_owner_states, "sensor.lower": FakeState("20.4", unit="°C")}
_before_reload = _zone_coord(_reload_states, floor_return_temp_entity="sensor.ret")
_asyncio.run(_before_reload._update_current_state())
_reload_hass = _before_reload.hass
R.check(
    "the notice is up before the sensor is assigned",
    [i[1] for i in getattr(_reload_hass, "issues", [])] == ["lower_floor_modelled"],
)
_after_reload = _Coord(
    _reload_hass,
    _FakeEntry(data={
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "floor_return_temp_entity": "sensor.ret",
        "lower_floor_temp_entity": "sensor.lower",
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
    }),
)
_asyncio.run(_after_reload._update_current_state())
R.check(
    "and assigning one clears it across the reload that follows",
    not [
        i for i in getattr(_reload_hass, "issues", [])
        if i[1] == "lower_floor_modelled"
    ],
    "a fresh coordinator's flag starts False, so the clear must not be "
    "gated on it",
)
R.check(
    "the reloaded coordinator really is reading the sensor",
    abs(_after_reload._current_state.lower_floor_temperature - 20.4) < 1e-6,
    f"got {_after_reload._current_state.lower_floor_temperature}",
)

# 11. The same shape for the fee notice this audit was copied from: it had
#     the identical flag-gated delete, and correcting a fee also reloads.
_fee_hass = _FakeHass()
_fee_steps = [
    datetime(2026, 1, 7, 12, 0, tzinfo=UTC) + timedelta(minutes=15 * i)
    for i in range(8)
]
_fee_bad = _Coord(
    _fee_hass,
    _FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                     "grid_fee_mode": "rules", "grid_fee_rules": "= 25"}),
)
_fee_bad._fee_series(_fee_steps)
_fee_fixed = _Coord(
    _fee_hass,
    _FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                     "grid_fee_mode": "rules", "grid_fee_rules": "= 0.25"}),
)
_fee_fixed._fee_series(_fee_steps)
R.check(
    "correcting a grid fee clears its notice across the reload too",
    not [
        i for i in getattr(_fee_hass, "issues", [])
        if i[1] == "grid_fee_magnitude"
    ],
)


# D2-s1-51 (P6, F1.5): the outdoor state write is a producer with ten
# coordinator readers, and `_update_current_state` wrote it only under
# ``if outdoor.ok`` -- so with no outdoor thermometer every one of them
# read the ThermalState constructor default (5.0 degC) beside a plan solved
# on the forecast: the judge measured the DHW setpoint advisor pricing all
# 7 candidates up to 53 % off, and the solve seed, the defrost band, the
# COP curve and the house-loss learners read the same default. The fix is
# at the producer: whenever no outdoor reading is ok, the state carries the
# forecast's current hour (`forecast_outdoor_now`, the number the horizon
# starts on) instead of the default. The four arms below are the full
# decision table of that write.
from homeassistant.util import dt as _f15_dt

_F15_NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
_F15_ROWS = [
    {"datetime": (_F15_NOW - timedelta(hours=1)).isoformat(),
     "temperature": -9.0},
    {"datetime": _F15_NOW.isoformat(), "temperature": -15.0},
    {"datetime": (_F15_NOW + timedelta(hours=1)).isoformat(),
     "temperature": -10.0},
]


def _f15_outdoor_after(rows, states):
    """The outdoor state after one update. The outdoor entity is mapped
    only when a state for it is given; the indoor sensor always is."""
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
    }
    if "sensor.outdoor" in states:
        cfg["outdoor_temp_entity"] = "sensor.outdoor"
    coord = _Coord(_FakeHass(states), _FakeEntry(data=cfg))
    coord._weather_forecast = rows
    _asyncio.run(coord._update_current_state())
    return coord._current_state.outdoor_temperature


_f15_dt.freeze(_F15_NOW)
R.check(
    "D2-s1-51: with no outdoor reading the state carries the forecast's "
    "current hour, not the 5.0 constructor default",
    _f15_outdoor_after(list(_F15_ROWS),
                       {"sensor.indoor": FakeState("21.0", unit="°C")})
    == -15.0,
    "the current hour is -15.0 between a -9.0 hour before it and a -10.0 "
    "hour after it; the merge base kept the 5.0 default here",
)
R.check(
    "D2-s1-51 (null control): a fresh outdoor reading wins over the forecast",
    _f15_outdoor_after(
        list(_F15_ROWS),
        {"sensor.indoor": FakeState("21.0", unit="°C"),
         "sensor.outdoor": FakeState("-3.0", unit="°C")},
    )
    == -3.0,
)
R.check(
    "D2-s1-51: an unreadable outdoor entity (mapped, state unavailable) "
    "falls back to the forecast too",
    _f15_outdoor_after(
        list(_F15_ROWS),
        {"sensor.indoor": FakeState("21.0", unit="°C"),
         "sensor.outdoor": FakeState("unavailable")},
    )
    == -15.0,
)
R.check(
    "D2-s1-51: with no forecast either, the constructor default is what the "
    "horizon honestly gets (forecast_outdoor_now's None branch)",
    _f15_outdoor_after([], {"sensor.indoor": FakeState("21.0", unit="°C")})
    == 5.0,
)
_f15_dt.freeze(None)


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
_term, _ = _opt_valve._terminal_cost(_prices, _outdoor)
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

# 5. But a full tank is only worth what the next window gets to SPEND.
#    The credit above is undiscounted, so in summer -- when the house coasts
#    six degrees clear of its comfort floor and needs no bought heat for days
#    -- it was the only term in the objective with a gradient, and the plan
#    bought space heat at 27 C to collect it. A tank leaks to ambient whether
#    or not anyone draws on it, so heat stored against a demand that will not
#    arrive is largely gone before it is wanted.
from heatpump_optimizer.optimizer import (  # noqa: E402
    hold_demand_kw as _hold_kw,
    stored_heat_survival as _survival,
)

_p750 = ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=750.0,
    mixing_valve_mode="manual", buffer_max_temp=70.0,
)
_ua750 = _p750.buffer_tank_heat_loss_coefficient

R.check(
    "a tank's terminal credit survives intact when the house is drawing hard",
    _survival(_ua750, 70.0, 4.7) > 0.95,
    f"winter demand must not be discounted, got {_survival(_ua750, 70.0, 4.7):.4f}",
)
R.check(
    "and collapses to nothing when the house needs no bought heat at all",
    _survival(_ua750, 70.0, 0.0) == 0.0,
    "an unbounded hold time means every stored kWh leaks away unspent",
)
R.check(
    "with no cliff between the two: the discount is continuous in demand",
    all(
        _survival(_ua750, 70.0, a) <= _survival(_ua750, 70.0, b) + 1e-12
        for a, b in zip((0.01, 0.1, 0.5, 1.0, 2.0), (0.1, 0.5, 1.0, 2.0, 4.7))
    )
    and _survival(_ua750, 70.0, 0.02) < 0.01
    and _survival(_ua750, 70.0, 0.01) < 1e-5,
    "monotone in demand, and already negligible just above zero: at this "
    "tank 0.02 kW of demand survives 0.2% and 0.01 kW survives 4e-4%",
)
R.check(
    "a better-insulated tank is discounted less than a bare one",
    _survival(_ua750 * 8.0, 70.0, 0.5) < _survival(_ua750, 70.0, 0.5),
    "the discount is this tank's learned physics, not a tuning constant",
)
R.check(
    "a tank that loses nothing keeps its whole credit, even with no demand",
    _survival(0.0, 70.0, 0.0) == 1.0 and _survival(0.0, 70.0, 0.5) == 1.0,
    "the zero-demand collapse above is leakage over an unbounded hold; with "
    "UA 0 there is no leakage to collapse to",
)
# The discount must not be a function of the end temperature the solver is
# choosing, or the terminal term gains a second-order kink and the descent
# path bends for no physical reason. Proof: the cost stays exactly linear in
# the buffer end temperature, so its second difference is zero.
_lin, _ = _opt_valve._terminal_cost(_prices, _outdoor, np.zeros(96))
_at = lambda t: _lin(
    _flat(21.0), _flat(25.0), _flat(21.0), _flat(20.5), _flat(t)
)
_d2 = _at(50.0) - 2.0 * _at(55.0) + _at(60.0)
R.check(
    "the discount does not depend on the end temperature the solver picks",
    abs(_d2) < 1e-9 and _at(50.0) > _at(60.0),
    f"second difference {_d2:.3e} must vanish while the term still slopes",
)

# The gate: gains that cover the loss mean no demand, and no demand means no
# credit. This is the owner's reported case (two zone, valve, 750 L, 25 C day
# / 11 C night, comfort 17-23) reduced to the term that drove it.
_p_gain = ThermalParameters(two_zone_enabled=True, internal_gains=5.0)
R.check(
    "free gains that cover the whole loss leave no hold demand",
    _hold_kw(_p_gain, 21.0, 18.0, solar_mean=2.0) == 0.0,
    "a house holding target on gains alone is not waiting to spend stored heat",
)
R.check(
    "and solar is only counted when the caller asks for it",
    _hold_kw(_p_gain, 21.0, 18.0) >= _hold_kw(_p_gain, 21.0, 18.0, solar_mean=2.0),
    "the slab ceiling deliberately ignores solar; the survival term does not",
)

_opt_summer = _optimizer_for("manual")[2]
_out_summer = np.full(96, 18.0)
_caps_summer = _opt_summer._settlement_caps(_out_summer)
R.check(
    "so in summer the tank's terminal credit is switched off entirely",
    _opt_summer._buffer_survival(
        _out_summer, np.full(96, 2.0), _caps_summer.get("buffer")
    )
    == 0.0,
    "this is what stopped 5.5 kWh of space heat being planned at 27 C",
)
R.check(
    "while at -5 C the same tank keeps essentially all of it",
    _opt_valve._buffer_survival(_outdoor, np.zeros(96), _caps_valve.get("buffer"))
    > 0.95,
    "winter behaviour must be preserved, not traded away",
)
R.check(
    "and without a valve the discount is exactly 1.0, changing nothing",
    _opt_none._buffer_survival(
        _out_summer, np.full(96, 2.0), _caps_none.get("buffer")
    )
    == 1.0,
    "the no-store paths must stay byte-for-byte identical",
)

# 6. Inert without a valve.
_term_none, _ = _opt_none._terminal_cost(_prices, _outdoor)
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
_term_tiny, _ = _opt_tiny._terminal_cost(_prices, _outdoor)
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

# 5. The trajectory the objective needs travels with the return value (#280).
_tr280 = _m_valve.simulate_trajectory(
    _st(45.0), np.full(96, 3.0), _WS(_outdoor), dt_hours=0.25
)
R.check(
    "simulate_trajectory returns the buffer trajectory",
    len(_tr280) == 7 and _tr280[4] is not None and len(_tr280[4]) == 97,
    "room, slab, upper, lower, buffer, refused, wood",
)
_r280, _s280, _u280, _l280, _buf280, *_ = _tr280
_tc280 = float(_term(_r280, _s280, _u280, _l280, _buf280))
_m_valve.simulate_trajectory(
    _st(45.0), np.zeros(96), _WS(_outdoor), dt_hours=0.25
)
R.check(
    "terminal cost is stable when the buffer came from the return value (#280)",
    abs(float(_term(_r280, _s280, _u280, _l280, _buf280)) - _tc280) < 1e-9,
    "an intervening simulation must not change a caller's retained buffer",
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

# R3-D2-01: at fixed flow the lift shrinks as outdoor rises, so COP must
# not fall. Calls compute_cop; does not re-implement the Carnot ratio.
_mono_flows = (36.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0)
_mono_outs = [n / 2.0 for n in range(-40, 71)]
_mono_m = ThermalModel(ThermalParameters(cop_flow_carnot=True))
_mono_viol = 0
for _mf in _mono_flows:
    _mc = [_mono_m.compute_cop(_mo, flow_temp=_mf) for _mo in _mono_outs]
    if any(_mc[i + 1] + 1e-12 < _mc[i] for i in range(len(_mc) - 1)):
        _mono_viol += 1
R.check(
    "Carnot flow correction leaves COP non-decreasing in outdoor temperature",
    _mono_viol == 0,
    f"{_mono_viol} of {len(_mono_flows)} flow temps invert as outdoor rises",
)
_mono_off_viol = 0
for _mf in _mono_flows:
    _mc = [_off.compute_cop(_mo, flow_temp=_mf) for _mo in _mono_outs]
    if any(_mc[i + 1] + 1e-12 < _mc[i] for i in range(len(_mc) - 1)):
        _mono_off_viol += 1
R.check(
    "and the nameplate curve itself is already non-decreasing",
    _mono_off_viol == 0,
    f"carnot-off inverted {_mono_off_viol} of {len(_mono_flows)}",
)

# R4-D2-04 (#928): the Carnot flow term and the DHW setpoint penalty
# multiply in AFTER that nameplate curve's own 0.3 factor floor, and their
# product crosses 1.0 in deep cold -- the model then delivers less heat
# than the electricity it is charged for, under the resistive backup every
# such system carries and under the Carnot bound of any vapour-compression
# cycle. In the band where the factor is pinned (outdoor below -21 C) the
# same mechanism inverts COP: the falling Carnot ratio outruns a curve that
# cannot rise, so the pump models worse as the weather warms. The sweep
# above stops at -20 C, which is exactly why the floored band escaped it.
# Envelope from the configuration's own caps (buffer_max_temp,
# dhw_hard_max_temp), and the learner's cop_scale is swept at both ends of
# its range -- no evidence, and pinned to its floor -- because it too
# multiplies in before the clamp.
_r4f_outs = np.arange(-40.0, 15.0 + 1e-9, 0.5)
for _r4f_tag, _r4f_m in (
    ("shipped scale", ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True))),
    ("cop_scale on its floor", ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True,
        cop_scale=COP_SCALE_MIN))),
):
    _r4f_flows = np.arange(35.0, _r4f_m.params.buffer_max_temp + 1e-9, 5.0)
    _r4f_tanks = np.arange(40.0, _r4f_m.params.dhw_hard_max_temp + 1e-9, 5.0)
    _r4f_space = np.array(
        [[_r4f_m.compute_cop(float(o), flow_temp=float(f)) for o in _r4f_outs]
         for f in _r4f_flows]
    )
    _r4f_worst = int(np.argmin(_r4f_space))
    R.check(
        f"space COP never models below the resistive floor ({_r4f_tag})",
        float(_r4f_space.min()) >= 1.0,
        f"min {_r4f_space.min():.5f} at outdoor="
        f"{_r4f_outs[_r4f_worst % _r4f_space.shape[1]]:.1f} C, flow="
        f"{_r4f_flows[_r4f_worst // _r4f_space.shape[1]]:.1f} C",
    )
    _r4f_dhw = np.array(
        [[_r4f_m.compute_cop_dhw(float(o), float(t)) for o in _r4f_outs]
         for t in _r4f_tanks]
    )
    R.check(
        f"DHW COP never models below the resistive floor ({_r4f_tag})",
        float(_r4f_dhw.min()) >= 1.0,
        f"min {_r4f_dhw.min():.5f} over "
        f"{_r4f_dhw.size} outdoor x tank cells",
    )
    _r4f_inv = sum(
        1 for _row in _r4f_space
        if any(_row[i + 1] + 1e-12 < _row[i] for i in range(len(_row) - 1))
    )
    R.check(
        f"COP is non-decreasing in outdoor through the floored band "
        f"({_r4f_tag})",
        _r4f_inv == 0,
        f"{_r4f_inv} of {len(_r4f_flows)} flow temperatures invert as "
        "outdoor rises",
    )
R.check(
    "the settlement price rides the same floor",
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True)
    ).marginal_cop(-25.0, "buffer", store_temp=70.0) >= 1.0
    and ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True)
    ).marginal_cop(-25.0, "dhw", store_temp=60.0) >= 1.0,
    "marginal_cop returned a sub-unity price for stored heat",
)

# The batched twins inline the same COP law (they exist so the solver's
# finite-difference gradient evaluates its perturbations in one vectorised
# pass), so the floor must hold on the gradient's path too. Pin it as
# bitwise parity with the scalar path through cells whose raw product sits
# far below unity: at -25 C against a 70 C buffer the corrections multiply
# out near 0.74, and with cop_scale on its floor the single-zone curve
# itself lands at 0.525 -- a twin still clamped at 0.5 diverges from the
# scalar path on the very first step.
_r4f_deep = np.full(8, -25.0)
_r4f_calm = np.zeros(8)
_r4f_pow = np.vstack([np.zeros(8), np.full(8, 1.5), np.full(8, 3.0)])

def _r4f_parity(m, st, label):
    batch = m.simulate_trajectory_batch(
        st, _r4f_pow, _WS(_r4f_deep, _r4f_calm, _r4f_calm, _r4f_calm),
        dt_hours=0.25)
    mism = []
    for b in range(_r4f_pow.shape[0]):
        r, s, u, l, buf, _, _ = m.simulate_trajectory(
            st, _r4f_pow[b],
            _WS(_r4f_deep, _r4f_calm, _r4f_calm, _r4f_calm), dt_hours=0.25)
        for name, arr, ref in (
            ("room", batch["room"][b], r), ("slab", batch["slab"][b], s),
            ("upper", batch["upper"][b], u), ("lower", batch["lower"][b], l),
            ("buffer", batch["buffer"][b], buf),
        ):
            if not np.array_equal(arr, ref):
                mism.append(f"{name}[{b}]@{int(np.argmax(arr != ref))}")
    R.check(
        f"the batched twin carries the COP floor: {label}",
        not mism,
        f"first divergences: {mism[:4]}",
    )

_r4f_parity(
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True,
        mixing_valve_mode=_mv.MODE_MANUAL)),
    ThermalState(
        room_temperature=20.5, slab_temperature=22.0,
        outdoor_temperature=-25.0, upper_floor_temperature=21.2,
        lower_floor_temperature=20.1, buffer_tank_temperature=70.0,
    ),
    "two-zone throttled, tank on its cap",
)
# A tank just above the Carnot reference with enough mass to stay there
# leaves the raw product above 1.0 across the run (1.02-1.03 here), so the
# resistive clamp cannot mask a twin whose floored-band freeze drifted
# from the scalar's -- this cell sees the raw values, where the 70 C cell
# above sees only the clamp.
_r4f_parity(
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, cop_flow_carnot=True,
        mixing_valve_mode=_mv.MODE_MANUAL, buffer_tank_volume=5000.0)),
    ThermalState(
        room_temperature=20.5, slab_temperature=22.0,
        outdoor_temperature=-25.0, upper_floor_temperature=21.2,
        lower_floor_temperature=20.1, buffer_tank_temperature=37.0,
    ),
    "two-zone throttled, tank just above the Carnot reference",
)
_r4f_parity(
    ThermalModel(ThermalParameters(cop_scale=COP_SCALE_MIN)),
    ThermalState(
        room_temperature=20.5, slab_temperature=22.0,
        outdoor_temperature=-25.0, upper_floor_temperature=21.2,
        lower_floor_temperature=20.1, buffer_tank_temperature=45.0,
    ),
    "single-zone, learned scale on its floor",
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

# A degenerate install can report design_power == 0, which gives emitter_ua
# == 0.0. The 1e-6 floor in flow_setpoint is the only thing between that call
# and a ZeroDivisionError; the setpoint it returns saturates high, which is
# the correct answer for a house that cannot lose heat. Without the guard the
# whole plan fails, so the floor is load-bearing, not decoration.
try:
    _fs_zero_ua = _mv.flow_setpoint(
        target_temp=21.0, outdoor_temp=-5.0,
        heat_loss_coefficient=0.2, emitter_ua=0.0,
    )
except ZeroDivisionError as _fs_zero_err:
    _fs_zero_ua = _fs_zero_err
R.check(
    "a zero-UA install yields a finite flow setpoint, not ZeroDivisionError",
    isinstance(_fs_zero_ua, float) and _fs_zero_ua < 1e12,
    f"emitter_ua=0.0 -> {_fs_zero_ua!r}",
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
from heatpump_optimizer import optimizer as _optmod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _StoreOpt,
    OptimizationConfig as _StoreCfg,
    OptimizationResult as _StoreRes,
    _Horizon,
    _price_ranked_start,
)


def _storage_plan(price_profile, two_zone=True):
    p = ThermalParameters(
        two_zone_enabled=two_zone, buffer_tank_volume=750.0,
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
    r = opt.optimize(inputs=solve_inputs(
        initial_state=st,
        prices=prices,
        outdoor_temps=outdoor,
        wind_speeds=zeros,
        precipitation=zeros,
        solar_radiation=zeros,
        start_time=datetime(2026, 1, 15),
    ))
    pw = np.asarray(r.power_schedule)
    _, _, _, _, buf, _, _ = m.simulate_trajectory(
        st, pw, _WS(outdoor, zeros, zeros, zeros), dt_hours=0.25)
    night = float(pw[hours < 5].sum() * 0.25)
    peaks = float(
        pw[((hours >= 7) & (hours < 10)) | ((hours >= 16) & (hours < 20))].sum()
        * 0.25
    )
    return night, peaks, buf


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

# R10-BUFFER-STORE (#2500): the single-zone step had no valve branch, so a
# valved 750 L tank sat at its start temperature, the plan matched the
# no-buffer plan bit for bit, and the terminal credit never listed the tank.
_night_s1, _peak_s1, _buf_s1 = _storage_plan("spread", two_zone=False)
_night_f1, _peak_f1, _buf_f1 = _storage_plan("flat", two_zone=False)
R.check(
    "single-zone: the valved tank is charged for the cheap night",
    float(_buf_s1.max()) > 25.0 + 8.0,
    f"tank peaked at {float(_buf_s1.max()):.1f} C from a 25 C start",
)
R.check(
    "single-zone: the plan buys less across the price peaks than at flat prices",
    _peak_s1 < _peak_f1 - 5.0,
    f"peak-hours kWh: spread {_peak_s1:.1f}, flat {_peak_f1:.1f}",
)
R.check(
    "single-zone null control: flat prices concentrate nothing at night",
    _night_f1 < _night_s1 - 5.0,
    f"flat night {_night_f1:.1f} kWh vs spread {_night_s1:.1f}",
)

_p_sz = ThermalParameters(
    buffer_tank_volume=750.0, mixing_valve_mode=_mv.MODE_MANUAL,
    mixing_valve_target=23.0,
)
_m_sz = ThermalModel(_p_sz)
_st_sz = ThermalState(
    room_temperature=21.0, slab_temperature=25.0,
    buffer_tank_temperature=50.0, outdoor_temperature=-5.0,
)
_after_sz = _m_sz.simulate_step(_st_sz, 0.0, -5.0, dt_hours=0.25)
_ua_sz = (
    _p_sz.max_electrical_power * _p_sz.cop_nominal_floored
    / _p_sz.emitter_design_delta_t_floored
)
_fs_sz = _mv.flow_setpoint(
    target_temp=23.0, outdoor_temp=-5.0,
    heat_loss_coefficient=_m_sz.effective_heat_loss_coefficient(
        _p_sz.heat_loss_coefficient, 0.0, 0.0
    ),
    emitter_ua=_ua_sz,
)
_q_sz = _mv.emitter_delivery(mix_temp=min(50.0, _fs_sz), zone_temp=25.0, ua=_ua_sz)
_stand_sz = _p_sz.buffer_tank_heat_loss_coefficient * (50.0 - 20.0)
_lost_sz = (50.0 - _after_sz.buffer_tank_temperature) * _p_sz.buffer_tank_thermal_mass
R.check(
    "single-zone valve: the tank's loss is the slab's delivery plus standing loss",
    abs(_lost_sz - (_q_sz + _stand_sz) * 0.25) < 1e-6,
    f"tank lost {_lost_sz:.4f} kWh vs {(_q_sz + _stand_sz) * 0.25:.4f}",
)
_slab_gain_sz = (_after_sz.slab_temperature - 25.0) * _p_sz.slab_thermal_mass
_slab_out_sz = _p_sz.slab_heat_transfer * (25.0 - 21.0) * 0.25
R.check(
    "single-zone valve: the slab receives exactly what the tank delivered",
    abs(_slab_gain_sz + _slab_out_sz - _q_sz * 0.25) < 1e-6,
    f"slab gained {_slab_gain_sz + _slab_out_sz:.4f} kWh vs {_q_sz * 0.25:.4f}",
)
# The energy bound, driven on one undivided step (the stability count keeps
# `simulate_step` inside it): a 10 L tank at 60 C must not hand the slab
# more than it holds above the slab.
_p_sz10 = ThermalParameters(buffer_tank_volume=10.0, mixing_valve_mode=_mv.MODE_MANUAL)
_after_sz10 = ThermalModel(_p_sz10)._simulate_step_single(
    ThermalState(room_temperature=21.0, slab_temperature=22.0,
                 buffer_tank_temperature=60.0, outdoor_temperature=-5.0),
    0.0, -5.0, dt_hours=0.25,
)
R.check(
    "single-zone valve: a small tank coasting one step never falls below the slab",
    _after_sz10.buffer_tank_temperature >= 22.0 - 1e-9,
    f"tank ended at {_after_sz10.buffer_tank_temperature:.2f} C against a 22 C slab",
)
# The stability count must carry the tank's own row: the shipped 35 L
# valved tank, one 15-minute step against 400 sub-steps of the same law.
_m_sz35 = ThermalModel(
    ThermalParameters(buffer_tank_volume=35.0, mixing_valve_mode=_mv.MODE_MANUAL)
)
_st_sz35 = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                        buffer_tank_temperature=60.0, outdoor_temperature=-5.0)
_one_sz35 = _m_sz35.simulate_step(_st_sz35, 0.0, -5.0, dt_hours=0.25)
_ref_sz35 = _st_sz35
for _ in range(400):
    _ref_sz35 = _m_sz35.simulate_step(_ref_sz35, 0.0, -5.0, dt_hours=0.25 / 400)
R.check(
    "single-zone valve: the stability count subdivides for the tank's own row",
    abs(_one_sz35.buffer_tank_temperature - _ref_sz35.buffer_tank_temperature) < 0.3,
    f"one step {_one_sz35.buffer_tank_temperature:.3f} C vs "
    f"400 sub-steps {_ref_sz35.buffer_tank_temperature:.3f} C",
)
_m_cap = ThermalModel(_p_sz)
_hot = _m_cap.simulate_step(
    ThermalState(room_temperature=21.0, slab_temperature=25.0,
                 buffer_tank_temperature=69.5, outdoor_temperature=-5.0),
    5.0, -5.0, dt_hours=0.25,
)
R.check(
    "single-zone valve: charging stops at buffer_max_temp and books the refusal",
    _hot.buffer_tank_temperature <= _p_sz.buffer_max_temp + 1e-9
    and _m_cap._step_buffer_refused > 0.0,
    f"tank {_hot.buffer_tank_temperature:.2f} C, "
    f"refused {_m_cap._step_buffer_refused:.3f} kW",
)
_opt_sz = _StoreOpt(_m_sz, _StoreCfg(
    horizon_hours=24, time_step_minutes=15,
    target_temp=21.0, min_temp=17.0, max_temp=23.0,
))
_term_sz, _ = _opt_sz._terminal_cost(np.full(96, 1.0), np.full(96, -5.0))
_ends_sz = (np.full(97, 21.0), np.full(97, 25.0), np.full(97, 21.0), np.full(97, 21.0))
R.check(
    "single-zone: the terminal cost credits a valved store tank",
    _term_sz(*_ends_sz, np.full(97, 30.0)) > _term_sz(*_ends_sz, np.full(97, 60.0)),
    "a tank left cold is heat bought back, in either zoning",
)
# The COP is priced at the tank's own temperature behind a valve, so a step
# that delivers nothing and loses a known figure raises the tank by exactly
# cop(tank)*P*dt/C less that loss. Same power at a 40 C tank raises it more:
# the lift, and nothing else, is what the row under test changes.
_p_cop = ThermalParameters(
    buffer_tank_volume=750.0, mixing_valve_mode=_mv.MODE_MANUAL,
    mixing_valve_target=23.0, cop_flow_carnot=True,
)
_m_cop = ThermalModel(_p_cop)
_cop_state = ThermalState(
    room_temperature=21.0, slab_temperature=90.0,
    buffer_tank_temperature=60.0, outdoor_temperature=-5.0,
)
_after_cop = _m_cop.simulate_step(_cop_state, 3.0, -5.0, dt_hours=0.25)
_cop_expect = 60.0 + (
    _m_cop.compute_cop(-5.0, flow_temp=60.0) * 3.0
    - _p_cop.buffer_tank_heat_loss_coefficient * (60.0 - 20.0)
) / _p_cop.buffer_tank_thermal_mass * 0.25
_cold_cop = _m_cop.simulate_step(
    ThermalState(room_temperature=21.0, slab_temperature=90.0,
                 buffer_tank_temperature=40.0, outdoor_temperature=-5.0),
    3.0, -5.0, dt_hours=0.25,
)
R.check(
    "single-zone valve: the step prices the COP at the tank's own temperature",
    abs(_after_cop.buffer_tank_temperature - _cop_expect) < 1e-9
    and _cold_cop.buffer_tank_temperature - 40.0
    > _after_cop.buffer_tank_temperature - 60.0 + 0.2,
    f"60 C tank +{_after_cop.buffer_tank_temperature - 60.0:.3f} K against "
    f"the priced {_cop_expect - 60.0:.3f} K; 40 C tank "
    f"+{_cold_cop.buffer_tank_temperature - 40.0:.3f} K",
)

# --- Zoned-store census: #2500's class --------------------------------------
# The class: a store capability implemented at one zoning's seam and silently
# missing at its sibling. Two instances in two rounds (D12-01's flow write
# target, refused at the config page; #2500's buffer, inert in the
# single-zone step), so the class is held by a census rather than by one
# instance's check. The zoning domain is two_zone_enabled's two values --
# complete by construction -- and the capability tuple below is the class's
# seam list: a new store capability is added here, and every capability must
# be live in EVERY value of the domain. Each arm reads production's own
# outputs; none re-derives a formula, so a formula that improves moves both
# sides together.
def _zoned_store_capabilities(two_zone):
    """One zoning's three live store capabilities: the tank's response to a
    configured valve (K), the heat the cap refuses (kW), and the terminal
    cost's credit for a tank left hot rather than cold (negative = cheaper)."""
    _zp = ThermalParameters(
        two_zone_enabled=two_zone, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=23.0,
        buffer_max_temp=70.0, cop_flow_carnot=True,
    )
    _zq = ThermalParameters(
        two_zone_enabled=two_zone, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_NONE, buffer_max_temp=70.0,
        cop_flow_carnot=True,
    )

    def _zs(slab, tank):
        return ThermalState(
            room_temperature=21.0, slab_temperature=slab,
            upper_floor_temperature=21.0, lower_floor_temperature=21.0,
            buffer_tank_temperature=tank, outdoor_temperature=-5.0,
        )

    _on, _off = ThermalModel(_zp), ThermalModel(_zq)
    _valved = _on.simulate_step(_zs(22.0, 60.0), 4.0, -5.0, dt_hours=0.25)
    _bare = _off.simulate_step(_zs(22.0, 60.0), 4.0, -5.0, dt_hours=0.25)
    _on.simulate_step(_zs(25.0, 69.5), 5.0, -5.0, dt_hours=0.25)
    _zopt = _StoreOpt(ThermalModel(_zp), _StoreCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0,
    ))
    _zterm, _ = _zopt._terminal_cost(np.full(96, 1.0), np.full(96, -5.0))
    _zends = (np.full(97, 21.0), np.full(97, 25.0), np.full(97, 21.0), np.full(97, 21.0))
    return (
        _valved.buffer_tank_temperature - _bare.buffer_tank_temperature,
        _on._step_buffer_refused,
        float(_zterm(*_zends, np.full(97, 60.0)) - _zterm(*_zends, np.full(97, 30.0))),
    )


_zoned_caps = {_tz: _zoned_store_capabilities(_tz) for _tz in (False, True)}
R.check(
    "zoned store census: the valve moves the tank in every zoning (#2500)",
    all(abs(_cap[0]) > 1e-6 for _cap in _zoned_caps.values()),
    f"single-zone {_zoned_caps[False][0]:+.4f} K, "
    f"two-zone {_zoned_caps[True][0]:+.4f} K",
)
R.check(
    "zoned store census: the cap books what it refuses in every zoning (#2500)",
    all(_cap[1] > 1e-6 for _cap in _zoned_caps.values()),
    f"single-zone {_zoned_caps[False][1]:.4f} kW, "
    f"two-zone {_zoned_caps[True][1]:.4f} kW",
)
R.check(
    "zoned store census: the terminal cost credits the tank in every zoning (#2500)",
    all(_cap[2] < -1e-6 for _cap in _zoned_caps.values()),
    f"single-zone {_zoned_caps[False][2]:.4f}, two-zone {_zoned_caps[True][2]:.4f}",
)

# --- Batch two-zone twin: the cap the parity cells never reach --------------
# The parity cells start a 750 L tank with charge to spare, so no step there
# refuses heat: a defect confined to the batch's own clamp survives every
# cell (measured -- this group's M11 did). This case drives the tank into
# buffer_max_temp and demands the batch track the scalar step bit for bit:
# the cells' own contract, aimed where they are blind. The null controls
# below hold the reach -- a case that refused nothing would prove nothing
# about the clamp. (The batch's discharge bound is *not* reachable this way:
# the stability count divides the step until the heat the tank holds above
# its floor exceeds the draw, on either API, so that arm cannot bind.)
def _batch_cap_twin():
    _cp = ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=750.0,
        mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=23.0,
        buffer_max_temp=70.0, cop_flow_carnot=True,
        max_electrical_power=12.0, radiator_power_fraction=0.5,
    )
    _cm = ThermalModel(_cp)
    _cs = ThermalState(
        room_temperature=21.0, slab_temperature=25.0,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=69.5, outdoor_temperature=-5.0,
    )
    _cn = 8
    _cpw = np.full(_cn, 12.0)
    _cwx = WeatherSeries(outdoor_temps=np.full(_cn, -5.0))
    _cb = _cm.simulate_trajectory_batch(_cs, _cpw.reshape(1, _cn), _cwx)
    _ct = _cm.simulate_trajectory(_cs, _cpw, _cwx)
    _tracks = (
        ("room", _cb["room"][0], _ct[0]), ("slab", _cb["slab"][0], _ct[1]),
        ("upper", _cb["upper"][0], _ct[2]), ("lower", _cb["lower"][0], _ct[3]),
        ("buffer", _cb["buffer"][0], _ct[4]),
        ("refused", _cb["refused"][0], np.asarray(_ct[5])),
    )
    return (
        [name for name, a, b in _tracks if not np.array_equal(a, b)],
        float(np.max(_cb["refused"][0])),
        float(np.max(_cb["buffer"][0])),
    )


_cap_bad, _cap_refused, _cap_peak = _batch_cap_twin()
R.check(
    "batch twin: charging into buffer_max_temp matches the scalar step bit-for-bit",
    not _cap_bad and _cap_refused > 1.0 and _cap_peak <= 70.0 + 1e-9,
    f"diverged tracks: {_cap_bad}; peak refused {_cap_refused:.4f} kW; "
    f"tank peaked at {_cap_peak:.4f} C",
)

# R10-BUFFER-STORE review 1: the savings reference sized its power from the
# emitters' need as if the step delivered it straight to them, so behind a
# valve its tank climbed to buffer_max_temp and the refused heat was paid for
# and booked as savings (single-zone 3.3x, two-zone 1.66x the unvalved
# reference on a flat day, a night setback's recovery asking more than the
# curve delivers). The unvalved arm is the null: nothing in it can store, and
# the valved reference may cost no more than the tank's own loss.
_RT_TARGETS = np.array([21.0] * 8 + [19.5] * 36 + [21.0] * 52)


def _ref_tank_arm(two_zone, valved):
    from heatpump_optimizer import mixing_valve as _rt_mv
    from heatpump_optimizer.optimizer import (
        HeatPumpOptimizer as _RtOpt, OptimizationConfig as _RtCfg,
    )
    from heatpump_optimizer.thermal_model import WeatherSeries as _RtWS
    _rp = ThermalParameters(
        two_zone_enabled=two_zone, min_electrical_power=1.5,
        max_electrical_power=5.0, dhw_enabled=False, house_heat_loss_scale=0.6,
    )
    if valved:
        _rp.mixing_valve_mode, _rp.buffer_tank_volume = _rt_mv.MODE_MANUAL, 750.0
    _rm = ThermalModel(_rp)
    _seen = {"refused": 0.0, "tank": []}
    _real = _rm.simulate_step

    def _spy(*a, **k):
        _s = _real(*a, **k)
        _seen["refused"] += _rm._step_buffer_refused * 0.25
        _seen["tank"].append(_s.buffer_tank_temperature)
        return _s

    _rm.simulate_step = _spy
    _bp, _ = _RtOpt(_rm, _RtCfg())._compute_baseline_power(
        _RtWS(outdoor_temps=np.full(96, 5.0), wind_speeds=np.zeros(96),
                      precipitation=np.zeros(96), solar_radiation=np.zeros(96)),
        ThermalState(room_temperature=20.0, upper_floor_temperature=20.0,
                     lower_floor_temperature=20.0, slab_temperature=20.5,
                     outdoor_temperature=5.0, buffer_tank_temperature=24.0),
        0.25, _RT_TARGETS,
    )
    _loss = _rp.buffer_tank_heat_loss_coefficient * max(
        0.0, max(_seen["tank"]) - 20.0) * 24.0 if valved else 0.0
    return float(np.sum(_bp)) * 0.25, _seen["refused"], max(_seen["tank"]), _loss


for _rt_tz, _rt_name in ((False, "single-zone"), (True, "two-zone")):
    _rt_kwh, _rt_ref, _rt_top, _rt_loss = _ref_tank_arm(_rt_tz, True)
    _rt_null, _, _, _ = _ref_tank_arm(_rt_tz, False)
    R.check(
        f"{_rt_name}: the savings reference never charges its valved tank into the cap",
        _rt_ref < 1e-9 and _rt_top < 45.0,
        f"reference refused {_rt_ref:.2f} kWh; its tank peaked at {_rt_top:.1f} C",
    )
    R.check(
        f"{_rt_name}: a valved reference costs the unvalved one plus the tank's loss",
        _rt_kwh <= _rt_null + _rt_loss + 0.5,
        f"valved {_rt_kwh:.2f} kWh vs unvalved {_rt_null:.2f} + loss bound "
        f"{_rt_loss:.2f}",
    )


# The reference converts its tank charge to electricity at the COP the step
# itself prices: behind a valve the tank is the flow. Read off one undivided
# step's own energy balance (tank gain, slab delivery, standing loss), a
# Carnot-priced install with a 60 C tank, where the flow term moves the COP.
def _ref_cop_gap():
    from heatpump_optimizer import mixing_valve as _rc_mv
    from heatpump_optimizer.optimizer import _reference_cop

    _cp = ThermalParameters(
        mixing_valve_mode=_rc_mv.MODE_MANUAL, buffer_tank_volume=750.0,
        cop_flow_carnot=True,
    )
    _cm = ThermalModel(_cp)
    _cs = ThermalState(room_temperature=21.0, slab_temperature=24.0,
                       buffer_tank_temperature=60.0, outdoor_temperature=0.0)
    _n = _cm._simulate_step_single(_cs, 1.0, 0.0, dt_hours=0.25)
    _tank = (_n.buffer_tank_temperature - 60.0) * _cp.buffer_tank_thermal_mass / 0.25
    _slab = (_n.slab_temperature - 24.0) * _cp.slab_thermal_mass / 0.25 + (
        _cp.slab_heat_transfer * (24.0 - 21.0))
    _loss = _cp.buffer_tank_heat_loss_coefficient * (60.0 - 20.0)
    _made = _tank + _slab + _loss
    return _made, _reference_cop(_cm, _cs, 0.0, None), _cm.compute_cop(0.0)


def _charge_case(need_kw, tank0=25.0):
    """One step of the tank law's charge, then one coasting step: the tank's
    peak, what the first step refused, and what the slab received next."""
    from heatpump_optimizer import mixing_valve as _cc_mv
    from heatpump_optimizer.optimizer import _reference_cop
    from heatpump_optimizer.thermal_model import valve_charge_demand

    _cp = ThermalParameters(mixing_valve_mode=_cc_mv.MODE_MANUAL,
                            buffer_tank_volume=750.0, mixing_valve_target=23.0)
    _cm = ThermalModel(_cp)
    _cs = ThermalState(room_temperature=21.0, slab_temperature=24.0,
                       buffer_tank_temperature=tank0, outdoor_temperature=-5.0)
    _kw = valve_charge_demand(_cm, _cs, need_kw, -5.0, 0.0, 0.0, 0.25)
    _s1 = _cm._simulate_step_single(
        _cs, _kw / _reference_cop(_cm, _cs, -5.0, None), -5.0, dt_hours=0.25)
    _refused = _cm._step_buffer_refused
    _s2 = _cm._simulate_step_single(_s1, 0.0, -5.0, dt_hours=0.25)
    _got = (_s2.slab_temperature - _s1.slab_temperature) * _cp.slab_thermal_mass / 0.25 + (
        _cp.slab_heat_transfer * (_s1.slab_temperature - _s1.room_temperature))
    return _s1.buffer_tank_temperature, _refused, _got, _kw


_cc_top, _cc_ref, _, _ = _charge_case(1e3)
R.check(
    "the tank law never charges past the curve, however much the emitters need",
    _cc_ref == 0.0 and _cc_top < 45.0,
    f"a 1000 kW need left the tank at {_cc_top:.1f} C, {_cc_ref:.3f} kW refused",
)
_cc_idle = _charge_case(0.0, tank0=22.0)[3]
R.check(
    "the tank law idles the pump when the emitters need nothing",
    _cc_idle == 0.0,
    f"a zero need behind a tank colder than the slab asked {_cc_idle:.3f} kW",
)
_, _, _cc_got, _ = _charge_case(2.0)
_, _, _cc_cold, _ = _charge_case(2.0, tank0=22.0)
R.check(
    "the tank law charges to the temperature whose draw is the need",
    abs(_cc_got - 2.0) < 0.5 and abs(_cc_cold - 2.0) < 0.5,
    f"a 2.0 kW need delivered {_cc_got:.3f} kW the next step from a 25 C tank, "
    f"{_cc_cold:.3f} kW from a 22 C tank below the slab",
)

# Behind the direct-slab layout no curve caps the slab's water, so only
# buffer_max_temp bounds the tank law there.
def _direct_slab_refused():
    from heatpump_optimizer import mixing_valve as _ds_mv
    from heatpump_optimizer.const import TOPOLOGY_VALVE_UPPER_DIRECT_SLAB
    from heatpump_optimizer.optimizer import _reference_cop
    from heatpump_optimizer.thermal_model import valve_charge_demand

    _dp = ThermalParameters(two_zone_enabled=True, mixing_valve_mode=_ds_mv.MODE_MANUAL,
                            buffer_tank_volume=750.0,
                            topology_layout_override=TOPOLOGY_VALVE_UPPER_DIRECT_SLAB)
    _dm = ThermalModel(_dp)
    assert _dp.slab_fed_direct, "the case must drive the direct-slab layout"
    _ds = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0,
                       lower_floor_temperature=21.0, slab_temperature=24.0,
                       buffer_tank_temperature=60.0, outdoor_temperature=-5.0)
    _kw = valve_charge_demand(_dm, _ds, 1e3, -5.0, 0.0, 0.0, 0.25)
    _d1 = _dm._simulate_step_two_zone(
        _ds, _kw / _reference_cop(_dm, _ds, -5.0, None), -5.0, dt_hours=0.25)
    return _dm._step_buffer_refused, _d1.buffer_tank_temperature


_ds_ref, _ds_tank = _direct_slab_refused()
R.check(
    "behind a direct slab the tank law stops at buffer_max_temp",
    _ds_ref < 1e-6 and 60.0 < _ds_tank <= 70.0 + 1e-9,
    f"a 1000 kW need refused {_ds_ref:.3f} kW; the tank ended at {_ds_tank:.2f} C",
)

# Only the charging direction is capped (`_single_valve_rates`'s headroom
# floor): a tank read above buffer_max_temp cools at its physical rate, the
# slab's delivery plus its standing loss, and refuses nothing.
def _over_cap_coast():
    from heatpump_optimizer import mixing_valve as _oc_mv

    _op = ThermalParameters(mixing_valve_mode=_oc_mv.MODE_MANUAL,
                            buffer_tank_volume=750.0, mixing_valve_target=23.0)
    _om = ThermalModel(_op)
    _os = ThermalState(room_temperature=21.0, slab_temperature=24.0,
                       buffer_tank_temperature=75.0, outdoor_temperature=-5.0)
    _o1 = _om._simulate_step_single(_os, 0.0, -5.0, dt_hours=0.25)
    _slab = (_o1.slab_temperature - 24.0) * _op.slab_thermal_mass / 0.25 + (
        _op.slab_heat_transfer * (24.0 - 21.0))
    _lost = (75.0 - _o1.buffer_tank_temperature) * _op.buffer_tank_thermal_mass / 0.25
    _stand = _op.buffer_tank_heat_loss_coefficient * (75.0 - 20.0)
    return _om._step_buffer_refused, _lost, _slab + _stand


_oc_ref, _oc_lost, _oc_phys = _over_cap_coast()
R.check(
    "single-zone valve: a tank above buffer_max_temp cools at its physical rate",
    _oc_ref == 0.0 and abs(_oc_lost - _oc_phys) < 1e-6,
    f"refused {_oc_ref:.3f} kW; the tank gave {_oc_lost:.4f} kW against "
    f"{_oc_phys:.4f} kW delivered and lost",
)

# The two-zone reference asks the tank for both circuits' need: a cold upper
# floor over a slab already hot enough must still draw a charge.
def _two_zone_rad_demand():
    from heatpump_optimizer import mixing_valve as _tz_mv
    from heatpump_optimizer.optimizer import _thermostat_demand

    _tp = ThermalParameters(two_zone_enabled=True, mixing_valve_mode=_tz_mv.MODE_MANUAL,
                            buffer_tank_volume=750.0)
    _tm = ThermalModel(_tp)
    _ts = ThermalState(room_temperature=20.0, upper_floor_temperature=18.0,
                       lower_floor_temperature=23.0, slab_temperature=30.0,
                       buffer_tank_temperature=24.0, outdoor_temperature=-5.0)
    return _thermostat_demand(
        _tm, _ts, 21.0, -5.0, 0.0, 0.0, 0.0, 0.25, _tp.slab_heat_transfer_floored)


# Unvalved, the two-zone reference still replaces the tank's standing loss
# (the term the router carries for that arm alone).
def _two_zone_unvalved_loss():
    from heatpump_optimizer.optimizer import _thermostat_demand

    _up = ThermalParameters(two_zone_enabled=True, buffer_tank_volume=750.0)
    _um = ThermalModel(_up)

    def _at(tank):
        return _thermostat_demand(
            _um, ThermalState(room_temperature=21.0, upper_floor_temperature=21.0,
                              lower_floor_temperature=21.0, slab_temperature=25.0,
                              buffer_tank_temperature=tank, outdoor_temperature=-5.0),
            21.0, -5.0, 0.0, 0.0, 0.0, 0.25, _up.slab_heat_transfer_floored)
    return _at(50.0) - _at(20.0), _up.buffer_tank_heat_loss_coefficient * 30.0


_ul_gap, _ul_loss = _two_zone_unvalved_loss()
R.check(
    "two-zone, no valve: the reference replaces the tank's standing loss",
    abs(_ul_gap - _ul_loss) < 1e-9 and _ul_loss > 0.0,
    f"a 50 C tank asks {_ul_gap:.4f} kW more than a 20 C one; its loss is {_ul_loss:.4f} kW",
)

# Single-zone behind a valve, the reference's charge lands the tank on the
# curve its emitters are mixed down to, run through the step's own tank law:
# a need past what the curve delivers buys the curve's draw and no more. The
# pump sized to the need alone, or the draw read off two-zone circuits, lands
# it elsewhere.
def _single_valve_charge_landing():
    from heatpump_optimizer import mixing_valve as _sv_mv
    from heatpump_optimizer.optimizer import _thermostat_demand
    from heatpump_optimizer.thermal_model import (
        _single_valve_rates, _valve_flow_set, _valve_ua,
    )

    _sp = ThermalParameters(mixing_valve_mode=_sv_mv.MODE_MANUAL, buffer_tank_volume=750.0)
    _sm = ThermalModel(_sp)
    _su = _sm.effective_heat_loss_coefficient(_sp.heat_loss_coefficient, 0.0, 0.0)
    _ss = ThermalState(room_temperature=21.0, slab_temperature=25.0,
                       buffer_tank_temperature=26.0, outdoor_temperature=-5.0)
    _sd = _thermostat_demand(
        _sm, _ss, 21.0, -5.0, 0.0, 0.0, 0.0, 0.25, _sp.slab_heat_transfer_floored)
    _, _sdt, _ = _single_valve_rates(_sp, 26.0, 25.0, _sd, -5.0, _su, None, 0.25)
    return 26.0 + float(_sdt) * 0.25, _valve_flow_set(_sp, None, -5.0, _su, _valve_ua(_sp))


_sv_tank, _sv_curve = _single_valve_charge_landing()
R.check(
    "single-zone valve: the reference charges the tank onto its curve, never past it",
    abs(_sv_tank - _sv_curve) < 1e-9,
    f"a 26 C tank over a 25 C slab ends the step at {_sv_tank:.4f} C; the curve is "
    f"{_sv_curve:.4f} C",
)

_tz_kw = _two_zone_rad_demand()
R.check(
    "two-zone valve: the reference charges for the radiators' need over a hot slab",
    _tz_kw > 0.5,
    f"an 18 C upper floor over a 30 C slab asked {_tz_kw:.3f} kW of the tank",
)

_rc_made, _rc_cop, _rc_plain = _ref_cop_gap()
R.check(
    "the valved reference prices its draw at the step's own tank-flow COP",
    abs(_rc_made - _rc_cop) < 1e-6 and abs(_rc_plain - _rc_cop) > 0.05,
    f"1 kW made {_rc_made:.4f} kW in the step; reference COP {_rc_cop:.4f}, "
    f"flow-blind COP {_rc_plain:.4f}",
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
    return opt.optimize(inputs=solve_inputs(
        initial_state=st,
        prices=prices,
        outdoor_temps=outdoor,
        wind_speeds=zeros,
        precipitation=zeros,
        solar_radiation=zeros,
        start_time=datetime(2026, 1, 15),
    )), hours


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
_, _, _, _, _ht_open_buf, _, _ = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, _WS(np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero),
    dt_hours=0.25, valve_targets=np.full(24, 23.0),
)
_ht_open_end = float(_ht_open_buf[-1])
_, _, _, _, _ht_held_buf, _, _ = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, _WS(np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero),
    dt_hours=0.25, valve_targets=np.full(24, 17.0),
)
_ht_held_end = float(_ht_held_buf[-1])
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
        _ht_st, _ht_zero,
        _WS(np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero),
        dt_hours=0.25, valve_targets=None,
    )[0][-1]) == float(_ht_m.simulate_trajectory(
        _ht_st, _ht_zero,
        _WS(np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero),
        dt_hours=0.25, valve_targets=np.full(24, _ht_p.comfort_ceiling),
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
_, _, _, _, _, _full_refused, _ = _cm.simulate_trajectory(
    _cst, _full, _WS(_cout, _czeros, _czeros, _czeros), dt_hours=0.25
)
R.check(
    "charging a full tank at full power is refused by the physics",
    _full_refused is not None and _full_refused.max() > 0.5,
    f"peak refusal {_full_refused.max():.2f} kW",
)


class _FakeResult:
    power_schedule = _full


_caps = np.full(96, _cp.max_electrical_power)
_tightened = _copt._tighten_buffer_caps(
    _WS(_cout, _czeros, _czeros, _czeros), _cst, _FakeResult(), _caps, 0.25
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
_cres = _copt.optimize(inputs=solve_inputs(
    initial_state=_cst,
    prices=_cprices,
    outdoor_temps=_cout,
    wind_speeds=_czeros,
    precipitation=_czeros,
    solar_radiation=_czeros,
    start_time=datetime(2026, 1, 15),
))
_, _, _, _, _cres_buf, _cres_refused, _ = _cm.simulate_trajectory(
    _cst, np.asarray(_cres.power_schedule),
    _WS(_cout, _czeros, _czeros, _czeros), dt_hours=0.25,
)
R.check(
    "even free electricity cannot plan past the tank's ceiling",
    float(_cres_refused.max()) < 1e-6,
    f"refused {float(_cres_refused.max()):.4f} kW somewhere in the "
    "final plan; the cap loop should have re-solved it away",
)
R.check(
    "and the trajectory itself respects the cap",
    float(_cres_buf.max()) <= 60.0 + 1e-6,
    f"tank peaked at {float(_cres_buf.max()):.2f} C",
)

# #234: extra_starts must be the clipped prior plus equal-energy bang-bang,
# and they must lead the multi-start list. The free-electricity solve above
# can already sit inside the cap, so tighten may not fire; drive both
# production sites directly.
_n234 = 8
_dt234 = 0.25
_z234 = np.zeros(_n234)
_p234 = np.array([3.0, 0.4, 2.0, 1.2, 4.0, 0.2, 1.8, 0.9])
_st234 = ThermalState(
    room_temperature=21.0, upper_floor_temperature=21.0,
    lower_floor_temperature=21.0, slab_temperature=23.0,
    buffer_tank_temperature=55.0, outdoor_temperature=-2.0,
)
_opt234 = _StoreOpt(
    ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=35.0,
        mixing_valve_mode=_mv.MODE_MANUAL, buffer_max_temp=70.0,
        cop_flow_carnot=True,
    )),
    _StoreCfg(horizon_hours=2, time_step_minutes=15,
              target_temp=21.0, min_temp=17.0, max_temp=23.0),
)
_caps234 = np.full(_n234, 1.0)
_prev234 = np.array([0.8, 0.9, 0.7, 1.2, 0.6, 1.5, 0.5, 0.4])
_clipped234 = np.minimum(_prev234, _caps234)
_bang234 = np.minimum(
    _price_ranked_start(
        _p234, float(np.sum(_clipped234) * _dt234),
        _opt234.model.params.max_electrical_power, _dt234,
    ),
    _caps234,
)
_h234 = _Horizon(
    initial_state=_st234,
    prices=_p234,
    outdoor_temps=np.full(_n234, -2.0),
    wind_speeds=_z234,
    precipitation=_z234,
    solar_radiation=_z234,
    start_time=datetime(2026, 1, 15),
    n_steps=_n234,
    dt=_dt234,
    comfort_targets=np.full(_n234, 21.0),
    temp_min_bounds=np.full(_n234, 17.0),
    temp_max_bounds=np.full(_n234, 23.0),
    step_hours=np.arange(_n234) * _dt234,
    solar_gains=_z234,
    heat_loss_factors=np.ones(_n234),
    forecast={
        "future_solar_energy_kwh": 0.0,
        "solar_peak_indices": [],
        "pre_heat_urgency": 0.5,
        "solar_reduction_factor": 1.0,
        "wind_anticipation_factor": 1.0,
        "rain_anticipation_factor": 1.0,
    },
    t_start=0.0,
    power_caps=_caps234,
    extra_starts=(_clipped234, _bang234),
)
_seen234 = []


class _Min234:
    def __init__(self, x):
        self.x = x
        self.success = True
        self.message = "ok"
        self.nit = 0
        self.nfev = 1
        self.fun = 0.0


def _ms234(objective, starts, *a, **kw):
    _seen234.append([np.asarray(s, dtype=float).copy() for s in starts])
    return _Min234(np.asarray(starts[0], dtype=float))


_real_ms234 = _optmod._multi_start_minimize
_optmod._multi_start_minimize = _ms234
try:
    _opt234._optimize_space_only(_h234)
finally:
    _optmod._multi_start_minimize = _real_ms234
R.check(
    "extra_starts are prepended ahead of the usual candidates",
    len(_seen234) == 1
    and len(_seen234[0]) >= 2
    and np.allclose(_seen234[0][0], _clipped234)
    and np.allclose(_seen234[0][1], _bang234),
    "clipped/bang-bang pair did not lead _multi_start_minimize",
)


class _Got234(Exception):
    def __init__(self, extras, prices, caps, dt):
        self.extras = extras
        self.prices = prices
        self.caps = caps
        self.dt = dt


_fake234 = _StoreRes(
    power_schedule=_prev234.tolist(),
    room_temp_trajectory=[21.0] * (_n234 + 1),
    slab_temp_trajectory=[23.0] * (_n234 + 1),
    timestamps=[datetime(2026, 1, 15)] * _n234,
    prices=_p234.tolist(),
    predicted_cost=1.0,
    baseline_cost=1.0,
    predicted_savings=0.0,
    savings_percentage=0.0,
    optimal_setpoints=[21.0] * _n234,
    status="optimal",
    objective_value=1.0,
    upper_temp_trajectory=[21.0] * (_n234 + 1),
    lower_temp_trajectory=[21.0] * (_n234 + 1),
)
_real_space234 = _StoreOpt._optimize_space_only
_real_tight234 = _StoreOpt._tighten_buffer_caps
_fired234 = {"n": 0}


def _space234(self, h):
    if h.extra_starts:
        raise _Got234(
            tuple(np.asarray(s, dtype=float).copy() for s in h.extra_starts),
            np.asarray(h.prices, dtype=float).copy(),
            None if h.power_caps is None else np.asarray(h.power_caps, dtype=float).copy(),
            float(h.dt),
        )
    return _fake234


def _tight234(self, weather, initial_state, result, power_caps, *a, **kw):
    _fired234["n"] += 1
    if _fired234["n"] != 1:
        return False
    power_caps[:] = np.minimum(
        power_caps, np.maximum(np.asarray(result.power_schedule, dtype=float) * 0.5, 0.05)
    )
    return True


_StoreOpt._optimize_space_only = _space234
_StoreOpt._tighten_buffer_caps = _tight234
_got234 = None
try:
    _opt234.optimize(inputs=solve_inputs(
        initial_state=_st234,
        prices=_p234,
        outdoor_temps=np.full(_n234, -2.0),
        wind_speeds=_z234,
        precipitation=_z234,
        solar_radiation=_z234,
        start_time=datetime(2026, 1, 15),
    ))
except _Got234 as exc:
    _got234 = exc
finally:
    _StoreOpt._optimize_space_only = _real_space234
    _StoreOpt._tighten_buffer_caps = _real_tight234
R.check(
    "cap-tighten re-solve seeds extra_starts with clipped and bang-bang",
    _got234 is not None and len(_got234.extras) == 2,
    "cap-tighten path never passed extra_starts into _solve",
)
if _got234 is not None:
    _clip_w, _bang_w = _got234.extras
    _expect_clip = np.minimum(np.asarray(_prev234), _got234.caps)
    _expect_bang = np.minimum(
        _price_ranked_start(
            _got234.prices, float(np.sum(_expect_clip) * _got234.dt),
            _opt234.model.params.max_electrical_power, _got234.dt,
        ),
        _got234.caps,
    )
    R.check(
        "the bang-bang extra_start is equal-energy price-ranked then capped",
        np.allclose(_clip_w, _expect_clip) and np.allclose(_bang_w, _expect_bang),
        "wired extra_starts are not (clipped prev, equal-energy bang-bang)",
    )

# The cap-tighten re-solve runs both arms -- seeded and unseeded -- and keeps
# the better. Seeds may only win.
_keep234 = {"seeded": 0, "unseeded": 0}
_unseeded_keep234 = _StoreRes(
    power_schedule=_prev234.tolist(),
    room_temp_trajectory=[21.0] * (_n234 + 1),
    slab_temp_trajectory=[23.0] * (_n234 + 1),
    timestamps=[datetime(2026, 1, 15)] * _n234,
    prices=_p234.tolist(),
    predicted_cost=1.0,
    baseline_cost=1.0,
    predicted_savings=0.0,
    savings_percentage=0.0,
    optimal_setpoints=[21.0] * _n234,
    status="optimal",
    objective_value=1.0,
    upper_temp_trajectory=[21.0] * (_n234 + 1),
    lower_temp_trajectory=[21.0] * (_n234 + 1),
)
_seeded_keep234 = _StoreRes(
    power_schedule=_prev234.tolist(),
    room_temp_trajectory=[21.0] * (_n234 + 1),
    slab_temp_trajectory=[23.0] * (_n234 + 1),
    timestamps=[datetime(2026, 1, 15)] * _n234,
    prices=_p234.tolist(),
    predicted_cost=10.0,
    baseline_cost=1.0,
    predicted_savings=0.0,
    savings_percentage=0.0,
    optimal_setpoints=[21.0] * _n234,
    status="optimal",
    objective_value=10.0,
    upper_temp_trajectory=[21.0] * (_n234 + 1),
    lower_temp_trajectory=[21.0] * (_n234 + 1),
)
_fired_keep234 = {"n": 0}


def _space_keep234(self, h):
    if h.extra_starts:
        _keep234["seeded"] += 1
        return _seeded_keep234
    _keep234["unseeded"] += 1
    return _unseeded_keep234


def _tight_keep234(self, weather, initial_state, result, power_caps, *a, **kw):
    _fired_keep234["n"] += 1
    if _fired_keep234["n"] != 1:
        return False
    power_caps[:] = np.minimum(
        power_caps, np.maximum(np.asarray(result.power_schedule, dtype=float) * 0.5, 0.05)
    )
    return True


_StoreOpt._optimize_space_only = _space_keep234
_StoreOpt._tighten_buffer_caps = _tight_keep234
try:
    _kept234 = _opt234.optimize(inputs=solve_inputs(
        initial_state=_st234,
        prices=_p234,
        outdoor_temps=np.full(_n234, -2.0),
        wind_speeds=_z234,
        precipitation=_z234,
        solar_radiation=_z234,
        start_time=datetime(2026, 1, 15),
    ))
finally:
    _StoreOpt._optimize_space_only = _real_space234
    _StoreOpt._tighten_buffer_caps = _real_tight234
R.check(
    "cap-tighten re-solve keeps the better of seeded and unseeded",
    _fired_keep234["n"] >= 1
    and _keep234["seeded"] >= 1
    and _keep234["unseeded"] >= 2
    and abs(float(_kept234.objective_value) - 1.0) < 1e-12,
    f"seeded={_keep234['seeded']} unseeded={_keep234['unseeded']} "
    f"obj={getattr(_kept234, 'objective_value', None)}",
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
# --- round-5 D3-04 (#1312): the valve ratio's two-price floor ----------------
# The mutant that moved ``len(positives) >= 2`` to ``>= 200`` survived this
# script's whole closure and the full gate: every check above reads a view
# whose ``_prices`` is empty, so the ratio is None for a reason the floor
# never had to reach. The floor is what makes the published price_ratio
# non-None at all once two real prices are in, and a ratio that is always
# None is the recommendation's only quantitative input silently switched off.
_vr_two = _zone_coord(_BASE, mixing_valve_mode="manual", max_temperature=23.0)
_vr_two._prices = [{"total": 1.0}, {"total": 4.0}]
_vr_two_ratio = _vr_two._mixing_valve_view()["valve_target_recommendation"][
    "price_ratio"
]
R.check(
    "two published prices give the valve a price ratio",
    _vr_two_ratio == 0.25,
    f"price_ratio={_vr_two_ratio!r}: cheapest over dearest of [1.0, 4.0] is "
    "0.25, and the >= 2 floor is the only thing that admits two",
)
_vr_one = _zone_coord(_BASE, mixing_valve_mode="manual", max_temperature=23.0)
_vr_one._prices = [{"total": 1.0}]
_vr_one_ratio = _vr_one._mixing_valve_view()["valve_target_recommendation"][
    "price_ratio"
]
R.check(
    "one published price is too few to state a ratio",
    _vr_one_ratio is None,
    f"price_ratio={_vr_one_ratio!r}: one price is its own cheapest and "
    "dearest, a ratio of 1.0 that says nothing",
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
# The 23.5 degC ceiling goes out on the entity's step, rounded down because
# it caps delivery: a whole 23 on an entity that states no step
# (R10-SETPOINT-BOOST, tvofi 2026-10-19).
R.check(
    "a number entity is commanded through set_value",
    _calls == [("number", "set_value",
                {"entity_id": "number.valve", "value": 23})],
    f"got {_calls!r}",
)
R.check(
    "and the commanded number is the comfort ceiling, the same value the "
    "dumb-valve recommendation gives",
    _calls and _calls[0][2]["value"] == 23,
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
                                  "temperature": 23})],
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
R.check(
    "#2351: a write the valve refused is not remembered as commanded, so the "
    "next cycle retries it rather than skipping it as unchanged",
    _uc._valve_commanded_target is None,
    f"remembered {_uc._valve_commanded_target!r} after an uncommandable write",
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


R.section("Unit-correct write target for flow set-point entities (#398)")

# The write path already commands a temperature to whatever entity is
# configured; the value has always been an *indoor* target
# (`mixing_valve_target`/`comfort_ceiling`). Pointed at a flow/water
# set-point that value is roughly 21 C to something expecting 35-45 C -- a
# real underheating hazard, not a cosmetic mismatch. The new key makes the
# target explicit and defaults to the value already written, so an existing
# entry's behaviour does not move.

R.check(
    "the default preserves today's behaviour exactly",
    hp_const.DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND == _mv.WRITE_TARGET_INDOOR,
    f"default is {hp_const.DEFAULT_MIXING_VALVE_WRITE_TARGET_KIND!r}",
)

_fi = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="number.valve",
)
_asyncio.run(_fi._command_valve_target())
_fx = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="number.valve",
    mixing_valve_write_target_kind=_mv.WRITE_TARGET_INDOOR,
)
_asyncio.run(_fx._command_valve_target())
R.check(
    "an explicit 'indoor' kind writes the same value as an absent key",
    _fi.hass.services.calls == _fx.hass.services.calls,
    f"absent {_fi.hass.services.calls!r} vs explicit {_fx.hass.services.calls!r}",
)

# 'flow' derives the commanded value from the flow curve
# `_simulate_step_two_zone` already uses to bound a dumb valve's delivery
# (`mixing_valve.flow_setpoint`, called there with the same UA/heat-loss
# construction) -- reused rather than re-derived, per #398's scope.
_ff = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="number.valve",
    mixing_valve_write_target_kind=_mv.WRITE_TARGET_FLOW,
    upper_floor_heat_loss=0.10, lower_floor_heat_loss=0.10,
    heat_pump_max_power=10.0, heat_pump_cop_nominal=1.0,
)
_ff._current_state.outdoor_temperature = -5.0
_asyncio.run(_ff._command_valve_target())
_expected_flow = _mv.flow_setpoint(
    target_temp=23.5, outdoor_temp=-5.0,
    heat_loss_coefficient=0.20, emitter_ua=10.0 / 15.0,
)
R.check(
    "'flow' commands the flow curve's temperature, not the raw indoor target",
    bool(_ff.hass.services.calls)
    and _ff.hass.services.calls[0][2]["value"] == int(_expected_flow)
    and _expected_flow > 23.5,
    f"got {_ff.hass.services.calls!r}, expected {int(_expected_flow)} "
    f"(unrounded {_expected_flow:.4f})",
)

# The mode is validated, not trusted -- the same rule `from_config` already
# applies to `mixing_valve_mode` itself, for the same reason: an unknown
# string must not fall through to a silently wrong branch.
_fs = _write_coord(
    mixing_valve_mode="smart_write", mixing_valve_write_entity="climate.valve",
    mixing_valve_write_target_kind="not-a-real-kind",
)
_asyncio.run(_fs._command_valve_target())
R.check(
    "an unrecognised kind is validated away to 'indoor' rather than trusted",
    bool(_fs.hass.services.calls)
    and _fs.hass.services.calls[0][2]["temperature"] == 23,
    f"got {_fs.hass.services.calls!r}",
)

# The catch #398 names: the flow curve is two-zone building physics
# (`_simulate_step_two_zone`'s own heat-loss/emitter-UA construction), so
# 'flow' on a single-zone install -- which has neither -- has no curve to
# derive from. Caught rather than commanded: skip the write instead of
# sending a fabricated number to what is believed to be a flow set-point.
_fu_cfg = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "mixing_valve_mode": "smart_write",
    "mixing_valve_write_entity": "number.valve",
    "mixing_valve_write_target_kind": _mv.WRITE_TARGET_FLOW,
    "max_temperature": 23.5,
}
_fu = _Coord(_FakeHass(_BASE), _FakeEntry(data=_fu_cfg))
R.check(
    "and single-zone is exactly the install that has none -- fixture check",
    not _fu._thermal_params.two_zone_enabled,
    "this next check is only meaningful if the fixture is actually single-zone",
)
_asyncio.run(_fu._command_valve_target())
R.check(
    "single-zone with 'flow' selected skips the write rather than "
    "commanding an indoor value to a flow set-point",
    _fu.hass.services.calls == [],
    f"got {_fu.hass.services.calls!r}",
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
_x_blind = _x_opt.optimize(inputs=solve_inputs(
    initial_state=_x_st,
    prices=_x_prices,
    outdoor_temps=_x_out,
    wind_speeds=_x_zero,
    precipitation=_x_zero,
    solar_radiation=_x_zero,
    start_time=datetime(2026, 1, 15),
))
_x_fc = np.zeros(96)
_x_fc[:24] = 6.0
_x_aware = _x_opt.optimize(inputs=solve_inputs(
    initial_state=_x_st,
    prices=_x_prices,
    outdoor_temps=_x_out,
    wind_speeds=_x_zero,
    precipitation=_x_zero,
    solar_radiation=_x_zero,
    start_time=datetime(2026, 1, 15),
    external_heat_kw=_x_fc,
))
_x_pb = np.asarray(_x_blind.power_schedule)
_x_pa = np.asarray(_x_aware.power_schedule)
R.check(
    "a burn forecast reduces electric heating during the burn",
    float(_x_pa[:24].sum()) < float(_x_pb[:24].sum()) - 2.0,
    f"first 6 h: blind {_x_pb[:24].sum() * 0.25:.1f} kWh vs "
    f"aware {_x_pa[:24].sum() * 0.25:.1f} kWh",
)
_x_zeroed = _x_opt.optimize(inputs=solve_inputs(
    initial_state=_x_st,
    prices=_x_prices,
    outdoor_temps=_x_out,
    wind_speeds=_x_zero,
    precipitation=_x_zero,
    solar_radiation=_x_zero,
    start_time=datetime(2026, 1, 15),
    external_heat_kw=np.zeros(96),
))
R.check(
    "an all-zero forecast is byte-identical to no forecast",
    np.array_equal(np.asarray(_x_zeroed.power_schedule), _x_pb),
    "zeros must take the exact default path",
)
# A forecast shorter than the horizon is padded with no free heat, not
# truncated into a horizon of its own length: the first six hours alone plan
# exactly as the full forecast whose remainder is zero.
try:
    _x_short = np.asarray(_x_opt.optimize(inputs=solve_inputs(
        initial_state=_x_st,
        prices=_x_prices,
        outdoor_temps=_x_out,
        wind_speeds=_x_zero,
        precipitation=_x_zero,
        solar_radiation=_x_zero,
        start_time=datetime(2026, 1, 15),
        external_heat_kw=_x_fc[:24],
    )).power_schedule)
except Exception as _x_err:  # noqa: BLE001 - a raise is the failure measured
    _x_short = repr(_x_err)
R.check(
    "a short burn forecast is padded with zeros: it plans exactly as the "
    "full-length forecast",
    isinstance(_x_short, np.ndarray) and np.array_equal(_x_short, _x_pa),
    f"{_x_short if isinstance(_x_short, str) else 'plans differ'}",
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
_off_wood = _topo.describe_setup({**_full_cfg, "wood_furnace_enabled": False})
R.check(
    "an explicit wood-off flag hides the wood tank despite leftover probes",
    not _off_wood["wood"]["present"]
    and "wood_tank" not in {s["place"] for s in _off_wood["slots"]},
)
_off_dhw = _topo.describe_setup({**_full_cfg, "dhw_enabled": False})
R.check(
    "an explicit DHW-off flag hides the hot-water tank despite leftover volume",
    not _off_dhw["dhw"]
    and "dhw_tank" not in {s["place"] for s in _off_dhw["slots"]},
)

R.section("R9 N-language: setup text takes the install's language (D4-s2-81)")
_sv_full = _topo.describe_setup(_full_cfg, "sv")
_en_labels = {s["key"]: s["label"] for s in _full["slots"]}
_sv_labels = {s["key"]: s["label"] for s in _sv_full["slots"]}
R.check(
    "every slot label differs from English on a Swedish install",
    _sv_labels.keys() == _en_labels.keys()
    and all(_sv_labels[k] != _en_labels[k] for k in _en_labels),
    f"unchanged: {[k for k in _en_labels if _sv_labels.get(k) == _en_labels[k]]}",
)
_sv_text = _topo.render_text_summary(_sv_full)
_en_words = ("not configured", "House:", "Heat pump", "Buffer tank",
             "Mixing valve", "Hot water tank", "Outside", "Wood furnace tank")
R.check(
    "the text summary carries no English heading on a Swedish install",
    not any(w in _sv_text for w in _en_words)
    and "Värmepump" in _sv_text and "Ute" in _sv_text,
    _sv_text,
)
R.check(
    "null control: English and an unknown language read as before",
    _topo.render_text_summary(_topo.describe_setup(_full_cfg, "de"))
    == _text_en_ref
    if (_text_en_ref := _topo.render_text_summary(_full)) else False,
)
R.check(
    "the layout catalog and sensor gaps follow the language too",
    all(e["label"] != n["label"]
        for e, n in zip(_full["catalog"], _sv_full["catalog"]))
    and all(e["label"] != n["label"]
            for e, n in zip(_full["sensor_gaps"], _sv_full["sensor_gaps"])),
)
R.check(
    "a region-tagged Swedish locale counts as Swedish",
    _topo.describe_setup(_full_cfg, "sv-SE")["slots"][0]["label"]
    == _sv_full["slots"][0]["label"],
)

_flow_text = _topo.render_text_summary(_full)
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

_dumb_cfg = {
    "indoor_temp_entity": "sensor.indoor",
    "upper_floor_thermal_mass": 3.0,
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    hp_const.CONF_MIXING_VALVE_TARGET: 21.0,
}
_dumb_setup = _topo.describe_setup(_dumb_cfg)
_dumb_valve = next(
    s
    for s in _dumb_setup["slots"]
    if s["key"] == hp_const.CONF_MIXING_VALVE_TARGET_ENTITY
)
R.check(
    "a mixing valve without a target entity still publishes its place",
    _dumb_valve["entity"] is None,
    "the dumb-valve case is no entity, not a missing slot",
)
R.check(
    "and the published slot carries the manual setpoint",
    _dumb_valve.get("manual_setpoint") == 21.0,
    f"manual_setpoint was {_dumb_valve.get('manual_setpoint')!r}",
)
R.check(
    "ThermalParameters.from_config uses that number when no entity is set",
    ThermalParameters.from_config(_dumb_cfg).mixing_valve_target == 21.0,
)

R.check(
    "the flow overview is a fenced monospaced block",
    _flow_text.startswith("```\n") and _flow_text.endswith("\n```"),
    "the one drawing surface every install already renders",
)
R.check(
    "with configured sensors named and empty slots called out",
    "sensor.wood_top" in _flow_text and "not configured" in _flow_text,
)
R.check(
    "and the storage claim matches the model",
    "used as a store" in _flow_text,
    "a 750 L tank behind a manual valve is a store as of v3.10.0",
)
# _full_cfg is itself a two-tank configuration (two zones, manual valve,
# a wood-tank probe), so as of v3.15.0 its summary claims the wood tank as
# a real store. The v3.14.1 abstraction caption must survive exactly where
# the abstraction still runs: wood present without a probe.
R.check(
    "a modelled wood tank is claimed as its own store",
    "modelled as its own store" in _flow_text
    and "modelled as heat into the heat-pump tank" not in _flow_text
    and "Heat pump tank: 750 L" in _flow_text,
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

# R5-D2-02 (#1307): more power must never leave the buffer cooler. Where the
# valve throttles, every step draws ua*(t_mix - zone) out of the tank with the
# conductance both circuits are backed out of the nameplate output at, so once
# u*dt/C_buf passes 1 explicit Euler no longer decays toward the zone: it
# overshoots past it. Past the coldest zone the tank feeds, delivery is already
# zero, so the discharge bound snaps the tank there -- and the ring that
# follows makes the trough a chaotic function of the commanded power rather
# than a monotone one. `_substeps_and_loss` subdivides the four
# boundary-floored masses but used to exempt the buffer on the grounds that its
# energy bound made it safe; that bound is the discontinuity, not the cure.
#
# The schedule is a single sine sweep of the 6 kW shipped ceiling: at the merge
# base a +1e-3 kW bump cooled the 35 L buffer by 2.32e-1 K, +0.1 kW by 13.05 K
# and +1 kW by 12.98 K. Any single-step perturbation is fair game for the bug,
# so the check hunts every step rather than the demonstrated one.
_p35_model = ThermalModel(ThermalParameters(
    two_zone_enabled=True, buffer_tank_volume=35.0,
    mixing_valve_mode=_mv.MODE_MANUAL, mixing_valve_target=21.0,
    cop_flow_carnot=True, max_electrical_power=6.0, buffer_max_temp=70.0,
))


def _p35_buffer_after(base, bump, at):
    """The 35 L valved buffer's trajectory with `bump` kW added at step `at`."""
    state = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=32.0, outdoor_temperature=-5.0,
    )
    seen = []
    for k, power in enumerate(base):
        state = _p35_model.simulate_step(
            state, float(power + (bump if k == at else 0.0)), -5.0,
            dt_hours=0.25,
        )
        seen.append(state.buffer_tank_temperature)
    return np.asarray(seen)


_p35_sched = 6.0 * (1.0 + np.sin(np.linspace(0.0, 6.0, 48))) / 2.0
_p35_plain = _p35_buffer_after(_p35_sched, 0.0, -1)
_p35_worst = 0.0
_p35_where = None
for _bump in (1e-3, 0.1, 1.0):
    for _at in range(len(_p35_sched)):
        _delta = float(
            (_p35_buffer_after(_p35_sched, _bump, _at)[_at:] - _p35_plain[_at:]).min()
        )
        if _delta < _p35_worst:
            _p35_worst, _p35_where = _delta, (_bump, _at)
R.check(
    "more power never leaves the 35 L valved buffer cooler",
    _p35_worst >= -1e-9,
    f"a bump cooled the buffer by {_p35_worst:.4e} K at {_p35_where}; the "
    "discharge bound snaps the Euler overshoot, so the trough is not a "
    "monotone function of the commanded power",
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


def _drive_lower(coord, *, observed_lower, hours=0.5, power=2.0, sun=0.0):
    """One learning interval, with the plant landing on `observed_lower`.

    ``sun`` is the interval's irradiance, W/m², which #2223's dark gauge
    reads on the interval's opening state.
    """
    base = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.0, slab_temperature=27.0,
        outdoor_temperature=-5.0, solar_radiation=sun,
    )
    now = _lz_dt.now()
    coord._last_house_sample = base
    coord._last_house_sample_time = now - _timedelta(hours=hours)
    coord._current_state = replace(base, lower_floor_temperature=observed_lower)
    coord._current_action = {"power": power}
    _asyncio.run(coord._async_learn_lower_floor_loss(coord._close_fabric_interval()))
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

# D7-s4-8x-fabric (#2249): the two fabric learners replay one interval, closed
# once by `_close_fabric_interval`, the one place the baseline advances. The
# house learner run FIRST is the order that used to silence the split learner
# (it compared the current state against itself); the split learner run alone
# is the null control, learning one sample either way.
def _fabric_lower_samples(observed_lower, *, house_first):
    coord = _two_zone_learner(lower_entity="sensor.lower")
    base = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.0, slab_temperature=27.0,
        outdoor_temperature=-5.0,
    )
    coord._last_house_sample = base
    coord._last_house_sample_time = _lz_dt.now() - _timedelta(hours=0.5)
    coord._current_state = replace(base, lower_floor_temperature=observed_lower)
    coord._current_action = {"power": 2.0}
    interval = coord._close_fabric_interval()
    if house_first:
        _asyncio.run(coord._async_learn_house_heat_loss(interval))
    _asyncio.run(coord._async_learn_lower_floor_loss(interval))
    return coord._lower_floor_loss_samples


R.check(
    "the fabric interval is closed once, so the house learner run first does "
    "not silence the split learner",
    _fabric_lower_samples(19.9, house_first=True)
    == _fabric_lower_samples(19.9, house_first=False) == 1,
    "the split learner compared the current state against itself",
)


# --- R10-HOTFIX-LEARNER-INPUTS: a zone-sensor swap and the reset action ------
#
# Each heat-loss learner fits its residual on one zone sensor: the scale on
# the indoor (upper zone) one, the ratio on the lower floor's. Evidence fitted
# against one sensor says nothing about a sensor in another place, so a
# changed entity id voids that learner, and the reset button and service void
# either or both -- one void path, ``_void_heat_loss_learners``. Real
# coordinators over the stock two-zone house, every expectation a property.
from homeassistant.config_entries import ConfigEntryState as _li_state  # noqa: E402
from harness import FakeServiceCall as _li_call  # noqa: E402
from heatpump_optimizer import services as _li_services  # noqa: E402

R.section("A zone-sensor swap and the reset action void the heat-loss learners")

_LI_CFG = dict(_RA_CFG, indoor_temp_entity="sensor.indoor")
_LI_LEARNED = (_RA_S, _RA_R, _RA_NS, _RA_NR)


def _li_state_of(c):
    return (c._house_heat_loss_scale, c._lower_floor_loss_ratio,
            c._house_heat_loss_samples, c._lower_floor_loss_samples)


def _li_swap(cfg_now, store=None):
    store = store or _ra_learned(_LI_CFG)
    saves = store.saves
    c = _ra_reload(cfg_now, store)
    return _li_state_of(c), store.saves - saves, store


_li_lower, _li_lower_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"))
R.check(
    "a lower-floor sensor swap voids the ratio and leaves the scale intact",
    _li_lower == (_RA_S, 1.0, _RA_NS, 0) and _li_lower_saves == 1,
    f"(scale, ratio, samples) {_li_lower}, {_li_lower_saves} save(s)",
)
_li_indoor, _li_indoor_saves, _ = _li_swap(dict(_LI_CFG, indoor_temp_entity="sensor.bthome"))
R.check(
    "an indoor sensor swap voids the scale and leaves the ratio intact",
    _li_indoor == (1.0, _RA_R, 0, _RA_NR) and _li_indoor_saves == 1,
    f"(scale, ratio, samples) {_li_indoor}, {_li_indoor_saves} save(s)",
)
# The owner's move: T6 from indoor to lower floor, a room sensor as indoor.
_li_both, _, _ = _li_swap(dict(_LI_CFG, indoor_temp_entity="sensor.bthome",
                               lower_floor_temp_entity="sensor.indoor"))
R.check(
    "moving a sensor from indoor to the lower floor voids both learners",
    _li_both == (1.0, 1.0, 0, 0),
    f"(scale, ratio, samples) {_li_both}",
)
# Null control: an options change touching neither zone sensor.
_li_null, _li_null_saves, _ = _li_swap(dict(_LI_CFG, outdoor_temp_entity="sensor.other_outdoor",
                                            comfort_weight=3.0))
R.check(
    "an unrelated options change keeps both learners verbatim and writes nothing",
    _li_null == _LI_LEARNED and _li_null_saves == 0,
    f"(scale, ratio, samples) {_li_null}, {_li_null_saves} save(s)",
)
# A store from before the record proves nothing about which sensor it fitted:
# the load adopts the ids in force, it does not void.
_li_old = _ra_learned(_LI_CFG)
_li_old.saved = {k: v for k, v in _li_old.saved.items() if k != "heat_loss_zone_entities"}
_li_pre, _li_pre_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"), _li_old)
R.check(
    "a store without recorded zone sensors keeps both learners and adopts the ids",
    _li_pre == _LI_LEARNED and _li_pre_saves == 1
    and _li_old.saved.get("heat_loss_zone_entities", {}).get("lower_floor_temp_entity") == "sensor.t6",
    f"(scale, ratio, samples) {_li_pre}, adopted {_li_old.saved.get('heat_loss_zone_entities')!r}",
)
# And a second load over the same sensors keeps what the first one left.
_li_twice, _li_twice_saves, _ = _li_swap(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"),
                                        _ra_reload(dict(_LI_CFG, lower_floor_temp_entity="sensor.t6"),
                                                   _ra_learned(_LI_CFG))._thermal_learning_store)
R.check(
    "a reload over the swapped sensor voids nothing more",
    _li_twice == (_RA_S, 1.0, _RA_NS, 0) and _li_twice_saves == 0,
    f"(scale, ratio, samples) {_li_twice}, {_li_twice_saves} save(s)",
)


def _li_others(c):
    """Every learner's persisted shape but the two heat-loss learners', the zone-total
    anchor their ratio enters (re-derived on save), and the save stamp."""
    out = c._learner_snapshot_payloads()
    out["thermal_learning"] = {k: v for k, v in out["thermal_learning"].items() if k not in (
        "house_heat_loss_scale", "house_heat_loss_samples", "lower_floor_loss_ratio",
        "lower_floor_loss_samples", "house_heat_loss_anchor", "updated_at")}
    return out


def _li_reset(learners=None):
    c = _ra_reload(_LI_CFG, _ra_learned(_LI_CFG))
    c._apply_cop_scale(1.13)
    c._comfort_learner.evidence = -1.4
    before = _li_others(c)
    _aio.run(c.async_reset_heat_loss_learners(*([learners] if learners else [])))
    return c, before


_li_r, _li_r_before = _li_reset()
_li_r_after = _ra_reload(_LI_CFG, _li_r._thermal_learning_store)
R.check(
    "the reset returns both learners to 1.0 with no samples, and saves it",
    _li_state_of(_li_r) == _li_state_of(_li_r_after) == (1.0, 1.0, 0, 0)
    and _li_r._thermal_params.house_heat_loss_scale == 1.0
    and _li_r._thermal_params.lower_floor_heat_loss_learned == _li_r._thermal_params.lower_floor_heat_loss,
    f"live {_li_state_of(_li_r)}, reloaded {_li_state_of(_li_r_after)}",
)
R.check(
    "the reset leaves the comfort weight and the DHW, COP and defrost learners as they were",
    _li_others(_li_r) == _li_r_before and _li_r._cop_scale == 1.13
    and _li_r._comfort_learner.evidence == -1.4,
    str(sorted(f"{k}/{f}" for k, v in _li_others(_li_r).items() for f in set(v) | set(_li_r_before[k])
               if v.get(f) != _li_r_before[k].get(f))),
)
_li_one, _ = _li_reset(("lower_floor_loss_ratio",))
R.check(
    "resetting the ratio alone leaves the scale and its samples intact",
    _li_state_of(_li_one) == (_RA_S, 1.0, _RA_NS, 0),
    f"(scale, ratio, samples) {_li_state_of(_li_one)}",
)
_li_one_s, _ = _li_reset(("house_heat_loss_scale",))
R.check(
    "resetting the scale alone leaves the ratio and its samples intact",
    _li_state_of(_li_one_s) == (1.0, _RA_R, 0, _RA_NR),
    f"(scale, ratio, samples) {_li_state_of(_li_one_s)}",
)


async def _li_service(data, store):
    """The service over a loaded coordinator, with the refresh it asks for counted."""
    hass = FakeHass({})
    entry = _ra_entry(data=_LI_CFG, entry_id="li_service")
    coord = _ra_coord(_LI_CFG, store)
    await coord._async_load_thermal_learning()
    refreshes = []

    async def _refresh(*_a, **_k):
        refreshes.append(_li_state_of(coord))

    coord.async_request_refresh = _refresh
    entry.state = _li_state.LOADED
    entry.runtime_data = coord
    hass.config_entries.entries.append(entry)
    answer = await _li_services.handle_reset_heat_loss(
        hass, _li_call("heatpump_optimizer", "reset_heat_loss_learners",
                       _li_services.SERVICE_SCHEMA_RESET_HEAT_LOSS(data)))
    return _li_state_of(coord), refreshes, answer


_li_svc_both = _aio.run(_li_service({}, _ra_learned(_LI_CFG)))
_li_svc_one = _aio.run(_li_service({"learners": ["lower_floor_loss_ratio"]}, _ra_learned(_LI_CFG)))
R.check(
    "the service resets both by default, then re-plans on the reset values",
    _li_svc_both[0] == (1.0, 1.0, 0, 0) and _li_svc_both[1] == [(1.0, 1.0, 0, 0)],
    f"state {_li_svc_both[0]}, refreshes {_li_svc_both[1]}, answer {_li_svc_both[2]}",
)
R.check(
    "the service's learners field resets one learner alone",
    _li_svc_one[0] == (_RA_S, 1.0, _RA_NS, 0) and len(_li_svc_one[1]) == 1,
    f"state {_li_svc_one[0]}, answer {_li_svc_one[2]}",
)
try:
    _li_services.SERVICE_SCHEMA_RESET_HEAT_LOSS({"learners": ["cop_scale"]})
    _li_refused = False
except Exception:  # vol.Invalid
    _li_refused = True
R.check("the service refuses a learner it does not reset", _li_refused)

# After a reset the next fold starts from the configuration: the reset
# coordinator and one that never learned take the same interval to the same
# ratio, one sample each.
_li_fold = _two_zone_learner(lower_entity="sensor.lower", ratio=2.4)
_li_fold._lower_floor_loss_samples = 90
_aio.run(_li_fold.async_reset_heat_loss_learners())
_li_fresh = _two_zone_learner(lower_entity="sensor.lower")
_li_fold_got = _drive_lower(_li_fold, observed_lower=19.6)
_li_fresh_got = _drive_lower(_li_fresh, observed_lower=19.6)
R.check(
    "the next fold after a reset starts from the configuration",
    _li_fold_got == _li_fresh_got and _li_fold_got[1] == 1 and _li_fold_got[0] != 1.0,
    f"reset {_li_fold_got} vs never learned {_li_fresh_got}",
)


sys.exit(R.close("CUT"))
