#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor b028ad9d6c702965 (audit round 11, seat D3-s1).
# Metric: length of the warm-start plan _warm_seeded hands the fresh per-solve optimizer (`_prev_shipped_plan`) when the coordinator holds a previous plan (0 = no warm start).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_b028ad9d6c702965.py
# Expected: warm_plan_len_baseline=96, warm_plan_len_mutant=0 (attribute absent); cold start (no previous plan) 0 in both arms (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_warm_seeded, line 2360 (read by optimizer.py HeatPumpOptimizer via getattr(self, '_prev_shipped_plan', None) as one extra multi-start candidate)
# Perturbation: key b028ad9d6c702965 GUARD_OFF, `if result is not None:` -> `if False:`, in memory. Direction: 96 -> 0: the MPC warm start (#1295) is never seeded.
# Null control: a cold start (`_optimization_result` None), where the guard is false either way.
# Count key: the value the production symbol returns or stores (never an input attribute).
# Runs from the repository root, writes nothing; the mutant lives only in memory.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, logging, sys, textwrap, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_P0, _T0 = time.process_time(), time.thread_time()


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


def mutated(obj, module, old, new):
    """``obj`` (a function, or a method/classmethod read off its class) re-compiled
    from its own source with the one-line mutant applied, in ``module``'s namespace."""
    raw = obj.__func__ if hasattr(obj, "__func__") else obj
    full = inspect.getsource(raw)
    cut = len(full) - len(full.lstrip(" "))  # the def's own indent, which dedent strips
    src = textwrap.dedent(full)
    old, new = old[cut:], new[cut:]
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(old, new, 1), module.__file__, "exec"), ns)
    return ns[raw.__name__]


class _Count(logging.Handler):
    def __init__(self, needle):
        super().__init__(logging.DEBUG)
        self.needle, self.n = needle, 0

    def emit(self, record):
        if self.needle in record.getMessage():
            self.n += 1


def logged(logger_name, needle, fn):
    """How many records containing ``needle`` ``fn()`` logs on ``logger_name``."""
    lg = logging.getLogger(logger_name)
    h = _Count(needle)
    lg.addHandler(h)
    old = lg.level
    lg.setLevel(logging.DEBUG)
    try:
        fn()
    finally:
        lg.removeHandler(h)
        lg.setLevel(old)
    return h.n

import numpy as np
from custom_components.heatpump_optimizer import coordinator as c
OLD = "    if result is not None:"
mut = mutated(c._warm_seeded, c, OLD, "    if False:")
plan = SimpleNamespace(power_schedule=list(np.linspace(0.5, 2.5, 96)))
for label, prev in (("previous_plan", plan), ("cold_start", None)):
    for arm, fn in (("baseline", c._warm_seeded), ("mutant", mut)):
        coord = SimpleNamespace(_optimization_result=prev)
        opt = fn(coord, SimpleNamespace())
        seeded = getattr(opt, "_prev_shipped_plan", None)
        print(f"RESULT {label}_warm_plan_len_{arm}={0 if seeded is None else len(seeded)} count")


def _swapins():
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except OSError:
        pass
    return 0


_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_swapins()}")
