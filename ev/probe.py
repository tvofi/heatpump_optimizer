import sys, itertools, numpy as np, traceback
sys.path[:0]=["tests/hastub","tests","custom_components"]
from profiles import house
from heatpump_optimizer.optimizer import HeatPumpOptimizer as O, OptimizationConfig as C, _thermostat_held_state as H
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as P, ThermalState as S, WeatherSeries as WS
n=0; worst=0.0; bad=[]; maxsag=0
for mode,tz,lay,hp,vt,out in itertools.product(["manual","smart_read","smart_write"],[True,False],[None,"two_tank_4way"],[4.0,6.0,9.0],[21.0,25.0,30.0,40.0],[-25.,-15.,-5.,0.,5.,10.,14.,16.,18.]):
    cfg=dict(mixing_valve_mode=mode,mixing_valve_target=vt,buffer_tank_volume=750.0,buffer_max_temperature=56.0,heat_pump_max_power=hp)
    if lay: cfg["topology_layout"]=lay
    try:
        p=P.from_config(house(two_zone=tz,dhw=False,**cfg)); m=M(p)
        o=O(m,C(horizon_hours=1,time_step_minutes=15,target_temp=21.0))
        w=WS(outdoor_temps=np.array([out]),wind_speeds=np.zeros(1),precipitation=np.zeros(1),solar_radiation=np.zeros(1))
        st=S(room_temperature=20.5,slab_temperature=22.0,outdoor_temperature=out,upper_floor_temperature=20.5,lower_floor_temperature=20.5,buffer_tank_temperature=30.0)
        h=H(m,st,w,21.0); pw=float(o._compute_baseline_power(w,st,0.25)[0][0])
        nx=m.simulate_step(h,pw,out,0.,0.,0.,0.25); ds=o._stored_thermal_energy(nx)-o._stored_thermal_energy(h)
        n+=1
        if not (out-1e-9<=h.room_temperature<=21.0) : bad.append(("range",mode,tz,lay,hp,vt,out,h.room_temperature))
        if abs(ds)>abs(worst): worst=ds; wk=(mode,tz,lay,hp,vt,out,round(h.room_temperature,3),pw)
        maxsag=max(maxsag,21-h.room_temperature)
    except Exception as e:
        bad.append(("exc",mode,tz,lay,hp,vt,out,repr(e)[:120]))
print(f"RESULT probe: cases {n}, bad {len(bad)}, worst first-step dS {worst:.4f} kWh_th at {wk}, max sag {maxsag:.3f} K")
for b in bad[:10]: print(b)
