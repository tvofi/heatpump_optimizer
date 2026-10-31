"""Round 5 D1 seat-a: persisted-store corruption fuzzing.

WHAT IT MEASURES (metric definition, one line): for each of the
integration's persisted stores (every production ``Store(`` site), the
harness seeds the stub storage with the HEALTHY payload the production
writers themselves wrote after one clean cycle, applies one seeded mutant
(type swaps, missing keys, NaN/inf, negative/huge numbers, wrong nesting,
truncation, strings where dicts go, whole-payload type swaps), loads it
through the REAL loader (the coordinator's own spawned ``_async_load_*``
tasks on a real asyncio loop), runs TWO bounded update cycles
(``_async_update_data`` with a stubbed-cheap optimize; executor boundary
and everything else real), and counts: loader crashes, cycle crashes
(non-UpdateFailed exceptions), UpdateFailed cycles, mutants whose
WARNING-or-higher failure message REPEATS identically in cycle 2 (the
corruption was not quarantined or reset), and mutants that publish NaN
into ``coordinator.data``.

COMMANDS (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/seat-a/store_fuzz.py            # 200 mutants/store
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/seat-a/store_fuzz.py --healthy  # null control, no corruption
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/seat-a/store_fuzz.py --corrupt-harder  # 3 mutations per mutant

EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1,
CPython 3.11, measured 2026-09-20, seed 20260920): --healthy gives
load_crash=0 cycle_crash=0 repeat_failure=0 nan_publish=0
nonfinite_state=0. The plain sweep: 2400 mutants, load_crash=0,
cycle_crash=0, cycle1_failed=0, cycle2_failed=0, repeat_failure=0,
nan_publish=3, nonfinite_state=14. --quarantine: nonfinite_state=0
(nan_publish=1 residual via CurveLearner, which that arm does not gate).
--corrupt-harder: nan_publish=10, nonfinite_state=25 (direction: up).
Counts are exact for the committed seed; per-mutant wall time is
provisional (shared box, load1 quoted).

SEPARATION OF SEMANTICS: the stub ``Store`` is in-memory and shared by
storage key (class-level dict), which is exactly the seam the fuzz needs:
mutants are written as raw JSON documents (NaN/Infinity included, as
json.dumps/loads round-trip them) and every load goes through the
production loader coroutines. The solve is stubbed CHEAP
(``HeatPumpOptimizer.optimize`` swapped in memory) and the process-pool
route is bypassed in memory (``_await_process`` -> plain executor job),
because 2400 real cold solves do not fit the shared box; the lifecycle
harness (lifecycle_loop.py) exercises the real solve route.
"""
from __future__ import annotations

import asyncio
import gc
import importlib
import json
import logging
import math
import random
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import d1a_lib as L  # noqa: E402  (BLAS thread pin first)

from homeassistant.util import dt as dt_util  # noqa: E402

SEED = 20260920
MUTANTS_PER_STORE = 200

STORE_KEYS = {
    "snapshots": "heatpump_optimizer_{eid}_snapshots",
    "thermal_learning": "heatpump_optimizer_{eid}_thermal_learning",
    "price_model": "heatpump_optimizer_{eid}_price_model",
    "ledger": "heatpump_optimizer_{eid}_ledger",
    "accuracy": "heatpump_optimizer_{eid}_accuracy",
    "energy": "heatpump_optimizer_{eid}_energy",
    "manual_plan": "heatpump_optimizer_{eid}_manual_plan",
    "dhw_profile": "heatpump_optimizer_{eid}_dhw_profile",
    "dhw_draws": "heatpump_optimizer_{eid}_dhw_draws",
    "legionella": "heatpump_optimizer_{eid}_dhw_legionella",
    "boost": "heatpump_optimizer_{eid}_boost",
    "away": "heatpump_optimizer_{eid}_away",
}

EID = "d1a_fuzz"


