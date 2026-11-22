#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) when sigma2 equals x1_spread2/9 exactly in float64; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_44bb0ce0.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2038 `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:` (CMP_BOUND 44bb0ce0b258242c).
# Perturbation: line 2038 -> `if sigma2 > 0.0 and sigma2 >= x1_spread2 / 9.0:`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=sigma_tie
#   RESULT outcome_baseline=[refused:fit gave implausible signs]
#   RESULT outcome_mutant=[refused:sensor noise dominates the excursion]
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

LINE = 2038
OLD = '        if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:'
NEW = '        if sigma2 > 0.0 and sigma2 >= x1_spread2 / 9.0:'

CASES = [("sigma_tie", L.sigma_tie_series())]
NULLS = [("sigma_tie_broken", L.sigma_tie_series(break_tie=True)), ("plant", L.plant())]

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
