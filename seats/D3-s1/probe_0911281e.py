#!/usr/bin/env python3
# Metric: total DHW electrical energy (kWh, plan.sum()*dt) that DhwPlanner._plan_dhw_min_cost buys on a fixed 12-step
#   horizon whose availability floor (60 C) can only be met by buying in steps priced far above the shortfall slack.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_0911281e.py
# EXPECTED RESULT dhw_kwh_baseline=2.5056 kWh  (spread prices: steps 0-10 at 100000, step 11 at 0; floor 60 C)
# EXPECTED RESULT dhw_kwh_mutant=1.9948 kWh    (penalty 1000*(min|p|+1)=1000 < 100000/cop: slack beats buying)
# EXPECTED RESULT null_delta_kwh=0.0 kWh           (flat price 1.0: min=max, the edit cannot matter)
# EXPECTED RESULT realistic_delta_kwh=0.000000 kWh (price spread 0.1..5.0 per kWh, an ordinary day)
# EXPECTED RESULT min_price_for_separation=8000 per-kWh (smallest swept max price at which mutant != baseline)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (line 1559
#   `            shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)`), reached from DhwPlanner.optimize
#   (dhw_planner.py:1235) as the stage-1 seed.
# Perturbation: np.max -> np.min on that line (GUARD-free value mutant 0911281eca895664), in memory: the method is
#   re-compiled from its own source and attached with mock.patch.object for the mutant arm only.
#   Direction: DHW kWh down (slack is cheaper than buying), only once price/COP > 1000*(min|p|+1).
# Reach: separation needs price/COP above 1000*(min|p|+1), i.e. a per-kWh price of about 8000 with a free step
#   in the horizon; an ordinary 0.1..5.0 per-kWh day does not move (realistic_delta). Reachable only in a
#   unit that prices a kWh in the thousands (e.g. a sub-unit price scale); see UNCERTAINTIES.
# Null control: a flat price vector, where np.max == np.min.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from dataclasses import replace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

OLD = "shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)"
NEW = "shortfall_price = 1000.0 * (float(np.min(np.abs(prices))) + 1.0)"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(DhwPlanner._plan_dhw_min_cost))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(dhw_planner.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), dhw_planner.__file__, "exec"), ns)
    return ns["_plan_dhw_min_cost"]


params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
    horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
planner = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
N = 12
MUT = mutant_fn()


def kwh(prices, method=None):
    ctx = _DhwPlanContext(
        prices=prices, import_prices=prices, outdoor_temps=np.full(N, -5.0), humidity=None, n_steps=N, dt=1.0,
        store=replace(params.dhw_store, capacity_kwh_per_c=0.232), p_dhw_max=3.0, min_run_power=0.1,
        max_lead_steps=24, tank_exo_kw=None)
    fn = method or DhwPlanner._plan_dhw_min_cost
    plan = fn(planner, ctx, 45.0, np.full(N, 60.0), np.zeros(N), np.full(N, 60.0))
    return float("nan") if plan is None else float(plan.sum())


spread = np.array([100000.0] * 11 + [0.0])
flat = np.full(N, 1.0)
real = np.linspace(0.1, 5.0, N)
b, m = kwh(spread), kwh(spread, MUT)
print(f"RESULT dhw_kwh_baseline={b:.4f} kWh")
print(f"RESULT dhw_kwh_mutant={m:.4f} kWh")
print(f"RESULT delta_kwh={m - b:.4f} kWh")
print(f"RESULT null_delta_kwh={abs(kwh(flat, MUT) - kwh(flat)):.6f} kWh")
print(f"RESULT realistic_delta_kwh={abs(kwh(real, MUT) - kwh(real)):.6f} kWh")
sep = None
for hi in (5, 20, 50, 100, 300, 600, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 100000):
    p = np.array([float(hi)] * 11 + [0.0])
    if abs(kwh(p, MUT) - kwh(p)) > 1e-6:
        sep = hi
        break
print(f"RESULT min_price_for_separation={sep} per-kWh")
