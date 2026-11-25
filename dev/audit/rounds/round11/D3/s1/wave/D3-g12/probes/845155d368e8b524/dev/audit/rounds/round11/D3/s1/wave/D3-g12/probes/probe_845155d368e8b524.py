#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 845155d368e8b524 (audit round 11, seat D3-s1).
# Metric: what _outage_reading reports at a restart whose heartbeat gap is exactly OUTAGE_GAP_MINUTES (90 min); None means 'no outage'.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_845155d368e8b524.py
# Expected: gap_90.0min_baseline=None, gap_90.0min_mutant='Update gap of 90 minutes'; gaps 89.0 and 91.0 min identical in both arms (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_outage_reading, line 900
# Perturbation: key 845155d368e8b524 CMP_BOUND, `if gap_minutes <= OUTAGE_GAP_MINUTES:` -> `if gap_minutes < OUTAGE_GAP_MINUTES:`, in memory. Direction: None -> an outage reading at the tie.
# Null control: gaps of 89 and 91 minutes, where the bound is not tied.
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

from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import coordinator as c
OLD = "if gap_minutes <= OUTAGE_GAP_MINUTES:"
mut = mutated(c._outage_reading, c, OLD, OLD.replace("<=", "<"))
now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
print(f"RESULT outage_gap_minutes={c.OUTAGE_GAP_MINUTES}")
moved = 0
for gap in (89.0, 90.0, 91.0, 89.999, 90.001):
    last = (now - timedelta(minutes=gap)).isoformat()
    b, m = c._outage_reading(last, now, False), mut(last, now, False)
    print(f"RESULT gap_{gap}min_baseline={b!r}")
    print(f"RESULT gap_{gap}min_mutant={m!r}")
    moved += b != m
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
