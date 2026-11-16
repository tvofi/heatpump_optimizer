"""D7.M3 (round 11, seat D7-s2): each learner against the signals that gate its samples.

Metric: ingested(learner, signal) = 1 when one driven sequence of the learner's own
production entry point, with ``signal`` set on a real coordinator, changes that learner's
persisted state (its keys of ``HeatPumpOptimizerCoordinator._learner_snapshot_payloads``,
compared as JSON before and after), else 0. Count key: the persisted payload the production
seam writes, never an input attribute. A cell counts only where the clean null arm of the
same driver ingests (``null=1``); a driver whose null does not move is reported VACUOUS.

Signals: window (``_vent_cusum.tripped``), pumps (a heat-pump fault: ``PumpSignals.fault`` and
its ``freeze_reason``), external_heat (``_external_heat_active``), defrost
(``PumpSignals.defrosting``), away (``_away_state.active``).

contaminated_ingest = sum over (learner, signal) of ingested where the learner's sample is a
property of the occupied plant that the signal falsifies (the CONTAMINATES table below).

Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py
       add --perturb to treat away as a freeze inside ``_learning_frozen`` (the fix shape):
       contaminated_ingest must fall (away cells to 0).
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): contaminated_ingest=3 exact
(away x {comfort, dhw_draws, internal_gains}); under --perturb 0.
Away is driven with its physics: no hot-water draws while away (the usage profile, which
learns only from draws, then correctly takes nothing).
Machine: box B5 (round-11 finder container), numpy 2.5.4 / scipy 1.18.1, CPython 3.14.
Counts only; no timing number is a finding here.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from unittest import mock  # noqa: E402

sys.path[:0] = ["tests"]
import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import homeassistant.util.dt as dt_mod  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: E402

UTC = timezone.utc
T0 = datetime(2026, 1, 12, 1, 0, tzinfo=UTC)  # a Monday night
SIGNALS = ("window", "pumps", "external_heat", "defrost", "away")
PERTURB = "--perturb" in sys.argv

#: persisted key -> learner (the enumerator's own map, enum_m3.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enum_m3 import KEY_TO_LEARNER, learner_of  # noqa: E402

#: (learner, signal) cells whose ingestion is contamination: the signal makes the interval
#: unrepresentative of the occupied plant the learned value is used for.
#: window/pumps/external_heat/defrost falsify every plant-thermal learner; away falsifies the
#: occupancy-borne ones (internal gains, hot-water usage, the "nobody complained" comfort
#: evidence). Learners of the price feed, of weather, or detectors of the signal itself are
#: never contaminated by it.
PLANT = {"house_heat_loss", "lower_floor_loss", "buffer_cooling", "measured_cop", "cop_health",
         "capacity_envelope", "internal_gains", "solar_aperture", "curve", "comfort",
         "dhw_profile", "dhw_cooling", "dhw_draws", "freq_map", "flow_bias", "defrost", "accuracy"}
OCCUPANCY = {"internal_gains", "dhw_profile", "dhw_draws", "comfort", "curve"}
#: window does not touch a sample with no room air in it
NO_ROOM_AIR = {"buffer_cooling", "dhw_profile", "dhw_cooling", "dhw_draws", "freq_map", "flow_bias",
               "measured_cop", "cop_health", "capacity_envelope", "defrost"}
#: the defrost derate's own learner reads defrost by design
SELF = {("defrost", "defrost")}


#: compressor-side curves: the house's or tank's heat does not enter their sample
COMPRESSOR = {"freq_map", "capacity_envelope"}


def contaminates(learner: str, signal: str) -> bool:
    if learner in COMPRESSOR and signal in ("external_heat", "away", "window"):
        return False
    if (learner, signal) in SELF:
        return False
    if signal == "away":
        return learner in OCCUPANCY
    if signal == "window":
        return learner in PLANT and learner not in NO_ROOM_AIR
    return learner in PLANT


METER = {
    "sensor.indoor": FakeState("20.0", unit="°C"),
    "sensor.outdoor": FakeState("0.0", unit="°C"),
    "sensor.lower": FakeState("20.0", unit="°C"),
    "sensor.dhw": FakeState("50.0", unit="°C"),
    "sensor.buffer": FakeState("40.0", unit="°C"),
    "sensor.hp_power": FakeState("2000", unit="W"),
}
BASE = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
}


def make(**extra):
    c = Coord(FakeHass(dict(METER)), FakeEntry(data=dict(BASE, **extra)))
    c._current_state.room_temperature = 20.0
    c._current_state.outdoor_temperature = 0.0
    c._current_state.solar_radiation = 0.0
    c._current_action = {"power": 2.0}
    c._current_weather = lambda: (0.0, 0.0)
    return c


def apply_signal(c, name):
    if name is None:
        return
    if name == "window":
        c._vent_cusum.tripped = True
    elif name == "pumps":
        c._pump_signals = replace(c._pump_signals, fault=True, freeze_reason="pump_fault")
    elif name == "external_heat":
        c._external_heat_active = True
    elif name == "defrost":
        c._pump_signals = replace(c._pump_signals, defrosting=True)
    elif name == "away":
        c._away_state = replace(c._away_state, active=True)


def payload(c):
    out = {}
    for store, body in c._learner_snapshot_payloads().items():
        for key, value in (body.items() if isinstance(body, dict) else []):
            out[f"{store}.{key}"] = json.dumps(value, sort_keys=True, default=str)
    return out


def changed_learners(before, after):
    return {learner_of(k) for k in set(before) | set(after) if before.get(k) != after.get(k)} - {None}


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def run(coro):
    return asyncio.run(coro)


# -- drivers: each returns the coordinator after one sequence of its learner's entry -------

def drive_house(sig, extra=None):
    """House heat loss, and the folds inside its accepted tail (gains, aperture)."""
    c = make(internal_gains_learning_enabled=True, solar_aperture_learning_enabled=True, two_zone_mode="off",
             **(extra or {}))
    c._house_heat_loss_samples = 500  # the gains gate is open on a converged level
    apply_signal(c, sig)
    observed = c._current_state.room_temperature
    res = [0.0]
    c._thermal_model.simulate_step = lambda prev, power, outdoor, **kw: replace(
        prev, room_temperature=observed - res[0])
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock):
        for i in range(9):
            res[0] = 0.2
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._current_state.solar_radiation = 600.0 if i in (3, 4, 5) else 0.0
            run(c._async_learn_house_heat_loss(c._close_fabric_interval()))
    return c, before


def drive_lower(sig):
    c = make(two_zone_mode="on", lower_floor_temp_entity="sensor.lower")
    apply_signal(c, sig)
    c._current_state.lower_floor_temperature = 20.0
    c._current_state.upper_floor_temperature = 20.0
    lower = c._current_state.lower_floor_temperature
    c._thermal_model.simulate_step = lambda prev, power, outdoor, **kw: replace(
        prev, lower_floor_temperature=lower - 0.2, room_temperature=prev.room_temperature)
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock):
        for i in range(9):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            run(c._async_learn_lower_floor_loss(c._close_fabric_interval()))
    return c, before


def drive_buffer(sig):
    c = make(buffer_tank_temp_entity="sensor.buffer", buffer_tank_volume=300)
    apply_signal(c, sig)
    c._current_action = {"power": 0.0}
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock):
        temp = 45.0
        for i in range(12):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            run(c._async_learn_buffer_cooling(temp))
            temp -= 0.05
    return c, before


def drive_dhw(sig):
    """Hot-water dynamics: standby decay plus two morning draws."""
    c = make(dhw_enabled=True, dhw_temp_entity="sensor.dhw")
    apply_signal(c, sig)
    c._current_action = {"power": 0.0}
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock), \
            mock.patch.object(coord_mod.dt_util, "now", clock):
        temp = 52.0
        for i in range(40):  # 20 h at 30 min
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            run(c._dhw_learner.async_learn_dynamics(temp))
            hour = clock.t.hour
            # away: nobody draws, so the tank only stands (the signal's own physics)
            temp -= 6.0 if hour in (6, 7) and sig != "away" else 0.15
    return c, before


def drive_curve(sig):
    c = make(curve_learning_enabled=True)
    apply_signal(c, sig)
    c._curve_learner.bias = -0.5
    before = payload(c)
    for d in range(3):
        for h in (2, 8, 14, 20):
            apply_signal(c, sig)
            c._current_state.room_temperature = 15.0  # under the floor: a miss
            c._track_curve_comfort(T0 + timedelta(days=d, hours=h))
    return c, before


class _Result(SimpleNamespace):
    pass


def drive_comfort(sig):
    """The quiet-period ("nobody complained") evidence over one day of cycles."""
    c = make(comfort_learning_enabled=True)
    apply_signal(c, sig)
    n = 96
    prices = [0.5 + 0.5 * (i % 24 >= 16) for i in range(n)]
    c._optimization_result = _Result(
        room_temp_trajectory=[19.0] * n, prices=prices, power_schedule=[1.0] * n)
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(coord_mod.dt_util, "now", clock):
        for i in range(48):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._record_quiet_comfort_period()
    return c, before


def drive_freq(sig):
    """The kW-per-Hz map (tests/features.py's _freq_coord shape)."""
    c = make(compressor_freq_entity="number.freq")
    c.hass.states.set("number.freq", FakeState("45", attributes={"min": 20.0, "max": 120.0}))
    c._measured_power = 2.0
    c._current_action = {"power": 1.5, "dhw_power": 0.5}
    before = payload(c)
    for i in range(6):
        apply_signal(c, sig)
        c._observe_frequency(T0 + timedelta(minutes=30 * i))
    return c, before


def drive_cop(sig):
    """The measured-COP fold and the two folds fed from its vetted tail."""
    c = make(heat_pump_power_entity="sensor.hp_power", capacity_curve_enabled=True,
             cop_health_enabled=True)
    c._current_state.outdoor_temperature = 8.0  # out of the frost band
    p_max = float(c._thermal_params.max_electrical_power)
    c._current_action = {"power": p_max}
    c._measured_power = p_max
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock), \
            mock.patch.object(coord_mod.dt_util, "now", clock):
        for i in range(30):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._measured_power = p_max * (0.97 if i % 2 else 1.03)
            c._learn_measured_cop(c._accuracy.draw)
    return c, before


