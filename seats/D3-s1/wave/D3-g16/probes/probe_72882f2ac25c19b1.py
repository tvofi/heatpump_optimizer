#!/usr/bin/env python3
# Metric: the DHW planning price of a step where the space-heating profile draws more than the PV surplus (per-kWh), and the cheapest step's index.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_72882f2ac25c19b1.py
# EXPECTED RESULT step0_price_baseline=2.000000
# EXPECTED RESULT step0_price_mutant=3.333333
# EXPECTED RESULT cheapest_step_baseline=0
# EXPECTED RESULT cheapest_step_mutant=1
# EXPECTED RESULT null_inputs_moved=0 of 4
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_planning_prices (custom_components/heatpump_optimizer/dhw_planner.py:474 `surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None)`).
# Perturbation: mutant 72882f2ac25c19b1, `surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None)` -> `surplus = (surplus - space_demand[: len(prices)])`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: price up: a negative surplus inflates the import price by margin * deficit / p_run, and the ranking flips.
# Reach: production: the co-optimization replan passes the space profile (optimizer.py:2065 and 3986 -> DhwPlanner._build_dhw_requirements -> dhw_planner.py:1147); space demand above the PV surplus is the ordinary case on a cold sunny morning.
# Null control: space demand below, equal to, absent and zero: 0 moved.
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

OLD = "surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None)"
NEW = "surplus = (surplus - space_demand[: len(prices)])"
MUT = mutant_method("_dhw_planning_prices", OLD, NEW)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

CFG = OptimizationConfig(horizon_hours=4, time_step_minutes=60)  # pv_export_price default 0.0
MODEL = ThermalModel(ThermalParameters(dhw_enabled=True))


def planning_prices(prices, surplus, space_demand=None, p_run=3.0, fn=None):
    """DhwPlanner._dhw_planning_prices: the per-step prices the DHW planners rank steps by."""
    planner = DhwPlanner(MODEL, CFG, None if surplus is None else np.asarray(surplus, dtype=float), None)
    return (fn or DhwPlanner._dhw_planning_prices)(planner, np.asarray(prices, dtype=float), p_run, space_demand)

# Co-optimization replan: 1 kW of PV surplus at step 0, but the space-heating profile already takes 3 kW there.
prices = [2.0, 2.5, 3.0, 3.5]
surplus = [1.0, 0.0, 0.0, 0.0]
space = np.array([3.0, 0.0, 0.0, 0.0])
b = planning_prices(prices, surplus, space)
m = planning_prices(prices, surplus, space, fn=MUT)
print(f"# baseline={np.round(b, 4).tolist()} mutant={np.round(m, 4).tolist()}")
print(f"RESULT step0_price_baseline={b[0]:.6f} per-kWh")
print(f"RESULT step0_price_mutant={m[0]:.6f} per-kWh")
print(f"RESULT cheapest_step_baseline={int(np.argmin(b))}")
print(f"RESULT cheapest_step_mutant={int(np.argmin(m))}")
inputs = {"space_below_surplus": np.array([0.5, 0, 0, 0]), "space_equals_surplus": np.array([1.0, 0, 0, 0]),
          "no_space_profile": None, "space_zero": np.zeros(4)}
moved = []
for name, sd in inputs.items():
    bb, mm = planning_prices(prices, surplus, sd), planning_prices(prices, surplus, sd, fn=MUT)
    if not np.array_equal(bb, mm):
        moved.append(name)
print(f"RESULT null_inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved) or '-'})")
footer()