def result(name: str, value, unit: str = "") -> None:
    line = f"RESULT {name}={value}"
    if unit and unit not in line:
        line += f" {unit}"
    print(line, flush=True)


class PhaseCapture(logging.Handler):
    """Records WARNING+ messages, tagged with the current fuzz phase."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.phase = "load"
        self.by_phase: dict[str, list[str]] = {}

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage().split(":")[0][:70]
        self.by_phase.setdefault(self.phase, []).append(msg)


def normalize(msg: str) -> str:
    return msg.split(":")[0][:70]


# ---------------------------------------------------------------- mutations

SCALARS = [
    "xx", 12.5, -3, 1e308, -1e308, True, None, ["x"], {"x": 1},
    float("nan"), float("inf"), -float("inf"), 0, -1, 10**12,
]


def all_paths(obj, path=()):
    """Every mutable path in a JSON-ish structure."""
    out = [path]
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(all_paths(v, path + (k,)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(all_paths(v, path + (i,)))
    return out


def get_at(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def set_at(obj, path, value):
    if not path:
        return value
    target = obj
    for p in path[:-1]:
        target = target[p]
    target[path[-1]] = value
    return obj


def del_at(obj, path):
    if not path:
        return None
    target = obj
    for p in path[:-1]:
        target = target[p]
    last = path[-1]
    if isinstance(target, list) and isinstance(last, int) and target:
        target.pop(min(last, len(target) - 1))
    elif isinstance(target, dict):
        target.pop(last, None)
    return obj


def mutate(healthy, rng, harder=False):
    """One (or ``harder``: three) seeded mutations on a deep copy."""
    obj = json.loads(json.dumps(healthy))  # deep copy, NaN-safe
    for _ in range(3 if harder else 1):
        choice = rng.randrange(10)
        if choice == 0:  # whole-payload type swap
            return rng.choice([[], "gone", 42, None, True, [1, 2, 3]])
        paths = [p for p in all_paths(obj) if p]
        if not paths:
            return obj
        path = rng.choice(paths)
        try:
            current = get_at(obj, path)
        except (KeyError, IndexError, TypeError):
            continue
        kind = rng.randrange(7)
        if kind == 0:
            obj = set_at(obj, path, rng.choice(SCALARS))
        elif kind == 1:
            obj = del_at(obj, path)
        elif kind == 2 and isinstance(current, list):
            obj = set_at(obj, path, current[: max(0, len(current) // 2)])
        elif kind == 3 and isinstance(current, dict):
            obj = set_at(obj, path, {"nested": current})
        elif kind == 4 and isinstance(current, (int, float)) and not isinstance(current, bool):
            obj = set_at(obj, path, rng.choice([float("nan"), float("inf"), -1e308, 10**15, -10.0]))
        elif kind == 5:
            obj = set_at(obj, path, "a string where structure goes")
        else:
            obj = set_at(obj, path, rng.choice(SCALARS))
    return obj


# ------------------------------------------------------------------ walking

def walk_nan(value, out, path="data"):
    if isinstance(value, float) and math.isnan(value):
        out.append(path)
    elif isinstance(value, dict):
        for k, v in value.items():
            walk_nan(v, out, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            walk_nan(v, out, f"{path}[{i}]")


def learned_state_snapshot(coord) -> dict:
    """The loaded learned values the real solve and the publishers read."""
    out: dict = {}
    for attr in (
        "_house_heat_loss_scale", "_buffer_cooling_rate", "_cop_scale",
        "_lower_floor_loss_ratio", "_house_heat_loss_samples",
        "_buffer_cooling_samples", "_cop_samples", "_operation_score",
    ):
        out[attr] = getattr(coord, attr, None)
    out["energy_totals"] = getattr(coord, "_energy_totals", None)
    out["score_day"] = getattr(coord, "_score_day", None)
    learner = getattr(coord, "_dhw_learner", None)
    if learner is not None:
        for attr in (
            "cooling_rate", "cooling_samples", "hourly_profile",
            "profile_weekday", "profile_weekend", "daytype_samples",
        ):
            out[f"dhw.{attr}"] = getattr(learner, attr, None)
        out["dhw.draw_stats"] = getattr(getattr(learner, "draw_stats", None), "as_dict", lambda: None)()
    params = getattr(coord, "_thermal_params", None) or getattr(
        getattr(coord, "_ctx", None), "_thermal_params", None
    )
    if params is not None:
        for k, v in vars(params).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out[f"params.{k}"] = v
    for name in ("_peak_tracker", "_defrost", "_comfort_learner", "_accuracy"):
        obj = getattr(coord, name, None)
        if obj is not None:
            for k, v in vars(obj).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    out[f"{name}.{k}"] = v
    return out


def nonfinite_state(snapshot: dict) -> list[str]:
    bad: list[str] = []

    def _walk(v, path):
        if isinstance(v, float) and not math.isfinite(v):
            bad.append(path)
        elif isinstance(v, dict):
            for k, vv in v.items():
                _walk(vv, f"{path}.{k}")
        elif isinstance(v, (list, tuple)):
            for i, vv in enumerate(v):
                _walk(vv, f"{path}[{i}]")

    for k, v in snapshot.items():
        _walk(v, k)
    return bad


# ------------------------------------------------------------- fast solve

class _FastSolve:
    """In-memory cheap optimize seam (restored on exit)."""

    def __init__(self) -> None:
        self.saved_optimize = None
        self.saved_await_process = None

    def install(self, optimizer_cls, coord_mod) -> None:
        from heatpump_optimizer.optimizer import OptimizationResult
        from datetime import timedelta

        def fast_optimize(self_, state, prices, outdoor, wind, precip, solar,
                          start_time, *args, **kwargs):
            n = max(1, len(prices))
            return OptimizationResult(
                power_schedule=[1.0] * n,
                room_temp_trajectory=[21.0] * (n + 1),
                slab_temp_trajectory=[22.0] * (n + 1),
                timestamps=[start_time + timedelta(hours=0.25 * i) for i in range(n)],
                prices=[float(p) for p in prices],
                predicted_cost=1.0,
                baseline_cost=1.0,
                predicted_savings=0.0,
                savings_percentage=0.0,
                optimal_setpoints=[21.0] * n,
                status="ok",
            )

        self.saved_optimize = optimizer_cls.optimize
        optimizer_cls.optimize = fast_optimize

        async def fast_route(hass, fn, *args):
            return await hass.async_add_executor_job(fn, *args)

        self.saved_await_process = coord_mod._await_process
        coord_mod._await_process = fast_route

    def restore(self, optimizer_cls, coord_mod) -> None:
        if self.saved_optimize is not None:
            optimizer_cls.optimize = self.saved_optimize
        if self.saved_await_process is not None:
            coord_mod._await_process = self.saved_await_process


async def one_mutant(healthy_all, key, mutant_doc, storage, coord_mod):
    """Load through the real loaders, run two bounded cycles. Metrics dict."""
    from harness import FakeEntry

    storage._DISK.clear()
    storage.SAVE_COUNTS.clear()
    for k, v in healthy_all.items():
        storage._DISK[k] = json.dumps(v)
    storage._DISK[key] = json.dumps(mutant_doc)

    cap = PhaseCapture()
    logging.getLogger().addHandler(cap)
    m = {
        "load_crash": None, "cycle1_crash": None, "cycle2_crash": None,
        "cycle1_failed": False, "cycle2_failed": False,
        "warn1": set(), "warn2": set(), "nan_paths": [],
        "nonfinite_state": [],
    }
    hass = L.LoopHass()
    L.seed_states(hass)
    entry = FakeEntry(data=L.base_config(EID), entry_id=EID)
    hass.bind_loop(asyncio.get_running_loop())
    cap.phase = "load"
    try:
        coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
        loaders = [t for t in hass.tasks if not t.done()]
        if loaders:
            done, pending = await asyncio.wait(loaders, timeout=30)
            for t in list(done) + list(pending):
                if not t.cancelled() and t.exception() is not None:
                    m["load_crash"] = repr(t.exception())[:120]
                    if pending:
                        for p in pending:
                            p.cancel()
    except Exception as err:  # constructor itself
        m["load_crash"] = repr(err)[:120]
        coord = None
    if coord is not None:
        m["nonfinite_state"] = nonfinite_state(learned_state_snapshot(coord))
        cap.phase = "cycle1"
        try:
            payload1 = await coord._async_update_data()
        except Exception as err:
            if type(err).__name__ == "UpdateFailed":
                m["cycle1_failed"] = True
            else:
                m["cycle1_crash"] = repr(err)[:120]
        nan_out: list[str] = []
        try:
            walk_nan(payload1 or {}, nan_out)
        except Exception:
            pass
        m["nan_paths"] = nan_out[:3]
        cap.phase = "cycle2"
        try:
            payload2 = await coord._async_update_data()
        except Exception as err:
            if type(err).__name__ == "UpdateFailed":
                m["cycle2_failed"] = True
            else:
                m["cycle2_crash"] = repr(err)[:120]
        nan_out2: list[str] = []
        try:
            walk_nan(payload2 or {}, nan_out2)
        except Exception:
            pass
        m["nan_paths"] = (m["nan_paths"] or nan_out2[:3])
        # Let fire-and-forget saves land before the loop closes.
        for _ in range(4):
            await asyncio.sleep(0)
        pending = [t for t in hass.tasks if not t.done()]
        if pending:
            await asyncio.wait(pending, timeout=10)
            for t in pending:
                t.cancel()
        m["entry_released"] = coord._entry_released
        try:
            await coord.async_shutdown()
        except Exception:
            pass
    await hass.shutdown_executor()
    logging.getLogger().removeHandler(cap)
    m["warn1"] = set(cap.by_phase.get("cycle1", []))
    m["warn2"] = set(cap.by_phase.get("cycle2", []))
    m["warn_load"] = set(cap.by_phase.get("load", []))
    m["repeat"] = sorted(m["warn1"] & m["warn2"])
    return m


async def build_healthy(coord_mod) -> dict:
    """Run one clean cycle and force every production writer to save."""
    from harness import FakeEntry
    from homeassistant.helpers import storage as storage_mod
    import heatpump_optimizer.boost as boost_mod
    import heatpump_optimizer.away as away_mod
    from heatpump_optimizer.manual_plan import ManualOverride

    storage_mod._DISK.clear()
    hass = L.LoopHass()
    L.seed_states(hass)
    entry = FakeEntry(data=L.base_config(EID), entry_id=EID)
    hass.bind_loop(asyncio.get_running_loop())
    fast = _FastSolve()
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    fast.install(HeatPumpOptimizer, coord_mod)
    try:
        coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
        loaders = [t for t in hass.tasks if not t.done()]
        if loaders:
            await asyncio.wait(loaders, timeout=30)
        await coord._async_update_data()
        # Force every writer so each store's healthy shape is real.
        await coord._async_save_thermal_learning()
        await coord._async_save_price_model()
        await coord._async_save_ledger()
        await coord._async_save_accuracy()
        await coord._async_save_energy_totals()
        await coord._async_save_snapshots()
        await coord._dhw_learner.async_save_profile()
        await coord._dhw_learner.async_save_draws()
        await coord._legionella.async_save()
        await boost_mod.set_channel(coord, "dhw", True)
        await boost_mod.persist(coord)
        import datetime as _dt
        away_mod.apply_override_payload(
            coord._away_state,
            {
                "active": True,
                "return_time": (L.START + _dt.timedelta(hours=12)).isoformat(),
                "migrated_helpers": True,
            },
        )
        await away_mod.persist_override(coord)
        coord._manual_override = ManualOverride(
            space_slots=[
                (L.START + _dt.timedelta(hours=1), L.START + _dt.timedelta(hours=3))
            ],
            dhw_slots=None,
            expires_at=L.START + _dt.timedelta(hours=12),
            created_at=L.START,
        )
        await coord._async_save_manual_plan()
        pending = [t for t in hass.tasks if not t.done()]
        if pending:
            await asyncio.wait(pending, timeout=10)
        await coord.async_shutdown()
        await hass.shutdown_executor()
    finally:
        fast.restore(HeatPumpOptimizer, coord_mod)
    healthy = {}
    for k, doc in storage_mod._DISK.items():
        healthy[k] = json.loads(doc)
    return healthy


def install_quarantine() -> list:
    """In-memory one-line-fix simulation: isfinite gates at the three seams.

    Returns restore callables. This is the perturbation arm: under these
    gates the loaded-learned-state non-finite count must drop to zero.
    """
    import numpy as np
    from heatpump_optimizer.dhw_learning import DhwProfileLearner
    from heatpump_optimizer.dhw_draws import DrawStats
    from heatpump_optimizer.tariff import PeakTracker

    restores = []

    orig_norm = DhwProfileLearner.normalize_profile

    def gated_normalize(self, profile):
        if len(profile) != 24:
            return self._params.dhw_hourly_draw_pattern.copy()
        if not all(
            isinstance(v, (int, float)) and np.isfinite(np.float64(v))
            for v in profile
        ):
            return self._params.dhw_hourly_draw_pattern.copy()
        return orig_norm(self, profile)

    DhwProfileLearner.normalize_profile = gated_normalize
    restores.append(lambda: setattr(DhwProfileLearner, "normalize_profile", orig_norm))

    orig_draws = DrawStats.from_dict.__func__

    @classmethod
    def gated_draws(cls, data):
        stats = orig_draws(cls, data)
        if not math.isfinite(stats._open_kwh):
            stats._open_kwh = 0.0
        return stats

    DrawStats.from_dict = gated_draws
    restores.append(lambda: setattr(DrawStats, "from_dict", orig_draws))

    orig_peak = PeakTracker.from_dict.__func__

    @classmethod
    def gated_peak(cls, data):
        tracker = orig_peak(cls, data)
        tracker.peaks = [p for p in tracker.peaks if math.isfinite(p)]
        for attr in ("_window_sum", "_window_wsum", "_window_weight", "_window_factor"):
            v = getattr(tracker, attr)
            if not math.isfinite(v):
                setattr(tracker, attr, 0.0 if attr != "_window_factor" else 1.0)
        return tracker

    PeakTracker.from_dict = gated_peak
    restores.append(lambda: setattr(PeakTracker, "from_dict", orig_peak))
    return restores


async def main() -> int:
    dt_util.freeze(L.START)
    rng = random.Random(SEED)
    healthy_mode = "--healthy" in sys.argv
    harder = "--corrupt-harder" in sys.argv
    quarantine = "--quarantine" in sys.argv

    coord_mod = importlib.import_module("heatpump_optimizer.coordinator")
    from homeassistant.helpers import storage as storage_mod
    from heatpump_optimizer.optimizer import HeatPumpOptimizer

    healthy = await build_healthy(coord_mod)
    missing = [n for n, tpl in STORE_KEYS.items() if tpl.format(eid=EID) not in healthy]
    result("stores_enumerated", len(STORE_KEYS))
    result("stores_with_healthy_payload", len(STORE_KEYS) - len(missing))
    if missing:
        result("stores_missing_payload", "|".join(missing))

    fast = _FastSolve()
    fast.install(HeatPumpOptimizer, coord_mod)
    restores = install_quarantine() if quarantine else []

    totals = {
        "mutants": 0, "load_crash": 0, "cycle_crash": 0,
        "update_failed_repeat": 0, "repeat_failure": 0, "nan_publish": 0,
        "cycle1_failed": 0, "cycle2_failed": 0, "nonfinite_state": 0,
    }
    per_store: dict[str, dict] = {}
    examples: dict[str, list] = {}
    t0 = time.monotonic()
    proc0, thr0 = time.process_time(), time.thread_time()

    try:
        for name, tpl in STORE_KEYS.items():
            key = tpl.format(eid=EID)
            base = healthy.get(key)
            if base is None:
                continue
            counts = {k: 0 for k in totals}
            counts["mutants"] = 0
            for i in range(MUTANTS_PER_STORE):
                if healthy_mode:
                    doc = json.loads(json.dumps(base))
                else:
                    doc = mutate(base, rng, harder=harder)
                m = await one_mutant(healthy, key, doc, storage_mod, coord_mod)
                counts["mutants"] += 1
                if m["load_crash"]:
                    counts["load_crash"] += 1
                if m["cycle1_crash"] or m["cycle2_crash"]:
                    counts["cycle_crash"] += 1
                if m["cycle1_failed"]:
                    counts["cycle1_failed"] += 1
                if m["cycle2_failed"]:
                    counts["cycle2_failed"] += 1
                if (m["cycle1_failed"] and m["cycle2_failed"]
                        and m["cycle1_failed"] == m["cycle2_failed"]):
                    counts["update_failed_repeat"] += 1
                if m["repeat"]:
                    counts["repeat_failure"] += 1
                    ex = examples.setdefault(name, [])
                    if len(ex) < 4:
                        ex.append({"msg": m["repeat"][0][:70],
                                   "load_crash": m["load_crash"],
                                   "c1": m["cycle1_crash"], "c2": m["cycle2_crash"],
                                   "doc": json.dumps(doc)[:220]})
                if m["nan_paths"]:
                    counts["nan_publish"] += 1
                    ex = examples.setdefault(name + ":nan", [])
                    if len(ex) < 3:
                        ex.append({"paths": m["nan_paths"],
                                   "doc": json.dumps(doc)[:220]})
                if m["nonfinite_state"]:
                    counts["nonfinite_state"] += 1
                    ex = examples.setdefault(name + ":state", [])
                    if len(ex) < 4:
                        ex.append({"paths": m["nonfinite_state"][:4],
                                   "doc": json.dumps(doc)[:220]})
            per_store[name] = counts
            print(
                f"  {name}: mutants={counts['mutants']} "
                f"load_crash={counts['load_crash']} "
                f"cycle_crash={counts['cycle_crash']} "
                f"c1_failed={counts['cycle1_failed']} c2_failed={counts['cycle2_failed']} "
                f"repeat={counts['repeat_failure']} nan={counts['nan_publish']} "
                f"badstate={counts['nonfinite_state']}",
                flush=True,
            )
            for k in ("load_crash", "cycle_crash", "repeat_failure", "nan_publish",
                      "cycle1_failed", "cycle2_failed", "update_failed_repeat",
                      "nonfinite_state"):
                totals[k] += counts[k]
            totals["mutants"] += counts["mutants"]
    finally:
        fast.restore(HeatPumpOptimizer, coord_mod)
        for restore in restores:
            restore()
        dt_util.freeze(None)

    wall = time.monotonic() - t0
    for k, v in totals.items():
        result(k, v)
    conds = L.box_conditions()
    result("wall_s", round(wall, 1), "s")
    result("thread_factor", round(
        (time.process_time() - proc0 - (0.0)) / max(1e-9, time.thread_time() - thr0), 3))
    result("load1", conds["load1"])
    result("concurrent_test_processes", conds["concurrent_test_processes"])
    result("seed", SEED)

    out = {"totals": totals, "per_store": per_store, "examples": examples}
    with open(_HERE / "store_fuzz_results.json", "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
