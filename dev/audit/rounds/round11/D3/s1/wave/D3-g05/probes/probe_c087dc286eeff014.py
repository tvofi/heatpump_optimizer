#!/usr/bin/env python3
# Metric: ExternalHeatConfig.max_sample_hours _external_heat_config delivers per optimization_interval (10..120 min, step 5, the config flow's range) and whether ExternalHeatDetector.suppressing turns on for a DHW tank rising 4 C/h with the compressor off, sampled once per interval (4 samples).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_c087dc286eeff014.py
# Expected: interval 61/90/120 min: max_sample_hours 1.525/2.25/3.0 -> 1.0 and detector suppressing True -> False; intervals_moved=16 of 23; tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._external_heat_config (line 5083), consumed by external_heat.ExternalHeatDetector._rate (external_heat.py:216).
# Perturbation: `max_sample_hours=max(1.0, 1.5 * interval_hours),` -> `max_sample_hours=(1.0),` (mutant c087dc286eeff014); direction: window shrinks to 1 h, detector blind past 60 min, applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: interval 30 min (the default) and 60 min: both arms 1.0 h and suppressing True (null: max(1, 1.5*0.5)=1.0; at 60 min dt=1.0 is not > 1.0).
# Count key: the value the production method returns or files (never an input attribute). Writes nothing.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
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
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """The coordinator method recompiled from its own source with the one-line mutant, in memory."""
    src = textwrap.dedent(inspect.getsource(getattr(CLS, name)))
    assert src.count(old) == 1, f"anchor {old!r} not unique in {name}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def coord(states=None, **extra):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **extra}
    return CLS(FakeHass(dict(states or {})), FakeEntry(data=cfg))


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")


from dataclasses import replace
from custom_components.heatpump_optimizer.external_heat import ExternalHeatDetector, ExternalHeatObservation
OLD, NEW = "max_sample_hours=max(1.0, 1.5 * interval_hours),", "max_sample_hours=(1.0),"
MUT = mutant_method("_external_heat_config", OLD, NEW)


def cfg(fn, minutes):
    return fn(coord(optimization_interval=minutes, wood_furnace_enabled=True, external_heat_detection_enabled=True))


def active_after(conf, minutes, n=4):
    """A DHW tank rising 4 C/h with the compressor off, sampled once per update cycle."""
    det = ExternalHeatDetector(conf)
    t0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    for i in range(n):
        h = i * minutes / 60.0
        det.update(ExternalHeatObservation(now=t0 + timedelta(minutes=i * minutes), dhw_temp=40.0 + 4.0 * h,
                                           buffer_temp=None, commanded_power_kw=0.0, measured_power_kw=0.0))
    return det.suppressing


moved = 0
for minutes in range(10, 125, 5):  # the config flow's own range, _number(10, 120, 5)
    b, m = cfg(CLS._external_heat_config, minutes), cfg(MUT, minutes)
    moved += int(b.max_sample_hours != m.max_sample_hours)
for minutes in (30, 60, 61, 90, 120):
    b, m = cfg(CLS._external_heat_config, minutes), cfg(MUT, minutes)
    print(f"RESULT interval{minutes}_max_sample_hours baseline={b.max_sample_hours} mutant={m.max_sample_hours}")
    print(f"RESULT interval{minutes}_detector_suppressing baseline={active_after(b, minutes)} mutant={active_after(m, minutes)}")
print(f"RESULT intervals_moved={moved} of 23 count")
tail()
