#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) when two same-phase samples share a timestamp (h_prev = 0) or sit 3600 us apart; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_20f72103.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2018 `if h_prev <= 1e-6:` (GUARD_OFF 20f72103eda78713).
# Perturbation: line 2018 -> `if False:`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=dup0_step
#   RESULT outcome_baseline=[completed ua=0.19574719588552128 C=5.126629633823094 conf=0.9928502727789756]
#   RESULT outcome_mutant=[completed ua=0.19575055138538477 C=5.126622761903924 conf=0.9928505855787655]
#   RESULT cases_differing=3 count (of 3)
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

LINE = 2018
OLD = '                if h_prev <= 1e-6:'
NEW = '                if False:'

CASES = [
    ("dup0_step", L.insert_after(L.plant(), 6, timedelta(0))),
    ("dup0_relax", L.insert_after(L.plant(), 15, timedelta(0))),
    ("tie3600us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3600))),
]
NULLS = [("gap3601us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3601))),
           ("dup0_across_phases", L.insert_after(L.plant(), 3, timedelta(0)))]

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
