import numpy as np, struct
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
import heatpump_optimizer.optimizer as O

def bits(x): return struct.pack('<d', float(x))

for kw in ({}, {"mixing_valve_mode": "manual", "buffer_tank_volume": 300.0, "cop_flow_carnot": True}):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(two_zone_enabled=True, **kw)), OptimizationConfig())
    real = O._terminal_row_cost
    cap = {}
    def capb(*a):
        out = real(*a); cap['spec'] = out[1]; return out
    O._terminal_row_cost = capb
    cost, cb = o._terminal_cost(np.full(96, 1.0), np.full(96, -5.0))
    O._terminal_row_cost = real
    spec = cap['spec']
    rng = np.random.default_rng(2512)
    traj = {k: rng.uniform(5.0, 32.0, size=(97, 5)) for k in ("room", "slab", "upper", "lower", "buffer")}
    sep = tot = 0
    for r in range(97):
        ends = {n: float(traj[n][r, -1]) for n in ("room", "slab", "upper", "lower", "buffer")}
        terms = [coef * max(0.0, cv - ends[n]) for coef, n, cv in spec]
        if not any(terms): continue
        tot += 1
        a = sum(terms)
        c = 0.0
        for t in terms: c += t
        if bits(a) != bits(c): sep += 1
    print(kw.get("mixing_valve_mode", "none"), "spec", [(round(c,1), n, round(v,1)) for c,n,v in spec])
    print("  rows", tot, "sum!=plain", sep)
