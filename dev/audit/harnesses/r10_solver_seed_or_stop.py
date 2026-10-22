#!/usr/bin/env python3
"""R10-SOLVER (#2240, class P4): is D0-s1-01's gap the seed set or the stop?

Written by the R10-SOLVER fixer. ``dev/audit/rounds/round10/D0/s1/race.py``'s
challenger c1 races production's candidates PLUS ten structured seeds PLUS
the shipped x itself through the production ``_multi_start_minimize``, so a
c1 win cannot say which of two refused knobs it is: more seeds (#1294,
refused on cost) or more descent from the shipped point (#1293's stop rule,
refused on money). This splits c1 into its two halves on every cell
race.py reports over 1e-3, on the same captured objective:

  seeds_only   -- production's candidates + the same ten seeds, no shipped x;
  restart_only -- the multi-start from ``[shipped x]`` alone (a fresh
                  L-BFGS-B run plus production's own polish).

Each is (J_prod - J_arm)/|J_prod| of the call's own objective; positive =
the arm beats production. A cell whose gap is seeds_only's and not
restart_only's is a seed gap. Null control: restart_only is the stop's own
arm -- on a cell where the stop were the cause it would carry the gap.

Run from a worktree root, with a race.py output from the same tree:

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s1/race.py > race.out
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_solver_seed_or_stop.py race.out
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ.setdefault(_v,"1")
import sys, re
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
from unittest import mock
from datetime import datetime
import numpy as np
from profiles import prices, weather, house, solve_inputs
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
ORIG=O._multi_start_minimize; START=datetime(2026,1,15)
cells=[l.split()[1:4] for l in open(sys.argv[1]) if l.startswith("cell") and float(re.search(r"gap_rel=(\S+)",l).group(1))>1e-3]
for tzs,pp,wp in cells:
    tz=int(tzs.split("=")[1])
    cfg=house(two_zone=tz); p=ThermalParameters.from_config(cfg); p.dhw_enabled=False
    m=ThermalModel(p); opt=O.HeatPumpOptimizer(m,O.OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0))
    pr=prices(pp,START)[:96]; ot,wi,ra,so=(s[:96] for s in weather(wp,START))
    st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
    caps=[]
    def wrap(objective,candidates,bounds,args=(),maxiter=300,batch_objective=None,fd_eps=1e-4,move_starts=lambda c,mi:c):
        cands=[np.array(c,float) for c in candidates]
        r=ORIG(objective,candidates,bounds,args=args,maxiter=maxiter,batch_objective=batch_objective,fd_eps=fd_eps,move_starts=move_starts)
        caps.append((objective,cands,bounds,args,maxiter,batch_objective,np.asarray(r.x,float))); return r
    with mock.patch.object(O,"_multi_start_minimize",wrap):
        opt.optimize(inputs=solve_inputs(initial_state=st,prices=pr,outdoor_temps=ot,wind_speeds=wi,precipitation=ra,solar_radiation=so,start_time=START))
    obj,cands,bounds,args,mi,bobj,px=caps[0]
    lb=np.array([b[0] for b in bounds]); ub=np.array([b[1] for b in bounds]); n=len(lb)
    e=float(px.sum()); order=np.argsort(pr[:n],kind="stable"); seeds=[]
    for frac in (0.3,0.5,0.7,1.0,1.3):
        s=np.zeros(n); left=e*frac
        for i in order:
            t=min(ub[i],left); s[i]=t; left-=t
            if left<=0: break
        seeds.append(s)
    seeds+=[ub*c for c in (0,.25,.5,.75,1.0)]
    seeds=[np.clip(s,lb,ub) for s in seeds]
    fp=float(obj(px,*args))
    fs=float(obj(ORIG(obj,list(cands)+seeds,bounds,args=args,maxiter=mi,batch_objective=bobj).x,*args))
    fr=float(obj(ORIG(obj,[px.copy()],bounds,args=args,maxiter=mi,batch_objective=bobj).x,*args))
    print(f"DECOMP tz={tz} {pp:16s} {wp:12s} seeds_only={(fp-fs)/abs(fp):.3e} restart_only={(fp-fr)/abs(fp):.3e}",flush=True)
