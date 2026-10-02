"""_buffer_charge_ceiling over a grid: the ceiling it returns, per input."""
import itertools, json, sys
sys.path.insert(0, 'tests')
import harness  # noqa: F401
from heatpump_optimizer.optimizer import HeatPumpOptimizer as P, OptimizationConfig as C
from heatpump_optimizer.thermal_model import ThermalModel as M, ThermalParameters as T
cfg = C(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0)
out = []
temps = []
for fc, bmax, ref, two, ua_scale, pmax, outm, hum in itertools.product(
    (False, True),
    (25.0, 35.0, 45.0, 55.0, 65.0, 75.0), (0.0, 10.0, 20.0, 25.0, 35.0, 50.0),
    (False, True), (0.0, 1.0, 5.0), (0.5, 3.0, 9.0),
    (-30.0, -20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0), (None, 90.0),
):
    p = T(buffer_max_temp=bmax, cop_flow_reference_temp=ref, two_zone_enabled=two,
          max_electrical_power=pmax, buffer_tank_heat_loss=0.01 * ua_scale,
          buffer_cooling_rate=0.5 * ua_scale, flow_curve_cop=fc)
    opt = P(M(p), cfg)
    real = opt.model.marginal_cop
    def spy(*a, _real=real, **k):
        if a[1] == "buffer":
            temps.append(k["store_temp"])
        return _real(*a, **k)
    opt.model.marginal_cop = spy
    out.append(round(opt._buffer_charge_ceiling(outm, hum), 12))
import collections; print(len(out), len(set(out)), collections.Counter(out).most_common(4)); print('net() evaluations', len(temps), 'min tank temp evaluated', min(temps)); json.dump(out, open(sys.argv[1], 'w'))
