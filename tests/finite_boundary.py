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
path), and a finite leaf below ``store.ABSURD`` is *not* scrubbed — the
boundary refuses only what is non-finite or of a magnitude no writer produces.

**Arm 4 -- the class sweep (round 9, class P1).** Every leaf kind, every
container, every int-like dict key, every store populated through its real
saver at an aware clock with a configured zone (Home Assistant's state; the
hastub's default is neither), and after the real loaders and consumers an
oracle over everything the coordinator owns: no raise, and nothing new that is
non-finite, naive, of absurd magnitude, or text/container where the healthy
load held a number. The substitution and seeding rules are the round-9 P1
RCA's, measured over the eleven judged instances its narrower predecessors
were green on.

**Arm 5 -- the store version seam (#1740).** Over Arm 1's construction set:
every store names its own version constant (no literal, none shared); every
store, seeded at its own version (the control), one below it (a bump: the
migration hook) and one above it (a downgrade), and read through its real
loader, surfaces each mismatch as a WARNING and a ``store_version`` repair
issue; and a store read at a version above 1 overrides the default migration
hook, so a bump without a migration fails here.

**I1 pins (round 9, F9.1).** Five guards outside the boundary above, each
correct already and each invisible to every closure script if deleted: a
direct call of the production symbol, not a store sweep, because I1 is
mutation-invisibility rather than a boundary defect.

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

from harness import Results, FakeHass, FakeEntry, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import coordinator as _coord_mod  # noqa: E402
from heatpump_optimizer import store as _store  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore, _sanitize  # noqa: E402
from homeassistant.util import dt as _dt_util  # noqa: E402
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


def _floats_poisoned(value, bad):
    """``value`` with every float leaf replaced by ``bad``; flags stay on."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (float, np.floating)):
        return bad
    if isinstance(value, dict):
        return {k: _floats_poisoned(v, bad) for k, v in value.items()}
    if isinstance(value, list):
        return [_floats_poisoned(v, bad) for v in value]
    return value


def _kinds_arm() -> None:
    """The domain predicates and the store-name lookup, pinned one by one.

    Each row is the smallest input on which one conjunct decides the answer
    alone, so replacing an ``and`` by an ``or`` (or dropping a return or a
    guard) flips a row: a value the parse accepts but the shape refuses, and
    a value of the right shape the parse refuses.
    """
    dom = _store.Domain
    rows = [
        ("int refuses a float inside its range", dom("int", 0, 10), 1.5, False),
        ("int refuses an integer outside its range", dom("int", 0, 10), 11, False),
        ("int admits an integer inside its range", dom("int", 0, 10), 5, True),
        ("instant refuses a parsing value with a foreign separator",
         dom("instant"), "2026-01-01x10:00:00", False),
        ("instant refuses a value that does not parse", dom("instant"), "xxxxxxxxxxT", False),
        ("instant admits the T separator", dom("instant"), "2026-01-01T10:00:00", True),
        ("day refuses a ten-character value that does not parse",
         dom("day"), "2026-13-45", False),
        ("day refuses a compact date of another length", dom("day"), "20260101", False),
        ("day admits an ISO day", dom("day"), "2026-01-31", True),
        ("month refuses a seven-character value that does not parse",
         dom("month"), "2026-13", False),
        ("month refuses a value of another length", dom("month"), "202601", False),
        ("month admits an ISO month", dom("month"), "2026-01", True),
    ]
    bad = [
        label for label, domain, value, want in rows
        if _store.in_domain(domain, value) is not want
    ]
    R.check("each kind's shape and parse conjuncts decide alone", not bad, f"{bad}")

    name = next(iter(_store.DOMAINS))
    got = _store._store_name(f"{const.DOMAIN}_{ENTRY_ID}_{name}")
    R.check(
        "a store key names its DOMAINS entry, and a foreign key names none",
        got == name and _store._store_name("no_such_entry_key") is None,
        f"{got!r}",
    )

    seen: list[str] = []

    class _Tap(logging.Handler):
        def emit(self, record):
            seen.append(record.getMessage())

    tap, log = _Tap(), _store._LOGGER
    old, floor = log.level, logging.root.manager.disable
    logging.disable(logging.NOTSET)
    log.addHandler(tap)
    log.setLevel(logging.DEBUG)
    try:
        holder = type("_Holder", (), {"key": f"{const.DOMAIN}_{ENTRY_ID}_thermal_learning"})()
        _store._log_off_domain(holder, {"cop_scale": 99.0})
        off_logged = len(seen)
        _store._log_off_domain(holder, {"cop_scale": 1.0})
        clean_logged = len(seen) - off_logged
    finally:
        log.removeHandler(tap)
        log.setLevel(old)
        logging.disable(floor)
    R.check(
        "the off-domain diagnostic logs an out-of-domain field and stays silent on a clean one",
        off_logged == 1 and clean_logged == 0 and "cop_scale" in seen[0],
        f"off={off_logged} clean={clean_logged} {seen}",
    )


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
            coord.data, opt.target_temp = _floats_poisoned(healthy, bad), bad
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
#     populated, at an AWARE clock with a CONFIGURED zone -- Home
#     Assistant's state (its ``dt_util.now()`` is always aware and its
#     ``DEFAULT_TIME_ZONE`` is never None); the hastub's default is neither,
#     and under it a loader that resolved a naive stamp into a zone would
#     break the stub's own naive round trips (F3.1's recorded control), so
#     the arm sets both, and only for its own duration;
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
# a poison, and is not measured here. Both stay per-seam in their instance
# PRs; a declared-domain barrier is card C1 (F9.3).

_A4_NOW = _dt.datetime(2026, 1, 15, 12, 0, 0, 0, tzinfo=_dt.timezone(_dt.timedelta(hours=1)))
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


def _a4_seed(enrich=None) -> dict[str, dict]:
    """Every store, every section populated, written by its real saver.

    ``enrich`` (Arm 6) fills what the populated defaults leave uniform or
    empty, before the savers run."""
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
    if enrich is not None:
        enrich(coord, t0)
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
    from zoneinfo import ZoneInfo
    t_start = time.monotonic()
    # Home Assistant's state, for this arm's duration only: an aware clock AND
    # a configured zone. Under the stub's default (naive clock, no zone) the
    # arm would refuse the stub's own healthy naive stamps, and a loader that
    # resolved one into UTC would break every naive round trip (F3.1's
    # recorded control, forward-carried from #1647).
    zone_before = _dt_util.DEFAULT_TIME_ZONE
    _dt_util.DEFAULT_TIME_ZONE = ZoneInfo("Europe/Stockholm")
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
        _dt_util.DEFAULT_TIME_ZONE = zone_before
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


# ---------------------------------------------------------------------------
# Arm 5 -- the instant bound (round 9, persisted future instant)
# ---------------------------------------------------------------------------

def _instants(obj, path=()):
    """Every string leaf that reads as a date AND a time (longer than a date)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _instants(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _instants(v, path + (i,))
    elif isinstance(obj, str) and len(obj) > 10:
        try:
            when = _dt.datetime.fromisoformat(obj)
        except ValueError:
            return
        yield path, when


def _utc(when):
    return when if when.tzinfo is not None else when.replace(tzinfo=_dt.timezone.utc)


def _with_instants(payload, when):
    """The payload with every instant leaf, and two probes, set to ``when``."""
    out = json.loads(json.dumps(payload))
    for path, _w in list(_instants(out)):
        _set_path(out, path, when.isoformat())
    if isinstance(out, dict):
        out["__instant_probe"] = when.isoformat()
        out["__instant_probe_aware"] = _utc(when).isoformat()
    return out


#: Stores whose instants no system bound governs (``lead=None``), each with
#: its reason. An opt-out not listed here, or a listed one that no longer
#: opts out, fails the arm: an exemption is reviewed, never inferred.
LEAD_OPT_OUTS = {
    "away": "the user-set return time; no system maximum exists",
}


def _instant_arm(by_name) -> None:
    """No stored instant reaches a loader beyond the clock plus its store's lead.

    Every store, through its real loader: each instant leaf -- and a probe leaf,
    so a store with none is still driven -- written 400 days ahead of the clock
    that reads it back. What ``QuarantiningStore.async_load`` hands the loader
    is recorded, and none of its instants may lie beyond now plus that store's
    declared lead. A lead of ``None`` is an opt-out, printed. Null controls: an
    honest payload comes back byte-identical, and so does an instant one minute
    inside a store's lead, so a lead cannot be dropped to zero unseen.
    """
    t0 = _dt.datetime(2026, 6, 1, 12, 0, 0)
    seen: list = []
    original = QuarantiningStore.async_load

    async def _recording(self):
        data = await original(self)
        seen.append((str(getattr(self, "key", None) or getattr(self, "_key", "")),
                     getattr(self, "_lead", _dt.timedelta(0)), data))
        return data

    def _load(name, key, payload):
        seen.clear()
        _storage._DISK.clear()
        _storage._DISK[key] = json.dumps(payload)
        asyncio.run(LOADERS[name](_build_coord()))
        _storage._DISK.clear()
        return [r for r in seen if r[0] == key]

    escaped, opted_out, rewritten, lead_lost, driven, checked = [], [], [], [], 0, 0
    QuarantiningStore.async_load = _recording
    _dt_util.freeze(t0)
    try:
        for name in LOADERS:
            if name not in by_name:
                continue
            key, healthy = by_name[name]
            records = _load(name, key, _with_instants(healthy, t0 + _dt.timedelta(days=400)))
            driven += bool(records)
            for _key, lead, data in records:
                if lead is None:
                    opted_out.append(name)
                    continue
                bound = _utc(t0) + lead
                for path, when in _instants(data):
                    checked += 1
                    if _utc(when) > bound:
                        escaped.append(f"{name}:{'/'.join(map(str, path))}")
            honest = _with_instants(healthy, t0 - _dt.timedelta(hours=1))
            for _key, lead, data in _load(name, key, honest):
                if json.dumps(data, sort_keys=True) != json.dumps(honest, sort_keys=True):
                    rewritten.append(name)
                if lead:
                    inside = _with_instants(healthy, t0 + lead - _dt.timedelta(minutes=1))
                    for _k, _l, kept in _load(name, key, inside):
                        if json.dumps(kept, sort_keys=True) != json.dumps(inside, sort_keys=True):
                            lead_lost.append(name)
        # What an honest clock wrote, the same clock reads back unchanged: the
        # real writers of the two stores that hold legitimate futures, at
        # their longest lead, so a lead dropped to zero cannot go unseen.
        _storage._DISK.clear()
        writer = _build_coord()
        from heatpump_optimizer import accuracy as _acc, boost as _boost
        _boost.held_for(writer).set("dhw", True, t0)
        asyncio.run(_boost.persist(writer))
        _far = max(_acc.LEAD_BUCKETS)
        writer._accuracy.note_lead_prediction(t0 + _dt.timedelta(hours=_far), _far, 21.0)
        asyncio.run(writer._async_save_accuracy())
        written = {n: by_name[n][0] for n in ("boost", "accuracy")}
        wrote = {n: json.loads(_storage._DISK[k]) for n, k in written.items()}
        for name, key in written.items():
            for _k, _l, kept in _load(name, key, wrote[name]):
                if json.dumps(kept, sort_keys=True) != json.dumps(wrote[name], sort_keys=True):
                    lead_lost.append(f"{name} (writer round trip)")
    finally:
        QuarantiningStore.async_load = original
        _dt_util.freeze(None)
    R.check(
        "no stored instant reaches a loader beyond the clock plus its store's lead",
        not escaped,
        f"escaped={escaped[:8]} of {len(escaped)}",
    )
    R.check(
        "the instant sweep drove every loader and checked instants (not vacuous)",
        driven == len(LOADERS) and checked >= 2 * (driven - len(LEAD_OPT_OUTS)),
        f"driven={driven} loaders={len(LOADERS)} instants_checked={checked}",
    )
    R.check(
        "every lead opt-out is a listed, reasoned one, and every listed one opts out",
        set(opted_out) == set(LEAD_OPT_OUTS),
        f"opted_out={sorted(set(opted_out))} listed={sorted(LEAD_OPT_OUTS)}",
    )
    R.check(
        "an honest payload comes back byte-identical (null control)",
        not rewritten,
        f"rewritten={rewritten}",
    )
    R.check(
        "an instant inside its store's lead survives the load (a lead is not lost)",
        not lead_lost,
        f"lead_lost={lead_lost}",
    )
    print(f"RESULT instant_escaped_total={len(escaped)} count")
    print(f"RESULT instant_stores_driven={driven} count")
    print(f"RESULT instant_leaves_checked={checked} count")
    print(f"RESULT instant_lead_opt_outs={sorted(set(opted_out))}")


# ---------------------------------------------------------------------------
# Arm 6 -- the declared domain (round 9, class P1, card C1)
# ---------------------------------------------------------------------------

# Arm 4 refuses poison and magnitude; it cannot refuse a finite value outside
# the domain only the field's writer knows (a duty of 1.5, a decile of 12),
# nor a loader that drops a whole valid grid for one bad cell. This arm reads
# each stored field's domain from ``store.DOMAINS`` and measures, through the
# real loaders and the real savers (what a store holds after a load is what
# its saver writes from the live model):
#
#   * coverage: every leaf and map key the rich seed's savers write has a
#     declared domain (no allow-list: an undeclared field is refused), and
#     the seed itself lies in its declarations;
#   * out/in: every bounded field (and bounded key) substituted just outside
#     its domain comes back inside it, and substituted with a fresh value
#     inside it comes back as that value (the probe reaches live state, so a
#     green out-probe is not a field the loader never read);
#   * blast radius: one bad cell in a grid costs that cell, not its
#     neighbours, unless the declaration names the grid ``whole`` and why;
#   * null control: the healthy seed round-trips unchanged.

def _a6_enrich(coord, t0) -> None:
    """Arm 6's rich seed: every section a saver can write, with distinct values.

    Direct state sets (the Arm 4 idiom) where a learner's update path would
    need hours of history; the savers that write them are the real ones.
    """
    from heatpump_optimizer.manual_plan import ManualOverride
    from heatpump_optimizer.comfort_learning import OverrideEvent
    ld = t0.date().isoformat()
    grid = [[round(0.05 + 0.1 * i + 0.03 * j, 4) for j in range(2)] for i in range(6)]
    derate = coord._defrost
    derate.duty = grid
    derate.factors = [[round(0.6 + 0.05 * i + 0.02 * j, 4) for j in range(2)] for i in range(6)]
    for name in ("counts", "duty_counts", "duty_events"):
        setattr(derate, name, [[i + j + 1 for j in range(2)] for i in range(6)])
    for day in (1, 2, 5, 6):  # weekdays and a weekend, so both shape rows learn
        when = t0 - _dt.timedelta(days=day)
        coord._price_model.observe_day(when, [0.5 + 0.1 * ((h * (day + 3)) % 11) for h in range(24)])
        coord._price_model.observe_day_quarters(
            when, [0.5 + 0.05 * ((q * (day + 2)) % 7) for q in range(96)])
    coord._price_days_seen = {ld, "2026-01-13"}
    coord._price_qdays_seen = {ld}
    for decile, kw in ((2, 3.0), (5, 5.5), (8, 8.0)):
        coord._freq_map.observe(30.0 + 5 * decile, kw, 20.0, 100.0)
    coord._capacity_envelope[3] = [7.5, 2]
    coord._cop_baseline[(4, False)] = [3.1, 5]
    coord._cop_baseline[(4, True)] = [2.4, 3]
    coord._internal_gains_profile = [round(0.2 + 0.01 * h, 3) for h in range(24)]
    coord._snow_accum_last = t0
    coord._last_heavy_snow = t0
    for cusum in (coord._vent_cusum, coord._cop_health_cusum):
        cusum.stat = 0.3
        cusum.evidence = ["a reading"]
        cusum.last_fed = t0
    for tracker in (coord._accuracy, coord._dhw_accuracy):
        tracker.lead_sigma = {3.0: 0.4, 6.0: 0.7}
        tracker.lead_counts = {3.0: 4, 6.0: 2}
        tracker.note_lead_prediction(t0 + _dt.timedelta(hours=3), 3.0, 21.5)
    coord._comfort_learner.record_override(OverrideEvent(
        when=t0, delta_c=1.0, indoor_temp=20.0, planned_setpoint=21.0, relative_price=0.8))
    coord._ledger.add(t0 - _dt.timedelta(days=40), "spot", kwh=3.0, sek=4.0)
    coord._month_reports["2025-12"] = coord._freeze_month_report("2025-12")
    coord._score_day = {"day": ld, "kwh": 2.0, "sek": 3.0, "spot_sum": 4.0, "spot_h": 2.0,
                        "free_streak": 1.0}
    coord._operation_score = 72.0
    coord._start_counter.months["2026-01"] = 3
    coord._start_counter.lifetime = 9
    coord._energy_totals_since = ld
    coord._legionella.disinfect.owned = ["switch.immersion"]
    coord._manual_override = ManualOverride(
        space_slots=[(_A4_NOW + _dt.timedelta(hours=1), _A4_NOW + _dt.timedelta(hours=2))],
        dhw_slots=None, expires_at=_A4_NOW + _dt.timedelta(hours=6), created_at=t0)
    coord._away_state.migrated_helpers = True
    coord._flow_bias.bias_k, coord._flow_bias.samples = 2.5, 4
    learner = coord._dhw_learner
    for name, low in (("hourly_profile", 0.5), ("profile_weekday", 0.75), ("profile_weekend", 0.25)):
        # Dyadic, mean exactly 1: the loader's renormalisation is the identity
        # on it (an arbitrary learned profile moves an ulp).
        setattr(learner, name, [low if h % 2 else 2.0 - low for h in range(24)])
    learner.draw_stats.reservoirs["evening"] = [3.5, 4.5, 2.0]


def _a6_savers():
    import importlib

    def mod(name):
        return importlib.import_module("heatpump_optimizer." + name)

    return {
        "thermal_learning": lambda c: c._async_save_thermal_learning(),
        "price_model": lambda c: c._async_save_price_model(),
        "ledger": lambda c: c._async_save_ledger(),
        "accuracy": lambda c: c._async_save_accuracy(),
        "energy": lambda c: c._async_save_energy_totals(),
        "manual_plan": lambda c: c._async_save_manual_plan(),
        "snapshots": lambda c: c._async_save_snapshots(),
        "dhw_profile": lambda c: c._dhw_learner.async_save_profile(),
        "dhw_draws": lambda c: c._dhw_learner.async_save_draws(),
        "dhw_legionella": lambda c: c._legionella.async_save(),
        "boost": lambda c: mod("boost").persist(c),
        "away": lambda c: mod("away").persist_override(c),
        "pump_duty": lambda c: mod("pump_arbiter")._persist(c),
    }


def _a6_roundtrip(store: str, payload, savers) -> tuple[object, list[str]]:
    """What ``store`` holds after its loader reads ``payload`` and its saver writes."""
    key = const.DOMAIN + "_" + ENTRY_ID + "_" + store
    _storage._DISK.clear()
    _storage._DISK[key] = json.dumps(payload)
    coord = _build_coord()
    coord.entry.runtime_data = coord
    escapes = []
    try:
        asyncio.run(LOADERS[store](coord))
        if store == "ledger":  # the fuse advisor's own reader of this store
            loaded = asyncio.run(_coord_mod._stored_fuse_advisor(coord._ledger_store))
            coord._fuse_advisor, coord._fuse_advisor_at = loaded or ({}, None)
        if store == "snapshots":  # the ring is opaque until a restore reads it
            asyncio.run(coord.async_restore_learned_snapshot())
        _storage._DISK.clear()
        for name in _A6_RESTORED if store == "snapshots" else (store,):
            asyncio.run(savers[name](coord))
    except Exception as exc:  # noqa: BLE001 -- the escape is the measurement
        escapes.append(type(exc).__name__)
    after = {k.replace(const.DOMAIN + "_" + ENTRY_ID + "_", ""): json.loads(v)
             for k, v in _storage._DISK.items()}
    _storage._DISK.clear()
    if store == "snapshots":
        return after, escapes
    return after.get(store), escapes


#: What a snapshot restore writes back: the ring, and every learner store it
#: restores (a snapshot's learner payloads are opaque in the ring by design).
_A6_RESTORED = ("snapshots", "thermal_learning", "dhw_profile", "dhw_draws", "price_model",
                "accuracy")


def _a6_probes(domain):
    """(out, in) substitutes for a bounded domain: just outside, freshly inside."""
    if domain.kind == "choice" and domain.choices and all(isinstance(x, float) for x in domain.choices):
        return [max(domain.choices) + 1.0], list(domain.choices[:1])
    if domain.kind == "choice":
        return ["zz-no-such-choice"], list(domain.choices[-1:])
    if domain.kind not in ("real", "int"):
        return [], []
    lo, hi = domain.lo, domain.hi
    span = (hi - lo) if math.isfinite(lo) and math.isfinite(hi) else 2.0
    step = max(1, round(span / 2)) if domain.kind == "int" else span / 2
    outs = [v for v, ok in ((hi + step, math.isfinite(hi)), (lo - step, math.isfinite(lo))) if ok]
    inside = lo + span * 0.37 if math.isfinite(lo) else hi - 1.37 if math.isfinite(hi) else 1.37
    inside = min(max(round(inside) if domain.kind == "int" else inside, lo), hi)
    # A domain unbounded below admits a negative value, and a loader that
    # floors it at zero (the signed cost totals, F9.3 review) is refused only
    # by an in-probe below zero.
    below = [min(hi, 0.0) - (2 if domain.kind == "int" else 1.37)] if not math.isfinite(lo) else []
    return outs, [inside] + below


def _a6_off(store: str, payload, restored: bool = False) -> list[str]:
    """Fields off their declaration; ``restored``: a snapshot load's write-back."""
    if restored:
        return [f"{name}:{o}" for name, held in payload.items()
                for o in _a6_off(name, held) if not (name == "snapshots" and "/learners/" in o)]
    return [
        "/".join(map(str, p)) + ("~" if k else "")
        for p, k, d, v in _store.stored_fields(store, payload)
        if d is None or not _store.in_domain(d, v)
    ]


def _a6_get(obj, path):
    for step in path:
        obj = obj[step]
    return obj


def _a6_grid(path, seed):
    """The grid a cell belongs to (its innermost numeric list), or None."""
    parent = _a6_get(seed, path[:-1]) if path and isinstance(path[-1], int) else None
    # A grid is a list of more than one number of one type; a mixed
    # ``[ratio, count]`` pair is one entry, and the entry is the unit a bad
    # cell may cost.
    numeric = isinstance(parent, list) and len(parent) > 1 and len({type(x) for x in parent}) == 1 \
        and type(parent[0]) in (int, float)
    return path[:-1] if numeric else None


def _a6_lost(seed, after, grid, cell) -> int:
    """Cells of ``grid`` other than ``cell`` that a load changed."""
    try:
        before, now = _a6_get(seed, grid), _a6_get(after, grid)
    except (KeyError, IndexError, TypeError):
        return len(_a6_get(seed, grid))
    if not isinstance(now, list):
        return len(before) - 1
    if len(now) == len(before):
        return sum(1 for i, (a, b) in enumerate(zip(before, now)) if i != cell and a != b)
    # An entry list the loader re-ranks or shortens: count survivors, not places.
    kept = [x for i, x in enumerate(before) if i != cell]
    for x in now:
        if x in kept:
            kept.remove(x)
    return len(kept)


def _a6_sampled(seed, path) -> bool:
    """Grid rows and cells first and last only (the P1 RCA's cut): a middle
    cell is loaded by the same line as its ends."""
    for i, step in enumerate(path):
        if isinstance(step, int) and 0 < step < len(_a6_get(seed, path[:i])) - 1:
            return False
    return True


def _a6_store(store, seed, savers, out):
    """Drive one store's declared fields; append refusals to ``out``."""
    for path, is_key, domain, value in _store.stored_fields(store, seed):
        if domain is None or not _a6_sampled(seed, path):
            continue
        outs, ins = _a6_probes(domain)
        label = f"{store}:{'/'.join('#' if isinstance(p, int) else str(p) for p in path)}"
        label += "~" if is_key else ""
        for sub in outs + ins + ([None] if _a6_grid(path, seed) and not is_key else []):
            mutant = json.loads(json.dumps(seed))
            if is_key:
                parent = _a6_get(mutant, path[:-1])
                text = str(sub) if domain.kind != "int" else str(int(sub))
                if text in parent:
                    continue  # the fresh key is already a sibling's
                parent[text] = parent.pop(path[-1])
            else:
                _set_path(mutant, path, sub)
            after, esc = _a6_roundtrip(store, mutant, savers)
            out["driven"] += 1
            if esc:
                out["refused"].add(f"{label} raised {esc} on {sub!r}")
                continue
            off = _a6_off(store, after, store == "snapshots") if after is not None else []
            after = after.get("snapshots") if store == "snapshots" and after else after
            if sub in outs and off:
                out["refused"].add(f"{label} held {sub!r} out of domain: {off[:2]}")
            grid = _a6_grid(path, seed) if not is_key else None
            if sub not in ins and grid and not domain.whole:
                lost = _a6_lost(seed, after, grid, path[-1])
                if lost:
                    out["refused"].add(f"{label} bad cell {sub!r} cost {lost} neighbour(s)")
            if sub in ins and not is_key and not domain.unread:
                try:
                    held = _a6_get(after, path)
                except (KeyError, IndexError, TypeError):
                    held = "<gone>"
                # Back as the seed (never read), or with its sign lost (floored).
                lost_sign = all(isinstance(x, (int, float)) for x in (held, sub)) and (held < 0) != (sub < 0)
                if held != sub and (held == value or lost_sign):
                    out["unreached"].add(f"{label} in-domain {sub!r} came back {held!r}")


def _domain_arm() -> None:
    import time
    from zoneinfo import ZoneInfo
    t_start = time.monotonic()
    zone_before = _dt_util.DEFAULT_TIME_ZONE
    _dt_util.DEFAULT_TIME_ZONE = ZoneInfo("Europe/Stockholm")
    _dt_util.freeze(_A4_NOW)
    savers = _a6_savers()
    out = {"driven": 0, "refused": set(), "unreached": set()}
    try:
        disk = _a4_seed(enrich=_a6_enrich)
        seeds = {k.replace(const.DOMAIN + "_" + ENTRY_ID + "_", ""): v for k, v in disk.items()}
        undeclared = sorted({o for s, v in seeds.items() for o in _a6_off(s, v)})
        roundtrip = sorted(s for s, v in seeds.items() if s != "snapshots"
                           and _a6_roundtrip(s, v, savers) != (v, []))
        # A restore writes back only what a snapshot carries, so its null is
        # the ring unchanged and every store it restored inside its domain.
        restored, esc = _a6_roundtrip("snapshots", seeds["snapshots"], savers)
        roundtrip += esc + _a6_off("snapshots", restored, True) + (
            ["snapshots ring"] if restored.get("snapshots") != seeds["snapshots"] else [])
        planted = json.loads(json.dumps(seeds["energy"]))
        planted["zz_planted"] = 1.0
        control = _a6_off("energy", planted)
        # _close_score_day's free-day branch writes a book with no day, only
        # the #908 streak; a restart before the next fold must keep it.
        streak = {**seeds["ledger"], "score_day": {"free_streak": 3.0}}
        streak_back = (_a6_roundtrip("ledger", streak, savers)[0] or {}).get("score_day")
        for store in sorted(seeds):
            _a6_store(store, seeds[store], savers, out)
    finally:
        _dt_util.freeze(None)
        _dt_util.DEFAULT_TIME_ZONE = zone_before
    fields = sum(len(_store.stored_fields(s, v)) for s, v in seeds.items())
    for line in sorted(out["refused"]):
        print(f"  DOMAIN {line}")
    for line in sorted(out["unreached"]):
        print(f"  UNREACHED {line}")
    print(f"RESULT domain_stores={len(seeds)} count")
    print(f"RESULT domain_fields={fields} count")
    print(f"RESULT domain_probes={out['driven']} count")
    print(f"RESULT domain_refused={len(out['refused'])} count")
    print(f"RESULT domain_unreached={len(out['unreached'])} count")
    print(f"RESULT domain_arm_seconds={time.monotonic() - t_start:.1f}")
    R.check(
        "every store the rich seed writes is seeded, and every field it writes is declared "
        "in store.DOMAINS and lies in its declaration (no allow-list)",
        len(seeds) == len(LOADERS) and not undeclared,
        f"stores={sorted(seeds)} off={undeclared[:6]}",
    )
    R.check(
        "a planted undeclared field is refused (the coverage check's own control)",
        control == ["zz_planted~", "zz_planted"],
        f"control={control}",
    )
    R.check(
        "the healthy rich seed round-trips unchanged through every loader and saver (null control)",
        not roundtrip,
        f"changed={roundtrip}",
    )
    R.check(
        "a day-less score_day book (the free-day close's streak) survives a reload (#908)",
        streak_back == {"free_streak": 3.0},
        f"came back {streak_back!r}",
    )
    R.check(
        "the domain sweep drove every bounded field (it cannot go green by skipping)",
        out["driven"] > 0,
        f"probes={out['driven']}",
    )
    R.check(
        "no stored field substituted just outside its declared domain is held live, and "
        "no one bad grid cell costs its neighbours (class P1, card C1)",
        not out["refused"],
        f"refused={len(out['refused'])}",
    )
    R.check(
        "every in-domain probe reaches live state (the out-probes are not vacuous)",
        not out["unreached"],
        f"unreached={len(out['unreached'])}",
    )
    from heatpump_optimizer import dhw_learning
    R.check(
        "the DHW profile's declared ceiling is dhw_learning's own (a literal, since that "
        "module imports the store)",
        _store.DOMAINS["dhw_profile"]["hourly_profile/#"].hi == dhw_learning.DHW_PROFILE_MAX_INTENSITY,
        f"declared={_store.DOMAINS['dhw_profile']['hourly_profile/#'].hi}",
    )
    _overflow_sites()


def _overflow_sites() -> None:
    """The float() sites a Python int past a double reaches in production.

    orjson (storage, config entries, HTTP) never yields such an int and the
    store boundary scrubs one, so these four are the ones fed by what orjson
    does not parse: entity attributes and service-call fields (the F3.3 lead,
    D1-s5-03's shape). Each must refuse it as unreadable, not raise.
    """
    from heatpump_optimizer import freq_control, inputs, wood_fuel
    huge = 10 ** 400
    got = {}
    for name, call, want in (
        ("coordinator._as_float", lambda: _coord_mod._as_float(huge, 1.5), 1.5),
        ("freq_control._finite", lambda: freq_control._finite(huge), None),
        ("inputs._finite", lambda: inputs._finite(huge), None),
        ("wood_fuel._wood_slots_error",
         lambda: wood_fuel._wood_slots_error([{"liters": huge}], []), "invalid_wood_slots"),
    ):
        try:
            got[name] = call() == want
        except Exception as exc:  # noqa: BLE001 -- the raise is the defect
            got[name] = type(exc).__name__
    R.check(
        "an int past a double refuses as unreadable at each attribute- or service-fed float() site",
        all(v is True for v in got.values()),
        f"{got}",
    )


# ---------------------------------------------------------------------------
# I1 -- deletable-guard pins (round 9, F9.1): five guards whose deletion no
# closure script notices. Each is one direct call of the production symbol
# (not a store-boundary sweep), because I1 is mutation-invisibility, not a
# boundary defect -- the boundary above is already correct at every one of
# these sites.
# ---------------------------------------------------------------------------

def _i1_pins_arm() -> None:
    from heatpump_optimizer.coordinator import _dhw_inlet_c
    from heatpump_optimizer.flow_lift import FlowCurveBias
    from heatpump_optimizer.price_model import PriceShapeModel, HOURS_PER_DAY
    from heatpump_optimizer.dhw_draws import DrawStats
    from heatpump_optimizer.ledger import MonthlyLedger

    # D3-s1-01: _dhw_inlet_c's lower plausibility bound is inclusive
    # (coordinator.py:1371, `-5.0 <= value <= 35.0`). CMP_BOUND C0043 turns it
    # into `-5.0 < value`, which no closure script notices.
    now = _dt_util.utcnow()
    hass = FakeHass({"sensor.inlet": FakeState("-5.0", last_updated=now, unit=None)})
    R.check(
        "_dhw_inlet_c keeps the inclusive lower plausibility bound (-5.0 is valid)",
        _dhw_inlet_c(hass, "sensor.inlet") == -5.0,
        f"got {_dhw_inlet_c(hass, 'sensor.inlet')!r}",
    )

    # D3-s2-01 (weakened(low)): FlowCurveBias.from_dict's isfinite guard is
    # the one store-parser guard QuarantiningStore leaves reachable
    # (flow_lift.py:210). GUARD_OFF S34 lets a non-finite stored bias survive
    # into ``bias_k`` instead of restoring to inert.
    learner = FlowCurveBias.from_dict({"bias_k": float("nan"), "samples": 5})
    R.check(
        "FlowCurveBias.from_dict restores to inert on a non-finite stored bias_k",
        learner.bias_k == 0.0 and learner.samples == 0,
        f"bias_k={learner.bias_k!r} samples={learner.samples!r}",
    )

    # D3-s2-02: PriceShapeModel.from_dict's residual_var restore keeps a
    # legitimate stored variance (price_model.py:368, `max(0.0, float(v))`).
    # CLAMP_DROP S19 replaces the per-value parse with a literal 0.0, so a
    # real recorded variance is silently zeroed with the gate green.
    var = [[2.5] * HOURS_PER_DAY, [1.0] * HOURS_PER_DAY]
    model = PriceShapeModel.from_dict({"residual_var": var})
    R.check(
        "PriceShapeModel.from_dict keeps a legitimate stored residual_var value",
        model.residual_var[0][0] == 2.5,
        f"residual_var[0][0]={model.residual_var[0][0]!r}",
    )

    # D3-s3-02: DrawStats.from_dict's open-occurrence parse keeps a
    # legitimate stored value (dhw_draws.py:136,
    # `max(0.0, float(data.get("open_kwh", 0.0)))`). CLAMP_DROP M19 replaces
    # it with a literal 0.0, zeroing a real open draw with the gate green.
    draws = DrawStats.from_dict({"open_kwh": 2.5})
    R.check(
        "DrawStats.from_dict keeps a legitimate stored open_kwh value",
        draws._open_kwh == 2.5,
        f"_open_kwh={draws._open_kwh!r}",
    )

    # D3-s3-03: MonthlyLedger.add's non-finite guard is the only thing
    # keeping a NaN amount from ever reaching a month entry (ledger.py:117).
    # GUARD_OFF M21 (`if False:`) lets it through, creating a month whose
    # kwh/sek line is NaN, unnoticed by any closure script.
    ledger = MonthlyLedger()
    when = _dt.datetime(2026, 1, 15, 12, tzinfo=_dt.timezone.utc)
    ledger.add(when, "spot", kwh=float("nan"), sek=1.0)
    R.check(
        "MonthlyLedger.add drops a non-finite amount before any month is created",
        not ledger.months,
        f"months={ledger.months!r}",
    )


# ---------------------------------------------------------------------------
# Arm 5 -- the store version seam (#1740, R9-EG-B4)
# ---------------------------------------------------------------------------

def _version_names() -> list[tuple[str, str | None]]:
    """(site, version constant) per ``QuarantiningStore(...)`` construction.

    Arm 1's enumeration rule; the version is the second positional argument or
    ``version=``, and a literal (or anything not a name) reads as ``None``.
    """
    out: list[tuple[str, str | None]] = []
    for path in sorted(PKG.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "QuarantiningStore"):
                continue
            arg = node.args[1] if len(node.args) > 1 else next(
                (k.value for k in node.keywords if k.arg == "version"), None)
            name = arg.id if isinstance(arg, ast.Name) else (
                arg.attr if isinstance(arg, ast.Attribute) else None)
            out.append((f"{path.relative_to(ROOT)}:{node.lineno}", name))
    return out


def _version_arm(by_name) -> None:
    """Every store's version mismatch is surfaced, and a bump carries a migration.

    A store's loader catches a failed load and resets at DEBUG (legionella
    re-stamps its last cycle), so a version mismatch the store does not surface
    is invisible. Each store is seeded with its healthy payload stamped at its
    own version (the control: nothing surfaced), one below (what a bump leaves
    on disk: the migration hook) and one above (a downgrade: Home Assistant's
    UnsupportedStorageVersionError), and read through its real loader.
    """
    names = _version_names()
    literal = [site for site, name in names if name is None]
    R.check(
        "every store's version is a named constant, never a literal (#1740)",
        not literal and len(names) == len(_quarantined),
        f"literal={literal} constructions={len(names)} boundaries={len(_quarantined)}",
    )
    used: dict[str, list[str]] = {}
    for site, name in names:
        used.setdefault(name or "", []).append(site)
    shared = {n: s for n, s in used.items() if n and len(s) > 1}
    R.check(
        "no two stores share a version constant, so a bump migrates one store (#1740)",
        not shared,
        f"shared={shared}",
    )

    seen: list[tuple[int, str]] = []

    class _Tap(logging.Handler):
        def emit(self, record):
            seen.append((record.levelno, record.getMessage()))

    reads: list = []
    real_load = QuarantiningStore.async_load

    async def _recording(self):
        reads.append(self)
        return await real_load(self)

    def _surfaced(coord, key: str) -> tuple[bool, bool]:
        warned = any(lvl >= logging.WARNING and key in msg for lvl, msg in seen)
        issued = any(
            kw.get("translation_key") == "store_version"
            and kw.get("translation_placeholders", {}).get("store") == key
            for _d, _i, kw in getattr(coord.hass, "issues", None) or []
        )
        return warned, issued

    tap, log = _Tap(), _store._LOGGER
    old, floor = log.level, logging.root.manager.disable
    logging.disable(logging.NOTSET)
    log.addHandler(tap)
    log.setLevel(logging.DEBUG)
    QuarantiningStore.async_load = _recording
    stores: dict[str, object] = {}
    noisy: list[str] = []
    unsurfaced: list[str] = []
    overwritten: list[str] = []
    try:
        for name, loader in LOADERS.items():
            key, healthy = by_name[name]
            for lag in (0, 1, -1):
                _storage._DISK.clear()
                _storage._VERSIONS.clear()
                reads.clear()
                seen.clear()
                _storage._DISK[key] = json.dumps(healthy)
                if lag:
                    _storage._VERSIONS[key] = stores[key]._version - lag
                coord = _build_coord()
                coord.entry.runtime_data = coord
                try:
                    asyncio.run(loader(coord))
                except Exception as exc:  # noqa: BLE001 -- an escape is a finding too
                    unsurfaced.append(f"{name}@{lag}:raised {type(exc).__name__}")
                    continue
                if not lag:
                    stores[key] = next(s for s in reads if s._key == key)
                if lag == 1:
                    # The control: a bump's reset is saved at this release's
                    # version, so read-only is a downgrade's alone.
                    st = next(s for s in reads if s._key == key)
                    asyncio.run(st.async_save(healthy))
                    if _storage._VERSIONS.get(key) != stores[key]._version:
                        overwritten.append(f"{name}@bump:unsaved")
                if lag == -1:
                    # A downgrade: the newer release's document must survive
                    # the load (legionella saves inside its own) and the next
                    # save, so reinstalling that release finds it intact.
                    newer = stores[key]._version + 1
                    after_load = (_storage._VERSIONS.get(key), _storage._DISK.get(key))
                    st = next(s for s in reads if s._key == key)
                    asyncio.run(st.async_save({"overwritten": True}))
                    after_save = (_storage._VERSIONS.get(key), _storage._DISK.get(key))
                    for when, got in (("load", after_load), ("save", after_save)):
                        if got != (newer, json.dumps(healthy)):
                            overwritten.append(f"{name}@{when}:version={got[0]}")
                    # The user's way out: once the document no longer reads
                    # newer (deleted, or replaced), a fresh load saves again.
                    _storage._VERSIONS[key] = stores[key]._version
                    asyncio.run(st.async_load())
                    _storage._DISK.pop(key, None)
                    asyncio.run(st.async_save(healthy))
                    if key not in _storage._DISK:
                        overwritten.append(f"{name}@reload:unsaved")
                warned, issued = _surfaced(coord, key)
                if not lag and (warned or issued):
                    noisy.append(name)
                elif lag and not (warned and issued):
                    unsurfaced.append(f"{name}@{lag}:warned={warned},issued={issued}")
    finally:
        QuarantiningStore.async_load = real_load
        log.removeHandler(tap)
        log.setLevel(old)
        logging.disable(floor)
        _storage._DISK.clear()
        _storage._VERSIONS.clear()
        _store._NEWER_ON_DISK.clear()
    R.check(
        "a store read at its own version surfaces nothing (the control)",
        not noisy and len(stores) == len(LOADERS),
        f"noisy={noisy} stores={len(stores)} loaders={len(LOADERS)}",
    )
    R.check(
        "every store's version mismatch, older or newer, logs a WARNING and raises "
        "a repair issue naming its key (#1740)",
        not unsurfaced,
        f"unsurfaced={unsurfaced}",
    )
    R.check(
        "a downgraded store keeps the newer release's document through its load and "
        "the next save, so reinstalling that release finds it intact; a bumped "
        "store, and one re-read once the newer document is gone, still saves (#1869)",
        not overwritten,
        f"overwritten={overwritten}",
    )
    default = getattr(QuarantiningStore, "_async_migrate_func", None)
    unmigrated = sorted(
        k for k, s in stores.items()
        if s._version > 1 and getattr(type(s), "_async_migrate_func", None) is default
    )
    R.check(
        "a store whose version exceeds 1 overrides the default migration hook, so a "
        "bump without a migration fails here (#1740)",
        not unmigrated,
        f"unmigrated={unmigrated}",
    )

    # The default hook's branches, directly: a major mismatch surfaces, older
    # or newer, and a minor-only one (same major) does not -- Home Assistant
    # then reads the document as stored on the NotImplementedError the hook
    # raises either way. Newer matters at the 2025.2.0 floor, which has no
    # UnsupportedStorageVersionError and hands a downgrade to this hook; the
    # stub models only the later releases' refusal, so this drives it here.
    verdicts = []
    for major in (1, 2, 3):
        # A fresh hass per call: the registry keeps one issue per id, so a
        # shared one would read a second surfacing as the first.
        probe_hass = FakeHass()
        probe = QuarantiningStore(probe_hass, 2, f"{const.DOMAIN}_{ENTRY_ID}_version_probe")
        try:
            asyncio.run(probe._async_migrate_func(major, 1, {}))
            verdicts.append("returned")
        except NotImplementedError:
            verdicts.append("not-implemented")
        except Exception as exc:  # noqa: BLE001 -- a base without the hook
            verdicts.append(type(exc).__name__)
        verdicts.append(len(getattr(probe_hass, "issues", None) or []))
    R.check(
        "the default hook raises NotImplementedError and surfaces a major mismatch "
        "older or newer, not a minor-only one",
        verdicts == ["not-implemented", 1, "not-implemented", 0, "not-implemented", 1],
        f"verdicts={verdicts}",
    )
    # The floor's route: no refusal class, the hook is handed the newer
    # document. Once it has seen one, the store must not save over it either.
    fkey = f"{const.DOMAIN}_{ENTRY_ID}_version_floor_save"
    floor = QuarantiningStore(FakeHass(), 2, fkey)
    try:
        asyncio.run(floor._async_migrate_func(3, 1, {}))
    except NotImplementedError:
        pass
    _storage.SAVE_COUNTS.pop(fkey, None)
    asyncio.run(floor.async_save({"overwritten": True}))
    floor_saves = _storage.SAVE_COUNTS.pop(fkey, 0)
    _store._NEWER_ON_DISK.discard(fkey)
    _storage._DISK.pop(fkey, None)
    _storage._VERSIONS.pop(fkey, None)
    R.check(
        "a store whose hook was handed a newer document (the 2025.2.0 floor's "
        "downgrade) does not save over it (#1869)",
        floor_saves == 0,
        f"saves after the hook saw a newer major={floor_saves}",
    )
    # A downgrade leaves the store as Home Assistant's own exception, after the
    # surfacing: the loaders catch any exception alike, so only the type tells
    # a re-raise from a fall-through that fails on unbound data.
    dkey = f"{const.DOMAIN}_{ENTRY_ID}_version_downgrade"
    _storage._DISK[dkey] = json.dumps({"v": 1.0})
    _storage._VERSIONS[dkey] = 3
    try:
        asyncio.run(QuarantiningStore(FakeHass(), 2, dkey).async_load())
        escaped = "returned"
    except BaseException as exc:  # noqa: BLE001 -- the type is the measurement
        escaped = type(exc).__name__
    _storage._DISK.clear()
    _storage._VERSIONS.clear()
    R.check(
        "a downgrade leaves the store as UnsupportedStorageVersionError (#1740)",
        escaped == "UnsupportedStorageVersionError",
        f"escaped={escaped}",
    )

    # A store that does migrate: Home Assistant saves the migration's result
    # from inside the load, while async_save waits for the read in flight --
    # its own. That write-back must not wait on itself.
    class _Migrating(QuarantiningStore):
        async def _async_migrate_func(self, old_major_version, old_minor_version, old_data):
            if old_major_version == 1:
                return {**old_data, "migrated": True}
            return await super()._async_migrate_func(old_major_version, old_minor_version, old_data)

    mkey = f"{const.DOMAIN}_{ENTRY_ID}_version_migrating"
    _storage._DISK[mkey] = json.dumps({"v": 1.0})
    _storage._VERSIONS[mkey] = 1

    async def _migrate_load():
        return await asyncio.wait_for(_Migrating(FakeHass(), 2, mkey).async_load(), 5)

    try:
        got = asyncio.run(_migrate_load())
    except BaseException as exc:  # noqa: BLE001 -- a timeout is the measurement
        got = type(exc).__name__
    saved_at = _storage._VERSIONS.get(mkey)
    _storage._DISK.clear()
    _storage._VERSIONS.clear()
    R.check(
        "a store that migrates loads the migrated payload and saves it at its own "
        "version, without waiting on its own read (#1740)",
        got == {"v": 1.0, "migrated": True} and saved_at == 2,
        f"got={got!r} saved_at={saved_at}",
    )
    # The other side of that exemption: a save from any OTHER task still waits
    # for the read in flight (D1-s2-52). The cycle writers wait before building
    # their payload, so they do not pin async_save's own wait; this does.
    wkey = f"{const.DOMAIN}_{ENTRY_ID}_version_writer"
    orig_load = _storage.Store.async_load

    async def _race():
        gate = asyncio.Event()

        async def _gated(self):
            await gate.wait()
            return await orig_load(self)

        _storage.Store.async_load = _gated
        st = QuarantiningStore(FakeHass(), 1, wkey)
        load = asyncio.create_task(st.async_load())
        await asyncio.sleep(0)
        save = asyncio.create_task(st.async_save({"v": 2.0}))
        for _ in range(3):
            await asyncio.sleep(0)
        early = _storage.SAVE_COUNTS.get(wkey, 0)
        gate.set()
        await asyncio.wait_for(asyncio.gather(load, save), 5)
        return early, _storage.SAVE_COUNTS.get(wkey, 0)

    try:
        early, late = asyncio.run(_race())
    except BaseException as exc:  # noqa: BLE001 -- a hang is the measurement
        early, late = type(exc).__name__, None
    finally:
        _storage.Store.async_load = orig_load
        _storage._DISK.clear()
        _storage.SAVE_COUNTS.pop(wkey, None)
    R.check(
        "a save from another task waits for the store's read in flight, and lands after it",
        early == 0 and late == 1,
        f"saves before the read landed={early} after={late}",
    )
    _version_floor_import()
    _version_concurrent_reads()
    print(f"RESULT store_version_unsurfaced={len(unsurfaced)} count")


def _version_floor_import() -> None:
    """``store.py`` imports at the 2025.2.0 floor, where Home Assistant has no
    ``UnsupportedStorageVersionError`` (it arrives in 2026.3).

    The stub defines the class, so every other check here imports a tree the
    floor cannot: the module is executed afresh, beside the live one, with
    the class taken out of the stub -- the floor's shape. An import that
    fails fails every module that persists anything, and the integration
    with them (#1869's nightly-ha 2025.2.0 arm).
    """
    import importlib.util

    name = "heatpump_optimizer._store_at_floor"
    spec = importlib.util.spec_from_file_location(name, PKG / "store.py")
    held = _storage.__dict__.pop("UnsupportedStorageVersionError")
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        got = f"ok:{module.QuarantiningStore.__name__}"
    except Exception as exc:  # noqa: BLE001 -- the failure is the measurement
        got = f"{type(exc).__name__}: {exc}"
    finally:
        _storage.UnsupportedStorageVersionError = held
        sys.modules.pop(name, None)
    R.check(
        "store.py imports at the 2025.2.0 floor, which has no "
        "UnsupportedStorageVersionError (#1869)",
        got == "ok:QuarantiningStore",
        f"got={got}",
    )


def _version_concurrent_reads() -> None:
    """Two reads in flight, and a reader whose read has landed.

    Home Assistant's ``Store.async_load`` parks a second concurrent load on
    the first's future (``_load_future``, 2025.2.0 and since); the stub has no
    such dedupe, so it is wrapped in one here. A migration's write-back from
    the first read must not wait on the second, which waits on the first. And
    once a task's read has landed, that task is a writer like any other: its
    save waits for a read another task has in flight.
    """
    key = f"{const.DOMAIN}_{ENTRY_ID}_version_concurrent"
    orig_load = _storage.Store.async_load

    class _Migrating(QuarantiningStore):
        async def _async_migrate_func(self, old_major_version, old_minor_version, old_data):
            return {**old_data, "migrated": True}

    async def _two_loaders():
        gate, pending = asyncio.Event(), {}

        async def _deduped(self):
            if id(self) in pending:
                return await asyncio.shield(pending[id(self)])
            pending[id(self)] = future = asyncio.get_running_loop().create_future()
            try:
                await gate.wait()
                result = await orig_load(self)
            except BaseException as exc:
                future.set_exception(exc)
                raise
            finally:
                pending.pop(id(self), None)
            future.set_result(result)
            return result

        _storage.Store.async_load = _deduped
        st = _Migrating(FakeHass(), 2, key)
        first = asyncio.create_task(st.async_load())
        await asyncio.sleep(0)
        second = asyncio.create_task(st.async_load())
        await asyncio.sleep(0)
        gate.set()
        return await asyncio.wait_for(asyncio.gather(first, second), 5)

    _storage._DISK[key] = json.dumps({"v": 1.0})
    _storage._VERSIONS[key] = 1
    try:
        got = asyncio.run(_two_loaders())
    except BaseException as exc:  # noqa: BLE001 -- a hang is the measurement
        got = type(exc).__name__
    finally:
        _storage.Store.async_load = orig_load
        _storage._DISK.clear()
        _storage._VERSIONS.clear()
        _storage.SAVE_COUNTS.pop(key, None)
    want = {"v": 1.0, "migrated": True}
    R.check(
        "two concurrent loads of a migrating store both land: the write-back "
        "does not wait on the second read, parked on the first (#1869)",
        got == [want, want],
        f"got={got!r}",
    )

    async def _landed_reader():
        hold, gate, go = {"on": False}, asyncio.Event(), asyncio.Event()

        async def _gated(self):
            if hold["on"]:
                await gate.wait()
            return await orig_load(self)

        _storage.Store.async_load = _gated
        st = QuarantiningStore(FakeHass(), 1, wkey)

        async def _writer():
            await st.async_load()  # this task's own read lands ...
            await go.wait()
            await st.async_save({"v": 2.0})  # ... so this save waits for another's

        writer = asyncio.create_task(_writer())
        for _ in range(3):
            await asyncio.sleep(0)
        hold["on"] = True
        other = asyncio.create_task(st.async_load())
        await asyncio.sleep(0)
        go.set()
        for _ in range(3):
            await asyncio.sleep(0)
        early = _storage.SAVE_COUNTS.get(wkey, 0)
        gate.set()
        await asyncio.wait_for(asyncio.gather(writer, other), 5)
        return early, _storage.SAVE_COUNTS.get(wkey, 0)

    wkey = f"{key}_writer"
    _storage.SAVE_COUNTS.pop(wkey, None)
    try:
        early, late = asyncio.run(_landed_reader())
    except BaseException as exc:  # noqa: BLE001 -- a hang is the measurement
        early, late = type(exc).__name__, None
    finally:
        _storage.Store.async_load = orig_load
        _storage._DISK.clear()
        _storage.SAVE_COUNTS.pop(wkey, None)
    R.check(
        "a task whose read has landed saves after another task's read in flight, "
        "not before it (#1869)",
        early == 0 and late == 1,
        f"saves before the read landed={early} after={late}",
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
        # A string, not float("nan"): json.dumps writes the float as a bare
        # NaN token, which Home Assistant's orjson Store (and the stub, since
        # round-9 D1-s1-51) refuses whole, so the loader would see no store.
        peaks["peaks"] = list(peaks["peaks"]) + ["NaN"]
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
    _instant_arm(by_name)
    _class_arm()
    _domain_arm()
    _kinds_arm()
    _publish_arm()
    _no_rewrap_check()
    _i1_pins_arm()
    _version_arm(by_name)
    return R.close("FINITE BOUNDARY CHECKS")


if __name__ == "__main__":
    sys.exit(_main())
