#!/usr/bin/env python3
"""D15-s3 enumerator: the universe of D15.md steps M7, M8 and M9 over one bundle.

One item per line, by name only: no bundle value, entity id, store key or
instant is printed (store documents by their ``store.DOMAINS`` name, rows by
index, days by their ordinal from the first row's local day).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/s3_enumerate.py --step M7 --bundle B
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/s3_enumerate.py --step M8 --bundle B
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/s3_enumerate.py --step M9 --bundle B

M7: every row check (each ranges over all ``cycle_rows``), every payload
snapshot, every self-test the manifest recorded, and the redispatched items.
M8: every anomaly ``m7_rowscan.py`` raises on the bundle (its ``ANOMALY``
lines), one per line, plus the redispatched items.
M9: every install-day the rows span (local days, the replay half's zone).
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import m7_rowscan as scan  # noqa: E402

REDISPATCHED = {
    "M7": ["redispatched:C1 the whole step (round 10 spot, no denominator)",
           "redispatched:C3 solve-time outliers re-checked at baseline"],
    "M8": ["redispatched:C2 the whole step (round 10 none, no denominator)",
           "redispatched:C4 anomaly reproduced by debug_replay --start/--end"],
    "M9": [],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=["M7", "M8", "M9"])
    ap.add_argument("--bundle", required=True, type=Path)
    a = ap.parse_args()
    bundle = scan.load(a.bundle)
    if a.step == "M7":
        for name in scan.ROW_CHECKS:
            print(f"rows:{name}")
        for i, _ in enumerate(bundle.get("payload_snapshots") or []):
            print(f"snapshot:{i}:action_vs_plan")
        for name in sorted((bundle.get("manifest") or {}).get("self_tests") or {}):
            print(f"self_test:{name}")
    elif a.step == "M8":
        for line in scan.anomalies(bundle, scan._download_config(a.bundle)):
            print(f"anomaly:{line}")
    else:
        for day in scan.install_days(bundle):
            print(f"install_day:{day}")
    for line in REDISPATCHED[a.step]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
