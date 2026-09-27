# Cross-seed probe: solve the 750 L winter_typical arm on tree A, then re-solve on tree A
# with plan P (from either tree) as the _prev_shipped_plan candidate; report objective_value.
import sys, os, io, contextlib, json
import numpy as np
root=sys.argv[1]; mode=sys.argv[2]; os.chdir(root); sys.path[:0]=[root+'/tests', root+'/tests/hastub', root]
src=open('tests/backtest.py').read(); cut=src.index('_store_gain = {}')
H={'__name__':'bt','__file__':root+'/tests/backtest.py'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], 'backtest.py', 'exec'), H)
def solve(vol, prof, seed=None):
    cfg = H['house'](two_zone=True, dhw=False, buffer_tank_volume=vol, buffer_max_temperature=70.0, mixing_valve_mode="manual")
    params = H['ThermalParameters'].from_config(cfg); params.dhw_enabled=False
    model = H['ThermalModel'](params)
    oc = H['OptimizationConfig'](horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
    opt = H['HeatPumpOptimizer'](model, oc)
    if seed is not None: opt._prev_shipped_plan = np.asarray(seed)
    ps = H['prices'](prof, H['START']); out, wind, rain, solar = H['weather']("winter_cold", H['START'])
    st = H['ThermalState'](room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0, slab_temperature=21.0, buffer_tank_temperature=H['_STORE_START'], outdoor_temperature=float(out[0]))
    r = opt.optimize(st, ps, out, wind, rain, solar, H['START'])
    return np.asarray(r.power_schedule), float(r.objective_value), float(r.predicted_cost)
vol=float(sys.argv[3]); prof=sys.argv[4]
if mode=='plan':
    p,j,c = solve(vol,prof); json.dump(p.tolist(), open(sys.argv[5],'w')); print(root[-8:], 'own', round(j,4), round(c,3))
else:
    seed=np.array(json.load(open(sys.argv[5])))
    p,j,c = solve(vol,prof,seed); print(root[-8:], 'seeded', os.path.basename(sys.argv[5]), round(j,4), round(c,3), 'ships_seed', bool(np.allclose(p,seed,atol=1e-3)))
