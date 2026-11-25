#!/usr/bin/env python3
# Metric: whether DhwPlanner._plan_dhw_min_cost returns a different plan (None = "fall back to the greedy planner"
#   versus a kW vector) under the mutant, per solver outcome; and how often line 1613 is reached at all.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2580fdeb3923a03e.py
# EXPECTED RESULT reached_ok_solve=0 count               (a solvable 12-step program never enters the branch)
# EXPECTED RESULT real_failure_statuses_tried=3 count     (infeasible 2, unbounded 3, iteration limit 1, from scipy)
# EXPECTED RESULT real_failures_returning_x=0 count       (installed scipy: every failure carries x=None)
# EXPECTED RESULT differing_real_failures=0 count         (x=None: the mutant falls to `if solution is None: return best`)
# EXPECTED RESULT differing_failure_with_vector=1 count   (a failure that carries a vector: mutant publishes it)
# EXPECTED RESULT golden_dhw_lp_failures=0 count          (spy on linprog over three golden DHW scenarios)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost, line 1613 `return best`
#   (the `if not result.success:` branch), reached from DhwPlanner._build_dhw_requirements (1235).
# Perturbation: mutant 2580fdeb3923a03e, `return best` -> `pass`, applied in memory (the method is recompiled from
#   its own source and passed explicitly for the mutant arm). The solver outcome is the input: dhw_planner.linprog
#   is replaced, for both arms alike, by a stub that returns a real scipy failure result (from three genuinely
#   failing programs) or the real result of this program with success forced False and x kept.
# Reach: the full-net trace found no baseline executing line 1613; this probe counts solver failures over three
#   golden DHW scenarios (golden.capture) as the production reach number.
# Null control: the real solver on a solvable program (both arms return the same plan; branch not reached).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import inspect  # noqa: E402
import logging  # noqa: E402
import textwrap  # noqa: E402
from dataclasses import replace  # noqa: E402
from unittest import mock  # noqa: E402

import numpy as np  # noqa: E402
from scipy.optimize import linprog as real_linprog  # noqa: E402

logging.disable(logging.CRITICAL)
from heatpump_optimizer import dhw_planner  # noqa: E402
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

OLD = "            return best\n\n        solution = result.x"
SRC = textwrap.dedent(inspect.getsource(DhwPlanner._plan_dhw_min_cost))
assert SRC.count(OLD) == 1, "anchor line moved"
NS = dict(dhw_planner.__dict__)
exec(compile(SRC.replace(OLD, "            pass\n\n        solution = result.x", 1), dhw_planner.__file__, "exec"), NS)
MUT = NS["_plan_dhw_min_cost"]

params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
    horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
planner = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
N = 12
PRICES = np.linspace(0.5, 3.0, N)


def plan(fn, stub=None):
    ctx = _DhwPlanContext(
        prices=PRICES, import_prices=PRICES, outdoor_temps=np.full(N, -5.0), humidity=None, n_steps=N, dt=1.0,
        store=replace(params.dhw_store, capacity_kwh_per_c=0.232), p_dhw_max=3.0, min_run_power=0.1,
        max_lead_steps=24, tank_exo_kw=None)
    # Both arms see the stub: the module's global and the recompiled mutant's own globals (NS).
    patch = mock.patch.object(dhw_planner, "linprog", stub) if stub else mock.MagicMock()
    patch_ns = mock.patch.dict(NS, {"linprog": stub}) if stub else mock.MagicMock()
    with patch, patch_ns:
        return fn(planner, ctx, initial_temp=45.0, requirement=np.full(N, 55.0), draw_rates=np.zeros(N),
                  max_temp=np.full(N, 60.0))


def same(a, b):
    return (a is None and b is None) or (a is not None and b is not None and np.array_equal(a, b))


reached = []


def spy(*a, **k):
    r = real_linprog(*a, **k)
    if not r.success:
        reached.append(r.status)
    return r


base_ok = plan(DhwPlanner._plan_dhw_min_cost, spy)
mut_ok = plan(MUT, spy)
reached_ok = len(reached)
# Three genuinely failing programs, solved by the installed scipy.
FAIL = [
    real_linprog([1, 1], A_ub=[[1, 0], [-1, 0]], b_ub=[-1, -1], bounds=[(0, None)] * 2, method="highs"),
    real_linprog([-1, 1], bounds=[(0, None)] * 2, method="highs"),
    real_linprog(-np.ones(20), A_ub=np.random.default_rng(0).random((30, 20)), b_ub=np.full(30, 1.5),
                 bounds=[(0, None)] * 20, method="highs", options={"maxiter": 1}),
]
with_x = sum(1 for r in FAIL if r.x is not None)
diff_real = 0
for r in FAIL:
    assert not r.success
    stub = lambda *a, _r=r, **k: _r  # noqa: E731
    diff_real += not same(plan(DhwPlanner._plan_dhw_min_cost, stub), plan(MUT, stub))


def failing_with_vector(*a, **k):
    r = real_linprog(*a, **k)
    r.success, r.status, r.message = False, 4, "numerical difficulties (stub)"
    return r


diff_vec = int(not same(plan(DhwPlanner._plan_dhw_min_cost, failing_with_vector), plan(MUT, failing_with_vector)))

# Production reach: linprog failures over three golden DHW scenarios.
import golden  # noqa: E402

golden_failures = []


def gspy(*a, **k):
    r = real_linprog(*a, **k)
    if not r.success:
        golden_failures.append(r.status)
    return r


with mock.patch.object(dhw_planner, "linprog", gspy):  # production code only; the mutant is not used here
    for name in ("winter_single_dhw", "winter_two_zone_dhw", "summer_dhw_only"):
        golden.capture(name, golden.SCENARIOS[name])
assert same(base_ok, mut_ok)
print(f"RESULT reached_ok_solve={reached_ok} count")
print(f"RESULT real_failure_statuses_tried={len(FAIL)} count")
print(f"RESULT real_failures_returning_x={with_x} count")
print(f"RESULT differing_real_failures={diff_real} count")
print(f"RESULT differing_failure_with_vector={diff_vec} count")
print(f"RESULT golden_dhw_lp_failures={len(golden_failures)} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
