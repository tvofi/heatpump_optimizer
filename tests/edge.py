import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "custom_components"))
import numpy as np, traceback
from datetime import datetime
from profiles import prices, weather, house, DT, N
from profiles import solve_inputs  # noqa: E402
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
        r=opt.optimize(inputs=solve_inputs(
            initial_state=st,
            prices=pr,
            outdoor_temps=ot,
            wind_speeds=wi,
            precipitation=ra,
            solar_radiation=so,
            start_time=start,
        ))
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

print("=== two-tank topology nulls (issue #40) ===")
# End-to-end through the full solve, not just the model: an unusable wood
# tank must not move a single decision, and a warm one must displace HP
# energy. The 5 C arm is the byte-identity null -- a tank colder than any
# temperature the solver can drive a zone to can never be drawn on. A tank
# at 15 C is deliberately NOT byte-equal: a coasting slab falls below 15,
# and 15 C water genuinely heats a 14 C slab (verified while writing this).
def _two_tank_run(wood_temp):
    cfg = house(two_zone=True)
    cfg.update(mixing_valve_mode="manual", buffer_tank_volume=750.0,
               buffer_max_temperature=70.0, wood_tank_volume=500.0)
    if wood_temp is not None:
        cfg["wood_tank_top_entity"] = "sensor.wood_top"
    p = ThermalParameters.from_config(cfg)
    m = ThermalModel(p)
    oc = OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                            target_temp=cfg["target_temperature"],
                            min_temp=cfg["min_temperature"],
                            max_temp=cfg["max_temperature"])
    opt = HeatPumpOptimizer(m, oc)
    start = datetime(2026, 1, 15)
    pr = prices("winter_typical", start)
    ot, wi, ra, so = weather("winter_cold", start)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), dhw_temperature=50.0,
                      dhw_hours_since_legionella=20.0,
                      upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      buffer_tank_temperature=32.0,
                      wood_tank_temperature=wood_temp)
    r = opt.optimize(inputs=solve_inputs(
        initial_state=st,
        prices=pr,
        outdoor_temps=ot,
        wind_speeds=wi,
        precipitation=ra,
        solar_radiation=so,
        start_time=start,
    ))
    return np.asarray(r.power_schedule)

try:
    _off = _two_tank_run(None)
    _cold = _two_tank_run(5.0)
    check("two-tank null", np.array_equal(_off, _cold),
          "an unusable 5 C wood tank changed the schedule")
    print(f"  ok  {'unusable wood tank: byte-equal plan':<38} "
          f"kWh={_off.sum()*DT:7.2f}")
    _warm = _two_tank_run(55.0)
    check("two-tank warm", float(_warm.sum()) < float(_off.sum()) - 1e-6,
          f"a 55 C wood tank did not displace HP energy "
          f"({_warm.sum()*DT:.2f} vs {_off.sum()*DT:.2f} kWh)")
    print(f"  ok  {'warm wood tank displaces HP energy':<38} "
          f"kWh={_warm.sum()*DT:7.2f} < {_off.sum()*DT:7.2f}")
except Exception as e:
    FAIL.append(f"[two-tank nulls] EXCEPTION {type(e).__name__}: {e}")
    print(f"  FAIL two-tank nulls {type(e).__name__}: {e}")

# -- #3616 R11-OUTSIDE-ROOMS-P2: the room lift through the production solve ----
# rooms.lifted's own array as SolveLimits.min_temp_margins, on the mild
# day of dev/audit/harnesses/room_lift_solve.py: floor 19.5, target 20.0, the
# house at 19.6, room A three kelvin under its target.
from datetime import UTC  # noqa: E402
from heatpump_optimizer import rooms as _rooms  # noqa: E402

_RL_START = datetime(2026, 4, 15, 12, 0, tzinfo=UTC)
_RL_OC = OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=20.0,
                            min_temp=19.5, max_temp=23.0, comfort_temp_day=20.0,
                            comfort_temp_night=20.0)


class _RlOwner:
    """What rooms' side tables key on in place of a coordinator."""


