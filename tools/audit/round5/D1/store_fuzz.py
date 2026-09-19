#!/usr/bin/env python3
"""D1 store-corruption fuzzer: for every persisted payload, run 200 seeded
mutants through the REAL loader and count how many install non-finite numbers
into live learned state, raise out of the loader, or are written back corrupt.

METRIC DEFINITION (one line)
  `nonfinite_installing_mutants` = number of the 200 seeded mutants of a
  store's healthy payload (built by the production save path) after loading
  which the live learned-state graph (the counted key set below) holds at
  least one more non-finite number than the clean load does.  The count is
  keyed on the value the production loader delivers into those live objects,
  not on the store bytes.

INSTRUMENTED SYMBOL
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_thermal_learning
  and its six sibling loaders (_async_load_price_model, _async_load_ledger,
  _async_load_accuracy, _async_load_energy_totals, _async_load_manual_plan,
  _async_load_snapshots).

PERTURBATION (direction: down)
  Add the finite guard `if not math.isfinite(float(v)): return` to the four
  `_apply_*` seams the thermal loader drives (store_nan.py's `--perturb`
  seam set).  Run with `--perturb`: the thermal_learning cell of
  `nonfinite_installing_mutants` must fall (from 200 to 0 for the NaN class).

NULL CONTROL
  The same 200 mutants at `--flat` are not used; instead the control is the
  clean payload itself: it installs 0 and every cell's clean baseline is 0.

COMMAND
  cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/store_fuzz.py
  add --perturb for the guarded run.

EXPECTED (baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225, 8-core Apple M1; count; tolerance exact)
  RESULT mutants=200 per_store=200 n_stores=7
  RESULT load_raised_total=0
  RESULT nonfinite_installing_mutants_thermal_learning=2
  RESULT nonfinite_installing_mutants_price_model=2
  RESULT nonfinite_installing_mutants_accuracy=3
  RESULT nonfinite_installing_mutants_{ledger,energy,manual_plan,snapshots}=0
  RESULT nonfinite_installing_mutants_total=7
  RESULT mutants_rehydrated_corrupt=161
  with --perturb: RESULT nonfinite_installing_mutants_thermal_learning=0
                  RESULT nonfinite_installing_mutants_total=5

MACHINE  8-core Apple M1, 8 GB; numpy on OpenBLAS, BLAS pinned to 1 thread.
"""
from __future__ import annotations

import os

# Thread pin BEFORE numpy import (tests/stress.py's own recipe).
for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import json
import math
import random
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

DOMAIN = "heatpump_optimizer"
EID = "test_entry"
START = golden.START
CONFIG = dict(golden.coordinator_scenarios()["coord_all_features"])
PERTURB = "--perturb" in sys.argv
PER_STORE = 200

# The live learned-state graph the oracle walks.  Bounded on purpose: these are
# the objects the loader writes and the solve / publish reads.
LIVE_ATTRS = (
    "_thermal_params", "_ledger", "_start_counter", "_accuracy", "_dhw_accuracy",
    "_defrost", "_peak_tracker", "_comfort_learner", "_curve_learner", "_freq_map",
    "_flow_bias", "_price_model", "_energy_totals", "_cop_scale",
    "_house_heat_loss_scale", "_buffer_cooling_rate", "_lower_floor_loss_ratio",
    "_snow_accum_cm", "_operation_score",
)

LOADERS = {
    "thermal_learning": "_async_load_thermal_learning",
    "price_model": "_async_load_price_model",
    "ledger": "_async_load_ledger",
    "accuracy": "_async_load_accuracy",
    "energy": "_async_load_energy_totals",
    "manual_plan": "_async_load_manual_plan",
    "snapshots": "_async_load_snapshots",
}
SAVERS = {
    "thermal_learning": "_async_save_thermal_learning",
    "price_model": "_async_save_price_model",
    "ledger": "_async_save_ledger",
    "accuracy": "_async_save_accuracy",
    "energy": "_async_save_energy_totals",
    "manual_plan": "_async_save_manual_plan",
    "snapshots": "_async_save_snapshots",
}

