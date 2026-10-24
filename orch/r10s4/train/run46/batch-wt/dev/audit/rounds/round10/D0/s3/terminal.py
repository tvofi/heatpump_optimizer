"""D0.M7 terminal credit: does HeatPumpOptimizer._terminal_cost change the plan the way its docstring claims
("without this the optimizer always dumps the last couple of hours ... breaches the comfort floor at the tail")?

Metric: per cell, tail_kwh = space+DHW electrical kWh over the last 2 h of the shipped plan
(OptimizationResult.power_schedule + dhw_power_schedule), end_room = room_temp_trajectory[-1],
tail_breach = degree-steps of room_temp_trajectory below config.min_temp over the last 2 h.
Arms: production (terminal on) vs --off (both terminal closures return 0).
Count key: the shipped schedules/trajectory production returns.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s3/terminal.py [--off]
Perturbation: --off zeroes _terminal_cost; tail_kwh must fall / end_room must fall if the docstring holds.
Baseline 17f1c55fad1b, machine macOS arm64 (B3).
"""
import os
for _k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k,"1")
import sys, time, argparse
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from datetime import datetime
from profiles import prices, weather, house, solve_inputs, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import optimizer as O
ap=argparse.ArgumentParser(); ap.add_argument("--off",action="store_true")
ap.add_argument("--prices",default="winter_typical,winter_extreme,winter_narrow,winter_moderate,summer_typical,summer_negative,shoulder,flat")
ap.add_argument("--weather",default="winter_cold,winter_mild,shoulder,summer_cool")
ap.add_argument("--dhw",default="1")
a=ap.parse_args()
if a.off:
    _o=O.HeatPumpOptimizer._terminal_cost
    def zero(self,*x,**k):
        c,b=_o(self,*x,**k)
        return (lambda *aa,**kk:0.0),(lambda traj: np.zeros(traj["room"].shape[0]))
    O.HeatPumpOptimizer._terminal_cost=zero
start=datetime(2026,1,15); T=int(2/DT)
t0=time.process_time();th0=time.thread_time(); rows=[]
for tz in (False,True):
  for pp in a.prices.split(","):
    for wp in a.weather.split(","):
        cfg=house(two_zone=tz); p=ThermalParameters.from_config(cfg); p.dhw_enabled=bool(int(a.dhw))
        m=ThermalModel(p)
        opt=O.HeatPumpOptimizer(m,O.OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
        pr=prices(pp,start); ot,wi,ra,so=weather(wp,start)
        st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0,dhw_temperature=48.0)
        r=opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=start))
        pw=np.asarray(r.power_schedule,float); dw=np.asarray(getattr(r,"dhw_power_schedule",[]) or np.zeros_like(pw),float)
        room=np.asarray(r.room_temp_trajectory,float)
        tail=float((pw[-T:]+dw[-T:]).sum()*DT); br=float(np.maximum(0,17.0-room[-T:]).sum())
        rows.append((tail,room[-1],br,float(((pw+dw)*pr).sum()*DT)))
        print(f"CELL tz={int(tz)} {pp:16s} {wp:12s} tail_kwh={tail:.3f} end_room={room[-1]:.3f} tail_breach={br:.4f} energy_cost={rows[-1][3]:.3f}",flush=True)
R=np.array(rows)
print(f"RESULT cells={len(R)}")
print(f"RESULT mean_tail_kwh={R[:,0].mean():.4f} kWh")
print(f"RESULT mean_end_room={R[:,1].mean():.4f} C")
print(f"RESULT cells_tail_breach={int((R[:,2]>1e-6).sum())}")
print(f"RESULT mean_energy_cost={R[:,3].mean():.4f} SEK")
pc=time.process_time()-t0; tc=time.thread_time()-th0
print(f"RESULT thread_factor={pc/max(tc,1e-9):.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=na")
