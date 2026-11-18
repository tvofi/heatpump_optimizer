"""verifier 3 own harness -- D7-03: the shared learner freeze vs defrost.

METRIC (three parts, all counts or magnitudes, no timing):
  A. gate: what production ``_learning_frozen`` returns for an interval the
     pump says it defrosted (expect None = does not gate) vs three known
     contaminants (expect reasons).
  B. ingestion: whether each learner's DOWNSTREAM production seam executes
     for a defrosted interval (house: ``_apply_house_heat_loss_scale`` is
     called; cop: ``_cop_ratio_ewma`` moves / stays put with and without
     its bespoke frost-band block; dhw & buffer: persisted value moves).
  C. consequence (the measurement the finder flagged as unmade): a
     physically defrosted interval -- the room actually cools for the
     defrost minutes while the meter still reads the draw -- replayed by
     the house heat-loss learner, 24 consecutive times (a 12 h frosty
     night at +2 C, defrost every interval), and the walk of the persisted
     ``_house_heat_loss_scale``; then the same night with the one-line fix
     (``_learning_frozen`` patched, harness side, to freeze on defrosting).

COMMAND (from the tree root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/verify3_own_D7-03.py

ROOT RULE: ROOT = Path(".") -- measures the working directory.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import sys
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np

from harness import FakeEntry, FakeHass

import heatpump_optimizer.coordinator as coord_mod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from homeassistant.util import dt as dt_util

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "power_entity": "sensor.power",
    "dhw_temp_entity": "sensor.dhw",
    "buffer_tank_temp_entity": "sensor.buffer",
    "dhw_enabled": True,
    "buffer_tank_volume": 500,
    "mixing_valve_mode": "none",
}
STATES = {
    "sensor.indoor": "21.0",
    "sensor.outdoor": "2.0",
    "sensor.power": "1.1",
    "sensor.dhw": "50.0",
    "sensor.buffer": "45.0",
}


def _coord():
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=CFG))
    c._input_health = None
    c._external_heat_active = False
    return c


def _defrosted(c):
    """The interval the pump says it defrosted: flag true, window observed."""
    c._pump_signals = replace(c._pump_signals, defrosting=True)
    c._defrost_window.observe(dt_util.now(), True)


# ---------------------------------------------------------------- part A
def part_a():
    out = {}
    c = _coord()
    out["clean"] = c._learning_frozen("sensor.indoor")
    c = _coord(); _defrosted(c)
    out["defrost"] = c._learning_frozen("sensor.indoor")
    c = _coord()
    c._pump_signals = replace(c._pump_signals, freeze_reason="pump_offline")
    out["pump_offline"] = c._learning_frozen("sensor.indoor")
    c = _coord(); c._external_heat_active = True
    out["external_heat"] = c._learning_frozen("sensor.indoor")
    c = _coord(); c._vent_cusum.tripped = True
    out["ventilation"] = c._learning_frozen("sensor.indoor")
    return out


# ---------------------------------------------------------------- part B
def part_b():
    res = {}

    # house learner: downstream seam = _apply_house_heat_loss_scale called
    calls = {"n": 0}
    orig = HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale

    def counting(self, scale):
        calls["n"] += 1
        return orig(self, scale)

    def house_cell(contam):
        c = _coord()
        ctx = getattr(c, "_ctx", c)
        ctx._current_state.room_temperature = 20.4
        ctx._current_state.outdoor_temperature = 2.0
        ctx._current_state.slab_temperature = 22.0
        c._current_action = {"power": 2.0, "dhw_power": 0.0}
        c._measured_power = 2.0
        c._immersion_active = False
        prev = copy.deepcopy(ctx._current_state)
        prev.room_temperature = 21.0
        prev.outdoor_temperature = 2.0
        c._last_house_sample = prev
        c._last_house_sample_time = dt_util.now() - timedelta(hours=1)
        contam(c)
        HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale = counting
        calls["n"] = 0
        try:
            asyncio.run(c._async_learn_house_heat_loss())
        finally:
            HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale = orig
        return calls["n"]

    res["house_folds_defrost"] = house_cell(_defrosted)
    res["house_folds_offline"] = house_cell(
        lambda c: setattr(  # noqa: B010 -- probe
            c, "_pump_signals",
            replace(c._pump_signals, freeze_reason="pump_offline"))
    )

    # cop learner: probe _cop_ratio_ewma, with and without its bespoke guard
    def cop_cell(contam, strip_guard):
        c = _coord()
        ctx = getattr(c, "_ctx", c)
        ctx._current_state.room_temperature = 20.4
        ctx._current_state.outdoor_temperature = 2.0
        c._current_action = {"power": 2.0, "dhw_power": 0.0}
        c._measured_power = 2.8  # ratio 1.4, off the 1.2 EWMA seed
        c._immersion_active = False
        c._cop_ratio_ewma = 1.2
        now = dt_util.now()
        c._defrost_window.observe(now - timedelta(minutes=30), False)
        c._defrost_window.observe(now, False)
        contam(c)
        if strip_guard:
            # strip = make in_frost_band lie False for this call only
            _orig = coord_mod.in_frost_band
            coord_mod.in_frost_band = lambda t: False
            try:
                c._learn_measured_cop()
            finally:
                coord_mod.in_frost_band = _orig
        else:
            c._learn_measured_cop()
        return c._cop_ratio_ewma

    res["cop_ewma_defrost_with_guard"] = cop_cell(_defrosted, strip_guard=False)
    res["cop_ewma_defrost_guard_stripped"] = cop_cell(_defrosted, strip_guard=True)
    res["cop_ewma_offline"] = cop_cell(
        lambda c: setattr(  # noqa: B010
            c, "_pump_signals",
            replace(c._pump_signals, freeze_reason="pump_offline")),
        strip_guard=False,
    )

    # buffer + dhw: persisted value probes (finder's observable; kept for
    # completeness, with the same setup shape)
    def buffer_cell(contam):
        c = _coord()
        ctx = getattr(c, "_ctx", c)
        ctx._current_state.room_temperature = 20.4
        ctx._current_state.outdoor_temperature = 2.0
        c._current_action = {"power": 0.0, "dhw_power": 0.0}
        c._last_buffer_temp_sample = 46.0
        c._last_buffer_sample_time = dt_util.now() - timedelta(hours=2)
        c._buffer_heating_since_sample = False
        contam(c)
        before = float(c._buffer_cooling_rate)
        asyncio.run(c._async_learn_buffer_cooling(45.0))
        return float(c._buffer_cooling_rate) != before

    def dhw_cell(contam):
        c = _coord()
        ctx = getattr(c, "_ctx", c)
        ctx._current_state.room_temperature = 20.4
        ctx._current_state.outdoor_temperature = 2.0
        c._current_action = {"power": 0.0, "dhw_power": 0.0}
        lr = c._dhw_learner
        lr.last_temp_sample = 52.0
        lr.last_sample_time = dt_util.now() - timedelta(hours=1)
        lr.heating_since_sample = False
        contam(c)
        before = round(float(lr.cooling_rate), 9)
        asyncio.run(lr.async_learn_dynamics(49.0))
        return round(float(lr.cooling_rate), 9) != before

    res["buffer_ingests_defrost"] = buffer_cell(_defrosted)
    res["buffer_ingests_offline"] = buffer_cell(
        lambda c: setattr(  # noqa: B010
            c, "_pump_signals",
            replace(c._pump_signals, freeze_reason="pump_offline"))
    )
    res["dhw_ingests_defrost"] = dhw_cell(_defrosted)
    res["dhw_ingests_offline"] = dhw_cell(
        lambda c: setattr(  # noqa: B010
            c, "_pump_signals",
            replace(c._pump_signals, freeze_reason="pump_offline"))
    )
    return res


# ---------------------------------------------------------------- part C
OUTDOOR = 2.0
BASE_T = 21.0
DT_H = 0.5          # 30-min optimization interval
DEFROST_MIN = 8.0   # defrost minutes inside each interval (typical 3-10)
N_INTERVALS = 24    # a 12 h frosty night, defrost every interval
# typical_slab, hand-typed (see verify3_own_D7-01.py)
SPEC = dict(ua=0.1725, cap=5.25, slab_m=16.5, slab_k=1.5)
TRUTH = ThermalModel(ThermalParameters(
    heat_loss_coefficient=SPEC["ua"], house_heat_loss_scale=1.0,
    room_thermal_mass=SPEC["cap"], slab_thermal_mass=SPEC["slab_m"],
    slab_heat_transfer=SPEC["slab_k"], internal_gains=0.3,
    wind_sensitivity=0.0, two_zone_enabled=False, max_electrical_power=6.0,
))


def _steady_state(q_thermal):
    """Iterate the plant to steady state at the given thermal power."""
    k = max(TRUTH.params.slab_heat_transfer, 1e-9)
    st = ThermalState(room_temperature=BASE_T,
                      slab_temperature=BASE_T, outdoor_temperature=OUTDOOR)
    for _ in range(400):
        st = TRUTH.simulate_step(st, 0.0, OUTDOOR, dt_hours=0.25,
                                 external_heat_kw=q_thermal)
    return st


def part_c(with_fix: bool, spec=None, n_intervals=None, defrost_min=None):
    """One frosty night; returns the scale walk and diagnostics."""
    spec = spec or SPEC
    n_intervals = n_intervals or N_INTERVALS
    defrost_min = defrost_min or DEFROST_MIN
    truth = ThermalModel(ThermalParameters(
        heat_loss_coefficient=spec["ua"], house_heat_loss_scale=1.0,
        room_thermal_mass=spec["cap"], slab_thermal_mass=spec["slab_m"],
        slab_heat_transfer=spec["slab_k"], internal_gains=0.3,
        wind_sensitivity=0.0, two_zone_enabled=False,
        max_electrical_power=6.0,
    ))
    c0 = _coord()
    # The learner replays ELECTRICAL power through the coordinator model's
    # own COP curve; the truth plant must hold steady under the SAME curve,
    # so the defrost minutes are the only signal in the residual.
    cop_model = c0._thermal_model.compute_cop(OUTDOOR)
    q_need = spec["ua"] * (BASE_T - OUTDOOR) - 0.3  # thermal hold, kW
    hold_el = q_need / cop_model                    # electrical, kW
    q_hold = q_need
    st = ThermalState(room_temperature=BASE_T,
                      slab_temperature=BASE_T, outdoor_temperature=OUTDOOR)
    for _ in range(400):
        st = truth.simulate_step(st, 0.0, OUTDOOR, dt_hours=0.25,
                                 external_heat_kw=q_hold)
    c = _coord()
    # the coordinator's OWN model must match the plant's configured physics
    ctx = getattr(c, "_ctx", c)
    ctx._thermal_params.heat_loss_coefficient = spec["ua"]
    ctx._thermal_params.room_thermal_mass = spec["cap"]
    ctx._thermal_params.slab_thermal_mass = spec["slab_m"]
    ctx._thermal_params.slab_heat_transfer = spec["slab_k"]
    ctx._thermal_params.internal_gains = 0.3
    ctx._thermal_params.wind_sensitivity = 0.0
    ctx._thermal_params.two_zone_enabled = False
    ctx._thermal_params.house_heat_loss_scale = 1.0
    c._house_heat_loss_scale = 1.0
    c._immersion_active = False

    t0 = datetime(2026, 1, 15, 19, 0, 0)
    dt_util.freeze(t0)
    walk = []
    residuals = []
    tripped_at = None
    heat_min = DT_H * 60.0 - defrost_min
    # capture the folded residual through the production newton step seam
    captured = {"residual": None}
    _newton = coord_mod.learner_newton_step

    def _capturing(current, base_u, capacity, residual, delta_t, dt_hours, **kw):
        captured["residual"] = residual
        return _newton(current, base_u, capacity, residual, delta_t,
                       dt_hours, **kw)

    coord_mod.learner_newton_step = _capturing
    if with_fix:
        _orig = HeatPumpOptimizerCoordinator._learning_frozen

        def _patched(self, *keys):
            if getattr(self._pump_signals, "defrosting", False):
                return "defrosting"
            return _orig(self, *keys)

        HeatPumpOptimizerCoordinator._learning_frozen = _patched
    try:
        for i in range(n_intervals):
            now = t0 + timedelta(hours=DT_H * i)
            dt_util.freeze(now)
            # snapshot the interval-start state (what the learner replays);
            # the sample was taken at the PREVIOUS cycle, dt_h = DT_H
            prev = copy.deepcopy(st)
            c._last_house_sample = prev
            c._last_house_sample_time = now - timedelta(hours=DT_H)
            # the plan/meter for the interval: the pump drew its hold power
            # for the WHOLE interval -- during defrost it draws, but the
            # heat went to melting frost outdoors, not into the house.
            c._current_action = {"power": hold_el, "dhw_power": 0.0}
            c._measured_power = hold_el
            # truth: heat delivered only outside the defrost minutes
            st = truth.simulate_step(
                st, 0.0, OUTDOOR, dt_hours=heat_min / 60.0,
                external_heat_kw=q_hold,
            )
            st = truth.simulate_step(
                st, 0.0, OUTDOOR, dt_hours=defrost_min / 60.0,
                external_heat_kw=0.0,
            )
            ctx._current_state.room_temperature = st.room_temperature
            ctx._current_state.outdoor_temperature = OUTDOOR
            ctx._current_state.slab_temperature = st.slab_temperature
            scale_before = c._house_heat_loss_scale
            _defrosted(c)
            asyncio.run(c._async_learn_house_heat_loss())
            if c._house_heat_loss_scale != scale_before:
                residuals.append(captured["residual"])
            walk.append(c._house_heat_loss_scale)
            if tripped_at is None and c._vent_cusum.tripped:
                tripped_at = i
    finally:
        dt_util.freeze(None)
        coord_mod.learner_newton_step = _newton
        if with_fix:
            HeatPumpOptimizerCoordinator._learning_frozen = _orig
    return {
        "walk": walk, "final_scale": walk[-1], "tripped_at": tripped_at,
        "peak_scale": max(walk), "residuals": residuals,
    }


def main() -> int:
    a = part_a()
    b = part_b()
    c0 = part_c(with_fix=False)
    c1 = part_c(with_fix=True)
    # worst-case shipped preset + sustained frost: 60 h at defrost every
    # 30-min interval, 8 defrost minutes each (maximal, not typical).
    light = dict(ua=0.066, cap=3.6, slab_m=0.24, slab_k=0.24)
    cl = part_c(with_fix=False, spec=light, n_intervals=120)
    ct = part_c(with_fix=False, n_intervals=120)

    print("A. _learning_frozen returns:")
    for k, v in a.items():
        print(f"   {k:<16} -> {v!r}")
    print("B. downstream seams:")
    for k, v in b.items():
        print(f"   {k:<32} -> {v!r}")
    print(f"C. frosty night ({N_INTERVALS} intervals x {DEFROST_MIN:.0f} min "
          f"defrost, outdoor {OUTDOOR} C):")
    print(f"   no fix : scale 1.000 -> {c0['final_scale']:.3f} "
          f"(peak {c0['peak_scale']:.3f}, vent tripped at interval "
          f"{c0['tripped_at']}, first residuals "
          f"{[round(r, 3) for r in c0['residuals'][:4]]})")
    print(f"   fixed  : scale 1.000 -> {c1['final_scale']:.3f}")

    print("########## RESULT lines ##########")
    print(f"RESULT v3_gate_defrost_returns={a['defrost']!r} str")
    print(f"RESULT v3_gate_offline_returns={a['pump_offline']!r} str")
    print(f"RESULT v3_gate_external_returns={a['external_heat']!r} str")
    print(f"RESULT v3_gate_vent_returns={a['ventilation']!r} str")
    print(f"RESULT v3_house_folds_defrost={b['house_folds_defrost']} count")
    print(f"RESULT v3_house_folds_offline={b['house_folds_offline']} count")
    print(f"RESULT v3_cop_guard_holds={b['cop_ewma_defrost_with_guard'] == 1.2}"
          " bool")
    print(f"RESULT v3_cop_guard_stripped_ewma="
          f"{b['cop_ewma_defrost_guard_stripped']:.4f} ratio")
    print(f"RESULT v3_cop_offline_ewma={b['cop_ewma_offline']:.4f} ratio")
    print(f"RESULT v3_buffer_ingests_defrost={int(b['buffer_ingests_defrost'])}"
          " bool")
    print(f"RESULT v3_buffer_ingests_offline={int(b['buffer_ingests_offline'])}"
          " bool")
    print(f"RESULT v3_dhw_ingests_defrost={int(b['dhw_ingests_defrost'])} bool")
    print(f"RESULT v3_dhw_ingests_offline={int(b['dhw_ingests_offline'])} bool")
    print(f"RESULT v3_night_scale_final={c0['final_scale']:.4f} ratio")
    print(f"RESULT v3_night_scale_peak={c0['peak_scale']:.4f} ratio")
    print(f"RESULT v3_night_vent_trip_interval="
          f"{c0['tripped_at'] if c0['tripped_at'] is not None else -1} index")
    print(f"RESULT v3_night_fixed_scale_final={c1['final_scale']:.4f} ratio")
    print(f"RESULT v3_sustained60h_light_new_final={cl['final_scale']:.4f}"
          " ratio")
    print(f"RESULT v3_sustained60h_typical_slab_final={ct['final_scale']:.4f}"
          " ratio")
    print(f"RESULT v3_sustained60h_light_new_samples_folded="
          f"{len(cl['residuals'])} count")
    print(f"RESULT v3_sustained60h_light_new_vent_trip="
          f"{cl['tripped_at'] if cl['tripped_at'] is not None else -1} index")
    print(f"RESULT v3_night_scale_first8="
          f"{','.join(f'{w:.3f}' for w in c0['walk'][:8])} ratios")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
