"""D0-s2 tolerance race: is the residual gap the L-BFGS-B ftol=1e-6 stop?

Metric: per cell, relative gap = (J(prod.x) - J(polish))/|J(prod.x)| where J is the
captured optimizer:_multi_start_minimize objective and polish = scipy L-BFGS-B from
prod.x with ftol 1e-12 (same bounds/args), i.e. the descent production left on the
table at its own point; also prod nit/nfev summed over the call, counted via a
wrapper of optimizer:_scoped_minimize. Key: captured objective value.
Perturbation: --ftol F overrides the ftol that production passes to
optimizer:_scoped_minimize (both the main run and _lbfgsb_restart); gap must fall
toward 0 as F shrinks, and nfev rise.
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D0/s2/ftol_race.py [--ftol 1e-9]
Baseline 17f1c55fad1b, macOS arm64 box B2. Expected (ftol default): see REPORT.md, +-0.3 pp.
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
from profiles import prices, weather, house, solve_inputs, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer import optimizer as OM
ap=argparse.ArgumentParser(); ap.add_argument("--ftol",type=float,default=0.0)
ap.add_argument("--prices",default="winter_typical,winter_extreme,winter_narrow,winter_moderate,flat")
ap.add_argument("--weather",default="winter_cold,winter_mild")
ap.add_argument("--tz",default="1"); ap.add_argument("--dhw",default="1")
A=ap.parse_args()
REAL=OM._multi_start_minimize; RSM=OM._scoped_minimize
t0p,t0t=time.process_time(),time.thread_time()
CNT={"nfev":0,"nit":0}
def sm(*a,**kw):
    if A.ftol and "options" in kw:
        kw["options"]=dict(kw["options"],ftol=A.ftol)
    r=RSM(*a,**kw); CNT["nfev"]+=int(getattr(r,"nfev",0)); CNT["nit"]+=int(getattr(r,"nit",0)); return r
rows=[]
for pp in A.prices.split(","):
  for wp in A.weather.split(","):
    for tz in [bool(int(x)) for x in A.tz.split(",")]:
      for dh in [bool(int(x)) for x in A.dhw.split(",")]:
        start=datetime(2026,1,15)
        cfg=house(two_zone=tz,dhw=dh); p=ThermalParameters.from_config(cfg); p.dhw_enabled=dh
        m=ThermalModel(p); opt=HeatPumpOptimizer(m,OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
        pr=prices(pp,start); ot,wi,ra,so=weather(wp,start)
        st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
        calls=[]; CNT.update(nfev=0,nit=0)
        def cap(o,c,b,args=(),maxiter=300,**kw):
            r=REAL(o,c,b,args,maxiter,**kw); calls.append((o,b,args,np.array(r.x))); return r
        with mock.patch.object(OM,"_multi_start_minimize",cap), mock.patch.object(OM,"_scoped_minimize",sm):
            opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=start))
        nf,ni=CNT["nfev"],CNT["nit"]
        for i,(o,b,args,x) in enumerate(calls):
            f=lambda z: float(o(z,*args)); J0=f(x)
            pol=minimize(f,x,method="L-BFGS-B",bounds=b,options=dict(maxiter=5000,maxfun=100000,ftol=1e-12))
            g=max(0.0,(J0-pol.fun)/abs(J0)); cell=f"{pp}/{wp}/tz{int(tz)}/dhw{int(dh)}/call{i}"
            rows.append((pp,g))
            print(f"RESULT polish_gap[{cell}]={100*g:.4f} pct J0={J0:.4f} Jpol={pol.fun:.4f} dJ={J0-pol.fun:.4f} prod_nfev={nf} prod_nit={ni} step0_dkW={abs(pol.x[0]-x[0]):.3f}",flush=True)
for pp in A.prices.split(","):
    g=sorted(x for q,x in rows if q==pp)
    if g: print(f"RESULT polish_gap_max[{pp}]={100*g[-1]:.4f} pct mean={100*np.mean(g):.4f} n={len(g)}")
w=sorted(x for q,x in rows if q!="flat")
if len(w)>1: print(f"RESULT polish_gap_winter_mean={100*np.mean(w):.4f} pct n={len(w)} range={100*w[0]:.4f}..{100*w[-1]:.4f} drop_max_mean={100*np.mean(w[:-1]):.4f}")
pc,tc=time.process_time()-t0p,time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=n/a")
