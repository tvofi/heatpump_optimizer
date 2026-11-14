import sys, itertools, numpy as np
sys.path[:0]=["tests/hastub","tests","custom_components"]
from profiles import house
from heatpump_optimizer.optimizer import HeatPumpOptimizer as O, OptimizationConfig as C, _thermostat_held_state as H
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as P, ThermalState as S, WeatherSeries as WS
for mode,tz,hp,wood,out,hum in itertools.product(["none","manual","smart_write"],[True,False],[4.0,9.0],[None,15.0,85.0],[-25.,-5.],[None,95.0]):
    cfg=dict(buffer_tank_volume=750.0,buffer_max_temperature=56.0,heat_pump_max_power=hp,topology_layout="two_tank_4way")
    if mode!="none": cfg.update(mixing_valve_mode=mode,mixing_valve_target=30.0)
    p=P.from_config(house(two_zone=tz,dhw=False,**cfg)); m=M(p)
    o=O(m,C(horizon_hours=1,time_step_minutes=15,target_temp=21.0))
    w=WS(outdoor_temps=np.array([out]),wind_speeds=np.zeros(1),precipitation=np.zeros(1),solar_radiation=np.zeros(1),humidity=None if hum is None else np.array([hum]))
    st=S(room_temperature=20.5,slab_temperature=22.0,outdoor_temperature=out,upper_floor_temperature=20.5,lower_floor_temperature=20.5,buffer_tank_temperature=30.0,wood_tank_temperature=wood)
    h=H(m,st,w,21.0); pw=float(o._compute_baseline_power(w,st,0.25)[0][0])
    nx=m.simulate_step(h,pw,out,0.,0.,0.,0.25); ds=o._stored_thermal_energy(nx)-o._stored_thermal_energy(h)
    flag = "DRAW" if ds<-0.02 else "ok"
    print(f"{flag} mode={mode} tz={tz} hp={hp} wood={wood} out={out} hum={hum}: held {h.room_temperature:.3f} pw {pw:.3f} dS {ds:+.4f}")
