"""D0.M4/M5/M6 capture-and-race on the summer_typical / summer_negative / shoulder / flat price axis.

Metric: per captured optimizer._multi_start_minimize call (the call whose x matches the shipped power_schedule),
rel_gap = (S_prod - S_best)/|S_prod| where S is the recorded objective(x,*args) and S_best is the best of
challengers raced through the SAME production _multi_start_minimize (same objective, bounds, args,
batch_objective/jac path): (A) production candidates + structured seeds (price-ranked bang-bang at energy
fractions 0.1..1.0 of the production plan's energy, zero, headroom, flat 0.25/0.5/0.75); (B) A at maxiter 3000
and ftol 1e-12 (via optimizer._scoped_minimize options). Feasibility parity: both plans are inside the
recorded bounds; comfort floor degree-steps (thermal_model simulate_trajectory via the objective's own room
trajectory is not exposed, so parity is checked as: challenger x within bounds; comfort is priced inside the
objective). M6: step0_diff = |x_prod[0]-x_best[0]| kW for gap cells.
Count key: objective value returned by the captured production objective.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s3/race.py [--prices flat] [--seeds prod]
Perturbation: --seeds prod (challenger = production candidates only, production budget) must give gap ~0.
Null control: --prices flat. Baseline 17f1c55fad1b, machine macOS arm64 (B3).
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
ap=argparse.ArgumentParser()
ap.add_argument("--prices",default="summer_typical,summer_negative,shoulder,flat")
ap.add_argument("--weather",default="winter_cold,winter_mild,summer_warm,summer_cool,shoulder")
ap.add_argument("--tz",default="0,1"); ap.add_argument("--dhw",default="0,1")
ap.add_argument("--seeds",default="full",choices=["full","prod"])
ap.add_argument("--tight",type=int,default=1,help="arm B (maxiter 3000, ftol 1e-12 polish) on/off")
ap.add_argument("--horizon",type=int,default=24)
a=ap.parse_args()
orig=O._multi_start_minimize; orig_sm=O._scoped_minimize
calls=[]
def cap(objective,candidates,bounds,args=(),maxiter=300,batch_objective=None,fd_eps=1e-4,move_starts=lambda c,m:c):
    res=orig(objective,candidates,bounds,args=args,maxiter=maxiter,batch_objective=batch_objective,fd_eps=fd_eps,move_starts=move_starts)
    calls.append(dict(obj=objective,cand=[np.array(c,float) for c in move_starts(list(candidates),maxiter)],bounds=bounds,args=args,maxiter=maxiter,bo=batch_objective,eps=fd_eps,x=np.array(res.x,float)))
    return res
O._multi_start_minimize=cap
TIGHT={"on":False}
def sm(*aa,**kk):
    if TIGHT["on"]:
        o=dict(kk.get("options",{})); o["ftol"]=1e-12; o["maxiter"]=3000; o["maxfun"]=200000; kk["options"]=o
    return orig_sm(*aa,**kk)
O._scoped_minimize=sm
def ranked(pr,e,ub):
    x=np.zeros(len(ub)); left=e/DT
    for i in np.argsort(pr,kind="stable"):
        t=min(ub[i],left); x[i]=t; left-=t
        if left<=1e-12: break
    return x
start=datetime(2026,7,15); rows=[]
t0=time.process_time();th0=time.thread_time()
for tz in [bool(int(v)) for v in a.tz.split(",")]:
 for dhw in [bool(int(v)) for v in a.dhw.split(",")]:
  for pp in a.prices.split(","):
   for wp in a.weather.split(","):
    cfg=house(two_zone=tz); p=ThermalParameters.from_config(cfg); p.dhw_enabled=dhw
    m=ThermalModel(p)
    opt=O.HeatPumpOptimizer(m,O.OptimizationConfig(horizon_hours=a.horizon,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
    n=int(a.horizon/DT)
    pr=prices(pp,start); ot,wi,ra,so=weather(wp,start)
    rep=lambda v: np.resize(v,n)
    pr,ot,wi,ra,so=map(rep,(pr,ot,wi,ra,so))
    st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0,dhw_temperature=48.0)
    calls.clear()
    res=opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=start))
    if not calls: print(f"CELL {pp}/{wp} tz={int(tz)} dhw={int(dhw)} no capture"); continue
    shp=np.asarray(res.power_schedule,float)
    c=min(calls,key=lambda k: float(np.abs(np.clip(k["x"],0,None)[:len(shp)]-shp).sum()) if len(k["x"])==len(shp) else 1e18); nc=len(calls)
    f=lambda x: float(c["obj"](x,*c["args"]))
    s_prod=f(c["x"]); ub=np.array([b[1] for b in c["bounds"]]); lb=np.array([b[0] for b in c["bounds"]])
    seeds=list(c["cand"])
    if a.seeds=="full":
        e=float(np.sum(c["x"])*DT)
        for fr in (0.1,0.2,0.35,0.5,0.75,1.0,1.25):
            seeds.append(np.maximum(ranked(pr[:len(ub)],e*fr,ub),lb))
        for fr in (0.0,0.25,0.5,0.75,1.0): seeds.append(np.clip(ub*fr,lb,ub))
        seeds.append(c["x"].copy())
    calls_before=len(calls)
    rA=orig(c["obj"],seeds,c["bounds"],args=c["args"],maxiter=c["maxiter"],batch_objective=c["bo"],fd_eps=c["eps"])
    best_x=np.array(rA.x); sA=f(best_x)
    if a.tight:
        TIGHT["on"]=True
        try: rB=orig(c["obj"],[best_x,c["x"]],c["bounds"],args=c["args"],maxiter=3000,batch_objective=c["bo"],fd_eps=c["eps"])
        finally: TIGHT["on"]=False
        sB=f(np.array(rB.x))
        if sB<sA: best_x=np.array(rB.x); sA=sB
    feas=bool(np.all(best_x>=lb-1e-9) and np.all(best_x<=ub+1e-9))
    g=(s_prod-sA)/max(abs(s_prod),1e-9)
    s0=abs(c["x"][0]-best_x[0])
    rows.append((g,s_prod-sA,s0))
    print(f"CELL tz={int(tz)} dhw={int(dhw)} {pp:16s} {wp:12s} calls={nc} S_prod={s_prod:.4f} S_best={sA:.4f} gap={g*100:.4f}% abs={s_prod-sA:.4f} step0_diff={s0:.3f}kW feas={feas}",flush=True)
G=np.array([r[0] for r in rows]); A=np.array([r[1] for r in rows])
srt=np.sort(G)
print(f"RESULT cells={len(G)}")
print(f"RESULT cells_gap_gt_0.1pct={int((G>1e-3).sum())}")
print(f"RESULT cells_gap_gt_1pct={int((G>1e-2).sum())}")
print(f"RESULT max_rel_gap={G.max()*100:.4f} %")
print(f"RESULT min_rel_gap={G.min()*100:.4f} %")
print(f"RESULT mean_rel_gap={G.mean()*100:.4f} %")
print(f"RESULT mean_rel_gap_drop_best_cell={srt[:-1].mean()*100:.4f} %")
print(f"RESULT max_abs_gap={A.max():.4f} objective-units")
pc=time.process_time()-t0; tc=time.thread_time()-th0
print(f"RESULT thread_factor={pc/max(tc,1e-9):.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=na")
