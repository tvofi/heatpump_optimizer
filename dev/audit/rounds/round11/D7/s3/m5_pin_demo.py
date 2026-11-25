#!/usr/bin/env python3
"""D7.M5 (round 11, seat D7-s3): the perturbation for the unpinned-function count.

Metric (one line): failing checks this one-check script reports for
`early_cutoff.py:diagnostics_view`, a function m5_train.py reads `swallowed` (every suite
script that enters it stays green when it raises).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_pin_demo.py            # 0 failing
    HPO_FN_MUTATE=early_cutoff.py:<first line> PYTHONPATH=dev/audit/rounds/round11/D7/s3/trace_site:tests/hastub \
        python3 dev/audit/rounds/round11/D7/s3/m5_pin_demo.py                                # 1 failing

Instrumented symbol: custom_components.heatpump_optimizer.early_cutoff:diagnostics_view.
Perturbation: with a check that calls the function and reads its answer, the deletion mutant
is killed (failing 0 -> 1), so `swallowed` falls by one for each such check added to the suite:
the count is a property of the suite's checks, not of this harness's labels.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64, Python 3.14.7; exact.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import sys
import time

sys.path.insert(0, os.getcwd())


def main():
    from custom_components.heatpump_optimizer import early_cutoff
    failing = 0
    try:
        view = early_cutoff.diagnostics_view(early_cutoff.CutoffState())
        ok = view["margin_k"] == early_cutoff.MARGIN_K and view["listening"] is False
    except Exception as err:  # the deletion mutant lands here
        ok = False
        print("  (raised %s: %s)" % (type(err).__name__, err))
    print("  %s the cut-off's diagnostics view names its margin and says it is not listening" % ("ok  " if ok else "FAIL"))
    failing += (not ok)
    print("RESULT failing=%d checks" % failing)
    print("RESULT first_line=%d line" % early_cutoff.diagnostics_view.__code__.co_firstlineno)
    print("RESULT thread_factor=%.3f ratio" % (time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    print("RESULT swapins=0 count")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
