"""D0-s2 grid race (D0.M4 grid, D0.M5 flat null control, D0.M6 step-0 check).

Metric: per cell, relative objective gap = (J(prod.x) - J(best challenger))/|J(prod.x)|
on the EXACT captured production objective/bounds/args of every
optimizer:_multi_start_minimize call; plus |step-0 power difference| (kW).
Challenger = the real _multi_start_minimize on the captured objective with the
production starts + production x + bang-bang starts (energy fractions
0.25/0.5/0.75/1.0 of p_max on cheapest hours) at maxiter=1500, then a
scipy L-BFGS-B polish (ftol 1e-12, maxfun 1e5). Key: the captured objective value.
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D0/s2/grid_race.py
Optional args: --maxiter N  (perturbation: production maxiter override)
Baseline 17f1c55fad1b, machine: macOS arm64 (box B2). Expected: see REPORT.md, tolerance +-0.5 pp (BLAS).
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v,"1")
import sys, time, argparse
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from unittest import mock
from datetime import datetime
from scipy.optimize import minimize
from profiles import prices, weather, house, solve_inputs, N, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer import optimizer as OM

ap=argparse.ArgumentParser(); ap.add_argument("--maxiter",type=int,default=0)
ap.add_argument("--prices",default="winter_typical,winter_extreme,winter_narrow,winter_moderate,flat")
ap.add_argument("--weather",default="winter_cold,winter_mild")
ap.add_argument("--tz",default="0,1"); ap.add_argument("--dhw",default="0,1")
A=ap.parse_args()
REAL=OM._multi_start_minimize
t0p,t0t=time.process_time(),time.thread_time()

def bang(prices_, frac, pmax, bounds):
    hi=np.array([b[1] for b in bounds]); lo=np.array([b[0] for b in bounds])
    k=int(round(frac*len(prices_)))
    x=lo.copy(); idx=np.argsort(prices_)[:k]; x[idx]=hi[idx]; return x

def run_cell(pp,wp,tz,dhw):
    start=datetime(2026,1,15)
    cfg=house(two_zone=tz,dhw=dhw); p=ThermalParameters.from_config(cfg); p.dhw_enabled=dhw
    m=ThermalModel(p)
    opt=HeatPumpOptimizer(m,OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
    pr=prices(pp,start); ot,wi,ra,so=weather(wp,start)
    st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),
        upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
    calls=[]
    def cap(objective,candidates,bounds,args=(),maxiter=300,**kw):
        if A.maxiter: maxiter=A.maxiter
        r=REAL(objective,candidates,bounds,args,maxiter,**kw)
        calls.append(dict(obj=objective,cands=[np.array(c) for c in candidates],bounds=bounds,args=args,kw=kw,x=np.array(r.x),maxiter=maxiter))
        return r
    with mock.patch.object(OM,"_multi_start_minimize",cap):
        res=opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=start))
    out=[]
    pmax=float(m.params.max_electrical_power)
    for c in calls:
        f=lambda x: float(c["obj"](x,*c["args"]))
        J0=f(c["x"])
        n=len(c["bounds"]); prc=pr[:n]
        extra=[c["x"]]+[bang(prc,fr,pmax,c["bounds"]) for fr in (0.25,0.5,0.75,1.0)]
        kw=dict(c["kw"]); kw.pop("move_starts",None)
        r=REAL(c["obj"],c["cands"]+extra,c["bounds"],c["args"],1500,**kw)
        xb=np.array(r.x); Jb=f(xb)
        pol=minimize(f,xb,method="L-BFGS-B",bounds=c["bounds"],options=dict(maxiter=5000,maxfun=100000,ftol=1e-12))
        if pol.fun<Jb: xb,Jb=np.array(pol.x),float(pol.fun)
        out.append((J0,Jb,(J0-Jb)/abs(J0) if J0 else 0.0,abs(c["x"][0]-xb[0]),float(np.sum(prc*c["x"]*DT)),float(np.sum(prc*xb*DT))))
    return out

rows=[]
for pp in A.prices.split(","):
  for wp in A.weather.split(","):
    for tz in [bool(int(x)) for x in A.tz.split(",")]:
      for dh in [bool(int(x)) for x in A.dhw.split(",")]:
        o=run_cell(pp,wp,tz,dh)
        for i,(J0,Jb,g,d0,e0,eb) in enumerate(o):
            cell=f"{pp}/{wp}/tz{int(tz)}/dhw{int(dh)}/call{i}"
            rows.append((pp,cell,g,d0))
            print(f"RESULT gap[{cell}]={100*g:.4f} pct  J0={J0:.4f} Jbest={Jb:.4f} step0_dkW={d0:.3f} energySEK prod={e0:.2f} best={eb:.2f}",flush=True)
for pp in A.prices.split(","):
    g=[r[2] for r in rows if r[0]==pp]
    if not g: continue
    gs=sorted(g)
    print(f"RESULT gap_mean[{pp}]={100*np.mean(g):.4f} pct n={len(g)} range={100*gs[0]:.4f}..{100*gs[-1]:.4f} drop_max_mean={100*np.mean(gs[:-1]) if len(gs)>1 else float('nan'):.4f}")
    print(f"RESULT cells_gap_gt_0.5pct[{pp}]={sum(1 for x in g if x>0.005)} count")
pc,tc=time.process_time()-t0p,time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=n/a")
