#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 0e3569fef6b39497 (audit round 11, seat D3-s1).
# Metric: INFO 'takes over from the inferred estimate' records DefrostDerate.observe_duty logs when a bucket's duty count reaches DERATE_CONFIDENCE_SAMPLES, for a bucket with NO inferred samples (counts 0) and one with some; plus the bucket's grids after the 12 folds.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_0e3569fef6b39497.py
# Expected: no_inferred_handover_logs_baseline=0, mutant=1; with_inferred 1 in both arms; grids identical (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate.observe_duty, line 434
# Perturbation: key 0e3569fef6b39497 CMP_BOUND, `self.counts[t][h] > 0` -> `self.counts[t][h] >= 0`, in memory. Direction: 0 -> 1 handover log on a bucket that had nothing to hand over from (it reports 'inferred estimate 1.000 -> x').
# Null control: a bucket with inferred samples (counts 3), where the comparison is true either way.
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

from custom_components.heatpump_optimizer import defrost as d
OLD = "            and self.counts[t][h] > 0"
mut = mutated(d.DefrostDerate.observe_duty, d, OLD, OLD.replace("> 0", ">= 0"))
for label, n_inf in (("no_inferred", 0), ("with_inferred", 3)):
    grids = {}
    for arm, fn in (("baseline", d.DefrostDerate.observe_duty), ("mutant", mut)):
        dd = d.DefrostDerate()
        for _ in range(n_inf):
            dd.observe(0.0, 90.0, 0.8)
        n = logged(d.__name__, "takes over from the inferred", lambda: [fn(dd, 0.0, 90.0, 0.1) for _ in range(12)])
        grids[arm] = (dd.as_dict(), dd.factor(0.0, 90.0))
        print(f"RESULT {label}_handover_logs_{arm}={n} count")
    print(f"RESULT {label}_state_equal={int(grids['baseline'] == grids['mutant'])}")


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
