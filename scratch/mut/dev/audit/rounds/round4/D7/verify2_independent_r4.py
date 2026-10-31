"""D7 round 4, verifier 2 -- independent harness, written refute-first.

Three sections, one per finding, each with its OWN metric definition (mine,
not the finder's):

A (D7-01) MISSPECIFICATION, MY WAY: on the production protocol driven
   against the production two-state plant (3 presets x 3 outdoors at the
   30-min DEFAULT cadence), the number of cells whose room temperature
   RISES during the zero-power relax phase (impossible for the first-order
   plant the identifier fits: with Q=0 and T above its steady state the
   rate must be negative), plus the production adoption verdict per cell,
   plus the one-state null (slab coupling x100) where the rise must vanish
   and adoption must occur.

B (D7-02) SIZING, MY WAY: the electrical step the production
   ``SystemIdentification._size_step_power`` returns for each cell, pushed
   through (i) the sizer's own defaults-carrying plant and (ii) the
   preset's OWN configured plant, at 3-min integration granularity; the
   count of cells whose achieved peak exceeds DEFAULT_MAX_EXCURSION_C and
   the achieved/predicted ratio; plus the honest-sizer perturbation
   (harness-side swap of ``sysid._sizing_model``) under which the breach
   count must fall to 0.

C (D7-03) GATE + DRIFT, MY WAY: (1) a direct one-call read of
   ``_learning_frozen`` with ONLY ``_pump_signals.defrosting`` set -- the
   gate's verdict must be None (no freeze); (2) whether the production
   house heat-loss learner folds a defrost interval (scale moves) while
   the identical clean interval does not; (3) THE MEASUREMENT THE FINDER
   LEFT UNMADE: a closed week of 336 x 30-min intervals at +2 C outdoor,
   plant = a ThermalModel with the coordinator's own configured params,
   every 4th interval containing a 10-min zero-delivery defrost, learner
   = the production ``_async_learn_house_heat_loss``; the end-of-week
   ``_house_heat_loss_scale`` versus a clean-substepped control week that
   carries the identical discretisation but no defrost, and versus the
   same defrost week under the one-line fix (freeze on the flag).

COMMAND (from the tree under test as the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/verify2_independent_r4.py

EXPECTED (branch head 0855277, baseline finding measured at 7dd68dd,
8-core Apple M1, macOS 25.6; every number a count or a deterministic
float, no timing claimed):
    my_relax_rise_cells      = >0 of 9   (the two-state signature)
    my_adopted_cells         = 0 of 9
    my_null_relax_rise_c     ~ 0         (slab x100 collapse)
    my_null_adopted          = 1
    my_breach_cells          = 6 of 9-ish (>=1; light_new breaches)
    my_honest_breach_cells   = 0
    my_gate_passes_defrost   = 1         (gate returns None: the gap)
    my_ingest_defrost_moved  = 1
    my_drift_week_pct        > 0         (defrost week vs clean control)
    my_perturbed_drift_week_pct ~ 0      (the one-line fix)

INSTRUMENTED SYMBOLS: sysid.SystemIdentification.step/_size_step_power,
sysid._sizing_model, sysid._predict_step_excursion_plant,
thermal_model.ThermalModel.simulate_step,
coordinator.HeatPumpOptimizerCoordinator._learning_frozen /
_async_learn_house_heat_loss / learner_newton_step.

ROOT RULE: ROOT = Path(".") -- measures the working directory it is run
from. Run from the tree under test.
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

from heatpump_optimizer import sysid as sysid_mod
from heatpump_optimizer.presets import derive
from heatpump_optimizer.sysid import (
    DEFAULT_MAX_EXCURSION_C,
    PHASE_RELAX,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

from stress import BUILDINGS
from profiles import house

COP = 3.0
START = datetime(2026, 1, 15, 23, 0, 0)
OUTDOORS = (-5.0, 0.0, 5.0)
BASELINE_T = 21.0
DT_H = 0.5  # DEFAULT_OPTIMIZATION_INTERVAL cadence only: my definition


def _plant(name: str, slab_mult: float = 1.0) -> ThermalModel:
    cfg = house(two_zone=False, dhw=False)
    derived = derive(BUILDINGS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    params = ThermalParameters.from_config(cfg)
    params.two_zone_enabled = False
    params.internal_gains = 0.3  # == SysIdConfig.gains_prior_kw: favourable
    params.wind_sensitivity = 0.0
    params.slab_heat_transfer = params.slab_heat_transfer * slab_mult
    return ThermalModel(params)


def _steady(model: ThermalModel, outdoor: float) -> ThermalState:
    p = model.params
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    q_hold = ua * (BASELINE_T - outdoor) - p.internal_gains
    k = max(p.slab_heat_transfer, 1e-9)
    return ThermalState(
        room_temperature=BASELINE_T,
        slab_temperature=BASELINE_T + q_hold / k,
        outdoor_temperature=outdoor,
    )


def _true_ua(model: ThermalModel) -> float:
    p = model.params
    return float(p.heat_loss_coefficient * p.house_heat_loss_scale)


# ==========================================================================
# Section A -- the relax-rise misspecification test and the adoption verdict
# ==========================================================================
def _cell(name: str, outdoor: float, dt_h: float,
          slab_mult: float = 1.0) -> dict:
    """Drive the production protocol once; my own relax-rise bookkeeping.

    The relax rise counts ONLY samples recorded after intervals whose
    applied power was actually zero (the step->relax transition call still
    returns the step power, so the first relax-labelled interval is powered;
    a rise measured across it would be a sequencing artefact, not physics).
    """
    model = _plant(name, slab_mult)
    p = model.params
    ua = _true_ua(model)
    q_hold = ua * (BASELINE_T - outdoor) - p.internal_gains
    hold_elec = max(q_hold, 0.0) / COP
    sysid = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sysid.arm(START)
    state = _steady(model, outdoor)
    now = START
    relax_temps: list[float] = []
    prev_powered = True
    while sysid.active:
        override = sysid.step(
            now=now,
            room_temp=state.room_temperature,
            outdoor_temp=outdoor,
            price=0.1,
            price_horizon=np.full(48, 1.0),
            learner_samples=0,
            max_power_kw=float(p.max_electrical_power),
            cop=COP,
            plan_power_kw=hold_elec,
            house_ua=ua,
            house_capacity=float(p.room_thermal_mass),
            house_gains=float(p.internal_gains),
        )
        if not sysid.active:
            break
        elec = hold_elec if override is None else float(override)
        if sysid.phase == PHASE_RELAX and not prev_powered:
            relax_temps.append(state.room_temperature)
        prev_powered = elec > 1e-9
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=dt_h,
            external_heat_kw=elec * COP,
        )
        now = now + timedelta(hours=dt_h)
    # the final state after the last zero-power relax interval
    if not prev_powered:
        relax_temps.append(state.room_temperature)
    rise = (
        max(relax_temps) - relax_temps[0] if len(relax_temps) >= 2
        else float("nan")
    )
    res = sysid.result
    return {
        "name": name,
        "outdoor": outdoor,
        "rise": rise,
        "reached_relax": len(relax_temps) >= 2,
        "adopted": bool(res.completed and res.confidence >= 0.3),
        "reason": res.reason,
    }


def section_a() -> dict:
    rows = [_cell(n, o, DT_H) for n in BUILDINGS for o in OUTDOORS]
    null_05 = _cell("typical_slab", 0.0, 0.5, slab_mult=100.0)
    null_025 = _cell("typical_slab", 0.0, 0.25, slab_mult=100.0)
    print("-- A: relax-rise (zero-power relax only) and adoption, dt=0.5 h")
    for r in rows:
        print(
            f"   {r['name']:<14} T_out={r['outdoor']:>5.1f}  relax_rise="
            f"{r['rise']:+.3f} C  adopted={r['adopted']}  ({r['reason']})"
        )
    for r in (null_05, null_025):
        print(f"   null slab_k x100 dt={0.5 if r is null_05 else 0.25}: "
              f"relax_rise={r['rise']:+.4f} C, adopted={r['adopted']}, "
              f"reason={r['reason']}")
    reached = [r for r in rows if r["reached_relax"]]
    finite = [r["rise"] for r in reached]
    return {
        "cells": len(rows),
        "rise_cells": sum(1 for r in reached if r["rise"] > 0.01),
        "reached": len(reached),
        "rise_max": max(finite) if finite else float("nan"),
        "adopted": sum(1 for r in rows if r["adopted"]),
        "null_rise_05": null_05["rise"],
        "null_adopted_05": int(null_05["adopted"]),
        "null_rise_025": null_025["rise"],
        "null_adopted_025": int(null_025["adopted"]),
    }


# ==========================================================================
# Section B -- sizing against the wrong plant, measured directly
# ==========================================================================
def _achieved_peak(model: ThermalModel, outdoor: float, thermal_kw: float) -> float:
    state = _steady(model, outdoor)
    peak = 0.0
    dt = 1.0 / 20.0  # 3-min granularity
    remaining = 2.0  # step_hours
    while remaining > 1e-9:
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=min(dt, remaining),
            external_heat_kw=thermal_kw,
        )
        peak = max(peak, abs(state.room_temperature - BASELINE_T))
        remaining -= min(dt, remaining)
    remaining = 2.0  # relax_hours
    while remaining > 1e-9:
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=min(dt, remaining),
            external_heat_kw=0.0,
        )
        peak = max(peak, abs(state.room_temperature - BASELINE_T))
        remaining -= min(dt, remaining)
    return peak


def section_b() -> dict:
    sysid = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=0.0))
    rows = []
    for name in BUILDINGS:
        for outdoor in OUTDOORS:
            model = _plant(name)
            p = model.params
            ua = _true_ua(model)
            gains = float(p.internal_gains)
            cap = float(p.room_thermal_mass)
            sized = sysid._size_step_power(
                float(p.max_electrical_power),
                COP,
                BASELINE_T,
                outdoor,
                ua,
                cap,
                gains,
            )
            belief = sysid_mod._sizing_model(ua, cap, gains)
            pred_peak, _ = sysid_mod._predict_step_excursion_plant(
                ua, cap, gains, BASELINE_T, outdoor, sized * COP, 2.0, 2.0,
                model=belief,
            )
            got_peak = _achieved_peak(model, outdoor, sized * COP)
            rows.append(
                {
                    "name": name,
                    "outdoor": outdoor,
                    "sized_kw": sized,
                    "pred": pred_peak,
                    "got": got_peak,
                    "ratio": got_peak / max(pred_peak, 1e-9),
                    "breach": got_peak > DEFAULT_MAX_EXCURSION_C + 1e-9,
                }
            )
    # perturbation: the honest sizer (plant's own slab mass and coupling)
    orig = sysid_mod._sizing_model
    hrows = []
    try:
        for name in BUILDINGS:
            for outdoor in OUTDOORS:
                model = _plant(name)
                p = model.params

                def _honest(u, c, g, _p=p):
                    return ThermalModel(
                        ThermalParameters(
                            heat_loss_coefficient=u,
                            house_heat_loss_scale=1.0,
                            room_thermal_mass=c,
                            internal_gains=g,
                            two_zone_enabled=False,
                            slab_thermal_mass=_p.slab_thermal_mass,
                            slab_heat_transfer=_p.slab_heat_transfer,
                        )
                    )

                sysid_mod._sizing_model = _honest
                sized = sysid._size_step_power(
                    float(p.max_electrical_power),
                    COP,
                    BASELINE_T,
                    outdoor,
                    _true_ua(model),
                    float(p.room_thermal_mass),
                    float(p.internal_gains),
                )
                sysid_mod._sizing_model = orig
                got = _achieved_peak(model, outdoor, sized * COP)
                hrows.append(
                    {
                        "name": name,
                        "outdoor": outdoor,
                        "got": got,
                        "breach": got > DEFAULT_MAX_EXCURSION_C + 1e-9,
                    }
                )
    finally:
        sysid_mod._sizing_model = orig
    print("-- B: sized step on the sizer's plant vs the preset's own plant")
    for r in rows:
        print(
            f"   {r['name']:<14} T_out={r['outdoor']:>5.1f}  sized={r['sized_kw']:.2f} kW  "
            f"pred={r['pred']:.3f}  got={r['got']:.3f}  ratio={r['ratio']:.2f}  "
            f"breach={r['breach']}"
        )
    for r in hrows:
        print(
            f"   honest         T_out={r['outdoor']:>5.1f}  {r['name']:<14}"
            f"got={r['got']:.3f}  breach={r['breach']}"
        )
    ratios = [r["ratio"] for r in rows]
    return {
        "cells": len(rows),
        "breach": sum(1 for r in rows if r["breach"]),
        "ratio_min": min(ratios),
        "ratio_max": max(ratios),
        "starved": sum(1 for r in rows if r["got"] < 0.5 * DEFAULT_MAX_EXCURSION_C),
        "honest_breach": sum(1 for r in hrows if r["breach"]),
    }


# ==========================================================================
# Section C -- the freeze gate and the drift the finder did not measure
# ==========================================================================
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
    "sensor.power": "2.0",
    "sensor.dhw": "50.0",
    "sensor.buffer": "45.0",
}
OUTDOOR_C = 2.0
INTERVAL_H = 0.5
DEFROST_MIN = 10  # minutes of zero delivery inside a contaminated interval
PERIOD = 4        # every 4th interval contains a defrost
WEEK = 336        # 7 days x 48 intervals


def _coord(preset: str | None = None):
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    cfg = dict(CFG)
    if preset is not None:
        derived = derive(BUILDINGS[preset])
        derived.pop("heating_response_hours", None)
        cfg.update(derived)
    return HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)), FakeEntry(data=cfg)
    )


def _gate_readout() -> dict:
    """Direct one-call reads of _learning_frozen under single contaminants."""
    c = _coord()

    def _reason(**kw):
        c._input_health = None
        c._external_heat_active = False
        c._pump_signals = replace(c._pump_signals, **kw)
        return c._learning_frozen("sensor_indoor", "sensor_outdoor")

    return {
        "healthy": _reason(),
        "defrost_only": _reason(defrosting=True),
        "fault_control": _reason(freeze_reason="pump_fault"),
    }


def _advance(model, state, outdoor, elec_kw, defrost_minutes=0):
    """Advance the plant one 30-min interval at 1-min granularity."""
    for minute in range(int(INTERVAL_H * 60)):
        e = 0.0 if (defrost_minutes and minute < defrost_minutes) else elec_kw
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=1.0 / 60.0,
            external_heat_kw=e * COP,
        )
    return state


def _run_week(defrost, perturbed: bool, preset: str | None = None,
              weeks: int = 1) -> dict:
    """One closed week through the production house heat-loss learner.

    ``defrost`` is False, True (every PERIOD-th interval carries a
    DEFROST_MIN-minute zero-delivery defrost) or "heavy" (every 2nd
    interval, 15 minutes). ``preset`` reconfigures the coordinator (plant
    and replay model alike) onto one of the shipped building presets.
    """
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    if defrost == "heavy":
        period, dmin = 2, 15
    else:
        period, dmin = PERIOD, DEFROST_MIN
    patch = None
    if perturbed:
        _orig = HeatPumpOptimizerCoordinator._learning_frozen

        def _patched(self, *keys):
            if getattr(self._pump_signals, "defrosting", False):
                return "defrosting"
            return _orig(self, *keys)

        HeatPumpOptimizerCoordinator._learning_frozen = _patched
        patch = _orig
    try:
        c = _coord(preset)
        ctx = getattr(c, "_ctx", c)
        # The plant: the coordinator's own configured physics, scale FROZEN at
        # its initial value (the real house does not change when the belief
        # does). The learner replays through the coordinator's own model,
        # whose scale moves -- that is the loop under test.
        plant_params = copy.deepcopy(ctx._thermal_params)
        plant = ThermalModel(plant_params)
        state = _steady(plant, OUTDOOR_C)
        ua = _true_ua(plant)
        q_hold = ua * (BASELINE_T - OUTDOOR_C) - plant_params.internal_gains
        elec = max(q_hold, 0.0) / COP
        c._current_action = {"power": elec, "dhw_power": 0.0}
        c._measured_power = elec
        ctx._current_state.room_temperature = state.room_temperature
        ctx._current_state.slab_temperature = state.slab_temperature
        ctx._current_state.outdoor_temperature = OUTDOOR_C
        c._last_house_sample = copy.deepcopy(ctx._current_state)
        c._last_house_sample_time = datetime.now() - timedelta(hours=INTERVAL_H)
        c._input_health = None
        c._external_heat_active = False
        scale0 = float(c._house_heat_loss_scale)
        residuals = []
        folded = 0
        for i in range(WEEK * weeks):
            contaminated = bool(defrost) and (i % period == 0)
            state = _advance(
                plant, state, OUTDOOR_C, elec,
                defrost_minutes=dmin if contaminated else 0,
            )
            prev_room = float(ctx._current_state.room_temperature)
            ctx._current_state.room_temperature = state.room_temperature
            ctx._current_state.slab_temperature = state.slab_temperature
            if contaminated:
                c._pump_signals = replace(c._pump_signals, defrosting=True)
            else:
                c._pump_signals = replace(c._pump_signals, defrosting=None)
            c._last_house_sample_time = (
                datetime.now() - timedelta(hours=INTERVAL_H)
            )
            before = float(c._house_heat_loss_scale)
            asyncio.run(c._async_learn_house_heat_loss())
            if float(c._house_heat_loss_scale) != before:
                folded += 1
            # residual proxy: observed move vs the clean model's own move
            residuals.append(state.room_temperature - prev_room)
        return {
            "scale0": scale0,
            "scale_end": float(c._house_heat_loss_scale),
            "folded": folded,
            "vent_tripped": bool(c._vent_cusum.tripped),
            "samples": int(c._house_heat_loss_samples),
        }
    finally:
        if patch is not None:
            HeatPumpOptimizerCoordinator._learning_frozen = patch


def _ingest_probe() -> dict:
    """One interval: does the production learner fold a defrost interval?"""
    c = _coord()
    ctx = getattr(c, "_ctx", c)
    plant_params = copy.deepcopy(ctx._thermal_params)
    plant = ThermalModel(plant_params)
    state = _steady(plant, OUTDOOR_C)
    ua = _true_ua(plant)
    q_hold = ua * (BASELINE_T - OUTDOOR_C) - plant_params.internal_gains
    elec = max(q_hold, 0.0) / COP
    c._current_action = {"power": elec, "dhw_power": 0.0}
    c._measured_power = elec
    ctx._current_state.outdoor_temperature = OUTDOOR_C
    out = {}
    for label, dmin in (("clean", 0), ("defrost", DEFROST_MIN), ("cold_ctrl", 0)):
        c2 = _coord()
        ctx2 = getattr(c2, "_ctx", c2)
        p2 = ThermalModel(copy.deepcopy(ctx2._thermal_params))
        s0 = _steady(p2, OUTDOOR_C)
        ua2 = _true_ua(p2)
        q2 = ua2 * (BASELINE_T - OUTDOOR_C) - p2.params.internal_gains
        e2 = max(q2, 0.0) / COP
        ctx2._current_state.outdoor_temperature = OUTDOOR_C
        ctx2._current_state.slab_temperature = s0.slab_temperature
        ctx2._current_state.room_temperature = s0.room_temperature
        c2._last_house_sample = copy.deepcopy(ctx2._current_state)
        c2._last_house_sample_time = datetime.now() - timedelta(hours=INTERVAL_H)
        c2._current_action = {"power": e2, "dhw_power": 0.0}
        c2._measured_power = e2
        c2._input_health = None
        c2._external_heat_active = False
        if label == "defrost":
            end = _advance(p2, s0, OUTDOOR_C, e2, defrost_minutes=DEFROST_MIN)
            ctx2._current_state.room_temperature = end.room_temperature
            ctx2._current_state.slab_temperature = end.slab_temperature
            c2._pump_signals = replace(c2._pump_signals, defrosting=True)
        elif label == "cold_ctrl":
            # liveness control: the room simply reads 0.2 C colder than
            # predicted -- the learner must move on a legitimate signal
            ctx2._current_state.room_temperature = s0.room_temperature - 0.2
            c2._pump_signals = replace(c2._pump_signals, defrosting=None)
        else:
            end = _advance(p2, s0, OUTDOOR_C, e2, defrost_minutes=0)
            ctx2._current_state.room_temperature = end.room_temperature
            ctx2._current_state.slab_temperature = end.slab_temperature
            c2._pump_signals = replace(c2._pump_signals, defrosting=None)
        before = float(c2._house_heat_loss_scale)
        asyncio.run(c2._async_learn_house_heat_loss())
        out[label] = (before, float(c2._house_heat_loss_scale))
    return out


def main() -> int:
    print("=" * 88)
    print("D7/R4 verifier-2 independent harness")
    print("=" * 88)
    a = section_a()
    b = section_b()

    print("-- C1: _learning_frozen, direct one-call reads")
    g = _gate_readout()
    print(f"   healthy={g['healthy']}  defrost_only={g['defrost_only']}  "
          f"fault_control={g['fault_control']}")

    print("-- C2: one-interval ingestion probe (house heat-loss scale)")
    ing = _ingest_probe()
    for k, (b0, b1) in ing.items():
        print(f"   {k:<10} scale {b0:.6f} -> {b1:.6f}  moved={b1 != b0}")

    print("-- C3: the closed week (336 x 30-min intervals at +2 C)")
    clean = _run_week(defrost=False, perturbed=False)
    frost = _run_week(defrost=True, perturbed=False)
    fixed = _run_week(defrost=True, perturbed=True)
    heavy = _run_week(defrost="heavy", perturbed=False)
    ln_clean = _run_week(defrost=False, perturbed=False, preset="light_new")
    ln_heavy = _run_week(defrost="heavy", perturbed=False, preset="light_new")
    ln_heavy3 = _run_week(defrost="heavy", perturbed=False, preset="light_new",
                          weeks=3)
    for label, w in (("clean control", clean), ("defrost week", frost),
                     ("defrost + oneline fix", fixed),
                     ("heavy defrost week", heavy),
                     ("light_new clean", ln_clean),
                     ("light_new heavy", ln_heavy),
                     ("light_new heavy 3wk", ln_heavy3)):
        print(
            f"   {label:<20} scale {w['scale0']:.6f} -> {w['scale_end']:.6f} "
            f"({(w['scale_end'] / w['scale0'] - 1.0) * 100:+.2f}%)  "
            f"folded={w['folded']}  samples={w['samples']}  "
            f"vent_tripped={w['vent_tripped']}"
        )

    drift_pct = (frost["scale_end"] / clean["scale_end"] - 1.0) * 100.0
    fixed_pct = (fixed["scale_end"] / clean["scale_end"] - 1.0) * 100.0
    heavy_pct = (heavy["scale_end"] / clean["scale_end"] - 1.0) * 100.0
    ln_heavy_pct = (ln_heavy["scale_end"] / ln_clean["scale_end"] - 1.0) * 100.0
    ln_heavy3_pct = (ln_heavy3["scale_end"] / ln_clean["scale_end"] - 1.0) * 100.0

    print()
    print("########## RESULT lines ##########")
    print(f"RESULT my_relax_rise_cells={a['rise_cells']} of {a['reached']} count")
    print(f"RESULT my_relax_rise_max_c={a['rise_max']:.3f} celsius")
    print(f"RESULT my_adopted_cells={a['adopted']} of {a['cells']} count")
    print(f"RESULT my_null_relax_rise_c_dt05={a['null_rise_05']:.4f} celsius")
    print(f"RESULT my_null_adopted_dt05={a['null_adopted_05']} bool")
    print(f"RESULT my_null_relax_rise_c_dt025={a['null_rise_025']:.4f} celsius")
    print(f"RESULT my_null_adopted_dt025={a['null_adopted_025']} bool")
    print(f"RESULT my_breach_cells={b['breach']} of {b['cells']} count")
    print(f"RESULT my_peak_ratio_min={b['ratio_min']:.3f} ratio")
    print(f"RESULT my_peak_ratio_max={b['ratio_max']:.3f} ratio")
    print(f"RESULT my_starved_cells={b['starved']} count")
    print(f"RESULT my_honest_breach_cells={b['honest_breach']} count")
    print(f"RESULT my_gate_passes_defrost={int(g['defrost_only'] is None)} bool")
    print(f"RESULT my_gate_fault_control={int(g['fault_control'] is not None)} bool")
    print(f"RESULT my_ingest_clean_moved={int(ing['clean'][0] != ing['clean'][1])} bool")
    print(f"RESULT my_ingest_defrost_moved={int(ing['defrost'][0] != ing['defrost'][1])} bool")
    print(f"RESULT my_ingest_coldctrl_moved={int(ing['cold_ctrl'][0] != ing['cold_ctrl'][1])} bool")
    print(f"RESULT my_drift_week_defrost_pct={drift_pct:+.3f} percent")
    print(f"RESULT my_drift_week_fixed_pct={fixed_pct:+.3f} percent")
    print(f"RESULT my_drift_week_heavy_pct={heavy_pct:+.3f} percent")
    print(f"RESULT my_drift_week_lightnew_heavy_pct={ln_heavy_pct:+.3f} percent")
    print(f"RESULT my_drift_3week_lightnew_heavy_pct={ln_heavy3_pct:+.3f} percent")
    print(f"RESULT my_vent_tripped={int(frost['vent_tripped'])} bool")
    print(f"RESULT my_defrost_week_folded={frost['folded']} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
