import sys; sys.path.insert(0, 'tests')
import harness  # noqa
import numpy as np
from heatpump_optimizer.optimizer import HeatPumpOptimizer as P, OptimizationConfig as C
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as T
cfg = C(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0)
def ready(rate, **kw):
    params = T(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=rate, **kw)
    opt = P(M(params), cfg)
    w, _ = opt._effective_dhw_windows()
    r = opt._dhw_window_floors(params, w, np.arange(96)*0.25, None, 0.25, 96, None)
    return [(i, round(float(v), 6)) for i, v in enumerate(r[6]) if v]
for kw in ({}, dict(dhw_setpoint=24.0, dhw_min_temp=12.0, dhw_idle_min_temp=12.0),
           dict(dhw_setpoint=75.0, dhw_min_temp=40.0, dhw_idle_min_temp=40.0)):
    print(kw, ready(0.0, **kw), ready(1.5, **kw))
