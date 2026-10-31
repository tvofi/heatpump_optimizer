"""D0.M7 decomposition race: does iterating the DHW<->space split more than once lower the objective?

Metric: per cell, rel_gap = (S1 - SK)/|S1| where S1 is the space-stage objective
score production ships after its single _co_optimize pass and SK the score after
iterating that same pass (same planner, same solve_space, same adoption rule) up to
K=6 times until it stops changing. Count key: the objective value solve_space
(HeatPumpOptimizer._solve_space) returns for the adopted (space,dhw) pair.
--cold widens the replan pass's space solve from the warm start alone to warm+cold multi-start.
Also reports how often the first pass fires/adopts.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s3/decomp.py [--k 1]
Perturbation: --k 1 (iteration count 1 == production) must give gap 0 everywhere;
  raising K is the challenger. Production one-line edit: wrap _co_optimize in a loop.
Expected: see REPORT.md; tolerance 1e-6 relative. Baseline 17f1c55fad1b, machine: macOS arm64 (B3).
"""
import os
for _k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k,"1")
import sys, time, argparse
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from datetime import datetime
from profiles import prices, weather, house, solve_inputs
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import optimizer as O

ap=argparse.ArgumentParser(); ap.add_argument("--k",type=int,default=6)
ap.add_argument("--prices",default="winter_typical,winter_extreme,winter_narrow,winter_moderate,summer_typical,summer_negative,shoulder,flat")
ap.add_argument("--weather",default="winter_cold,winter_mild,shoulder,summer_cool")
ap.add_argument("--tz",default="0,1")
ap.add_argument("--cold",action="store_true",help="challenger: the replan pass also solves space cold (full multi-start) and keeps the better")
a=ap.parse_args()
orig=O.HeatPumpOptimizer._co_optimize
rec={}
def looped(self,h,*,space_power,dhw_power,status,best_score,solve_space,p_max,planner):
    s0=best_score; rec.update(s1=None,sK=None,fires=0,adopt=0)
    sp,dp,st,best=space_power,dhw_power,status,best_score
    for k in range(a.k):
        last={}
        def ss(d,w):
            r=solve_space(d,w)
            if a.cold:
                rc=solve_space(d,None)
                if rc[2]<r[2]: r=rc
            last["s"]=r[2]; return r
        nsp,ndp,nst=orig(self,h,space_power=sp,dhw_power=dp,status=st,best_score=best,solve_space=ss,p_max=p_max,planner=planner)
        if "s" in last: rec["fires"]+=1
        changed = nsp is not sp
        if changed: rec["adopt"]+=1; best=last["s"]
        sp,dp,st=nsp,ndp,nst
        if k==0: rec["s1"]=best
        if not changed: break
    rec["s0"]=s0; rec["sK"]=best
    return sp,dp,st
O.HeatPumpOptimizer._co_optimize=looped
start=datetime(2026,1,15)
gaps=[];t0=time.process_time();th0=time.thread_time()
for tz in [bool(int(x)) for x in a.tz.split(",")]:
  for pp in a.prices.split(","):
    for wp in a.weather.split(","):
        cfg=house(two_zone=tz); p=ThermalParameters.from_config(cfg); p.dhw_enabled=True
        m=ThermalModel(p)
        opt=O.HeatPumpOptimizer(m,O.OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
        pr=prices(pp,start); ot,wi,ra,so=weather(wp,start)
        st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0,dhw_temperature=48.0)
        rec.clear()
        opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=start))
        if rec.get("s1") is None: print(f"CELL tz={int(tz)} {pp}/{wp} co_optimize not reached"); continue
        g=(rec["s1"]-rec["sK"])/max(abs(rec["s1"]),1e-9)
        gaps.append((f"{int(tz)}/{pp}/{wp}",g,rec["s1"]-rec["sK"]))
        print(f"CELL tz={int(tz)} {pp:16s} {wp:12s} s0={rec['s0']:.4f} s1={rec['s1']:.4f} sK={rec['sK']:.4f} fires={rec['fires']} adopt={rec['adopt']} gap={g*100:.4f}%",flush=True)
G=np.array([g for _,g,_ in gaps]); A=np.array([d for *_,d in gaps])
print(f"RESULT cells={len(G)}")
print(f"RESULT cells_gap_gt_1e-6={int((G>1e-6).sum())}")
print(f"RESULT max_rel_gap={G.max()*100:.4f} %")
print(f"RESULT mean_rel_gap={G.mean()*100:.4f} %")
srt=np.sort(G); print(f"RESULT mean_rel_gap_drop_best_cell={srt[:-1].mean()*100 if len(srt)>1 else 0:.4f} %")
print(f"RESULT max_abs_gap={A.max():.4f} objective-units")
pc=time.process_time()-t0; tc=time.thread_time()-th0
print(f"RESULT thread_factor={pc/max(tc,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=na")
