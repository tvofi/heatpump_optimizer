#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 89bec0a0291b4756 (audit round 11, seat D3-s1).
# Metric: whether _storable_sample_count accepts a stored learner sample count of exactly 2**31 (1 accepted with its int, 0 raised ValueError: the learned value is then discarded on load).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_89bec0a0291b4756.py
# Expected: accepted_2^31_baseline=1, accepted_2^31_mutant=0; 2**31-1 and 2**31+1 identical in both arms (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_storable_sample_count, line 467
# Perturbation: key 89bec0a0291b4756 CMP_BOUND, `not 0 <= count <= 2**31` -> `not 0 <= count < 2**31`, in memory. Direction: accepted -> rejected at the tie.
# Null control: counts 2**31-1 and 2**31+1 and 0, where the upper bound is not tied.
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

from custom_components.heatpump_optimizer import coordinator as c
OLD = "if not np.isfinite(count) or not 0 <= count <= 2**31:"
mut = mutated(c._storable_sample_count, c, OLD, OLD.replace("count <= 2**31", "count < 2**31"))


def acc(fn, raw):
    try:
        return 1, fn(raw)
    except ValueError:
        return 0, None


moved = 0
for name, raw in (("0", 0), ("2^31-1", 2**31 - 1), ("2^31", 2**31), ("2^31+1", 2**31 + 1), ("2^31_float", float(2**31))):
    (ba, bv), (ma, mv) = acc(c._storable_sample_count, raw), acc(mut, raw)
    print(f"RESULT accepted_{name}_baseline={ba} (value {bv!r})")
    print(f"RESULT accepted_{name}_mutant={ma} (value {mv!r})")
    moved += ba != ma
print(f"RESULT inputs_moved={moved} count")


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
