#!/usr/bin/env python3
# Metric: WARNING-or-higher log records and valve write attempts from one _command_valve_target() call in smart_write mode with NO valve write entity configured (the option left unset: None, or saved empty: ''). Count keyed on the records the coordinator's loggers emit.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_466c95cb8978ea1d.py
# EXPECTED RESULT warnings_baseline=0 count
# EXPECTED RESULT warnings_mutant=1 count  (per unset form: None and '')
# EXPECTED RESULT warnings_delta=2 count  (summed over the two unset forms)
# EXPECTED RESULT commanded_delta=0 count
# EXPECTED RESULT null_warnings_delta=0 count  (a configured number entity: both arms write 23.0 once, warn nothing)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._command_valve_target (coordinator.py:7733 `if not entity_id:`)
# Perturbation: `        if not entity_id:` -> `        if False:`. Direction: warnings 0 -> 1 per call (the write is attempted on a None/'' entity, fails inside _valve_write_problem and is latched as a WARNING 'Valve write entity None could not be commanded').
# Null control: mixing_valve_write_entity='number.valve' present in hass: the guard is not taken on either arm.
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

import logging
NAME, OLD, NEW = "_command_valve_target", "if not entity_id:", "if False:"


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


def run(entity):
    extra = {"mixing_valve_mode": "smart_write"}
    if entity is not None:
        extra["mixing_valve_write_entity"] = entity
    c = coord({"number.valve": FakeState("40", unit="°C")}, **extra)
    h = Count()
    root = logging.getLogger("custom_components.heatpump_optimizer")
    root.addHandler(h)
    try:
        asyncio.run(c._command_valve_target())
    finally:
        root.removeHandler(h)
    return h.n, c._valve_commanded_target, len(c.hass.services.calls)


logging.getLogger("custom_components.heatpump_optimizer").setLevel(logging.DEBUG)
logging.getLogger("custom_components.heatpump_optimizer").propagate = False
res = {e: both(NAME, OLD, NEW, lambda e=e: run(e)) for e in (None, "", "number.valve")}
for e in (None, ""):
    print(f"RESULT inputs[{e!r}] baseline={res[e][0]} mutant={res[e][1]}")
print(f"RESULT warnings_baseline={res[None][0][0]} count")
print(f"RESULT warnings_mutant={res[None][1][0]} count")
print(f"RESULT warnings_delta={sum(res[e][1][0] - res[e][0][0] for e in (None, ''))} count")
print(f"RESULT commanded_delta={sum(int(res[e][1][1:] != res[e][0][1:]) for e in (None, ''))} count")
nb, nm = res["number.valve"]
print(f"RESULT null_warnings_delta={nm[0] - nb[0]} count")
print(f"RESULT null_commanded={nb[1]},{nm[1]}")
tail()
