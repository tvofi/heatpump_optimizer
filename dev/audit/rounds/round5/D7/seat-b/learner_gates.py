#!/usr/bin/env python3
"""D7-b scope 1: learner freeze versus COP flow — contamination matrix.

METRIC (one line): for each (learner, contamination) cell, 1 if the learner
folded a sample over the measured interval on a real coordinator (its sample
counter or evidence store moved / its fold method was entered) and 0 if it
refused; the comfort-quiet learner's cell is the count of folds under
contamination.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/seat-b/learner_gates.py

EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1,
macOS, python3.11): every thermal/COP learner refuses (0) under
external_heat, defrost, cooling, ventilation and the dead-indoor arm and
ingests (1) in the control; the curve learner also refuses under away; and
RESULT comfort_quiet_folds_under_contamination = 2 (the quiet-period comfort
learner folds during defrost and dead-indoor — the two contaminations that
leave the PLAN flat while the realized house is not — the one learner
outside the shared freeze discipline) with tolerance 0.

KEY OF THE COUNTED NUMBER: the fold is counted on the learner's own state
move (counter increment / evidence decrement / fold-method entry), never on
an input attribute.
"""
import os
import sys

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from types import SimpleNamespace  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const as hpo_const  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.dhw_learning import DhwProfileLearner  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

T0 = datetime(2026, 1, 15, 6, 0, 0)
KW_ATTR = {"unit_of_measurement": "kW"}

# The contamination scenarios the brief names, plus the dead-input arm.
SCENARIOS = (
    "none",
    "external_heat",
    "defrost",
    "cooling",
    "ventilation",
    "away",
    "power_dead",
    "indoor_dead",
)


def build_cfg(two_zone=False):
    cfg = {
        hpo_const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        hpo_const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        hpo_const.CONF_POWER_ENTITY: "sensor.power",
        hpo_const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
        hpo_const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
        hpo_const.CONF_DHW_TANK_VOLUME: 180.0,
        hpo_const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.supply",
        hpo_const.CONF_CURVE_LEARNING_ENABLED: True,
        hpo_const.CONF_COMFORT_LEARNING_ENABLED: True,
        # external-heat detection on, with the user's own stove flag as the
        # authoritative override entity.
        hpo_const.CONF_WOOD_FURNACE_ENABLED: True,
        hpo_const.CONF_EXTERNAL_HEAT_ENABLED: True,
        hpo_const.CONF_EXTERNAL_HEAT_ENTITY: "input_boolean.stove",
        hpo_const.CONF_HEAT_PUMP_DEFROST_ENTITY: "sensor.defrost",
        hpo_const.CONF_HEAT_PUMP_MODE_ENTITY: "sensor.hpmode",
    }
    if two_zone:
        cfg[hpo_const.CONF_TWO_ZONE_MODE] = True
        cfg[hpo_const.CONF_LOWER_FLOOR_TEMP_ENTITY] = "sensor.lower"
    return cfg


def build_coord(cfg):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    hass.states.set("sensor.power", FakeState("2.6", attributes=KW_ATTR))
    hass.states.set("sensor.dhw", FakeState("55.0"))
    hass.states.set("sensor.buffer", FakeState("45.0"))
    hass.states.set("sensor.supply", FakeState("40.0"))
    hass.states.set("sensor.lower", FakeState("20.0"))
    hass.states.set("input_boolean.stove", FakeState("off"))
    hass.states.set("sensor.defrost", FakeState("off"))
    # A select-style mode entity (options declared), so the single-duty
    # words are taken at face value rather than refused as status-ambiguous.
    hass.states.set(
        "sensor.hpmode",
        FakeState("heat", attributes={"options": ["heat", "cool", "auto"]}),
    )
    return hass, HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))


def cycle(coord):
    asyncio.run(coord._update_current_state())


def apply_contamination(hass, scenario):
    if scenario == "external_heat":
        hass.states.set("input_boolean.stove", FakeState("on"))
    elif scenario == "defrost":
        hass.states.set("sensor.defrost", FakeState("on"))
    elif scenario == "cooling":
        hass.states.set(
            "sensor.hpmode",
            FakeState("cool", attributes={"options": ["heat", "cool", "auto"]}),
        )
    elif scenario == "power_dead":
        hass.states.set("sensor.power", FakeState("unavailable"))
    elif scenario == "indoor_dead":
        hass.states.set("sensor.indoor", FakeState("unavailable"))