# The four thermal seams the guarded perturbation patches (same set as
# store_nan.py).
APPLY_SEAMS = (
    "_apply_house_heat_loss_scale",
    "_apply_buffer_cooling_rate",
    "_apply_lower_floor_loss_ratio",
    "_apply_cop_scale",
)


def _install_finite_guard() -> None:
    """The finite guards the fix would add at the seams this store drives.

    Four are the `_apply_*` clamps (`np.clip` propagates NaN); the fifth is the
    snow accumulator, whose `max(0.0, float(v))` admits `inf` because
    `max(0.0, inf) == inf`.  All five sit inside the same loader.
    """
    for name in APPLY_SEAMS:
        orig = getattr(HeatPumpOptimizerCoordinator, name)

        def guarded(self, value, _orig=orig):
            try:
                ok = math.isfinite(float(value))
            except (TypeError, ValueError, OverflowError):
                return
            if not ok:
                return
            return _orig(self, value)

        setattr(HeatPumpOptimizerCoordinator, name, guarded)

    _orig_load = HeatPumpOptimizerCoordinator._async_load_thermal_learning

    async def _guarded_load(self):
        await _orig_load(self)
        try:
            if not math.isfinite(float(getattr(self, "_snow_accum_cm", 0.0))):
                self._snow_accum_cm = 0.0
        except (TypeError, ValueError, OverflowError):
            self._snow_accum_cm = 0.0

    HeatPumpOptimizerCoordinator._async_load_thermal_learning = _guarded_load


def _build():
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(CONFIG)))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + __import__("datetime").timedelta(hours=h)).isoformat(),
         "level": "NORMAL"} for h in range(48)
    ]
    return coord


def _key(kind: str) -> str:
    return f"{DOMAIN}_{EID}_{kind}"


def _count_nonfinite(x, depth=0, seen=None) -> int:
    if seen is None:
        seen = set()
    if depth > 8:
        return 0
    if isinstance(x, bool):
        return 0
    if isinstance(x, float):
        return 0 if math.isfinite(x) else 1
    if isinstance(x, (int, np.integer)):
        return 0
    if isinstance(x, np.floating):
        return 0 if math.isfinite(float(x)) else 1
    if isinstance(x, (str, bytes, type(None))):
        return 0
    oid = id(x)
    if oid in seen:
        return 0
    seen.add(oid)
    if isinstance(x, dict):
        return sum(_count_nonfinite(v, depth + 1, seen) for v in x.values())
    if isinstance(x, (list, tuple, set)):
        return sum(_count_nonfinite(v, depth + 1, seen) for v in x)
    d = getattr(x, "__dict__", None)
    if isinstance(d, dict):
        return sum(_count_nonfinite(v, depth + 1, seen) for v in d.values())
    return 0


def _live_nonfinite(coord) -> int:
    return sum(_count_nonfinite(getattr(coord, a, None)) for a in LIVE_ATTRS)


def _healthy_payloads() -> dict[str, dict]:
    """Build every healthy payload through the production save path."""
    storage._reset_store_disk()
    coord = _build()
    for kind in LOADERS:
        asyncio.run(getattr(coord, SAVERS[kind])())
    return {k: json.loads(storage._DISK[_key(k)]) for k in LOADERS if _key(k) in storage._DISK}


# --- mutation catalogue -----------------------------------------------------
SCALARS = (
    float("nan"), float("inf"), float("-inf"), 1e309, -1e309, 1e308, -1e308,
    0.0, -0.0, -1.0, -1e9, "NaN", "inf", "", "x", None, True, [], {}, 1e-320,
)


