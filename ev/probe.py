"""Reviewer's probe (builder: the round-2 reviewer). Truth arms only (no dip):
a real draw near a planned DHW charge must be booked identically at base and head.
Varies sample cadence, draw start, and adds quantised sensor jitter."""
import sys, importlib.util, json
spec = importlib.util.spec_from_file_location("h", sys.argv[1]); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
import numpy as np, types, asyncio
from datetime import datetime, timedelta
from heatpump_optimizer import dhw_learning as dl
from heatpump_optimizer.dhw_draws import labels_for
from heatpump_optimizer.thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters

def run(step, draw_min, jitter, dip, days=14):
    params = ThermalParameters(); params.dhw_enabled = True
    cap = params.dhw_store.capacity_kwh_per_c
    clock=[datetime(2026,11,2)]; heating=[False]; pts=[0]
    L = dl.DhwProfileLearner(None,"h",lambda: params, publish=lambda **k: pts.__setitem__(0,pts[0]+1),
        frozen=lambda *a: None, heating_active=lambda: heating[0], external_heat_active=lambda: False)
    async def _n(): return None
    L.async_save_draws=_n; L.async_save_profile=_n; L.cooling_rate=0.3
    dl.dt_util = types.SimpleNamespace(now=lambda: clock[0])
    rng=np.random.default_rng(7); draws=rng.lognormal(1.0,0.5,size=days); nrng=np.random.default_rng(11)
    t=55.0; cs=None; loop=asyncio.new_event_loop()
    for i in range(days*24*60//step):
        now=clock[0]=datetime(2026,11,2)+timedelta(minutes=i*step)
        day,minute=divmod(i*step,1440); dt_h=step/60
        t -= 0.3*(t-TANK_ROOM_AMBIENT_TEMP)/25*dt_h
        if draw_min<=minute<draw_min+15: t -= draws[day]*(step/15)/cap
        if minute==450: cs=now
        inch = cs is not None and 0<=(now-cs).total_seconds()<600
        heating[0]=inch
        if inch: t += (55-t)/2*(step/5)
        r=t
        if dip and cs is not None:
            m=(now-cs).total_seconds()/60; r -= h.dip_at(m)
        if jitter: r += nrng.choice([-jitter,0,0,jitter])
        loop.run_until_complete(L.async_learn_dynamics(round(r,1) if jitter else round(r,2)))
    loop.close()
    s=L.draw_stats
    return {lab:(s.count(lab), None if s.quantile(lab,0.9) is None else round(s.quantile(lab,0.9),4)) for lab in labels_for(params.dhw_demand_windows)} | {"pts":pts[0]}
for step in (1,5,10):
  for dm in (440,452,460,465):
    for jit in (0,0.1):
      for dip in (False,True):
        print(f"step={step:2d} draw={dm//60:02d}:{dm%60:02d} jitter={jit} dip={int(dip)} {run(step,dm,jit,dip)}", flush=True)
