#!/usr/bin/env python3
# Metric: the initial-guess weights optimizer._price_guess_weights returns for a 4-step horizon whose mean price lies
#   between the mutant's and the baseline's threshold (prices [0.0, 0.0004, 0.0008, 0.0012], mean 6e-4 SEK/kWh):
#   max |weight_baseline - weight_mutant| over the steps.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_eee37674711fa45f.py
# EXPECTED RESULT weights_baseline=[1.0, 0.7333, 0.4667, 0.2]  (rank fill: mean 6e-4 <= 1e-3)
# EXPECTED RESULT weights_mutant=[1.0, 0.8344, 0.2, 0.2]  (smooth mean-normalised clip: mean 6e-4 > 2e-6; the two most
#   expensive steps saturate at the 0.2 floor, the rank order between them is lost)
# EXPECTED RESULT max_abs_delta=0.2667 (tolerance 1e-3)
# EXPECTED RESULT null_max_abs_delta=0.0  (mean 0.5 SEK/kWh, above both thresholds; and mean -0.1, below both)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_price_guess_weights (reads PRICE_MEAN_GUESS_EPS,
#   optimizer.py:2006, at line 2082).
# Perturbation: `PRICE_MEAN_GUESS_EPS = 1e-3` -> `PRICE_MEAN_GUESS_EPS = 0.002e-3` (CONST eee37674711fa45f), applied in memory
#   with mock.patch.object on the module constant (read at call time). Direction: rank weights -> smooth clipped weights
#   for a horizon mean in (2e-6, 1e-3].
# Null control: prices mean 0.5 and mean -0.1 (both arms take the same branch; delta 0).
# Inputs tried: the 4-step ramp above; a 24-step ramp 0..0.0012; the two null horizons.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
from pathlib import Path
from unittest import mock


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
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer as O  # noqa: E402

NEW = 0.002e-3
assert O.PRICE_MEAN_GUESS_EPS == 1e-3


def both(p):
    p = np.asarray(p, dtype=float)
    b = O._price_guess_weights(p)
    with mock.patch.object(O, "PRICE_MEAN_GUESS_EPS", NEW):
        m = O._price_guess_weights(p)
    return b, m


b, m = both([0.0, 0.0004, 0.0008, 0.0012])
b24, m24 = both(np.linspace(0.0, 0.0012, 24))
nb1, nm1 = both([0.2, 0.4, 0.6, 0.8])
nb2, nm2 = both([-0.2, -0.1, 0.0, -0.1])
print(f"RESULT weights_baseline={[round(float(x), 4) for x in b]}")
print(f"RESULT weights_mutant={[round(float(x), 4) for x in m]}")
print(f"RESULT max_abs_delta={float(np.max(np.abs(b - m))):.4f}")
print(f"RESULT max_abs_delta_24step={float(np.max(np.abs(b24 - m24))):.4f}")
print(f"RESULT null_max_abs_delta={max(float(np.max(np.abs(nb1 - nm1))), float(np.max(np.abs(nb2 - nm2))))}")
tail()
