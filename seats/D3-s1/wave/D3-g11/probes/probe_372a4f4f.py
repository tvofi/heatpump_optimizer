#!/usr/bin/env python3
# Metric: whether coordinator._learned_pair accepts a stored fold [value, samples] (1 = installed, 0 = ValueError, dropped).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_372a4f4f.py
# Expected: RESULT zero_value_baseline=0, zero_value_mutant=1 (a stored [0.0, 3] fold is installed); null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_learned_pair (line 490,
#   `    if not (np.isfinite(value) and value > 0 and count >= 1):`).
# Perturbation: mutant 372a4f4fcc8de86f, `value > 0` -> `value >= 0`, applied in memory
#   (the function recompiled from its own source in the module namespace). Direction: accepted 0 -> 1 at value 0.0.
# Null control: values 1.5, -1.0, nan, inf and the count-0 entry, where both arms agree (null_moved counts disagreements).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")


def accepted(fn, entry):
    try:
        fn(entry)
        return 1
    except ValueError:
        return 0


import time
t0, t1 = time.process_time(), time.thread_time()
MUT = mutate(co._learned_pair, "value > 0 and", "value >= 0 and")
for name, entry in {"zero_value": [0.0, 3], "neg_zero_value": [-0.0, 1]}.items():
    print(f"RESULT {name}_baseline={accepted(co._learned_pair, entry)}")
    print(f"RESULT {name}_mutant={accepted(MUT, entry)}")
nulls = [[1.5, 3], [-1.0, 3], [float("nan"), 3], [float("inf"), 3], [2.0, 0]]
print(f"RESULT null_moved={sum(accepted(co._learned_pair, e) != accepted(MUT, e) for e in nulls)} count")
tail_results(t0, t1)
