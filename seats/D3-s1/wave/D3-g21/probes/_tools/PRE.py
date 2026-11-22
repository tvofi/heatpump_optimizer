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
