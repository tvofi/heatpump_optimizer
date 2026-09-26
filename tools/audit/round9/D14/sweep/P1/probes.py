#!/usr/bin/env python3
# Round 9 sweep S3, class P1: one failing probe per dispositioned `instance`
# seam. Each function name is `probe_<id>`; it returns (ok, detail) where
# ok=False means the seam reproduces the defect (the probe FAILS at baseline
# 1936d5ca -- that failure is the fixer's failing test). The fixer imports the
# production symbol directly, per COMMON.md #2.
#
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P1/probes.py
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))


def probe_D1_s1_01_snapshots():
    from custom_components.heatpump_optimizer.snapshots import SnapshotRing
    ring = SnapshotRing.from_dict({"snapshots": [{"taken_at": "2026-01-01T00:00:00"}]})
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    try:
        ring.due(now)
        return True, "due() did not raise on a naive stored taken_at vs an aware now"
    except TypeError as err:
        return False, f"due() raised TypeError: {err}"


def probe_D1_s1_01_curve_learning():
    from custom_components.heatpump_optimizer.curve_learning import CurveLearner
    learner = CurveLearner.from_dict({"last_step_at": "2026-01-01T00:00:00"})
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    try:
        learner._step_down(now)
        return True, "_step_down() did not raise on a naive last_step_at vs an aware now"
    except TypeError as err:
        return False, f"_step_down() raised TypeError: {err}"


def probe_D1_s1_01_comfort_learning():
    from custom_components.heatpump_optimizer.comfort_learning import ComfortLearner
    learner = ComfortLearner.from_dict(
        {"configured_weight": 1.0, "learned_weight": 1.0, "evidence": 1.0,
         "overrides": 0, "last_update": "2026-01-01T00:00:00"}, 1.0)
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    try:
        learner._decay(now)
        return True, "_decay() did not raise on a naive last_update vs an aware now"
    except TypeError as err:
        return False, f"_decay() raised TypeError: {err}"


def probe_D1_s1_02_best_restore():
    from custom_components.heatpump_optimizer.snapshots import SnapshotRing
    ring = SnapshotRing.from_dict({"snapshots": [
        {"healthy": True, "taken_at": "2026-01-01T00:00:00",
         "accuracy": {"temperature_bias": "nan"}},
    ]})
    try:
        ring.best_restore()
        return True, "best_restore() did not raise on a non-numeric temperature_bias"
    except TypeError as err:
        return False, f"best_restore() raised TypeError: {err}"


def probe_D1_s2_03_sample_count():
    from custom_components.heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C
    stored = {"capacity_envelope": {"3": [1.0, 2 ** 64]}}
    inst = C.__new__(C)
    inst._capacity_envelope = {}
    try:
        C._load_t4b_learners(inst, stored)
    except Exception as err:  # noqa: BLE001 -- disposition records whichever fires
        return False, f"_load_t4b_learners raised {type(err).__name__}: {err}"
    count = inst._capacity_envelope.get(3, [None, None])[1]
    if isinstance(count, int) and count >= 2 ** 63:
        return False, f"a sample count of {count} loaded with no magnitude guard"
    return True, "sample count was bounded on load"


def probe_D1_s3_03_pump_arbiter():
    import asyncio
    from custom_components.heatpump_optimizer import pump_arbiter as pa

    class _Store:
        async def async_load(self):
            return {"written": {"space": ["not-a-number", "2026-01-01T00:00:00"]}}

    class _Coord:
        pass

    coord = _Coord()
    held = pa.state_for(coord)
    orig_store = pa._store
    pa._store = lambda c: _Store()
    try:
        asyncio.run(pa._load(coord))
    finally:
        pa._store = orig_store
    value, _at = held.written.get("space", (None, None))
    if isinstance(value, str):
        return False, f"held.written['space'][0] loaded as {value!r}, not a set-point float"
    return True, "non-numeric set-point value was rejected on load"


def probe_D1_s3_06_freq_control():
    from custom_components.heatpump_optimizer.freq_control import FrequencyMap
    fmap = FrequencyMap.from_dict({"99": [1e300, 1]})
    if 99 in fmap.buckets and fmap.buckets[99][0] == 1e300:
        return False, "an out-of-range decile (99) and an unbounded ratio (1e300) both loaded"
    return True, "out-of-range decile / unbounded ratio was rejected"


def probe_D1_s4_01_defrost_duty():
    from custom_components.heatpump_optimizer.defrost import DefrostDerate, TEMP_EDGES, HUMIDITY_EDGES
    n_t, n_h = len(TEMP_EDGES) - 1, len(HUMIDITY_EDGES) - 1
    grid = [[float("nan")] * n_h for _ in range(n_t)]
    counts = [[5] * n_h for _ in range(n_t)]
    inst = DefrostDerate.from_dict({"duty": grid, "duty_counts": counts})
    if not math.isfinite(inst.duty[0][0]):
        return False, "a non-finite duty cell loaded unguarded"
    return True, "non-finite duty cell was rejected"


