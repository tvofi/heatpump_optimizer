#!/usr/bin/env python3
# Metric: the first step DhwPlanner._plan_dhw_cheapest_first charges at on a 12 h horizon, need at step 10, max_lead_steps 2, cheapest price at step 0.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_84eb14f49ff66736.py
# EXPECTED RESULT first_charge_step_baseline=10
# EXPECTED RESULT first_charge_step_mutant=0
# EXPECTED RESULT charge_steps_outside_lead_window_mutant=1 count
# EXPECTED RESULT null_inputs_moved=0 of 3
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (custom_components/heatpump_optimizer/dhw_planner.py:2232 `j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j)`).
# Perturbation: mutant 84eb14f49ff66736, `j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j)` -> `j for j in range((0), k + 1) if usable(j)`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: charge moves earlier than the configured lead limit allows (step 10 -> step 0).
# Reach: production: ctx.max_lead_steps is ceil(ThermalModel.dhw_hold_hours() / dt) (dhw_planner.py:1173, 1214), the hours the tank holds heat, under the horizon whenever the tank's standby loss is material.
# Null control: a lead covering the horizon, flat prices, the cheapest step inside the lead window: 0 moved.
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

OLD = "j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j)"
NEW = "j for j in range((0), k + 1) if usable(j)"
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

b = greedy(CHEAP_EARLY, 2, REQ, MAX_T)
m = greedy(CHEAP_EARLY, 2, REQ, MAX_T, fn=MUT)
print(f"# max_lead_steps=2: baseline={np.round(b, 3).tolist()} mutant={np.round(m, 3).tolist()}")
print(f"RESULT first_charge_step_baseline={int(np.flatnonzero(b)[0])}")
print(f"RESULT first_charge_step_mutant={int(np.flatnonzero(m)[0])}")
print(f"RESULT charge_steps_outside_lead_window_mutant={int(np.count_nonzero(m[: 10 - 2]))} count")
nulls = {"lead_24_covers_horizon": (CHEAP_EARLY, 24), "flat_prices_lead_2": (np.ones(N), 2),
         "cheapest_inside_lead_window": (np.where(np.arange(N) == 9, 0.1, 5.0), 2)}
moved = [k for k, (pr, lead) in nulls.items() if not np.array_equal(greedy(pr, lead, REQ, MAX_T), greedy(pr, lead, REQ, MAX_T, fn=MUT))]
print(f"RESULT null_inputs_moved={len(moved)} of {len(nulls)} ({','.join(moved) or '-'})")
footer()
