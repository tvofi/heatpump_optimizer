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
path), and a finite leaf below ``store.ABSURD`` is *not* scrubbed — the boundary
refuses only what is non-finite or of a magnitude no writer produces.

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

NONFINITE = [
    float("nan"), float("inf"), float("-inf"),
    "NaN", "Infinity", "-Infinity", 1e309, -1e309, 1e308,
]
#: Round 8 (#1518): a leaf that is not a number at all. The boundary above
#: passes it through by design (it is not non-finite), so the loader behind
#: it owns the refusal; ``"12,5"`` is the decimal-comma hand edit that took
#: every refresh down through ``MonthlyLedger.line``.
WRONG_TYPE = ["not_a_number", "12,5", [1.0, 2.0], {"k": 1.0}]
SUBSTITUTES = NONFINITE + WRONG_TYPE


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

_kept = _sanitize({"rate": 0.3, "big": 9.9e14, "label": "abc", "zero": 0.0, "flag": True, "n": 7,
                   "3": 1.0, "-2": 2.0})
R.check(
    "a finite payload round-trips unchanged (no over-refusal)",
    _kept == {"rate": 0.3, "big": 9.9e14, "label": "abc", "zero": 0.0, "flag": True, "n": 7,
              "3": 1.0, "-2": 2.0},
    f"kept={_kept!r}",
)
_absurd = _sanitize({"f": 1e300, "i": 2 ** 64, "j": 10 ** 400, "s": "1e300", "1000000000000000": 1.0,
                     "k": [-1e15]})
R.check(
    "the boundary quarantines an absurd magnitude as it does a non-finite (class P1)",
    _absurd == {"f": None, "i": None, "j": None, "s": None, "k": [None]},
    f"scrubbed={_absurd!r}",
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
    # A fresh coordinator persists an EMPTY ledger month map and draw
    # reservoir, so the sweep had no leaf to corrupt there and #1518's month
    # leaves went undriven. Book one line, one month mean and one draw
    # through the real writers, so those leaves exist to substitute.
    _when = _dt.datetime(2026, 1, 15, 12, 0, 0)
    coord._ledger.add(_when, "savings_baseline", kwh=2.0, sek=3.0)
    coord._ledger.observe_meta_mean(_when, "spot_price", 1.25)
    coord._dhw_learner.draw_stats.reservoirs["morning"] = [1.5, 2.5]
    run(coord._async_save_thermal_learning())
    run(coord._async_save_price_model())
    # #1512: the peak tracker persists its dated peaks in the accuracy store.
    # Seed three closed windows on two days so the sweep corrupts real peak
    # leaves and the shape arm below has labels to break.
    _tariff = coord._capacity_tariff()
    for _hour, _kw in ((6, 9.0), (7, 8.0), (30, 7.0), (31, 3.0)):
        coord._peak_tracker.observe(
            _dt.datetime(2026, 1, 1) + _dt.timedelta(hours=_hour), _kw, _tariff
        )
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


def _kind(obj) -> str:
    """``number`` for a real number, else the container or scalar kind."""
    if isinstance(obj, bool) or obj is None:
        return "other"
    if isinstance(obj, (int, float, np.integer, np.floating)):
        return "number"
    return "text" if isinstance(obj, str) else type(obj).__name__


def _walk_nonfinite(obj, label, depth=0, out=None, kinds=None):
    if out is None:
        out = []
    if kinds is not None:
        kinds[label] = _kind(obj)
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
            _walk_nonfinite(v, f"{label}[{k}]", depth + 1, out, kinds)
        return out
    if isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj[:80]):
            _walk_nonfinite(v, f"{label}[{i}]", depth + 1, out, kinds)
        return out
    if dataclasses.is_dataclass(obj):
        for f in dataclasses.fields(obj):
            _walk_nonfinite(getattr(obj, f.name, None), f"{label}.{f.name}", depth + 1, out, kinds)
        return out
    if hasattr(obj, "__dict__") and not callable(obj):
        mod = type(obj).__module__
        if mod.startswith("homeassistant") or mod.startswith("aiohttp"):
            return out
        for k, v in list(vars(obj).items())[:120]:
            if k.startswith("__"):
                continue
            _walk_nonfinite(v, f"{label}.{k}", depth + 1, out, kinds)
    return out


