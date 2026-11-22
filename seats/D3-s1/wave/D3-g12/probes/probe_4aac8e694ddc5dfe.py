#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 4aac8e694ddc5dfe (audit round 11, seat D3-s1).
# Metric: the duty count a DefrostDerate bucket keeps across as_dict -> from_dict when its stored duty is exactly 0.0 (12 = kept, 0 = the bucket restarts unmeasured), the factor published after the restore, and how many measured cells a store of zero-duty buckets keeps.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4aac8e694ddc5dfe.py
# Expected: duty0.0_restored_duty_count_baseline=12, mutant=0; duties 0.25, 0.5, 1.0 identical (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict._unit, line 537
# Perturbation: key 4aac8e694ddc5dfe CMP_BOUND, `0.0 <= v <= 1.0` -> `0.0 < v <= 1.0`, in memory. Direction: a zero-duty cell (the commonest measured observation: 'no defrost happened') kept -> reset at every restart.
# Null control: stored duties 0.25, 0.5 and 1.0, where the lower bound is not tied.
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
OLD = "            return 0.0 <= v <= 1.0  # observe_duty's gate; NaN fails it"
NEW = OLD.replace('0.0 <= v', '0.0 < v')
mut = mutated(d.DefrostDerate.from_dict, d, OLD, NEW)  # a classmethod object (the decorator is in the source)
moved = 0
for duty in (0.0, 0.5, 1.0, 0.25):
    src = d.DefrostDerate()
    for _ in range(12):
        src.observe_duty(0.0, 90.0, duty)
    t, h = src._bucket(0.0, 90.0)
    store = src.as_dict()
    store["duty"][t][h] = duty  # the cell holds exactly the edge value
    b = d.DefrostDerate.from_dict(store)
    with mock.patch.object(d.DefrostDerate, "from_dict", mut):
        m = d.DefrostDerate.from_dict(store)
    for arm, inst in (("baseline", b), ("mutant", m)):
        print(f"RESULT duty{duty}_restored_duty_count_{arm}={inst.duty_counts[t][h]} count")
        print(f"RESULT duty{duty}_published_factor_{arm}={inst.factor(0.0, 90.0)!r}")
    moved += b.duty_counts[t][h] != m.duty_counts[t][h]
    if duty == 0.0:
        cells_b = sum(n > 0 for row in b.duty_counts for n in row)
        cells_m = sum(n > 0 for row in m.duty_counts for n in row)
        print(f"RESULT duty0.0_measured_cells_kept_baseline={cells_b} count")
        print(f"RESULT duty0.0_measured_cells_kept_mutant={cells_m} count")
print(f"RESULT duties_moved={moved} count")
# The consequence on a bucket that also carries a learned inferred derate (0.8 over 12 samples):
# a reset measured half hands the bucket back to the inferred estimator.
for duty in (0.0, 1.0):
    src = d.DefrostDerate()
    t, h = src._bucket(0.0, 90.0)
    src.factors[t][h], src.counts[t][h] = 0.8, 12
    src.duty[t][h], src.duty_counts[t][h] = duty, 12
    store = src.as_dict()
    b = d.DefrostDerate.from_dict(store)
    with mock.patch.object(d.DefrostDerate, "from_dict", mut):
        m = d.DefrostDerate.from_dict(store)
    print(f"RESULT with_inferred_duty{duty}_factor_before_restore={src.factor(0.0, 90.0)!r}")
    print(f"RESULT with_inferred_duty{duty}_factor_after_restore_baseline={b.factor(0.0, 90.0)!r}")
    print(f"RESULT with_inferred_duty{duty}_factor_after_restore_mutant={m.factor(0.0, 90.0)!r}")


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
