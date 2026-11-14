import itertools, numpy as np, sys
sys.path[:0] = ["tests/hastub","tests","custom_components"]
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from heatpump_optimizer.optimizer import _thermostat_held_state
from profiles import replay_install
counts = {}
diffs = []
orig = tm.valve_top_equilibrium
for outdoor, solar, curve, cap, pump in itertools.product((10.0,5.0,0.0,-5.0,-15.0,-25.0),(0.0,100.0,300.0,600.0),(None,3.0,10.0,25.0,35.0),(None,25.0,30.0),(None,2.0,4.0,9.0)):
    over = {}
    if curve is not None: over["mixing_valve_target"]=curve
    if cap is not None: over["buffer_max_temperature"]=cap
    if pump is not None: over["heat_pump_max_power"]=pump
    params = ThermalParameters.from_config(replay_install(**over)); model = ThermalModel(params)
    start = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=outdoor,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    w = WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.full(1,3.0), precipitation=np.zeros(1), solar_radiation=np.array([solar]))
    seen = []
    def spy(model, state, o, wi, r, s, _seen=seen):
        (ua_rad, top_rad, _), (ua_floor, top_floor, _) = tm._valve_draw_circuits(model, state, o, wi, r)
        p = model.params
        t_rad, t_floor = min(top_rad, p.buffer_max_temp), min(top_floor, p.buffer_max_temp)
        res = orig(model, state, o, wi, r, s)
        # replicate the solve to see halves
        tm_ = tm
        u_upper, u_lower = model._zone_loss(wi, r)
        def rates(x): return np.array(model._two_zone_rates(x[0],x[1],x[2],o,ua_rad*(t_rad-x[0]),ua_floor*(t_floor-x[2]),u_upper,u_lower,s,None))
        x0=np.array([state.upper_floor_temperature,state.lower_floor_temperature,state.slab_temperature]); a=rates(x0)
        up,lo,sl = x0+np.linalg.solve(np.column_stack([rates(x0+e)-a for e in np.eye(3)]),-a)
        _seen.append((up>=t_rad, sl>=t_floor))
        return res
    tm_mod = sys.modules["heatpump_optimizer.optimizer"]
    tm_mod.valve_top_equilibrium = spy
    try:
        _thermostat_held_state(model, start, w, 21.0)
    finally:
        tm_mod.valve_top_equilibrium = orig
    for s in seen:
        counts[s] = counts.get(s,0)+1
        if s in ((True,False),(False,True)): diffs.append((outdoor,solar,curve,cap,pump,s))
print("RESULT guard halves (upper>=t_rad, slab>=t_floor) -> count over calls:", counts)
print("RESULT one-half-only cases:", len(diffs)); [print("  ",d) for d in diffs[:20]]
