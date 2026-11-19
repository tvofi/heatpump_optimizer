#!/usr/bin/env python3
# Metric: the (projection, threshold) pair HeatPumpOptimizerCoordinator._on_power_event hands the peak guard
#   (GuardState.update args proj_eff / threshold_kw) and the guard's resulting `suppressing` flag after 2 events,
#   with a 10 kW fuse, a 5 kW meter reading and a tracker that holds a 3 kW billed peak.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_5e8d48ef.py
# EXPECTED RESULT caseB_enabled_factor0_baseline=(5.0, 10.0) suppressing=False  (months mask excludes July: factor 0)
# EXPECTED RESULT caseB_enabled_factor0_mutant=(0.0, 3.0) suppressing=False     (a zero-factor window judged against the 3 kW peak)
# EXPECTED RESULT caseA_disabled_factor1_baseline=(5.0, 10.0) suppressing=False
# EXPECTED RESULT caseA_disabled_factor1_mutant=(5.0, 3.0) suppressing=True     (disabled tariff's stale peak engages the guard)
# EXPECTED RESULT null_moved=0 count  (enabled+factor1 and disabled+factor0: both operands agree, arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._on_power_event
#   (line 8806 `        if tariff.enabled and factor > 0.0:`), the meter listener registered at coordinator.py:8746.
# Perturbation: `and` -> `or` (mutant 5e8d48eff7e4fa8d), in memory: the method is recompiled from its own source
#   (decorator included, from the module namespace) and attached by mock.patch.object for the mutant arm only.
#   The method is called on a SimpleNamespace carrying only the attributes it reads (no `_ctx`, so _ctx_of(self) is
#   self): real PeakTracker and GuardState, stub publish/_spawn. dt_util.now is patched to two fixed instants 20 s apart.
#   Direction: caseB threshold 10 -> 3 / proj 5 -> 0; caseA suppressing False -> True.
# Reach: caseB (enabled tariff, window with factor 0 via the months mask, tariff.sample_factor tariff.py:138) and
#   caseA (tariff disabled while the tracker still holds peaks restored by PeakTracker.from_dict at coordinator.py:8378)
#   are both production states. Note the disjunction only matters while the tracker has a FINITE threshold
#   (an empty tracker returns inf, which loses the max() either way).
# Null control: enabled with factor 1 and disabled with factor 0 (months mask on a disabled tariff): the two operands
#   agree, so `and` and `or` return the same candidates.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.power_guard import GuardState  # noqa: E402
from custom_components.heatpump_optimizer.tariff import CapacityTariff, PeakTracker  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD = "if tariff.enabled and factor > 0.0:"
NEW = "if tariff.enabled or factor > 0.0:"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(CLS._on_power_event))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns["_on_power_event"]


MUT = mutant_fn()
T0 = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)  # July: a {1} months mask gives factor 0


def drive(fn, tariff):
    tracker = PeakTracker()
    tracker.month, tracker.peaks, tracker.peak_days = "2026-07", [3.0], ["2026-07-01"]
    guard = GuardState()
    seen = []
    real_update = guard.update

    def spy(now, key, proj, thr, margin, *, floor_hold):
        seen.append((round(proj, 6), thr))
        return real_update(now, key, proj, thr, margin, floor_hold=floor_hold)

    guard.update = spy
    me = SimpleNamespace(
        _peak_guard=guard, _peak_tracker=tracker, _guard_last_fold=None,
        _config=SimpleNamespace(peak_guard_margin_kw=0.5),
        _capacity_tariff=lambda: tariff, _fuse_kw=lambda: 10.0, _guard_floor_hold=lambda: False,
        publish=lambda *a, **k: None, _spawn=lambda *a, **k: None, _async_peak_guard_transition=lambda: None,
    )
    event = SimpleNamespace(data={"new_state": SimpleNamespace(state="5.0", attributes={"unit_of_measurement": "kW"})})
    times = iter([T0, T0 + timedelta(seconds=20)])
    with mock.patch.object(co.dt_util, "now", lambda: next(times)):
        for _ in range(2):
            fn(me, event)
    return seen[-1], guard.suppressing


cases = {
    "caseB_enabled_factor0": CapacityTariff(enabled=True, months=frozenset({1})),
    "caseA_disabled_factor1": CapacityTariff(enabled=False),
}
for name, tar in cases.items():
    b, m = drive(CLS._on_power_event, tar), drive(MUT, tar)
    print(f"RESULT {name}_baseline={b[0]} suppressing={b[1]}")
    print(f"RESULT {name}_mutant={m[0]} suppressing={m[1]}")
nulls = (CapacityTariff(enabled=True), CapacityTariff(enabled=False, months=frozenset({1})))
print(f"RESULT null_moved={sum(int(drive(CLS._on_power_event, t) != drive(MUT, t)) for t in nulls)} count")
