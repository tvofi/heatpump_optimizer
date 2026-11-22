"""Shared plumbing for box D3-g20's step-4 probes (not a probe itself).

Applies one key's one-line mutant to a HeatPumpOptimizer method IN MEMORY: the method's
own source is re-compiled with the line swapped and patched onto the class for the
mutant arm only; the file on disk is never touched. Builds a default optimizer the
way tests/optimality.py:setup does (ThermalParameters.from_config, 24 h, 15 min).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, inspect, resource, sys, textwrap, time
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
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
from custom_components.heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402

_T0 = (time.process_time(), time.thread_time())


def build(cfg=None, **params):
    p = ThermalParameters.from_config(cfg or {})
    for k, v in params.items():
        setattr(p, k, v)
    return HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))


def mutant_method(name, old, new):
    """HeatPumpOptimizer.<name> with the single line `old` replaced by `new` (stripped match)."""
    src = textwrap.dedent(inspect.getsource(getattr(HeatPumpOptimizer, name)))
    lines = src.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.strip() == old.strip()]
    assert len(hits) == 1, f"anchor {old!r} found {len(hits)}x"
    i = hits[0]
    indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indent + new.strip() + "\n"
    ns = dict(opt_mod.__dict__)
    exec(compile("".join(lines), opt_mod.__file__, "exec"), ns)
    return ns[name]


@contextlib.contextmanager
def mutated(name, old, new):
    with mock.patch.object(HeatPumpOptimizer, name, mutant_method(name, old, new)):
        yield


def outcome(fn):
    """The call's value, or the exception's type name: an exception is an observable outcome."""
    try:
        return fn()
    except Exception as err:  # noqa: BLE001
        return f"raises {type(err).__name__}"


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt} count")
