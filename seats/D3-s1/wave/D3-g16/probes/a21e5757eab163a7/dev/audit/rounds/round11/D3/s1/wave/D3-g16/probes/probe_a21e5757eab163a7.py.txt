#!/usr/bin/env python3
# Metric: DhwPlanner._dhw_raise_fits's verdict (1 fits, 0 refused) when one simulated tank temperature equals its limit + 1e-9 exactly.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_a21e5757eab163a7.py
# EXPECTED RESULT raise_fits_baseline=1
# EXPECTED RESULT raise_fits_mutant=0
# EXPECTED RESULT non_tie_inputs_moved=0 of 4
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_raise_fits (custom_components/heatpump_optimizer/dhw_planner.py:2140 `if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):`).
# Perturbation: mutant a21e5757eab163a7, `if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):` -> `if not bool(np.all(candidate[pos + 1: end + 1] < limit + 1e-9)):`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: verdict down (fits -> refused) on the exact tie only.
# Reach: exact float tie only: a candidate temperature equal to max(ceiling + 0.5, base) + 1e-9 to the last bit.
# Null control: a rounded ceiling, the ceiling at the temperature, 2e-9 and 0.1 below: 0 moved.
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

OLD = "if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):"
NEW = "if not bool(np.all(candidate[pos + 1: end + 1] < limit + 1e-9)):"
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


def tie_ceiling(v):
    """The float c nearest v - 1e-9 with c + 1e-9 == v exactly: the one ceiling where <= and < disagree."""
    c = v - 1e-9
    for _ in range(64):
        s = c + 1e-9
        if s == v:
            return c
        c = np.nextafter(c, np.inf) if s < v else np.nextafter(c, -np.inf)
    return None


n, slot = 12, 0
plan = np.full(n, 3.0)
traj = sim(plan)
k = 5                                    # the step whose simulated temperature sits exactly on its limit + 1e-9
ceiling = np.full(n + 1, 90.0)
c = tie_ceiling(float(traj[k]))
ceiling[k] = c
base = np.zeros(n + 1)
b, m = fits(plan, slot, ceiling, base), fits(plan, slot, ceiling, base, fn=MUT)
print(f"# tie: temps[{k}]={traj[k]!r} ceiling={c!r} ceiling+1e-9={c + 1e-9!r}")
print(f"RESULT raise_fits_baseline={int(bool(b[0]))}")
print(f"RESULT raise_fits_mutant={int(bool(m[0]))}")
inputs = {"ceiling_rounded_64": 64.0, "ceiling_at_temp": float(traj[k]), "ceiling_2e-9_below": float(traj[k]) - 2e-9, "ceiling_0.1_below": float(traj[k]) - 0.1}
moved = []
for name, cv in inputs.items():
    ce = np.full(n + 1, 90.0)
    ce[k] = cv
    if fits(plan, slot, ce, base) != fits(plan, slot, ce, base, fn=MUT):
        moved.append(name)
print(f"RESULT non_tie_inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved) or '-'})")
footer()
