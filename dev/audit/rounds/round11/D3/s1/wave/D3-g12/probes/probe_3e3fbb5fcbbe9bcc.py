#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 3e3fbb5fcbbe9bcc (audit round 11, seat D3-s1).
# Metric: INFO records 'a pre-v5.3.0 store was upgraded' DefrostDerate.from_dict logs for a v1 store (factors/counts only), plus the restored `migrated` flag and factor grid (state the diagnostics publish).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3e3fbb5fcbbe9bcc.py
# Expected: upgrade_log_records_baseline=1, upgrade_log_records_mutant=0; migrated True and factors identical in both arms (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict, line 566
# Perturbation: key 3e3fbb5fcbbe9bcc GUARD_OFF, `if instance.migrated:` -> `if False:`, in memory (the classmethod re-compiled and patched onto the class). Direction: 1 -> 0 log records; state unchanged.
# Null control: a v2 store (duty grids present), where `migrated` is False and the guard is false either way.
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
OLD = "            if instance.migrated:"
mut = mutated(d.DefrostDerate.from_dict, d, OLD, "            if False:")  # a classmethod object (the decorator is in the source)
src = d.DefrostDerate()
src.observe(0.0, 90.0, 0.8)
v2 = src.as_dict()
v1 = {"factors": v2["factors"], "counts": v2["counts"]}
for label, store in (("v1_store", v1), ("v2_store", v2)):
    for arm in ("baseline", "mutant"):
        out = {}
        def go():
            if arm == "mutant":
                with mock.patch.object(d.DefrostDerate, "from_dict", mut):
                    out["i"] = d.DefrostDerate.from_dict(dict(store))
            else:
                out["i"] = d.DefrostDerate.from_dict(dict(store))
        n = logged(d.__name__, "store was upgraded", go)
        inst = out["i"]
        print(f"RESULT {label}_upgrade_log_records_{arm}={n} count")
        print(f"RESULT {label}_migrated_{arm}={inst.migrated!r}")
        print(f"RESULT {label}_factors_equal_source_{arm}={int(inst.factors == src.factors)}")


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
