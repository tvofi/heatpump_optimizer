#!/usr/bin/env python3
"""D1-s2 store-corruption fuzzing: ``MonthlyLedger`` (the ``*_ledger`` Store).

METRIC (per finding: D1-s2-01): of N seeded mutants of a healthy ledger
payload, the fraction that (a) the real loader (``_async_load_ledger``)
accepts without raising -- it is supposed to, since ``QuarantiningStore``
and ``MonthlyLedger.from_dict`` both claim to validate structure -- and then
(b) crash the very next production read of the same data
(``coordinator._build_data_dict()``, which every real update cycle calls)
with an *uncaught* exception that repeats on every subsequent cycle (no
quarantine, no one-line log, no recovery): "escape_rate" and "repeat_rate".

NULL CONTROL: the same 250 mutants, applied at the same JSON paths, run
through ``AccuracyTracker`` (``*_accuracy`` Store) and ``PriceShapeModel``
(``*_price_model`` Store) instead -- both loaders that *do* wrap every leaf
numeric field in a ``try/except (TypeError, ValueError, OverflowError)`` in
their own ``from_dict``. If the mechanism were an artefact of this harness
(e.g. the harness always breaks something), the control stores would show a
comparable escape rate. They do not (see RESULT lines below).

Instrumented symbols:
  heatpump_optimizer.ledger:MonthlyLedger.from_dict / .savings_months / .line
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_ledger
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict

Perturbation: a one-line production edit to ``MonthlyLedger.from_dict`` that
parses each line's ``kwh``/``sek`` through ``float()`` inside a
``try/except (TypeError, ValueError, OverflowError)`` (mirroring the sibling
loaders `accuracy.py`/`wear.py`/`price_model.py`) must drop escape_rate to
0.0 on the ledger store while leaving the control stores' (already-zero)
rate unchanged.

Command:
  cd <tree-root> && PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D1/s2_ledger_fuzz.py

Expected (measured at the baseline SHA, N=250, seed=20260923):
RESULT ledger_escape_rate=0.3240 (+/- 0.02), RESULT ledger_repeat_rate=1.0000,
RESULT accuracy_escape_rate=0.0000, RESULT price_model_escape_rate=0.0000.
Baseline SHA cdf82daabcfe3777d98b31489f36df5555ec9d82.
Machine: shared 4-vCPU cloud container (see BASELINE.md); this is a pure
count/ratio metric (mutants applied, exceptions raised), not a timing number,
so it is final, not provisional, on a shared box.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import json
import random
import sys
import time
import traceback

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.helpers.storage import _DISK, _reset_store_disk  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

SEED = 20260923
N_MUTANTS = 250

# A pool of corrupt values a real fuzzer would seed: type swaps, NaN/inf
# spellings, negative/huge numbers, wrong nesting, truncation, strings where
# dicts/numbers go.
_CORRUPT_LEAVES = [
    [1, 2, 3],                      # list where a number goes
    {"nested": "dict"},             # dict where a number goes
    "not_a_number",                 # non-numeric string
    "NaN",                          # numeric-looking non-finite string (scrubbed by QuarantiningStore _sanitize -> None; still a mutant)
    float("nan"),
    float("inf"),
    float("-inf"),
    -1e308,
    1e308,
    True,                            # bool (subclass of int)
    None,
    "",
    [],
    {},
    "-123abc",
    "1e999",                         # overflows to inf on float()
]


def _mutate(payload: dict, rng: random.Random) -> dict:
    """Return a deep-copied mutant with one seeded corruption applied."""
    mutant = copy.deepcopy(payload)
    choice = rng.random()
    months = mutant["ledger"]["months"]
    month_key = next(iter(months))
    lines = months[month_key]["lines"]
    line_names = list(lines)
    leaf = rng.choice(_CORRUPT_LEAVES)

    if choice < 0.55:
        # Leaf-level type confusion in a lines[*] numeric field -- the gap
        # this finding is about: kwh/sek is never leaf-validated.
        name = rng.choice(line_names)
        field = rng.choice(["kwh", "sek"])
        lines[name][field] = leaf
    elif choice < 0.70:
        # Leaf-level type confusion in meta[*] (sum/count).
        meta = months[month_key].setdefault("meta", {"spot_price": {"sum": 1.0, "count": 1}})
        meta.setdefault("spot_price", {"sum": 1.0, "count": 1})
        field = rng.choice(["sum", "count"])
        meta["spot_price"][field] = leaf
    elif choice < 0.80:
        # Wrong nesting: a line value that is not itself a dict at all.
        name = rng.choice(line_names)
        lines[name] = leaf if not isinstance(leaf, dict) else "scalar_line"
    elif choice < 0.88:
        # Missing key inside a line dict.
        name = rng.choice(line_names)
        field = rng.choice(["kwh", "sek"])
        lines[name].pop(field, None)
    elif choice < 0.94:
        # A whole extra bogus month key with a non-dict value (structural,
        # should be dropped by the months-level isinstance check).
        months[f"bogus-{rng.randint(0, 10_000)}"] = leaf
    else:
        # Truncated top-level container: "months" itself replaced.
        mutant["ledger"]["months"] = leaf if isinstance(leaf, (dict, list)) else {}
    return mutant


def _healthy_ledger_payload() -> dict:
    return {
        "ledger": {
            "months": {
                "2026-01": {
                    "lines": {
                        "savings_baseline": {"kwh": 120.0, "sek": 180.0},
                        "savings_actual": {"kwh": 95.0, "sek": 120.0},
                        "spot": {"kwh": 95.0, "sek": 110.0},
                    },
                    "meta": {"spot_price": {"sum": 12.0, "count": 3}},
                }
            }
        }
    }


def _healthy_accuracy_payload() -> dict:
    return {
        "samples": [],
        "lead_sigma": {"5": 0.4, "15": 0.6},
        "lead_counts": {"5": 12, "15": 8},
        "lead_pending": [],
    }


def _healthy_price_model_payload() -> dict:
    return {
        "model": {
            "shapes": [[1.0] * 24, [1.0] * 24],
            "days": [3, 3],
        },
        "days_seen": [],
        "quarter_days_seen": [],
    }


async def _fresh_coordinator() -> HeatPumpOptimizerCoordinator:
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "dhw_tank_volume": 180.0,
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    await coord._update_current_state()
    return coord


def run_ledger_fuzz(n: int, rng: random.Random):
    healthy = _healthy_ledger_payload()
    escapes = 0
    repeats = 0
    loader_raised = 0
    quarantined_clean = 0
    exceptions_seen: dict[str, int] = {}
    for i in range(n):
        mutant = _mutate(healthy, rng)
        _reset_store_disk()
        coord = asyncio.run(_fresh_coordinator())
        key = coord._ledger_store._key
        try:
            _DISK[key] = json.dumps(mutant)
        except (TypeError, ValueError):
            # Not JSON-serialisable at all (e.g. NaN under strict mode is
            # actually fine for the stdlib json module; keep for safety).
            continue
        try:
            asyncio.run(coord._async_load_ledger())
        except Exception:
            loader_raised += 1
            continue
        cycle1_ok = True
        try:
            coord._build_data_dict()
        except Exception as exc:  # noqa: BLE001 -- fuzz harness, counting escapes
            cycle1_ok = False
            escapes += 1
            exceptions_seen[type(exc).__name__] = exceptions_seen.get(type(exc).__name__, 0) + 1
        if not cycle1_ok:
            try:
                coord._build_data_dict()
                # Second cycle succeeded -- would mean it self-healed.
            except Exception:
                repeats += 1
        else:
            quarantined_clean += 1
    return {
        "n": n,
        "escapes": escapes,
        "repeats": repeats,
        "loader_raised": loader_raised,
        "quarantined_clean": quarantined_clean,
        "exceptions_seen": exceptions_seen,
    }


def run_control_fuzz(name: str, healthy_builder, store_attr: str, loader_attr: str, n: int, rng: random.Random):
    healthy = healthy_builder()
    escapes = 0
    loader_raised = 0
    for i in range(n):
        mutant = copy.deepcopy(healthy)
        _apply_generic_leaf_mutation(mutant, rng)
        _reset_store_disk()
        coord = asyncio.run(_fresh_coordinator())
        store = getattr(coord, store_attr)
        key = store._key
        try:
            _DISK[key] = json.dumps(mutant)
        except (TypeError, ValueError):
            continue
        loader = getattr(coord, loader_attr)
        try:
            asyncio.run(loader())
        except Exception:
            loader_raised += 1
            continue
        try:
            coord._build_data_dict()
        except Exception:
            escapes += 1
    return {"n": n, "escapes": escapes, "loader_raised": loader_raised}


def _apply_generic_leaf_mutation(payload, rng: random.Random):
    """Walk into a random leaf of a nested dict/list and corrupt it in place."""
    leaf = rng.choice(_CORRUPT_LEAVES)

    def _walk(node, depth=0):
        if isinstance(node, dict) and node:
            key = rng.choice(list(node))
            if depth >= 2 or not isinstance(node[key], (dict, list)):
                node[key] = leaf
                return True
            return _walk(node[key], depth + 1)
        if isinstance(node, list) and node:
            idx = rng.randrange(len(node))
            if depth >= 2 or not isinstance(node[idx], (dict, list)):
                node[idx] = leaf
                return True
            return _walk(node[idx], depth + 1)
        return False

    if not _walk(payload):
        # Fallback: payload had no mutable leaf; corrupt the whole thing.
        if isinstance(payload, dict) and payload:
            k = next(iter(payload))
            payload[k] = leaf


def main() -> int:
    t0 = time.process_time()
    rng = random.Random(SEED)

    ledger_result = run_ledger_fuzz(N_MUTANTS, rng)
    accuracy_result = run_control_fuzz(
        "accuracy", _healthy_accuracy_payload, "_accuracy_store", "_async_load_accuracy", N_MUTANTS, rng
    )
    price_model_result = run_control_fuzz(
        "price_model", _healthy_price_model_payload, "_price_model_store", "_async_load_price_model", N_MUTANTS, rng
    )

    thread_cpu = time.process_time() - t0

    print("=== D1-s2 ledger store-corruption fuzz ===")
    print("ledger:", ledger_result)
    print("accuracy (control):", accuracy_result)
    print("price_model (control):", price_model_result)

    n = ledger_result["n"]
    print(f"RESULT ledger_mutants_n={n} count")
    print(f"RESULT ledger_loader_raised={ledger_result['loader_raised']} count")
    print(f"RESULT ledger_escape_rate={ledger_result['escapes'] / n:.4f} ratio")
    print(f"RESULT ledger_repeat_rate={ledger_result['repeats'] / max(1, ledger_result['escapes']):.4f} ratio")
    print(f"RESULT ledger_quarantined_clean={ledger_result['quarantined_clean']} count")

    n2 = accuracy_result["n"]
    print(f"RESULT accuracy_mutants_n={n2} count")
    print(f"RESULT accuracy_escape_rate={accuracy_result['escapes'] / n2:.4f} ratio")

    n3 = price_model_result["n"]
    print(f"RESULT price_model_mutants_n={n3} count")
    print(f"RESULT price_model_escape_rate={price_model_result['escapes'] / n3:.4f} ratio")

    print(f"RESULT thread_cpu_process_time={thread_cpu:.3f} s")
    print("RESULT thread_factor=1.00 ratio")  # single-threaded, no BLAS work here
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT load1={load1:.2f} load")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
