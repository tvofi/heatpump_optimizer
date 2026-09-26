"""Prototype: the R8-P5b runner (tests/features.py _z1524_run) with a free-heat axis."""
import sys, time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
from profiles import house as _grad_house
from stress import BUILDINGS as _b942
from heatpump_optimizer import presets, sysid as S
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
night = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)

def run(name, two_zone, true_ua=1.0, true_mass=1.0, true_gains=0.0, prod_prior=False):
    cfg = _grad_house(two_zone=two_zone, dhw=False)
    derived = presets.derive(presets.BuildingPreset(**{**vars(_b942[name]), "two_zone": two_zone}))
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    declared = ThermalParameters.from_config(cfg)
    declared.wind_sensitivity = 0.0
    plant = ThermalModel(replace(declared, house_heat_loss_scale=true_ua,
        room_thermal_mass=declared.room_thermal_mass * true_mass,
        upper_floor_thermal_mass=declared.upper_floor_thermal_mass * true_mass,
        lower_floor_thermal_mass=declared.lower_floor_thermal_mass * true_mass,
        internal_gains=declared.internal_gains + true_gains))
    cop = plant.compute_cop(0.0)
    base_ua = (declared.upper_floor_heat_loss + declared.lower_floor_heat_loss) if two_zone else declared.heat_loss_coefficient
    hold = max(base_ua * true_ua * 21.0 - (declared.internal_gains + true_gains), 0.1) / cop
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      slab_temperature=25.0, outdoor_temperature=0.0, buffer_tank_temperature=35.0)
    for _ in range(2400):
        st = plant.simulate_step(st, electrical_power=hold, outdoor_temp=0.0)
    kw = dict(enabled=True, min_days_between_runs=0.0)
    if prod_prior:
        kw["gains_prior_kw"] = float(declared.internal_gains)
    sid = S.SystemIdentification(S.SysIdConfig(**kw))
    sid.arm(night, plant=declared)
    when, base, peak = night, st.upper_floor_temperature, 0.0
    while sid.active:
        reading = st.upper_floor_temperature
        peak = max(peak, abs(reading - base))
        ov = sid.step(now=when, room_temp=reading, outdoor_temp=0.0, price=0.1,
            price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=declared.max_electrical_power,
            cop=cop, plan_power_kw=hold, house_ua=declared.heat_loss_coefficient * declared.house_heat_loss_scale,
            house_capacity=declared.room_thermal_mass, house_gains=declared.internal_gains,
            house_slab_mass=declared.slab_thermal_mass, house_slab_transfer=declared.slab_heat_transfer)
        el = hold if ov is None else float(ov)
        st = plant.simulate_step(st, electrical_power=el, outdoor_temp=0.0)
        when += timedelta(hours=0.25)
    d = S.adoption_decision(sid.result, declared, sid.config)
    return d, peak, sid.result.reason, declared.internal_gains

if __name__ == "__main__":
    bar = float(np.expm1(S.UA_ADOPTION_HALFWIDTH_BAR))
    prod = "--prod-prior" in sys.argv
    t = time.time(); over = 0; cells = 0; adm0 = 0
    for tz in (False, True):
        for name in _b942:
            for g in (0.0, 0.4, 0.8, -0.2):
                d, peak, why, g0 = run(name, tz, true_gains=g, prod_prior=prod)
                cells += 1
                bad = d.admit and abs(d.scale - 1.0) > bar
                over += bad; adm0 += (g == 0.0 and d.admit)
                print(f"CELL {name:12s} tz={int(tz)} dG={g:+.1f} decl_gains={g0:.2f} admit={int(d.admit)} scale={d.scale:.4f} peak={peak:.3f} bad={int(bad)} why={d.reason[:60]}")
    print(f"RESULT over_bar={over} null_admitted={adm0} cells={cells} wall_s={time.time()-t:.1f}")
