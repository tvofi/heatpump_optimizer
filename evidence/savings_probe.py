"""Reviewer's probe (not the finder's): what the published predicted_savings
reads on the finder's 0.6-loss, no-DHW cell, flat and spread, buffer vs none,
single-zone vs two-zone, with the result's baseline/optimized cost, kWh and
min room temperature; run in each tree."""
import sys
sys.path[:0] = ["tests/hastub", "custom_components", "tests"]
import numpy as np
from datetime import datetime, timezone
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs
sys.argv = ["x"]
import importlib.util
spec = importlib.util.spec_from_file_location("fh", sys.argv[0] if False else __file__.replace("savings_probe.py", "finder_harness.py"))
fh = importlib.util.module_from_spec(spec); spec.loader.exec_module(fh)
T0 = datetime(2026, 1, 12, 20, 0, tzinfo=timezone.utc)
for tz in (False, True):
    for tag, prices in (("flat", fh.FLAT), ("spread", fh.SPREAD)):
        for buf in (750.0, 0.0):
            p = ThermalParameters(two_zone_enabled=tz)
            if buf:
                p.mixing_valve_mode, p.buffer_tank_volume = "manual", buf
            p.min_electrical_power, p.max_electrical_power = 1.5, 5.0
            p.dhw_enabled, p.house_heat_loss_scale = False, 0.6
            r = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig()).optimize(inputs=solve_inputs(
                initial_state=ThermalState(room_temperature=20.0, upper_floor_temperature=20.0,
                    lower_floor_temperature=20.0, slab_temperature=20.5, outdoor_temperature=5.0,
                    buffer_tank_temperature=24.0, dhw_temperature=48.0),
                prices=prices, outdoor_temps=np.full(96, 5.0), start_time=T0))
            g = lambda k: getattr(r, k, None)
            base = g("baseline_cost"); opt = g("predicted_cost")
            bp = np.asarray(g("baseline_power_schedule") or [], float)
            rt = np.asarray(g("room_temp_trajectory") or g("upper_temp_trajectory") or [], float)
            bt = np.asarray(g("buffer_temp_trajectory") or [], float)
            print(f"RESULT {'2z' if tz else '1z'} {tag:6s} buf={buf:5.0f} savings={float(r.predicted_savings):7.2f} "
                  f"baseline_cost={base} plan_cost={opt} plan_kwh={sum(r.power_schedule)*0.25:.2f} "
                  f"baseline_kwh={bp.sum()*0.25 if bp.size else None} "
                  f"room_min={rt.min() if rt.size else None} tank_max={bt.max() if bt.size else None}")