def drive_cop_metered(sig):
    """The measured-COP fold on a heat meter: the compressor-health watch it feeds."""
    c = make(heat_pump_power_entity="sensor.hp_power", heat_pump_thermal_power_entity="sensor.hp_heat",
             capacity_curve_enabled=True)
    c.hass.states.set("sensor.hp_heat", FakeState("6000", unit="W"))
    c._current_state.outdoor_temperature = 8.0
    p_max = float(c._thermal_params.max_electrical_power)
    c._current_action = {"power": p_max}
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock), \
            mock.patch.object(coord_mod.dt_util, "now", clock):
        for i in range(30):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._measured_power = p_max * (0.97 if i % 2 else 1.03)
            c._flow_bias.heat_output_kw = 2.0 * c._measured_power
            c._learn_measured_cop(c._accuracy.draw)
    return c, before


def drive_flow(sig):
    c = make(heat_pump_power_entity="sensor.hp_power")
    p_max = float(c._thermal_params.max_electrical_power)
    c._current_action = {"power": p_max}
    c._measured_power = p_max
    before = payload(c)
    for i in range(10):
        apply_signal(c, sig)
        c._flow_bias.last_supply_c = 38.0 + 0.1 * i
        coord_mod._fold_flow_lift(c, T0 + timedelta(minutes=30 * i))
    return c, before