def probe_D1_s4_03_defrost_migration():
    from custom_components.heatpump_optimizer.defrost import DefrostDerate, TEMP_EDGES, HUMIDITY_EDGES
    n_t, n_h = len(TEMP_EDGES) - 1, len(HUMIDITY_EDGES) - 1
    good = [[0.9] * n_h for _ in range(n_t)]
    bad_counts = [[5] * n_h for _ in range(n_t)]
    bad_counts[0][0] = "oops"  # one unreadable cell
    factors = [[0.8] * n_h for _ in range(n_t)]
    inst = DefrostDerate.from_dict({"duty": good, "duty_counts": bad_counts, "factors": factors})
    if inst.migrated and inst.duty != good:
        return False, ("one unreadable duty_counts cell discarded all 12 valid measured "
                        "duty buckets and relabelled the store 'migrated' (pre-v5.3.0)")
    return True, "a single bad cell did not void the whole measured grid"


def probe_D1_s5_02_price_model_residual_var():
    from custom_components.heatpump_optimizer.price_model import PriceShapeModel, HOURS_PER_DAY
    row = [float("nan")] + [1.0] * (HOURS_PER_DAY - 1)
    m = PriceShapeModel.from_dict({"residual_var": [row, [1.0] * HOURS_PER_DAY]})
    if not math.isfinite(m.residual_var[0][0]) is False and m.residual_var[0][0] != row[0]:
        pass
    if math.isnan(row[0]) and m.residual_var[0][0] == 0.0:
        return False, "a NaN residual_var bin silently became 0.0 with no isfinite guard on the field"
    return True, "residual_var bin was finiteness-checked"


def probe_D1_s5_02_tariff_window_factor():
    from custom_components.heatpump_optimizer.tariff import PeakTracker
    t = PeakTracker.from_dict({"window_factor": 1e12})
    if t._window_factor > 100:
        return False, f"window_factor loaded at {t._window_factor} with no domain bound, only isfinite"
    return True, "window_factor was domain-bounded"


def probe_D14_s1_01_legionella_attempt_peak():
    import asyncio
    from custom_components.heatpump_optimizer import legionella as leg

    class _Store:
        async def async_load(self):
            return {"last_cycle": "2026-01-01T00:00:00+00:00",
                    "last_attempt": "2026-01-01T00:00:00+00:00",
                    "last_attempt_peak": float("nan")}

    class _Guard(leg.LegionellaGuard):
        def __init__(self):
            self.store = _Store()
            self.mode_block_notice = None
            self._switch = None

    import types
    g = _Guard.__new__(_Guard)
    g.store = _Store()
    g.mode_block_notice = None
    g.disinfect = types.SimpleNamespace(owned=[])
    g.switch_latched = False
    g.attempt = None
    g.attempt_peak = None
    g.last_cycle = None
    try:
        asyncio.run(leg.LegionellaGuard.async_load(g))
    except Exception as err:  # noqa: BLE001
        return False, f"async_load raised {type(err).__name__}: {err}"
    peak = getattr(g, "attempt_peak", None)
    if isinstance(peak, float) and math.isnan(peak):
        return False, "attempt_peak loaded as NaN with no isfinite guard"
    return True, "attempt_peak was finiteness-checked"


def probe_D14_s1_02_comfort_learning_gate_bypass():
    from custom_components.heatpump_optimizer.comfort_learning import ComfortLearner
    learner = ComfortLearner.from_dict(
        {"configured_weight": float("nan"), "learned_weight": 5.0, "evidence": 5.0,
         "overrides": 0}, 1.0)
    if learner.learned_weight == 5.0:
        return False, ("stored_configured=NaN made 'abs(stored-configured)>1e-6' False, "
                        "bypassing the stale-weight gate instead of discarding it")
    return True, "a NaN configured_weight was rejected before the comparison gate"


def probe_D14_s1_03_comfort_learning_nonfinite_fields():
    from custom_components.heatpump_optimizer.comfort_learning import ComfortLearner
    learner = ComfortLearner.from_dict(
        {"configured_weight": 1.0, "learned_weight": float("inf"),
         "evidence": float("nan"), "overrides": 0}, 1.0)
    bad = [v for v in (learner.learned_weight, learner.evidence) if not math.isfinite(v)]
    if bad:
        return False, f"learned_weight/evidence loaded non-finite with no isfinite guard: {bad}"
    return True, "learned_weight and evidence were finiteness-checked"


PROBES = {k[len("probe_"):]: v for k, v in list(globals().items())
          if k.startswith("probe_") and callable(v)}


def main() -> int:
    failures = 0
    for name, fn in PROBES.items():
        try:
            ok, detail = fn()
        except Exception as err:  # noqa: BLE001
            ok, detail = False, f"probe itself raised {type(err).__name__}: {err}"
        status = "PASS" if ok else "FAIL(instance)"
        print(f"RESULT probe_{name}={status} {detail}")
        if not ok:
            failures += 1
    print(f"RESULT total_probes={len(PROBES)} count")
    print(f"RESULT failing_probes={failures} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
