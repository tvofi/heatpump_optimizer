#!/usr/bin/env python3
# Metric: the tank temperature at the need step (C) of the plan DhwPlanner._plan_dhw_cheapest_first returns when a manual Off pin covers the whole lead window.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_7da9151a6a79c43e.py
# EXPECTED RESULT dhw_kw_sum_baseline=1.9870 kW
# EXPECTED RESULT dhw_kw_sum_mutant=0.0000 kW
# EXPECTED RESULT tank_at_need_baseline=55.451 C (requirement 55)
# EXPECTED RESULT tank_at_need_mutant=41.891 C
# EXPECTED RESULT null_inputs_moved=0 of 2
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (custom_components/heatpump_optimizer/dhw_planner.py:2234 `if not candidates:\n            candidates = [j for`).
# Perturbation: mutant 7da9151a6a79c43e, `if not candidates:\n            candidates = [j for` -> `if False:\n            candidates = [j for`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: nothing bought: the requirement is marked unreachable instead of being bought before the pin (55.45 C -> 41.89 C).
# Reach: production: forced_off carries manual pins and the quiet Off window.
# Null control: no pin and a pin outside the lead window: 0 moved.
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

OLD = "if not candidates:\n            candidates = [j for"
NEW = "if False:\n            candidates = [j for"
MUT = mutant_method("_plan_dhw_cheapest_first", OLD, NEW)
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

# A manual Off pin covers the whole lead window (steps 8-10): the fallback must buy before it.
fo = np.zeros(N, dtype=bool)
fo[8:11] = True
b = greedy(CHEAP_EARLY, 2, REQ, MAX_T, forced_off=fo)
m = greedy(CHEAP_EARLY, 2, REQ, MAX_T, forced_off=fo, fn=MUT)
print(f"# baseline={np.round(b, 3).tolist()} mutant={np.round(m, 3).tolist()}")
print(f"RESULT dhw_kw_sum_baseline={float(b.sum()):.4f} kW")
print(f"RESULT dhw_kw_sum_mutant={float(m.sum()):.4f} kW")
tb = PLANNER._dhw_plan_temps(b, 45.0, np.full(N, -5.0), np.zeros(N), 1.0, None, None)
tm = PLANNER._dhw_plan_temps(m, 45.0, np.full(N, -5.0), np.zeros(N), 1.0, None, None)
print(f"RESULT tank_at_need_baseline={float(tb[11]):.3f} C  (requirement 55)")
print(f"RESULT tank_at_need_mutant={float(tm[11]):.3f} C")
nulls = {"no_pin": None, "pin_outside_lead_window": np.arange(N) < 3}
moved = [k for k, f in nulls.items() if not np.array_equal(greedy(CHEAP_EARLY, 2, REQ, MAX_T, forced_off=f), greedy(CHEAP_EARLY, 2, REQ, MAX_T, forced_off=f, fn=MUT))]
print(f"RESULT null_inputs_moved={len(moved)} of {len(nulls)} ({','.join(moved) or '-'})")
footer()
