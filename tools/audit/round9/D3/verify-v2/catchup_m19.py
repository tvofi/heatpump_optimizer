#!/usr/bin/env python3
"""Verifier V2, D3-s3-02 (mutant M19, dhw_draws.py:136 DrawStats.from_dict).

Metric (own): among a representative set of ``open_kwh`` values on the
DrawStats.as_dict()/from_dict() round trip (0.0, 1.5, 1e9, -3.0, float("nan"),
float("inf")), the count on which the recorded mutant (M19: ``stats._open_kwh
= (0.0)`` in place of ``max(0.0, float(data.get("open_kwh", 0.0)))``) and
unmutated production disagree on the restored ``_open_kwh``.
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
  tools/audit/round9/D3/verify-v2/catchup_m19.py
Expected: RESULT differ=2/6 (only the two positive-finite inputs, 1.5 and
  1e9, differ; 0.0/-3.0/nan/inf already read 0.0 in production via the same
  clamp/finite check, so the mutant is indistinguishable there).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud box G1-V2,
  4 vCPU Linux, CPython 3.14.0rc2.
Instrumented symbol:
  custom_components.heatpump_optimizer.dhw_draws:DrawStats.from_dict.
Perturbation: the recorded mutant M19 applied in memory to a second copy of
  the module (source text patched, then exec'd into its own namespace).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import time
import types
import resource
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

POOL = json.loads((ROOT / "tools/audit/round9/D3/s3/pool.json").read_text())["pool"]
M19 = next(m for m in POOL if m["id"] == "M19")


def _load_module(name: str, source_text: str, file_path: Path) -> types.ModuleType:
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
    import custom_components.heatpump_optimizer.dhw_draws as real

    path = SRC / "dhw_draws.py"
    src = path.read_text()
    assert M19["old"] in src, "anchor text not found -- module drifted since M19 was recorded"
    mutant_src = src.replace(M19["old"], M19["new"], 1)
    assert mutant_src != src
    mutant = _load_module("d3s3_catchup_mut_dhw_draws", mutant_src, path)
    return real, mutant


VALUES = [0.0, 1.5, 1.0e9, -3.0, float("nan"), float("inf")]


def restored_open_kwh(mod, open_kwh):
    data = {"reservoirs": {}, "open_label": "morning", "open_date": "2026-02-01",
            "open_kwh": open_kwh}
    stats = mod.DrawStats.from_dict(data)
    return stats._open_kwh


def main() -> int:
    real, mutant = build_pair()
    differ = 0
    detail = []
    for v in VALUES:
        r = restored_open_kwh(real, v)
        m = restored_open_kwh(mutant, v)
        same = (r == m) or (r != r and m != m)  # nan == nan is False
        if not same:
            differ += 1
        detail.append((v, r, m))
    for v, r, m in detail:
        print(f"  input open_kwh={v!r}: real={r!r} mutant={m!r}")
    print(f"RESULT differ={differ}/{len(VALUES)} open_kwh_inputs")
    print("RESULT thread_factor=1.00 (no numpy call on this path)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    positive_case = next(d for d in detail if d[0] == 1.5)
    ok = differ == 2 and positive_case[1] == 1.5 and positive_case[2] == 0.0
    print(f"RESULT verdict={'CONFIRMED' if ok else 'NOT-CONFIRMED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
