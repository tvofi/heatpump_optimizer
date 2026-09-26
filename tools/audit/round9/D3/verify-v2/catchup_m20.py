#!/usr/bin/env python3
"""Verifier V2, D3-s3-05 (mutant M20, legionella.py:453 LegionellaGuard._drive_switch).

Metric (own): with a real LegionellaGuard built the same way tests/guard_pins.py
builds one (a real DisinfectionSwitch, no owned/failed switch, so five
observe-mode cycles with no state change), the number of
``ir.async_delete_issue``/``create_issue`` calls the write-failed-notice memo
suppresses on cycles 2-5, real vs the recorded mutant M20 (the
``if switch.failed == self.write_failed_notice: return`` guard replaced by
``if False:``) applied in memory.
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
  tools/audit/round9/D3/verify-v2/catchup_m20.py
Expected: RESULT real_calls=0/5 mutant_calls=5/5 differ=1.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud box G1-V2,
  4 vCPU Linux, CPython 3.14.0rc2.
Instrumented symbol:
  custom_components.heatpump_optimizer.legionella:LegionellaGuard._drive_switch.
Perturbation: the recorded mutant M20 applied in memory to a second copy of
  the module (source text patched, then exec'd into its own namespace);
  ``ir.async_delete_issue`` is counted via an attribute-swap stub, never a
  suite run.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import sys
import types
import resource
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from harness import FakeHass  # noqa: E402

POOL = json.loads((ROOT / "tools/audit/round9/D3/s3/pool.json").read_text())["pool"]
M20 = next(m for m in POOL if m["id"] == "M20")


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
    import custom_components.heatpump_optimizer.legionella as real

    path = SRC / "legionella.py"
    src = path.read_text()
    assert M20["old"] in src, "anchor text not found -- module drifted since M20 was recorded"
    mutant_src = src.replace(M20["old"], M20["new"], 1)
    assert mutant_src != src
    mutant = _load_module("d3s3_catchup_mut_legionella", mutant_src, path)
    return real, mutant


def count_registry_calls(legionella_mod, n_cycles=5):
    from heatpump_optimizer.thermal_model import ThermalParameters
    from heatpump_optimizer.disinfection import DisinfectionSwitch

    calls = []
    orig_create_issue = legionella_mod.create_issue
    orig_delete_issue = legionella_mod.ir.async_delete_issue
    legionella_mod.create_issue = lambda *a, **k: calls.append(("create", a[2] if len(a) > 2 else a))
    legionella_mod.ir.async_delete_issue = lambda *a, **k: calls.append(("delete", a[2] if len(a) > 2 else a))
    try:
        params = ThermalParameters()
        params.dhw_enabled = True
        disinfect = DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None)
        guard = legionella_mod.LegionellaGuard(
            FakeHass(), "catchup-m20", params, {},
            action=lambda: {}, disinfect=disinfect, dhw_blocked=lambda: False,
        )
        for _ in range(n_cycles):
            asyncio.run(guard._drive_switch(False))
    finally:
        legionella_mod.create_issue = orig_create_issue
        legionella_mod.ir.async_delete_issue = orig_delete_issue
    write_failed_calls = [c for c in calls if "write_failed" in str(c[1])]
    return len(write_failed_calls)


def main() -> int:
    real, mutant = build_pair()
    real_calls = count_registry_calls(real)
    mutant_calls = count_registry_calls(mutant)
    print(f"  real_calls={real_calls}/5  mutant_calls={mutant_calls}/5")
    differ = 1 if real_calls != mutant_calls else 0
    print(f"RESULT real_calls={real_calls}/5")
    print(f"RESULT mutant_calls={mutant_calls}/5")
    print(f"RESULT differ={differ}")
    print("RESULT thread_factor=1.00 (no BLAS on this path)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    ok = real_calls == 0 and mutant_calls == 5 and differ == 1
    print(f"RESULT verdict={'CONFIRMED' if ok else 'NOT-CONFIRMED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
