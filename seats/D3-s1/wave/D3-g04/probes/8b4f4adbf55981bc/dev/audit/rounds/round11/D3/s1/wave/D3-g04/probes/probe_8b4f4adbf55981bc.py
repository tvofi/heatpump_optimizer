#!/usr/bin/env python3
# Metric: Count of reachable _weather_forecast values on which _current_humidity() differs between arms. The attribute is a list from __init__ (coordinator.py:3725) and is only ever assigned a non-empty list (7076) or a fabricated one (7111); the arms differ only on a non-iterable (None), which raises under the mutant.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_8b4f4adbf55981bc.py
# EXPECTED RESULT init_type=list
# EXPECTED RESULT differing_reachable=0 count  ([], [{}], [{'humidity': None}], [{'humidity': 80}], a timestamped list)
# EXPECTED RESULT differing_unreachable=1 count  (None: baseline None, mutant raises TypeError)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._current_humidity (coordinator.py:9931 `if not self._weather_forecast:`)
# Perturbation: `if not self._weather_forecast:` -> `if False:`. Direction: on [] the loop runs zero times and best stays None: same None; only None raises.
# Null control: a forecast with humidity 80: both arms 80.0.
# Run from the repository root; the mutant is applied in memory (the method recompiled from its own
# source with the one line replaced, patched onto the class for the mutant arm only).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock

# The repository root is the working directory (the harness contract): the probe imports
# production from there, so a gate mutating the tree it is stored in never leaks into it.
ROOT = Path.cwd()
assert (ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
_T0, _C0 = time.thread_time(), time.process_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
C = co.HeatPumpOptimizerCoordinator


def mutant(name, old, new):
    """The method recompiled from its own source with the one-line mutant applied."""
    src = textwrap.dedent(inspect.getsource(getattr(C, name)))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return C(FakeHass(dict(states or {})), FakeEntry(data={**BASE_CFG, **extra}))


def both(name, old, new, fn):
    """fn() on the baseline and under the mutant; an exception is the value (its type name)."""
    def run():
        try:
            return fn()
        except Exception as err:  # noqa: BLE001 - a raise is an observable outcome
            return f"raises {type(err).__name__}"
    base = run()
    with mock.patch.object(C, name, mutant(name, old, new)):
        mut = run()
    return base, mut


def tail():
    thread = time.thread_time() - _T0
    proc = time.process_time() - _C0
    print(f"RESULT thread_factor={proc / thread if thread > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")][0].split()[1]
    except Exception:  # noqa: BLE001
        swap = "na"
    print(f"RESULT swapins={swap}")

NAME, OLD, NEW = "_current_humidity", "if not self._weather_forecast:", "if False:"
c0 = coord()
print(f"RESULT init_type={type(c0._weather_forecast).__name__}")
now = co.dt_util.now()
reach = [[], [{}], [{"humidity": None}], [{"humidity": 80}],
         [{"datetime": now.isoformat(), "humidity": 55}, {"datetime": now.replace(year=now.year + 1).isoformat(), "humidity": 90}]]


def hum(fc):
    c = coord()
    c._weather_forecast = fc
    return c._current_humidity()


diff = 0
for fc in reach:
    b, m = both(NAME, OLD, NEW, lambda fc=fc: hum(fc))
    diff += int(b != m)
    print(f"RESULT input {fc!r}: baseline={b} mutant={m}")
ub, um = both(NAME, OLD, NEW, lambda: hum(None))
print(f"RESULT input None: baseline={ub} mutant={um}")
print(f"RESULT differing_reachable={diff} count")
print(f"RESULT differing_unreachable={int(ub != um)} count")
tail()
