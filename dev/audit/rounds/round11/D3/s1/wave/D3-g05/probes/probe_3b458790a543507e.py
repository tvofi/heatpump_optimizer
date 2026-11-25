#!/usr/bin/env python3
# Metric: whether _external_heat_forecast returns None or an array, over detector states reached through ExternalHeatDetector.update with suppressing False; moved_states = states whose return differs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_3b458790a543507e.py
# Expected: moved_states=0 count; positive arm (suppressing, displacement > 0) sum 11.25 kW in both arms; tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._external_heat_forecast (line 5248 `if not self._external_heat.suppressing:`).
# Perturbation: `if not self._external_heat.suppressing:` -> `if False:` (mutant 3b458790a543507e), applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: positive arm: a suppressing detector with free heat, where the guard is not taken in either arm.
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


import numpy as np
from custom_components.heatpump_optimizer.external_heat import ExternalHeatObservation
OLD, NEW = "if not self._external_heat.suppressing:", "if False:"
MUT = mutant_method("_external_heat_forecast", OLD, NEW)
T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def obs(i, override, **kw):
    base = dict(now=T0 + timedelta(minutes=30 * i), dhw_temp=None, buffer_temp=None, commanded_power_kw=0.0,
                measured_power_kw=0.0, override=override, outlet_temp=60.0, wood_top=80.0, wood_bottom=70.0,
                hp_tank_temp=40.0, space_demand_kw=5.0)
    base.update(kw)
    return ExternalHeatObservation(**base)


def states():
    """Detector states where suppressing is False, reached through update() alone."""
    out = {}
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    out["fresh"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, True))            # fire on, displacement > 0
    c._external_heat.update(obs(1, False))           # user says off: deactivate -> fading
    for i in range(2, 12):                            # 5 h later: decay over
        c._external_heat.update(obs(i, False))
    out["after_fire_decayed"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, True))
    c._external_heat.config.enabled = False
    c._external_heat.update(obs(1, None))            # disabled: _reset
    out["disabled_after_fire"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, False))
    out["override_off"] = c
    return out


moved = 0
for name, c in states().items():
    sup = c._external_heat.suppressing
    b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
    same = (b is None and m is None) or (b is not None and m is not None and np.array_equal(b, m))
    moved += int(not same)
    print(f"RESULT {name} suppressing={sup} free_heat_kw={c._external_heat.state.free_heat_kw} "
          f"baseline={'None' if b is None else 'array'} mutant={'None' if m is None else 'array'}")
# positive arm: suppressing with free heat -- the guard is not consulted, both arms build the array
c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
c._external_heat.config.enabled = True
c._external_heat.update(obs(0, True))
b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
print(f"RESULT positive_suppressing sum_baseline={float(np.sum(b)):.4f} sum_mutant={float(np.sum(m)):.4f} kW")
print(f"RESULT moved_states={moved} count")
tail()
