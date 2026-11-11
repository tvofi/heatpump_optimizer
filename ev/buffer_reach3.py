import sys, numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_sav_wood_reference as h
from heatpump_optimizer import optimizer as om
seen = {}
real = om._terminal_row_cost
def wrap(rp, ce, cb, stores, refill=None):
    seen["c"] = (ce, cb, refill is not None, [s[1] for s in stores])
    return real(rp, ce, cb, stores, refill)
om._terminal_row_cost = wrap
for d in (0.0, 0.2):
    opt, model = h._install(False, True)
    model.params.cop_partload_derate = d
    prices, out = np.linspace(0.5, 2.0, 96), np.full(96, -5.0)
    cost, _ = opt._terminal_cost(prices, out)
    t = np.full(96, 12.0)
    print(f"d={d} valve={model.params.mixing_valve_mode} buffer_is_store={model.params.buffer_is_store} (cop_end, cop_buffer, law, stores)={seen['c']} terminal={cost(t, t, t, t, t):.6f}")
