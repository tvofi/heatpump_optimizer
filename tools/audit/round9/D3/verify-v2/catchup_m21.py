#!/usr/bin/env python3
"""Verifier V2, D3-s3-03 (mutant M21, ledger.py:117 MonthlyLedger.add).

Metric (own): for a set of (kwh, sek) pairs including one finite pair after
one non-finite pair on the same month, whether real vs mutant MonthlyLedger
agree on the month's line total after an as_dict()/from_dict() round trip
(the mutant's guard-off write leaves a NaN line that from_dict's
_clean_month then drops whole).
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
  tools/audit/round9/D3/verify-v2/catchup_m21.py
Expected: RESULT differ_months_after_reload=1/1 (real keeps the month with
  the finite kwh preserved; mutant loses the whole month).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud box G1-V2,
  4 vCPU Linux, CPython 3.14.0rc2.
Instrumented symbol:
  custom_components.heatpump_optimizer.ledger:MonthlyLedger.add.
Perturbation: the recorded mutant M21 applied in memory to a second copy of
  the module (source text patched, then exec'd into its own namespace).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import types
import resource
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

POOL = json.loads((ROOT / "tools/audit/round9/D3/s3/pool.json").read_text())["pool"]
M21 = next(m for m in POOL if m["id"] == "M21")


def _load_module(name, source_text, file_path):
    mod = types.ModuleType(name)
    mod.__package__ = "custom_components.heatpump_optimizer"
    mod.__file__ = str(file_path)
    sys.modules[name] = mod
    try:
        exec(compile(source_text, str(file_path), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    return mod


def build_pair():
    import custom_components.heatpump_optimizer.ledger as real

    path = SRC / "ledger.py"
    src = path.read_text()
    assert M21["old"] in src, "anchor text not found -- module drifted since M21 was recorded"
    mutant_src = src.replace(M21["old"], M21["new"], 1)
    assert mutant_src != src
    mutant = _load_module("d3s3_catchup_mut_ledger", mutant_src, path)
    return real, mutant


def run(mod):
    ledger = mod.MonthlyLedger()
    when = datetime(2026, 3, 5, 12, 0, tzinfo=timezone.utc)
    ledger.add(when, "grid_import", kwh=10.0, sek=25.0)
    ledger.add(when, "grid_import", kwh=float("nan"), sek=5.0)
    round_tripped = mod.MonthlyLedger.from_dict(ledger.as_dict())
    month_key = mod.month_key(when)
    n_months_before = len(ledger.months)
    n_months_after = len(round_tripped.months)
    kwh_after = (
        round_tripped.months.get(month_key, {}).get("lines", {}).get("grid_import", {}).get("kwh")
    )
    return n_months_before, n_months_after, kwh_after


def main() -> int:
    real, mutant = build_pair()
    r_before, r_after, r_kwh = run(real)
    m_before, m_after, m_kwh = run(mutant)
    print(f"  real:   months_before={r_before} months_after={r_after} kwh_after={r_kwh!r}")
    print(f"  mutant: months_before={m_before} months_after={m_after} kwh_after={m_kwh!r}")
    differ = 1 if (r_after, r_kwh) != (m_after, m_kwh) else 0
    print(f"RESULT differ_months_after_reload={differ}/1")
    print("RESULT thread_factor=1.00 (numpy.isfinite only, no BLAS)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    ok = differ == 1 and r_after == 1 and r_kwh == 10.0 and m_after == 0
    print(f"RESULT verdict={'CONFIRMED' if ok else 'NOT-CONFIRMED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
