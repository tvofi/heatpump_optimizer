"""D14 class P1 detector: a non-finite or malformed value crossing a persisted-store boundary.

Metric (one line): p1_escaping_mutants = single-leaf store mutants (store key, leaf or container
path, substitute) for which an exception escapes a real store loader or one of the store's real
downstream consumers (publication, snapshot restore service, every saver), counted over the
whole store roster seeded with a populated healthy payload; p1_poison_mutants = mutants after
which a non-finite number is reachable from the live learned state or the published payload
where the healthy load had none.

Count key: the exception (type) raised by the production loader/consumer call and the value the
production object holds after the load -- never an attribute of the harness's own mutant.

Seam enumeration (the rule, not a list): every Store/QuarantiningStore(...) construction in the
package (AST), every coroutine that reads one (discovered at run time by recording which store
key each loader's async_load touches), and every leaf and container of every store's persisted
payload after a seeding that populates each store through its real writer (snapshot ring taken,
manual plan applied, boost channel held, ledger month and fuse advisor booked, legionella cycle,
arbiter duty). Lists of scalars are sampled at their first and last index (one seam per list).

Substitutes: numeric leaf -> nan, +-inf, "NaN", "Infinity", 1e309, None, "garbage", "12,5", [],
{}; string leaf -> None, 7, 1.5, "garbage", a naive ISO timestamp, a string "false", [], {};
bool leaf -> "false", None, "garbage"; None leaf -> "garbage", 1.5, "NaN", [], {}; container ->
None, "x", 3.0, and the other container kind.

The clock is frozen at an AWARE instant (Europe/Stockholm), as Home Assistant's dt_util.now()
always is; the hastub's default now() is naive, which would make every healthy aware timestamp
the malformed one.

Clean fixture (zero): the healthy seeded payloads through the same loaders and consumers.
Perturbations (in memory):
  --perturb=sanitize   QuarantiningStore's scrub becomes the identity (re-opens R5 D1-05/06,
                       R6 D1-01/02): p1_poison_mutants goes UP.
  --perturb=snapguard  SnapshotRing.best_restore loses its isinstance(accuracy, dict) guard
                       (re-opens R1 D1-05): p1_escaping_mutants goes UP.
Pre-fix trees: run from the root of a `git archive <sha>^` export (cwd = the tree measured).

Run (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s1/p1_store.py
  ... p1_store.py --perturb sanitize | --perturb snapguard | --json <out>
  cd <export of 3511677a^> && PYTHONPATH=tests/hastub python <abs path>/p1_store.py   (pre-fix tree)
Expected at baseline 1936d5ca: see REPORT.md (exact; deterministic counts).
Machine: round-9 box B8 (4 cores, 15 GB, Linux, CPython 3.14.0rc2).
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import ast
import asyncio
import collections
import copy
import dataclasses
import json
import logging
import math
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
ap.add_argument("--tree", default=".")
ap.add_argument("--perturb", default="", choices=["", "sanitize", "snapguard"])
ap.add_argument("--json", default=None)
ap.add_argument("--only", default=None, help="restrict to these store names (comma-separated)")
ap.add_argument("--no-wedge", action="store_true", help="skip the 3-cycle wedge arm (old trees solve slowly)")
ap.add_argument("--barrier", action="store_true",
                help="also measure which escape seams tests/finite_boundary.py's reach arm drives")
ARGS = ap.parse_args()
TREE = Path(ARGS.tree).resolve()
# tests/harness.py inserts the RELATIVE paths "tests" and "custom_components", so the package
# measured is always the one under the working directory: measure another tree from its root.
if TREE != Path.cwd().resolve():
    sys.exit(f"run from the tree under measurement: cd {TREE} && PYTHONPATH=tests/hastub python <this file>")
for sub in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(TREE / sub))
logging.disable(logging.CRITICAL)
PKG = TREE / "custom_components" / "heatpump_optimizer"
_T0P, _T0T = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # type: ignore  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402

NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("Europe/Stockholm"))
ENTRY_ID = "test_entry"


# ---------------------------------------------------------------------------
# Seam rule 1: every store construction in the package
# ---------------------------------------------------------------------------
def store_constructions() -> list[str]:
    out = []
    for p in sorted(PKG.rglob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("Store", "QuarantiningStore"):
                out.append(f"{p.name}:{n.lineno}:{n.func.id}")
    return out


# ---------------------------------------------------------------------------
# Perturbations
# ---------------------------------------------------------------------------
if ARGS.perturb == "sanitize":
    try:
        from heatpump_optimizer import store as _st
        _st._sanitize = lambda v: v
    except ImportError:
        pass
if ARGS.perturb == "snapguard":
    from heatpump_optimizer import snapshots as _sn

    def _best_restore_unguarded(self):
        for snap in reversed(self.snapshots):
            if not snap.get("healthy"):
                continue
            if snap.get("alarmed_at_capture"):
                continue
            bias = (snap.get("accuracy") or {}).get("temperature_bias")
            if bias is not None and (not np.isfinite(bias) or abs(float(bias)) > _sn.BIAS_BAND_C):
                continue
            return snap
        return None
    _sn.SnapshotRing.best_restore = _best_restore_unguarded


# ---------------------------------------------------------------------------
# Coordinator, seeding, loaders, consumers
# ---------------------------------------------------------------------------
CFG = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_tank_volume": 180.0,
    "comfort_learning_enabled": True,
    "system_identification_enabled": True,
    "away_enabled": True,
    "price_entity": "sensor.prices",
    "price_source": "entity",
}


def build_coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    top = NOW.replace(minute=0, second=0, microsecond=0)
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (top + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
        for h in range(48)]}))
    entry = FakeEntry(data=dict(CFG))
    coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    return coord


def _zero_arg(fn) -> bool:
    import inspect
    try:
        return not [p for p in inspect.signature(fn).parameters.values()
                    if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
    except (TypeError, ValueError):
        return False


def _try(label, fn, notes):
    try:
        r = fn()
        if asyncio.iscoroutine(r):
            asyncio.run(r)
    except Exception as exc:  # seeding is best effort across trees
        notes.append(f"{label}: {type(exc).__name__}: {exc}"[:160])


def seed() -> tuple[dict, list[str]]:
    _storage._DISK.clear()
    notes: list[str] = []
    coord = build_coord()
    import importlib
    t0 = datetime(2026, 1, 14, 12, 0, 0, tzinfo=NOW.tzinfo)
    _try("ledger.add", lambda: coord._ledger.add(t0, "savings_baseline", kwh=2.0, sek=3.0), notes)
    _try("ledger.meta", lambda: coord._ledger.observe_meta_mean(t0, "spot_price", 1.25), notes)
    _try("draws", lambda: coord._dhw_learner.draw_stats.reservoirs.__setitem__("morning", [1.5, 2.5]), notes)

    def _peaks():
        tariff = coord._capacity_tariff()
        for h, kw in ((6, 9.0), (7, 8.0), (30, 7.0), (31, 3.0)):
            coord._peak_tracker.observe(datetime(2026, 1, 1, tzinfo=NOW.tzinfo) + timedelta(hours=h), kw, tariff)
    _try("peaks", _peaks, notes)

    def _fuse():
        coord._fuse_advisor = {"month": "2026-01", "current_fuse_a": 25, "candidate_fuse_a": 20,
                               "candidate_kw": 13.8, "feasible": True, "comfort_shortfall_c": 0.0,
                               "worst_margin_kw": 2.5, "cost_delta_sek_month": -30.0}
        coord._fuse_advisor_at = t0
    _try("fuse", _fuse, notes)

    def _manual():
        from heatpump_optimizer import manual_plan as mp
        ov = mp.build_override(
            dhw_slots=[{"start": (NOW + timedelta(hours=2)).isoformat(), "end": (NOW + timedelta(hours=3)).isoformat()}],
            space_slots=[{"start": (NOW + timedelta(hours=1)).isoformat(), "end": (NOW + timedelta(hours=4)).isoformat()}],
            expires_at=NOW + timedelta(hours=10), now=NOW)
        coord._manual_override = ov
    _try("manual", _manual, notes)

    def _legion():
        coord._legionella.last_cycle = t0
        coord._legionella.attempt = t0
        coord._legionella.attempt_peak = 2.0
    _try("legionella", _legion, notes)

    def _snap():
        coord._snapshot_ring.take(t0, coord._learner_snapshot_payloads(), coord._accuracy.summary(), True)
    _try("snapshot", _snap, notes)

    for name in sorted(dir(coord)):
        if name.startswith("_async_save_") and _zero_arg(getattr(coord, name)):
            _try(name, getattr(coord, name), notes)
    for obj, meths in ((getattr(coord, "_dhw_learner", None), ("async_save_profile", "async_save_draws")),
                       (getattr(coord, "_legionella", None), ("async_save",))):
        for m in meths:
            if obj is not None and hasattr(obj, m):
                _try(m, getattr(obj, m), notes)

    def _boost():
        boost = importlib.import_module("heatpump_optimizer.boost")
        boost.held_for(coord).set("dhw", True, NOW)
        return boost.persist(coord)
    _try("boost", _boost, notes)

    def _away():
        away = importlib.import_module("heatpump_optimizer.away")
        st = coord._away_state
        st.override_active = True
        st.override_return_iso = (NOW + timedelta(hours=20)).isoformat()
        st.migrated_helpers = True
        return away.persist_override(coord)
    _try("away", _away, notes)

    def _arb():
        pa = importlib.import_module("heatpump_optimizer.pump_arbiter")
        held = pa.state_for(coord)
        held.written["dhw_setpoint"] = (55.0, t0)
        return pa._persist(coord)
    _try("arbiter", _arb, notes)
    disk = {k: json.loads(v) for k, v in _storage._DISK.items()}
    _storage._DISK.clear()
    return disk, notes


def loaders(coord) -> dict:
    import importlib
    out = {}
    for name in sorted(dir(type(coord))):
        if name.startswith("_async_load_") and _zero_arg(getattr(coord, name)):
            out[name] = getattr(coord, name)
    for obj, lbl, meths in ((getattr(coord, "_dhw_learner", None), "dhw", ("async_load_profile", "async_load_draws")),
                            (getattr(coord, "_legionella", None), "legionella", ("async_load",))):
        for m in meths:
            if obj is not None and hasattr(obj, m):
                out[f"{lbl}.{m}"] = getattr(obj, m)
    for mod, fn in (("boost", "restore_session"), ("pump_arbiter", "_load")):
        try:
            f = getattr(importlib.import_module(f"heatpump_optimizer.{mod}"), fn)
            out[f"{mod}.{fn}"] = (lambda f=f: f(coord))
        except Exception:
            pass
    return out


_LOAD_KEYS: list[str] = []
_orig_load = _storage.Store.async_load


async def _recording_load(self):
    _LOAD_KEYS.append(getattr(self, "_key", "?"))
    return await _orig_load(self)
_storage.Store.async_load = _recording_load


def loader_map(disk) -> dict[str, list[str]]:
    """store key -> loader names that read it (recorded, not declared)."""
    m: dict[str, list[str]] = collections.defaultdict(list)
    for k, v in disk.items():
        _storage._DISK[k] = json.dumps(v)
    coord = build_coord()
    for name, fn in loaders(coord).items():
        _LOAD_KEYS.clear()
        try:
            asyncio.run(fn())
        except Exception:
            pass
        for k in set(_LOAD_KEYS):
            m[k].append(name)
    _storage._DISK.clear()
    return m


def consumers(coord) -> dict:
    out = {"publish": coord._build_data_dict}
    ring = getattr(coord, "_snapshot_ring", None)
    if ring is not None:
        out["snapshot.best_restore"] = ring.best_restore
    if hasattr(coord, "async_restore_learned_snapshot"):
        out["service.restore_learned_snapshot"] = coord.async_restore_learned_snapshot
    if hasattr(coord, "_roll_month"):
        # the month rollover a month after the booked line (R1 D1-01's consumer)
        out["ledger.roll_month"] = lambda: coord._roll_month(NOW + timedelta(days=45))
    for name in sorted(dir(type(coord))):
        if name.startswith("_async_save_") and _zero_arg(getattr(coord, name)):
            out[name] = getattr(coord, name)
    return out


# ---------------------------------------------------------------------------
# Live-state scan
# ---------------------------------------------------------------------------
_SKIP_ATTRS = {"hass", "entry", "_ctx", "_listeners", "logger", "_debounced_refresh", "config_entry"}


def _walk(obj, label, out, seen, depth=0):
    if depth > 6 or id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str, bytes)):
        return
    if isinstance(obj, (float, np.floating)):
        if not math.isfinite(float(obj)):
            out.add(label)
        return
    if isinstance(obj, np.ndarray):
        try:
            if obj.size and obj.dtype.kind == "f" and not np.all(np.isfinite(obj)):
                out.add(label)
        except Exception:
            pass
        return
    if isinstance(obj, dict):
        for k, v in list(obj.items())[:200]:
            _walk(v, f"{label}[{k}]", out, seen, depth + 1)
        return
    if isinstance(obj, (list, tuple, collections.deque)):
        for i, v in enumerate(list(obj)[:200]):
            _walk(v, f"{label}[{i}]", out, seen, depth + 1)
        return
    if callable(obj) and not hasattr(obj, "__dict__"):
        return
    mod = type(obj).__module__ or ""
    if not mod.startswith("heatpump_optimizer"):
        return
    if dataclasses.is_dataclass(obj):
        items = [(f.name, getattr(obj, f.name, None)) for f in dataclasses.fields(obj)]
    else:
        items = list(getattr(obj, "__dict__", {}).items())
    for k, v in items[:300]:
        if k in _SKIP_ATTRS or k.startswith("__"):
            continue
        _walk(v, f"{label}.{k}", out, seen, depth + 1)


def scan_state(coord) -> set[str]:
    out: set[str] = set()
    seen = {id(coord.hass), id(coord.entry)}
    ctx = getattr(coord, "_ctx", None)
    _walk(getattr(coord, "_thermal_params", None), "params", out, seen)
    items = [(k, v) for k, v in vars(coord).items() if k not in _SKIP_ATTRS]
    for k, v in items:
        _walk(v, f"coord.{k}", out, seen)
    return out


#: Documented non-finite sentinels, not poison: ``peak_threshold_kw`` publishes +inf for
#: "no capacity ceiling yet" (tests/golden.py:capture_coordinator's invariant note).
SENTINELS = {"data[peak_threshold_kw]"}


def scan_pub(data) -> set[str]:
    out: set[str] = set()
    _walk(data, "data", out, set())
    return out - SENTINELS


# ---------------------------------------------------------------------------
NONFIN = [float("nan"), float("inf"), float("-inf"), "NaN", "Infinity", 1e309]
SUBS_NUM = NONFIN + [None, "garbage", "12,5", [], {}]
SUBS_STR = [None, 7, 1.5, "garbage", "2026-01-15T20:00:00", "false", [], {}]
SUBS_BOOL = ["false", None, "garbage"]
SUBS_NONE = ["garbage", 1.5, "NaN", [], {}]
SUBS_DICT = [None, "x", 3.0, []]
SUBS_LIST = [None, "x", 3.0, {}]


def label(v) -> str:
    if isinstance(v, float) and not math.isfinite(v):
        return repr(v)
    if v == 1e309:
        return "1e309"
    return json.dumps(v)


def seams(obj, path=()):
    """(path, current value) for every leaf and every non-root container; scalar lists sampled."""
    out = []
    if isinstance(obj, dict):
        if path:
            out.append((path, obj))
        for k, v in obj.items():
            out.extend(seams(v, path + (k,)))
    elif isinstance(obj, list):
        if path:
            out.append((path, obj))
        idx = range(len(obj))
        if obj and all(not isinstance(x, (dict, list)) for x in obj) and len(obj) > 2:
            idx = [0, len(obj) - 1]
        for i in idx:
            out.extend(seams(obj[i], path + (i,)))
    else:
        out.append((path, obj))
    return out


def subs_for(v):
    if isinstance(v, bool):
        return SUBS_BOOL
    if isinstance(v, (int, float)):
        return SUBS_NUM
    if isinstance(v, str):
        return SUBS_STR
    if v is None:
        return SUBS_NONE
    if isinstance(v, dict):
        return SUBS_DICT
    if isinstance(v, list):
        return SUBS_LIST
    return []


def set_path(obj, path, value):
    cur = obj
    for s in path[:-1]:
        cur = cur[s]
    cur[path[-1]] = value


def run_once(disk, key, mutant, lmap):
    """Load one store's (possibly mutated) payload through its loaders; run the consumers."""
    _storage._DISK.clear()
    _storage._DISK[key] = json.dumps(mutant)
    dt_util.freeze(NOW)
    coord = build_coord()
    ldrs = loaders(coord)
    escapes = []
    for name in lmap.get(key, []):
        try:
            asyncio.run(ldrs[name]())
        except Exception as exc:
            escapes.append(f"loader {name}: {type(exc).__name__}")
    state = scan_state(coord)
    pub = set()
    for cname, fn in consumers(coord).items():
        try:
            r = fn()
            if asyncio.iscoroutine(r):
                r = asyncio.run(r)
            if cname == "publish":
                pub = scan_pub(r)
        except Exception as exc:
            escapes.append(f"consumer {cname}: {type(exc).__name__}")
    state |= scan_state(coord)
    return escapes, state, pub


