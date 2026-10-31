"""D7-s1 sysid on a TWO-ZONE house: the one-room fit read through the upper-zone thermometer.

Metric (adopted_scale_err_pct): (heat-loss scale the production gate writes - 1.0) * 100, on a
  plant whose TRUE parameters equal the declared ones (so the correct scale is exactly 1.0).
  Count key: the value stub._apply_house_heat_loss_scale receives from
  coordinator:HeatPumpOptimizerCoordinator._adopt_system_identification.
  fit_vs_base_pct: (identify_slab's UA / (upper_floor_heat_loss + lower_floor_heat_loss) - 1)*100,
  the ratio the gate turns into that scale.
Plant: production ThermalModel with two_zone_enabled (tests/stress.py:BUILDINGS presets derived with
  two_zone=True), pre-settled 600 h at a constant hold power; the sensor the fit sees is
  upper_floor_temperature (coordinator._update_current_state writes the indoor reading to both
  room_temperature and upper_floor_temperature); the recorded COP is ThermalModel.compute_cop(outdoor),
  as coordinator._run_system_identification passes it.
Null control: the same drive on the SINGLE-zone derivation of each preset (declared == true): err ~0.
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_sysid_twozone.py [--perturb]
  --perturb: switch the plant's two_zone_enabled off (declared stays two-zone): the fit then sees
  a one-room plant, and the error must move.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging, dataclasses
sys.path.insert(0, "tools/audit/round8/D7")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from datetime import timedelta
import s1_sysid as H
S = H.S
from heatpump_optimizer.presets import BuildingPreset, derive
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import house

PERTURB = "--perturb" in sys.argv
OUT = 0.0


def params(name, two_zone):
    cfg = house(two_zone=two_zone, dhw=False)
    d = derive(BuildingPreset(**{**vars(H.BUILDINGS[name]), "two_zone": two_zone}))
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.wind_sensitivity = 0.0
    return p


def base_ua(p):
    return (p.upper_floor_heat_loss + p.lower_floor_heat_loss) if p.two_zone_enabled else p.heat_loss_coefficient


def run(declared, plant_p):
    model = ThermalModel(plant_p)
    cop = model.compute_cop(OUT)
    ua_decl = base_ua(declared) * declared.house_heat_loss_scale
    gains = float(declared.internal_gains)
    hold_el = max(ua_decl * (21.0 - OUT) - gains, 0.1) / cop
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      slab_temperature=25.0, outdoor_temperature=OUT, buffer_tank_temperature=35.0)
    for _ in range(int(600 / 0.25)):  # 600 h: several slow time constants
        st = model.simulate_step(st, electrical_power=hold_el, outdoor_temp=OUT, dt_hours=0.25)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sid.arm(H.NOW, plant=declared)
    when = H.NOW
    base = None
    peak = 0.0
    last_phase = None
    for _ in range(int(5.0 / 0.25) + 4):
        reading = st.upper_floor_temperature if plant_p.two_zone_enabled else st.room_temperature
        ov = sid.step(now=when, room_temp=reading, outdoor_temp=OUT, price=0.1,
                      price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=H.MAXP,
                      cop=cop, plan_power_kw=hold_el,
                      house_ua=declared.heat_loss_coefficient * declared.house_heat_loss_scale,
                      house_capacity=float(declared.room_thermal_mass), house_gains=gains,
                      house_slab_mass=float(declared.slab_thermal_mass),
                      house_slab_transfer=float(declared.slab_heat_transfer))
        base = reading if base is None else base
        peak = max(peak, abs(reading - base))
        last_phase = sid.phase if sid.active else last_phase
        if not sid.active:
            break
        el = hold_el if ov is None else float(ov)
        st = model.simulate_step(st, electrical_power=el, outdoor_temp=OUT, dt_hours=0.25)
        when += timedelta(hours=0.25)
    sid._h_peak, sid._h_phase = peak, last_phase
    return sid


worst = 0.0
admitted = 0
completed = {True: 0, False: 0}
for zone in (True, False):
    for name in H.BUILDINGS:
        declared = params(name, zone)
        plant = dataclasses.replace(declared, two_zone_enabled=False) if (PERTURB and zone) else declared
        sid = run(declared, plant)
        r = sid.result
        if not r.completed:
            print(f"CELL {name} two_zone={zone}: not completed ({r.reason}) in phase {sid._h_phase}, "
                  f"sensor excursion {sid._h_peak:.2f} K, step {sid._step_power:.2f} kW", flush=True)
            continue
        hw = S.slab_ua_adoption_halfwidth(r.ua_profile_halfwidth, r.ua_prior_halfwidth)
        sc = H.gate(sid, declared)
        completed[zone] += int(sc is not None)
        fit_vs = (r.heat_loss_kw_per_c / base_ua(declared) - 1) * 100
        err = (sc - 1.0) * 100 if sc is not None else None
        print(f"CELL {name} two_zone={zone}: fit_UA={r.heat_loss_kw_per_c:.4f} base={base_ua(declared):.4f} "
              f"fit_vs_base={fit_vs:+.2f}% hw={hw:.4f} admitted={sc is not None} adopted_scale_err={err}", flush=True)
        if zone and sc is not None:
            admitted += 1
            worst = max(worst, abs(err))
print(f"RESULT singlezone_admitted={completed[False]} count (of 3; null control)")
print(f"RESULT twozone_admitted={admitted} count (of 3)")
print(f"RESULT twozone_worst_adopted_scale_err={worst:.2f} pct")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
