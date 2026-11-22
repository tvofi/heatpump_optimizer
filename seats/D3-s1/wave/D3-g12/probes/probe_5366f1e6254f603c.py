#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 5366f1e6254f603c (audit round 11, seat D3-s1).
# Metric: samples DefrostDerate.observe folds into a bucket (counts) and the resulting factor for delivered_ratio exactly 0.0 (1 = folded, 0 = dropped).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_5366f1e6254f603c.py
# Expected: ratio0.0_count_baseline=0, mutant=1 (factor 1.0 -> 0.9775, the target clamped to DERATE_MIN); other ratios identical (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate.observe, line 392
# Perturbation: key 5366f1e6254f603c CMP_BOUND, `delivered_ratio <= 0` -> `delivered_ratio < 0`, in memory. Direction: a zero ratio dropped -> folded as the deepest derate.
# Null control: ratios 1e-9, 1.0, 2.999999, where the lower bound is not tied.
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
OLD = "        if delivered_ratio <= 0 or delivered_ratio > 3.0:"
mut = mutated(d.DefrostDerate.observe, d, OLD, OLD.replace('delivered_ratio <= 0 ', 'delivered_ratio < 0 '))
moved = 0
for ratio in (0.0, 3.0, 1e-9, 2.999999, 3.000001, 1.0):
    out = {}
    for arm, fn in (("baseline", d.DefrostDerate.observe), ("mutant", mut)):
        dd = d.DefrostDerate()
        t, h = dd._bucket(0.0, 90.0)
        fn(dd, 0.0, 90.0, ratio)
        out[arm] = (dd.counts[t][h], dd.factors[t][h])
        print(f"RESULT ratio{ratio}_count_{arm}={dd.counts[t][h]} count")
        print(f"RESULT ratio{ratio}_factor_{arm}={dd.factors[t][h]!r}")
    moved += out["baseline"] != out["mutant"]
print(f"RESULT ratios_moved={moved} count")
# On a bucket already learned to 0.8 over 6 samples (half trust), the edge ratio's fold moves the factor.
for ratio in (0.0, 3.0):
    for arm, fn in (("baseline", d.DefrostDerate.observe), ("mutant", mut)):
        dd = d.DefrostDerate()
        t, h = dd._bucket(0.0, 90.0)
        dd.factors[t][h], dd.counts[t][h] = 0.8, 6
        fn(dd, 0.0, 90.0, ratio)
        print(f"RESULT learned_ratio{ratio}_published_factor_{arm}={dd.factor(0.0, 90.0)!r}")


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
