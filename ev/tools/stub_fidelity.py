"""Reviewer probe: baseline_cost with the real solver vs the stub, at intraday starts."""
import copy, sys, types
from datetime import timedelta
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_advisor_degree as H
from heatpump_optimizer import optimizer as O, price_tiles
from profiles import solve_inputs
real = O._multi_start_minimize
def stub(objective, starts, bounds, maxiter=200, **kw):
    x = np.asarray(starts[0], float)
    return types.SimpleNamespace(x=x, fun=float(objective(x)), success=True, nit=0, status=0, message="stub")
opt, model = H._optimizer()
specs = price_tiles.specs(opt.config, 6.0)
pr = np.concatenate([H._day(k)[0] for k in range(12)])
wx = [np.concatenate([H._day(k)[1][i] for k in range(12)]) for i in range(4)]
for j in (10*96+2, 10*96+30, 11*96+50):
    t = H.START + timedelta(hours=j*0.25); sl = slice(j, j+96)
    st = H._state(21.0, 22.0, float(wx[0][j]))
    kw = dict(prices=pr[sl], outdoor_temps=wx[0][sl], wind_speeds=wx[1][sl], precipitation=wx[2][sl], solar_radiation=wx[3][sl], start_time=t)
    out = []
    for f in (real, stub):
        O._multi_start_minimize = f
        live = opt.optimize(inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
        vals = [price_tiles.per_month(H._shadow(opt, model, ov).optimize(inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw)).baseline_cost - live.baseline_cost, 24.0) for _, ov in specs[:2]]
        out.append(vals)
    print(f"RESULT fidelity {t} real {out[0][0]:+.4f} {out[0][1]:+.4f} stub {out[1][0]:+.4f} {out[1][1]:+.4f} asym {out[0][0]+out[0][1]:+.3f}")
