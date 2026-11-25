#!/usr/bin/env python3
# Metric: what HeatPumpOptimizerCoordinator._on_power_event leaves behind after an event sequence: every
#   (projection, threshold) pair it hands GuardState.update, the guard's `suppressing` flag, the PeakTracker's open
#   window mean (window_snapshot) and its weighted accumulators (_window_wsum, _window_weight), or the exception it
#   raises; key = those delivered values.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_37e281ab084b40ae.py
# Expected: only a zero spacing differs at the line; through production a same-instant event is throttled (GuardState.throttled, MIN_EVENT_SPACING_S = 10 s, and _last_event is stamped on every pass that sets _guard_last_fold), and even when forced through, PeakTracker.observe ignores dt_hours <= 0 (tariff.py:279): moved 0 in every case. Exact (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._on_power_event
#   (coordinator.py:8785), the meter listener registered at coordinator.py:8746.
# Perturbation: mutant 37e281ab084b40ae (CMP_BOUND) `if 0.0 < spacing <= 0.25:` -> `if 0.0 <= spacing <= 0.25:`, compiled in memory from the method's source
#   (the @callback decorator included, from the module namespace).
# Inputs: a SimpleNamespace coordinator carrying only what the method reads (no _ctx): real PeakTracker, GuardState
#   and CapacityTariff; stub publish/_spawn; dt_util.now patched to each event's instant (T0 = 2026-07-15 12:00 UTC
#   plus the offsets in seconds); meter states in kW. Cases in CASES; `force_reach` clears GuardState._last_event
#   before each event, so the throttle cannot hide the line (a state production does not produce: reported apart).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.power_guard import GuardState  # noqa: E402
from custom_components.heatpump_optimizer.tariff import CapacityTariff, PeakTracker  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD, NEW = "if 0.0 < spacing <= 0.25:", "if 0.0 <= spacing <= 0.25:"


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._on_power_event)
T0 = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
MISSING = object()


def ev(state):
    if state is MISSING:
        return SimpleNamespace(data={})
    if state is None:
        return SimpleNamespace(data={"new_state": None})
    return SimpleNamespace(data={"new_state": SimpleNamespace(state=state, attributes={"unit_of_measurement": "kW"})})


def drive(fn, tariff, events, fuse=None, peaks=(), margin=0.5, force_reach=False):
    tracker = PeakTracker()
    if peaks:
        tracker.month, tracker.peaks, tracker.peak_days = "2026-07", list(peaks), ["2026-07-01"] * len(peaks)
    guard = GuardState()
    seen = []
    real_update = guard.update

    def spy(now, key, proj, thr, mg, *, floor_hold):
        seen.append((round(proj, 6), thr))
        return real_update(now, key, proj, thr, mg, floor_hold=floor_hold)

    guard.update = spy
    me = SimpleNamespace(
        _peak_guard=guard, _peak_tracker=tracker, _guard_last_fold=None,
        _config=SimpleNamespace(peak_guard_margin_kw=margin),
        _capacity_tariff=lambda: tariff, _fuse_kw=lambda: fuse, _guard_floor_hold=lambda: False,
        publish=lambda *a, **k: None, _spawn=lambda *a, **k: None, _async_peak_guard_transition=lambda: None,
    )
    last = T0
    try:
        for off, state in events:
            last = T0 + timedelta(seconds=off)
            if force_reach:
                guard._last_event = None
            with mock.patch.object(co.dt_util, "now", lambda t=last: t):
                fn(me, ev(state))
    except Exception as exc:
        return f"raises {type(exc).__name__}"
    _, mean, _, _ = tracker.window_snapshot(last, tariff)
    return (tuple(seen), guard.suppressing, None if mean is None else round(mean, 6),
            round(tracker._window_wsum, 6), round(tracker._window_weight, 6))


TON = CapacityTariff(enabled=True)
CASES = {
    "same_instant_pair": dict(tariff=TON, events=[(0, "4.0"), (0, "6.0")]),
    "same_instant_after_weighted": dict(tariff=TON, events=[(0, "2.0"), (60, "4.0"), (60, "8.0"), (120, "4.0")]),
    "same_instant_forced_reach": dict(tariff=TON, events=[(0, "2.0"), (60, "4.0"), (60, "8.0"), (120, "4.0")], force_reach=True),
    "same_instant_fuse_forced": dict(tariff=TON, fuse=10.0, events=[(0, "9.0"), (0, "9.8"), (0, "9.9")], force_reach=True),
    "backwards_clock_forced": dict(tariff=TON, events=[(60, "4.0"), (0, "8.0"), (120, "4.0")], force_reach=True),
}
NULLS = {"spaced_60s": dict(tariff=TON, events=[(0, "4.0"), (60, "6.0"), (120, "8.0")])}

moved = nmoved = 0
for name, kw in CASES.items():
    b, m = drive(CLS._on_power_event, **kw), drive(MUT, **kw)
    moved += int(b != m)
    print(f"RESULT {name}_baseline={b}")
    print(f"RESULT {name}_mutant={m}")
for name, kw in NULLS.items():
    b, m = drive(CLS._on_power_event, **kw), drive(MUT, **kw)
    nmoved += int(b != m)
    print(f"RESULT null_{name}_baseline={b} mutant={m}")
print(f"RESULT cases_moved={moved} count of {len(CASES)}")
print(f"RESULT null_moved={nmoved} count of {len(NULLS)}")