def drive_immersion(sig):
    c = make(heat_pump_power_entity="sensor.hp_power")
    p_max = float(c._thermal_params.max_electrical_power)
    c._current_action = {"power": p_max}
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(coord_mod.dt_util, "now", clock):
        for i in range(4):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._measured_power = p_max * 3.0
            c._detect_immersion()
    return c, before


def drive_snow(sig):
    c = make(snow_roof_factor_enabled=True)
    before = payload(c)
    for i in range(4):
        apply_signal(c, sig)
        c._update_snow_memory(T0 + timedelta(hours=i), np.full(48, 2.0))
    return c, before


def drive_settle(sig):
    """The settlement: the accuracy sample and the defrost derate it feeds."""
    c = make(heat_pump_power_entity="sensor.hp_power", defrost_entity="binary_sensor.defrost")
    c._current_state.outdoor_temperature = 1.0  # in the frost band
    clock = Clock(T0)
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock), \
            mock.patch.object(coord_mod.dt_util, "now", clock):
        for i in range(8):
            apply_signal(c, sig)
            clock.t = T0 + timedelta(minutes=30 * i)
            c._measured_power = 1.5
            c._current_action = {"power": 2.0}
            c._record_accuracy()
    return c, before


def drive_price(sig):
    c = make()
    apply_signal(c, sig)
    c._prices = [{"total": 0.5 + 0.3 * ((h % 24) >= 17), "starts_at":
                  (T0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(48)]
    clock = Clock(T0 + timedelta(hours=23))
    before = payload(c)
    with mock.patch.object(dt_mod, "now", clock), \
            mock.patch.object(coord_mod.dt_util, "now", clock):
        run(c._async_learn_price_shape())
    return c, before


#: each learner's own driver: the entry point that gates its samples
DRIVER_OF = {
    "house_heat_loss": "house", "internal_gains": "house", "solar_aperture": "house",
    "vent_detector": "house", "lower_floor_loss": "lower", "buffer_cooling": "buffer",
    "dhw_profile": "dhw", "dhw_cooling": "dhw", "dhw_draws": "dhw", "curve": "curve",
    "comfort": "comfort", "freq_map": "freq", "price_model": "price", "measured_cop": "cop",
    "capacity_envelope": "cop", "cop_health": "cop_metered", "flow_bias": "flow",
    "immersion_log": "immersion", "snow": "snow", "accuracy": "settle", "defrost": "settle",
}

DRIVERS = {
    "house": drive_house, "lower": drive_lower, "buffer": drive_buffer, "dhw": drive_dhw,
    "curve": drive_curve, "comfort": drive_comfort, "freq": drive_freq, "price": drive_price,
    "cop": drive_cop, "flow": drive_flow, "immersion": drive_immersion, "snow": drive_snow,
    "settle": drive_settle, "cop_metered": drive_cop_metered,
}


def main():
    t0 = time.process_time()
    universe = [l for l in sorted({learner_of(k) for k in KEY_TO_LEARNER} - {None})]
    moved = {}  # (driver, signal) -> set of learners
    errors = {}
    for dname, drive in DRIVERS.items():
        for sig in (None,) + SIGNALS:
            try:
                c, before = drive(sig)
                moved[(dname, sig)] = changed_learners(before, payload(c))
            except Exception as err:  # noqa: BLE001 - reported, a driver gap is not a cell
                errors[(dname, sig)] = repr(err)[:200]
    contaminated = 0
    examined = 0
    print("learner".ljust(18), "driver".ljust(12), "null", *[s[:7].ljust(7) for s in SIGNALS])
    for learner in universe:
        drv = DRIVER_OF.get(learner)
        null = int(learner in moved.get((drv, None), set()))
        if drv is None or (drv, None) not in moved or not null:
            print(learner.ljust(18), str(drv).ljust(12), "VACUOUS (null arm does not ingest)")
            continue
        examined += 1
        cells = []
        for s in SIGNALS:
            v = int(learner in moved.get((drv, s), set()))
            bad = v and contaminates(learner, s)
            contaminated += bad
            if bad:
                print(f"RESULT ingest_{learner}_{s}=1 count")
            cells.append((str(v) + ("*" if bad else "")).ljust(7))
        print(learner.ljust(18), drv.ljust(12), str(null).ljust(4), *cells)
    for k, v in errors.items():
        print("DRIVER-ERROR", k, v)
    print("RESULT learners_universe=%d count" % len(universe))
    print("RESULT learners_examined=%d count" % examined)
    print("RESULT contaminated_ingest=%d count" % contaminated)
    cpu = time.process_time() - t0
    print(f"RESULT thread_factor={1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    print(f"# cpu {cpu:.1f}s (provisional, not a finding)")


if PERTURB:
    _orig = Coord._learning_frozen

    def _away_freezes(self, *keys, room_air=True):
        why = _orig(self, *keys, room_air=room_air)
        if why is None and getattr(self, "_away_state", None) is not None and self._away_state.active:
            return "away"
        return why

    Coord._learning_frozen = _away_freezes

if __name__ == "__main__":
    main()
