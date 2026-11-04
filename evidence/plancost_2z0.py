"""Reviewer's own differential: plan cost per cell, base vs head.
Cells: r10_setpoint_boost.CELLS (16) + 4 two-zone manual-valve cells (buffer 0/750 L, dhw on/off)
that reach _substeps_and_loss's throttled two-zone branch. Price days spread and flat.
Derates 0.0, 0.112 and perturbed 0.162. Prints repr of predicted_cost, sum(P*price)/4,
dhw cost, baseline_cost, deferred_energy_cost."""
import sys, itertools
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_setpoint_boost as sb
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from heatpump_optimizer.thermal_model import heat_per_cop_kw
cells = [((1.0, 0.0, d, True), True) for d in (False, True)]
for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
    for (loss, buf, dhw, rounded), two in cells:
        for der in (0.0, 0.112):
            p = ThermalParameters()
            if buf or two:
                p.mixing_valve_mode = "manual"; p.buffer_tank_volume = buf
            p.two_zone_enabled = two
            p.min_electrical_power, p.max_electrical_power = sb.CFG_MIN, sb.CFG_MAX
            p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
            p.cop_partload_derate = der
            opt = sb.HeatPumpOptimizer(ThermalModel(p), sb.OptimizationConfig(clamp_planned_levels=rounded))
            try:
                r = opt.optimize(inputs=sb.solve_inputs(initial_state=sb.ThermalState(
                    room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0,
                    slab_temperature=20.5, outdoor_temperature=5.0, buffer_tank_temperature=24.0,
                    dhw_temperature=48.0), prices=prices, outdoor_temps=np.full(96, 5.0), start_time=sb.T0))
            except Exception as e:
                print(tag, loss, buf, dhw, rounded, two, der, "FAILED", repr(e)); continue
            pr = np.asarray(r.prices, float)
            P = np.asarray(r.power_schedule, float)
            D = np.asarray(r.dhw_power_schedule or [0.0]*len(pr), float)
            lp_err = float((pr * (D - heat_per_cop_kw(opt.model.params, D))).sum() * 0.25)
            print(tag, loss, buf, dhw, rounded, two, der, repr(float(r.predicted_cost)),
                  repr(float((P*pr).sum()/4)), repr(float((D*pr).sum()/4)), repr(float(r.baseline_cost)),
                  repr(float(r.deferred_energy_cost)), "lp_err", round(lp_err, 6))