def _rl_margins(**signals):
    owner = _RlOwner()
    _rooms.record(owner, (
        _rooms.RoomReading("climate.a", 18.0, target_c=21.0, hvac_mode="heat"),
        _rooms.RoomReading("climate.d", 17.0, target_c=22.0, hvac_mode="off")))
    gated = _rooms.gate(**dict(dict(enabled=True, economy=False, open_window=False, away=False,
                                    manual_pin=False, two_zone=False), **signals))
    held = _rooms.resolve(_rooms.readings_of(owner), None, gated, _RL_OC, 19.6, _RL_START)
    return _rooms.lifted(held, None, _RL_OC, _RL_START, N)


def _rl_run(margins, pins=None):
    params = ThermalParameters.from_config(house(target_temperature=20.0, min_temperature=19.5))
    ot, wi, ra, so = weather("shoulder", _RL_START)
    st = ThermalState(room_temperature=19.6, slab_temperature=20.6,
                      outdoor_temperature=float(ot[0]), dhw_temperature=50.0,
                      dhw_hours_since_legionella=20.0, upper_floor_temperature=19.6,
                      lower_floor_temperature=19.6, buffer_tank_temperature=40.0)
    return HeatPumpOptimizer(ThermalModel(params), _RL_OC).optimize(inputs=solve_inputs(
        initial_state=st, prices=prices("winter_typical", _RL_START), outdoor_temps=ot,
        wind_speeds=wi, precipitation=ra, solar_radiation=so, start_time=_RL_START,
        min_temp_margins=margins, space_pins=pins))


try:
    _rl_lift = _rl_margins()
    _rl_none, _rl_zero, _rl_on = _rl_run(None), _rl_run(np.zeros(N)), _rl_run(_rl_lift)
    _rl_low = lambda r: float(np.min(r.room_temp_trajectory[1 + int(3 / DT):]))  # noqa: E731
    _rl_kwh = lambda r: float(np.sum(r.power_schedule) * DT)  # noqa: E731
    check("room lift null", _rl_none.power_schedule == _rl_zero.power_schedule
          and all(_rl_margins(**{k: k != "enabled"}) is None for k in
                  ("enabled", "economy", "open_window", "away", "manual_pin", "two_zone")),
          "an all-zero margin array, or a gated lift, did not reproduce the unlifted plan's inputs")
    check("room lift plan", _rl_lift is not None and _rl_low(_rl_on) > _rl_low(_rl_none) + 0.2
          and _rl_kwh(_rl_on) > _rl_kwh(_rl_none) + 0.5,
          f"the lift did not raise the lowest planned temperature and the space energy "
          f"({_rl_low(_rl_none):.3f} -> {_rl_low(_rl_on):.3f} C, "
          f"{_rl_kwh(_rl_none):.2f} -> {_rl_kwh(_rl_on):.2f} kWh)")
    print(f"  ok  {'room lift: floor held, more heat':<38} "
          f"min={_rl_low(_rl_none):.3f}->{_rl_low(_rl_on):.3f} C "
          f"kWh={_rl_kwh(_rl_none):.2f}->{_rl_kwh(_rl_on):.2f}")
    # Why a manual pin gates the lift: forced into a plan with a forced-off
    # pin, the lifted floor releases pinned steps the unlifted plan keeps.
    _rl_pins = np.full(N, np.nan)
    _rl_pins[int(1 / DT):int(3 / DT)] = 0.0
    _rl_kept, _rl_forced = _rl_run(None, _rl_pins), _rl_run(_rl_lift, _rl_pins)
    check("room lift pins", _rl_kept.manual_released_space == []
          and len(_rl_forced.manual_released_space) > 0,
          f"released: unlifted {_rl_kept.manual_released_space}, "
          f"lift forced in {_rl_forced.manual_released_space}")
    print(f"  ok  {'room lift: a pin is why it is gated':<38} "
          f"released {len(_rl_kept.manual_released_space)} unlifted, "
          f"{len(_rl_forced.manual_released_space)} with the lift forced in")
except Exception as e:
    FAIL.append(f"[room lift] EXCEPTION {type(e).__name__}: {e}")
    print(f"  FAIL room lift {type(e).__name__}: {e}")

print()
print(f"{len(FAIL)} FAILURES" if FAIL else "ALL EDGE CASES PASS")
for f in FAIL: print("  "+f)
sys.exit(1 if FAIL else 0)
