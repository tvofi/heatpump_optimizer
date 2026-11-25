#!/usr/bin/env python3
# Metric: _dhw_mixed_water()'s outcome at shower_flow_lpm = 0 (baseline omits shower_minutes; mutant divides by zero), and whether the options flow lets 0 (or anything below 4) be stored.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_201955bf671ce8aa.py
# EXPECTED RESULT outcome_baseline=no shower_minutes
# EXPECTED RESULT outcome_mutant=raises ZeroDivisionError
# EXPECTED RESULT flow_option_min=4
# EXPECTED RESULT flow_values_refused=3 count (0, -1, 3.9 refused by the option's NumberSelector)
# EXPECTED RESULT differing_reachable=0 count (flow 4..20)
# EXPECTED RESULT null_delta=0 count (flow 8)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._dhw_mixed_water (coordinator.py:4396 `if flow > 0:`)
# Perturbation: `if flow > 0:` -> `if flow >= 0:`. Direction: at flow 0 a ZeroDivisionError instead of an omitted key; identical on 4..20.
# Null control: flow 8 L/min (the default range): both arms the same.
# Reachability: EntryConfig parses shower_flow_lpm with finite_float alone (entry_config.py:193); the bound is the options flow's (config_flow.py:1811, 4..20).
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

from custom_components.heatpump_optimizer import config_flow as cf


def mw(inlet=None, flow=None, tank=55.0):
    """_dhw_mixed_water() on a DHW entry; ``inlet`` sets the coordinator-resolved inlet (dhw_inlet_current)."""
    extra = {"dhw_enabled": True}
    if flow is not None:
        extra["shower_flow_lpm"] = flow
    c = coord(**extra)
    c._ctx._current_state.dhw_temperature = tank
    if inlet is not None:
        c._ctx._thermal_params.dhw_inlet_current = inlet
    return c._dhw_mixed_water()


def field_cfg(key):
    return dict([f for f in cf._OPTION_FIELDS if f.key == key][0].widget.config)


def inlet_reach():
    """The highest inlet production can resolve: the configured mean plus the seasonal amplitude (both
    option maxima), or a live probe, which _dhw_inlet_c refuses above 35 C."""
    cfg_max = field_cfg("dhw_inlet_temp")["max"] + field_cfg("dhw_inlet_seasonal_amplitude")["max"]
    fresh = co.dt_util.utcnow()
    live = {}
    for v in (30.0, 35.0, 35.5, 39.0):
        st = FakeState(str(v), unit="°C")
        for attr in ("last_updated", "last_reported", "last_changed"):
            try:
                setattr(st, attr, fresh)
            except Exception:  # noqa: BLE001
                pass
        live[v] = co._dhw_inlet_c(FakeHass({"sensor.inlet": st}), "sensor.inlet")
    return cfg_max, live

NAME, OLD, NEW = "_dhw_mixed_water", "if flow > 0:", "if flow >= 0:"
b, m = both(NAME, OLD, NEW, lambda: mw(flow=0.0))
print(f"RESULT outcome_baseline={'shower_minutes present' if 'shower_minutes' in b else 'no shower_minutes'}")
print(f"RESULT outcome_mutant={m if isinstance(m, str) else m}")
w = [f for f in cf._OPTION_FIELDS if f.key == "shower_flow_lpm"][0].widget
print(f"RESULT flow_option_min={field_cfg('shower_flow_lpm')['min']}")
refused = 0
for v in (0, -1, 3.9):
    try:
        w(v)
    except Exception:  # noqa: BLE001
        refused += 1
print(f"RESULT flow_values_refused={refused} count")
grid = [4 + x / 2 for x in range(33)]
diff = sum(int(both(NAME, OLD, NEW, lambda f=f: mw(flow=f))[0] != both(NAME, OLD, NEW, lambda f=f: mw(flow=f))[1]) for f in grid)
print(f"RESULT differing_reachable={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: mw(flow=8.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