def wedge(disk, key, mutant, cycles=3) -> int:
    """Failing update cycles out of ``cycles`` with every store healthy but this mutant,
    every discovered loader run first (a restart), through the real _async_update_data."""
    _storage._DISK.clear()
    for k, v in disk.items():
        _storage._DISK[k] = json.dumps(v)
    _storage._DISK[key] = json.dumps(mutant)
    dt_util.freeze(NOW)
    coord = build_coord()
    for _n, fn in loaders(coord).items():
        try:
            asyncio.run(fn())
        except Exception:
            pass
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (NOW + timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(48)]
    coord._weather_forecast = [{"datetime": (NOW + timedelta(hours=h)).isoformat(), "temperature": 2.0,
                                "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0} for h in range(48)]
    coord._solar_radiation_forecast = [0.0] * 48
    fails = 0
    for _ in range(cycles):
        try:
            asyncio.run(coord._async_update_data())
        except Exception:
            fails += 1
    return fails


def barrier_gap(seam_rows, short) -> None:
    """The standing P1 barrier (tests/finite_boundary.py) substitutes only the NUMERIC leaves of
    the payloads its own _healthy_payloads() writes, and drives only the loader and
    _build_data_dict. Count, per store, the leaves it substitutes, and how many of this
    detector's escape seams fall on a leaf it substitutes (hooks finite_boundary:_healthy_payloads
    and finite_boundary:_leaf_paths, the instrument's own enumeration)."""
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import finite_boundary as fb  # type: ignore
        bdisk = fb._healthy_payloads()
    driven: dict[str, set[str]] = {}
    for k, v in bdisk.items():
        paths = set()
        for path, val in fb._leaf_paths(v):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                paths.add("/".join(str(p) if not isinstance(p, int) else "#" for p in path))
        driven[short(k)] = paths
        print(f"RESULT barrier_substituted_leaves_{short(k)}={len(paths)} count")
    hit = {(n, pth) for (n, pth, _e) in seam_rows if pth in driven.get(n, set())}
    print(f"RESULT barrier_driven_escape_seams={len(hit)} count")
    dt_util.freeze(NOW)


def main() -> int:
    dt_util.freeze(NOW)
    sites = store_constructions()
    disk, notes = seed()
    lmap = loader_map(disk)
    short = lambda k: k.replace(f"{const.DOMAIN}_{ENTRY_ID}_", "")
    print(f"# store constructions: {len(sites)}")
    for s in sites:
        print(f"SITE {s}")
    for n in notes:
        print(f"NOTE seed {n}")
    esc_mut = 0
    poison_mut = 0
    total = 0
    per_store = collections.Counter()
    per_store_poison = collections.Counter()
    seam_rows: dict[tuple, set] = collections.defaultdict(set)
    poison_rows: dict[tuple, set] = collections.defaultdict(set)
    clean_esc = 0
    wedge_done: dict = {}
    unread = []
    for key in sorted(disk):
        name = short(key)
        if ARGS.only and name not in ARGS.only.split(","):
            continue
        healthy = disk[key]
        if not lmap.get(key):
            unread.append(name)
            continue
        e0, s0, p0 = run_once(disk, key, copy.deepcopy(healthy), lmap)
        print(f"RESULT seams_{name}={len(seams(healthy))} count")
        clean_esc += len(e0)
        base_state, base_pub = s0, p0
        for path, val in seams(healthy):
            for sub in subs_for(val):
                mutant = copy.deepcopy(healthy)
                try:
                    set_path(mutant, path, sub)
                except (KeyError, IndexError, TypeError):
                    continue
                total += 1
                esc, st, pb = run_once(disk, key, mutant, lmap)
                new_state = st - base_state
                new_pub = pb - base_pub
                pstr = "/".join(str(p) if not isinstance(p, int) else "#" for p in path)
                if esc:
                    if (name, pstr) not in wedge_done:
                        wedge_done[(name, pstr)] = (key, mutant)
                    esc_mut += 1
                    per_store[name] += 1
                    for e in esc:
                        seam_rows[(name, pstr, e)].add(label(sub))
                if new_state or new_pub:
                    poison_mut += 1
                    per_store_poison[name] += 1
                    poison_rows[(name, pstr)].add(label(sub))
    print(f"# stores seeded: {len(disk)}; unread by any discovered loader: {unread}")
    wedged = 0
    for (name, pstr), (key, mutant) in sorted(wedge_done.items()):
        if ARGS.no_wedge:
            break
        f = wedge(disk, key, mutant)
        wedged += f == 3
        print(f"WEDGE store={name} path={pstr} failed_cycles={f}/3")
    # null control for the wedge arm: every store healthy
    k0 = sorted(disk)[0]
    null_wedge = wedge(disk, k0, disk[k0])
    print(f"RESULT wedge_null_control_failed_cycles={null_wedge} count")
    print(f"RESULT p1_wedged_seams={wedged} count")
    for (name, pstr, e), subs in sorted(seam_rows.items()):
        print(f"SEAM escape store={name} path={pstr} {e} subs={sorted(subs)}")
    for (name, pstr), subs in sorted(poison_rows.items()):
        print(f"SEAM poison store={name} path={pstr} subs={sorted(subs)}")
    for name, n in sorted(per_store.items()):
        print(f"RESULT escapes_{name}={n} count")
    for name, n in sorted(per_store_poison.items()):
        print(f"RESULT poison_{name}={n} count")
    tf = (time.process_time() - _T0P) / max(time.thread_time() - _T0T, 1e-9)
    print(f"RESULT store_constructions={len(sites)} count")
    print(f"RESULT stores_seeded={len(disk)} count")
    print(f"RESULT mutants={total} count")
    print(f"RESULT clean_fixture_escapes={clean_esc} count")
    print(f"RESULT p1_escaping_mutants={esc_mut} count")
    print(f"RESULT p1_escape_seams={len({(n, p) for (n, p, _e) in seam_rows})} count")
    print(f"RESULT p1_poison_mutants={poison_mut} count")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")
    if ARGS.barrier:
        barrier_gap(seam_rows, short)
    if ARGS.json:
        Path(ARGS.json).write_text(json.dumps({
            "escape": [[*k, sorted(v)] for k, v in sorted(seam_rows.items())],
            "poison": [[*k, sorted(v)] for k, v in sorted(poison_rows.items())],
            "notes": notes, "sites": sites}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
