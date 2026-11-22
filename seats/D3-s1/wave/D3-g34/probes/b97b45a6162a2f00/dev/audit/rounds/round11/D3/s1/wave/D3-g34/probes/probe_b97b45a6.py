#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) when sigma2 == 0 (no or fewer than three in-phase triples, or flat second differences); counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_b97b45a6.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2038 `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:` (CMP_BOUND b97b45a6162a2f00).
# Perturbation: line 2038 -> `if sigma2 >= 0.0 and sigma2 > x1_spread2 / 9.0:`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=no_triples_relabelled_plant
#   RESULT outcome_baseline=[refused:sensor drift collapsed into heat-loss]
#   RESULT outcome_mutant=[refused:sensor drift collapsed into heat-loss]
#   RESULT cases_differing=0 count (of 6)
#   RESULT null_differing=0 count (of 0)
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
NEW = '        if sigma2 >= 0.0 and sigma2 > x1_spread2 / 9.0:'

CASES = [
    ("no_triples_relabelled_plant", L.relabel(L.plant(dt_h=0.5), L.ALT)),
    ("no_triples_exact_series", L.exact_series(0.5, 0.25, [4.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0])),
    ("two_triples", L.plant(hours=(0.5, 0.75, 0.5), dt_h=0.25)[:8]),
    ("no_triples_flat_delta", L.relabel(L.samples([20.0 + 0.25 * i for i in range(10)], [15.0 + 0.25 * i for i in range(10)],
                                         [2, 2, 2, 5, 5, 5, 0, 0, 0, 2], [L.S] * 10, list(range(10))), L.ALT)),
    ("sigma_tie", L.sigma_tie_series()),
    ("plant", L.plant()),
]
NULLS = []

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
