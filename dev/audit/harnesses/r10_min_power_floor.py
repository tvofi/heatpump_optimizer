"""r10-min-power-floor (issue 3289): per-step electrical power against heat_pump_min_power.

Solves a 2.5-3.5 kW pump over 24 h with clamp_planned_levels False and True, spread and
flat prices, DHW off/on, two outdoor means, and counts running steps (space+DHW > 0.1 kW)
below the 2.5 kW minimum. The clamp=True arm on identical inputs is the null control: the
counter reads 0 where the floor is honoured.

R10-MIN-POWER-FLOOR fix extension: the arm `clamp=on_off` takes `clamp_planned_levels` from
`levels_clamped` on a fully metered map (power entity, frequency sensor) declaring
`compressor_modulation: on_off`; an install no probe clamps without the declaration.
`max_total` is the largest space+DHW step (above p_max 3.5 is a draw the pump cannot
deliver); `space_only_below_min` counts space steps below 2.5 kW where DHW is off
(<= MIN_RUNNING_DRAW_KW): in a mixed step space is a diverter share of a compressor that
runs at >= p_min, so only a space-only step is a sub-minimum compressor level.

    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_min_power_floor.py [-v]
"""
import sys
from datetime import datetime, timezone
import numpy as np
from heatpump_optimizer import const
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW, ThermalModel, ThermalParameters, ThermalState, channel_heating_steps, levels_clamped
from heatpump_optimizer.plan_slots import plan_slots
from profiles import solve_inputs
S = np.arange(96)
SPREAD = 1.3 + 0.9*np.sin(2*np.pi*(S-30)/96.0)
FLAT = np.full(96, float(SPREAD.mean()))
ON_OFF_METERED = {const.CONF_POWER_ENTITY: "sensor.p", const.CONF_COMPRESSOR_FREQ_SENSOR: "sensor.f",
                  "compressor_modulation": "on_off"}
def run(clamp, prices, dhw, out_mean):
    p = ThermalParameters(); p.mixing_valve_mode="none"; p.buffer_tank_volume=0.0
    p.min_electrical_power, p.max_electrical_power = 2.5, 3.5
    p.dhw_enabled = dhw
    out = out_mean + 3*np.sin(2*np.pi*(S-50)/96)
    opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
        clamp_planned_levels=levels_clamped(ON_OFF_METERED) if clamp == "on_off" else clamp))
    r = opt.optimize(inputs=solve_inputs(initial_state=ThermalState(room_temperature=20.5, upper_floor_temperature=20.5,
        lower_floor_temperature=20.5, slab_temperature=21.0, outdoor_temperature=float(out[0]), dhw_temperature=50.0),
        prices=prices, outdoor_temps=out, start_time=datetime(2026,1,10,tzinfo=timezone.utc)))
    sp = np.asarray(r.power_schedule,float); dw = np.asarray(r.dhw_power_schedule or np.zeros(96),float)
    tot = sp+dw; on = tot>0.1
    below = int(np.sum(on & (tot < 2.5-1e-9)))
    sl = plan_slots(list(r.timestamps), list(sp), list(r.prices), 0.25, other_powers=list(dw))
    slot_min = min((s["avg_power_kw"] for s in sl), default=None)
    space_only_below = int(np.sum(np.array(channel_heating_steps(sp,dw)) & (sp<2.5-1e-9)))
    lone = int(np.sum((sp > MIN_RUNNING_DRAW_KW) & (dw <= MIN_RUNNING_DRAW_KW) & (sp < 2.5-1e-9)))
    print(f"clamp={clamp} prices={'flat' if prices is FLAT else 'spread'} dhw={dhw} out={out_mean}: steps_on={int(on.sum())} total_below_min={below} space_steps_below_min={space_only_below} slots={len(sl)} min_slot_avg={slot_min} cost={r.objective_value:.3f} max_total={tot.max():.2f} space_only_below_min={lone}")
    if '-v' in sys.argv: print(' space', np.round(sp,2).tolist()); print(' dhw', np.round(dw,2).tolist()); print(' slots', [(s['start'][11:16],s['end'][11:16],s['avg_power_kw']) for s in sl])
CASES = [(False, FLAT, False, 5.0)] if "-v" in sys.argv else None
import itertools
for c in CASES or itertools.product((False, True, "on_off"),(SPREAD, FLAT),(False, True),(-4.0,5.0)):
    run(*c)