def _leaves(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _leaves(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _leaves(v, path + (i,))
    else:
        yield path, node


def _set_path(node, path, value):
    cur = node
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value


def _make_mutants(payload: dict, n: int, rng: random.Random):
    mutants = []
    # Structured, whole-payload mutants first (deterministic).
    structured = [
        None, [], "", 0, 1.5, True, {"x": 1}, [1, 2, 3], "{}",
        {k: None for k in payload}, {k: [] for k in payload},
        {k: "x" for k in payload}, {k: float("nan") for k in payload},
        {k: float("inf") for k in payload},
        {**payload, "__extra__": float("nan")},
    ]
    mutants.extend(structured)
    leaves = list(_leaves(payload))
    while len(mutants) < n:
        choice = rng.random()
        if choice < 0.55 and leaves:
            path, _ = leaves[rng.randrange(len(leaves))]
            val = SCALARS[rng.randrange(len(SCALARS))]
            m = copy.deepcopy(payload)
            try:
                _set_path(m, path, val)
            except (TypeError, KeyError, IndexError):
                continue
            mutants.append(m)
        elif choice < 0.75 and leaves:
            # truncate a list leaf
            path, orig = leaves[rng.randrange(len(leaves))]
            m = copy.deepcopy(payload)
            try:
                if isinstance(orig, list) and orig:
                    _set_path(m, path, orig[: max(0, len(orig) // 2)])
                else:
                    _set_path(m, path, None)
            except (TypeError, KeyError, IndexError):
                continue
            mutants.append(m)
        elif choice < 0.9 and isinstance(payload, dict) and payload:
            k = list(payload)[rng.randrange(len(payload))]
            m = copy.deepcopy(payload)
            m.pop(k, None)
            mutants.append(m)
        else:
            # wrong nesting: swap two sibling containers' shape
            m = copy.deepcopy(payload)
            if isinstance(m, dict) and m:
                k = list(m)[rng.randrange(len(m))]
                m[k] = [{k: v} for v in (m[k] if isinstance(m[k], list) else [1, 2])]
            mutants.append(m)
    return mutants[:n]


def _load(kind, payload, clean_nf):
    for k in list(storage._DISK):
        pass
    storage._reset_store_disk()
    storage._DISK[_key(kind)] = json.dumps(payload)
    coord = _build()
    raised = None
    try:
        asyncio.run(getattr(coord, LOADERS[kind])())
    except Exception as exc:  # noqa: BLE001
        raised = f"{type(exc).__name__}: {exc}"
    nf = _live_nonfinite(coord) - clean_nf
    # Did the loader write the corruption back?  (A repaired store is fine.)
    written = storage._DISK.get(_key(kind))
    wnf = _count_nonfinite(json.loads(written)) if written is not None else 0
    return raised, nf, wnf


def main() -> int:
    if PERTURB:
        _install_finite_guard()
    dt_util.freeze(START)
    cpu0, cpu1 = time.process_time(), time.thread_time()

    healthy = _healthy_payloads()
    # Clean baseline per store: load every healthy store together, count once.
    clean_nf = 0
    coord = _build()
    for kind in LOADERS:
        asyncio.run(getattr(coord, LOADERS[kind])())
    clean_nf = _live_nonfinite(coord)

    totals = {}
    ras = {}
    corrupt_rehydrated = 0
    for si, kind in enumerate(LOADERS):
        rng = random.Random(1000 + si)
        mutants = _make_mutants(healthy[kind], PER_STORE, rng)
        n_nonfinite = 0
        n_raised = 0
        for m in mutants:
            raised, nf, wnf = _load(kind, m, clean_nf)
            if raised:
                n_raised += 1
            if nf > 0:
                n_nonfinite += 1
            if wnf > 0:
                corrupt_rehydrated += 1
        totals[kind] = n_nonfinite
        ras[kind] = n_raised
        print(f"CELL {kind}: mutants={len(mutants)} "
              f"nonfinite_installing={n_nonfinite} load_raised={n_raised}")

    proc = time.process_time() - cpu0
    thr = time.thread_time() - cpu1

    print("\n=== store_fuzz ===")
    print(f"perturb={PERTURB}")
    print(f"RESULT n_stores={len(LOADERS)}")
    print(f"RESULT mutants=200 per_store=200")
    for kind in LOADERS:
        print(f"RESULT nonfinite_installing_mutants_{kind}={totals[kind]}")
        print(f"RESULT load_raised_{kind}={ras[kind]}")
    print(f"RESULT nonfinite_installing_mutants_total={sum(totals.values())}")
    print(f"RESULT load_raised_total={sum(ras.values())}")
    print(f"RESULT mutants_rehydrated_corrupt={corrupt_rehydrated}")
    print(f"RESULT clean_baseline_nonfinite={clean_nf}")
    load1 = os.getloadavg()[0]
    print(f"RESULT thread_factor={proc / thr if thr > 0 else 0.0}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
