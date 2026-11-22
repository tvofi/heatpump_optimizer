#!/usr/bin/env python3
# Metric: The DHW advisor's recommended_setpoint when a candidate's usable energy equals the heaviest window exactly: a zero-kWh learned heaviest window and a tank minimum equal to a candidate setpoint (usable 0 == heaviest 0).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_feed2751f4116bd1.py
# EXPECTED RESULT recommended_baseline=48 (min 48, zero draws)
# EXPECTED RESULT recommended_mutant=50
# EXPECTED RESULT differing_cells=3 of 8 (min 48, 50, 55 with zero draws)
# EXPECTED RESULT null_delta=0 count (profile-fallback heaviest: no tie)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._dhw_setpoint_sweep (coordinator.py:4464 `meets = usable_kwh >= heaviest`)
# Perturbation: `>=` -> `>`. Direction: at the tie the candidate no longer meets and the recommendation moves up one or more steps.
# Null control: the fresh-install profile heaviest (4.97 kWh): no candidate ties, both arms recommend 60.
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

def sweep_coord(dmin=None, zero_draws=True):
    """A DHW entry with a day of 1.0 prices; ``zero_draws`` gives every demand window a learned draw reservoir
    of twenty zero-kWh occurrences (a window the household never draws in: DrawStats._close appends 0.0)."""
    extra = {"dhw_enabled": True}
    if dmin is not None:
        extra.update(dhw_min_temperature=dmin, dhw_setpoint=60.0)
    c = coord(**extra)
    c._prices = [{"total": 1.0, "start": "x"}] * 24
    if zero_draws:
        for lab in co.labels_for(c._ctx._thermal_params.dhw_demand_windows):
            c._dhw_learner.draw_stats.reservoirs[lab] = [0.0] * 20
    return c


def rec(c, kp=None):
    r = c._dhw_setpoint_sweep(kp)
    return r["recommended_setpoint"], r["covers_heaviest_window"], tuple(x["meets_heaviest_window"] for x in r["candidates"])

NAME, OLD, NEW = "_dhw_setpoint_sweep", "meets = usable_kwh >= heaviest", "meets = usable_kwh > heaviest"
cells = [(d, z) for d in (None, 48.0, 50.0, 55.0) for z in (False, True)]
diff = 0
for d, z in cells:
    b, m = both(NAME, OLD, NEW, lambda d=d, z=z: rec(sweep_coord(d, z)))
    diff += int(b != m)
    print(f"RESULT input min={d} zero_draws={z}: baseline={b} mutant={m}")
b, m = both(NAME, OLD, NEW, lambda: rec(sweep_coord(48.0, True)))
print(f"RESULT recommended_baseline={b[0]}")
print(f"RESULT recommended_mutant={m[0]}")
print(f"RESULT differing_cells={diff} of {len(cells)}")
nb, nm = both(NAME, OLD, NEW, lambda: rec(sweep_coord(48.0, False)))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
