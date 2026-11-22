#!/usr/bin/env python3
# Metric: buffer-cooling samples HeatPumpOptimizerCoordinator._async_learn_buffer_cooling folds (and the learned
#   rate's move, degC/h) from one quiet 0.2 h interval, 40.0 -> 39.8 degC, on a live coordinator.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_622996d751dca0c4.py
# EXPECTED RESULT samples_baseline=1 count (rate +0.017208) ; samples_mutant=0 count (rate +0.0)
# EXPECTED RESULT null_delta=0 count  (a 0.5 h interval: above both minimums, folded either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_buffer_cooling
#   (the dt_h gate at coordinator.py:5654 reads BUFFER_COOLING_MIN_SAMPLE_HOURS, coordinator.py:1622); dt_util.now
#   stubbed to two instants dt_h apart, the store save stubbed to a no-op.
# Perturbation: key 622996d751dca0c4, `BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15` -> `= 0.3`, in memory
#   (mock.patch.multiple on the module global). Direction: a 0.15..0.3 h quiet interval folded -> refused.
# Null control: a 0.5 h interval, above both minimums.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
logging.disable(logging.CRITICAL)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


T0 = co.dt_util.now().replace(microsecond=0)


def drive(dt_h, start, end, **patch):
    """One quiet buffer interval of dt_h hours from start to end degC; returns the samples the learner folded."""
    c = coord()
    c._current_action = {"power": 0.0}
    c._last_buffer_temp_sample, c._last_buffer_sample_time = None, None
    c._buffer_heating_since_sample = False
    rate0, n0 = c._buffer_cooling_rate, c._buffer_cooling_samples
    clock = [T0]

    async def nosave():
        return None

    with mock.patch.object(co.dt_util, "now", lambda: clock[0]), \
         mock.patch.object(c, "_async_save_thermal_learning", nosave), \
         mock.patch.multiple(co, **patch) if patch else mock.patch.object(co, "BUFFER_AMBIENT_TEMP", co.BUFFER_AMBIENT_TEMP):
        asyncio.run(c._async_learn_buffer_cooling(start))
        clock[0] = T0 + co.timedelta(hours=dt_h)
        asyncio.run(c._async_learn_buffer_cooling(end))
    return c._buffer_cooling_samples - n0, round(c._buffer_cooling_rate - rate0, 6)


b, m = drive(0.2, 40.0, 39.8), drive(0.2, 40.0, 39.8, BUFFER_COOLING_MIN_SAMPLE_HOURS=0.3)
print(f"RESULT samples_baseline={b[0]} count (rate {b[1]:+.6f})")
print(f"RESULT samples_mutant={m[0]} count (rate {m[1]:+.6f})")
for h in (0.1, 0.15, 0.29, 0.3):
    print(f"RESULT inputs dt_h={h}: baseline={drive(h, 40.0, 39.8)} mutant={drive(h, 40.0, 39.8, BUFFER_COOLING_MIN_SAMPLE_HOURS=0.3)}")
nb, nm = drive(0.5, 40.0, 39.8), drive(0.5, 40.0, 39.8, BUFFER_COOLING_MIN_SAMPLE_HOURS=0.3)
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
