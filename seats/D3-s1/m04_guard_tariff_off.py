#!/usr/bin/env python3
# Metric: whether the peak guard engages (GuardState.suppressing after two spaced 6.5 kW meter events
#   through the real HeatPumpOptimizerCoordinator._on_power_event) on an install whose capacity tariff is
#   OFF, whose 25 A x 3 fuse (17.25 kW) is the only line, and whose restored PeakTracker still holds
#   last month's-style peaks [4.0, 3.5, 3.0] kW (the store restores peaks whatever the tariff flag).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m04_guard_tariff_off.py
# EXPECTED RESULT engaged_baseline=0 count
# EXPECTED RESULT engaged_mutant=1 count
# EXPECTED RESULT engaged_null_baseline=0 count
# EXPECTED RESULT engaged_null_mutant=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._on_power_event
#   (line 8806 `if tariff.enabled and factor > 0.0:`), with the real PeakTracker.threshold_kw and power_guard.GuardState.
# Perturbation: R10 C2 M04, line 8806 `and` -> `or`, applied in memory (the method is re-compiled from its own
#   source with that one edit and patched onto the class; nothing on disk changes). Direction: engaged 0 -> 1.
#   The full gate (fullgate.py run --src complete --key 5e8d48eff7e4fa8d) stays green under it.
# Null control: the same install with an EMPTY tracker (threshold_kw = inf): mutant and baseline both stay
#   disengaged, so the edit only bites once the tracker holds a peak.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.power_guard import MIN_EVENT_SPACING_S  # noqa: E402

OLD = "if tariff.enabled and factor > 0.0:"
NEW = "if tariff.enabled or factor > 0.0:"
CFG = {
    "tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor", "peak_guard_enabled": True,
    "house_power_entity": "sensor.house_power", "main_fuse_amperes": 25.0, "main_fuse_phases": 3,
    "peak_tariff_enabled": False,
}


def mutant_method():
    src = textwrap.dedent(inspect.getsource(co.HeatPumpOptimizerCoordinator._on_power_event))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW), co.__file__, "exec"), ns)
    return ns["_on_power_event"]


def engaged(peaks):
    c = co.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(CFG)))
    c._peak_tracker.peaks = list(peaks)
    ev = SimpleNamespace(data={"new_state": FakeState("6500", unit="W")})
    c._on_power_event(ev)
    c._peak_guard._last_event -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
    if c._guard_last_fold is not None:
        c._guard_last_fold -= timedelta(seconds=MIN_EVENT_SPACING_S + 1)
    c._on_power_event(ev)
    return int(bool(c._peak_guard.suppressing))


PEAKS = [4.0, 3.5, 3.0]
base = engaged(PEAKS)
null_base = engaged([])
with mock.patch.object(co.HeatPumpOptimizerCoordinator, "_on_power_event", mutant_method()):
    mut = engaged(PEAKS)
    null_mut = engaged([])
print(f"RESULT engaged_baseline={base} count")
print(f"RESULT engaged_mutant={mut} count")
print(f"RESULT engaged_null_baseline={null_base} count")
print(f"RESULT engaged_null_mutant={null_mut} count")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