def vent_pretrip(coord, hass):
    """Trip the open-window CUSUM honestly: sustained colder-than-predicted.

    Three 20-minute cycles with the pump running the plan (commanded 3.0,
    metered 2.6 — a consistent pair, or `_interval_space_power` returns None
    for tracking error and the detector never gets fed) while the room falls
    far faster than the model predicts; each cycle feeds the detector a
    clipped -0.6 residual (threshold 1.2, drift 0.08), which trips it on the
    third sample.
    """
    indoor = 21.4
    for i in range(1, 5):
        dt_util.freeze(T0 + timedelta(minutes=20 * i))
        indoor -= 2.5
        hass.states.set("sensor.indoor", FakeState(f"{indoor:.2f}"))
        coord._current_action = {"power": 3.0, "dhw_power": 0.0}
        cycle(coord)
        if coord._vent_cusum.tripped:
            return True
    return coord._vent_cusum.tripped


def quiet_plan(scenario):
    """The plan `_record_quiet_comfort_period` would really see, per scenario.

    The quiet-period learner reads the SOLVED plan, so each contamination
    arm feeds the plan that contamination actually produces, not one flat
    trajectory for all: external heat plans near-zero heating (the free-heat
    forecast replaces it), a cooling freeze suppresses space heating, and
    away/ventilation plans span a coast or a recovery rather than holding
    flat. Only defrost and a dead indoor sensor leave the plan itself flat
    while the realized house is not.
    """
    flat = dict(
        room_temp_trajectory=[20.9, 21.0, 20.9, 21.0],
        prices=[0.10, 0.30, 0.20, 0.40],
        power_schedule=[3.0, 3.0, 3.0, 3.0],
    )
    if scenario in ("external_heat",):
        return dict(flat, power_schedule=[0.05, 0.05, 0.05, 0.05])
    if scenario in ("cooling",):
        return dict(flat, power_schedule=[0.0, 0.0, 0.0, 0.0])
    if scenario == "away":
        return dict(
            flat,
            room_temp_trajectory=[21.0, 19.0, 17.5, 17.5],
        )
    if scenario == "ventilation":
        return dict(
            flat,
            room_temp_trajectory=[18.9, 19.8, 20.6, 21.0],
        )
    return flat


def heated_interval(scenario, two_zone=False):
    """One interval with the pump commanded on: house/lower/COP/flow/curve."""
    dt_util.freeze(T0)
    hass, coord = build_coord(build_cfg(two_zone))
    cycle(coord)
    if scenario == "ventilation":
        tripped = vent_pretrip(coord, hass)
        if not tripped:
            raise RuntimeError("vent CUSUM did not trip")
    if scenario == "away":
        coord._away_state.active = True
    # What the model predicts for the elapsed hour at the measured draw, so
    # the control interval's residual is small and the sample is eligible.
    prev = coord._last_house_sample
    power = 0.0 if scenario == "power_dead" else 2.6
    pred = coord._thermal_model.simulate_step(
        prev, power, prev.outdoor_temperature,
        wind_speed=0.0, precipitation=0.0,
        solar_radiation=prev.solar_radiation, dt_hours=1.0,
        hour_of_day=7.0,
    )
    dt_util.freeze(T0 + timedelta(hours=1))
    apply_contamination(hass, scenario)
    coord._current_action = {"power": 3.0, "dhw_power": 0.0}
    observed_room = (
        pred.upper_floor_temperature if two_zone else pred.room_temperature
    )
    if scenario != "indoor_dead":
        hass.states.set("sensor.indoor", FakeState(f"{observed_room + 0.05:.4f}"))
    if two_zone:
        hass.states.set(
            "sensor.lower",
            FakeState(f"{pred.lower_floor_temperature + 0.05:.4f}"),
        )
    before = (
        coord._house_heat_loss_samples,
        coord._lower_floor_loss_samples,
        coord._cop_samples,
        coord._flow_bias.samples,
    )
    # Instrument the curve learner's day book: forcing the worst-margin
    # slot to None before the cycle makes "the tracker ingested this
    # cycle's evidence" a binary read — a frozen tracker leaves it None.
    coord._curve_day_worst = None
    cycle(coord)
    if scenario in ("none", "power_dead", "indoor_dead"):
        # The flow-lift fold lives on the accuracy seam, after the solve.
        coord_mod._fold_flow_lift(coord, dt_util.now())
    house = coord._house_heat_loss_samples - before[0]
    lower = coord._lower_floor_loss_samples - before[1]
    cop = coord._cop_samples - before[2]
    flow = coord._flow_bias.samples - before[3]
    curve = 1 if coord._curve_day_worst is not None else 0
    # The comfort quiet-period learner, same coordinator state, driven the
    # way _record_quiet_comfort_period's caller does: with the plan that
    # this contamination actually produces.
    coord._optimization_result = SimpleNamespace(**quiet_plan(scenario))
    ev_before = coord._comfort_learner.evidence
    coord._record_quiet_comfort_period()
    quiet = 1 if coord._comfort_learner.evidence < ev_before else 0
    # The defrost derate's documented exemption (#944): its settlement runs
    # on exactly the intervals the shared gate refuses.
    derate_gate = coord._learning_frozen(hpo_const.CONF_POWER_ENTITY) in (
        None, "defrosting",
    )
    return {
        "house": house, "lower": lower, "cop": cop, "flow_lift": flow,
        "curve_comfort": curve, "comfort_quiet": quiet,
        "defrost_derate_exempt": 1 if derate_gate else 0,
    }


