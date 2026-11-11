"""Reviewer's probe (the reviewer's instrument, not the finder's): the schedule figure and the pair on fixtures the PR's harnesses do not read."""
import sys, math, time
from dataclasses import replace
from datetime import datetime, timedelta
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_advisor_degree as deg
from profiles import DT, house, solve_inputs
from heatpump_optimizer import price_tiles, whatif
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

N = deg.N
pr, wx = deg._series(3, False)

def mk(two_zone, dhw, **cfgover):
    cfg = house(two_zone=two_zone, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    if not dhw: params.dhw_enabled = False
    kw = dict(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0, comfort_temp_day=21.0, comfort_temp_night=19.5)
    kw.update(cfgover)
    return HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(**kw)), params

def st(room=21.0, slab=22.0, out=0.0, dhw=52.0, buf=40.0):
    return ThermalState(room_temperature=room, slab_temperature=slab, outdoor_temperature=out, upper_floor_temperature=room, lower_floor_temperature=room, dhw_temperature=dhw, dhw_hours_since_legionella=20.0, buffer_tank_temperature=buf)

def inp(j, state, start=deg.START, pv=None):
    sl = slice(j, j + N)
    return solve_inputs(initial_state=state, prices=pr[sl], outdoor_temps=wx[0][sl], wind_speeds=wx[1][sl], precipitation=wx[2][sl], solar_radiation=wx[3][sl], start_time=start + timedelta(hours=j * DT), pv_surplus=pv)

def shadow(opt, params, ov):
    c, p = whatif.scratch_copies(opt.config, params, ov)
    return HeatPumpOptimizer(ThermalModel(p), c)

SCHED = [("day-1", {"comfort_temp_day": 20.0}, -1), ("day+1", {"comfort_temp_day": 22.0}, 1), ("night-1", {"comfort_temp_night": 18.5}, -1), ("night+1", {"comfort_temp_night": 20.5}, 1),
         ("daystart-1h", {"day_start_hour": None}, 1), ("dayend-1h", {"day_end_hour": None}, -1)]

def sched_asks(opt):
    out = []
    for n, ov, want in SCHED:
        ov = dict(ov)
        if "day_start_hour" in ov: ov["day_start_hour"] = opt.config.day_start_hour - 1
        if "day_end_hour" in ov: ov["day_end_hour"] = opt.config.day_end_hour - 1
        out.append((n, ov, want))
    return out

for two_zone in (False, True):
    for dhw in (False, True):
        opt, params = mk(two_zone, dhw)
        rows = wrong = none = 0; spread = 0.0; kmin = 1e9; kmax = -1e9
        for hour in range(1, 24, 2):
            j = int(hour / DT)
            for n, ov, want in sched_asks(opt):
                figs = []
                for s in (st(), st(20.4, 21.3), st(21.7, 23.0), st(21.0, 22.0, dhw=42.0, buf=30.0), st(19.0, 19.0, dhw=58.0, buf=50.0)):
                    i = inp(j, s)
                    days = whatif.schedule_days((shadow(opt, params, {}), i), (shadow(opt, params, ov), i))
                    if days is None: none += 1; continue
                    f = price_tiles.schedule_figure(*days, float(np.mean(i.forecast.prices)), 0.0, 24.0).get(whatif.STEADY_KEY)
                    figs.append(f); kmin = min(kmin, days[0]); kmax = max(kmax, days[0])
                if not figs: continue
                rows += 1
                spread = max(spread, max(figs) - min(figs))
                wrong += any(f is None or f * want <= 0 for f in figs)
        print(f"RESULT probe schedule two_zone={two_zone} dhw={dhw}: rows {rows} against the ask {wrong} branch-None {none} max spread over 5 measured states {spread:.4f} live day kWh {kmin:.2f}..{kmax:.2f}", flush=True)

# weekend boundary: Friday 2026-01-09, weekend day comfort differs
opt, params = mk(False, False, comfort_temp_day_weekend=22.0, comfort_temp_night_weekend=20.0)
fri = datetime(2026, 1, 9, 0, 0)
rows = wrong = none = 0
for hour in range(1, 24, 2):
    j = int(hour / DT)
    for n, ov, want in sched_asks(opt) + [("wkday+1", {"comfort_temp_day_weekend": 23.0}, 1), ("wknight-1", {"comfort_temp_night_weekend": 19.0}, -1)]:
        i = inp(j, st(), start=fri)
        days = whatif.schedule_days((shadow(opt, params, {}), i), (shadow(opt, params, ov), i))
        if days is None: none += 1; continue
        f = price_tiles.schedule_figure(*days, float(np.mean(i.forecast.prices)), 0.0, 24.0).get(whatif.STEADY_KEY)
        rows += 1; bad = f is None or f * want <= 0; wrong += bad
        if bad: print(f"  row weekend {hour:02d}:00 {n} fig {f} days {days}")
print(f"RESULT probe weekend (Fri->Sat, weekend comfort set): rows {rows} against the ask {wrong} branch-None (reads the pair) {none}", flush=True)

# the pair on a tanked house: hot-water asks, sign and spread by measured state
opt, params = mk(False, True)
for n, ov in (("dhw_setpoint+5", {"dhw_setpoint": 60.0}), ("dhw_min+5", {"dhw_min_temperature": 50.0}), ("dhw_setpoint-5", {"dhw_setpoint": 50.0})):
    for hour in (1, 9, 17):
        j = int(hour / DT); figs = []
        for s in (st(), st(20.4, 21.3), st(21.0, 22.0, dhw=44.0), st(21.0, 22.0, dhw=58.0)):
            i = replace(inp(j, s), held_start=True)
            assert whatif.schedule_days((shadow(opt, params, {}), i), (shadow(opt, params, ov), i)) is None
            t = time.time()
            live = shadow(opt, params, {}).optimize(inputs=i); sim = shadow(opt, params, ov).optimize(inputs=i)
            figs.append(price_tiles.monthly_deltas(live, sim, 0.0, 24.0, steady=(live, sim))[whatif.STEADY_KEY])
        print(f"RESULT probe pair tanked {n} {hour:02d}:00 steady by state (base, coasted, tank 44, tank 58) {' '.join(f'{f:+8.1f}' for f in figs)} spread {max(figs)-min(figs):.1f}", flush=True)
