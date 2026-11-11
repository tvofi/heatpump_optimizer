"""Reviewer's cadence probe (builder: round-2 reviewer). Per-minute tank physics, the
learner sampled every STEP minutes (production: optimization_interval, 10-120, default 30).
A charge (plan flag on while it runs) and one 15-min draw a day at an offset from the charge start.
Prints p90 / count of the all-day window and usage points, for the truth (no dip) and dip arms."""
import sys, importlib.util
spec = importlib.util.spec_from_file_location("h", sys.argv[1]); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
import numpy as np, types, asyncio
from datetime import datetime, timedelta
from heatpump_optimizer import dhw_learning as dl
from heatpump_optimizer.dhw_draws import labels_for
from heatpump_optimizer.thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters
def run(step, cstart, clen, off, dip, days=14):
    p=ThermalParameters(); p.dhw_enabled=True; cap=p.dhw_store.capacity_kwh_per_c
    clock=[datetime(2026,11,2)]; heating=[False]; pts=[0]
    L=dl.DhwProfileLearner(None,"h",lambda:p,publish=lambda **k:pts.__setitem__(0,pts[0]+1),frozen=lambda *a:None,heating_active=lambda:heating[0],external_heat_active=lambda:False)
    async def n(): return None
    L.async_save_draws=n; L.async_save_profile=n; L.cooling_rate=0.3
    dl.dt_util=types.SimpleNamespace(now=lambda:clock[0])
    draws=np.random.default_rng(7).lognormal(1.0,0.5,size=days); t=55.0; loop=asyncio.new_event_loop()
    dm=cstart+off
    for i in range(days*1440):
        day,m=divmod(i,1440)
        t-=0.3*(t-TANK_ROOM_AMBIENT_TEMP)/25/60
        if dm<=m<dm+15: t-=draws[day]/15/cap
        inch=cstart<=m<cstart+clen
        if inch: t+=(55-t)*0.13
        if i%step==0:
            clock[0]=datetime(2026,11,2)+timedelta(minutes=i); heating[0]=inch
            r=t-(h.dip_at(m-cstart) if dip else 0.0)
            loop.run_until_complete(L.async_learn_dynamics(round(r,2)))
    loop.close(); s=L.draw_stats; lab=labels_for(p.dhw_demand_windows)[0]
    q=s.quantile(lab,0.9); return (s.count(lab), None if q is None else round(q,4), pts[0])
for step in (10,15,30,60):
  for cstart,clen in ((450,10),(450,40),(455,15)):
    for off in (-30,-10,5,15,25,45):
      print(f"step={step} charge={cstart//60:02d}:{cstart%60:02d}+{clen} off={off:+d} truth={run(step,cstart,clen,off,False)} dip={run(step,cstart,clen,off,True)}",flush=True)
