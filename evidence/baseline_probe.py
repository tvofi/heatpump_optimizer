"""Reviewer's probe: the thermostat reference's own tank on the finder's
0.6-loss no-DHW single-zone 750 L manual-valve cell, flat price day: record
every simulate_step the baseline makes (tank temperature, refused kW)."""
import sys
sys.path[:0] = ["tests/hastub", "custom_components", "tests"]
import numpy as np
from datetime import datetime, timezone
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs
T0 = datetime(2026, 1, 12, 20, 0, tzinfo=timezone.utc)
FLAT = None
import importlib.util
spec = importlib.util.spec_from_file_location("fh", __file__.replace("baseline_probe.py", "finder_harness.py"))
fh = importlib.util.module_from_spec(spec); spec.loader.exec_module(fh)
for buf in (750.0, 0.0):
    p = ThermalParameters(); 
    if buf: p.mixing_valve_mode, p.buffer_tank_volume = "manual", buf
    p.min_electrical_power, p.max_electrical_power = 1.5, 5.0
    p.dhw_enabled, p.house_heat_loss_scale = False, 0.6
    m = ThermalModel(p); opt = HeatPumpOptimizer(m, OptimizationConfig())
    rec = {"on": False, "buf": [], "ref": [], "room": []}
    orig_b = opt._compute_baseline_power
    def wrapped(*a, **k):
        rec["on"] = True
        try: return orig_b(*a, **k)
        finally: rec["on"] = False
    opt._compute_baseline_power = wrapped
    orig_s = m.simulate_step
    def ss(*a, **k):
        s = orig_s(*a, **k)
        if rec["on"]:
            rec["buf"].append(s.buffer_tank_temperature); rec["ref"].append(m._step_buffer_refused); rec["room"].append(s.room_temperature)
        return s
    m.simulate_step = ss
    r = opt.optimize(inputs=solve_inputs(initial_state=ThermalState(room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=20.5, outdoor_temperature=5.0, buffer_tank_temperature=24.0,
        dhw_temperature=48.0), prices=fh.FLAT, outdoor_temps=np.full(96, 5.0), start_time=T0))
    b = np.asarray(rec["buf"]); f = np.asarray(rec["ref"]); rm = np.asarray(rec["room"])
    bp = np.asarray(r.baseline_power_schedule, float)
    print(f"RESULT flat buf={buf:.0f} savings={r.predicted_savings:.2f} pct={r.savings_percentage:.1f} baseline_kwh={bp.sum()*0.25:.2f} "
          f"plan_kwh={sum(r.power_schedule)*0.25:.2f} baseline-steps={len(b)} baseline tank min/max/end={b.min():.1f}/{b.max():.1f}/{b[-1]:.1f} "
          f"refused kWh={f.sum()*0.25:.2f} baseline room min/max={rm.min():.2f}/{rm.max():.2f}")
