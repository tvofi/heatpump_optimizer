#!/usr/bin/env python3
# Metric: over 600 seeded direct calls of DhwPlanner._plan_dhw_min_cost (random tank size, horizon, step, prices,
#   outdoor temps, requirement, start temperature, draws), the count whose returned DHW plan differs under the
#   mutant, the largest per-step difference (kW), and the count of calls whose first LP pass is already
#   COP-consistent (the only calls the guard decides).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_64576dd552491452.py
# EXPECTED RESULT calls=600 count
# EXPECTED RESULT first_pass_converged=17 count
# EXPECTED RESULT differing_plans=16 count
# EXPECTED RESULT max_step_delta_kw=1.740 kW  (3 decimals: solver floats)
# EXPECTED RESULT null_differing=0 count             (calls whose first pass did not converge: the edit is inert)
# EXPECTED RESULT golden_first_pass_converged=0 count (three golden DHW scenarios: production never exits early)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost, line 1627
#   `if np.allclose(refined, cop, rtol=0.02):` (the COP-refinement early exit), reached from
#   DhwPlanner._build_dhw_requirements (1235).
# Perturbation: mutant 64576dd552491452, the guard -> `if False:`, applied in memory (the method is recompiled from
#   its own source for the mutant arm). Direction: when the first pass is already COP-consistent the mutant solves
#   a second program at the refined COP; on a degenerate (flat or tied) price vector that moves energy between
#   steps, so the plan's timing changes while its kWh barely does.
# Null control: the calls whose first pass did not converge (both arms run the same two passes).
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

logging.disable(logging.CRITICAL)
from heatpump_optimizer import dhw_planner  # noqa: E402
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

GUARD = "if np.allclose(refined, cop, rtol=0.02):"
BREAK = GUARD + "\n            break"
SRC = textwrap.dedent(inspect.getsource(DhwPlanner._plan_dhw_min_cost))
assert SRC.count(BREAK) == 1, "anchor line moved"
NS = dict(dhw_planner.__dict__)
exec(compile(SRC.replace(GUARD, "if False:", 1), dhw_planner.__file__, "exec"), NS)
MUT = NS["_plan_dhw_min_cost"]
# A recorder with the baseline's behaviour: it notes on which pass the early exit fires.
REC = dict(dhw_planner.__dict__, HITS=[])
exec(compile(SRC.replace(BREAK, GUARD + "\n            HITS.append(_)\n            break", 1),
             dhw_planner.__file__, "exec"), REC)
BASE = REC["_plan_dhw_min_cost"]


def same(a, b):
    return (a is None and b is None) or (a is not None and b is not None and np.array_equal(a, b))


rng = np.random.default_rng(4)
calls = conv = diff = null = 0
max_d = 0.0
for _ in range(600):
    vol = float(rng.choice([80.0, 150.0, 200.0, 300.0]))
    params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=vol, dhw_cooling_rate=float(rng.choice([0.1, 0.3, 1.0])))
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pl = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
    n = int(rng.integers(4, 24))
    dt = float(rng.choice([0.25, 1.0]))
    kind = rng.integers(0, 3)
    prices = np.full(n, 1.0) if kind == 0 else (np.round(rng.uniform(0.5, 2, n), 1) if kind == 1 else rng.uniform(0.1, 4, n))
    out = np.full(n, float(rng.uniform(-15, 20))) + (rng.uniform(-3, 3, n) if rng.random() < 0.5 else 0)
    req = np.full(n, float(rng.uniform(40, 58)))
    it = float(req[0] + rng.uniform(-8, 3))
    draws = rng.uniform(0, 4, n) * (rng.random(n) < 0.3)
    ctx = _DhwPlanContext(
        prices=prices, import_prices=prices, outdoor_temps=out, humidity=None, n_steps=n, dt=dt,
        store=replace(params.dhw_store, capacity_kwh_per_c=vol * 0.00116), p_dhw_max=float(rng.choice([1.5, 3.0, 4.0])),
        min_run_power=0.3, max_lead_steps=24, tank_exo_kw=None)
    kw = dict(initial_temp=it, requirement=req, draw_rates=draws, max_temp=np.full(n, 60.0))
    h0 = len(REC["HITS"])
    b = BASE(pl, ctx, **kw)
    first = 0 in REC["HITS"][h0:]
    m = MUT(pl, ctx, **kw)
    calls += 1
    conv += first
    if not same(b, m):
        if first:
            diff += 1
            if b is not None and m is not None:
                max_d = max(max_d, float(np.abs(b - m).max()))
        else:
            null += 1

# Production reach: does the first pass ever converge over three golden DHW scenarios?
import golden  # noqa: E402

GH = dict(dhw_planner.__dict__, HITS=[])
exec(compile(SRC.replace(BREAK, GUARD + "\n            HITS.append(_)\n            break", 1),
             dhw_planner.__file__, "exec"), GH)
with mock.patch.object(DhwPlanner, "_plan_dhw_min_cost", GH["_plan_dhw_min_cost"]):
    for name in ("winter_single_dhw", "winter_two_zone_dhw", "summer_dhw_only"):
        golden.capture(name, golden.SCENARIOS[name])
print(f"RESULT calls={calls} count")
print(f"RESULT first_pass_converged={conv} count")
print(f"RESULT differing_plans={diff} count")
print(f"RESULT max_step_delta_kw={max_d:.3f} kW")
print(f"RESULT null_differing={null} count")
print(f"RESULT golden_first_pass_converged={sum(1 for h in GH['HITS'] if h == 0)} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
