#!/usr/bin/env python3
# Metric: which DHW plan HeatPumpOptimizer._co_optimize returns ("original" or "replanned") when the re-planned
#   candidate scores EXACTLY best_score - 1e-9 (the tie of the adoption rule), baseline vs mutant; plus the same one
#   ulp either side of the tie (where both arms must agree).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_fd57e13959b23a4c.py
# EXPECTED RESULT tie_baseline=original
# EXPECTED RESULT tie_mutant=replanned
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (score one ulp below and above the tie: both arms agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize
#   (line 3997 `            if score < best_score - 1e-9:`), called from _optimize_with_dhw.
# Perturbation: line 3997 `<` -> `<=` (CMP_BOUND fd57e13959b23a4c), in memory. Direction: a candidate scoring exactly
#   1e-9 better is adopted instead of kept out (the docstring's 'adopted only if it scores better').
# Harness: the method's collaborators are stubbed (duty_legs.space_headroom, _dhw_build, the planner's coil forecast,
#   the space re-solve) so the adoption comparison is reached with a controlled score; the comparison itself is the
#   production line, recompiled from source.
# Null control: scores one ulp off the tie.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, resource
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock


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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, SolveInputs, ForecastSeries, SolveLimits)
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_P0, _T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """HeatPumpOptimizer.<name> recompiled from its own source with the one line swapped."""
    raw = inspect.getattr_static(HeatPumpOptimizer, name)
    fn = raw.__func__ if isinstance(raw, staticmethod) else raw
    src = textwrap.dedent(inspect.getsource(fn))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = {}
    # globals = the live module dict, so a collaborator patched on the module is seen by both arms alike
    exec(compile(src.replace(old, new, 1), optimizer.__file__, "exec"), optimizer.__dict__, ns)
    out = ns[name]
    if isinstance(raw, staticmethod) and not isinstance(out, staticmethod):
        out = staticmethod(out)
    return out


def mutated(name, old, new):
    """Context manager: the class attribute swapped to the mutant for the block."""
    return mock.patch.object(HeatPumpOptimizer, name, mutant_method(name, old, new))


def outcome(fn, *a, **k):
    try:
        r = fn(*a, **k)
    except Exception as exc:  # the mutant's failure is the number
        return f"raise:{type(exc).__name__}"
    if r is None:
        return "None"
    if isinstance(r, np.ndarray):
        return "array:" + ",".join(f"{v:g}" for v in r.tolist())
    return repr(r)


def footer():
    p, t = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
from types import SimpleNamespace  # noqa: E402
NAME = "_co_optimize"
OLD, NEW = "if score < best_score - 1e-9:", "if score <= best_score - 1e-9:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
    horizon_hours=4, time_step_minutes=60))
P_MAX = 5.0
space = np.array([5.0, 5.0, 1.0, 1.0])
dhw = np.array([1.0, 0.0, 0.0, 0.0])        # step 0 has DHW and space hard at the headroom -> pinned
replanned = np.array([0.0, 1.0, 0.0, 0.0])
planner = SimpleNamespace(_dhw_coil_wood_forecast=lambda *a: None)
BEST = 12.345678


def run(score):
    cand_space = np.array([4.0, 4.0, 1.0, 1.0])
    with mock.patch.object(optimizer.duty_legs, "space_headroom", lambda *a: np.full(4, 5.0)), \
            mock.patch.object(optimizer, "_dhw_build", lambda *a, **k: (SimpleNamespace(schedule=replanned), None)):
        out = HeatPumpOptimizer._co_optimize(
            opt, None, space_power=space, dhw_power=dhw, status="ok", best_score=BEST,
            solve_space=lambda r, s: (cand_space, "cand", score), p_max=P_MAX, planner=planner)
    return "replanned" if np.array_equal(out[1], replanned) else "original"


tie = BEST - 1e-9
below, above = np.nextafter(tie, -np.inf), np.nextafter(tie, np.inf)
b = (run(tie), run(below), run(above))
with mutated(NAME, OLD, NEW):
    m = (run(tie), run(below), run(above))
print(f"RESULT tie_baseline={b[0]}")
print(f"RESULT tie_mutant={m[0]}")
print(f"RESULT moved={int(b[0] != m[0])} count")
print(f"RESULT null_delta={int(b[1:] != m[1:])} count")
print(f"RESULT below_tie={b[1]}|{m[1]}")
print(f"RESULT above_tie={b[2]}|{m[2]}")
footer()
