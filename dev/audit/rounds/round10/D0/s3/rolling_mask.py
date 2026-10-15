"""D0.M6 MPC masking: is the convergence gap race.py measures realised under receding-horizon re-planning?

Metric: realised 24 h closed loop (plant == model, DHW off, re-plan every --every steps, 24 h horizon,
prices/weather repeated daily) of HeatPumpOptimizer.optimize: realised_cost = sum(price*power*dt) of executed
steps; floor_ds = degree-steps below 17 C; end_room/end_slab = state after 24 h; score = realised_cost +
terminal_cost(end state) priced by the production _terminal_cost closure of the final solve's optimizer.
Arms: production vs --tight (optimizer._scoped_minimize options ftol 1e-12, maxiter 3000, maxfun 2e5: the
budget challenger race.py's arm B uses). Count key: realised schedules production returns each cycle.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s3/rolling_mask.py --price shoulder --weather winter_cold [--tight]
Perturbation: --tight; if the gap is realised, score must fall under --tight; null control --price flat.
Baseline 17f1c55fad1b, machine macOS arm64 (B3).
"""
import os
for _k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k,"1")
import sys, time, argparse
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from datetime import datetime, timedelta
from profiles import prices, weather, house, solve_inputs, DT, N
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from heatpump_optimizer import optimizer as O
ap=argparse.ArgumentParser(); ap.add_argument("--price",default="shoulder"); ap.add_argument("--weather",default="winter_cold")
ap.add_argument("--tz",type=int,default=0); ap.add_argument("--every",type=int,default=4); ap.add_argument("--tight",action="store_true")
a=ap.parse_args()
if a.tight:
    _sm=O._scoped_minimize
    def sm(*aa,**kk):
        o=dict(kk.get("options",{})); o.update(ftol=1e-12,maxiter=3000,maxfun=200000); kk["options"]=o
        return _sm(*aa,**kk)
    O._scoped_minimize=sm
start=datetime(2026,1,15)
P=np.tile(prices(a.price,start),3); OT,WI,RA,SO=(np.tile(v,3) for v in weather(a.weather,start))
cfg=house(two_zone=bool(a.tz)); p=ThermalParameters.from_config(cfg); p.dhw_enabled=False; m=ThermalModel(p)
st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(OT[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
cost=0.0; fds=0.0; s0=[]; t0=time.process_time(); th0=time.thread_time()
k=0
while k<N:
    opt=O.HeatPumpOptimizer(m,O.OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
    sl=slice(k,k+N)
    r=opt.optimize(inputs=solve_inputs(initial_state=st,prices=P[sl],outdoor_temps=OT[sl],wind_speeds=WI[sl],precipitation=RA[sl],solar_radiation=SO[sl],start_time=start+timedelta(hours=k*DT)))
    pw=np.asarray(r.power_schedule,float)[:a.every]; s0.append(pw[0])
    e=slice(k,k+a.every)
    room,slab,up,lo,buf,_,_=m.simulate_trajectory(st,pw,WeatherSeries(outdoor_temps=OT[e],wind_speeds=WI[e],precipitation=RA[e],solar_radiation=SO[e]),dt_hours=DT)
    cost+=float((P[e]*pw).sum()*DT); fds+=float(np.maximum(0,17.0-room[1:]).sum())
    st=ThermalState(room_temperature=float(room[-1]),slab_temperature=float(slab[-1]),outdoor_temperature=float(OT[k+a.every]),upper_floor_temperature=float(up[-1]),lower_floor_temperature=float(lo[-1]),buffer_tank_temperature=float(buf[-1]))
    k+=a.every
term,_=opt._terminal_cost(P[N:2*N],OT[N:2*N])
tc=term(np.array([st.room_temperature]),np.array([st.slab_temperature]),np.array([st.upper_floor_temperature]),np.array([st.lower_floor_temperature]),np.array([st.buffer_tank_temperature]))
print(f"RESULT realised_cost={cost:.4f} SEK")
print(f"RESULT floor_degree_steps={fds:.4f} K*step")
print(f"RESULT end_room={st.room_temperature:.4f} C"); print(f"RESULT end_slab={st.slab_temperature:.4f} C")
print(f"RESULT terminal_cost_end={tc:.4f} SEK")
print(f"RESULT score={cost+tc:.4f} SEK")
pc=time.process_time()-t0; tcpu=time.thread_time()-th0
print(f"RESULT thread_factor={pc/max(tcpu,1e-9):.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=na")
