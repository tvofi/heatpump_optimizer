#!/usr/bin/env python3
# Metric: METRIC_953a106a1aa39cee
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_953a106a1aa39cee.py
# Expected: EXPECTED_953a106a1aa39cee
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g02 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB);
#   counts and float values only, no timing (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_buffer_cooling,
#   line 5658 `if buffer_temp > previous_temp:`.
# Perturbation: key 953a106a1aa39cee (GUARD_OFF), `if buffer_temp > previous_temp:` -> `if False:`, applied in memory: the method is recompiled from its own
#   source with that one line replaced and patched onto the class for the mutant arm only (never on disk).
#   DIRECTION_953a106a1aa39cee
# Null control: NULL_953a106a1aa39cee
# Key of the count: the coordinator's own _buffer_cooling_samples / _buffer_cooling_rate after one real
#   _async_learn_buffer_cooling call (features.py's _t2_buffer fixture: FakeHass, frozen clock, quiet interval).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
_cpu0, _th0 = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass  # noqa: E402
import numpy as np  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
FN = "_async_learn_buffer_cooling"
OLD = 'if buffer_temp > previous_temp:'
NEW = 'if False:'
BASE_T = datetime(2026, 2, 1, 3, 0, 0, tzinfo=timezone.utc)


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(getattr(CLS, FN)))
    lines = src.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines) if ln.strip() == OLD]
    assert len(hits) == 1, f"anchor {OLD!r} found {len(hits)} times"
    ln = lines[hits[0]]
    lines[hits[0]] = ln[: len(ln) - len(ln.lstrip())] + NEW + "\n"
    ns = dict(co.__dict__)
    exec(compile("".join(lines), co.__file__, "exec"), ns)
    return ns[FN]


MUT = mutant_fn()


def run(arm, previous_temp, buffer_temp, seconds, volume=None, rate=None):
    """One quiet buffer-cooling interval; returns (samples, rate, saves)."""
    data = {"tibber_token": "x", "weather_entity": "weather.home"}
    if volume is not None:
        data["buffer_tank_volume"] = volume
    c = CLS(FakeHass(), FakeEntry(data=data))
    if rate is not None:
        c._apply_buffer_cooling_rate(rate)
    saves = []

    async def counted():
        saves.append(c._buffer_cooling_rate)

    c._async_save_thermal_learning = counted
    c._last_buffer_temp_sample = previous_temp
    c._last_buffer_sample_time = BASE_T
    c._buffer_heating_since_sample = False
    dt_util.freeze(BASE_T + timedelta(seconds=seconds))
    try:
        if arm == "mutant":
            with mock.patch.object(CLS, FN, MUT):
                asyncio.run(c._async_learn_buffer_cooling(buffer_temp))
        else:
            asyncio.run(c._async_learn_buffer_cooling(buffer_temp))
    finally:
        dt_util.freeze(None)
    return c._buffer_cooling_samples, c._buffer_cooling_rate, len(saves)


def observed_of(previous_temp, buffer_temp, seconds):
    """The learner's own expression for the implied rate (for input search only, never a RESULT)."""
    dt_h = (seconds) / 3600.0
    return float(-np.log((buffer_temp - 20.0) / (previous_temp - 20.0)) / dt_h * 25.0)


def exact_end(target, previous_temp=50.0, seconds=3600.0, span=4000):
    """A buffer_temp whose implied rate equals `target` bit-for-bit, searched over neighbouring floats."""
    guess = 20.0 + (previous_temp - 20.0) * float(np.exp(-target * (seconds / 3600.0) / 25.0))
    lo = hi = guess
    for _ in range(span):
        for cand in (lo, hi):
            if observed_of(previous_temp, cand, seconds) == target:
                return cand
        lo, hi = np.nextafter(lo, -np.inf), np.nextafter(hi, np.inf)
    return None


_FRESH = CLS(FakeHass(), FakeEntry(data={{"tibber_token": "x", "weather_entity": "weather.home"}}))
LOW, HIGH = _FRESH._buffer_cooling_bounds()
RATE0 = _FRESH._buffer_cooling_rate
print(f"RESULT bounds_low={{LOW!r}} C/h high={{HIGH!r}} C/h prior={{RATE0!r}} C/h (35 L default tank)")
INPUTS = [("warm_48_50_1h", (48.0, 50.0, 3600.0)), ("warm_ulp", (50.0, float(np.nextafter(50.0, 99.0)), 3600.0)), ("warm_24_90_0p15h", (24.0, 90.0, 540.0)), ("warm_vol0", (48.0, 50.0, 3600.0, 0.0001)), ("warm_vol1e6", (48.0, 50.0, 3600.0, 1e6)), ("warm_to_inf", (50.0, float("inf"), 3600.0)), ("warm_from_minus_inf", (float("-inf"), 50.0, 3600.0)), ("warm_rate_at_floor", (48.0, 50.0, 3600.0, None, 0.0)), ("cool_null", (50.0, 48.0, 3600.0))]

moved = 0
tried = []
for label, args in INPUTS:
    if args is None:
        print(f"RESULT {label}=unconstructible")
        tried.append(label + ":unconstructible")
        continue
    b = run("baseline", *args)
    m = run("mutant", *args)
    d = int(b != m)
    moved += d
    tried.append(label)
    print(f"RESULT {label}_baseline_samples={b[0]} count rate={b[1]!r} saves={b[2]}")
    print(f"RESULT {label}_mutant_samples={m[0]} count rate={m[1]!r} saves={m[2]}")
    print(f"RESULT {label}_moved={d} count")
print(f"RESULT inputs_moved={moved} count of {len(INPUTS)}")
_cpu, _th = time.process_time() - _cpu0, time.thread_time() - _th0
print(f"RESULT thread_factor={_cpu / max(_th, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
except OSError:
    _sw = -1
print(f"RESULT swapins={_sw}")
