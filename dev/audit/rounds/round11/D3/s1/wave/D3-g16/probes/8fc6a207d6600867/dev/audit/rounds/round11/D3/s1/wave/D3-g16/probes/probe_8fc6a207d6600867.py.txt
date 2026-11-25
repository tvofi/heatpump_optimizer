#!/usr/bin/env python3
# Metric: the DHW planning price of a step whose PV surplus is exactly 1e-6 kW, the largest anywhere (per-kWh).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_8fc6a207d6600867.py
# EXPECTED RESULT step0_price_baseline=2.000000000
# EXPECTED RESULT step0_price_mutant=1.999999333
# EXPECTED RESULT max_abs_delta=6.667e-07
# EXPECTED RESULT rank_changed=0
# EXPECTED RESULT inputs_moved=1 of 6 (the exact-tie input only)
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_planning_prices (custom_components/heatpump_optimizer/dhw_planner.py:470 `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):`).
# Perturbation: mutant 8fc6a207d6600867, `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):` -> `if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: price down by surplus/p_run * margin, only when the largest surplus is exactly 1e-6.
# Reach: exact float tie only: a forecast surplus equal to 1e-6 kW at its maximum; any other surplus gives identical prices.
# Null control: no surplus, zero surplus, 2e-6, 1 kW and nextafter(1e-6, 0): 0 moved.
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

OLD = "if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):"
NEW = "if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):"
MUT = mutant_method("_dhw_planning_prices", OLD, NEW)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

CFG = OptimizationConfig(horizon_hours=4, time_step_minutes=60)  # pv_export_price default 0.0
MODEL = ThermalModel(ThermalParameters(dhw_enabled=True))


def planning_prices(prices, surplus, space_demand=None, p_run=3.0, fn=None):
    """DhwPlanner._dhw_planning_prices: the per-step prices the DHW planners rank steps by."""
    planner = DhwPlanner(MODEL, CFG, None if surplus is None else np.asarray(surplus, dtype=float), None)
    return (fn or DhwPlanner._dhw_planning_prices)(planner, np.asarray(prices, dtype=float), p_run, space_demand)

prices = [2.0, 1.0, 1.5, 0.5]
b = planning_prices(prices, [1e-6, 0.0, 0.0, 0.0])
m = planning_prices(prices, [1e-6, 0.0, 0.0, 0.0], fn=MUT)
print(f"RESULT step0_price_baseline={b[0]:.9f} per-kWh")
print(f"RESULT step0_price_mutant={m[0]:.9f} per-kWh")
print(f"RESULT max_abs_delta={float(np.max(np.abs(m - b))):.3e} per-kWh")
print(f"RESULT rank_changed={int(not np.array_equal(np.argsort(b, kind='stable'), np.argsort(m, kind='stable')))}")
inputs = {"no_surplus_None": None, "zero_surplus": [0.0] * 4, "surplus_2e-6": [2e-6, 0, 0, 0],
          "surplus_1kW": [1.0, 0, 0, 0], "surplus_just_below_1e-6": [np.nextafter(1e-6, 0), 0, 0, 0],
          "all_steps_1e-6": [1e-6] * 4}
moved = []
for name, s in inputs.items():
    bb, mm = planning_prices(prices, s), planning_prices(prices, s, fn=MUT)
    print(f"# input {name}: max|delta|={float(np.max(np.abs(mm - bb))):.3e}")
    if not np.array_equal(bb, mm):
        moved.append(name)
print(f"RESULT inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved) or '-'})")
footer()
