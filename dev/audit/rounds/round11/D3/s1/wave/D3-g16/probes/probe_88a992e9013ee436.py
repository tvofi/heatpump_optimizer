#!/usr/bin/env python3
# Metric: count of inputs on which the plan DhwPlanner._plan_dhw_cheapest_first returns differs, over 21 inputs that include every way to leave no usable step.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_88a992e9013ee436.py
# EXPECTED RESULT inputs_tried=21 count
# EXPECTED RESULT baseline_plans_with_nothing_bought=6 count
# EXPECTED RESULT outputs_differing=0 count
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (custom_components/heatpump_optimizer/dhw_planner.py:2236 `if not candidates:  (the second, line 2236)`).
# Perturbation: mutant 88a992e9013ee436, `if not candidates:  (the second, line 2236)` -> `if False:`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: none found: with no candidates the fall-through sorts an empty list, buys nothing, and the `added <= 1e-9` branch adds k to unreachable exactly as the guard's `continue` does.
# Reach: production.
# Null control: the grid itself; liveness is the no-candidate path being reached.
# Count key: the value the production method returns (never an input attribute).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
_T0 = (time.process_time(), time.thread_time())
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner  # noqa: E402


def mutant_method(name, old, new):
    """DhwPlanner.<name> re-compiled from its own source with the one mutated line, in memory."""
    src = textwrap.dedent(inspect.getsource(getattr(DhwPlanner, name)))
    assert src.count(old) == 1, f"anchor line moved: {old!r}"
    ns = dict(dhw_planner.__dict__)
    exec(compile(src.replace(old, new, 1), dhw_planner.__file__, "exec"), ns)
    return ns[name]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            sw = next((l.split()[1] for l in f if l.startswith("pswpin ")), "0")
    except OSError:
        sw = "0"
    print(f"RESULT swapins={sw}")

OLD = "if not candidates:"
NEW = "if False:"
# The SECOND `if not candidates:` (line 2236): mutant_method replaces the first, so this probe splices by position.
_src = textwrap.dedent(inspect.getsource(DhwPlanner._plan_dhw_cheapest_first))
_first = _src.index(OLD)
_second = _src.index(OLD, _first + len(OLD))
assert _src.count(OLD) == 2
_ns = dict(dhw_planner.__dict__)
exec(compile(_src[:_second] + NEW + _src[_second + len(OLD):], dhw_planner.__file__, "exec"), _ns)
MUT = _ns["_plan_dhw_cheapest_first"]
from dataclasses import replace  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import _DhwPlanContext  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

PARAMS = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
PLANNER = DhwPlanner(ThermalModel(PARAMS), OptimizationConfig(horizon_hours=12, time_step_minutes=60), None, None)


def ctx(prices, lead, n, c_dhw=0.232):
    prices = np.asarray(prices, dtype=float)
    return _DhwPlanContext(prices=prices, import_prices=prices, outdoor_temps=np.full(n, -5.0), humidity=None,
                           n_steps=n, dt=1.0, store=replace(PARAMS.dhw_store, capacity_kwh_per_c=c_dhw),
                           p_dhw_max=3.0, min_run_power=0.1, max_lead_steps=lead, tank_exo_kw=None)


def greedy(prices, lead, req, max_temp, t0=45.0, draws=None, forced_off=None, c_dhw=0.232, fn=None):
    """The plan DhwPlanner._plan_dhw_cheapest_first returns (kW per step)."""
    n = len(prices)
    return (fn or DhwPlanner._plan_dhw_cheapest_first)(
        PLANNER, ctx(prices, lead, n, c_dhw), t0, np.asarray(req, dtype=float).copy(),
        np.zeros(n) if draws is None else np.asarray(draws, dtype=float), np.asarray(max_temp, dtype=float).copy(),
        forced_off=forced_off)


N = 12
CHEAP_EARLY = np.array([0.1] + [5.0] * 11)        # the cheapest hour is 10 h before the need
REQ = np.zeros(N)
REQ[10] = 55.0                                    # hot water needed at 10:00
MAX_T = np.full(N, 65.0)

# Inputs that leave NO usable step at all (the only way to reach line 2236): every step pinned off, a ceiling
# under the tank, every step already at full power, a requirement over the ceiling; plus ordinary inputs.
grid = {
    "all_forced_off": dict(forced_off=np.ones(N, dtype=bool)),
    "ceiling_below_tank": dict(max_temp=np.full(N, 40.0)),
    "ceiling_at_tank_plus_0.05": dict(max_temp=np.full(N, 46.05)),
    "lead_window_pinned": dict(forced_off=np.arange(N) >= 8),
    "two_requirements": dict(req=np.where((np.arange(N) == 4) | (np.arange(N) == 10), 55.0, 0.0)),
    "big_draws": dict(draws=np.full(N, 2.0)),
    "ordinary": dict(),
}
moved, unmet = [], 0
for name, kw in grid.items():
    args = dict(req=REQ, max_temp=MAX_T)
    args.update(kw)
    req, mt = args.pop("req"), args.pop("max_temp")
    for lead in (0, 2, 24):
        b = greedy(CHEAP_EARLY, lead, req, mt, **args)
        m = greedy(CHEAP_EARLY, lead, req, mt, fn=MUT, **args)
        unmet += int(not b.any())
        if not np.array_equal(b, m):
            moved.append(f"{name}/lead{lead}")
print(f"RESULT inputs_tried={len(grid) * 3} count")
print(f"RESULT baseline_plans_with_nothing_bought={unmet} count  (the no-candidate path is reached)")
print(f"RESULT outputs_differing={len(moved)} count ({','.join(moved) or '-'})")
footer()
