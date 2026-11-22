#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor d1197dfed14a6927 (audit round 11, seat D3-s1).
# Metric: the estimator DefrostDerate._decide names (source, value, samples) for a bucket whose inferred and measured trust-blended derates are exactly equal while the duty count is below DERATE_CONFIDENCE_SAMPLES; source is published per bucket in summary() (the diagnostics attribute).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_d1197dfed14a6927.py
# Expected: tie_source_baseline='measured', tie_source_mutant='inferred'; value identical; a different-count tie also moves `samples` (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate._decide, line 313 (read by summary() and factor())
# Perturbation: key d1197dfed14a6927 CMP_BOUND, `if inferred < measured:` -> `if inferred <= measured:`, in memory. Direction: source 'measured' -> 'inferred' at the tie.
# Null control: inferred strictly above / below measured, where the comparison is not tied.
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
OLD = "        if inferred < measured:"
mut = mutated(d.DefrostDerate._decide, d, OLD, "        if inferred <= measured:")


def bucket(factor, n_inf, duty, n_duty):
    dd = d.DefrostDerate()
    t, h = dd._bucket(0.0, 90.0)
    dd.factors[t][h], dd.counts[t][h] = factor, n_inf
    dd.duty[t][h], dd.duty_counts[t][h] = duty, n_duty
    return dd, t, h


def _diff_count_tie(duty=0.2, n_duty=3):
    """The first inferred count (!= n_duty) and factor whose trust-blended value equals
    the measured one bit for bit, searched rather than assumed (float ties are exact or absent)."""
    target = d.DefrostDerate._trusted(d.derate_from_duty(duty), n_duty)
    for n in range(1, d.DERATE_CONFIDENCE_SAMPLES):
        if n == n_duty:
            continue
        trust = min(1.0, n / d.DERATE_CONFIDENCE_SAMPLES)
        for f in (1.0 + (target - 1.0) / trust,):
            for g in (f, f + 1e-16, f - 1e-16, f + 2e-16, f - 2e-16):
                if d.DefrostDerate._trusted(g, n) == target:
                    return (g, n, duty, n_duty)
    return (0.8, 6, duty, n_duty)


cases = {
    "tie_same_count": (d.derate_from_duty(0.1), 5, 0.1, 5),
    "tie_diff_count": _diff_count_tie(),
    "inferred_lower": (0.7, 6, 0.1, 5),
    "inferred_higher": (0.99, 6, 0.2, 5),
}
moved = 0
for name, args in cases.items():
    dd, t, h = bucket(*args)
    tie = d.DefrostDerate._trusted(dd.factors[t][h], dd.counts[t][h]) == d.DefrostDerate._trusted(d.derate_from_duty(dd.duty[t][h]), dd.duty_counts[t][h])
    b = dd._decide(t, h)
    m = mut(dd, t, h)
    with mock.patch.object(d.DefrostDerate, "_decide", mut):
        ms = [(r["source"], r["samples"]) for r in dd.summary()]
    bs = [(r["source"], r["samples"]) for r in dd.summary()]
    print(f"RESULT {name}_exact_tie={int(tie)}")
    print(f"RESULT {name}_decide_baseline={b!r}")
    print(f"RESULT {name}_decide_mutant={m!r}")
    print(f"RESULT {name}_summary_baseline={bs!r}")
    print(f"RESULT {name}_summary_mutant={ms!r}")
    moved += b != m
print(f"RESULT cases_moved={moved} count")


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
