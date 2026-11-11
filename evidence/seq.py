"""Reviewer's sequence probe: one learner, 5-min samples, prints open-occurrence kWh."""
import types, asyncio, sys
from datetime import datetime, timedelta
from heatpump_optimizer import dhw_learning as dl
from heatpump_optimizer.thermal_model import ThermalParameters
def run(temps, heated_at):
    p=ThermalParameters(); p.dhw_enabled=True; p.dhw_schedule_enabled=False
    clock=[datetime(2026,11,3,8,0)]; heating=[False]
    L=dl.DhwProfileLearner(None,"h",lambda:p,publish=lambda **k:None,frozen=lambda *a:None,heating_active=lambda:heating[0],external_heat_active=lambda:False)
    async def n(): return None
    L.async_save_draws=n; L.async_save_profile=n; L.cooling_rate=0.3
    dl.dt_util=types.SimpleNamespace(now=lambda:clock[0])
    for i,t in enumerate(temps):
        clock[0]=datetime(2026,11,3,8,0)+timedelta(minutes=5*i); heating[0]=i in heated_at
        asyncio.run(L.async_learn_dynamics(t))
    return round(L.draw_stats.as_dict()["open_kwh"],4)
cap=ThermalParameters().dhw_store.capacity_kwh_per_c
print("cap kWh/K", round(cap,4))
# A: a 3 K draw before the charge, a 1 K charge-start dip, then 2 K of unheated rise inside the settle window
print("A pre-draw, 1K dip, two +1K settle rises :", run((50,47,47,47,46,47,48,48,48),(3,)))
print("A control: same, no second rise           :", run((50,47,47,47,46,47,47,47,47),(3,)))
# B: an 8 K drop during the charge, then three +3 K unheated rises all inside the settle window
print("B 8K drop, three +3K settle rises        :", run((50,50,42,45,48,51,51,51),(1,2)))
print("B control: one +3K rise                   :", run((50,50,42,45,45,45,45,45),(1,2)))
