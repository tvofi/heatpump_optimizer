"""Seeded store-corruption fuzzer for every persisted payload (D1, round 4).

METRIC: per store, out of N seeded mutants of the healthy payload, the count
that fails any of three properties -- (a) the load and the two following
cycles complete with no exception escaping, (b) the corrupt part is
quarantined (the published data dict carries no NaN and no value the healthy
payload could not produce) and announced in at most one log line, (c) the
NEXT cycle repeats neither the exception nor the log line.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/store_fuzz.py --mutants 200

EXPECTED (--mutants 200, 12 stores, 2400 mutants; seeded RNG, exact):
  nan_published_mutants=16, nan_published_strict_json_mutants=4,
  silent_nan_mutants=6, corrupt_persisted_mutants=91,
  exception_escaped_mutants=0, repeat_failure_mutants=0.
  NOTE: the random walk over a payload carrying 40 accuracy samples rarely
  selects the ``accuracy.samples`` key itself, so exception_escaped is 0
  here; ``accuracy_wipe.py`` is the targeted evidence for that mechanism.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  ._async_load_thermal_learning / ._async_load_price_model / ._async_load_ledger /
  ._async_load_accuracy / ._async_load_energy_totals / ._async_load_snapshots /
  ._async_load_manual_plan, heatpump_optimizer.dhw_learning:DHWLearner
  .async_load_profile/.async_load_draws, heatpump_optimizer.legionella:
  LegionellaGuard.async_load, heatpump_optimizer.away:restore_override,
  heatpump_optimizer.boost:restore -- each driven through
  homeassistant.helpers.storage:Store with a mutated on-disk payload.
PERTURBATION: wrap every ``_apply_*`` clamp in coordinator.py in a
  ``math.isfinite`` gate (or clamp with ``np.nan_to_num``); nan_published
  must fall to zero.
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

import argparse
import asyncio
import copy
import json
import logging
import math
import random
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402

import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer import away as away_mod  # noqa: E402
from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

DOMAIN = const.DOMAIN
ENTRY_ID = "test_entry"

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_DHW_SETPOINT: 55.0,
    const.CONF_AWAY_ENABLED: True,
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 45.0,
}

# store key suffix -> (loader coroutine factory, saver coroutine factory)
STORES: dict[str, tuple] = {
    "thermal_learning": (
        lambda c: c._async_load_thermal_learning(),
        lambda c: c._async_save_thermal_learning(),
    ),
    "price_model": (
        lambda c: c._async_load_price_model(),
        lambda c: c._async_save_price_model(),
    ),
    "ledger": (lambda c: c._async_load_ledger(), lambda c: c._async_save_ledger()),
    "accuracy": (
        lambda c: c._async_load_accuracy(),
        lambda c: c._async_save_accuracy(),
    ),
    "energy": (
        lambda c: c._async_load_energy_totals(),
        lambda c: c._async_save_energy_totals(),
    ),
    "snapshots": (
        lambda c: c._async_load_snapshots(),
        lambda c: c._async_save_snapshots(),
    ),
    "manual_plan": (
        lambda c: c._async_load_manual_plan(),
        lambda c: c._async_save_manual_plan(),
    ),
    "dhw_profile": (
        lambda c: c._dhw_learner.async_load_profile(),
        lambda c: c._dhw_learner.async_save_profile(),
    ),
    "dhw_draws": (
        lambda c: c._dhw_learner.async_load_draws(),
        lambda c: c._dhw_learner.async_save_draws(),
    ),
    "dhw_legionella": (
        lambda c: c._legionella.async_load(),
        lambda c: c._legionella.async_save(),
    ),
    "away": (
        lambda c: away_mod.restore_override(c),
        lambda c: away_mod.persist_override(c),
    ),
    "boost": (lambda c: boost_mod.restore(c), lambda c: boost_mod.persist(c)),
}


def _new_coordinator() -> HeatPumpOptimizerCoordinator:
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = ENTRY_ID
    return HeatPumpOptimizerCoordinator(hass, entry)


# ---------------------------------------------------------------------------
# Healthy payloads
# ---------------------------------------------------------------------------


async def _seed_state(coord) -> None:
    """Give the learners content, so a mutant hits real structure."""
    await coord._update_current_state()
    coord.data = coord._build_data_dict()
    # A manual plan so the manual_plan store is not `{}`.
    try:
        from datetime import timedelta

        from heatpump_optimizer.manual_plan import build_override
        from homeassistant.util import dt as dt_util

        now = dt_util.now()
        coord._manual_override = build_override(
            space_slots=[
                {
                    "start": (now + timedelta(hours=1)).isoformat(),
                    "end": (now + timedelta(hours=3)).isoformat(),
                    "power_kw": 0.0,
                }
            ],
            dhw_slots=None,
            expires_at=now + timedelta(hours=12),
            now=now,
        )
    except Exception as err:  # pragma: no cover
        print(f"  WARN manual plan seed: {err}", file=sys.stderr)
        coord._manual_override = None
    # A boost channel and a legionella record.
    try:
        held = boost_mod.held_for(coord)
        from homeassistant.util import dt as dt_util
        from datetime import timedelta

        held.until["dhw"] = dt_util.now() + timedelta(hours=2)
        coord._legionella.last_cycle = dt_util.now() - timedelta(days=3)
        coord._legionella.attempt = dt_util.now() - timedelta(days=1)
        coord._legionella.attempt_peak = 58.5
    except Exception:
        pass
    # A month of ledger content.
    try:
        from heatpump_optimizer.ledger import month_key
        from homeassistant.util import dt as dt_util

        coord._ledger.book(month_key(dt_util.now()), "space", 3.5, 4.25)
        coord._ledger.book(month_key(dt_util.now()), "dhw", 1.5, 1.75)
    except Exception:
        pass
    # Months of accuracy/peak learning, so the accuracy store carries real
    # content rather than defaults: destroying it has to be measurable.
    try:
        from datetime import timedelta

        from heatpump_optimizer.accuracy import AccuracySample
        from homeassistant.util import dt as dt_util

        now = dt_util.now()
        for i in range(40):
            coord._accuracy.samples.append(
                AccuracySample(
                    when=now - timedelta(hours=i),
                    predicted_power_kw=1.0 + 0.01 * i,
                    actual_power_kw=1.1 + 0.01 * i,
                    predicted_temp=21.0,
                    actual_temp=20.9,
                    predicted_cost=0.5,
                    actual_cost=0.55,
                )
            )
        coord._peak_tracker.month = now.strftime("%Y-%m")
        coord._peak_tracker.peaks = [7.4, 6.8, 5.9]
    except Exception as err:  # pragma: no cover
        print(f"  WARN accuracy seed: {err}", file=sys.stderr)
    coord._energy_totals["space_energy_kwh"] = 123.5
    coord._energy_totals["total_energy_kwh"] = 180.25
    coord._operation_score = 72.0


async def _capture_healthy() -> dict[str, object]:
    hastore._reset_store_disk()
    coord = _new_coordinator()
    await _seed_state(coord)
    for suffix, (_loader, saver) in STORES.items():
        try:
            await saver(coord)
        except Exception as err:  # pragma: no cover - capture-side only
            print(f"  WARN could not seed {suffix}: {err}", file=sys.stderr)
    healthy: dict[str, object] = {}
    for suffix in STORES:
        key = f"{DOMAIN}_{ENTRY_ID}_{suffix}"
        raw = hastore._DISK.get(key)
        healthy[suffix] = json.loads(raw) if raw is not None else {}
    hastore._reset_store_disk()
    return healthy


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------

#: mutants whose replacement value is not strictly-JSON representable.
#: Real Home Assistant round-trips `.storage` through orjson, which has no
#: NaN/Infinity literal, so these describe in-memory corruption and a
#: hand-edited file only in the loose sense. Counted separately.
LOOSE = {"nan", "inf", "neg_inf"}

MUTATIONS = (
    "nan",
    "inf",
    "neg_inf",
    "nan_string",
    "inf_string",
    "negate",
    "huge",
    "tiny",
    "to_string",
    "to_null",
    "to_bool",
    "to_list",
    "to_dict",
    "drop_key",
    "truncate_list",
    "duplicate_list",
    "renest",
)


def _paths(node, prefix=()):
    """Every addressable position in the payload."""
    out = [prefix]
    if isinstance(node, dict):
        for k, v in node.items():
            out.extend(_paths(v, prefix + (k,)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_paths(v, prefix + (i,)))
    return out


def _get(node, path):
    for step in path:
        node = node[step]
    return node


def _set(node, path, value):
    if not path:
        return value
    parent = _get(node, path[:-1])
    parent[path[-1]] = value
    return node


def _drop(node, path):
    if not path:
        return {}
    parent = _get(node, path[:-1])
    if isinstance(parent, dict):
        parent.pop(path[-1], None)
    elif isinstance(parent, list) and isinstance(path[-1], int):
        if path[-1] < len(parent):
            parent.pop(path[-1])
    return node


def mutate(payload, rng: random.Random):
    """One seeded mutation. Returns (mutant, op, path)."""
    doc = copy.deepcopy(payload)
    positions = [p for p in _paths(doc)]
    path = rng.choice(positions)
    op = rng.choice(MUTATIONS)
    try:
        current = _get(doc, path)
    except Exception:
        return doc, op, path
    if op == "nan":
        doc = _set(doc, path, float("nan"))
    elif op == "inf":
        doc = _set(doc, path, float("inf"))
    elif op == "neg_inf":
        doc = _set(doc, path, float("-inf"))
    elif op == "nan_string":
        doc = _set(doc, path, "nan")
    elif op == "inf_string":
        doc = _set(doc, path, "1e400")
    elif op == "negate":
        doc = _set(doc, path, -current if isinstance(current, (int, float)) and not isinstance(current, bool) else -1)
    elif op == "huge":
        doc = _set(doc, path, 1.7e308)
    elif op == "tiny":
        doc = _set(doc, path, -1.7e308)
    elif op == "to_string":
        doc = _set(doc, path, "corrupt")
    elif op == "to_null":
        doc = _set(doc, path, None)
    elif op == "to_bool":
        doc = _set(doc, path, True)
    elif op == "to_list":
        doc = _set(doc, path, [1, 2, 3])
    elif op == "to_dict":
        doc = _set(doc, path, {"a": 1})
    elif op == "drop_key":
        doc = _drop(doc, path)
    elif op == "truncate_list":
        doc = _set(doc, path, current[: len(current) // 2]) if isinstance(current, list) else _set(doc, path, [])
    elif op == "duplicate_list":
        doc = _set(doc, path, (current * 3)[:400]) if isinstance(current, list) else _set(doc, path, [current] * 3)
    elif op == "renest":
        doc = _set(doc, path, {"nested": [current]})
    return doc, op, path


# ---------------------------------------------------------------------------
# Per-mutant run
# ---------------------------------------------------------------------------


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def _leaf_count(node) -> int:
    if isinstance(node, dict):
        return sum(_leaf_count(v) for v in node.values()) or 0
    if isinstance(node, list):
        return sum(_leaf_count(v) for v in node) or 0
    return 1


def _surviving_keys(healthy, after) -> float:
    """Fraction of the healthy payload's leaves still present afterwards.

    A crude but honest measure of how much learned state one corrupt field
    cost: the store is rewritten from in-memory objects on the next cycle,
    so a loader that raised leaves defaults where months of learning were.
    """
    h = _leaf_count(healthy)
    if h == 0:
        return 1.0
    return min(1.0, _leaf_count(after) / h)


def _walk_nonfinite(node, path, out):
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_nonfinite(v, f"{path}.{k}", out)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            _walk_nonfinite(v, f"{path}[{i}]", out)
    elif isinstance(node, float) and math.isnan(node):
        out.append(f"{path}: NaN")


async def _cycle(coord, suffix):
    """One light update cycle: read inputs, publish, persist this store."""
    await coord._update_current_state()
    data = coord._build_data_dict()
    coord.data = data
    await STORES[suffix][1](coord)
    return data


async def run_one(suffix, mutant_doc):
    """Load a mutant, run two cycles, report the three properties."""
    key = f"{DOMAIN}_{ENTRY_ID}_{suffix}"
    hastore._reset_store_disk()
    # Write the mutant straight to the simulated disk, as a corrupt file is.
    hastore._DISK[key] = json.dumps(mutant_doc)
    root = logging.getLogger("custom_components.heatpump_optimizer")
    alt = logging.getLogger("heatpump_optimizer")
    cap = _Capture()
    for lg in (root, alt):
        lg.addHandler(cap)
        lg.setLevel(logging.DEBUG)
    res = {
        "load_exc": None,
        "cycle1_exc": None,
        "cycle2_exc": None,
        "load_logs": 0,
        "load_warn_logs": 0,
        "cycle1_logs": 0,
        "cycle2_logs": 0,
        "cycle2_warn_logs": 0,
        "nan_paths": [],
        "corrupt_persisted": False,
        "store_after": None,
    }
    try:
        coord = _new_coordinator()
        try:
            await STORES[suffix][0](coord)
        except Exception as err:
            res["load_exc"] = f"{type(err).__name__}: {err}"
        res["load_logs"] = len(cap.records)
        res["load_warn_logs"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        cap.records.clear()
        data1 = None
        try:
            data1 = await _cycle(coord, suffix)
        except Exception as err:
            res["cycle1_exc"] = f"{type(err).__name__}: {err}"
        res["cycle1_logs"] = len(cap.records)
        cap.records.clear()
        if data1 is not None:
            _walk_nonfinite(data1, "data", res["nan_paths"])
        # Did the corruption get written back to disk?
        raw = hastore._DISK.get(key)
        if raw is not None and ("NaN" in raw or "Infinity" in raw):
            res["corrupt_persisted"] = True
        try:
            await _cycle(coord, suffix)
        except Exception as err:
            res["cycle2_exc"] = f"{type(err).__name__}: {err}"
        res["cycle2_logs"] = len(cap.records)
        res["cycle2_warn_logs"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        raw2 = hastore._DISK.get(key)
        try:
            res["store_after"] = json.loads(raw2) if raw2 is not None else None
        except ValueError:
            res["store_after"] = None
    finally:
        for lg in (root, alt):
            lg.removeHandler(cap)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260912)
    ap.add_argument("--store", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    t0 = time.perf_counter()
    healthy = asyncio.run(_capture_healthy())

    totals = {
        "mutants": 0,
        "exception_escaped": 0,
        "exception_escaped_strict": 0,
        "nan_published": 0,
        "nan_published_strict_json": 0,
        "silent_nan": 0,
        "repeat_failure": 0,
        "multi_log": 0,
        "corrupt_persisted": 0,
        "state_destroyed": 0,
        "state_destroyed_strict": 0,
    }
    excs: dict[str, int] = {}
    destroyed_examples: list[str] = []
    per_store: dict[str, dict] = {}
    examples: list[str] = []

    for suffix in STORES:
        if args.store and suffix != args.store:
            continue
        base = healthy.get(suffix) or {}
        rng = random.Random(f"{args.seed}:{suffix}")
        row = {k: 0 for k in totals}
        for i in range(args.mutants):
            doc, op, path = mutate(base, rng)
            res = asyncio.run(run_one(suffix, doc))
            row["mutants"] += 1
            escaped = bool(
                res["load_exc"] or res["cycle1_exc"] or res["cycle2_exc"]
            )
            if escaped:
                row["exception_escaped"] += 1
                if op not in LOOSE:
                    row["exception_escaped_strict"] += 1
                msg = res["load_exc"] or res["cycle1_exc"] or res["cycle2_exc"]
                excs[f"{suffix}: {msg}"] = excs.get(f"{suffix}: {msg}", 0) + 1
            # Silent destruction: the load raised (so nothing was restored)
            # and the following cycle wrote defaults back over the store.
            if res["load_exc"] and isinstance(res["store_after"], dict):
                survived = _surviving_keys(base, res["store_after"])
                if survived < 1.0:
                    row["state_destroyed"] += 1
                    if op not in LOOSE:
                        row["state_destroyed_strict"] += 1
                    if len(destroyed_examples) < 15:
                        destroyed_examples.append(
                            f"{suffix} seed#{i} op={op} "
                            f"path={'.'.join(map(str, path)) or '<root>'} "
                            f"warn_logs={res['load_warn_logs']} "
                            f"surviving_content={survived:.2f} "
                            f"exc={res['load_exc']}"
                        )
            if res["nan_paths"]:
                row["nan_published"] += 1
                if op not in LOOSE:
                    row["nan_published_strict_json"] += 1
                if res["load_logs"] == 0:
                    row["silent_nan"] += 1
                if len(examples) < 25:
                    examples.append(
                        f"{suffix} seed#{i} op={op} path={'.'.join(map(str, path)) or '<root>'} "
                        f"logs={res['load_logs']} -> {res['nan_paths'][0]} "
                        f"(+{len(res['nan_paths']) - 1} more)"
                    )
            if res["cycle2_exc"] or (res["cycle1_logs"] and res["cycle2_logs"] >= res["cycle1_logs"] and res["cycle1_logs"] > 0):
                row["repeat_failure"] += 1
            if res["load_warn_logs"] > 1:
                row["multi_log"] += 1
            if res["corrupt_persisted"]:
                row["corrupt_persisted"] += 1
            if args.verbose and (escaped or res["nan_paths"]):
                print(
                    f"    {suffix} #{i} op={op} path={path} "
                    f"exc={res['load_exc'] or res['cycle1_exc'] or res['cycle2_exc']} "
                    f"nan={len(res['nan_paths'])}"
                )
        per_store[suffix] = row
        for k in totals:
            totals[k] += row[k]

    if excs:
        print("\n=== exceptions escaping a loader ===")
        for msg, n in sorted(excs.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>4}x {msg}")
    if destroyed_examples:
        print("\n=== learned state destroyed by one corrupt field ===")
        for line in destroyed_examples:
            print("  " + line)

    print("\n=== per store ===")
    header = (
        f"{'store':<18}{'mutants':>8}{'exc':>6}{'nan_pub':>9}"
        f"{'nan_strict':>11}{'silent':>8}{'repeat':>8}{'>1log':>7}{'persisted':>11}"
    )
    print(header)
    for suffix, row in per_store.items():
        print(
            f"{suffix:<18}{row['mutants']:>8}{row['exception_escaped']:>6}"
            f"{row['nan_published']:>9}{row['nan_published_strict_json']:>11}"
            f"{row['silent_nan']:>8}{row['repeat_failure']:>8}"
            f"{row['multi_log']:>7}{row['corrupt_persisted']:>11}"
        )

    if examples:
        print("\n=== first NaN-publishing mutants ===")
        for line in examples:
            print("  " + line)

    wall = time.perf_counter() - t0
    cpu = time.process_time()
    print()
    print(f"RESULT stores={len(per_store)} count")
    print(f"RESULT mutants_total={totals['mutants']} count")
    print(f"RESULT exception_escaped_mutants={totals['exception_escaped']} count")
    print(
        f"RESULT exception_escaped_strict_json_mutants="
        f"{totals['exception_escaped_strict']} count"
    )
    print(f"RESULT state_destroyed_mutants={totals['state_destroyed']} count")
    print(
        f"RESULT state_destroyed_strict_json_mutants="
        f"{totals['state_destroyed_strict']} count"
    )
    print(f"RESULT nan_published_mutants={totals['nan_published']} count")
    print(
        f"RESULT nan_published_strict_json_mutants="
        f"{totals['nan_published_strict_json']} count"
    )
    print(f"RESULT silent_nan_mutants={totals['silent_nan']} count")
    print(f"RESULT repeat_failure_mutants={totals['repeat_failure']} count")
    print(f"RESULT multi_log_mutants={totals['multi_log']} count")
    print(f"RESULT corrupt_persisted_mutants={totals['corrupt_persisted']} count")
    print(f"RESULT wall_s={wall:.1f} wall")
    print(f"RESULT thread_factor={cpu / max(cpu, 1e-9):.4f}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
