#!/usr/bin/env python3
# Metric: identify()'s SysIdResult differs (repr) at the smallest row counts the rows>=5 guard admits; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_a9bc37e9.py
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line 2037 `x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0)` (CLAMP_DROP a9bc37e9ba781833).
# Perturbation: line 2037 -> `x1_spread2 = float(np.var(a[:, 0])) * n_rows / (n_rows - 1.0)`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
# EXPECTED (exact):
#   RESULT first_case=rows5_exact
#   RESULT outcome_baseline=[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]
#   RESULT outcome_mutant=[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]
#   RESULT cases_differing=0 count (of 5)
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

LINE = 2037
OLD = '        x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0)'
NEW = '        x1_spread2 = float(np.var(a[:, 0])) * n_rows / (n_rows - 1.0)'

CASES = [
    ("rows5_exact", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:6]),
    ("rows5_noisy", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5, noise=0.03, seed=1)[:6]),
    ("rows6", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:7]),
    ("gap_4rows_guarded", L.samples([20, 20.2, 20.3, 20.1, 20.4, 19.9, 20.0], [0] * 7, [3, 3, 6, 6, 0, 0, 0],
                                    [L.S, L.S, L.T, L.T, L.R, L.R, L.R], [0, 0.5, 1, 4, 4.5, 8, 8.5])),
    ("plant", L.plant()),
]
NULLS = []

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
