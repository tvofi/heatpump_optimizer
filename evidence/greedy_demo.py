"""Reviewer's own probe (out of tree): does the stage-2 cheapest-first repair,
which still converts heat to power with take / (cop * dt), meet the tank floor
under a part-load derate, as the stage-1 LP now does?"""
import sys, numpy as np
sys.path[:0]=["tests/hastub","custom_components","tests"]
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
cfg=OptimizationConfig(horizon_hours=24,time_step_minutes=15,target_temp=21.0,min_temp=17.0,max_temp=23.0)
def run(derate, p_dhw_max, dt, n, floor, start=45.0, seed=False):
    p=ThermalParameters(dhw_enabled=True,dhw_tank_volume=200.0,cop_partload_derate=derate)
    opt=HeatPumpOptimizer(ThermalModel(p),cfg)
    pl=DhwPlanner(opt.model,opt.config,opt._pv_surplus,opt._price_known)
    req=np.full(n,40.0); req[-1]=floor
    prices=np.array([5.0]*(n-1)+[1.0]); out=np.full(n,5.0); draws=np.zeros(n)
    ctx=_DhwPlanContext(prices=prices,import_prices=prices,outdoor_temps=out,humidity=None,n_steps=n,dt=dt,
        c_dhw=p.dhw_tank_thermal_mass,p_dhw_max=p_dhw_max,min_run_power=0.1,max_lead_steps=24)
    init=None
    if seed: init=pl._plan_dhw_min_cost(ctx,start,req,draws,np.full(n,65.0))
    plan=pl._plan_dhw_cheapest_first(ctx,start,req,draws,np.full(n,65.0),initial_plan=init)
    T=opt.model.simulate_dhw_only(initial_temp=start,dhw_power_schedule=plan,outdoor_temps=out,draw_rates=draws,dt_hours=dt)
    return float(T[-1]), float(plan.sum()*dt), float(plan.max())
for seed in (False, True):
  for d in (0.0,0.2):
    for (pmax,dt,n,floor) in [(3.0,1.0,8,58.0),(2.0,0.5,8,58.0),(5.0,0.25,24,60.0)]:
        T,kwh,mx=run(d,pmax,dt,n,floor,seed=seed)
        print(f"RESULT cheapest_first seed={'LP' if seed else 'none'} d={d} p_dhw_max={pmax} dt={dt}: end {T:.3f} C vs floor {floor} ({'MET' if T>=floor-0.05 else 'SHORT'}) kWh {kwh:.3f} max {mx:.3f}")
