#!/usr/bin/env python3
# Metric: count of seeded direct calls of DhwPlanner._repair_dhw_floor whose repaired DHW plan differs under the
#   mutant, (a) inside the production envelope (min_run_power <= p_dhw_max, which _build_dhw_requirements
#   guarantees at dhw_planner.py:1141) and (b) outside it (min_run_power > p_dhw_max); the largest planned step
#   in kW over p_dhw_max in each arm; and how many golden DHW repair calls carry min_run_power > p_dhw_max.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_d7e250feefbd0343.py
# EXPECTED RESULT calls_in_envelope=1500 count
# EXPECTED RESULT differing_in_envelope=0 count        (min(min_run, p_dhw_max) == min_run whenever min_run <= p)
# EXPECTED RESULT calls_outside_envelope=600 count
# EXPECTED RESULT differing_outside_envelope=122 count
# EXPECTED RESULT max_over_cap_kw_mutant=0.000000 kW    (line 1879 still clips every step to p_dhw_max)
# EXPECTED RESULT golden_min_run_above_cap=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.dhw_planner:DhwPlanner._repair_dhw_floor, line 1871
#   `runnable = min(min_run_power, p_dhw_max)`; min_run_power comes from ctx (dhw_planner.py:1141
#   `min_run_power = min(p_dhw_run, ...)` with p_dhw_max = p_dhw_run at 1226).
# Perturbation: mutant d7e250feefbd0343, `min(min_run_power, p_dhw_max)` -> `(min_run_power)`, applied in memory
#   (the method is recompiled from its own source for the mutant arm). Direction: only min_run_power > p_dhw_max
#   moves (a larger runnable block is refused by the room test more often); the published step is still clipped.
# Null control: the production envelope arm, where the clamp is the identity.
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

SRC = textwrap.dedent(inspect.getsource(DhwPlanner._repair_dhw_floor))


def mutant(old, new):
    """_repair_dhw_floor recompiled from its own source with one line edited (in memory)."""
    assert SRC.count(old) == 1, "anchor line moved"
    ns = dict(dhw_planner.__dict__)
    exec(compile(SRC.replace(old, new, 1), dhw_planner.__file__, "exec"), ns)
    return ns["_repair_dhw_floor"]


def case(rng, prod=True):
    """One seeded direct call of the floor repair: tank, horizon, prices, ceiling, requirement, draws and an
    initial plan. prod=True keeps the envelope _build_dhw_requirements guarantees (dhw_planner.py:1138-1141):
    p_dhw_max >= 0.1 and min_run_power <= p_dhw_max."""
    vol = float(rng.choice([80.0, 150.0, 200.0, 300.0]))
    params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=vol, dhw_cooling_rate=float(rng.choice([0.05, 0.1, 0.3, 1.0, 3.0])))  # config range 0.05..3.0 (config_flow.py:1800)
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pl = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
    n = int(rng.integers(4, 16))
    dt = float(rng.choice([0.25, 0.5, 1.0]))
    if prod:
        pmax = float(rng.choice([0.1, 0.3, 1.0, 2.0, 3.0, 4.8]))
        mrp = min(pmax, float(rng.choice([0.15, 0.3, 0.6, 1.2, 2.4])))
    else:
        pmax = float(rng.choice([0.3, 1.0, 2.0]))
        mrp = float(rng.choice([2.5, 4.0]))
    prices = rng.uniform(0, 5, n)
    ctx = _DhwPlanContext(
        prices=prices, import_prices=prices, outdoor_temps=rng.uniform(-15, 15, n), humidity=None, n_steps=n, dt=dt,
        store=replace(params.dhw_store, capacity_kwh_per_c=vol * 0.00116), p_dhw_max=pmax, min_run_power=mrp,
        max_lead_steps=24, tank_exo_kw=None)
    ceil = float(rng.choice([50.0, 55.0, 60.0, 65.0]))
    req = np.full(n, float(rng.uniform(35, ceil + 3)))
    if rng.random() < 0.5:
        req[: int(rng.integers(0, n))] = 0.0
    mt = np.full(n, ceil)
    if rng.random() < 0.3:
        mt[: n // 2] = ceil + 10
    plan = np.where(rng.random(n) < 0.4, rng.uniform(0, pmax, n), 0.0)
    draws = rng.uniform(0, 3, n) * (rng.random(n) < 0.5)
    it = float(rng.uniform(30, ceil + 2))
    fo = (rng.random(n) < 0.2) if rng.random() < 0.3 else None
    sb = np.full(n, float(it - rng.uniform(-5, 10))) if rng.random() < 0.3 else None
    kw = dict(plan=plan, initial_temp=it, draw_rates=draws, requirement=req, max_temp=mt, forced_off=fo, start_below=sb)
    return pl, ctx, kw


def golden_repair_calls(names=("winter_single_dhw", "winter_two_zone_dhw", "summer_dhw_only")):
    """The (planner, ctx, kwargs) of every _repair_dhw_floor call three golden DHW scenarios make."""
    import copy
    import golden
    calls = []
    real = DhwPlanner._repair_dhw_floor

    def spy(self, ctx, **kw):
        calls.append((self, copy.deepcopy(ctx), copy.deepcopy(kw)))
        return real(self, ctx, **kw)

    with mock.patch.object(DhwPlanner, "_repair_dhw_floor", spy):
        for name in names:
            golden.capture(name, golden.SCENARIOS[name])
    return calls
MUT = mutant("runnable = min(min_run_power, p_dhw_max)", "runnable = (min_run_power)")


def arm(seed, n, prod):
    rng = np.random.default_rng(seed)
    diff = 0
    over = 0.0
    for _ in range(n):
        pl, ctx, kw = case(rng, prod=prod)
        b = DhwPlanner._repair_dhw_floor(pl, ctx, **kw)
        m = MUT(pl, ctx, **kw)
        diff += not np.array_equal(b, m)
        over = max(over, float(np.max(m)) - ctx.p_dhw_max if m.size else 0.0)
    return diff, max(over, 0.0)


d_in, _ = arm(2, 1500, True)
d_out, over = arm(3, 600, False)
gcalls = golden_repair_calls()
print("RESULT calls_in_envelope=1500 count")
print(f"RESULT differing_in_envelope={d_in} count")
print("RESULT calls_outside_envelope=600 count")
print(f"RESULT differing_outside_envelope={d_out} count")
print(f"RESULT max_over_cap_kw_mutant={over:.6f} kW")
print(f"RESULT golden_min_run_above_cap={sum(1 for _, c, _ in gcalls if c.min_run_power > c.p_dhw_max)} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
