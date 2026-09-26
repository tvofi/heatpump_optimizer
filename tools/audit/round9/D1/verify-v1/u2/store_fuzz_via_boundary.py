#!/usr/bin/env python3
"""Round 9 verify V1, unit D1-2: the finder's store_fuzz.py re-run with every payload passed
through the production store boundary (store._sanitize, what QuarantiningStore.async_load
hands DefrostDerate.from_dict in real Home Assistant) before the loader sees it.

Metric (one line): the finder's own RESULT lines (tools/audit/round9/D1/s4/store_fuzz.py,
unchanged) with DefrostDerate.from_dict wrapped as from_dict(_sanitize(data)) in memory.
Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/verify-v1/u2/store_fuzz_via_boundary.py [finder flags]
Expected: duty_targeted_stuck=30, duty_targeted_pinned_at_derate_min=23,
          v2_one_bad_cell_flagged_migrated=226, nan_bucket_factor_after_200_zero_folds=1.0000
          (exact, seeded; see verify-v1-2.md).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence tree 6f51db2c).
Machine: 4 vCPU cloud container (box G1-V1), CPython 3.14.0rc2. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import runpy
import sys

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, ".")

from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer import store as S  # noqa: E402

_orig = D.DefrostDerate.from_dict.__func__


def _through_boundary(cls, data):
    return _orig(cls, S._sanitize(data))


D.DefrostDerate.from_dict = classmethod(_through_boundary)
sys.argv = ["store_fuzz.py"] + sys.argv[1:]
runpy.run_path("tools/audit/round9/D1/s4/store_fuzz.py", run_name="__main__")
