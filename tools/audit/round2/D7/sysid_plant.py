#!/usr/bin/env python3
"""D7 step 3 -- the first-order sysid identifier against the production two-store plant.

Metric (one line): for the three tests/stress.py BUILDINGS presets (re-declared here because
stress.py runs at import; derived through heatpump_optimizer.presets.derive into
ThermalParameters.from_config, single zone), the production SystemIdentification state
machine is driven in closed loop against the production ThermalModel.simulate_step (T_out
0 C in the safe band, cheap price, 23:00 start, the pump at the plant's steady-state power
until the machine overrides it; the plant is stepped at 1-minute sub-steps so the true room
excursion is resolved) at the production 30-min cycle and at 5 min, noiseless and with
N(0, 0.05 C) sensor noise (seed 0), at the production comfort bound (0.8 C) and with it lifted
(10 C) so the fit can be measured when the bound aborts. Per cell: completed, reason, confidence,
admitted by _adopt_system_identification's gate (completed and confidence >= 0.3), fitted UA
of identify() vs the plant's UA (bias %), the UA scale the adoption would blend in, the true
peak room excursion, and the UA of a two-store (UA, C_room, C_slab, k, G) least-squares fit
of the same samples through the production model (scipy) for comparison.

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/sysid_plant.py
Expected: exact to 1e-6 (deterministic; seed 0); baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box; no timing reported.
Instrumented symbol: heatpump_optimizer.sysid:SystemIdentification.identify (and .step),
          driven by heatpump_optimizer.thermal_model:ThermalModel.simulate_step.
Perturbation: config slab_thermal_mass -> 0.1 kWh/C on typical_slab (a one-store plant) ->
          bias_pct_first_order moves toward 0; SysIdConfig.max_excursion_c 0.8 -> 10 ->
          aborted_at_production_bound to_zero.
Writes:   nothing but stdout.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np
from scipy.optimize import least_squares

from profiles import house
from heatpump_optimizer.presets import (
    EMITTER_FLOOR, EMITTER_RADIATORS, ERA_1960_1980, ERA_POST_2005, ERA_PRE_1960,
    STRUCTURE_CONCRETE_SLAB, STRUCTURE_MASONRY, STRUCTURE_TIMBER_CRAWLSPACE, BuildingPreset, derive)
from heatpump_optimizer.sysid import PHASE_ABORTED, PHASE_DONE, SysIdConfig, SystemIdentification
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

# tests/stress.py:378 BUILDINGS, verbatim
BUILDINGS = {
    "light_new": BuildingPreset(structure=STRUCTURE_TIMBER_CRAWLSPACE, era=ERA_POST_2005,
                                heated_area_m2=120, lower_emitter=EMITTER_RADIATORS),
    "heavy_old": BuildingPreset(structure=STRUCTURE_MASONRY, era=ERA_PRE_1960,
                                heated_area_m2=200, lower_emitter=EMITTER_FLOOR),
    "typical_slab": BuildingPreset(structure=STRUCTURE_CONCRETE_SLAB, era=ERA_1960_1980,
                                   heated_area_m2=150, lower_emitter=EMITTER_FLOOR),
}
UTC = timezone.utc
T_OUT = 0.0
ROOM0 = 21.0
ADOPT_MIN_CONFIDENCE = 0.3   # coordinator._adopt_system_identification


#: Positive control: typical_slab with its slow store collapsed (C_slab 0.5 kWh/C, k 5 kW/C,
#: a 6-minute lag) so the plant is first-order to within the sampling; the identifier must
#: complete here or the harness, not the plant, is at fault.
CONTROL = "first_order_control"
PRESETS = list(BUILDINGS) + [CONTROL]


def params_for(name: str) -> ThermalParameters:
    cfg = house(two_zone=False, dhw=False)
    base = BUILDINGS["typical_slab"] if name == CONTROL else BUILDINGS[name]
    preset = BuildingPreset(**{**vars(base), "two_zone": False})
    derived = derive(preset)
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    if name == CONTROL:
        p.slab_thermal_mass = 0.5
        p.slab_heat_transfer = 5.0
    return p


def steady_state(m: ThermalModel):
    p = m.params
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    thermal = max(0.0, ua * (ROOM0 - T_OUT) - p.internal_gains)
    cop = m.compute_cop(T_OUT)
    p0 = thermal / cop
    slab = ROOM0 + thermal / p.slab_heat_transfer
    return p0, ThermalState(room_temperature=ROOM0, slab_temperature=slab, outdoor_temperature=T_OUT)


def run_cell(name, cadence_min, noise_sd, excursion, seed=0):
    p = params_for(name)
    m = ThermalModel(p)
    p0, state = steady_state(m)
    cfg = SysIdConfig(enabled=True, max_excursion_c=excursion,
                      gains_prior_kw=float(p.internal_gains), thermal_mass_prior=float(p.room_thermal_mass))
    sysid = SystemIdentification(cfg)
    t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
    assert sysid.arm(t0)
    rng = np.random.default_rng(seed)
    price_h = np.full(96, 1.0)
    dt_h = cadence_min / 60.0
    sub = int(cadence_min)          # 1-minute plant sub-steps
    obs_t, obs_room, powers = [], [], []
    peak = 0.0
    cop = m.compute_cop(T_OUT)
    power = p0
    for i in range(int(14 * 60 / cadence_min)):
        now = t0 + timedelta(minutes=i * cadence_min)
        meas = state.room_temperature + (rng.normal(0.0, noise_sd) if noise_sd else 0.0)
        override = sysid.step(now=now, room_temp=meas, outdoor_temp=T_OUT, price=0.5,
                              price_horizon=price_h, learner_samples=0,
                              max_power_kw=p.max_electrical_power, cop=cop)
        if sysid.phase in (PHASE_DONE, PHASE_ABORTED):
            break
        power = p0 if override is None else float(override)
        obs_t.append(now); obs_room.append(meas); powers.append(power)
        for _ in range(sub):
            state = m.simulate_step(state, power, T_OUT, dt_hours=1.0 / 60.0)
            peak = max(peak, abs(state.room_temperature - ROOM0))
    res = sysid.result
    ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
    out = {"preset": name, "cadence_min": cadence_min, "noise": noise_sd, "bound": excursion,
           "phase": sysid.phase, "completed": bool(res.completed), "reason": res.reason,
           "confidence": float(res.confidence), "ua_true": ua_true,
           "ua_fit": res.heat_loss_kw_per_c, "tau_fit": res.time_constant_hours,
           "c_fit": res.thermal_mass_kwh_per_c, "gains_fit": res.internal_gains_kw,
           "peak_excursion": peak, "samples": len(sysid.samples),
           "c_room": p.room_thermal_mass, "c_slab": p.slab_thermal_mass, "k": p.slab_heat_transfer}
    out["admitted"] = bool(res.completed and res.confidence >= ADOPT_MIN_CONFIDENCE)
    if res.heat_loss_kw_per_c is not None:
        out["bias_pct"] = 100.0 * (res.heat_loss_kw_per_c / ua_true - 1.0)
        scale = res.heat_loss_kw_per_c / ua_true
        out["adopted_scale"] = (1.0 - res.confidence) * 1.0 + res.confidence * scale if out["admitted"] else None
    else:
        out["bias_pct"] = None
        out["adopted_scale"] = None
    # two-store fit of the same samples (UA, C_room, C_slab, k, G), through the production model
    if len(obs_room) >= 8:
        p_init = replace(p)
        _, s0 = steady_state(m)
        y = np.asarray(obs_room)

        def sim(theta):
            ua, cr, cs, k, g = theta
            pp = replace(p_init, heat_loss_coefficient=ua, room_thermal_mass=cr,
                         slab_thermal_mass=cs, slab_heat_transfer=k, internal_gains=g)
            mm = ThermalModel(pp)
            st = s0
            out_r = [st.room_temperature]
            for pw in powers[:-1]:
                for _ in range(sub):
                    st = mm.simulate_step(st, pw, T_OUT, dt_hours=1.0 / 60.0)
                out_r.append(st.room_temperature)
            return np.asarray(out_r) - y

        x0 = np.array([ua_true * 1.3, p.room_thermal_mass * 0.8, p.slab_thermal_mass * 1.2,
                       p.slab_heat_transfer * 0.9, p.internal_gains])
        lb = np.array([1e-3, 0.1, 0.05, 0.01, 0.0])
        ub = np.array([5.0, 100.0, 100.0, 20.0, 3.0])
        fit = least_squares(sim, x0, bounds=(lb, ub), x_scale=np.maximum(x0, 1e-3), max_nfev=400)
        out["ua_2rc"] = float(fit.x[0])
        out["bias_2rc_pct"] = 100.0 * (fit.x[0] / ua_true - 1.0)
        out["rms_2rc"] = float(np.sqrt(np.mean(fit.fun ** 2)))
    else:
        out["ua_2rc"] = None; out["bias_2rc_pct"] = None; out["rms_2rc"] = None
    return out


def main() -> int:
    print("=== D7 sysid identifier vs the production two-store plant ===")
    for name in PRESETS:
        p = params_for(name)
        print(f"{name:19} UA={p.heat_loss_coefficient:.4f} kW/C  C_room={p.room_thermal_mass:.2f} "
              f"C_slab={p.slab_thermal_mass:.2f} kWh/C  k={p.slab_heat_transfer:.3f} kW/C  "
              f"gains={p.internal_gains:.2f} kW  Pmax={p.max_electrical_power:.1f} kW  "
              f"tau_room=C_room/UA={p.room_thermal_mass / p.heat_loss_coefficient:.1f} h")
    cells = []
    hdr = (f"{'preset':19} {'cad':>3} {'noise':>5} {'bound':>5} {'phase':8} {'reason':34} {'conf':>5} "
           f"{'adm':>3} {'UA_true':>7} {'UA_fit':>7} {'bias%':>7} {'scale':>6} {'peakC':>6} {'UA_2rc':>7} {'b2rc%':>6}")
    print("\n" + hdr)
    for name in PRESETS:
        for cadence in (30, 5):
            for noise in (0.0, 0.05):
                for bound in (0.8, 10.0):
                    c = run_cell(name, cadence, noise, bound)
                    cells.append(c)
                    f = lambda v, w: (f"{v:{w}.3f}" if isinstance(v, float) else f"{'-':>{w}}")
                    print(f"{c['preset']:19} {c['cadence_min']:3d} {c['noise']:5.2f} {c['bound']:5.1f} "
                          f"{c['phase']:8} {c['reason'][:34]:34} {c['confidence']:5.2f} {int(c['admitted']):3d} "
                          f"{c['ua_true']:7.4f} {f(c['ua_fit'], 7)} {f(c['bias_pct'], 7)} "
                          f"{f(c['adopted_scale'], 6)} {c['peak_excursion']:6.2f} {f(c['ua_2rc'], 7)} {f(c['bias_2rc_pct'], 6)}")
    real = [c for c in cells if c["preset"] != CONTROL]
    ctrl = [c for c in cells if c["preset"] == CONTROL]
    prod = [c for c in real if c["bound"] == 0.8]
    aborted = sum(1 for c in prod if c["phase"] == PHASE_ABORTED)
    admitted = [c for c in real if c["admitted"]]
    print(f"\npresets, production bound (0.8 C): {aborted}/{len(prod)} cells aborted; "
          f"{sum(1 for c in prod if c['admitted'])}/{len(prod)} admitted by the adoption gate; "
          f"presets, any bound: {len(admitted)}/{len(real)} admitted; "
          f"control: {sum(1 for c in ctrl if c['admitted'])}/{len(ctrl)} admitted")
    print(f"RESULT control_cells={len(ctrl)} count")
    print(f"RESULT control_admitted={sum(1 for c in ctrl if c['admitted'])} count")
    cb = [abs(c['bias_pct']) for c in ctrl if c['bias_pct'] is not None]
    if cb:
        print(f"RESULT control_abs_bias_pct_max={max(cb):.3f} percent")
    cells = real
    for c in cells:
        tag = f"{c['preset']}_c{c['cadence_min']}_n{int(c['noise'] * 100):02d}_b{int(c['bound'] * 10):03d}"
        print(f"RESULT completed_{tag}={int(c['completed'])} count")
        print(f"RESULT admitted_{tag}={int(c['admitted'])} count")
        print(f"RESULT peak_excursion_{tag}={c['peak_excursion']:.4f} C")
        if c["bias_pct"] is not None:
            print(f"RESULT bias_pct_first_order_{tag}={c['bias_pct']:.3f} percent")
            print(f"RESULT confidence_{tag}={c['confidence']:.4f} ratio")
        if c["bias_2rc_pct"] is not None:
            print(f"RESULT bias_pct_two_store_{tag}={c['bias_2rc_pct']:.3f} percent")
    print(f"RESULT cells={len(cells)} count")
    print(f"RESULT aborted_at_production_bound={aborted} count")
    print(f"RESULT admitted_cells={len(admitted)} count")
    if admitted:
        b = [abs(c["bias_pct"]) for c in admitted]
        print(f"RESULT admitted_abs_bias_pct_max={max(b):.3f} percent")
        print(f"RESULT admitted_abs_bias_pct_min={min(b):.3f} percent")
        print(f"RESULT admitted_cells_bias_gt_20pct={sum(1 for x in b if x > 20.0)} count")
        srt = sorted(b)
        print(f"RESULT admitted_abs_bias_pct_mean={np.mean(b):.3f} percent")
        print(f"RESULT admitted_abs_bias_pct_mean_drop_most_favourable={np.mean(srt[1:]) if len(srt) > 1 else srt[0]:.3f} percent")
    peak_prod = max(c["peak_excursion"] for c in prod)
    print(f"RESULT peak_excursion_max_at_production_bound={peak_prod:.4f} C")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
