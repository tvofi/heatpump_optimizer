"""The finiteness sweep: a non-finite persisted leaf never reaches live state.

The class this closes: a non-finite (invalid) value in a persisted store is
installed onto the live/learned model. The round-5 fix (#1296/#1345) guarded
four named seams; the fifth — ``DhwProfileLearner.apply_cooling_rate`` — and its
sibling (``DefrostDerate.from_dict``'s ``duty`` grid) are the round-6 findings
(#1379, #1380). Guards placed per seam guard the seam a harness showed, while
the next sibling in the same store dict stays open.

The fix is one store-load boundary — ``QuarantiningStore.async_load`` scrubs
non-finite numeric leaves to ``None``, the loaders' absent-data default — and
this test is the property instrument that holds it closed. It has two arms:

**Arm 1 — the boundary set is derived from the tree, never carried.** The seam
set is every ``QuarantiningStore(...)`` construction in the package, found by
AST walk (the command below is the enumeration, not a list). Two assertions
make a new seam unable to escape silently:

* no raw ``Store(...)`` is constructed anywhere in the package — every store
  funnels through the boundary, so a store added on the raw class is refused;
* the number of loaders the reach arm drives equals the number of boundaries —
  a store added with no loader in this sweep leaves the counts unequal and the
  sweep refuses.

**Arm 2 — the reach sweep.** For every store, the healthy payload's numeric
leaves are substituted one at a time with each of the nine non-finite spellings
(``nan``/``+-inf``, the strings ``"NaN"``/``"Infinity"``/``"-Infinity"`` that
``float()`` turns into them, and the overflow/underflow floats), driven through
the **real** loader, and nothing non-finite may be reachable from
``_thermal_params`` (what the solver reads) or the published payload.

Null controls: the healthy payload through the same loaders reaches nothing
non-finite (the count is a property of the corrupt input, not of the load
path), and a finite-but-large leaf (``1e308``) is *not* scrubbed — the boundary
refuses only what is non-finite.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 tests/finite_boundary.py
"""
from __future__ import annotations

import asyncio
import ast
import dataclasses
import datetime as _dt
import json
import logging
import math
import os
import sys
from pathlib import Path

for _t in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests" / "hastub"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

import numpy as np  # noqa: E402

from harness import Results, FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.store import _sanitize  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402

logging.disable(logging.CRITICAL)

R = Results("finite store-load boundary")
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "heatpump_optimizer"
ENTRY_ID = "test_entry"

SUBSTITUTES = [
    float("nan"), float("inf"), float("-inf"),
    "NaN", "Infinity", "-Infinity", 1e309, -1e309, 1e308,
]


# ---------------------------------------------------------------------------
# Arm 1 — the seam set is derived, not carried
# ---------------------------------------------------------------------------

def _boundary_sites() -> tuple[list[str], list[str]]:
    """Every ``QuarantiningStore(...)`` and raw ``Store(...)`` construction.

    The enumeration rule: walk the package's AST; a ``Call`` whose callee is the
    bare name ``QuarantiningStore`` is a store-load boundary, and a ``Call``
    whose callee is the bare name ``Store`` is a boundary that skipped the
    choke point. ``Store[_T]`` in a base class or a type annotation is neither
    (a ``Subscript``/base, not a ``Call``), so it never trips the raw check.
    """
    quarantined: list[str] = []
    raw: list[str] = []
    for path in sorted(PKG.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                rel = str(path.relative_to(ROOT))
                if func.id == "QuarantiningStore":
                    quarantined.append(f"{rel}:{node.lineno}")
                elif func.id == "Store":
                    raw.append(f"{rel}:{node.lineno}")
    return quarantined, raw


_quarantined, _raw = _boundary_sites()
R.check(
    "no raw Store() is constructed outside the quarantine boundary",
    not _raw,
    f"raw={_raw}",
)
R.check(
    "the boundary set is non-empty (a rename erasing it must fail)",
    len(_quarantined) > 0,
    "the AST walk found no QuarantiningStore(...) construction",
)


# ---------------------------------------------------------------------------
# The boundary refuses non-finite and preserves finite (unit level)
# ---------------------------------------------------------------------------

_SANITIZE_CASES = {
    "nan": float("nan"), "inf": float("inf"), "-inf": float("-inf"),
    "str-nan": "NaN", "str-inf": "Infinity", "str--inf": "-Infinity",
}
for _name, _bad in _SANITIZE_CASES.items():
    _scrubbed = _sanitize({"leaf": _bad, "nested": [[_bad], {"k": _bad}]})
    R.check(
        f"the boundary quarantines {_name} at every depth",
        _scrubbed == {"leaf": None, "nested": [[None], {"k": None}]},
        f"scrubbed={_scrubbed!r}",
    )

_kept = _sanitize({"rate": 0.3, "big": 1e308, "label": "abc", "zero": 0.0, "flag": True, "n": 7})
R.check(
    "a finite payload round-trips unchanged (no over-refusal)",
    _kept == {"rate": 0.3, "big": 1e308, "label": "abc", "zero": 0.0, "flag": True, "n": 7},
    f"kept={_kept!r}",
)


# ---------------------------------------------------------------------------
# Arm 2 — the reach sweep, real loaders, real live-model scan
# ---------------------------------------------------------------------------

def _build_coord() -> HeatPumpOptimizerCoordinator:
    hass = FakeHass()
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))


