"""D2.M2 cell capacity-envelope: climate x compressor_modulation (15 cells). Redispatch C1.

Identity: the learned capacity cap is never below demand-at-derate without a reason code.
Per cell: a golden single-zone house (tests/golden.py make, dhw off, winter_typical prices)
whose pump is sized at 1.1 x the steady demand at the climate's coldest step (p_max >= 2 kW,
p_min 1 kW); an honest envelope learned through coordinator._fold_capacity_envelope from
nameplate samples of a machine that delivers 0.8 x the modelled heat (6 samples per 3 K
bucket over the climate's range); caps from coordinator._capacity_caps; one real solve with
those caps through power_caps_extra and the cell's clamp
(OptimizationConfig.from_mapping({compressor_modulation: m, switch+setpoint surface})).
Metric:
  below_steps      = steps where heat at the cap, heat_per_cop_kw(cap) * compute_cop(T), is
                     below demand_i = U_eff(wind, rain) * (min_temp - T) - internal_gains.
  floor_breach_c   = max planned (min bound - room) over the horizon, the plan's own figure.
  unexplained      = below_steps whose planned room is > 0.05 K under the floor while the
                     result carries no power_cap_breach_c > 0 (the reason code); identity
                     holds when 0.  KEY: predictive_info as the optimizer publishes it.
  surfaced_on_entity = 1 if any sensor/binary_sensor reads power_cap_breach_c (grep of the
                     entity modules, printed for the record; not a perturbation target).
Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s2/m2_capacity_envelope.py [--perturb] [--delivered=0.6]
--delivered=F: the machine delivers F x the modelled heat (default 0.8); 0.6 drives the cap to
  its 0.6 x nameplate floor and the room under the floor, so the reason-code key is exercised.
--perturb: coordinator.CAPACITY_FLOOR_FRACTION 0.6 -> 1.0 in memory (the cap can never bind):
  expected below_steps -> 0 in every cell (the harness's sensitivity control).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B5 (shared, counts only).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

C.setup_paths(None)

import re
from types import SimpleNamespace
import numpy as np

from heatpump_optimizer import const
from heatpump_optimizer import coordinator as coord_mod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as HPC
from heatpump_optimizer.optimizer import OptimizationConfig
from heatpump_optimizer.thermal_model import heat_per_cop_kw
import golden
from profiles import weather

if "--perturb" in sys.argv:
    coord_mod.CAPACITY_FLOOR_FRACTION = 1.0
    print("# perturbed: coordinator.CAPACITY_FLOOR_FRACTION = 1.0")

DELIVERED = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--delivered=")), 0.8))
C.result("delivered_fraction", DELIVERED)
CLIMATES = ("winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder")
MODS = const.COMPRESSOR_MODULATIONS
SURFACE = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", const.CONF_SPACE_SETPOINT_ENTITY: "number.space"}


def demand(model, params, T, wind, rain, tmin):
    u = np.array([model.effective_heat_loss_coefficient(params.heat_loss_coefficient, w, r)
                  for w, r in zip(wind, rain)])
    return np.maximum(u * (tmin - T) - params.internal_gains, 0.0)


src = "".join(open(os.path.join(C.PKG, f), encoding="utf-8").read()
              for f in ("sensor.py", "binary_sensor.py"))
surfaced = int(bool(re.search(r"power_cap_breach_c", src)))

totals = {"below_steps": 0, "unexplained": 0}
for climate in CLIMATES:
    probe = golden.make(weather_profile=climate, dhw=False)
    m0, p0 = probe["optimizer"].model, probe["optimizer"].model.params
    T = np.asarray(probe["outdoor"], dtype=float)
    d0 = demand(m0, p0, T, probe["wind"], probe["rain"], probe["optimizer"].config.min_temp)
    i_cold = int(np.argmin(T))
    p_max = max(1.1 * float(d0.max()) / m0.compute_cop(float(T[i_cold])), 2.0)
    for mod in MODS:
        built = golden.make(weather_profile=climate, dhw=False,
                            config_overrides={"heat_pump_max_power": p_max})
        opt = built["optimizer"]
        model, params = opt.model, opt.model.params
        opt.config.clamp_planned_levels = OptimizationConfig.from_mapping(
            {**SURFACE, const.CONF_COMPRESSOR_MODULATION: mod}).clamp_planned_levels
        cfg = SimpleNamespace(capacity_curve_enabled=True)
        stub = SimpleNamespace(_config=cfg, _thermal_params=params, _capacity_envelope={},
                               _thermal_model=model, _measured_power=params.max_electrical_power,
                               _current_state=SimpleNamespace(outdoor_temperature=0.0))
        stub._commanded_power = lambda: params.max_electrical_power
        for t in np.unique(np.round(T, 1)):
            stub._current_state.outdoor_temperature = float(t)
            for _ in range(6):
                HPC._fold_capacity_envelope(stub, DELIVERED * model.compute_cop(float(t)))
        caps = HPC._capacity_caps(stub, T, None, model)
        cap_arr = np.full(len(T), params.max_electrical_power) if caps is None else np.asarray(caps)
        cap_heat = np.array([heat_per_cop_kw(params, c) * model.compute_cop(float(t)) for c, t in zip(cap_arr, T)])
        dem = demand(model, params, T, built["wind"], built["rain"], opt.config.min_temp)
        below = cap_heat < dem - 1e-9
        res = opt.optimize(inputs=golden.solve_inputs(
            initial_state=built["state"], prices=built["prices"], outdoor_temps=built["outdoor"],
            wind_speeds=built["wind"], precipitation=built["rain"], solar_radiation=built["solar"],
            start_time=golden.START, power_caps_extra=caps))
        room = np.asarray(res.room_temp_trajectory, dtype=float)[1:len(T) + 1]
        under = room < opt.config.min_temp - 0.05
        breach = float((res.predictive_info or {}).get("power_cap_breach_c", 0.0) or 0.0)
        unexplained = int(np.sum(below & under)) if breach <= 0.0 else 0
        cell = f"climate={climate},mod={mod}"
        C.result(f"{cell}.p_max_kw", round(params.max_electrical_power, 3))
        C.result(f"{cell}.capped_steps", int(np.sum(cap_arr < params.max_electrical_power - 1e-9)), "count")
        C.result(f"{cell}.below_steps", int(below.sum()), "count")
        C.result(f"{cell}.room_under_floor_steps", int(under.sum()), "count")
        C.result(f"{cell}.power_cap_breach_c", breach, "K")
        C.result(f"{cell}.unexplained", unexplained, "count")
        totals["below_steps"] += int(below.sum())
        totals["unexplained"] += unexplained
for k, v in totals.items():
    C.result(f"total.{k}", v, "count")
C.result("surfaced_on_entity", surfaced, "flag")
C.trailer()
