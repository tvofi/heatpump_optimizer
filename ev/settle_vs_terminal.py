"""Reviewer's instrument: under a derate, does _deferred_energy_cost (law on the
NET gap) equal f(D_plan) - f(D_ref), the difference of the two ends' refill
from their caps, which is what the objective's _terminal_cost prices? Anchor =
a state at 1000 C everywhere, which `caps` clamps to each store's cap."""
import sys, dataclasses, numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_partload_pricing as pp, r10_partload_residue as pr, r10_setpoint_boost as sb
from heatpump_optimizer import optimizer as om
real = om.HeatPumpOptimizer._deferred_energy_cost
rows = []
def defer(self, base, plan, prices, out, include_dhw=False, caps=None, humidity=None):
    v = real(self, base, plan, prices, out, include_dhw, caps, humidity)
    if caps:
        hot = dataclasses.replace(base, **{f.name: 1000.0 for f in dataclasses.fields(base)
                                           if f.name.endswith("temperature") and f.name != "outdoor_temperature"})
        via = real(self, hot, plan, prices, out, include_dhw, caps, humidity) - real(self, hot, base, prices, out, include_dhw, caps, humidity)
        rows.append((v, via))
    return v
om.HeatPumpOptimizer._deferred_energy_cost = defer
d = pr.central_derate()
for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
    for dd in (0.0, d):
        rows.clear()
        for cell in sb.CELLS:
            pp.solve(cell, prices, dd)
        g = [abs(a - b) for a, b in rows]
        print(f"{tag} d={dd}: capped deferred calls {len(rows)} | max |f(gap) - (f(D_plan)-f(D_ref))| {max(g, default=0):.6f} | max |deferred| {max((abs(a) for a,_ in rows), default=0):.4f}")
