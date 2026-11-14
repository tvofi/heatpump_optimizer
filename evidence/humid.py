import sys, itertools, numpy as np
sys.path[:0]=["tests/hastub","tests","custom_components"]
from profiles import house
from heatpump_optimizer.optimizer import HeatPumpOptimizer as O, OptimizationConfig as C, _thermostat_held_state as H
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as P, ThermalState as S, WeatherSeries as WS
from heatpump_optimizer.defrost import DefrostDerate
d=DefrostDerate()
for _ in range(60): d.observe(2.0,90.0,0.6)
nd=0
for mode,tz,hp,out in itertools.product(["none","manual"],[True,False],[1.0,1.5,2.0,3.0],[0.0,2.0,4.0]):
    cfg=dict(buffer_tank_volume=750.0,buffer_max_temperature=56.0,heat_pump_max_power=hp)
    if mode!="none": cfg.update(mixing_valve_mode=mode,mixing_valve_target=40.0)
    p=P.from_config(house(two_zone=tz,dhw=False,**cfg)); p.defrost_derate=d; m=M(p)
    o=O(m,C(horizon_hours=1,time_step_minutes=15,target_temp=21.0))
    w=WS(outdoor_temps=np.array([out]),wind_speeds=np.zeros(1),precipitation=np.zeros(1),solar_radiation=np.zeros(1),humidity=np.array([90.0]))
    st=S(room_temperature=20.5,slab_temperature=22.0,outdoor_temperature=out,upper_floor_temperature=20.5,lower_floor_temperature=20.5,buffer_tank_temperature=30.0)
    h=H(m,st,w,21.0); pw=float(o._compute_baseline_power(w,st,0.25)[0][0])
    nx=m.simulate_step(h,pw,out,0.,0.,0.,0.25); ds=o._stored_thermal_energy(nx)-o._stored_thermal_energy(h)
    print(f"held {h.room_temperature:.3f} pw {pw:.3f} ds {ds:+.4f} cop90 {m.compute_cop(out,humidity=90.0):.3f} cop {m.compute_cop(out):.3f}") if (mode,tz)==("none",True) else None
    if ds<-0.02: nd+=1; print(f"DRAW mode={mode} tz={tz} hp={hp} out={out}: held {h.room_temperature:.3f} pw {pw:.3f} dS {ds:+.4f}")
print(f"RESULT humid (learned derate 0.6 @2C/90%, humidity 90): draws<-0.02 {nd} of 48")
