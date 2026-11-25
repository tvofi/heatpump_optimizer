#!/usr/bin/env python3
# Metric: the step list HeatPumpOptimizer._expand_off_blocks returns, baseline vs mutant: on a pin of exactly 0.5 (the
#   tie), and the count of differing outputs over 5000 seeded random pin arrays drawn from the values production
#   writes (manual_plan PIN_OFF 0.0, PIN_ON 1.0, PIN_FREE NaN; channel_pins builds every pin from these three).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_904118eef67fced3.py
# EXPECTED RESULT tie_baseline=[2]
# EXPECTED RESULT tie_mutant=[0,1,2]
# EXPECTED RESULT production_domain_differ=0 count  (of 5000)
# EXPECTED RESULT null_delta=0 count  (pins 0.0/1.0 only)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._expand_off_blocks
#   (line 5271 `while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:`), callers 5257-5258.
# Perturbation: line 5271 `< 0.5` -> `<= 0.5` (CMP_BOUND 904118eef67fced3), in memory. Direction: a 0.5 pin joins the
#   released off-block; no move on the {0, 1, NaN} pins the integration writes.
# Null control: pins of 0.0 and 1.0 only.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, resource
from datetime import datetime, timedelta
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, SolveInputs, ForecastSeries, SolveLimits)
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_P0, _T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """HeatPumpOptimizer.<name> recompiled from its own source with the one line swapped."""
    raw = inspect.getattr_static(HeatPumpOptimizer, name)
    fn = raw.__func__ if isinstance(raw, staticmethod) else raw
    src = textwrap.dedent(inspect.getsource(fn))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = {}
    # globals = the live module dict, so a collaborator patched on the module is seen by both arms alike
    exec(compile(src.replace(old, new, 1), optimizer.__file__, "exec"), optimizer.__dict__, ns)
    out = ns[name]
    if isinstance(raw, staticmethod) and not isinstance(out, staticmethod):
        out = staticmethod(out)
    return out


def mutated(name, old, new):
    """Context manager: the class attribute swapped to the mutant for the block."""
    return mock.patch.object(HeatPumpOptimizer, name, mutant_method(name, old, new))


def outcome(fn, *a, **k):
    try:
        r = fn(*a, **k)
    except Exception as exc:  # the mutant's failure is the number
        return f"raise:{type(exc).__name__}"
    if r is None:
        return "None"
    if isinstance(r, np.ndarray):
        return "array:" + ",".join(f"{v:g}" for v in r.tolist())
    return repr(r)


def footer():
    p, t = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
from custom_components.heatpump_optimizer.manual_plan import PIN_FREE, PIN_OFF, PIN_ON  # noqa: E402
NAME = "_expand_off_blocks"
OLD = "while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:"
NEW = "while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) <= 0.5:"
f = lambda p, b: repr(HeatPumpOptimizer._expand_off_blocks(np.asarray(p, float), b))  # noqa: E731
tie = ([0.5, 0.5, 0.0, 1.0], [2])
null = ([0.0, 1.0, 0.0, 0.0], [3])
rng = np.random.default_rng(11)
dom = np.array([PIN_OFF, PIN_ON, PIN_FREE])
FUZZ = []
for _ in range(5000):
    n = int(rng.integers(1, 30))
    FUZZ.append((dom[rng.integers(0, 3, n)], sorted(set(rng.integers(0, n, int(rng.integers(1, 4))).tolist()))))
b = (f(*tie), f(*null), [f(*c) for c in FUZZ])
with mutated(NAME, OLD, NEW):
    m = (f(*tie), f(*null), [f(*c) for c in FUZZ])
print(f"RESULT tie_baseline={b[0].replace(' ', '')}")
print(f"RESULT tie_mutant={m[0].replace(' ', '')}")
print(f"RESULT production_domain_differ={sum(x != y for x, y in zip(b[2], m[2]))} count")
print(f"RESULT null_delta={int(b[1] != m[1])} count")
footer()
