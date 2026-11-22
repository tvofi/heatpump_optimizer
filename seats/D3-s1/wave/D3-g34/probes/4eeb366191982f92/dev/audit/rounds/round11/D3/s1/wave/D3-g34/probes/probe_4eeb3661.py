#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) on a window with exactly three in-phase second differences; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_4eeb3661.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2032 `if len(d2_all) >= 3:` (CMP_BOUND 4eeb366191982f92).
# Perturbation: line 2032 -> `if len(d2_all) > 3:`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=3triples_noise0.02
#   RESULT outcome_baseline=[completed ua=0.1931445891215017 C=4.5987039940244845 conf=0.3039170461625474]
#   RESULT outcome_mutant=[completed ua=0.1931817916300817 C=4.598419055037595 conf=0.30391700686422346]
#   RESULT cases_differing=2 count (of 2)
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

LINE = 2032
OLD = '        if len(d2_all) >= 3:'
NEW = '        if len(d2_all) > 3:'

CASES = [
    ("3triples_noise0.02", L.plant(hours=(0.75, 0.75, 0.75), noise=0.02, seed=0)[:9]),
    ("3triples_clean", L.plant(hours=(0.75, 0.75, 0.75))[:9]),
]
NULLS = [("4triples_noise0.02", L.plant(hours=(1.0, 1.0, 0.75), noise=0.02, seed=0)[:12]),
           ("plant", L.plant())]

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
