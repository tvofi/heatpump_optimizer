"""Reviewer's own probe (not the finder's): is the 10.83 % flat-price residual the comfort trade?
Replays the harness's null loop, and beside it prices a steady thermostat at (a) the comfort target
and (b) the room the plan actually delivered, both as thermal demand / COP. If (a)-(b) ~ booked
thermostat kWh - plan kWh, the residual is the comfort gap, not accounting."""
import sys
sys.path.insert(0, "dev/audit/harnesses")
from datetime import timedelta
import numpy as np
import r10_sav_baseline as h
from heatpump_optimizer.optimizer import _floor_demand_at_target
from heatpump_optimizer.thermal_model import WeatherSeries
from profiles import DT, prices, solve_inputs, weather

opt, model, _ = h._optimizer()
days, replan = 2, 4
total = int(days * 24 / DT); span = total + int(24 / DT) + 4
tile = lambda a: np.tile(np.asarray(a, float), int(np.ceil(span / len(a))))[:span]
pr = tile(prices("flat", h.START)); out, wind, rain, sol = (tile(a) for a in weather("winter_cold", h.START)); out = np.full_like(out, float(np.mean(out[:int(2*24/DT)])))
hs = int(24 / DT); state = h._state(21.0, 22.0, float(out[0])); plan = None; s0 = (state.room_temperature, state.slab_temperature); th_b = 0.0; copw = 0.0
kp = kb = ea = eb = 0.0
for k in range(total):
    now = h.START + timedelta(hours=k * DT)
    if k % replan == 0:
        plan = opt.optimize(inputs=solve_inputs(initial_state=state, prices=pr[k:k+hs], outdoor_temps=out[k:k+hs],
            wind_speeds=wind[k:k+hs], precipitation=rain[k:k+hs], solar_radiation=sol[k:k+hs], start_time=now))
    o = k % replan; p = float(plan.power_schedule[o])
    kp += p * DT; kb += float(plan.baseline_power_schedule[o]) * DT
    tgt = opt.config.get_comfort_temp(now.hour + now.minute / 60.0, when=now)
    cop = model.compute_cop(float(out[k]))
    copw += p * cop; th_bw = globals().get('th_bw', 0.0) + float(plan.baseline_power_schedule[o]) * cop; globals()['th_bw'] = th_bw
    room_before = state.room_temperature
    room, slab, up, lo, *_ = model.simulate_trajectory(initial_state=state, power_schedule=np.array([p]),
        weather=WeatherSeries(outdoor_temps=out[k:k+1], wind_speeds=wind[k:k+1], precipitation=rain[k:k+1],
        solar_radiation=sol[k:k+1]), dt_hours=DT)
    room_mid = 0.5 * (room_before + float(room[-1]))
    args = (float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]))
    ea += max(0.0, _floor_demand_at_target(model, tgt, *args)) / cop * DT
    eb += max(0.0, _floor_demand_at_target(model, room_mid, *args)) / cop * DT
    th_b += max(0.0, _floor_demand_at_target(model, room_mid, *args)) * DT
    state = h._state(float(room[-1]), float(slab[-1]), float(out[k]))
    state.upper_floor_temperature = float(up[-1]); state.lower_floor_temperature = float(lo[-1])
print(f"RESULT probe booked_thermostat_kwh {kb:.1f} plan_kwh {kp:.1f} gap {kb-kp:.1f}")
print(f"RESULT probe steady_at_target_kwh {ea:.1f} steady_at_delivered_room_kwh {eb:.1f} comfort_gap {ea-eb:.1f}")
print(f"RESULT probe plan_vs_steady_at_delivered_room {kp-eb:+.1f} kWh ({(eb-kp)/ea*100:+.2f} % of steady_at_target)")
pm = model.params
drain = pm.room_thermal_mass * (s0[0] - state.room_temperature) + pm.slab_thermal_mass * (s0[1] - state.slab_temperature)
print(f"RESULT probe start room/slab {s0[0]:.2f}/{s0[1]:.2f} end {state.room_temperature:.2f}/{state.slab_temperature:.2f} stored_heat_drawn_kwh_th {drain:.1f}")
print(f"RESULT probe thermal_loss_at_delivered_room_kwh_th {th_b:.1f}; plan_effective_cop {(th_b - drain)/kp:.3f} vs steady_cop {th_b/eb:.3f}")
print(f"RESULT probe drawdown_at_steady_cop_kwh_e {drain/(th_b/eb):.1f}")
print(f"RESULT probe power_weighted_cop plan {copw/kp:.3f} thermostat {th_bw/kb:.3f} (outdoor-timing gain {(copw/kp)/(th_bw/kb)*100-100:+.2f} %)")
print(f"RESULT probe outdoor min/max over loop {float(np.min(out[:total])):.1f}/{float(np.max(out[:total])):.1f} C; thermal_delivered_by_plan_at_its_cop {copw*DT:.1f} kWh_th vs loss+charge {th_b - drain:.1f}")
from heatpump_optimizer.ledger import MonthlyLedger