def _scan_model(coord, kinds=None):
    global _SEEN
    _SEEN = set()
    _SEEN.add(id(coord))
    _SEEN.add(id(coord.hass))
    _SEEN.add(id(coord.entry))
    _SEEN.add(id(getattr(coord, "_ctx", None)))
    return _walk_nonfinite(coord._thermal_params, "params", kinds=kinds)


def _type_drift(healthy_kinds, mutant_kinds):
    """Labels a healthy load held as a number and the mutant load holds as
    text or a container -- a wrong-type leaf the loader installed live."""
    return sorted(
        label for label, kind in mutant_kinds.items()
        if healthy_kinds.get(label) == "number" and kind not in ("number", "other")
    )


R.check(
    "the type-drift reader flags a number that loaded as text (its own control)",
    _type_drift({"p.x": "number", "p.y": "number"}, {"p.x": "text", "p.y": "number"}) == ["p.x"],
    "the reader under the reach arm's type check returned the wrong labels",
)


_RAISED = "<build_data_dict raised>"


def _scan_published(coord):
    try:
        pub = coord._build_data_dict()
    except Exception:
        return [_RAISED]
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


# ---------------------------------------------------------------------------
# Arm 3 -- the publish sweep (#1541): every entity of every platform
# ---------------------------------------------------------------------------

def _published(ent) -> dict:
    """Every public property the integration defines on the entity's class
    chain, read the way Home Assistant's state write reads them. The stub
    ``Entity`` has no ``state_attributes``, so the rule is the package's own
    properties -- which is where a coordinator value enters a state write."""
    out: dict = {}
    for cls in type(ent).__mro__:
        if not cls.__module__.startswith("heatpump_optimizer"):
            continue
        for name, member in vars(cls).items():
            if isinstance(member, property) and not name.startswith("_") and name not in out:
                try:
                    out[name] = getattr(ent, name)
                except Exception as exc:  # a raise is a failed state write
                    out[name] = (_RAISED, type(exc).__name__)
    return out