def _healthy_payloads() -> dict[str, dict]:
    _storage._DISK.clear()
    _storage.SAVE_COUNTS.clear()
    coord = _build_coord()
    run = asyncio.run
    run(coord._async_save_thermal_learning())
    run(coord._async_save_price_model())
    run(coord._async_save_accuracy())
    run(coord._async_save_energy_totals())
    run(coord._async_save_manual_plan())
    run(coord._async_save_snapshots())
    run(coord._async_save_ledger())
    run(coord._dhw_learner.async_save_profile())
    run(coord._dhw_learner.async_save_draws())
    # Legionella's async_save is a no-op until a cycle has completed, so a
    # fresh coordinator persists nothing for it and the sweep would skip the
    # store's numeric leaf (``last_attempt_peak``). Seed one completed cycle
    # so that leaf is exercised like every other store's.
    coord._legionella.last_cycle = _dt.datetime(2026, 1, 1, 12, 0, 0)
    coord._legionella.attempt = _dt.datetime(2026, 1, 1, 12, 0, 0)
    coord._legionella.attempt_peak = 2.0
    run(coord._legionella.async_save())
    try:
        from heatpump_optimizer import boost, away
        run(boost.persist(coord))
        run(away.persist_override(coord))
    except Exception as exc:  # pragma: no cover - diagnostic only
        print("note: boost/away persist skipped: %r" % (exc,))
    try:
        from heatpump_optimizer import pump_arbiter
        held = pump_arbiter.state_for(coord)
        held.written["dhw_setpoint"] = (55.0, _dt.datetime(2026, 1, 1, 12, 0, 0))
        run(pump_arbiter._persist(coord))
    except Exception as exc:  # pragma: no cover - diagnostic only
        print("note: pump_arbiter persist skipped: %r" % (exc,))
    disk = {k: json.loads(v) for k, v in _storage._DISK.items()}
    _storage._DISK.clear()
    _storage.SAVE_COUNTS.clear()
    return disk


def _leaf_paths(obj, path=()):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_leaf_paths(v, path + (k,)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(_leaf_paths(v, path + (i,)))
    else:
        out.append((path, obj))
    return out


def _set_path(obj, path, value):
    cur = obj
    for step in path[:-1]:
        cur = cur[step]
    cur[path[-1]] = value


_SKIP_TYPES = (str, bytes, bool, int, float, type(None))
_SEEN: set = set()


def _walk_nonfinite(obj, label, depth=0, out=None):
    if out is None:
        out = []
    if depth > 5 or id(obj) in _SEEN:
        return out
    _SEEN.add(id(obj))
    if isinstance(obj, bool) or obj is None:
        return out
    if isinstance(obj, float):
        if not math.isfinite(obj):
            out.append(label)
        return out
    if isinstance(obj, (int, str, bytes)):
        return out
    if isinstance(obj, np.floating):
        if not math.isfinite(float(obj)):
            out.append(label)
        return out
    if isinstance(obj, np.ndarray):
        try:
            if obj.size and not np.all(np.isfinite(obj.astype(float))):
                out.append(label)
        except (TypeError, ValueError):
            pass
        return out
    if isinstance(obj, dict):
        for k, v in list(obj.items())[:80]:
            _walk_nonfinite(v, f"{label}[{k}]", depth + 1, out)
        return out
    if isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj[:80]):
            _walk_nonfinite(v, f"{label}[{i}]", depth + 1, out)
        return out
    if dataclasses.is_dataclass(obj):
        for f in dataclasses.fields(obj):
            _walk_nonfinite(getattr(obj, f.name, None), f"{label}.{f.name}", depth + 1, out)
        return out
    if hasattr(obj, "__dict__") and not callable(obj):
        mod = type(obj).__module__
        if mod.startswith("homeassistant") or mod.startswith("aiohttp"):
            return out
        for k, v in list(vars(obj).items())[:120]:
            if k.startswith("__"):
                continue
            _walk_nonfinite(v, f"{label}.{k}", depth + 1, out)
    return out


