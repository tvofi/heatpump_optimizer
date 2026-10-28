"""Reviewer probe (#2872): is delivered heat monotone in electrical power on the
band, for every derate _partload_derate accepts? Uses the tree's own helpers."""
import numpy as np
from heatpump_optimizer.thermal_model import (
    ThermalParameters, delivered_heat_kw, heat_per_cop_kw, _partload_derate)
from heatpump_optimizer import const

def peak(pmin, pmax, d, cop=3.0):
    p = ThermalParameters(min_electrical_power=pmin, max_electrical_power=pmax,
                          cop_partload_derate=d)
    P = np.linspace(pmin, pmax, 4001)
    q = delivered_heat_kw(p, cop, P)
    i = int(np.argmax(q))
    return P[i], q[i], float(delivered_heat_kw(p, cop, pmax))

print("cap", const.MAX_HEAT_PUMP_COP_PARTLOAD_DERATE,
      "accepted 0.5 ->", _partload_derate(0.5), "accepted 0.3 ->", _partload_derate(0.3))
for pmin, pmax in ((1.0, 5.0), (1.5, 5.0), (2.0, 5.0), (3.0, 5.0), (4.0, 5.0), (0.0, 5.0)):
    band = pmax - pmin
    dcrit = band / (band + pmax)
    for d in (0.112, 0.19, 0.3, 0.5):
        Pk, qk, qmax = peak(pmin, pmax, d)
        flag = "NON-MONOTONE" if qk > qmax + 1e-12 else "monotone"
        print(f"RESULT band [{pmin},{pmax}] d={d}: d_crit={dcrit:.3f} peak heat {qk:.4f} at P={Pk:.3f} vs heat at p_max {qmax:.4f} {flag}")
# null control: derate 0 is monotone and exactly cop*P
p0 = ThermalParameters(min_electrical_power=1.0, max_electrical_power=5.0, cop_partload_derate=0.0)
P = np.linspace(0, 5, 1001)
print("RESULT null d=0: bitwise cop*P", bool(np.array_equal(delivered_heat_kw(p0, 3.1, P), 3.1 * P)),
      "monotone", bool(np.all(np.diff(delivered_heat_kw(p0, 3.1, P)) > 0)))
# scalar vs elementwise parity at 0.15
p15 = ThermalParameters(min_electrical_power=1.0, max_electrical_power=5.0, cop_partload_derate=0.15)
rng = np.random.default_rng(0); Pv = rng.uniform(0, 6, 20000); cv = rng.uniform(1.5, 6, 20000)
vec = cv * heat_per_cop_kw(p15, Pv)
sca = np.array([delivered_heat_kw(p15, float(c), float(x)) for c, x in zip(cv, Pv)])
print("RESULT parity d=0.15 scalar vs vector bitwise", bool(np.array_equal(vec, sca)), "n", Pv.size)