def _numbers(value) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (float, np.floating)):
        return [float(value)]
    if isinstance(value, dict):
        return [x for v in value.values() for x in _numbers(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in _numbers(v)]
    return []


def _poisoned(value, bad):
    """``value`` with every float leaf replaced by ``bad``; flags stay on."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (float, np.floating)):
        return bad
    if isinstance(value, dict):
        return {k: _poisoned(v, bad) for k, v in value.items()}
    if isinstance(value, list):
        return [_poisoned(v, bad) for v in value]
    return value


def _publish_arm() -> None:
    """Every float the coordinator publishes set non-finite; every entity of
    every registered platform must still publish finite values in process.

    The platform set is ``PLATFORM_LIST``, the list the integration forwards
    to Home Assistant, so a platform added there is swept without an edit
    here. ``reading_ok`` flags are all set, so the gated temperatures reach
    their entities, and the comfort target is poisoned too, because the
    thermostat's ``target_temperature`` reads it rather than the data dict.
    """
    import importlib
    import heatpump_optimizer as integration

    start = _dt.datetime(2026, 1, 15, 0, 0, tzinfo=_dt.timezone.utc)
    coord = _build_coord()
    coord._prices = [
        {"total": 0.7, "starts_at": (start + _dt.timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (start + _dt.timedelta(hours=h)).isoformat(), "temperature": 2.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48
    coord._forecast_arrays()
    healthy = coord._build_data_dict()
    healthy["reading_ok"] = {k: True for k in healthy.get("reading_ok") or {}}
    coord.entry.runtime_data = coord
    opt = getattr(coord, "_ctx", coord)._opt_config
    target = opt.target_temp
    for platform in integration.PLATFORM_LIST:
        module = importlib.import_module(f"heatpump_optimizer.{platform}")
        entities: list = []
        coord.data = healthy
        asyncio.run(module.async_setup_entry(coord.hass, coord.entry, entities.extend))
        before = {id(e): _published(e) for e in entities}
        leaks: list[str] = []
        reach = 0
        for bad in (float("nan"), float("inf"), float("-inf")):
            coord.data, opt.target_temp = _poisoned(healthy, bad), bad
            for ent in entities:
                after = _published(ent)
                reach += after != before[id(ent)]
                leaks += [
                    f"{type(ent).__name__}.{name}" for name, v in after.items()
                    if (isinstance(v, tuple) and v[:1] == (_RAISED,))
                    or any(not math.isfinite(x) for x in _numbers(v))
                ]
            opt.target_temp = target
        R.check(
            f"every {platform} entity publishes finite values from non-finite input (#1541)",
            not leaks,
            f"entities={len(entities)} leaks={sorted(set(leaks))}",
        )
        if any(_numbers(v) for pub in before.values() for v in pub.values()):
            R.check(
                f"the poisoned input reaches a published {platform} value (the arm is not vacuous)",
                reach > 0,
                "no published value moved when every float input went non-finite",
            )
        print(f"RESULT publish_{platform}_entities={len(entities)} count")
        print(f"RESULT publish_{platform}_leaks={len(leaks)} count")


def _no_rewrap_check() -> None:
    """The base wraps a published property once. A subclass that re-exports an
    inherited, already-scrubbed property in its own namespace must reuse that
    wrapper, not stack a second one per level (``_finite_scrubbed``)."""
    from heatpump_optimizer import sensor

    parent = sensor.CurrentPriceSensor
    alias = type("_AliasedPrice", (parent,), {"native_value": parent.native_value})
    R.check(
        "an inherited scrubbed property re-exported by a subclass is not wrapped twice",
        alias.native_value.fget is parent.native_value.fget,
        "the subclass's native_value was re-wrapped around the parent's wrapper",
    )



# ---------------------------------------------------------------------------
# Arm 4 -- the class sweep (round 9, class P1): every leaf kind, every store
# populated, every live object scanned
# ---------------------------------------------------------------------------
#
# Arm 2 holds one sub-property closed: nothing NON-FINITE reaches live state.
# The class is wider -- "a non-finite OR MALFORMED value crosses a persisted-
# store boundary with no guard" -- and at 1936d5ca Arm 2 was green over eleven
# instances of it, because (measured by the round-9 P1 RCA seat): it
# substituted numeric leaves only; its seeding left the snapshot ring, the
# frequency map, the capacity envelope, boost, away and the manual plan with
# no leaf to substitute; and it read only ``_thermal_params`` and the publish
# dict, so a wrong type, a naive instant or an absurd magnitude installed on
# any other learner was invisible. This arm measures the class property:
#
#   * seeding: every store written by its real saver after its sections are
#     populated, at an AWARE clock (Home Assistant's ``dt_util.now()`` is
#     always aware; the hastub's default is naive);
#   * substitution: every leaf AND every container, by kind -- numbers get
#     the non-finite, wrong-type and magnitude spellings; strings holding an
#     aware instant get the same instant naive; every int-like dict key gets
#     an absurd one;
#   * oracle, after the real loaders and the real consumers (publish, the
#     snapshot restore path): no raise; and over EVERY object the
#     coordinator owns (its attributes, and the per-coordinator registries
#     the package keeps at module level) nothing new that is non-finite,
#     naive, of absurd magnitude, or text/container where the healthy load
#     held a number.
#
# Its limits, stated so nobody reads more into a zero: a finite value inside
# the representable range but outside a field's physical domain (duty 1.5,
# a decile of 12) is not refused -- the magnitude oracle refuses only what
# no writer can produce (>= 1e15); and a loader that discards more than the
# corrupt leaf (a whole grid for one bad cell) is data loss, not a crash or
# a poison, and is not measured here.

from homeassistant.util import dt as _dt_util  # noqa: E402

_A4_NOW = _dt.datetime(2026, 1, 15, 12, 0, 0, tzinfo=_dt.timezone(_dt.timedelta(hours=1)))
_A4_ABSURD = 1e15
_A4_NUM = [float("nan"), float("inf"), "NaN", 1e309, None, "garbage", "12,5", [], {},
           1e300, -1e300, 2 ** 64]
_A4_STR = [None, 7, 1.5, "garbage", [], {}]
_A4_BOOL = ["false", None, "garbage"]
_A4_NONE = ["garbage", 1.5, "NaN", [], {}]
_A4_DICT = [None, "x", 3.0, []]
_A4_LIST = [None, "x", 3.0, {}]


def _a4_instant(value):
    """The aware datetime an ISO date-time string holds, else None."""
    if not isinstance(value, str) or len(value) < 16 or value[10:11] != "T":
        return None
    try:
        return _dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def _a4_subs(value) -> list:
    if isinstance(value, bool):
        return _A4_BOOL
    if isinstance(value, (int, float)):
        return _A4_NUM
    if isinstance(value, str):
        inst = _a4_instant(value)
        naive = [inst.replace(tzinfo=None).isoformat()] if inst and inst.tzinfo else []
        return _A4_STR + naive
    if value is None:
        return _A4_NONE
    if isinstance(value, dict):
        return _A4_DICT
    if isinstance(value, list):
        return _A4_LIST
    return []


def _a4_seams(obj, path=()):
    """(path, value) for every leaf and non-root container; ("key", path, k)
    for every int-like dict key. Scalar lists are sampled first and last."""
    out = []
    if isinstance(obj, dict):
        if path:
            out.append((path, obj))
        for k, v in obj.items():
            if isinstance(k, str) and k.lstrip("-").isdigit():
                out.append((("<key>",) + path + (k,), None))
            out.extend(_a4_seams(v, path + (k,)))
    elif isinstance(obj, list):
        if path:
            out.append((path, obj))
        idx = range(len(obj))
        if len(obj) > 2 and all(not isinstance(x, (dict, list)) for x in obj):
            idx = [0, len(obj) - 1]
        for i in idx:
            out.extend(_a4_seams(obj[i], path + (i,)))
    else:
        out.append((path, obj))
    return out


def _a4_mutants(healthy):
    for path, value in _a4_seams(healthy):
        if path[:1] == ("<key>",):
            mutant = json.loads(json.dumps(healthy))
            cur = mutant
            for step in path[1:-1]:
                cur = cur[step]
            cur[str(10 ** 15)] = cur.pop(path[-1])
            yield path, "key->1e15", mutant
            continue
        for sub in _a4_subs(value):
            mutant = json.loads(json.dumps(healthy))
            try:
                _set_path(mutant, path, sub)
            except (KeyError, IndexError, TypeError):
                continue
            yield path, sub, mutant


def _a4_seed() -> dict[str, dict]:
    """Every store, every section populated, written by its real saver."""
    import importlib
    _storage._DISK.clear()
    _storage.SAVE_COUNTS.clear()
    coord = _build_coord()
    t0 = _A4_NOW - _dt.timedelta(days=1)
    run = asyncio.run
    coord._ledger.add(t0, "savings_baseline", kwh=2.0, sek=3.0)
    coord._ledger.observe_meta_mean(t0, "spot_price", 1.25)
    coord._dhw_learner.draw_stats.reservoirs["morning"] = [1.5, 2.5]
    tariff = coord._capacity_tariff()
    for hour, kw in ((6, 9.0), (7, 8.0), (30, 7.0), (31, 3.0)):
        coord._peak_tracker.observe(
            _dt.datetime(2026, 1, 1, tzinfo=_A4_NOW.tzinfo) + _dt.timedelta(hours=hour), kw, tariff
        )
    coord._freq_map.observe(50.0, 2.0, 20.0, 100.0)
    coord._capacity_envelope[-1] = [6.0, 3]
    coord._defrost.observe_duty(0.0, 85.0, 0.1, 1)
    coord._curve_learner._last_step_at = t0.isoformat()
    coord._comfort_learner.last_update = t0
    coord._legionella.last_cycle = t0
    coord._legionella.attempt = t0
    coord._legionella.attempt_peak = 2.0
    from heatpump_optimizer.accuracy import AccuracySample
    for tracker in (coord._accuracy, coord._dhw_accuracy):
        tracker.record(AccuracySample(
            when=t0, predicted_power_kw=1.0, actual_power_kw=1.2, predicted_temp=21.0,
            actual_temp=21.2, predicted_cost=0.5, actual_cost=0.6, outdoor_temp=-2.0,
            humidity=80.0, cop_residual=0.1,
        ))
    coord._immersion_events.append(t0.isoformat())
    coord._fuse_advisor = {"month": "2026-01", "current_fuse_a": 25, "candidate_fuse_a": 20,
                           "candidate_kw": 13.8, "feasible": True, "comfort_shortfall_c": 0.0,
                           "worst_margin_kw": 2.5, "cost_delta_sek_month": -30.0}
    coord._fuse_advisor_at = t0
    coord._snapshot_ring.take(t0, coord._learner_snapshot_payloads(), coord._accuracy.summary(), True)
    for name in sorted(dir(coord)):
        if name.startswith("_async_save_"):
            try:
                run(getattr(coord, name)())
            except TypeError:
                continue  # a saver that needs arguments is not a store flush
    run(coord._dhw_learner.async_save_profile())
    run(coord._dhw_learner.async_save_draws())
    run(coord._legionella.async_save())
    boost = importlib.import_module("heatpump_optimizer.boost")
    boost.held_for(coord).set("dhw", True, _A4_NOW)
    run(boost.persist(coord))
    away = importlib.import_module("heatpump_optimizer.away")
    coord._away_state.override_active = True
    coord._away_state.override_return_iso = (_A4_NOW + _dt.timedelta(hours=20)).isoformat()
    run(away.persist_override(coord))
    arbiter = importlib.import_module("heatpump_optimizer.pump_arbiter")
    arbiter.state_for(coord).written["dhw_setpoint"] = (55.0, t0)
    run(arbiter._persist(coord))
    disk = {k: json.loads(v) for k, v in _storage._DISK.items()}
    _storage._DISK.clear()
    return disk


def _a4_owned(coord) -> list[tuple[str, object]]:
    """Everything the coordinator owns: its attributes, and each value a
    package module keeps for it in a module-level mapping keyed by it."""
    out = [(f"coord.{k}", v) for k, v in vars(coord).items()
           if k not in ("hass", "entry", "_ctx", "_listeners", "logger", "config_entry",
                        "_snapshot_ring")]
    # The ring holds snapshots as opaque payloads by design (restored only
    # through the loaders the restore consumer below drives, and scanned there).
    ring = getattr(coord, "_snapshot_ring", None)
    if ring is not None:
        out += [(f"ring.{k}", v) for k, v in vars(ring).items() if k != "snapshots"]
    for name, module in list(sys.modules.items()):
        if not name.startswith("heatpump_optimizer."):
            continue
        for gname, gval in list(vars(module).items()):
            if hasattr(gval, "get") and hasattr(gval, "keys") and not isinstance(gval, type):
                try:
                    held = gval.get(coord)
                except TypeError:
                    continue
                if held is not None:
                    out.append((f"{name.rsplit('.', 1)[-1]}.{gname}", held))
    return out


def _a4_walk(obj, label, found, seen, depth=0):
    if depth > 7 or id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, bool) or obj is None or isinstance(obj, bytes):
        return
    if isinstance(obj, (int, float, np.integer, np.floating)):
        x = float(obj) if not isinstance(obj, int) else obj
        if isinstance(x, float) and not math.isfinite(x):
            found.add(("nonfinite", label))
        elif abs(x) >= _A4_ABSURD:
            found.add(("magnitude", label))
        found.add(("number", label))
        return
    if isinstance(obj, _dt.datetime):
        if obj.tzinfo is None:
            found.add(("naive", label))
        return
    if isinstance(obj, str):
        inst = _a4_instant(obj)
        if inst is not None and inst.tzinfo is None:
            found.add(("naive", label))
        found.add(("text", label))
        return
    if isinstance(obj, np.ndarray):
        if obj.dtype.kind in "fiu" and obj.size:
            arr = obj.astype(float)
            if not np.all(np.isfinite(arr)):
                found.add(("nonfinite", label))
            elif np.any(np.abs(arr) >= _A4_ABSURD):
                found.add(("magnitude", label))
        return
    if isinstance(obj, dict):
        for k, v in list(obj.items())[:200]:
            if isinstance(k, (int, np.integer)) and not isinstance(k, bool) and abs(int(k)) >= _A4_ABSURD:
                found.add(("magnitude", f"{label}<key>"))
            _a4_walk(v, f"{label}[{k}]", found, seen, depth + 1)
        return
    if isinstance(obj, (list, tuple)) or type(obj).__name__ == "deque":
        items = list(obj)
        found.add(("container", label))
        for i, v in enumerate(items[:200]):
            _a4_walk(v, f"{label}[{i}]", found, seen, depth + 1)
        return
    if callable(obj) and not hasattr(obj, "__dict__"):
        return
    if not (type(obj).__module__ or "").startswith("heatpump_optimizer"):
        return
    if dataclasses.is_dataclass(obj):
        items = [(f.name, getattr(obj, f.name, None)) for f in dataclasses.fields(obj)]
    else:
        items = list(getattr(obj, "__dict__", {}).items())
    for k, v in items[:300]:
        if not k.startswith("__"):
            _a4_walk(v, f"{label}.{k}", found, seen, depth + 1)


def _a4_scan(coord, published) -> set:
    found: set = set()
    seen = {id(coord.hass), id(coord.entry)}
    for label, value in _a4_owned(coord):
        _a4_walk(value, label, found, seen)
    _a4_walk(published, "data", found, set())
    return found


def _a4_verdict(healthy: set, mutant: set) -> set:
    """The oracle: what the mutant load installed that the healthy one did not."""
    bad = {(k, l) for (k, l) in mutant - healthy if k in ("nonfinite", "naive", "magnitude")}
    numbers = {l for (k, l) in healthy if k == "number"}
    bad |= {("type", l) for (k, l) in mutant if k in ("text", "container") and l in numbers}
    # peak_threshold_kw publishes +inf for "no ceiling yet" (a documented sentinel).
    return {(k, l) for (k, l) in bad if l != "data[peak_threshold_kw]"}


_A4_PLANT = {("number", "p.n"), ("number", "p.t"), ("naive", "p.d"), ("magnitude", "p.m"),
             ("nonfinite", "p.f"), ("text", "p.t")}
R.check(
    "the class oracle flags a planted naive, magnitude, non-finite and number-turned-text "
    "label, and nothing on the healthy set (its own control)",
    {k for k, _l in _a4_verdict({("number", "p.n"), ("number", "p.t")}, _A4_PLANT)}
    == {"naive", "magnitude", "nonfinite", "type"}
    and not _a4_verdict(_A4_PLANT, _A4_PLANT - {("text", "p.t")}),
    "the verdict under the class arm returned the wrong kinds",
)


def _a4_load(key: str, payload: dict) -> tuple[list[str], set]:
    _storage._DISK.clear()
    _storage.SAVE_COUNTS.clear()
    _storage._DISK[key] = json.dumps(payload)
    coord = _build_coord()
    coord.entry.runtime_data = coord
    loader = LOADERS[key.replace(const.DOMAIN + "_" + ENTRY_ID + "_", "")]
    escapes: list[str] = []
    try:
        asyncio.run(loader(coord))
    except Exception as exc:  # noqa: BLE001 -- the escape is the measurement
        escapes.append(f"loader:{type(exc).__name__}")
    # Snapshot restore reads the ring the snapshot loader filled; for every
    # other store it is a no-op, so it runs for all of them (derived, not wired).
    if key.endswith("_snapshots"):
        asyncio.run(LOADERS["thermal_learning"](coord))
    published = None
    for cname, call in (
        ("best_restore", lambda: coord._snapshot_ring.best_restore()),
        ("restore_service", lambda: asyncio.run(coord.async_restore_learned_snapshot())),
        ("publish", coord._build_data_dict),
    ):
        try:
            result = call()
            if cname == "publish":
                published = result
        except Exception as exc:  # noqa: BLE001
            escapes.append(f"{cname}:{type(exc).__name__}")
    _storage._DISK.clear()
    return escapes, _a4_scan(coord, published)


def _class_arm() -> None:
    import time
    t_start = time.monotonic()
    _dt_util.freeze(_A4_NOW)
    try:
        disk = _a4_seed()
        empty = sorted(
            f"{k.replace(const.DOMAIN + '_' + ENTRY_ID + '_', '')}:{'/'.join(map(str, p))}"
            for k, v in disk.items() for p, c in _a4_seams(v)
            if p[:1] != ("<key>",) and isinstance(c, (dict, list)) and not c
        )
        seams: dict[str, set] = {}
        mutants = 0
        null_bad: list[str] = [
            f"{k}: the boundary rewrote a healthy payload"
            for k, v in disk.items() if _sanitize(v) != v
        ]
        for key in sorted(disk):
            store = key.replace(const.DOMAIN + "_" + ENTRY_ID + "_", "")
            esc0, healthy = _a4_load(key, disk[key])
            if esc0 or _a4_verdict(healthy, healthy):
                null_bad.append(f"{store}: {esc0}")
            naive0 = {l for (k, l) in healthy if k in ("naive", "magnitude", "nonfinite")}
            if naive0 - {"data[peak_threshold_kw]"}:
                null_bad.append(f"{store}: healthy load holds {sorted(naive0)[:3]}")
            for path, sub, mutant in _a4_mutants(disk[key]):
                mutants += 1
                esc, found = _a4_load(key, mutant)
                why = sorted(set(esc) | {k for (k, _l) in _a4_verdict(healthy, found)})
                if why:
                    pstr = "/".join("#" if isinstance(p, int) else str(p) for p in path)
                    seams.setdefault(f"{store}:{pstr} {','.join(why)}", set()).add(
                        sub if isinstance(sub, str) else json.dumps(sub) if not (
                            isinstance(sub, float) and not math.isfinite(sub)) else repr(sub))
    finally:
        _dt_util.freeze(None)
    for seam, subs in sorted(seams.items()):
        print(f"  SEAM {seam} subs={sorted(map(str, subs))[:6]}")
    print(f"RESULT class_mutants={mutants} count")
    print(f"RESULT class_seams={len(seams)} count")
    print(f"RESULT class_unseeded_sections={len(empty)} count")
    for section in empty:
        print(f"  UNSEEDED {section}")
    print(f"RESULT class_arm_seconds={time.monotonic() - t_start:.1f}")
    R.check(
        "the class sweep drove every seeded store (it cannot go green by skipping)",
        mutants > 0 and len(disk) == len(LOADERS),
        f"mutants={mutants} stores={len(disk)} loaders={len(LOADERS)}",
    )
    R.check(
        "the healthy populated stores load clean through every loader and consumer (null control)",
        not null_bad,
        f"{null_bad}",
    )
    R.check(
        "no single-leaf malformation of a store raises, or installs a non-finite, naive, "
        "absurd-magnitude or wrong-type value anywhere the coordinator owns (class P1)",
        not seams,
        f"seams={len(seams)}",
    )


def _main() -> int:
    disk = _healthy_payloads()
    by_name = {}
    for k, v in disk.items():
        by_name[k.replace(const.DOMAIN + "_" + ENTRY_ID + "_", "")] = (k, v)

    model_poison = 0
    published_poison = 0
    loader_escape = 0
    type_drift = 0
    refresh_escape = 0
    stores_swept = 0

    _ledger_leaves = [
        p for p, _v in _leaf_paths(by_name.get("ledger", ("", {}))[1])
        if p[:2] == ("ledger", "months")
    ]
    R.check(
        "the ledger payload carries month line and meta leaves to corrupt (#1518)",
        any("lines" in p for p in _ledger_leaves) and any("meta" in p for p in _ledger_leaves),
        f"ledger month leaves={_ledger_leaves}",
    )

    for name, loader in LOADERS.items():
        if name not in by_name:
            R.check(f"loader {name} has a healthy payload to corrupt", False, "no payload")
            continue
        key, healthy = by_name[name]
        leaves = _leaf_paths(healthy)
        stores_swept += 1
        _storage._DISK[key] = json.dumps(healthy)
        coord = _build_coord()
        asyncio.run(loader(coord))
        healthy_kinds: dict = {}
        _scan_model(coord, healthy_kinds)
        _storage._DISK.clear()
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
                kinds: dict = {}
                bad = _scan_model(coord, kinds)
                pbad = _scan_published(coord)
                if _type_drift(healthy_kinds, kinds):
                    type_drift += 1
                if bad:
                    model_poison += 1
                if pbad[:1] == [_RAISED]:
                    refresh_escape += 1
                elif pbad:
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
        "no corrupt leaf makes the next refresh's publication raise (#1518)",
        refresh_escape == 0,
        f"refresh_escape_total={refresh_escape}",
    )
    R.check(
        "no wrong-type leaf is installed where the live model holds a number",
        type_drift == 0,
        f"type_drift_total={type_drift}",
    )
    R.check(
        "no loader raised on a quarantined payload",
        loader_escape == 0,
        f"loader_escape_total={loader_escape}",
    )

    # #1512 shape arm: the accuracy store's peak list in the shape a store
    # written before ``peak_days`` has (no labels), and malformed label lists,
    # through the real loader. Each must load without raising, keep only
    # finite peaks, and give every peak exactly one string label.
    shape_bad = []
    acc_key, acc_healthy = by_name["accuracy"]
    shapes = {
        "pre-#1512 store, no labels": None,
        "labels not a list": "2026-01-01",
        "labels of the wrong type": [1, None, ["x"]],
        "fewer labels than peaks": ["2026-01-01"],
    }
    for label, days in shapes.items():
        mutant = json.loads(json.dumps(acc_healthy))
        peaks = mutant["peaks"]
        peaks["peaks"] = list(peaks["peaks"]) + [float("nan")]
        if days is None:
            peaks.pop("peak_days", None)
        else:
            peaks["peak_days"] = days
        _storage._DISK[acc_key] = json.dumps(mutant)
        _storage.SAVE_COUNTS.clear()
        coord = _build_coord()
        try:
            asyncio.run(LOADERS["accuracy"](coord))
        except Exception as exc:
            shape_bad.append(f"{label}: raised {type(exc).__name__}")
            _storage._DISK.clear()
            continue
        tracker = coord._peak_tracker
        if not (
            len(tracker.peaks) == len(acc_healthy["peaks"]["peaks"])
            and len(tracker.peak_days) == len(tracker.peaks)
            and all(isinstance(d, str) for d in tracker.peak_days)
            and all(math.isfinite(p) for p in tracker.peaks)
        ):
            shape_bad.append(f"{label}: {tracker.peaks} {tracker.peak_days}")
        _storage._DISK.clear()
    R.check(
        "the peak store loads its pre-#1512 and malformed label shapes: "
        "finite peaks only, one string label each, no raise",
        not shape_bad and len(acc_healthy["peaks"]["peaks"]) == 2,
        f"{shape_bad} healthy peaks {acc_healthy['peaks']}",
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
    print(f"RESULT type_drift_total={type_drift} count")
    print(f"RESULT refresh_escape_total={refresh_escape} count")
    _publish_arm()
    _no_rewrap_check()
    _class_arm()
    return R.close("FINITE BOUNDARY CHECKS")


if __name__ == "__main__":
    sys.exit(_main())
