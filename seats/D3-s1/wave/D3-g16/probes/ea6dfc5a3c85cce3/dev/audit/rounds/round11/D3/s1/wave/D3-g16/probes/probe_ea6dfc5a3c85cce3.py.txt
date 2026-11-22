#!/usr/bin/env python3
# Metric: count of inputs on which DhwPlanner._dhw_raise_fits's verdict, the candidate array after the call, or an exception differ, over every size/slot pair that lands a pass at pos == size.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_ea6dfc5a3c85cce3.py
# EXPECTED RESULT inputs_tried=116 count
# EXPECTED RESULT baseline_refusals=44 count
# EXPECTED RESULT inputs_with_extra_pass=60 count
# EXPECTED RESULT outputs_differing=0 count
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_raise_fits (custom_components/heatpump_optimizer/dhw_planner.py:2133 `while pos < size:`).
# Perturbation: mutant ea6dfc5a3c85cce3, `while pos < size:` -> `while pos <= size:`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: none found: the extra pass at pos == size reads candidate[size] (it exists: n + 1 temperatures), runs an empty step loop and checks empty slices.
# Reach: production weak-slot repair (dhw_planner.py:2091).
# Null control: the grid itself; liveness is both verdicts occurring.
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

OLD = "while pos < size:"
NEW = "while pos <= size:"
MUT = mutant_method("_dhw_raise_fits", OLD, NEW)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

PARAMS = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0)
MODEL = ThermalModel(PARAMS)
PLANNER = DhwPlanner(MODEL, OptimizationConfig(horizon_hours=24, time_step_minutes=60))


def sim(plan, t0=45.0, draws=None):
    """The tank trajectory (n + 1 temperatures) the production step function gives for ``plan``."""
    n = plan.size
    temps = np.empty(n + 1)
    temps[0] = t0
    return MODEL.extend_dhw_temps(temps, 0, plan, np.full(n, 5.0), np.zeros(n) if draws is None else draws, dt_hours=1.0)


def fits(plan, slot, ceiling, base, t0=45.0, fn=None):
    """(verdict, candidate bytes after the call, exception) from DhwPlanner._dhw_raise_fits."""
    n = plan.size
    cand = sim(np.where(np.arange(n) < slot, plan, 0.0), t0)  # the prefix up to slot is already simulated
    try:
        ok = (fn or DhwPlanner._dhw_raise_fits)(PLANNER, cand, base, ceiling, slot, plan, np.full(n, 5.0),
                                                 np.zeros(n), 1.0, None)
        return ok, cand.tobytes(), None
    except Exception as err:
        return None, None, type(err).__name__

# The extra pass at pos == size only happens when (size - slot) is a multiple of the chunk (8): every size and
# slot below, with ceilings that pass, refuse at the first chunk and refuse only at the last step.
tried = moved = extra_pass = refused = 0
for n in (1, 7, 8, 9, 16, 24, 96):
    for slot in sorted({0, 1, n - 8, n - 1, n} & set(range(0, n + 1))):
        for name, plan, ceil_v in (("idle_high_ceiling", np.zeros(n), 90.0), ("flat_out_high", np.full(n, 3.0), 90.0),
                                   ("flat_out_tight", np.full(n, 3.0), 46.0), ("tight_last_step", np.full(n, 0.5), None)):
            ceiling = np.full(n + 1, ceil_v if ceil_v is not None else 90.0)
            if ceil_v is None:
                ceiling[-1] = 40.0
            base = np.full(n + 1, 0.0)
            tried += 1
            extra_pass += int((n - slot) % 8 == 0)
            b, m = fits(plan, slot, ceiling, base), fits(plan, slot, ceiling, base, fn=MUT)
            refused += int(b[0] is False)
            if b != m:
                moved += 1
                print(f"# moved: n={n} slot={slot} {name}: baseline={b[0], b[2]} mutant={m[0], m[2]}")
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT baseline_refusals={refused} count  (liveness: both verdicts occur)")
print(f"RESULT inputs_with_extra_pass={extra_pass} count")
print(f"RESULT outputs_differing={moved} count  (verdict, the candidate array after the call, any exception)")
footer()
