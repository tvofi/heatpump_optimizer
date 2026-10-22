"""Reviewer-built null (not the finder's): flat-price solve, fused vs scalar-valued runs."""
import sys, os, hashlib
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from datetime import datetime
from unittest import mock
import numpy as np
from profiles import house, prices, weather, solve_inputs
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

def scalar_valued(objective, fused, x0, bounds, args, maxiter):
    return om._scoped_minimize(objective, x0, args=args, method="L-BFGS-B", bounds=bounds,
        jac=lambda x, *a: fused(x, *a)[1], options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4})

def solve(pp, wx, two_zone, run=None):
    cfg = house(two_zone=two_zone, dhw=False); p = ThermalParameters.from_config(cfg); p.dhw_enabled = False
    opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"],
        clamp_planned_levels=True))
    t0 = datetime(2026, 1, 15)
    out, wind, rain, sun = weather(wx, t0)
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        slab_temperature=22.0, outdoor_temperature=float(out[0]))
    kinds = {}
    real = om._scoped_minimize
    def sm(fun, x0, *a, **kw):
        k = "continuation" if opt._floor_l1_scale != 1.0 else "relaxed" if opt._levels_relaxed else "multi-start"
        kinds[k] = kinds.get(k, 0) + 1
        return real(fun, x0, *a, **kw)
    ctx = [mock.patch.object(om, "_scoped_minimize", sm)]
    if run: ctx.append(mock.patch.object(om, "_lbfgsb_run", run))
    for c in ctx: c.__enter__()
    try:
        r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=prices(pp, t0), outdoor_temps=out,
            wind_speeds=wind, precipitation=rain, solar_radiation=sun, start_time=t0))
    finally:
        for c in reversed(ctx): c.__exit__(None, None, None)
    P = np.asarray(r.power_schedule, float)
    return P, float(getattr(r, "total_cost", float("nan"))), kinds

for pp, wx, tz in [("flat", "winter_cold", True), ("flat", "winter_mild", True), ("flat", "winter_cold", False), ("winter_typical", "winter_cold", True)]:
    a, ca, ka = solve(pp, wx, tz)
    b, cb, kb = solve(pp, wx, tz, scalar_valued)
    print(f"RESULT null prices={pp} weather={wx} two_zone={tz} identical={np.array_equal(a,b)} "
          f"max_dP={float(np.max(np.abs(a-b))):.3e} cost_fused={ca:.6f} cost_scalar_valued={cb:.6f} "
          f"sha={hashlib.sha1(a.tobytes()).hexdigest()[:12]}/{hashlib.sha1(b.tobytes()).hexdigest()[:12]} runs={ka}")
