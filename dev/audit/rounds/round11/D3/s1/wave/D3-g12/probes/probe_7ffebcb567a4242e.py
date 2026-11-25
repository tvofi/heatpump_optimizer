#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 7ffebcb567a4242e (audit round 11, seat D3-s1).
# Metric: the previous plan's seeded value _open_loop_plan_value returns when `now` sits exactly one step (900 s) before the plan's first timestamp; None means 'the plan says nothing'.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_7ffebcb567a4242e.py
# Expected: seed_at_900s_baseline=42.0, seed_at_900s_mutant=None; seed_at_899s and seed_at_901s identical in both arms (42.0 / None) (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_open_loop_plan_value, line 2540
# Perturbation: key 7ffebcb567a4242e CMP_BOUND, `starts[0] - now_s <= 900.0` -> `starts[0] - now_s < 900.0`, in memory (the function re-compiled from its own source and patched onto the module). Direction: 42.0 -> None at exactly 900 s.
# Null control: lead times 899 s and 901 s, where the bound is not tied: both arms agree.
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
OLD = "if starts[0] - now_s <= 900.0 else None"
mut = mutated(c._open_loop_plan_value, c, OLD, OLD.replace("<=", "<"))
start = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
plan = SimpleNamespace(timestamps=[start + timedelta(minutes=15 * i) for i in range(4)], tank_temp=[42.0, 43.0, 44.0, 45.0])
moved = 0
for lead in (899.0, 900.0, 901.0, 0.5, 1800.0):
    now = start - timedelta(seconds=lead)
    b = c._open_loop_plan_value(plan, "tank_temp", now)
    m = mut(plan, "tank_temp", now)
    tag = f"{lead:g}s"
    print(f"RESULT seed_at_{tag}_baseline={b!r}")
    print(f"RESULT seed_at_{tag}_mutant={m!r}")
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