def _scan_model(coord):
    global _SEEN
    _SEEN = set()
    _SEEN.add(id(coord))
    _SEEN.add(id(coord.hass))
    _SEEN.add(id(coord.entry))
    _SEEN.add(id(getattr(coord, "_ctx", None)))
    return _walk_nonfinite(coord._thermal_params, "params")


def _scan_published(coord):
    try:
        pub = coord._build_data_dict()
    except Exception as exc:  # pragma: no cover - diagnostic only
        return ["<build_data_dict raised %s>" % type(exc).__name__]
    global _SEEN
    _SEEN = set()
    return _walk_nonfinite(pub, "data")


# The reach arm's wiring: which real loader consumes which store. This is the
# instrument's configuration, not the seam set — the seam set is Arm 1's AST
# walk, and the equality check below holds this map to it.
LOADERS = {
    "thermal_learning": lambda c: c._async_load_thermal_learning(),
    "price_model": lambda c: c._async_load_price_model(),
    "ledger": lambda c: c._async_load_ledger(),
    "accuracy": lambda c: c._async_load_accuracy(),
    "energy": lambda c: c._async_load_energy_totals(),
    "manual_plan": lambda c: c._async_load_manual_plan(),
    "snapshots": lambda c: c._async_load_snapshots(),
    "dhw_profile": lambda c: c._dhw_learner.async_load_profile(),
    "dhw_draws": lambda c: c._dhw_learner.async_load_draws(),
    "dhw_legionella": lambda c: c._legionella.async_load(),
    "boost": lambda c: __import__("heatpump_optimizer.boost", fromlist=["x"]).restore_session(c),
    "away": lambda c: __import__("heatpump_optimizer.away", fromlist=["x"]).restore_override(c),
    "pump_duty": lambda c: __import__("heatpump_optimizer.pump_arbiter", fromlist=["x"])._load(c),
}

R.check(
    "every derived boundary is wired to a loader in the reach sweep",
    len(LOADERS) == len(_quarantined),
    f"boundaries={len(_quarantined)} loaders={len(LOADERS)}",
)


def _main() -> int:
    disk = _healthy_payloads()
    by_name = {}
    for k, v in disk.items():
        by_name[k.replace(const.DOMAIN + "_" + ENTRY_ID + "_", "")] = (k, v)

    model_poison = 0
    published_poison = 0
    loader_escape = 0
    stores_swept = 0

    for name, loader in LOADERS.items():
        if name not in by_name:
            R.check(f"loader {name} has a healthy payload to corrupt", False, "no payload")
            continue
        key, healthy = by_name[name]
        leaves = _leaf_paths(healthy)
        stores_swept += 1
        for path, val in leaves:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                continue
            for sub in SUBSTITUTES:
                mutant = json.loads(json.dumps(healthy))
                try:
                    _set_path(mutant, path, sub)
                except (KeyError, IndexError, TypeError):
                    continue
                blob = json.dumps(mutant)
                _storage._DISK[key] = blob
                _storage.SAVE_COUNTS.clear()
                coord = _build_coord()
                try:
                    asyncio.run(loader(coord))
                except Exception:
                    loader_escape += 1
                    _storage._DISK.clear()
                    continue
                bad = _scan_model(coord)
                pbad = _scan_published(coord)
                if bad:
                    model_poison += 1
                if pbad:
                    published_poison += 1
                _storage._DISK.clear()

    R.check(
        "no non-finite value reaches the live thermal model",
        model_poison == 0,
        f"model_poison_total={model_poison}",
    )
    R.check(
        "no non-finite value reaches the published payload",
        published_poison == 0,
        f"published_poison_total={published_poison}",
    )
    R.check(
        "no loader raised on a quarantined payload",
        loader_escape == 0,
        f"loader_escape_total={loader_escape}",
    )

    # Null control: the healthy payloads reach nothing non-finite either — the
    # zero above is the corrupt input, not a sweep that skips its work.
    for key, healthy in by_name.values():
        _storage._DISK[key] = json.dumps(healthy)
        _storage.SAVE_COUNTS.clear()
        coord = _build_coord()
        asyncio.run(LOADERS[
            key.replace(const.DOMAIN + "_" + ENTRY_ID + "_", "")
        ](coord))
        bad = _scan_model(coord)
        R.check(
            f"healthy payload {key!r} leaves the model finite (null control)",
            not bad,
            f"bad={bad[:4]}",
        )
        _storage._DISK.clear()

    print(f"RESULT store_boundaries={len(_quarantined)} count")
    print(f"RESULT raw_store_calls={len(_raw)} count")
    print(f"RESULT stores_swept={stores_swept} count")
    print(f"RESULT model_poison_total={model_poison} count")
    print(f"RESULT published_poison_total={published_poison} count")
    print(f"RESULT loader_escape_total={loader_escape} count")
    return R.close("FINITE BOUNDARY CHECKS")


if __name__ == "__main__":
    sys.exit(_main())