def quiet_interval(scenario):
    """One interval with the pump idle: buffer/DHW cooling + draw stats."""
    dt_util.freeze(T0)
    hass, coord = build_coord(build_cfg())
    cycle(coord)
    if scenario == "ventilation":
        if not vent_pretrip(coord, hass):
            raise RuntimeError("vent CUSUM did not trip")
    if scenario == "away":
        coord._away_state.active = True
    dt_util.freeze(T0 + timedelta(hours=1))
    apply_contamination(hass, scenario)
    coord._current_action = {"power": 0.0, "dhw_power": 0.0}
    hass.states.set("sensor.power", FakeState("0.10", attributes=KW_ATTR))
    hass.states.set("sensor.dhw", FakeState("54.0"))
    hass.states.set("sensor.buffer", FakeState("44.0"))
    folds = []
    orig = DhwProfileLearner.async_fold_draw_stats

    async def spy(self, *a, **k):
        folds.append(1)
        return await orig(self, *a, **k)

    before = (
        coord._buffer_cooling_samples,
        coord._dhw_learner.cooling_samples,
    )
    DhwProfileLearner.async_fold_draw_stats = spy
    try:
        cycle(coord)
    finally:
        DhwProfileLearner.async_fold_draw_stats = orig
    return {
        "buffer_cooling": coord._buffer_cooling_samples - before[0],
        "dhw_cooling": coord._dhw_learner.cooling_samples - before[1],
        "dhw_draw_stats": len(folds),
    }


def main():
    rows = {}
    for scenario in SCENARIOS:
        heated = heated_interval(scenario)
        # The lower-zone learner needs the two-zone plant; run the same
        # interval on a two-zone coordinator for that one column.
        two_zone = heated_interval(scenario, two_zone=True)
        heated["lower"] = two_zone["lower"]
        quiet = quiet_interval(scenario)
        rows[scenario] = {**heated, **quiet}
    learners = (
        "house", "lower", "cop", "flow_lift", "curve_comfort",
        "comfort_quiet", "defrost_derate_exempt",
        "buffer_cooling", "dhw_cooling", "dhw_draw_stats",
    )
    print(f"{'scenario':<14} " + " ".join(f"{l:>12}" for l in learners))
    for scenario in SCENARIOS:
        cells = rows[scenario]
        print(
            f"{scenario:<14} "
            + " ".join(f"{cells[l]:>12}" for l in learners)
        )
    # The finding's number: quiet-period comfort folds under the thermal
    # contaminations every other learner freezes on (power_dead excluded —
    # the power reading is not this learner's input, so folding there is
    # correct scoping, not a miss).
    contaminated = (
        "external_heat", "defrost", "cooling", "ventilation", "indoor_dead",
        "away",
    )
    quiet_folds = sum(rows[s]["comfort_quiet"] for s in contaminated)
    print(f"RESULT comfort_quiet_folds_under_contamination={quiet_folds} count")
    # Control: the same learner in a clean interval folds exactly once —
    # the count above is missing gates, not a double-counting instrument.
    print(f"RESULT comfort_quiet_folds_control={rows['none']['comfort_quiet']} count")
    frozen_everywhere_else = sum(
        rows[s][l] for s in contaminated for l in learners
        if l not in ("comfort_quiet", "defrost_derate_exempt")
    )
    print(
        "RESULT thermal_or_cop_folds_under_contamination="
        f"{frozen_everywhere_else} count"
    )
    proc_cpu = time.process_time()
    thread_cpu = time.thread_time()
    print(f"RESULT thread_factor={(proc_cpu / thread_cpu if thread_cpu else 1.0):.2f}")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    swapins = 0
    try:
        with open("/usr/bin/vm_stat", errors="ignore") as fh:
            for line in fh:
                if "swapins" in line:
                    token = line.split()[-1].rstrip(".")
                    if token.isdigit():
                        swapins = int(token)
                    break
    except OSError:
        pass
    print(f"RESULT swapins={swapins}")


if __name__ == "__main__":
    main()
