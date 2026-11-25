#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor fc4fe0f49de831a8 (audit round 11, seat D3-s1).
# Metric: the derate derate_from_duty returns over a grid of measured duties 0..1 (step 0.01), and the derate DefrostDerate.factor publishes for a bucket trusted at duty 0.5: count of grid points whose value differs between arms, and the largest difference.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_fc4fe0f49de831a8.py
# Expected: points_differ: only duties above 0.30, by at most 1 ulp (5.6e-17): DERATE_MIN (0.55) already equals 1 - 1.5 * 0.30, so the duty cap binds nowhere the DERATE_MIN floor does not (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:derate_from_duty (reads DEFROST_DUTY_MAX at defrost.py:204); constant at defrost.py:142
# Perturbation: key fc4fe0f49de831a8 CONST, `DEFROST_DUTY_MAX = 0.30` -> `DEFROST_DUTY_MAX = 0.6`, in memory (mock.patch.object). Direction searched: any duty whose derate changes.
# Null control: duties 0..0.30, where neither cap binds: identical.
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
print(f"RESULT derate_min={d.DERATE_MIN!r}")
print(f"RESULT one_minus_loss_x_cap={1.0 - d.DEFROST_DUTY_MAX * d.DEFROST_LOSS_MULTIPLIER!r}")
grid = [i / 100 for i in range(101)] + [0.299999, 0.300001, 0.3666667, 2.0, -0.1]
diff, maxd, maxd_gt_ulp = 0, 0.0, 0
for x in grid:
    b = d.derate_from_duty(x)
    with mock.patch.object(d, "DEFROST_DUTY_MAX", 0.6):
        m = d.derate_from_duty(x)
    if b != m:
        diff += 1
        maxd = max(maxd, abs(b - m))
        maxd_gt_ulp += abs(b - m) > 1e-12
print(f"RESULT grid_points={len(grid)} count")
print(f"RESULT points_differ={diff} count")
print(f"RESULT points_differ_beyond_1e-12={maxd_gt_ulp} count")
print(f"RESULT max_abs_diff={maxd!r}")
for arm, cap in (("baseline", d.DEFROST_DUTY_MAX), ("mutant", 0.6)):
    with mock.patch.object(d, "DEFROST_DUTY_MAX", cap):
        dd = d.DefrostDerate()
        for _ in range(12):
            dd.observe_duty(0.0, 90.0, 0.5)
        print(f"RESULT published_factor_duty0.5_{arm}={dd.factor(0.0, 90.0)!r}")
        print(f"RESULT summary_derate_duty0.5_{arm}={[r['derate'] for r in dd.summary()]!r}")


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
