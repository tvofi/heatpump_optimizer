import sys, os, io, contextlib
import numpy as np
root=sys.argv[1]; os.chdir(root); sys.path[:0]=[root+'/tests', root+'/tests/hastub', root]
src=open('tests/backtest.py').read(); cut=src.index('_store_gain = {}')
H={'__name__':'bt','__file__':root+'/tests/backtest.py'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], 'backtest.py', 'exec'), H)
import heatpump_optimizer.optimizer as O
orig=O._multi_start_minimize
calls=[0]
def wrap(objective, candidates, bounds, args=(), **kw):
    calls[0]+=1
    if calls[0]==1:
        for i,c in enumerate(candidates):
            try:
                r=orig(objective,[c],bounds,args,**kw)
                print(f"  seed{i:02d} start={float(objective(c,*args)):.3f} -> {float(objective(r.x,*args)):.4f}")
            except Exception as e: print('  seed',i,'err',e)
    return orig(objective,candidates,bounds,args,**kw)
O._multi_start_minimize=wrap
cfg = H['house'](two_zone=True, dhw=False, buffer_tank_volume=750.0, buffer_max_temperature=70.0, mixing_valve_mode="manual")
params = H['ThermalParameters'].from_config(cfg); params.dhw_enabled=False
model = H['ThermalModel'](params)
oc = H['OptimizationConfig'](horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
opt = H['HeatPumpOptimizer'](model, oc)
ps = H['prices']('winter_typical', H['START']); out, wind, rain, solar = H['weather']("winter_cold", H['START'])
st = H['ThermalState'](room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0, slab_temperature=21.0, buffer_tank_temperature=H['_STORE_START'], outdoor_temperature=float(out[0]))
r = opt.optimize(st, ps, out, wind, rain, solar, H['START'])
print(root[-8:], 'shipped', round(float(r.objective_value),4), 'msm calls', calls[0])
