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
from heatpump_optimizer.defrost import (
    DEFROST_LOSS_MULTIPLIER,
    DERATE_CONFIDENCE_SAMPLES,
    DERATE_MAX,
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
from heatpump_optimizer import pump_mode, pump_signals
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
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    _smooth_topk_sum,
    peak_cost,
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

# Clock skew: a hub whose clock runs behind the sensor's stamps a state in
# the future. The age is published verbatim in `input_ages_minutes` and read
# by the health summary, so it has to be an age, not a signed difference.
future = reader(
    {"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(-30, NOW))}
)
_future_reading = future.read("indoor_temp_entity")
R.check(
    "a future-stamped state reads as age 0, never as a negative age",
    _future_reading.ok and _future_reading.age_minutes == 0.0,
    f"age {_future_reading.age_minutes} minutes from a stamp 30 minutes ahead",
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
# nobody has reported for ninety minutes is not evidence about the pump now.
_old_mode = signals(
    {"select.pump_mode": FakeState("cool", last_updated=minutes_ago(90, NOW))}
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
    {"select.pump_mode": FakeState("turbo", last_updated=minutes_ago(90, NOW))}
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
R.check(
    "the convenience accessors mirror value()",
    _health_reader.text("heat_pump_mode_entity") == "heat"
    and _health_reader.flag("heat_pump_online_entity", default=None) is None
    and _health_reader.flag("heat_pump_defrost_entity", default=True) is True,
    "an unusable or unread key falls back to the caller's default",
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

# The plan-side charge is `peak_cost` (what the optimizer's capacity term
# calls, optimizer.py `_grid_terms`); the former `tariff.peak_penalty`
# wrapper around it was dead in production (#226) and is gone.
R.check(
    "staying under the threshold costs nothing",
    peak_cost(
        np.full(8, 2.0), np.full(8, 1.0), 5.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25,
    ) == 0.0,
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
    abs(charged - 60.0 * float(np.mean(top3))) < 0.05,
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
    peak_cost(
        burst, np.zeros(8), 1.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25,
    )
    < peak_cost(
        np.full(8, 8.0), np.zeros(8), 1.0,
        tariff.marginal_price_per_kw, tariff.window_minutes, 0.25,
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
            _distinct, np.zeros(8), 5.0,
            tariff.marginal_price_per_kw, tariff.window_minutes, 1.0,
            tariff.peaks_averaged,
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

# A one-window +eps probe always moves a hard top-k (that window becomes
# the unique largest, FD ≈ price_per_kw). Smooth top-k shares weight k/n
# across the tie, so the same probe is ≈ price * k/n (here 20 * 3/24 ≈ 2.5).
_tied_base = peak_cost(
    np.full(24, 7.0), np.zeros(24), 6.0, 20.0, 60, 1.0, 3,
)
_tied_fd = [
    (
        peak_cost(
            np.where(np.arange(24) == i, 7.0001, 7.0),
            np.zeros(24),
            6.0,
            20.0,
            60,
            1.0,
            3,
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
# dead and is gone (#226). The import margin's zero floor -- an export
# price above the import price can never pay the house to consume -- is
# pinned on the live `pv.import_margin` here; the objective checks below
# pin the draw-side piecewise cases on the live inline.
_pw_prices = np.array([1.5, 1.5, 1.5])
_pw_surplus = np.array([0.0, 2.0, 5.0])
_pw_margin = pv.import_margin(_pw_prices, 0.3)
R.check(
    "the import margin floors at zero, never paying the house to consume",
    list(_pw_margin) == [1.2, 1.2, 1.2]
    and list(pv.import_margin(np.array([0.2]), 0.9)) == [0.0],
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
    return _o.optimize(_st, _pr, _ot, _wi, _ra, _so, start)

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
    _plan = _o._build_dhw_requirements(
        initial_state=ThermalState(
            room_temperature=21.0, slab_temperature=22.0,
            outdoor_temperature=-5.0, dhw_temperature=48.0,
            dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0),
        prices=np.full(_n, 1.0),
        outdoor_temps=np.full(_n, -5.0),
        step_hours=_hours,
        n_steps=_n, dt=0.25, p_max=4.0,
        step_weekdays=np.array(
            [(start + __import__("datetime").timedelta(hours=(i - 1) * 0.25)).weekday()
             for i in range(_n + 1)]),
    )
    _idle = min(_p.dhw_idle_min_temp, _p.dhw_min_temp)
    _floors = np.asarray(_plan["floor_temps"])
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
                 min_substeps=1):
    cfg = _grad_house(two_zone=two_zone)
    extra = dict(extra_cfg or {})
    if valve:
        extra.setdefault("mixing_valve_mode", valve)
    if wood:
        extra.setdefault("two_tank_modelled", True)
    p = ThermalParameters.from_config({**cfg, **extra})
    m = ThermalModel(p)
    n = 48
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
    subs = [m._stability_substeps(float(wi[k]), float(ra[k]), 0.25)
            for k in range(n)]
    R.check(
        f"grad-parity cell subdivides as claimed (n_sub >= {min_substeps}): "
        f"{label}",
        min(subs) >= min_substeps,
        f"_stability_substeps gave min={min(subs)} max={max(subs)} "
        f"over {n} steps, wanted every step >= {min_substeps}",
    )
    batch = m.simulate_trajectory_batch(
        st, powers, ot, wi, ra, so, 0.25, ext, None, hum, 7.0)
    mism = []
    for b in range(powers.shape[0]):
        r, s, u, l, buf, _, wood = m.simulate_trajectory(
            st, powers[b], ot, wi, ra, so, 0.25, ext, None, hum, 7.0)
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
            st, np.clip(x, 0.0, None), ot, wi, ra, so, 0.25, ext, None, hum, 7.0)
        room = rr[1:]
        return float(np.sum((room - targets) ** 2) + 0.01 * np.sum(x))

    def space_obj_batch(mat, *a):
        tr = m.simulate_trajectory_batch(
            st, np.clip(mat, 0.0, None), ot, wi, ra, so, 0.25,
            ext, None, hum, 7.0)
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
                maxiter=25, batch_objective=space_obj_batch, fd_eps=1e-4,
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
        batch_objective=batch_obj, fd_eps=1e-4,
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

# Space-only, uniform bounds (the historical five, unchanged).
_grad_parity(False, label="single-zone")
_grad_parity(True, label="two-zone")
_grad_parity(True, valve="manual", label="two-zone with valve")
_grad_parity(True, wood=True, valve="manual", label="two-tank")
# D2-01: the Euler sub-step regime, in both zonings, asserted rather than
# named. `_stability_substeps` subdivides a step whose worst u*dt/C exceeds
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


class _CopGate:
    _learn_measured_cop = Coord._learn_measured_cop
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
        self._last_cop_curve_dhw = False
        self._last_cop_dhw_temp = None
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(
            room_temperature=21.0, outdoor_temperature=outdoor
        )
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._cop_ratio_ewma = None
        self._last_measured_cop = None
        self._immersion_active = False
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
    _house_heat_loss_anchor = Coord._house_heat_loss_anchor
    _reanchor_house_heat_loss_scale = Coord._reanchor_house_heat_loss_scale
    _apply_learner_payloads = Coord._apply_learner_payloads

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

from harness import FakeEntry as _StoreFakeEntry, FakeHass as _StoreFakeHass
from homeassistant.helpers.storage import _reset_store_disk as _reset_stores

_STORE_LOADERS = (
    ("_dhw_profile_store", "_async_load_dhw_profile"),
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


for _store_attr, _loader_name in _STORE_LOADERS:
    for _junk in ([1, 2, 3], "nonsense", 7):
        _coord = _store_coord()
        _aio.run(getattr(_coord, _store_attr).async_save(_junk))
        try:
            _aio.run(getattr(_coord, _loader_name)())
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
_aio.run(_dhw_junk._dhw_profile_store.async_save({"hourly_profile": ["x"] * 24}))
try:
    _aio.run(_dhw_junk._async_load_dhw_profile())
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

# Below the learner's own step limit, today's behaviour stands: the law
# is a measured regression on exactly that path (the 30-hop walk), and
# the learner absorbs a small edit in one step.
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
_tz_eff = _tz_new._house_heat_loss_scale * (0.20 + 0.10)
R.check(
    "a two-zone edit re-anchors on the zone total, not the upper zone",
    abs(_tz_eff - ((1.0 - _phi_tz) * 0.30 + _phi_tz * 0.40)) < 1e-9
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
    "dhw_weekly_windows",       # parsed with it (#3): the same spec's day view
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
# The discount must not be a function of the end temperature the solver is
# choosing, or the terminal term gains a second-order kink and the descent
# path bends for no physical reason. Proof: the cost stays exactly linear in
# the buffer end temperature, so its second difference is zero.
_lin = _opt_valve._terminal_cost(_prices, _outdoor, np.zeros(96))
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

# 5. The trajectory the objective needs travels with the return value (#280).
_tr280 = _m_valve.simulate_trajectory(
    _st(45.0), np.full(96, 3.0), _outdoor, dt_hours=0.25
)
R.check(
    "simulate_trajectory returns the buffer trajectory",
    len(_tr280) == 7 and _tr280[4] is not None and len(_tr280[4]) == 97,
    "room, slab, upper, lower, buffer, refused, wood",
)
_r280, _s280, _u280, _l280, _buf280, *_ = _tr280
_tc280 = float(_term(_r280, _s280, _u280, _l280, _buf280))
_m_valve.simulate_trajectory(
    _st(45.0), np.zeros(96), _outdoor, dt_hours=0.25
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
from heatpump_optimizer import optimizer as _optmod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _StoreOpt,
    OptimizationConfig as _StoreCfg,
    OptimizationResult as _StoreRes,
    _Horizon,
    _price_ranked_start,
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
    _, _, _, _, buf, _, _ = m.simulate_trajectory(st, pw, outdoor, zeros, zeros, zeros, 0.25)
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
_, _, _, _, _ht_open_buf, _, _ = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero, 0.25,
    valve_targets=np.full(24, 23.0),
)
_ht_open_end = float(_ht_open_buf[-1])
_, _, _, _, _ht_held_buf, _, _ = _ht_m.simulate_trajectory(
    _ht_st, _ht_zero, np.full(24, -5.0), _ht_zero, _ht_zero, _ht_zero, 0.25,
    valve_targets=np.full(24, 17.0),
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
_, _, _, _, _, _full_refused, _ = _cm.simulate_trajectory(
    _cst, _full, _cout, _czeros, _czeros, _czeros, 0.25
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
_, _, _, _, _cres_buf, _cres_refused, _ = _cm.simulate_trajectory(
    _cst, np.asarray(_cres.power_schedule), _cout,
    _czeros, _czeros, _czeros, 0.25,
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


def _tight234(self, result, power_caps, *a, **kw):
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
    _opt234.optimize(
        _st234, _p234, np.full(_n234, -2.0), _z234, _z234, _z234,
        datetime(2026, 1, 15),
    )
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

# Extra seeds occupy two of `_MULTI_START_SOLVES` slots. On winter_extreme
# that displaced a cheaper unseeded basin. Seeds may only win.
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


def _tight_keep234(self, result, power_caps, *a, **kw):
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
    _kept234 = _opt234.optimize(
        _st234, _p234, np.full(_n234, -2.0), _z234, _z234, _z234,
        datetime(2026, 1, 15),
    )
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
    and abs(_ff.hass.services.calls[0][2]["value"] - round(_expected_flow, 1)) < 1e-6
    and _expected_flow > 23.5,
    f"got {_ff.hass.services.calls!r}, expected {round(_expected_flow, 1)} "
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
    and abs(_fs.hass.services.calls[0][2]["temperature"] - 23.5) < 1e-6,
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

# The card's schedule editor edits the CONFIGURED windows, so the coordinator
# answers them in the grammar the config flow accepts: the flat form for a
# flat spec, the weekly form when the spec names days, "" when none are set --
# and not the plan's flat reading, which is what `dhw_windows` carries.
R.check(
    "the configured windows are answered in the flat grammar",
    param_coord.configured_dhw_windows() == "07:00-09:00",
    param_coord.configured_dhw_windows(),
)
asyncio.run(
    param_coord.async_update_thermal_params(
        {"dhw_windows": "weekdays 06:00-08:30, weekend 08:00-09:30"}
    )
)
R.check(
    "and in the weekly grammar when the configuration names days",
    param_coord.configured_dhw_windows()
    == "weekdays 06:00-08:30, weekend 08:00-09:30",
    param_coord.configured_dhw_windows(),
)
R.check(
    "which the plan's flat view could not carry: it merges the two days into one",
    param_coord._thermal_params.dhw_weekly_windows is not None
    and param_coord._thermal_params.dhw_windows == [(6.0, 9.5)],
    str(param_coord._thermal_params.dhw_windows),
)
asyncio.run(param_coord.async_update_thermal_params({"dhw_windows": ""}))
R.check(
    "and empty when none are configured",
    param_coord.configured_dhw_windows() == "",
    repr(param_coord.configured_dhw_windows()),
)
asyncio.run(
    param_coord.async_update_thermal_params({"dhw_windows": "07:00-09:00"})
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
    _wood_share_vec as _w2t_share_vec,
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
        for a, b in zip(_w2t_out_none[:5], _w2t_out_ref[:5])
    ),
    "a 5 kW burn must fold into the heat-pump tank identically in both, or "
    "a stale probe silently changes the plan",
)
R.check(
    "and reports no wood trajectory at all",
    _w2t_out_none[6] is None,
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

# Region 3 meets region 1 at the flow curve: wood_share itself must not jump
# when hp_temp sits inside the switch margin (issue #245).
_w2t_flow_set = 45.0
_w2t_floor = 21.0
_w2t_share_jump = 0.0
for _w2t_hp in np.linspace(
    _w2t_flow_set - _W2T_MARGIN, _w2t_flow_set, 21
):
    _w2t_a = _w2t_share(_w2t_flow_set - 1e-6, _w2t_hp, _w2t_flow_set, _w2t_floor)
    _w2t_b = _w2t_share(_w2t_flow_set, _w2t_hp, _w2t_flow_set, _w2t_floor)
    _w2t_share_jump = max(_w2t_share_jump, abs(_w2t_b - _w2t_a))
R.check(
    "wood_share is continuous as wood_temp crosses the flow curve in region 3",
    _w2t_share_jump < 1e-6,
    f"max jump {_w2t_share_jump:.4f} at flow_set with hp inside the margin",
)
_w2t_grid_w = np.linspace(20.0, 70.0, 101)
_w2t_grid_h = np.linspace(20.0, 70.0, 101)
_w2t_W, _w2t_H = np.meshgrid(_w2t_grid_w, _w2t_grid_h)
_w2t_vec = _w2t_share_vec(
    _w2t_W.ravel(), _w2t_H.ravel(), _w2t_flow_set, np.full(_w2t_W.size, _w2t_floor)
)
_w2t_scal = np.array([
    _w2t_share(float(w), float(h), _w2t_flow_set, _w2t_floor)
    for w, h in zip(_w2t_W.ravel(), _w2t_H.ravel())
])
R.check(
    "the vector wood_share path stays bitwise-identical to the scalar law",
    float(np.max(np.abs(_w2t_vec - _w2t_scal))) == 0.0,
    "a 96-step solve lands in a different basin if the two paths diverge",
)


# --- The regression this release exists for -------------------------------
#
# Equal power schedules, hot wood tank, burn versus no burn. The burn must be
# invisible to everything the heat pump is judged by.

_w2t_m_burn, _w2t_out_burn = _w2t_run(_w2t_params_two, 60.0, 10.0)
_w2t_m_calm, _w2t_out_calm = _w2t_run(_w2t_params_two, 60.0, 0.0)
_w2t_m_old, _w2t_out_old = _w2t_run(_w2t_params_off, None, 10.0)

R.check(
    "a burn charges the wood tank, pointwise",
    np.all(
        _w2t_out_burn[6]
        >= _w2t_out_calm[6] - 1e-12
    )
    and _w2t_out_burn[6][-1]
    > _w2t_out_calm[6][-1] + 1.0,
    f"ends at {_w2t_out_burn[6][-1]:.1f} C against "
    f"{_w2t_out_calm[6][-1]:.1f} C unburnt",
)
R.check(
    "and takes no cap headroom from the heat pump's tank",
    _w2t_out_burn[5].max() == 0.0
    and _w2t_out_burn[4].max()
    < _w2t_params_two.buffer_max_temp - 1.0,
    f"HP tank peaked at {_w2t_out_burn[4].max():.1f} C "
    f"against a {_w2t_params_two.buffer_max_temp:.0f} C cap with nothing "
    "refused",
)
R.check(
    "the burn moves load off the heat pump's tank rather than into it",
    _w2t_out_burn[4][-1]
    >= _w2t_out_calm[4][-1] - 1e-9,
    f"HP tank ends {_w2t_out_burn[4][-1]:.1f} C with the "
    f"burn and {_w2t_out_calm[4][-1]:.1f} C without: the "
    "wood side carries the emitters, so the HP tank is drawn less",
)
R.check(
    "which is exactly what the single-tank abstraction could not do",
    _w2t_out_old[4].max()
    > _w2t_out_burn[4].max() + 5.0
    and _w2t_out_old[5].max() > 0.0,
    f"the same burn put the old model's tank at "
    f"{_w2t_out_old[4].max():.1f} C and had it refuse "
    f"{_w2t_out_old[5].max():.1f} kW of the pump's own heat",
)
_w2t_cop_model = ThermalModel(_w2t_params_two)
_w2t_cop_two = _w2t_cop_model.compute_cop(
    -5.0, flow_temp=float(_w2t_out_burn[4][-1])
)
_w2t_cop_old = _w2t_cop_model.compute_cop(
    -5.0, flow_temp=float(_w2t_out_old[4][-1])
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

_w2t_m_q, _w2t_out_q = _w2t_run(_w2t_params_two, 60.0, 3.0, n=24, dt=0.25)
_w2t_m_f, _w2t_out_f = _w2t_run(_w2t_params_two, 60.0, 3.0, n=72, dt=1.0 / 12.0)
R.check(
    "six hours of two-tank operation does not depend on the step length",
    abs(
        _w2t_out_q[6][-1] - _w2t_out_f[6][-1]
    ) < 0.5
    and abs(
        _w2t_out_q[4][-1]
        - _w2t_out_f[4][-1]
    ) < 0.5,
    f"wood ends {_w2t_out_q[6][-1]:.2f} C at 15 min vs "
    f"{_w2t_out_f[6][-1]:.2f} C at 5 min",
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
_w2t_wood_tiny = _w2t_out_tiny[6]
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
        for a, b in zip(_w2t_out_cold[:5], _w2t_out_flat[:5])
    ),
    "the share is zero, the supply is the HP tank either way, and the two "
    "branches must agree exactly there -- not to within a tolerance",
)
R.check(
    "and the cold tank only drifts towards the room it stands in",
    _w2t_out_cold[6][-1] > 15.0
    and _w2t_out_cold[6][-1] < 20.0,
    f"ended at {_w2t_out_cold[6][-1]:.2f} C from 15 C, on "
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
    float(_out_on[6][-1])
    < float(_out_off[6][-1]),
    f"wood ended {_out_on[6][-1]:.2f} with the coil vs "
    f"{_out_off[6][-1]:.2f} without",
)
_m_flag, _out_flag = _coil_run(_p_coil, None)
_m_ref2, _out_ref2 = _coil_run(_p_nocoil, None)
R.check(
    "an unsensed wood tank disables the coil byte-identically",
    all(np.array_equal(a, b) for a, b in zip(_out_flag, _out_ref2)),
    "no probe means no preheat claim, exactly the two-tank rule",
)


R.section("Topology catalog and the layout editor's contract (v3.16.0)")

# The Python-side `match_layout` twin was dead (#226): the editor that
# snaps a drawing to a catalog key lives in the card's JS (its verdict
# strings are covered by the Node harnesses). What this side owns is the
# catalog itself -- `LAYOUTS` and `layout_edges`, published to the card by
# `describe_setup` -- so that is what is pinned here.
from heatpump_optimizer.topology import (
    LAYOUTS as _LAYOUTS,
    layout_edges as _layout_edges,
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
        frozenset(
            _layout_edges(_key, two_zone=True, wood=(_key == "two_tank_4way"))
        )
        != frozenset(
            _layout_edges(
                _other, two_zone=True, wood=(_other == "two_tank_4way")
            )
        )
        for _key in _LAYOUTS
        if _LAYOUTS[_key].selectable
        for _other in _LAYOUTS
        if _other != _key
    ),
    "the editor stores whichever key the edge set snaps to; a collision "
    "stores the wrong physics",
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
    float(_out_vud[4][-1])
    < float(_out_valved[4][-1]),
    "raw tank water to the slab must drain the tank faster",
)
_m_a, _out_a2 = _vud_run(
    {k: v for k, v in _vud_cfg.items() if k != "topology_layout"}
)
R.check(
    "no stored layout means byte-identical v3.15.1 behaviour",
    all(np.array_equal(a, b) for a, b in zip(_out_valved[:5], _out_a2[:5])),
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
    and {tuple(e) for e in _u["edges"]}
    == set(
        _layout_edges(
            "two_tank_4way", two_zone=True, wood=True, dhw_coil=False, dhw=True
        )
    ),
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
    "a rate float() accepts but the planner cannot price is rejected too",
    not _gf.is_valid_spec("Mon-Fri = nan")
    and not _gf.is_valid_spec("Mon-Fri = inf")
    and not _gf.is_valid_spec("06:00-22:00 = -inf"),
    "float('nan') and float('inf') parse: a non-finite rate reaches "
    "fee_vector, and the coordinator's magnitude audit compares with > and "
    "never sees a NaN",
)
_nan_rules = _try_exc(lambda: _gf.parse_rules("Mon-Fri = nan"))
R.check(
    "and the parser is where it is rejected, so no NaN ever reaches a schedule",
    isinstance(_nan_rules, _gf.GridFeeError),
    f"parse_rules returned {_nan_rules!r}",
)
# D4-05 (#169): the form's verdict. The parser stays permissive -- a stored
# spec must keep loading -- and ``spec_problem`` is the stricter view the
# config flow applies, naming which of the three things is wrong.
R.check(
    "a negative rate is named as such by the form's verdict",
    _gf.spec_problem("Nov-Mar Mon-Fri 06:00-22:00 = -0.25") == _gf.ERROR_NEGATIVE
    and _gf.spec_problem("= 0.10, Mon-Fri = -0.20") == _gf.ERROR_NEGATIVE,
    f"{_gf.spec_problem('= -0.25')!r}",
)
R.check(
    "a rate above the implausibility bound is named, and the bound itself is not",
    _gf.spec_problem("= 25") == _gf.ERROR_IMPLAUSIBLE
    and _gf.spec_problem(f"= {_gf.IMPLAUSIBLE_FEE_SEK_PER_KWH + 0.01}")
    == _gf.ERROR_IMPLAUSIBLE
    and _gf.spec_problem(f"= {_gf.IMPLAUSIBLE_FEE_SEK_PER_KWH}") is None,
    f"{_gf.spec_problem('= 25')!r}",
)
R.check(
    "a negative rate outranks an implausible one: the sign is the worse slip",
    _gf.spec_problem("= 25, Jul = -0.10") == _gf.ERROR_NEGATIVE,
)
R.check(
    "the documented rules, zero, and an empty spec are no problem",
    _gf.spec_problem("Nov-Mar Mon-Fri 06:00-22:00 = 0.25, Jul = 0.10") is None
    and _gf.spec_problem("= 0") is None
    and _gf.spec_problem("") is None,
)
R.check(
    "an unreadable spec keeps its original error",
    _gf.spec_problem("Nov-Mar = banana") == _gf.ERROR_INVALID,
)
R.check(
    "the permissive parser still loads the negative rule the form refuses",
    _gf.parse_rules("= -0.25")[0].rate == -0.25,
    "a stored spec that stopped loading would silently zero every fee",
)
_neg_sched = _gf.GridFeeSchedule(
    mode=_gf.MODE_RULES, fixed=0.05, rules=_gf.parse_rules("= 0.10, Jul = -0.30")
)
R.check(
    "min_component finds the most negative component and its source",
    _gf.min_component(_neg_sched) == (-0.30, "rules")
    and _gf.min_component(
        _gf.GridFeeSchedule(mode=_gf.MODE_ENTITY, fixed=0.05), entity_value=-0.4
    )
    == (-0.4, "entity")
    and _gf.min_component(
        _gf.GridFeeSchedule(mode=_gf.MODE_RULES, fixed=-0.02, rules=_rules)
    )
    == (-0.02, "fixed"),
    f"{_gf.min_component(_neg_sched)}",
)
R.check(
    "and reports the fixed component when nothing is negative",
    _gf.min_component(_sched) == (0.05, "fixed")
    and _gf.min_component(_gf.GridFeeSchedule(mode=_gf.MODE_NONE, fixed=-9.0))
    == (0.0, "fixed"),
    f"{_gf.min_component(_sched)}",
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
# D1-01: a month whose persisted JSON parses but has a wrong-shaped nested
# "lines"/"meta" field used to load silently, then wedge every future
# _roll_month -> _freeze_month_report -> month_summary() cycle forever
# because the crash happened before the month was marked closed. from_dict
# now quarantines any month whose "lines"/"meta" aren't dicts, with one
# WARNING, and keeps everything else.
_bad_shapes = ["CORRUPT-NOT-A-DICT", ["not", "a", "dict"], 12345, None]
for _bad in _bad_shapes:
    _quarantined = _Ledger.from_dict(
        {
            "months": {
                "2025-01": {"lines": _bad, "meta": {}},
                "2025-02": {"lines": {"spot": {"kwh": 1.0, "sek": 2.0}}, "meta": {}},
            }
        }
    )
    R.check(
        f"a wrong-shape 'lines' field ({type(_bad).__name__}) is quarantined, "
        "the healthy month survives",
        "2025-01" not in _quarantined.months
        and _quarantined.month_summary("2025-01") == {}
        and _quarantined.line("2025-02", "spot")["kwh"] == 1.0,
        f"months kept: {sorted(_quarantined.months)}",
    )
# A malformed "meta" is quarantined the same way as a malformed "lines".
_bad_meta = _Ledger.from_dict(
    {"months": {"2025-03": {"lines": {}, "meta": "CORRUPT-NOT-A-DICT"}}}
)
R.check(
    "a wrong-shape 'meta' field is quarantined too",
    "2025-03" not in _bad_meta.months,
)
# Even if a malformed month slipped through some other path,
# month_summary() itself must degrade to empty rather than raise --
# the crash site gets defensive handling too, per the fix's second half.
_led_direct = _Ledger()
_led_direct.months["2025-04"] = {"lines": "CORRUPT-NOT-A-DICT", "meta": {}}
R.check(
    "month_summary() never raises on a malformed month, even reached directly",
    _led_direct.month_summary("2025-04") == {},
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
# A fee with no time structure cannot create time-shifting. Measured in kWh
# per half of the day rather than as a SHARE of the total, which is what this
# used to do and what made it fragile: a uniform price rise legitimately buys
# less energy overall (it trades against the comfort weight, which is fixed in
# currency), and the energy it gives up is the discretionary pre-heat, which
# lives at night. A share therefore moves even though nothing was shifted —
# the reason the bar here had already been loosened from 0.02 to 0.03 in
# v4.0.5, and it was loose enough by v5.1.10 to be measuring the level effect
# rather than the shift.
#
# The direct statement has no such confound and more teeth: a uniform fee may
# take energy OUT of either half of the day, but it may not put energy INTO
# one — that is what shifting means. A ToU fee on the same day must do exactly
# that, by a wide margin.
def _fee_plan(prices_add):
    _sc = _mk_golden(price_profile="flat")
    _res = _sc["optimizer"].optimize(
        _sc["state"], _sc["prices"] + prices_add, _sc["outdoor"], _sc["wind"],
        _sc["rain"], _sc["solar"], _G_START,
    )
    _tot = np.asarray(_res.power_schedule) + np.asarray(_res.dhw_power_schedule)
    _dhw = np.asarray(_res.dhw_power_schedule)
    _day = float(_tot[24:88].sum()) * 0.25  # 06:00-22:00 on the 15-min grid
    _night = float(_tot[:24].sum() + _tot[88:].sum()) * 0.25
    _dhw_day = float(_dhw[24:88].sum()) / max(float(_dhw.sum()), 1e-9)
    return _day, _night, _dhw_day

_day_none, _night_none, _dhwday_none = _fee_plan(0.0)
_day_flat, _night_flat, _dhwday_flat = _fee_plan(0.25)
_tou_add = np.zeros(96)
_tou_add[24:88] = 0.25  # the höglast window priced up
_day_tou, _night_tou, _dhwday_tou = _fee_plan(_tou_add)
R.check(
    "a flat fee moves no energy INTO either half of the day — the null "
    "control",
    _day_flat <= _day_none + 0.5 and _night_flat <= _night_none + 0.5,
    f"day {_day_none:.2f} -> {_day_flat:.2f} kWh, "
    f"night {_night_none:.2f} -> {_night_flat:.2f} kWh under a uniform fee",
)
R.check(
    "…and the hot-water schedule it produces is untouched by one",
    abs(_dhwday_flat - _dhwday_none) < 0.005,
    f"DHW 06-22 share {_dhwday_none:.4f} -> {_dhwday_flat:.4f}",
)
R.check(
    "a höglast fee moves energy out of the hours it prices up and into "
    "the ones it does not",
    _day_tou < _day_none - 5.0 and _night_tou > _night_none + 5.0,
    f"day {_day_none:.2f} -> {_day_tou:.2f} kWh, "
    f"night {_night_none:.2f} -> {_night_tou:.2f} kWh under a 06-22 fee",
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

# A tank hot enough that the daily requirement is already covered, but still
# under the charge limit — otherwise the unflagged plan does no discretionary
# top-ups either and the pair below is vacuous. 58 °C was such a temperature
# while the planning ceiling was the 60 °C disinfection temperature; since
# v5.1.10 the ceiling is the 55 °C charge limit, and a 58 °C tank is simply
# over it.
_FLAG_TANK = 52.0
_r_guard = _flag_solve(dhw_temperature=_FLAG_TANK, peak_guard_active=True)
_r_ext = _flag_solve(dhw_temperature=_FLAG_TANK, external_heat_active=True)
_r_neither = _flag_solve(dhw_temperature=_FLAG_TANK)
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
# The old `DrawStats.ready_energy` blend (p90 ramped toward the mean by
# evidence) was production-dead and is gone (#226): the optimizer blends
# INLINE, where the mean it blends against is computed (optimizer.py's
# ready-temperature loop), and the `_q_solve` mutation pair below pins
# that live blend end to end. The quantile/count facts here feed it.
_ds2 = DrawStats()
for day in range(DHW_QUANTILE_MIN_EVENTS):
    _ds2.fold(_D1 + timedelta(days=day), "06:00-08:30", 3.0)
    _ds2.fold(_D1 + timedelta(days=day, hours=4), "", 0.0)
R.check(
    "a full week of windows is all evidence and every quantile is finite",
    _ds2.count("06:00-08:30") == DHW_QUANTILE_MIN_EVENTS
    and _ds2.quantile("06:00-08:30", 0.9) == 3.0,
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
# A worthless-energy day. The sweep ranks candidates by cost, and a negative
# price level flips every cost_per_day negative, so min-cost would crown the
# candidate using the MOST energy. The advice must not depend on the sign of
# the price: same tank, same draws, same recommendation as the +1.0 day above.
_c9n = _t2_coord(dhw_tank_volume=1500.0)
_c9n._thermal_params.dhw_enabled = True
_c9n._prices = [{"total": -1.0}] * 24
_sweep_neg = _c9n._dhw_setpoint_sweep()
R.check(
    "a negative-price day still ranks a hotter tank as the dearer one",
    _sweep_neg["candidates"][-1]["cost_per_day"]
    > _sweep_neg["candidates"][0]["cost_per_day"],
    f"got {[c['cost_per_day'] for c in _sweep_neg['candidates']]} — a negative "
    "price level inverts the ranking the whole advisor is",
)
R.check(
    "and recommends what the mirrored positive day recommends",
    _sweep_neg.get("recommended_setpoint") == _rec1
    and _sweep_neg.get("covers_heaviest_window") is True,
    f"got {_sweep_neg.get('recommended_setpoint')} at -1.0/kWh vs {_rec1} at "
    "+1.0/kWh on the same 1500 L tank",
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
# be driven by the flatline: an unusable input outranks ventilation, so the
# latch simply holds until real data returns. Real ``InputReading`` objects,
# not namespaces: the predicate reads ``entity_id``/``ok``/``problem``, and a
# hand-rolled stub can satisfy a predicate the real dataclass would not.
_cs11 = _vent_coord()
_cs11._vent_cusum.tripped = True
_cs11._input_health = _NS(
    readings={
        "indoor_temp_entity": InputReading(
            key="indoor_temp_entity",
            entity_id="sensor.indoor",
            value=21.0,
            problem="stale",
        )
    }
)
R.check(
    "a stale sensor outranks the ventilation freeze for the feed path",
    _cs11._learning_frozen("indoor_temp_entity") == "stale:indoor_temp_entity"
    and _cs11._learning_frozen() == "ventilation",
    "a dead battery's flatline must not drive the very detector that "
    "froze everything",
)
# v5.1.3: and so does every other unusable problem, while a slot the user
# never configured stays out of the way entirely.
_cs11._input_health = _NS(
    readings={
        "indoor_temp_entity": InputReading(
            key="indoor_temp_entity",
            entity_id="sensor.indoor",
            problem="unavailable",
        )
    }
)
R.check(
    "an unavailable sensor outranks the ventilation freeze the same way",
    _cs11._learning_frozen("indoor_temp_entity")
    == "unavailable:indoor_temp_entity",
    f"got {_cs11._learning_frozen('indoor_temp_entity')!r}",
)
_cs11._input_health = _NS(
    readings={
        "dhw_temp_entity": InputReading(
            key="dhw_temp_entity", entity_id=None, problem="not_configured"
        )
    }
)
R.check(
    "an unconfigured slot never freezes learning",
    _cs11._learning_frozen("dhw_temp_entity") == "ventilation",
    "only the ventilation latch may speak here; a missing optional sensor "
    "must not stop every learner on every install that lacks it",
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
    _ch._cop_baseline.get((3, False), [0, 0])[1] >= COP_BASELINE_MIN_SAMPLES
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
    == {"shortfall_percent", "cost_month", "currency"}
    and _cop_issues[0][2].get("is_persistent") is True,
    "a non-persistent issue vanishes on reboot while the fault stays",
)
# D4-04 (#168): the notice prices the shortfall in the instance's currency,
# not in the SEK the placeholder used to be named after.
_eur_hass = _FakeHass(dict(_METER))
_eur_hass.config.currency = "EUR"
_eur_cop = _Coord(
    _eur_hass,
    _FakeEntry(
        data={
            "tibber_token": "x",
            "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor",
            "outdoor_temp_entity": "sensor.outdoor",
        }
    ),
)
_eur_cop._last_measured_cop = 2.4
_eur_cop._raise_cop_issue(3.0)
_eur_cop_issues = [
    i for i in getattr(_eur_hass, "issues", []) if i[1] == "cop_degradation"
]
R.check(
    "the notice carries the instance currency as a placeholder",
    bool(_eur_cop_issues)
    and _eur_cop_issues[0][2]["translation_placeholders"].get("currency") == "EUR",
    "an EUR instance was told its shortfall in SEK",
)

# D3-04: ``sek_month`` is supposed to be ``monthly_kwh * mean_price *
# shortfall`` — only the correction attributable to the *actual* measured
# shortfall, not the household's entire monthly bill. The check above only
# asserts the placeholder *keys* are present, which cannot tell a correct
# formula apart from one that dropped ``* shortfall`` and always claims the
# full bill. This drives ``_raise_cop_issue`` directly with a known ledger
# and price so the claimed SEK/month can be checked by value and for
# proportionality across two different shortfall magnitudes.
import homeassistant.util.dt as _cop_dt_mod
from heatpump_optimizer.ledger import month_key as _cop_month_key

_sek_coord = _t2_coord()
_sek_now = _cop_dt_mod.now()
_sek_month = _cop_month_key(_sek_now)
# 900 kWh/month scaled down to month-to-date the same way the real ledger
# is read, so the ``* 30.0 / now.day`` re-scale in ``_raise_cop_issue``
# lands back on 900.0 regardless of what day this runs.
_sek_coord._ledger._month(_sek_month)["lines"]["spot"] = {
    "kwh": 900.0 * _sek_now.day / 30.0,
    "sek": 0.0,
}
_sek_coord._prices = [{"total": 1.2}]


def _raise_and_read(coord, baseline, current):
    coord.hass.issues = []
    coord._last_measured_cop = current
    coord._raise_cop_issue(baseline)
    issues = [i for i in coord.hass.issues if i[1] == "cop_degradation"]
    placeholders = issues[-1][2]["translation_placeholders"]
    return float(placeholders["shortfall_percent"]), float(placeholders["cost_month"])


_shortfall_1pct, _sek_1pct = _raise_and_read(_sek_coord, baseline=3.0, current=2.97)
_shortfall_20pct, _sek_20pct = _raise_and_read(_sek_coord, baseline=3.0, current=2.4)
R.check(
    "a modest 1% shortfall claims roughly monthly_kwh*price*shortfall, not the full bill",
    abs(_shortfall_1pct - 1.0) < 0.5 and abs(_sek_1pct - (900.0 * 1.2 * 0.01)) < 2.0,
    f"got shortfall={_shortfall_1pct}% sek_month={_sek_1pct} "
    f"(expected ~{900.0 * 1.2 * 0.01:.0f} SEK, not ~{900.0 * 1.2:.0f} SEK)",
)
R.check(
    "the claimed cost scales with the shortfall, not a fixed full-bill number",
    abs(_shortfall_20pct - 20.0) < 0.5
    and abs(_sek_20pct - (900.0 * 1.2 * 0.20)) < 2.0
    and _sek_20pct > 10 * _sek_1pct,
    f"1%% -> {_sek_1pct} SEK, 20%% -> {_sek_20pct} SEK: a dropped '* shortfall' "
    "term would make both numbers identical (~1080 SEK)",
)

_baseline_at_trip = _ch._cop_baseline[(3, False)][0]
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
    _ch._cop_baseline[(3, False)][0] == _baseline_at_trip,
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
    _ch3._cop_baseline[(3, False)][0] < 3.5,
    f"got {_ch3._cop_baseline[(3, False)][0]:.2f}: a plain mean while young; an "
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
# D1-05: a snapshot's "accuracy" field can be corrupt to a non-dict, truthy
# value (partial write, hand-edited store). best_restore()'s old
# `(snap.get("accuracy") or {}).get(...)` only fell back to {} on a FALSY
# value, so a truthy-but-wrong "accuracy" raised AttributeError and killed
# both the manual restore_snapshot service and the automatic drift
# rollback. It must now skip the malformed snapshot (with a warning) and
# keep evaluating the rest of the ring instead of raising.
for _bad_accuracy in ("CORRUPT-NOT-A-DICT", ["not", "a", "dict"], 42):
    _bad_ring = SnapshotRing.from_dict(
        {
            "snapshots": [
                {
                    "taken_at": "2026-06-01T00:00:00",
                    "healthy": True,
                    "alarmed_at_capture": False,
                    "accuracy": _bad_accuracy,
                    "learners": {},
                }
            ],
        }
    )
    R.check(
        f"a malformed 'accuracy' field ({type(_bad_accuracy).__name__}) is "
        "skipped by best_restore(), not raised",
        _bad_ring.best_restore() is None,
    )
# A corrupted NEWEST snapshot must not block recovery to a valid OLDER one.
_bad_newest_ring = SnapshotRing.from_dict(
    {
        "snapshots": [
            {
                "taken_at": "2026-05-01T00:00:00",
                "healthy": True,
                "alarmed_at_capture": False,
                "accuracy": {"temperature_bias": 0.1},
                "learners": {"marker": "OLDER_VALID_SNAPSHOT"},
            },
            {
                "taken_at": "2026-06-01T00:00:00",
                "healthy": True,
                "alarmed_at_capture": False,
                "accuracy": "CORRUPT-NOT-A-DICT",
                "learners": {"marker": "NEWER_CORRUPT_SNAPSHOT"},
            },
        ],
    }
)
R.check(
    "a corrupted newest snapshot is skipped, falling through to the valid older one",
    (_bad_newest_ring.best_restore() or {}).get("learners", {}).get("marker")
    == "OLDER_VALID_SNAPSHOT",
)
# Non-dict entries in the raw "snapshots" list are quarantined at load time.
R.check(
    "malformed snapshot entries are quarantined on load, valid ones kept",
    len(
        SnapshotRing.from_dict(
            {"snapshots": [{"taken_at": "x", "healthy": True}, "garbage", 1, None]}
        ).snapshots
    )
    == 1,
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
_cp._cop_baseline[(3, False)] = [3.0, 25]
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
    _cq._cop_baseline.get((3, False)) == [3.0, 25]
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

# The same barrier on the KEY side of the same dict. lead_sigma is keyed by
# lead hours as strings; a hand-edited or half-written store keyed by a label
# must lose that bucket, not raise out of from_dict -- which runs during
# setup, before there is a coordinator to catch anything.
_bad_key_store = {"lead_sigma": {"abc": 0.4, "3.0": 0.5}, "lead_counts": {"3.0": 3}}
_bad_key_err = _try_exc(lambda: AccuracyTracker.from_dict(_bad_key_store))
R.check(
    "a non-numeric lead_sigma key is skipped, not raised out of from_dict",
    _bad_key_err is None
    and dict(AccuracyTracker.from_dict(_bad_key_store).lead_sigma) == {3.0: 0.5},
    f"from_dict raised {_bad_key_err!r}"
    if _bad_key_err is not None
    else f"loaded {dict(AccuracyTracker.from_dict(_bad_key_store).lead_sigma)}",
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
_cmach._cop_baseline[(3, False)] = [3.0, COP_BASELINE_MIN_SAMPLES + 1]
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
for _lang6 in narrative_mod.TEMPLATES:  # the languages the narratives ship
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

# D1-01's coordinator half: a month that CRASHES the freezer must not wedge
# every future cycle. The pre-fix loop ran _freeze_month_report unguarded,
# so one raising month aborted _roll_month before the month was marked
# closed -- and since the month stayed unmarked, the next cycle raised
# again, forever, with the receipt save never reached either. The fix skips
# the month with an empty receipt, which also marks it closed: the wedge is
# broken and the retry never happens.
_wedge = _t2_coord()
_wedge._ledger.add(_T6, "spot", kwh=1.0, sek=2.0)
_freeze_calls = {"n": 0}


def _exploding_freeze(month):
    _freeze_calls["n"] += 1
    raise ValueError("D1-01: malformed month wedges the freezer")


_wedge._freeze_month_report = _exploding_freeze
try:
    _wedge._roll_month(_apr)
    _rolled_ok = True
except Exception:
    _rolled_ok = False
R.check(
    "a crashing month no longer takes _roll_month down with it",
    _rolled_ok,
    "the freeze loop must complete; the coordinator's month bookkeeping "
    "cannot depend on every historical month parsing",
)
R.check(
    "the crashed month is marked closed with an empty receipt",
    _wedge._month_reports.get("2026-03") == {"month": "2026-03", "lines": {}},
    f"reports: {_wedge._month_reports}",
)
_wedge._roll_month(_apr)
R.check(
    "and it is never retried: the second roll freezes nothing",
    _freeze_calls["n"] == 1,
    f"freeze called {_freeze_calls['n']} times; the pre-fix loop retried "
    "the crashing month on every cycle forever",
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
from harness import (
    ha_setup_component as _ha_setup_component,
    ha_setup_entry as _ha_setup_entry,
    ha_unload_entry as _ha_unload_entry,
)

_LC_DATA = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
}

# The full lifecycle through the real handlers, driven the way Home
# Assistant drives them: the domain's async_setup once, then the entry's
# setup, then its unload. The FakeServices registry is honest — registration
# stores, removal deletes — so what it holds at each step is what Home
# Assistant would hold. The services belong to the domain (action-setup,
# #180): async_setup registers all eleven before any entry exists, an
# entry's setup adds and replaces nothing, and the last unload removes
# nothing — a service that vanished with its entry is exactly what made an
# automation fail validation while the entry was unloaded. (Under the old
# per-entry registration two services once leaked past the last unload
# because a hand-written removal tuple drifted; with nothing to remove,
# that class of leak has nowhere to live.)
_lc_hass = FakeHass()
_lc_entry = FakeEntry(data=_LC_DATA)
_asyncio.run(_ha_setup_component(_integ, _lc_hass))
_lc_registered = dict(_lc_hass.services.async_services().get(_DOMAIN, {}))
R.check(
    "async_setup registers the integration's eleven services before any entry",
    len(_lc_registered) == 11,
    f"{len(_lc_registered)} registered: {sorted(_lc_registered)}",
)
_asyncio.run(_ha_setup_entry(_integ, _lc_hass, _lc_entry))
R.check(
    "an entry's setup neither adds a service nor replaces a handler",
    dict(_lc_hass.services.async_services().get(_DOMAIN, {})) == _lc_registered,
)
R.check(
    "setup hands the coordinator to the entry as runtime_data",
    isinstance(
        getattr(_lc_entry, "runtime_data", None), HeatPumpOptimizerCoordinator
    ),
)
_asyncio.run(_ha_unload_entry(_integ, _lc_hass, _lc_entry))
_lc_left = dict(_lc_hass.services.async_services().get(_DOMAIN, {}))
R.check(
    "every service is still registered after the last entry unloads",
    _lc_left == _lc_registered,
    f"lost: {sorted(set(_lc_registered) - set(_lc_left))}",
)
R.check(
    "and the unload took the coordinator with it",
    not hasattr(_lc_entry, "runtime_data"),
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

# D10-04 (#294, Silver `action-exceptions`): a service action that fails to
# do its job raises HomeAssistantError rather than returning as if it had.
# The issue's three driven cases -- run_optimization returning None after a
# WARNING when no usable prices exist, restore_learned_snapshot answering
# {restored: []}, simulate_plan reporting its failure only inside the
# response dict -- plus the fourth the all-handler sweep found:
# set_thermal_parameters dropping an unparseable dhw_windows write with a
# WARNING while reporting success. Every case is driven through the real
# registry (ha_setup_component + ha_setup_entry + hass.services.async_call)
# on a coordinator with no prices, plan or snapshot: exactly the state the
# verifier drove. What is asserted is the raise's shape (class, domain, key,
# placeholders), never its wording, and each raise must carry translation
# kwargs like the 13 validation sites (#217).
R.section("service operational failures raise (D10-04, #294)")

from homeassistant.exceptions import (  # noqa: E402
    HomeAssistantError as _svc_hae,
    ServiceValidationError as _svc_sve,
)

#: translation_key -> the placeholder names the raise must pass. The class
#: column: "hae" (an operational failure) or "sve" (bad input).
_SVC_KEYS = {
    "run_optimization_no_prices": ({"entry_ids"}, "hae"),
    "run_optimization_solve_failed": ({"entry_ids"}, "hae"),
    "simulate_plan_no_plan": ({"entry_ids"}, "hae"),
    "simulate_plan_no_prices": ({"entry_ids"}, "hae"),
    "simulate_plan_invalid_windows": ({"windows", "error"}, "sve"),
    "simulate_plan_failed": ({"entry_ids", "error"}, "hae"),
    "restore_learned_snapshot_no_snapshot": ({"entry_ids"}, "hae"),
    "set_thermal_params_invalid_dhw_windows": ({"windows", "error"}, "sve"),
}


def _svc_call(hass, service, data):
    """Drive one service call; return ("returned", value) or ("raised", err)."""
    try:
        return "returned", _asyncio.run(
            hass.services.async_call(_DOMAIN, service, data)
        )
    except _svc_hae as err:
        return "raised", err


def _svc_why(outcome, key):
    """Why `outcome` is not a translated raise of `key` ("" when it is one)."""
    kind, err = outcome
    want_ph, want_cls = _SVC_KEYS[key]
    if kind != "raised":
        return f"returned {err!r} instead of raising"
    if want_cls == "sve" and not isinstance(err, _svc_sve):
        return f"raised {type(err).__name__}, not ServiceValidationError"
    if want_cls == "hae" and isinstance(err, _svc_sve):
        return f"raised ServiceValidationError for an operational failure: {err}"
    problems = []
    if getattr(err, "translation_domain", None) != _DOMAIN:
        problems.append(
            f"translation_domain={getattr(err, 'translation_domain', None)!r}"
        )
    if getattr(err, "translation_key", None) != key:
        problems.append(
            f"translation_key={getattr(err, 'translation_key', None)!r} "
            f"want {key!r}"
        )
    ph = getattr(err, "translation_placeholders", None) or {}
    if set(ph) != want_ph:
        problems.append(f"placeholders={sorted(ph)} want={sorted(want_ph)}")
    elif any(not isinstance(v, str) or not v for v in ph.values()):
        problems.append(f"placeholder values not non-empty strings: {ph!r}")
    if not str(err):
        problems.append("the English message is empty (str(err) must inform)")
    return "; ".join(problems)


def _svc_check(name, outcome, key):
    R.check(name, not _svc_why(outcome, key), _svc_why(outcome, key) or "ok")


# The driven state: one loaded entry, its coordinator holding no prices, no
# plan and no snapshot -- what a fresh install (or a dead price feed) looks
# like from a service call.
_svc_hass = FakeHass()
_svc_entry = FakeEntry(data=_LC_DATA)
_asyncio.run(_ha_setup_component(_integ, _svc_hass))
_asyncio.run(_ha_setup_entry(_integ, _svc_hass, _svc_entry))
_svc_coord = _svc_entry.runtime_data
R.check(
    "the driven coordinator really has no prices, plan or snapshot",
    not _svc_coord._prices and _svc_coord._optimization_result is None,
    f"prices={len(_svc_coord._prices)} "
    f"plan={_svc_coord._optimization_result is not None}",
)

_svc_check(
    "run_optimization with no usable prices raises a translated operational error",
    _svc_call(_svc_hass, "run_optimization", {}),
    "run_optimization_no_prices",
)

# #239: a non-empty price list whose timestamps miss the horizon used to
# invent a prior-only curve and let the service solve. The empty-list
# guard above does not cover that arm — `_prices` is truthy, `known` is not.
R.section("stuck prices skip the service solve (#239)")

from homeassistant.util import dt as _stale_dt  # noqa: E402

_STALE_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
_stale_dt.freeze(_STALE_NOW)
_stale_hass = FakeHass()
_stale_entry = FakeEntry(data=_LC_DATA, entry_id="stuck_prices")
_asyncio.run(_ha_setup_entry(_integ, _stale_hass, _stale_entry))
_stale_coord = _stale_entry.runtime_data
_stale_yesterday = _STALE_NOW.replace(hour=0) - timedelta(days=2)
_stale_coord._prices = [
    {
        "total": 0.6 + 0.5 * (h % 12) / 12.0,
        "starts_at": (_stale_yesterday + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(48)
]
_stale_priced = _stale_coord._price_series(
    _stale_coord._opt_config.n_steps,
    _STALE_NOW.replace(hour=0, minute=0, second=0, microsecond=0),
    0,
)
R.check(
    "a stale list that covers no horizon step returns None, not a prior",
    _stale_priced is None,
    "empty known must match an empty list",
)
_stale_arrays = _stale_coord._forecast_arrays(_STALE_NOW)
R.check(
    "no price_known-false step reaches a horizon that can still solve",
    len(_stale_arrays.prices) == 0
    and int(np.sum(~np.asarray(_stale_arrays.price_known, dtype=bool))) == 0,
    f"n={len(_stale_arrays.prices)} "
    f"unknown={int(np.sum(~np.asarray(_stale_arrays.price_known, dtype=bool)))}",
)
R.check(
    "async_run_optimization reports no_prices on that list",
    _asyncio.run(_stale_coord.async_run_optimization()) == "no_prices"
    and _stale_coord._optimization_result is None,
)
_svc_check(
    "run_optimization on a stale list raises the same no-prices error",
    _svc_call(_stale_hass, "run_optimization", {}),
    "run_optimization_no_prices",
)

_cover_hass = FakeHass()
_cover_entry = FakeEntry(data=_LC_DATA, entry_id="covering_prices")
_asyncio.run(_ha_setup_entry(_integ, _cover_hass, _cover_entry))
_cover_coord = _cover_entry.runtime_data
_cover_mid = _STALE_NOW.replace(hour=0, minute=0, second=0, microsecond=0)
_cover_coord._prices = [
    {
        "total": 0.6 + 0.5 * (h % 12) / 12.0,
        "starts_at": (_cover_mid + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(48)
]
_cover_priced = _cover_coord._price_series(
    _cover_coord._opt_config.n_steps, _cover_mid, 0
)
R.check(
    "a covering list still builds a series (the #239 null)",
    _cover_priced is not None
    and int(np.sum(_cover_priced[1])) == _cover_coord._opt_config.n_steps,
    "known_steps must stay 96 when the list covers the horizon",
)
R.check(
    "and the service path still solves on that covering list",
    _asyncio.run(_cover_coord.async_run_optimization()) is None
    and _cover_coord._optimization_result is not None,
)
_stale_dt.freeze(None)
_svc_check(
    "simulate_plan with no plan raises a translated operational error",
    _svc_call(_svc_hass, "simulate_plan", {"target_temp": 21.0}),
    "simulate_plan_no_plan",
)
_svc_check(
    "restore_learned_snapshot with no qualifying snapshot raises a translated "
    "operational error",
    _svc_call(_svc_hass, "restore_learned_snapshot", {}),
    "restore_learned_snapshot_no_snapshot",
)
_svc_check(
    "set_thermal_parameters with unparseable windows refuses the call "
    "(sweep finding: the write used to be dropped with a WARNING)",
    _svc_call(
        _svc_hass, "set_thermal_parameters", {"dhw_windows": "25-99"}
    ),
    "set_thermal_params_invalid_dhw_windows",
)

# #321 (the PR #319 review's window-spec battery), now closed at the grammar
# instead of at the handler. The pre-check above once gated a weekly spec on
# the weekly parser alone, so "Sa,Su 08:00-09:30" was acknowledged and then
# dropped with a WARNING by the flat parser in the write path. The first fix
# made the pre-check refuse it -- which stopped the silent drop by refusing a
# string this module's own docstring documents and its own renderer emits.
# With ONE segmenter (#329) the flat parser reads the selector's comma too,
# so the honest outcome is available: the call succeeds and the write LANDS,
# on Saturday and Sunday and on no other day. Driven on a fresh entry so the
# write half can be asserted, and the pre-check's refusal is still pinned
# below on a spec that is genuinely malformed.
_svc_corner_hass = FakeHass()
_svc_corner_entry = FakeEntry(data=_LC_DATA, entry_id="corner_windows")
_asyncio.run(_ha_setup_entry(_integ, _svc_corner_hass, _svc_corner_entry))
_svc_corner_coord = _svc_corner_entry.runtime_data
_svc_corner_out = _svc_call(
    _svc_corner_hass,
    "set_thermal_parameters",
    {"dhw_windows": "Sa,Su 08:00-09:30"},
)
R.check(
    "set_thermal_parameters accepts a comma-list day selector "
    "(#321/#329: both parsers now read the selector's comma)",
    _svc_corner_out[0] == "returned",
    f"{_svc_corner_out}",
)
R.check(
    "and the write LANDED on Saturday and Sunday only -- not dropped with a "
    "WARNING, not spread across the week",
    _svc_corner_coord._thermal_params.dhw_windows == [(8.0, 9.5)]
    and (_svc_corner_coord._thermal_params.dhw_weekly_windows or [])
    == [[], [], [], [], [], [(8.0, 9.5)], [(8.0, 9.5)]],
    f"flat={_svc_corner_coord._thermal_params.dhw_windows} "
    f"weekly={_svc_corner_coord._thermal_params.dhw_weekly_windows}",
)
# The pre-check is still load-bearing: a comma-list selector carrying an
# unreadable time is refused, so "one grammar" did not become "no grammar".
_svc_check(
    "set_thermal_parameters still refuses a comma-list selector with a bad time",
    _svc_call(
        _svc_corner_hass,
        "set_thermal_parameters",
        {"dhw_windows": "Sa,Su 25:00-99:00"},
    ),
    "set_thermal_params_invalid_dhw_windows",
)
R.check(
    "and that refusal left Saturday and Sunday as the accepted call set them",
    (_svc_corner_coord._thermal_params.dhw_weekly_windows or [])
    == [[], [], [], [], [], [(8.0, 9.5)], [(8.0, 9.5)]],
    "a refused call must not apply or half-apply anything",
)
# Null control: a single-day spec still parses, the call still returns, and
# the write reaches BOTH structures the write path builds.
_svc_single_out = _svc_call(
    _svc_corner_hass, "set_thermal_parameters", {"dhw_windows": "Sa 08:00-09:30"}
)
R.check(
    "set_thermal_parameters with a single-day weekly spec still succeeds",
    _svc_single_out[0] == "returned",
    f"{_svc_single_out}",
)
R.check(
    "and the single-day spec reached both window structures",
    _svc_corner_coord._thermal_params.dhw_windows == [(8.0, 9.5)]
    and [
        len(day)
        for day in _svc_corner_coord._thermal_params.dhw_weekly_windows or []
    ]
    == [0, 0, 0, 0, 0, 1, 0],
    f"flat={_svc_corner_coord._thermal_params.dhw_windows} "
    f"weekly={[len(d) for d in _svc_corner_coord._thermal_params.dhw_weekly_windows or []]}",
)

# The sub-paths behind the first two cases. A solve that raises inside
# async_run_optimization is swallowed by its own except-Exception fence (the
# repair-issue path), so the handler has to hear about it through the
# coordinator's status rather than an exception; and simulate_plan's
# no_prices / invalid_windows arms are separate returns inside async_simulate.
_svc_crash_hass = FakeHass()
_svc_crash_entry = FakeEntry(data=_LC_DATA, entry_id="crash_pump")
_asyncio.run(_ha_setup_entry(_integ, _svc_crash_hass, _svc_crash_entry))
_svc_crash_coord = _svc_crash_entry.runtime_data
_svc_cover_mid = _stale_dt.now().replace(minute=0, second=0, microsecond=0)
_svc_crash_coord._prices = [
    {
        "total": 0.8,
        "starts_at": (_svc_cover_mid + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(48)
]


def _tariff_boom():
    raise RuntimeError("tariff exploded")


_svc_crash_coord._capacity_tariff = _tariff_boom
_svc_check(
    "run_optimization when the solve raises raises a translated operational error",
    _svc_call(_svc_crash_hass, "run_optimization", {}),
    "run_optimization_solve_failed",
)
R.check(
    "the coordinator reports the solve crash as a reason, not an exception",
    _asyncio.run(_svc_crash_coord.async_run_optimization()) == "solve_failed",
    "async_run_optimization did not report solve_failed",
)

_svc_sim_hass = FakeHass()
_svc_sim_entry = FakeEntry(data=_LC_DATA, entry_id="sim_pump")
_asyncio.run(_ha_setup_entry(_integ, _svc_sim_hass, _svc_sim_entry))
_svc_sim_coord = _svc_sim_entry.runtime_data
_svc_sim_coord._optimization_result = object()  # non-None: "a plan exists"
_svc_check(
    "simulate_plan with a plan but no prices raises the no-prices error",
    _svc_call(_svc_sim_hass, "simulate_plan", {"target_temp": 21.0}),
    "simulate_plan_no_prices",
)
_svc_sim_coord._prices = [
    {
        "total": 0.8,
        "starts_at": (_svc_cover_mid + timedelta(hours=h)).isoformat(),
        "level": "NORMAL",
    }
    for h in range(48)
]
_svc_check(
    "simulate_plan with unparseable windows refuses the call",
    _svc_call(_svc_sim_hass, "simulate_plan", {"dhw_windows": "25-99"}),
    "simulate_plan_invalid_windows",
)

# Controls: a handler that did its job still returns. The coordinators are
# patched per instance -- what is asserted is the handler's contract (a
# success must not raise), not the solve itself.
async def _svc_ok_run():
    return None


async def _svc_ok_simulate(overrides):
    return {"status": "ok"}


async def _svc_ok_restore():
    return True


_svc_coord.async_run_optimization = _svc_ok_run
_svc_out = _svc_call(_svc_hass, "run_optimization", {})
R.check(
    "run_optimization returns normally when the solve ran",
    _svc_out[0] == "returned",
    f"{_svc_out[0]}: {_svc_out[1]}",
)
_svc_coord.async_simulate = _svc_ok_simulate
_svc_out = _svc_call(_svc_hass, "simulate_plan", {"target_temp": 21.0})
R.check(
    "simulate_plan returns its response when the what-if ran",
    _svc_out[0] == "returned"
    and _svc_out[1] == {"results": {_svc_entry.entry_id: {"status": "ok"}}},
    f"{_svc_out}",
)
_svc_coord.async_restore_learned_snapshot = _svc_ok_restore
_svc_out = _svc_call(_svc_hass, "restore_learned_snapshot", {})
R.check(
    "restore_learned_snapshot returns {restored: [...]} when a snapshot applied",
    _svc_out == ("returned", {"restored": [_svc_entry.entry_id]}),
    f"{_svc_out}",
)
_svc_valid_hass = FakeHass()
_svc_valid_entry = FakeEntry(data=_LC_DATA, entry_id="valid_windows")
_asyncio.run(_ha_setup_entry(_integ, _svc_valid_hass, _svc_valid_entry))
_svc_out = _svc_call(
    _svc_valid_hass, "set_thermal_parameters", {"dhw_windows": "06-07"}
)
R.check(
    "set_thermal_parameters with parseable windows still succeeds",
    _svc_out[0] == "returned",
    f"{_svc_out}",
)
R.check(
    "and the valid windows reached the coordinator",
    [(6, 7)] == _svc_valid_entry.runtime_data._thermal_params.dhw_windows,
    f"{_svc_valid_entry.runtime_data._thermal_params.dhw_windows}",
)

# The translations: every new key in all three files, each message naming
# exactly the placeholders its raise passes, strings.json parity with
# en.json (hassfest), and no single-quoted placeholder anywhere (hassfest).
import json as _svc_json  # noqa: E402
import re as _svc_re  # noqa: E402

_SVC_FILES = {}
for _svc_label, _svc_path in (
    ("strings", "custom_components/heatpump_optimizer/strings.json"),
    ("en", "custom_components/heatpump_optimizer/translations/en.json"),
    ("sv", "custom_components/heatpump_optimizer/translations/sv.json"),
):
    with open(_svc_path, encoding="utf-8") as _svc_fh:
        _SVC_FILES[_svc_label] = _svc_json.load(_svc_fh).get("exceptions", {})

_svc_missing = {
    f"{label}:{key}"
    for label, block in _SVC_FILES.items()
    for key in _SVC_KEYS
    if key not in block
}
R.check(
    "every operational-failure key exists in strings.json, en.json and sv.json",
    not _svc_missing,
    f"missing: {sorted(_svc_missing)}",
)


def _svc_names(message):
    return set(_svc_re.findall(r"\{([a-z_]+)\}", message))


_svc_bad = []
for _svc_key, (_svc_want, _svc_cls) in _SVC_KEYS.items():
    for _svc_label in ("strings", "en", "sv"):
        _svc_msg = _SVC_FILES[_svc_label].get(_svc_key, {}).get("message", "")
        if _svc_names(_svc_msg) != _svc_want:
            _svc_bad.append(
                f"{_svc_label}:{_svc_key} names {sorted(_svc_names(_svc_msg))} "
                f"want={sorted(_svc_want)}"
            )
        if _svc_re.search(r"'\{[a-z_]+\}'", _svc_msg):
            _svc_bad.append(f"{_svc_label}:{_svc_key} single-quotes a placeholder")
R.check(
    "each operational-failure message names exactly its placeholders, unquoted",
    not _svc_bad,
    "; ".join(_svc_bad),
)
R.check(
    "the new keys keep strings.json and en.json parity",
    all(
        _SVC_FILES["strings"].get(k) == _SVC_FILES["en"].get(k)
        for k in _SVC_KEYS
    ),
    "hassfest requires the two files to match",
)

# #222 (decomposition program, child of #193): the service-handler module in
# disguise is a module. Everything in this section is structural -- the
# behavioral sections around it (#294's raises, #321's pre-check, #217's
# translation kwargs) drive the real registry through the real registration
# path and are untouched by the move, which is what makes it
# behavior-invisible. Pinned here: the handlers live in services.py,
# __init__.py defines none of them, and async_setup's registration path
# registers the services module's own functions.
R.section("services.py is the service-handler module (#222)")

import ast as _hpo_ast  # noqa: E402

try:
    from heatpump_optimizer import services as _hpo_services
    _hpo_services_err = ""
except Exception as _hpo_exc:  # noqa: BLE001 - the failure IS the finding
    _hpo_services = None
    _hpo_services_err = f"{type(_hpo_exc).__name__}: {_hpo_exc}"
R.check(
    "heatpump_optimizer.services exists and imports",
    _hpo_services is not None,
    _hpo_services_err or "ok",
)

# The twelve moved definitions (eleven handle_* plus the _manual_targets
# helper the manual-plan trio shares) and the two entry resolvers every
# handler dispatches through.
_HPO_MOVED = (
    "handle_run_optimization",
    "handle_set_mode",
    "handle_set_thermal_params",
    "handle_simulate_plan",
    "handle_assign_entity",
    "handle_apply_topology",
    "handle_apply_schedule",
    "handle_apply_manual_plan",
    "handle_clear_manual_plan",
    "handle_restore_snapshot",
    "handle_diagnose_interval",
    "_manual_targets",
    "_loaded_entries",
    "_loaded_coordinators",
)
_hpo_missing = (
    [
        _hpo_n
        for _hpo_n in _HPO_MOVED
        if not callable(getattr(_hpo_services, _hpo_n, None))
    ]
    if _hpo_services is not None
    else list(_HPO_MOVED)
)
R.check(
    "every service handler and resolver lives at module level in services.py",
    not _hpo_missing,
    f"missing: {_hpo_missing}",
)

_hpo_init_tree = _hpo_ast.parse(
    _Path("custom_components/heatpump_optimizer/__init__.py").read_text()
)
_hpo_defs = {
    _hpo_n.name
    for _hpo_n in _hpo_ast.walk(_hpo_init_tree)
    if isinstance(_hpo_n, (_hpo_ast.FunctionDef, _hpo_ast.AsyncFunctionDef))
}
R.check(
    "__init__.py no longer defines any service handler or resolver",
    not (_hpo_defs & set(_HPO_MOVED)),
    f"still defined in __init__.py: {sorted(_hpo_defs & set(_HPO_MOVED))}",
)
R.check(
    "__init__.py keeps the registration path (_async_register_services)",
    "_async_register_services" in _hpo_defs,
    "async_setup calls it; it is the seam that delegates to services.py",
)

_hpo_params = {}
if _hpo_services is not None:
    for _hpo_n in _HPO_MOVED:
        if _hpo_n.startswith("handle_"):
            _hpo_params[_hpo_n] = list(
                inspect.signature(getattr(_hpo_services, _hpo_n)).parameters
            )
R.check(
    "each handler takes (hass, call) explicitly, the one sanctioned change",
    bool(_hpo_params)
    and all(_hpo_v == ["hass", "call"] for _hpo_v in _hpo_params.values()),
    "; ".join(f"{k}={v}" for k, v in _hpo_params.items()) or "no module",
)

# service name -> the handler function that must be behind it. Driving
# async_setup on a fresh hass and asking the registry for identity (not
# just presence) proves __init__'s path delegates to the module rather
# than registering functions of its own.
_HPO_SERVICE_MAP = {
    "run_optimization": "handle_run_optimization",
    "set_mode": "handle_set_mode",
    "set_thermal_parameters": "handle_set_thermal_params",
    "simulate_plan": "handle_simulate_plan",
    "assign_entity": "handle_assign_entity",
    "apply_topology": "handle_apply_topology",
    "apply_schedule": "handle_apply_schedule",
    "apply_manual_plan": "handle_apply_manual_plan",
    "clear_manual_plan": "handle_clear_manual_plan",
    "restore_learned_snapshot": "handle_restore_snapshot",
    "diagnose_interval": "handle_diagnose_interval",
}
_hpo_hass = FakeHass()
_asyncio.run(_ha_setup_component(_integ, _hpo_hass))
_hpo_registered = _hpo_hass.services.async_services().get(_DOMAIN, {})
R.check(
    "async_setup registers all eleven services, unchanged",
    set(_hpo_registered) == set(_HPO_SERVICE_MAP),
    f"registered: {sorted(_hpo_registered)}",
)
# The registry calls a handler with one argument (the ServiceCall), so the
# module functions -- which take (hass, call) -- are registered bound to the
# registering hass via functools.partial. The identity asked for is the
# function behind the binding, and that the binding carries that same hass.
_hpo_wrong = []
for _hpo_svc, _hpo_fn in _HPO_SERVICE_MAP.items():
    _hpo_obj = _hpo_registered.get(_hpo_svc)
    if (
        getattr(_hpo_obj, "func", _hpo_obj)
        is not getattr(_hpo_services, _hpo_fn, None)
        or tuple(getattr(_hpo_obj, "args", ())) != (_hpo_hass,)
    ):
        _hpo_wrong.append(f"{_hpo_svc}:{_hpo_fn}")
R.check(
    "the registration path registers the services module's own functions",
    _hpo_services is not None and not _hpo_wrong,
    "; ".join(_hpo_wrong) or "ok",
)

_hpo_services_path = _Path("custom_components/heatpump_optimizer/services.py")
_hpo_reg_sites = 0
if _hpo_services_path.exists():
    for _hpo_n in _hpo_ast.walk(_hpo_ast.parse(_hpo_services_path.read_text())):
        if (
            isinstance(_hpo_n, _hpo_ast.Call)
            and isinstance(_hpo_n.func, _hpo_ast.Attribute)
            and _hpo_n.func.attr == "async_register"
        ):
            _hpo_reg_sites += 1
R.check(
    "the eleven registration sites live in services.py, none in __init__.py",
    _hpo_reg_sites == 11
    and not any(
        isinstance(_hpo_n, _hpo_ast.Call)
        and isinstance(_hpo_n.func, _hpo_ast.Attribute)
        and _hpo_n.func.attr == "async_register"
        for _hpo_n in _hpo_ast.walk(_hpo_init_tree)
    ),
    f"services.py: {_hpo_reg_sites} registration site(s)",
)

# #361: the budget table's recorded_at must name a commit a reader can resolve.
# A re-record only ever happens on a branch, and a branch commit is rewritten
# by the next --amend and deleted by the squash-merge that lands it -- so
# stamping HEAD wrote a SHA that resolves to nothing, and the committed value
# was correct only when somebody noticed and fixed it by hand. Pinned by AST
# rather than by running git, so the check cannot flake on a shallow clone.
_hpo_struct_tree = _hpo_ast.parse(_Path("tests/structure.py").read_text())
_hpo_recorded_at_src = [
    _hpo_ast.dump(_hpo_n.value)
    for _hpo_n in _hpo_ast.walk(_hpo_struct_tree)
    if isinstance(_hpo_n, _hpo_ast.Assign)
    and any(
        isinstance(_hpo_t, _hpo_ast.Subscript)
        and isinstance(_hpo_t.slice, _hpo_ast.Constant)
        and _hpo_t.slice.value == "recorded_at"
        for _hpo_t in _hpo_n.targets
    )
]
R.check(
    "structure.py stamps recorded_at from the merge base, never from HEAD (#361)",
    len(_hpo_recorded_at_src) == 1
    and "recorded_at_sha" in _hpo_recorded_at_src[0]
    and "head_sha" not in _hpo_recorded_at_src[0],
    f"assignments to recorded_at: {_hpo_recorded_at_src or 'none found'}",
)
# The distinction that matters: the branch must COUNT the failure, not print a
# note. A note is what let this defect survive two instances.
_hpo_ratchet_fn = next(
    (
        _hpo_n
        for _hpo_n in _hpo_ast.walk(_hpo_struct_tree)
        if isinstance(_hpo_n, _hpo_ast.FunctionDef) and _hpo_n.name == "ratchet"
    ),
    None,
)
_hpo_unreach_vars = {
    _hpo_t.id
    for _hpo_a in _hpo_ast.walk(_hpo_ratchet_fn or _hpo_ast.Module(body=[], type_ignores=[]))
    if isinstance(_hpo_a, _hpo_ast.Assign)
    and "recorded_at_unreachable" in _hpo_ast.dump(_hpo_a.value)
    for _hpo_t in _hpo_a.targets
    if isinstance(_hpo_t, _hpo_ast.Name)
}
_hpo_counts_it = any(
    isinstance(_hpo_i, _hpo_ast.If)
    and (_hpo_unreach_vars & {
        _hpo_x.id
        for _hpo_x in _hpo_ast.walk(_hpo_i.test)
        if isinstance(_hpo_x, _hpo_ast.Name)
    })
    and any(
        isinstance(_hpo_g, _hpo_ast.AugAssign)
        and isinstance(_hpo_g.target, _hpo_ast.Name)
        and _hpo_g.target.id == "failures"
        for _hpo_stmt in _hpo_i.body
        for _hpo_g in _hpo_ast.walk(_hpo_stmt)
    )
    for _hpo_i in _hpo_ast.walk(_hpo_ratchet_fn or _hpo_ast.Module(body=[], type_ignores=[]))
)
R.check(
    "an unresolvable recorded_at FAILS the ratchet, it is not merely noted (#361)",
    bool(_hpo_unreach_vars) and _hpo_counts_it,
    f"ratchet() must branch on recorded_at_unreachable and increment failures "
    f"inside that branch (vars={sorted(_hpo_unreach_vars)}, counts={_hpo_counts_it})",
)
R.check(
    "recorded_at_sha prefers the upstream merge base and falls back to HEAD (#361)",
    any(
        isinstance(_hpo_n, _hpo_ast.FunctionDef)
        and _hpo_n.name == "recorded_at_sha"
        and "merge-base" in _hpo_ast.dump(_hpo_n)
        and "head_sha" in _hpo_ast.dump(_hpo_n)
        for _hpo_n in _hpo_ast.walk(_hpo_struct_tree)
    ),
    "recorded_at_sha must call git merge-base and keep head_sha as the fallback",
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
_g_room, _g_slab, _g_up, _g_low, *_ = _g_stiff.simulate_trajectory(
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
    parse_day_range as _fee_day_range,
    parse_rules as _fee_parse,
)
from heatpump_optimizer.optimizer import (
    PRICE_MEAN_GUESS_EPS as _GUESS_EPS,
    _price_guess_weights as _guess_weights,
)
from heatpump_optimizer.price_model import (
    quarters_from_entries as _quarters_from_entries,
)

# D3-07: ``parse_day_range``'s wrap-around branch (``start > end`` -> Fri..Sun..Mon)
# is only reached when a configured day-range string actually wraps across the
# week boundary; every day-range string used anywhere else in this suite
# ("Mon-Fri", "Mån-Fre", "Lör-Sön") is non-wrapping and takes the other branch.
# Deleting the wrap branch silently resolves a wrapping spec to an empty set
# (Python's own ``range(start, end+1)`` is empty when start > end) with no
# error and no log. Fri=4, Sat=5, Sun=6, Mon=0, Tue=1 in this module's own
# weekday numbering.
R.check(
    "a Fri-Mon wrap covers Friday through Monday, inclusive",
    _fee_day_range("Fri-Mon") == frozenset({4, 5, 6, 0}),
    str(_fee_day_range("Fri-Mon")),
)
R.check(
    "Saturday, Sunday and Monday are all inside a Fri-Mon wrap",
    5 in _fee_day_range("Fri-Mon")
    and 6 in _fee_day_range("Fri-Mon")
    and 0 in _fee_day_range("Fri-Mon"),
)
R.check(
    "Tuesday is outside a Fri-Mon wrap",
    1 not in _fee_day_range("Fri-Mon"),
    "a deleted wrap branch resolves to an EMPTY set, which would also "
    "(vacuously) satisfy 'Tuesday is not in it' — paired with the "
    "membership check above, this closes that gap",
)
R.check(
    "a Fri-Mon wrap is not silently empty",
    len(_fee_day_range("Fri-Mon")) == 4,
    "the exact failure mode this asserts against: the deleted branch's "
    "start>end range() is empty, so a wrapping rule would silently apply "
    "on zero days",
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
    == {"rate", "source", "currency"},
    # D4-04 (#168): the notice names the instance currency, not SEK.
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

# D4-05 (#169), the store layer: the form now refuses a negative rate, but a
# store written before the fix, or a fee sensor publishing a negative value,
# still reaches the plan as a subsidy. Warn-only like the magnitude audit --
# the plan keeps pricing with exactly what is configured -- and named.


def _sign_issues(hass):
    return [i for i in getattr(hass, "issues", []) if i[1] == "grid_fee_sign"]


_gf_neg = HeatPumpOptimizerCoordinator(
    FakeHass(),
    FakeEntry(
        data={**_LC_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= -0.25"}
    ),
)
_gf_neg_vec = _gf_neg._fee_series(_gf_steps)
R.check(
    "a stored negative rule raises the sign notice, attributed to the rules",
    len(_sign_issues(_gf_neg.hass)) == 1
    and _sign_issues(_gf_neg.hass)[0][2].get("translation_key") == "grid_fee_sign"
    and _sign_issues(_gf_neg.hass)[0][2]["translation_placeholders"]
    == {"rate": "-0.25", "source": "rules", "currency": _gf_neg.currency}
    and _sign_issues(_gf_neg.hass)[0][2].get("is_persistent") is True,
    str(_sign_issues(_gf_neg.hass)),
)
R.check(
    "warn-only: the plan still prices with the negative value it was given",
    bool(np.all(_gf_neg_vec == -0.25)),
    f"vector {_gf_neg_vec[:2]}",
)
_gf_neg._fee_series(_gf_steps)
R.check(
    "the sign notice is raised once per offending value, not every cycle",
    len(_sign_issues(_gf_neg.hass)) == 1,
)
R.check(
    "and a negative rate of ordinary size is not mistaken for a magnitude slip",
    not [
        i
        for i in getattr(_gf_neg.hass, "issues", [])
        if i[1] == "grid_fee_magnitude"
    ],
)
_gf_neg._config["grid_fee_rules"] = "= 0.25"
_gf_neg._fee_series(_gf_steps)
R.check(
    "correcting the sign clears the notice on the next cycle",
    not _sign_issues(_gf_neg.hass),
)
_gf_neg_ent = HeatPumpOptimizerCoordinator(
    FakeHass({"sensor.fee": FakeState("-0.4")}),
    FakeEntry(
        data={**_LC_DATA, "grid_fee_mode": "entity", "grid_fee_entity": "sensor.fee"}
    ),
)
_gf_neg_ent._fee_series(_gf_steps)
R.check(
    "a fee sensor publishing a negative value trips the same notice, attributed to it",
    len(_sign_issues(_gf_neg_ent.hass)) == 1
    and _sign_issues(_gf_neg_ent.hass)[0][2]["translation_placeholders"]["source"]
    == "entity",
)
R.check(
    "the magnitude notice and the sign notice are independent: -25 raises both",
    (
        lambda c: (
            c._fee_series(_gf_steps) is not None
            and len(_sign_issues(c.hass)) == 1
            and len(
                [
                    i
                    for i in getattr(c.hass, "issues", [])
                    if i[1] == "grid_fee_magnitude"
                ]
            )
            == 1
        )
    )(
        HeatPumpOptimizerCoordinator(
            FakeHass(),
            FakeEntry(
                data={**_LC_DATA, "grid_fee_mode": "rules", "grid_fee_rules": "= -25"}
            ),
        )
    ),
)
R.check(
    "0.25 SEK/kWh raises neither",
    not _sign_issues(_gf_ok.hass),
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
# v5.4.0: the credit repays that cost times the fraction of the stored heat
# the next window actually gets to spend. The identity is unchanged in
# substance -- no artificial COP gap either way -- but a tank that leaks
# before its heat is wanted repays less than it cost, on purpose. Pinned
# against the factor rather than loosened to a tolerance, so a change to the
# discount still fails here.
_surv5 = _opt5._buffer_survival(_out5, None, _caps5["buffer"])
R.check(
    "the terminal credit repays a stored buffer kWh at the flow-derated COP "
    "the simulation charged to store it, less what the tank loses first",
    abs(_grad_buf - _sim_cost * _surv5) < 1e-9,
    f"terminal {_grad_buf:.4f} vs simulate {_sim_cost:.4f} x survival "
    f"{_surv5:.4f} = {_sim_cost * _surv5:.4f} SEK/kWh",
)
R.check(
    "and at -5 C that haircut is small: winter storage is not discouraged",
    0.95 < _surv5 < 1.0,
    f"survival {_surv5:.4f} must be a real discount, but a slight one, when "
    "the house is drawing hard enough to spend the tank within hours",
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
# fixture untouched. This fixture is not itself unthrottled (it has a valve
# and a 750 L tank, so the tank IS a store); what it pins is the single-sum
# path taken when cop_buffer == cop_end. v5.4.0 adds the survival factor to
# the buffer's share, so the expectation carries it — computed from the
# optimizer rather than hardcoded, which keeps this an arithmetic-identity
# check and not a second implementation of the discount.
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
        * _opt5_off._buffer_survival(_out5, None, _caps5_off["buffer"])
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
    # Strictly above, not by a wide margin: the mixed-use draw reference
    # (40 °C) keeps the debit at full nominal further down than the old
    # setpoint ramp did, so a cold tank legitimately runs closer to the
    # inlet — what must never happen is touching it (the floor would then
    # be fabricating heat, and the ledger check above asserts it is not).
    min(_ec_T) > _ec_p.dhw_inlet_reference + 0.05,
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
# v5.1.10 split the rating from the everyday charge limit: this clamp is the
# RATING, because a disinfection cycle is meant to go above the limit and
# clamping it here would cap the cycle at the setpoint.
_hot = _ec_m.simulate_dhw_step(54.0, 500.0, 0.0, dt_hours=0.25, draw_power=0.0)
R.check(
    "charging cannot pass the tank rating, and the excess is booked",
    _hot == _ec_p.dhw_hard_max_temp and _ec_m._step_dhw_refused > 0.0,
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
    PHASE_SETTLING as _PH_SETTLE,
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

# --- D2-01/D7-02: noise-robust sysid, and an adoption gate that can open --
R.section("sysid under sensor noise (D2-01) and a reachable gate (D7-02)")

_NOISE_SEED = 20260902


def _noisy_sid_samples(noise_c, cadence_min=30, seed=_NOISE_SEED):
    """A truth-known step/relax window with iid sensor noise, one seed."""
    rng = np.random.default_rng(seed)
    ua, cap, gains = 0.28, 12.0, 0.3
    p_step, t_out = 10.8, -3.0
    temp = 20.5
    when = datetime(2026, 2, 12, 23, 30, tzinfo=UTC)
    dt_h = cadence_min / 60.0
    out = []
    t = 0.0
    while t < 5.0:
        phase = (
            _PH_STEP if 1.0 <= t < 3.0
            else (_PH_RELAX if 3.0 <= t < 5.0 else "settle")
        )
        power = p_step if phase == _PH_STEP else 0.0
        if phase in (_PH_STEP, _PH_RELAX):
            out.append(_SidSample(
                when, temp + rng.normal(0.0, noise_c),
                t_out + rng.normal(0.0, noise_c * 0.5), power, phase,
            ))
        temp += (power + gains - ua * (temp - t_out)) / cap * dt_h
        when += timedelta(minutes=cadence_min)
        t += dt_h
    return out


# Ensemble-level assertion (single-seed checks cannot separate the
# correction from the Bayesian prior: the mutation proof caught exactly
# that -- a one-seed bias bound passed with the correction deleted).
# The pre-C2 production code measured p90 +54 % at 0.10 degC noise on
# this same harness; the load-bearing half of the fix is the noise
# gate, and the p90 over an ensemble is what it protects.
_ens_bias, _ens_done, _ens_refused = [], 0, 0
for _seed in range(20260902, 20260942):
    _e = SystemIdentification()
    _e.samples = _noisy_sid_samples(0.10, seed=_seed)
    _er = _e.identify()
    if _er.completed and _er.heat_loss_kw_per_c is not None:
        _ens_done += 1
        _ens_bias.append(
            (_er.heat_loss_kw_per_c - 0.28) / 0.28 * 100.0
        )
    elif _er.reason == "sensor noise dominates the excursion":
        _ens_refused += 1
R.check(
    "a 40-seed 0.10 degC ensemble: the worst-window noise gate engages",
    _ens_refused >= 10 and _ens_done >= 15,
    f"completed {_ens_done}, refused-for-noise {_ens_refused} of 40",
)
R.check(
    "the ensemble's UA bias p90 is inside 15 % (pre-fix production: +54 %)",
    bool(_ens_bias)
    and float(np.percentile(np.abs(_ens_bias), 90)) < 15.0
    and abs(float(np.median(_ens_bias))) < 8.0,
    f"n={len(_ens_bias)}, median {np.median(_ens_bias):+.1f} %, "
    f"|bias| p90 {np.percentile(np.abs(_ens_bias), 90):.1f} %",
)
# The uncorrected comparator on the worst completing seed's rows -- the
# v4.0.5 section's own technique -- showing what the gate + correction
# stand between.
_worst_i = int(np.argmax(np.abs(_ens_bias))) if _ens_bias else 0
_WORST = SystemIdentification()
_WORST.samples = _noisy_sid_samples(0.10, seed=20260902 + _worst_i)
_wr = _WORST.identify()
_nr, _nt = [], []
for _prv, _cur in zip(_WORST.samples, _WORST.samples[1:]):
    _dth = (_cur.when - _prv.when).total_seconds() / 3600.0
    _nr.append([-(_prv.room_temp - _prv.outdoor_temp), _prv.power_kw, 1.0])
    _nt.append((_cur.room_temp - _prv.room_temp) / _dth)
_ols, *_ = np.linalg.lstsq(np.asarray(_nr), np.asarray(_nt), rcond=None)
_uncorrected_bias = (float(_ols[0]) / float(_ols[1]) - 0.28) / 0.28 * 100.0
R.check(
    "raw uncorrected OLS on the same rows is far worse (the comparator)",
    abs(_uncorrected_bias) > 20.0,
    f"raw OLS {_uncorrected_bias:+.1f} % vs production "
    f"{_wr.heat_loss_kw_per_c and round((_wr.heat_loss_kw_per_c - 0.28) / 0.28 * 100, 1):+} %"
    if _wr.completed
    else f"raw OLS {_uncorrected_bias:+.1f} % (production refused: {_wr.reason})",
)
_BRUTAL = SystemIdentification()
_BRUTAL.samples = _noisy_sid_samples(0.45)
R.check(
    "a window whose noise swamps the excursion is refused outright",
    (not _BRUTAL.identify().completed)
    and _BRUTAL.identify().reason == "sensor noise dominates the excursion",
    _BRUTAL.identify().reason,
)
# D7-02: at the DEFAULT protocol (30-min cadence, excursion bounded by the
# 0.8 °C comfort constraint) the gate can actually open. The old formula
# capped confidence at rows/20 x excursion/2 ~ 0.13 -- unreachable.
_CLEAN = SystemIdentification()
_CLEAN.samples = _noisy_sid_samples(0.0)
_clean_res = _CLEAN.identify()
R.check(
    "a clean default-protocol experiment is adoptable (gate can open)",
    _clean_res.completed and _clean_res.confidence >= 0.3,
    f"confidence {_clean_res.confidence:.3f} (reason {_clean_res.reason})",
)
_NOISY2 = SystemIdentification()
_NOISY2.samples = _noisy_sid_samples(0.08, cadence_min=15, seed=20260904)
R.check(
    "a noisy experiment's confidence is discounted, not just its bias",
    _NOISY2.identify().confidence < _clean_res.confidence,
    f"noisy {_NOISY2.identify().confidence:.3f} vs clean "
    f"{_clean_res.confidence:.3f}",
)

# --- D2-07: a drifting sensor is neither trusted nor believed (#310) ------
R.section("sysid vs a drifting room sensor, and a bound-blind gate (D2-07)")

_DRIFT_UA, _DRIFT_CAP, _DRIFT_G = 0.28, 12.0, 0.3


def _drifting_sid_samples(
    drift_c_per_h, cadence_min=30, settle_power_kw=0.0, record_settle_kw=None,
):
    """The 0.10 °C harness's plant, noise-free, with a LINEAR sensor drift.

    Euler-integrated so the discrete regression's model is exact: with no
    drift the fit must recover UA, C and G to machine precision, which makes
    this the unbiasedness null control. A drifting sensor adds ``d·t`` to the
    room reading only — the contaminant a second-difference noise estimate is
    structurally blind to, because a straight line has no second difference.

    This plant coasts at ``settle_power_kw`` during settle (0 kW by default,
    the committed #325 instrument). Recorded settle power defaults to what
    was actually applied; pass ``record_settle_kw`` only to lie.
    """
    ua, cap, gains = _DRIFT_UA, _DRIFT_CAP, _DRIFT_G
    p_step, t_out = 10.8, -3.0
    temp = 20.5
    when = datetime(2026, 2, 12, 23, 30, tzinfo=UTC)
    dt_h = cadence_min / 60.0
    out = []
    t = 0.0
    while t < 5.0:
        phase = (
            _PH_STEP if 1.0 <= t < 3.0
            else (_PH_RELAX if 3.0 <= t < 5.0 else _PH_SETTLE)
        )
        if phase == _PH_STEP:
            applied = recorded = p_step
        elif phase == _PH_SETTLE:
            applied = settle_power_kw
            recorded = (
                settle_power_kw if record_settle_kw is None else record_settle_kw
            )
        else:
            applied = recorded = 0.0
        out.append(_SidSample(
            when, temp + drift_c_per_h * t, t_out, recorded, phase,
        ))
        temp += (applied + gains - ua * (temp - t_out)) / cap * dt_h
        when += timedelta(minutes=cadence_min)
        t += dt_h
    return out


def _sid_on(samples, **cfg):
    _s = SystemIdentification(SysIdConfig(enabled=True, **cfg))
    _s.samples = samples
    return _s.identify()


_D_CLEAN = _sid_on(_drifting_sid_samples(0.0))
R.check(
    "the unbiasedness null: a noise-free window recovers UA exactly",
    _D_CLEAN.completed
    and abs(_D_CLEAN.heat_loss_kw_per_c / _DRIFT_UA - 1.0) < 5e-4,
    f"UA {_D_CLEAN.heat_loss_kw_per_c} vs truth {_DRIFT_UA} "
    f"({_D_CLEAN.reason})",
)
R.check(
    "a clean sensor is still adopted (the gate stays open at the low end)",
    _D_CLEAN.completed and _D_CLEAN.confidence >= 0.3,
    f"confidence {_D_CLEAN.confidence:.3f} ({_D_CLEAN.reason})",
)
_D_DRIFT = _sid_on(_drifting_sid_samples(0.10))
# The comparator: the same rows through a plain three-column OLS, the fit
# this section's mechanism has to survive.
_dr_rows, _dr_targets = [], []
_D_DRIFT_S = _drifting_sid_samples(0.10)
for _prv, _cur in zip(_D_DRIFT_S, _D_DRIFT_S[1:]):
    _dth = (_cur.when - _prv.when).total_seconds() / 3600.0
    _dr_rows.append([-(_prv.room_temp - _prv.outdoor_temp), _prv.power_kw, 1.0])
    _dr_targets.append((_cur.room_temp - _prv.room_temp) / _dth)
_dr_ols, *_ = np.linalg.lstsq(
    np.asarray(_dr_rows), np.asarray(_dr_targets), rcond=None
)
_dr_ols_ua = float(_dr_ols[0]) / float(_dr_ols[1])
R.check(
    "the comparator: a plain fit on the drifting rows IS biased",
    abs(_dr_ols_ua / _DRIFT_UA - 1.0) > 0.05,
    f"plain OLS UA {_dr_ols_ua:.4f} vs truth {_DRIFT_UA} "
    f"({(_dr_ols_ua / _DRIFT_UA - 1.0) * 100:+.1f} %)",
)
R.check(
    "a 0.10 °C/h drifting sensor no longer biases the identified UA",
    _D_DRIFT.completed
    and abs(_D_DRIFT.heat_loss_kw_per_c / _DRIFT_UA - 1.0) < 0.02,
    f"UA {_D_DRIFT.heat_loss_kw_per_c} vs truth {_DRIFT_UA} "
    f"({_D_DRIFT.reason})",
)
R.check(
    "the drift is identified as such, not absorbed into the house",
    _D_DRIFT.completed
    and getattr(_D_DRIFT, "sensor_drift_c_per_h", None) is not None
    and abs(_D_DRIFT.sensor_drift_c_per_h - 0.10) < 0.01,
    f"fitted drift {getattr(_D_DRIFT, 'sensor_drift_c_per_h', 'ABSENT')} "
    f"°C/h vs 0.10",
)
R.check(
    "drift buys no confidence: the excursion it fakes is not identifiability",
    _D_DRIFT.confidence <= _D_CLEAN.confidence + 1e-3,
    f"drift {_D_DRIFT.confidence:.3f} vs clean {_D_CLEAN.confidence:.3f}",
)
# D7-01's positive control, as a property: the same experiment scored under
# a WIDER comfort bound gathered no less information, so it cannot earn
# less confidence. Normalising the achieved excursion by the CONFIGURED
# bound inverted exactly this, and collapsed the D7 harness's own control.
_D_TIGHT = _sid_on(_drifting_sid_samples(0.0), max_excursion_c=0.8)
_D_WIDE = _sid_on(_drifting_sid_samples(0.0), max_excursion_c=8.0)
R.check(
    "widening the comfort bound cannot lower a finished experiment's "
    "confidence",
    _D_WIDE.completed and _D_TIGHT.completed
    and _D_WIDE.confidence >= _D_TIGHT.confidence - 1e-12,
    f"bound 8.0 -> {_D_WIDE.confidence:.3f}, bound 0.8 -> "
    f"{_D_TIGHT.confidence:.3f}",
)
R.check(
    "an experiment run under a lifted bound is still adoptable",
    _D_WIDE.completed and _D_WIDE.confidence >= 0.3,
    f"confidence {_D_WIDE.confidence:.3f} ({_D_WIDE.reason})",
)

# --- W2-G5: settle power recorded, step sized, settle rows in the fit ------
R.section(
    "sysid settle power, comfort-bounded step sizing, settle window (W2-G5)"
)

from heatpump_optimizer.sysid import (  # noqa: E402
    PHASE_ABORTED as _PH_ABORTED,
    _predict_step_excursion,
)


def _drive_sysid_step(ua, cap, gains, cop, max_el=5.0, cadence_min=30, size=True):
    sid = SystemIdentification(SysIdConfig(enabled=True))
    t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
    sid.arm(t0)
    temp, tout = 21.0, 2.0
    dt_h = cadence_min / 60.0
    when = t0
    prices = np.full(48, 0.5)
    tau = cap / ua
    while when < t0 + timedelta(hours=8):
        plan = max(0.0, ua * (temp - tout) - gains) / max(cop, 0.1)
        kw = dict(
            now=when,
            room_temp=temp,
            outdoor_temp=tout,
            price=0.5,
            price_horizon=prices,
            learner_samples=0,
            max_power_kw=max_el,
            cop=cop,
            plan_power_kw=plan,
        )
        if size:
            kw.update(house_ua=ua, house_capacity=cap, house_gains=gains)
        override = sid.step(**kw)
        if sid.phase in (PHASE_DONE, _PH_ABORTED):
            break
        el = plan if override is None else float(override)
        q = el * cop
        t_ss = tout + (q + gains) / ua
        temp = t_ss + (temp - t_ss) * np.exp(-dt_h / tau)
        when += timedelta(minutes=cadence_min)
    return sid


_G5_EMPTY = {(4, 0.20), (4, 0.35), (4, 0.50), (8, 0.50)}
_G5_SHORT = {(16, 0.50, 2.0)}
_G5_TAU = {(25, 0.10, 2.0), (25, 0.10, 2.5), (25, 0.10, 3.0), (25, 0.10, 3.5)}
_MAIN244_OK = (
    (8, 0.20, 2.0), (8, 0.35, 3.0),
    (16, 0.10, 2.0), (16, 0.10, 2.5), (16, 0.20, 2.0), (16, 0.20, 2.5),
    (16, 0.20, 3.0), (16, 0.35, 2.0), (16, 0.35, 2.5), (16, 0.35, 3.0),
    (16, 0.35, 3.5), (16, 0.50, 3.5),
    (25, 0.20, 2.0), (25, 0.20, 2.5), (25, 0.20, 3.0), (25, 0.20, 3.5),
    (25, 0.35, 2.0), (25, 0.35, 2.5), (25, 0.35, 3.0), (25, 0.35, 3.5),
    (25, 0.50, 2.0), (25, 0.50, 2.5), (25, 0.50, 3.0), (25, 0.50, 3.5),
)
_g5_midstep = _g5_empty = _g5_short = _g5_tau = _g5_other = 0
_g5_done = 0
for _cap in (4, 8, 16, 25):
    for _ua in (0.10, 0.20, 0.35, 0.50):
        for _cop in (2.0, 2.5, 3.0, 3.5):
            _run = _drive_sysid_step(_ua, _cap, 0.3, _cop)
            _reason = _run.result.reason or ""
            if _run.phase == PHASE_DONE and _run.result.completed:
                _g5_done += 1
            elif "drifted beyond" in _reason:
                _g5_midstep += 1
            elif (_cap, _ua) in _G5_EMPTY and "no step fits" in _reason:
                _g5_empty += 1
            elif (_cap, _ua, _cop) in _G5_SHORT and "no step fits" in _reason:
                _g5_short += 1
            elif (_cap, _ua, _cop) in _G5_TAU and "plausible bounds" in _reason:
                _g5_tau += 1
            else:
                _g5_other += 1
R.check(
    "#244: mid-step comfort abort 36/64 -> 0 (sized step, predicted bound)",
    _g5_midstep == 0,
    f"{_g5_midstep} mid-step aborts, {_g5_done}/64 completed",
)
R.check(
    "#244 remaining: 16 empty-band declines (C=4 UA>=0.20 and C=8 UA=0.50)",
    _g5_empty == 16,
    f"{_g5_empty} empty-band declines",
)
R.check(
    "#244 remaining: 1 nameplate-short decline (C=16 UA=0.50 COP=2, Qmin=12 kW, max=10)",
    _g5_short == 1,
    f"{_g5_short} nameplate-short declines",
)
R.check(
    "#244 remaining: 4 identify() tau-guard failures (C=25 UA=0.10, tau=250 h > 200)",
    _g5_tau == 4 and _g5_other == 0 and _g5_done == 43,
    f"tau={_g5_tau} other={_g5_other} done={_g5_done}",
)
R.check(
    "every cell that completed under 0.6 x nameplate still completes",
    all(
        (_r := _drive_sysid_step(_ua, _cap, 0.3, _cop)).phase == PHASE_DONE
        and _r.result.completed
        for _cap, _ua, _cop in _MAIN244_OK
    ),
    "regression on the 24/64 cells main already completed",
)
_g5_null = _drive_sysid_step(0.20, 8.0, 0.3, 1.0, max_el=6.0)
_g5_sr = [s for s in _g5_null.samples if s.phase in (_PH_STEP, _PH_RELAX)]
_g5_sr_sid = SystemIdentification(SysIdConfig(enabled=True))
_g5_sr_sid.samples = _g5_sr
_g5_sr_res = _g5_sr_sid.identify()
_g5_full = _g5_null.identify()
R.check(
    "null: 6.0 kW thermal via real step() completes rows=7 at conf 0.445 "
    "matching identify() on the STEP+RELAX samples (sysid_bias.py plant)",
    _g5_null.result.completed
    and abs(_g5_null._step_power * 1.0 - 6.0) < 1e-9
    and len(_g5_sr) - 1 == 7
    and abs(_g5_sr_res.confidence - 0.445) < 5e-4
    and abs(_g5_full.confidence - _g5_null.result.confidence) < 1e-12,
    f"Pel={_g5_null._step_power:.3f} rows={len(_g5_sr) - 1} "
    f"sr_conf={_g5_sr_res.confidence:.3f} full={_g5_full.confidence:.3f}",
)
_g5_frac30 = _drive_sysid_step(0.20, 8.0, 0.3, 3.0, max_el=6.0, size=False)
_g5_frac15 = _drive_sysid_step(0.20, 8.0, 0.3, 3.0, max_el=3.0, size=False)
R.check(
    "perturbation: 0.3 x nameplate (6 kW el, COP 3, no sizer) completes",
    _g5_frac30.phase == PHASE_DONE
    and _g5_frac30.result.completed
    and abs(_g5_frac30._step_power - 1.8) < 1e-9,
    f"phase={_g5_frac30.phase} conf={_g5_frac30.result.confidence:.3f} "
    f"Pel={_g5_frac30._step_power}",
)
R.check(
    "perturbation: 0.15 x nameplate-equivalent (2.7 kW thermal) aborts on undershoot",
    _g5_frac15.phase == _PH_ABORTED
    and "excursion" in _g5_frac15.result.reason
    and abs(_g5_frac15._step_power - 0.9) < 1e-9,
    f"phase={_g5_frac15.phase} reason={_g5_frac15.result.reason}",
)
_peak, _final = _predict_step_excursion(21.0, 2.0, 0.20, 8.0, 0.3, 9.0, 2.0, 2.0)
R.check(
    "perturbation: 0.6 x nameplate x COP overshoots the comfort band",
    _peak > 0.8,
    f"peak {_peak:.2f} K",
)
_peak30, _ = _predict_step_excursion(21.0, 2.0, 0.20, 8.0, 0.3, 4.5, 2.0, 2.0)
R.check(
    "perturbation: 0.3 x nameplate x COP lands inside the band",
    _peak30 <= 0.8,
    f"peak {_peak30:.2f} K",
)
_settle_sid = SystemIdentification(
    SysIdConfig(enabled=True, settle_hours=0.5, step_hours=2.0, relax_hours=2.0)
)
_settle_sid.arm(datetime(2026, 2, 1, 23, 0, tzinfo=UTC))
_settle_t = datetime(2026, 2, 1, 23, 0, tzinfo=UTC)
for _ in range(3):
    _settle_sid.step(
        now=_settle_t,
        room_temp=21.0,
        outdoor_temp=2.0,
        price=0.5,
        price_horizon=np.full(48, 0.5),
        learner_samples=0,
        max_power_kw=5.0,
        cop=3.0,
        plan_power_kw=2.0,
        house_ua=0.20,
        house_capacity=8.0,
        house_gains=0.3,
    )
    _settle_t += timedelta(minutes=30)
_settle_rows = [s for s in _settle_sid.samples if s.phase == _PH_SETTLE]
R.check(
    "settle rows record the plan's delivered thermal power, not zero",
    _settle_rows
    and all(abs(s.power_kw - 6.0) < 1e-9 for s in _settle_rows),
    f"powers {[s.power_kw for s in _settle_rows]}",
)
_D_LIE = _sid_on(_drifting_sid_samples(0.0, settle_power_kw=3.0, record_settle_kw=0.0))
_D_TRUE3 = _sid_on(_drifting_sid_samples(0.0, settle_power_kw=3.0))
R.check(
    "mis-recorded settle 3 kW as 0 kW biases clean UA (#325 trap)",
    _D_LIE.completed
    and (_D_LIE.heat_loss_kw_per_c / _DRIFT_UA - 1.0) < -0.04,
    f"UA err {_D_LIE.heat_loss_kw_per_c / _DRIFT_UA - 1.0:+.3f}",
)
R.check(
    "the same 3 kW settle hour recorded correctly stays unbiased",
    _D_TRUE3.completed
    and abs(_D_TRUE3.heat_loss_kw_per_c / _DRIFT_UA - 1.0) < 5e-4,
    f"UA {_D_TRUE3.heat_loss_kw_per_c} ({_D_TRUE3.reason})",
)
R.check(
    "including the settle hour keeps a clean sensor unbiased (#325 guard)",
    _D_CLEAN.completed
    and abs(_D_CLEAN.heat_loss_kw_per_c / _DRIFT_UA - 1.0) < 5e-4,
    f"UA {_D_CLEAN.heat_loss_kw_per_c} ({_D_CLEAN.reason})",
)
R.check(
    "sigma->0 recovers d exactly on both arms",
    _D_CLEAN.completed
    and abs((_D_CLEAN.sensor_drift_c_per_h or 0.0) - 0.0) < 5e-5
    and _D_DRIFT.completed
    and abs(_D_DRIFT.sensor_drift_c_per_h - 0.10) < 5e-5,
    f"clean d={_D_CLEAN.sensor_drift_c_per_h} drift d={_D_DRIFT.sensor_drift_c_per_h}",
)

# --- D7-05: detected free heat skips the accuracy sample, like a freeze ---
R.section("Free heat skips the accuracy sample (D7-05)")

_xh_pending = {
    "when": dt_util.now() - timedelta(minutes=30),
    "predicted_temp": 20.5,
    "power_kw": 2.0,
    "space_power": 2.0,
    "dhw_power": 0.0,
    "outdoor_temp": -2.0,
    "indoor_entity": "sensor.indoor",
}
# The control's pending must be armed BEFORE the first call consumes and
# replaces the dict it copied -- an early draft copied it after, inherited
# the fresh zero-elapsed pending, and recorded nothing either way.
_xh = _t2_coord()
_xh._external_heat_active = True
_xh._pending_prediction = dict(_xh_pending)
_xh.hass.states.set("sensor.indoor", FakeState("21.9"))
_xh._record_accuracy()
_xh_kept = len(_xh._accuracy.samples)
_xh2 = _t2_coord()
_xh2._external_heat_active = False
_xh2._pending_prediction = dict(_xh_pending)
_xh2.hass.states.set("sensor.indoor", FakeState("21.9"))
_xh2._record_accuracy()
_xh2_kept = len(_xh2._accuracy.samples)
R.check(
    "an interval with detected free heat records no accuracy sample",
    _xh2_kept > _xh_kept,
    f"external-heat kept {_xh_kept}, control kept {_xh2_kept}; "
    f"freeze={_xh2._pump_signals.freeze_reason}",
)

# --- D7-03 (#279): open window skips the accuracy sample -------------------
_xv = _t2_coord()
_xv._vent_cusum.tripped = True
_xv._pending_prediction = dict(_xh_pending)
_xv.hass.states.set("sensor.indoor", FakeState("21.9"))
_xv._record_accuracy()
_xv_kept = len(_xv._accuracy.samples)
_xv2 = _t2_coord()
_xv2._vent_cusum.tripped = False
_xv2._pending_prediction = dict(_xh_pending)
_xv2.hass.states.set("sensor.indoor", FakeState("21.9"))
_xv2._record_accuracy()
_xv2_kept = len(_xv2._accuracy.samples)
R.check(
    "an interval with the open-window detector tripped records no accuracy sample",
    _xv2_kept > _xv_kept,
    f"vent-tripped kept {_xv_kept}, control kept {_xv2_kept}; "
    f"frozen={_xv._learning_frozen('sensor.indoor')!r}",
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
_ip._measured_power = 3.2
R.check(
    "with one, the meter wins, net of the hot-water allocation the meter "
    "cannot tell apart",
    abs(_ip._interval_space_power() - 2.7) < 1e-9,
)
_ip._measured_power = 2.0
R.check(
    "a meter far off the commanded total is a tracking gap: the split "
    "would land the whole error on the space figure, so no sample",
    _ip._interval_space_power() is None,
    f"got {_ip._interval_space_power()}",
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
R.section("v4.0.6 — the floor gets the same physics check the rating has")

# The stress sweep's winter_mild catch: the LP and greedy passes plan on an
# affine tank, the published trajectory runs the real simulation, and the
# gap let a plan satisfying every linear floor drain the real tank ~1-2 °C
# below the promised minimum inside the evening demand window — on main
# too, just under the sweep's tolerance. The repair pass walks the real
# simulation and tops up ahead of each breach.
from heatpump_optimizer.dhw_schedule import (
    hour_in_windows as _fl_in_win,
    parse_windows as _fl_parse,
)
from profiles import house as _fl_house

_fl_cfg = _fl_house(two_zone=False, dhw=True)
_fl_built = _mk_golden(
    two_zone=False, dhw=True,
    price_profile="winter_typical", weather_profile="winter_mild",
)
_fl_opt = _fl_built["optimizer"]
_fl_params = _fl_opt.model.params

def _fl_worst(opt):
    r = opt.optimize(
        _fl_built["state"], _fl_built["prices"], _fl_built["outdoor"],
        _fl_built["wind"], _fl_built["rain"], _fl_built["solar"], _G_START,
    )
    T = np.asarray(r.dhw_temp_trajectory[1:])
    wins = _fl_parse(_fl_cfg.get("dhw_windows", "") or "")
    hours = [(_G_START.hour + i * 0.25) % 24 for i in range(len(T))]
    inside = np.array([_fl_in_win(h, wins) for h in hours])
    return float(max(0.0, _fl_params.dhw_min_temp - T[inside].min()))

_fl_shortfall = _fl_worst(_fl_opt)
R.check(
    "winter_mild's evening window holds the promised minimum",
    _fl_shortfall <= 0.1,
    f"shortfall {_fl_shortfall:.2f} °C",
)
# Mutation value: with the repair neutered, the same solve breaches — the
# check above genuinely depends on the repair, not on planner luck.
_FlOpt = type(_fl_opt)
_fl_orig = _FlOpt._repair_dhw_floor
try:
    _FlOpt._repair_dhw_floor = lambda self, *, plan, **kw: plan
    _fl_mutant = _fl_worst(_fl_opt)
finally:
    _FlOpt._repair_dhw_floor = _fl_orig
R.check(
    "neutering the floor repair reopens the breach (mutation check)",
    _fl_mutant > 0.5,
    f"mutant shortfall {_fl_mutant:.2f} °C",
)

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

R.section("v5.1.1 — reloads that change nothing, and setups that do not solve")

# The setup-time refresh must not run the MPC solve: with the flag set, the
# solve entry point raising is PROOF the light path never reaches it, and the
# call still has to succeed with a publishable payload.
_fr_hass = _FakeHass()
_fr_coord = Coord(_fr_hass, _FakeEntry(data=_LC_DATA))
_fr_calls: list[str] = []


async def _fr_prices_ok() -> None:
    # D10-07 made a failed Tibber fetch fail the whole update (entities go
    # unavailable -- the honest signal). These two checks are about the
    # solve-skip flag, not the fetch, so the fetch succeeds trivially.
    _fr_coord._prices = [{"total": 1.0, "starts_at": "2026-03-28T00:00:00Z"}] * 24


_fr_coord._fetch_tibber_prices = _fr_prices_ok


async def _fr_boom() -> None:
    _fr_calls.append("boom")
    raise AssertionError("the setup refresh ran the solve")


_fr_coord.async_run_optimization = _fr_boom
_fr_coord._skip_solve_once = True
_fr_data = _asyncio.run(_fr_coord._async_update_data())
R.check(
    "with the flag set the first refresh completes without invoking the solve",
    isinstance(_fr_data, dict) and not _fr_calls,
    f"solve calls: {_fr_calls}",
)
R.check(
    "the light payload still carries the live-state keys entities read",
    "mode" in _fr_data and "current_action" in _fr_data
    and "plan_stale" in _fr_data,
    f"keys: {sorted(_fr_data)[:8]}...",
)
R.check(
    "the flag is consumed by the light refresh",
    not _fr_coord._skip_solve_once,
)


async def _fr_note() -> None:
    _fr_calls.append("solved")


_fr_coord.async_run_optimization = _fr_note
_fr_data2 = _asyncio.run(_fr_coord._async_update_data())
R.check(
    "the second refresh solves normally — the flag never latches",
    _fr_calls == ["solved"] and isinstance(_fr_data2, dict),
    f"solve calls: {_fr_calls}",
)

# --- D10-06 / D10-07 / D10-09: unload lifecycle and Tibber failure --------
R.section("Unload lifecycle and Tibber failure semantics (D10-06/07/09)")

from heatpump_optimizer.const import CONF_TIBBER_TOKEN as _CONF_TIBBER_TOKEN  # noqa: E402

# D10-07: a failed price fetch must FAIL the update. Every failure path used
# to return silently, so last_update_success never moved and the entities
# stayed available forever behind stale prices. The stub's session getter
# raises, which is exactly one such failure.
_tib = Coord(_FakeHass(), _FakeEntry(data=_LC_DATA))
_tib._config[_CONF_TIBBER_TOKEN] = "stub-token"
_tib_raised = None
try:
    _asyncio.run(_tib._fetch_tibber_prices())
except Exception as err:  # noqa: BLE001 - the specific class is the assertion
    _tib_raised = err
R.check(
    "a failed Tibber fetch raises UpdateFailed, failing the update cycle",
    type(_tib_raised).__name__ == "UpdateFailed",
    f"raised {type(_tib_raised).__name__}: {_tib_raised}",
)

# D10-09: the outage latches. The first failure logs ERROR; the second must
# not -- a day-long outage used to print the same ERROR on every cycle.
_tib._tibber_outage_cycles = 0
for _ in range(2):
    try:
        _asyncio.run(_tib._fetch_tibber_prices())
    except Exception:  # noqa: BLE001 - expected
        pass
R.check(
    "two failed fetches count two outage cycles (the ERROR logged once)",
    _tib._tibber_outage_cycles == 2,
    f"cycles: {_tib._tibber_outage_cycles}",
)
_tib._tibber_fetch_recovered()
R.check(
    "a successful fetch clears the outage latch",
    _tib._tibber_outage_cycles == 0,
    f"cycles: {_tib._tibber_outage_cycles}",
)

# #216 (round-2 D10-B): the latch must OWN the outage's logging. The four
# in-try failure verdicts (401/403, HTTP != 200, GraphQL errors, no homes)
# call _tibber_fetch_failed from inside _fetch_tibber_prices's try, so the
# UpdateFailed it raises was re-caught by that method's own `except
# Exception` — a second _tibber_fetch_failed entry per poll (latch 10 after
# 5 polls, "recovered after 10 failed cycle(s)") — and the wrapper in
# _async_update_data then logged its own ERROR with traceback on EVERY
# poll. The stub's raising session getter (used above) cannot see this: it
# lands in the except handler directly, where the raise is not re-caught.
# So these polls drive a scriptable session, the pattern of the round-2
# D10-B harness, through the FULL _async_update_data cycle (wrapper
# included) with the rest of the cycle patched to no-ops on the instance.
import logging as _logging  # noqa: E402

import aiohttp as _aiohttp  # noqa: E402

from heatpump_optimizer import coordinator as _coord_mod  # noqa: E402
from heatpump_optimizer.const import MODE_OFF as _MODE_OFF  # noqa: E402


class _ScriptedResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _ScriptedSession:
    """One post() per scripted entry: an Exception is raised (connect
    failure), a (status, payload) pair is returned as the response."""

    def __init__(self, script):
        self._script = list(script)

    def post(self, *args, **kwargs):
        entry = self._script.pop(0)
        if isinstance(entry, Exception):
            raise entry
        status, payload = entry
        return _ScriptedResponse(status, payload)


_TIBBER_OK_PAIR = (
    200,
    {
        "data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
            "today": [{"total": 0.42, "startsAt": "2026-09-02T00:00:00Z",
                       "level": "NORMAL"}],
            "tomorrow": [],
        }}}]}}
    },
)


class _LogCapture(_logging.Handler):
    def __init__(self):
        super().__init__(level=_logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append((record.levelno, record.getMessage()))


async def _drive_outage_polls(coord, script):
    """One full update cycle per scripted entry; returns what the
    integration logged while they ran."""
    capture = _LogCapture()
    logger = _logging.getLogger("heatpump_optimizer")
    real_level, real_session = logger.level, _coord_mod.async_get_clientsession
    logger.addHandler(capture)
    logger.setLevel(_logging.DEBUG)
    _coord_mod.async_get_clientsession = (
        lambda hass, verify_ssl=True: _ScriptedSession(script)
    )
    try:
        for _ in script:
            try:
                await coord._async_update_data()
            except Exception:  # noqa: BLE001 - UpdateFailed is the verdict
                pass
    finally:
        _coord_mod.async_get_clientsession = real_session
        logger.setLevel(real_level)
        logger.removeHandler(capture)
    return capture.records


def _outage_cycle_coord():
    """A coordinator whose update cycle is the Tibber fetch and its real
    wrapper, nothing else: every later step patched to a no-op on the
    instance (the round-2 D10-B harness pattern)."""
    coord = Coord(_FakeHass(), _FakeEntry(data=_LC_DATA))
    coord._config[_CONF_TIBBER_TOKEN] = "stub-token"

    async def _noop(*_a, **_k):
        return None

    for name in (
        "_update_current_state", "_fetch_weather_forecast",
        "_fetch_solar_forecast", "_async_learn_price_shape",
        "_apply_action", "_command_frequency", "_async_drive_pumps",
        "_async_save_accuracy", "_async_save_energy_totals",
        "_async_watch_learning_drift",
    ):
        setattr(coord, name, _noop)
    coord._record_accuracy = lambda *a, **k: None
    coord._track_realised_peak = lambda *a, **k: None
    coord._mode = _MODE_OFF
    return coord


def _error_count(records):
    return sum(1 for lvl, _ in records if lvl >= _logging.ERROR)


# HTTP 500 for five polls: one ERROR (the latch's first-failure record),
# five outage cycles, then a recovery that reports the true length.
_c500 = _outage_cycle_coord()
_c500_records = _asyncio.run(_drive_outage_polls(_c500, [(500, None)] * 5))
R.check(
    "five HTTP-500 polls log exactly one ERROR - the latch owns the transition (#216)",
    _error_count(_c500_records) == 1,
    f"ERROR records: {_error_count(_c500_records)} of {len(_c500_records)}",
)
R.check(
    "five HTTP-500 polls count five outage cycles, not ten (#216)",
    _c500._tibber_outage_cycles == 5,
    f"cycles: {_c500._tibber_outage_cycles}",
)
_c500_recovery = _asyncio.run(_drive_outage_polls(_c500, [_TIBBER_OK_PAIR]))
_c500_infos = [m for lvl, m in _c500_recovery if lvl == _logging.INFO]
R.check(
    "recovery after five failures reports 'after 5 failed cycle(s)' once (#216)",
    len(_c500_infos) == 1
    and "recovered after 5 failed cycle(s)" in _c500_infos[0]
    and _c500._tibber_outage_cycles == 0,
    f"INFO records: {_c500_infos}",
)

# The first-refresh path has its own wrapper with the same re-log: a
# zero-evidence install whose very first poll fails logs once, not twice.
_cfirst = _outage_cycle_coord()
_cfirst._skip_solve_once = True  # the setup-time light refresh
_cfirst_records = _asyncio.run(_drive_outage_polls(_cfirst, [(500, None)]))
R.check(
    "a failed first-refresh poll (zero-evidence install) logs one ERROR, once (#216)",
    _error_count(_cfirst_records) == 1 and _cfirst._tibber_outage_cycles == 1,
    f"ERROR records: {_error_count(_cfirst_records)}, "
    f"cycles: {_cfirst._tibber_outage_cycles}",
)

# Connect failures (aiohttp.ClientError) never re-entered the latch — only
# the wrapper's per-poll ERROR was wrong there. Both numbers must hold.
_cconn = _outage_cycle_coord()
_cconn_records = _asyncio.run(
    _drive_outage_polls(
        _cconn, [_aiohttp.ClientError("connection refused")] * 5
    )
)
R.check(
    "five connect-failure polls also log exactly one ERROR (#216)",
    _error_count(_cconn_records) == 1,
    f"ERROR records: {_error_count(_cconn_records)} of {len(_cconn_records)}",
)
R.check(
    "five connect-failure polls count five outage cycles (already single-counted)",
    _cconn._tibber_outage_cycles == 5,
    f"cycles: {_cconn._tibber_outage_cycles}",
)

# D10-06: the override must run the base class's shutdown. Real HA's
# async_shutdown stops the refresh debouncer and any in-flight refresh; an
# override that drops super() leaks both on every unload/reload. The stub
# records the call for exactly this assertion.
_shut = Coord(_FakeHass(), _FakeEntry(data=_LC_DATA))
_asyncio.run(_shut.async_shutdown())
R.check(
    "async_shutdown runs the base class's shutdown (timer/debouncer leak)",
    _shut.base_shutdown_called,
    "the override dropped super().async_shutdown()",
)

# D1-02 hygiene: fire-and-forget tasks are tracked, and shutdown lets them
# finish rather than orphaning them against a torn-down entry. The shared
# FakeHass closes spawned coroutines (nothing awaits setup tasks there), so
# this one runs on a local hass stand-in whose create_task is real.
class _TaskHass(_FakeHass):
    def async_create_task(self, coro):
        import asyncio as _aio

        try:
            loop = _aio.get_running_loop()
        except RuntimeError:
            # Constructed outside a loop, like the shared fake: close.
            coro.close()
            return None
        return loop.create_task(coro)


_bg = Coord(_TaskHass(), _FakeEntry(data=_LC_DATA))
_bg_done = {"n": 0}


async def _bg_drive() -> None:
    async def _bg_save() -> None:
        _bg_done["n"] += 1

    _bg_task = _bg._spawn(_bg_save())
    R.check(
        "a spawned task is tracked until it lands",
        _bg_task in _bg._background_tasks and not _bg_task.done(),
        "the tracker never saw the task",
    )
    await _bg.async_shutdown()


_asyncio.run(_bg_drive())
R.check(
    "shutdown lets a pending background save finish",
    _bg_done["n"] == 1 and not _bg._background_tasks,
    f"saves done: {_bg_done['n']}, still tracked: {len(_bg._background_tasks)}",
)

# A save that changes nothing must not reload. The options flow rewrites the
# options dict on every page it leaves, so "the listener fired" is not "the
# config changed" — the comparison against the config the loaded coordinator
# was built from (runtime_data) is what tells them apart, and the
# FakeConfigEntries reload ledger is the honest witness.
_nr_hass = _FakeHass()
_nr_entry = _FakeEntry(data=dict(_LC_DATA), options={"target_temp": 21.0})
_asyncio.run(_ha_setup_entry(_integ, _nr_hass, _nr_entry))
_asyncio.run(_integ.async_update_options(_nr_hass, _nr_entry))
R.check(
    "an options save with an unchanged effective config reloads nothing",
    _nr_hass.config_entries.reloaded == [],
    f"reloads: {_nr_hass.config_entries.reloaded}",
)
# The live bug's exact shape: the flow's page-merge copies effective-config
# keys into options. Options differ, the effective config does not.
_nr_entry.options = {**_nr_entry.options, "tibber_token": "x"}
_asyncio.run(_integ.async_update_options(_nr_hass, _nr_entry))
R.check(
    "the page-merge no-op (options rewritten, config identical) skips too",
    _nr_hass.config_entries.reloaded == [],
    f"reloads: {_nr_hass.config_entries.reloaded}",
)
_nr_entry.options = {**_nr_entry.options, "target_temp": 22.0}
_asyncio.run(_integ.async_update_options(_nr_hass, _nr_entry))
R.check(
    "a genuinely changed config reloads exactly once",
    _nr_hass.config_entries.reloaded == [_nr_entry.entry_id],
    f"reloads: {_nr_hass.config_entries.reloaded}",
)
# The fake reload only records the request; do what the real one does —
# unload and set up again — so the new coordinator carries the new config,
# and the same save repeated is a no-op once more.
_asyncio.run(_ha_unload_entry(_integ, _nr_hass, _nr_entry))
_asyncio.run(_ha_setup_entry(_integ, _nr_hass, _nr_entry))
_asyncio.run(_integ.async_update_options(_nr_hass, _nr_entry))
R.check(
    "after the reload the same save skips again: the new coordinator holds the new config",
    _nr_hass.config_entries.reloaded == [_nr_entry.entry_id],
    f"reloads: {_nr_hass.config_entries.reloaded}",
)
# Mutation: the zero-reload results above must hinge on the comparison.
# Take the loaded coordinator away — the guard's memory — and the very same
# unchanged save now reloads, which is what an always-reload listener would
# do every time.
_nr_memory = _nr_entry.runtime_data
del _nr_entry.runtime_data
_asyncio.run(_integ.async_update_options(_nr_hass, _nr_entry))
R.check(
    "removing the coordinator comparison makes the no-op save reload (mutation)",
    len(_nr_hass.config_entries.reloaded) == 2,
    f"reloads: {_nr_hass.config_entries.reloaded}",
)
_nr_entry.runtime_data = _nr_memory
_asyncio.run(_ha_unload_entry(_integ, _nr_hass, _nr_entry))

# The plan survives a reload: unload stashes the published payload, the next
# setup pops it, and the light first refresh returns it without so much as a
# sensor read — an options save must not wait on Tibber. The fetch methods
# raising is the proof. The stash is the one thing that legitimately outlives
# the entry's runtime_data (Home Assistant deletes that on unload), so it
# lives under the integration's own hass.data key, never on the entry.
_ho_hass = _FakeHass()
_ho_entry = _FakeEntry(data=dict(_LC_DATA))
_asyncio.run(_ha_setup_entry(_integ, _ho_hass, _ho_entry))
_ho_old = _ho_entry.runtime_data
_ho_payload = {"mode": "auto", "sentinel": "the pre-reload plan"}
_ho_old.data = _ho_payload
_asyncio.run(_ha_unload_entry(_integ, _ho_hass, _ho_entry))
R.check(
    "unload stashes the last published payload for the next setup",
    _integ._plan_handovers(_ho_hass).get(_ho_entry.entry_id) is _ho_payload,
)
R.check(
    "and the unloaded entry carries no coordinator any more",
    not hasattr(_ho_entry, "runtime_data"),
)
_asyncio.run(_ha_setup_entry(_integ, _ho_hass, _ho_entry))
_ho_new = _ho_entry.runtime_data
R.check(
    "setup always pops the handover — it never outlives one reload",
    _ho_entry.entry_id not in _integ._plan_handovers(_ho_hass)
    and _ho_new is not _ho_old,
)


async def _ho_untouchable(*args, **kwargs) -> None:
    raise AssertionError("the handover path touched a fetch")


for _ho_name in (
    "_update_current_state",
    "_fetch_tibber_prices",
    "_fetch_weather_forecast",
    "_fetch_solar_forecast",
    "_async_learn_price_shape",
    "async_run_optimization",
):
    setattr(_ho_new, _ho_name, _ho_untouchable)
R.check(
    "the reloaded coordinator arrives with the skip-solve flag armed",
    _ho_new._skip_solve_once,
)
_ho_out = _asyncio.run(_ho_new._async_update_data())
R.check(
    "the light refresh returns the handed-over plan itself, fetch-free",
    _ho_out is _ho_payload,
)
R.check(
    "the handover is single-use on the coordinator too",
    _ho_new._reload_handover is None and not _ho_new._skip_solve_once,
)
_asyncio.run(_ha_unload_entry(_integ, _ho_hass, _ho_entry))

R.section("#236/#237/#240 — the coordinator's lifecycle seam")

# The three registrations the coordinator puts on `hass` -- the peak guard's
# meter listener, the defrost watch and the ECL110 MQTT subscription -- are
# spawned from `__init__`, BEFORE `async_setup_entry` awaits the first
# refresh. When Tibber is unreachable at boot that refresh raises
# ConfigEntryNotReady, and Home Assistant then runs the entry's
# `async_on_unload` callbacks and nothing else: no `async_unload_entry`, so
# no `async_shutdown`. Every retry -- about 45 an hour -- used to leave a
# whole live coordinator on the bus.
#
# Everything below runs on a hass whose `async_create_task` is REAL. The
# shared FakeHass closes spawned coroutines, which would make the leak
# unreproducible, and `mqtt.async_subscribe` is swapped for one that returns
# a real unsubscribe -- the stub returns None, so an MQTT leak is invisible
# through it.
from homeassistant.components import mqtt as _lc_mqtt
from homeassistant.exceptions import HomeAssistantError as _HAError
import heatpump_optimizer.coordinator as _coord_mod


class _NotReady(_HAError):
    """Stands in for ConfigEntryNotReady, which the stub does not carry."""


_GUARDED_DATA = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "house_power_entity": "sensor.house_power",
    "heat_pump_defrost_entity": "binary_sensor.defrost",
    "peak_guard_enabled": True,
}


# asyncio grew eager task start in 3.12; below that only the lazy arm is
# reachable, so the eager arm falls back rather than erroring at import.
_EAGER_TASKS = sys.version_info >= (3, 12)


class _BusHass(_FakeHass):
    """A real loop behind async_create_task, and an honest MQTT registry."""

    def __init__(self, states=None, *, eager=True) -> None:
        super().__init__(states)
        self.state_listeners = []
        self.mqtt_subs = []
        self.eager = eager

    def async_create_task(self, coro, name=None, eager_start=None):
        try:
            loop = _asyncio.get_running_loop()
        except RuntimeError:
            coro.close()
            return None
        if self.eager and _EAGER_TASKS:
            # Home Assistant 2024.3+ installs asyncio's eager task factory.
            return _asyncio.Task(coro, loop=loop, eager_start=True)
        # 2024.1-2024.2, and plain asyncio: queued, run on a later iteration.
        # Also the fallback below 3.12, which has no eager_start: the arm
        # degenerates to the lazy one rather than skipping, and the leak this
        # asserts against shows up in both arms (10 listeners either way).
        return loop.create_task(coro)


async def _lc_subscribe(hass, topic, callback, qos=0, **kwargs):
    entry = [topic, callback]
    hass.mqtt_subs.append(entry)

    def _unsub():
        if entry in hass.mqtt_subs:
            hass.mqtt_subs.remove(entry)

    return _unsub


def _lc_bus_states():
    return {
        "sensor.house_power": FakeState("2000", unit="W"),
        "binary_sensor.defrost": FakeState("off"),
    }


async def _notready_retries(retries: int, *, eager: bool, settle: bool) -> dict:
    """`retries` setups that all raise ConfigEntryNotReady, HA's way.

    ``settle`` decides whether the loop is yielded to before the failure --
    a real first refresh is several awaits of network I/O, so it normally is.
    With it off, a lazily started registration task arrives only AFTER the
    entry's unload callbacks have already run: the arm the latch exists for.
    """
    hass = _BusHass(_lc_bus_states(), eager=eager)
    original = Coord.async_config_entry_first_refresh

    async def _raise_not_ready(self):
        if settle:
            for _ in range(6):
                await _asyncio.sleep(0)
        raise _NotReady("Tibber unreachable at boot")

    Coord.async_config_entry_first_refresh = _raise_not_ready
    try:
        for i in range(retries):
            entry = _FakeEntry(data=dict(_GUARDED_DATA), entry_id=f"retry_{i}")
            try:
                await _integ.async_setup_entry(hass, entry)
            except _NotReady:
                # ConfigEntry.async_setup -> _async_process_on_unload, and
                # nothing else, on this path.
                for cb in list(entry._on_unload):
                    cb()
                entry._on_unload.clear()
            for _ in range(6):
                await _asyncio.sleep(0)
    finally:
        Coord.async_config_entry_first_refresh = original

    fired = 0
    event = type("Ev", (), {"data": {"new_state": FakeState("2500", unit="W")}})()
    for _ids, action in list(hass.state_listeners):
        if getattr(action, "__name__", "") == "_on_power_event":
            action(event)
            fired += 1
    return {
        "listeners": len(hass.state_listeners),
        "mqtt_subs": len(hass.mqtt_subs),
        "dead_handler_runs": fired,
    }


_lc_real_subscribe = _lc_mqtt.async_subscribe
_lc_mqtt.async_subscribe = _lc_subscribe
try:
    for _arm_name, _eager in (("eager (HA 2024.3+)", True), ("lazy (HA 2024.1)", False)):
        for _n in (1, 5):
            _leak = _asyncio.run(
                _notready_retries(_n, eager=_eager, settle=True)
            )
            R.check(
                f"{_n} ConfigEntryNotReady retries leak no listener or "
                f"subscription, {_arm_name} (#236)",
                _leak["listeners"] == 0
                and _leak["mqtt_subs"] == 0
                and _leak["dead_handler_runs"] == 0,
                f"{_leak['listeners']} listeners, {_leak['mqtt_subs']} subs, "
                f"{_leak['dead_handler_runs']} dead handlers ran",
            )
    # The arm the panel called load-bearing: on the declared floor the
    # registration tasks start lazily and can arrive AFTER the teardown.
    _late = _asyncio.run(_notready_retries(5, eager=False, settle=False))
    R.check(
        "a registration arriving after the entry's unload callbacks does not "
        "register at all (#236, the lazy-start arm)",
        _late["listeners"] == 0 and _late["mqtt_subs"] == 0,
        f"{_late['listeners']} listeners, {_late['mqtt_subs']} subs",
    )

    # NULL CONTROL. The fix must not have simply stopped the listeners
    # working: a setup that SUCCEEDS still registers all three, the guard
    # still runs on a meter event, and the unload still removes them.
    async def _healthy_lifecycle() -> dict:
        hass = _BusHass(_lc_bus_states(), eager=True)
        entry = _FakeEntry(data=dict(_GUARDED_DATA), entry_id="healthy")
        ok = await _ha_setup_entry(_integ, hass, entry)
        for _ in range(6):
            await _asyncio.sleep(0)
        live = (len(hass.state_listeners), len(hass.mqtt_subs))
        fired = 0
        event = type(
            "Ev", (), {"data": {"new_state": FakeState("2500", unit="W")}}
        )()
        for _ids, action in list(hass.state_listeners):
            if getattr(action, "__name__", "") == "_on_power_event":
                action(event)
                fired += 1
        unloaded = await _ha_unload_entry(_integ, hass, entry)
        return {
            "ok": ok,
            "live": live,
            "fired": fired,
            "unloaded": unloaded,
            "after": (len(hass.state_listeners), len(hass.mqtt_subs)),
        }

    _ctl = _asyncio.run(_healthy_lifecycle())
    R.check(
        "null control: a healthy setup still registers both listeners and the "
        "MQTT subscription, and the guard still fires (#236)",
        _ctl["ok"] and _ctl["live"] == (2, 1) and _ctl["fired"] == 1,
        f"live={_ctl['live']}, guard fired {_ctl['fired']}x",
    )
    R.check(
        "null control: the normal unload still removes every one of them (#236)",
        _ctl["unloaded"] and _ctl["after"] == (0, 0),
        f"after unload={_ctl['after']}",
    )
finally:
    _lc_mqtt.async_subscribe = _lc_real_subscribe

# `async_shutdown` is also called directly -- by `async_unload_entry`, before
# Home Assistant gets to the entry's callbacks, and by any test that tears a
# coordinator down on its own. It has always been where the three
# unsubscribes lived, and moving them into `_release_registrations` must not
# have quietly made the entry's callback the only path that runs them.
async def _direct_shutdown() -> tuple:
    hass = _BusHass(_lc_bus_states(), eager=True)
    coord = Coord(hass, _FakeEntry(data=dict(_GUARDED_DATA), entry_id="direct"))
    for _ in range(6):
        await _asyncio.sleep(0)
    live = (len(hass.state_listeners), len(hass.mqtt_subs))
    await coord.async_shutdown()
    return live, (len(hass.state_listeners), len(hass.mqtt_subs))


_lc_real_subscribe = _lc_mqtt.async_subscribe
_lc_mqtt.async_subscribe = _lc_subscribe
try:
    _ds_live, _ds_after = _asyncio.run(_direct_shutdown())
finally:
    _lc_mqtt.async_subscribe = _lc_real_subscribe
R.check(
    "async_shutdown on its own still drops both listeners and the MQTT "
    "subscription, without the entry's unload callbacks (#236)",
    _ds_live == (2, 1) and _ds_after == (0, 0),
    f"live={_ds_live}, after direct shutdown={_ds_after}",
)

# ---------------------------------------------------------------------------
# #237: an options reload while the scheduled refresh is inside the executor.
#
# `async_shutdown`'s docstring used to claim the base class stops an in-flight
# refresh. It does not: Home Assistant's DataUpdateCoordinator cancels the
# scheduled TIMER and the debouncer, and a refresh already running is a task
# somebody else owns. Nothing between the executor await and `_apply_action`
# consulted a shutdown flag, so the torn-down coordinator commanded the
# supply switch, published two MQTT commands and wrote two stores after its
# own shutdown had returned -- concurrently with its replacement's setup.


class _SolveHass(_FakeHass):
    """Real tasks, a recording service registry, and a holdable executor.

    ``spawn_real`` is off while the coordinator is constructed, so the ten
    fire-and-forget store loads `__init__` spawns are closed rather than run:
    the simulated disk is class-level and shared across this whole file, and a
    timestamp some earlier case wrote is not an input these checks want.
    """

    spawn_real = False

    def __init__(self, states=None) -> None:
        super().__init__(states)
        self.state_listeners = []
        self.entered = None
        self.release = None

    def async_create_task(self, coro, name=None, eager_start=None):
        if not self.spawn_real:
            coro.close()
            return None
        try:
            loop = _asyncio.get_running_loop()
        except RuntimeError:
            coro.close()
            return None
        return loop.create_task(coro)

    async def async_add_executor_job(self, func, *args):
        if self.entered is not None:
            self.entered.set()
        if self.release is not None:
            await self.release.wait()
        return func(*args)


def _solve_coord() -> Coord:
    """A coordinator with prices and forecasts, ready to solve.

    The horizon is anchored on the real clock rather than a fixed day, so the
    published prices are the ones `_forecast_arrays` picks up and the solve
    genuinely runs -- a horizon in the past yields "no_prices" and the
    executor is never reached at all.
    """
    hass = _SolveHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C"),
            "sensor.outdoor": FakeState("-5.0", unit="°C"),
        }
    )
    coord = Coord(
        hass,
        _FakeEntry(
            data={
                "tibber_token": "x",
                "weather_entity": "weather.home",
                "heat_pump_switch_entity": "switch.heat_pump",
                "indoor_temp_entity": "sensor.indoor",
                "outdoor_temp_entity": "sensor.outdoor",
            }
        ),
    )
    hass.spawn_real = True
    coord._skip_solve_once = False
    _t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=1
    )
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (_t0 + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (_t0 + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop():
        return None

    for _name in (
        "_update_current_state",
        "_fetch_tibber_prices",
        "_fetch_weather_forecast",
        "_fetch_solar_forecast",
        "_async_learn_price_shape",
    ):
        setattr(coord, _name, _noop)
    return coord


def _actuations(hass) -> list[str]:
    return [
        f"{domain}.{service}"
        for domain, service, _data in hass.services.calls
        if domain in ("switch", "mqtt")
    ]


async def _mqtt_publish_recording(hass, *a, **k):
    """mqtt.async_publish routed through the honest service registry.

    The committed stub swallows the publish, so the two ECL110 commands the
    plan issues would be invisible; production's own call path is left
    untouched.
    """
    await hass.services.async_call("mqtt", "publish", {})


async def _reload_midsolve(*, hold_the_solve: bool, orphan_task: bool = False) -> dict:
    """Shut the coordinator down while its refresh sits in the executor.

    ``orphan_task`` drops the coordinator's handle on the running refresh
    before the shutdown. That is the arm the audit panel could not settle on
    this box: whether Home Assistant's scheduled interval refresh is a task
    entry unload cancels. With the handle gone nothing cancels the refresh,
    the solve runs to completion, and only the ``_entry_released`` guards
    stand between it and the pump.
    """
    coord = _solve_coord()
    hass = coord.hass
    hass.entered = _asyncio.Event()
    hass.release = _asyncio.Event()

    task = hass.async_create_task(coord._async_update_data())
    await hass.entered.wait()
    if orphan_task:
        coord._refresh_task = None
    before = sum(1 for c in hass.services.calls if c[0] in ("switch", "mqtt"))
    saves_before = sum(_ha_storage.SAVE_COUNTS.values())
    await coord.async_shutdown()
    if hold_the_solve:
        # Let the held solve run to completion anyway, so the guards -- not
        # the cancellation alone -- are what is under test.
        hass.release.set()
    cancelled = False
    try:
        # Shielded and capped: without the cancellation in async_shutdown the
        # refresh is still parked in the executor and would hang the gate
        # rather than report a failed check.
        await _asyncio.wait_for(_asyncio.shield(task), timeout=15.0)
    except _asyncio.CancelledError:
        cancelled = True
    except _asyncio.TimeoutError:
        hass.release.set()
        try:
            await task
        except Exception:  # noqa: BLE001
            pass
    except Exception:  # noqa: BLE001
        pass
    return {
        "cancelled": cancelled or task.cancelled(),
        "post_shutdown_actuations": _actuations(hass)[before:],
        "post_shutdown_saves": sum(_ha_storage.SAVE_COUNTS.values()) - saves_before,
        # getattr, not attribute access: a tree without the fix at all must
        # report a FAILED check here rather than crash the whole script.
        "shutdown_flag": getattr(coord, "_entry_released", None),
    }


async def _solve_after_shutdown() -> tuple:
    """The solve's own tail: does it publish a plan cut before the teardown?"""
    coord = _solve_coord()
    hass = coord.hass
    hass.entered = _asyncio.Event()
    hass.release = _asyncio.Event()
    task = hass.async_create_task(coord.async_run_optimization())
    await hass.entered.wait()
    await coord.async_shutdown()
    hass.release.set()
    status = await task
    return status, coord._optimization_result


async def _uninterrupted_cycle() -> tuple:
    """NULL CONTROL: with no shutdown, the same cycle still actuates and saves."""
    coord = _solve_coord()
    hass = coord.hass
    saves_before = sum(_ha_storage.SAVE_COUNTS.values())
    await coord._async_update_data()
    return (
        _actuations(hass),
        sum(_ha_storage.SAVE_COUNTS.values()) - saves_before,
    )


_lc_real_publish = _lc_mqtt.async_publish
_lc_mqtt.async_publish = _mqtt_publish_recording
try:
    _rl = _asyncio.run(_reload_midsolve(hold_the_solve=True))
    _rl_orphan = _asyncio.run(
        _reload_midsolve(hold_the_solve=True, orphan_task=True)
    )
    _rl_cancel = _asyncio.run(_reload_midsolve(hold_the_solve=False))
    _sa_status, _sa_result = _asyncio.run(_solve_after_shutdown())
    _uc_calls, _uc_saves = _asyncio.run(_uninterrupted_cycle())
finally:
    _lc_mqtt.async_publish = _lc_real_publish

R.check(
    "a solve that finishes after shutdown actuates nothing (#237)",
    _rl["post_shutdown_actuations"] == [],
    f"post-shutdown service calls: {_rl['post_shutdown_actuations']}",
)
R.check(
    "and writes no store after shutdown (#237)",
    _rl["post_shutdown_saves"] == 0,
    f"post-shutdown store writes: {_rl['post_shutdown_saves']}",
)
R.check(
    "async_shutdown latches the shutdown flag the guards read (#237)",
    _rl["shutdown_flag"],
    "the flag was never set",
)
R.check(
    "async_shutdown cancels the in-flight refresh rather than trusting the "
    "base class to have done it (#237)",
    _rl_cancel["cancelled"],
    "the refresh task survived shutdown",
)
R.check(
    "and when nothing cancels the refresh at all -- the ownership question "
    "the panel could not settle -- the guards still stop every actuation "
    "and every store write (#237)",
    _rl_orphan["post_shutdown_actuations"] == []
    and _rl_orphan["post_shutdown_saves"] == 0,
    f"calls={_rl_orphan['post_shutdown_actuations']}, "
    f"writes={_rl_orphan['post_shutdown_saves']}",
)
R.check(
    "a solve completed after shutdown reports it and adopts no plan (#237)",
    _sa_status == "shutdown" and _sa_result is None,
    f"status={_sa_status!r}, result adopted={_sa_result is not None}",
)
R.check(
    "null control: an uninterrupted cycle still commands the pump and saves "
    "(#237 -- the guards fire on shutdown, not on every cycle)",
    len(_uc_calls) == 3 and _uc_saves > 0,
    f"calls={_uc_calls}, store writes={_uc_saves}",
)
# ---------------------------------------------------------------------------
# #240: the what-if's parameters must share no mutable container with the
# live ones. `dataclasses.replace` copies scalars only, so the shadow solve
# carried the live DefrostDerate learner, the live gains profile, the live
# draw pattern and the live windows into the executor, where
# `_record_accuracy`'s once-a-cycle `observe` could write them out from under
# it. The what-if never writes back, so nothing was corrupted -- but the
# answer the card printed was not the answer it was asked.


async def _whatif_scratch_params():
    """The parameter and config objects `async_simulate` actually builds."""
    coord = _solve_coord()
    await coord.async_run_optimization()
    coord._thermal_params.internal_gains_profile = [0.3] * 24
    captured = []
    real_model = _coord_mod.ThermalModel

    class _Spy(real_model):
        def __init__(self, params, *a, **k):
            captured.append(params)
            super().__init__(params, *a, **k)

    _coord_mod.ThermalModel = _Spy
    try:
        coord._last_simulation = None
        payload = await coord.async_simulate({"target_temp": 20.5})
    finally:
        _coord_mod.ThermalModel = real_model
    return coord, captured[-1] if captured else None, payload


_wi_coord, _wi_params, _wi_payload = _asyncio.run(_whatif_scratch_params())
R.check(
    "the what-if actually reached a solve (else the sharing check is vacuous)",
    _wi_params is not None and "cost_delta" in _wi_payload,
    f"payload keys: {sorted(_wi_payload)[:5]}",
)
_wi_shared = [
    _name
    for _name in (
        "defrost_derate",
        "internal_gains_profile",
        "dhw_hourly_draw_pattern",
        "dhw_windows",
    )
    if getattr(_wi_params, _name, None) is not None
    and getattr(_wi_params, _name) is getattr(_wi_coord._thermal_params, _name)
]
R.check(
    "the what-if shares no mutable learner container with the live "
    "parameters (#240)",
    _wi_shared == [],
    f"shared by identity: {_wi_shared}",
)
R.check(
    "the what-if's own defrost learner is a copy, not the live one (#240)",
    _wi_params.defrost_derate is not _wi_coord._defrost,
    "the live DefrostDerate went into the executor",
)


async def _whatif_scratch_config():
    coord = _solve_coord()
    await coord.async_run_optimization()
    captured = []
    real_opt = _coord_mod.HeatPumpOptimizer

    class _OptSpy(real_opt):
        def __init__(self, model, config, *a, **k):
            captured.append(config)
            super().__init__(model, config, *a, **k)

    _coord_mod.HeatPumpOptimizer = _OptSpy
    try:
        coord._last_simulation = None
        await coord.async_simulate({"target_temp": 20.5})
    finally:
        _coord_mod.HeatPumpOptimizer = real_opt
    return coord, captured[-1] if captured else None


_wc_coord, _wc_config = _asyncio.run(_whatif_scratch_config())
R.check(
    "the what-if's optimizer config is a deep copy too, so the live "
    "baseline-load array does not travel with it (#240)",
    _wc_config is not None
    and _wc_config.baseline_load_kw is not _wc_coord._opt_config.baseline_load_kw,
    "the scratch config shares the live baseline load array",
)

R.section("v5.1.3 — an unusable sensor freezes the learners, not just a quiet one")

# The rank-1 finding of the second audit. `_learning_frozen` froze only on
# `problem == "stale"`. Every other unusable-input condition — `unavailable`
# (a flat battery, a Zigbee dropout), `missing_entity` (an entity renamed or
# removed), `not_numeric` (a sensor reporting a word) — left the learners
# running, and `_update_current_state` deliberately PINS the last good value
# on those branches. So the house learner spent the outage regressing against
# a number that had not moved since the sensor died, and persisted the result
# every 10 samples. Measured before the fix: 1.0 -> 0.57 at 24 h -> 0.3737 at
# 48 h, surviving restarts and outliving the outage by weeks.
#
# This drives the REAL path: `_update_current_state` reads real fake states
# through the real `InputReader` and calls the real learners at its foot.
# Nothing is stubbed but the clock and the weather.

_LF_T0 = datetime(2025, 1, 10, 0, 0, tzinfo=UTC)


def _lf_broken_state(condition, t):
    """The indoor sensor as this condition presents it at wall-clock ``t``."""
    if condition == "healthy":
        # A live sensor that actually moves — so "the scale moved" cannot be
        # passing because a flatline happens to look like one.
        return FakeState(f"{21.0 + 0.4 * np.sin(t.hour / 3.0):.2f}",
                         unit="°C", last_updated=t)
    if condition == "stale":
        # Still reporting a perfectly valid number, just 12 hours old.
        return FakeState("21.0", unit="°C", last_updated=t - timedelta(hours=12))
    if condition == "unavailable":
        return FakeState("unavailable", unit="°C", last_updated=t)
    if condition == "missing_entity":
        return None
    if condition == "not_numeric":
        return FakeState("warm", unit="°C", last_updated=t)
    raise AssertionError(condition)


def _lf_drive(condition, cycles=96):
    """96 half-hour cycles (48 h) at -8 °C outdoors. Returns the coordinator."""
    import homeassistant.util.dt as _lf_dt

    hass = _FakeHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C", last_updated=_LF_T0),
            "sensor.outdoor": FakeState("-8.0", unit="°C", last_updated=_LF_T0),
        }
    )
    coord = Coord(
        hass,
        _FakeEntry(
            data={
                "tibber_token": "x",
                "weather_entity": "weather.home",
                "indoor_temp_entity": "sensor.indoor",
                "outdoor_temp_entity": "sensor.outdoor",
            }
        ),
    )
    coord._current_action = {"power": 2.0}
    coord._current_weather = lambda: (0.0, 0.0)
    real_now, real_utcnow = _lf_dt.now, _lf_dt.utcnow
    try:
        for i in range(cycles):
            t = _LF_T0 + timedelta(minutes=30 * i)
            _lf_dt.now = lambda t=t: t
            _lf_dt.utcnow = lambda t=t: t
            state = _lf_broken_state(condition, t)
            if state is None:
                hass.states._states.pop("sensor.indoor", None)
            else:
                hass.states.set("sensor.indoor", state)
            # The outdoor sensor stays healthy throughout, or a freeze would
            # prove nothing about the indoor one.
            hass.states.set(
                "sensor.outdoor", FakeState("-8.0", unit="°C", last_updated=t)
            )
            _asyncio.run(coord._update_current_state())
    finally:
        _lf_dt.now, _lf_dt.utcnow = real_now, real_utcnow
    return coord


# The control first: with the fix in place the learners must still LEARN.
# A freeze predicate that fires on everything would pass all four cases below
# and be a silent regression — every install would stop learning forever.
_lf_ok = _lf_drive("healthy")
R.check(
    "a healthy 48 h still moves the house heat-loss scale",
    _lf_ok._house_heat_loss_scale != 1.0 and _lf_ok._house_heat_loss_samples > 50,
    f"scale {_lf_ok._house_heat_loss_scale:.4f}, "
    f"{_lf_ok._house_heat_loss_samples} samples",
)
R.check(
    "and nothing reports a freeze reason on that run",
    _lf_ok._learner_freeze_reason is None,
    f"got {_lf_ok._learner_freeze_reason!r}",
)

for _lf_cond in ("stale", "unavailable", "missing_entity", "not_numeric"):
    _lf_c = _lf_drive(_lf_cond)
    R.check(
        f"48 h with an indoor sensor that is {_lf_cond} leaves the scale at 1.0",
        _lf_c._house_heat_loss_scale == 1.0,
        f"scale walked to {_lf_c._house_heat_loss_scale:.4f} over "
        f"{_lf_c._house_heat_loss_samples} samples",
    )
    R.check(
        f"no heat-loss sample is taken at all while {_lf_cond}",
        _lf_c._house_heat_loss_samples == 0,
        f"{_lf_c._house_heat_loss_samples} samples",
    )
    R.check(
        f"and the freeze reason names both the condition and the key ({_lf_cond})",
        _lf_c._learner_freeze_reason == f"{_lf_cond}:indoor_temp_entity",
        f"got {_lf_c._learner_freeze_reason!r}",
    )

# The three other consumers of the same predicate, checked on a coordinator
# whose indoor sensor is unavailable rather than stale — the case that used to
# slip through all four.
_lf_u = _lf_drive("unavailable", cycles=2)
R.check(
    "the input-health gate on the drift watchdog sees it too",
    not _lf_u._inputs_healthy(),
    "an unavailable sensor must suppress a drift alarm exactly as a stale "
    "one does, or the watchdog rolls back learners the sensor broke",
)
R.check(
    "the curve comfort tracker's gate sees it",
    _lf_u._learning_frozen("indoor_temp_entity") is not None,
    "a pinned +1 K reads as 'comfortable' and biases the standing ECL "
    "displace down",
)
R.check(
    "the lead-prediction scorer's gate sees it",
    _lf_u._learning_frozen("indoor_temp_entity")
    == "unavailable:indoor_temp_entity",
    f"got {_lf_u._learning_frozen('indoor_temp_entity')!r}",
)

# The pinning itself is deliberate and out of scope: the planner is better off
# steering from the last known room temperature than from nothing. This pins
# that contract so a later change cannot "fix" the wrong half.
R.check(
    "the pinned input is left exactly as it was — this PR bounds the learners "
    "only",
    _lf_u._current_state.room_temperature == 21.0,
    f"room temperature {_lf_u._current_state.room_temperature}",
)


# ===========================================================================
# v5.1.7 — an ordinary slot stops calling itself weather pre-heating
# ===========================================================================
R.section("Plan reason codes: the fall-through is neutral (v5.1.7)")

# `REASON_PREHEAT_WEATHER` was both the high-heat-loss branch AND the
# fall-through default, so every heating step that was not idle, at the floor,
# solar-surplus, terminal or in the cheapest 35 % was published as
# "Pre-heating before colder weather". The card renders exactly that sentence,
# which is what an owner read on a mild afternoon and reported as the
# optimizer chasing weather it had never been shown.
from heatpump_optimizer.optimizer import (  # noqa: E402
    REASON_CHEAP_PRICE as _R_CHEAP,
    REASON_COMFORT_FLOOR as _R_FLOOR,
    REASON_IDLE as _R_IDLE,
    REASON_PREHEAT_WEATHER as _R_PREHEAT,
    REASON_SCHEDULED as _R_SCHED,
    REASON_SOLAR_SURPLUS as _R_SURPLUS,
    REASON_TERMINAL_VALUE as _R_TERMINAL,
    classify_space_steps as _classify,
    slab_settlement_cap as _slab_cap,
)

# Ten steps. Prices rise, so the 35th percentile sits low and the later steps
# are "not cheap"; the room is comfortably above the floor throughout; the
# terminal window is the last step only (max(1, int(0.08 * 10)) == 1).
_n_cl = 10
_pw_cl = np.full(_n_cl, 1.0)
_pr_cl = np.linspace(0.5, 2.0, _n_cl)
_room_cl = np.full(_n_cl + 1, 21.0)
_min_cl = np.full(_n_cl, 19.0)
_hl_cl = np.full(_n_cl, 1.0)  # ordinary weather: nothing to anticipate
_reasons_cl = _classify(_pw_cl, _pr_cl, _room_cl, _min_cl, _hl_cl, None, _n_cl)
R.check(
    "an ordinary mid-price step is no longer called weather pre-heating",
    _R_PREHEAT not in _reasons_cl,
    f"{_reasons_cl}",
)
R.check(
    "it carries the neutral fall-through instead",
    _reasons_cl[5] == _R_SCHED,
    f"step 5 is {_reasons_cl[5]!r} in {_reasons_cl}",
)
R.check(
    "and the cheap steps keep their own, more specific, reason",
    _reasons_cl[0] == _R_CHEAP and _reasons_cl[-1] == _R_TERMINAL,
    f"{_reasons_cl}",
)

# The genuine branch must survive: a step whose heat-loss factor says the
# weather is turning still reports weather pre-heating.
_hl_hot = _hl_cl.copy()
_hl_hot[5] = 1.4
_reasons_hl = _classify(_pw_cl, _pr_cl, _room_cl, _min_cl, _hl_hot, None, _n_cl)
R.check(
    "a real high-heat-loss step still says weather pre-heating",
    _reasons_hl[5] == _R_PREHEAT,
    f"{_reasons_hl}",
)

# Ranking is unchanged: the specific reasons still outrank the fall-through.
_room_low = _room_cl.copy()
# Trajectories carry the initial state at index 0, so step i reads index i+1:
# this is the room at the END of step 3.
_room_low[4] = 19.1
_surplus_cl = np.zeros(_n_cl)
_surplus_cl[4] = 0.5
_pw_idle = _pw_cl.copy()
_pw_idle[2] = 0.0
_ranked = _classify(
    _pw_idle, _pr_cl, _room_low, _min_cl, _hl_cl, _surplus_cl, _n_cl
)
R.check(
    "idle, comfort floor and solar surplus all still outrank it",
    _ranked[2] == _R_IDLE
    and _ranked[3] == _R_FLOOR
    and _ranked[4] == _R_SURPLUS,
    f"{_ranked}",
)

# Every code the classifier can emit needs a sentence in both languages, or a
# plan says nothing in Swedish and shows a raw identifier in English.
for _lang_cl in narrative_mod.TEMPLATES:  # every shipped language
    R.check(
        f"the new reason has a narrative sentence ({_lang_cl})",
        _R_SCHED in narrative_mod.TEMPLATES[_lang_cl],
    )
_card_src_cl = _Path(
    "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
).read_text(encoding="utf-8")
R.check(
    "and a card label in both languages, wired to the code",
    _card_src_cl.count('"reasons.scheduled"') == 3
    and "scheduled: \"reasons.scheduled\"," in _card_src_cl,
)


# ===========================================================================
# v5.1.7 — the slab's battery ceiling is the settlement cap
# ===========================================================================
R.section("Virtual battery: the slab reports against the optimizer's cap")

# `comfort_max + 6.0` was the last magic offset from the v4.0.6 sweep. It is a
# fixed 29.0 at the default ceiling, while the optimizer's own settlement cap
# is weather-dependent -- so the view claimed capacity the plan can never use
# and reported a lower state of charge than the slab actually holds.
_bat_params = ThermalParameters.from_config(
    {"tibber_token": "x", "weather_entity": "weather.home"}
)
_bat_state = ThermalState(
    room_temperature=21.0,
    slab_temperature=24.0,
    outdoor_temperature=-10.0,
    buffer_tank_temperature=None,
)
_bat_cap = _slab_cap(_bat_params, 21.0, -10.0)
_bat_new = battery_view.build(
    _bat_params, _bat_state,
    comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=60.0, cop=3.0,
    slab_max=_bat_cap,
)
_bat_old = battery_view.build(
    _bat_params, _bat_state,
    comfort_min=19.0, comfort_max=23.0,
    dhw_min=45.0, dhw_max=60.0, cop=3.0,
)
_slab_new = next(c for c in _bat_new.components if c.name == "slab")
_slab_old = next(c for c in _bat_old.components if c.name == "slab")
R.check(
    "the slab's ceiling is the settlement cap, not comfort + 6",
    abs(_slab_new.max_temperature - _bat_cap) < 1e-9
    and abs(_slab_old.max_temperature - 29.0) < 1e-9,
    f"cap {_bat_cap:.2f} vs old {_slab_old.max_temperature:.2f}",
)
R.check(
    "which is below the old offset in cold weather, so capacity shrinks",
    _slab_new.usable_capacity_kwh < _slab_old.usable_capacity_kwh
    and _slab_new.soc > _slab_old.soc,
    f"usable {_slab_new.usable_capacity_kwh:.2f} vs "
    f"{_slab_old.usable_capacity_kwh:.2f} kWh, soc "
    f"{_slab_new.soc:.3f} vs {_slab_old.soc:.3f}",
)
# Direction is configuration-dependent, and the release note has to say so.
# A weak emitter needs a HOTTER loop to sustain the target, so on a radiator
# install the settlement cap is far above the old fixed 29 °C, capacity rises
# and the reported charge falls. Both directions are the same correction.
_rad_cfg = presets.derive(
    presets.BuildingPreset(
        structure=presets.STRUCTURE_MASONRY,
        era=presets.ERA_PRE_1960,
        heated_area_m2=250,
        lower_emitter=presets.EMITTER_RADIATORS,
    )
)
_rad_cfg.pop("heating_response_hours", None)
_rad_params = ThermalParameters.from_config(
    {"tibber_token": "x", "weather_entity": "weather.home", **_rad_cfg}
)
_rad_cap = _slab_cap(_rad_params, 21.0, -15.0)
R.check(
    "a radiator install moves the OTHER way: the cap is above comfort + 6",
    _rad_cap > 23.0 + 6.0,
    f"cap {_rad_cap:.1f} °C vs the old fixed 29.0",
)

# The cap is `target + demand / slab_heat_transfer`, unbounded above as that
# coefficient falls. The optimizer has always lived with that; a user-visible
# capacity figure must not, so the view alone clamps to the plant's ceiling.
_tiny = ThermalParameters.from_config(
    {"tibber_token": "x", "weather_entity": "weather.home",
     "slab_heat_transfer": 0.01}
)
_tiny_cap = _slab_cap(_tiny, 21.0, -15.0)
_tiny_slab = next(
    c
    for c in battery_view.build(
        _tiny, _bat_state, comfort_min=19.0, comfort_max=23.0,
        dhw_min=45.0, dhw_max=60.0, cop=3.0, slab_max=_tiny_cap,
    ).components
    if c.name == "slab"
)
R.check(
    "the raw cap is itself bounded at the schema's minimum transfer",
    abs(_tiny_cap - _tiny.buffer_max_temp) < 1e-9,
    f"cap {_tiny_cap:.0f} °C at slab_heat_transfer=0.01 "
    f"(plant ceiling {_tiny.buffer_max_temp} °C)",
)
R.check(
    "but the REPORTED ceiling is clamped to the tank's rating",
    abs(_tiny_slab.max_temperature - _tiny.buffer_max_temp) < 1e-9,
    f"reported {_tiny_slab.max_temperature} vs cap {_tiny_cap:.0f}",
)
R.check(
    "and a realistic cap is left alone by that clamp",
    abs(_slab_new.max_temperature - _bat_cap) < 1e-9
    and _bat_cap < _bat_params.buffer_max_temp,
    f"{_slab_new.max_temperature} vs {_bat_cap}",
)

# The bound is not just for the schema minimum: across EVERY coefficient
# `presets.derive` can emit — swept at the area and upper-ratio bounds,
# every structure, era, foundation, emitter and zone combination — the
# cap must stay inside physically reachable temperatures (issue #87).
# At the default 70 °C plant ceiling the raw worst across that span is
# ~63 °C, so two checks below pin the bound from both sides: the schema
# minimum (0.01 kW/°C, raw cap in the hundreds) and a reachable LOW
# ceiling (45 °C, a low-temperature store) against derive's own worst
# case. Deleting the `buffer_max_temp` min() in slab_settlement_cap
# fails both.
_span_transfers = set()
_span_worst = 0.0
_span_worst_cfg = None
for _structure in (
    presets.STRUCTURE_TIMBER_CRAWLSPACE, presets.STRUCTURE_TIMBER_SLAB,
    presets.STRUCTURE_CONCRETE_SLAB, presets.STRUCTURE_MASONRY,
):
    for _era in (
        presets.ERA_LOW_ENERGY, presets.ERA_1980_2005,
        presets.ERA_PRE_1960,
    ):
        for _foundation in (
            presets.FOUNDATION_NONE, presets.FOUNDATION_CRAWLSPACE,
            presets.FOUNDATION_BASEMENT,
        ):
            for _emitter in (presets.EMITTER_FLOOR, presets.EMITTER_RADIATORS):
                for _two_zone in (False, True):
                    for _area in (20.0, 1000.0):
                        for _ratio in (0.2, 0.8):
                            _cfg = presets.derive(
                                presets.BuildingPreset(
                                    structure=_structure, era=_era,
                                    foundation=_foundation,
                                    heated_area_m2=_area,
                                    lower_emitter=_emitter,
                                    two_zone=_two_zone,
                                    upper_area_ratio=_ratio,
                                )
                            )
                            _cfg.pop("heating_response_hours", None)
                            _p = ThermalParameters.from_config(
                                {"tibber_token": "x",
                                 "weather_entity": "weather.home", **_cfg}
                            )
                            _span_transfers.add(_p.slab_heat_transfer)
                            _c = _slab_cap(_p, 21.0, -25.0)
                            if _c > _span_worst:
                                _span_worst = _c
                                _span_worst_cfg = _cfg
R.check(
    "the settlement cap never leaves physical temperatures across derive's span",
    _span_worst <= 70.0 and _span_worst > 21.0,
    f"worst cap {_span_worst:.1f} °C across {len(_span_transfers)} "
    f"distinct transfer values, min {min(_span_transfers):.3f}",
)
R.check(
    "and the sweep really reached derive's own floor",
    abs(min(_span_transfers) - 0.05) < 1e-9,
    f"minimum emitted slab_heat_transfer {min(_span_transfers)}",
)
# A low-temperature store (the selector runs 40-90 °C) cannot put a
# 63 °C slab under the house: the bound must clamp derive's own worst
# case to the plant it is attached to.
_low_cfg = dict(_span_worst_cfg)
_low_p = ThermalParameters.from_config(
    {"tibber_token": "x", "weather_entity": "weather.home",
     "buffer_max_temperature": 45.0, **_low_cfg}
)
R.check(
    "a low-temperature plant clamps derive's worst case to its own ceiling",
    abs(_slab_cap(_low_p, 21.0, -25.0) - 45.0) < 1e-9
    and _span_worst > 45.0,
    f"capped {_slab_cap(_low_p, 21.0, -25.0):.1f} vs unclamped "
    f"{_span_worst:.1f} °C",
)

R.check(
    "the cap the view reads is the one the optimizer settles against",
    abs(
        _Opt(
            ThermalModel(_bat_params),
            _OptCfg(target_temp=21.0),
        )._settlement_caps(np.full(8, -10.0))["slab"]
        - _bat_cap
    )
    < 1e-9,
)


# ===========================================================================
# v5.1.7 — the comfort band's rules, on every path that writes it
# ===========================================================================
R.section("Comfort band validation is shared, not per-form")

from heatpump_optimizer import comfort_band as _cb  # noqa: E402
from heatpump_optimizer import config_flow as _cf_mod  # noqa: E402

R.check(
    "the config flow's errors are the shared rules",
    _cf_mod._band_errors({"min_temperature": 22.0}, {})
    == _cb.errors({"min_temperature": 22.0}, {}),
)
R.check(
    "a partial write is judged against what would be stored, not itself",
    _cb.errors({"target_temperature": 24.0}, {"max_temperature": 23.0})
    == {"max_temperature": "max_below_target"},
    str(_cb.errors({"target_temperature": 24.0}, {"max_temperature": 23.0})),
)
R.check(
    "a band that agrees with itself raises nothing",
    _cb.errors({}, {}) == {} and _cb.violations({}, {}) == [],
)
R.check(
    "every violation carries a sentence a service caller can be told",
    all(
        v.message and v.field and v.code
        for v in _cb.violations({"min_temperature": 25.0}, {})
    ),
)

R.section("v5.3.0 — the four heat-pump signals, resolved")

# ``pump_signals.read`` is where the four optional slots become the three
# answers the rest of the integration asks. Two rules are load-bearing and
# both are tested here rather than inferred: a value acts and its absence
# never does, and staleness demotes a signal to silence instead of promoting
# it to bad news.

_PS_CFG = {
    "heat_pump_mode_entity": "select.pump_mode",
    "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
    "heat_pump_online_entity": "binary_sensor.pump_online",
    "heat_pump_fault_entity": "binary_sensor.pump_fault",
}
_PS_NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)


#: What Home Assistant's SelectEntity always publishes: the list of options
#: it will accept. The reference integration builds these from the device's
#: mode enum, and `pump_mode` reads a word at face value only from an entity
#: that declares it among them — so a fixture without them is not modelling a
#: select at all.
_PS_SELECT_OPTIONS = [
    "Cooling",
    "Heating",
    "DHW (Hot Water)",
    "Cooling + DHW",
    "Heating + DHW",
]


def _ps_state(entity: str, state, age: float):
    """A FakeState shaped like the entity it stands for."""
    attributes = (
        {"options": list(_PS_SELECT_OPTIONS)}
        if entity.split(".")[0] in ("select", "input_select")
        else None
    )
    return FakeState(
        state, last_updated=minutes_ago(age, _PS_NOW), attributes=attributes
    )


def _ps_read(states, *, config=None, last_good=None, age=2):
    """Resolve the four signals from a set of entity states."""
    stamped = {
        entity: (
            state
            if state is None or isinstance(state, FakeState)
            else _ps_state(entity, state, age)
        )
        for entity, state in states.items()
    }
    reader = InputReader(
        FakeHass({k: v for k, v in stamped.items() if v is not None}),
        _PS_CFG if config is None else config,
        now=lambda: _PS_NOW,
    )
    return pump_signals.read(reader, last_good=last_good), reader


# -- the null case: nothing configured must change nothing ------------------
_ps_none, _ps_none_reader = _ps_read({}, config={})
R.check(
    "with no slots configured the pump can do everything",
    _ps_none.mode is pump_mode.FULL_CAPABILITY
    and not _ps_none.mode_observed
    and _ps_none.mode_source == pump_signals.MODE_SOURCE_ABSENT,
    f"{_ps_none.as_dict()}",
)
R.check(
    "nothing is blocked and nothing is frozen",
    not _ps_none.space_blocked
    and not _ps_none.dhw_blocked
    and _ps_none.freeze_reason is None,
)
R.check(
    "and the three flags are None — no evidence, not False",
    _ps_none.defrosting is None
    and _ps_none.online is None
    and _ps_none.fault is None,
    "False would be a claim; None is the absence of one",
)
R.check(
    "an unconfigured slot never lands in missing_keys",
    _ps_none_reader.health.missing_keys == [],
    "otherwise every install without an optional sensor reports as unhealthy",
)

# -- symmetric suppression, all five modes ----------------------------------
#
# The state Home Assistant holds is the select's LABEL, so these are the
# strings a real Rotenso install actually publishes.
for _label, _blk_space, _blk_dhw, _freeze in (
    ("Heating + DHW", False, False, None),
    ("Heating", False, True, None),
    ("DHW (Hot Water)", True, False, None),
    ("Cooling", True, True, pump_signals.FREEZE_COOLING),
    ("Cooling + DHW", True, False, pump_signals.FREEZE_COOLING),
):
    _sig, _ = _ps_read({"select.pump_mode": _label})
    R.check(
        f"{_label}: space blocked={_blk_space}, hot water blocked={_blk_dhw}",
        _sig.space_blocked is _blk_space and _sig.dhw_blocked is _blk_dhw,
        f"got space={_sig.space_blocked} dhw={_sig.dhw_blocked}",
    )
    R.check(
        f"{_label}: freeze reason {_freeze!r}",
        _sig.freeze_reason == _freeze,
        f"got {_sig.freeze_reason!r}",
    )

# The asymmetry that matters: a heating-only mode suppresses HOT WATER. It is
# the half that is easy to forget, because "the pump is heating" sounds fine.
_sig_heat, _ = _ps_read({"select.pump_mode": "Heating"})
R.check(
    "a heating-only pump must not be promised a hot-water slot",
    _sig_heat.dhw_blocked and not _sig_heat.space_blocked,
    "suppression is symmetric or it is not a capability model",
)

# -- an unrecognised mode plans normally, and says so -----------------------
_sig_odd, _odd_reader = _ps_read({"select.pump_mode": "Turbo Eco Plus"})
R.check(
    "an unrecognised mode falls back to full capability",
    _sig_odd.mode is pump_mode.FULL_CAPABILITY and not _sig_odd.mode_observed,
)
R.check(
    "so nothing is suppressed on the strength of a word nobody recognised",
    not _sig_odd.space_blocked and not _sig_odd.dhw_blocked,
    "in January that would be a cold house",
)
R.check(
    "but the unrecognised word is visible in the diagnostics",
    _odd_reader.health.readings["heat_pump_mode_entity"].problem
    == "unknown_value"
    and "heat_pump_mode_entity" in _odd_reader.health.missing_keys,
    "silent is the one thing it must not be",
)

# -- the last-good fallback --------------------------------------------------
_dhw_only = pump_mode.capability("DHW")
_sig_stale, _ = _ps_read(
    {"select.pump_mode": "DHW (Hot Water)"}, age=600, last_good=_dhw_only
)
R.check(
    "a mode entity that goes stale falls back to the last good mode",
    _sig_stale.mode_observed
    and _sig_stale.mode_source == pump_signals.MODE_SOURCE_LAST_GOOD
    and _sig_stale.space_blocked,
    "the pump did not change mode because its sensor stopped reporting",
)
_sig_never, _ = _ps_read({"select.pump_mode": "DHW (Hot Water)"}, age=600)
R.check(
    "with no last good mode ever seen it falls back to full capability",
    not _sig_never.mode_observed and not _sig_never.space_blocked,
)

# -- online: the value acts, its silence does not ---------------------------
R.check(
    "an online pump does not freeze anything",
    _ps_read({"binary_sensor.pump_online": "on"})[0].freeze_reason is None,
)
R.check(
    "a pump reporting offline freezes the learners",
    _ps_read({"binary_sensor.pump_online": "off"})[0].freeze_reason
    == pump_signals.FREEZE_OFFLINE,
    "this is the ONLY signal that closes the cloud gap: that coordinator "
    "returns stale data with is_online=False and does not raise UpdateFailed, "
    "so nothing about freshness can see it",
)
R.check(
    "a stale online flag does NOT freeze",
    _ps_read(
        {"binary_sensor.pump_online": FakeState("on",
                                                last_updated=minutes_ago(90, _PS_NOW))}
    )[0].freeze_reason
    is None,
    "under MQTT push that integration writes only on change, so a healthy "
    "pump idling overnight goes hours without an update; reading silence as "
    "'the pump is gone' would freeze every MQTT install every night",
)
R.check(
    "an unavailable online flag does not freeze either",
    _ps_read({"binary_sensor.pump_online": "unavailable"})[0].freeze_reason
    is None,
    "in LAN mode the pump's own entities go unavailable when it drops and "
    "v5.1.3's per-key rule already covers that; a second, plant-wide freeze "
    "on the same evidence would fire on a momentary blip too",
)

# -- fault -------------------------------------------------------------------
R.check(
    "a fault freezes the learners",
    _ps_read({"binary_sensor.pump_fault": "on"})[0].freeze_reason
    == pump_signals.FREEZE_FAULT,
)
R.check(
    "a healthy fault flag does not",
    _ps_read({"binary_sensor.pump_fault": "off"})[0].freeze_reason is None,
)
R.check(
    "the RAW fault code sensor works too: 0 is healthy",
    _ps_read({"binary_sensor.pump_fault": "0"})[0].fault is False,
    "the source integration's own mapping is literally value != 0, so "
    "pointing the slot at the code sensor must agree with the binary one",
)
R.check(
    "and any non-zero code is a fault",
    _ps_read({"binary_sensor.pump_fault": "3"})[0].freeze_reason
    == pump_signals.FREEZE_FAULT,
)

# -- precedence --------------------------------------------------------------
_sig_all, _ = _ps_read(
    {
        "select.pump_mode": "Cooling",
        "binary_sensor.pump_online": "off",
        "binary_sensor.pump_fault": "on",
    }
)
R.check(
    "offline outranks fault outranks cooling",
    _sig_all.freeze_reason == pump_signals.FREEZE_OFFLINE,
    "a pump off the network explains its own sensors; reporting the symptom "
    "sends the user to the wrong place",
)

# -- defrost flag ------------------------------------------------------------
R.check(
    "the defrost flag reads through the same guard",
    _ps_read({"binary_sensor.pump_defrost": "on"})[0].defrosting is True
    and _ps_read({"binary_sensor.pump_defrost": "off"})[0].defrosting is False,
)
R.check(
    "a stale defrost flag is no evidence, not 'not defrosting'",
    _ps_read(
        {"binary_sensor.pump_defrost": FakeState("on",
                                                 last_updated=minutes_ago(90, _PS_NOW))}
    )[0].defrosting
    is None,
    "a latched on from yesterday must not keep excluding COP samples",
)


R.section("v5.3.0 — the meter split follows the observed mode")

# ``_interval_space_power`` subtracts THE PLAN'S hot-water allocation from the
# measured total. When the pump is actually in `heat` no hot water was made,
# the whole reading is space heating, and the subtraction hands the house
# heat-loss learner a figure that is too low by exactly the allocation —
# every interval, in the same direction.

_HEAT_ONLY = pump_signals.PumpSignals(
    mode=pump_mode.capability("heat"), mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
)
_DHW_ONLY = pump_signals.PumpSignals(
    mode=pump_mode.capability("DHW"), mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
)


class _Split:
    _commanded_split = Coord._commanded_split
    _commanded_power = Coord._commanded_power
    _interval_space_power = Coord._interval_space_power

    def __init__(self, signals, measured=2.0):
        self._current_action = {"power": 2.0, "dhw_power": 1.0}
        self._config = {"heat_pump_power_entity": "sensor.pump"}
        self._measured_power = measured
        self._immersion_active = False
        self._pump_signals = signals


_sp_blind = _Split(PumpSignals())
R.check(
    "with no mode entity the split is exactly what it always was",
    _sp_blind._commanded_power() == 3.0
    and _sp_blind._commanded_split() == (2.0, 1.0),
    "every pre-v5.3.0 install must be bit-identical",
)
R.check(
    "and a 2.0 kW meter against a 3.0 kW command is still discarded as tracking",
    _sp_blind._interval_space_power() is None,
    "|2.0-3.0|/3.0 = 0.33, past the 0.30 gate — the old behaviour",
)

_sp_heat = _Split(_HEAT_ONLY)
R.check(
    "in `heat` the phantom hot-water allocation is dropped from the command",
    _sp_heat._commanded_split() == (2.0, 0.0)
    and _sp_heat._commanded_power() == 2.0,
)
R.check(
    "so the measured 2.0 kW is recognised as space heating in full",
    _sp_heat._interval_space_power() == 2.0,
    "before v5.3.0 this same interval was thrown away as a tracking error, "
    "and when it was not, 1.0 kW of real space heating went missing",
)

_sp_dhw = _Split(_DHW_ONLY)
R.check(
    "in a hot-water-only mode there is no space figure to extract at all",
    _sp_dhw._interval_space_power() is None,
    "returning 0.0 would be a confident claim that the house got nothing, "
    "which the heat-loss learner would replay as thermal behaviour",
)
R.check(
    "and the commanded space allocation is dropped from the command too",
    _sp_dhw._commanded_split() == (0.0, 1.0),
)


R.section("v5.3.0 — the COP learner uses the curve the mode implies")

# ``_learn_measured_cop`` compared every interval against ``compute_cop`` —
# the SPACE curve — including the ones the pump spent making hot water, where
# the model itself says the COP is ~16 % lower at a 55 °C setpoint.

_cop_space = _CopGate(outdoor=8.0)
_cop_space._learn_measured_cop()
_dhw_action = {"power": 0.0, "dhw_power": 3.0}
_cop_dhw = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
_cop_dhw._current_state.dhw_temperature = 55.0
_cop_dhw._learn_measured_cop()
R.check(
    "a hot-water interval is judged against the DHW curve",
    _cop_dhw._last_measured_cop is not None
    and _cop_dhw._last_measured_cop < _cop_space._last_measured_cop,
    f"dhw {_cop_dhw._last_measured_cop} vs space {_cop_space._last_measured_cop}",
)
_expected_penalty = 1.0 - 0.008 * (55.0 - 35.0)
R.check(
    "and the gap is exactly the model's own DHW penalty, not a fudge",
    abs(
        _cop_dhw._last_measured_cop
        - round(_cop_space._last_measured_cop * _expected_penalty, 2)
    )
    <= 0.02,
    f"{_cop_dhw._last_measured_cop} vs "
    f"{_cop_space._last_measured_cop * _expected_penalty:.2f}",
)
R.check(
    "the reported COP for a healthy pump on the space curve is unchanged",
    _CopGate(outdoor=8.0, action=_dhw_action)._cop_reference_curve()
    == _CopGate(outdoor=8.0)._cop_reference_curve(),
    "without a mode entity the plan's split is not evidence about the pump, "
    "so nothing about the curve choice may change",
)

_HEAT_DHW = pump_signals.PumpSignals(
    mode=pump_mode.capability("HEATDHW"), mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
)
_cop_both = _CopGate(
    outdoor=8.0, signals=_HEAT_DHW, action={"power": 1.5, "dhw_power": 1.5}
)
R.check(
    "a genuinely concurrent interval is skipped, not guessed at",
    _cop_both._cop_reference_curve()[0] is None,
    "HEATDHW runs both duties at once, and one power ratio cannot be "
    "attributed to two curves",
)
_cop_both._learn_measured_cop()
R.check(
    "and it teaches the COP scale nothing",
    _cop_both._cop_samples == 0 and _cop_both._cop_scale == 1.0,
)
_cop_mostly_space = _CopGate(
    outdoor=8.0, signals=_HEAT_DHW, action={"power": 2.9, "dhw_power": 0.1}
)
R.check(
    "a trickle of hot water does not disqualify a space-heating interval",
    _cop_mostly_space._cop_reference_curve()[0] is not None,
)

# The pairing bug: the curve CHOICE used to be recorded as a side effect of
# _cop_reference_curve, but several guards sit between that call and the write
# of _last_measured_cop. A cycle that chose a curve and then returned early
# re-pointed the residual's reference while leaving the stored COP alone — and
# in HEATDHW with an even split that is every cycle on the target hardware.
_cop_pair = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
_cop_pair._current_state.dhw_temperature = 55.0
_cop_pair._learn_measured_cop()
_cop_pair_cop = _cop_pair._last_measured_cop
R.check(
    "the premise: a hot-water interval stores a DHW-referenced COP",
    _cop_pair_cop is not None and _cop_pair._last_cop_curve_dhw
    and _cop_pair._last_cop_dhw_temp == 55.0,
    f"{_cop_pair_cop} dhw={_cop_pair._last_cop_curve_dhw} "
    f"tank={_cop_pair._last_cop_dhw_temp}",
)
# Now a blended cycle, which produces no COP at all.
_cop_pair._pump_signals = _HEAT_DHW
_cop_pair._current_action = {"power": 1.5, "dhw_power": 1.5}
_cop_pair._learn_measured_cop()
R.check(
    "a cycle that produces no COP leaves the stored COP's reference alone",
    _cop_pair._last_measured_cop == _cop_pair_cop
    and _cop_pair._last_cop_curve_dhw
    and _cop_pair._last_cop_dhw_temp == 55.0,
    f"cop {_cop_pair._last_measured_cop} dhw={_cop_pair._last_cop_curve_dhw} "
    f"tank={_cop_pair._last_cop_dhw_temp} — before the fix the flag was "
    f"cleared here and cop_residual then subtracted the SPACE curve from a "
    f"COP that had been referenced to the DHW one",
)
# And a cycle that DOES produce one moves both together.
_cop_pair._pump_signals = PumpSignals()
_cop_pair._current_action = {"power": 3.0}
_cop_pair._learn_measured_cop()
R.check(
    "and a cycle that does produce one moves the pair together",
    _cop_pair._last_measured_cop != _cop_pair_cop
    and not _cop_pair._last_cop_curve_dhw
    and _cop_pair._last_cop_dhw_temp is None,
    f"cop {_cop_pair._last_measured_cop} dhw={_cop_pair._last_cop_curve_dhw}",
)

R.section("v5.3.0 — defrost: duty is measured, the derate is physics")

# Establish the premise first, because it inverts what the flag looks like it
# is for. `defrost.py`'s only learning input WAS `delivered_ratio`, which
# despite its docstring is `predicted_power / actual_power` — purely
# electrical, no heat term. During a real defrost the compressor draws roughly
# normal power while delivering ~zero heat, so that ratio reads ~1.0: a
# perfect unit. Gating the OLD learner on a real defrost flag would therefore
# have taught it "no derate".
_defrost_sample = AccuracySample(
    when=_PS_NOW,
    predicted_power_kw=3.0,
    # A real defrost: the compressor still draws its power.
    actual_power_kw=3.0,
    outdoor_temp=2.0,
)
R.check(
    "the inferred estimator reads a real defrost as a PERFECT interval",
    abs(delivered_ratio(_defrost_sample) - 1.0) < 1e-9,
    "this is why the flag does not simply gate the old learner: it would "
    "learn 'no derate' from the one event the derate exists to model",
)

# And the optimistic bias, which is now bounded by arithmetic.
_opt = DefrostDerate()
for _ in range(200):
    # Tracking gaps mean the pump drew LESS than commanded, so the ratio comes
    # out above 1 — "delivers more than modelled", in the band that exists to
    # be pessimistic.
    _opt.observe(2.0, 80.0, 1.40)
R.check(
    "an over-1 ratio can no longer park the derate above 1.0",
    _opt.factor(2.0, 80.0) <= 1.0 + 1e-9 and DERATE_MAX == 1.0,
    f"factor {_opt.factor(2.0, 80.0):.4f}; a defrost cycle cannot make a heat "
    f"pump exceed its own curve, so the bound is arithmetic",
)

# -- the window ---------------------------------------------------------------
_w = DefrostWindow()
_w.observe(_PS_NOW, False)
_w.observe(_PS_NOW + timedelta(minutes=10), True)
_w.observe(_PS_NOW + timedelta(minutes=15), False)
_wobs = _w.close(_PS_NOW + timedelta(minutes=30))
R.check(
    "five defrosting minutes in thirty is a duty of 1/6",
    abs(_wobs.duty - 5.0 / 30.0) < 1e-9 and _wobs.events == 1,
    f"duty {_wobs.duty}, events {_wobs.events}",
)
R.check(
    "and the interval counts as observed",
    _wobs.observed and _wobs.any_defrost and _wobs.seconds == 1800.0,
)
_w2 = DefrostWindow()
_w2.observe(_PS_NOW, False)
_wobs2 = _w2.close(_PS_NOW + timedelta(minutes=30))
R.check(
    "a quiet interval is duty zero AND observed — that is real evidence",
    _wobs2.observed and _wobs2.duty == 0.0 and not _wobs2.any_defrost,
    "'no defrost happened at 3 °C this hour' is what stops a bucket keeping "
    "a derate it no longer earns",
)
_w3 = DefrostWindow()
_w3.observe(_PS_NOW, None)
_wobs3 = _w3.close(_PS_NOW + timedelta(minutes=30))
R.check(
    "an unreadable flag yields duty zero but NOT observed",
    not _wobs3.observed and not _wobs3.any_defrost,
    "a duty of 0 from an unreadable flag is a claim nobody can make",
)
_w4 = DefrostWindow()
_w4.observe(_PS_NOW, True)
_w4.close(_PS_NOW + timedelta(minutes=30))
_wobs4 = _w4.close(_PS_NOW + timedelta(minutes=60))
R.check(
    "a defrost spanning an interval boundary keeps its second half",
    abs(_wobs4.duty - 1.0) < 1e-9,
    f"duty {_wobs4.duty}; the level carries over across close()",
)

# -- the physics --------------------------------------------------------------
R.check(
    "zero duty is no derate at all",
    derate_from_duty(0.0) == 1.0,
)
R.check(
    "the derate is 1 - duty x the loss multiplier",
    abs(derate_from_duty(0.1) - (1.0 - 0.1 * DEFROST_LOSS_MULTIPLIER)) < 1e-9,
)
R.check(
    "more duty is always a deeper derate, never a shallower one",
    all(
        derate_from_duty(d1) >= derate_from_duty(d2)
        for d1, d2 in zip((0.0, 0.05, 0.1), (0.05, 0.1, 0.2))
    ),
)
R.check(
    "and it is bounded below, so a latched flag cannot zero the pump",
    derate_from_duty(1.0) >= 0.55,
)

_meas = DefrostDerate()
for _ in range(40):
    _meas.observe_duty(2.0, 80.0, 0.10, events=1)
R.check(
    "a measured bucket derates from its counted duty",
    _meas.measured(2.0, 80.0)
    and abs(_meas.factor(2.0, 80.0) - derate_from_duty(0.10)) < 0.01,
    f"factor {_meas.factor(2.0, 80.0):.4f} vs {derate_from_duty(0.10):.4f}",
)
_meas.observe(2.0, 80.0, 1.4)
R.check(
    "and a measurement is never averaged with an inference of the same thing",
    abs(_meas.factor(2.0, 80.0) - derate_from_duty(0.10)) < 0.01,
    "mixing them produces a number that is neither, the more so when the "
    "inference is known to be biased",
)
R.check(
    "an untouched bucket still derates nothing",
    _meas.factor(-20.0, 30.0) == 1.0,
)
_bucket = [b for b in _meas.summary() if b["source"] == "measured"]
R.check(
    "the summary says which estimator a bucket rests on, and how many "
    "defrosts were actually witnessed",
    len(_bucket) == 1 and _bucket[0]["events"] == 40 and "duty" in _bucket[0],
    "a duty counted from three-minute cloud polls is a much weaker number "
    "than the same duty counted from MQTT transitions, and nothing else on "
    "the row would show that",
    )

# -- persistence: an OLD store must load ------------------------------------
_v1_store = {
    "factors": [[0.92, 0.88] for _ in range(6)],
    "counts": [[40, 40] for _ in range(6)],
}
_migrated = DefrostDerate.from_dict(_v1_store)
R.check(
    "a pre-v5.3.0 store loads without raising, and says it was upgraded",
    isinstance(_migrated, DefrostDerate) and _migrated.migrated,
)
R.check(
    "its learned factors are KEPT, not discarded",
    abs(_migrated.factor(2.0, 80.0) - 0.88) < 1e-9
    and _migrated.total_samples == 480,
    f"factor {_migrated.factor(2.0, 80.0)} — a stored factor below 1.0 is "
    f"evidence pointing the careful way; resetting every bucket to 1.0 would "
    f"make frost-band plans LESS conservative on upgrade",
)
_v1_optimistic = DefrostDerate.from_dict(
    {"factors": [[1.05, 1.05] for _ in range(6)],
     "counts": [[40, 40] for _ in range(6)]}
)
R.check(
    "but the estimator's optimistic tail is clamped away on load",
    _v1_optimistic.factor(2.0, 80.0) == 1.0,
    "a derate above 1 says frost makes the pump exceed its own curve; "
    "reading it back unchanged would let the old bound outlive the fix",
)
R.check(
    "a measured duty then overrides the carried-over inference",
    (lambda d: [d.observe_duty(2.0, 80.0, 0.02) for _ in range(40)] and
     abs(d.factor(2.0, 80.0) - derate_from_duty(0.02)) < 0.01)(
        DefrostDerate.from_dict(_v1_store)
    ),
    "the carried value is a floor to stand on until something is counted, "
    "not a prior the measurement has to argue with",
)
R.check(
    "a v2 store round-trips exactly",
    abs(
        DefrostDerate.from_dict(_meas.as_dict()).factor(2.0, 80.0)
        - _meas.factor(2.0, 80.0)
    )
    < 1e-12,
)
R.check(
    "a v2 store still carries factors/counts, so a DOWNGRADE loads too",
    "factors" in _meas.as_dict() and "counts" in _meas.as_dict(),
    "v5.1.5's validator is strict about those two keys and ignores the rest",
)
for _junk in (None, {}, [], "nope", {"factors": "bad", "duty": 3}):
    R.check(
        f"a garbage store loads as empty rather than raising ({_junk!r})",
        DefrostDerate.from_dict(_junk).factor(2.0, 80.0) == 1.0,
    )

# -- the primary win: cop_scale is no longer blind in 0-5 °C ----------------
def _band_window(defrosting: bool):
    """A window covering the elapsed interval, with or without a defrost.

    Stamped from ``dt_util.now`` because that is the clock
    ``_learn_measured_cop`` reads it with, and a window whose stamps cannot be
    compared with the caller's deliberately declines to answer.
    """
    import homeassistant.util.dt as _bw_dt

    origin = _bw_dt.now()
    w = DefrostWindow()
    w.observe(origin - timedelta(minutes=30), False)
    if defrosting:
        w.observe(origin - timedelta(minutes=20), True)
        w.observe(origin - timedelta(minutes=17), False)
    return w


# The tz guard itself: a window it cannot measure must decline, not raise, and
# declining must fall back to the whole-band exclusion.
_band_mixed = DefrostWindow()
_band_mixed.observe(_PS_NOW - timedelta(minutes=30), False)
_band_mixed_gate = _CopGate(outdoor=2.0, defrost=_band_mixed)
_band_mixed_gate._learn_measured_cop()
R.check(
    "a window whose clock cannot be compared measures nothing, and is refused",
    _band_mixed_gate._cop_samples == 0,
    "an uncomparable pair means the elapsed time is unknown, which is not "
    "the same as zero",
)


_band_clean = _CopGate(outdoor=2.0, defrost=_band_window(False))
_band_clean._learn_measured_cop()
R.check(
    "inside 0-5 °C an interval with NO defrost now teaches the COP scale",
    _band_clean._cop_samples == 1 and _band_clean._cop_scale != 1.0,
    "the exclusion covered the whole band because nothing could tell which "
    "intervals the derate owned; in a Swedish shoulder season that blinded "
    "the one multiplier every plan's cost runs through, for most of its "
    "heating hours",
)
_band_defrost = _CopGate(outdoor=2.0, defrost=_band_window(True))
_band_defrost._learn_measured_cop()
R.check(
    "and an interval that DID contain a defrost is still refused",
    _band_defrost._cop_samples == 0 and _band_defrost._cop_scale == 1.0,
    "the attribution stays disjoint, just at a far finer grain",
)
_band_blind = _CopGate(outdoor=2.0)
_band_blind._learn_measured_cop()
R.check(
    "with no defrost evidence the whole band is excluded exactly as before",
    _band_blind._cop_samples == 0 and _band_blind._cop_scale == 1.0,
    "an install with no defrost sensor must be bit-identical to v5.1.5",
)

R.section("v5.3.0 — offline, fault and cooling freeze the real learners")

# The same driver as v5.1.3's: a real coordinator, real `InputReader` reads
# from real fake states, the real learners at the foot of
# `_update_current_state`. Nothing stubbed but the clock. A freeze predicate
# is only worth anything if it actually stops the learner it claims to.

_PSD_T0 = datetime(2025, 1, 10, 0, 0, tzinfo=UTC)


def _psd_drive(states=None, config=None, cycles=96):
    """48 h at -8 °C with a live indoor sensor. Returns the coordinator."""
    import homeassistant.util.dt as _psd_dt

    extra = dict(states or {})
    hass = _FakeHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C", last_updated=_PSD_T0),
            "sensor.outdoor": FakeState("-8.0", unit="°C", last_updated=_PSD_T0),
        }
    )
    coord = Coord(
        hass,
        _FakeEntry(
            data=dict(
                {
                    "tibber_token": "x",
                    "weather_entity": "weather.home",
                    "indoor_temp_entity": "sensor.indoor",
                    "outdoor_temp_entity": "sensor.outdoor",
                },
                **(config or {}),
            )
        ),
    )
    coord._current_action = {"power": 2.0}
    coord._current_weather = lambda: (0.0, 0.0)
    real_now, real_utcnow = _psd_dt.now, _psd_dt.utcnow
    try:
        for i in range(cycles):
            t = _PSD_T0 + timedelta(minutes=30 * i)
            _psd_dt.now = lambda t=t: t
            _psd_dt.utcnow = lambda t=t: t
            hass.states.set(
                "sensor.indoor",
                FakeState(
                    f"{21.0 + 0.4 * np.sin(t.hour / 3.0):.2f}",
                    unit="°C",
                    last_updated=t,
                ),
            )
            hass.states.set(
                "sensor.outdoor", FakeState("-8.0", unit="°C", last_updated=t)
            )
            for entity, value in extra.items():
                # A real SelectEntity always publishes its options, and
                # pump_mode takes a word at face value only from an entity
                # that declares it among them.
                attrs = (
                    {"options": list(_PS_SELECT_OPTIONS)}
                    if entity.split(".")[0] in ("select", "input_select")
                    else None
                )
                hass.states.set(
                    entity,
                    FakeState(value, last_updated=t, attributes=attrs),
                )
            _asyncio.run(coord._update_current_state())
    finally:
        _psd_dt.now, _psd_dt.utcnow = real_now, real_utcnow
    return coord


# The control: with none of the four slots configured, 48 h still learns.
_psd_none = _psd_drive()
R.check(
    "with no heat-pump signals configured the learners run exactly as before",
    _psd_none._house_heat_loss_scale != 1.0
    and _psd_none._house_heat_loss_samples > 50,
    f"scale {_psd_none._house_heat_loss_scale:.4f}, "
    f"{_psd_none._house_heat_loss_samples} samples",
)
R.check(
    "and nothing reports a freeze",
    _psd_none._learner_freeze_reason is None
    and _psd_none._learning_frozen("indoor_temp_entity") is None,
)

# THE CLOUD GAP. In cloud mode the source integration answers 200/success,
# finds the device's property timestamps stale, sets is_online=False and
# RETURNS THE STALE DATA — no UpdateFailed on that branch. Its online sensor
# hardcodes available=True. So every entity stays available and Home
# Assistant bumps last_reported on each write: to `InputReader` (which
# prefers last_reported, deliberately) the pump looks perfectly fresh.
# Neither `unavailable` nor `stale` fires. Only the VALUE can see it.
_psd_offline = _psd_drive(
    states={"binary_sensor.pump_online": "off"},
    config={"heat_pump_online_entity": "binary_sensor.pump_online"},
)
R.check(
    "a pump reporting offline freezes the house heat-loss learner",
    _psd_offline._house_heat_loss_scale == 1.0
    and _psd_offline._house_heat_loss_samples == 0,
    f"scale walked to {_psd_offline._house_heat_loss_scale:.4f} over "
    f"{_psd_offline._house_heat_loss_samples} samples",
)
R.check(
    "and the reason names the pump, not a sensor",
    _psd_offline._learner_freeze_reason == pump_signals.FREEZE_OFFLINE,
    f"got {_psd_offline._learner_freeze_reason!r}",
)
R.check(
    "the freeze is plant-wide: it does not depend on which key is asked about",
    _psd_offline._learning_frozen("indoor_temp_entity")
    == pump_signals.FREEZE_OFFLINE
    and not _psd_offline._inputs_healthy(),
    "the pump being absent invalidates the interval, not one reading of it",
)

# The null control for the same wiring: online = on must change nothing.
_psd_online = _psd_drive(
    states={"binary_sensor.pump_online": "on"},
    config={"heat_pump_online_entity": "binary_sensor.pump_online"},
)
R.check(
    "an online pump learns exactly as an unconfigured one does",
    _psd_online._house_heat_loss_scale == _psd_none._house_heat_loss_scale
    and _psd_online._learner_freeze_reason is None,
    f"{_psd_online._house_heat_loss_scale:.6f} vs "
    f"{_psd_none._house_heat_loss_scale:.6f}",
)

# And the LAN mode counterpart: the pump's entities go unavailable there,
# which must NOT produce a second, different freeze — nor a false one.
_psd_lan = _psd_drive(
    states={"binary_sensor.pump_online": "unavailable"},
    config={"heat_pump_online_entity": "binary_sensor.pump_online"},
)
R.check(
    "an unavailable online entity does not freeze on its own",
    _psd_lan._learner_freeze_reason is None
    and _psd_lan._house_heat_loss_samples > 50,
    "in LAN mode the pump's own power and temperature entities go unavailable "
    "with it, and v5.1.3's per-key rule freezes on those; freezing again here "
    "would only add false positives on a momentary blip",
)

# A fault: degraded operation must not train the learners, and must say so.
_psd_fault = _psd_drive(
    states={"binary_sensor.pump_fault": "on"},
    config={"heat_pump_fault_entity": "binary_sensor.pump_fault"},
)
R.check(
    "a fault freezes the learners",
    _psd_fault._house_heat_loss_samples == 0
    and _psd_fault._learner_freeze_reason == pump_signals.FREEZE_FAULT,
    f"{_psd_fault._house_heat_loss_samples} samples, "
    f"reason {_psd_fault._learner_freeze_reason!r}",
)
_psd_view = _psd_fault._input_health_view()
R.check(
    "and the diagnostics say WHY the samples stopped",
    _psd_view["learners_frozen"]
    and _psd_view["learner_freeze_reason"] == pump_signals.FREEZE_FAULT,
    f"{_psd_view['learner_freeze_reason']!r} — silently starving the "
    "learners is the failure this whole view exists to prevent",
)
R.check(
    "the resolved signals are published too",
    _psd_fault._learning_view()["heat_pump_signals"]["fault"] is True,
)

# Cooling: power drawn while the house gets COLDER is not a noisy heating
# sample, it is a sign-inverted one.
_psd_cool = _psd_drive(
    states={"select.pump_mode": "Cooling"},
    config={"heat_pump_mode_entity": "select.pump_mode"},
)
R.check(
    "a cooling pump freezes the learners",
    _psd_cool._house_heat_loss_samples == 0
    and _psd_cool._learner_freeze_reason == pump_signals.FREEZE_COOLING,
    f"{_psd_cool._house_heat_loss_samples} samples, "
    f"reason {_psd_cool._learner_freeze_reason!r}",
)
R.check(
    "and it suppresses BOTH channels of the plan",
    _psd_cool._pump_signals.space_blocked
    and _psd_cool._pump_signals.dhw_blocked,
)

# A mode nobody recognises must not disable anything.
_psd_odd = _psd_drive(
    states={"select.pump_mode": "Silent Night Mode"},
    config={"heat_pump_mode_entity": "select.pump_mode"},
)
R.check(
    "an unrecognised mode plans and learns exactly as no mode entity does",
    _psd_odd._house_heat_loss_scale == _psd_none._house_heat_loss_scale
    and not _psd_odd._pump_signals.space_blocked
    and not _psd_odd._pump_signals.dhw_blocked,
    f"{_psd_odd._house_heat_loss_scale:.6f} vs "
    f"{_psd_none._house_heat_loss_scale:.6f}",
)

# A heating mode is the ordinary winter case and must be completely inert.
_psd_heat = _psd_drive(
    states={"select.pump_mode": "Heating + DHW"},
    config={"heat_pump_mode_entity": "select.pump_mode"},
)
R.check(
    "the pump's normal winter mode changes nothing at all",
    _psd_heat._house_heat_loss_scale == _psd_none._house_heat_loss_scale
    and _psd_heat._learner_freeze_reason is None
    and not _psd_heat._pump_signals.space_blocked
    and not _psd_heat._pump_signals.dhw_blocked,
)

# The last-good fallback, driven through the real coordinator: a mode entity
# that dies must not quietly re-enable a channel the pump cannot serve.
_psd_last = _psd_drive(
    states={"select.pump_mode": "DHW (Hot Water)"},
    config={"heat_pump_mode_entity": "select.pump_mode"},
    cycles=2,
)
_psd_last.hass.states.set(
    "select.pump_mode", FakeState("unavailable", last_updated=_PSD_T0)
)
import homeassistant.util.dt as _psd_dt2

_psd_real = _psd_dt2.now, _psd_dt2.utcnow
try:
    _psd_t = _PSD_T0 + timedelta(hours=1)
    _psd_dt2.now = lambda: _psd_t
    _psd_dt2.utcnow = lambda: _psd_t
    _asyncio.run(_psd_last._update_current_state())
finally:
    _psd_dt2.now, _psd_dt2.utcnow = _psd_real
R.check(
    "a mode entity that drops out holds the last mode the pump reported",
    _psd_last._pump_signals.space_blocked
    and _psd_last._pump_signals.mode_source
    == pump_signals.MODE_SOURCE_LAST_GOOD,
    f"{_psd_last._pump_signals.as_dict()} — the pump did not switch out of "
    f"hot-water mode because its sensor stopped reporting",
)


R.section("v5.3.0 — a blocked channel is suppressed, and visibly so")

import profiles as _mb_profiles
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer as _MbOpt,
    OptimizationConfig as _MbCfg,
)

_MB_START = datetime(2026, 1, 15, 0, 0)
_mb_params = ThermalParameters.from_config(_mb_profiles.house())
_mb_params.dhw_enabled = True
_mb_opt = _MbOpt(
    ThermalModel(_mb_params),
    _MbCfg(horizon_hours=12, time_step_minutes=15, min_temp=19.0, max_temp=23.0),
)
_mb_n = _mb_opt.config.n_steps
_mb_prices = np.asarray(_mb_profiles.prices("winter_typical", _MB_START))[:_mb_n]
_mb_t, _mb_wind, _mb_rain, _mb_solar = _mb_profiles.weather(
    "winter_cold", _MB_START
)
_mb_state = ThermalState(
    room_temperature=21.0, outdoor_temperature=-12.0, dhw_temperature=45.0
)


def _mb_run(**kw):
    return _mb_opt.optimize(
        _mb_state, _mb_prices, _mb_t[:_mb_n], _mb_wind[:_mb_n], _mb_rain[:_mb_n],
        _mb_solar[:_mb_n], _MB_START, **kw
    )


_mb_base = _mb_run()
R.check(
    "the control: a January plan really does heat and really does make hot water",
    sum(_mb_base.power_schedule) > 1.0 and sum(_mb_base.dhw_power_schedule) > 1.0,
    "a suppression test against a plan that was empty anyway proves nothing",
)
_mb_space = _mb_run(space_blocked=True)
R.check(
    "a mode that cannot heat rooms plans no space heating at all",
    max(_mb_space.power_schedule) == 0.0,
)
R.check(
    "and hot water is untouched — suppression is per channel",
    _mb_space.dhw_power_schedule == _mb_base.dhw_power_schedule,
)
R.check(
    "every empty space slot says WHY, instead of reading as 'idle'",
    set(_mb_space.space_reasons) == {"pump_mode"},
    f"{sorted(set(_mb_space.space_reasons))}",
)
R.check(
    "the comfort floor is left visibly unmet, not silently relaxed",
    _mb_space.predictive_info.get("power_cap_breach_c", 0.0) > 0.5,
    f"breach {_mb_space.predictive_info.get('power_cap_breach_c')} °C — the "
    f"user is owed the fact that the mode is costing them comfort",
)
_mb_dhw = _mb_run(dhw_blocked=True)
R.check(
    "a heating-only mode plans no hot water at all",
    max(_mb_dhw.dhw_power_schedule) == 0.0,
)
R.check(
    "and space heating is not reduced — the freed capacity stays available",
    max(_mb_dhw.power_schedule) > 0.0
    and sum(_mb_dhw.power_schedule) >= sum(_mb_base.power_schedule) - 1e-6,
    f"{sum(_mb_dhw.power_schedule):.4f} vs {sum(_mb_base.power_schedule):.4f}",
)
R.check(
    "the space plan may re-arrange, because the compressor is no longer shared",
    _mb_dhw.power_schedule != _mb_base.power_schedule,
    "an identical schedule would mean the hot-water blocks never competed "
    "for capacity in the first place, and this fixture would prove nothing",
)
R.check(
    "every empty hot-water slot says why",
    set(_mb_dhw.dhw_reasons) == {"pump_mode"},
)
R.check(
    "the result flags which channel the mode closed",
    _mb_space.mode_blocked_space
    and not _mb_space.mode_blocked_dhw
    and _mb_dhw.mode_blocked_dhw
    and not _mb_dhw.mode_blocked_space,
)
R.check(
    "and a blocked channel is NOT a manual pin — the two must not be confused",
    not _mb_space.manual_pins_active and not _mb_dhw.manual_pins_active,
    "a pin gets released for safety when a floor would breach; releasing "
    "this one would put back power the hardware refuses to draw",
)

# The safety-release loop is the specific hazard: a manual force-ON pin must
# not resurrect a channel the pump cannot serve.
_mb_pins = np.full(_mb_n, float("nan"))
_mb_pins[:8] = 1.0
_mb_pinned = _mb_run(space_pins=_mb_pins.copy(), space_blocked=True)
R.check(
    "a manual force-on pin cannot make the pump heat in a cooling mode",
    max(_mb_pinned.power_schedule) == 0.0,
    "a pin expresses a preference; the mode is the hardware",
)
_mb_dhw_pins = np.full(_mb_n, float("nan"))
_mb_dhw_pins[:8] = 1.0
_mb_dhw_pinned = _mb_run(dhw_pins=_mb_dhw_pins.copy(), dhw_blocked=True)
R.check(
    "and the same on the hot-water channel",
    max(_mb_dhw_pinned.dhw_power_schedule) == 0.0,
)

# The null control that protects every golden fixture.
_mb_null = _mb_run(space_blocked=False, dhw_blocked=False)
R.check(
    "both flags default off and off is byte-for-byte the previous plan",
    _mb_null.power_schedule == _mb_base.power_schedule
    and _mb_null.dhw_power_schedule == _mb_base.dhw_power_schedule
    and _mb_null.space_reasons == _mb_base.space_reasons
    and _mb_null.dhw_reasons == _mb_base.dhw_reasons,
)


# ===========================================================================
# v5.3.0 review — the coverage gaps a green suite was hiding
# ===========================================================================
R.section("v5.3.0 review — presence is not trust (the defrost derate)")

# The bug: DefrostDerate.factor branched on "does this bucket have a duty
# sample" BEFORE consulting trust, so n=1 (trust 1/12) beat counts=200 (trust
# 1.0). _settle_defrost folds a duty on the first settled interval after the
# flag is configured and that first duty is usually zero, so a bucket carrying
# a fully-earned 0.80 was reset to 1.0 one interval after the upgrade — the
# exact optimistic reset from_dict was rewritten to avoid, arriving by another
# door and on the very install this feature targets.

_RV_T, _RV_H = 2.0, 60.0


def _rv_mature(factor=0.80, counts=200):
    """A bucket whose INFERRED derate is fully trusted."""
    d = DefrostDerate()
    t, h = d._bucket(_RV_T, _RV_H)
    d.factors[t][h] = factor
    d.counts[t][h] = counts
    return d


_rv_inferred = _rv_mature()
R.check(
    "the premise: 200 inferred samples at 0.80 apply the whole 0.80",
    abs(_rv_inferred.factor(_RV_T, _RV_H) - 0.80) < 1e-9,
    f"factor {_rv_inferred.factor(_RV_T, _RV_H):.4f}",
)
_rv_one_zero = _rv_mature()
_rv_one_zero.observe_duty(_RV_T, _RV_H, 0.0)
R.check(
    "ONE zero-duty sample does not discard a fully-trusted inferred derate",
    abs(_rv_one_zero.factor(_RV_T, _RV_H) - 0.80) < 1e-9,
    f"factor {_rv_one_zero.factor(_RV_T, _RV_H):.4f} — before the fix this "
    f"returned exactly 1.0, i.e. no derate at all, on one sample worth 1/12 "
    f"of a trust ramp",
)
R.check(
    "and it reports the estimator the plan is actually using",
    not _rv_one_zero.measured(_RV_T, _RV_H)
    and _rv_one_zero.samples(_RV_T, _RV_H) == 200,
    f"measured={_rv_one_zero.measured(_RV_T, _RV_H)} "
    f"samples={_rv_one_zero.samples(_RV_T, _RV_H)} — saying 'measured, 1 "
    f"sample' while planning from 200 inferred ones is how the diagnostics "
    f"and the plan come to disagree",
)
_rv_summary = [
    b
    for b in _rv_one_zero.summary()
    if b["outdoor_range"][0] <= _RV_T < b["outdoor_range"][1]
][0]
R.check(
    "the summary agrees with the plan, and still shows what has been counted",
    _rv_summary["source"] == "inferred"
    and _rv_summary["samples"] == 200
    and _rv_summary["duty_samples"] == 1,
    f"{_rv_summary}",
)

# The ramp: the measurement takes over only once it has earned full trust,
# and never averages with the inference on the way.
_rv_ramp = []
for _n in (1, 4, 8, 11, 12, 40):
    d = _rv_mature()
    for _ in range(_n):
        d.observe_duty(_RV_T, _RV_H, 0.10)
    _rv_ramp.append((_n, d.factor(_RV_T, _RV_H), d.measured(_RV_T, _RV_H)))
R.check(
    "while the measurement is short of full trust the inference is a FLOOR",
    all(
        abs(f - 0.80) < 1e-9 and not m
        for n, f, m in _rv_ramp
        if n < DERATE_CONFIDENCE_SAMPLES
    ),
    f"{[(n, round(f, 4)) for n, f, _ in _rv_ramp]}",
)
R.check(
    "and at full trust the measurement takes over, as from_dict promises",
    all(
        m and abs(f - 0.80) > 1e-6
        for n, f, m in _rv_ramp
        if n >= DERATE_CONFIDENCE_SAMPLES
    ),
    f"{[(n, round(f, 4), m) for n, f, m in _rv_ramp]} — the carried value is "
    f"'a floor to stand on until something better is counted', not a prior "
    f"the measurement must argue with forever",
)
R.check(
    "the handover never averages the two estimators",
    all(
        abs(f - 0.80) < 1e-9 or abs(f - _rv_measured_only) < 1e-9
        for n, f, _ in _rv_ramp
        for _rv_measured_only in [
            (lambda dd: dd.factor(_RV_T, _RV_H))(
                (lambda: [
                    (lambda d2: [d2.observe_duty(_RV_T, _RV_H, 0.10)
                                 for _ in range(n)] and d2)(DefrostDerate())
                ][0])()
            )
        ]
    ),
    "every value is one estimator's or the other's; a blend of the two is "
    "a number that is neither",
)

# A measurement is still allowed to argue the derate DEEPER before it reaches
# full trust: the selection takes the more careful of the two, not always the
# inference. Six samples of a 30% duty is well short of the twelve that would
# hand the bucket over, and already deeper than a 0.95 inference.
_rv_deep = _rv_mature(factor=0.95, counts=200)
for _ in range(6):
    _rv_deep.observe_duty(_RV_T, _RV_H, 0.30)
_rv_deep_t, _rv_deep_h = _rv_deep._bucket(_RV_T, _RV_H)
R.check(
    "a measured duty deeper than the inference wins before full trust",
    _rv_deep.factor(_RV_T, _RV_H) < 0.95 - 1e-9
    and _rv_deep.measured(_RV_T, _RV_H)
    and _rv_deep.duty_counts[_rv_deep_t][_rv_deep_h] < DERATE_CONFIDENCE_SAMPLES,
    f"factor {_rv_deep.factor(_RV_T, _RV_H):.4f} against an inferred 0.95 on "
    f"{_rv_deep.duty_counts[_rv_deep_t][_rv_deep_h]} duty samples — selection "
    f"is by which is more careful, not by which is older; the floor must not "
    f"become a ceiling",
)
_rv_fresh = DefrostDerate()
_rv_fresh.observe_duty(_RV_T, _RV_H, 0.20)
R.check(
    "with no inference to stand on, one measurement still ramps from 1.0",
    abs(
        _rv_fresh.factor(_RV_T, _RV_H)
        - (1.0 + (derate_from_duty(0.20 * 0.10) - 1.0) / DERATE_CONFIDENCE_SAMPLES)
    )
    < 1e-6,
    f"factor {_rv_fresh.factor(_RV_T, _RV_H):.4f} — an empty bucket has no "
    f"floor, so the trust ramp is the only guard and must still apply",
)


R.section("v5.3.0 review — DERATE_MAX 1.05 -> 1.0, on a POPULATED bucket")

# The deliberate change no golden covers: defrost_buckets is [] in every
# fixture, so "no fixture moved" was never evidence the re-clamp is inert.
# Here it is exercised directly, on a store that actually carries a bucket
# above 1.0, through the model the planner reads the derate with.
_dm_store = {
    "factors": [[1.05, 1.04] for _ in range(6)],
    "counts": [[40, 40] for _ in range(6)],
}
_dm_loaded = DefrostDerate.from_dict(_dm_store)
R.check(
    "a v1 store's above-1 factors are re-clamped on load, not carried",
    _dm_loaded.factor(2.0, 80.0) == 1.0 and _dm_loaded.factor(2.0, 30.0) == 1.0,
    f"{_dm_loaded.factor(2.0, 80.0)} / {_dm_loaded.factor(2.0, 30.0)} — the "
    f"old bound would otherwise outlive the fix in every upgrading store",
)
R.check(
    "the re-clamp is a real change: the OLD bound would have kept 1.05",
    _dm_store["factors"][0][0] > DERATE_MAX and DERATE_MAX == 1.0,
    f"stored {_dm_store['factors'][0][0]} vs DERATE_MAX {DERATE_MAX}",
)
# And the change is visible in a PLAN, not just in the loader.
_dm_params = ThermalParameters.from_config(_mb_profiles.house())
_dm_model = ThermalModel(_dm_params)
_dm_cop_plain = _dm_model.compute_cop(2.0, humidity=80.0)
_dm_params.defrost_derate = DefrostDerate.from_dict(_dm_store)
_dm_cop_clamped = _dm_model.compute_cop(2.0, humidity=80.0)
_dm_optimistic = DefrostDerate.from_dict(_dm_store)
_dm_t, _dm_h = _dm_optimistic._bucket(2.0, 80.0)
_dm_optimistic.factors[_dm_t][_dm_h] = 1.05  # what the old bound stored
_dm_params.defrost_derate = _dm_optimistic
_dm_cop_old = _dm_model.compute_cop(2.0, humidity=80.0)
R.check(
    "a populated frost-band bucket really does reach the COP the plan prices",
    abs(_dm_cop_old - _dm_cop_plain) > 1e-6,
    f"clamped {_dm_cop_clamped:.4f}, unclamped {_dm_cop_old:.4f}, none "
    f"{_dm_cop_plain:.4f} — if these were equal this fixture would prove "
    f"nothing about the bound",
)
R.check(
    "and the new bound can only ever make the frost band MORE careful",
    _dm_cop_clamped <= _dm_cop_plain + 1e-9 and _dm_cop_clamped < _dm_cop_old,
    f"clamped {_dm_cop_clamped:.4f} <= plain {_dm_cop_plain:.4f} < old "
    f"{_dm_cop_old:.4f}: an upgrading install with a learned factor above 1.0 "
    f"loses exactly that optimism and nothing else",
)
_dm_params.defrost_derate = None


R.section("v5.3.0 review — an unreadable flag makes no confident claim")

# DefrostWindow.close carried _observed into the NEXT interval, so exactly one
# interval after the flag went unreadable was reported observed with duty 0 —
# which _settle_defrost then folded as a measured zero AND used to admit a
# frost-band COP sample with no defrost evidence behind it.
_dw_t0 = datetime(2026, 1, 10, 3, 0, tzinfo=UTC)
_dw_cycle = timedelta(minutes=5)


def _dw_run(flags_per_interval):
    """Drive a window through intervals of six cycles each."""
    w = DefrostWindow()
    now = _dw_t0
    out = []
    for flag in flags_per_interval:
        for _ in range(6):
            w.observe(now, flag)
            now += _dw_cycle
        out.append(w.close(now))
    return out


_dw = _dw_run([False, None, None])
R.check(
    "a readable flag reporting 'not defrosting' IS an observation",
    _dw[0].observed and _dw[0].duty == 0.0,
)
R.check(
    "the first interval after the flag dies is NOT reported as observed",
    not _dw[1].observed,
    "before the fix this one interval came back observed with duty 0 — 'a "
    "duty of 0 from an unreadable flag is a confident claim nobody can make', "
    "and per the derate above one folded zero was enough to flip the bucket",
)
R.check(
    "and neither is any interval after it",
    not _dw[2].observed,
)
_dw_back = _dw_run([None, False])
R.check(
    "legibility comes back with the next reading, within one cycle",
    (not _dw_back[0].observed) and _dw_back[1].observed,
    "resetting on close must not cost a healthy flag its next interval",
)
# The level still carries across the boundary; only legibility resets.
_dw_w = DefrostWindow()
_dw_now = _dw_t0
for _ in range(6):
    _dw_w.observe(_dw_now, True)
    _dw_now += _dw_cycle
_dw_w.close(_dw_now)
for _ in range(6):
    _dw_w.observe(_dw_now, True)
    _dw_now += _dw_cycle
_dw_half = _dw_w.close(_dw_now)
R.check(
    "a defrost spanning the boundary keeps its second half",
    _dw_half.observed and _dw_half.duty > 0.99,
    f"duty {_dw_half.duty:.4f} — the flag's LEVEL still carries over; only "
    f"its legibility is re-established",
)


R.section("v5.3.0 review — an unrecognised mode never latches suppression")

# pump_mode's contract is explicit: "Unknown means full capability, never
# suppress everything". read() broke it by routing unknown_value into the
# last_good branch, so a status sensor that said Heating once and idle
# thereafter held hot water blocked for the life of the install.
_um_cfg = {"heat_pump_mode_entity": "sensor.hp_status"}
_um_now = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)


#: What the reference integration's select actually publishes as `options`.
_UM_OPTIONS = [
    "Cooling",
    "Heating",
    "DHW (Hot Water)",
    "Cooling + DHW",
    "Heating + DHW",
]


def _um_read(
    state,
    last_good=None,
    entity="sensor.hp_status",
    age=2,
    options=None,
    last_good_age=None,
):
    cfg = {"heat_pump_mode_entity": entity}
    # A select declares its options; a bare status sensor declares nothing,
    # and that difference is what decides which vocabulary it gets.
    if options is None and entity.split(".")[0] in ("select", "input_select"):
        options = _UM_OPTIONS
    attrs = {"options": list(options)} if options else None
    hass = FakeHass(
        {entity: FakeState(state, last_updated=minutes_ago(age, _um_now),
                           attributes=attrs)}
    )
    return pump_signals.read(
        InputReader(hass, cfg, now=lambda: _um_now),
        last_good=last_good,
        last_good_age_minutes=last_good_age,
    )


_um_heat = pump_mode.capability("Heating")
_um_unknown = _um_read("idle", last_good=_um_heat)
R.check(
    "an unrecognised word resolves to full capability, not to the last mode",
    _um_unknown.mode is pump_mode.FULL_CAPABILITY
    and not _um_unknown.mode_observed,
    f"mode {_um_unknown.mode.label} from {_um_unknown.mode_source}",
)
R.check(
    "so it suppresses nothing, in either channel",
    not _um_unknown.space_blocked and not _um_unknown.dhw_blocked,
    "before the fix this returned the last good mode and latched its "
    "suppression permanently, with no recovery path at all",
)
R.check(
    "and it is visible as its own source, not folded into 'absent'",
    _um_unknown.mode_source == pump_signals.MODE_SOURCE_UNKNOWN
    and _um_unknown.mode_text == "idle",
    f"{_um_unknown.mode_source}/{_um_unknown.mode_text} — 'your mode entity "
    f"works, we do not know what it is telling us' is the one case a user "
    f"can act on",
)
# The recovery path, end to end.
_um_seq = []
_um_last = None
for _word in ("Heating + DHW", "Heating", "idle", "idle", "Heating + DHW"):
    _um_sig = _um_read(_word, last_good=_um_last, entity="select.hp_mode")
    if _um_sig.mode.known:
        _um_last = _um_sig.mode
    _um_seq.append((_word, _um_sig.dhw_blocked))
R.check(
    "a select recovers from an unrecognised state instead of latching",
    _um_seq == [
        ("Heating + DHW", False),
        ("Heating", True),
        ("idle", False),
        ("idle", False),
        ("Heating + DHW", False),
    ],
    f"{_um_seq}",
)
# What last_good is still for: an entity that stops being readable.
for _problem_state, _label in (("unavailable", "unavailable"),):
    _um_lg = _um_read(_problem_state, last_good=_um_heat, entity="select.hp_mode")
    R.check(
        f"an {_label} mode entity still falls back to the last good mode",
        _um_lg.mode is _um_heat
        and _um_lg.mode_source == pump_signals.MODE_SOURCE_LAST_GOOD
        and _um_lg.dhw_blocked,
        "the pump did not change mode because its sensor went quiet",
    )
_um_stale = _um_read("Heating", last_good=_um_heat, entity="select.hp_mode", age=600)
R.check(
    "and so does a stale one — staleness is unreadability, not disagreement",
    _um_stale.mode is _um_heat
    and _um_stale.mode_source == pump_signals.MODE_SOURCE_LAST_GOOD,
    f"{_um_stale.mode_source}",
)
_um_never = _um_read("idle")
R.check(
    "with nothing ever recognised, an unknown word is simply absent evidence",
    _um_never.mode is pump_mode.FULL_CAPABILITY and not _um_never.mode_observed,
)


R.section("v5.3.0 review — a status sensor is not a mode selector")

# The alias table mapped bare `heating`/`cooling`/`hot water` to single-duty
# MODES, and topology accepts `sensor` for this slot. A generic status sensor
# cycling heating/cooling/defrosting/idle is exactly what a user drops into a
# field labelled "Heat pump operating mode" — and there "heating" means "the
# compressor is making heat now", not "this unit cannot make hot water".
for _word in ("heating", "heat", "cooling", "cool", "hot water", "DHW"):
    R.check(
        f"a select still recognises {_word!r} — the vocabulary is unchanged there",
        pump_mode.is_known(_word) and pump_mode.resolve(_word) is not None,
        "a select's state is one of a list its integration declared, so its "
        "words can be taken at face value",
    )
    R.check(
        f"a plain sensor's {_word!r} is refused as a mode",
        not pump_mode.is_known(_word, strict=True)
        and pump_mode.capability(_word, strict=True) is pump_mode.FULL_CAPABILITY,
        "refusing means full capability, which is the documented safe "
        "direction; accepting means suppressing a channel on a misreading",
    )
for _word in ("Heating + DHW", "HEATDHW", "Cooling + DHW", "COOLDHW"):
    R.check(
        f"the multi-duty spelling {_word!r} survives strict mode",
        pump_mode.is_known(_word, strict=True),
        "no status sensor reports 'Heating + DHW' as a momentary activity",
    )
# What chooses the vocabulary is whether the ENTITY declares its own state
# among its options — not its domain. That is the property the trust rests
# on, it is visible at runtime, and it fails safe for any entity type nobody
# has thought of yet.
_um_declared = FakeState("Heating", attributes={"options": _UM_OPTIONS})
_um_undeclared = FakeState("Heating")
_um_off_list = FakeState("Turbo Eco", attributes={"options": _UM_OPTIONS})
R.check(
    "an entity that declares this state among its options is taken at face value",
    pump_mode.validator_for(_um_declared) is pump_mode.is_known
    and pump_mode.declares_current_option(_um_declared),
)
R.check(
    "one that declares nothing gets the careful vocabulary",
    pump_mode.validator_for(_um_undeclared) is not pump_mode.is_known
    and pump_mode.validator_for(None) is not pump_mode.is_known,
)
R.check(
    "and so does one reporting a word it never declared",
    pump_mode.validator_for(_um_off_list) is not pump_mode.is_known,
    "a select whose state is off its own list is not a select doing its job",
)
R.check(
    "a user-built input_select listing the modes is a declaration too",
    pump_mode.declares_current_option(
        FakeState("Cooling", attributes={"options": _UM_OPTIONS})
    ),
    "somebody who builds a helper listing the pump's modes and sets it to "
    "one is telling us the mode; that is the input this slot wants",
)
_sm_sensor = _um_read("heating", entity="sensor.hp_status")
R.check(
    "so a status sensor reading 'heating' does NOT block hot water",
    not _sm_sensor.dhw_blocked and not _sm_sensor.space_blocked,
    f"dhw_blocked={_sm_sensor.dhw_blocked} — with the latch above this was "
    f"a permanent hot-water suppression on a word that meant something else",
)
_sm_select = _um_read("Heating", entity="select.hp_mode")
R.check(
    "while a real select reading 'Heating' still does",
    _sm_select.dhw_blocked and not _sm_select.space_blocked,
    "the feature must keep working for the hardware it was written for",
)
_sm_sensor_multi = _um_read("Heating + DHW", entity="sensor.hp_mode")
R.check(
    "and a sensor carrying a real mode label is still read as one",
    _sm_sensor_multi.mode.key == pump_mode.MODE_HEAT_DHW,
    "a template sensor mirroring the select must not be collateral damage",
)
_sm_mirror = _um_read(
    "Cooling", entity="sensor.hp_mode_mirror", options=_UM_OPTIONS
)
R.check(
    "a template sensor that also mirrors the OPTIONS gets the full vocabulary",
    _sm_mirror.mode.key == pump_mode.MODE_COOL and _sm_mirror.space_blocked,
    f"{_sm_mirror.mode.label} — the single-word spellings are reachable from "
    f"any domain that declares them, so mirroring a select properly is not "
    f"collateral damage either",
)


R.section("v5.3.0 review — the narrative explains a blocked channel")

from heatpump_optimizer.optimizer import REASON_PUMP_MODE  # noqa: E402

R.check(
    "pump_mode has a sentence in BOTH languages",
    all(
        REASON_PUMP_MODE in narrative_mod.TEMPLATES[lang]
        for lang in narrative_mod.TEMPLATES  # en and sv alike
    ),
    "the en/sv parity test passes when a key is missing from both, so parity "
    "alone could never catch this",
)
_nb_items = narrative_mod.build(
    {"powers": [0.0] * 8, "prices": [1.0] * 8, "reasons": [REASON_PUMP_MODE] * 8},
    {"powers": [], "prices": [], "reasons": []},
    0.5,
)
R.check(
    "a blocked channel survives the zero-energy filter, as idle does",
    [i["reason"] for i in _nb_items] == [REASON_PUMP_MODE]
    and _nb_items[0]["hours"] == 4.0,
    f"{_nb_items} — the blocked slots were relabelled away from 'idle', so "
    f"filtering them out leaves silence where the explanation belongs",
)
for _lang in narrative_mod.TEMPLATES:  # every shipped language renders it
    _nb_lines = narrative_mod.render(_nb_items, _lang)
    R.check(
        f"and it renders a real sentence in {_lang}",
        len(_nb_lines) == 1 and "4.0" in _nb_lines[0] and "{" not in _nb_lines[0],
        f"{_nb_lines}",
    )
R.check(
    "an ordinary zero-energy reason is still filtered out",
    narrative_mod.build(
        {"powers": [0.0] * 4, "prices": [1.0] * 4, "reasons": ["cheap_price"] * 4},
        {"powers": [], "prices": [], "reasons": []},
        0.5,
    )
    == [],
    "only reasons whose whole meaning is 'no energy' are exempt",
)


R.section("v5.3.0 review — a blocked channel is published, not just recorded")

R.check(
    "a space block reaches predictive_info, where the coordinator can see it",
    _mb_space.predictive_info.get("mode_blocked_space") is True
    and "mode_blocked_dhw" not in _mb_space.predictive_info,
)
R.check(
    "a hot-water block gets the numeric trace the space channel already had",
    _mb_dhw.predictive_info.get("mode_blocked_dhw") is True
    and _mb_dhw.predictive_info.get("dhw_floor_breach_c", 0.0) > 0.0,
    f"breach {_mb_dhw.predictive_info.get('dhw_floor_breach_c')} °C — "
    f"power_cap_breach_c is space-only, so without this a blocked tank left "
    f"no number anywhere saying how far short it fell",
)
R.check(
    "and an unblocked plan carries none of the new keys at all",
    not any(
        k in _mb_null.predictive_info
        for k in ("mode_blocked_space", "mode_blocked_dhw", "dhw_floor_breach_c")
    ),
    f"{sorted(_mb_null.predictive_info)} — every golden fixture plans with no "
    f"mode entity, so this is what keeps them still",
)



R.section("v5.3.0 review — the experiment obeys the mode gate too")

from pathlib import Path as _Path  # noqa: E402
from heatpump_optimizer import sysid as _SysIdModule  # noqa: E402

_PKG_DIR = _Path("custom_components/heatpump_optimizer")

# _run_system_identification writes _current_action["power"] AFTER the solve,
# so it is the one route that bypasses the bounds the mode block is enforced
# at — and the worst one to bypass them by, because
# _adopt_system_identification seeds the persisted thermal parameters from
# whatever the experiment measured.


class _SysIdHost:
    _run_system_identification = Coord._run_system_identification

    def __init__(self, signals) -> None:
        self._pump_signals = signals
        self._sysid = _SysIdModule.SystemIdentification(
            _SysIdModule.SysIdConfig(enabled=True)
        )
        self._sysid.arm(datetime(2026, 1, 5, 2, 0, tzinfo=UTC))
        self._current_action = {"power": 0.0, "heat_pump_on": False}
        self._current_state = ThermalState(
            room_temperature=21.0, outdoor_temperature=3.0
        )
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._house_heat_loss_samples = 0

    def _get_current_price(self):
        return 0.2


_COOLING = pump_signals.PumpSignals(
    mode=pump_mode.capability("Cooling"),
    mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
    freeze_reason=pump_signals.FREEZE_COOLING,
)
_DHW_ONLY_SIG = pump_signals.PumpSignals(
    mode=pump_mode.capability("DHW"),
    mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
)
_OFFLINE = pump_signals.PumpSignals(
    online=False, freeze_reason=pump_signals.FREEZE_OFFLINE
)

_si_free = _SysIdHost(PumpSignals())
_si_free._run_system_identification(np.full(48, 0.2))
R.check(
    "the control: with no mode entity the experiment is untouched",
    _si_free._sysid.active,
    f"phase {_si_free._sysid.phase}",
)
for _sig, _name in (
    (_COOLING, "a cooling mode"),
    (_DHW_ONLY_SIG, "a hot-water-only mode"),
    (_OFFLINE, "a pump that is off the network"),
):
    _si = _SysIdHost(_sig)
    _si._run_system_identification(np.full(48, 0.2))
    R.check(
        f"{_name} aborts an armed experiment instead of commanding heat",
        not _si._sysid.active
        and _si._sysid.phase == _SysIdModule.PHASE_ABORTED
        and _si._current_action["power"] == 0.0,
        f"phase {_si._sysid.phase} power {_si._current_action['power']} — a "
        f"step response measured through this is not a noisy measurement of "
        f"the house, and _adopt_system_identification persists what it fits",
    )
_si_reason = _SysIdHost(_COOLING)
_si_reason._run_system_identification(np.full(48, 0.2))
R.check(
    "the aborted result carries the cause",
    _si_reason._sysid.result.reason
    and not _si_reason._sysid.result.completed,
    f"{_si_reason._sysid.result.reason!r}",
)


R.section("v5.3.0 review — a mode-blocked tank says so, loudly")

# An indefinitely blocked DHW channel silently defers the anti-legionella
# cycle: forced_off is all-ones, the schedule is hard-zeroed, the legionella
# slot never runs, and dhw_legionella_due_in_hours merely goes negative in an
# attribute. A pump left in heating for a fortnight produced no warning at all.

_LG_ISSUE = "dhw_legionella_mode_blocked"


def _lg_coord(*, days_since=20.0, enabled=True, dhw=True):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(_LC_DATA)))
    c._thermal_params.dhw_enabled = dhw
    c._thermal_params.dhw_legionella_enabled = enabled
    c._thermal_params.dhw_legionella_interval_days = 7.0
    c._dhw_last_legionella = dt_util.now() - timedelta(days=days_since)
    return c


def _lg_issues(c):
    return [i for i in getattr(c.hass, "issues", []) if i[1] == _LG_ISSUE]


_lg_blocked = _lg_coord()
R.check(
    "the premise: the cycle really is overdue",
    _lg_blocked._dhw_legionella_due_in_hours() < 0.0,
    f"due in {_lg_blocked._dhw_legionella_due_in_hours()} h",
)
_lg_blocked._check_legionella_mode_block(False)
R.check(
    "an overdue cycle with hot water available raises nothing here",
    not _lg_issues(_lg_blocked),
    "that case is the disinfection timer's own business, not the mode's",
)
_lg_blocked._check_legionella_mode_block(True)
_lg_raised = _lg_issues(_lg_blocked)
R.check(
    "an overdue cycle the pump's mode is blocking raises a repair issue",
    len(_lg_raised) == 1
    and _lg_raised[0][2].get("translation_key") == _LG_ISSUE
    and set(_lg_raised[0][2].get("translation_placeholders", {}))
    == {"overdue_days", "interval_days"},
    f"{_lg_raised}",
)
R.check(
    "and it says how long the tank has gone undisinfected",
    int(_lg_raised[0][2]["translation_placeholders"]["overdue_days"]) >= 13,
    f"{_lg_raised[0][2]['translation_placeholders']} — 20 days since the last "
    f"cycle on a 7-day interval is 13 days overdue",
)
_lg_blocked._check_legionella_mode_block(True)
R.check(
    "it is not re-raised every cycle while nothing has changed",
    len(_lg_issues(_lg_blocked)) == 1,
)
_lg_blocked._check_legionella_mode_block(False)
R.check(
    "a mode that can make hot water again clears it",
    not _lg_issues(_lg_blocked),
    "the notice describes a live condition, not a historical fact",
)
_lg_off = _lg_coord(enabled=False)
_lg_off._check_legionella_mode_block(True)
R.check(
    "a user who turned disinfection off is not nagged about it",
    not _lg_issues(_lg_off),
)
_lg_no_dhw = _lg_coord(dhw=False)
_lg_no_dhw._check_legionella_mode_block(True)
R.check(
    "nor is an install with no hot-water tank at all",
    not _lg_issues(_lg_no_dhw),
)
_lg_recent = _lg_coord(days_since=1.0)
_lg_recent._check_legionella_mode_block(True)
R.check(
    "and a block that has not yet outlived the deadline is not an alarm",
    not _lg_issues(_lg_recent),
    f"due in {_lg_recent._dhw_legionella_due_in_hours()} h — a mode block is "
    f"only news once the cycle it is holding up has actually come due",
)
_lg_unknown = _lg_coord()
_lg_unknown._dhw_last_legionella = None
_lg_unknown._check_legionella_mode_block(True)
R.check(
    "an unknown history is not evidence of an overdue cycle",
    not _lg_issues(_lg_unknown),
)
for _lang_file in ("strings.json", "translations/en.json", "translations/sv.json"):
    _lg_doc = _json.loads(
        (_PKG_DIR / _lang_file).read_text(encoding="utf-8")
    )
    R.check(
        f"the notice has a title and a description in {_lang_file}",
        _LG_ISSUE in _lg_doc.get("issues", {})
        and _lg_doc["issues"][_LG_ISSUE].get("title")
        and "{overdue_days}" in _lg_doc["issues"][_LG_ISSUE]["description"]
        and "{interval_days}" in _lg_doc["issues"][_LG_ISSUE]["description"],
    )



R.section("v5.3.0 review 2 — the health watch judges like against like")

# The BLOCKER: _cop_reference_curve made observed_cop curve-dependent, but
# _observe_cop_health bucketed its baseline by outdoor temperature alone. A
# hot-water interval is measured against the DHW curve, which the model
# prices 8-20 % below the space curve at the same outdoor temperature, so a
# perfectly healthy pump produced a standing "shortfall" of exactly the gap
# between the curves. The CUSUM is one-sided: it accumulates that and tells
# the owner his compressor has degraded, persistently, and stops absorbing
# samples while tripped so it never self-corrects.

_hw_params = ThermalParameters()
_hw_model = ThermalModel(_hw_params)
_HW_OUT = 4.0
_hw_space = _hw_model.compute_cop(_HW_OUT)
_hw_dhw = _hw_model.compute_cop_dhw(_HW_OUT, 55.0)
R.check(
    "the premise: the two curves really are far apart at one outdoor temp",
    (_hw_space - _hw_dhw) / _hw_space > 0.08,
    f"space {_hw_space:.3f} vs dhw {_hw_dhw:.3f} — "
    f"{100 * (_hw_space - _hw_dhw) / _hw_space:.1f}% apart, and a fixture "
    f"that did not separate them would prove nothing",
)


def _hw_coord():
    c = _t2_coord()
    c._current_state.outdoor_temperature = _HW_OUT
    return c


def _hw_settle(c, n=60):
    """A pump tracking its plan perfectly on both curves."""
    for _ in range(n):
        c._observe_cop_health(_hw_space, False)
        c._observe_cop_health(_hw_dhw, True)


def _hw_trip_after(c, space_factor=1.0, dhw_factor=1.0, limit=200):
    for i in range(1, limit + 1):
        c._observe_cop_health(_hw_space * space_factor, False)
        c._observe_cop_health(_hw_dhw * dhw_factor, True)
        if c._cop_health_cusum.tripped:
            return i
    return None


# The plan shape that produced the false alarm: shoulder.json runs 38
# space-only steps against 30 DHW-only ones in the same outdoor bucket.
_hw_mixed = _hw_coord()
for _ in range(60):
    _hw_mixed._observe_cop_health(_hw_space, False)
_hw_alarm_at = None
for _i in range(1, 200):
    _hw_mixed._observe_cop_health(
        _hw_dhw if _i % 2 else _hw_space, bool(_i % 2)
    )
    if _hw_mixed._cop_health_cusum.tripped:
        _hw_alarm_at = _i
        break
R.check(
    "a healthy pump alternating space and hot water raises NO fault report",
    _hw_alarm_at is None
    and not [
        i for i in getattr(_hw_mixed.hass, "issues", []) if i[1] == "cop_degradation"
    ],
    f"tripped at interval {_hw_alarm_at} — before the fix the 50/50 shape of "
    f"the committed shoulder fixture raised cop_degradation inside a day, "
    f"sending an owner to a service engineer for nothing",
)
R.check(
    "and the two curves keep separate baselines rather than one blended one",
    (_hw_mixed._cop_baseline.get((1, False)) or [0])[0]
    > (_hw_mixed._cop_baseline.get((1, True)) or [0])[0],
    f"space {_hw_mixed._cop_baseline.get((1, False))} vs "
    f"dhw {_hw_mixed._cop_baseline.get((1, True))}",
)

# The watch must still do its job — on either channel independently.
_hw_space_bad = _hw_coord()
_hw_settle(_hw_space_bad)
_hw_n_space = _hw_trip_after(_hw_space_bad, space_factor=0.85)
_hw_dhw_bad = _hw_coord()
_hw_settle(_hw_dhw_bad)
_hw_n_dhw = _hw_trip_after(_hw_dhw_bad, dhw_factor=0.85)
R.check(
    "a real 15% loss on the space channel is still caught, and quickly",
    _hw_n_space is not None and _hw_n_space <= 15,
    f"caught after {_hw_n_space} intervals",
)
R.check(
    "and so is one on the hot-water channel, which had no watch before",
    _hw_n_dhw is not None and _hw_n_dhw <= 15,
    f"caught after {_hw_n_dhw} intervals — separating the baselines must "
    f"sharpen the watch, not switch half of it off",
)
_hw_healthy = _hw_coord()
_hw_settle(_hw_healthy)
R.check(
    "a pump that is simply healthy never trips on either",
    _hw_trip_after(_hw_healthy) is None,
)

# The wiring between the two halves: the learner must TELL the watch which
# curve it used. Separate baselines are worthless if every sample arrives
# labelled "space".
_hw_gate_space = _CopGate(outdoor=8.0)
_hw_gate_space._learn_measured_cop()
_hw_gate_dhw = _CopGate(outdoor=8.0, signals=_DHW_ONLY, action=_dhw_action)
_hw_gate_dhw._current_state.dhw_temperature = 55.0
_hw_gate_dhw._learn_measured_cop()
R.check(
    "the COP learner labels each sample with the curve it was judged against",
    [c[1] for c in _hw_gate_space.cop_health_calls] == [False]
    and [c[1] for c in _hw_gate_dhw.cop_health_calls] == [True],
    f"space {_hw_gate_space.cop_health_calls} vs dhw "
    f"{_hw_gate_dhw.cop_health_calls} — separate baselines are worthless if "
    f"every sample arrives labelled the same way",
)

# Persistence: additive, and an existing store keeps every bucket it had.
_hw_old = _t2_coord()
_hw_old._cop_baseline = {}
_hw_v1_payload = {"cop_baseline": {"1": [3.2, 40], "2": [3.5, 25]}}


async def _hw_load_v1(_p=_hw_v1_payload):
    return _p


_hw_old._thermal_learning_store.async_load = _hw_load_v1
_asyncio.run(_hw_old._async_load_thermal_learning())
R.check(
    "a pre-v5.3.0 store's buckets load as SPACE baselines, not discarded",
    _hw_old._cop_baseline.get((1, False)) == [3.2, 40]
    and _hw_old._cop_baseline.get((2, False)) == [3.5, 25],
    f"{_hw_old._cop_baseline} — the watch's memory is weeks long; throwing "
    f"it away on upgrade would blind it for a month",
)
_hw_old._current_state.outdoor_temperature = _HW_OUT
_hw_old._observe_cop_health(_hw_dhw, True)
_hw_written = _hw_old._thermal_learning_payload()["cop_baseline"]
R.check(
    "and it writes back under the SAME keys, with the DHW curve alongside",
    _hw_written.get("1") == [3.2, 40]
    and _hw_written.get("2") == [3.5, 25]
    and "1:dhw" in _hw_written,
    f"{_hw_written} — additive, so a downgrade still reads what it wrote",
)



R.section("v5.3.0 review 2 — legibility belongs to the interval")

from heatpump_optimizer.const import (  # noqa: E402
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    MODE_LAST_GOOD_MAX_AGE_MINUTES,
)

# The previous fix stopped _observed carrying ACROSS a boundary but not
# WITHIN an interval: one legible read marked the whole of it observed. The
# earlier fixture missed it because it applied one flag to all six cycles of
# an interval, which is the one thing the real system never does — the state
# listener exists precisely because the flag changes mid-interval.
_iv_t0 = datetime(2026, 1, 10, 3, 0, tzinfo=UTC)
_iv_cycle = timedelta(minutes=5)


def _iv(flags):
    """Drive ONE interval, one flag per cycle. Returns the settled reading."""
    w, now = DefrostWindow(), _iv_t0
    for f in flags:
        w.observe(now, f)
        now += _iv_cycle
    return w.close(now)


_iv_legible_then_dark = _iv([False, None, None, None, None, None])
R.check(
    "one legible read does not vouch for the twenty-five minutes after it",
    not _iv_legible_then_dark.observed,
    f"observed={_iv_legible_then_dark.observed} duty="
    f"{_iv_legible_then_dark.duty:.3f} — a defrost anywhere in that dark "
    f"stretch is invisible, and this reported a confident zero over it",
)
_iv_dark_then_legible = _iv([None, None, None, None, None, False])
R.check(
    "and neither does one at the END of a dark interval",
    not _iv_dark_then_legible.observed,
    "the mirror of the same claim: the duty's denominator is the whole "
    "interval either way",
)
_iv_clean = _iv([False] * 6)
R.check(
    "an interval legible throughout is still observed",
    _iv_clean.observed and _iv_clean.duty == 0.0,
    "the guard must not cost a healthy flag its evidence",
)
_iv_defrost = _iv([False, False, True, True, False, False])
R.check(
    "and a real mid-interval defrost is still measured, at its real duty",
    _iv_defrost.observed
    and abs(_iv_defrost.duty - 1.0 / 3.0) < 0.01
    and _iv_defrost.events == 1,
    f"duty {_iv_defrost.duty:.3f} events {_iv_defrost.events} — two of six "
    f"cycles defrosting is a third of the interval",
)
_iv_all = _iv([True] * 6)
R.check(
    "a defrost spanning the whole interval reads as the whole interval",
    _iv_all.observed and _iv_all.duty > 0.99,
)
# The boundary case the previous round fixed must still hold.
_iv_w = DefrostWindow()
_iv_now = _iv_t0
for _ in range(6):
    _iv_w.observe(_iv_now, True)
    _iv_now += _iv_cycle
_iv_w.close(_iv_now)
for _ in range(6):
    _iv_w.observe(_iv_now, True)
    _iv_now += _iv_cycle
_iv_second_half = _iv_w.close(_iv_now)
R.check(
    "a defrost spanning an interval boundary still keeps its second half",
    _iv_second_half.observed and _iv_second_half.duty > 0.99,
    "the flag's LEVEL carries over; only its legibility is re-established",
)


R.section("v5.3.0 review 2 — a mode nobody can read stops acting")

# pump_signals' own rule: "a cooling mode read six hours ago must not still be
# freezing the learners". The implementation did the opposite -- stale routed
# to last_good, which restored identical capability with mode_observed still
# true, and nothing ever cleared it.
_ex_cool = pump_mode.capability("Cooling")
_ex_rows = []
for _label, _state, _age, _lg in (
    ("fresh", "Cooling", 2, 2),
    ("61 min old", "Cooling", 61, 61),
    ("6 hours old", "Cooling", 360, 360),
    ("3 days old", "Cooling", 4320, 4320),
    ("unavailable 10 min", "unavailable", 2, 10),
    ("unavailable 6 hours", "unavailable", 2, 360),
):
    _ex = _um_read(
        _state, last_good=_ex_cool, entity="select.hp_mode",
        age=_age, last_good_age=_lg,
    )
    _ex_rows.append((_label, _ex.space_blocked, _ex.mode_source))
R.check(
    "a mode read minutes ago still acts, one read hours ago does not",
    [r[1] for r in _ex_rows] == [True, True, False, False, True, False],
    f"{_ex_rows} — an unbounded fallback made the 60 minute horizon on this "
    f"entity do nothing at all",
)
R.check(
    "and the expiry is visible as its own source, not silence",
    [r[2] for r in _ex_rows if not r[1]]
    == [pump_signals.MODE_SOURCE_EXPIRED] * 3,
    f"{_ex_rows}",
)
R.check(
    "an expired mode suppresses nothing and freezes nothing",
    (
        lambda s: not s.space_blocked
        and not s.dhw_blocked
        and s.freeze_reason is None
        and not s.mode_observed
    )(
        _um_read(
            "Cooling", last_good=_ex_cool, entity="select.hp_mode",
            age=4320, last_good_age=4320,
        )
    ),
    "full capability is the documented safe direction; a dead mode entity "
    "must not leave a house cold indefinitely",
)
R.check(
    "the bound is longer than the reading's own horizon and shorter than six hours",
    60.0 < MODE_LAST_GOOD_MAX_AGE_MINUTES < 360.0,
    f"{MODE_LAST_GOOD_MAX_AGE_MINUTES} min",
)
for _lang_file in ("strings.json", "translations/en.json", "translations/sv.json"):
    _ex_doc = _json.loads((_PKG_DIR / _lang_file).read_text(encoding="utf-8"))
    R.check(
        f"the mode-unreadable notice is translated in {_lang_file}",
        "pump_mode_unreadable" in _ex_doc.get("issues", {})
        and "{hours}" in _ex_doc["issues"]["pump_mode_unreadable"]["description"],
    )

# D3-05: everything checked above is the *pure* signal-reading side of an
# expired mode (``pump_signals``/``pump_mode``). The coordinator-level
# trigger that actually surfaces this to the user —
# ``_check_pump_mode_expired``, which calls ``ir.async_create_issue``/
# ``async_delete_issue`` for "pump_mode_unreadable" — has no test anywhere
# in the suite; making the whole method an unconditional no-op passes every
# closure script unnoticed. This drives the real coordinator end-to-end:
# force the mode source to expired, call the method, and assert the repair
# issue was actually raised; then force it back and assert it is cleared.
_pme_coord = _t2_coord()
R.check(
    "a fresh coordinator starts with no pump-mode-unreadable issue and no notice latched",
    not _pme_coord._pump_mode_expired_notice
    and not [
        i
        for i in getattr(_pme_coord.hass, "issues", [])
        if i[1] == "pump_mode_unreadable"
    ],
)
_pme_coord._pump_signals = dataclasses.replace(
    _pme_coord._pump_signals, mode_source=pump_signals.MODE_SOURCE_EXPIRED
)
_pme_coord._check_pump_mode_expired()
_pme_raised = [
    i
    for i in getattr(_pme_coord.hass, "issues", [])
    if i[1] == "pump_mode_unreadable"
]
R.check(
    "an expired pump-mode source actually raises the repair issue end-to-end",
    len(_pme_raised) == 1
    and _pme_raised[0][2].get("translation_key") == "pump_mode_unreadable"
    and _pme_coord._pump_mode_expired_notice is True,
    f"got issues={_pme_raised}; a no-op'd _check_pump_mode_expired would "
    "leave the user with no warning that the mode entity died",
)
_pme_coord._pump_signals = dataclasses.replace(
    _pme_coord._pump_signals, mode_source=pump_signals.MODE_SOURCE_LIVE
)
_pme_coord._check_pump_mode_expired()
R.check(
    "recovery of the mode source clears the repair issue again",
    not [
        i
        for i in getattr(_pme_coord.hass, "issues", [])
        if i[1] == "pump_mode_unreadable"
    ]
    and _pme_coord._pump_mode_expired_notice is False,
)


R.section("v5.3.0 review 2 — a status sensor is not a flag either")

# BOOL_TRUE/BOOL_FALSE carry heating, running, idle and standby, and all three
# flag slots accept a plain `sensor`. Read as flags those words are actively
# wrong in every slot.
_fl_now = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)


def _fl_read(slot, entity, state):
    hass = FakeHass(
        {entity: FakeState(state, last_updated=minutes_ago(2, _fl_now))}
    )
    return pump_signals.read(
        InputReader(hass, {slot: entity}, now=lambda: _fl_now)
    )


for _slot, _word, _what in (
    ("heat_pump_online_entity", "idle", "an idle pump is not an offline one"),
    ("heat_pump_fault_entity", "heating", "a heating pump is not a faulted one"),
    ("heat_pump_fault_entity", "running", "nor is a running one"),
    ("heat_pump_defrost_entity", "heating", "heating is not defrosting"),
):
    _fl = _fl_read(_slot, "sensor.hp_status", _word)
    R.check(
        f"a status sensor in the {_slot.split('_')[2]} slot reading {_word!r} "
        f"is no evidence: {_what}",
        _fl.online is None and _fl.fault is None and _fl.defrosting is None
        and _fl.freeze_reason is None,
        f"online={_fl.online} fault={_fl.fault} defrost={_fl.defrosting} "
        f"freeze={_fl.freeze_reason} — 'idle' in the online slot froze every "
        f"learner on a pump that was merely not running",
    )
for _slot, _word, _want in (
    ("heat_pump_online_entity", "off", False),
    ("heat_pump_online_entity", "on", True),
    ("heat_pump_fault_entity", "on", True),
    ("heat_pump_defrost_entity", "1", True),
    ("heat_pump_defrost_entity", "0", False),
):
    _fl = _fl_read(_slot, "sensor.hp_flag", _word)
    _got = {
        "heat_pump_online_entity": _fl.online,
        "heat_pump_fault_entity": _fl.fault,
        "heat_pump_defrost_entity": _fl.defrosting,
    }[_slot]
    R.check(
        f"but an unambiguous {_word!r} from a sensor still reads as a flag",
        _got is _want,
        f"got {_got} — a template sensor carrying a raw Tuya DP must keep "
        f"working; only the activity words are refused",
    )
for _word, _want in (("idle", False), ("heating", True), ("running", True)):
    _fl = _fl_read("heat_pump_online_entity", "binary_sensor.hp_online", _word)
    R.check(
        f"and a real binary_sensor is unaffected by the guard ({_word!r})",
        _fl.online is _want,
        "its state is on/off by construction, so it cannot make the mistake",
    )


R.section("v5.3.0 review 2 — the block never actuates")

# _apply_action calls switch.turn_off whenever the plan is empty. A mode that
# blocks both channels makes every step empty, so a cooling pump was switched
# off every cycle -- defeating the cooling its owner selected, from a feature
# documented as read-only.
_ac_entity = "switch.hp_supply"


def _ac_calls(signals, heat_pump_on):
    c = _t2_coord()
    c._config[CONF_HEAT_PUMP_SWITCH_ENTITY] = _ac_entity
    c._pump_signals = signals
    c._current_action = {"heat_pump_on": heat_pump_on, "power": 0.0}
    c._mode = "comfort"
    _asyncio.run(c._apply_action())
    return [
        call
        for call in c.hass.services.calls
        if call[0] == "switch" and call[2].get("entity_id") == _ac_entity
    ]


_AC_FREE = pump_signals.PumpSignals()
_AC_COOL = pump_signals.PumpSignals(
    mode=pump_mode.capability("Cooling"),
    mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
    freeze_reason=pump_signals.FREEZE_COOLING,
)
_AC_DHW_ONLY = pump_signals.PumpSignals(
    mode=pump_mode.capability("DHW"),
    mode_observed=True,
    mode_source=pump_signals.MODE_SOURCE_LIVE,
)
R.check(
    "the control: with no mode entity an empty plan still switches off",
    [c[1] for c in _ac_calls(_AC_FREE, False)] == ["turn_off"],
    "every install without a mode entity must behave exactly as before",
)
R.check(
    "and a plan that wants the pump still switches on",
    [c[1] for c in _ac_calls(_AC_FREE, True)] == ["turn_on"],
)
R.check(
    "a cooling mode does NOT switch the pump off",
    _ac_calls(_AC_COOL, False) == [],
    "both channels are hard-zeroed by the block, so 'the plan is empty' is "
    "this integration's own doing — cutting the supply would defeat the "
    "cooling the owner selected, from a feature documented as read-only",
)
R.check(
    "nor does a mode that blocks only the other channel",
    _ac_calls(_AC_DHW_ONLY, False) == [],
)
R.check(
    "but a block never stops the pump being switched ON",
    [c[1] for c in _ac_calls(_AC_DHW_ONLY, True)] == ["turn_on"],
    "that is the plan asking for something the unblocked channel can "
    "deliver, which the block has no claim over",
)


R.section("v5.3.0 review 2 — the what-if and the fuse advisor see the block")

_wf_src = inspect.getsource(_Coord.async_simulate)
R.check(
    "the shadow solve inherits the block, like every other input it inherits",
    "space_blocked=self._pump_signals.space_blocked" in _wf_src
    and "dhw_blocked=self._pump_signals.dhw_blocked" in _wf_src,
    "the what-if is DIFFERENCED against the live plan, so an input that "
    "shaped one and not the other turns the difference into a comparison of "
    "two different questions",
)
_wf_adv = inspect.getsource(_Coord._maybe_run_fuse_advisor)
R.check(
    "and the advisor declines to answer at all while a channel is blocked",
    "space_blocked or self._pump_signals.dhw_blocked" in _wf_adv,
    "a month in which the pump could not heat is not evidence about how "
    "many amperes the house needs",
)

# The arithmetic the advisor does, on real solves, with and without a block.
_fa_base_free = _mb_run()
_fa_base_blocked = _mb_run(space_blocked=True)
_fa_capped = _mb_run(power_caps_extra=np.full(_mb_n, 1.2))


def _fa_coldest(plan):
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


def _fa_verdict(baseline):
    breach = float(_fa_capped.predictive_info.get("power_cap_breach_c") or 0.0)
    bc, sc = _fa_coldest(baseline), _fa_coldest(_fa_capped)
    if breach > 0.0 and bc is not None and sc is not None:
        breach = max(0.0, min(breach, float(bc) - float(sc)))
    return breach


R.check(
    "the premise: a tight candidate fuse really does breach the floor",
    _fa_verdict(_fa_base_free) > 0.05,
    f"shortfall {_fa_verdict(_fa_base_free):.2f} °C against an unblocked "
    f"baseline — a fixture where the fuse fitted would prove nothing",
)
R.check(
    "and a blocked baseline would have called that same fuse feasible",
    _fa_verdict(_fa_base_blocked) <= 0.05,
    f"shortfall {_fa_verdict(_fa_base_blocked):.2f} °C — min_room "
    f"{_fa_coldest(_fa_base_free)} unblocked vs {_fa_coldest(_fa_base_blocked)} "
    f"blocked, so base_cold - sim_cold goes negative and the clamp zeroes a "
    f"real breach. This is the arithmetic the advisor was publishing.",
)


R.section("v5.3.0 review 2 — the smaller repairs")

# m9: the summary must report the number the plan applies, not the raw one.
_sm_young = DefrostDerate()
_sm_t, _sm_h = _sm_young._bucket(2.0, 60.0)
_sm_young.factors[_sm_t][_sm_h] = 0.80
_sm_young.counts[_sm_t][_sm_h] = 3
_sm_row = [
    b
    for b in _sm_young.summary()
    if b["outdoor_range"][0] <= 2.0 < b["outdoor_range"][1]
][0]
R.check(
    "the summary's derate is the one the plan multiplies by",
    abs(_sm_row["derate"] - _sm_young.factor(2.0, 60.0)) < 1e-3,
    f"summary {_sm_row['derate']} vs factor {_sm_young.factor(2.0, 60.0):.3f} "
    f"— reporting the raw estimator showed 0.80 while the plan used 0.95",
)
R.check(
    "and what it has learned is reported alongside, not instead",
    abs(_sm_row["learned"] - 0.80) < 1e-9,
    f"{_sm_row}",
)

# m11: hours are wall clock and do not add across the two channels.
_nh_both = narrative_mod.build(
    {"powers": [0.0] * 48, "prices": [1.0] * 48, "reasons": ["pump_mode"] * 48},
    {"powers": [0.0] * 48, "prices": [1.0] * 48, "reasons": ["pump_mode"] * 48},
    0.5,
)
R.check(
    "a 24 h horizon blocked on both channels reports 24 h, not 48",
    _nh_both[0]["hours"] == 24.0,
    f"{_nh_both} — the two schedules run over the same horizon, so a reason "
    f"carried on both sides of one step happened once",
)
_nh_energy = narrative_mod.build(
    {"powers": [2.0] * 4, "prices": [1.0] * 4, "reasons": ["cheap_price"] * 4},
    {"powers": [1.0] * 4, "prices": [1.0] * 4, "reasons": ["cheap_price"] * 4},
    0.5,
)
R.check(
    "while energy and money still add, because they are per channel",
    abs(_nh_energy[0]["kwh"] - 6.0) < 1e-9,
    f"{_nh_energy}",
)

# m14: the stub had no last_reported, so the mechanism the cloud-gap argument
# rests on was never exercised by any freshness test in the suite.
_lr_live = FakeState(
    "21.4",
    last_updated=minutes_ago(600, NOW),
    last_reported=minutes_ago(2, NOW),
)
_lr_dead = FakeState("21.4", last_updated=minutes_ago(600, NOW))
_lr_a = InputReader(
    FakeHass({"sensor.indoor": _lr_live}),
    {"indoor_temp_entity": "sensor.indoor"},
    now=lambda: NOW,
).read("indoor_temp_entity")
_lr_b = InputReader(
    FakeHass({"sensor.indoor": _lr_dead}),
    {"indoor_temp_entity": "sensor.indoor"},
    now=lambda: NOW,
).read("indoor_temp_entity")
R.check(
    "a stable sensor that is still REPORTING is fresh, though it last changed "
    "ten hours ago",
    _lr_a.ok and not _lr_a.stale,
    f"age {_lr_a.age_minutes} min — this is the preference the whole "
    f"cloud-gap argument rests on, and no test exercised it before",
)
R.check(
    "while one that stopped reporting is stale on the same last_changed",
    _lr_b.stale and not _lr_b.ok,
    f"age {_lr_b.age_minutes} min",
)



# v5.2.0: the hot-water tank's own prediction-accuracy record, and the
# expected-error band the card draws from it.
#
# The room already had this machinery (T5 #16). The tank had none, so the
# card had no error band for any series -- and the dashed pair beside the
# room curve, which is the two FLOORS, was being read as one. These checks
# cover the three claims the feature makes: the record fills only from a
# configured, usable probe; its sigma widens with lead time; and the
# published band brackets the curve and is absent until there is evidence.
# ===========================================================================
from heatpump_optimizer.optimizer import OptimizationResult as _DbResult

_DB_T0 = datetime(2025, 3, 3, 0, 0, tzinfo=UTC)
#: Half-hour cycles, 30 h — past the 24 h lead bucket, so every bucket in
#: LEAD_BUCKETS gets a chance to score at least one pair.
_DB_CYCLES = 62
#: The solver's step, which is what `_file_lead_predictions` buckets against.
_DB_DT_H = 0.25
#: The tank as measured: dead steady. The plan below predicts it climbing,
#: so the model's error at lead L is exactly 0.4·L °C — known in closed
#: form, which is what makes "widens with lead" a check and not a hope.
_DB_TANK_C = 55.0
_DB_DRIFT_PER_STEP = 0.1
#: Cycles the "goes_stale" probe reads normally before it stops updating.
#: Long enough that the record is already filling when the sensor dies, so
#: the check that follows is about what STOPS, not about an empty tracker.
_DB_FREEZE_AT = 24


def _db_plan(solve_time):
    """A plan whose tank trajectory climbs away from the measured truth."""
    n = 120  # > 24 h / 0.25 h, so the longest lead bucket has an index
    return _DbResult(
        power_schedule=[0.0] * n,
        room_temp_trajectory=[21.0] * (n + 1),
        slab_temp_trajectory=[22.0] * (n + 1),
        timestamps=[solve_time + timedelta(hours=_DB_DT_H * k) for k in range(n)],
        prices=[1.0] * n,
        predicted_cost=0.0,
        baseline_cost=0.0,
        predicted_savings=0.0,
        savings_percentage=0.0,
        optimal_setpoints=[21.0] * n,
        status="optimal",
        dhw_power_schedule=[0.0] * n,
        dhw_temp_trajectory=[
            _DB_TANK_C + _DB_DRIFT_PER_STEP * k for k in range(n + 1)
        ],
        space_reasons=["idle"] * n,
        dhw_reasons=["idle"] * n,
        price_known=[True] * n,
    )


def _db_probe_state(condition, t, i=0):
    """The tank probe as this condition presents it at cycle ``i``, time ``t``."""
    if condition == "healthy":
        return FakeState(f"{_DB_TANK_C:.1f}", unit="°C", last_updated=t)
    if condition == "goes_stale":
        # The one case the `raw is None` gate cannot catch. The sensor keeps
        # reporting a perfectly readable number; it just stops UPDATING it.
        # `_update_current_state` then pins `_dhw_temperature` at the last
        # good value by design, so the accuracy record still sees 55.0 every
        # cycle. Only `_learning_frozen` can tell that this is a corpse
        # rather than a measurement -- which is why the other four
        # conditions above do not exercise that gate at all.
        if i < _DB_FREEZE_AT:
            return FakeState(f"{_DB_TANK_C:.1f}", unit="°C", last_updated=t)
        return FakeState(
            f"{_DB_TANK_C:.1f}",
            unit="°C",
            last_updated=_DB_T0 + timedelta(minutes=30 * (_DB_FREEZE_AT - 1)),
        )
    if condition == "stale":
        return FakeState(
            f"{_DB_TANK_C:.1f}", unit="°C", last_updated=t - timedelta(hours=12)
        )
    if condition == "unavailable":
        return FakeState("unavailable", unit="°C", last_updated=t)
    if condition == "missing_entity":
        return None
    if condition == "not_numeric":
        return FakeState("hot", unit="°C", last_updated=t)
    raise AssertionError(condition)


def _db_drive(probe="healthy", configured=True, feed=True, cycles=_DB_CYCLES):
    """Drive the real filing/scoring path for ``cycles`` half hours.

    ``configured=False`` is the house with no tank probe at all — the case
    that must record nothing. ``feed=False`` is the MUTATION: the filing
    call is neutered and everything else left exactly as it is, so a band
    that still appears is a band coming from somewhere other than evidence.
    """
    import homeassistant.util.dt as _db_dt

    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }
    states = {
        "sensor.indoor": FakeState("21.0", unit="°C", last_updated=_DB_T0),
        "sensor.outdoor": FakeState("-2.0", unit="°C", last_updated=_DB_T0),
    }
    if configured:
        cfg["dhw_temp_entity"] = "sensor.tank"
        states["sensor.tank"] = FakeState(
            f"{_DB_TANK_C:.1f}", unit="°C", last_updated=_DB_T0
        )
    hass = _FakeHass(states)
    coord = Coord(hass, _FakeEntry(data=cfg))
    coord._opt_config.time_step_minutes = _DB_DT_H * 60.0
    coord._current_action = {"power": 0.0}
    coord._current_weather = lambda: (0.0, 0.0)
    if not feed:
        coord._file_dhw_lead_predictions = lambda *a, **k: None
    real_now, real_utcnow = _db_dt.now, _db_dt.utcnow
    try:
        for i in range(cycles):
            t = _DB_T0 + timedelta(minutes=30 * i)
            _db_dt.now = lambda t=t: t
            _db_dt.utcnow = lambda t=t: t
            hass.states.set(
                "sensor.indoor", FakeState("21.0", unit="°C", last_updated=t)
            )
            hass.states.set(
                "sensor.outdoor", FakeState("-2.0", unit="°C", last_updated=t)
            )
            if configured:
                st = _db_probe_state(probe, t, i)
                if st is None:
                    hass.states._states.pop("sensor.tank", None)
                else:
                    hass.states.set("sensor.tank", st)
            _asyncio.run(coord._update_current_state())
            # The two real call sites, in the order the update cycle runs
            # them: file this solve's promises, then settle the matured ones.
            coord._file_lead_predictions(_db_plan(t), t)
            coord._record_accuracy()
    finally:
        _db_dt.now, _db_dt.utcnow = real_now, real_utcnow
    return coord


def _db_band(coord, solve_time=_DB_T0):
    """The published DHW forecast for this coordinator's tank record."""
    return coord._build_plan_views(_db_plan(solve_time))["dhw_plan"]["forecast"]


# --- the record fills only from a configured, usable probe -----------------
_db_ok = _db_drive()
R.check(
    "a configured, healthy tank probe fills the hot-water accuracy record",
    _db_ok._dhw_accuracy.has_lead_history()
    and sum(_db_ok._dhw_accuracy.lead_counts.values()) > 0,
    f"counts {_db_ok._dhw_accuracy.lead_counts}",
)
R.check(
    "and it does so without touching the room's record's lead buckets",
    _db_ok._dhw_accuracy is not _db_ok._accuracy
    and _db_ok._dhw_accuracy.lead_sigma != {},
    f"room {_db_ok._accuracy.lead_sigma}, tank {_db_ok._dhw_accuracy.lead_sigma}",
)
R.check(
    "the tank record stays out of the one-step sample deque, which is the "
    "room's",
    len(_db_ok._dhw_accuracy.samples) == 0,
    f"{len(_db_ok._dhw_accuracy.samples)} samples on the tank tracker",
)

_db_none = _db_drive(configured=False)
R.check(
    "a house with no tank probe records nothing at all",
    not _db_none._dhw_accuracy.has_lead_history()
    and not _db_none._dhw_accuracy.lead_pending,
    f"sigma {_db_none._dhw_accuracy.lead_sigma}, "
    f"pending {len(_db_none._dhw_accuracy.lead_pending)}",
)
R.check(
    "and it publishes no band, so the card draws nothing",
    all(
        p["dhw_temp_lo"] is None and p["dhw_temp_hi"] is None
        for p in _db_band(_db_none)
    ),
)

# v5.1.3's discipline: an unusable configured input freezes the learners, not
# only a stale one. A sample the tank's own learners would refuse must not
# reach the accuracy record either — a probe pinned at its last good value
# reads as a flawless prediction and would collapse the band to a hairline.
for _db_cond in ("stale", "unavailable", "missing_entity", "not_numeric"):
    _db_c = _db_drive(probe=_db_cond)
    R.check(
        f"a tank probe that is {_db_cond} scores nothing into the record",
        not _db_c._dhw_accuracy.has_lead_history(),
        f"sigma {_db_c._dhw_accuracy.lead_sigma}, "
        f"counts {_db_c._dhw_accuracy.lead_counts}",
    )
    R.check(
        f"and no band is published while the probe is {_db_cond}",
        all(p["dhw_temp_lo"] is None for p in _db_band(_db_c)),
    )

# A probe that dies HALFWAY, which none of the four conditions above reach:
# they present an unusable sensor from the first cycle, so `_dhw_temperature`
# is never set and the "no value read yet" gate answers on its own. Here the
# sensor reads normally for twelve hours and then stops updating, leaving
# `_update_current_state`'s deliberate pin holding a stale 55.0 that looks
# exactly like a healthy reading. Only the v5.1.3 freeze predicate separates
# the two, so this is the case that actually exercises it.
_db_frozen = _db_drive(probe="goes_stale")
_db_frozen_longer = _db_drive(probe="goes_stale", cycles=_DB_CYCLES + 40)
R.check(
    "a tank probe pinned at its last good value still reads back, and the "
    "record refuses it anyway",
    _db_frozen._dhw_temperature == _DB_TANK_C
    and _db_frozen._dhw_probe_temperature() is None,
    f"pinned {_db_frozen._dhw_temperature}, "
    f"probe answers {_db_frozen._dhw_probe_temperature()}",
)
R.check(
    "so a probe that stops updating stops filling the record, while the "
    "same run on a live probe keeps filling it",
    sum(_db_frozen._dhw_accuracy.lead_counts.values())
    < sum(_db_ok._dhw_accuracy.lead_counts.values())
    and _db_frozen._dhw_accuracy.has_lead_history(),
    f"frozen {_db_frozen._dhw_accuracy.lead_counts} vs "
    f"live {_db_ok._dhw_accuracy.lead_counts}",
)
R.check(
    "and it stays stopped: another 20 h against the dead probe scores "
    "nothing more and files nothing more",
    _db_frozen_longer._dhw_accuracy.lead_counts
    == _db_frozen._dhw_accuracy.lead_counts
    and _db_frozen_longer._dhw_accuracy.lead_sigma
    == _db_frozen._dhw_accuracy.lead_sigma,
    f"{_db_frozen_longer._dhw_accuracy.lead_counts} after the extra cycles "
    f"vs {_db_frozen._dhw_accuracy.lead_counts} before them",
)
R.check(
    "the band it had already earned survives the outage -- a dead probe "
    "stops the record, it does not erase it",
    any(p["dhw_temp_lo"] is not None for p in _db_band(_db_frozen)),
)

# --- sigma widens with lead ------------------------------------------------
_db_sigmas = [
    (lead, _db_ok._dhw_accuracy.sigma(lead)) for lead in (1.0, 3.0, 6.0, 12.0, 24.0)
]
R.check(
    "the tank's expected error grows monotonically with how far ahead the "
    "promise was made",
    all(b[1] > a[1] for a, b in zip(_db_sigmas, _db_sigmas[1:])),
    "; ".join(f"{lead:g}h={sig:.3f}" for lead, sig in _db_sigmas),
)
R.check(
    "and it lands on the error the plan actually made (0.4 °C per hour of "
    "lead, by construction)",
    all(
        abs(sig - 0.4 * lead) < 0.05 * max(1.0, 0.4 * lead)
        for lead, sig in _db_sigmas
    ),
    "; ".join(f"{lead:g}h={sig:.3f} vs {0.4 * lead:.3f}" for lead, sig in _db_sigmas),
)

# --- the published band ----------------------------------------------------
_db_fc = _db_band(_db_ok)
R.check(
    "every DHW forecast step carries both band keys",
    all("dhw_temp_lo" in p and "dhw_temp_hi" in p for p in _db_fc),
)
R.check(
    "the band brackets the tank curve at every step",
    all(
        p["dhw_temp_lo"] <= p["dhw_temp"] <= p["dhw_temp_hi"]
        for p in _db_fc
        if p["dhw_temp"] is not None
    ),
    next(
        (
            f"{p['dhw_temp_lo']} / {p['dhw_temp']} / {p['dhw_temp_hi']}"
            for p in _db_fc
            if p["dhw_temp"] is not None
            and not p["dhw_temp_lo"] <= p["dhw_temp"] <= p["dhw_temp_hi"]
        ),
        "",
    ),
)
R.check(
    "and it is symmetric about it, to the published rounding",
    all(
        abs(
            (p["dhw_temp_hi"] - p["dhw_temp"]) - (p["dhw_temp"] - p["dhw_temp_lo"])
        )
        <= 0.01
        for p in _db_fc
        if p["dhw_temp"] is not None
    ),
)
_db_widths = [
    round(p["dhw_temp_hi"] - p["dhw_temp_lo"], 3)
    for p in _db_fc
    if p["dhw_temp_lo"] is not None
]
R.check(
    "the band widens further into the plan, because the record says the "
    "model does",
    len(_db_widths) > 2 and _db_widths[-1] > _db_widths[0],
    f"first {_db_widths[0] if _db_widths else '-'}, "
    f"last {_db_widths[-1] if _db_widths else '-'}",
)
# The band must END where the curve ends. `series()` fills past the end of a
# trajectory with None, and a band drawn around a step that has no centre
# would be two dashed lines bracketing nothing.
_db_short = _db_plan(_DB_T0)
_db_short.dhw_temp_trajectory = _db_short.dhw_temp_trajectory[:20]
_db_short_fc = _db_ok._build_plan_views(_db_short)["dhw_plan"]["forecast"]
R.check(
    "a tank trajectory that stops early takes its band with it, step for "
    "step",
    all(
        (p["dhw_temp"] is None)
        == (p["dhw_temp_lo"] is None)
        == (p["dhw_temp_hi"] is None)
        for p in _db_short_fc
    )
    and any(p["dhw_temp"] is None for p in _db_short_fc)
    and any(p["dhw_temp_lo"] is not None for p in _db_short_fc),
    f"{sum(1 for p in _db_short_fc if p['dhw_temp'] is None)} curve nulls, "
    f"{sum(1 for p in _db_short_fc if p['dhw_temp_lo'] is None)} band nulls",
)

R.check(
    "the band is rounded exactly as `dhw_temp` is: two decimals",
    all(
        round(p["dhw_temp_lo"], 2) == p["dhw_temp_lo"]
        and round(p["dhw_temp_hi"], 2) == p["dhw_temp_hi"]
        for p in _db_fc
        if p["dhw_temp_lo"] is not None
    ),
)

# A fresh tracker: sigma answers 0.0 for want of evidence, and `dhw_temp ± 0`
# would draw two dashed lines exactly on the curve — a brand new install
# claiming perfect foresight. Nulls instead.
_db_fresh = _db_drive(cycles=1)
R.check(
    "a fresh record publishes None, not a zero-width band",
    all(
        p["dhw_temp_lo"] is None and p["dhw_temp_hi"] is None
        for p in _db_band(_db_fresh)
    )
    and not _db_fresh._dhw_accuracy.has_lead_history(),
)
R.check(
    "and the tank curve itself is published exactly as before",
    all(p["dhw_temp"] is not None for p in _db_band(_db_fresh)),
)

# --- MUTATION: neuter the feed, the band must vanish -----------------------
#
# Everything above would also pass against a band computed from something
# other than the record — a constant, the plan's own spread, anything. This
# is the check that rules that out: the same 30 h drive with only the filing
# call neutered must leave no record and publish no band.
_db_mut = _db_drive(feed=False)
R.check(
    "MUTATION: with the tracker feed neutered the record stays empty",
    not _db_mut._dhw_accuracy.has_lead_history()
    and not _db_mut._dhw_accuracy.lead_pending,
    f"sigma {_db_mut._dhw_accuracy.lead_sigma}, "
    f"counts {_db_mut._dhw_accuracy.lead_counts}",
)
R.check(
    "MUTATION: and the published band vanishes with it",
    all(
        p["dhw_temp_lo"] is None and p["dhw_temp_hi"] is None
        for p in _db_band(_db_mut)
    ),
    "the band survived its own evidence being removed",
)
R.check(
    "MUTATION: while the un-neutered run on identical inputs does publish "
    "one — the two differ only in the feed",
    any(p["dhw_temp_lo"] is not None for p in _db_band(_db_ok)),
)
R.check(
    "MUTATION: and nothing else about the DHW forecast moved",
    [
        {k: v for k, v in p.items() if not k.startswith("dhw_temp_")}
        for p in _db_band(_db_mut)
    ]
    == [
        {k: v for k, v in p.items() if not k.startswith("dhw_temp_")}
        for p in _db_band(_db_ok)
    ],
)

# --- the "configured at all" gate, which nothing was testing ---------------
#
# Found by deleting it: the whole suite still passed. Today it is genuinely
# redundant -- `_dhw_temperature` is only ever assigned from an `ok` reading,
# so an unconfigured house is already answered by the "nothing read yet"
# gate, which is why `_db_drive(configured=False)` above cannot reach this.
#
# It is kept, and pinned, because of the OTHER tank temperature in the
# coordinator. `_current_state.dhw_temperature` carries a 55 °C MODELLING
# DEFAULT, and the coordinator already falls back to it elsewhere
# (`self._dhw_temperature or self._current_state.dhw_temperature`). One such
# fallback reaching this probe would train the record on a constant on a
# house with no thermometer, and a record trained on a constant reports a
# flawless model: the band would collapse to a hairline claiming a precision
# nothing measured. The freeze predicate cannot stand in for the check --
# an unconfigured slot must never freeze learning, so it answers None.
_db_unconf = _t2_coord()
_db_unconf._dhw_temperature = 55.0
_db_unconf._current_state.dhw_temperature = 55.0
R.check(
    "a tank temperature with no tank entity configured is not a measurement, "
    "and the probe refuses it",
    _db_unconf._dhw_probe_temperature() is None
    and _db_unconf._learning_frozen(hp_const.CONF_DHW_TEMP_ENTITY) is None,
    f"probe {_db_unconf._dhw_probe_temperature()}, "
    f"frozen {_db_unconf._learning_frozen(hp_const.CONF_DHW_TEMP_ENTITY)}",
)
_db_conf = _t2_coord(dhw_temp_entity="sensor.tank")
_db_conf._dhw_temperature = 55.0
R.check(
    "and the very same value with the entity configured IS one -- the "
    "configuration is the whole difference",
    _db_conf._dhw_probe_temperature() == 55.0,
    f"{_db_conf._dhw_probe_temperature()}",
)

# --- the three branches that void or protect the tank's promises ----------
#
# All three mirror a room-side branch that IS covered, and all three were
# covered on the room side only: deleting any of the tank's three lines left
# the whole suite passing. They are not cosmetic. A promise scored against a
# tank that comfort/boost/off or a step-response experiment is driving on its
# own rules charges the model with an error it never made, and the band the
# card draws is exactly that error.

# 1. Leaving auto/economy: the plan stops being what runs.
_db_mode = _t2_coord()
_db_mode._mode = "auto"
for _db_rec in (_db_mode._accuracy, _db_mode._dhw_accuracy):
    _db_rec.note_lead_prediction(_T5 + timedelta(hours=1), 1.0, 55.0)
_asyncio.run(_db_mode.async_set_mode("economy"))
_db_mode_kept = bool(_db_mode._dhw_accuracy.lead_pending)
_asyncio.run(_db_mode.async_set_mode("comfort"))
R.check(
    "leaving auto/economy voids the TANK's unmatured promises, not only the "
    "room's",
    _db_mode_kept and not _db_mode._dhw_accuracy.lead_pending,
    "auto -> economy keeps them; auto -> comfort clears them",
)

# 2. A step-response experiment overrides the plan for its duration.
_db_exp = _db_drive(cycles=2)
_db_exp._mode = "auto"
_db_exp._dhw_accuracy.lead_pending.clear()
_db_exp._file_lead_predictions(_db_plan(_DB_T0), _DB_T0)
_db_exp_filed = len(_db_exp._dhw_accuracy.lead_pending)
_db_exp._sysid.phase = PHASE_ARMED
_db_exp._file_lead_predictions(_db_plan(_DB_T0), _DB_T0)
R.check(
    "an active experiment files no tank promises and voids the ones the "
    "plan it overrides had filed",
    _db_exp_filed == len(LEAD_BUCKETS)
    and not _db_exp._dhw_accuracy.lead_pending,
    f"{_db_exp_filed} filed before the experiment, "
    f"{len(_db_exp._dhw_accuracy.lead_pending)} left after it",
)

# 3. Order inside `_file_lead_predictions`: the tank is filed BEFORE the
# room's `if not trajectory: return`. A house whose plan carries no room
# trajectory at all still has a tank to promise about, and moving the call
# below that return would silence the tank's record on exactly those houses
# — silently, because the room's own checks would all still pass.
_db_noroom = _db_drive(cycles=2)
_db_noroom._mode = "auto"
_db_noroom._accuracy.lead_pending.clear()
_db_noroom._dhw_accuracy.lead_pending.clear()
_db_noroom_plan = _db_plan(_DB_T0)
_db_noroom_plan.room_temp_trajectory = []
_db_noroom_plan.upper_temp_trajectory = []
_db_noroom_plan.lower_temp_trajectory = []
_db_noroom._file_lead_predictions(_db_noroom_plan, _DB_T0)
R.check(
    "a plan with no room trajectory still files the tank's promises -- the "
    "room's early return must not take the tank down with it",
    len(_db_noroom._dhw_accuracy.lead_pending) == len(LEAD_BUCKETS)
    and not _db_noroom._accuracy.lead_pending,
    f"tank {len(_db_noroom._dhw_accuracy.lead_pending)}, "
    f"room {len(_db_noroom._accuracy.lead_pending)}",
)

# --- persistence, additively ----------------------------------------------
_db_store = {
    "accuracy": _db_ok._accuracy.as_dict(),
    "dhw_accuracy": _db_ok._dhw_accuracy.as_dict(),
}
_db_round = AccuracyTracker.from_dict(_db_store["dhw_accuracy"])
R.check(
    "the tank record survives a save/load round trip",
    _db_round.has_lead_history()
    and _db_round.lead_counts == _db_ok._dhw_accuracy.lead_counts
    and all(
        abs(_db_round.sigma(lead) - _db_ok._dhw_accuracy.sigma(lead)) < 1e-3
        for lead in (1.0, 3.0, 6.0, 12.0, 24.0)
    ),
    f"{_db_round.lead_counts} vs {_db_ok._dhw_accuracy.lead_counts}",
)
R.check(
    "a store written before v5.2.0 loads without error and simply has no "
    "tank record",
    not AccuracyTracker.from_dict(
        {"accuracy": _db_ok._accuracy.as_dict()}.get("dhw_accuracy")
    ).has_lead_history(),
)
R.check(
    "and an older build reading a v5.2.0 store still finds its own key "
    "untouched",
    _db_store["accuracy"] == _db_ok._accuracy.as_dict(),
)

# `has_lead_history` is the whole difference between "no evidence" and "the
# model has been perfect", which `sigma` cannot express. Pin both directions.
_db_perfect = AccuracyTracker()
_db_perfect.lead_sigma[1.0] = 0.0
_db_perfect.lead_counts[1.0] = 40
R.check(
    "a record that scored 40 flawless pairs HAS history, though its sigma "
    "is zero",
    _db_perfect.has_lead_history() and _db_perfect.sigma(1.0) == 0.0,
)
_db_halfrestored = AccuracyTracker()
_db_halfrestored.lead_sigma[1.0] = 1.2
R.check(
    "a sigma with no counts behind it does not count as history",
    not _db_halfrestored.has_lead_history()
    and _db_halfrestored.sigma(1.0) == 0.0,
)
# ---------------------------------------------------------------------------
R.section("v5.1.10 — the charge limit is the charge limit, every ordinary day")

# The owner's report: "Highest tank temperature to charge to" 52 °C, the
# anti-legionella cycle at its default 60 °C, no cycle due. Until v5.1.10 the
# disinfection temperature was folded into `dhw_max_temp` permanently, so the
# cost planner had a 60 °C ceiling to spend every day of the week — and it
# spent it, because pre-buying at the night trough beats heating at the
# evening window even after standby losses.
from heatpump_optimizer.optimizer import REASON_LEGIONELLA as _LG_REASON


def _lg_plan(setpoint, *, leg_temp=60.0, enabled=True, hours_since=20.0):
    built = _mk_golden(
        config_overrides={
            "dhw_setpoint": setpoint,
            "dhw_legionella_enabled": enabled,
        },
        param_overrides={"dhw_legionella_temp": leg_temp},
        state_overrides={"dhw_hours_since_legionella": hours_since},
    )
    res = built["optimizer"].optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], _G_START,
    )
    return built, res, np.asarray(res.dhw_temp_trajectory, dtype=float)


_lg_built, _lg_res, _lg_traj = _lg_plan(52.0)
R.check(
    "the owner's 52/60 pair keeps the tank at or below the 52 °C limit "
    "on a day with no cycle due",
    _lg_traj.max() <= 52.1,
    f"peak {_lg_traj.max():.2f} °C",
)
R.check(
    "…and the ceiling the parameters publish is the charge limit itself",
    _lg_built["optimizer"].model.params.dhw_max_temp == 52.0,
    f"dhw_max_temp {_lg_built['optimizer'].model.params.dhw_max_temp}",
)

# Mutation value: put the old definition back and the same solve reproduces
# the reported behaviour. Without this the check above could be passing for
# any number of unrelated reasons.
_lg_old = ThermalParameters.dhw_max_temp
try:
    ThermalParameters.dhw_max_temp = property(
        lambda self: min(
            70.0,
            max(self.dhw_setpoint, self.dhw_legionella_temp)
            if self.dhw_legionella_enabled
            else self.dhw_setpoint,
        )
    )
    _lg_mut_traj = _lg_plan(52.0)[2]
finally:
    ThermalParameters.dhw_max_temp = _lg_old
R.check(
    "reverting dhw_max_temp reproduces the reported over-charge "
    "(mutation check)",
    _lg_mut_traj.max() >= 58.0,
    f"mutant peak {_lg_mut_traj.max():.2f} °C — v5.1.5 recorded 58.39",
)

# Row 4 of the report: this was never one owner's misconfiguration. The stock
# defaults are a 55 °C charge limit and a 60 °C cycle, so every installation
# on defaults was running its tank 4 °C over the limit.
_lg_stock_traj = _lg_plan(55.0)[2]
R.check(
    "the stock 55/60 defaults stay at the 55 °C limit too",
    _lg_stock_traj.max() <= 55.1,
    f"peak {_lg_stock_traj.max():.2f} °C — v5.1.5 recorded 59.16",
)

# Disinfection is a safety feature and the fix must not quietly disable it.
# The regression that would matter most is a cycle that is scheduled, costs
# money, and never reaches temperature.
_lg_due_built, _lg_due_res, _lg_due_traj = _lg_plan(52.0, hours_since=150.0)
_lg_due_info = _lg_due_res.predictive_info or {}
R.check(
    "a cycle that IS due is still scheduled",
    bool(_lg_due_info.get("dhw_legionella_due")),
    f"predictive_info says {_lg_due_info.get('dhw_legionella_due')!r}",
)
R.check(
    "…and the boost actually attains the disinfection temperature",
    _lg_due_traj.max() >= 59.5,
    f"peak {_lg_due_traj.max():.2f} °C against a 60 °C target",
)
R.check(
    "…while the plan still marks the step it did it in",
    _LG_REASON in (_lg_due_res.dhw_reasons or []),
    "no step carries the legionella reason code",
)

# The per-step ceiling is exactly that: raised around the cycle, the charge
# limit everywhere else. A cycle at hour X must not license a hot tank at
# hour X + 12.
# `predictive_info` publishes the cycle's HOUR, not its step; the step the
# planner actually chose is stashed on the optimizer, which is what these two
# checks are about.
_lg_due_step = _lg_due_built["optimizer"]._dhw_legionella_step
if _lg_due_step is not None:
    _lg_late = _lg_due_traj[int(_lg_due_step) + 12 * 4 :]
    R.check(
        "twelve hours after the cycle the tank is back under the limit",
        _lg_late.size == 0 or _lg_late.max() <= 52.1,
        f"peak {_lg_late.max():.2f} °C" if _lg_late.size else "no steps left",
    )

# An overdue timer used to collapse the placement search to `limit = 1` and
# pin the requirement on step 0 — the one step the tank provably cannot be at
# 60 °C by, which is what made the failure permanent.
_lg_over = {}
for _hours in (170.0, 500.0, 2000.0):
    _b, _r, _t = _lg_plan(52.0, hours_since=_hours)
    _lg_over[_hours] = (_b["optimizer"]._dhw_legionella_step, float(_t.max()))
R.check(
    "an overdue cycle is not pinned to step 0 of every plan",
    all(step not in (None, 0) for step, _ in _lg_over.values()),
    f"placements {[s for s, _ in _lg_over.values()]}",
)
R.check(
    "…and it reaches temperature instead of being re-commanded for ever",
    all(peak >= 59.5 for _, peak in _lg_over.values()),
    f"peaks {[round(p, 2) for _, p in _lg_over.values()]}",
)

# The model still has to allow the boost: the everyday ceiling is a
# preference, the tank rating is physics, and conflating the two would cap a
# disinfection cycle at the setpoint.
_lg_p = ThermalParameters(dhw_setpoint=52.0, dhw_legionella_temp=60.0)
R.check(
    "the tank rating stays above the disinfection temperature",
    _lg_p.dhw_max_temp == 52.0 and _lg_p.dhw_hard_max_temp == 60.0,
    f"ceiling {_lg_p.dhw_max_temp}, rating {_lg_p.dhw_hard_max_temp}",
)
_lg_p_off = ThermalParameters(
    dhw_setpoint=52.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=False
)
R.check(
    "with disinfection off the two are the same number, as before",
    _lg_p_off.dhw_max_temp == _lg_p_off.dhw_hard_max_temp == 52.0,
    f"{_lg_p_off.dhw_max_temp} / {_lg_p_off.dhw_hard_max_temp}",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — the disinfection timer cannot latch")

from heatpump_optimizer.config_flow import (
    _dhw_legionella_warning as _lgw,
)

_LG_CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "dhw_temp_entity": "sensor.tank",
    "dhw_tank_volume": 300.0,
    "dhw_setpoint": 52.0,
    "dhw_legionella_temperature": 60.0,
}


def _lg_coord(**over):
    cfg = {**_LG_CFG, **over}
    coord = _Coord(_FakeHass(), _FakeEntry(data=cfg))
    coord._dhw_last_legionella = _G_START - timedelta(days=8)
    return coord


def _lg_cycle(coord, temps):
    """Command a boost, feed it `temps`, then let the plan move on."""
    for temp in temps:
        coord._current_action = {"dhw_reason": _LG_REASON}
        _asyncio.run(coord._async_track_dhw_legionella_cycle(temp))
    coord._current_action = {"dhw_reason": "idle"}
    _asyncio.run(coord._async_track_dhw_legionella_cycle(temps[-1]))


# A pump that tops out at 54 °C never reaches `legionella_temp - 1`, so the
# observer's reset can never fire. Before v5.1.10 that left `hours_since`
# climbing for ever.
_lg_short = _lg_coord()
_lg_before = _lg_short._dhw_hours_since_legionella()
_lg_cycle(_lg_short, [50.0, 52.0, 53.5, 54.0])
_lg_after = _lg_short._dhw_hours_since_legionella()
R.check(
    "a tank that never gets hot still completes its cycle rather than "
    "latching overdue",
    _lg_before > 168.0 and _lg_after < 1.0,
    f"{_lg_before:.0f} h before, {_lg_after:.2f} h after",
)
R.check(
    "…and it is recorded as an attempt, not as a successful cycle",
    _lg_short._dhw_legionella_attempt is not None
    and _lg_short._dhw_legionella_attempt_peak == 54.0
    and _lg_short._dhw_last_legionella == _G_START - timedelta(days=8),
    f"attempt {_lg_short._dhw_legionella_attempt!r}, "
    f"success {_lg_short._dhw_last_legionella!r}",
)
R.check(
    "…and the user is told the water is not being disinfected",
    any(
        i[1] == "dhw_legionella_unreachable"
        for i in getattr(_lg_short.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_short.hass, 'issues', [])]}",
)

# A cycle that does reach temperature clears both the attempt and the notice.
_lg_short._current_action = {"dhw_reason": "idle"}
_asyncio.run(_lg_short._async_track_dhw_legionella(59.5))
R.check(
    "a cycle that reaches temperature clears the notice and the attempt",
    _lg_short._dhw_legionella_attempt is None
    and not any(
        i[1] == "dhw_legionella_unreachable"
        for i in getattr(_lg_short.hass, "issues", [])
    ),
)

# No tank probe at all: the observer cannot run, so the countdown had no
# reset path whatsoever. It resets — but on an ATTEMPT, not a claim of
# success; see the v5.1.10 section below for why the two are the same
# countdown and only one of them can also be honest about what happened.
_lg_blind = _lg_coord()
_lg_blind._config.pop("dhw_temp_entity", None)
_lg_cycle_blind_before = _lg_blind._dhw_hours_since_legionella()
_lg_blind._current_action = {"dhw_reason": _LG_REASON}
_asyncio.run(_lg_blind._async_track_dhw_legionella_cycle(None))
_lg_blind._current_action = {"dhw_reason": "idle"}
_asyncio.run(_lg_blind._async_track_dhw_legionella_cycle(None))
_lg_blind_since = _lg_blind._dhw_hours_since_legionella()
R.check(
    "with no tank sensor a commanded cycle still resets the countdown "
    "rather than leaving it counting up for ever",
    _lg_cycle_blind_before > 168.0
    and _lg_blind_since is not None
    and _lg_blind_since < 1.0
    and _lg_blind._dhw_legionella_attempt is not None,
    f"{_lg_blind_since} h since, attempt "
    f"{_lg_blind._dhw_legionella_attempt!r}",
)

# A boost nobody commanded must not credit anything.
_lg_idle = _lg_coord()
_lg_idle._current_action = {"dhw_reason": "dhw_window"}
_asyncio.run(_lg_idle._async_track_dhw_legionella_cycle(45.0))
R.check(
    "an ordinary hot-water step is not mistaken for a disinfection cycle",
    (_lg_idle._dhw_hours_since_legionella() or 0.0) > 168.0,
    f"{_lg_idle._dhw_hours_since_legionella()} h since",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — the setpoint/disinfection pair warns, and never blocks")

R.check(
    "a 52 °C limit with a 60 °C cycle is reported, with how often",
    _lgw({"dhw_setpoint": 52.0}, {"dhw_legionella_temperature": 60.0})
    == {"legionella_temp": "60", "setpoint": "52", "interval_days": "7"},
    f"got {_lgw({'dhw_setpoint': 52.0}, {'dhw_legionella_temperature': 60.0})!r}",
)
R.check(
    "the stock defaults are reported too — this is not an exotic pairing",
    _lgw({}, {}) is not None,
    "55 °C limit against a 60 °C cycle is what a fresh install ships with",
)
R.check(
    "a cycle at or below the limit says nothing",
    _lgw({"dhw_setpoint": 60.0}, {"dhw_legionella_temperature": 60.0}) is None,
)
R.check(
    "and disinfection switched off says nothing",
    _lgw(
        {"dhw_setpoint": 52.0, "dhw_legionella_enabled": False},
        {"dhw_legionella_temperature": 60.0},
    )
    is None,
)
# The pair a page already holds must be judged, not just the half submitted:
# the options pages save one page over the stored rest.
R.check(
    "the stored half of the pair still counts",
    _lgw({"dhw_legionella_temperature": 62.0}, {"dhw_setpoint": 52.0})
    == {"legionella_temp": "62", "setpoint": "52", "interval_days": "7"},
)

# Warning, not a block: the coordinator raises the notice from the parameters
# actually in force, which is the only path that also covers the
# set_thermal_parameters service.
_lg_warn = _lg_coord()
_lg_warn._check_dhw_legionella_ceiling()
R.check(
    "the coordinator raises the notice for a live 52/60 pair",
    any(
        i[1] == "dhw_legionella_above_setpoint"
        for i in getattr(_lg_warn.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_warn.hass, 'issues', [])]}",
)
_lg_warn._thermal_params.dhw_legionella_temp = 52.0
_lg_warn._check_dhw_legionella_ceiling()
R.check(
    "…and takes it down again once the pair no longer says anything",
    not any(
        i[1] == "dhw_legionella_above_setpoint"
        for i in getattr(_lg_warn.hass, "issues", [])
    ),
)


from profiles import house as _lg_house, prices as _lg_prices
from profiles import weather as _lg_weather
from heatpump_optimizer.const import DHW_LEGIONELLA_BOOST_MAX_HOURS

# ---------------------------------------------------------------------------
R.section("v5.1.10 — a due cycle actually reaches the disinfection temperature")

# Honouring the charge limit means a summer plan legitimately parks the tank at
# ~37 °C, so a cycle that comes due has the whole climb to make in the hours
# before it. The first cut of this release could not buy that run-up: the floor
# repair bounded its top-ups over the whole tail, every later step sitting ON
# the charge limit read as zero room, and the suffix-minimum carried that zero
# back over every candidate. The cycle then arrived at whatever the greedy pass
# happened to leave in the tank — around 58 °C: never disinfected, never
# creditable, and reported to the owner as "your pump cannot reach 60 °C" on
# hardware that reaches exactly 60.
#
# Two things had to be true for this band to pass. The repair has to be able to
# buy the run-up, and the capacity clamp has to size its allowance from the
# END of a step — draw and standby loss included — or every step of a
# ceiling-pinned ramp lands just below the ceiling it was aimed at and the
# cycle stops at 59.9 rather than 60.0.
from heatpump_optimizer.optimizer import HeatPumpOptimizer as _LgOpt


def _lg_band(setpoint, *, hours_since=150.0, tank=37.0, volume=300.0, pump=6.0):
    built = _mk_golden(
        config_overrides={
            "dhw_tank_volume": volume,
            "heat_pump_max_power": pump,
            "dhw_setpoint": setpoint,
            "dhw_min_temperature": setpoint - 5.0,
        },
        param_overrides={"dhw_legionella_temp": 60.0},
        state_overrides={
            "dhw_hours_since_legionella": hours_since,
            "dhw_temperature": tank,
        },
        price_profile="summer_typical",
        weather_profile="summer_warm",
    )
    res = built["optimizer"].optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], _G_START,
    )
    return built, res, np.asarray(res.dhw_temp_trajectory, dtype=float)


_LG_BAND = tuple(range(41, 50))
_lg_peaks = {s: float(_lg_band(float(s))[2].max()) for s in _LG_BAND}
# The observer credits a cycle at `legionella_temp - 1`, so 59.0 is the bar
# that decides whether the cycle counts at all.
R.check(
    "a due cycle reaches the disinfection temperature at every charge limit "
    "from 41 to 49 °C",
    all(p >= 59.0 for p in _lg_peaks.values()),
    "peaks " + ", ".join(f"{s}:{_lg_peaks[s]:.2f}" for s in _LG_BAND),
)
R.check(
    "…and lands ON it rather than a fraction short",
    all(p >= 59.95 for p in _lg_peaks.values()),
    "peaks " + ", ".join(f"{s}:{_lg_peaks[s]:.2f}" for s in _LG_BAND),
)

# Mutation: put the whole-tail room bound back — the first cut of the floor
# repair's own ceiling, and what left the ramp short.
def _lg_whole_tail_repair(
    self, *, plan, initial_temp, outdoor_temps, draw_rates, dt,
    requirement, max_temp, p_dhw_max, min_run_power, prices, c_dhw,
    forced_off=None,
):
    """The rejected floor repair: the room bound taken over the WHOLE tail, and
    nothing behind it to enforce the ceiling. Same loop, same ranking, same
    arithmetic; the bound is the only difference."""
    plan = np.asarray(plan, dtype=float).copy()
    n = plan.size
    ceiling = np.asarray(max_temp, dtype=float)[:n]
    req = np.minimum(np.asarray(requirement, dtype=float)[:n], ceiling)
    ua = max(self.model.params.dhw_tank_heat_loss_coefficient, 1e-6)
    decay = float(np.clip(1.0 - ua * dt / max(c_dhw, 0.05), 0.0, 1.0))
    weight = np.power(decay, np.arange(n))
    unreachable: set[int] = set()
    for _ in range(48):
        temps = np.asarray(self.model.simulate_dhw_only(
            initial_temp=initial_temp, dhw_power_schedule=plan,
            outdoor_temps=outdoor_temps, draw_rates=draw_rates, dt_hours=dt))
        deficit = req - temps[1:n + 1]
        breach = [int(i) for i in np.where(deficit > 0.05)[0]
                  if int(i) not in unreachable]
        if not breach:
            return plan
        b = breach[0]
        pinned = np.where(temps[:b + 1] >= ceiling[:b + 1] - 0.1)[0]
        lo = int(pinned[-1]) if pinned.size else 0
        headroom = p_dhw_max - plan[lo:b + 1]
        usable = headroom > 1e-6
        if forced_off is not None:
            usable &= ~np.asarray(forced_off[lo:b + 1], dtype=bool)
        gap = ceiling - temps[1:n + 1]
        room_c = (np.minimum.accumulate((gap / weight)[::-1])[::-1]
                  * weight)[lo:b + 1]
        usable &= room_c > 0.01
        costs = np.where(usable, prices[lo:b + 1], np.inf)
        placed = False
        for j_local in np.argsort(costs, kind="stable"):
            j_local = int(j_local)
            if not usable[j_local]:
                break
            j = lo + j_local
            cop_j = max(self.model.marginal_cop(
                float(outdoor_temps[j]), "dhw",
                store_temp=float(temps[j])), 0.5)
            cop_room = max(cop_j, self.model.compute_cop_dhw(
                float(outdoor_temps[j]), float(temps[j])))
            needed = float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6)
            room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)
            add = min(float(np.clip(needed, min_run_power, headroom[j_local])),
                      room_kw)
            level = plan[j] + add
            if level < min_run_power - 1e-9:
                runnable = min(min_run_power, p_dhw_max)
                if runnable > plan[j] + room_kw + 1e-9:
                    continue
                level = runnable
            plan[j] = min(p_dhw_max, level)
            placed = True
            break
        if not placed:
            unreachable.add(b)
    return plan


_lg_saved_repair = _LgOpt._repair_dhw_floor
try:
    _LgOpt._repair_dhw_floor = _lg_whole_tail_repair
    _lg_mut_peaks = {s: float(_lg_band(float(s))[2].max()) for s in _LG_BAND}
finally:
    _LgOpt._repair_dhw_floor = _lg_saved_repair
R.check(
    "the whole-tail bound reproduces the cycle that never reaches "
    "temperature (mutation check)",
    sum(1 for p in _lg_mut_peaks.values() if p < 59.0) >= 2
    and sum(1 for p in _lg_mut_peaks.values() if p < 59.95) >= 6,
    "mutant peaks " + ", ".join(f"{s}:{_lg_mut_peaks[s]:.2f}" for s in _LG_BAND),
)

# The same cycle on other hardware, because the band above is one tank.
_lg_hw = {
    "300 L / 4 kW": _lg_band(45.0, volume=300.0, pump=4.0)[2].max(),
    "500 L / 6 kW": _lg_band(44.0, volume=500.0, pump=6.0)[2].max(),
    "150 L / 6 kW": _lg_band(43.0, volume=150.0, pump=6.0)[2].max(),
}
R.check(
    "…on other tank and pump sizes too",
    all(v >= 59.0 for v in _lg_hw.values()),
    ", ".join(f"{k} {v:.2f}" for k, v in _lg_hw.items()),
)

# The run-up must not turn into a licence to sit at the limit all day: it is
# the LATEST ramp that still arrives, so the hours before it stay ordinary.
_lg_ramp_built, _lg_ramp_res, _lg_ramp_traj = _lg_band(45.0)
_lg_ramp_step = _lg_ramp_built["optimizer"]._dhw_legionella_step
R.check(
    "the run-up is a ramp, not a day at the ceiling",
    _lg_ramp_step is not None
    and _lg_ramp_traj[: max(int(_lg_ramp_step) - 8, 1)].max() <= 45.1,
    f"cycle at step {_lg_ramp_step}, peak before it "
    f"{_lg_ramp_traj[: max(int(_lg_ramp_step) - 8, 1)].max():.2f} °C",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — the floor repair tops the tank up again")

# The first cut of this release bounded the repair's room over the WHOLE tail. Every later step
# sitting exactly ON the charge limit therefore read as zero room, the
# suffix-minimum carried that zero back over every earlier candidate, and the
# repair refused every top-up there was — including a hard `dhw_min` breach
# inside a demand window.
_fr_built = _mk_golden(
    config_overrides={"dhw_setpoint": 52.0, "dhw_legionella_enabled": False}
)
_fr_opt = _fr_built["optimizer"]
_fr_c = _fr_opt.model.params.dhw_tank_thermal_mass
_FR_N, _FR_DT, _FR_RUN, _FR_MIN = 24, 0.25, 3.0, 0.6
_fr_ceiling = np.full(_FR_N, 52.0)
_fr_outdoor = np.zeros(_FR_N)
_fr_prices = np.linspace(1.0, 2.0, _FR_N)
_fr_req = np.full(_FR_N, 20.0)
_fr_req[8] = 45.0
_fr_draws = np.zeros(_FR_N)
_fr_draws[4:9] = 2.2 * _fr_c / _FR_DT

# A plan that empties the tank into a demand floor at step 8 and then charges
# the tail right up to the limit — the shape the whole-tail bound choked on.
_fr_plan = np.zeros(_FR_N)
_fr_plan[10:] = _FR_RUN
_fr_plan = _fr_opt._clamp_dhw_to_capacity(
    plan=_fr_plan, initial_temp=52.0, outdoor_temps=_fr_outdoor,
    draw_rates=_fr_draws, dt=_FR_DT, max_temp=_fr_ceiling,
)
_fr_plan = np.where(_fr_plan < _FR_MIN - 1e-9, 0.0, _fr_plan)


def _fr_traj(plan):
    return np.asarray(_fr_opt.model.simulate_dhw_only(
        initial_temp=52.0, dhw_power_schedule=plan, outdoor_temps=_fr_outdoor,
        draw_rates=_fr_draws, dt_hours=_FR_DT,
    ))


_fr_before = _fr_traj(_fr_plan)
R.check(
    "the fixture really does breach its floor, with the tail on the limit",
    _fr_req[8] - _fr_before[9] > 1.0
    and _fr_before[12:].max() >= 51.5,
    f"deficit {_fr_req[8] - _fr_before[9]:.2f} °C, tail peak "
    f"{_fr_before[12:].max():.2f} °C",
)

# Mutation: the whole-tail bound, computed here from the same trajectory. Its best
# candidate cannot take a block the pump can actually run, so the repair had
# nothing to place and the breach stood.
_fr_ua = max(_fr_opt.model.params.dhw_tank_heat_loss_coefficient, 1e-6)
_fr_decay = float(np.clip(1.0 - _fr_ua * _FR_DT / max(_fr_c, 0.05), 0.0, 1.0))
_fr_w = np.power(_fr_decay, np.arange(_FR_N))
_fr_gap = _fr_ceiling - _fr_before[1:_FR_N + 1]
_fr_room_all = np.minimum.accumulate((_fr_gap / _fr_w)[::-1])[::-1] * _fr_w
_fr_pinned = np.where(_fr_before[:9] >= _fr_ceiling[:9] - 0.1)[0]
_fr_lo = int(_fr_pinned[-1]) if _fr_pinned.size else 0
_fr_cop = _fr_opt.model.compute_cop_dhw(0.0, float(_fr_before[_fr_lo]))
_fr_old_kw = float(_fr_room_all[_fr_lo:9].max()) * _fr_c / (_FR_DT * _fr_cop)
R.check(
    "the whole-tail bound leaves no candidate a runnable block fits in "
    "(mutation check)",
    _fr_old_kw < _FR_MIN,
    f"best whole-tail room {_fr_old_kw:.3f} kW against a {_FR_MIN} kW "
    f"minimum run",
)

_fr_fixed = _fr_opt._repair_dhw_floor(
    plan=_fr_plan.copy(), initial_temp=52.0, outdoor_temps=_fr_outdoor,
    draw_rates=_fr_draws, dt=_FR_DT, requirement=_fr_req,
    max_temp=_fr_ceiling, p_dhw_max=_FR_RUN, min_run_power=_FR_MIN,
    prices=_fr_prices, c_dhw=_fr_c,
)
_fr_after = _fr_traj(_fr_fixed)
R.check(
    "the repair closes the breach",
    _fr_req[8] - _fr_after[9] <= 0.05,
    f"deficit {_fr_req[8] - _fr_after[9]:.3f} °C",
)
R.check(
    "…without taking the tank a degree over the charge limit",
    _fr_after.max() <= 52.0 + 1e-6,
    f"peak {_fr_after.max():.4f} °C against a 52.00 °C limit",
)
R.check(
    "…and publishes no power the hardware cannot run",
    not np.any((_fr_fixed > 1e-9) & (_fr_fixed < _FR_MIN - 1e-9)),
    f"weak slots {np.round(_fr_fixed[(_fr_fixed > 1e-9) & (_fr_fixed < _FR_MIN)], 3).tolist()}",
)

# End to end, at the start hour where the reported breach was worst.
def _lg_e2e(start_hour, hours_since, price_p, weather_p):
    start = datetime(2026, 1, 15, start_hour, 0)
    cfg = _lg_house(dhw=True)
    cfg["dhw_setpoint"] = 52.0
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    params.dhw_legionella_temp = 60.0
    ocfg = _PvOptCfg(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    _fit = lambda a: np.asarray(a, dtype=float)[:96]
    ps = _fit(_lg_prices(price_p, start))
    o, w, rn, sol = (_fit(x) for x in _lg_weather(weather_p, start))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(o[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, dhw_temperature=50.0,
        dhw_hours_since_legionella=hours_since, buffer_tank_temperature=40.0,
    )
    opt = _LgOpt(ThermalModel(params), ocfg)
    res = opt.optimize(st, ps, o, w, rn, sol, start)
    traj = np.asarray(res.dhw_temp_trajectory, dtype=float)
    req = np.asarray(opt._dhw_requirement, dtype=float)
    n = len(req)
    served = req >= params.dhw_min_temp - 1e-9
    worst = float(np.max((params.dhw_min_temp - traj[1:n + 1])[served]))
    return worst, float(traj.max())


_lg_e2e_worst = {
    f"{h:02d}:00 since {s:.0f} h {p}": _lg_e2e(h, s, p, w)
    for h, s, p, w in (
        (16, 150.0, "summer_typical", "summer_warm"),
        (16, 20.0, "summer_typical", "summer_warm"),
        (12, 20.0, "winter_typical", "winter_cold"),
        (18, 150.0, "winter_typical", "winter_cold"),
    )
}
R.check(
    "no plan leaves a demand window under the usable minimum",
    all(v[0] <= 0.1 for v in _lg_e2e_worst.values()),
    "; ".join(f"{k}: {v[0]:+.2f} °C" for k, v in _lg_e2e_worst.items())
    + " (the whole-tail bound recorded +1.11 on the first of these)",
)
R.check(
    "…and every one of them still honours the 52 °C charge limit or the "
    "60 °C cycle exactly",
    all(v[1] <= 52.001 or abs(v[1] - 60.0) <= 0.05
        for v in _lg_e2e_worst.values()),
    "; ".join(f"{k}: {v[1]:.2f}" for k, v in _lg_e2e_worst.items()),
)
try:
    _LgOpt._repair_dhw_floor = _lg_whole_tail_repair
    _lg_e2e_mut = {
        k: _lg_e2e(h, s, p, w)
        for k, (h, s, p, w) in (
            ("16:00 since 150 h summer", (16, 150.0, "summer_typical",
                                          "summer_warm")),
        )
    }
finally:
    _LgOpt._repair_dhw_floor = _lg_saved_repair
R.check(
    "the whole-tail bound puts the demand-window breach back (mutation "
    "check)",
    all(v[0] > 0.5 for v in _lg_e2e_mut.values()),
    "; ".join(f"{k}: {v[0]:+.2f} °C" for k, v in _lg_e2e_mut.items()),
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — a cycle the tank cannot reach is not parked at the end")

# Reachability is simulated, not estimated. A closed-form lift ÷ rate ignores
# the draws and the standby losses the charge pays on the way, and one fixed
# COP ignores how the pump slows as the tank warms: it called step 91 of 96
# reachable on a 3000 L tank that actually tops out at 52 °C. A cycle placed at
# a step it cannot reach and near the END of the plan is never the current
# action, so no boost is commanded, the tracker never runs, and the "cannot
# reach temperature" notice can never be raised. Unreachable means start now.
def _lg_big(hours, volume, pump, tank=35.0, hours_since=300.0):
    built = _mk_golden(
        hours=hours,
        config_overrides={
            "dhw_tank_volume": volume, "heat_pump_max_power": pump,
            "dhw_setpoint": 52.0,
        },
        param_overrides={"dhw_legionella_temp": 60.0},
        state_overrides={
            "dhw_hours_since_legionella": hours_since, "dhw_temperature": tank,
        },
    )
    res = built["optimizer"].optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], _G_START,
    )
    opt = built["optimizer"]
    n = int(hours * 4)
    # What the tank could do charging flat out for the whole horizon: the
    # honest answer to "is this reachable at all".
    p_run = max(0.1, min(pump * 0.8, pump))
    best = float(np.asarray(opt.model.simulate_dhw_only(
        initial_temp=tank, dhw_power_schedule=np.full(n, p_run),
        outdoor_temps=np.asarray(built["outdoor"], dtype=float)[:n],
        draw_rates=opt.model.dhw_draw_rates(
            (np.arange(n) * 0.25 + _G_START.hour) % 24.0
        ),
        dt_hours=0.25,
    )).max())
    return opt._dhw_legionella_step, n, best, (res.dhw_reasons or [])


for _label, _args in (
    ("6 h, 1500 L, 3 kW", (6, 1500.0, 3.0)),
    ("24 h, 3000 L, 3 kW", (24, 3000.0, 3.0)),
):
    _step, _n, _best, _reasons = _lg_big(*_args)
    R.check(
        f"{_label}: the tank provably cannot reach 60 °C in the horizon",
        _best < 60.0,
        f"flat-out best {_best:.2f} °C",
    )
    R.check(
        f"{_label}: the cycle is commanded now, not parked at the last step",
        _step == 0 and _step != _n - 1,
        f"placed at step {_step} of {_n}",
    )
    R.check(
        f"{_label}: …so the boost is the current action and can be observed",
        bool(_reasons) and _reasons[0] == _LG_REASON,
        f"first step reason {_reasons[0] if _reasons else None!r}",
    )

# A cycle that IS reachable must still be shopped for, not dragged to step 0.
_lg_ok_step, _lg_ok_n, _lg_ok_best, _ = _lg_big(24, 300.0, 6.0)
R.check(
    "a reachable cycle is still placed where the pump can do it, not at 0",
    _lg_ok_best >= 60.0 and _lg_ok_step not in (None, 0),
    f"flat-out best {_lg_ok_best:.2f} °C, placed at step {_lg_ok_step}",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — a commanded cycle is credited only when something saw it")

# With no tank probe it is tempting to write the COMPLETION timestamp for a
# boost nothing has verified. The claim buys no scheduling benefit whatsoever:
# `_dhw_hours_since_legionella` already counts attempts, so an attempt drives
# the countdown from 192 h to 0 identically — and it costs the ability to say
# the cycle is unverified. This integration publishes a plan; the actuation
# may be an automation that never ran.
_lg_blind2 = _lg_coord()
_lg_blind2._config.pop("dhw_temp_entity", None)
_lg_blind_before = _lg_blind2._dhw_hours_since_legionella()
_lg_cycle(_lg_blind2, [None, None])
_lg_blind_after = _lg_blind2._dhw_hours_since_legionella()
R.check(
    "the countdown still resets without a probe — the plan is not wedged",
    _lg_blind_before > 168.0
    and _lg_blind_after is not None
    and _lg_blind_after < 1.0,
    f"{_lg_blind_before:.0f} h before, {_lg_blind_after} h after",
)
R.check(
    "…but it is recorded as an attempt, not as a verified cycle",
    _lg_blind2._dhw_legionella_attempt is not None
    and _lg_blind2._dhw_last_legionella == _G_START - timedelta(days=8),
    f"attempt {_lg_blind2._dhw_legionella_attempt!r}, "
    f"completion {_lg_blind2._dhw_last_legionella!r}",
)
R.check(
    "…and the user is told the cycle cannot be verified",
    any(
        i[1] == "dhw_legionella_unverified"
        for i in getattr(_lg_blind2.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_blind2.hass, 'issues', [])]}",
)
# Mutation value: the completion claim buys nothing. Writing it instead of the
# attempt produces the SAME countdown, which is the whole argument for not
# writing it.
_lg_claim = _lg_coord()
_lg_claim._config.pop("dhw_temp_entity", None)
_lg_claim._dhw_last_legionella = _lg_blind2._dhw_legionella_attempt
R.check(
    "claiming success instead would give an identical countdown "
    "(mutation check)",
    abs((_lg_claim._dhw_hours_since_legionella() or 0.0)
        - (_lg_blind_after or 0.0)) < 0.01,
    f"attempt {_lg_blind_after!r} vs completion "
    f"{_lg_claim._dhw_hours_since_legionella()!r}",
)
# A probe that later observes a real cycle takes the notice down.
_lg_blind2._config["dhw_temp_entity"] = "sensor.tank"
_lg_blind2._current_action = {"dhw_reason": "idle"}
_asyncio.run(_lg_blind2._async_track_dhw_legionella(60.5))
R.check(
    "an observed cycle clears the cannot-verify notice",
    not any(
        i[1] == "dhw_legionella_unverified"
        for i in getattr(_lg_blind2.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_blind2.hass, 'issues', [])]}",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — free disinfection cannot latch the timer either")

# The observer's hold rule credits at `target - 0.5`, held for
# DHW_LEGIONELLA_HOLD_MINUTES. The boost tracker used to return early at
# `target - 1.0`, so a cycle peaking in [59.0, 59.5) was neither credited by
# the observer nor recorded as an attempt: `hours_since` stayed at 192 h for
# ever and the cycle was re-commanded on every single solve.
def _lg_cycle_obs(coord, temps):
    """A boost with the observer running alongside it, as the update does."""
    for temp in temps:
        coord._current_action = {"dhw_reason": _LG_REASON}
        _asyncio.run(coord._async_track_dhw_legionella_cycle(temp))
        _asyncio.run(coord._async_track_dhw_legionella(temp))
    coord._current_action = {"dhw_reason": "idle"}
    _asyncio.run(coord._async_track_dhw_legionella_cycle(temps[-1]))


_lg_gap = _lg_coord(dhw_free_disinfection_enabled=True)
_LG_GAP_PEAK = 59.2
_lg_gap_before = _lg_gap._dhw_hours_since_legionella()
_lg_cycle_obs(_lg_gap, [55.0, 58.0, _LG_GAP_PEAK])
_lg_gap_after = _lg_gap._dhw_hours_since_legionella()
R.check(
    "the peak sits in the gap the old early return covered "
    "(mutation check: any rule that returns on `peak >= target - 1.0` "
    "records nothing here)",
    59.0 <= _LG_GAP_PEAK < 59.5,
    f"peak {_LG_GAP_PEAK} against a 60 °C target",
)
R.check(
    "the observer demonstrably did not credit it under the hold rule",
    _lg_gap._dhw_last_legionella == _G_START - timedelta(days=8),
    f"completion {_lg_gap._dhw_last_legionella!r}",
)
R.check(
    "…and the timer moves anyway, instead of latching at 192 h",
    _lg_gap_before > 168.0 and _lg_gap_after is not None and _lg_gap_after < 1.0,
    f"{_lg_gap_before:.0f} h before, {_lg_gap_after} h after",
)
R.check(
    "…recorded as an attempt with its peak, so the retry is spaced",
    _lg_gap._dhw_legionella_attempt is not None
    and _lg_gap._dhw_legionella_attempt_peak == _LG_GAP_PEAK,
    f"attempt peak {_lg_gap._dhw_legionella_attempt_peak!r}",
)
R.check(
    "…and no 'cannot reach temperature' notice, because it plainly can",
    not any(
        i[1] == "dhw_legionella_unreachable"
        for i in getattr(_lg_gap.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_gap.hass, 'issues', [])]}",
)
# With the flag off the observer credits at 59.0, so nothing is recorded here.
_lg_gap_off = _lg_coord()
_lg_cycle_obs(_lg_gap_off, [_LG_GAP_PEAK])
R.check(
    "with the flag off the same peak is a real completion, not an attempt",
    _lg_gap_off._dhw_last_legionella != _G_START - timedelta(days=8)
    and _lg_gap_off._dhw_legionella_attempt is None,
    f"completion {_lg_gap_off._dhw_last_legionella!r}",
)

# A boost the plan re-commands for ever is closed out and judged, so a tank
# that cannot finish still reports rather than heating without end.
import homeassistant.util.dt as _lg_dt_mod

_lg_stuck = _lg_coord()
_lg_stuck_before = _lg_stuck._dhw_hours_since_legionella()
_lg_real_now = _lg_dt_mod.now
try:
    _lg_t0 = _lg_dt_mod.now()
    for _h, _t in ((0, 50.0), (2, 53.0), (6, 54.0),
                   (DHW_LEGIONELLA_BOOST_MAX_HOURS + 0.1, 54.0)):
        _lg_dt_mod.now = lambda h=_h: _lg_t0 + timedelta(hours=h)
        _lg_stuck._current_action = {"dhw_reason": _LG_REASON}
        _asyncio.run(_lg_stuck._async_track_dhw_legionella_cycle(_t))
finally:
    _lg_dt_mod.now = _lg_real_now
_lg_stuck_after = _lg_stuck._dhw_hours_since_legionella()
R.check(
    "a boost still commanded after the bound is judged rather than waited on",
    _lg_stuck_before > 168.0
    and _lg_stuck_after is not None
    and _lg_stuck_after < 1.0
    and _lg_stuck._dhw_legionella_attempt_peak == 54.0,
    f"{_lg_stuck_before:.0f} h before, {_lg_stuck_after} h after, peak "
    f"{_lg_stuck._dhw_legionella_attempt_peak!r}",
)
R.check(
    "…and the user is told the tank is not reaching temperature",
    any(
        i[1] == "dhw_legionella_unreachable"
        for i in getattr(_lg_stuck.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_stuck.hass, 'issues', [])]}",
)


# ---------------------------------------------------------------------------
R.section("v5.1.10 — the stock defaults are not a Repairs card")

# `dhw_enabled=True` alone gives a 55 °C charge limit and a 60 °C cycle, both
# straight from DEFAULT_*. A WARNING-severity, non-fixable Repairs issue on
# that pair would put a card on every fresh install — one whose own text reads
# "That is allowed and nothing is wrong", which is not what a Repairs card is
# for. A pair the owner actually chose still gets it.
_lg_stock = _Coord(
    _FakeHass(),
    _FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                     "dhw_enabled": True}),
)
R.check(
    "a stock install really is on the default pair",
    _lg_stock._thermal_params.dhw_setpoint == 55.0
    and _lg_stock._thermal_params.dhw_legionella_temp == 60.0
    and _lg_stock._thermal_params.dhw_legionella_enabled,
    f"{_lg_stock._thermal_params.dhw_setpoint}/"
    f"{_lg_stock._thermal_params.dhw_legionella_temp}",
)
_lg_stock._check_dhw_legionella_ceiling()
R.check(
    "…and it raises no Repairs card",
    not any(
        i[1] == "dhw_legionella_above_setpoint"
        for i in getattr(_lg_stock.hass, "issues", [])
    ),
    f"issues {[i[1] for i in getattr(_lg_stock.hass, 'issues', [])]}",
)
# Mutation value: a pair the owner actually edited still gets the card, so
# the check above is not passing because the notice was simply deleted.
_lg_edited = _lg_coord()
_lg_edited._check_dhw_legionella_ceiling()
R.check(
    "a pair the owner edited to differ still gets it (mutation check)",
    any(
        i[1] == "dhw_legionella_above_setpoint"
        for i in getattr(_lg_edited.hass, "issues", [])
    ),
    f"52/60: issues {[i[1] for i in getattr(_lg_edited.hass, 'issues', [])]}",
)
_lg_edited_leg = _lg_coord(dhw_setpoint=55.0, dhw_legionella_temperature=65.0)
_lg_edited_leg._check_dhw_legionella_ceiling()
R.check(
    "…and so does a raised disinfection temperature on the default limit",
    any(
        i[1] == "dhw_legionella_above_setpoint"
        for i in getattr(_lg_edited_leg.hass, "issues", [])
    ),
)


# --- M2: a weather outage is surfaced, never silently papered over ---------
R.section("Weather staleness is surfaced (M2)")

_WX_ENTITY = "weather.home"
_wx_cfg = dict(_LC_DATA)
_wx_cfg["weather_entity"] = _WX_ENTITY
_wx = Coord(_FakeHass(), _FakeEntry(data=_wx_cfg))


async def _wx_call(domain, service, data=None, **kwargs):
    # No handler registered for get_forecasts: the fetch fails exactly as
    # it does against an unresponsive weather integration.
    return None


_wx.hass.services.async_call = _wx_call

_asyncio.run(_wx._fetch_weather_forecast())
R.check(
    "a failed weather fetch latches the outage and marks the forecast stale",
    _wx._weather_outage_cycles == 1
    and _wx._weather_stale_since is not None
    and _wx.weather_stale_hours() is not None
    and _wx.weather_stale_hours() >= 0.0,
    f"cycles {_wx._weather_outage_cycles}, stale since "
    f"{_wx._weather_stale_since}, age {_wx.weather_stale_hours()}",
)

_asyncio.run(_wx._fetch_weather_forecast())
R.check(
    "a second failed cycle counts the outage but keeps one staleness start",
    _wx._weather_outage_cycles == 2 and _wx.weather_stale_hours() is not None,
    f"cycles {_wx._weather_outage_cycles}",
)

# A failing FIRST fetch with a live entity state fabricates the constant
# 48 h trajectory -- and it is stale from birth, disclosed as such.
_wx_fab = Coord(_FakeHass(), _FakeEntry(data=_wx_cfg))


async def _wx_raising_call(domain, service, data=None, **kwargs):
    # The fallback fabrication lives in the except path: the service call
    # itself must blow up, as it does when the weather integration is
    # broken rather than merely empty.
    raise RuntimeError("weather integration broken")


_wx_fab.hass.services.async_call = _wx_raising_call
_wx_fab.hass.states.set(
    _WX_ENTITY,
    FakeState("cold", attributes={"temperature": "-8.0", "wind_speed": "3.0"}),
)
_asyncio.run(_wx_fab._fetch_weather_forecast())
R.check(
    "the fabricated fallback forecast exists and is stale from birth",
    len(_wx_fab._weather_forecast) == 48
    and _wx_fab._weather_stale_since is not None
    and all(
        fc["temperature"] == -8.0 for fc in _wx_fab._weather_forecast
    ),
    f"entries {len(_wx_fab._weather_forecast)}, stale "
    f"{_wx_fab.weather_stale_hours()} h",
)

# Recovery: a good fetch clears the latch and the staleness.
_wx_ok = Coord(_FakeHass(), _FakeEntry(data=_wx_cfg))


async def _wx_good_call(domain, service, data=None, **kwargs):
    return {_WX_ENTITY: {"forecast": [
        {"datetime": "2026-03-28T%02d:00:00Z" % h, "temperature": 1.5,
         "wind_speed": 2.0, "precipitation": 0.0, "solar_irradiance": 10.0}
        for h in range(24)
    ]}}


_wx_ok.hass.services.async_call = _wx_good_call
_asyncio.run(_wx_ok._fetch_weather_forecast())
R.check(
    "a successful fetch clears the outage and the staleness",
    _wx_ok._weather_outage_cycles == 0
    and _wx_ok._weather_stale_since is None
    and _wx_ok.weather_stale_hours() is None
    and len(_wx_ok._weather_forecast) == 24
    and _wx_ok._solar_radiation_forecast[:1] == [10.0],
    f"cycles {_wx_ok._weather_outage_cycles}, stale "
    f"{_wx_ok.weather_stale_hours()}, entries {len(_wx_ok._weather_forecast)}",
)

# D8-02's half: an EMPTY result keeps the previous forecast -- marked
# stale, not silently fresh forever.
_wx_empty = Coord(_FakeHass(), _FakeEntry(data=_wx_cfg))


async def _wx_empty_call(domain, service, data=None, **kwargs):
    return {_WX_ENTITY: {"forecast": []}}


_wx_empty.hass.services.async_call = _wx_empty_call
_wx_empty._weather_forecast = [{"temperature": 2.0}] * 24
_asyncio.run(_wx_empty._fetch_weather_forecast())
R.check(
    "an empty result keeps the previous forecast, marked stale",
    len(_wx_empty._weather_forecast) == 24
    and _wx_empty._weather_stale_since is not None
    and _wx_empty._weather_outage_cycles == 1,
    f"entries {len(_wx_empty._weather_forecast)}, stale since "
    f"{_wx_empty._weather_stale_since}",
)

# D10-17 (#217, Gold `exception-translations`): every user-facing
# ServiceValidationError must carry translation_domain + translation_key and
# placeholders for exactly the values the old English f-string interpolated,
# and strings.json / en.json / sv.json must carry an exceptions section
# covering them. Each of the 13 raise sites is driven with input that reaches
# it -- through hass.services.async_call, which dispatches the real schema to
# the real handler the way Home Assistant does, and for the coordinator's
# site through the climate entity's set_temperature path (climate.py:281) --
# and what is asserted is the raised error's translation payload, not its
# wording. Config-flow step errors are a different channel (the translated
# step-errors dict) and are deliberately not asserted here.
R.section("exception translations (D10-17, #217)")

import json as _et_json  # noqa: E402
import re as _et_re  # noqa: E402

from homeassistant.exceptions import (  # noqa: E402
    HomeAssistantError as _ET_HAE,
    ServiceValidationError as _ET_SVE,
)
from heatpump_optimizer.climate import (  # noqa: E402
    HeatPumpOptimizerClimate as _ET_Climate,
)

#: translation_key -> the placeholder names the old f-string interpolated.
#: A bare ``set()`` means the raise had no interpolation to preserve.
_ET_KEYS = {
    "config_entry_not_found": {"entry_id"},
    "config_entry_not_loaded": {"entry_id"},
    "no_loaded_config_entry": set(),
    "set_thermal_params_dhw_min_no_deadband": {"minimum", "setpoint", "ceiling"},
    "assign_entity_missing": {"entity_id"},
    "assign_entity_wrong_domain": {"entity_id", "domain", "key", "domains"},
    "apply_topology_unsupported": {"layout", "requirement"},
    "apply_schedule_invalid_dhw_windows": {"windows", "error"},
    "apply_schedule_comfort_band_violation": {"violations"},
    "apply_schedule_dhw_min_no_deadband": {"minimum", "setpoint", "ceiling"},
    "manual_plan_invalid_expires_at": {"expires_at"},
    "manual_plan_invalid_slots": {"error"},
    "run_optimization_no_prices": {"entry_ids"},
    "run_optimization_solve_failed": {"entry_ids"},
    "simulate_plan_no_plan": {"entry_ids"},
    "simulate_plan_no_prices": {"entry_ids"},
    "simulate_plan_invalid_windows": {"error", "windows"},
    "simulate_plan_failed": {"error", "entry_ids"},
    "restore_learned_snapshot_no_snapshot": {"entry_ids"},
    "set_thermal_params_invalid_dhw_windows": {"error", "windows"},
    "set_temperature_comfort_band_violation": {"violations"},
}


def _et_call(hass, service, data):
    """Drive one service call; return the HomeAssistantError it raised."""
    try:
        _asyncio.run(hass.services.async_call(_DOMAIN, service, data))
    except _ET_HAE as err:
        return err
    return None


def _et_why(err, key):
    """Why `err` is not a translatable raise of `key` ("" when it is one)."""
    problems = []
    if not isinstance(err, _ET_SVE):
        problems.append(f"raised {type(err).__name__}, not ServiceValidationError")
        return "; ".join(problems)
    ph = getattr(err, "translation_placeholders", None) or {}
    if getattr(err, "translation_domain", None) != _DOMAIN:
        problems.append(
            f"translation_domain={getattr(err, 'translation_domain', None)!r}"
        )
    if getattr(err, "translation_key", None) != key:
        problems.append(
            f"translation_key={getattr(err, 'translation_key', None)!r} want {key!r}"
        )
    if set(ph) != _ET_KEYS[key]:
        problems.append(
            f"placeholders={sorted(ph)} want={sorted(_ET_KEYS[key])}"
        )
    elif any(not isinstance(v, str) or not v for v in ph.values()):
        problems.append(f"placeholder values not non-empty strings: {ph!r}")
    return "; ".join(problems)


def _et_check(name, err, key):
    R.check(name, not _et_why(err, key), _et_why(err, key) or "ok")


# Services registered, one NOT_LOADED entry parked in the manager the way an
# entry that has never been set up (or has been unloaded) sits there: that is
# the state the two entry-id refusals and the nothing-loaded one live in.
_et_idle = FakeHass()
_asyncio.run(_ha_setup_component(_integ, _et_idle))
_et_idle.config_entries.entries.append(FakeEntry(data=_LC_DATA))

_et_check(
    "clear_manual_plan with an unknown entry_id raises a translatable error",
    _et_call(_et_idle, "clear_manual_plan", {"entry_id": "ghost"}),
    "config_entry_not_found",
)
_et_check(
    "clear_manual_plan with a known but unloaded entry_id raises a translatable error",
    _et_call(_et_idle, "clear_manual_plan", {"entry_id": "test_entry"}),
    "config_entry_not_loaded",
)
_et_check(
    "clear_manual_plan with no loaded entry at all raises a translatable error",
    _et_call(_et_idle, "clear_manual_plan", {}),
    "no_loaded_config_entry",
)

# A loaded entry, so the handlers that resolve targets get a coordinator.
_et_hass = FakeHass()
_et_entry = FakeEntry(data=_LC_DATA)
_asyncio.run(_ha_setup_entry(_integ, _et_hass, _et_entry))

_et_check(
    "set_thermal_parameters with a deadband-less hot water minimum raises a translatable error",
    _et_call(_et_hass, "set_thermal_parameters", {"dhw_min_temperature": 51}),
    "set_thermal_params_dhw_min_no_deadband",
)
_et_check(
    "assign_entity with a nonexistent entity raises a translatable error",
    _et_call(
        _et_hass,
        "assign_entity",
        {"key": "outdoor_temp_entity", "entity_id": "sensor.nope"},
    ),
    "assign_entity_missing",
)
_et_hass.states.set("light.lamp", "on")
_et_check(
    "assign_entity with a wrong-domain entity raises a translatable error",
    _et_call(
        _et_hass,
        "assign_entity",
        {"key": "outdoor_temp_entity", "entity_id": "light.lamp"},
    ),
    "assign_entity_wrong_domain",
)
_et_check(
    "apply_topology with a layout this system cannot use raises a translatable error",
    _et_call(_et_hass, "apply_topology", {"layout": "single_tank_valve"}),
    "apply_topology_unsupported",
)
_et_check(
    "apply_schedule with unparseable hot water windows raises a translatable error",
    _et_call(_et_hass, "apply_schedule", {"dhw_windows": "25-99"}),
    "apply_schedule_invalid_dhw_windows",
)
_et_check(
    "apply_schedule that introduces a comfort-band violation raises a translatable error",
    _et_call(
        _et_hass, "apply_schedule", {"day_start_hour": 22, "day_end_hour": 6}
    ),
    "apply_schedule_comfort_band_violation",
)
_et_check(
    "apply_schedule with a deadband-less hot water minimum raises a translatable error",
    _et_call(_et_hass, "apply_schedule", {"dhw_min_temperature": 51}),
    "apply_schedule_dhw_min_no_deadband",
)
_et_check(
    "apply_manual_plan with an unparseable expires_at raises a translatable error",
    _et_call(_et_hass, "apply_manual_plan", {"expires_at": "not-a-datetime"}),
    "manual_plan_invalid_expires_at",
)
_et_check(
    "apply_manual_plan with an invalid slot raises a translatable error",
    _et_call(
        _et_hass,
        "apply_manual_plan",
        {
            "expires_at": "2031-01-01T00:00:00",
            "space_slots": [
                {
                    "start": "2030-06-01T10:00:00",
                    "end": "2030-06-01T09:00:00",
                }
            ],
        },
    ),
    "manual_plan_invalid_slots",
)

# The thirteenth site is the coordinator's, reached the way a user reaches
# it: the thermostat's set_temperature (climate.py:281), which refuses a
# target outside the comfort band (v5.1.7).
_et_coord = Coord(FakeHass(), FakeEntry(data=_LC_DATA))
_et_climate = _ET_Climate(_et_coord, FakeEntry(data=_LC_DATA))
try:
    _asyncio.run(_et_climate.async_set_temperature(temperature=30.0))
    _et_err = None
except _ET_HAE as err:
    _et_err = err
_et_check(
    "climate.set_temperature outside the comfort band raises a translatable error",
    _et_err,
    "set_temperature_comfort_band_violation",
)

# The translations themselves: same key set in all three files, each message
# naming exactly the placeholders its raise site passes, and strings.json
# staying parity-identical with translations/en.json (hassfest).
_ET_FILES = {}
for _et_label, _et_path in (
    ("strings", "custom_components/heatpump_optimizer/strings.json"),
    ("en", "custom_components/heatpump_optimizer/translations/en.json"),
    ("sv", "custom_components/heatpump_optimizer/translations/sv.json"),
):
    with open(_et_path, encoding="utf-8") as _et_fh:
        _ET_FILES[_et_label] = _et_json.load(_et_fh).get("exceptions", {})

R.check(
    "every raised exception key exists in strings.json, en.json and sv.json",
    set(_ET_KEYS)
    == set(_ET_FILES["strings"])
    == set(_ET_FILES["en"])
    == set(_ET_FILES["sv"]),
    f"strings={sorted(_ET_FILES['strings'])} en={sorted(_ET_FILES['en'])} "
    f"sv={sorted(_ET_FILES['sv'])}",
)


def _et_names(message):
    return set(_et_re.findall(r"\{([a-z_]+)\}", message))


_et_bad = []
for _et_key, _et_want in _ET_KEYS.items():
    for _et_label in ("strings", "en", "sv"):
        _et_msg = _ET_FILES[_et_label].get(_et_key, {}).get("message", "")
        if _et_names(_et_msg) != _et_want:
            _et_bad.append(
                f"{_et_label}:{_et_key} names {sorted(_et_names(_et_msg))} "
                f"want {sorted(_et_want)}"
            )
R.check(
    "each exception message names exactly the placeholders its raise passes",
    not _et_bad,
    "; ".join(_et_bad),
)
R.check(
    "the exceptions section stays parity-identical between strings.json and en.json",
    _ET_FILES["strings"] == _ET_FILES["en"],
    "hassfest requires the two files to match",
)


# ===========================================================================
# #226: the verified dead symbols stay deleted
# ===========================================================================
# Reachability was re-verified before each deletion (full-repo grep plus a
# dynamic-use sweep: string keys, getattr, services.yaml, strings.json,
# translations/, www/). This section pins the verdicts so a symbol cannot
# quietly come back without its production caller. The hasattr checks import
# the production modules themselves -- a test that only re-derived the
# verdict would pin nothing.
R.section("Dead symbols stay deleted (#226)")

from heatpump_optimizer import tariff as tariff_mod  # noqa: E402

R.check(
    "the ten #226 symbols no longer exist in production",
    not hasattr(ComfortLearner, "set_configured")
    and not hasattr(Coord, "optimization_result")
    and not hasattr(Coord, "current_state")
    and not hasattr(Coord, "_prepare_forecast_data")
    and not hasattr(DrawStats, "ready_energy")
    and not hasattr(pv, "piecewise_cost")
    and not hasattr(tariff_mod, "peak_penalty")
    and not hasattr(_topo, "match_layout")
    and not hasattr(narrative_mod, "LANGUAGES")
    and not hasattr(pump_mode, "MODE_KEYS"),
    "each of these had zero production references (tests do not count); "
    "if one is needed again, re-add it together with the production caller "
    "that needs it",
)

# The two grid_fee helpers PR-0's name-only screen ALSO flagged, which are
# alive: the coordinator imports them under aliased names
# (``as grid_fee_max_abs_component`` / ``as grid_fee_min_component``), so a
# scan keyed on the bare def name misses the reference. They stay.
R.check(
    "grid_fee.max_abs_component and grid_fee.min_component stay (aliased imports)",
    callable(_gf.max_abs_component) and callable(_gf.min_component),
    "coordinator.py imports them as grid_fee_* and calls them in the fee "
    "issue checks; a name-only deadness screen cannot see an asname import",
)

# The four CONF keys look dead to the same name-only scan but are read
# dynamically: ThermalParameters.from_config resolves them through
# ``getattr(const, f"CONF_{conf}")`` over its parameter table. The sentinel
# proves both halves -- the attribute resolves AND from_config actually
# reads it, because a distinctive value set through the resolved key must
# arrive on the parameter (it differs from every default).
_conf4 = {
    "CONF_BUFFER_TANK_LOSS": ("buffer_tank_heat_loss", 0.75),  # default 0.01
    "CONF_SOLAR_UPPER_FRACTION": ("solar_upper_fraction", 0.65),  # default 0.4
    "CONF_HOUSE_HEAT_LOSS_SCALE": ("house_heat_loss_scale", 1.5),  # default 1.0
    "CONF_LOWER_FLOOR_LOSS_RATIO": ("lower_floor_loss_ratio", 0.42),  # dflt 1.0
}
_conf4_params = ThermalParameters.from_config(
    {getattr(hp_const, _k): _v for _k, (_, _v) in _conf4.items()}
)
R.check(
    "the four getattr-read CONF keys stay live in from_config",
    all(
        getattr(_conf4_params, _attr) == _v
        for _k, (_attr, _v) in _conf4.items()
    ),
    "thermal_model.from_config reads these via getattr(const, f'CONF_...'); "
    "deleting one crashes from_config at import of any config entry",
)



# --- #341: golden.py reads GOLDEN_MODE and GOLDEN_REF itself -----------------
#
# The defect: tests/run.sh read both variables; tests/golden.py read neither.
# Run directly it therefore always made the strict, bit-exact comparison
# against fixtures recorded on another machine, and reported a FIXED 34 of 55
# scenarios changed on a clean checkout of main -- measured on this box at
# a5b5fc2, and again in a separate clean worktree of the same commit, with the
# identical scenario list both times. A noise floor that big is where a real
# diff hides; `config_flow` (the stale fixture of #326) is one of the 34.
#
# These pin the resolution itself, not the comparison: resolve_mode is pure,
# so the whole decision table is checkable without capturing a single tree.
from golden import (  # noqa: E402
    DEFAULT_MODE as _GDEF_MODE,
    DEFAULT_REF as _GDEF_REF,
    drift_command as _g_drift_cmd,
    resolve_mode as _g_resolve,
)

_g_unset = _g_resolve({})
R.check(
    "an unset GOLDEN_MODE gets the drift comparison, not the strict one",
    _g_unset.mode == "drift" and not _g_unset.error,
    f"golden.py run with no environment chose {_g_unset.mode!r}; strict on a "
    "machine whose BLAS differs reports 34 of 55 changed on a clean tree, so "
    "an accidental strict run is a gate that always fires",
)
R.check(
    "and compares against the fork point when no ref was named",
    _g_unset.ref == _GDEF_REF == "origin/main",
    f"defaulted to {_g_unset.ref!r}",
)
R.check(
    "the default is stated in one place both this file and golden.py read",
    _GDEF_MODE == "drift",
    f"golden.DEFAULT_MODE is {_GDEF_MODE!r}",
)

# The half that guards the gate rather than the developer. tests/run.sh's
# strict lane is the ONLY place the committed fixtures are compared at all --
# CI sets GOLDEN_MODE=drift, where run.sh skips golden.py entirely -- so if a
# GOLDEN_MODE the suite set as strict arrived here as drift, that comparison
# would vanish from the project.
_g_strict = _g_resolve({"GOLDEN_MODE": "strict"})
R.check(
    "GOLDEN_MODE=strict still gets the strict comparison, ref or no ref",
    _g_strict.mode == "strict" and not _g_strict.error,
    f"run.sh's strict lane would have got {_g_strict.mode!r}",
)
# run.sh branches on an exact `= "drift"` and treats everything else as
# strict. golden.py has to agree, or `GOLDEN_MODE=stict ./tests/run.sh` runs
# the strict LANE around a drift comparison and reports neither.
R.check(
    "a misspelt mode falls to strict here exactly as it does in run.sh",
    _g_resolve({"GOLDEN_MODE": "stict"}).mode == "strict"
    and _g_resolve({"GOLDEN_MODE": "Drift"}).mode == "strict",
    "an unrecognised GOLDEN_MODE must land on the stricter comparison, and on "
    "the same one run.sh's `[ \"$GOLDEN_MODE\" = drift ]` lands on",
)

_g_drift = _g_resolve({"GOLDEN_MODE": "drift", "GOLDEN_REF": "deadbee"})
R.check(
    "GOLDEN_MODE=drift takes the named ref verbatim",
    _g_drift.mode == "drift" and _g_drift.ref == "deadbee",
    f"got mode={_g_drift.mode!r} ref={_g_drift.ref!r}",
)
R.check(
    "and delegates to the same script and arguments run.sh's drift lane uses",
    _g_drift_cmd("deadbee")[1:] == ["tests/env_drift.py", "--all", "deadbee"],
    f"drift_command built {_g_drift_cmd('deadbee')[1:]}; run.sh's drift lane "
    "runs `$PYTHON tests/env_drift.py --all $GOLDEN_REF`, and a direct run "
    "that ran anything else would answer a different question",
)

# --record and --only name committed fixtures, which only strict reads. By
# default they select strict -- this is the path tests/derive_closures.sh
# records golden.py on (`--only __no_such_scenario__`), and if that turned
# into a drift capture the closures job would record the wrong closure and
# spend an hour doing it.
R.check(
    "--only with no GOLDEN_MODE set selects strict, as derive_closures needs",
    _g_resolve({}, only="__no_such_scenario__").mode == "strict"
    and not _g_resolve({}, only="__no_such_scenario__").error,
    "tests/derive_closures.sh records golden.py with --only and sets no "
    "GOLDEN_MODE; a drift default there would re-record the wrong closure",
)
R.check(
    "--record with no GOLDEN_MODE set selects strict too",
    _g_resolve({}, record=True).mode == "strict"
    and not _g_resolve({}, record=True).error,
    "re-recording fixtures is a strict-mode act; drift never writes one",
)
# Asked for explicitly, the same combination is a contradiction. Saying so is
# the point: silently dropping --only would re-record 55 fixtures when one was
# asked for.
_g_conflict = _g_resolve({"GOLDEN_MODE": "drift"}, record=True)
R.check(
    "--record against an explicit GOLDEN_MODE=drift is refused, not guessed",
    bool(_g_conflict.error) and "--record" in _g_conflict.error,
    f"error was {_g_conflict.error!r}",
)

# The other half of #341, in tests/run.sh: the suite resolves both defaults
# into shell variables, and golden.py is a child process. Unexported, a plain
# `./tests/run.sh` would choose strict here and hand golden.py an environment
# in which nobody chose anything -- and golden.py's own default is drift.
import re as _g341_re  # noqa: E402

_g_runsh = _Path("tests/run.sh").read_text()
R.check(
    "tests/run.sh exports GOLDEN_MODE and GOLDEN_REF to the scripts it runs",
    _g341_re.search(r"^export .*\bGOLDEN_MODE\b", _g_runsh, _g341_re.M) is not None
    and _g341_re.search(r"^export .*\bGOLDEN_REF\b", _g_runsh, _g341_re.M) is not None,
    "both are resolved with `${VAR:-default}` and read by tests/golden.py in "
    "a child process; without the export the suite's decision never arrives",
)


# The two lines above that no pure check can see: main() must ACT on what
# resolve_mode decided, and run_drift must actually run what drift_command
# names. Both matter more than usual here, because CI never executes this
# script's entry point at all -- `fast` and `slow` set GOLDEN_MODE=drift and
# run.sh skips golden.py outright in that mode -- so no CI lane would notice
# either line rotting. Pinned by substitution rather than by spending two
# minutes capturing two trees.
import contextlib as _g341ctx  # noqa: E402
import golden as _g341mod  # noqa: E402
import io as _g341io  # noqa: E402

# Both calls below print the banner and the command they would run. That is
# right when a human runs golden.py and noise in the middle of a check list,
# so it goes to a buffer -- the checks assert on what was CALLED, not on what
# was said about it.
_g341_quiet = _g341io.StringIO()

_g341_dispatched = []
_g341_real_run_drift = _g341mod.run_drift
_g341_saved_argv = sys.argv
_g341_saved_env = {k: _os.environ.get(k) for k in ("GOLDEN_MODE", "GOLDEN_REF")}
try:
    _g341mod.run_drift = lambda ref: _g341_dispatched.append(ref) or 0
    sys.argv = ["tests/golden.py"]
    _os.environ["GOLDEN_MODE"] = "drift"
    _os.environ["GOLDEN_REF"] = "deadbee"
    with _g341ctx.redirect_stdout(_g341_quiet):
        _g341_main_rc = _g341mod.main()
finally:
    _g341mod.run_drift = _g341_real_run_drift
    sys.argv = _g341_saved_argv
    for _k, _v in _g341_saved_env.items():
        if _v is None:
            _os.environ.pop(_k, None)
        else:
            _os.environ[_k] = _v

R.check(
    "golden.py's entry point hands a drift run to the drift comparison",
    _g341_dispatched == ["deadbee"] and _g341_main_rc == 0,
    f"main() dispatched {_g341_dispatched} and returned {_g341_main_rc}; a "
    "main() that resolves the mode and then checks fixtures anyway is the "
    "#341 bug with an extra print in front of it",
)


class _G341Completed:
    """Stands in for subprocess.CompletedProcess with a status nobody guesses."""

    returncode = 7


_g341_ran = {}


def _g341_fake_run(cmd, cwd=None, **kwargs):
    _g341_ran["cmd"] = list(cmd)
    _g341_ran["cwd"] = str(cwd)
    return _G341Completed()


_g341_saved_run = _g341mod.subprocess.run
try:
    _g341mod.subprocess.run = _g341_fake_run
    with _g341ctx.redirect_stdout(_g341_quiet):
        _g341_drift_rc = _g341_real_run_drift("deadbee")
finally:
    _g341mod.subprocess.run = _g341_saved_run

R.check(
    "run_drift runs exactly the command drift_command names, from the repo root",
    _g341_ran.get("cmd") == _g341mod.drift_command("deadbee")
    and _g341_ran.get("cwd") == str(_Path(_g341mod.__file__).resolve().parent.parent),
    f"ran {_g341_ran.get('cmd')} in {_g341_ran.get('cwd')}; golden.py resolves "
    "relative paths against the repo root, so a drift run started anywhere "
    "else finds neither tests/env_drift.py nor the fixtures",
)
R.check(
    "and reports the comparison's own exit status, not its own opinion of it",
    _g341_drift_rc == 7,
    f"run_drift returned {_g341_drift_rc} for a child that exited 7 -- a drift "
    "run that swallows the status is a gate that cannot fail",
)


R.section("#369/#370 — the duplication window can fire, and --record refuses a laundered regression")

# These drive tests/structure.py's OWN symbols, not a re-implementation of
# them: the window scan and the re-record guard are the production code here,
# and a test that rebuilt either would pin nothing (tests/README.md).
import contextlib as _hpo_g_ctx
import io as _hpo_g_io
import json as _hpo_g_json
import tempfile as _hpo_g_tmp

import structure as _hpo_st

_hpo_g_dup = getattr(_hpo_st, "duplicate_runs", None)
_hpo_g_reg = getattr(_hpo_st, "regression_rows", None)


def _hpo_g_sample(shared: int) -> dict:
    """Two functions of one module sharing exactly ``shared`` normalized lines.

    The shape ``duplicate_runs`` consumes: fid -> [(segment, text)], which is
    what ``measure()`` builds per module once blanks, comment-only lines and
    nested def spans are stripped.
    """
    body = [(0, f"shared_statement_{i} = compute({i})") for i in range(shared)]
    return {
        ("dup.py", "left", 10): [(0, "only_left = 1"), *body, (0, "return only_left")],
        ("dup.py", "right", 90): [(0, "only_right = 2"), *body, (0, "return only_right")],
    }


def _hpo_g_runs(sample: dict, window: int):
    if _hpo_g_dup is None:
        return "duplicate_runs is missing from tests/structure.py"
    return _hpo_g_dup(sample, window)


# ---- #369 ---------------------------------------------------------------
# DUP_BLOCK_LINES was 30 against a longest real duplicated run of 19, so
# duplication_blocks reported 0 because nothing in the tree could reach the
# window -- not because the tree was clean. Measured on this fork at
# a2c4982: window 30 -> 0, 25 -> 0, 20 -> 0, 15 -> 4, 12 -> 6, 10 -> 13.
# Both ends of the window are pinned here on a constructed duplication, so
# reverting the constant fails instead of silently going quiet again.
_hpo_g_s12 = _hpo_g_sample(12)
R.check(
    "a 12-line duplication is invisible to the old 30-line window (#369)",
    _hpo_g_runs(_hpo_g_s12, 30) == [],
    f"duplicate_runs(sample, 30) = {_hpo_g_runs(_hpo_g_s12, 30)}",
)
R.check(
    "and invisible at 20 too -- which is why duplication_blocks could only read 0",
    _hpo_g_runs(_hpo_g_s12, 20) == [],
    f"duplicate_runs(sample, 20) = {_hpo_g_runs(_hpo_g_s12, 20)}",
)
_hpo_g_caught = _hpo_g_runs(_hpo_g_s12, _hpo_st.DUP_BLOCK_LINES)
R.check(
    "the shipped window catches it: one row per side, 12 normalized lines each",
    isinstance(_hpo_g_caught, list)
    and len(_hpo_g_caught) == 2
    and sorted(row[1] for row in _hpo_g_caught) == ["left", "right"]
    and [row[4] for row in _hpo_g_caught] == [12, 12],
    f"duplicate_runs(sample, DUP_BLOCK_LINES={_hpo_st.DUP_BLOCK_LINES}) = {_hpo_g_caught}",
)
R.check(
    "DUP_BLOCK_LINES is 10 -- the tree measures 0 at 20 and 13 at 10 (#369)",
    _hpo_st.DUP_BLOCK_LINES == 10,
    f"DUP_BLOCK_LINES = {_hpo_st.DUP_BLOCK_LINES}; the longest duplicated run in "
    "the integration is 19 normalized lines, so any window above it leaves the "
    "metric incapable of firing at all",
)
R.check(
    "the window is still a floor: a 9-line shared run is not reported at 10",
    _hpo_g_runs(_hpo_g_sample(9), _hpo_st.DUP_BLOCK_LINES) == [],
    f"duplicate_runs(9-line sample, {_hpo_st.DUP_BLOCK_LINES}) = "
    f"{_hpo_g_runs(_hpo_g_sample(9), _hpo_st.DUP_BLOCK_LINES)}",
)

# ---- #370 ---------------------------------------------------------------
# record_budgets() never read the table it replaced, so --record could not
# tell locking in a gain from laundering a regression. The direction is
# uniformly `new > old` -- ratchet() compares all 22 metrics the same way, so
# there is no per-metric direction table to maintain -- and FRACTION_METRICS
# is skipped: a tolerance metric inside its band has nothing to record, and
# outside it a failure is a decision, not bookkeeping.
_hpo_g_old = {
    "coordinator_loc": 10394,
    "methods_over_150": 23,
    "duplication_blocks": 13,
    "cross_seam_fraction": 0.4289,
    "recorded_at": "4b6e076517431bd8658530c5ac751f2b7ddb7ef6",
}
_hpo_g_base = {k: v for k, v in _hpo_g_old.items() if k != "recorded_at"}
_hpo_g_worse = dict(_hpo_g_base, coordinator_loc=10420, methods_over_150=22)
_hpo_g_better = dict(_hpo_g_base, coordinator_loc=10380, cross_seam_fraction=0.4301)
_hpo_g_frac = dict(_hpo_g_base, cross_seam_fraction=0.4301)


def _hpo_g_rows(old: dict, new: dict):
    if _hpo_g_reg is None:
        return "regression_rows is missing from tests/structure.py"
    return _hpo_g_reg(old, new)


R.check(
    "regression_rows names the metric that moved the wrong way, old and new (#370)",
    _hpo_g_rows(_hpo_g_old, _hpo_g_worse) == [("coordinator_loc", 10394, 10420)],
    f"regression_rows = {_hpo_g_rows(_hpo_g_old, _hpo_g_worse)}; methods_over_150 "
    "improved in the same table and must not be named -- the whole defect is a "
    "re-record that carries one row along with another",
)
R.check(
    "cross_seam_fraction moving up is NOT a regression row: FRACTION_METRICS is skipped",
    _hpo_g_rows(_hpo_g_old, _hpo_g_frac) == [],
    f"regression_rows = {_hpo_g_rows(_hpo_g_old, _hpo_g_frac)}; FRACTION_METRICS = "
    f"{sorted(getattr(_hpo_st, 'FRACTION_METRICS', ()))}",
)


def _hpo_g_record(new_metrics: dict, **kwargs):
    """record_budgets against a throwaway table. Returns (rc, table-after)."""
    saved = _hpo_st.BUDGET_FILE
    with _hpo_g_tmp.TemporaryDirectory() as tmp:
        path = _Path(tmp) / "structure_budgets.json"
        path.write_text(_hpo_g_json.dumps(_hpo_g_old, indent=1, sort_keys=True) + "\n")
        _hpo_st.BUDGET_FILE = path
        try:
            with _hpo_g_ctx.redirect_stdout(_hpo_g_io.StringIO()):
                rc = _hpo_st.record_budgets({"metrics": dict(new_metrics)}, **kwargs)
        except TypeError as exc:
            return f"TypeError: {exc}", {}
        finally:
            _hpo_st.BUDGET_FILE = saved
        return rc, _hpo_g_json.loads(path.read_text())


_hpo_g_refused = _hpo_g_record(_hpo_g_worse)
R.check(
    "--record REFUSES a worsened metric by default and leaves the table untouched",
    _hpo_g_refused == (1, _hpo_g_old),
    f"record_budgets returned {_hpo_g_refused[0]!r}; table now {_hpo_g_refused[1]!r}. "
    "#350 makes re-recording routine and gate-demanded, and a regression "
    "laundered by a gate that ASKED for the re-record carries the gate's authority.",
)
_hpo_g_allowed = _hpo_g_record(
    _hpo_g_worse, allow_regression="the dhw seam extraction trades 26 lines for the cut"
)
R.check(
    "an explicit --allow-regression reason lets it through and writes the new value",
    _hpo_g_allowed[0] == 0
    and _hpo_g_allowed[1].get("coordinator_loc") == 10420
    and _hpo_g_allowed[1].get("methods_over_150") == 22,
    f"record_budgets returned {_hpo_g_allowed[0]!r}; table now {_hpo_g_allowed[1]!r}",
)
_hpo_g_blank = _hpo_g_record(_hpo_g_worse, allow_regression="   ")
R.check(
    "a blank reason is refused, so the flag cannot decay into pasted boilerplate",
    _hpo_g_blank == (1, _hpo_g_old),
    f"record_budgets returned {_hpo_g_blank[0]!r}; table now {_hpo_g_blank[1]!r}",
)
_hpo_g_tight = _hpo_g_record(_hpo_g_better)
R.check(
    "a pure tightening still records with no flag -- that is the point of the exercise",
    _hpo_g_tight[0] == 0 and _hpo_g_tight[1].get("coordinator_loc") == 10380,
    f"record_budgets returned {_hpo_g_tight[0]!r}; table now {_hpo_g_tight[1]!r}",
)
R.check(
    "and the path that proceeds still stamps a resolvable recorded_at (#363)",
    isinstance(_hpo_g_tight[1].get("recorded_at"), str)
    and len(_hpo_g_tight[1].get("recorded_at", "")) == 40,
    f"recorded_at = {_hpo_g_tight[1].get('recorded_at')!r}",
)
R.check(
    "cross_seam_fraction is carried forward, never re-recorded (#370)",
    _hpo_g_tight[1].get("cross_seam_fraction") == 0.4289
    and _hpo_g_record(_hpo_g_frac)[1].get("cross_seam_fraction") == 0.4289,
    "a tolerance metric passing inside its band has nothing to record and failing "
    "outside it is a decision, so re-recording one can only ever loosen the band. "
    f"Got {_hpo_g_tight[1].get('cross_seam_fraction')!r} and "
    f"{_hpo_g_record(_hpo_g_frac)[1].get('cross_seam_fraction')!r}",
)
R.check(
    "--allow-regression is a flag that demands a reason, not a bare switch",
    any(
        isinstance(_hpo_n, _hpo_ast.Call)
        and getattr(_hpo_n.func, "attr", "") == "add_argument"
        and any(
            isinstance(_hpo_a, _hpo_ast.Constant) and _hpo_a.value == "--allow-regression"
            for _hpo_a in _hpo_n.args
        )
        and not any(_hpo_k.arg == "action" for _hpo_k in _hpo_n.keywords)
        and any(
            _hpo_k.arg == "metavar" or _hpo_k.arg == "default" for _hpo_k in _hpo_n.keywords
        )
        for _hpo_n in _hpo_ast.walk(_hpo_ast.parse(_Path("tests/structure.py").read_text()))
    ),
    "main() must expose --allow-regression=\"<reason>\" as a value-taking option; "
    "store_true would make the reason unrecordable",
)

R.section("#350/#374 — an improvement must be recorded, and the worst method has a budget")

# Same rule as the section above: these drive tests/structure.py's own
# symbols. `structure as _hpo_st` is already imported there.
_hpo_h_never = getattr(_hpo_st, "NEVER_RERECORDED", None)
_hpo_h_imp = getattr(_hpo_st, "improvement_rows", None)
_hpo_h_report = getattr(_hpo_st, "report_improvements", None)

# ---- #350 ---------------------------------------------------------------
# Headroom was advisory and had a 0-for-6 record: #338 opened five metrics of
# slack, the note printed on six consecutive commits including a release
# stamp, and nobody ever locked it in. For everything in that gap the gate is
# not loose, it is absent -- five dead symbols could have been reintroduced
# and #338's own gate would have said nothing.
_hpo_h_budgets = {
    "coordinator_loc": 10394,
    "max_class_loc": 10394,
    "internal_call_edges": 379,
    "methods_over_150": 23,
    "cross_seam_fraction": 0.4289,
    "recorded_at": "4b6e076517431bd8658530c5ac751f2b7ddb7ef6",
}
_hpo_h_better = {
    "coordinator_loc": 10365,
    "max_class_loc": 10365,
    "internal_call_edges": 372,
    "methods_over_150": 23,
    "cross_seam_fraction": 0.4220,
}
_hpo_h_worse = dict(_hpo_h_better, methods_over_150=24)
_hpo_h_level = {k: v for k, v in _hpo_h_budgets.items() if k != "recorded_at"}


def _hpo_h_rows(budgets: dict, metrics: dict):
    if _hpo_h_imp is None:
        return "improvement_rows is missing from tests/structure.py"
    return _hpo_h_imp(budgets, metrics)


R.check(
    "improvement_rows names every metric with headroom, budget and measured (#350)",
    _hpo_h_rows(_hpo_h_budgets, _hpo_h_better)
    == [
        ("coordinator_loc", 10394, 10365),
        ("internal_call_edges", 379, 372),
        ("max_class_loc", 10394, 10365),
    ],
    f"improvement_rows = {_hpo_h_rows(_hpo_h_budgets, _hpo_h_better)}; the advisory "
    "note it replaces named the metrics too and was ignored six times running -- "
    "naming them is not the fix, failing on them is, and the failure has to say "
    "which ones so the author can write down what they earned",
)
R.check(
    "and is the exact mirror of regression_rows: a worsening is not an improvement",
    isinstance(_hpo_h_rows(_hpo_h_budgets, _hpo_h_worse), list)
    and _hpo_h_rows(_hpo_h_budgets, _hpo_h_worse)
    == _hpo_h_rows(_hpo_h_budgets, _hpo_h_better)
    and _hpo_g_rows(_hpo_h_budgets, _hpo_h_worse) == [("methods_over_150", 23, 24)],
    f"improvement_rows = {_hpo_h_rows(_hpo_h_budgets, _hpo_h_worse)}, "
    f"regression_rows = {_hpo_g_rows(_hpo_h_budgets, _hpo_h_worse)}; a metric that "
    "moved the wrong way must appear in exactly one of the two",
)
R.check(
    "a level metric is neither an improvement nor a regression",
    isinstance(_hpo_h_rows(_hpo_h_budgets, _hpo_h_level), list)
    and _hpo_h_rows(_hpo_h_budgets, _hpo_h_level) == []
    and _hpo_g_rows(_hpo_h_budgets, _hpo_h_level) == [],
    f"improvement_rows = {_hpo_h_rows(_hpo_h_budgets, _hpo_h_level)}, "
    f"regression_rows = {_hpo_g_rows(_hpo_h_budgets, _hpo_h_level)}",
)

# The category #370's fourth comment asked for. Without it, `tvofi-claude-09`'s
# two correct decisions to decline re-recording cross_seam_fraction become two
# gate violations the moment re-recording is mandatory.
R.check(
    "NEVER_RERECORDED exists and holds cross_seam_fraction (#350, #370)",
    isinstance(_hpo_h_never, (set, frozenset)) and "cross_seam_fraction" in _hpo_h_never,
    f"NEVER_RERECORDED = {_hpo_h_never!r}; a tolerance metric passing inside its "
    "band has nothing to record and failing outside it is a decision, so there is "
    "no third case and a re-record could only ever loosen the band",
)
R.check(
    "improvement_rows skips it, so declining to re-record it can never be a failure",
    _hpo_h_rows(
        {"cross_seam_fraction": 0.4289, "coordinator_loc": 10394},
        {"cross_seam_fraction": 0.4220, "coordinator_loc": 10394},
    )
    == [],
    "cross_seam_fraction reads 0.4220 against a recorded 0.4289 on this fork, which "
    "is headroom by any comparison; demanding a re-record there would loosen the "
    "0.4339 ceiling for nothing. Got "
    f"{_hpo_h_rows({'cross_seam_fraction': 0.4289, 'coordinator_loc': 10394}, {'cross_seam_fraction': 0.4220, 'coordinator_loc': 10394})}",
)
R.check(
    "every tolerance metric is in the category -- a ratchet on a band is a contradiction",
    _hpo_h_never is not None
    and set(getattr(_hpo_st, "FRACTION_METRICS", set())) <= set(_hpo_h_never),
    f"FRACTION_METRICS = {sorted(getattr(_hpo_st, 'FRACTION_METRICS', ()))}, "
    f"NEVER_RERECORDED = {sorted(_hpo_h_never or ())}; a metric with both a "
    "tolerance band and a re-record demand is carrying two mechanisms for one job "
    "and they disagree",
)


def _hpo_h_ratchet(budgets: dict, metrics: dict):
    """ratchet() against a throwaway table. Returns (rc, captured stdout).

    ``recorded_at_unreachable`` is stubbed to None for the duration: whether a
    recorded SHA resolves is #361/#363's concern, pinned separately above, and
    leaving it live would make these checks depend on the clone depth of
    whatever runner they execute on rather than on the headroom decision.
    """
    saved_file = _hpo_st.BUDGET_FILE
    saved_check = _hpo_st.recorded_at_unreachable
    out = _hpo_g_io.StringIO()
    with _hpo_g_tmp.TemporaryDirectory() as tmp:
        path = _Path(tmp) / "structure_budgets.json"
        path.write_text(_hpo_g_json.dumps(budgets, indent=1, sort_keys=True) + "\n")
        _hpo_st.BUDGET_FILE = path
        _hpo_st.recorded_at_unreachable = lambda recorded: None
        try:
            with _hpo_g_ctx.redirect_stdout(out):
                rc = _hpo_st.ratchet(
                    {
                        "metrics": dict(metrics),
                        "tables": {"top_is_coordinator": True, "cross_edges": 0},
                    }
                )
        finally:
            _hpo_st.BUDGET_FILE = saved_file
            _hpo_st.recorded_at_unreachable = saved_check
    return rc, out.getvalue()


_hpo_h_run_better = _hpo_h_ratchet(_hpo_h_budgets, _hpo_h_better)
R.check(
    "the ratchet FAILS on an improvement instead of printing a note (#350)",
    _hpo_h_run_better[0] == 1,
    f"ratchet returned {_hpo_h_run_better[0]!r} for a tree three metrics better than "
    "its budgets. A failing gate would have fired on 2 of the last 18 commits on "
    f"main (~11%). Output:\n{_hpo_h_run_better[1]}",
)
_hpo_h_block = (
    _hpo_h_run_better[1].split("IMPROVED", 1)[-1]
    if "IMPROVED" in _hpo_h_run_better[1]
    else ""
)
R.check(
    "and the improvement block names all three, so the author knows what to write down",
    all(
        k in _hpo_h_block
        for k in ("coordinator_loc", "internal_call_edges", "max_class_loc")
    )
    and "cross_seam_fraction" not in _hpo_h_block,
    f"the block after the IMPROVED header was:\n{_hpo_h_block}",
)
R.check(
    "and prints the exact runnable command, not just the numbers",
    "python3 tests/structure.py --record" in _hpo_h_run_better[1],
    "an improving PR must be able to re-record in the same commit; a gate that "
    "demands a re-record without naming the command is unsatisfiable by anyone "
    f"who has not read the source. Output:\n{_hpo_h_run_better[1]}",
)
R.check(
    "and frames it as 'you made this better, write it down', not as a breach",
    "BREACHED" not in _hpo_h_run_better[1]
    and "IMPROVED" in _hpo_h_run_better[1],
    "a gate that scolds a PR for improving the tree will be worked around, and "
    f"then it protects nothing (#350). Output:\n{_hpo_h_run_better[1]}",
)
_hpo_h_run_level = _hpo_h_ratchet(_hpo_h_budgets, _hpo_h_level)
R.check(
    "a zero-headroom tree still passes silently -- eleven of the last eighteen commits",
    _hpo_h_run_level[0] == 0 and "STRUCTURE RATCHET PASSED" in _hpo_h_run_level[1],
    f"ratchet returned {_hpo_h_run_level[0]!r}. This must add a failure mode, not "
    f"replace one. Output:\n{_hpo_h_run_level[1]}",
)
_hpo_h_run_worse = _hpo_h_ratchet(_hpo_h_budgets, _hpo_h_worse)
R.check(
    "a worsening still fails, and still as a breach",
    _hpo_h_run_worse[0] == 1
    and "FAIL methods_over_150 24 > 23" in _hpo_h_run_worse[1]
    and "BREACHED" in _hpo_h_run_worse[1],
    f"ratchet returned {_hpo_h_run_worse[0]!r}. Output:\n{_hpo_h_run_worse[1]}",
)
_hpo_h_run_frac = _hpo_h_ratchet(
    {"cross_seam_fraction": 0.4289, "coordinator_loc": 10394,
     "recorded_at": _hpo_h_budgets["recorded_at"]},
    {"cross_seam_fraction": 0.4220, "coordinator_loc": 10394},
)
R.check(
    "headroom on a never-re-recorded metric alone leaves the run green",
    _hpo_h_run_frac[0] == 0,
    f"ratchet returned {_hpo_h_run_frac[0]!r} for a tree whose only movement is "
    "cross_seam_fraction inside its own category. Output:\n"
    f"{_hpo_h_run_frac[1]}",
)
if _hpo_h_report is not None:
    _hpo_h_mixed_out = _hpo_g_io.StringIO()
    with _hpo_g_ctx.redirect_stdout(_hpo_h_mixed_out):
        _hpo_h_report([("coordinator_loc", 10394, 10365)], breached=True)
    _hpo_h_mixed = _hpo_h_mixed_out.getvalue()
else:
    _hpo_h_mixed = "report_improvements is missing from tests/structure.py"
R.check(
    "with a breach in the same diff the improvement is still named but --record is not offered",
    "coordinator_loc" in _hpo_h_mixed
    and "python3 tests/structure.py --record" not in _hpo_h_mixed,
    "--record REFUSES a table with a worsened row (#370), so telling the author to "
    f"run it while a breach stands would send them into a refusal. Output:\n{_hpo_h_mixed}",
)

# ---- #374 ---------------------------------------------------------------
# methods_over_150/200 and functions_cc_over_15/25 are counts over a
# threshold: once a function is over the line it is already counted, so it can
# grow without bound and no key in the table moves. With methods_over_200
# pinned at 14 and functions_cc_over_25 at 11, `optimize` could go 540 -> 1,080
# lines and CC 87 -> 174 with all 22 budgets unchanged. max_class_loc already
# does exactly this job for the one shape family that has it.
#
# Driven through table_maxima() on rows shaped exactly as measure() builds
# them, NOT by calling measure(). measure() reads every module under
# custom_components/ and nothing outside it, so calling it here would add to
# this script's closure the HA platform modules that closure does not already
# list -- modules these checks do not test and would open purely because
# measure() walks the directory.
#
# The costlier dependency was a different one, and measure() was never its
# source: a check that read tests/structure_budgets.json directly to confirm
# both new keys had been recorded. It is gone, replaced by the AST checks
# below, because a closure entry on the budget table would put these 1764
# checks in scope for EVERY future re-record -- exactly the traffic #350 makes
# mandatory.
#
# What the real tree measures is pinned by tests/structure.py, which is in the
# same closure and runs in the same gate: its two-way key-set check fails a
# measured-but-absent key, and its ratchet fails the value.
_hpo_h_max = getattr(_hpo_st, "table_maxima", None)
_hpo_struct_src = _Path("tests/structure.py").read_text()
_hpo_h_monsters = [
    (540, "optimizer.py", "1926-2465", "optimize"),
    (483, "optimizer.py", "4613-5095", "_optimize_with_dhw"),
    (416, "optimizer.py", "3419-3834", "_build_dhw_requirements"),
]
_hpo_h_ccs = [
    (87, "optimizer.py", 1926, "optimize"),
    (43, "thermal_model.py", 2316, "simulate_trajectory_batch"),
    (35, "sysid.py", 355, "identify"),
]
R.check(
    "table_maxima reports the worst row of each table measure() already sorts (#374)",
    _hpo_h_max is not None
    and _hpo_h_max(_hpo_h_monsters, _hpo_h_ccs) == (540, 87),
    f"table_maxima = {_hpo_h_max(_hpo_h_monsters, _hpo_h_ccs) if _hpo_h_max else None!r}; "
    "both tables are already built and already sorted, so this is the number the "
    "evidence section has been printing at the top all along",
)
R.check(
    "and it is a MAX, not the first row -- an unsorted table still reports the worst",
    _hpo_h_max is not None
    and _hpo_h_max(list(reversed(_hpo_h_monsters)), list(reversed(_hpo_h_ccs)))
    == (540, 87),
    f"table_maxima(reversed) = "
    f"{_hpo_h_max(list(reversed(_hpo_h_monsters)), list(reversed(_hpo_h_ccs))) if _hpo_h_max else None!r}",
)
R.check(
    "an empty table reads 0, which tightens the gate rather than opening a hole",
    _hpo_h_max is not None and _hpo_h_max([], []) == (0, 0),
    f"table_maxima([], []) = {_hpo_h_max([], []) if _hpo_h_max else None!r}; monsters "
    "starts at 150 LOC and cc_scores at CC 15, so a tree with nothing over those "
    "thresholds reports 0. A budget re-recorded to 0 fails the moment a function "
    "crosses 150 again, so the truncation cannot hide a 149-line method behind a "
    "budget of 540",
)
R.check(
    "and measure() wires both budget keys to it (#374)",
    any(
        isinstance(_hpo_n, _hpo_ast.Dict)
        and {
            _hpo_k.value
            for _hpo_k in _hpo_n.keys
            if isinstance(_hpo_k, _hpo_ast.Constant)
        }
        >= {"max_method_loc", "max_cc", "max_class_loc", "methods_over_200"}
        for _hpo_n in _hpo_ast.walk(_hpo_struct_tree)
    )
    and any(
        isinstance(_hpo_n, _hpo_ast.Call)
        and getattr(_hpo_n.func, "id", "") == "table_maxima"
        for _hpo_n in _hpo_ast.walk(_hpo_struct_tree)
    ),
    "the two keys must be in the metrics dict measure() returns, next to the "
    "threshold counts they close the hole in, and they must come from "
    "table_maxima rather than from a second scan",
)
R.check(
    "both are plain counts, so the existing current > budget arm handles them",
    "max_method_loc" not in _hpo_st.FRACTION_METRICS
    and "max_cc" not in _hpo_st.FRACTION_METRICS
    and _hpo_h_ratchet(
        {"max_cc": 87, "recorded_at": _hpo_h_budgets["recorded_at"]}, {"max_cc": 88}
    )[0] == 1
    and "FAIL max_cc 88 > 87" in _hpo_h_ratchet(
        {"max_cc": 87, "recorded_at": _hpo_h_budgets["recorded_at"]}, {"max_cc": 88}
    )[1],
    "no tolerance, no new polarity, nothing that touches the FRACTION_METRICS "
    "exemption. Output:\n"
    f"{_hpo_h_ratchet({'max_cc': 87, 'recorded_at': _hpo_h_budgets['recorded_at']}, {'max_cc': 88})[1]}",
)
R.check(
    "one extra `and` clause inside a function costs exactly 1 of CC -- the vector, priced",
    _hpo_st.cyclomatic_complexity(
        _hpo_ast.parse("def f(a, b):\n    return bool(a and b)\n").body[0]
    )
    - _hpo_st.cyclomatic_complexity(
        _hpo_ast.parse("def f(a, b):\n    return bool(a)\n").body[0]
    )
    == 1,
    "'add a defensive branch to the function that already has CC 87' has to cost "
    "something; today it costs nothing, because the only place the gate cannot see "
    "new complexity is the worst function in the tree",
)
R.check(
    "and print_report prints both, so the evidence and the RESULT line agree",
    all(
        f'metrics["{_hpo_key}"]' in _hpo_struct_src
        and f"{_hpo_key} = %d" in _hpo_struct_src
        for _hpo_key in ("max_method_loc", "max_cc")
    ),
    "a budgeted number with no evidence line above it is the shape tests/README.md "
    "refuses; the reader has to be able to see which function the budget is about",
)
R.check(
    "sum_cc is rejected IN THE CODE, with the reason and the issue it would break (#374)",
    "sum_cc" in (_hpo_st.__doc__ or "") and "#224" in (_hpo_st.__doc__ or ""),
    "splitting a CC-87 method into a parent and four CC-20 helpers lands near 100 "
    "where there was 87, so a sum_cc budget would fail the exact refactor #224 "
    "exists to perform. It is the obvious next proposal and it is wrong, so the "
    "refusal belongs where the next person reads it, not only in the issue. "
    f"docstring mentions sum_cc: {'sum_cc' in (_hpo_st.__doc__ or '')}",
)

# ===========================================================================
# #283 numpy scalars at two roots; #284 legacy schedule span
# ===========================================================================
R.section("#283 numpy scalars at compute_solar_gain and _deferred_energy_cost")

from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _HPO283,
    OptimizationConfig as _OC283,
    OptimizationResult as _OR283,
)

_gain283 = ThermalModel(ThermalParameters()).compute_solar_gain(np.float64(400.0))
R.check(
    "compute_solar_gain returns a builtin float when irradiance is numpy (#283)",
    type(_gain283) is float,
    repr(type(_gain283)),
)
R.check(
    "the zero-sun early return is already a builtin float (#283)",
    type(ThermalModel(ThermalParameters()).compute_solar_gain(np.float64(0.0)))
    is float,
)

_p283 = ThermalParameters(
    two_zone_enabled=True,
    buffer_tank_volume=750.0,
    mixing_valve_mode="manual",
    buffer_max_temp=70.0,
    cop_flow_carnot=True,
)
_opt283 = _HPO283(
    ThermalModel(_p283),
    _OC283(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=21.0,
        min_temp=19.0,
        max_temp=23.0,
    ),
)
_out283 = np.full(96, -5.0)
_caps283 = _opt283._settlement_caps(_out283)


def _st283(buf):
    return ThermalState(
        room_temperature=21.0,
        upper_floor_temperature=21.0,
        lower_floor_temperature=20.5,
        slab_temperature=25.0,
        buffer_tank_temperature=buf,
        outdoor_temperature=-5.0,
    )


_cost283 = _opt283._deferred_energy_cost(
    _st283(np.float64(50.0)),
    _st283(np.float64(45.0)),
    np.full(96, 1.0),
    _out283,
    caps=_caps283,
)
R.check(
    "_deferred_energy_cost returns a builtin float when stores are numpy (#283)",
    type(_cost283) is float,
    repr(type(_cost283)),
)
R.check(
    "predicted_savings subtraction of that cost stays a builtin float (#283)",
    type(10.0 - _cost283) is float,
    repr(type(10.0 - _cost283)),
)

_ts283 = [
    datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc) + timedelta(minutes=15 * i)
    for i in range(4)
]
_act283 = _opt283.get_current_action(
    _OR283(
        power_schedule=[1.0] * 4,
        room_temp_trajectory=[21.0] * 5,
        slab_temp_trajectory=[22.0] * 5,
        timestamps=_ts283,
        prices=[1.0] * 4,
        predicted_cost=1.0,
        baseline_cost=2.0,
        predicted_savings=1.0,
        savings_percentage=50.0,
        optimal_setpoints=[21.0] * 4,
        status="optimal",
        solar_gain_trajectory=[_gain283] * 4,
    ),
    _ts283[0],
)
R.check(
    "get_current_action solar_gain_kw is a builtin float after compute_solar_gain (#283)",
    type(_act283["solar_gain_kw"]) is float,
    repr(type(_act283.get("solar_gain_kw"))),
)

R.section("#284 legacy schedule publishes the full horizon")

_n284 = 96
_start284 = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
_ts284 = [_start284 + timedelta(minutes=15 * i) for i in range(_n284)]
_coord284 = _t2_coord(dhw_tank_volume=180.0)
_coord284._optimization_result = _OR283(
    power_schedule=[1.0] * _n284,
    room_temp_trajectory=[21.0] * (_n284 + 1),
    slab_temp_trajectory=[22.0] * (_n284 + 1),
    timestamps=_ts284,
    prices=[1.0] * _n284,
    predicted_cost=10.0,
    baseline_cost=12.0,
    predicted_savings=2.0,
    savings_percentage=16.7,
    optimal_setpoints=[21.0] * _n284,
    status="optimal",
    dhw_power_schedule=[0.5] * _n284,
    dhw_temp_trajectory=[50.0] * (_n284 + 1),
    solar_gain_trajectory=[0.1] * _n284,
)
_data284 = _coord284._build_data_dict()
_sched284 = _data284.get("schedule") or []
_dhw284 = _data284.get("dhw_schedule") or []
_forecast284 = (_data284.get("space_plan") or {}).get("forecast") or []
_span284 = (
    datetime.fromisoformat(_sched284[-1]["time"])
    - datetime.fromisoformat(_sched284[0]["time"])
    if len(_sched284) >= 2
    else timedelta(0)
)
R.check(
    "_build_data_dict publishes the full 24 h schedule, not 6 h (#284)",
    len(_sched284) == _n284
    and len(_sched284) == len(_forecast284)
    and _span284 == timedelta(hours=23, minutes=45),
    f"schedule={len(_sched284)} forecast={len(_forecast284)} span={_span284}",
)
R.check(
    "and the DHW schedule matches that span (#284)",
    len(_dhw284) == _n284,
    f"dhw_schedule={len(_dhw284)}",
)

# ---------------------------------------------------------------------------
R.section("W3-G2 — DHW planner re-simulation count (#289)")

from heatpump_optimizer.thermal_model import ThermalModel as _G2Tm

_g2_sim_calls = 0
_g2_sim_orig = _G2Tm.simulate_dhw_only


def _g2_count_sim(self, *a, **k):
    global _g2_sim_calls
    _g2_sim_calls += 1
    return _g2_sim_orig(self, *a, **k)


def _g2_planning_sim_calls(**kw):
    global _g2_sim_calls
    _g2_sim_calls = 0
    _G2Tm.simulate_dhw_only = _g2_count_sim
    try:
        built = _mk_golden(dhw=True, two_zone=False, **kw)
        opt = built["optimizer"]
        st = built["state"]
        n = len(built["prices"])
        step_hours = np.array(
            [
                (_G_START + timedelta(hours=i * 0.25)).hour
                + (_G_START + timedelta(hours=i * 0.25)).minute / 60.0
                for i in range(n)
            ]
        )
        opt._build_dhw_requirements(
            initial_state=st,
            prices=built["prices"],
            outdoor_temps=built["outdoor"],
            step_hours=step_hours,
            n_steps=n,
            dt=0.25,
            p_max=opt.model.params.max_electrical_power,
        )
    finally:
        _G2Tm.simulate_dhw_only = _g2_sim_orig
    return _g2_sim_calls


_g2_winter_calls = _g2_planning_sim_calls(
    price_profile="winter_typical", weather_profile="winter_cold"
)
R.check(
    "winter single-zone planning uses fewer than 64 simulate_dhw_only calls "
    "(judge baseline per _build_dhw_requirements)",
    _g2_winter_calls < 64,
    f"got {_g2_winter_calls}",
)

# Mutation: incremental greedy refresh gone — each edit is a full
# simulate_dhw_only. Cannot call simulate_dhw_only from a live
# extend_dhw_temps patch: production simulate_dhw_only delegates into
# extend_dhw_temps and that pair recurses (CI fast on 1afa09b).
_g2_saved_extend = _G2Tm.extend_dhw_temps


def _g2_extend_via_full_sim(self, temps, from_step, schedule, outdoor, draws, dt_hours=0.25):
    _G2Tm.extend_dhw_temps = _g2_saved_extend
    try:
        new = self.simulate_dhw_only(
            initial_temp=float(temps[0]),
            dhw_power_schedule=schedule,
            outdoor_temps=outdoor,
            draw_rates=draws,
            dt_hours=dt_hours,
        )
    finally:
        _G2Tm.extend_dhw_temps = _g2_extend_via_full_sim
    temps[:] = new
    return temps


try:
    _G2Tm.extend_dhw_temps = _g2_extend_via_full_sim
    _g2_mut_calls = _g2_planning_sim_calls(
        price_profile="winter_typical", weather_profile="winter_cold"
    )
finally:
    _G2Tm.extend_dhw_temps = _g2_saved_extend
R.check(
    "restoring full greedy re-simulation raises simulate_dhw_only count (mutation)",
    _g2_mut_calls >= _g2_winter_calls + 4,
    f"fixed {_g2_winter_calls} vs mutant {_g2_mut_calls}",
)

R.section("3L-G7 — monthly savings history")

from datetime import datetime as _SavDT
from heatpump_optimizer.ledger import (
    MonthlyLedger as _SavLedger,
    month_key as _sav_month_key,
    pro_rata_factor as _sav_factor,
    savings_pct as _sav_pct,
)

_feb10 = _SavDT(2026, 2, 10, 15, 0)
_feb1 = _SavDT(2026, 2, 1, 8, 0)
_jan31 = _SavDT(2026, 1, 31, 12, 0)
R.check(
    "February 10 uses 28 / 10",
    abs(_sav_factor(_feb10) - 2.8) < 1e-12,
    repr(_sav_factor(_feb10)),
)
R.check(
    "day 1 uses divisor 1 (February 1 is 28 / 1)",
    abs(_sav_factor(_feb1) - 28.0) < 1e-12,
    repr(_sav_factor(_feb1)),
)
R.check(
    "January 31 uses 31 / 31",
    abs(_sav_factor(_jan31) - 1.0) < 1e-12,
    repr(_sav_factor(_jan31)),
)
R.check(
    "pct is baseline-relative and clipped",
    abs(_sav_pct(100.0, 60.0) - 60.0) < 1e-12
    and abs(_sav_pct(100.0, 200.0) - 100.0) < 1e-12
    and abs(_sav_pct(100.0, -200.0) - (-100.0)) < 1e-12,
)
R.check(
    "pct is omitted when baseline_sek <= 0.01, not published as 0.0",
    _sav_pct(0.01, 0.0) is None and _sav_pct(0.0, 1.0) is None,
    repr(_sav_pct(0.01, 0.0)),
)

_led = _SavLedger()
_led.add_savings_settlement(
    _feb10, baseline_kw=2.0, actual_kwh=0.5, spot=2.0, dt=0.5
)
_k = _sav_month_key(_feb10)
_base = _led.line(_k, "savings_baseline")
_act = _led.line(_k, "savings_actual")
R.check(
    "settlement books baseline kW×dt and actual kWh at spot",
    abs(_base["kwh"] - 1.0) < 1e-12
    and abs(_base["sek"] - 2.0) < 1e-12
    and abs(_act["kwh"] - 0.5) < 1e-12
    and abs(_act["sek"] - 1.0) < 1e-12,
    f"base {_base} actual {_act}",
)
_led_skip = _SavLedger()
_led_skip.add_savings_settlement(
    _feb10, baseline_kw=None, actual_kwh=0.5, spot=2.0, dt=0.5
)
R.check(
    "missing baseline_kw writes neither line",
    "savings_baseline" not in _led_skip.months.get(_k, {}).get("lines", {})
    and "savings_actual" not in _led_skip.months.get(_k, {}).get("lines", {}),
)
_led.add(_feb10, "spot", kwh=1.0, sek=2.0)
_led.add(_SavDT(2026, 1, 15), "spot", kwh=10.0, sek=20.0)
_rows = _led.savings_months(_feb10)
R.check(
    "a month without savings_baseline is omitted, even if spot was booked",
    [r["month"] for r in _rows] == ["2026-02"],
    repr([r["month"] for r in _rows]),
)
R.check(
    "open month scales all three SEK columns and leaves pct unchanged",
    _rows[0]["estimated"] is True
    and abs(_rows[0]["baseline_sek"] - 5.6) < 1e-9
    and abs(_rows[0]["actual_sek"] - 2.8) < 1e-9
    and abs(_rows[0]["savings_sek"] - 2.8) < 1e-9
    and abs(_rows[0]["savings_pct"] - 50.0) < 1e-9,
    repr(_rows[0]),
)
_led.add_savings_settlement(
    _SavDT(2026, 1, 20), baseline_kw=1.0, actual_kwh=1.0, spot=1.0, dt=1.0
)
_ordered = [r["month"] for r in _led.savings_months(_feb10)]
R.check(
    "rows are oldest first, newest last",
    _ordered == ["2026-01", "2026-02"],
    repr(_ordered),
)
_closed = [r for r in _led.savings_months(_feb10) if r["month"] == "2026-01"][0]
R.check(
    "a closed month is unscaled",
    _closed["estimated"] is False
    and abs(_closed["baseline_sek"] - 1.0) < 1e-9
    and abs(_closed["actual_sek"] - 1.0) < 1e-9,
    repr(_closed),
)

import inspect as _sav_inspect
import pickle as _sav_pickle
from pathlib import Path as _SavPath
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer as _SavOpt,
    OptimizationResult as _SavOR,
)

_ts_sav = [_SavDT(2026, 2, 10, 12, 0) + timedelta(minutes=15 * i) for i in range(4)]
_res_sav = _SavOR(
    power_schedule=[1.0] * 4,
    room_temp_trajectory=[21.0] * 5,
    slab_temp_trajectory=[22.0] * 5,
    timestamps=_ts_sav,
    prices=[1.0] * 4,
    predicted_cost=1.0,
    baseline_cost=2.0,
    predicted_savings=1.0,
    savings_percentage=50.0,
    optimal_setpoints=[21.0] * 4,
    status="optimal",
    baseline_power_schedule=[3.5, 4.0, 0.0, 1.25],
)
R.check(
    "baseline_power_schedule pickles as a plain float list",
    _sav_pickle.dumps(_res_sav.baseline_power_schedule) and True,
)
_act_sav = _bl_opt.get_current_action(_res_sav, _ts_sav[1])
R.check(
    "get_current_action copies the current step's baseline kW",
    abs(_act_sav["baseline_kw"] - 4.0) < 1e-12,
    repr(_act_sav.get("baseline_kw")),
)
_act_zero = _bl_opt.get_current_action(_res_sav, _ts_sav[2])
R.check(
    "a 0.0 baseline step is copied, not treated as missing",
    "baseline_kw" in _act_zero and _act_zero["baseline_kw"] == 0.0,
    repr(_act_zero.get("baseline_kw")),
)
_src_br = _sav_inspect.getsource(_SavOpt._build_result)
R.check(
    "_build_result writes baseline_power_schedule",
    "baseline_power_schedule=" in _src_br,
)
_src_opt = _SavPath("custom_components/heatpump_optimizer/optimizer.py").read_text()
R.check(
    "both solve paths pass the baseline array into _build_result",
    "baseline_power=baseline_power," in _src_opt
    and "baseline_power=baseline_power + baseline_dhw," in _src_opt,
)

sys.exit(R.close("FEATURE CHECKS"))
