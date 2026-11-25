#!/usr/bin/env python3
# Metric: the rain share coordinator._liquid_fraction returns for one step with precipitation exactly 1e-9 mm/h and a
#   snowfall whose water equivalent is at least that (1.0 = treated as dry / fully liquid; 0.0 = all snow).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_6f5898d3.py
# Expected: RESULT precip_1e-9_snow_baseline=1.0, mutant=0.0; null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_liquid_fraction (line 3101, `            precip > 1e-9,`).
# Perturbation: mutant 6f5898d327366799, `precip > 1e-9` -> `precip >= 1e-9`, in memory (recompiled from its own source in
#   the module namespace). Direction: 1.0 -> 0.0 at precip == 1e-9 with snow; boundary-only, the value multiplies a
#   1e-9 mm/h precipitation, so the wetting effect downstream is ~1e-9 (consequence negligible).
# Null control: precip 0, 2e-9, 1.0 with and without snow, and 1e-9 without snow, where both arms agree.
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

import time
import numpy as np

MUT = mutate(co._liquid_fraction, "precip > 1e-9,", "precip >= 1e-9,")
t0, t1 = time.process_time(), time.thread_time()
snow = co.SNOW_CM_PER_MM_WATER * 1e-9  # snowfall in cm whose water equivalent is 1e-9 mm
b = float(co._liquid_fraction(np.array([1e-9]), np.array([snow]))[0])
m = float(MUT(np.array([1e-9]), np.array([snow]))[0])
print(f"RESULT precip_1e-9_snow_baseline={b} mutant={m}")
P = np.array([0.0, 2e-9, 1.0, 0.0, 2e-9, 1.0, 1e-9])
S = np.array([0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0])
print(f"RESULT null_moved={int(np.sum(co._liquid_fraction(P, S) != MUT(P, S)))} count")
tail_results(t0, t1)
