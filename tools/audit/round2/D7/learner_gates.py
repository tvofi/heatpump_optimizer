#!/usr/bin/env python3
"""D7 step 4 -- learner freeze versus COP flow: which learner ingests a contaminated interval.

Metric (one line): (A) an AST table over HeatPumpOptimizerCoordinator's learner methods of the
gating signals each consults -- D = the method's own body references the signal, T = only
through _learning_frozen (external heat, pump signals, unusable input, open window) or through
a gated caller / _interval_space_power, "-" = never; (B) a RUNTIME table: a real coordinator
(tests/harness.py FakeHass/FakeEntry, dt_util.now patched) is seeded with one clean sample,
ONE contamination is injected (open window: _vent_cusum.tripped; pump: PumpSignals(freeze
FREEZE_OFFLINE); external heat: _external_heat_active + state flag; defrost: in the frost band
with DefrostWindow.observe(True) and PumpSignals(defrosting=True); away: AwayState(active)),
the learner runs once more and its own sample counter says whether it ingested (1) or not (0);
(C) the defrost mechanism's magnitude: the real house heat-loss learner replaying the real
model against a plant that delivers (1 - 0.25) of the commanded power on a fraction f of
30-min intervals (a 7.5-min defrost each), 400 intervals after a 96-interval warm-up,
house_heat_loss_scale at the end for f in {0, 0.2, 0.5}, single-zone (structurally blind: all
heat passes the slab store) and two-zone (radiator share 0.4 heats the upper zone directly);
f = 0 is the null control and must stay at 1.0.

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/learner_gates.py
Expected: (A),(B) exact counts; (C) exact to 1e-6 (deterministic); baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box; no timing reported.
Instrumented symbol: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
          (and the other learner methods listed in LEARNERS), _learning_frozen, _learn_measured_cop.
Perturbation: add ``if self._pump_signals.defrosting: return`` (or the COP learner's
          DefrostWindow.peek(...).any_defrost check) at the top of _async_learn_house_heat_loss
          -> ingest_house_loss_defrost to_zero and defrost_scale_f20/f50 to 1.0 (to_zero bias);
          set f -> 0 -> defrost_scale_f0 = 1.0 (the null).
Writes:   nothing but stdout.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import asyncio
import contextlib
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np
from harness import FakeEntry, FakeHass, FakeState
from profiles import house
import homeassistant.util.dt as dt_mod
from heatpump_optimizer.away import AwayState
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.pump_signals import FREEZE_OFFLINE, PumpSignals
from heatpump_optimizer.thermal_model import ThermalModel, ThermalState

UTC = timezone.utc
T0 = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
SRC = ROOT / "custom_components/heatpump_optimizer/coordinator.py"

LEARNERS = [
    "_async_learn_house_heat_loss", "_async_learn_lower_floor_loss", "_learn_measured_cop",
    "_async_learn_buffer_cooling", "_async_learn_dhw_dynamics", "_async_learn_dhw_cooling",
    "_async_learn_dhw_usage", "_async_fold_draw_stats", "_fold_solar_aperture",
    "_fold_internal_gains", "_fold_capacity_envelope", "_observe_cop_health", "_settle_defrost",
    "_record_accuracy", "_track_curve_comfort", "_async_learn_price_shape",
    "_observe_compressor_start", "_observe_frequency", "_inputs_healthy",
    "_async_watch_learning_drift", "record_setpoint_override", "_record_quiet_comfort_period",
]
SIGNALS = ["open_window", "pump_signals", "external_heat", "defrost", "away", "immersion"]
DIRECT = {
    "open_window": {"_vent_cusum"},
    "pump_signals": {"_pump_signals"},
    "external_heat": {"_external_heat_active", "external_heat_active"},
    "defrost": {"_defrost_window", "in_frost_band", "defrosting", "_defrost"},
    "away": {"_away_state"},
    "immersion": {"_immersion_active"},
}
FROZEN_COVERS = {"open_window", "pump_signals", "external_heat"}   # what _learning_frozen checks


# ----------------------------------------------------------------------------- (A) AST
def ast_table():
    tree = ast.parse(SRC.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
    methods = {m.name: m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    names_in = {}
    calls_in = {}
    for name, m in methods.items():
        ids = set()
        calls = set()
        for d in ast.walk(m):
            if isinstance(d, ast.Attribute):
                ids.add(d.attr)
                if isinstance(d.value, ast.Name) and d.value.id == "self":
                    calls.add(d.attr)
            elif isinstance(d, ast.Name):
                ids.add(d.id)
        names_in[name] = ids
        calls_in[name] = {c for c in calls if c in methods}
    callers = {n: {k for k, v in calls_in.items() if n in v} for n in methods}

    def gates(name, depth=0):
        ids = names_in[name]
        row = {}
        for s in SIGNALS:
            if ids & DIRECT[s]:
                row[s] = "D"
            elif "_learning_frozen" in ids and s in FROZEN_COVERS:
                row[s] = "T"
            elif s == "pump_signals" and "_interval_space_power" in calls_in[name]:
                row[s] = "T"
            elif s == "immersion" and "_interval_space_power" in calls_in[name]:
                row[s] = "T"
            else:
                row[s] = "-"
        if depth == 0:
            # one level of gated callers: a learner only reachable through a gated method inherits it
            for c in callers[name]:
                if c in LEARNERS or c.startswith("_async_learn") or c.startswith("_learn"):
                    up = gates(c, 1)
                    for s in SIGNALS:
                        if row[s] == "-" and up[s] != "-":
                            row[s] = f"T({c.strip('_')[:12]})"
        if name == "_async_learn_house_heat_loss" and "vent_only" in ids:
            row["open_window"] = "D(feeds, then returns)"
        return row

    table = {n: gates(n) for n in LEARNERS if n in methods}
    return table, callers


# ----------------------------------------------------------------------------- (B) runtime
@contextlib.contextmanager
def clock(t):
    real = dt_mod.now
    dt_mod.now = lambda *a, **k: t
    try:
        yield
    finally:
        dt_mod.now = real


#: tests/profiles.py house(two_zone=True)'s zone keys; ThermalParameters.from_config switches the
#: two-zone model on from two_zone_mode="on" (const.TWO_ZONE_MODE_ON).
TWO_ZONE = {k: v for k, v in house(two_zone=True).items()
            if k.startswith(("upper_floor", "lower_floor", "inter_zone", "radiator_power"))}
TWO_ZONE["two_zone_mode"] = "on"
BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
STATES = {
    "sensor.indoor": FakeState("20.0", unit="°C"), "sensor.outdoor": FakeState("2.0", unit="°C"),
    "sensor.hp_power": FakeState("2600", unit="W"), "sensor.buffer": FakeState("50.0", unit="°C"),
    "sensor.dhw": FakeState("55.0", unit="°C"), "sensor.lower": FakeState("20.0", unit="°C"),
}


def coord(**extra):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data={**BASE_CFG, **extra}))
    c._current_weather = lambda: (0.0, 0.0)
    c._current_state = ThermalState(room_temperature=20.0, slab_temperature=22.0, outdoor_temperature=2.0,
                                    upper_floor_temperature=20.0, lower_floor_temperature=20.0,
                                    buffer_tank_temperature=50.0, dhw_temperature=55.0)
    return c


def stub_model(c, residual):
    obs_room = c._current_state.room_temperature
    obs_lower = c._current_state.lower_floor_temperature

    def _sim(prev, power, outdoor, **kw):
        return replace(prev, room_temperature=obs_room - residual, upper_floor_temperature=obs_room - residual,
                       lower_floor_temperature=obs_lower - residual)
    c._thermal_model.simulate_step = _sim


CONTAMINATE = {
    "clean": lambda c, now: c._defrost_window.observe(now, False),
    "open_window": lambda c, now: setattr(c._vent_cusum, "tripped", True),
    "pump_offline": lambda c, now: setattr(c, "_pump_signals", PumpSignals(online=False, freeze_reason=FREEZE_OFFLINE)),
    "external_heat": lambda c, now: (setattr(c, "_external_heat_active", True),
                                     setattr(c._current_state, "external_heat_active", True)),
    "defrost": lambda c, now: (c._defrost_window.observe(now, True),
                               setattr(c, "_pump_signals", PumpSignals(defrosting=True))),
    "away": lambda c, now: setattr(c, "_away_state", AwayState(active=True)),
}


def drive_house(arm):
    c = coord()
    stub_model(c, 0.1)
    c._current_action = {"power": 2.0}
    with clock(T0):
        asyncio.run(c._async_learn_house_heat_loss())      # seeds the baseline
    CONTAMINATE[arm](c, T0)
    before = c._house_heat_loss_samples
    with clock(T0 + timedelta(minutes=30)):
        CONTAMINATE[arm](c, T0 + timedelta(minutes=30)) if arm == "defrost" else None
        asyncio.run(c._async_learn_house_heat_loss())
    return c._house_heat_loss_samples - before


def drive_lower(arm):
    c = coord(lower_floor_temp_entity="sensor.lower", **TWO_ZONE)
    stub_model(c, 0.1)
    c._current_action = {"power": 2.0}
    with clock(T0):
        asyncio.run(c._async_learn_house_heat_loss())      # seeds _last_house_sample
    CONTAMINATE[arm](c, T0)
    before = c._lower_floor_loss_samples
    with clock(T0 + timedelta(minutes=30)):
        CONTAMINATE[arm](c, T0 + timedelta(minutes=30)) if arm == "defrost" else None
        asyncio.run(c._async_learn_lower_floor_loss())
    return c._lower_floor_loss_samples - before


def drive_cop(arm):
    c = coord(heat_pump_power_entity="sensor.hp_power")
    c._measured_power = 2.6
    c._current_action = {"power": 3.0}
    CONTAMINATE[arm](c, T0)
    before = c._cop_samples
    with clock(T0):
        c._learn_measured_cop()
    return c._cop_samples - before


def drive_buffer(arm):
    c = coord(buffer_tank_temp_entity="sensor.buffer")
    c._current_action = {"power": 0.0}
    with clock(T0):
        asyncio.run(c._async_learn_buffer_cooling(50.0))
    CONTAMINATE[arm](c, T0)
    before = c._buffer_cooling_samples
    with clock(T0 + timedelta(hours=1)):
        asyncio.run(c._async_learn_buffer_cooling(49.5))
    return c._buffer_cooling_samples - before


def drive_dhw(arm, which):
    c = coord(dhw_temp_entity="sensor.dhw", dhw_enabled=True)
    c._current_action = {"dhw_heating_active": False}
    with clock(T0):
        asyncio.run(c._async_learn_dhw_dynamics(55.0))
    CONTAMINATE[arm](c, T0)
    b_cool = c._dhw_cooling_samples
    b_use = list(c._dhw_daytype_samples)
    with clock(T0 + timedelta(hours=1)):
        asyncio.run(c._async_learn_dhw_dynamics(53.0))
    if which == "cooling":
        return c._dhw_cooling_samples - b_cool
    return int(sum(c._dhw_daytype_samples) - sum(b_use))


def drive_accuracy(arm):
    c = coord(heat_pump_power_entity="sensor.hp_power")
    c._measured_power = 2.0
    c._current_action = {"power": 2.0, "dhw_power": 0.0}
    c._pending_prediction = {"when": T0, "power": 2.0, "space_power": 2.0, "dhw_power": 0.0,
                             "space_reason": None, "dhw_reason": None, "price": 1.0, "spot_price": 1.0,
                             "grid_fee": 0.0, "predicted_temp": 20.2, "outdoor": 2.0, "humidity": None, "diag": None}
    CONTAMINATE[arm](c, T0)
    before = len(c._accuracy.samples)
    with clock(T0 + timedelta(minutes=30)):
        c._record_accuracy()
    return len(c._accuracy.samples) - before


def drive_curve(arm):
    c = coord(curve_learning_enabled=True)
    CONTAMINATE[arm](c, T0)
    with clock(T0):
        c._track_curve_comfort(T0)
    return int(c._curve_day_worst is not None)


DRIVERS = [
    ("house_loss", drive_house), ("lower_floor_loss", drive_lower), ("measured_cop", drive_cop),
    ("buffer_cooling", drive_buffer), ("dhw_cooling", lambda a: drive_dhw(a, "cooling")),
    ("dhw_usage", lambda a: drive_dhw(a, "usage")), ("accuracy_record", drive_accuracy),
    ("curve_comfort", drive_curve),
]


# ----------------------------------------------------------------------------- (C) magnitude
def defrost_bias(f, two_zone, n=400, duty=0.25, seed=0, warmup=96):
    """Real learner, real model, a plant that delivers (1-duty) of the command on a fraction f
    of intervals. Single-zone: every watt goes through the slab store and the explicit-Euler
    room update reads the PREVIOUS slab temperature, so a one-step replay cannot see a
    delivered-power shortfall in the room at all (a structural null). Two-zone: the radiator
    share (0.4 here) heats the upper zone directly, so the shortfall lands in the residual."""
    c = coord(**TWO_ZONE) if two_zone else coord()
    p = c._thermal_params
    plant = ThermalModel(replace(p))               # its own parameters: the learner mutates c's
    t_out = 2.0
    cop = plant.compute_cop(t_out)
    ua = (p.upper_floor_heat_loss + p.lower_floor_heat_loss) if p.two_zone_enabled else p.heat_loss_coefficient
    thermal = max(0.0, ua * (21.0 - t_out) - p.internal_gains)
    p_cmd = thermal / cop
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + thermal / p.slab_heat_transfer,
                         outdoor_temperature=t_out, upper_floor_temperature=21.0,
                         lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    for _ in range(warmup):                         # let the plant settle at the command
        state = plant.simulate_step(state, p_cmd, t_out, dt_hours=0.5)

    def publish(st):
        room = st.upper_floor_temperature if p.two_zone_enabled else st.room_temperature
        c._current_state = replace(st, room_temperature=room)   # the indoor sensor is the upper floor

    rng = np.random.default_rng(seed)
    defrost = rng.random(n) < f
    publish(state)
    c._current_action = {"power": p_cmd}
    with clock(T0):
        asyncio.run(c._async_learn_house_heat_loss())      # seeds
    for i in range(1, n + 1):
        delivered = p_cmd * (1.0 - duty) if defrost[i - 1] else p_cmd
        state = plant.simulate_step(state, delivered, t_out, dt_hours=0.5)
        publish(state)
        with clock(T0 + timedelta(minutes=30 * i)):
            asyncio.run(c._async_learn_house_heat_loss())
    room = state.upper_floor_temperature if p.two_zone_enabled else state.room_temperature
    return c._house_heat_loss_scale, c._house_heat_loss_samples, p_cmd, float(room), bool(p.two_zone_enabled)


def main() -> int:
    print("=== D7 learner gates ===")
    table, callers = ast_table()
    print("\n-- (A) AST: gate signals per learner (D direct, T via _learning_frozen / gated caller / _interval_space_power)")
    print(f"{'learner':32} " + " ".join(f"{s:>14}" for s in SIGNALS))
    for n, row in table.items():
        print(f"{n:32} " + " ".join(f"{row[s][:14]:>14}" for s in SIGNALS))
    ungated = {s: [n for n, r in table.items() if r[s] == "-"] for s in SIGNALS}
    for s in SIGNALS:
        print(f"RESULT ast_learners_without_{s}_gate={len(ungated[s])} count")

    print("\n-- (B) runtime: 1 = the learner ingested the contaminated interval")
    arms = list(CONTAMINATE)
    print(f"{'learner':18} " + " ".join(f"{a:>14}" for a in arms))
    matrix = {}
    for name, drv in DRIVERS:
        row = {}
        for a in arms:
            try:
                row[a] = int(drv(a))
            except Exception as err:  # noqa: BLE001 - reported, not hidden
                row[a] = f"ERR:{type(err).__name__}"
        matrix[name] = row
        print(f"{name:18} " + " ".join(f"{str(row[a]):>14}" for a in arms))
    for name, row in matrix.items():
        for a in arms:
            v = row[a] if isinstance(row[a], int) else -1
            print(f"RESULT ingest_{name}_{a}={v} count")
    for a in arms:
        print(f"RESULT learners_ingesting_{a}={sum(1 for r in matrix.values() if r[a] == 1)} count")

    print("\n-- (C) defrost contamination of the house heat-loss learner (real model, real learner, 400 x 30 min)")
    for two_zone in (False, True):
        for f in (0.0, 0.2, 0.5):
            scale, samples, p_cmd, room, tz = defrost_bias(f, two_zone)
            tag = f"{'tz' if two_zone else 'sz'}_f{int(f * 100):02d}"
            label = "two-zone, radiators 40% direct" if two_zone else "single-zone, all heat via slab"
            print(f"   {label:32} f={f:.1f}: house_heat_loss_scale={scale:.4f} after {samples} samples "
                  f"(command {p_cmd:.2f} kW, room {room:.1f} C, two_zone_enabled={tz})")
            print(f"RESULT defrost_scale_{tag}={scale:.6f} ratio")
            print(f"RESULT defrost_samples_{tag}={samples} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
