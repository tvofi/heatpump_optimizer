#!/usr/bin/env python3
"""Verifier V2, D3-s3-04 (mutant M24, dhw_learning.py:379
DhwProfileLearner.async_fold_draw_stats).

Metric (own): with a real DhwProfileLearner (built through the real
coordinator, FakeHass/FakeEntry per tests/harness.py -- the README's reuse
table), the folded open-occurrence energy after one beyond-standby interval
(previous_temp=60, temp_drop=4.0, dt_h=1.0), comparing real vs the recorded
mutant M24 (dhw_learning.py:379's `if self._external_heat_active():` replaced
by `if False:`) in memory.
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
  tools/audit/round9/D3/verify-v2/catchup_m24.py
Expected: RESULT differ_fold=0/1 (no wood burn: the guard reads False on
  both sides, so real and mutant agree); RESULT differ_fold_woodburn=1/1
  (wood burn forced: real skips the fold at 0.0, the mutant folds it
  anyway at >0 -- the seam only shows under a predicate no gate check ever
  drives to True).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud box G1-V2,
  4 vCPU Linux, CPython 3.14.0rc2.
Instrumented symbol:
  custom_components.heatpump_optimizer.dhw_learning:DhwProfileLearner.async_fold_draw_stats.
Perturbation: the recorded mutant M24 applied in memory to a second copy of
  the module (source text patched, then exec'd into its own namespace); the
  coordinator's ``_dhw_learner`` for each side is instantiated straight from
  its own patched/unpatched module class.
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
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from harness import FakeEntry, FakeHass  # noqa: E402

POOL = json.loads((ROOT / "tools/audit/round9/D3/s3/pool.json").read_text())["pool"]
M24 = next(m for m in POOL if m["id"] == "M24")


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
    import custom_components.heatpump_optimizer.dhw_learning as real

    path = SRC / "dhw_learning.py"
    src = path.read_text()
    assert M24["old"] in src, "anchor text not found -- module drifted since M24 was recorded"
    mutant_src = src.replace(M24["old"], M24["new"], 1)
    assert mutant_src != src
    mutant = _load_module("d3s3_catchup_mut_dhw_learning", mutant_src, path)
    return real, mutant


def _make_coord():
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

    coord = Coord(FakeHass(), FakeEntry(
        data={"tibber_token": "x", "weather_entity": "weather.home",
              "dhw_tank_volume": 200.0},
    ))
    coord._thermal_params.dhw_enabled = True
    return coord


def fold_energy(dhw_learning_mod, force_external_heat=False):
    coord = _make_coord()
    learner = coord._dhw_learner
    # Swap in the class from the module under test, and re-point the bound
    # method so async_fold_draw_stats runs the module's own code on the same
    # real, fully-constructed learner instance.
    learner.async_fold_draw_stats = types.MethodType(
        dhw_learning_mod.DhwProfileLearner.async_fold_draw_stats.__wrapped__
        if hasattr(dhw_learning_mod.DhwProfileLearner.async_fold_draw_stats, "__wrapped__")
        else dhw_learning_mod.DhwProfileLearner.async_fold_draw_stats,
        learner,
    )
    learner.cooling_rate = 0.3
    if force_external_heat:
        learner._external_heat_active = lambda: True
    asyncio.run(learner.async_fold_draw_stats(
        datetime(2026, 2, 1, 7, 0, tzinfo=timezone.utc), 60.0, 4.0, 1.0,
    ))
    return learner.draw_stats._open_kwh


def main() -> int:
    real, mutant = build_pair()

    r0 = fold_energy(real, force_external_heat=False)
    m0 = fold_energy(mutant, force_external_heat=False)
    r1 = fold_energy(real, force_external_heat=True)
    m1 = fold_energy(mutant, force_external_heat=True)

    print(f"  no-wood-burn:  real={r0!r} mutant={m0!r}")
    print(f"  wood-burn:     real={r1!r} mutant={m1!r}")

    differ0 = 0 if r0 == m0 else 1
    differ1 = 0 if r1 == m1 else 1
    print(f"RESULT differ_fold={differ0}/1")
    print(f"RESULT differ_fold_woodburn={differ1}/1")
    print("RESULT thread_factor=1.00 (no BLAS on this construction/call path)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")

    # This harness measures reachability of the guard's seam directly, not
    # the suite's own checks (that half of the claim -- that no gate check
    # ever asserts a positive fold, so the mutant M24 as well as this
    # stronger woodburn-arm difference go unnoticed -- rests on the finder's
    # recorded prescreen kill count, cited rather than re-run here per the
    # no-heavy-D3-re-runs rule).
    # Non-wood-burn arm: the guard is False on both sides (no contamination
    # to skip), so real and mutant must agree -- and do (differ0 == 0).
    # Wood-burn arm: real skips the fold (0.0), the mutant folds it anyway
    # (> 0), reproducing the claimed mechanism -- the guard's deletion is
    # only observable when external heat is active, which no gate check
    # drives, matching the finder's own null_control direction.
    ok = differ0 == 0 and differ1 == 1 and r1 == 0.0 and m1 > 0.0
    print(f"RESULT verdict={'CONFIRMED-SEAM-REACHABLE' if ok else 'NOT-CONFIRMED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
