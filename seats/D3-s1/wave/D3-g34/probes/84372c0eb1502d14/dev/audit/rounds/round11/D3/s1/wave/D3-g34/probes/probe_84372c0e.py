#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) on a noisy window whose first-pass UA/C slope is negative; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_84372c0e.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2010 `k_hat = max(float(pass1[0]), 0.0)` (CLAMP_DROP 84372c0eb1502d14).
# Perturbation: line 2010 -> `k_hat = (float(pass1[0]))`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=seed53_noise0.1
#   RESULT outcome_baseline=[completed ua=0.0711885946897037 C=5.2908388164657465 conf=0.7509833795353332]
#   RESULT outcome_mutant=[completed ua=0.07119096309555645 C=5.290664908635567 conf=0.7509833763113594]
#   RESULT cases_differing=1 count (of 1)
#   RESULT null_differing=0 count (of 2)
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

LINE = 2010
OLD = '        k_hat = max(float(pass1[0]), 0.0)'
NEW = '        k_hat = (float(pass1[0]))'

CASES = [
    ("seed53_noise0.1", L.plant(ua=0.0831723946810419, cap=5.681713411968536, gains=0.5743780480979319, noise=0.1,
                                dt_h=0.5, drift=0.05, seed=53, q=(3.96809291432578, 7.542472144251088, 0.0))),
]
NULLS = [("plant_clean", L.plant()), ("plant_noisy", L.plant(noise=0.03, seed=4))]

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
