#!/usr/bin/env python3
# Metric: count of duty inputs (15: negatives, +-0.0, the clamp edges, above-cap, +-inf, nan) on which
#   derate_from_duty returns a different float baseline vs mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_168e4035dbc9bb84.py
# EXPECTED RESULT inputs_moved=0 of 15 ()  (a negative duty gives 1 + |duty|*1.5 > 1, which min(DERATE_MAX=1.0, .)
#   caps back to exactly 1.0; nan goes through max(DERATE_MIN, nan)=0.55 in both arms)
# EXPECTED RESULT posctl_derate_max_1_05 baseline=1.0 mutant=1.05  (the harness separates once the cap is above 1)
# Count key: the float derate_from_duty returns (DefrostDerate._decide's measured estimator).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:derate_from_duty
#   (line 204 `    duty = min(max(float(duty), 0.0), DEFROST_DUTY_MAX)`).
# Perturbation: mutant 168e4035dbc9bb84, the 0.0 floor dropped, in memory (function recompiled from its own source).
#   Direction if not equivalent: derate above 1.0 for a negative duty; capped by DERATE_MAX = 1.0.
# Null control: non-negative duties, where the floor is inactive.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
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
_T0 = (time.process_time(), time.thread_time())


def mutated(module, func, old, new, name=None):
    """``func`` recompiled from its own source with the one mutant line swapped (anchor must occur once)."""
    src = textwrap.dedent(inspect.getsource(func))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(o, n, 1), module.__file__, "exec"), ns)
    return ns[name or func.__name__]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")]
        print(f"RESULT swapins={swp[0].split()[1] if swp else 0}")
    except OSError:
        print("RESULT swapins=n/a")
from custom_components.heatpump_optimizer import defrost  # noqa: E402

OLD = "duty = min(max(float(duty), 0.0), DEFROST_DUTY_MAX)"
NEW = "duty = min((float(duty)), DEFROST_DUTY_MAX)"
MUT = mutated(defrost, defrost.derate_from_duty, OLD, NEW)
inputs = [-1e9, -1.0, -0.3, -1e-12, -0.0, 0.0, 1e-12, 0.1, 0.3, 0.31, 1.0, 5.0,
          float("inf"), float("-inf"), float("nan")]
moved = []
for v in inputs:
    b, m = defrost.derate_from_duty(v), MUT(v)
    print(f"RESULT derate({v!r}) baseline={b!r} mutant={m!r}")
    if not (b == m or (b != b and m != m)) or str(b) != str(m):
        moved.append(repr(v))
print(f"RESULT inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved)})")
print(f"RESULT DERATE_MAX={defrost.DERATE_MAX}")
# Positive control on the harness: if DERATE_MAX were above 1 the dropped floor would show (the M4 condition).
with mock.patch.object(defrost, "DERATE_MAX", 1.05):
    b = defrost.derate_from_duty(-0.3)
    m = mutated(defrost, defrost.derate_from_duty, OLD, NEW)(-0.3)
print(f"RESULT posctl_derate_max_1_05 baseline={b} mutant={m}")
footer()
