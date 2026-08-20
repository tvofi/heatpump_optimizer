import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_components"))
import numpy as np, traceback
from datetime import datetime
from profiles import prices, weather, house, DT, N
from heatpump_optimizer.thermal_model import ThermalModel,ThermalParameters,ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer,OptimizationConfig
FAIL=[]
def check(name, cond, msg):
    if not cond: FAIL.append(f"[{name}] {msg}")

def go(name, *, cfgmod=None, ocmod=None, price_p="winter_typical", weather_p="winter_cold",
       hours=24, stmod=None, prmod=None, wxmod=None):
    try:
        cfg=house(two_zone=False)
        if cfgmod: cfgmod(cfg)
        p=ThermalParameters.from_config(cfg); m=ThermalModel(p)
        kw=dict(horizon_hours=hours,time_step_minutes=15,target_temp=cfg["target_temperature"],
                min_temp=cfg["min_temperature"],max_temp=cfg["max_temperature"])
        if ocmod: ocmod(kw)
        oc=OptimizationConfig(**kw); opt=HeatPumpOptimizer(m,oc)
        start=datetime(2026,1,15)
        n=int(hours/DT)
        # Tile the 24 h profiles so horizons longer than a day get real data.
        def _fit(a):
            return np.concatenate([a] * (n // len(a) + 1))[:n]
        pr=_fit(prices(price_p,start)); ot,wi,ra,so=[_fit(a) for a in weather(weather_p,start)]
        if prmod is not None: pr=prmod(pr)
        if wxmod is not None: ot,wi,ra,so=wxmod(ot,wi,ra,so)
        st=ThermalState(room_temperature=21.0,slab_temperature=22.0,outdoor_temperature=float(ot[0]),
            dhw_temperature=50.0,dhw_hours_since_legionella=20.0,
            upper_floor_temperature=21.0,lower_floor_temperature=21.0,buffer_tank_temperature=40.0)
        if stmod: stmod(st)
        r=opt.optimize(st,pr,ot,wi,ra,so,start)
        pw=np.asarray(r.power_schedule)
        check(name,len(pw)==n,f"schedule len {len(pw)} != {n}")
        check(name,np.all(np.isfinite(pw)),"non-finite power")
        check(name,pw.min()>=-1e-6,f"negative power {pw.min():.3f}")
        check(name,pw.max()<=p.max_electrical_power+1e-6,f"power {pw.max():.2f} > max")
        check(name,np.isfinite(r.savings_percentage),"non-finite savings")
        check(name,-100<=r.savings_percentage<=100,f"savings {r.savings_percentage:.1f}% out of range")
        print(f"  ok  {name:<38} n={n:3d} kWh={pw.sum()*DT:7.2f} sav={r.savings_percentage:6.1f}% {r.status}")
    except Exception as e:
        FAIL.append(f"[{name}] EXCEPTION {type(e).__name__}: {e}")
        print(f"  FAIL {name:<38} {type(e).__name__}: {e}")

print("=== horizon / resolution edge cases ===")
go("1-step horizon", hours=0.25)
go("1-hour horizon", hours=1)
go("48-hour horizon", hours=48)
go("5-min steps", ocmod=lambda k: k.update(time_step_minutes=5), hours=6)

print("=== degenerate price curves ===")
go("all-identical prices", prmod=lambda pr: np.full_like(pr,1.0))
go("all-zero prices",      prmod=lambda pr: np.zeros_like(pr))
go("all-negative prices",  prmod=lambda pr: np.full_like(pr,-0.5))
go("single huge spike",    prmod=lambda pr: np.where(np.arange(len(pr))==40,50.0,0.5))

print("=== extreme weather ===")
go("extreme cold -25C", wxmod=lambda o,w,r,s:(np.full_like(o,-25.0),w,r,s))
go("storm 25 m/s",      wxmod=lambda o,w,r,s:(o,np.full_like(w,25.0),r,s))
go("very warm +30C",    wxmod=lambda o,w,r,s:(np.full_like(o,30.0),w,r,s))

print("=== initial states outside the band ===")
go("start cold 15C", stmod=lambda s: setattr(s,"room_temperature",15.0))
go("start hot 26C",  stmod=lambda s: setattr(s,"room_temperature",26.0))
go("start empty tank 15C", stmod=lambda s: setattr(s,"dhw_temperature",15.0))
go("legionella overdue", stmod=lambda s: setattr(s,"dhw_hours_since_legionella",500.0))

print("=== config extremes ===")
go("1500 L tank", cfgmod=lambda c: c.update(dhw_tank_volume=1500))
go("band collapsed (min==target)", cfgmod=lambda c: c.update(min_temperature=21.0))
go("very wide band 10-30", cfgmod=lambda c: c.update(min_temperature=10.0,max_temperature=30.0))

print()
print(f"{len(FAIL)} FAILURES" if FAIL else "ALL EDGE CASES PASS")
for f in FAIL: print("  "+f)
