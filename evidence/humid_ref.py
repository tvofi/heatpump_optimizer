import sys, numpy as np
sys.path[:0]=["tests/hastub","tests","custom_components"]
from profiles import house
from heatpump_optimizer.optimizer import HeatPumpOptimizer as O, OptimizationConfig as C
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as P, ThermalState as S, WeatherSeries as WS
from heatpump_optimizer.defrost import DefrostDerate
d=DefrostDerate()
for _ in range(60): d.observe(2.0,90.0,0.6)
p=P.from_config(house(two_zone=True,dhw=False,heat_pump_max_power=9.0)); p.defrost_derate=d; m=M(p)
o=O(m,C(horizon_hours=1,time_step_minutes=15,target_temp=21.0))
st=S(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=2.0,upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=30.0)
for hum in [None,np.array([90.0])]:
    w=WS(outdoor_temps=np.array([2.0]),wind_speeds=np.zeros(1),precipitation=np.zeros(1),solar_radiation=np.zeros(1),humidity=hum)
    print(f"RESULT reference power at 2 C, humidity {None if hum is None else 90}: {float(o._compute_baseline_power(w,st,0.25)[0][0]):.4f} kW")
