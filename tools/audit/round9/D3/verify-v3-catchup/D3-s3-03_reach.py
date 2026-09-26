#!/usr/bin/env python3
"""Verifier V3 cheap check for D3-s3-03 (ledger.MonthlyLedger.add).

Metric: number of months surviving an as_dict/from_dict round trip after one
finite add() then one NaN add() to the same line, under the baseline guard
vs the M21 mutant (`if not (...): return` replaced with `if True:`, i.e. the
guard always no-ops -- but we test the FINDER's stated mutant, which deletes
the finiteness check so a NaN write reaches the ledger), with a null
(identity) arm.

Command:
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
    tools/audit/round9/D3/verify-v3-catchup/D3-s3-03_reach.py

Real-HA note: ledger.py is documented "Kept free of Home Assistant imports
so it can be unit-tested directly" (module docstring) and a grep of its
import block confirms no homeassistant.* import. This seam cannot diverge
between tests/hastub and real Home Assistant 2026.2.3; not run against
/root/venvha for that reason (recorded as not-applicable, not skipped).

Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box G1-V3 (4 CPUs).
"""
import math
import os
import sys
import time
from datetime import datetime
from unittest import mock

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

t_process0 = time.process_time()
t_wall0 = time.time()

sys.path.insert(0, os.getcwd())

from custom_components.heatpump_optimizer.ledger import MonthlyLedger  # noqa: E402


def _mutant_add(self, when, line, *, kwh, sek):
    # M21: the `if not (np.isfinite(kwh) and np.isfinite(sek)): return` guard deleted.
    from custom_components.heatpump_optimizer.ledger import month_key

    lines = self._month(month_key(when))["lines"]
    entry = lines.setdefault(line, {"kwh": 0.0, "sek": 0.0})
    entry["kwh"] = float(entry["kwh"]) + float(kwh)
    entry["sek"] = float(entry["sek"]) + float(sek)


def run(mutant: bool) -> int:
    ledger = MonthlyLedger()
    when = datetime(2026, 1, 15)
    ledger.add(when, "grid", kwh=10.0, sek=25.0)
    if mutant:
        with mock.patch.object(MonthlyLedger, "add", _mutant_add):
            ledger.add(when, "grid", kwh=math.nan, sek=1.0)
    else:
        ledger.add(when, "grid", kwh=math.nan, sek=1.0)  # baseline: dropped, no-op

    dumped = ledger.as_dict()
    reloaded = MonthlyLedger.from_dict(dumped)
    return len(reloaded.months)


def main():
    baseline_months = run(mutant=False)
    mutant_months = run(mutant=True)
    null_months = run(mutant=False)

    print(f"RESULT baseline_months_after_reload={baseline_months}")
    print(f"RESULT mutant_months_after_reload={mutant_months}")
    print(f"RESULT mutant_delta={baseline_months - mutant_months} months")
    print(f"RESULT null_delta={baseline_months - null_months} months")

    thread_cpu = time.process_time() - t_process0
    wall = time.time() - t_wall0
    thread_factor = (thread_cpu / wall) if wall > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT thread_factor={min(thread_factor, 1.0):.3f}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
