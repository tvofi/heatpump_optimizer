#!/usr/bin/env python3
# Metric: count of inputs on which DhwPlanner._dhw_legionella_due's (due, hour, step, ready_temps) differ between the baseline and the mutant, over an 864-input grid of the elastic branch.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_01acd6cc2431d71d.py
# EXPECTED RESULT inputs_tried=864 count
# EXPECTED RESULT outputs_differing=0 count
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due (custom_components/heatpump_optimizer/dhw_planner.py:692 `known_mask[: min(reach_step, n_steps)] = False`).
# Perturbation: mutant 01acd6cc2431d71d, `known_mask[: min(reach_step, n_steps)] = False` -> `known_mask[: (reach_step)] = False`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: none found: reach_step is int(hot[0]) < n_steps or n_steps itself, so min(reach_step, n_steps) == reach_step, and numpy slicing clamps besides.
# Reach: production elastic-legionella branch.
# Null control: the grid itself: equal outputs on every input; liveness is baseline_cycles_placed > 0.
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

OLD = "known_mask[: min(reach_step, n_steps)] = False"
NEW = "known_mask[: (reach_step)] = False"
MUT = mutant_method("_dhw_legionella_due", OLD, NEW)
from types import SimpleNamespace  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

N = 24


def legionella(known, prices, *, tank=55.0, p_run=3.0, volume=200.0, ceiling=1.0, off=None, fn=None):
    """(due, hour, step, ready_temps) from DhwPlanner._dhw_legionella_due inside the elastic window (130 h since
    the last cycle: past the 5-day minimum, before the 7-day deadline, so the hard-deadline branch is not taken)."""
    p = ThermalParameters(dhw_enabled=True, dhw_legionella_enabled=True, dhw_elastic_legionella_enabled=True,
                          dhw_legionella_price_ceiling=ceiling, dhw_tank_volume=volume)
    planner = DhwPlanner(ThermalModel(p), OptimizationConfig(horizon_hours=N, time_step_minutes=60), None, known)
    h = SimpleNamespace(initial_state=ThermalState(dhw_temperature=tank, dhw_hours_since_legionella=130.0),
                        n_steps=N, dt=1.0, outdoor_temps=np.full(N, 5.0), humidity=None)
    ready = np.zeros(N)
    due, hour, step = (fn or DhwPlanner._dhw_legionella_due)(
        planner, h, params=p, hours_mod=np.arange(N, dtype=float), draw_rates=np.zeros(N),
        ready_temps=ready, p_dhw_run=p_run, dhw_prices=np.asarray(prices, dtype=float), off_steps=off)
    return due, hour, step, ready.tobytes()

# Every input that reaches line 692: tank temperatures from cold (reach_step == n_steps, the clamp's only
# candidate case) to hot (reach_step 0), small and big tanks, small and big pumps, partial/None/full known masks,
# cheap steps early, late and at the last step, an Off window, and ceilings that pass and refuse.
grid = []
for tank in (10.0, 30.0, 45.0, 55.0, 59.9, 65.0):
    for volume, p_run in ((200.0, 3.0), (3000.0, 0.5), (50.0, 6.0)):
        for known_name, known in (("None", None), ("all", np.ones(N, dtype=bool)),
                                  ("first12", np.array([True] * 12 + [False] * 12)), ("short5", np.ones(5, dtype=bool))):
            for cheap in (0, 11, 23):
                for ceiling in (1.0, 1e-6):
                    for off_name in ("none", "steps0-3"):
                        off = None if off_name == "none" else np.array([True] * 4 + [False] * (N - 4))
                        grid.append((tank, volume, p_run, known_name, known, cheap, ceiling, off_name, off))
moved, placed, reach_end = [], 0, 0
for tank, volume, p_run, kn, known, cheap, ceiling, on, off in grid:
    prices = np.full(N, 2.0)
    prices[cheap] = 0.1
    b = legionella(known, prices, tank=tank, p_run=p_run, volume=volume, ceiling=ceiling, off=off)
    m = legionella(known, prices, tank=tank, p_run=p_run, volume=volume, ceiling=ceiling, off=off, fn=MUT)
    placed += int(b[0])
    if b != m:
        moved.append((tank, volume, p_run, kn, cheap, ceiling, on))
print(f"RESULT inputs_tried={len(grid)} count")
print(f"RESULT baseline_cycles_placed={placed} count")
print(f"RESULT outputs_differing={len(moved)} count")
print(f"# differing inputs: {moved[:5]}")
footer()
