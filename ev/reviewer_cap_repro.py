"""Reviewer's own instrument: an external total cap under a clamped install's floor, base against head."""
import sys, dataclasses
from datetime import datetime, timezone
import numpy as np
import heatpump_optimizer.optimizer as om
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs
STEPS = np.arange(96); T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
tot_over = {}
for p_min, cost, dhw_on, pair, capkw, out_mean, a, ln in [
    (5.5, 2.0, True, (1.0, 0.0), 0.6, 10.0, 20, 8), (5.5, 2.0, True, (1.0, 0.0), 0.6, 10.0, 50, 6), (5.5, 2.0, False, (0.0, 0.0), 0.6, 10.0, 20, 8),
    (5.5, 0.25, False, (0.0, 0.0), 2.0, 4.0, 30, 10), (5.5, 0.0, False, (0.0, 0.0), 2.0, 4.0, 30, 10), (1.5, 0.25, False, (0.0, 0.0), 1.2, 4.0, 30, 10),
    (1.5, 0.0, False, (0.0, 0.0), 1.2, 4.0, 30, 10), (1.5, 0.0, False, (0.0, 0.0), 0.6, -4.0, 40, 12), (1.5, 0.25, False, (0.0, 0.0), 0.6, -4.0, 40, 12),
    (5.5, 0.25, False, (0.0, 0.0), 0.6, -4.0, 40, 12), (5.5, 0.0, False, (0.0, 0.0), 0.6, -4.0, 40, 12)]:
    params = ThermalParameters(); params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5; params.dhw_enabled = dhw_on
    cfg = om.OptimizationConfig(clamp_planned_levels=True, cycling_cost=cost)
    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, (501.0, 300.0)
    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    win = np.zeros(96, bool); win[a:a + ln] = True
    inp = solve_inputs(initial_state=ThermalState(room_temperature=20.5, upper_floor_temperature=20.5, lower_floor_temperature=20.5,
        slab_temperature=21.0, outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0, dhw_temperature=45.0, dhw_hours_since_legionella=20.0),
        prices=np.full(96, 1.0), outdoor_temps=outdoor, start_time=T0, power_caps_extra=np.where(win, capkw, 99.0))
    res = om.HeatPumpOptimizer(ThermalModel(params), cfg).optimize(inputs=inp)
    sp = np.asarray(res.power_schedule, float); dh = np.asarray(res.dhw_power_schedule, float) if dhw_on else np.zeros(96)
    if dh.size != 96: dh = np.zeros(96)
    print(f"RESULT cap p_min={p_min} cost={cost} dhw={dhw_on} pair={pair} cap={capkw} out={out_mean} win={a}+{ln}: capped steps with space over cap {int(np.sum(sp[win] > capkw + 1e-6))}, with hot water over cap {int(np.sum(dh[win] > capkw + 1e-6))}, max total over cap {float(np.max((sp + dh)[win]) - capkw):.2f} kW, status {res.status}")
