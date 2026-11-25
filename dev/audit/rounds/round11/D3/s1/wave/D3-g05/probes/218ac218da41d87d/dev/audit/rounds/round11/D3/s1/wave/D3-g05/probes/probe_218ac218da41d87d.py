#!/usr/bin/env python3
# Metric: _external_heat_override's value for a fresh numeric flue probe at 29.9, 30.0, 30.1 and 400 C; moved_inputs = readings whose override differs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_218ac218da41d87d.py
# Expected: flue 30.0 C: False -> True; moved_inputs=1 count; tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._external_heat_override (line 5156 `return probe.value > 30.0`).
# Perturbation: `>` -> `>=` (mutant 218ac218da41d87d); direction: a probe at exactly 30.0 C reads as a fire, applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: 29.9, 30.1 and 400 C must not move.
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

from custom_components.heatpump_optimizer.inputs import InputReader
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
ENT = "sensor.flue"


def override(fn, state, cycles=1):
    """_external_heat_override over `cycles` update cycles on one coordinator; (last value, warnings logged)."""
    c = coord({ENT: state} if state is not None else {}, external_heat_entity=ENT if state is not None else "")
    warns = []
    val = None
    with mock.patch.object(co._LOGGER, "warning", lambda *a, **k: warns.append(a[0])):
        for i in range(cycles):
            now = NOW + timedelta(minutes=30 * i)
            reader = InputReader(c.hass, c._config, enabled=True, scale=1.0, now=lambda now=now: now)
            val = fn(c, reader)
    return val, len(warns)


OLD, NEW = "return probe.value > 30.0", "return probe.value >= 30.0"
MUT = mutant_method("_external_heat_override", OLD, NEW)
moved = 0
for v in ("29.9", "30.0", "30.1", "400"):
    b, m = override(CLS._external_heat_override, FakeState(v, unit="°C"))[0], override(MUT, FakeState(v, unit="°C"))[0]
    moved += int(b != m)
    print(f"RESULT flue_{v}C baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count  (null: 29.9, 30.1 and 400 must not move)")
tail()
