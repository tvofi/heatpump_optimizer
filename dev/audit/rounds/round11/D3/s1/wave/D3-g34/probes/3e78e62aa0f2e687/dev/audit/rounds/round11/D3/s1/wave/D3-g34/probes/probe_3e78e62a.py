#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) when the fitted 1/C lands on 1e-6 exactly (the <= / < tie); counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_3e78e62a.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2126 `if one_over_c <= 1e-6 or ua_over_c <= 1e-6:` (CMP_BOUND 3e78e62aa0f2e687).
# Perturbation: line 2126 -> `if one_over_c < 1e-6 or ua_over_c <= 1e-6:`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=negative_ua
#   RESULT outcome_baseline=[refused:fit gave implausible signs]
#   RESULT outcome_mutant=[refused:fit gave implausible signs]
#   RESULT cases_differing=0 count (of 1602)
#   RESULT null_differing=0 count (of 1)
#   RESULT thread_factor ~1.0, load1 and swapins as measured (provisional)
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math, sys
from datetime import timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sysid_lib as L  # noqa: E402
import numpy as np  # noqa: E402,F401
from custom_components.heatpump_optimizer import sysid  # noqa: E402,F401

LINE = 2126
OLD = '        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:'
NEW = '        if one_over_c < 1e-6 or ua_over_c <= 1e-6:'

def tie_cases(which):
    """Exact-model 2-column-fallback series (power constant, so the 4-column solve is singular) whose true
    coefficient on the guarded side is 1e-6 and its +-300 neighbouring floats, plus 1000 random outdoor
    sequences at the true value: the search for an input where the fitted value lands on 1e-6 exactly."""
    out = []
    outs = [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0]
    for j in range(-300, 301):
        x = 1e-6
        for _ in range(abs(j)):
            x = math.nextafter(x, math.inf if j > 0 else -math.inf)
        out.append((f"ulp{j:+d}", L.exact_series(x, 0.25, [4.0] * 9, outs) if which == "k"
                    else L.exact_series(0.5, x, [4.0] * 9, outs)))
    rng = np.random.default_rng(1)
    for t in range(1000):
        o = [float(v) for v in rng.integers(-8, 12, 9)]
        out.append((f"rand{t}", L.exact_series(1e-6, 0.25, [4.0] * 9, o) if which == "k"
                    else L.exact_series(0.5, 1e-6, [4.0] * 9, o)))
    return out

CASES = [("negative_ua", L.plant(ua=-0.1, t_room=20.0))] + tie_cases("p")
NULLS = [("plant", L.plant())]

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
