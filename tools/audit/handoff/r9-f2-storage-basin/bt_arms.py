import sys, os, io, contextlib
import numpy as np
root=sys.argv[1]; os.chdir(root); sys.path[:0]=[root+'/tests', root+'/tests/hastub', root]
src=open('tests/backtest.py').read()
cut=src.index('_store_gain = {}')
g={'__name__':'bt','__file__':root+'/tests/backtest.py'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], 'backtest.py', 'exec'), g)
# instrumented copy of _storage_arm
H=g
def arm(volume, prof):
    cfg = H['house'](two_zone=True, dhw=False, buffer_tank_volume=volume, buffer_max_temperature=70.0, mixing_valve_mode="manual")
    params = H['ThermalParameters'].from_config(cfg); params.dhw_enabled=False
    model = H['ThermalModel'](params)
    oc = H['OptimizationConfig'](horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
    opt = H['HeatPumpOptimizer'](model, oc)
    ps = H['prices'](prof, H['START']); out, wind, rain, solar = H['weather']("winter_cold", H['START'])
    st = H['ThermalState'](room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0, slab_temperature=21.0, buffer_tank_temperature=H['_STORE_START'], outdoor_temperature=float(out[0]))
    r = opt.optimize(st, ps, out, wind, rain, solar, H['START'])
    p = np.asarray(r.power_schedule)
    s = H['score'](model, oc, p, ps, out, wind, rain, solar, st)
    room, slab, up, lo, buf, _, _ = model.simulate_trajectory(st, p, out, wind, rain, solar, H['DT'])
    m = model.params
    ed = (m.upper_floor_thermal_mass*(up[-1]-20)+m.lower_floor_thermal_mass*(lo[-1]-20)+m.slab_thermal_mass*(slab[-1]-21)+m.buffer_tank_thermal_mass*(min(buf[-1],70)-H['_STORE_START']))
    refill=float(np.percentile(ps,25)); cop=model.compute_cop(float(np.mean(out)))
    return dict(cost=round(s['cost'],3), viol=round(s['violation'],3), settle=round(ed*refill/cop,3), net=round(s['cost']-ed*refill/cop,3), kwh=round(float(p.sum())*0.25,2), up_end=round(up[-1],2), lo_end=round(lo[-1],2), buf_end=round(buf[-1],1), umin=round(float(np.min(up)),2), lmin=round(float(np.min(lo)),2), obj=round(float(r.predicted_cost),3))
for prof in ("winter_typical","flat"):
    for v in (99.0,750.0):
        print(root[-8:], prof, v, arm(v,prof))
