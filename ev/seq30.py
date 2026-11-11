"""Reviewer's minimal 30-min sequence (builder: round-2 reviewer). Prints the open occurrence in kWh.
07:00 50.0 | 07:30 47.0 (plan flag on: a 3 K draw 07:00-07:30, before the charge) |
08:00 heated interval | 08:30 unheated. truth: 08:00 48.0, 08:30 48.0 (charge heats +1, no dip).
dip: 08:00 44.0 (the same +1 heat under a 4 K dip), 08:30 48.0 (dip recovered)."""
import types, asyncio
from datetime import datetime, timedelta
from heatpump_optimizer import dhw_learning as dl
from heatpump_optimizer.thermal_model import ThermalParameters
def run(temps, heated_at, step=30):
    p=ThermalParameters(); p.dhw_enabled=True; p.dhw_schedule_enabled=False
    t0=datetime(2026,11,3,7,0); clock=[t0]; heating=[False]
    L=dl.DhwProfileLearner(None,"h",lambda:p,publish=lambda **k:None,frozen=lambda *a:None,heating_active=lambda:heating[0],external_heat_active=lambda:False)
    async def n(): return None
    L.async_save_draws=n; L.async_save_profile=n; L.cooling_rate=0.3
    dl.dt_util=types.SimpleNamespace(now=lambda:clock[0])
    for i,t in enumerate(temps):
        clock[0]=t0+timedelta(minutes=step*i); heating[0]=i in heated_at
        asyncio.run(L.async_learn_dynamics(t))
    return round(L.draw_stats.as_dict()["open_kwh"],4)
print("truth", run((50.0,47.0,48.0,48.0,48.0),(1,)))
print("dip  ", run((50.0,47.0,44.0,48.0,48.0),(1,)))
print("no-charge control (flag never on, dip trace)", run((50.0,47.0,44.0,48.0,48.0),()))
